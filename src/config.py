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
