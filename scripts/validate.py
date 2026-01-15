#!/usr/bin/env python3
"""CSV validation script for CDP migration.

Usage:
    ape run validate --chain mainnet

This script validates CSV data files before migration:
- Checks file exists and is readable
- Validates all required columns are present
- Validates address formats
- Validates numeric values are non-negative
- Halts on any invalid row with detailed error messages
"""

import click
from ape import project
from ape.cli import ape_cli_context

from src.config import get_csv_path, get_supported_chains, validate_chain_config


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
    - Address formats are valid
    - Numeric values are non-negative
    - No duplicate addresses

    Halts immediately on any validation error.
    """
    click.echo(f"Validating CSV data for {chain}...")

    # Check chain configuration
    missing_config = validate_chain_config(chain)
    if missing_config:
        click.echo(
            click.style(
                f"Warning: Chain config incomplete. Missing: {', '.join(missing_config)}",
                fg="yellow",
            )
        )

    # Get CSV path
    csv_path = get_csv_path(chain)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV file not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    click.echo(f"CSV file: {csv_path}")

    # TODO: Implement CSV validation in PR 2
    # - Parse CSV file
    # - Validate each row
    # - Report errors with row numbers
    # - Halt on first error

    click.echo(click.style("CSV validation not yet implemented (PR 2)", fg="yellow"))
    click.echo(click.style("Validation placeholder complete.", fg="green"))
