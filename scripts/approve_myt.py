import src.env  # load .env
#!/usr/bin/env python3
"""Phase C: Approve the Alchemist to pull MYT shares from the multisig.

Usage:
    ape run approve_myt --chain arbitrum --asset eth --mode json
    ape run approve_myt --chain arbitrum --asset eth --mode impersonate

Run AFTER Phase B (`ape run deposit_myt`), BEFORE Phase 1 (`ape run deposit`).
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    ChainConfigError,
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    verify_asset_config,
)
from src.executor import make_executor
from src.gas import (
    create_approve_myt_batches,
    format_batch_summary,
    verify_batch_gas_limits,
)
from src.safe import format_safe_batch
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--mode", type=click.Choice(["json", "impersonate", "propose"]), default="json")
@click.option("--yes", "-y", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--verbose", "-v", is_flag=True, default=False)
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str, mode: str, yes: bool, dry_run: bool, verbose: bool) -> None:
    """Step 0c: Approve MYT → Alchemist (lets Alchemist pull MYT during deposit step)."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — PHASE C (approve MYT → Alchemist)", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain: {click.style(chain, fg='cyan')}  Asset: {click.style(asset_type.value, fg='cyan')}  Mode: {click.style(mode, fg='magenta', bold=True)}")

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]
    myt = asset_config["myt"]
    alchemist = asset_config["alchemist"]
    myt_decimals = int(asset_config.get("myt_decimals", 18))

    click.echo(f"Multisig: {multisig}")
    click.echo(f"MYT:      {myt}")
    click.echo(f"Alchemist: {alchemist}")
    click.echo("-" * 70)

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("\n[1/3] Validating CSV & computing total MYT...", fg="cyan", bold=True))
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)
    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)
    total_myt = result.total_deposit_wei
    click.echo(click.style("OK", fg="green") + f"  total MYT to approve: {total_myt:,}")

    if not dry_run:
        try:
            verify_asset_config(chain, asset_type)
        except ChainConfigError as e:
            click.echo(click.style(f"Config error: {e}", fg="red"))
            raise SystemExit(1)

    # Preflight: skip if allowance already covers required OR deposits done.
    try:
        from src.preflight import check_approve_myt_done, check_deposit_done
        dep_done, dep_msg, _ = check_deposit_done(
            chain=chain, nft_address=asset_config["nft"], multisig=multisig,
            expected_positions=result.total_positions,
        )
        click.echo(f"  preflight (deposits): {dep_msg}")
        if dep_done:
            click.echo(click.style("SKIPPED — deposits already complete; approval no longer needed.", fg="yellow", bold=True))
            return
        done, msg, _current = check_approve_myt_done(
            chain=chain, myt=myt, multisig=multisig, alchemist=alchemist, required=total_myt,
        )
        click.echo(f"  preflight (allowance): {msg}")
        if done:
            click.echo(click.style("SKIPPED — allowance already satisfies requirement.", fg="yellow", bold=True))
            return
    except Exception as e:
        click.echo(click.style(f"  preflight check failed ({e}); proceeding.", fg="yellow"))

    click.echo(click.style("\n[2/3] Building approve batch...", fg="cyan", bold=True))
    batches = create_approve_myt_batches(
        myt_address=myt, alchemist_address=alchemist, amount_wei=total_myt, chain=chain,
    )
    ok, errors = verify_batch_gas_limits(batches, chain=chain)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)
    click.echo(format_batch_summary(batches, chain=chain))

    click.echo(click.style("\n[3/3] Execution...", fg="cyan", bold=True))
    if dry_run:
        click.echo(click.style("DRY RUN — not submitting.", fg="yellow"))
        return
    if not yes and not click.confirm(f"Proceed with {mode}?"):
        click.echo("Cancelled.")
        raise SystemExit(0)

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(batches, chain_id=chain_id)
    executor = make_executor(
        mode,  # type: ignore[arg-type]
        batches=batches, safe_address=multisig, chain_id=chain_id,
        chain=chain, asset_type=asset_type, step_name="approve_myt",
    )
    results = executor.propose_all_batches(safe_txs)
    ok_count = sum(1 for r in results if r.get("status") in ("success", "stubbed"))
    status = click.style("SUCCESS", fg="green", bold=True) if ok_count == len(results) else click.style("PARTIAL", fg="yellow", bold=True)
    click.echo(f"\nStatus: {status}  ({ok_count}/{len(results)})")
    for r in results:
        if r.get("path"):
            click.echo(f"  JSON: {r['path']}")
