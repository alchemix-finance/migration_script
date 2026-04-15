"""Execution-layer abstraction for Safe transaction batches.

Three execution modes, each implementing `propose_all_batches(safe_txs)`:

- `propose`     → legacy Safe API proposal (requires private key). Existing behavior.
- `json`        → writes Safe Transaction Builder JSON files to out/ for UI upload.
                  Production path (no signing key needed).
- `impersonate` → directly sends each call from the multisig on an ape fork
                  using account impersonation. Testing path (no signing key needed).

Factory: `make_executor(mode, *, batches, safe_address, chain_id, chain, asset_type,
step_name, out_dir, post_conditions=None)`.

The factory-returned object matches `ProposeToSafe`'s `propose_all_batches` interface
so existing scripts swap one line: `proposer = ProposeToSafe(...)` →
`proposer = make_executor("json", ..., batches=batches)`.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Protocol

from src.safe import ProposeToSafe, SafeTransaction
from src.types import AssetType, TransactionBatch

ExecMode = Literal["json", "impersonate", "propose"]


class Executor(Protocol):
    def propose_all_batches(
        self, safe_txs: list[SafeTransaction], sender: str | None = None
    ) -> list[dict[str, Any]]: ...


def _asset_slug(asset_type: AssetType) -> str:
    return "alUSD" if asset_type == AssetType.USD else "alETH"


@dataclass
class JsonExporter:
    """Writes one Safe Transaction Builder JSON file per batch to out_dir.

    Format: https://docs.safe.global/sdk/transaction-builder  (v1.0).

    For multi-call batches, each inner call becomes a flat transaction entry
    (not a packed multisend bundle). This keeps the Safe UI preview readable
    and avoids forcing reviewers to decode multisend bytes.
    """

    batches: list[TransactionBatch]
    safe_address: str
    chain_id: int
    chain: str
    asset_type: AssetType
    step_name: str
    out_dir: Path

    _cursor: int = 0  # next batch index to consume across calls

    def __post_init__(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def propose_all_batches(
        self, safe_txs: list[SafeTransaction], sender: str | None = None
    ) -> list[dict[str, Any]]:
        # Consume the next len(safe_txs) batches starting from the cursor.
        # This lets scripts call propose_all_batches([safe_tx]) one at a time
        # (checkpoint mode) without re-emitting earlier batches.
        results: list[dict[str, Any]] = []
        for _safe_tx in safe_txs:
            if self._cursor >= len(self.batches):
                break
            batch = self.batches[self._cursor]
            self._cursor += 1
            path = self._write_batch(batch)
            results.append({
                "status": "success",
                "mode": "json",
                "path": str(path),
                "batch_number": batch.batch_number,
                "batch_type": batch.batch_type,
                "call_count": len(batch.calls),
            })
        return results

    def _write_batch(self, batch: TransactionBatch) -> Path:
        asset_slug = _asset_slug(self.asset_type)
        fname = (
            f"{self.chain}_{asset_slug}_{self.step_name}"
            f"_batch{batch.batch_number:02d}.json"
        )
        path = self.out_dir / fname

        transactions = [
            {
                "to": call.to,
                "value": str(call.value),
                "data": "0x" + call.data.hex() if call.data else "0x",
                "contractMethod": None,
                "contractInputsValues": None,
            }
            for call in batch.calls
        ]

        payload = {
            "version": "1.0",
            "chainId": str(self.chain_id),
            "createdAt": int(time.time() * 1000),
            "meta": {
                "name": f"{self.chain}_{asset_slug}_{self.step_name}_batch{batch.batch_number}",
                "description": f"{self.step_name} — batch {batch.batch_number} ({len(batch.calls)} calls)",
                "txBuilderVersion": "1.17.0",
                "createdFromSafeAddress": self.safe_address,
                "createdFromOwnerAddress": "",
            },
            "transactions": transactions,
        }

        path.write_text(json.dumps(payload, indent=2))
        return path


@dataclass
class ForkImpersonator:
    """Executes calls directly from the multisig on an ape fork.

    Requires an active ape provider with impersonation support (anvil/foundry,
    or hardhat). Each call in each batch is sent with sender=multisig.
    After each batch, runs the optional post_conditions callback.
    """

    batches: list[TransactionBatch]
    safe_address: str
    chain_id: int
    chain: str
    asset_type: AssetType
    step_name: str
    out_dir: Path
    post_conditions: Callable[[TransactionBatch], None] | None = None
    _cursor: int = 0

    def propose_all_batches(
        self, safe_txs: list[SafeTransaction], sender: str | None = None
    ) -> list[dict[str, Any]]:
        """Execute each call directly against a running anvil/hardhat fork.

        Expects a fork listening at the URL given by the FORK_RPC_URL env var
        (default http://localhost:8545). Use anvil's impersonation RPCs rather
        than ape's foundry provider so the fork can be long-lived across many
        script runs.
        """
        import os
        from web3 import Web3

        multisig = Web3.to_checksum_address(self.safe_address)
        rpc_url = os.environ.get("FORK_RPC_URL", "http://localhost:8545")
        receipt_timeout = float(os.environ.get("FORK_RECEIPT_TIMEOUT", "300"))
        http_timeout = float(os.environ.get("FORK_HTTP_TIMEOUT", "120"))
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": http_timeout}))

        if not w3.is_connected():
            raise RuntimeError(
                f"No fork reachable at {rpc_url}. Start anvil:\n"
                f"  anvil --fork-url <RPC> --port 8545 --chain-id <id>"
            )

        # Anvil / hardhat impersonation RPCs
        w3.provider.make_request("anvil_impersonateAccount", [multisig])
        w3.provider.make_request("anvil_setBalance", [multisig, hex(10 * 10**18)])

        # Consume the next len(safe_txs) batches (checkpoint-safe).
        consume_count = len(safe_txs)
        start = self._cursor
        end = min(start + consume_count, len(self.batches))
        self._cursor = end

        # Fork-throughput tuning:
        # - Skip per-call eth_estimateGas; use a high static gas cap (anvil
        #   discards unused gas, so overbudgeting is free). Saves one RPC
        #   round-trip per call.
        # - Wait for each tx's receipt before submitting the next. Earlier
        #   experiment with pipelined submit (send all → sweep receipts)
        #   produced occasional 300s stalls on large batches because some
        #   submits outpaced anvil's tx acceptance, leaving hashes without
        #   matching receipts. Per-tx wait with a tight 10ms poll_latency
        #   is nearly as fast and deterministic.
        fork_gas = int(os.environ.get("FORK_GAS_PER_CALL", str(5_000_000)))
        poll_latency = float(os.environ.get("FORK_POLL_LATENCY", "0.01"))

        results: list[dict[str, Any]] = []
        for batch in self.batches[start:end]:
            tx_hashes: list[str] = []
            for call in batch.calls:
                tx = {
                    "from": multisig,
                    "to": Web3.to_checksum_address(call.to),
                    "data": "0x" + call.data.hex() if call.data else "0x",
                    "value": hex(call.value),
                    "gas": hex(fork_gas),
                }
                tx_hash = w3.eth.send_transaction(tx)
                receipt = w3.eth.wait_for_transaction_receipt(
                    tx_hash, timeout=receipt_timeout, poll_latency=poll_latency,
                )
                if receipt.status != 1:
                    raise RuntimeError(
                        f"Impersonated tx reverted: batch {batch.batch_number} "
                        f"call '{call.description}' tx {tx_hash.hex()}"
                    )
                tx_hashes.append(tx_hash.hex())

            if self.post_conditions is not None:
                self.post_conditions(batch)

            results.append({
                "status": "success",
                "mode": "impersonate",
                "batch_number": batch.batch_number,
                "batch_type": batch.batch_type,
                "call_count": len(batch.calls),
                "tx_hashes": tx_hashes,
            })
        return results


def make_executor(
    mode: ExecMode,
    *,
    batches: list[TransactionBatch],
    safe_address: str,
    chain_id: int,
    chain: str,
    asset_type: AssetType,
    step_name: str,
    out_dir: Path | None = None,
    post_conditions: Callable[[TransactionBatch], None] | None = None,
) -> Executor:
    """Return an executor matching `ProposeToSafe.propose_all_batches`.

    Args:
        mode: 'json' (default production), 'impersonate' (fork testing), 'propose' (legacy API).
        batches: Raw TransactionBatch list — needed by json/impersonate modes.
        safe_address: Migration multisig address.
        chain_id: EVM chain id.
        chain: Chain name ('mainnet'/'optimism'/'arbitrum') — for filename slugs.
        asset_type: AssetType.USD or AssetType.ETH.
        step_name: Short step identifier, e.g. 'deposit', 'approve_underlying'.
        out_dir: Directory for JSON output (default: <project>/out).
        post_conditions: Optional callback run after each batch in impersonate mode.
    """
    if out_dir is None:
        from src.config import PROJECT_ROOT
        out_dir = PROJECT_ROOT / "out"

    if mode == "json":
        return JsonExporter(
            batches=batches,
            safe_address=safe_address,
            chain_id=chain_id,
            chain=chain,
            asset_type=asset_type,
            step_name=step_name,
            out_dir=out_dir,
        )
    if mode == "impersonate":
        return ForkImpersonator(
            batches=batches,
            safe_address=safe_address,
            chain_id=chain_id,
            chain=chain,
            asset_type=asset_type,
            step_name=step_name,
            out_dir=out_dir,
            post_conditions=post_conditions,
        )
    if mode == "propose":
        return ProposeToSafe(safe_address=safe_address, chain_id=chain_id)
    raise ValueError(f"Unknown mode: {mode!r}. Expected 'json', 'impersonate', or 'propose'.")
