#!/usr/bin/env python3
"""CSV validation for V3 migration.

Usage:
    ape run validate --chain mainnet --asset usd
    ape run validate --chain optimism --asset eth
"""

import click
from ape.cli import ape_cli_context

from src.config import get_asset_config, get_csv_path, get_supported_chains
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str) -> None:
    """Validate a migration CSV file for one asset type on one chain."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH
    csv_path = get_csv_path(chain, asset_type)

    click.echo(f"Validating {csv_path}...")

    if not csv_path.exists():
        click.echo(click.style(f"Error: file not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    asset_config = get_asset_config(chain, asset_type)
    token_decimals = asset_config.get("token_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, token_decimals=token_decimals)

    if not result.is_valid:
        click.echo("")
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)

    click.echo(click.style("\nValidation OK", fg="green"))
    click.echo(f"  Total positions: {result.total_positions}")
    click.echo(f"  Debt users:      {result.debt_count}")
    click.echo(f"  Credit users:    {result.credit_count}")
    click.echo(f"  Zero-debt:       {result.zero_debt_count}")
    click.echo(f"  Total deposit:   {result.total_deposit_wei:,} wei")
    click.echo(f"  Total mint:      {result.total_mint_wei:,} wei")
    click.echo(f"  Total credit:    {result.total_credit_wei:,} wei")
    click.echo(f"  Net burn:        {result.total_mint_wei - result.total_credit_wei:,} wei")
