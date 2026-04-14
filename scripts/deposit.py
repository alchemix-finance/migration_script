import src.env  # Load .env on startup
#!/usr/bin/env python3
"""Phase 1: Deposit MYT and create NFT positions (no mint).

Usage:
    ape run deposit --chain mainnet --asset usd
    ape run deposit --chain mainnet --asset usd --dry-run

Proposes batches to the Safe one at a time: after each batch (except the last),
you can review the queue before confirming the next. Use `-y` to propose all
batches without those pauses.

After deposits execute on-chain, run `ape run read_ids` to capture token IDs.
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
    create_deposit_batches,
    format_batch_summary,
    verify_batch_gas_limits,
)
from src.executor import make_executor
from src.safe import ProposeToSafe, format_safe_batch  # ProposeToSafe kept for legacy --mode propose path
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--yes", "-y", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--skip-validation", is_flag=True, default=False)
@click.option("--mode", type=click.Choice(["json", "impersonate", "propose"]), default="json",
              help="json=emit Safe Builder JSON; impersonate=fork execute; propose=legacy API")
@ape_cli_context()
def cli(
    cli_ctx,
    chain: str,
    asset: str,
    verbose: bool,
    yes: bool,
    dry_run: bool,
    skip_validation: bool,
    mode: str,
) -> None:
    """Step 1: Deposit MYT to create NFT positions (minting is separate)."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — DEPOSIT", fg="white", bold=True))
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

    if not skip_validation:
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
    else:
        myt_decimals = asset_config.get("myt_decimals", 18)
        result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)
        click.echo(click.style("Skipped detailed validation.", fg="yellow"))

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

    # Read on-chain depositCap so we don't emit a setDepositCap that would
    # lower it (V3 alchemist reverts on downward changes).
    live_cap = 0
    try:
        from src.preflight import read_deposit_cap
        live_cap = read_deposit_cap(chain, alchemist)
        click.echo(f"  on-chain depositCap(): {live_cap:,} wei")
    except Exception as e:
        click.echo(click.style(f"  warning: could not read live depositCap ({e}); defaulting to 0", fg="yellow"))

    # Build deposit batches
    click.echo(click.style("\n[2/4] Building deposit batches...", fg="cyan", bold=True))

    batches = create_deposit_batches(
        positions=result.positions,
        alchemist_address=alchemist,
        multisig=multisig,
        chain=chain,
        current_deposit_cap_wei=live_cap,
    )

    ok, errors = verify_batch_gas_limits(batches, chain=chain)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(f"Deposit batches: {len(batches)}", fg="green"))
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

    n_plan = len(batches)
    if n_plan > 1:
        click.echo(
            click.style(
                "\nThe summary above is the full migration plan. "
                "Only ONE batch is proposed to the Safe at a time.",
                fg="cyan",
            )
        )
        if not yes:
            click.echo(
                click.style(
                    f"Next step (if you confirm below): propose batch 1/{n_plan} only — "
                    f"not all {n_plan} batches.",
                    fg="cyan",
                )
            )

    # Confirm + Execute
    click.echo(click.style("\n[4/4] Confirmation...", fg="cyan", bold=True))
    if not yes:
        click.echo(
            click.style("\nWARNING: ", fg="red", bold=True) +
            f"Deposit proposals on {chain} ({asset_type.value}). "
            f"{n_plan} Safe transaction(s) total, submitted one-by-one with a pause between each "
            f"(unless you used -y).\n"
            f"NOTE: This only creates NFT positions (no minting)."
        )
        if dry_run:
            click.echo(click.style("DRY RUN: skipping actual submission.", fg="yellow"))
        elif not click.confirm(
            f"Propose batch 1/{n_plan} to the Safe queue now?"
            if n_plan > 1
            else "Propose this deposit batch to the Safe queue now?"
        ):
            click.echo(click.style("Cancelled.", fg="yellow"))
            raise SystemExit(0)

    if dry_run:
        click.echo(click.style("\nDRY RUN: skipping Safe proposal.", fg="yellow"))
        for i, batch in enumerate(batches, 1):
            click.echo(
                f"  [deposit ] Batch {i}: "
                f"{len(batch.calls)} txns, {batch.total_gas:,} gas"
            )
        click.echo(click.style("\nDry run complete. Run without --dry-run to execute.", fg="blue"))
        return

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(batches, chain_id=chain_id)
    proposer = make_executor(
        mode, batches=batches, safe_address=multisig, chain_id=chain_id,
        chain=chain, asset_type=asset_type, step_name="deposit",
    )

    # Checkpoint mode: propose one batch at a time; pause for verification before each next batch.
    all_results: list = []
    n_batches = len(safe_txs)
    safe_url = f"https://app.safe.global/transactions/queue?safe=eth:{multisig}"

    for i, safe_tx in enumerate(safe_txs):
        if i > 0 and not yes:
            click.echo(click.style(
                f"\n[CHECKPOINT] Batches proposed so far: {i}/{n_batches}. "
                f"Review batch {i} in the Safe queue before continuing.",
                fg="yellow", bold=True,
            ))
            click.echo(f"  Safe: {safe_url}")
            if not click.confirm(
                click.style(f"Propose batch {i + 1}/{n_batches}?", fg="yellow")
            ):
                click.echo(click.style(
                    "Aborted. Earlier batches may already be in the Safe queue — cancel there if needed.",
                    fg="red",
                ))
                raise SystemExit(1)

        label = f"batch {i + 1}/{n_batches}" if n_batches > 1 else "batch"
        click.echo(click.style(f"\n[CHECKPOINT] Proposing {label}...", fg="yellow", bold=True))
        batch_results = proposer.propose_all_batches([safe_tx])
        all_results.extend(batch_results)

        ok = sum(1 for r in batch_results if r.get("status") in ("success", "stubbed"))
        if ok == 0:
            click.echo(click.style(f"Batch {i + 1} proposal failed. Aborting.", fg="red"))
            raise SystemExit(1)

        if i < n_batches - 1:
            click.echo(click.style(
                f"\n[CHECKPOINT] Batch {i + 1}/{n_batches} proposed. Verify in Safe UI.",
                fg="yellow", bold=True,
            ))
            click.echo(f"  Safe: {safe_url}")
            click.echo("  Verify: cross-reference the CSV data in the batch calldata.")

    ok_count = sum(1 for r in all_results if r.get("status") in ("success", "stubbed"))
    fail_count = len(all_results) - ok_count

    status = (
        click.style("SUCCESS", fg="green", bold=True) if fail_count == 0
        else click.style(f"PARTIAL ({ok_count}/{len(all_results)})", fg="yellow", bold=True)
    )

    click.echo(f"\nStatus: {status}")
    click.echo(f"Proposed: {ok_count}/{len(all_results)} deposit batches")
    click.echo(click.style(
        f"\nNext: run `ape run read_ids --chain {chain} --asset {asset} --from-block <N>` "
        f"to capture token IDs.",
        fg="cyan",
    ))

    if fail_count > 0:
        raise SystemExit(1)
