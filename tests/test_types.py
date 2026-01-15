"""Tests for data types module."""

import pytest
from src.types import (
    AssetType,
    ChainName,
    CSVRow,
    MigrationSummary,
    PositionMigration,
    TransactionBatch,
    TransactionCall,
    ValidationError,
)


class TestAssetType:
    """Tests for AssetType enum."""

    def test_asset_type_values(self) -> None:
        """Test asset type enum values."""
        assert AssetType.USD.value == "USD"
        assert AssetType.ETH.value == "ETH"

    def test_asset_type_string_comparison(self) -> None:
        """Test that asset types can be compared with strings."""
        assert AssetType.USD == "USD"
        assert AssetType.ETH == "ETH"


class TestChainName:
    """Tests for ChainName enum."""

    def test_chain_name_values(self) -> None:
        """Test chain name enum values."""
        assert ChainName.MAINNET.value == "mainnet"
        assert ChainName.OPTIMISM.value == "optimism"
        assert ChainName.ARBITRUM.value == "arbitrum"


class TestPositionMigration:
    """Tests for PositionMigration dataclass."""

    def test_valid_position(self) -> None:
        """Test creating a valid position."""
        position = PositionMigration(
            user_address="0x1234567890123456789012345678901234567890",
            asset_type="USD",
            token_id=0,
            deposit_amount=1000000000000000000,
            mint_amount=500000000000000000,
            chain="mainnet",
        )
        assert position.user_address == "0x1234567890123456789012345678901234567890"
        assert position.asset_type == "USD"
        assert position.token_id == 0

    def test_invalid_address_format(self) -> None:
        """Test that invalid address raises ValueError."""
        with pytest.raises(ValueError, match="Invalid address format"):
            PositionMigration(
                user_address="invalid",
                asset_type="USD",
                token_id=0,
                deposit_amount=1000,
                mint_amount=500,
                chain="mainnet",
            )

    def test_negative_deposit_amount(self) -> None:
        """Test that negative deposit raises ValueError."""
        with pytest.raises(ValueError, match="Deposit amount cannot be negative"):
            PositionMigration(
                user_address="0x1234567890123456789012345678901234567890",
                asset_type="USD",
                token_id=0,
                deposit_amount=-1000,
                mint_amount=500,
                chain="mainnet",
            )

    def test_negative_mint_amount(self) -> None:
        """Test that negative mint raises ValueError."""
        with pytest.raises(ValueError, match="Mint amount cannot be negative"):
            PositionMigration(
                user_address="0x1234567890123456789012345678901234567890",
                asset_type="USD",
                token_id=0,
                deposit_amount=1000,
                mint_amount=-500,
                chain="mainnet",
            )

    def test_negative_token_id(self) -> None:
        """Test that negative token ID raises ValueError."""
        with pytest.raises(ValueError, match="Token ID cannot be negative"):
            PositionMigration(
                user_address="0x1234567890123456789012345678901234567890",
                asset_type="USD",
                token_id=-1,
                deposit_amount=1000,
                mint_amount=500,
                chain="mainnet",
            )


class TestCSVRow:
    """Tests for CSVRow dataclass."""

    def test_has_usd_position(self) -> None:
        """Test USD position detection."""
        row = CSVRow(
            address="0x123",
            usd_debt=1000.0,
            usd_underlying_value=5000.0,
            eth_debt=0.0,
            eth_underlying_value=0.0,
            row_number=1,
        )
        assert row.has_usd_position is True
        assert row.has_eth_position is False

    def test_has_eth_position(self) -> None:
        """Test ETH position detection."""
        row = CSVRow(
            address="0x123",
            usd_debt=0.0,
            usd_underlying_value=0.0,
            eth_debt=0.5,
            eth_underlying_value=2.0,
            row_number=1,
        )
        assert row.has_usd_position is False
        assert row.has_eth_position is True

    def test_has_both_positions(self) -> None:
        """Test detecting both positions."""
        row = CSVRow(
            address="0x123",
            usd_debt=1000.0,
            usd_underlying_value=5000.0,
            eth_debt=0.5,
            eth_underlying_value=2.0,
            row_number=1,
        )
        assert row.has_usd_position is True
        assert row.has_eth_position is True


class TestTransactionBatch:
    """Tests for TransactionBatch dataclass."""

    def test_add_call(self) -> None:
        """Test adding a call to a batch."""
        batch = TransactionBatch(batch_number=1)
        call = TransactionCall(
            to="0x123",
            data=b"",
            gas_estimate=100000,
            description="test call",
        )
        batch.add_call(call)
        assert len(batch.calls) == 1
        assert batch.total_gas == 100000

    def test_add_multiple_calls(self) -> None:
        """Test adding multiple calls accumulates gas."""
        batch = TransactionBatch(batch_number=1)
        batch.add_call(TransactionCall(to="0x1", data=b"", gas_estimate=100000))
        batch.add_call(TransactionCall(to="0x2", data=b"", gas_estimate=200000))
        batch.add_call(TransactionCall(to="0x3", data=b"", gas_estimate=150000))
        assert len(batch.calls) == 3
        assert batch.total_gas == 450000


class TestMigrationSummary:
    """Tests for MigrationSummary dataclass."""

    def test_has_errors_false(self) -> None:
        """Test has_errors when no errors."""
        summary = MigrationSummary(
            chain="mainnet",
            total_positions=10,
            usd_positions=5,
            eth_positions=5,
            total_batches=2,
            total_transactions=30,
        )
        assert summary.has_errors is False

    def test_has_errors_true(self) -> None:
        """Test has_errors when errors present."""
        summary = MigrationSummary(
            chain="mainnet",
            total_positions=10,
            usd_positions=5,
            eth_positions=5,
            total_batches=2,
            total_transactions=30,
            errors=["Some error occurred"],
        )
        assert summary.has_errors is True


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_str_without_value(self) -> None:
        """Test string representation without value."""
        error = ValidationError(
            row_number=5,
            field_name="address",
            message="Invalid format",
        )
        expected = "Row 5, field 'address': Invalid format"
        assert str(error) == expected

    def test_str_with_value(self) -> None:
        """Test string representation with value."""
        error = ValidationError(
            row_number=5,
            field_name="address",
            message="Invalid format",
            value="bad_address",
        )
        expected = "Row 5, field 'address': Invalid format (got: 'bad_address')"
        assert str(error) == expected
