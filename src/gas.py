"""Gas estimation and transaction batching for V3 migration.

Batching strategy:
  Each batch is limited by three constraints (whichever is hit first):
    1. Gas:   90% of chain's block gas limit
    2. Size:  90% of chain's max transaction calldata
    3. Calls: MAX_CALLS_PER_BATCH (default 50)

  Per-chain limits:
    mainnet:  60M gas,  128KB calldata
    optimism: 30M gas,  120KB calldata
    arbitrum: 32M gas,  118KB calldata

  Flow:
    1. deposit_batches  — setDepositCap + deposit per user (creates NFTs)
    2. read_ids         — read events to get user→tokenId mapping
    3. mint_batches     — mint(tokenId, amount, multisig) using real IDs
    4. verify           — check positions match snapshot
    5. transfer_batches — NFT transferFrom using real IDs
    6. credit_batches   — alToken.transfer to credit users
    Burn is handled manually by the multisig.
"""

from src.config import (
    GAS_DEPOSIT,
    GAS_MINT,
    GAS_SET_DEPOSIT_CAP,
    GAS_TRANSFER_ALTOKEN,
    GAS_TRANSFER_NFT,
    GAS_LARGE_POSITION_SURCHARGE,
    LARGE_POSITION_THRESHOLD,
    MAX_CALLS_PER_BATCH,
    MULTISEND_CALL_BYTES,
    MULTISEND_WRAPPER_BYTES,
    get_effective_gas_limit,
    get_effective_size_limit,
)
from src.types import MigrationPlan, PositionMigration, TransactionBatch, TransactionCall


def _batch_calldata_size(calls: list[TransactionCall]) -> int:
    """Compute the total MultiSend calldata size for a list of calls."""
    return MULTISEND_WRAPPER_BYTES + sum(MULTISEND_CALL_BYTES + len(c.data) for c in calls)


def _can_add_call(
    batch: TransactionBatch,
    call: TransactionCall,
    gas_limit: int,
    size_limit: int,
    max_calls: int,
) -> bool:
    """Check if adding a call would exceed any batch constraint."""
    if len(batch.calls) >= max_calls:
        return False
    if batch.total_gas + call.gas_estimate > gas_limit:
        return False
    new_size = _batch_calldata_size(batch.calls + [call])
    if new_size > size_limit:
        return False
    return True


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
    chain: str = "mainnet",
    current_deposit_cap_wei: int = 0,
) -> list[TransactionBatch]:
    """Create deposit-only batches: [setDepositCap?, deposit, deposit, ...]

    Each batch:
      1. `setDepositCap(new_cap)` — ONLY when the cumulative required cap exceeds
         the current live `depositCap()`. V3 alchemist reverts on downward
         changes, so never emit a call that would lower the cap.
      2. For each user: `deposit(amount, multisig, 0)` → creates NFT

    Mints are NOT included — they require real tokenIds from deposit events.
    Run `ape run read_ids` after these execute, then `ape run mint`.

    `current_deposit_cap_wei`: pass the on-chain `depositCap()` value (read via
    `src.preflight.read_deposit_cap`). Defaults to 0, which means "assume fresh
    alchemist" — fine for first-run but causes reverts on any chain where the
    cap is already raised (arbitrum alUSD, etc.). Callers should read live state.
    """
    from src.transactions import build_deposit_tx, build_set_deposit_cap_tx

    if not positions:
        return []

    # Reserve gas + size headroom for a potential setDepositCap at batch start,
    # so adding one doesn't push the batch past the chain limits. Even when we
    # end up NOT emitting it (live cap already covers), the headroom is fine.
    gas_limit = get_effective_gas_limit(chain) - GAS_SET_DEPOSIT_CAP
    size_limit = get_effective_size_limit(chain) - MULTISEND_CALL_BYTES - 36  # 4 selector + 32 arg
    # Reserve 1 slot for a potential setDepositCap at batch start.
    max_deposits = MAX_CALLS_PER_BATCH - 1

    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1, batch_type="deposit")
    # `live_cap` tracks what the alchemist's depositCap will be after any
    # setDepositCap calls we've already emitted in earlier batches. Starts at
    # the actual on-chain value.
    live_cap = current_deposit_cap_wei
    # `cumulative_needed` is the cap value the alchemist must reach to cover
    # every deposit we'll make. Starts at the current live cap (= current
    # alchemist.totalDeposited assumption) so resumed runs don't underbid the
    # cap. Each new deposit pushes this higher.
    cumulative_needed = current_deposit_cap_wei
    batch_deposit_sum = 0

    def _finalize_batch(batch: TransactionBatch, cap_sum: int) -> TransactionBatch:
        """Finalize batch by prepending setDepositCap IF the new cumulative
        requirement exceeds the live cap; otherwise omit it entirely."""
        nonlocal live_cap
        new_cap_needed = cumulative_needed  # includes this batch's sum already
        if new_cap_needed > live_cap:
            cap_tx = build_set_deposit_cap_tx(alchemist_address, new_cap_needed)
            batch.calls.insert(0, cap_tx)
            batch.total_gas += cap_tx.gas_estimate
            live_cap = new_cap_needed
        batch.deposit_sum_wei = cap_sum
        return batch

    def _start_new_batch(n: int) -> TransactionBatch:
        return TransactionBatch(batch_number=n, batch_type="deposit")

    for position in positions:
        dep_tx = build_deposit_tx(position, alchemist_address, multisig)

        # Will adding this call exceed any batch limit? If so, finalize current
        # batch and start a new one. Reserve 1 slot for the cap call (may or
        # may not be emitted, but we budget conservatively).
        if len(current_batch.calls) >= max_deposits or not _can_add_call(
            current_batch, dep_tx, gas_limit, size_limit, MAX_CALLS_PER_BATCH
        ):
            if current_batch.calls:
                batches.append(_finalize_batch(current_batch, batch_deposit_sum))
            current_batch = _start_new_batch(len(batches) + 1)
            batch_deposit_sum = 0

        current_batch.add_call(dep_tx)
        batch_deposit_sum += position.deposit_amount_wei
        cumulative_needed += position.deposit_amount_wei

    if current_batch.calls:
        batches.append(_finalize_batch(current_batch, batch_deposit_sum))

    return batches


