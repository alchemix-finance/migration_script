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
    underlying_value: Decimal   # collateral amount (human units, not wei)
    debt: Decimal               # debt amount; negative = credit
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

    Flow:
      1. deposit(deposit_amount_wei, multisig, 0)  → receives token_id from contract
      2. if mint_amount_wei > 0: mint(token_id, mint_amount_wei, multisig)
         — alAssets land in multisig, user's debt is recorded on position

    After all positions are created and verified:
      3. Transfer credit alAssets to credit_amount_wei users
      4. burn(debt_amount, token_id) on Alchemist for each debt user → clears debt
      5. transferFrom(multisig, user, token_id)
    """

    user_address: Address
    asset_type: AssetType
    chain: str

    deposit_amount_wei: Wei         # MYT shares to deposit (1:1 with underlying at migration time)
    mint_amount_wei: Wei            # alAssets to mint (0 for credit users)
    credit_amount_wei: Wei          # alAssets owed to user (0 for debt users)

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
        # A user cannot simultaneously have debt AND credit
        if self.mint_amount_wei > 0 and self.credit_amount_wei > 0:
            raise ValueError("Position cannot have both mint_amount and credit_amount")

    @property
    def is_debt_user(self) -> bool:
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

    Phases:
      deposit_batches  — raise cap + deposit + mint per user
      burn_batches     — burn excess alAssets per debt-user position
      credit_batches   — transfer alAssets to credit users
      transfer_batches — transfer NFTs to users
    """

    chain: str
    asset_type: AssetType
    positions: list[PositionMigration] = field(default_factory=list)

    deposit_batches: list[TransactionBatch] = field(default_factory=list)
    burn_batches: list[TransactionBatch] = field(default_factory=list)
    credit_batches: list[TransactionBatch] = field(default_factory=list)
    transfer_batches: list[TransactionBatch] = field(default_factory=list)

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
    def total_burn_wei(self) -> int:
        """alAssets to burn = total minted - total credit owed to credit users."""
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
