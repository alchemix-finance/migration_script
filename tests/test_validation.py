"""Tests for CSV validation module."""

import pytest
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.validation import (
    CSVValidationError,
    ValidationResult,
    convert_to_wei,
    create_positions_from_row,
    format_validation_errors,
    is_valid_eth_address,
    parse_numeric_field,
    validate_csv_content,
    validate_csv_file,
    validate_csv_string,
    validate_headers,
    validate_row,
)
from src.types import CSVRow, ValidationError


class TestIsValidEthAddress:
    """Tests for Ethereum address validation."""

    def test_valid_lowercase_address(self) -> None:
        """Test valid lowercase hex address."""
        assert is_valid_eth_address("0x1234567890abcdef1234567890abcdef12345678")

    def test_valid_uppercase_address(self) -> None:
        """Test valid uppercase hex address."""
        assert is_valid_eth_address("0x1234567890ABCDEF1234567890ABCDEF12345678")

    def test_valid_mixed_case_address(self) -> None:
        """Test valid mixed case address."""
        assert is_valid_eth_address("0xAbCdEf1234567890AbCdEf1234567890AbCdEf12")

    def test_invalid_missing_0x_prefix(self) -> None:
        """Test address without 0x prefix is invalid."""
        assert not is_valid_eth_address("1234567890abcdef1234567890abcdef12345678")

    def test_invalid_short_address(self) -> None:
        """Test address with fewer than 40 hex chars is invalid."""
        assert not is_valid_eth_address("0x123456789012345678901234567890123456789")

    def test_invalid_long_address(self) -> None:
        """Test address with more than 40 hex chars is invalid."""
        assert not is_valid_eth_address("0x12345678901234567890123456789012345678901")

    def test_invalid_non_hex_chars(self) -> None:
        """Test address with non-hex characters is invalid."""
        assert not is_valid_eth_address("0x123456789012345678901234567890123456789g")

    def test_invalid_empty_string(self) -> None:
        """Test empty string is invalid."""
        assert not is_valid_eth_address("")

    def test_invalid_only_prefix(self) -> None:
        """Test only 0x prefix is invalid."""
        assert not is_valid_eth_address("0x")


