#!/usr/bin/env python3
"""Show batching stats for a migration.

Usage:
    ape run batch --chain mainnet --asset usd
    ape run batch --chain mainnet --asset usd --verbose
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    EFFECTIVE_GAS_LIMIT,
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
)
from src.gas import (
    build_migration_plan,
    calculate_batch_statistics,
    format_batch_summary,
    verify_batch_gas_limits,
)
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str, verbose: bool) -> None:
    """Show batch statistics for a migration (no transactions submitted)."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"Error: {csv_path} not found", fg="red"))
        raise SystemExit(1)

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)
    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)
    multisig = chain_config["multisig"]
    alchemist = asset_config.get("alchemist") or "0x" + "0" * 40
    al_token = asset_config.get("al_token") or "0x" + "0" * 40

    plan = build_migration_plan(
        positions=result.positions,
        chain=chain,
        alchemist_address=alchemist,
        al_token_address=al_token,
        nft_address=asset_config.get("nft", "") or alchemist,
        multisig=multisig,
    )

    s1_batches = plan.deposit_batches
    s2_batches = (
        plan.credit_batches
        + plan.transfer_batches
        + ([plan.final_burn_batch] if plan.final_burn_batch else [])
    )
    all_batches = s1_batches + s2_batches

    ok, errors = verify_batch_gas_limits(all_batches)
    if not ok:
        for e in errors:
            click.echo(click.style(f"  {e}", fg="red"))
        raise SystemExit(1)

    click.echo(f"\nChain: {chain} | Asset: {asset_type.value}")
    click.echo(f"Gas target: {EFFECTIVE_GAS_LIMIT:,} per batch (90% of 16M)")

    click.echo(click.style("\nScript 1 — Deposit + Mint:", fg="cyan"))
    click.echo(format_batch_summary(s1_batches))

    click.echo(click.style("\nScript 2 — Distribute + Burn:", fg="cyan"))
    click.echo(format_batch_summary(s2_batches))

    if verbose:
        for batch in all_batches:
            click.echo(f"\n  [{batch.batch_type}] Batch {batch.batch_number}:")
            for i, call in enumerate(batch.calls[:10], 1):
                click.echo(f"    {i:3}. {call.description[:80]}")
            if len(batch.calls) > 10:
                click.echo(f"    ... +{len(batch.calls) - 10} more")
