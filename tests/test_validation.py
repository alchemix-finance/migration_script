"""Tests for CSV validation module (V3).

V1 CSV format combined USD + ETH columns per row; V3 splits into one file per
chain+asset with columns `address,underlyingValue,debt`. V1 exposed many
individual helpers; V3 keeps those helpers as public exports on
src.validation (with some renames: parse_numeric_field → parse_decimal /
parse_non_negative_decimal; create_positions_from_row → position_from_row).

These tests preserve the original intent (strict parsing, halt-on-error,
correct wei conversion, correct position mapping) against the current API.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from src.types import AssetType, CSVRow, PositionMigration, ValidationError
from src.validation import (
    CSVValidationError,
    ValidationResult,
    convert_to_wei,
    format_validation_errors,
    is_valid_eth_address,
    parse_decimal,
    parse_non_negative_decimal,
    position_from_row,
    validate_csv_file,
    validate_csv_string,
    validate_headers,
    validate_row,
)


# --- is_valid_eth_address --------------------------------------------------

class TestIsValidEthAddress:
    def test_valid_lowercase_address(self) -> None:
        assert is_valid_eth_address("0x1234567890abcdef1234567890abcdef12345678")

    def test_valid_uppercase_hex(self) -> None:
        assert is_valid_eth_address("0x1234567890ABCDEF1234567890ABCDEF12345678")

    def test_valid_mixed_case(self) -> None:
        assert is_valid_eth_address("0x1234567890AbCdEf1234567890aBcDeF12345678")

    def test_missing_0x_prefix_rejected(self) -> None:
        assert not is_valid_eth_address("1234567890abcdef1234567890abcdef12345678")

    def test_wrong_length_rejected(self) -> None:
        assert not is_valid_eth_address("0x1234")
        assert not is_valid_eth_address("0x" + "a" * 41)

    def test_non_hex_rejected(self) -> None:
        assert not is_valid_eth_address("0xZZZZ567890abcdef1234567890abcdef12345678")

    def test_empty_rejected(self) -> None:
        assert not is_valid_eth_address("")


# --- parse_decimal / parse_non_negative_decimal ---------------------------

class TestParseDecimal:
    def test_positive_integer(self) -> None:
        assert parse_decimal("1000", "debt", 1) == Decimal("1000")

    def test_positive_fractional(self) -> None:
        assert parse_decimal("1000.5", "debt", 1) == Decimal("1000.5")

    def test_zero(self) -> None:
        assert parse_decimal("0", "debt", 1) == Decimal("0")

    def test_negative(self) -> None:
        # parse_decimal allows negatives (debt < 0 is a credit user).
        assert parse_decimal("-25.0", "debt", 1) == Decimal("-25.0")

    def test_whitespace_stripped(self) -> None:
        assert parse_decimal("  1000  ", "debt", 1) == Decimal("1000")

    def test_empty_rejected(self) -> None:
        with pytest.raises(CSVValidationError) as excinfo:
            parse_decimal("", "debt", 5)
        assert excinfo.value.error.row_number == 5
        assert excinfo.value.error.field_name == "debt"

    def test_non_numeric_rejected(self) -> None:
        with pytest.raises(CSVValidationError) as excinfo:
            parse_decimal("abc", "debt", 5)
        assert "Invalid numeric value" in excinfo.value.error.message


class TestParseNonNegativeDecimal:
    def test_positive_accepted(self) -> None:
        assert parse_non_negative_decimal("500.0", "underlyingValue", 1) == Decimal("500.0")

    def test_zero_accepted(self) -> None:
        assert parse_non_negative_decimal("0", "underlyingValue", 1) == Decimal("0")

    def test_negative_rejected(self) -> None:
        with pytest.raises(CSVValidationError) as excinfo:
            parse_non_negative_decimal("-1", "underlyingValue", 3)
        assert excinfo.value.error.row_number == 3


# --- validate_headers -----------------------------------------------------

class TestValidateHeaders:
    def test_all_present_returns_empty(self) -> None:
        assert validate_headers(["address", "underlyingValue", "debt"]) == []

    def test_order_does_not_matter(self) -> None:
        assert validate_headers(["debt", "address", "underlyingValue"]) == []

    def test_extra_columns_tolerated(self) -> None:
        assert validate_headers(["address", "underlyingValue", "debt", "extra"]) == []

    def test_missing_column_reported(self) -> None:
        errors = validate_headers(["address", "underlyingValue"])
        assert len(errors) == 1
        assert errors[0].field_name == "debt"

    def test_whitespace_stripped_in_headers(self) -> None:
        assert validate_headers([" address ", "underlyingValue", " debt"]) == []


# --- validate_row ---------------------------------------------------------

VALID_ADDR = "0x1234567890abcdef1234567890abcdef12345678"


class TestValidateRow:
    def _row(self, **kwargs) -> dict[str, str]:
        base = {"address": VALID_ADDR, "underlyingValue": "100", "debt": "50"}
        base.update(kwargs)
        return base

    def test_valid_row_returns_csvrow(self) -> None:
        out = validate_row(self._row(), 1)
        assert isinstance(out, CSVRow)
        assert out.address == VALID_ADDR
        assert out.underlying_value == Decimal("100")
        assert out.debt == Decimal("50")
        assert out.row_number == 1

    def test_empty_address_rejected(self) -> None:
        with pytest.raises(CSVValidationError) as excinfo:
            validate_row(self._row(address=""), 7)
        assert excinfo.value.error.field_name == "address"

    def test_invalid_address_rejected(self) -> None:
        with pytest.raises(CSVValidationError) as excinfo:
            validate_row(self._row(address="0xdeadbeef"), 7)
        assert "Invalid Ethereum address" in excinfo.value.error.message

    def test_zero_underlying_rejected(self) -> None:
        with pytest.raises(CSVValidationError) as excinfo:
            validate_row(self._row(underlyingValue="0"), 3)
        assert "must be > 0" in excinfo.value.error.message

    def test_negative_underlying_rejected(self) -> None:
        with pytest.raises(CSVValidationError) as excinfo:
            validate_row(self._row(underlyingValue="-5"), 3)
        assert excinfo.value.error.field_name == "underlyingValue"

    def test_negative_debt_accepted_as_credit(self) -> None:
        out = validate_row(self._row(debt="-20"), 1)
        assert out.debt == Decimal("-20")
        assert out.is_credit_user is True


# --- convert_to_wei -------------------------------------------------------

class TestConvertToWei:
    def test_18_decimal_default(self) -> None:
        assert convert_to_wei(Decimal("1")) == 10**18

    def test_fractional(self) -> None:
        assert convert_to_wei(Decimal("1.5")) == 15 * 10**17

    def test_zero(self) -> None:
        assert convert_to_wei(Decimal(0)) == 0

    def test_6_decimal_scale(self) -> None:
        assert convert_to_wei(Decimal("1"), decimals=6) == 10**6

    def test_negative(self) -> None:
        assert convert_to_wei(Decimal("-1")) == -10**18


# --- position_from_row ----------------------------------------------------

class TestPositionFromRow:
    def _csv_row(self, *, debt: str, underlying: str = "100") -> CSVRow:
        return CSVRow(
            address=VALID_ADDR,
            underlying_value=Decimal(underlying),
            debt=Decimal(debt),
            row_number=1,
        )

    def test_debt_user(self) -> None:
        pos = position_from_row(self._csv_row(debt="50"), "mainnet", AssetType.USD)
        assert pos.user_address == VALID_ADDR
        assert pos.deposit_amount_wei == 100
        assert pos.mint_amount_wei == 50
        assert pos.credit_amount_wei == 0
        assert pos.is_debt_user is True

    def test_credit_user(self) -> None:
        pos = position_from_row(self._csv_row(debt="-25"), "mainnet", AssetType.USD)
        assert pos.mint_amount_wei == 0
        assert pos.credit_amount_wei == 25
        assert pos.is_credit_user is True

    def test_zero_debt(self) -> None:
        pos = position_from_row(self._csv_row(debt="0"), "mainnet", AssetType.USD)
        assert pos.mint_amount_wei == 0
        assert pos.credit_amount_wei == 0
        assert pos.is_debt_user is False

    def test_myt_decimals_rescales_deposit(self) -> None:
        # 18-dec input → 6-dec vault: divide by 10^12.
        row = self._csv_row(debt="0", underlying=str(5 * 10**18))
        pos_18 = position_from_row(row, "mainnet", AssetType.USD, myt_decimals=18)
        pos_6 = position_from_row(row, "mainnet", AssetType.USD, myt_decimals=6)
        assert pos_18.deposit_amount_wei == 5 * 10**18
        assert pos_6.deposit_amount_wei == 5 * 10**6
        assert pos_18.deposit_amount_wei // pos_6.deposit_amount_wei == 10**12

    def test_debt_is_not_rescaled_by_myt_decimals(self) -> None:
        # alAssets are always 18-decimal — debt amount must pass through regardless of myt_decimals.
        row = self._csv_row(debt="1000", underlying=str(10**18))
        pos = position_from_row(row, "mainnet", AssetType.USD, myt_decimals=6)
        assert pos.mint_amount_wei == 1000  # NOT rescaled

    def test_chain_propagated(self) -> None:
        pos = position_from_row(self._csv_row(debt="1"), "arbitrum", AssetType.ETH)
        assert pos.chain == "arbitrum"
        assert pos.asset_type == AssetType.ETH


# --- validate_csv_string --------------------------------------------------

class TestValidateCsvString:
    def _csv(self, rows: str) -> str:
        return "address,underlyingValue,debt\n" + rows

    def test_valid_multi_row(self) -> None:
        csv_content = self._csv(
            f"{VALID_ADDR},100,50\n"
            "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,200,-30\n"
            "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb,300,0\n"
        )
        result = validate_csv_string(csv_content, "mainnet", AssetType.USD)
        assert result.is_valid
        assert len(result.positions) == 3
        assert result.debt_count == 1
        assert result.credit_count == 1
        assert result.zero_debt_count == 1
        assert result.total_positions == 3

    def test_totals_sum_rows(self) -> None:
        csv_content = self._csv(
            f"{VALID_ADDR},100,50\n"
            "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,200,-30\n"
        )
        result = validate_csv_string(csv_content, "mainnet", AssetType.USD)
        assert result.total_deposit_wei == 300
        assert result.total_mint_wei == 50
        assert result.total_credit_wei == 30

    def test_invalid_address_halts(self) -> None:
        csv_content = self._csv(
            f"{VALID_ADDR},100,50\n"
            "0xdeadbeef,200,10\n"
        )
        result = validate_csv_string(csv_content, "mainnet", AssetType.USD)
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].row_number == 2

    def test_duplicate_address_halts(self) -> None:
        csv_content = self._csv(
            f"{VALID_ADDR},100,50\n"
            f"{VALID_ADDR},200,10\n"
        )
        result = validate_csv_string(csv_content, "mainnet", AssetType.USD)
        assert not result.is_valid
        assert "Duplicate address" in result.errors[0].message

    def test_missing_header_column_halts(self) -> None:
        csv_content = "address,underlyingValue\n" + f"{VALID_ADDR},100\n"
        result = validate_csv_string(csv_content, "mainnet", AssetType.USD)
        assert not result.is_valid
        assert any(e.field_name == "debt" for e in result.errors)

    def test_empty_csv_halts(self) -> None:
        result = validate_csv_string("", "mainnet", AssetType.USD)
        assert not result.is_valid
        assert result.errors[0].field_name == "header"

    def test_negative_underlying_halts(self) -> None:
        csv_content = self._csv(f"{VALID_ADDR},-100,50\n")
        result = validate_csv_string(csv_content, "mainnet", AssetType.USD)
        assert not result.is_valid
        assert result.errors[0].field_name == "underlyingValue"


# --- validate_csv_file ----------------------------------------------------

class TestValidateCsvFile:
    def test_missing_file(self, tmp_path: Path) -> None:
        result = validate_csv_file(tmp_path / "nonexistent.csv", "mainnet", AssetType.USD)
        assert not result.is_valid
        assert "not found" in result.errors[0].message

    def test_valid_file_loads(self, write_csv) -> None:
        csv_content = (
            "address,underlyingValue,debt\n"
            f"{VALID_ADDR},100,50\n"
        )
        path = write_csv(csv_content, name="single.csv")
        result = validate_csv_file(path, "mainnet", AssetType.USD)
        assert result.is_valid
        assert len(result.positions) == 1
        assert result.positions[0].chain == "mainnet"
        assert result.positions[0].asset_type == AssetType.USD

    def test_real_csv_files_parse(self, project_root: Path) -> None:
        """Lock in: all 6 committed CSVs parse cleanly. Covers the multi-chain matrix."""
        targets = [
            ("mainnet", AssetType.USD, "alUSDValues-sum-and-debt-mainnet.csv"),
            ("mainnet", AssetType.ETH, "alETHValues-sum-and-debt-mainnet.csv"),
            ("optimism", AssetType.USD, "alUSDValues-sum-and-debt-optimism.csv"),
            ("optimism", AssetType.ETH, "alETHValues-sum-and-debt-optimism.csv"),
            ("arbitrum", AssetType.USD, "alUSDValues-sum-and-debt-arbitrum.csv"),
            ("arbitrum", AssetType.ETH, "alETHValues-sum-and-debt-arbitrum.csv"),
        ]
        for chain, asset, fname in targets:
            path = project_root / "data" / fname
            assert path.exists(), f"missing CSV: {fname}"
            result = validate_csv_file(path, chain, asset)
            assert result.is_valid, f"{fname} failed validation: {result.errors[:3]}"
            assert result.total_positions > 0


# --- format_validation_errors --------------------------------------------

class TestFormatValidationErrors:
    def test_empty_list(self) -> None:
        assert format_validation_errors([]) == "No validation errors."

    def test_single_error_formatted(self) -> None:
        errors = [ValidationError(row_number=3, field_name="address", message="Invalid")]
        text = format_validation_errors(errors)
        assert "Row 3" in text
        assert "address" in text
        assert "Invalid" in text

    def test_multiple_errors(self) -> None:
        errors = [
            ValidationError(row_number=1, field_name="address", message="err1"),
            ValidationError(row_number=2, field_name="debt", message="err2"),
        ]
        text = format_validation_errors(errors)
        assert "err1" in text
        assert "err2" in text


# --- ValidationResult properties -----------------------------------------

class TestValidationResultProperties:
    def test_is_valid_when_no_errors(self) -> None:
        r = ValidationResult()
        assert r.is_valid

    def test_is_valid_false_when_errors(self) -> None:
        r = ValidationResult()
        r.errors.append(ValidationError(0, "f", "m"))
        assert not r.is_valid

    def test_total_positions_matches_list(self, make_position) -> None:
        r = ValidationResult()
        r.positions.append(make_position())
        r.positions.append(make_position())
        assert r.total_positions == 2