def create_mint_batches(
    positions: list[PositionMigration],
    alchemist_address: str,
    multisig: str,
    token_id_map: dict[str, int],
    chain: str = "mainnet",
) -> list[TransactionBatch]:
    """Create mint batches using real token IDs from the event mapping.

    mint(tokenId, mint_amount_wei, multisig) for each debt user (mint_amount_wei > 0).
    Credit users have mint_amount_wei = 0 and are skipped.
    """
    from src.transactions import build_mint_tx

    gas_limit = get_effective_gas_limit(chain)
    size_limit = get_effective_size_limit(chain)

    mintable = [p for p in positions if p.mint_amount_wei > 0]
    if not mintable:
        return []

    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1, batch_type="mint")

    for position in mintable:
        addr = position.user_address.lower()
        if addr not in token_id_map:
            raise ValueError(f"No token ID for {position.user_address}. Run `ape run read_ids`.")
        token_id = token_id_map[addr]
        mint_tx = build_mint_tx(position, alchemist_address, multisig, token_id)

        if current_batch.calls and not _can_add_call(
            current_batch, mint_tx, gas_limit, size_limit, MAX_CALLS_PER_BATCH
        ):
            batches.append(current_batch)
            current_batch = TransactionBatch(batch_number=len(batches) + 1, batch_type="mint")

        current_batch.add_call(mint_tx)

    if current_batch.calls:
        batches.append(current_batch)

    return batches

def create_credit_batches(
    credit_positions: list[PositionMigration],
    al_token_address: str,
    chain: str = "mainnet",
) -> list[TransactionBatch]:
    """Create credit batches: alToken.transfer(user, creditAmount) per credit user.

    These send alAssets from the multisig to users who had negative debt in V2.
    The alAssets come from the pool minted for debt users.
    """
    from src.transactions import build_altoken_transfer_tx

    if not credit_positions:
        return []

    gas_limit = get_effective_gas_limit(chain)
    size_limit = get_effective_size_limit(chain)
    batches: list[TransactionBatch] = []
    current_batch = TransactionBatch(batch_number=1, batch_type="credit")

    for position in credit_positions:
        tx = build_altoken_transfer_tx(
            al_token_address=al_token_address,
            recipient=position.user_address,
            amount_wei=position.credit_amount_wei,
            user_address=position.user_address,
        )

        if current_batch.calls and not _can_add_call(
            current_batch, tx, gas_limit, size_limit, MAX_CALLS_PER_BATCH
        ):
            batches.append(current_batch)
            current_batch = TransactionBatch(batch_number=len(batches) + 1, batch_type="credit")

        current_batch.add_call(tx)

    if current_batch.calls:
        batches.append(current_batch)

    return batches


