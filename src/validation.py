"""CSV validation for V3 migration.

CSV schema: address,underlyingValue,debt
  - address: Ethereum address
  - underlyingValue: collateral in atomic/wei units (MYT share token atomic units)
  - debt: positive = user owes alAssets (atomic units); negative = protocol owes user (credit)

Values are already in the smallest unit of their respective tokens and are passed
directly to contract calls without further scaling (token_decimals=0 in config).

One file per asset type per chain:
  alUSDValues-sum-and-debt-mainnet.csv
  alETHValues-sum-and-debt-mainnet.csv
  etc.
"""

import csv
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from io import StringIO
from pathlib import Path
from typing import TextIO

from src.types import AssetType, CSVRow, PositionMigration, ValidationError


EXPECTED_COLUMNS = ["address", "underlyingValue", "debt"]
ETH_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")


class CSVValidationError(Exception):
    def __init__(self, error: ValidationError) -> None:
        self.error = error
        super().__init__(str(error))


@dataclass
class ValidationResult:
    rows: list[CSVRow] = field(default_factory=list)
    positions: list[PositionMigration] = field(default_factory=list)
    errors: list[ValidationError] = field(default_factory=list)
    total_deposit_wei: int = 0
    total_mint_wei: int = 0
    total_credit_wei: int = 0
    debt_count: int = 0
    credit_count: int = 0
    zero_debt_count: int = 0

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def total_positions(self) -> int:
        return len(self.positions)


def is_valid_eth_address(address: str) -> bool:
    return bool(ETH_ADDRESS_PATTERN.match(address))


def parse_decimal(value: str, field_name: str, row_number: int) -> Decimal:
    """Parse a decimal field. Allows negative values (debt < 0 = credit)."""
    value = value.strip()
    if not value:
        raise CSVValidationError(
            ValidationError(row_number, field_name, "Field is empty", value)
        )
    try:
        return Decimal(value)
    except InvalidOperation:
        raise CSVValidationError(
            ValidationError(row_number, field_name, "Invalid numeric value", value)
        )


def parse_non_negative_decimal(value: str, field_name: str, row_number: int) -> Decimal:
    """Parse a decimal that must be >= 0 (underlyingValue)."""
    d = parse_decimal(value, field_name, row_number)
    if d < 0:
        raise CSVValidationError(
            ValidationError(row_number, field_name, "Value must be >= 0", value)
        )
    return d


def validate_row(row: dict[str, str], row_number: int) -> CSVRow:
    address = row.get("address", "").strip()
    if not address:
        raise CSVValidationError(
            ValidationError(row_number, "address", "Address is empty", address)
        )
    if not is_valid_eth_address(address):
        raise CSVValidationError(
            ValidationError(
                row_number, "address",
                "Invalid Ethereum address (must be 0x + 40 hex chars)",
                address,
            )
        )

    underlying = parse_non_negative_decimal(
        row.get("underlyingValue", ""), "underlyingValue", row_number
    )
    if underlying <= 0:
        raise CSVValidationError(
            ValidationError(
                row_number, "underlyingValue",
                "underlyingValue must be > 0 (rows with no collateral should be omitted)",
                str(underlying),
            )
        )

    debt = parse_decimal(row.get("debt", ""), "debt", row_number)

    return CSVRow(
        address=address,
        underlying_value=underlying,
        debt=debt,
        row_number=row_number,
    )


def validate_headers(headers: list[str]) -> list[ValidationError]:
    errors = []
    normalized = [h.strip() for h in headers]
    for col in EXPECTED_COLUMNS:
        if col not in normalized:
            errors.append(
                ValidationError(0, col, f"Required column '{col}' is missing from CSV header")
            )
    return errors


def convert_to_wei(value: Decimal, decimals: int = 18) -> int:
    """Convert human-unit amount to wei."""
    return int(value * Decimal(10 ** decimals))


