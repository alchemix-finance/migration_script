#!/usr/bin/env python3
"""Main migration script for CDP positions.

Usage:
    ape run migrate --chain mainnet
    ape run migrate --chain mainnet --yes  # Skip confirmation
    ape run migrate --chain mainnet --verbose  # Detailed output

This is the main entry point for executing CDP migrations.
It orchestrates the full migration flow:
1. Validate CSV data
2. Build transaction batches
3. Preview transactions
4. Prompt for confirmation
5. Convert to Safe transactions and propose
6. Report results
"""

import click
from ape.cli import ape_cli_context

from src.config import get_chain_config, get_csv_path, get_supported_chains, validate_chain_config
from src.gas import calculate_batch_statistics, create_batches
from src.preview import (
    format_confirmation_prompt,
    format_execution_progress,
    format_final_summary,
    print_full_preview,
)
from src.safe import ProposeToSafe, format_safe_batch
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option(
    "--chain",
    type=click.Choice(get_supported_chains()),
    required=True,
    help="Chain to execute migration on",
)
@click.option(
    "--skip-validation",
    is_flag=True,
    default=False,
    help="Skip CSV validation (not recommended)",
)
@click.option(
    "--skip-preview",
    is_flag=True,
    default=False,
    help="Skip preview step (not recommended)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show detailed transaction data in preview",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation prompt",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Run through the flow without proposing to Safe",
)
@ape_cli_context()
def cli(
    cli_ctx,
    chain: str,
    skip_validation: bool,
    skip_preview: bool,
    verbose: bool,
    yes: bool,
    dry_run: bool,
) -> None:
    """Execute CDP migration for a specific chain.

    This script performs the full migration workflow:

    1. VALIDATE: Check CSV data integrity
    2. BUILD: Create transaction batches
    3. PREVIEW: Show all transactions to be executed
    4. CONFIRM: Prompt for user confirmation
    5. EXECUTE: Propose batched transactions to Gnosis Safe
    6. SUMMARY: Report results

    Each position migration involves 3 transactions:
    - deposit(): Create position with collateral
    - mint(): Borrow against position
    - transferFrom(): Transfer NFT to original user
    """
    click.echo("=" * 70)
    click.echo(click.style("CDP MIGRATION TOOL", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain: {click.style(chain, fg='cyan')}")

    if dry_run:
        click.echo(click.style("Mode: DRY RUN (no transactions will be proposed)", fg="yellow"))

    # Validate chain configuration
    missing_config = validate_chain_config(chain)
    if missing_config:
        click.echo(
            click.style(
                f"\nWarning: Chain configuration incomplete. Missing: {', '.join(missing_config)}",
                fg="yellow",
            )
        )
        if not dry_run:
            click.echo(
                click.style(
                    "Please configure all addresses in src/config.py before migration.",
                    fg="yellow",
                )
            )
            click.echo(
                click.style(
                    "Use --dry-run to test the flow without configured addresses.",
                    fg="blue",
                )
            )
            raise SystemExit(1)
        click.echo(click.style("Continuing with placeholder addresses (dry-run mode).", fg="yellow"))

    chain_config = get_chain_config(chain)
    click.echo(f"Chain ID: {chain_config['chain_id']}")

    if chain_config.get("multisig"):
        click.echo(f"Multisig: {chain_config['multisig']}")
    else:
        click.echo(f"Multisig: {click.style('<not configured>', fg='yellow')}")

    # Check CSV exists
    csv_path = get_csv_path(chain)
    if not csv_path.exists():
        click.echo(click.style(f"\nError: CSV file not found: {csv_path}", fg="red"))
        raise SystemExit(1)
    click.echo(f"Data file: {csv_path}")

    click.echo("-" * 70)

    # =========================================================================
    # Step 1: Validation
    # =========================================================================
    click.echo(click.style("\n[Step 1/5] Validating CSV data...", fg="cyan", bold=True))

    if skip_validation:
        click.echo(click.style("Skipping validation (--skip-validation)", fg="yellow"))
        # Still need to load the CSV to get positions
        result = validate_csv_file(csv_path, chain)
        if not result.is_valid:
            click.echo(click.style("Warning: CSV has validation errors:", fg="yellow"))
            click.echo(format_validation_errors(result.errors))
    else:
        result = validate_csv_file(csv_path, chain)

        if not result.is_valid:
            click.echo("")
            click.echo(click.style(format_validation_errors(result.errors), fg="red"))
            click.echo(click.style("\nMigration aborted: CSV validation failed.", fg="red"))
            raise SystemExit(1)

        click.echo(click.style("Validation successful!", fg="green"))
        click.echo(f"  Total rows:      {len(result.rows)}")
        click.echo(f"  Total positions: {result.total_positions}")
        click.echo(f"  USD positions:   {result.usd_token_count}")
        click.echo(f"  ETH positions:   {result.eth_token_count}")

    if not result.positions:
        click.echo(click.style("\nNo positions found in CSV file.", fg="yellow"))
        raise SystemExit(0)

    # =========================================================================
    # Step 2: Build transaction batches
    # =========================================================================
    click.echo(click.style("\n[Step 2/5] Building transaction batches...", fg="cyan", bold=True))

    batches = create_batches(result.positions, chain, chain_config)

    if not batches:
        click.echo(click.style("No batches created.", fg="yellow"))
        raise SystemExit(0)

    stats = calculate_batch_statistics(batches)
    click.echo(click.style(f"Created {stats['total_batches']} batch(es) with {stats['total_transactions']} transactions.", fg="green"))

    # =========================================================================
    # Step 3: Preview
    # =========================================================================
    if not skip_preview:
        click.echo(click.style("\n[Step 3/5] Transaction preview...", fg="cyan", bold=True))
        print_full_preview(
            chain=chain,
            positions=result.positions,
            batches=batches,
            chain_config=chain_config,
            verbose=verbose,
        )
    else:
        click.echo(click.style("\n[Step 3/5] Skipping preview (--skip-preview)", fg="yellow"))

    # =========================================================================
    # Step 4: Confirmation
    # =========================================================================
    click.echo(click.style("\n[Step 4/5] Confirmation...", fg="cyan", bold=True))

    if not yes:
        click.echo(format_confirmation_prompt(
            chain=chain,
            total_positions=len(result.positions),
            total_batches=stats["total_batches"],
            total_gas=stats["total_gas"],
        ))

        if dry_run:
            click.echo(click.style("DRY RUN: Would prompt for confirmation here.", fg="yellow"))
        else:
            if not click.confirm("Proceed with migration?"):
                click.echo(click.style("\nMigration cancelled by user.", fg="yellow"))
                raise SystemExit(0)
            click.echo(click.style("Confirmed. Proceeding with migration...", fg="green"))
    else:
        click.echo(click.style("Skipping confirmation (--yes)", fg="yellow"))

    # =========================================================================
    # Step 5: Execution
    # =========================================================================
    click.echo(click.style("\n[Step 5/5] Proposing transactions to Safe...", fg="cyan", bold=True))

    if dry_run:
        click.echo(click.style("\nDRY RUN: Skipping actual Safe proposal.", fg="yellow"))
        click.echo("The following batches would be proposed:")

        for i, batch in enumerate(batches, 1):
            click.echo(f"  Batch {i}: {len(batch.calls)} transactions, {batch.total_gas:,} gas")

        # Create mock results for summary
        batch_results = [
            {"status": "dry_run", "nonce": i, "message": "Would be proposed"}
            for i in range(len(batches))
        ]
        successful_batches = len(batches)
        failed_batches = 0

    else:
        # Convert batches to Safe transactions
        chain_id = chain_config["chain_id"]
        safe_txs = format_safe_batch(batches, chain_id=chain_id)

        # Initialize proposer
        multisig = chain_config.get("multisig", "")
        if not multisig:
            click.echo(click.style("\nError: Multisig address not configured.", fg="red"))
            raise SystemExit(1)

        try:
            proposer = ProposeToSafe(
                safe_address=multisig,
                chain_id=chain_id,
                signer_address=None,  # Would be set from connected wallet
            )
        except ValueError as e:
            click.echo(click.style(f"\nError initializing Safe proposer: {e}", fg="red"))
            raise SystemExit(1)

        # Propose each batch
        batch_results = []
        successful_batches = 0
        failed_batches = 0

        for i, safe_tx in enumerate(safe_txs, 1):
            click.echo(format_execution_progress(
                batch_index=i,
                total_batches=len(safe_txs),
                status="Proposing batch...",
            ))

            try:
                result_data = proposer.propose_batch(safe_tx)
                batch_results.append(result_data)

                if result_data.get("status") in ("success", "stubbed"):
                    successful_batches += 1
                    click.echo(format_execution_progress(
                        batch_index=i,
                        total_batches=len(safe_txs),
                        status=click.style("Proposed successfully", fg="green"),
                    ))
                else:
                    failed_batches += 1
                    click.echo(format_execution_progress(
                        batch_index=i,
                        total_batches=len(safe_txs),
                        status=click.style(f"Failed: {result_data.get('message', 'Unknown error')}", fg="red"),
                    ))

            except Exception as e:
                failed_batches += 1
                batch_results.append({
                    "status": "error",
                    "message": str(e),
                    "nonce": None,
                })
                click.echo(format_execution_progress(
                    batch_index=i,
                    total_batches=len(safe_txs),
                    status=click.style(f"Error: {e}", fg="red"),
                ))

    # =========================================================================
    # Final Summary
    # =========================================================================
    click.echo(format_final_summary(
        chain=chain,
        total_positions=len(result.positions),
        total_batches=len(batches),
        successful_batches=successful_batches,
        failed_batches=failed_batches,
        batch_results=batch_results,
    ))

    if dry_run:
        click.echo(
            click.style(
                "\nThis was a dry run. Run without --dry-run to execute.",
                fg="blue",
            )
        )

    # Exit with appropriate code
    if failed_batches > 0 and not dry_run:
        raise SystemExit(1)