class TestParseNumericField:
    """Tests for numeric field parsing."""

    def test_valid_integer(self) -> None:
        """Test parsing valid integer."""
        result = parse_numeric_field("1000", "test_field", 1)
        assert result == Decimal("1000")

    def test_valid_decimal(self) -> None:
        """Test parsing valid decimal."""
        result = parse_numeric_field("1000.50", "test_field", 1)
        assert result == Decimal("1000.50")

    def test_valid_zero(self) -> None:
        """Test parsing zero."""
        result = parse_numeric_field("0", "test_field", 1)
        assert result == Decimal("0")

    def test_valid_with_whitespace(self) -> None:
        """Test parsing value with whitespace."""
        result = parse_numeric_field("  100.5  ", "test_field", 1)
        assert result == Decimal("100.5")

    def test_invalid_negative(self) -> None:
        """Test negative value raises error."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_numeric_field("-100", "test_field", 5)
        assert exc_info.value.error.row_number == 5
        assert exc_info.value.error.field_name == "test_field"
        assert "non-negative" in exc_info.value.error.message

    def test_invalid_non_numeric(self) -> None:
        """Test non-numeric value raises error."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_numeric_field("abc", "test_field", 3)
        assert exc_info.value.error.row_number == 3
        assert "Invalid numeric" in exc_info.value.error.message

    def test_invalid_empty(self) -> None:
        """Test empty value raises error."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_numeric_field("", "test_field", 2)
        assert exc_info.value.error.row_number == 2
        assert "empty or missing" in exc_info.value.error.message


class TestValidateHeaders:
    """Tests for header validation."""

    def test_valid_headers(self) -> None:
        """Test all required headers present."""
        headers = [
            "address",
            "USD_debt",
            "USD_underlyingValue",
            "ETH_debt",
            "ETH_underlyingValue",
        ]
        errors = validate_headers(headers)
        assert len(errors) == 0

    def test_valid_headers_with_extra_whitespace(self) -> None:
        """Test headers with whitespace are handled."""
        headers = [
            " address ",
            " USD_debt",
            "USD_underlyingValue ",
            "ETH_debt",
            "ETH_underlyingValue",
        ]
        errors = validate_headers(headers)
        assert len(errors) == 0

    def test_missing_single_header(self) -> None:
        """Test single missing header is detected."""
        headers = [
            "address",
            "USD_debt",
            "ETH_debt",
            "ETH_underlyingValue",
        ]
        errors = validate_headers(headers)
        assert len(errors) == 1
        assert errors[0].field_name == "USD_underlyingValue"

    def test_missing_multiple_headers(self) -> None:
        """Test multiple missing headers are detected."""
        headers = ["address", "USD_debt"]
        errors = validate_headers(headers)
        assert len(errors) == 3


class TestValidateRow:
    """Tests for individual row validation."""

    def test_valid_row_both_positions(self) -> None:
        """Test valid row with both USD and ETH positions."""
        row = {
            "address": "0x1234567890123456789012345678901234567890",
            "USD_debt": "1000.50",
            "USD_underlyingValue": "5000.00",
            "ETH_debt": "0.5",
            "ETH_underlyingValue": "2.0",
        }
        result = validate_row(row, 1)
        assert result.address == "0x1234567890123456789012345678901234567890"
        assert result.usd_debt == 1000.50
        assert result.usd_underlying_value == 5000.00
        assert result.eth_debt == 0.5
        assert result.eth_underlying_value == 2.0
        assert result.row_number == 1

    def test_valid_row_usd_only(self) -> None:
        """Test valid row with only USD position."""
        row = {
            "address": "0x1234567890123456789012345678901234567890",
            "USD_debt": "1000.00",
            "USD_underlyingValue": "5000.00",
            "ETH_debt": "0",
            "ETH_underlyingValue": "0",
        }
        result = validate_row(row, 1)
        assert result.has_usd_position
        assert not result.has_eth_position

    def test_valid_row_eth_only(self) -> None:
        """Test valid row with only ETH position."""
        row = {
            "address": "0x1234567890123456789012345678901234567890",
            "USD_debt": "0",
            "USD_underlyingValue": "0",
            "ETH_debt": "0.5",
            "ETH_underlyingValue": "2.0",
        }
        result = validate_row(row, 1)
        assert not result.has_usd_position
        assert result.has_eth_position

    def test_invalid_address_empty(self) -> None:
        """Test empty address raises error."""
        row = {
            "address": "",
            "USD_debt": "1000",
            "USD_underlyingValue": "5000",
            "ETH_debt": "0",
            "ETH_underlyingValue": "0",
        }
        with pytest.raises(CSVValidationError) as exc_info:
            validate_row(row, 3)
        assert exc_info.value.error.field_name == "address"
        assert exc_info.value.error.row_number == 3

    def test_invalid_address_format(self) -> None:
        """Test invalid address format raises error."""
        row = {
            "address": "not_an_address",
            "USD_debt": "1000",
            "USD_underlyingValue": "5000",
            "ETH_debt": "0",
            "ETH_underlyingValue": "0",
        }
        with pytest.raises(CSVValidationError) as exc_info:
            validate_row(row, 2)
        assert exc_info.value.error.field_name == "address"
        assert "0x + 40 hex" in exc_info.value.error.message

    def test_invalid_no_positions(self) -> None:
        """Test row with no positions raises error."""
        row = {
            "address": "0x1234567890123456789012345678901234567890",
            "USD_debt": "0",
            "USD_underlyingValue": "0",
            "ETH_debt": "0",
            "ETH_underlyingValue": "0",
        }
        with pytest.raises(CSVValidationError) as exc_info:
            validate_row(row, 5)
        assert "at least one position" in exc_info.value.error.message.lower()

    def test_invalid_negative_debt(self) -> None:
        """Test negative debt raises error."""
        row = {
            "address": "0x1234567890123456789012345678901234567890",
            "USD_debt": "-100",
            "USD_underlyingValue": "5000",
            "ETH_debt": "0",
            "ETH_underlyingValue": "0",
        }
        with pytest.raises(CSVValidationError) as exc_info:
            validate_row(row, 1)
        assert exc_info.value.error.field_name == "USD_debt"


class TestConvertToWei:
    """Tests for wei conversion."""

    def test_convert_integer(self) -> None:
        """Test converting integer value to wei."""
        result = convert_to_wei(1.0)
        assert result == 1_000_000_000_000_000_000

    def test_convert_decimal(self) -> None:
        """Test converting decimal value to wei."""
        result = convert_to_wei(0.5)
        assert result == 500_000_000_000_000_000

    def test_convert_zero(self) -> None:
        """Test converting zero."""
        result = convert_to_wei(0.0)
        assert result == 0

    def test_convert_large_value(self) -> None:
        """Test converting large value."""
        result = convert_to_wei(1000000.0)
        assert result == 1_000_000_000_000_000_000_000_000


class TestCreatePositionsFromRow:
    """Tests for position creation from CSV rows."""

    def test_create_both_positions(self) -> None:
        """Test creating both USD and ETH positions."""
        row = CSVRow(
            address="0x1234567890123456789012345678901234567890",
            usd_debt=1000.0,
            usd_underlying_value=5000.0,
            eth_debt=0.5,
            eth_underlying_value=2.0,
            row_number=1,
        )
        positions, new_usd_id, new_eth_id = create_positions_from_row(
            row, "mainnet", 0, 0
        )
        assert len(positions) == 2
        assert new_usd_id == 1
        assert new_eth_id == 1

        usd_pos = positions[0]
        assert usd_pos.asset_type == "USD"
        assert usd_pos.token_id == 0
        assert usd_pos.deposit_amount == convert_to_wei(5000.0)
        assert usd_pos.mint_amount == convert_to_wei(1000.0)

        eth_pos = positions[1]
        assert eth_pos.asset_type == "ETH"
        assert eth_pos.token_id == 0

    def test_create_usd_only(self) -> None:
        """Test creating only USD position."""
        row = CSVRow(
            address="0x1234567890123456789012345678901234567890",
            usd_debt=1000.0,
            usd_underlying_value=5000.0,
            eth_debt=0.0,
            eth_underlying_value=0.0,
            row_number=1,
        )
        positions, new_usd_id, new_eth_id = create_positions_from_row(
            row, "mainnet", 5, 3
        )
        assert len(positions) == 1
        assert new_usd_id == 6
        assert new_eth_id == 3  # Unchanged
        assert positions[0].token_id == 5

    def test_create_eth_only(self) -> None:
        """Test creating only ETH position."""
        row = CSVRow(
            address="0x1234567890123456789012345678901234567890",
            usd_debt=0.0,
            usd_underlying_value=0.0,
            eth_debt=0.5,
            eth_underlying_value=2.0,
            row_number=1,
        )
        positions, new_usd_id, new_eth_id = create_positions_from_row(
            row, "mainnet", 5, 3
        )
        assert len(positions) == 1
        assert new_usd_id == 5  # Unchanged
        assert new_eth_id == 4
        assert positions[0].token_id == 3


class TestValidateCsvString:
    """Tests for full CSV validation."""

    def test_valid_csv(self) -> None:
        """Test validating a valid CSV."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000.50,5000.00,0.5,2.0
