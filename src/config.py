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
    myt: str            # MYT / ERC4626 share token passed to alchemist.deposit
    al_token: str       # alUSD or alETH token
    underlying: str     # Often vault asset(); may match myt for config completeness (unused by deposit encoding)
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


# Per-chain transaction gas limits (not block gas — a single tx can't fill a block)
# Mainnet block gas is 60M post-Pectra, but individual tx gas limit is ~15M.
CHAIN_GAS_LIMITS: dict[str, int] = {
    "mainnet": 15_000_000,          # Per-tx limit (block gas is 60M)
    "optimism": 15_000_000,
    "arbitrum": 15_000_000,
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
MAX_CALLS_PER_BATCH = 200           # Safety cap — real constraint is gas/size per chain

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


# Legacy alias
EFFECTIVE_GAS_LIMIT = get_effective_gas_limit("mainnet")  # 13,500,000


CHAINS: dict[str, ChainConfig] = {
    "mainnet": {
        "chain_id": 1,
        "multisig": "0xF56D660138815fC5d7a06cd0E1630225E788293D",
        "usd": {
            "alchemist": "0xeB83112d925268BeDe86654C13D423a987587e3E",
            "myt": "0x9B44efCa3e2a707B63Dc00CE79d646E5E5D24bA5",
            "al_token": "0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9",
            "underlying": "",
            "nft": "0x872a03FabC86b59c883CD9c439E969321b719bEB",
            "myt_decimals": 18,
        },
        "eth": {
            "alchemist": "0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B",
            "myt": "0x29bcfeD246ce37319d94eBa107db90C453D4c43D",
            "al_token": "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6",
            "underlying": "",
            "nft": "0x15da4c7db6404b92894d5214FAc92057Fb8a263d",
            "myt_decimals": 18,
        },
    },
    "optimism": {
        "chain_id": 10,
        "multisig": "0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d",
        "usd": {
            "alchemist": "0x930750a3510E703535e943E826ABa3c364fFC1De",
            "myt": "0xAf510a560744880410f0f65e3341A020FBC2cA41",
            "al_token": "0xCB8FA9a76b8e203D8C3797bF438d8FB81Ea3326A",
            "underlying": "",
            "nft": "0xF700c7e40efCA6f7a810e172AFCee3592ff4aD33",
            "myt_decimals": 18,
        },
        "eth": {
            "alchemist": "0xDeD3A04612FF12b57317abE38e68026Fc9D28114",
            "myt": "0x91b8657aea26Caa8A0E9D6DD4E24727Ccf32F822",
            "al_token": "0x3E29D3A9316dAB217754d13b28646B76607c5f04",
            "underlying": "",
            "nft": "0x763F5d567403add750e13234DB896CFe6b423059",
            "myt_decimals": 18,
        },
    },
    "arbitrum": {
        "chain_id": 42161,
        "multisig": "0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b",
        "usd": {
            "alchemist": "0x930750a3510E703535e943E826ABa3c364fFC1De",
            "myt": "0xEba62B842081CeF5a8184318Dc5C4E4aACa9f651",
            "al_token": "0xCB8FA9a76b8e203D8C3797bF438d8FB81Ea3326A",
            "underlying": "0xEba62B842081CeF5a8184318Dc5C4E4aACa9f651",
            "nft": "0xF700c7e40efCA6f7a810e172AFCee3592ff4aD33",
            "myt_decimals": 18,
        },
        "eth": {
            "alchemist": "0xDeD3A04612FF12b57317abE38e68026Fc9D28114",
            "myt": "0xfe8F223F3d81462F55bf8609897B8cEcfA4B195C",
            "al_token": "0x17573150d67d820542EFb24210371545a4868B03",
            "underlying": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
            "nft": "0x763F5d567403add750e13234DB896CFe6b423059",
            "myt_decimals": 18,
        },
    },
}
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
