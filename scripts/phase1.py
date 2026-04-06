#!/usr/bin/env python3
"""Script 1: Deposit MYT, create NFT positions, mint alAssets.

Usage:
    ape run phase1 --chain mainnet --asset usd
    ape run phase1 --chain mainnet --asset usd --dry-run
    ape run phase1 --chain mainnet --asset usd --yes

After this script completes:
  - All NFT positions exist on AlchemistV3, owned by the multisig.
  - alAssets are held in the multisig (total_mint_wei).
  - Team verifies positions match snapshot data before running phase2.
  - Read AlchemistV3PositionNFTMinted events to map user → tokenId
    and patch those IDs into the Script 2 transfer batches.
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    ChainConfigError,
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    validate_asset_config,
    verify_asset_config,
)
from src.gas import (
    build_migration_plan,
    verify_batch_gas_limits,
)
from src.preview import print_migration_plan
from src.safe import ProposeToSafe, format_safe_batch
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--skip-validation", is_flag=True, default=False)
@click.option("--skip-preview", is_flag=True, default=False)
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--yes", "-y", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@ape_cli_context()
def cli(
    cli_ctx,
    chain: str,
    asset: str,
    skip_validation: bool,
    skip_preview: bool,
    verbose: bool,
    yes: bool,
    dry_run: bool,
) -> None:
    """Script 1: deposit MYT + create positions + mint alAssets into multisig."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — SCRIPT 1: DEPOSIT + MINT", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain:  {click.style(chain, fg='cyan')}")
    click.echo(f"Asset:  {click.style(asset_type.value, fg='cyan')}")
    if dry_run:
        click.echo(click.style("Mode:   DRY RUN", fg="yellow"))

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]

    click.echo(f"Multisig: {multisig or click.style('<not configured>', fg='yellow')}")
    click.echo("-" * 70)

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"\nError: CSV not found: {csv_path}", fg="red"))
        raise SystemExit(1)
    click.echo(f"Data file: {csv_path}")

    # =========================================================================
    # Step 1: Validate CSV
    # =========================================================================
    click.echo(click.style("\n[1/4] Validating CSV...", fg="cyan", bold=True))

    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)

    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        click.echo(click.style("Aborted: CSV validation failed.", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("Validation OK", fg="green"))
    click.echo(f"  Total positions: {result.total_positions}")
    click.echo(f"  Debt users:      {result.debt_count}")
    click.echo(f"  Credit users:    {result.credit_count}")
    click.echo(f"  Zero-debt:       {result.zero_debt_count}")
    click.echo(f"  Total deposit:   {result.total_deposit_wei:,} wei")
    click.echo(f"  Total mint:      {result.total_mint_wei:,} wei")

    if not result.positions:
        click.echo(click.style("No positions found.", fg="yellow"))
        raise SystemExit(0)

    if not dry_run:
        try:
            verify_asset_config(chain, asset_type)
        except ChainConfigError as e:
            click.echo(click.style(f"\nError: {e}", fg="red"))
            click.echo(click.style("Use --dry-run to test without configured addresses.", fg="blue"))
            raise SystemExit(1)
    else:
        missing = validate_asset_config(chain, asset_type)
        if missing:
            click.echo(click.style(f"Warning: missing config: {', '.join(missing)}", fg="yellow"))

    alchemist = asset_config.get("alchemist", "") or "0x" + "0" * 40
    al_token = asset_config.get("al_token", "") or "0x" + "0" * 40
    nft = asset_config.get("nft", "") or "0x" + "0" * 40

    # =========================================================================
    # Step 2: Build plan
    # =========================================================================
    click.echo(click.style("\n[2/4] Building deposit plan...", fg="cyan", bold=True))

    plan = build_migration_plan(
        positions=result.positions,
        chain=chain,
        alchemist_address=alchemist,
        al_token_address=al_token,
        nft_address=nft,
        multisig=multisig,
        current_deposit_cap_wei=0,
    )

    ok, errors = verify_batch_gas_limits(plan.deposit_batches)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("Plan built:", fg="green"))
    click.echo(f"  Deposit batches: {len(plan.deposit_batches)}")

    # =========================================================================
    # Step 3: Preview
    # =========================================================================
    if not skip_preview:
        click.echo(click.style("\n[3/4] Preview...", fg="cyan", bold=True))
        print_migration_plan(plan, chain_config, asset_config, verbose=verbose)
    else:
        click.echo(click.style("\n[3/4] Skipping preview.", fg="yellow"))

    # =========================================================================
    # Step 4: Confirm + Execute
    # =========================================================================
    click.echo(click.style("\n[4/4] Confirmation...", fg="cyan", bold=True))
    if not yes:
        click.echo(
            click.style("\nWARNING: ", fg="red", bold=True) +
            f"About to propose {len(plan.deposit_batches)} deposit Safe tx(s) on "
            f"{chain} ({asset_type.value}).\n"
            f"NOTE: Token IDs in mint calls are PLACEHOLDERS (999999).\n"
            f"      Read AlchemistV3PositionNFTMinted events after execution\n"
            f"      and patch them into Script 2 transfer batches before signing."
        )
        if dry_run:
            click.echo(click.style("DRY RUN: skipping actual submission.", fg="yellow"))
        else:
            if not click.confirm("Proceed with Script 1?"):
                click.echo(click.style("Cancelled.", fg="yellow"))
                raise SystemExit(0)

    if dry_run:
        click.echo(click.style("\nDRY RUN: skipping Safe proposal.", fg="yellow"))
        for i, batch in enumerate(plan.deposit_batches, 1):
            click.echo(
                f"  [deposit ] Batch {i}: "
                f"{len(batch.calls)} txns, {batch.total_gas:,} gas"
            )
        click.echo(click.style("\nDry run complete. Run without --dry-run to execute.", fg="blue"))
        return

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(plan.deposit_batches, chain_id=chain_id)
    proposer = ProposeToSafe(safe_address=multisig, chain_id=chain_id)

    results = proposer.propose_all_batches(safe_txs)
    ok_count = sum(1 for r in results if r.get("status") in ("success", "stubbed"))
    fail_count = len(results) - ok_count

    status = (
        click.style("SUCCESS", fg="green", bold=True) if fail_count == 0
        else click.style(f"PARTIAL ({ok_count}/{len(results)})", fg="yellow", bold=True)
    )

    click.echo(f"\nStatus: {status}")
    click.echo(f"Proposed: {ok_count}/{len(results)} deposit batches")
    click.echo(
        click.style(
            "\nNext step: verify positions on-chain, then run `ape run phase2`.",
            fg="cyan",
        )
    )

    if fail_count > 0:
        raise SystemExit(1)
