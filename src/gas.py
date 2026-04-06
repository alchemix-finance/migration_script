"""Gas estimation and transaction batching for V3 migration.

Batching strategy:
  Deposits and mints are in SEPARATE batches because mint(tokenId, ...) needs
  the real tokenId assigned by the contract at deposit time. Flow:
    1. deposit_batches  — setDepositCap + deposit per user (creates NFTs)
    2. read_ids         — read events to get user→tokenId mapping
    3. mint_batches     — mint(tokenId, amount, multisig) using real IDs
    4. credit_batches   — alToken.transfer to credit users
    5. transfer_batches — NFT transferFrom using real IDs
    6. final_burn_batch — alToken.burn(remaining)

Gas limit: 16M. Target: 90% = 14.4M per batch (10% headroom).
"""

from src.config import (
    EFFECTIVE_GAS_LIMIT,
    GAS_ALTOKEN_BURN,
    GAS_DEPOSIT,
    GAS_MINT,
    GAS_SET_DEPOSIT_CAP,
    GAS_TRANSFER_ALTOKEN,
    GAS_TRANSFER_NFT,
    GAS_LARGE_POSITION_SURCHARGE,
    LARGE_POSITION_THRESHOLD,
)
from src.types import MigrationPlan, PositionMigration, TransactionBatch, TransactionCall


def _gas_deposit(p: PositionMigration) -> int:
    g = GAS_DEPOSIT
    if p.deposit_amount_wei >= LARGE_POSITION_THRESHOLD:
        g += GAS_LARGE_POSITION_SURCHARGE
    return g


def _gas_mint(p: PositionMigration) -> int:
    g = GAS_MINT
    if p.mint_amount_wei >= LARGE_POSITION_THRESHOLD:
        g += GAS_LARGE_POSITION_SURCHARGE
    return g


def gas_per_position_in_deposit_batch(p: PositionMigration) -> int:
    """Gas for one user's deposit call (no mint — mints are separate)."""
    return _gas_deposit(p)


def create_deposit_batches(
    positions: list[PositionMigration],
    alchemist_address: str,
    multisig: str,
    current_deposit_cap_wei: int = 0,
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> list[TransactionBatch]:
    """Create deposit-only batches: [setDepositCap, deposit, deposit, ...]

    Each batch:
      1. setDepositCap(currentCap + sum_of_this_batch_deposits)
      2. For each user: deposit(amount, multisig, 0) → creates NFT

    Mints are NOT included — they require real tokenIds from deposit events.
    Run `ape run read_ids` after these execute, then `ape run mint`.
    """
    from src.transactions import build_deposit_tx, build_set_deposit_cap_tx

    if not positions:
        return []

    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1, batch_type="deposit")
    current_cap = current_deposit_cap_wei
    batch_deposit_sum = 0

    current_batch.add_call(
        TransactionCall(
            to="",  # placeholder — replaced in _finalize_batch
            data=b"",
            gas_estimate=GAS_SET_DEPOSIT_CAP,
            description="setDepositCap(TBD)",
        )
    )

    def _finalize_batch(batch: TransactionBatch, cap_sum: int, cap_base: int) -> TransactionBatch:
        new_cap = cap_base + cap_sum
        cap_tx = build_set_deposit_cap_tx(alchemist_address, new_cap)
        batch.calls[0] = cap_tx
        batch.deposit_sum_wei = cap_sum
        return batch

    def _start_new_batch(n: int, cap_base: int) -> tuple[TransactionBatch, int]:
        b = TransactionBatch(batch_number=n, batch_type="deposit")
        b.add_call(
            TransactionCall(to="", data=b"", gas_estimate=GAS_SET_DEPOSIT_CAP,
                            description="setDepositCap(TBD)")
        )
        return b, 0

    for position in positions:
        pos_gas = gas_per_position_in_deposit_batch(position)

        if current_batch.total_gas + pos_gas > gas_limit and len(current_batch.calls) > 1:
            batches.append(_finalize_batch(current_batch, batch_deposit_sum, current_cap))
            current_cap += batch_deposit_sum
            current_batch, batch_deposit_sum = _start_new_batch(len(batches) + 1, current_cap)

        dep_tx = build_deposit_tx(position, alchemist_address, multisig)
        current_batch.add_call(dep_tx)
        batch_deposit_sum += position.deposit_amount_wei

    if len(current_batch.calls) > 1:
        batches.append(_finalize_batch(current_batch, batch_deposit_sum, current_cap))

    return batches


