"""Unit tests for gas estimation and batching logic."""

import pytest

from src.gas import (
    BASE_GAS_DEPOSIT,
    BASE_GAS_MINT,
    BASE_GAS_TRANSFER,
    EFFECTIVE_GAS_LIMIT,
    GAS_BUFFER,
    GAS_LIMIT,
    GAS_PER_LARGE_POSITION,
    LARGE_POSITION_THRESHOLD,
    OperationType,
    _greedy_bin_pack,
    calculate_batch_statistics,
    create_batches,
    estimate_deposit_gas,
    estimate_mint_gas,
    estimate_position_total_gas,
    estimate_transfer_gas,
    format_batch_summary,
    verify_batch_gas_limits,
)
from src.types import PositionMigration, TransactionBatch, TransactionCall


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_position() -> PositionMigration:
    """Create a sample position for testing (below large position threshold)."""
    return PositionMigration(
        user_address="0xAAA0000000000000000000000000000000000001",
        asset_type="USD",
        token_id=0,
        deposit_amount=500 * 10**18,  # 500 tokens (below 1000 threshold)
        mint_amount=100 * 10**18,  # 100 tokens debt (below threshold)
        chain="mainnet",
    )


@pytest.fixture
def large_position() -> PositionMigration:
    """Create a large position that exceeds the threshold."""
    return PositionMigration(
        user_address="0xBBB0000000000000000000000000000000000002",
        asset_type="ETH",
        token_id=0,
        deposit_amount=2000 * 10**18,  # 2000 tokens (above 1000 threshold)
        mint_amount=1500 * 10**18,  # 1500 tokens debt (above threshold)
        chain="mainnet",
    )


@pytest.fixture
def small_position() -> PositionMigration:
    """Create a small position below the threshold."""
    return PositionMigration(
        user_address="0xCCC0000000000000000000000000000000000003",
        asset_type="USD",
        token_id=1,
        deposit_amount=100 * 10**18,  # 100 tokens
        mint_amount=50 * 10**18,  # 50 tokens debt
        chain="mainnet",
    )


@pytest.fixture
def multiple_positions() -> list[PositionMigration]:
    """Create multiple positions for batch testing."""
    positions = []
    for i in range(10):
        positions.append(
            PositionMigration(
                user_address=f"0x{'A' * 3}{i:037d}",
                asset_type="USD" if i % 2 == 0 else "ETH",
                token_id=i // 2,  # Token IDs are per asset type
                deposit_amount=(1000 + i * 100) * 10**18,
                mint_amount=(500 + i * 50) * 10**18,
                chain="mainnet",
            )
        )
    return positions


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
# Test Constants
# ============================================================================


class TestGasConstants:
    """Test gas-related constants are correctly defined."""

    def test_gas_limit_is_16m(self):
        """Gas limit should be 16 million."""
        assert GAS_LIMIT == 16_000_000

    def test_gas_buffer_is_95_percent(self):
        """Gas buffer should provide 5% headroom (0.95)."""
        assert GAS_BUFFER == 0.95

    def test_effective_gas_limit(self):
        """Effective gas limit should be 16M * 0.95 = 15.2M."""
        assert EFFECTIVE_GAS_LIMIT == int(16_000_000 * 0.95)
        assert EFFECTIVE_GAS_LIMIT == 15_200_000

    def test_base_gas_values_are_reasonable(self):
        """Base gas values should be in reasonable ranges."""
        # Deposit is most expensive (creates storage)
        assert 100_000 <= BASE_GAS_DEPOSIT <= 300_000
        # Mint is medium (updates storage)
        assert 80_000 <= BASE_GAS_MINT <= 200_000
        # Transfer is cheapest (simple ownership change)
        assert 40_000 <= BASE_GAS_TRANSFER <= 100_000
        # Order should be: deposit > mint > transfer
        assert BASE_GAS_DEPOSIT > BASE_GAS_MINT > BASE_GAS_TRANSFER


# ============================================================================
# Test Gas Estimation Functions
# ============================================================================


