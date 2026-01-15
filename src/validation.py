"""CSV validation module for CDP migration.

This module provides strict CSV parsing and validation for position migration data.
Validation halts immediately on any invalid row with human-readable error messages.
"""

import csv
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator, TextIO

from src.types import CSVRow, PositionMigration, ValidationError


# Constants
EXPECTED_COLUMNS = [
    "address",
    "USD_debt",
    "USD_underlyingValue",
    "ETH_debt",
    "ETH_underlyingValue",
]

# Ethereum address regex: 0x followed by exactly 40 hex characters
ETH_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")


class CSVValidationError(Exception):
    """Exception raised when CSV validation fails.

    Contains the validation error with row number and field information.
    """

    def __init__(self, error: ValidationError) -> None:
        self.error = error
        super().__init__(str(error))


@dataclass
class ValidationResult:
    """Result of CSV validation containing parsed rows and any errors."""

    rows: list[CSVRow] = field(default_factory=list)
    positions: list[PositionMigration] = field(default_factory=list)
    errors: list[ValidationError] = field(default_factory=list)
    usd_token_count: int = 0
    eth_token_count: int = 0

    @property
    def is_valid(self) -> bool:
        """Check if validation passed with no errors."""
        return len(self.errors) == 0

    @property
    def total_positions(self) -> int:
        """Total number of positions to migrate."""
        return len(self.positions)


def is_valid_eth_address(address: str) -> bool:
    """Check if a string is a valid Ethereum address.

    Args:
        address: String to validate

    Returns:
        True if valid Ethereum address (0x + 40 hex chars), False otherwise
    """
    return bool(ETH_ADDRESS_PATTERN.match(address))


def parse_numeric_field(value: str, field_name: str, row_number: int) -> Decimal:
    """Parse a numeric field value and validate it's non-negative.

    Args:
        value: String value to parse
        field_name: Name of the field (for error messages)
        row_number: Row number in CSV (for error messages)

    Returns:
        Parsed Decimal value

    Raises:
        CSVValidationError: If value is not a valid non-negative number
    """
    value = value.strip()

    if not value:
        raise CSVValidationError(
            ValidationError(
                row_number=row_number,
                field_name=field_name,
                message="Field is empty or missing",
                value=value,
            )
        )

    try:
        decimal_value = Decimal(value)
    except InvalidOperation:
        raise CSVValidationError(
            ValidationError(
                row_number=row_number,
                field_name=field_name,
                message="Invalid numeric value",
                value=value,
            )
        )

    if decimal_value < 0:
        raise CSVValidationError(
            ValidationError(
                row_number=row_number,
                field_name=field_name,
                message="Value must be non-negative",
                value=value,
            )
        )

    return decimal_value


def validate_row(row: dict[str, str], row_number: int) -> CSVRow:
    """Validate a single CSV row and convert to CSVRow dataclass.

    Args:
        row: Dictionary of field name to value from CSV reader
        row_number: Row number in the CSV file (1-indexed, excluding header)

    Returns:
        Validated CSVRow instance

    Raises:
        CSVValidationError: If any field fails validation
    """
    # Validate address
    address = row.get("address", "").strip()
    if not address:
        raise CSVValidationError(
            ValidationError(
                row_number=row_number,
                field_name="address",
                message="Address field is empty or missing",
                value=address,
            )
        )

    if not is_valid_eth_address(address):
        raise CSVValidationError(
            ValidationError(
                row_number=row_number,
                field_name="address",
                message="Invalid Ethereum address format (must be 0x + 40 hex characters)",
                value=address,
            )
        )

    # Parse numeric fields
    usd_debt = parse_numeric_field(
        row.get("USD_debt", ""), "USD_debt", row_number
    )
    usd_underlying = parse_numeric_field(
        row.get("USD_underlyingValue", ""), "USD_underlyingValue", row_number
    )
    eth_debt = parse_numeric_field(
        row.get("ETH_debt", ""), "ETH_debt", row_number
    )
    eth_underlying = parse_numeric_field(
        row.get("ETH_underlyingValue", ""), "ETH_underlyingValue", row_number
    )

    # Validate at least one position has underlyingValue > 0
    if usd_underlying <= 0 and eth_underlying <= 0:
        raise CSVValidationError(
            ValidationError(
                row_number=row_number,
                field_name="USD_underlyingValue/ETH_underlyingValue",
                message="At least one position must have underlyingValue > 0",
                value=f"USD={usd_underlying}, ETH={eth_underlying}",
            )
        )

    return CSVRow(
        address=address,
        usd_debt=float(usd_debt),
        usd_underlying_value=float(usd_underlying),
        eth_debt=float(eth_debt),
        eth_underlying_value=float(eth_underlying),
        row_number=row_number,
    )


def validate_headers(headers: list[str]) -> list[ValidationError]:
    """Validate that all required headers are present.

    Args:
        headers: List of header names from CSV

    Returns:
        List of validation errors for missing columns
    """
    errors = []
    headers_normalized = [h.strip() for h in headers]

    for expected_col in EXPECTED_COLUMNS:
        if expected_col not in headers_normalized:
            errors.append(
                ValidationError(
                    row_number=0,
                    field_name=expected_col,
                    message=f"Required column '{expected_col}' is missing from CSV header",
                )
            )

    return errors