def create_approve_underlying_batches(
    underlying_address: str,
    myt_address: str,
    amount_wei: int,
    chain: str = "mainnet",
) -> list[TransactionBatch]:
    """One-call batch: approve(myt, amount) on the underlying ERC20.

    Lets the MYT vault pull underlying (USDC / WETH) from the multisig
    during the MYT deposit step.
    """
    from src.transactions import build_erc20_approve_tx

    if amount_wei <= 0:
        return []
    tx = build_erc20_approve_tx(
        token_address=underlying_address,
        spender=myt_address,
        amount_wei=amount_wei,
        description=f"approve underlying -> MYT ({amount_wei})",
    )
    batch = TransactionBatch(batch_number=1, batch_type="approve_underlying")
    batch.add_call(tx)
    return [batch]


def create_myt_deposit_batches(
    myt_address: str,
    multisig: str,
    assets_wei: int,
    chain: str = "mainnet",
) -> list[TransactionBatch]:
    """One-call batch: MYT.deposit(assets, multisig) — mints MYT shares to multisig."""
    from src.transactions import build_erc4626_deposit_tx

    if assets_wei <= 0:
        return []
    tx = build_erc4626_deposit_tx(
        vault_address=myt_address,
        assets_wei=assets_wei,
        receiver=multisig,
        description=f"MYT.deposit({assets_wei}, multisig)",
    )
    batch = TransactionBatch(batch_number=1, batch_type="deposit_myt")
    batch.add_call(tx)
    return [batch]


def create_approve_myt_batches(
    myt_address: str,
    alchemist_address: str,
    amount_wei: int,
    chain: str = "mainnet",
) -> list[TransactionBatch]:
    """One-call batch: approve(alchemist, amount) on the MYT share token.

    Lets the Alchemist pull MYT from the multisig during the deposit step.
    """
    from src.transactions import build_erc20_approve_tx

    if amount_wei <= 0:
        return []
    tx = build_erc20_approve_tx(
        token_address=myt_address,
        spender=alchemist_address,
        amount_wei=amount_wei,
        description=f"approve MYT -> Alchemist ({amount_wei})",
    )
    batch = TransactionBatch(batch_number=1, batch_type="approve_myt")
    batch.add_call(tx)
    return [batch]


def compute_underlying_total(
    positions: list[PositionMigration],
    underlying_decimals: int,
    myt_decimals: int = 18,
) -> int:
    """Total underlying needed to mint enough MYT shares to back all deposits.

    CSV deposit_amount_wei is normalized to myt_decimals (18 for all V3 MYTs).
    Underlying may be 6-decimal (USDC) or 18-decimal (WETH); rescale accordingly.
    Rounds UP so we never under-approve.
    """
    total_myt = sum(p.deposit_amount_wei for p in positions)
    if underlying_decimals == myt_decimals:
        return total_myt
    if underlying_decimals < myt_decimals:
        divisor = 10 ** (myt_decimals - underlying_decimals)
        return (total_myt + divisor - 1) // divisor  # ceil
    return total_myt * (10 ** (underlying_decimals - myt_decimals))