class TestEstimateDepositGas:
    """Tests for deposit gas estimation."""

    def test_small_deposit_returns_base_gas(self, sample_position):
        """Small deposits should use base gas only."""
        gas = estimate_deposit_gas(sample_position)
        assert gas == BASE_GAS_DEPOSIT

    def test_large_deposit_adds_extra_gas(self, large_position):
        """Large deposits should add extra gas."""
        gas = estimate_deposit_gas(large_position)
        assert gas == BASE_GAS_DEPOSIT + GAS_PER_LARGE_POSITION

    def test_threshold_boundary(self):
        """Test behavior at exact threshold."""
        # Just below threshold
        below = PositionMigration(
            user_address="0xAAA0000000000000000000000000000000000001",
            asset_type="USD",
            token_id=0,
            deposit_amount=LARGE_POSITION_THRESHOLD - 1,
            mint_amount=0,
            chain="mainnet",
        )
        assert estimate_deposit_gas(below) == BASE_GAS_DEPOSIT

        # At threshold
        at_threshold = PositionMigration(
            user_address="0xAAA0000000000000000000000000000000000001",
            asset_type="USD",
            token_id=0,
            deposit_amount=LARGE_POSITION_THRESHOLD,
            mint_amount=0,
            chain="mainnet",
        )
        assert estimate_deposit_gas(at_threshold) == BASE_GAS_DEPOSIT + GAS_PER_LARGE_POSITION


class TestEstimateMintGas:
    """Tests for mint gas estimation."""

    def test_small_mint_returns_base_gas(self, sample_position):
        """Small mints should use base gas only."""
        gas = estimate_mint_gas(sample_position)
        assert gas == BASE_GAS_MINT

    def test_large_mint_adds_extra_gas(self, large_position):
        """Large mints should add extra gas."""
        gas = estimate_mint_gas(large_position)
        assert gas == BASE_GAS_MINT + GAS_PER_LARGE_POSITION

    def test_zero_mint_amount(self):
        """Zero mint amount should still return base gas."""
        position = PositionMigration(
            user_address="0xAAA0000000000000000000000000000000000001",
            asset_type="USD",
            token_id=0,
            deposit_amount=1000 * 10**18,
            mint_amount=0,
            chain="mainnet",
        )
        assert estimate_mint_gas(position) == BASE_GAS_MINT


class TestEstimateTransferGas:
    """Tests for NFT transfer gas estimation."""

    def test_transfer_returns_base_gas(self, sample_position):
        """All transfers should return base gas (constant)."""
        gas = estimate_transfer_gas(sample_position)
        assert gas == BASE_GAS_TRANSFER

    def test_transfer_gas_is_constant(self, large_position, small_position):
        """Transfer gas should be the same regardless of position size."""
        assert estimate_transfer_gas(large_position) == estimate_transfer_gas(small_position)
        assert estimate_transfer_gas(large_position) == BASE_GAS_TRANSFER


class TestEstimatePositionTotalGas:
    """Tests for total position gas estimation."""

    def test_total_gas_sums_all_operations(self, sample_position):
        """Total gas should sum deposit + mint + transfer."""
        total = estimate_position_total_gas(sample_position)
        expected = (
            estimate_deposit_gas(sample_position)
            + estimate_mint_gas(sample_position)
            + estimate_transfer_gas(sample_position)
        )
        assert total == expected

    def test_large_position_total_gas(self, large_position):
        """Large positions should include extra gas for both deposit and mint."""
        total = estimate_position_total_gas(large_position)
        expected = (
            BASE_GAS_DEPOSIT
            + GAS_PER_LARGE_POSITION  # Extra for large deposit
            + BASE_GAS_MINT
            + GAS_PER_LARGE_POSITION  # Extra for large mint
            + BASE_GAS_TRANSFER
        )
        assert total == expected


# ============================================================================
# Test Greedy Bin-Packing Algorithm
# ============================================================================


