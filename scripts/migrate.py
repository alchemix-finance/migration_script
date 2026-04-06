#!/usr/bin/env python3
"""Migration entry point — delegates to phase1 and phase2.

The migration runs in four steps:

  1. ape run phase1    — deposit MYT, create NFT positions (no mint yet)
  2. ape run read_ids  — read AlchemistV3PositionNFTMinted events → token ID map
  3. ape run mint      — mint alAssets using real token IDs from the map
  4. ape run phase2    — send credits + NFTs to users, burn remaining alAssets

Run this script for a combined preview of all steps.
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
    """Preview the full two-script migration plan (no transactions submitted).

    To execute:
      Script 1:  ape run phase1 --chain <chain> --asset <asset>
      Script 2:  ape run phase2 --chain <chain> --asset <asset>
    """
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]

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

    alchemist = asset_config.get("alchemist", "") or "0x" + "0" * 40
    al_token = asset_config.get("al_token", "") or "0x" + "0" * 40
    nft = asset_config.get("nft", "") or "0x" + "0" * 40

    plan = build_migration_plan(
        positions=result.positions,
        chain=chain,
        alchemist_address=alchemist,
        al_token_address=al_token,
        nft_address=nft,
        multisig=multisig,
    )

    all_batches = (
        plan.deposit_batches + plan.mint_batches
        + plan.credit_batches + plan.transfer_batches
        + ([plan.final_burn_batch] if plan.final_burn_batch else [])
    )

    ok, errors = verify_batch_gas_limits(all_batches)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    click.echo(f"\nChain: {chain} | Asset: {asset_type.value}")

    print_migration_plan(plan, chain_config, asset_config, verbose=verbose)

    click.echo(click.style(
        "\nTo execute:\n"
        f"  1. ape run phase1 --chain {chain} --asset {asset}\n"
        f"  2. ape run read_ids --chain {chain} --asset {asset} --from-block <N>\n"
        f"  3. ape run mint --chain {chain} --asset {asset}\n"
        f"  4. (team verifies)\n"
        f"  5. ape run phase2 --chain {chain} --asset {asset}",
        fg="cyan",
    ))