def create_transfer_batches(
    positions: list[PositionMigration],
    nft_address: str,
    multisig: str,
    token_id_map: dict[str, int] | None = None,
    chain: str = "mainnet",
) -> list[TransactionBatch]:
    """Create NFT transfer batches: transferFrom(multisig, user, tokenId) per user.

    Uses real token IDs from token_id_map if provided, otherwise placeholder 999999.
    """
    from src.transactions import build_nft_transfer_tx

    if not positions:
        return []

    gas_limit = get_effective_gas_limit(chain)
    size_limit = get_effective_size_limit(chain)
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
            nft_address=nft_address, multisig=multisig,
            user_address=position.user_address, token_id=token_id,
        )

        if current_batch.calls and not _can_add_call(
            current_batch, tx, gas_limit, size_limit, MAX_CALLS_PER_BATCH
        ):
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
    token_id_map: dict[str, int] | None = None,
    myt_address: str = "",
    underlying_address: str = "",
    underlying_decimals: int = 18,
    myt_decimals: int = 18,
) -> "MigrationPlan":
    """Build the full migration plan for one asset type on one chain.

    token_id_map: if provided, builds mint and transfer batches with real IDs.
                  If None, mint_batches are empty and transfers use placeholder 999999.
    myt_address / underlying_address: if provided, also populates the three
                  pre-deposit batch lists (approve_underlying, myt_deposit, approve_myt).
    """
    from src.types import AssetType, MigrationPlan

    asset_type = positions[0].asset_type if positions else AssetType.USD

    plan = MigrationPlan(chain=chain, asset_type=asset_type, positions=positions)

    total_myt = plan.total_deposit_wei
    if myt_address and underlying_address and total_myt > 0:
        total_underlying = compute_underlying_total(
            positions, underlying_decimals=underlying_decimals, myt_decimals=myt_decimals,
        )
        plan.approve_underlying_batches = create_approve_underlying_batches(
            underlying_address, myt_address, total_underlying, chain,
        )
        plan.myt_deposit_batches = create_myt_deposit_batches(
            myt_address, multisig, total_underlying, chain,
        )
        plan.approve_myt_batches = create_approve_myt_batches(
            myt_address, alchemist_address, total_myt, chain,
        )

    plan.deposit_batches = create_deposit_batches(
        positions, alchemist_address, multisig, chain, current_deposit_cap_wei,
    )

    if token_id_map:
        plan.mint_batches = create_mint_batches(
            positions, alchemist_address, multisig, token_id_map, chain,
        )

    plan.transfer_batches = create_transfer_batches(
        positions, nft_address, multisig, token_id_map, chain,
    )

    plan.credit_batches = create_credit_batches(
        plan.credit_users, al_token_address, chain,
    )

    return plan


def calculate_batch_statistics(
    batches: list[TransactionBatch],
    chain: str = "mainnet",
) -> dict:
    if not batches:
        return {
            "total_batches": 0, "total_transactions": 0, "total_gas": 0,
            "avg_gas_per_batch": 0, "max_gas_batch": 0, "min_gas_batch": 0,
            "gas_utilization_percent": 0.0,
        }

    gas_limit = get_effective_gas_limit(chain)
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
        "gas_utilization_percent": (total_gas / (len(batches) * gas_limit)) * 100,
    }


def verify_batch_gas_limits(
    batches: list[TransactionBatch],
    chain: str = "mainnet",
) -> tuple[bool, list[str]]:
    gas_limit = get_effective_gas_limit(chain)
    errors = []
    for batch in batches:
        if batch.total_gas > gas_limit:
            errors.append(
                f"Batch {batch.batch_number} ({batch.batch_type}) exceeds gas limit: "
                f"{batch.total_gas:,} > {gas_limit:,}"
            )
    return len(errors) == 0, errors


def format_batch_summary(batches: list[TransactionBatch], chain: str = "mainnet") -> str:
    gas_limit = get_effective_gas_limit(chain)
    stats = calculate_batch_statistics(batches, chain)
    lines = [
        "=" * 50,
        "BATCH SUMMARY",
        "=" * 50,
        f"Total batches:      {stats['total_batches']}",
        f"Total transactions: {stats['total_transactions']}",
        f"Total gas:          {stats['total_gas']:,}",
        f"Avg gas per batch:  {stats['avg_gas_per_batch']:,}",
        f"Gas limit per batch:{gas_limit:,}",
        f"Max calls/batch:    {MAX_CALLS_PER_BATCH}",
        f"Gas utilization:    {stats['gas_utilization_percent']:.1f}%",
        "",
    ]
    for batch in batches:
        util = (batch.total_gas / gas_limit) * 100
        lines.append(
            f"  [{batch.batch_type:8}] Batch {batch.batch_number}: "
            f"{len(batch.calls)} txns, {batch.total_gas:,} gas ({util:.1f}%)"
        )
    lines.append("=" * 50)
    return "\n".join(lines)