0xBBB0000000000000000000000000000000000002,0,0,1.5,3.0
0xCCC0000000000000000000000000000000000003,3000.00,15000.00,0,0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert result.is_valid
        assert len(result.rows) == 3
        assert len(result.positions) == 4  # 2 USD + 2 ETH
        assert result.usd_token_count == 2
        assert result.eth_token_count == 2

    def test_token_id_assignment(self) -> None:
        """Test that token IDs are assigned correctly."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000,5000,0.5,2.0
0xBBB0000000000000000000000000000000000002,0,0,1.5,3.0
0xCCC0000000000000000000000000000000000003,3000,15000,0,0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert result.is_valid

        # Check USD token IDs
        usd_positions = [p for p in result.positions if p.asset_type == "USD"]
        assert len(usd_positions) == 2
        assert usd_positions[0].token_id == 0  # Row 1
        assert usd_positions[1].token_id == 1  # Row 3

        # Check ETH token IDs
        eth_positions = [p for p in result.positions if p.asset_type == "ETH"]
        assert len(eth_positions) == 2
        assert eth_positions[0].token_id == 0  # Row 1
        assert eth_positions[1].token_id == 1  # Row 2

    def test_empty_csv(self) -> None:
        """Test validating an empty CSV."""
        csv_content = ""
        result = validate_csv_string(csv_content, "mainnet")
        assert not result.is_valid
        assert any("empty" in str(e).lower() for e in result.errors)

    def test_missing_header(self) -> None:
        """Test CSV with missing header column."""
        csv_content = """address,USD_debt,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000,0.5,2.0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert not result.is_valid
        assert any("USD_underlyingValue" in str(e) for e in result.errors)

    def test_invalid_address_halts(self) -> None:
        """Test that invalid address halts processing."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000,5000,0.5,2.0
invalid_address,1000,5000,0.5,2.0
0xCCC0000000000000000000000000000000000003,3000,15000,0,0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert not result.is_valid
        assert len(result.errors) == 1  # Only first error
        assert result.errors[0].row_number == 2

    def test_duplicate_address(self) -> None:
        """Test that duplicate address is detected."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000,5000,0.5,2.0
