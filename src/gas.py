"""Gas estimation and transaction batching for CDP migration.

This module provides:
- Dynamic gas estimation per operation type (deposit, mint, transfer)
- Greedy bin-packing algorithm for batch optimization
- Batch size verification against 16M gas limit with 5% buffer

Gas Batching Rules (from CLAUDE.md):
- Target: Pack transactions to maximize batch size under ~16M gas limit
- Estimation: Dynamically estimate gas per transaction
- Strategy: Greedy bin-packing - add transactions until limit approached
- Buffer: Reserve 5% headroom below gas limit for safety
- Order: Process ALL deposits first, then ALL mints, then ALL transfers
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from src.config import GAS_BATCH_LIMIT
from src.types import PositionMigration, TransactionBatch, TransactionCall


# Gas constants
GAS_LIMIT = 16_000_000  # Maximum gas per block/batch
GAS_BUFFER = 0.95  # 5% headroom for safety
EFFECTIVE_GAS_LIMIT = int(GAS_LIMIT * GAS_BUFFER)  # 15,200,000

# Base gas costs for each operation type
# These are conservative estimates that account for:
# - Base transaction overhead
# - Storage operations (SSTORE costs)
# - Contract interaction costs
# Values can be tuned based on actual on-chain data
BASE_GAS_DEPOSIT = 150_000  # deposit() - creates position, stores collateral
BASE_GAS_MINT = 120_000  # mint() - borrows against position
BASE_GAS_TRANSFER = 65_000  # transferFrom() - standard ERC721 transfer

# Additional gas per significant collateral amount (for large positions)
# Large positions may have slightly higher gas due to overflow checks, etc.
GAS_PER_LARGE_POSITION = 10_000
LARGE_POSITION_THRESHOLD = 10**21  # 1000 tokens in wei


class OperationType(str, Enum):
    """Types of operations in a CDP migration."""

    DEPOSIT = "deposit"
    MINT = "mint"
    TRANSFER = "transfer"


@dataclass
class GasEstimate:
    """Gas estimate for a single operation."""

    operation_type: OperationType
    base_gas: int
    additional_gas: int = 0
    position_id: int | None = None

    @property
    def total_gas(self) -> int:
        """Total estimated gas for the operation."""
        return self.base_gas + self.additional_gas


def estimate_deposit_gas(position: PositionMigration) -> int:
    """Estimate gas for a deposit operation.

    Deposit operations create a new position by:
    1. Transferring collateral to the CDP contract
    2. Creating storage for the position state
    3. Minting a position NFT to the recipient

    Args:
        position: The position being migrated

    Returns:
        Estimated gas in wei
    """
    gas = BASE_GAS_DEPOSIT

    # Large deposits may require additional gas for overflow checks
    if position.deposit_amount >= LARGE_POSITION_THRESHOLD:
        gas += GAS_PER_LARGE_POSITION

    return gas


def estimate_mint_gas(position: PositionMigration) -> int:
    """Estimate gas for a mint operation.

    Mint operations borrow against an existing position by:
    1. Checking collateralization ratio
    2. Updating position debt
    3. Minting debt tokens to the recipient

    Args:
        position: The position being migrated

    Returns:
        Estimated gas in wei
    """
    gas = BASE_GAS_MINT

    # Large mint amounts may have additional checks
    if position.mint_amount >= LARGE_POSITION_THRESHOLD:
        gas += GAS_PER_LARGE_POSITION

    return gas


def estimate_transfer_gas(position: PositionMigration) -> int:
    """Estimate gas for an NFT transfer operation.

    Transfer operations move the position NFT by:
    1. Verifying ownership
    2. Updating owner mapping
    3. Emitting Transfer event

    Args:
        position: The position being migrated

    Returns:
        Estimated gas in wei (typically constant for ERC721)
    """
    # ERC721 transfers have relatively constant gas costs
    return BASE_GAS_TRANSFER


def estimate_position_total_gas(position: PositionMigration) -> int:
    """Estimate total gas for migrating a single position.

    A full position migration requires:
    1. deposit() - create position with collateral
    2. mint() - borrow against position
    3. transferFrom() - transfer NFT to user

    Args:
        position: The position being migrated

    Returns:
        Total estimated gas for all three operations
    """
    return (
        estimate_deposit_gas(position)
        + estimate_mint_gas(position)
        + estimate_transfer_gas(position)
    )


def _create_deposit_call(
    position: PositionMigration,
    cdp_contract: str,
    multisig: str,
) -> TransactionCall:
    """Create a deposit transaction call for a position.

    Note: Actual transaction data encoding happens in PR 4.
    This creates a placeholder structure with gas estimate.

    Args:
        position: The position to deposit
        cdp_contract: CDP contract address
        multisig: Multisig address (recipient of NFT)

    Returns:
        TransactionCall with gas estimate
    """
    return TransactionCall(
        to=cdp_contract,
        data=b"",  # Will be encoded in PR 4
        value=0,
        gas_estimate=estimate_deposit_gas(position),
        description=f"deposit({position.deposit_amount}, {multisig}, {position.token_id}) for {position.user_address}",
    )


def _create_mint_call(
    position: PositionMigration,
    cdp_contract: str,
) -> TransactionCall:
    """Create a mint transaction call for a position.

    Note: Actual transaction data encoding happens in PR 4.
    This creates a placeholder structure with gas estimate.

    Args:
        position: The position to mint against
        cdp_contract: CDP contract address

    Returns:
        TransactionCall with gas estimate
    """
    return TransactionCall(
        to=cdp_contract,
        data=b"",  # Will be encoded in PR 4
        value=0,
        gas_estimate=estimate_mint_gas(position),
        description=f"mint({position.token_id}, {position.mint_amount}, {position.user_address})",
    )


def _create_transfer_call(
    position: PositionMigration,
    nft_contract: str,
    multisig: str,
) -> TransactionCall:
    """Create an NFT transfer transaction call for a position.

    Note: Actual transaction data encoding happens in PR 4.
    This creates a placeholder structure with gas estimate.

    Args:
        position: The position NFT to transfer
        nft_contract: NFT contract address
        multisig: Multisig address (current owner)

    Returns:
        TransactionCall with gas estimate
    """
    return TransactionCall(
        to=nft_contract,
        data=b"",  # Will be encoded in PR 4
        value=0,
        gas_estimate=estimate_transfer_gas(position),
        description=f"transferFrom({multisig}, {position.user_address}, {position.token_id})",
    )


def _greedy_bin_pack(
    calls: list[TransactionCall],
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> list[TransactionBatch]:
    """Apply greedy bin-packing to create transaction batches.

    The greedy algorithm adds transactions to the current batch until
    adding another would exceed the gas limit, then starts a new batch.

    Args:
        calls: List of transaction calls to batch
        gas_limit: Maximum gas per batch (default: 15.2M with 5% buffer)

    Returns:
        List of TransactionBatch objects
    """
    if not calls:
        return []

    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1)

    for call in calls:
        # Check if adding this call would exceed the limit
        if current_batch.total_gas + call.gas_estimate > gas_limit:
            # Start a new batch if current batch has any calls
            if current_batch.calls:
                batches.append(current_batch)
                current_batch = TransactionBatch(batch_number=len(batches) + 1)

        # Add call to current batch
        current_batch.add_call(call)

    # Don't forget the last batch
    if current_batch.calls:
        batches.append(current_batch)

    return batches


def create_batches(
    positions: list[PositionMigration],
    chain: str,
    chain_config: dict[str, str] | None = None,
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> list[TransactionBatch]:
    """Create optimally-batched transaction lists for position migration.

    This implements the batching strategy from CLAUDE.md:
    - Process ALL deposits first, then ALL mints, then ALL transfers
    - Group similar operations for more predictable gas estimation
    - Each batch stays under ~16M gas (with 5% buffer)

    Args:
        positions: List of positions to migrate
        chain: Chain name (for configuration lookup)
        chain_config: Optional chain configuration dict. If not provided,
                      placeholder addresses are used.
        gas_limit: Maximum gas per batch (default: 15.2M with 5% buffer)

    Returns:
        List of TransactionBatch objects containing all migration calls
    """
    if not positions:
        return []

    # Use provided config or placeholders
    if chain_config is None:
        # Import here to avoid circular dependency
        from src.config import get_chain_config

        try:
            chain_config = get_chain_config(chain)
        except ValueError:
            # Use empty placeholders if chain not configured
            chain_config = {
                "multisig": "",
                "cdp_usd": "",
                "cdp_eth": "",
                "nft_usd": "",
                "nft_eth": "",
            }

    multisig = chain_config.get("multisig", "")

    # Group positions by asset type for contract address lookup
    def get_cdp_contract(asset_type: str) -> str:
        if asset_type == "USD":
            return chain_config.get("cdp_usd", "")
        return chain_config.get("cdp_eth", "")

    def get_nft_contract(asset_type: str) -> str:
        if asset_type == "USD":
            return chain_config.get("nft_usd", "")
        return chain_config.get("nft_eth", "")

    # Build all transaction calls in order: deposits -> mints -> transfers
    all_calls: list[TransactionCall] = []

    # Step 1: ALL deposits first
    for position in positions:
        cdp_contract = get_cdp_contract(position.asset_type)
        call = _create_deposit_call(position, cdp_contract, multisig)
        all_calls.append(call)

    # Step 2: ALL mints second
    for position in positions:
        cdp_contract = get_cdp_contract(position.asset_type)
        call = _create_mint_call(position, cdp_contract)
        all_calls.append(call)

    # Step 3: ALL transfers last
    for position in positions:
        nft_contract = get_nft_contract(position.asset_type)
        call = _create_transfer_call(position, nft_contract, multisig)
        all_calls.append(call)

    # Apply greedy bin-packing
    return _greedy_bin_pack(all_calls, gas_limit)


def calculate_batch_statistics(batches: list[TransactionBatch]) -> dict:
    """Calculate summary statistics for a set of batches.

    Args:
        batches: List of transaction batches

    Returns:
        Dictionary with statistics
    """
    if not batches:
        return {
            "total_batches": 0,
            "total_transactions": 0,
            "total_gas": 0,
            "avg_gas_per_batch": 0,
            "max_gas_batch": 0,
            "min_gas_batch": 0,
            "gas_utilization_percent": 0.0,
        }

    total_gas = sum(b.total_gas for b in batches)
    batch_gases = [b.total_gas for b in batches]
    total_transactions = sum(len(b.calls) for b in batches)

    return {
        "total_batches": len(batches),
        "total_transactions": total_transactions,
        "total_gas": total_gas,
        "avg_gas_per_batch": total_gas // len(batches) if batches else 0,
        "max_gas_batch": max(batch_gases),
        "min_gas_batch": min(batch_gases),
        "gas_utilization_percent": (
            (total_gas / (len(batches) * EFFECTIVE_GAS_LIMIT)) * 100
            if batches
            else 0.0
        ),
    }


def verify_batch_gas_limits(
    batches: list[TransactionBatch],
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> tuple[bool, list[str]]:
    """Verify all batches are within the gas limit.

    Args:
        batches: List of transaction batches to verify
        gas_limit: Maximum allowed gas per batch

    Returns:
        Tuple of (all_valid, list of error messages)
    """
    errors: list[str] = []

    for batch in batches:
        if batch.total_gas > gas_limit:
            errors.append(
                f"Batch {batch.batch_number} exceeds gas limit: "
                f"{batch.total_gas:,} > {gas_limit:,}"
            )

    return len(errors) == 0, errors


def format_batch_summary(batches: list[TransactionBatch]) -> str:
    """Format a human-readable summary of batches.

    Args:
        batches: List of transaction batches

    Returns:
        Formatted string summary
    """
    stats = calculate_batch_statistics(batches)

    lines = [
        "=" * 50,
        "BATCH SUMMARY",
        "=" * 50,
        f"Total batches: {stats['total_batches']}",
        f"Total transactions: {stats['total_transactions']}",
        f"Total gas: {stats['total_gas']:,}",
        f"Average gas per batch: {stats['avg_gas_per_batch']:,}",
        f"Gas limit per batch: {EFFECTIVE_GAS_LIMIT:,}",
        f"Gas utilization: {stats['gas_utilization_percent']:.1f}%",
        "",
    ]

    for batch in batches:
        utilization = (batch.total_gas / EFFECTIVE_GAS_LIMIT) * 100
        lines.append(
            f"Batch {batch.batch_number}: {len(batch.calls)} txns, "
            f"{batch.total_gas:,} gas ({utilization:.1f}%)"
        )

    lines.append("=" * 50)

    return "\n".join(lines)
