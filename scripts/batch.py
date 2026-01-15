#!/usr/bin/env python3
"""Transaction batching script for CDP migration.

Usage:
    ape run batch --chain mainnet

This script handles the gas-optimized batching of migration transactions:
- Estimates gas for each transaction type
- Uses greedy bin-packing to maximize batch efficiency
- Stays under 16M gas limit with 5% safety buffer
- Outputs batch statistics
"""

import click
from ape import project
from ape.cli import ape_cli_context

from src.config import (
    GAS_BATCH_LIMIT,
    GAS_HEADROOM_PERCENT,
    get_csv_path,
    get_supported_chains,
    validate_chain_config,
)


@click.command()
@click.option(
    "--chain",
    type=click.Choice(get_supported_chains()),
    required=True,
    help="Chain to batch transactions for",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="Only calculate batches, don't create Safe transactions",
)
@ape_cli_context()
def cli(cli_ctx, chain: str, dry_run: bool) -> None:
    """Calculate optimal transaction batches for migration.

    This script:
    1. Loads validated CSV data
    2. Builds all required transactions (deposit, mint, transfer)
    3. Estimates gas for each transaction
    4. Groups transactions into batches under gas limit
    5. Reports batch statistics

    By default, runs in dry-run mode (no actual transactions created).
    """
    click.echo(f"Calculating transaction batches for {chain}...")

    # Check chain configuration
    missing_config = validate_chain_config(chain)
    if missing_config:
        click.echo(
            click.style(
                f"Warning: Chain config incomplete. Missing: {', '.join(missing_config)}",
                fg="yellow",
            )
        )

    # Get CSV path
    csv_path = get_csv_path(chain)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV file not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    click.echo(f"CSV file: {csv_path}")
    click.echo(f"Gas limit per batch: {GAS_BATCH_LIMIT:,}")
    click.echo(f"Headroom: {GAS_HEADROOM_PERCENT}%")

    if dry_run:
        click.echo(click.style("Dry-run mode: No transactions will be created", fg="blue"))

    # TODO: Implement batching in PR 3
    # - Load CSV positions
    # - Build transaction objects
    # - Estimate gas per transaction
    # - Apply greedy bin-packing algorithm
    # - Output batch breakdown

    click.echo(click.style("Batching not yet implemented (PR 3)", fg="yellow"))

    # Placeholder output
    click.echo("\n" + "=" * 50)
    click.echo("BATCHING SUMMARY")
    click.echo("=" * 50)
    click.echo(f"Chain: {chain}")
    click.echo(f"Gas limit: {GAS_BATCH_LIMIT:,}")
    click.echo("Total transactions: <pending>")
    click.echo("Deposit transactions: <pending>")
    click.echo("Mint transactions: <pending>")
    click.echo("Transfer transactions: <pending>")
    click.echo("Batch count: <pending>")
    click.echo("=" * 50)
