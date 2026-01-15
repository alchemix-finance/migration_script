"""Chain and asset configuration for CDP migration.

This module contains all chain-specific addresses and configuration.
Addresses are placeholders and must be filled in before migration.
"""

from pathlib import Path
from typing import TypedDict

from src.types import AssetType, ChainName


class ChainConfig(TypedDict):
    """Configuration for a single chain."""

    chain_id: int
    multisig: str  # Temporary migration multisig
    cdp_usd: str  # CDP contract for USD positions (deposit/mint)
    cdp_eth: str  # CDP contract for ETH positions (deposit/mint)
    nft_usd: str  # NFT contract for USD positions (transfer)
    nft_eth: str  # NFT contract for ETH positions (transfer)
    collateral_usd: str  # USD collateral token address
    collateral_eth: str  # ETH collateral token address (or WETH)


# Chain configurations with placeholder addresses
# TODO: Fill in actual contract addresses before migration
CHAINS: dict[str, ChainConfig] = {
    "mainnet": {
        "chain_id": 1,
        "multisig": "",  # Temporary migration multisig
        "cdp_usd": "",  # CDP contract for USD positions (deposit/mint)
        "cdp_eth": "",  # CDP contract for ETH positions (deposit/mint)
        "nft_usd": "",  # NFT contract for USD positions (transfer)
        "nft_eth": "",  # NFT contract for ETH positions (transfer)
        "collateral_usd": "",  # USD collateral token address
        "collateral_eth": "",  # ETH collateral token address (or WETH)
    },
    "optimism": {
        "chain_id": 10,
        "multisig": "",
        "cdp_usd": "",
        "cdp_eth": "",
        "nft_usd": "",
        "nft_eth": "",
        "collateral_usd": "",
        "collateral_eth": "",
    },
    "arbitrum": {
        "chain_id": 42161,
        "multisig": "",
        "cdp_usd": "",
        "cdp_eth": "",
        "nft_usd": "",
        "nft_eth": "",
        "collateral_usd": "",
        "collateral_eth": "",
    },
}

# Gas configuration
GAS_BATCH_LIMIT = 15_200_000  # 16M with 5% buffer
GAS_HEADROOM_PERCENT = 5

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"
LOGS_DIR = PROJECT_ROOT / "logs"

# ABI file paths
CDP_ABI_PATH = CONTRACTS_DIR / "cdp_abi.json"
ERC721_ABI_PATH = CONTRACTS_DIR / "erc721_abi.json"


def get_chain_config(chain: str) -> ChainConfig:
    """Get configuration for a specific chain.

    Args:
        chain: Chain name (mainnet, optimism, arbitrum)

    Returns:
        Chain configuration dictionary

    Raises:
        ValueError: If chain is not supported
    """
    chain_lower = chain.lower()
    if chain_lower not in CHAINS:
        supported = ", ".join(CHAINS.keys())
        raise ValueError(f"Unsupported chain: {chain}. Supported chains: {supported}")
    return CHAINS[chain_lower]


def get_cdp_contract_address(chain: str, asset_type: str) -> str:
    """Get the CDP contract address for a chain and asset type.

    Args:
        chain: Chain name
        asset_type: Asset type (USD or ETH)

    Returns:
        Contract address string
    """
    config = get_chain_config(chain)
    if asset_type.upper() == AssetType.USD.value:
        return config["cdp_usd"]
    elif asset_type.upper() == AssetType.ETH.value:
        return config["cdp_eth"]
    else:
        raise ValueError(f"Unsupported asset type: {asset_type}")


def get_nft_contract_address(chain: str, asset_type: str) -> str:
    """Get the NFT contract address for a chain and asset type.

    Args:
        chain: Chain name
        asset_type: Asset type (USD or ETH)

    Returns:
        Contract address string
    """
    config = get_chain_config(chain)
    if asset_type.upper() == AssetType.USD.value:
        return config["nft_usd"]
    elif asset_type.upper() == AssetType.ETH.value:
        return config["nft_eth"]
    else:
        raise ValueError(f"Unsupported asset type: {asset_type}")


