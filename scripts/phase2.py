#!/usr/bin/env python3
"""Script 2: Distribute credits, transfer NFTs, burn remaining alAssets.

Usage:
    ape run phase2 --chain mainnet --asset usd
    ape run phase2 --chain mainnet --asset usd --dry-run
    ape run phase2 --chain mainnet --asset usd --burn-fallback   # transfer to 0x000... instead

Run ONLY after:
  1. `ape run phase1` (deposits) has fully executed on-chain.
  2. `ape run read_ids` has captured the token ID mapping.
  3. `ape run mint` has minted alAssets using real token IDs.
  4. Team has verified all positions match the snapshot data.

Order of operations:
  a. Credit distribution — alToken.transfer(user, amount) for each credit user
  b. NFT transfers       — ERC721.transferFrom(multisig, user, tokenId) for all users
  c. Final burn          — alToken.burn(remaining) on the alToken contract directly
                           (remaining = total minted − credits sent to users)
                           Fallback: alToken.transfer(0x000...000, remaining)
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
@click.option(
    "--burn-fallback",
    is_flag=True,
    default=False,
    help="Use alToken.transfer(0x000...000, amount) instead of alToken.burn(amount).",
)
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
    burn_fallback: bool,
) -> None:
    """Script 2: send credits + NFTs to users, then burn remaining alAssets."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style(
        "ALCHEMIX V3 MIGRATION — SCRIPT 2: DISTRIBUTE + BURN",
        fg="white", bold=True,
    ))
    click.echo("=" * 70)
    click.echo(f"Chain:  {click.style(chain, fg='cyan')}")
    click.echo(f"Asset:  {click.style(asset_type.value, fg='cyan')}")
    if dry_run:
        click.echo(click.style("Mode:   DRY RUN", fg="yellow"))
    if burn_fallback:
        click.echo(click.style("Burn:   FALLBACK (transfer to 0x000...000)", fg="yellow"))
    else:
        click.echo("Burn:   alToken.burn() (primary)")

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
    click.echo(f"  Credit users:    {result.credit_count}")
    click.echo(f"  Total credit:    {result.total_credit_wei:,} wei")
    click.echo(f"  Total mint:      {result.total_mint_wei:,} wei")
    click.echo(f"  Remaining burn:  {result.total_mint_wei - result.total_credit_wei:,} wei")

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

    # Load token ID mapping (required for NFT transfers)
    if not dry_run:
        try:
            token_id_map = load_token_id_map(chain, asset_type)
        except FileNotFoundError as e:
            click.echo(click.style(f"\nError: {e}", fg="red"))
            raise SystemExit(1)
        click.echo(f"Loaded {len(token_id_map)} token IDs from mapping")
    else:
        try:
            token_id_map = load_token_id_map(chain, asset_type)
            click.echo(f"Loaded {len(token_id_map)} token IDs from mapping")
        except FileNotFoundError:
            token_id_map = None
            click.echo(click.style("Warning: no token ID map — transfers will use placeholder 999999", fg="yellow"))

    # =========================================================================
    # Step 2: Build plan
    # =========================================================================
    click.echo(click.style("\n[2/4] Building distribution plan...", fg="cyan", bold=True))

    plan = build_migration_plan(
        positions=result.positions,
        chain=chain,
        alchemist_address=alchemist,
        al_token_address=al_token,
        nft_address=nft,
        multisig=multisig,
        use_burn_fallback=burn_fallback,
        token_id_map=token_id_map,
    )

    s2_batches = (
        plan.credit_batches
        + plan.transfer_batches
        + ([plan.final_burn_batch] if plan.final_burn_batch else [])
    )

    ok, errors = verify_batch_gas_limits(s2_batches)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    burn_label = (
        "alToken.transfer(0x000...000, ...)" if burn_fallback
        else "alToken.burn(...)"
    )
    click.echo(click.style("Plan built:", fg="green"))
    click.echo(f"  Credit batches:   {len(plan.credit_batches)}")
    click.echo(f"  Transfer batches: {len(plan.transfer_batches)}")
    click.echo(f"  Final burn:       {'1 batch — ' + burn_label if plan.final_burn_batch else 'none'}")
    click.echo(f"  Total Safe txns:  {len(s2_batches)}")

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
            f"About to propose {len(s2_batches)} Safe tx(s) on {chain} ({asset_type.value}).\n"
            f"  • Credit transfers: {len(plan.credit_batches)} batch(es)\n"
            f"  • NFT transfers:    {len(plan.transfer_batches)} batch(es)\n"
            f"  • Final burn:       {burn_label}\n"
            f"\nEnsure Script 1 is complete and positions are verified before proceeding."
        )
        if dry_run:
            click.echo(click.style("DRY RUN: skipping actual submission.", fg="yellow"))
        else:
            if not click.confirm("Proceed with Script 2?"):
                click.echo(click.style("Cancelled.", fg="yellow"))
                raise SystemExit(0)

    if dry_run:
        click.echo(click.style("\nDRY RUN: skipping Safe proposal.", fg="yellow"))
        for batch in s2_batches:
            click.echo(
                f"  [{batch.batch_type:10}] Batch {batch.batch_number}: "
                f"{len(batch.calls)} txns, {batch.total_gas:,} gas"
            )
        click.echo(click.style("\nDry run complete. Run without --dry-run to execute.", fg="blue"))
        return

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(s2_batches, chain_id=chain_id)
    proposer = ProposeToSafe(safe_address=multisig, chain_id=chain_id)

    results = proposer.propose_all_batches(safe_txs)
    ok_count = sum(1 for r in results if r.get("status") in ("success", "stubbed"))
    fail_count = len(results) - ok_count

    status = (
        click.style("SUCCESS", fg="green", bold=True) if fail_count == 0
        else click.style(f"PARTIAL ({ok_count}/{len(results)})", fg="yellow", bold=True)
    )

    click.echo(f"\nStatus: {status}")
    click.echo(f"Proposed: {ok_count}/{len(results)} Script 2 batches")

    if fail_count > 0:
        raise SystemExit(1)
