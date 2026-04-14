import src.env  # load .env
#!/usr/bin/env python3
"""Phase B: Deposit underlying into the MYT vault; mints MYT shares to multisig.

Usage:
    ape run deposit_myt --chain arbitrum --asset eth --mode json
    ape run deposit_myt --chain arbitrum --asset eth --mode impersonate

Run AFTER Phase A (`ape run approve_underlying`), BEFORE Phase C (`ape run approve_myt`).
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
    compute_underlying_total,
    create_myt_deposit_batches,
    format_batch_summary,
    verify_batch_gas_limits,
)
from src.myt_config import MYT_CONFIG
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
    """Step 0b: MYT.deposit(assets, multisig) — mint MYT shares to the multisig."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH
    asset_slug = "alUSD" if asset_type == AssetType.USD else "alETH"

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — PHASE B (deposit underlying → MYT)", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain: {click.style(chain, fg='cyan')}  Asset: {click.style(asset_type.value, fg='cyan')}  Mode: {click.style(mode, fg='magenta', bold=True)}")

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]

    myt = asset_config["myt"]
    myt_info = MYT_CONFIG[chain][asset_slug]
    underlying_decimals = int(myt_info["underlying_decimals"])
    myt_decimals = int(asset_config.get("myt_decimals", 18))

    click.echo(f"Multisig: {multisig}")
    click.echo(f"MYT vault: {myt}")
    click.echo("-" * 70)

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("\n[1/3] Validating CSV...", fg="cyan", bold=True))
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)
    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)

    total_underlying = compute_underlying_total(
        result.positions, underlying_decimals=underlying_decimals, myt_decimals=myt_decimals,
    )
    click.echo(click.style("OK", fg="green") + f"  total underlying to deposit: {total_underlying:,}")

    if not dry_run:
        try:
            verify_asset_config(chain, asset_type)
        except ChainConfigError as e:
            click.echo(click.style(f"Config error: {e}", fg="red"))
            raise SystemExit(1)

    # Preflight: skip if MYT already on hand OR deposits already complete.
    try:
        from src.preflight import check_myt_balance_done, check_deposit_done
        dep_done, dep_msg, _ = check_deposit_done(
            chain=chain, nft_address=asset_config["nft"], multisig=multisig,
            expected_positions=result.total_positions,
        )
        click.echo(f"  preflight (deposits): {dep_msg}")
        if dep_done:
            click.echo(click.style("SKIPPED — deposits already complete; no more MYT needed.", fg="yellow", bold=True))
            return
        required_myt = result.total_deposit_wei
        done, msg, _current = check_myt_balance_done(
            chain=chain, myt=myt, multisig=multisig, required=required_myt,
        )
        click.echo(f"  preflight (MYT balance): {msg}")
        if done:
            click.echo(click.style("SKIPPED — multisig already holds enough MYT.", fg="yellow", bold=True))
            return
    except Exception as e:
        click.echo(click.style(f"  preflight check failed ({e}); proceeding.", fg="yellow"))

    click.echo(click.style("\n[2/3] Building MYT.deposit batch...", fg="cyan", bold=True))
    batches = create_myt_deposit_batches(
        myt_address=myt, multisig=multisig, assets_wei=total_underlying, chain=chain,
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
        chain=chain, asset_type=asset_type, step_name="deposit_myt",
    )
    results = executor.propose_all_batches(safe_txs)
    ok_count = sum(1 for r in results if r.get("status") in ("success", "stubbed"))
    status = click.style("SUCCESS", fg="green", bold=True) if ok_count == len(results) else click.style("PARTIAL", fg="yellow", bold=True)
    click.echo(f"\nStatus: {status}  ({ok_count}/{len(results)})")
    for r in results:
        if r.get("path"):
            click.echo(f"  JSON: {r['path']}")