def get_csv_path(chain: str) -> Path:
    """Get the CSV file path for a specific chain.

    Args:
        chain: Chain name

    Returns:
        Path to the CSV file
    """
    # Validate chain name first
    get_chain_config(chain)
    return DATA_DIR / f"{chain.lower()}.csv"


def validate_chain_config(chain: str) -> list[str]:
    """Validate that all required addresses are configured for a chain.

    Args:
        chain: Chain name

    Returns:
        List of missing configuration fields (empty if all configured)
    """
    config = get_chain_config(chain)
    missing = []

    required_fields = [
        "multisig",
        "cdp_usd",
        "cdp_eth",
        "nft_usd",
        "nft_eth",
        "collateral_usd",
        "collateral_eth",
    ]

    for field in required_fields:
        if not config.get(field):
            missing.append(field)

    return missing


def get_supported_chains() -> list[str]:
    """Get list of supported chain names.

    Returns:
        List of chain name strings
    """
    return list(CHAINS.keys())


# Valid chain names constant
VALID_CHAINS = ("mainnet", "optimism", "arbitrum")


class ChainConfigError(Exception):
    """Raised when chain configuration is invalid or incomplete."""

    def __init__(self, chain: str, missing_fields: list[str], message: str = ""):
        self.chain = chain
        self.missing_fields = missing_fields
        self.message = message or f"Chain '{chain}' configuration incomplete. Missing or empty: {', '.join(missing_fields)}"
        super().__init__(self.message)


def is_valid_address(address: str) -> bool:
    """Check if an address is valid (non-empty and properly formatted).

    Args:
        address: Address string to validate

    Returns:
        True if valid, False otherwise
    """
    if not address or not isinstance(address, str):
        return False
    # Must start with 0x and have 40 hex characters after
    if not address.startswith("0x"):
        return False
    if len(address) != 42:
        return False
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def verify_chain_config(
    chain: str,
    has_usd_positions: bool = True,
    has_eth_positions: bool = True,
    require_all: bool = False,
) -> None:
    """Verify that required chain configuration is set before execution.

    This function verifies that the chain configuration has valid addresses
    for the operations that will be performed. It raises an error if any
    required addresses are missing or placeholder.

    Args:
        chain: Chain name (mainnet, optimism, arbitrum)
        has_usd_positions: Whether there are USD positions to migrate
        has_eth_positions: Whether there are ETH positions to migrate
        require_all: If True, verify all addresses regardless of position types

    Raises:
        ChainConfigError: If required configuration is missing or invalid
        ValueError: If chain is not supported

    Required addresses:
    - multisig: Always required
    - cdp_usd / nft_usd: Required if has_usd_positions
    - cdp_eth / nft_eth: Required if has_eth_positions
    """
    config = get_chain_config(chain)
    missing = []

    # Multisig is always required
    if not is_valid_address(config.get("multisig", "")):
        missing.append("multisig")

    # Check USD-specific addresses if needed
    if has_usd_positions or require_all:
        if not is_valid_address(config.get("cdp_usd", "")):
            missing.append("cdp_usd")
        if not is_valid_address(config.get("nft_usd", "")):
            missing.append("nft_usd")

    # Check ETH-specific addresses if needed
    if has_eth_positions or require_all:
        if not is_valid_address(config.get("cdp_eth", "")):
            missing.append("cdp_eth")
        if not is_valid_address(config.get("nft_eth", "")):
            missing.append("nft_eth")

    if missing:
        raise ChainConfigError(chain, missing)


def get_required_config_fields(
    has_usd_positions: bool = True,
    has_eth_positions: bool = True,
) -> list[str]:
    """Get list of required configuration fields based on position types.

    Args:
        has_usd_positions: Whether there are USD positions
        has_eth_positions: Whether there are ETH positions

    Returns:
        List of required field names
    """
    fields = ["multisig"]

    if has_usd_positions:
        fields.extend(["cdp_usd", "nft_usd"])

    if has_eth_positions:
        fields.extend(["cdp_eth", "nft_eth"])

    return fields
