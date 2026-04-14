"""Unit tests for Gnosis Safe integration module."""

import pytest

from src.safe import (
    MULTISEND_ADDRESSES,
    MULTISEND_SELECTOR,
    ProposeToSafe,
    SafeOperationType,
    SafeTransaction,
    compute_safe_tx_hash,
    convert_batch_to_safe_tx,
    encode_multisend_call,
    encode_multisend_data,
    format_safe_batch,
    serialize_batch_for_display,
    serialize_for_safe_api,
)
from src.types import PositionMigration, TransactionBatch, TransactionCall


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_transaction_call() -> TransactionCall:
    """Create a sample TransactionCall for testing."""
    return TransactionCall(
        to="0x2222222222222222222222222222222222222222",
        data=b"\x12\x34\x56\x78" + b"\x00" * 96,  # Selector + 3 args
        value=0,
        gas_estimate=150_000,
        description="deposit(1000, 0xMultisig, 0) for 0xUser",
    )


@pytest.fixture
def sample_transaction_calls() -> list[TransactionCall]:
    """Create multiple sample TransactionCalls for batch testing."""
    return [
        TransactionCall(
            to="0x2222222222222222222222222222222222222222",
            data=b"\x12\x34\x56\x78" + b"\x00" * 96,
            value=0,
            gas_estimate=150_000,
            description="deposit(1000, 0xMultisig, 0) for 0xUser1",
        ),
        TransactionCall(
            to="0x2222222222222222222222222222222222222222",
            data=b"\xab\xcd\xef\x01" + b"\x00" * 96,
            value=0,
            gas_estimate=120_000,
            description="mint(0, 500, 0xUser1)",
        ),
        TransactionCall(
            to="0x4444444444444444444444444444444444444444",
            data=b"\x23\x45\x67\x89" + b"\x00" * 96,
            value=0,
            gas_estimate=65_000,
            description="transferFrom(0xMultisig, 0xUser1, 0)",
        ),
    ]


@pytest.fixture
def sample_batch(sample_transaction_calls) -> TransactionBatch:
    """Create a sample TransactionBatch for testing."""
    batch = TransactionBatch(batch_number=1)
    for call in sample_transaction_calls:
        batch.add_call(call)
    return batch


@pytest.fixture
def single_call_batch(sample_transaction_call) -> TransactionBatch:
    """Create a batch with a single call."""
    batch = TransactionBatch(batch_number=1)
    batch.add_call(sample_transaction_call)
    return batch


@pytest.fixture
def sample_safe_transaction() -> SafeTransaction:
    """Create a sample SafeTransaction for testing."""
    return SafeTransaction(
        to="0x1234567890123456789012345678901234567890",
        value=0,
        data=b"\x12\x34\x56\x78" + b"\x00" * 96,
        operation=SafeOperationType.CALL,
        safe_tx_gas=150_000,
        descriptions=["Test transaction"],
    )


@pytest.fixture
def sample_chain_config() -> dict[str, str]:
    """Sample chain configuration for testing."""
    return {
        "chain_id": 1,
        "multisig": "0x1111111111111111111111111111111111111111",
        "cdp_usd": "0x2222222222222222222222222222222222222222",
        "cdp_eth": "0x3333333333333333333333333333333333333333",
        "nft_usd": "0x4444444444444444444444444444444444444444",
        "nft_eth": "0x5555555555555555555555555555555555555555",
        "collateral_usd": "0x6666666666666666666666666666666666666666",
        "collateral_eth": "0x7777777777777777777777777777777777777777",
    }


# ============================================================================
# Test SafeOperationType
# ============================================================================


class TestSafeOperationType:
    """Tests for SafeOperationType enum."""

    def test_call_value(self):
        """Test CALL operation has value 0."""
        assert SafeOperationType.CALL == 0

    def test_delegate_call_value(self):
        """Test DELEGATE_CALL operation has value 1."""
        assert SafeOperationType.DELEGATE_CALL == 1


# ============================================================================
# Test SafeTransaction Dataclass
# ============================================================================


