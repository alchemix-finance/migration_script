#!/usr/bin/env python3
"""Preview migration plan.

Usage:
    ape run preview --chain mainnet --asset usd
    ape run preview --chain mainnet --asset eth --verbose
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    validate_asset_config,
)
from src.gas import build_migration_plan
from src.preview import print_migration_plan
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str, verbose: bool) -> None:
    """Preview the full migration plan for one asset type on one chain."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"Error: {csv_path} not found", fg="red"))
        raise SystemExit(1)

    missing = validate_asset_config(chain, asset_type)
    if missing:
        click.echo(click.style(f"Warning: missing config: {', '.join(missing)} (using placeholders)", fg="yellow"))

    result = validate_csv_file(csv_path, chain, asset_type)
    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]

    alchemist = asset_config.get("alchemist") or "0x" + "0" * 40
    al_token = asset_config.get("al_token") or "0x" + "0" * 40
    nft = alchemist

    plan = build_migration_plan(
        positions=result.positions,
        chain=chain,
        alchemist_address=alchemist,
        al_token_address=al_token,
        nft_address=nft,
        multisig=multisig,
    )

    print_migration_plan(plan, chain_config, asset_config, verbose=verbose)
