import src.env  # Load .env on startup
#!/usr/bin/env python3
"""Step 5: Send alAsset credits to credit users.

Usage:
    ape run credit --chain mainnet --asset usd
    ape run credit --chain mainnet --asset usd --dry-run

Run AFTER `ape run distribute` has transferred all NFTs to users.
Credit users have zero debt but are owed alAssets (credit_amount_wei > 0).
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
from src.gas import create_credit_batches, format_batch_summary, verify_batch_gas_limits
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
    """Step 5: Send alAsset credits to credit users (zero-debt users owed alAssets)."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — CREDIT", fg="white", bold=True))
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

    # Validate CSV
    click.echo(click.style("\n[1/4] Validating CSV...", fg="cyan", bold=True))

    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)

    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        click.echo(click.style("Aborted: CSV validation failed.", fg="red"))
        raise SystemExit(1)

    credit_users = [p for p in result.positions if p.credit_amount_wei > 0]
    remaining_to_burn = result.total_mint_wei - result.total_credit_wei

    click.echo(click.style("Validation OK", fg="green"))
    click.echo(f"  Total positions:  {result.total_positions}")
    click.echo(f"  Credit users:     {len(credit_users)}")
    click.echo(f"  Total credit:     {result.total_credit_wei:,} wei")
    click.echo(f"  Total mint:       {result.total_mint_wei:,} wei")
    click.echo(f"  Remaining burn:   {remaining_to_burn:,} wei")

    if not credit_users:
        click.echo(click.style("No credit users found.", fg="yellow"))
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

    al_token = asset_config.get("al_token", "") or "0x" + "0" * 40

    # Build credit batches
    click.echo(click.style("\n[2/4] Building credit batches...", fg="cyan", bold=True))

    batches = create_credit_batches(
        credit_positions=credit_users,
        al_token_address=al_token,
        chain=chain,
    )

    ok, errors = verify_batch_gas_limits(batches, chain=chain)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(f"Credit batches: {len(batches)}", fg="green"))
    for batch in batches:
        click.echo(f"  Batch {batch.batch_number}: {len(batch.calls)} txns, {batch.total_gas:,} gas")
        if verbose:
            for call in batch.calls[:5]:
                click.echo(f"    {call.description[:90]}")
            if len(batch.calls) > 5:
                click.echo(f"    ... +{len(batch.calls) - 5} more")

    # Preview
    click.echo(click.style("\n[3/4] Batch summary...", fg="cyan", bold=True))
    click.echo(format_batch_summary(batches, chain=chain))

    # Confirm + Execute
    click.echo(click.style("\n[4/4] Confirmation...", fg="cyan", bold=True))
    if not yes:
        click.echo(
            click.style("\nWARNING: ", fg="red", bold=True) +
            f"About to propose {len(batches)} credit Safe tx(s) on {chain} ({asset_type.value}).\n"
            f"Sending alAssets to {len(credit_users)} credit users."
        )
        if dry_run:
            click.echo(click.style("DRY RUN: skipping actual submission.", fg="yellow"))
        elif not click.confirm("Proceed with credits?"):
            click.echo(click.style("Cancelled.", fg="yellow"))
            raise SystemExit(0)

    if dry_run:
        click.echo(click.style("\nDRY RUN: skipping Safe proposal.", fg="yellow"))
        for batch in batches:
            click.echo(
                f"  [credit   ] Batch {batch.batch_number}: "
                f"{len(batch.calls)} txns, {batch.total_gas:,} gas"
            )
        click.echo(click.style("\nDry run complete. Run without --dry-run to execute.", fg="blue"))
        return

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(batches, chain_id=chain_id)
    proposer = ProposeToSafe(safe_address=multisig, chain_id=chain_id)

    # Checkpoint mode: propose first batch, pause for verification, then continue
    all_results = []
    first_batch = [safe_txs[0]]
    remaining_batches = safe_txs[1:]

    click.echo(click.style(
        "\n[CHECKPOINT] Proposing first batch...", fg="yellow", bold=True
    ))
    first_results = proposer.propose_all_batches(first_batch)
    all_results.extend(first_results)

    first_ok = sum(
        1 for r in first_results if r.get("status") in ("success", "stubbed")
    )
    if first_ok == 0:
        click.echo(click.style("First batch proposal failed. Aborting.", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(
        "\n[CHECKPOINT] First batch proposed. Verify in Safe UI before continuing.",
        fg="yellow", bold=True,
    ))
    click.echo(f"  Safe: https://app.safe.global/transactions/queue?safe=eth:{multisig}")
    click.echo(f"  Verify: cross-reference the CSV data in the batch calldata.")
    click.echo(f"  Remaining batches: {len(remaining_batches)}")

    if not click.confirm(
        click.style("Verified first batch. Continue with remaining?", fg="yellow")
    ):
        click.echo(
            click.style(
                "Aborted. First batch still proposed — cancel in Safe UI if needed.",
                fg="red",
            )
        )
        raise SystemExit(1)

    if remaining_batches:
        click.echo(click.style("\nProposing remaining batches...", fg="cyan"))
        remaining_results = proposer.propose_all_batches(remaining_batches)
        all_results.extend(remaining_results)

    ok_count = sum(1 for r in all_results if r.get("status") in ("success", "stubbed"))
    fail_count = len(all_results) - ok_count

    status = (
        click.style("SUCCESS", fg="green", bold=True) if fail_count == 0
        else click.style(f"PARTIAL ({ok_count}/{len(all_results)})", fg="yellow", bold=True)
    )

    click.echo(f"\nStatus: {status}")
    click.echo(f"Proposed: {ok_count}/{len(all_results)} credit batches")
    click.echo(click.style(
        f"\nMigration complete. Multisig should burn remaining {remaining_to_burn:,} wei alAssets manually.",
        fg="cyan",
    ))

    if fail_count > 0:
        raise SystemExit(1)