def create_mint_batches(
    positions: list[PositionMigration],
    alchemist_address: str,
    multisig: str,
    token_id_map: dict[str, int],
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> list[TransactionBatch]:
    """Create mint batches using real token IDs from the event mapping.

    mint(tokenId, mint_amount_wei, multisig) for each position with mint_amount_wei > 0.
    Requires token_id_map from `ape run read_ids`.
    """
    from src.transactions import build_mint_tx

    mintable = [p for p in positions if p.mint_amount_wei > 0]
    if not mintable:
        return []

    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1, batch_type="mint")

    for position in mintable:
        addr = position.user_address.lower()
        if addr not in token_id_map:
            raise ValueError(
                f"No token ID found for {position.user_address}. "
                f"Run `ape run read_ids` first."
            )
        token_id = token_id_map[addr]

        mint_tx = build_mint_tx(position, alchemist_address, multisig, token_id)

        if current_batch.total_gas + mint_tx.gas_estimate > gas_limit and current_batch.calls:
            batches.append(current_batch)
            current_batch = TransactionBatch(batch_number=len(batches) + 1, batch_type="mint")

        current_batch.add_call(mint_tx)

    if current_batch.calls:
        batches.append(current_batch)

    return batches



def create_final_burn_batch(
    amount_wei: int,
    al_token_address: str,
    use_transfer_fallback: bool = False,
) -> "TransactionBatch | None":
    """Create the single final-burn batch for Script 2.

    Burns remaining alAssets in the multisig after credit distribution and NFT transfers.
    amount_wei = total_mint_wei - total_credit_wei (debt users' minted amounts only).

    Primary:  alToken.burn(amount)          — ERC20Burnable, reduces supply cleanly.
    Fallback: alToken.transfer(0x000, amt)  — if burn() is not available on the contract.

    Returns None if amount_wei is 0 (nothing to burn).
    """
    from src.transactions import build_altoken_burn_tx, build_altoken_transfer_zero_tx

    if amount_wei <= 0:
        return None

    if use_transfer_fallback:
        tx = build_altoken_transfer_zero_tx(al_token_address, amount_wei)
    else:
        tx = build_altoken_burn_tx(al_token_address, amount_wei)

    batch = TransactionBatch(batch_number=1, batch_type="final_burn")
    batch.add_call(tx)
    return batch


def create_credit_batches(
    credit_positions: list[PositionMigration],
    al_token_address: str,
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> list[TransactionBatch]:
    """Create credit batches: alToken.transfer(user, creditAmount) per credit user.

    These send alAssets from the multisig to users who had negative debt in V2.
    Executed before burn batches (so the multisig has enough alAssets).
    """
    from src.transactions import build_altoken_transfer_tx

    if not credit_positions:
        return []

    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1, batch_type="credit")

    for position in credit_positions:
        tx = build_altoken_transfer_tx(
            al_token_address=al_token_address,
            recipient=position.user_address,
            amount_wei=position.credit_amount_wei,
            user_address=position.user_address,
        )

        if current_batch.total_gas + tx.gas_estimate > gas_limit and current_batch.calls:
            batches.append(current_batch)
            current_batch = TransactionBatch(batch_number=len(batches) + 1, batch_type="credit")

        current_batch.add_call(tx)

    if current_batch.calls:
        batches.append(current_batch)

    return batches


def create_transfer_batches(
    positions: list[PositionMigration],
    nft_address: str,
    multisig: str,
    token_id_map: dict[str, int] | None = None,
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> list[TransactionBatch]:
    """Create NFT transfer batches: transferFrom(multisig, user, tokenId) per user.

    Uses real token IDs from token_id_map if provided, otherwise placeholder 999999.
    """
    from src.transactions import build_nft_transfer_tx

    if not positions:
        return []

    PLACEHOLDER_TOKEN_ID = 999_999
    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1, batch_type="transfer")

    for position in positions:
        if token_id_map is not None:
            addr = position.user_address.lower()
            if addr not in token_id_map:
                raise ValueError(f"No token ID found for {position.user_address}")
            token_id = token_id_map[addr]
        else:
            token_id = PLACEHOLDER_TOKEN_ID

        tx = build_nft_transfer_tx(
            nft_address=nft_address,
            multisig=multisig,
            user_address=position.user_address,
            token_id=token_id,
        )

        if current_batch.total_gas + tx.gas_estimate > gas_limit and current_batch.calls:
            batches.append(current_batch)
            current_batch = TransactionBatch(batch_number=len(batches) + 1, batch_type="transfer")

        current_batch.add_call(tx)

    if current_batch.calls:
        batches.append(current_batch)

    return batches


