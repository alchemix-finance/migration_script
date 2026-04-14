"""Gnosis Safe integration for CDP migration.

This module provides:
- SafeTransaction dataclass for Safe-compatible transaction format
- Functions to convert TransactionBatch objects to Safe format
- MultiSend encoding for batching multiple calls
- Serialization for Safe Transaction Service API

Safe Multi-Send Transaction Format:
Each transaction in a multi-send batch has:
- to: target contract address (20 bytes)
- value: ETH value (0 for these operations) (32 bytes)
- data: encoded function call (variable length)
- operation: 0 (Call) or 1 (DelegateCall) - we use 0

The MultiSend contract packs transactions as:
operation (1 byte) + to (20 bytes) + value (32 bytes) + data_length (32 bytes) + data (variable)
"""

import json as json_lib
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from eth_abi import encode
from eth_utils import keccak

from src.types import TransactionBatch, TransactionCall

# Lazy imports for signing — only needed when proposing to real Safe API


def _safe_api_timeout() -> float:
    from src.env import get_safe_api_timeout_seconds

    return get_safe_api_timeout_seconds()


def _ssl_context_for_https() -> ssl.SSLContext:
    """TLS context that uses certifi CA bundle when available (fixes macOS Python verify failures)."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


class SafeOperationType(IntEnum):
    """Safe operation types for transactions."""

    CALL = 0  # Regular call
    DELEGATE_CALL = 1  # Delegate call (not used for CDP migration)


@dataclass
class SafeTransaction:
    """A transaction formatted for Gnosis Safe.

    This represents either a single transaction or a batched
    multi-send transaction that can be proposed to a Safe.

    Attributes:
        to: Target contract address (MultiSend contract for batches)
        value: ETH value to send (always 0 for CDP operations)
        data: Encoded function call data
        operation: Call type (0 = Call, 1 = DelegateCall)
        safe_tx_gas: Gas for the Safe transaction execution
        base_gas: Base gas for signature checks, etc.
        gas_price: Gas price (0 for EIP-1559)
        gas_token: Token for gas payment (address(0) for ETH)
        refund_receiver: Address to receive gas refund (address(0) for tx.origin)
        nonce: Safe nonce for this transaction
        descriptions: Human-readable descriptions of included operations
    """

    to: str
    value: int = 0
    data: bytes = field(default_factory=bytes)
    operation: int = SafeOperationType.CALL
    safe_tx_gas: int = 0
    base_gas: int = 0
    gas_price: int = 0
    gas_token: str = "0x0000000000000000000000000000000000000000"
    refund_receiver: str = "0x0000000000000000000000000000000000000000"
    nonce: int | None = None  # Will be set when proposing
    descriptions: list[str] = field(default_factory=list)

    @property
    def is_multisend(self) -> bool:
        """Check if this is a multi-send transaction (batched)."""
        return len(self.descriptions) > 1

    @property
    def transaction_count(self) -> int:
        """Number of transactions in this Safe tx (1 for single, N for multisend)."""
        return max(1, len(self.descriptions))


# Known MultiSend contract addresses on different chains
# These are the official Gnosis Safe MultiSend contracts
MULTISEND_ADDRESSES: dict[int, str] = {
    1: "0x40A2aCCbd92BCA938b02010E17A5b8929b49130D",  # Ethereum Mainnet
    10: "0x998739BFdAAdde7C933B942a68053933098f9EDa",  # Optimism
    42161: "0x998739BFdAAdde7C933B942a68053933098f9EDa",  # Arbitrum
}

# MultiSend function selector: multiSend(bytes transactions)
MULTISEND_SELECTOR = keccak(text="multiSend(bytes)")[:4]


def encode_multisend_data(calls: list[TransactionCall]) -> bytes:
    """Encode multiple calls into MultiSend format.

    The MultiSend contract expects a packed bytes array where each
    transaction is encoded as:
    - operation: uint8 (1 byte) - always 0 (Call)
    - to: address (20 bytes)
    - value: uint256 (32 bytes)
    - dataLength: uint256 (32 bytes)
    - data: bytes (variable)

    Args:
        calls: List of transaction calls to encode

    Returns:
        Encoded bytes for the MultiSend contract
    """
    packed_transactions = b""

    for call in calls:
        # Operation: 1 byte (0 = Call)
        operation = SafeOperationType.CALL.to_bytes(1, "big")

        # To address: 20 bytes (remove 0x prefix, convert to bytes)
        to_address = bytes.fromhex(call.to[2:])

        # Value: 32 bytes (uint256)
        value = call.value.to_bytes(32, "big")

        # Data length: 32 bytes (uint256)
        data_length = len(call.data).to_bytes(32, "big")

        # Data: variable length
        data = call.data

        # Pack this transaction
        packed_transactions += operation + to_address + value + data_length + data

    return packed_transactions


def encode_multisend_call(calls: list[TransactionCall]) -> bytes:
    """Encode a complete multiSend function call.

    This creates the full calldata for calling the MultiSend contract's
    multiSend(bytes transactions) function.

    Args:
        calls: List of transaction calls to batch

    Returns:
        Complete calldata for multiSend function
    """
    # Encode the packed transactions
    packed_data = encode_multisend_data(calls)

    # Encode as multiSend(bytes)
    # The function signature is multiSend(bytes)
    # We need to ABI encode a bytes parameter
    encoded_args = encode(["bytes"], [packed_data])

    return MULTISEND_SELECTOR + encoded_args


def convert_batch_to_safe_tx(
    batch: TransactionBatch,
    chain_id: int = 1,
    multisend_address: str | None = None,
) -> SafeTransaction:
    """Convert a TransactionBatch to a SafeTransaction.

    For batches with multiple calls, this creates a multi-send transaction.
    For batches with a single call, it creates a simple transaction.

    Args:
        batch: The transaction batch to convert
        chain_id: Chain ID (for looking up MultiSend address)
        multisend_address: Optional override for MultiSend contract address

    Returns:
        SafeTransaction ready for proposal

    Raises:
        ValueError: If batch is empty or chain not supported
    """
    if not batch.calls:
        raise ValueError("Cannot convert empty batch to Safe transaction")

    # Collect descriptions
    descriptions = [call.description for call in batch.calls if call.description]

    # Single call - no need for MultiSend
    if len(batch.calls) == 1:
        call = batch.calls[0]
        return SafeTransaction(
            to=call.to,
            value=call.value,
            data=call.data,
            operation=SafeOperationType.CALL,
            safe_tx_gas=call.gas_estimate,
            descriptions=descriptions,
        )

    # Multiple calls - use MultiSend
    if multisend_address is None:
        multisend_address = MULTISEND_ADDRESSES.get(chain_id)
        if multisend_address is None:
            raise ValueError(
                f"No MultiSend address known for chain {chain_id}. "
                f"Supported chains: {list(MULTISEND_ADDRESSES.keys())}"
            )

    # Encode all calls into MultiSend format
    multisend_data = encode_multisend_call(batch.calls)

    # Total gas is sum of all individual gas estimates
    total_gas = sum(call.gas_estimate for call in batch.calls)

    return SafeTransaction(
        to=multisend_address,
        value=0,  # No ETH sent to MultiSend
        data=multisend_data,
        operation=SafeOperationType.DELEGATE_CALL,  # MultiSend uses delegatecall
        safe_tx_gas=total_gas,
        descriptions=descriptions,
    )


def format_safe_batch(
    batches: list[TransactionBatch],
    chain_id: int = 1,
    multisend_address: str | None = None,
) -> list[SafeTransaction]:
    """Convert multiple TransactionBatches to SafeTransactions.

    Args:
        batches: List of transaction batches to convert
        chain_id: Chain ID (for looking up MultiSend address)
        multisend_address: Optional override for MultiSend contract address

    Returns:
        List of SafeTransactions ready for proposal
    """
    safe_txs = []
    for batch in batches:
        if batch.calls:  # Skip empty batches
            safe_tx = convert_batch_to_safe_tx(
                batch=batch,
                chain_id=chain_id,
                multisend_address=multisend_address,
            )
            safe_txs.append(safe_tx)
    return safe_txs


def serialize_for_safe_api(safe_tx: SafeTransaction) -> dict[str, Any]:
    """Serialize a SafeTransaction for the Safe Transaction Service API.

    This creates a JSON-serializable dictionary that can be sent to
    the Safe Transaction Service API to propose a transaction.

    Args:
        safe_tx: The SafeTransaction to serialize

    Returns:
        Dictionary suitable for JSON serialization and API submission
    """
    return {
        "to": safe_tx.to,
        "value": str(safe_tx.value),  # API expects string for large numbers
        "data": "0x" + safe_tx.data.hex() if safe_tx.data else "0x",
        "operation": safe_tx.operation,
        "safeTxGas": str(safe_tx.safe_tx_gas),
        "baseGas": str(safe_tx.base_gas),
        "gasPrice": str(safe_tx.gas_price),
        "gasToken": safe_tx.gas_token,
        "refundReceiver": safe_tx.refund_receiver,
        "nonce": safe_tx.nonce,
    }


def serialize_batch_for_display(safe_tx: SafeTransaction) -> dict[str, Any]:
    """Create a human-readable summary of a SafeTransaction.

    This is useful for preview screens before proposing.

    Args:
        safe_tx: The SafeTransaction to summarize

    Returns:
        Dictionary with human-readable summary
    """
    return {
        "type": "MultiSend" if safe_tx.is_multisend else "Single",
        "target": safe_tx.to,
        "operation_count": safe_tx.transaction_count,
        "estimated_gas": safe_tx.safe_tx_gas,
        "operations": safe_tx.descriptions,
        "data_size_bytes": len(safe_tx.data),
    }


class ProposeToSafe:
    """Client for proposing transactions to a Gnosis Safe.

    This class handles the interaction with the Safe Transaction Service
    API to propose transactions for signature collection.

    Note: Actual API calls are stubbed for testing. In production, this
    would use the safe-eth-py library or direct HTTP calls.
    """

    # Safe Transaction Service URLs by chain
    SAFE_TX_SERVICE_URLS: dict[int, str] = {
        1: "https://safe-transaction-mainnet.safe.global",
        10: "https://safe-transaction-optimism.safe.global",
        42161: "https://api.safe.global/tx-service/arb1",
    }

    def __init__(
        self,
        safe_address: str,
        chain_id: int = 1,
        signer_address: str | None = None,
        api_url: str | None = None,
        signer_pk: str | None = None,
    ):
        """Initialize the Safe proposer.

        Args:
            safe_address: The Safe multisig address
            chain_id: Chain ID for the network
            signer_address: Address of the proposer (must be a Safe owner).
                If not provided, loaded from PROPOSER_ADDRESS env var.
            api_url: Optional override for Safe Transaction Service URL
            signer_pk: Hex-encoded private key for signing proposals.
                If not provided, loaded from PROPOSER_PRIVATE_KEY env var.
        """
        self.safe_address = safe_address
        self.chain_id = chain_id
        self._next_nonce: int | None = None

        # Resolve signer credentials from env if not passed explicitly
        from src.env import get_proposer_address, get_proposer_private_key

        try:
            self.signer_pk = signer_pk or get_proposer_private_key()
        except EnvironmentError:
            self.signer_pk = None

        try:
            self.signer_address = signer_address or get_proposer_address()
        except EnvironmentError:
            self.signer_address = None

        if self.signer_pk and not self.signer_address:
            from eth_account import Account

            self.signer_address = Account.from_key(f"0x{self.signer_pk}").address

        if api_url:
            self.api_url = api_url
        else:
            self.api_url = self.SAFE_TX_SERVICE_URLS.get(chain_id)
            if not self.api_url:
                raise ValueError(
                    f"No Safe Transaction Service URL known for chain {chain_id}"
                )

    def _resolve_initial_nonce(self) -> None:
        """Set _next_nonce from env override or Safe Transaction Service."""
        if self._next_nonce is not None:
            return
        from src.env import get_safe_proposal_start_nonce

        override = get_safe_proposal_start_nonce()
        if override is not None:
            self._next_nonce = override
            return
        try:
            self._next_nonce = self.get_next_nonce()
        except ValueError as e:
            raise ValueError(
                "Could not fetch Safe nonce from the Transaction Service API. "
                "Fix TLS (e.g. `pip install certifi`), increase SAFE_API_TIMEOUT, "
                "or set SAFE_PROPOSAL_START_NONCE in .env to the next nonce from the Safe app."
            ) from e

    def get_next_nonce(self) -> int:
        """Fetch the next available nonce from the Safe Transaction Service.

        Returns:
            Next available nonce for the Safe

        Raises:
            ValueError: If the API call fails
        """
        url = f"{self.api_url}/api/v1/safes/{self.safe_address}/"
        timeout = _safe_api_timeout()
        try:
            ctx = _ssl_context_for_https()
            with urllib.request.urlopen(url, timeout=timeout, context=ctx) as response:
                data = json_lib.loads(response.read().decode())
                return int(data["nonce"])
        except TimeoutError as e:
            raise ValueError(
                f"Safe API timed out ({timeout:.0f}s) fetching nonce from {url}. "
                "Set SAFE_PROPOSAL_START_NONCE in .env to skip this request, or set SAFE_API_TIMEOUT "
                "to a larger value (seconds)."
            ) from e
        except urllib.error.URLError as e:
            raise ValueError(f"Failed to fetch Safe nonce from {url}: {e}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Unexpected response from Safe API: {e}")

    def propose_batch(
        self,
        safe_tx: SafeTransaction,
        sender: str | None = None,
    ) -> dict[str, Any]:
        """Propose a Safe transaction for signatures.

        This creates a transaction proposal in the Safe Transaction Service.
        Other Safe owners can then sign it through the Safe UI.

        Args:
            safe_tx: The SafeTransaction to propose
            sender: Address proposing the transaction (must be a Safe owner)

        Returns:
            Dictionary with proposal result (stub for now)

        Raises:
            ValueError: If sender is not configured
        """
        sender = sender or self.signer_address
        if not sender:
            raise ValueError(
                "Sender address required for proposal. Set PROPOSER_ADDRESS in .env "
                "or PROPOSER_PRIVATE_KEY (address is derived from the key)."
            )

        self._resolve_initial_nonce()

        safe_tx.nonce = self._next_nonce
        self._next_nonce += 1

        tx_data = serialize_for_safe_api(safe_tx)

        # Compute the Safe tx hash and sign it with the proposer's private key
        tx_hash = compute_safe_tx_hash(
            self.safe_address, safe_tx, self.chain_id
        )

        if self.signer_pk:
            from eth_account import Account

            # eth-account >=0.13 removed Account.signHash; unsafe_sign_hash matches the old ECDSA-on-digest behavior.
            proposer = Account.from_key(f"0x{self.signer_pk}")
            signed = proposer.unsafe_sign_hash(tx_hash)
            sig_hex = signed.signature.hex()
        else:
            # Dry-run / no-key mode: propose without signature (will need manual signing in Safe UI)
            sig_hex = ""

        # POST to Safe Transaction Service API
        payload = {
            **tx_data,
            "contractTransactionHash": f"0x{tx_hash.hex()}",
            "signature": f"0x{sig_hex}" if sig_hex else "",
            "sender": sender,
        }

        api_endpoint = f"{self.api_url}/api/v1/safes/{self.safe_address}/multisig-transactions/"

        if not self.signer_pk:
            return {
                "status": "stubbed",
                "message": "No proposer key configured — transaction prepared but not submitted",
                "safe_address": self.safe_address,
                "chain_id": self.chain_id,
                "sender": sender,
                "nonce": safe_tx.nonce,
                "safe_tx_hash": f"0x{tx_hash.hex()}",
                "transaction_data": tx_data,
                "api_url": api_endpoint,
            }

        req = urllib.request.Request(
            api_endpoint,
            data=json_lib.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        timeout = _safe_api_timeout()
        try:
            ctx = _ssl_context_for_https()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                raw_body = response.read().decode()
                resp_body = json_lib.loads(raw_body) if raw_body.strip() else {}
                return {
                    "status": "success",
                    "safe_address": self.safe_address,
                    "chain_id": self.chain_id,
                    "sender": sender,
                    "nonce": safe_tx.nonce,
                    "safe_tx_hash": f"0x{tx_hash.hex()}",
                    "api_response": resp_body,
                    "api_url": api_endpoint,
                }
        except TimeoutError as e:
            return {
                "status": "error",
                "message": (
                    f"Safe API timed out ({timeout:.0f}s) posting proposal. "
                    f"Retry or increase SAFE_API_TIMEOUT. ({e})"
                ),
                "safe_address": self.safe_address,
                "chain_id": self.chain_id,
                "sender": sender,
                "nonce": safe_tx.nonce,
                "safe_tx_hash": f"0x{tx_hash.hex()}",
                "api_url": api_endpoint,
            }
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            return {
                "status": "error",
                "message": f"Safe API returned {e.code}: {body}",
                "safe_address": self.safe_address,
                "chain_id": self.chain_id,
                "sender": sender,
                "nonce": safe_tx.nonce,
                "safe_tx_hash": f"0x{tx_hash.hex()}",
                "api_url": api_endpoint,
            }

    def propose_all_batches(
        self,
        safe_txs: list[SafeTransaction],
        sender: str | None = None,
    ) -> list[dict[str, Any]]:
        """Propose multiple Safe transactions.

        Args:
            safe_txs: List of SafeTransactions to propose
            sender: Address proposing the transactions

        Returns:
            List of proposal results
        """
        # Resolve nonce once before proposing so API/env errors fail fast.
        self._resolve_initial_nonce()

        results = []
        for safe_tx in safe_txs:
            result = self.propose_batch(safe_tx, sender)
            results.append(result)
        return results


def compute_safe_tx_hash(
    safe_address: str,
    safe_tx: SafeTransaction,
    chain_id: int = 1,
) -> bytes:
    """Compute the Safe transaction hash for signing.

    This is the hash that Safe owners sign to approve a transaction.
    It follows EIP-712 structured data signing.

    Args:
        safe_address: The Safe multisig address
        safe_tx: The SafeTransaction to hash
        chain_id: Chain ID for domain separator

    Returns:
        32-byte transaction hash
    """
    # Safe transaction type hash
    SAFE_TX_TYPEHASH = keccak(
        text=(
            "SafeTx(address to,uint256 value,bytes data,uint8 operation,"
            "uint256 safeTxGas,uint256 baseGas,uint256 gasPrice,"
            "address gasToken,address refundReceiver,uint256 nonce)"
        )
    )

    # Domain separator type hash
    DOMAIN_SEPARATOR_TYPEHASH = keccak(
        text="EIP712Domain(uint256 chainId,address verifyingContract)"
    )

    # Compute domain separator
    domain_separator = keccak(
        encode(
            ["bytes32", "uint256", "address"],
            [DOMAIN_SEPARATOR_TYPEHASH, chain_id, safe_address],
        )
    )

    # Hash the data field
    data_hash = keccak(safe_tx.data)

    # Compute struct hash
    struct_hash = keccak(
        encode(
            [
                "bytes32",
                "address",
                "uint256",
                "bytes32",
                "uint8",
                "uint256",
                "uint256",
                "uint256",
                "address",
                "address",
                "uint256",
            ],
            [
                SAFE_TX_TYPEHASH,
                safe_tx.to,
                safe_tx.value,
                data_hash,
                safe_tx.operation,
                safe_tx.safe_tx_gas,
                safe_tx.base_gas,
                safe_tx.gas_price,
                safe_tx.gas_token,
                safe_tx.refund_receiver,
                safe_tx.nonce or 0,
            ],
        )
    )

    # Compute final hash: keccak256("\x19\x01" + domain_separator + struct_hash)
    return keccak(b"\x19\x01" + domain_separator + struct_hash)