def position_from_row(
    row: CSVRow,
    chain: str,
    asset_type: AssetType,
    token_decimals: int = 18,
) -> PositionMigration:
    """Build a PositionMigration from a validated CSV row.

    MYT is 1:1 with underlying at migration time (no strategies allocated yet),
    so deposit_amount_wei = underlying_value_wei.

    Debt:
      positive → real debt user: mint that amount as alAssets to multisig; no credit.
      negative → credit user: mint abs(debt) to multisig as a temporary debt (Phase 1),
                 distribute abs(debt) alAssets to the user (Phase 2), then burn the
                 temp debt back in Phase 3. Both mint_amount_wei AND credit_amount_wei
                 are set to abs(debt) — this is intentional and required for math to
                 balance. See PositionMigration docstring for full phase description.
      zero     → deposit only, no mint, no credit.
    """
    deposit_wei = convert_to_wei(row.underlying_value, token_decimals)
    mint_wei = convert_to_wei(row.debt, token_decimals) if row.debt > 0 else (
        convert_to_wei(abs(row.debt), token_decimals) if row.debt < 0 else 0
    )
    credit_wei = convert_to_wei(abs(row.debt), token_decimals) if row.debt < 0 else 0

    return PositionMigration(
        user_address=row.address,
        asset_type=asset_type,
        chain=chain,
        deposit_amount_wei=deposit_wei,
        mint_amount_wei=mint_wei,
        credit_amount_wei=credit_wei,
    )


def validate_csv_file(
    file_path: Path,
    chain: str,
    asset_type: AssetType,
    token_decimals: int = 18,
) -> ValidationResult:
    """Load and validate a migration CSV file.

    token_decimals: scaling factor for CSV values. CSV values are already in
        atomic/wei units, so this should be 0 (no scaling). Read from
        AssetConfig.token_decimals; do not hardcode.

    Stops immediately on the first invalid row.
    """
    result = ValidationResult()

    if not file_path.exists():
        result.errors.append(
            ValidationError(0, "file", f"CSV file not found: {file_path}")
        )
        return result

    with open(file_path, "r", newline="", encoding="utf-8") as f:
        return _validate_csv_content(f, chain, asset_type, token_decimals)


def validate_csv_string(
    csv_content: str,
    chain: str,
    asset_type: AssetType,
    token_decimals: int = 18,
) -> ValidationResult:
    """Validate CSV content from a string (for testing)."""
    return _validate_csv_content(StringIO(csv_content), chain, asset_type, token_decimals)


def _validate_csv_content(
    file_obj: TextIO,
    chain: str,
    asset_type: AssetType,
    token_decimals: int,
) -> ValidationResult:
    result = ValidationResult()

    try:
        reader = csv.DictReader(file_obj)

        if reader.fieldnames is None:
            result.errors.append(
                ValidationError(0, "header", "CSV file is empty or has no header row")
            )
            return result

        header_errors = validate_headers(list(reader.fieldnames))
        if header_errors:
            result.errors.extend(header_errors)
            return result

        seen_addresses: set[str] = set()

        for row_number, row in enumerate(reader, start=1):
            try:
                csv_row = validate_row(row, row_number)
            except CSVValidationError as e:
                result.errors.append(e.error)
                return result

            # Duplicate address check
            if csv_row.address.lower() in seen_addresses:
                result.errors.append(
                    ValidationError(row_number, "address", "Duplicate address", csv_row.address)
                )
                return result

            seen_addresses.add(csv_row.address.lower())
            result.rows.append(csv_row)

            position = position_from_row(csv_row, chain, asset_type, token_decimals)
            result.positions.append(position)

            result.total_deposit_wei += position.deposit_amount_wei
            result.total_mint_wei += position.mint_amount_wei
            result.total_credit_wei += position.credit_amount_wei

            if position.is_debt_user:
                result.debt_count += 1
            elif position.is_credit_user:
                result.credit_count += 1
            else:
                result.zero_debt_count += 1

    except csv.Error as e:
        result.errors.append(
            ValidationError(0, "csv", f"CSV parsing error: {e}")
        )

    return result


def format_validation_errors(errors: list[ValidationError]) -> str:
    if not errors:
        return "No validation errors."
    lines = ["CSV Validation Failed:", ""]
    for error in errors:
        lines.append(f"  - {error}")
    return "\n".join(lines)
