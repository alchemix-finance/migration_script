#!/usr/bin/env python3
"""Transaction preview script for CDP migration.

Usage:
    ape run preview --chain mainnet
    ape run preview --chain mainnet --verbose

This script generates a human-readable preview of all transactions
that would be executed during migration, including:
- Position summary (USD and ETH counts, totals)
- Transaction batches with gas estimates
- Individual transaction details (with --verbose)
- Batch overview and utilization statistics
"""

import click
from ape.cli import ape_cli_context

from src.config import get_chain_config, get_csv_path, get_supported_chains, validate_chain_config
from src.gas import create_batches
from src.preview import print_full_preview
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option(
    "--chain",
    type=click.Choice(get_supported_chains()),
    required=True,
    help="Chain to preview migration for",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show detailed transaction data",
)
@ape_cli_context()
def cli(cli_ctx, chain: str, verbose: bool) -> None:
    """Preview migration transactions for a specific chain.

    Displays:
    - Total positions to migrate (USD and ETH)
    - Position value summaries (collateral and debt)
    - Transaction batches with gas estimates
    - Individual transaction details (with --verbose)
    - Summary statistics
    """
    click.echo(f"Generating migration preview for {chain}...")
    click.echo("")

    # Check chain configuration
    missing_config = validate_chain_config(chain)
    if missing_config:
        click.echo(
            click.style(
                f"Warning: Chain config incomplete. Missing: {', '.join(missing_config)}",
                fg="yellow",
            )
        )
        click.echo(
            click.style(
                "Preview will use placeholder addresses.",
                fg="yellow",
            )
        )
        click.echo("")

    # Get CSV path
    csv_path = get_csv_path(chain)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV file not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    click.echo(f"CSV file: {csv_path}")

    # Step 1: Load and validate CSV
    click.echo("Validating CSV data...")
    result = validate_csv_file(csv_path, chain)

    if not result.is_valid:
        click.echo("")
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        raise SystemExit(1)

    if not result.positions:
        click.echo(click.style("No positions found in CSV file.", fg="yellow"))
        raise SystemExit(0)

    click.echo(
        click.style(
            f"Found {len(result.positions)} position(s) to migrate.",
            fg="green",
        )
    )

    # Step 2: Get chain config for contract addresses
    try:
        chain_config = get_chain_config(chain)
    except ValueError:
        # Use empty config if chain not found
        chain_config = {
            "chain_id": 0,
            "multisig": "",
            "cdp_usd": "",
            "cdp_eth": "",
            "nft_usd": "",
            "nft_eth": "",
            "collateral_usd": "",
            "collateral_eth": "",
        }

    # Step 3: Create transaction batches
    click.echo("Creating transaction batches...")
    batches = create_batches(result.positions, chain, chain_config)

    if not batches:
        click.echo(click.style("No batches created.", fg="yellow"))
        raise SystemExit(0)

    # Step 4: Print the full preview
    print_full_preview(
        chain=chain,
        positions=result.positions,
        batches=batches,
        chain_config=chain_config,
        verbose=verbose,
    )

    # Print usage hint
    click.echo("")
    if not verbose:
        click.echo(
            click.style(
                "Tip: Use --verbose to see individual transaction details.",
                fg="blue",
            )
        )
    click.echo(
        click.style(
            f"To execute: ape run migrate --chain {chain}",
            fg="blue",
        )
    )
