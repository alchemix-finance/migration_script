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


# Per-chain block gas limits (updated post-Pectra for mainnet, 2025-05)
CHAIN_GAS_LIMITS: dict[str, int] = {
    "mainnet": 60_000_000,          # Doubled in recent hardfork
    "optimism": 30_000_000,
    "arbitrum": 32_000_000,
}

# Per-chain max transaction calldata size (bytes)
CHAIN_TX_SIZE_LIMITS: dict[str, int] = {
    "mainnet": 131_072,             # 128 KB (geth hard limit)
    "optimism": 122_880,            # 120 KB
    "arbitrum": 117_964,            # ~118 KB (90% of 128 KB, DoS protection)
}

# Batching parameters
GAS_TARGET_PERCENT = 0.90           # Target 90% of block gas limit per batch
SIZE_TARGET_PERCENT = 0.90          # Target 90% of max tx size per batch
MAX_CALLS_PER_BATCH = 50            # Practical cap — keeps batches reviewable in Safe UI

# MultiSend encoding overhead (bytes)
MULTISEND_WRAPPER_BYTES = 68        # 4 (selector) + 32 (offset) + 32 (length)
MULTISEND_CALL_BYTES = 85           # 1 (op) + 20 (to) + 32 (value) + 32 (dataLen)

# Gas estimates per operation type
GAS_SET_DEPOSIT_CAP = 35_000        # setDepositCap() — cheap admin setter
GAS_DEPOSIT = 175_000               # deposit(amount, multisig, 0) — mints NFT + transfers MYT
GAS_MINT = 130_000                  # mint(tokenId, amount, multisig) — mints alAssets
GAS_TRANSFER_ALTOKEN = 65_000       # alToken.transfer(user, amount) — send credit to user
GAS_TRANSFER_NFT = 70_000           # ERC721.transferFrom(multisig, user, tokenId)

# Large position surcharge (> 1000 tokens in wei)
LARGE_POSITION_THRESHOLD = 10 ** 21
GAS_LARGE_POSITION_SURCHARGE = 15_000


def get_effective_gas_limit(chain: str) -> int:
    """90% of the chain's block gas limit."""
    base = CHAIN_GAS_LIMITS.get(chain.lower(), 30_000_000)
    return int(base * GAS_TARGET_PERCENT)


def get_effective_size_limit(chain: str) -> int:
    """90% of the chain's max transaction calldata size."""
    base = CHAIN_TX_SIZE_LIMITS.get(chain.lower(), 117_964)
    return int(base * SIZE_TARGET_PERCENT)


# Legacy alias — used by batch stats display
EFFECTIVE_GAS_LIMIT = get_effective_gas_limit("mainnet")


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


def get_token_ids_path(chain: str, asset_type: "AssetType") -> Path:
    """Return path for the token ID mapping JSON written by read_ids.py."""
    from src.types import AssetType as AT
    prefix = "alUSD" if asset_type == AT.USD else "alETH"
    return DATA_DIR / f"token_ids-{prefix}-{chain.lower()}.json"


def load_token_id_map(chain: str, asset_type: "AssetType") -> dict[str, int]:
    """Load the user→tokenId mapping from JSON. Keys are lowercase addresses."""
    import json
    path = get_token_ids_path(chain, asset_type)
    if not path.exists():
        raise FileNotFoundError(
            f"Token ID map not found: {path}\n"
            f"Run `ape run read_ids --chain {chain} --asset {'usd' if str(asset_type) == 'AssetType.USD' or str(asset_type) == 'USD' else 'eth'}` first."
        )
    with open(path) as f:
        raw = json.load(f)
    return {k.lower(): int(v) for k, v in raw.items()}

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
