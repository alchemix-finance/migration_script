"""Tests for data types module (V3).

V1 CSV schema was per-row usd_debt/eth_debt mixed; V3 splits into one CSV per
chain+asset with columns `underlyingValue,debt`. V1 PositionMigration had
`deposit_amount`/`mint_amount`; V3 renamed to `*_wei` for clarity. V1
MigrationSummary had `usd_positions`/`eth_positions`; V3 tracks separate
per-asset debt/credit counts at the ValidationResult level.

These tests preserve the original intent (enum shapes, dataclass validation,
batch gas accumulation, error formatting) against the current schema.
"""

from decimal import Decimal

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
    def test_asset_type_values(self) -> None:
        assert AssetType.USD.value == "USD"
        assert AssetType.ETH.value == "ETH"

    def test_asset_type_string_comparison(self) -> None:
        assert AssetType.USD == "USD"
        assert AssetType.ETH == "ETH"


class TestChainName:
    def test_chain_name_values(self) -> None:
        assert ChainName.MAINNET.value == "mainnet"
        assert ChainName.OPTIMISM.value == "optimism"
        assert ChainName.ARBITRUM.value == "arbitrum"


class TestPositionMigration:
    """V3 signature: deposit_amount_wei, mint_amount_wei, credit_amount_wei. No standalone token_id validation."""

    def test_valid_position(self) -> None:
        position = PositionMigration(
            user_address="0x1234567890123456789012345678901234567890",
            asset_type=AssetType.USD,
            chain="mainnet",
            deposit_amount_wei=1_000_000_000_000_000_000,
            mint_amount_wei=500_000_000_000_000_000,
            credit_amount_wei=0,
            token_id=0,
        )
        assert position.user_address == "0x1234567890123456789012345678901234567890"
        assert position.asset_type == AssetType.USD
        assert position.token_id == 0
        assert position.is_debt_user is True
        assert position.is_credit_user is False

    def test_credit_user_position(self) -> None:
        position = PositionMigration(
            user_address="0x1234567890123456789012345678901234567890",
            asset_type=AssetType.USD,
            chain="mainnet",
            deposit_amount_wei=1_000_000_000_000_000_000,
            mint_amount_wei=0,
            credit_amount_wei=100_000_000_000_000_000,
        )
        assert position.is_credit_user is True
        assert position.is_debt_user is False
        assert position.needs_burn is False

    def test_invalid_address_format(self) -> None:
        with pytest.raises(ValueError, match="Invalid address"):
            PositionMigration(
                user_address="invalid",
                asset_type=AssetType.USD,
                chain="mainnet",
                deposit_amount_wei=1000,
                mint_amount_wei=500,
                credit_amount_wei=0,
            )

    def test_negative_deposit_rejected(self) -> None:
        with pytest.raises(ValueError, match="deposit_amount_wei cannot be negative"):
            PositionMigration(
                user_address="0x1234567890123456789012345678901234567890",
                asset_type=AssetType.USD,
                chain="mainnet",
                deposit_amount_wei=-1000,
                mint_amount_wei=0,
                credit_amount_wei=0,
            )

    def test_negative_mint_rejected(self) -> None:
        with pytest.raises(ValueError, match="mint_amount_wei cannot be negative"):
            PositionMigration(
                user_address="0x1234567890123456789012345678901234567890",
                asset_type=AssetType.USD,
                chain="mainnet",
                deposit_amount_wei=1000,
                mint_amount_wei=-500,
                credit_amount_wei=0,
            )

    def test_negative_credit_rejected(self) -> None:
        with pytest.raises(ValueError, match="credit_amount_wei cannot be negative"):
            PositionMigration(
                user_address="0x1234567890123456789012345678901234567890",
                asset_type=AssetType.USD,
                chain="mainnet",
                deposit_amount_wei=1000,
                mint_amount_wei=0,
                credit_amount_wei=-1,
            )


class TestCSVRow:
    """V3 CSVRow schema: address, underlying_value, debt. One CSV per chain+asset."""

    def test_has_position_true(self) -> None:
        row = CSVRow(
            address="0x1234567890123456789012345678901234567890",
            underlying_value=Decimal("5000.0"),
            debt=Decimal("1000.0"),
            row_number=1,
        )
        assert row.has_position is True
        assert row.is_credit_user is False
        assert row.credit_amount == Decimal(0)

    def test_has_position_false(self) -> None:
        row = CSVRow(
            address="0x1234567890123456789012345678901234567890",
            underlying_value=Decimal("0"),
            debt=Decimal("0"),
            row_number=2,
        )
        assert row.has_position is False

    def test_credit_user_detected(self) -> None:
        row = CSVRow(
            address="0x1234567890123456789012345678901234567890",
            underlying_value=Decimal("5000.0"),
            debt=Decimal("-25.0"),
            row_number=3,
        )
        assert row.is_credit_user is True
        assert row.credit_amount == Decimal("25.0")


class TestTransactionBatch:
    def test_add_call(self) -> None:
        batch = TransactionBatch(batch_number=1)
        call = TransactionCall(
            to="0x1234567890123456789012345678901234567890",
            data=b"",
            gas_estimate=100_000,
            description="test call",
        )
        batch.add_call(call)
        assert len(batch.calls) == 1
        assert batch.total_gas == 100_000

    def test_add_multiple_calls_accumulates_gas(self) -> None:
        batch = TransactionBatch(batch_number=1)
        batch.add_call(TransactionCall(to="0x1", data=b"", gas_estimate=100_000))
        batch.add_call(TransactionCall(to="0x2", data=b"", gas_estimate=200_000))
        batch.add_call(TransactionCall(to="0x3", data=b"", gas_estimate=150_000))
        assert len(batch.calls) == 3
        assert batch.total_gas == 450_000


class TestMigrationSummary:
    """V3 MigrationSummary fields: chain, asset_type, total_positions, debt_users,
    credit_users, zero_debt_users, total_deposit_wei, total_mint_wei, total_credit_wei,
    total_burn_wei, total_batches, errors."""

    def _mk_summary(self, **overrides) -> MigrationSummary:
        kwargs = dict(
            chain="mainnet",
            asset_type="USD",
            total_positions=10,
            debt_users=5,
            credit_users=3,
            zero_debt_users=2,
            total_deposit_wei=10**21,
            total_mint_wei=5 * 10**20,
            total_credit_wei=10**20,
            total_burn_wei=4 * 10**20,
            total_batches=2,
        )
        kwargs.update(overrides)
        return MigrationSummary(**kwargs)

    def test_has_errors_false(self) -> None:
        summary = self._mk_summary()
        assert summary.has_errors is False

    def test_has_errors_true(self) -> None:
        summary = self._mk_summary(errors=["Some error occurred"])
        assert summary.has_errors is True


class TestValidationError:
    def test_str_without_value(self) -> None:
        error = ValidationError(row_number=5, field_name="address", message="Invalid format")
        assert str(error) == "Row 5, field 'address': Invalid format"

    def test_str_with_value(self) -> None:
        error = ValidationError(
            row_number=5, field_name="address", message="Invalid format", value="bad_address",
        )
        assert str(error) == "Row 5, field 'address': Invalid format (got: 'bad_address')"
