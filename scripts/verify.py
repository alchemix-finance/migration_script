#!/usr/bin/env python3
"""Step 3: Verify positions before distribution.

Usage:
    ape run verify --chain mainnet --asset usd

Checks that the CSV data and token ID map are consistent and ready
for distribution. Does NOT read on-chain state.
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    get_asset_config,
    get_csv_path,
    get_supported_chains,
    load_token_id_map,
)
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str) -> None:
    """Step 3: Verify positions and token ID map before distribution."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — VERIFY", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain:  {click.style(chain, fg='cyan')}")
    click.echo(f"Asset:  {click.style(asset_type.value, fg='cyan')}")
    click.echo("-" * 70)

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"\nError: CSV not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    asset_config = get_asset_config(chain, asset_type)
    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)

    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        click.echo(click.style("Aborted: CSV validation failed.", fg="red"))
        raise SystemExit(1)

    if not result.positions:
        click.echo(click.style("No positions found.", fg="yellow"))
        raise SystemExit(0)

    # Load token ID map
    try:
        token_id_map = load_token_id_map(chain, asset_type)
    except FileNotFoundError as e:
        click.echo(click.style(f"\nError: {e}", fg="red"))
        raise SystemExit(1)

    click.echo(f"Loaded {len(token_id_map)} token IDs from mapping")

    # Classify positions
    debt_users = [p for p in result.positions if p.mint_amount_wei > 0 and p.credit_amount_wei == 0]
    credit_users = [p for p in result.positions if p.mint_amount_wei == 0 and p.credit_amount_wei > 0]
    zero_debt_users = [p for p in result.positions if p.mint_amount_wei == 0 and p.credit_amount_wei == 0]

    errors = []

    # (a) Every CSV position has a token ID in the map
    missing_ids = [p.user_address for p in result.positions if p.user_address.lower() not in token_id_map]
    if missing_ids:
        errors.append(f"{len(missing_ids)} positions missing token IDs")
        for addr in missing_ids[:5]:
            errors.append(f"  {addr}")

    # (b) Count of token IDs matches count of positions
    if len(token_id_map) != len(result.positions):
        errors.append(
            f"Token ID count ({len(token_id_map)}) != position count ({len(result.positions)})"
        )

    # (c) Debt users: mint_amount_wei > 0, credit_amount_wei = 0
    bad_debt = [p for p in debt_users if p.credit_amount_wei != 0]
    if bad_debt:
        errors.append(f"{len(bad_debt)} debt users have non-zero credit_amount_wei")

    # (d) Credit users: mint_amount_wei = 0, credit_amount_wei > 0
    bad_credit = [p for p in credit_users if p.mint_amount_wei != 0]
    if bad_credit:
        errors.append(f"{len(bad_credit)} credit users have non-zero mint_amount_wei")

    # (e) Zero-debt users: mint_amount_wei = 0, credit_amount_wei = 0
    bad_zero = [p for p in zero_debt_users if p.mint_amount_wei != 0 or p.credit_amount_wei != 0]
    if bad_zero:
        errors.append(f"{len(bad_zero)} zero-debt users have unexpected amounts")

    # (f) total_mint_wei >= total_credit_wei
    if result.total_mint_wei < result.total_credit_wei:
        errors.append(
            f"total_mint_wei ({result.total_mint_wei:,}) < total_credit_wei ({result.total_credit_wei:,})"
        )

    if errors:
        click.echo(click.style("\nVerification FAILED:", fg="red", bold=True))
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    # Summary table
    remaining_to_burn = result.total_mint_wei - result.total_credit_wei

    click.echo(click.style("\nPosition Summary", fg="cyan", bold=True))
    click.echo("-" * 50)
    click.echo(f"  Debt users:      {len(debt_users):>6}  (mint > 0, credit = 0)")
    click.echo(f"  Credit users:    {len(credit_users):>6}  (mint = 0, ZERO debt, credit > 0)")
    click.echo(f"  Zero-debt users: {len(zero_debt_users):>6}  (mint = 0, credit = 0)")
    click.echo(f"  Total:           {len(result.positions):>6}")
    click.echo("-" * 50)
    click.echo(f"  Total mint:      {result.total_mint_wei:>26,} wei")
    click.echo(f"  Total credit:    {result.total_credit_wei:>26,} wei")
    click.echo(f"  Remaining burn:  {remaining_to_burn:>26,} wei")
    click.echo("-" * 50)

    click.echo(click.style("\nVerification OK.", fg="green", bold=True))
    click.echo(click.style(
        f"Next: run `ape run distribute --chain {chain} --asset {asset}` "
        f"then `ape run credit --chain {chain} --asset {asset}`",
        fg="cyan",
    ))
