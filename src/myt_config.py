"""Alchemix V3 contract reference — MYT vaults, underlyings, alchemists, and
related addresses per chain × asset.

Sourced from the Alchemix V3 Operator Dashboard SPA bundle and verified
on-chain via direct RPC calls to each MYT vault's `asset()` accessor
(ERC-4626 standard).

Do not edit by hand without re-running scripts/fetch_underlying.py.
"""

MYT_CONFIG: dict[str, dict[str, dict[str, str | int]]] = {
    "mainnet": {
        "alUSD": {
            "alchemist": "0xeB83112d925268BeDe86654C13D423a987587e3E",
            "transmuter": "0x2584E8b0616b3E750492c9629a3b27679C410cb9",
            "myt": "0x9B44efCa3e2a707B63Dc00CE79d646E5E5D24bA5",
            "myt_symbol": "",  # vault symbol() returned empty string
            "myt_decimals": 18,
            "allocator": "0x693b7594Ae0633d9c5574D0da46a040f92F5b281",
            "underlying": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "underlying_symbol": "USDC",
            "underlying_decimals": 6,
        },
        "alETH": {
            "alchemist": "0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B",
            "transmuter": "0x073598132f37756a7E665FB52f1757463120bd3C",
            "myt": "0x29bcfeD246ce37319d94eBa107db90C453D4c43D",
            "myt_symbol": "",
            "myt_decimals": 18,
            "allocator": "0x23a3C27Bb007887FD8CbfEaF323799093a450e7e",
            "underlying": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "underlying_symbol": "WETH",
            "underlying_decimals": 18,
        },
    },
    "arbitrum": {
        "alUSD": {
            "alchemist": "0x930750a3510E703535e943E826ABa3c364fFC1De",
            "transmuter": "0x693b7594Ae0633d9c5574D0da46a040f92F5b281",
            "myt": "0xEba62B842081CeF5a8184318Dc5C4E4aACa9f651",
            "myt_symbol": "mixUSDC",
            "myt_decimals": 18,
            "allocator": "0x143C2118417F2DF7489Ad241023B3BE915906865",
            "underlying": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            "underlying_symbol": "USDC",
            "underlying_decimals": 6,
        },
        "alETH": {
            "alchemist": "0xDeD3A04612FF12b57317abE38e68026Fc9D28114",
            "transmuter": "0x2584E8b0616b3E750492c9629a3b27679C410cb9",
            "myt": "0xfe8F223F3d81462F55bf8609897B8cEcfA4B195C",
            "myt_symbol": "",
            "myt_decimals": 18,
            "allocator": "0x12114Eb8e17800b3B2E777339b9E0C32638E0be0",
            "underlying": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
            "underlying_symbol": "WETH",
            "underlying_decimals": 18,
        },
    },
    "optimism": {
        "alUSD": {
            "alchemist": "0x930750a3510E703535e943E826ABa3c364fFC1De",
            "transmuter": "0x693b7594Ae0633d9c5574D0da46a040f92F5b281",
            "myt": "0xAf510a560744880410f0f65e3341A020FBC2cA41",
            "myt_symbol": "",
            "myt_decimals": 18,
            "allocator": "0x143C2118417F2DF7489Ad241023B3BE915906865",
            "underlying": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
            "underlying_symbol": "USDC",
            "underlying_decimals": 6,
        },
        "alETH": {
            "alchemist": "0xDeD3A04612FF12b57317abE38e68026Fc9D28114",
            "transmuter": "0x2584E8b0616b3E750492c9629a3b27679C410cb9",
            "myt": "0x91b8657aea26Caa8A0E9D6DD4E24727Ccf32F822",
            "myt_symbol": "",
            "myt_decimals": 18,
            "allocator": "0x12114Eb8e17800b3B2E777339b9E0C32638E0be0",
            "underlying": "0x4200000000000000000000000000000000000006",
            "underlying_symbol": "WETH",
            "underlying_decimals": 18,
        },
    },
}


MIGRATION_MULTISIG: dict[str, str] = {
    "mainnet": "0xF56D660138815fC5d7a06cd0E1630225E788293D",
    "optimism": "0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d",
    "arbitrum": "0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b",
}


# V2 alchemist addresses — the CURRENT whitelisted minters on each alToken.
# Sourced from github.com/alchemix-finance/deployments/tree/master/<chain>/AlchemistV2_<asset>.json
# and verified on-chain (`whiteList`/`whitelisted` returned True for each except Arbitrum alUSD,
# which has already been transitioned to the V3 alchemist).
#
# For the V3 migration to begin minting, each alToken owner must call:
#   alToken.setWhitelist(V2_ALCHEMIST, false)
#   alToken.setWhitelist(V3_ALCHEMIST, true)    # V3 from MYT_CONFIG[chain][asset]["alchemist"]
V2_ALCHEMIST: dict[str, dict[str, str]] = {
    "mainnet": {
        "alUSD": "0x5C6374a2ac4EBC38DeA0Fc1F8716e5Ea1AdD94dd",
        "alETH": "0x062Bf725dC4cDF947aa79Ca2aaCCD4F385b13b5c",
    },
    "optimism": {
        "alUSD": "0x10294d57A419C8eb78C648372c5bAA27fD1484af",
        "alETH": "0xe04Bb5B4de60FA2fBa69a93adE13A8B3B569d5B4",
    },
    "arbitrum": {
        "alUSD": "0xb46eE2E4165F629b4aBCE04B7Eb4237f951AC66F",  # already revoked
        "alETH": "0x654e16a0b161b150F5d1C8a5ba6E7A7B7760703A",
    },
}


# Owner of each alToken (must be the signer for setWhitelist).
# Discovered via `owner()` (L2) / AccessControl `ADMIN` role (mainnet).
AL_TOKEN_OWNER: dict[str, str] = {
    "mainnet": "0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9",   # ETH Ops Multisig (one of two ADMIN holders)
    "optimism": "0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a",  # OP Ops Multisig
    "arbitrum": "0x7e108711771DfdB10743F016D46d75A9379cA043",  # ARB Ops Multisig
}


# The name of the whitelist mapping accessor — differs between V1-era mainnet
# alTokens (`whiteList` with a capital L) and the FRAX-canonical L2 alTokens
# (`whitelisted`). setWhitelist() is uniform across all.
WHITELIST_ACCESSOR: dict[str, str] = {
    "mainnet": "whiteList",
    "optimism": "whitelisted",
    "arbitrum": "whitelisted",
}


def get(chain: str, asset: str) -> dict[str, str | int]:
    """Return the contract bundle for a given chain + asset ('alUSD' | 'alETH')."""
    return MYT_CONFIG[chain][asset]