def convert_to_wei(value: float, decimals: int = 18) -> int:
    """Convert a float value to wei (integer with 18 decimals).

    Args:
        value: Float value to convert
        decimals: Number of decimal places (default 18 for ETH/ERC20)

    Returns:
        Integer value in wei
    """
    return int(Decimal(str(value)) * Decimal(10 ** decimals))


def create_positions_from_row(
    row: CSVRow,
    chain: str,
    usd_token_id: int,
    eth_token_id: int,
) -> tuple[list[PositionMigration], int, int]:
    """Create PositionMigration objects from a validated CSV row.

    Token IDs are assigned only when underlyingValue > 0 for that asset.

    Args:
        row: Validated CSV row
        chain: Chain name for the positions
        usd_token_id: Current USD token ID counter
        eth_token_id: Current ETH token ID counter

    Returns:
        Tuple of (list of positions, new usd_token_id, new eth_token_id)
    """
    positions = []

    if row.has_usd_position:
        positions.append(
            PositionMigration(
                user_address=row.address,
                asset_type="USD",
                token_id=usd_token_id,
                deposit_amount=convert_to_wei(row.usd_underlying_value),
                mint_amount=convert_to_wei(row.usd_debt),
                chain=chain,
            )
        )
        usd_token_id += 1

    if row.has_eth_position:
        positions.append(
            PositionMigration(
                user_address=row.address,
                asset_type="ETH",
                token_id=eth_token_id,
                deposit_amount=convert_to_wei(row.eth_underlying_value),
                mint_amount=convert_to_wei(row.eth_debt),
                chain=chain,
            )
        )
        eth_token_id += 1

    return positions, usd_token_id, eth_token_id


def validate_csv_file(file_path: Path, chain: str) -> ValidationResult:
    """Validate an entire CSV file and return parsed positions.

    This function performs strict validation - it halts immediately on any
    invalid row and returns a result with the error.

    Args:
        file_path: Path to the CSV file
        chain: Chain name for the positions

    Returns:
        ValidationResult containing parsed rows/positions or errors

    Raises:
        FileNotFoundError: If the CSV file does not exist
    """
    if not file_path.exists():
        result = ValidationResult()
        result.errors.append(
            ValidationError(
                row_number=0,
                field_name="file",
                message=f"CSV file not found: {file_path}",
            )
        )
        return result

    with open(file_path, "r", newline="", encoding="utf-8") as f:
        return validate_csv_content(f, chain)


def validate_csv_content(file_obj: TextIO, chain: str) -> ValidationResult:
    """Validate CSV content from a file-like object.

    Args:
        file_obj: File-like object containing CSV data
        chain: Chain name for the positions

    Returns:
        ValidationResult containing parsed rows/positions or errors
    """
    result = ValidationResult()

    try:
        reader = csv.DictReader(file_obj)

        # Validate headers
        if reader.fieldnames is None:
            result.errors.append(
                ValidationError(
                    row_number=0,
                    field_name="header",
                    message="CSV file is empty or has no header row",
                )
            )
            return result

        header_errors = validate_headers(list(reader.fieldnames))
        if header_errors:
            result.errors.extend(header_errors)
            return result

        # Process rows
        usd_token_id = 0
        eth_token_id = 0
        seen_addresses: set[str] = set()

        for row_number, row in enumerate(reader, start=1):
            try:
                csv_row = validate_row(row, row_number)

                # Check for duplicate addresses
                if csv_row.address.lower() in seen_addresses:
                    result.errors.append(
                        ValidationError(
                            row_number=row_number,
                            field_name="address",
                            message="Duplicate address found",
                            value=csv_row.address,
                        )
                    )
                    return result

                seen_addresses.add(csv_row.address.lower())
                result.rows.append(csv_row)

                # Create positions
                positions, usd_token_id, eth_token_id = create_positions_from_row(
                    csv_row, chain, usd_token_id, eth_token_id
                )
                result.positions.extend(positions)

            except CSVValidationError as e:
                result.errors.append(e.error)
                return result  # Halt on first error

        result.usd_token_count = usd_token_id
        result.eth_token_count = eth_token_id

    except csv.Error as e:
        result.errors.append(
            ValidationError(
                row_number=0,
                field_name="csv",
                message=f"CSV parsing error: {e}",
            )
        )

    return result


def validate_csv_string(csv_content: str, chain: str) -> ValidationResult:
    """Validate CSV content from a string.

    Convenience function for testing.

    Args:
        csv_content: CSV content as string
        chain: Chain name for the positions

    Returns:
        ValidationResult containing parsed rows/positions or errors
    """
    from io import StringIO
    return validate_csv_content(StringIO(csv_content), chain)


def format_validation_errors(errors: list[ValidationError]) -> str:
    """Format validation errors as a human-readable string.

    Args:
        errors: List of validation errors

    Returns:
        Formatted string with all errors
    """
    if not errors:
        return "No validation errors."

    lines = ["CSV Validation Failed:", ""]
    for error in errors:
        lines.append(f"  - {error}")

    return "\n".join(lines)