class TestGreedyBinPack:
    """Tests for the greedy bin-packing algorithm."""

    def test_empty_list_returns_empty(self):
        """Empty input should return empty output."""
        result = _greedy_bin_pack([])
        assert result == []

    def test_single_call_creates_single_batch(self):
        """Single call should create single batch."""
        call = TransactionCall(
            to="0x1234567890123456789012345678901234567890",
            data=b"",
            gas_estimate=100_000,
        )
        result = _greedy_bin_pack([call])
        assert len(result) == 1
        assert len(result[0].calls) == 1
        assert result[0].batch_number == 1

    def test_calls_fit_in_one_batch(self):
        """Calls that fit should be in one batch."""
        calls = [
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=1_000_000)
            for _ in range(5)
        ]
        result = _greedy_bin_pack(calls, gas_limit=10_000_000)
        assert len(result) == 1
        assert len(result[0].calls) == 5
        assert result[0].total_gas == 5_000_000

    def test_calls_split_across_batches(self):
        """Calls exceeding limit should split into multiple batches."""
        calls = [
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=5_000_000)
            for _ in range(5)
        ]
        result = _greedy_bin_pack(calls, gas_limit=10_000_000)
        # 5 calls at 5M each = 25M total, limit is 10M
        # Should create 3 batches: [2, 2, 1] calls
        assert len(result) == 3
        assert len(result[0].calls) == 2  # 10M
        assert len(result[1].calls) == 2  # 10M
        assert len(result[2].calls) == 1  # 5M

    def test_batch_numbers_are_sequential(self):
        """Batch numbers should be sequential starting from 1."""
        calls = [
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=5_000_000)
            for _ in range(10)
        ]
        result = _greedy_bin_pack(calls, gas_limit=10_000_000)
        for i, batch in enumerate(result):
            assert batch.batch_number == i + 1

    def test_greedy_packs_tightly(self):
        """Greedy should pack calls tightly up to limit."""
        # Create calls of varying sizes
        calls = [
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=4_000_000),
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=4_000_000),
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=3_000_000),
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=5_000_000),
        ]
        result = _greedy_bin_pack(calls, gas_limit=10_000_000)
        # First batch: 4M + 4M = 8M (can't add 3M, would be 11M > 10M)
        # Second batch: 3M + 5M = 8M
        assert len(result) == 2
        assert result[0].total_gas == 8_000_000
        assert result[1].total_gas == 8_000_000

    def test_single_large_call_gets_own_batch(self):
        """A call that nearly fills a batch should be alone."""
        calls = [
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=9_500_000),
            TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=1_000_000),
        ]
        result = _greedy_bin_pack(calls, gas_limit=10_000_000)
        assert len(result) == 2
        assert len(result[0].calls) == 1
        assert len(result[1].calls) == 1


# ============================================================================
# Test Create Batches Function
# ============================================================================