class TestSafeTransaction:
    """Tests for SafeTransaction dataclass."""

    def test_create_simple_transaction(self):
        """Test creating a simple SafeTransaction."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            value=0,
            data=b"\x12\x34\x56\x78",
        )
        assert tx.to == "0x1234567890123456789012345678901234567890"
        assert tx.value == 0
        assert tx.data == b"\x12\x34\x56\x78"
        assert tx.operation == SafeOperationType.CALL

    def test_default_values(self):
        """Test default values are set correctly."""
        tx = SafeTransaction(to="0x1234567890123456789012345678901234567890")
        assert tx.value == 0
        assert tx.data == b""
        assert tx.operation == SafeOperationType.CALL
        assert tx.safe_tx_gas == 0
        assert tx.base_gas == 0
        assert tx.gas_price == 0
        assert tx.gas_token == "0x0000000000000000000000000000000000000000"
        assert tx.refund_receiver == "0x0000000000000000000000000000000000000000"
        assert tx.nonce is None
        assert tx.descriptions == []

    def test_is_multisend_single(self):
        """Test is_multisend returns False for single transaction."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            descriptions=["Single operation"],
        )
        assert tx.is_multisend is False

    def test_is_multisend_batch(self):
        """Test is_multisend returns True for batched transactions."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            descriptions=["Operation 1", "Operation 2", "Operation 3"],
        )
        assert tx.is_multisend is True

    def test_transaction_count_single(self):
        """Test transaction_count for single transaction."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            descriptions=["Single operation"],
        )
        assert tx.transaction_count == 1

    def test_transaction_count_batch(self):
        """Test transaction_count for batched transactions."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            descriptions=["Op 1", "Op 2", "Op 3"],
        )
        assert tx.transaction_count == 3

    def test_transaction_count_empty(self):
        """Test transaction_count returns 1 for empty descriptions."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            descriptions=[],
        )
        assert tx.transaction_count == 1


# ============================================================================
# Test MultiSend Encoding
# ============================================================================


class TestEncodeMultisendData:
    """Tests for encode_multisend_data function."""

    def test_encode_single_call(self, sample_transaction_call):
        """Test encoding a single call."""
        encoded = encode_multisend_data([sample_transaction_call])

        # Structure: operation (1) + to (20) + value (32) + data_length (32) + data
        expected_length = 1 + 20 + 32 + 32 + len(sample_transaction_call.data)
        assert len(encoded) == expected_length

        # Check operation byte (0 = Call)
        assert encoded[0] == 0

        # Check address (bytes 1-21)
        to_bytes = bytes.fromhex(sample_transaction_call.to[2:])
        assert encoded[1:21] == to_bytes

    def test_encode_multiple_calls(self, sample_transaction_calls):
        """Test encoding multiple calls."""
        encoded = encode_multisend_data(sample_transaction_calls)

        # Each call: 1 + 20 + 32 + 32 + len(data)
        total_length = sum(
            1 + 20 + 32 + 32 + len(call.data) for call in sample_transaction_calls
        )
        assert len(encoded) == total_length

    def test_encode_empty_list(self):
        """Test encoding empty list returns empty bytes."""
        encoded = encode_multisend_data([])
        assert encoded == b""

    def test_value_encoding(self):
        """Test that value is correctly encoded as 32 bytes."""
        call = TransactionCall(
            to="0x1234567890123456789012345678901234567890",
            data=b"\x00" * 4,
            value=1000,
            gas_estimate=100_000,
        )
        encoded = encode_multisend_data([call])

        # Value is at bytes 21-53 (after operation + to)
        value_bytes = encoded[21:53]
        value = int.from_bytes(value_bytes, "big")
        assert value == 1000


class TestEncodeMultisendCall:
    """Tests for encode_multisend_call function."""

    def test_includes_selector(self, sample_transaction_calls):
        """Test that encoded call includes multiSend selector."""
        encoded = encode_multisend_call(sample_transaction_calls)
        assert encoded[:4] == MULTISEND_SELECTOR

    def test_abi_encoded_data(self, sample_transaction_call):
        """Test that data is properly ABI encoded."""
        encoded = encode_multisend_call([sample_transaction_call])

        # Selector (4) + offset (32) + length (32) + data
        assert len(encoded) > 68  # At minimum selector + offset + length


# ============================================================================
# Test Batch Conversion
# ============================================================================


