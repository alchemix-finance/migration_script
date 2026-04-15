"""Fetch underlying tokens for each MYT vault by calling asset()/underlyingToken()
on a live Alchemy RPC for each chain. Prints a Python dict ready to paste.

Usage:
    ape run fetch_underlying
"""

import click
from ape import Contract, networks

MYT_VAULTS = {
    "mainnet": {
        "alUSD": "0x9B44efCa3e2a707B63Dc00CE79d646E5E5D24bA5",
        "alETH": "0x29bcfeD246ce37319d94eBa107db90C453D4c43D",
    },
    "arbitrum": {
        "alUSD": "0xEba62B842081CeF5a8184318Dc5C4E4aACa9f651",
        "alETH": "0xfe8F223F3d81462F55bf8609897B8cEcfA4B195C",
    },
    "optimism": {
        "alUSD": "0xAf510a560744880410f0f65e3341A020FBC2cA41",
        "alETH": "0x91b8657aea26Caa8A0E9D6DD4E24727Ccf32F822",
    },
}

MIN_ABI = [
    {"name": "asset", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"type": "address"}]},
    {"name": "underlyingToken", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"type": "address"}]},
    {"name": "symbol", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"type": "string"}]},
    {"name": "decimals", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"type": "uint8"}]},
    {"name": "name", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"type": "string"}]},
]


def _call_first(contract, fn_names):
    for fn in fn_names:
        try:
            return getattr(contract, fn)()
        except Exception:
            continue
    return None


ECOSYSTEM_BY_CHAIN = {
    "mainnet": "ethereum",
    "arbitrum": "arbitrum",
    "optimism": "optimism",
}


@click.command()
def cli():
    """Query each MYT vault for its underlying asset via live RPC."""
    result: dict = {}

    for chain, assets in MYT_VAULTS.items():
        ecosystem = ECOSYSTEM_BY_CHAIN[chain]
        net_id = f"{ecosystem}:mainnet:alchemy"
        click.echo(f"\n=== {chain} ({net_id}) ===")
        result[chain] = {}
        with networks.parse_network_choice(net_id):
            for asset_name, vault_addr in assets.items():
                vault = Contract(vault_addr, abi=MIN_ABI)
                underlying = _call_first(vault, ["asset", "underlyingToken"])
                vault_symbol = _call_first(vault, ["symbol"])
                vault_name = _call_first(vault, ["name"])
                vault_decimals = _call_first(vault, ["decimals"])

                under_symbol = under_decimals = None
                if underlying:
                    under = Contract(underlying, abi=MIN_ABI)
                    under_symbol = _call_first(under, ["symbol"])
                    under_decimals = _call_first(under, ["decimals"])

                result[chain][asset_name] = {
                    "myt": vault_addr,
                    "myt_name": vault_name,
                    "myt_symbol": vault_symbol,
                    "myt_decimals": vault_decimals,
                    "underlying": underlying,
                    "underlying_symbol": under_symbol,
                    "underlying_decimals": under_decimals,
                }
                click.echo(
                    f"  {asset_name}: MYT={vault_symbol} ({vault_decimals}d) "
                    f"-> underlying={under_symbol} @ {underlying} ({under_decimals}d)"
                )

    click.echo("\n\n# ---- Paste into src/myt_config.py ----")
    click.echo("MYT_CONFIG = {")
    for chain, assets in result.items():
        click.echo(f'    "{chain}": {{')
        for asset_name, info in assets.items():
            click.echo(f'        "{asset_name}": {{')
            for k, v in info.items():
                if isinstance(v, str):
                    click.echo(f'            "{k}": "{v}",')
                else:
                    click.echo(f'            "{k}": {v!r},')
            click.echo("        },")
        click.echo("    },")
    click.echo("}")


def main():
    cli()
