#!/usr/bin/env python3
"""CSV validation script for CDP migration.

Usage:
    ape run validate --chain mainnet

This script validates CSV data files before migration:
- Checks file exists and is readable
- Validates all required columns are present
- Validates address formats (0x + 40 hex chars)
- Validates numeric values are non-negative
- Validates at least one position per row has underlyingValue > 0
- Checks for duplicate addresses
- Halts on any invalid row with detailed error messages
"""

import click
from ape.cli import ape_cli_context

from src.config import get_csv_path, get_supported_chains, validate_chain_config
from src.validation import (
    format_validation_errors,
    validate_csv_file,
)


@click.command()
@click.option(
    "--chain",
    type=click.Choice(get_supported_chains()),
    required=True,
    help="Chain to validate CSV data for",
)
@ape_cli_context()
def cli(cli_ctx, chain: str) -> None:
    """Validate CSV data file for a specific chain.

    Validates:
    - CSV file exists and is readable
    - All required columns present
    - Address formats are valid (0x + 40 hex characters)
    - Numeric values are non-negative
    - At least one position per row has underlyingValue > 0
    - No duplicate addresses

    Halts immediately on any validation error.
    """
    click.echo(f"Validating CSV data for {chain}...")
    click.echo("")

    # Check chain configuration
    missing_config = validate_chain_config(chain)
    if missing_config:
        click.echo(
            click.style(
                f"Warning: Chain config incomplete. Missing: {', '.join(missing_config)}",
                fg="yellow",
            )
        )
        click.echo("")

    # Get CSV path
    csv_path = get_csv_path(chain)
    click.echo(f"CSV file: {csv_path}")

    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV file not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    # Validate CSV file
    result = validate_csv_file(csv_path, chain)

    if not result.is_valid:
        click.echo("")
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)

    # Success - print summary
    click.echo("")
    click.echo(click.style("Validation successful!", fg="green"))
    click.echo("")
    click.echo("Summary:")
    click.echo(f"  Total rows:        {len(result.rows)}")
    click.echo(f"  Total positions:   {result.total_positions}")
    click.echo(f"  USD positions:     {result.usd_token_count}")
    click.echo(f"  ETH positions:     {result.eth_token_count}")
