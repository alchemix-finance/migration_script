"""Chain and asset configuration for V3 migration.

Addresses are placeholders until deployment. The multisig addresses
are already known (provided by scoopy).
"""

from pathlib import Path
from typing import TypedDict

from src.types import AssetType


class AssetConfig(TypedDict):
    """Configuration for one asset type within a chain."""

    alchemist: str      # AlchemistV3 contract for this asset
    myt: str            # MYT token (USDCMYT or WETHMYT)
    al_token: str       # alUSD or alETH token
    underlying: str     # USDC or WETH
    nft: str            # AlchemistV3Position contract — separate from AlchemistV3. Read from alchemist.alchemistPositionNFT()
    myt_decimals: int   # Decimal precision of the MYT vault token (6 for USDCMYT, 18 for WETHMYT).
                        # CSV underlyingValue is exported as 18-decimal wei; deposit amount is
                        # computed as csv_value // 10^(18 - myt_decimals). Debt values are always
                        # 18-decimal alToken units and are NOT scaled by this field.


class ChainConfig(TypedDict):
    """Configuration for a single chain."""

    chain_id: int
    multisig: str                   # Migration multisig — known
    usd: AssetConfig               # USDC → alUSD path
    eth: AssetConfig               # WETH → alETH path


# Gas configuration
GAS_LIMIT = 16_000_000
GAS_TARGET_PERCENT = 0.90          # Target 90% of gas limit per batch
EFFECTIVE_GAS_LIMIT = int(GAS_LIMIT * GAS_TARGET_PERCENT)  # 14,400,000

# Gas estimates per operation type
GAS_SET_DEPOSIT_CAP = 35_000       # setDepositCap() — cheap admin setter
GAS_DEPOSIT = 175_000              # deposit(amount, multisig, 0) — mints NFT + transfers MYT
GAS_MINT = 130_000                 # mint(tokenId, amount, multisig) — mints alAssets
GAS_BURN = 120_000                 # burn(amount, tokenId) on Alchemist — burns alAssets, clears debt
GAS_TRANSFER_ALTOKEN = 65_000      # alToken.transfer(user, amount) — send credit to user
GAS_TRANSFER_NFT = 70_000          # ERC721.transferFrom(multisig, user, tokenId)
GAS_ALTOKEN_BURN = 35_000          # alToken.burn(amount) — ERC20Burnable direct burn

# Large position surcharge (> 1000 tokens in wei)
LARGE_POSITION_THRESHOLD = 10 ** 21
GAS_LARGE_POSITION_SURCHARGE = 15_000


CHAINS: dict[str, ChainConfig] = {
    "mainnet": {
        "chain_id": 1,
        "multisig": "0xF56D660138815fC5d7a06cd0E1630225E788293D",
        "usd": {
            "alchemist": "",    # TBD — not yet deployed
            "myt": "",
            "al_token": "",
            "underlying": "",
            "nft": "",          # AlchemistV3Position address — fill in after deployment
            "myt_decimals": 18, # USDCMYT vault uses 18 decimals (standard ERC-4626)
        },
        "eth": {
            "alchemist": "",
            "myt": "",
            "al_token": "",
            "underlying": "",
            "nft": "",          # AlchemistV3Position address — fill in after deployment
            "myt_decimals": 18, # WETHMYT vault uses 18 decimals (same as WETH underlying)
        },
    },
    "optimism": {
        "chain_id": 10,
        "multisig": "0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d",
        "usd": {
            "alchemist": "",
            "myt": "",
            "al_token": "",
            "underlying": "",
            "nft": "",          # AlchemistV3Position address — fill in after deployment
            "myt_decimals": 18, # USDCMYT vault uses 18 decimals (standard ERC-4626)
        },
        "eth": {
            "alchemist": "",
            "myt": "",
            "al_token": "",
            "underlying": "",
            "nft": "",          # AlchemistV3Position address — fill in after deployment
            "myt_decimals": 18, # WETHMYT vault uses 18 decimals (same as WETH underlying)
        },
    },
    "arbitrum": {
        "chain_id": 42161,
        "multisig": "0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b",
        "usd": {
            "alchemist": "",
            "myt": "",
            "al_token": "",
            "underlying": "",
            "nft": "",          # AlchemistV3Position address — fill in after deployment
            "myt_decimals": 18, # USDCMYT vault uses 18 decimals (standard ERC-4626)
        },
        "eth": {
            "alchemist": "",
            "myt": "",
            "al_token": "",
            "underlying": "",
            "nft": "",          # AlchemistV3Position address — fill in after deployment
            "myt_decimals": 18, # WETHMYT vault uses 18 decimals (same as WETH underlying)
        },
    },
}

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"
LOGS_DIR = PROJECT_ROOT / "logs"

# ABI paths
ALCHEMIST_ABI_PATH = CONTRACTS_DIR / "alchemist_abi.json"
ERC721_ABI_PATH = CONTRACTS_DIR / "erc721_abi.json"
ALTOKEN_ABI_PATH = CONTRACTS_DIR / "altoken_abi.json"

VALID_CHAINS = tuple(CHAINS.keys())


def get_chain_config(chain: str) -> ChainConfig:
    chain_lower = chain.lower()
    if chain_lower not in CHAINS:
        raise ValueError(f"Unsupported chain: {chain}. Supported: {', '.join(CHAINS)}")
    return CHAINS[chain_lower]


def get_asset_config(chain: str, asset_type: AssetType) -> AssetConfig:
    config = get_chain_config(chain)
    key = "usd" if asset_type == AssetType.USD else "eth"
    return config[key]


def get_supported_chains() -> list[str]:
    return list(CHAINS.keys())


def get_csv_path(chain: str, asset_type: AssetType) -> Path:
    """Return path for alAssetValues-sum-and-debt-chain.csv."""
    get_chain_config(chain)  # validate chain
    prefix = "alUSD" if asset_type == AssetType.USD else "alETH"
    return DATA_DIR / f"{prefix}Values-sum-and-debt-{chain.lower()}.csv"


def validate_asset_config(chain: str, asset_type: AssetType) -> list[str]:
    """Return list of empty/missing fields in the asset config."""
    asset = get_asset_config(chain, asset_type)
    missing = []
    for field in ("alchemist", "myt", "al_token", "underlying"):
        if not asset.get(field):
            missing.append(field)
    return missing


class ChainConfigError(Exception):
    def __init__(self, chain: str, missing_fields: list[str]):
        self.chain = chain
        self.missing_fields = missing_fields
        super().__init__(
            f"Chain '{chain}' configuration incomplete. Missing: {', '.join(missing_fields)}"
        )


def is_valid_address(address: str) -> bool:
    if not address or not isinstance(address, str):
        return False
    if not address.startswith("0x"):
        return False
    if len(address) != 42:
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False


def verify_asset_config(chain: str, asset_type: AssetType) -> None:
    """Raise ChainConfigError if required addresses are not set."""
    missing = validate_asset_config(chain, asset_type)
    if missing:
        raise ChainConfigError(chain, [f"{asset_type.value}.{f}" for f in missing])

    config = get_chain_config(chain)
    if not is_valid_address(config["multisig"]):
        raise ChainConfigError(chain, ["multisig"])