class TestConvertBatchToSafeTx:
    """Tests for convert_batch_to_safe_tx function."""

    def test_single_call_batch(self, single_call_batch):
        """Test converting a batch with a single call."""
        safe_tx = convert_batch_to_safe_tx(single_call_batch, chain_id=1)

        # Single call should NOT use MultiSend
        assert safe_tx.to == single_call_batch.calls[0].to
        assert safe_tx.data == single_call_batch.calls[0].data
        assert safe_tx.operation == SafeOperationType.CALL
        assert safe_tx.is_multisend is False

    def test_multi_call_batch(self, sample_batch):
        """Test converting a batch with multiple calls."""
        safe_tx = convert_batch_to_safe_tx(sample_batch, chain_id=1)

        # Multiple calls should use MultiSend
        assert safe_tx.to == MULTISEND_ADDRESSES[1]  # Mainnet MultiSend
        assert safe_tx.operation == SafeOperationType.DELEGATE_CALL
        assert safe_tx.is_multisend is True

    def test_gas_estimate_sum(self, sample_batch):
        """Test that gas estimate is sum of all calls."""
        safe_tx = convert_batch_to_safe_tx(sample_batch, chain_id=1)
        expected_gas = sum(call.gas_estimate for call in sample_batch.calls)
        assert safe_tx.safe_tx_gas == expected_gas

    def test_descriptions_collected(self, sample_batch):
        """Test that descriptions are collected from all calls."""
        safe_tx = convert_batch_to_safe_tx(sample_batch, chain_id=1)
        assert len(safe_tx.descriptions) == len(sample_batch.calls)

    def test_empty_batch_raises(self):
        """Test that empty batch raises ValueError."""
        empty_batch = TransactionBatch(batch_number=1)
        with pytest.raises(ValueError, match="empty batch"):
            convert_batch_to_safe_tx(empty_batch)

    def test_unsupported_chain_raises(self, sample_batch):
        """Test that unsupported chain raises ValueError."""
        with pytest.raises(ValueError, match="No MultiSend address"):
            convert_batch_to_safe_tx(sample_batch, chain_id=999)

    def test_custom_multisend_address(self, sample_batch):
        """Test using a custom MultiSend address."""
        custom_address = "0x9999999999999999999999999999999999999999"
        safe_tx = convert_batch_to_safe_tx(
            sample_batch, chain_id=999, multisend_address=custom_address
        )
        assert safe_tx.to == custom_address

    def test_supported_chains(self, sample_batch):
        """Test conversion for all supported chains."""
        for chain_id in MULTISEND_ADDRESSES.keys():
            safe_tx = convert_batch_to_safe_tx(sample_batch, chain_id=chain_id)
            assert safe_tx.to == MULTISEND_ADDRESSES[chain_id]


class TestFormatSafeBatch:
    """Tests for format_safe_batch function."""

    def test_format_multiple_batches(self, sample_transaction_calls):
        """Test formatting multiple batches."""
        batch1 = TransactionBatch(batch_number=1)
        batch2 = TransactionBatch(batch_number=2)
        batch1.add_call(sample_transaction_calls[0])
        batch2.add_call(sample_transaction_calls[1])

        safe_txs = format_safe_batch([batch1, batch2], chain_id=1)
        assert len(safe_txs) == 2

    def test_skip_empty_batches(self, sample_transaction_call):
        """Test that empty batches are skipped."""
        batch1 = TransactionBatch(batch_number=1)
        batch1.add_call(sample_transaction_call)
        empty_batch = TransactionBatch(batch_number=2)

        safe_txs = format_safe_batch([batch1, empty_batch], chain_id=1)
        assert len(safe_txs) == 1

    def test_empty_input(self):
        """Test formatting empty list."""
        safe_txs = format_safe_batch([], chain_id=1)
        assert safe_txs == []


# ============================================================================
# Test Serialization
# ============================================================================