class TestCreateBatches:
    """Tests for the main create_batches function."""

    def test_empty_positions_returns_empty(self, sample_chain_config):
        """Empty positions list should return empty batches."""
        result = create_batches([], "mainnet", sample_chain_config)
        assert result == []

    def test_single_position_creates_transactions(self, sample_position, sample_chain_config):
        """Single position should create deposit, mint, transfer transactions."""
        result = create_batches([sample_position], "mainnet", sample_chain_config)
        # All three txns should fit in one batch
        total_txns = sum(len(b.calls) for b in result)
        assert total_txns == 3  # deposit + mint + transfer

    def test_transaction_order_deposits_mints_transfers(
        self, multiple_positions, sample_chain_config
    ):
        """Transactions should be ordered: all deposits, then mints, then transfers."""
        result = create_batches(multiple_positions, "mainnet", sample_chain_config)

        # Collect all transaction descriptions
        all_descriptions = []
        for batch in result:
            for call in batch.calls:
                all_descriptions.append(call.description)

        n_positions = len(multiple_positions)

        # First n should be deposits
        for i in range(n_positions):
            assert "deposit" in all_descriptions[i].lower(), f"Expected deposit at index {i}"

        # Next n should be mints
        for i in range(n_positions, 2 * n_positions):
            assert "mint" in all_descriptions[i].lower(), f"Expected mint at index {i}"

        # Last n should be transfers
        for i in range(2 * n_positions, 3 * n_positions):
            assert "transfer" in all_descriptions[i].lower(), f"Expected transfer at index {i}"

    def test_batches_respect_gas_limit(self, sample_chain_config):
        """All batches should be under the gas limit."""
        # Create many positions to force multiple batches
        positions = [
            PositionMigration(
                user_address=f"0x{'A' * 3}{i:037d}",
                asset_type="USD",
                token_id=i,
                deposit_amount=1000 * 10**18,
                mint_amount=500 * 10**18,
                chain="mainnet",
            )
            for i in range(100)
        ]
        result = create_batches(positions, "mainnet", sample_chain_config)

        for batch in result:
            assert batch.total_gas <= EFFECTIVE_GAS_LIMIT, (
                f"Batch {batch.batch_number} exceeds gas limit: "
                f"{batch.total_gas} > {EFFECTIVE_GAS_LIMIT}"
            )

    def test_uses_correct_contract_addresses(self, sample_chain_config):
        """Transactions should use correct contract addresses for asset type."""
        usd_position = PositionMigration(
            user_address="0xAAA0000000000000000000000000000000000001",
            asset_type="USD",
            token_id=0,
            deposit_amount=1000 * 10**18,
            mint_amount=500 * 10**18,
            chain="mainnet",
        )
        eth_position = PositionMigration(
            user_address="0xBBB0000000000000000000000000000000000002",
            asset_type="ETH",
            token_id=0,
            deposit_amount=1000 * 10**18,
            mint_amount=500 * 10**18,
            chain="mainnet",
        )

        result = create_batches(
            [usd_position, eth_position], "mainnet", sample_chain_config
        )

        # Check that addresses are used correctly
        all_calls = [call for batch in result for call in batch.calls]

        # Deposits (first 2 calls)
        assert all_calls[0].to == sample_chain_config["cdp_usd"]  # USD deposit
        assert all_calls[1].to == sample_chain_config["cdp_eth"]  # ETH deposit

        # Mints (next 2 calls)
        assert all_calls[2].to == sample_chain_config["cdp_usd"]  # USD mint
        assert all_calls[3].to == sample_chain_config["cdp_eth"]  # ETH mint

        # Transfers (last 2 calls)
        assert all_calls[4].to == sample_chain_config["nft_usd"]  # USD transfer
        assert all_calls[5].to == sample_chain_config["nft_eth"]  # ETH transfer


# ============================================================================
# Test Batch Statistics and Verification
# ============================================================================


class TestCalculateBatchStatistics:
    """Tests for batch statistics calculation."""

    def test_empty_batches_returns_zeros(self):
        """Empty batch list should return zero statistics."""
        stats = calculate_batch_statistics([])
        assert stats["total_batches"] == 0
        assert stats["total_transactions"] == 0
        assert stats["total_gas"] == 0

    def test_statistics_are_correct(self):
        """Statistics should be accurately calculated."""
        batch1 = TransactionBatch(batch_number=1)
        batch1.add_call(TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=100_000))
        batch1.add_call(TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=200_000))

        batch2 = TransactionBatch(batch_number=2)
        batch2.add_call(TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=300_000))

        stats = calculate_batch_statistics([batch1, batch2])

        assert stats["total_batches"] == 2
        assert stats["total_transactions"] == 3
        assert stats["total_gas"] == 600_000
        assert stats["avg_gas_per_batch"] == 300_000
        assert stats["max_gas_batch"] == 300_000
        assert stats["min_gas_batch"] == 300_000


