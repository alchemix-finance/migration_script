"""Human-readable preview of the migration plan."""

from decimal import Decimal

import click

from src.config import EFFECTIVE_GAS_LIMIT, ChainConfig
from src.gas import calculate_batch_statistics
from src.types import AssetConfig, MigrationPlan, TransactionBatch

LINE = "=" * 70
SUB = "-" * 70


def _fmt_wei(wei: int, decimals: int = 18) -> str:
    if wei == 0:
        return "0"
    val = Decimal(wei) / Decimal(10 ** decimals)
    s = f"{val:.6f}".rstrip("0").rstrip(".")
    parts = s.split(".")
    int_part = f"{int(parts[0]):,}"
    return f"{int_part}.{parts[1]}" if len(parts) > 1 else int_part


def _fmt_gas(gas: int) -> str:
    return f"{gas:,}"


def _addr(a: str) -> str:
    if not a or a == "0x" + "0" * 40:
        return click.style("<TBD>", fg="yellow")
    return f"{a[:6]}...{a[-4:]}"


def _batch_row(batch: TransactionBatch) -> str:
    util = (batch.total_gas / EFFECTIVE_GAS_LIMIT) * 100
    color = "green" if util < 80 else "yellow" if util < 95 else "red"
    type_label = click.style(f"{batch.batch_type:8}", fg="cyan")
    util_label = click.style(f"{util:5.1f}%", fg=color)
    return (
        f"  {type_label} Batch {batch.batch_number:3}: "
        f"{len(batch.calls):4} txns | "
        f"{_fmt_gas(batch.total_gas):>12} gas | {util_label}"
    )


def print_migration_plan(
    plan: MigrationPlan,
    chain_config: "ChainConfig",
    asset_config: "AssetConfig",
    verbose: bool = False,
) -> None:
    """Print a full human-readable preview of the migration plan."""
    click.echo(f"\n{LINE}")
    click.echo(click.style("MIGRATION PLAN", fg="white", bold=True))
    click.echo(LINE)
    click.echo(f"Chain:        {click.style(plan.chain, fg='cyan')}")
    click.echo(f"Asset type:   {click.style(plan.asset_type.value, fg='cyan')}")
    click.echo(f"Multisig:     {_addr(chain_config['multisig'])}")
    click.echo(f"Alchemist:    {_addr(asset_config.get('alchemist', ''))}")
    click.echo(f"alToken:      {_addr(asset_config.get('al_token', ''))}")
    click.echo(f"MYT:          {_addr(asset_config.get('myt', ''))}")

    click.echo(f"\n{SUB}")
    click.echo(click.style("Position Summary", fg="white", bold=True))
    click.echo(SUB)
    click.echo(f"  Total positions:  {len(plan.positions)}")
    click.echo(f"  Debt users:       {len(plan.debt_users)}   (deposit + mint; multisig burns remainder in Script 2)")
    click.echo(f"  Credit users:     {len(plan.credit_users)}   (deposit + mint; receive alAssets in Script 2)")
    click.echo(f"  Zero-debt users:  {len(plan.zero_debt_users)}   (deposit only)")
    click.echo(f"  Total deposit:    {_fmt_wei(plan.total_deposit_wei)}")
    click.echo(f"  Total minted:     {_fmt_wei(plan.total_mint_wei)}")
    click.echo(f"  Total credit out: {_fmt_wei(plan.total_credit_wei)}")
    click.echo(f"  Net to burn:      {_fmt_wei(plan.total_burn_wei)}")

    all_batches = (
        plan.deposit_batches + plan.mint_batches
        + plan.credit_batches + plan.transfer_batches
        + ([plan.final_burn_batch] if plan.final_burn_batch else [])
    )

    def _print_batch_section(name, batches):
        if not batches:
            click.echo(f"\n  {name}: (none)")
            return
        stats = calculate_batch_statistics(batches)
        click.echo(
            f"\n  {click.style(name, fg='white', bold=True)} "
            f"— {stats['total_batches']} batch(es), "
            f"{stats['total_transactions']} txns, "
            f"{_fmt_gas(stats['total_gas'])} total gas"
        )
        for batch in batches:
            click.echo(_batch_row(batch))
            if verbose:
                for call in batch.calls[:5]:
                    click.echo(f"      • {call.description[:80]}")
                if len(batch.calls) > 5:
                    click.echo(f"      ... +{len(batch.calls) - 5} more")

    click.echo(f"\n{SUB}")
    click.echo(click.style("Step 1 — Deposit (phase1)", fg="white", bold=True))
    click.echo(SUB)
    _print_batch_section("Deposit", plan.deposit_batches)

    click.echo(f"\n{SUB}")
    click.echo(click.style("Step 2 — Read token IDs (read_ids)", fg="white", bold=True))
    click.echo(SUB)
    click.echo("  Run `ape run read_ids --from-block N` after deposits execute.")

    click.echo(f"\n{SUB}")
    click.echo(click.style("Step 3 — Mint (mint)", fg="white", bold=True))
    click.echo(SUB)
    _print_batch_section("Mint", plan.mint_batches)
    if not plan.mint_batches:
        click.echo("  (requires token ID map — run read_ids first)")

    click.echo(f"\n{SUB}")
    click.echo(click.style("Step 4 — Distribute + Burn (phase2)  [after team verification]", fg="white", bold=True))
    click.echo(SUB)
    _print_batch_section("Credit Distribution", plan.credit_batches)
    _print_batch_section("NFT Transfer", plan.transfer_batches)

    if plan.final_burn_batch:
        b = plan.final_burn_batch
        click.echo(f"\n  {click.style('Final Burn', fg='white', bold=True)} — 1 batch, 1 txn")
        click.echo(_batch_row(b))
        if verbose and b.calls:
            click.echo(f"      • {b.calls[0].description[:80]}")
    else:
        click.echo("\n  Final Burn: (nothing to burn — no debt users)")

    total_stats = calculate_batch_statistics(all_batches)
    click.echo(f"\n{SUB}")
    click.echo(click.style("Totals", fg="white", bold=True))
    click.echo(SUB)
    click.echo(f"  Deposit Safe txns:  {len(plan.deposit_batches)}")
    click.echo(f"  Mint Safe txns:     {len(plan.mint_batches)}")
    click.echo(f"  Phase2 Safe txns:   {len(plan.credit_batches) + len(plan.transfer_batches) + (1 if plan.final_burn_batch else 0)}")
    click.echo(f"  Total Safe txns:    {total_stats['total_batches']}")
    click.echo(f"  Total calls:        {total_stats['total_transactions']}")
    click.echo(f"  Total gas:          {_fmt_gas(total_stats['total_gas'])}")
    click.echo(f"  Gas limit/batch:    {_fmt_gas(EFFECTIVE_GAS_LIMIT)} (90% of 16M)")
    click.echo(f"  Remaining to burn:  {_fmt_wei(plan.total_burn_wei)}")
    click.echo(LINE)
