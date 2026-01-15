"""Preview formatting functions for CDP migration.

This module provides human-readable transaction preview formatting with:
- Colored output using click.style
- Batch summary with transaction counts and gas estimates
- Individual transaction details (type, target, amount, tokenId)
- Totals and summary statistics
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

import click

from src.gas import (
    EFFECTIVE_GAS_LIMIT,
    calculate_batch_statistics,
    estimate_deposit_gas,
    estimate_mint_gas,
    estimate_transfer_gas,
)
from src.types import PositionMigration, TransactionBatch, TransactionCall


# Display formatting constants
SEPARATOR_CHAR = "="
SUBSEPARATOR_CHAR = "-"
LINE_WIDTH = 70


@dataclass
class TransactionPreview:
    """Preview data for a single transaction."""

    tx_type: Literal["deposit", "mint", "transfer"]
    target_address: str
    user_address: str
    amount: int  # Wei amount (deposit_amount or mint_amount)
    token_id: int
    asset_type: str
    gas_estimate: int


def format_wei_to_display(wei: int, decimals: int = 18) -> str:
    """Format a wei amount for display with proper decimal places.

    Args:
        wei: Amount in wei
        decimals: Number of decimal places (default 18)

    Returns:
        Formatted string with commas and decimals
    """
    if wei == 0:
        return "0.0"

    value = Decimal(wei) / Decimal(10 ** decimals)

    # Format with up to 6 decimal places, removing trailing zeros
    formatted = f"{value:.6f}".rstrip("0").rstrip(".")

    # Add commas to the integer part
    parts = formatted.split(".")
    int_part = f"{int(parts[0]):,}"
    if len(parts) > 1:
        return f"{int_part}.{parts[1]}"
    return int_part


def format_gas(gas: int) -> str:
    """Format gas amount with commas.

    Args:
        gas: Gas amount

    Returns:
        Formatted string with commas
    """
    return f"{gas:,}"


def format_address(address: str, truncate: bool = True) -> str:
    """Format an Ethereum address for display.

    Args:
        address: Full address (0x...)
        truncate: If True, show first 6 and last 4 chars

    Returns:
        Formatted address string
    """
    if not address:
        return "<not configured>"

    if truncate and len(address) == 42:
        return f"{address[:6]}...{address[-4:]}"
    return address


def create_transaction_previews(
    positions: list[PositionMigration],
    chain_config: dict[str, str],
) -> list[TransactionPreview]:
    """Create preview data for all transactions from positions.

    Args:
        positions: List of positions to migrate
        chain_config: Chain configuration with contract addresses

    Returns:
        List of TransactionPreview objects in execution order
    """
    previews: list[TransactionPreview] = []
    multisig = chain_config.get("multisig", "")

    # Helper to get contract addresses
    def get_cdp_contract(asset_type: str) -> str:
        return chain_config.get(f"cdp_{asset_type.lower()}", "")

    def get_nft_contract(asset_type: str) -> str:
        return chain_config.get(f"nft_{asset_type.lower()}", "")

    # Create previews in execution order: ALL deposits, then ALL mints, then ALL transfers

    # Step 1: ALL deposits
    for position in positions:
        previews.append(TransactionPreview(
            tx_type="deposit",
            target_address=get_cdp_contract(position.asset_type),
            user_address=position.user_address,
            amount=position.deposit_amount,
            token_id=position.token_id,
            asset_type=position.asset_type,
            gas_estimate=estimate_deposit_gas(position),
        ))

    # Step 2: ALL mints
    for position in positions:
        previews.append(TransactionPreview(
            tx_type="mint",
            target_address=get_cdp_contract(position.asset_type),
            user_address=position.user_address,
            amount=position.mint_amount,
            token_id=position.token_id,
            asset_type=position.asset_type,
            gas_estimate=estimate_mint_gas(position),
        ))

    # Step 3: ALL transfers
    for position in positions:
        previews.append(TransactionPreview(
            tx_type="transfer",
            target_address=get_nft_contract(position.asset_type),
            user_address=position.user_address,
            amount=0,  # No amount for transfers
            token_id=position.token_id,
            asset_type=position.asset_type,
            gas_estimate=estimate_transfer_gas(position),
        ))

    return previews


def format_transaction_line(preview: TransactionPreview, index: int) -> str:
    """Format a single transaction for display.

    Args:
        preview: Transaction preview data
        index: Transaction index (1-based)

    Returns:
        Formatted single-line string
    """
    # Color code by transaction type
    type_colors = {
        "deposit": "cyan",
        "mint": "magenta",
        "transfer": "green",
    }
    color = type_colors.get(preview.tx_type, "white")

    type_str = click.style(f"{preview.tx_type:8}", fg=color, bold=True)

    # Format amount (only for deposit and mint)
    if preview.tx_type in ("deposit", "mint"):
        amount_str = format_wei_to_display(preview.amount)
    else:
        amount_str = "-"

    # Build the line
    target = format_address(preview.target_address)
    user = format_address(preview.user_address)

    return (
        f"  {index:3}. {type_str} | "
        f"Token #{preview.token_id:<4} | "
        f"{preview.asset_type:3} | "
        f"Amount: {amount_str:>15} | "
        f"To: {user}"
    )


def format_batch_header(batch: TransactionBatch, batch_index: int) -> str:
    """Format a batch header with summary info.

    Args:
        batch: The transaction batch
        batch_index: Batch number (1-based)

    Returns:
        Formatted header string
    """
    utilization = (batch.total_gas / EFFECTIVE_GAS_LIMIT) * 100 if EFFECTIVE_GAS_LIMIT else 0

    header = click.style(
        f"Batch {batch_index}",
        fg="yellow",
        bold=True
    )

    return (
        f"\n{SUBSEPARATOR_CHAR * LINE_WIDTH}\n"
        f"{header}: {len(batch.calls)} transactions | "
        f"Gas: {format_gas(batch.total_gas)} ({utilization:.1f}% of limit)\n"
        f"{SUBSEPARATOR_CHAR * LINE_WIDTH}"
    )


def format_preview_header(chain: str, total_positions: int) -> str:
    """Format the preview header section.

    Args:
        chain: Chain name
        total_positions: Total number of positions

    Returns:
        Formatted header string
    """
    title = click.style("MIGRATION PREVIEW", fg="white", bold=True)

    return (
        f"\n{SEPARATOR_CHAR * LINE_WIDTH}\n"
        f"{title}\n"
        f"{SEPARATOR_CHAR * LINE_WIDTH}\n"
        f"Chain: {click.style(chain, fg='cyan')}\n"
        f"Total positions to migrate: {click.style(str(total_positions), fg='green')}\n"
        f"Total transactions: {click.style(str(total_positions * 3), fg='green')} "
        f"(3 per position: deposit + mint + transfer)"
    )


def format_position_summary(
    usd_count: int,
    eth_count: int,
    total_usd_collateral: int,
    total_eth_collateral: int,
    total_usd_debt: int,
    total_eth_debt: int,
) -> str:
    """Format a summary of positions by asset type.

    Args:
        usd_count: Number of USD positions
        eth_count: Number of ETH positions
        total_usd_collateral: Total USD collateral in wei
        total_eth_collateral: Total ETH collateral in wei
        total_usd_debt: Total USD debt in wei
        total_eth_debt: Total ETH debt in wei

    Returns:
        Formatted summary string
    """
    lines = [
        f"\n{SUBSEPARATOR_CHAR * LINE_WIDTH}",
        click.style("Position Summary", fg="white", bold=True),
        f"{SUBSEPARATOR_CHAR * LINE_WIDTH}",
    ]

    if usd_count > 0:
        lines.extend([
            f"  USD Positions: {click.style(str(usd_count), fg='cyan')}",
            f"    Total Collateral: {format_wei_to_display(total_usd_collateral)}",
            f"    Total Debt:       {format_wei_to_display(total_usd_debt)}",
        ])

    if eth_count > 0:
        lines.extend([
            f"  ETH Positions: {click.style(str(eth_count), fg='cyan')}",
            f"    Total Collateral: {format_wei_to_display(total_eth_collateral)}",
            f"    Total Debt:       {format_wei_to_display(total_eth_debt)}",
        ])

    return "\n".join(lines)


def format_batch_totals(batches: list[TransactionBatch]) -> str:
    """Format batch totals summary.

    Args:
        batches: List of transaction batches

    Returns:
        Formatted totals string
    """
    stats = calculate_batch_statistics(batches)

    title = click.style("Batch Summary", fg="white", bold=True)

    return (
        f"\n{SUBSEPARATOR_CHAR * LINE_WIDTH}\n"
        f"{title}\n"
        f"{SUBSEPARATOR_CHAR * LINE_WIDTH}\n"
        f"  Total Batches:      {click.style(str(stats['total_batches']), fg='yellow')}\n"
        f"  Total Transactions: {click.style(str(stats['total_transactions']), fg='green')}\n"
        f"  Total Gas:          {format_gas(stats['total_gas'])}\n"
        f"  Avg Gas per Batch:  {format_gas(stats['avg_gas_per_batch'])}\n"
        f"  Gas Limit per Batch:{format_gas(EFFECTIVE_GAS_LIMIT)}\n"
        f"  Gas Utilization:    {stats['gas_utilization_percent']:.1f}%"
    )


def format_preview_footer() -> str:
    """Format the preview footer.

    Returns:
        Formatted footer string
    """
    return f"\n{SEPARATOR_CHAR * LINE_WIDTH}"


def print_full_preview(
    chain: str,
    positions: list[PositionMigration],
    batches: list[TransactionBatch],
    chain_config: dict[str, str],
    verbose: bool = False,
) -> None:
    """Print a complete migration preview to stdout.

    Args:
        chain: Chain name
        positions: List of positions to migrate
        batches: Transaction batches
        chain_config: Chain configuration
        verbose: If True, show individual transaction details
    """
    # Calculate position stats
    usd_positions = [p for p in positions if p.asset_type == "USD"]
    eth_positions = [p for p in positions if p.asset_type == "ETH"]

    total_usd_collateral = sum(p.deposit_amount for p in usd_positions)
    total_eth_collateral = sum(p.deposit_amount for p in eth_positions)
    total_usd_debt = sum(p.mint_amount for p in usd_positions)
    total_eth_debt = sum(p.mint_amount for p in eth_positions)

    # Print header
    click.echo(format_preview_header(chain, len(positions)))

    # Print position summary
    click.echo(format_position_summary(
        usd_count=len(usd_positions),
        eth_count=len(eth_positions),
        total_usd_collateral=total_usd_collateral,
        total_eth_collateral=total_eth_collateral,
        total_usd_debt=total_usd_debt,
        total_eth_debt=total_eth_debt,
    ))

    # Print batch details
    if verbose:
        click.echo(f"\n{SUBSEPARATOR_CHAR * LINE_WIDTH}")
        click.echo(click.style("Transaction Details", fg="white", bold=True))

        tx_index = 1
        for batch_idx, batch in enumerate(batches, 1):
            click.echo(format_batch_header(batch, batch_idx))

            for call in batch.calls:
                # Parse the description to determine transaction type
                desc = call.description
                if desc.startswith("deposit"):
                    tx_type = "deposit"
                    color = "cyan"
                elif desc.startswith("mint"):
                    tx_type = "mint"
                    color = "magenta"
                elif desc.startswith("transferFrom"):
                    tx_type = "transfer"
                    color = "green"
                else:
                    tx_type = "unknown"
                    color = "white"

                type_styled = click.style(f"{tx_type:8}", fg=color, bold=True)
                target = format_address(call.to)
                gas = format_gas(call.gas_estimate)

                click.echo(
                    f"  {tx_index:3}. {type_styled} | "
                    f"To: {target} | "
                    f"Gas: {gas:>10}"
                )
                tx_index += 1
    else:
        # Just show batch summary
        click.echo(f"\n{SUBSEPARATOR_CHAR * LINE_WIDTH}")
        click.echo(click.style("Batch Overview", fg="white", bold=True))
        click.echo(f"{SUBSEPARATOR_CHAR * LINE_WIDTH}")

        for batch_idx, batch in enumerate(batches, 1):
            utilization = (batch.total_gas / EFFECTIVE_GAS_LIMIT) * 100
            status_color = "green" if utilization < 80 else "yellow" if utilization < 95 else "red"

            click.echo(
                f"  Batch {batch_idx:2}: "
                f"{len(batch.calls):3} txns | "
                f"Gas: {format_gas(batch.total_gas):>12} | "
                f"{click.style(f'{utilization:5.1f}%', fg=status_color)}"
            )

    # Print totals
    click.echo(format_batch_totals(batches))

    # Print footer
    click.echo(format_preview_footer())


def format_confirmation_prompt(
    chain: str,
    total_positions: int,
    total_batches: int,
    total_gas: int,
) -> str:
    """Format the confirmation prompt message.

    Args:
        chain: Chain name
        total_positions: Number of positions to migrate
        total_batches: Number of Safe transaction batches
        total_gas: Total estimated gas

    Returns:
        Formatted prompt message
    """
    warning = click.style("WARNING", fg="red", bold=True)

    return (
        f"\n{warning}: You are about to propose {total_batches} transaction(s) "
        f"to the Safe on {chain}.\n"
        f"This will migrate {total_positions} position(s) with total estimated gas of {format_gas(total_gas)}.\n"
    )


def format_execution_progress(
    batch_index: int,
    total_batches: int,
    status: str,
    tx_hash: str | None = None,
) -> str:
    """Format execution progress message.

    Args:
        batch_index: Current batch number (1-based)
        total_batches: Total number of batches
        status: Status message
        tx_hash: Optional transaction hash

    Returns:
        Formatted progress message
    """
    progress = f"[{batch_index}/{total_batches}]"
    progress_styled = click.style(progress, fg="cyan", bold=True)

    line = f"{progress_styled} {status}"

    if tx_hash:
        line += f" | Hash: {format_address(tx_hash)}"

    return line


def format_final_summary(
    chain: str,
    total_positions: int,
    total_batches: int,
    successful_batches: int,
    failed_batches: int,
    batch_results: list[dict],
) -> str:
    """Format the final migration summary.

    Args:
        chain: Chain name
        total_positions: Number of positions migrated
        total_batches: Total number of batches
        successful_batches: Number of successful batch proposals
        failed_batches: Number of failed batch proposals
        batch_results: List of batch result dictionaries

    Returns:
        Formatted summary string
    """
    if failed_batches == 0:
        status = click.style("SUCCESS", fg="green", bold=True)
    elif successful_batches > 0:
        status = click.style("PARTIAL SUCCESS", fg="yellow", bold=True)
    else:
        status = click.style("FAILED", fg="red", bold=True)

    lines = [
        f"\n{SEPARATOR_CHAR * LINE_WIDTH}",
        click.style("MIGRATION SUMMARY", fg="white", bold=True),
        f"{SEPARATOR_CHAR * LINE_WIDTH}",
        f"Status: {status}",
        f"Chain: {chain}",
        f"Positions Migrated: {total_positions}",
        f"Batches Proposed: {successful_batches}/{total_batches}",
    ]

    if batch_results:
        lines.append(f"\n{SUBSEPARATOR_CHAR * LINE_WIDTH}")
        lines.append(click.style("Batch Details", fg="white", bold=True))
        lines.append(f"{SUBSEPARATOR_CHAR * LINE_WIDTH}")

        for i, result in enumerate(batch_results, 1):
            status_str = result.get("status", "unknown")
            if status_str == "stubbed":
                status_styled = click.style("proposed (stubbed)", fg="yellow")
            elif status_str == "success":
                status_styled = click.style("proposed", fg="green")
            else:
                status_styled = click.style(status_str, fg="red")

            nonce = result.get("nonce", "N/A")
            lines.append(f"  Batch {i}: {status_styled} | Nonce: {nonce}")

    lines.append(f"{SEPARATOR_CHAR * LINE_WIDTH}")

    return "\n".join(lines)
