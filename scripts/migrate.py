#!/usr/bin/env python3
"""Main migration script for CDP positions.

Usage:
    ape run migrate --chain mainnet

This is the main entry point for executing CDP migrations.
It orchestrates the full migration flow:
1. Validate CSV data
2. Preview transactions
3. Prompt for confirmation
4. Execute batched transactions via Gnosis Safe
5. Report results
"""

import click
from ape import project
from ape.cli import ape_cli_context

from src.config import get_chain_config, get_csv_path, get_supported_chains, validate_chain_config


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
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation prompt",
)
@ape_cli_context()
def cli(cli_ctx, chain: str, skip_validation: bool, skip_preview: bool, yes: bool) -> None:
    """Execute CDP migration for a specific chain.

    This script performs the full migration workflow:

    1. VALIDATE: Check CSV data integrity
    2. PREVIEW: Show all transactions to be executed
    3. CONFIRM: Prompt for user confirmation
    4. EXECUTE: Send batched transactions to Gnosis Safe

    Each position migration involves 3 transactions:
    - deposit(): Create position with collateral
    - mint(): Borrow against position
    - transferFrom(): Transfer NFT to original user
    """
    click.echo("=" * 60)
    click.echo("CDP MIGRATION TOOL")
    click.echo("=" * 60)
    click.echo(f"Chain: {chain}")

    # Validate chain configuration
    missing_config = validate_chain_config(chain)
    if missing_config:
        click.echo(
            click.style(
                f"Error: Chain configuration incomplete. Missing: {', '.join(missing_config)}",
                fg="red",
            )
        )
        click.echo("Please configure all addresses in src/config.py before migration.")
        raise SystemExit(1)

    chain_config = get_chain_config(chain)
    click.echo(f"Chain ID: {chain_config['chain_id']}")
    click.echo(f"Multisig: {chain_config['multisig']}")

    # Check CSV exists
    csv_path = get_csv_path(chain)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV file not found: {csv_path}", fg="red"))
        raise SystemExit(1)
    click.echo(f"Data file: {csv_path}")

    click.echo("-" * 60)

    # Step 1: Validation
    if not skip_validation:
        click.echo("\n[Step 1/4] Validating CSV data...")
        # TODO: Call validation logic from PR 2
        click.echo(click.style("Validation not yet implemented (PR 2)", fg="yellow"))
    else:
        click.echo(click.style("\n[Step 1/4] Skipping validation (--skip-validation)", fg="yellow"))

    # Step 2: Preview
    if not skip_preview:
        click.echo("\n[Step 2/4] Generating transaction preview...")
        # TODO: Call preview logic from PR 6
        click.echo(click.style("Preview not yet implemented (PR 6)", fg="yellow"))
    else:
        click.echo(click.style("\n[Step 2/4] Skipping preview (--skip-preview)", fg="yellow"))

    # Step 3: Confirmation
    click.echo("\n[Step 3/4] Confirmation...")
    if not yes:
        click.echo(click.style("Confirmation not yet implemented (PR 6)", fg="yellow"))
        # TODO: Show summary and prompt for confirmation
        # if not click.confirm("Proceed with migration?"):
        #     click.echo("Migration cancelled.")
        #     raise SystemExit(0)
    else:
        click.echo(click.style("Skipping confirmation (--yes)", fg="yellow"))

    # Step 4: Execution
    click.echo("\n[Step 4/4] Executing migration...")
    click.echo(click.style("Execution not yet implemented (PR 5)", fg="yellow"))
    # TODO: Execute batched transactions via Gnosis Safe

    click.echo("\n" + "=" * 60)
    click.echo("MIGRATION COMPLETE (placeholder)")
    click.echo("=" * 60)
    click.echo(click.style("Full migration implementation pending PRs 2-6", fg="yellow"))
