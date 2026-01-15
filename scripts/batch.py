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
from ape.cli import ape_cli_context

from src.config import (
    GAS_BATCH_LIMIT,
    GAS_HEADROOM_PERCENT,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    validate_chain_config,
)
from src.gas import (
    EFFECTIVE_GAS_LIMIT,
    calculate_batch_statistics,
    create_batches,
    format_batch_summary,
    verify_batch_gas_limits,
)
from src.validation import format_validation_errors, validate_csv_file


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
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show detailed batch breakdown",
)
@ape_cli_context()
def cli(cli_ctx, chain: str, dry_run: bool, verbose: bool) -> None:
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
    click.echo(f"Gas limit per batch: {EFFECTIVE_GAS_LIMIT:,} (16M with {GAS_HEADROOM_PERCENT}% buffer)")

    if dry_run:
        click.echo(click.style("Dry-run mode: No transactions will be created", fg="blue"))

    # Step 1: Validate and load CSV data
    click.echo("\nValidating CSV data...")
    validation_result = validate_csv_file(csv_path, chain)

    if not validation_result.is_valid:
        click.echo(click.style("CSV validation failed!", fg="red"))
        click.echo(format_validation_errors(validation_result.errors))
        raise SystemExit(1)

    positions = validation_result.positions
    click.echo(click.style(f"Validated {len(positions)} positions", fg="green"))
    click.echo(f"  - USD positions: {validation_result.usd_token_count}")
    click.echo(f"  - ETH positions: {validation_result.eth_token_count}")

    # Step 2: Get chain configuration for contract addresses
    chain_config = get_chain_config(chain)

    # Step 3: Create batches using greedy bin-packing
    click.echo("\nCreating transaction batches...")
    batches = create_batches(positions, chain, chain_config)

    # Step 4: Verify all batches are within gas limits
    all_valid, errors = verify_batch_gas_limits(batches)
    if not all_valid:
        click.echo(click.style("Batch verification failed!", fg="red"))
        for error in errors:
            click.echo(f"  - {error}")
        raise SystemExit(1)

    # Step 5: Calculate and display statistics
    stats = calculate_batch_statistics(batches)

    # Count transaction types
    deposit_count = len(positions)
    mint_count = len(positions)
    transfer_count = len(positions)

    click.echo("\n" + "=" * 60)
    click.echo("BATCHING SUMMARY")
    click.echo("=" * 60)
    click.echo(f"Chain: {chain}")
    click.echo(f"Gas limit per batch: {EFFECTIVE_GAS_LIMIT:,}")
    click.echo("")
    click.echo("Positions:")
    click.echo(f"  Total positions: {len(positions)}")
    click.echo(f"  USD positions: {validation_result.usd_token_count}")
    click.echo(f"  ETH positions: {validation_result.eth_token_count}")
    click.echo("")
    click.echo("Transactions:")
    click.echo(f"  Deposit transactions: {deposit_count}")
    click.echo(f"  Mint transactions: {mint_count}")
    click.echo(f"  Transfer transactions: {transfer_count}")
    click.echo(f"  Total transactions: {stats['total_transactions']}")
    click.echo("")
    click.echo("Batches:")
    click.echo(f"  Batch count: {stats['total_batches']}")
    click.echo(f"  Total gas: {stats['total_gas']:,}")
    click.echo(f"  Avg gas per batch: {stats['avg_gas_per_batch']:,}")
    click.echo(f"  Gas utilization: {stats['gas_utilization_percent']:.1f}%")

    if verbose:
        click.echo("")
        click.echo("Batch Breakdown:")
        for batch in batches:
            utilization = (batch.total_gas / EFFECTIVE_GAS_LIMIT) * 100
            click.echo(
                f"  Batch {batch.batch_number}: {len(batch.calls)} txns, "
                f"{batch.total_gas:,} gas ({utilization:.1f}% utilized)"
            )
            if verbose:
                # Show first few transactions in each batch
                for i, call in enumerate(batch.calls[:3]):
                    click.echo(f"    - {call.description[:60]}...")
                if len(batch.calls) > 3:
                    click.echo(f"    ... and {len(batch.calls) - 3} more")

    click.echo("=" * 60)
    click.echo(click.style("Batching complete!", fg="green"))