class TestVerifyBatchGasLimits:
    """Tests for batch gas limit verification."""

    def test_valid_batches_pass(self):
        """Batches under limit should pass verification."""
        batch = TransactionBatch(batch_number=1)
        batch.add_call(TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=1_000_000))

        valid, errors = verify_batch_gas_limits([batch])
        assert valid is True
        assert errors == []

    def test_over_limit_batch_fails(self):
        """Batches over limit should fail verification."""
        batch = TransactionBatch(batch_number=1)
        batch.total_gas = EFFECTIVE_GAS_LIMIT + 1

        valid, errors = verify_batch_gas_limits([batch])
        assert valid is False
        assert len(errors) == 1
        assert "exceeds gas limit" in errors[0]

    def test_custom_gas_limit(self):
        """Custom gas limit should be respected."""
        batch = TransactionBatch(batch_number=1)
        batch.total_gas = 5_000_000

        # Should pass with default limit
        valid, _ = verify_batch_gas_limits([batch])
        assert valid is True

        # Should fail with custom low limit
        valid, errors = verify_batch_gas_limits([batch], gas_limit=4_000_000)
        assert valid is False


class TestFormatBatchSummary:
    """Tests for batch summary formatting."""

    def test_formats_empty_batches(self):
        """Empty batches should format without error."""
        summary = format_batch_summary([])
        assert "BATCH SUMMARY" in summary
        assert "Total batches: 0" in summary

    def test_formats_batches_correctly(self):
        """Batches should be formatted with correct information."""
        batch = TransactionBatch(batch_number=1)
        batch.add_call(TransactionCall(to="0x" + "1" * 40, data=b"", gas_estimate=1_000_000))

        summary = format_batch_summary([batch])
        assert "BATCH SUMMARY" in summary
        assert "Total batches: 1" in summary
        assert "Batch 1:" in summary


# ============================================================================
# Integration Tests
# ============================================================================


class TestBatchingIntegration:
    """Integration tests for the full batching workflow."""

    def test_full_migration_workflow(self, sample_chain_config):
        """Test complete migration batching workflow."""
        # Create a realistic set of positions
        positions = []
        for i in range(50):
            if i % 3 == 0:
                # USD only
                positions.append(
                    PositionMigration(
                        user_address=f"0x{'A' * 3}{i:037d}",
                        asset_type="USD",
                        token_id=i // 3,
                        deposit_amount=1000 * 10**18,
                        mint_amount=500 * 10**18,
                        chain="mainnet",
                    )
                )
            elif i % 3 == 1:
                # ETH only
                positions.append(
                    PositionMigration(
                        user_address=f"0x{'B' * 3}{i:037d}",
                        asset_type="ETH",
                        token_id=i // 3,
                        deposit_amount=2 * 10**18,
                        mint_amount=1 * 10**18,
                        chain="mainnet",
                    )
                )
            else:
                # Both (two positions)
                positions.append(
                    PositionMigration(
                        user_address=f"0x{'C' * 3}{i:037d}",
                        asset_type="USD",
                        token_id=i // 3,
                        deposit_amount=500 * 10**18,
                        mint_amount=200 * 10**18,
                        chain="mainnet",
                    )
                )

        # Create batches
        batches = create_batches(positions, "mainnet", sample_chain_config)

        # Verify all batches are valid
        valid, errors = verify_batch_gas_limits(batches)
        assert valid, f"Batch verification failed: {errors}"

        # Verify transaction count
        total_txns = sum(len(b.calls) for b in batches)
        assert total_txns == len(positions) * 3  # deposit + mint + transfer per position

        # Verify statistics
        stats = calculate_batch_statistics(batches)
        assert stats["total_batches"] > 0
        assert stats["total_transactions"] == total_txns

    def test_large_migration_batching(self, sample_chain_config):
        """Test batching with a large number of positions."""
        # 500 positions should create multiple batches
        positions = [
            PositionMigration(
                user_address=f"0x{'A' * 3}{i:037d}",
                asset_type="USD" if i % 2 == 0 else "ETH",
                token_id=i // 2,
                deposit_amount=1000 * 10**18,
                mint_amount=500 * 10**18,
                chain="mainnet",
            )
            for i in range(500)
        ]

        batches = create_batches(positions, "mainnet", sample_chain_config)

        # Should create multiple batches
        assert len(batches) > 1

        # All batches should be under limit
        for batch in batches:
            assert batch.total_gas <= EFFECTIVE_GAS_LIMIT

        # Total transactions should be correct
        total_txns = sum(len(b.calls) for b in batches)
        assert total_txns == 1500  # 500 * 3
