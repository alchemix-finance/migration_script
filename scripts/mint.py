#!/usr/bin/env python3
"""Mint alAssets against NFT positions using real token IDs.

Usage:
    ape run mint --chain mainnet --asset usd
    ape run mint --chain mainnet --asset usd --dry-run

Run AFTER:
  1. `ape run phase1` (deposits) has fully executed on-chain
  2. `ape run read_ids --from-block N` has written the token ID mapping

Reads token_ids-{asset}-{chain}.json and builds mint(tokenId, amount, multisig)
batches for all positions with mint_amount_wei > 0 (debt + credit users).
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    ChainConfigError,
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    load_token_id_map,
    validate_asset_config,
    verify_asset_config,
)
from src.gas import create_mint_batches, verify_batch_gas_limits
from src.safe import ProposeToSafe, format_safe_batch
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--yes", "-y", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@ape_cli_context()
def cli(
    cli_ctx,
    chain: str,
    asset: str,
    verbose: bool,
    yes: bool,
    dry_run: bool,
) -> None:
    """Mint alAssets against positions using real token IDs from read_ids."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — MINT", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain:  {click.style(chain, fg='cyan')}")
    click.echo(f"Asset:  {click.style(asset_type.value, fg='cyan')}")
    if dry_run:
        click.echo(click.style("Mode:   DRY RUN", fg="yellow"))

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]

    # Load token ID mapping
    try:
        token_id_map = load_token_id_map(chain, asset_type)
    except FileNotFoundError as e:
        click.echo(click.style(f"\nError: {e}", fg="red"))
        raise SystemExit(1)

    click.echo(f"Loaded {len(token_id_map)} token IDs from mapping")

    # Validate CSV
    csv_path = get_csv_path(chain, asset_type)
    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)
    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)

    mintable = [p for p in result.positions if p.mint_amount_wei > 0]
    click.echo(f"Positions to mint: {len(mintable)}")
    click.echo(f"  Total mint: {result.total_mint_wei:,} wei")

    if not mintable:
        click.echo(click.style("No positions need minting.", fg="yellow"))
        raise SystemExit(0)

    # Verify all mintable positions have token IDs
    missing = [p.user_address for p in mintable if p.user_address.lower() not in token_id_map]
    if missing:
        click.echo(click.style(f"Error: {len(missing)} positions missing token IDs:", fg="red"))
        for addr in missing[:5]:
            click.echo(f"  {addr}")
        raise SystemExit(1)

    if not dry_run:
        try:
            verify_asset_config(chain, asset_type)
        except ChainConfigError as e:
            click.echo(click.style(f"\nError: {e}", fg="red"))
            raise SystemExit(1)

    alchemist = asset_config.get("alchemist", "") or "0x" + "0" * 40

    # Build mint batches
    batches = create_mint_batches(
        result.positions, alchemist, multisig, token_id_map,
    )

    ok, errors = verify_batch_gas_limits(batches)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(f"\nMint batches: {len(batches)}", fg="green"))
    for batch in batches:
        click.echo(f"  Batch {batch.batch_number}: {len(batch.calls)} txns, {batch.total_gas:,} gas")
        if verbose:
            for call in batch.calls[:5]:
                click.echo(f"    {call.description[:90]}")
            if len(batch.calls) > 5:
                click.echo(f"    ... +{len(batch.calls) - 5} more")

    if not yes:
        click.echo(
            click.style("\nWARNING: ", fg="red", bold=True) +
            f"About to propose {len(batches)} mint Safe tx(s) on {chain} ({asset_type.value})."
        )
        if dry_run:
            click.echo(click.style("DRY RUN: skipping.", fg="yellow"))
        elif not click.confirm("Proceed?"):
            click.echo(click.style("Cancelled.", fg="yellow"))
            raise SystemExit(0)

    if dry_run:
        click.echo(click.style("\nDry run complete.", fg="blue"))
        return

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(batches, chain_id=chain_id)
    proposer = ProposeToSafe(safe_address=multisig, chain_id=chain_id)

    results = proposer.propose_all_batches(safe_txs)
    ok_count = sum(1 for r in results if r.get("status") in ("success", "stubbed"))
    fail_count = len(results) - ok_count

    status = (
        click.style("SUCCESS", fg="green", bold=True) if fail_count == 0
        else click.style(f"PARTIAL ({ok_count}/{len(results)})", fg="yellow", bold=True)
    )
    click.echo(f"\nStatus: {status}")
    click.echo(f"Proposed: {ok_count}/{len(results)} mint batches")
    click.echo(click.style(
        "\nNext: team verifies positions, then `ape run phase2`.",
        fg="cyan",
    ))

    if fail_count > 0:
        raise SystemExit(1)
