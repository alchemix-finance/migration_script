"""Data models and types for V3 CDP migration."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Literal, TypeAlias


class AssetType(str, Enum):
    """Supported asset types for CDP positions.

    USD = USDC collateral → alUSD debt
    ETH = WETH collateral → alETH debt
    """

    USD = "USD"
    ETH = "ETH"


class ChainName(str, Enum):
    """Supported chain names."""

    MAINNET = "mainnet"
    OPTIMISM = "optimism"
    ARBITRUM = "arbitrum"


# Type aliases for clarity
Address: TypeAlias = str
Wei: TypeAlias = int
TokenId: TypeAlias = int


@dataclass
class CSVRow:
    """A single row from the V3 migration CSV.

    CSV schema: address,underlyingValue,debt
    - underlyingValue: collateral in underlying token units (USDC or WETH)
    - debt: positive = user owes alAssets; negative = protocol owes user alAssets (credit)

    One CSV file per asset type per chain.
    e.g. alUSDValues-sum-and-debt-mainnet.csv  (USDC positions)
         alETHValues-sum-and-debt-mainnet.csv   (WETH positions)
    """

    address: Address
    underlying_value: Decimal   # collateral in atomic MYT share units (already wei-scale)
    debt: Decimal               # debt in atomic alToken units (already wei-scale); negative = credit
    row_number: int = 0

    @property
    def has_position(self) -> bool:
        """Position exists iff underlying_value > 0."""
        return self.underlying_value > 0

    @property
    def is_credit_user(self) -> bool:
        """Credit users have negative debt (protocol owes them alAssets)."""
        return self.debt < 0

    @property
    def credit_amount(self) -> Decimal:
        """Amount of alAssets owed to this user (only meaningful when negative debt)."""
        return abs(self.debt) if self.debt < 0 else Decimal(0)


@dataclass
class PositionMigration:
    """One user's position to be migrated — per asset type.

    Step 1 — deposit (deposit.py):    deposit(amount, multisig, 0) → creates NFT
    Step 2 — read IDs (read_ids.py):  reads events → user→tokenId map
    Step 3 — mint (mint.py):          mint(tokenId, amount, multisig) for DEBT users only
    Step 4 — verify (verify.py):      check positions match snapshot, credit users = 0 debt
    Step 5 — distribute (distribute.py): ERC721.transferFrom(multisig, user, tokenId)
    Step 6 — credit (credit.py):      alToken.transfer(user, credit_amount) for credit users

    Credit users have mint_amount_wei = 0 (no debt on their position).
    Their alAssets come from the debt users' minted pool. Multisig burns remainder manually.
    """

    user_address: Address
    asset_type: AssetType
    chain: str

    deposit_amount_wei: Wei         # MYT shares to deposit (1:1 with underlying at migration time)
    mint_amount_wei: Wei            # alAssets to mint (debt users only; 0 for credit users)
    credit_amount_wei: Wei          # alAssets owed to user (0 for pure debt users)

    # Assigned at generation time, before batching
    token_id: TokenId = 0           # Filled in after deposit tx executes (0 = auto-assign)

    def __post_init__(self) -> None:
        if not self.user_address.startswith("0x"):
            raise ValueError(f"Invalid address: {self.user_address}")
        if self.deposit_amount_wei < 0:
            raise ValueError("deposit_amount_wei cannot be negative")
        if self.mint_amount_wei < 0:
            raise ValueError("mint_amount_wei cannot be negative")
        if self.credit_amount_wei < 0:
            raise ValueError("credit_amount_wei cannot be negative")
        # Credit users have mint_amount_wei = 0 (no debt on position) and credit_amount_wei > 0.
        # Debt users have mint_amount_wei > 0 and credit_amount_wei = 0.
        # Both should never be > 0 simultaneously.

    @property
    def is_debt_user(self) -> bool:
        return self.mint_amount_wei > 0

    @property
    def needs_burn(self) -> bool:
        """True for any position that requires a burn in Phase 3 (debt users and credit users
        whose temp mint must be cleared). Equivalent to is_debt_user; provided as a clearer
        name for burn-phase logic."""
        return self.mint_amount_wei > 0

    @property
    def is_credit_user(self) -> bool:
        return self.credit_amount_wei > 0


@dataclass
class TransactionCall:
    """A single encoded transaction call, ready to pack into a MultiSend batch."""

    to: Address
    data: bytes
    value: Wei = 0
    gas_estimate: int = 0
    description: str = ""


@dataclass
class TransactionBatch:
    """A batch of calls packed together into one Safe MultiSend transaction.

    Each batch begins with a setDepositCap() call that raises the cap
    by the sum of deposits in this batch.
    """

    calls: list[TransactionCall] = field(default_factory=list)
    total_gas: int = 0
    batch_number: int = 0
    deposit_sum_wei: int = 0        # Sum of deposit amounts in this batch (for cap raise)
    batch_type: str = "deposit"     # "deposit", "burn", "transfer", "credit"

    def add_call(self, call: TransactionCall) -> None:
        self.calls.append(call)
        self.total_gas += call.gas_estimate


@dataclass
class MigrationPlan:
    """Complete migration plan for one asset type on one chain.

    1. deposit_batches  — setDepositCap + deposit (creates NFTs)
    2. (read_ids)       — read events → token ID map (not a batch)
    3. mint_batches     — mint alAssets for debt users using real token IDs
    4. (verify)         — check positions match snapshot (not a batch)
    5. transfer_batches — send NFTs to users
    6. credit_batches   — send alAssets to credit users

    Burn is handled manually by the multisig after all scripts complete.
    """

    chain: str
    asset_type: AssetType
    positions: list[PositionMigration] = field(default_factory=list)

    deposit_batches: list[TransactionBatch] = field(default_factory=list)
    mint_batches: list[TransactionBatch] = field(default_factory=list)
    transfer_batches: list[TransactionBatch] = field(default_factory=list)
    credit_batches: list[TransactionBatch] = field(default_factory=list)

    @property
    def total_deposit_wei(self) -> int:
        return sum(p.deposit_amount_wei for p in self.positions)

    @property
    def total_mint_wei(self) -> int:
        return sum(p.mint_amount_wei for p in self.positions)

    @property
    def total_credit_wei(self) -> int:
        return sum(p.credit_amount_wei for p in self.positions)

    @property
    def remaining_to_burn_wei(self) -> int:
        """alAssets left in multisig after credit distribution = total minted − credits sent.

        Burned manually by the multisig (not handled by migration scripts).
        """
        return self.total_mint_wei - self.total_credit_wei

    @property
    def debt_users(self) -> list[PositionMigration]:
        return [p for p in self.positions if p.is_debt_user]

    @property
    def credit_users(self) -> list[PositionMigration]:
        return [p for p in self.positions if p.is_credit_user]

    @property
    def zero_debt_users(self) -> list[PositionMigration]:
        return [p for p in self.positions if not p.is_debt_user and not p.is_credit_user]


@dataclass
class ValidationError:
    """A validation error in CSV data."""

    row_number: int
    field_name: str
    message: str
    value: str | None = None

    def __str__(self) -> str:
        base = f"Row {self.row_number}, field '{self.field_name}': {self.message}"
        if self.value is not None:
            base += f" (got: '{self.value}')"
        return base


@dataclass
class MigrationSummary:
    """Summary stats for a migration run."""

    chain: str
    asset_type: str
    total_positions: int
    debt_users: int
    credit_users: int
    zero_debt_users: int
    total_deposit_wei: int
    total_mint_wei: int
    total_credit_wei: int
    total_burn_wei: int
    total_batches: int
    errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