class TestSerializeForSafeApi:
    """Tests for serialize_for_safe_api function."""

    def test_basic_serialization(self, sample_safe_transaction):
        """Test basic serialization of a SafeTransaction."""
        serialized = serialize_for_safe_api(sample_safe_transaction)

        assert serialized["to"] == sample_safe_transaction.to
        assert serialized["value"] == "0"  # String format
        assert serialized["operation"] == SafeOperationType.CALL

    def test_data_hex_encoding(self, sample_safe_transaction):
        """Test that data is hex encoded with 0x prefix."""
        serialized = serialize_for_safe_api(sample_safe_transaction)
        assert serialized["data"].startswith("0x")
        # Data should be hex encoded version of bytes
        assert len(serialized["data"]) == 2 + len(sample_safe_transaction.data) * 2

    def test_empty_data(self):
        """Test serialization with empty data."""
        tx = SafeTransaction(to="0x1234567890123456789012345678901234567890")
        serialized = serialize_for_safe_api(tx)
        assert serialized["data"] == "0x"

    def test_gas_as_string(self, sample_safe_transaction):
        """Test that gas values are serialized as strings."""
        serialized = serialize_for_safe_api(sample_safe_transaction)
        assert serialized["safeTxGas"] == str(sample_safe_transaction.safe_tx_gas)
        assert serialized["baseGas"] == str(sample_safe_transaction.base_gas)
        assert serialized["gasPrice"] == str(sample_safe_transaction.gas_price)

    def test_meta_exposed_via_serialize_batch_for_display(self, sample_safe_transaction):
        """V3 split: serialize_for_safe_api carries only API-required fields; the
        human-readable "meta" lives on serialize_batch_for_display (descriptions,
        transaction count, multisend flag). This test preserves the original
        intent by asserting those fields on the display helper."""
        display = serialize_batch_for_display(sample_safe_transaction)
        assert "operations" in display  # descriptions
        assert "operation_count" in display  # transactionCount
        assert "type" in display  # single vs multisend indicator
        assert display["type"] in ("Single", "MultiSend")

    def test_nonce_included(self):
        """Test that nonce is included when set."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            nonce=42,
        )
        serialized = serialize_for_safe_api(tx)
        assert serialized["nonce"] == 42


class TestSerializeBatchForDisplay:
    """Tests for serialize_batch_for_display function."""

    def test_single_tx_display(self, sample_safe_transaction):
        """Test display serialization for single transaction."""
        display = serialize_batch_for_display(sample_safe_transaction)

        assert display["type"] == "Single"
        assert display["target"] == sample_safe_transaction.to
        assert display["operation_count"] == 1

    def test_multisend_display(self):
        """Test display serialization for multisend transaction."""
        tx = SafeTransaction(
            to="0x1234567890123456789012345678901234567890",
            data=b"\x00" * 100,
            safe_tx_gas=500_000,
            descriptions=["Op 1", "Op 2", "Op 3"],
        )
        display = serialize_batch_for_display(tx)

        assert display["type"] == "MultiSend"
        assert display["operation_count"] == 3
        assert display["estimated_gas"] == 500_000
        assert len(display["operations"]) == 3

    def test_data_size_included(self, sample_safe_transaction):
        """Test that data size is included in display."""
        display = serialize_batch_for_display(sample_safe_transaction)
        assert display["data_size_bytes"] == len(sample_safe_transaction.data)


# ============================================================================
# Test ProposeToSafe
# ============================================================================


class TestProposeToSafe:
    """Tests for ProposeToSafe class."""

    def test_init_with_known_chain(self):
        """Test initialization with known chain ID."""
        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=1,
        )
        assert proposer.safe_address == "0x1111111111111111111111111111111111111111"
        assert proposer.chain_id == 1
        assert "mainnet" in proposer.api_url

    def test_init_with_custom_url(self):
        """Test initialization with custom API URL."""
        custom_url = "https://custom.safe.service"
        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=999,  # Unknown chain
            api_url=custom_url,
        )
        assert proposer.api_url == custom_url

    def test_init_unknown_chain_no_url_raises(self):
        """Test that unknown chain without URL raises ValueError."""
        with pytest.raises(ValueError, match="No Safe Transaction Service URL"):
            ProposeToSafe(
                safe_address="0x1111111111111111111111111111111111111111",
                chain_id=999,
            )

    def test_get_next_nonce_respects_env_override(self, monkeypatch):
        """With SAFE_PROPOSAL_START_NONCE set, no live API call is made.

        V1 expected `get_next_nonce()` to work with any safe address (stub).
        V3 actually fetches from the Safe Transaction Service, which requires a
        real Safe and network access. The production path for users without
        network access is to set SAFE_PROPOSAL_START_NONCE in .env; this test
        verifies that override mechanism without hitting the network.
        """
        monkeypatch.setenv("SAFE_PROPOSAL_START_NONCE", "42")
        monkeypatch.delenv("PROPOSER_PRIVATE_KEY", raising=False)
        monkeypatch.delenv("PROPOSER_ADDRESS", raising=False)

        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=1,
            signer_address="0x2222222222222222222222222222222222222222",
        )
        proposer._resolve_initial_nonce()
        assert proposer._next_nonce == 42

    def test_propose_batch_stubbed(self, sample_safe_transaction, monkeypatch):
        """Without a signing key, propose_batch returns a stubbed dict rather than
        POSTing to the Safe API. Uses env nonce override so no network call runs."""
        monkeypatch.setenv("SAFE_PROPOSAL_START_NONCE", "7")
        monkeypatch.delenv("PROPOSER_PRIVATE_KEY", raising=False)
        monkeypatch.delenv("PROPOSER_ADDRESS", raising=False)

        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=1,
            signer_address="0x2222222222222222222222222222222222222222",
        )
        result = proposer.propose_batch(sample_safe_transaction)

        assert result["status"] == "stubbed"
        assert "safe_address" in result
        assert "transaction_data" in result

    def test_propose_batch_requires_sender(self, sample_safe_transaction, monkeypatch):
        """propose_batch raises ValueError when no sender is configured."""
        monkeypatch.setenv("SAFE_PROPOSAL_START_NONCE", "0")
        monkeypatch.delenv("PROPOSER_PRIVATE_KEY", raising=False)
        monkeypatch.delenv("PROPOSER_ADDRESS", raising=False)

        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=1,
        )
        assert proposer.signer_address is None, (
            "Test requires an environment without PROPOSER_ADDRESS set"
        )
        with pytest.raises(ValueError, match="Sender address required"):
            proposer.propose_batch(sample_safe_transaction)

    def test_propose_batch_sets_nonce(self, sample_safe_transaction, monkeypatch):
        """propose_batch populates nonce from the env override and increments it."""
        monkeypatch.setenv("SAFE_PROPOSAL_START_NONCE", "13")
        monkeypatch.delenv("PROPOSER_PRIVATE_KEY", raising=False)
        monkeypatch.delenv("PROPOSER_ADDRESS", raising=False)

        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=1,
            signer_address="0x2222222222222222222222222222222222222222",
        )
        assert sample_safe_transaction.nonce is None
        result = proposer.propose_batch(sample_safe_transaction)
        assert result["nonce"] == 13
        assert proposer._next_nonce == 14  # advanced past this tx

    def test_propose_all_batches(self, sample_safe_transaction, monkeypatch):
        """propose_all_batches handles multiple transactions, advancing the nonce each time."""
        monkeypatch.setenv("SAFE_PROPOSAL_START_NONCE", "100")
        monkeypatch.delenv("PROPOSER_PRIVATE_KEY", raising=False)
        monkeypatch.delenv("PROPOSER_ADDRESS", raising=False)

        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=1,
            signer_address="0x2222222222222222222222222222222222222222",
        )
        tx2 = SafeTransaction(
            to="0x9999999999999999999999999999999999999999",
            descriptions=["Second tx"],
        )
        results = proposer.propose_all_batches([sample_safe_transaction, tx2])
        assert len(results) == 2
        assert results[0]["nonce"] == 100
        assert results[1]["nonce"] == 101


# ============================================================================
# Test Safe Transaction Hash
# ============================================================================


class TestComputeSafeTxHash:
    """Tests for compute_safe_tx_hash function."""

    def test_returns_32_bytes(self, sample_safe_transaction):
        """Test that hash is 32 bytes."""
        sample_safe_transaction.nonce = 0
        tx_hash = compute_safe_tx_hash(
            safe_address="0x1111111111111111111111111111111111111111",
            safe_tx=sample_safe_transaction,
            chain_id=1,
        )
        assert len(tx_hash) == 32

    def test_different_nonces_different_hashes(self, sample_safe_transaction):
        """Test that different nonces produce different hashes."""
        sample_safe_transaction.nonce = 0
        hash1 = compute_safe_tx_hash(
            safe_address="0x1111111111111111111111111111111111111111",
            safe_tx=sample_safe_transaction,
            chain_id=1,
        )

        sample_safe_transaction.nonce = 1
        hash2 = compute_safe_tx_hash(
            safe_address="0x1111111111111111111111111111111111111111",
            safe_tx=sample_safe_transaction,
            chain_id=1,
        )

        assert hash1 != hash2

    def test_different_chains_different_hashes(self, sample_safe_transaction):
        """Test that different chain IDs produce different hashes."""
        sample_safe_transaction.nonce = 0

        hash1 = compute_safe_tx_hash(
            safe_address="0x1111111111111111111111111111111111111111",
            safe_tx=sample_safe_transaction,
            chain_id=1,
        )

        hash2 = compute_safe_tx_hash(
            safe_address="0x1111111111111111111111111111111111111111",
            safe_tx=sample_safe_transaction,
            chain_id=10,
        )

        assert hash1 != hash2

    def test_deterministic(self, sample_safe_transaction):
        """Test that same inputs produce same hash."""
        sample_safe_transaction.nonce = 0

        hash1 = compute_safe_tx_hash(
            safe_address="0x1111111111111111111111111111111111111111",
            safe_tx=sample_safe_transaction,
            chain_id=1,
        )

        hash2 = compute_safe_tx_hash(
            safe_address="0x1111111111111111111111111111111111111111",
            safe_tx=sample_safe_transaction,
            chain_id=1,
        )

        assert hash1 == hash2


# ============================================================================
# Test MultiSend Addresses
# ============================================================================


class TestMultisendAddresses:
    """Tests for MultiSend address constants."""

    def test_mainnet_address(self):
        """Test Mainnet MultiSend address is valid."""
        assert MULTISEND_ADDRESSES[1].startswith("0x")
        assert len(MULTISEND_ADDRESSES[1]) == 42

    def test_optimism_address(self):
        """Test Optimism MultiSend address is valid."""
        assert MULTISEND_ADDRESSES[10].startswith("0x")
        assert len(MULTISEND_ADDRESSES[10]) == 42

    def test_arbitrum_address(self):
        """Test Arbitrum MultiSend address is valid."""
        assert MULTISEND_ADDRESSES[42161].startswith("0x")
        assert len(MULTISEND_ADDRESSES[42161]) == 42


# ============================================================================
# Test Integration
# ============================================================================


class TestIntegration:
    """Integration tests for the Safe module."""

    def test_full_workflow(self, sample_transaction_calls):
        """Complete workflow from TransactionCalls → SafeTransaction → API payload.

        V3 split: API payload is lean; the multisend-metadata is surfaced via the
        separate serialize_batch_for_display helper. Both halves of the intent
        are asserted below.
        """
        batch = TransactionBatch(batch_number=1)
        for call in sample_transaction_calls:
            batch.add_call(call)

        safe_tx = convert_batch_to_safe_tx(batch, chain_id=1)
        serialized = serialize_for_safe_api(safe_tx)

        # API-required fields.
        assert "to" in serialized
        assert "data" in serialized
        assert serialized["data"].startswith("0x")
        assert "safeTxGas" in serialized

        # Human-readable metadata (the V1 _meta block) now lives on the display helper.
        display = serialize_batch_for_display(safe_tx)
        assert display["type"] == "MultiSend"
        assert display["operation_count"] == 3

    def test_format_and_propose(self, sample_transaction_calls, monkeypatch):
        """End-to-end: format batches and propose via the stubbed (no-key) path."""
        monkeypatch.setenv("SAFE_PROPOSAL_START_NONCE", "0")
        monkeypatch.delenv("PROPOSER_PRIVATE_KEY", raising=False)
        monkeypatch.delenv("PROPOSER_ADDRESS", raising=False)

        batch = TransactionBatch(batch_number=1)
        for call in sample_transaction_calls:
            batch.add_call(call)

        safe_txs = format_safe_batch([batch], chain_id=1)
        proposer = ProposeToSafe(
            safe_address="0x1111111111111111111111111111111111111111",
            chain_id=1,
            signer_address="0x2222222222222222222222222222222222222222",
        )
        results = proposer.propose_all_batches(safe_txs)

        assert len(results) == 1
        assert results[0]["status"] == "stubbed"