0xAAA0000000000000000000000000000000000001,2000,6000,0.6,3.0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert not result.is_valid
        assert result.errors[0].row_number == 2
        assert "duplicate" in result.errors[0].message.lower()

    def test_duplicate_address_case_insensitive(self) -> None:
        """Test that duplicate detection is case-insensitive."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000,5000,0.5,2.0
0xaaa0000000000000000000000000000000000001,2000,6000,0.6,3.0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert not result.is_valid
        assert "duplicate" in result.errors[0].message.lower()

    def test_negative_value_halts(self) -> None:
        """Test that negative value halts processing."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,-1000,5000,0.5,2.0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert not result.is_valid
        assert result.errors[0].field_name == "USD_debt"

    def test_no_positions_halts(self) -> None:
        """Test that row with no positions halts processing."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,0,0,0,0
"""
        result = validate_csv_string(csv_content, "mainnet")
        assert not result.is_valid
        assert "at least one position" in result.errors[0].message.lower()


class TestValidateCsvFile:
    """Tests for file-based CSV validation."""

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test validation of non-existent file."""
        result = validate_csv_file(tmp_path / "nonexistent.csv", "mainnet")
        assert not result.is_valid
        assert "not found" in result.errors[0].message.lower()

    def test_valid_file(self, tmp_path: Path) -> None:
        """Test validation of valid CSV file."""
        csv_content = """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000,5000,0.5,2.0
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        result = validate_csv_file(csv_file, "mainnet")
        assert result.is_valid
        assert len(result.rows) == 1


class TestFormatValidationErrors:
    """Tests for error formatting."""

    def test_no_errors(self) -> None:
        """Test formatting with no errors."""
        result = format_validation_errors([])
        assert "No validation errors" in result

    def test_single_error(self) -> None:
        """Test formatting single error."""
        errors = [
            ValidationError(
                row_number=5,
                field_name="address",
                message="Invalid format",
                value="bad",
            )
        ]
        result = format_validation_errors(errors)
        assert "CSV Validation Failed" in result
        assert "Row 5" in result
        assert "address" in result

    def test_multiple_errors(self) -> None:
        """Test formatting multiple errors."""
        errors = [
            ValidationError(row_number=1, field_name="field1", message="Error 1"),
            ValidationError(row_number=2, field_name="field2", message="Error 2"),
        ]
        result = format_validation_errors(errors)
        assert "Row 1" in result
        assert "Row 2" in result


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_is_valid_true(self) -> None:
        """Test is_valid when no errors."""
        result = ValidationResult()
        assert result.is_valid

    def test_is_valid_false(self) -> None:
        """Test is_valid when errors present."""
        result = ValidationResult()
        result.errors.append(
            ValidationError(row_number=1, field_name="test", message="error")
        )
        assert not result.is_valid

    def test_total_positions(self) -> None:
        """Test total_positions calculation."""
        result = ValidationResult()
        assert result.total_positions == 0