def build_migration_plan(
    positions: list[PositionMigration],
    chain: str,
    alchemist_address: str,
    al_token_address: str,
    nft_address: str,
    multisig: str,
    current_deposit_cap_wei: int = 0,
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
    use_burn_fallback: bool = False,
    token_id_map: dict[str, int] | None = None,
) -> "MigrationPlan":
    """Build the full migration plan for one asset type on one chain.

    Deposit batches (phase1): deposit only — no mint (tokenIds not yet known).
    Mint batches (mint script): mint using real tokenIds from read_ids.
    Credit batches (phase2): alToken.transfer to credit users.
    Transfer batches (phase2): NFT transferFrom using real tokenIds.
    Final burn (phase2): alToken.burn(remaining).

    token_id_map: if provided, builds mint and transfer batches with real IDs.
                  If None, mint_batches are empty and transfers use placeholder 999999.
    """
    from src.types import AssetType, MigrationPlan

    asset_type = positions[0].asset_type if positions else AssetType.USD

    plan = MigrationPlan(chain=chain, asset_type=asset_type, positions=positions)

    plan.deposit_batches = create_deposit_batches(
        positions, alchemist_address, multisig,
        current_deposit_cap_wei, gas_limit,
    )

    if token_id_map:
        plan.mint_batches = create_mint_batches(
            positions, alchemist_address, multisig, token_id_map, gas_limit,
        )

    plan.credit_batches = create_credit_batches(
        plan.credit_users, al_token_address, gas_limit,
    )

    plan.transfer_batches = create_transfer_batches(
        positions, nft_address, multisig, token_id_map, gas_limit,
    )

    remaining_wei = plan.total_mint_wei - plan.total_credit_wei
    plan.final_burn_batch = create_final_burn_batch(
        remaining_wei, al_token_address, use_burn_fallback,
    )

    return plan


def calculate_batch_statistics(batches: list[TransactionBatch]) -> dict:
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
    gases = [b.total_gas for b in batches]
    total_txns = sum(len(b.calls) for b in batches)

    return {
        "total_batches": len(batches),
        "total_transactions": total_txns,
        "total_gas": total_gas,
        "avg_gas_per_batch": total_gas // len(batches),
        "max_gas_batch": max(gases),
        "min_gas_batch": min(gases),
        "gas_utilization_percent": (
            (total_gas / (len(batches) * EFFECTIVE_GAS_LIMIT)) * 100
        ),
    }


def verify_batch_gas_limits(
    batches: list[TransactionBatch],
    gas_limit: int = EFFECTIVE_GAS_LIMIT,
) -> tuple[bool, list[str]]:
    errors = []
    for batch in batches:
        if batch.total_gas > gas_limit:
            errors.append(
                f"Batch {batch.batch_number} ({batch.batch_type}) exceeds gas limit: "
                f"{batch.total_gas:,} > {gas_limit:,}"
            )
    return len(errors) == 0, errors


def format_batch_summary(batches: list[TransactionBatch]) -> str:
    stats = calculate_batch_statistics(batches)
    lines = [
        "=" * 50,
        "BATCH SUMMARY",
        "=" * 50,
        f"Total batches:      {stats['total_batches']}",
        f"Total transactions: {stats['total_transactions']}",
        f"Total gas:          {stats['total_gas']:,}",
        f"Avg gas per batch:  {stats['avg_gas_per_batch']:,}",
        f"Gas limit per batch:{EFFECTIVE_GAS_LIMIT:,}",
        f"Gas utilization:    {stats['gas_utilization_percent']:.1f}%",
        "",
    ]
    for batch in batches:
        util = (batch.total_gas / EFFECTIVE_GAS_LIMIT) * 100
        lines.append(
            f"  [{batch.batch_type:8}] Batch {batch.batch_number}: "
            f"{len(batch.calls)} txns, {batch.total_gas:,} gas ({util:.1f}%)"
        )
    lines.append("=" * 50)
    return "\n".join(lines)
