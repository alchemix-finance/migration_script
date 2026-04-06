#!/usr/bin/env python3
"""Preview the full migration plan (no transactions submitted).

Usage:
    ape run migrate --chain mainnet --asset usd
    ape run migrate --chain mainnet --asset usd --verbose

The migration runs in 5 steps:
  1. ape run deposit    — deposit MYT, create NFT positions
  2. ape run read_ids   — read token IDs from deposit events
     ape run mint       — mint alAsset debt using real token IDs
  3. ape run verify     — verify positions match snapshot
  4. ape run distribute — send NFTs to users
  5. ape run credit     — send alAsset credit to credit users

Burn of remaining alAssets is handled manually by the multisig.
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
from src.gas import build_migration_plan, verify_batch_gas_limits
from src.preview import print_migration_plan
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str, verbose: bool) -> None:
    """Preview the full migration plan (no transactions submitted)."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    missing = validate_asset_config(chain, asset_type)
    if missing:
        click.echo(click.style(f"Warning: missing config: {', '.join(missing)} (using placeholders)", fg="yellow"))

    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)
    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)

    plan = build_migration_plan(
        positions=result.positions,
        chain=chain,
        alchemist_address=asset_config.get("alchemist", "") or "0x" + "0" * 40,
        al_token_address=asset_config.get("al_token", "") or "0x" + "0" * 40,
        nft_address=asset_config.get("nft", "") or "0x" + "0" * 40,
        multisig=chain_config["multisig"],
    )

    all_batches = (
        plan.deposit_batches + plan.mint_batches
        + plan.transfer_batches + plan.credit_batches
    )
    ok, errors = verify_batch_gas_limits(all_batches, chain=chain)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    print_migration_plan(plan, chain_config, asset_config, verbose=verbose)

    click.echo(click.style(
        "\nTo execute:\n"
        f"  1. ape run deposit    --chain {chain} --asset {asset}\n"
        f"  2. ape run read_ids   --chain {chain} --asset {asset} --from-block <N>\n"
        f"     ape run mint       --chain {chain} --asset {asset}\n"
        f"  3. ape run verify     --chain {chain} --asset {asset}\n"
        f"  4. ape run distribute --chain {chain} --asset {asset}\n"
        f"  5. ape run credit     --chain {chain} --asset {asset}",
        fg="cyan",
    ))
