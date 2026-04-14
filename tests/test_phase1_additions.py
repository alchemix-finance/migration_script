"""Tests for Phase 1 additions: new transaction builders, batch builders,
executor (JsonExporter + factory), and idempotency preflight helpers.

Scoped to new code only — does not patch legacy broken tests in this suite.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from eth_abi import decode
from eth_utils import keccak

from src.executor import ForkImpersonator, JsonExporter, make_executor
from src.gas import (
    compute_underlying_total,
    create_approve_myt_batches,
    create_approve_underlying_batches,
    create_myt_deposit_batches,
)
from src.safe import SafeTransaction, format_safe_batch
from src.transactions import build_erc20_approve_tx, build_erc4626_deposit_tx
from src.types import AssetType, PositionMigration, TransactionBatch

MULTISIG = "0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b"
UNDERLYING = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"  # USDC on Arbitrum
MYT = "0xEba62B842081CeF5a8184318Dc5C4E4aACa9f651"
ALCHEMIST = "0x930750a3510E703535e943E826ABa3c364fFC1De"

APPROVE_SELECTOR = keccak(text="approve(address,uint256)")[:4]
ERC4626_DEPOSIT_SELECTOR = keccak(text="deposit(uint256,address)")[:4]


# ---- transaction builders ------------------------------------------------

def test_build_erc20_approve_tx_selector_and_args() -> None:
    tx = build_erc20_approve_tx(UNDERLYING, MYT, 12345)
    assert tx.to == UNDERLYING
    assert tx.value == 0
    assert tx.gas_estimate == 55_000
    assert tx.data[:4] == APPROVE_SELECTOR
    (spender, amount) = decode(["address", "uint256"], tx.data[4:])
    assert spender.lower() == MYT.lower()
    assert amount == 12345


def test_build_erc4626_deposit_tx_selector_and_args() -> None:
    tx = build_erc4626_deposit_tx(MYT, 10**18, MULTISIG)
    assert tx.to == MYT
    assert tx.data[:4] == ERC4626_DEPOSIT_SELECTOR
    (assets, receiver) = decode(["uint256", "address"], tx.data[4:])
    assert assets == 10**18
    assert receiver.lower() == MULTISIG.lower()
    assert tx.gas_estimate == 180_000


# ---- batch builders ------------------------------------------------------

def test_create_approve_underlying_batches_one_call() -> None:
    batches = create_approve_underlying_batches(UNDERLYING, MYT, 500, "arbitrum")
    assert len(batches) == 1
    assert len(batches[0].calls) == 1
    assert batches[0].batch_type == "approve_underlying"
    assert batches[0].calls[0].to == UNDERLYING


def test_create_myt_deposit_batches_one_call() -> None:
    batches = create_myt_deposit_batches(MYT, MULTISIG, 10**18, "arbitrum")
    assert len(batches) == 1
    assert batches[0].calls[0].to == MYT
    assert batches[0].batch_type == "deposit_myt"


def test_create_approve_myt_batches_one_call() -> None:
    batches = create_approve_myt_batches(MYT, ALCHEMIST, 10**18, "arbitrum")
    assert len(batches) == 1
    assert batches[0].calls[0].to == MYT
    assert batches[0].batch_type == "approve_myt"


def test_batch_builders_empty_on_zero_amount() -> None:
    assert create_approve_underlying_batches(UNDERLYING, MYT, 0, "arbitrum") == []
    assert create_myt_deposit_batches(MYT, MULTISIG, 0, "arbitrum") == []
    assert create_approve_myt_batches(MYT, ALCHEMIST, 0, "arbitrum") == []


# ---- compute_underlying_total -------------------------------------------

def _pos(deposit_wei: int) -> PositionMigration:
    return PositionMigration(
        user_address="0x1111111111111111111111111111111111111111",
        asset_type=AssetType.USD,
        chain="arbitrum",
        deposit_amount_wei=deposit_wei,
        mint_amount_wei=0,
        credit_amount_wei=0,
    )


def test_compute_underlying_total_same_decimals_passthrough() -> None:
    positions = [_pos(10**18), _pos(3 * 10**18)]
    total = compute_underlying_total(positions, underlying_decimals=18, myt_decimals=18)
    assert total == 4 * 10**18


def test_compute_underlying_total_usdc_rescale_ceil() -> None:
    # 1.5 USDC equivalent at 18-dec → 1_500_000_000_000_000_000 wei
    # Rescaled to 6 dec → 1_500_000 (exact, no ceil needed)
    positions = [_pos(1_500_000_000_000_000_000)]
    total = compute_underlying_total(positions, underlying_decimals=6, myt_decimals=18)
    assert total == 1_500_000


def test_compute_underlying_total_ceils_partial_wei() -> None:
    # 1 wei (at 18 dec) rescaled to 6 dec would be 0.000000001 → ceils to 1
    positions = [_pos(1)]
    total = compute_underlying_total(positions, underlying_decimals=6, myt_decimals=18)
    assert total == 1


# ---- JsonExporter --------------------------------------------------------

def _sample_batch(n: int = 1) -> TransactionBatch:
    b = TransactionBatch(batch_number=n, batch_type="approve_underlying")
    tx = build_erc20_approve_tx(UNDERLYING, MYT, 1000)
    b.add_call(tx)
    return b


def test_json_exporter_writes_valid_safe_builder_schema(tmp_path: Path) -> None:
    batch = _sample_batch(1)
    safe_txs = format_safe_batch([batch], chain_id=42161)
    exp = JsonExporter(
        batches=[batch], safe_address=MULTISIG, chain_id=42161,
        chain="arbitrum", asset_type=AssetType.USD, step_name="approve_underlying",
        out_dir=tmp_path,
    )
    results = exp.propose_all_batches(safe_txs)
    assert len(results) == 1
    assert results[0]["status"] == "success"
    out_path = Path(results[0]["path"])
    assert out_path.exists()
    payload = json.loads(out_path.read_text())
    assert payload["version"] == "1.0"
    assert payload["chainId"] == "42161"
    assert payload["meta"]["createdFromSafeAddress"] == MULTISIG
    assert len(payload["transactions"]) == 1
    t = payload["transactions"][0]
    assert t["to"] == UNDERLYING
    assert t["value"] == "0"
    assert t["data"].startswith("0x")
    assert t["data"][2:10] == APPROVE_SELECTOR.hex()


def test_json_exporter_cursor_advances_across_calls(tmp_path: Path) -> None:
    batches = [_sample_batch(1), _sample_batch(2), _sample_batch(3)]
    safe_txs = format_safe_batch(batches, chain_id=42161)
    exp = JsonExporter(
        batches=batches, safe_address=MULTISIG, chain_id=42161,
        chain="arbitrum", asset_type=AssetType.USD, step_name="x",
        out_dir=tmp_path,
    )
    # Call one-at-a-time (checkpoint mode) — each call consumes the next batch.
    r1 = exp.propose_all_batches([safe_txs[0]])
    r2 = exp.propose_all_batches([safe_txs[1]])
    r3 = exp.propose_all_batches([safe_txs[2]])
    assert r1[0]["batch_number"] == 1
    assert r2[0]["batch_number"] == 2
    assert r3[0]["batch_number"] == 3
    # 3 distinct files written
    files = sorted(tmp_path.glob("*.json"))
    assert len(files) == 3


# ---- make_executor factory ----------------------------------------------

def test_make_executor_returns_json_exporter_by_default(tmp_path: Path) -> None:
    batch = _sample_batch(1)
    ex = make_executor(
        "json", batches=[batch], safe_address=MULTISIG, chain_id=42161,
        chain="arbitrum", asset_type=AssetType.USD, step_name="x", out_dir=tmp_path,
    )
    assert isinstance(ex, JsonExporter)


def test_make_executor_impersonate_returns_fork_impersonator(tmp_path: Path) -> None:
    batch = _sample_batch(1)
    ex = make_executor(
        "impersonate", batches=[batch], safe_address=MULTISIG, chain_id=42161,
        chain="arbitrum", asset_type=AssetType.USD, step_name="x", out_dir=tmp_path,
    )
    assert isinstance(ex, ForkImpersonator)


def test_make_executor_unknown_mode_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        make_executor(
            "bogus",  # type: ignore[arg-type]
            batches=[_sample_batch(1)], safe_address=MULTISIG, chain_id=42161,
            chain="arbitrum", asset_type=AssetType.USD, step_name="x", out_dir=tmp_path,
        )


# ---- preflight helpers (rpc URL resolution only; no live network calls) --

def test_preflight_rpc_url_has_per_chain_entries() -> None:
    from src.preflight import _rpc_url
    for chain in ("mainnet", "arbitrum", "optimism"):
        url = _rpc_url(chain)
        assert url.startswith("https://")


def test_preflight_exports_expected_symbols() -> None:
    import src.preflight as p
    for name in (
        "check_approve_underlying_done", "check_myt_balance_done",
        "check_approve_myt_done", "check_deposit_done",
    ):
        assert hasattr(p, name), f"missing {name}"
