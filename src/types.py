"""Data models and types for CDP migration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, TypeAlias


class AssetType(str, Enum):
    """Supported asset types for CDP positions."""

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
class PositionMigration:
    """Represents a single position to be migrated.

    Each position contains all the information needed to execute:
    1. deposit() - create the position with collateral
    2. mint() - borrow against the position
    3. transferFrom() - transfer NFT to original user
    """

    user_address: Address
    asset_type: Literal["USD", "ETH"]
    token_id: TokenId
    deposit_amount: Wei  # underlyingValue in wei
    mint_amount: Wei  # debt in wei
    chain: str

    def __post_init__(self) -> None:
        """Validate position data after initialization."""
        if not self.user_address.startswith("0x"):
            raise ValueError(f"Invalid address format: {self.user_address}")
        if self.deposit_amount < 0:
            raise ValueError(f"Deposit amount cannot be negative: {self.deposit_amount}")
        if self.mint_amount < 0:
            raise ValueError(f"Mint amount cannot be negative: {self.mint_amount}")
        if self.token_id < 0:
            raise ValueError(f"Token ID cannot be negative: {self.token_id}")


@dataclass
class CSVRow:
    """Represents a single row from the CSV input file.

    CSV Format:
    address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
    """

    address: Address
    usd_debt: float
    usd_underlying_value: float
    eth_debt: float
    eth_underlying_value: float
    row_number: int = 0  # For error reporting

    @property
    def has_usd_position(self) -> bool:
        """Check if this row has a USD position to migrate."""
        return self.usd_underlying_value > 0

    @property
    def has_eth_position(self) -> bool:
        """Check if this row has an ETH position to migrate."""
        return self.eth_underlying_value > 0


@dataclass
class TransactionCall:
    """Represents a single transaction call to be batched."""

    to: Address
    data: bytes
    value: Wei = 0
    gas_estimate: int = 0
    description: str = ""


@dataclass
class TransactionBatch:
    """A batch of transactions to be executed together in a Safe multisig."""

    calls: list[TransactionCall] = field(default_factory=list)
    total_gas: int = 0
    batch_number: int = 0

    def add_call(self, call: TransactionCall) -> None:
        """Add a call to the batch and update total gas."""
        self.calls.append(call)
        self.total_gas += call.gas_estimate


@dataclass
class MigrationSummary:
    """Summary of a migration operation for reporting."""

    chain: str
    total_positions: int
    usd_positions: int
    eth_positions: int
    total_batches: int
    total_transactions: int
    errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if there were any errors during migration."""
        return len(self.errors) > 0


@dataclass
class ValidationError:
    """Represents a validation error in CSV data."""

    row_number: int
    field_name: str
    message: str
    value: str | None = None

    def __str__(self) -> str:
        """Human-readable error message."""
        base_msg = f"Row {self.row_number}, field '{self.field_name}': {self.message}"
        if self.value is not None:
            base_msg += f" (got: '{self.value}')"
        return base_msg
