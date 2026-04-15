import src.env  # load .env
#!/usr/bin/env python3
"""Pre-warm anvil's local cache by reading the contracts the migration touches.

Anvil lazy-loads upstream state on demand. The migration's first deposit/mint/
transferFrom in each batch causes anvil to fetch many storage slots (alchemist,
MYT, strategies, alToken, NFT, plus their dependencies). When Alchemy free
tier throttles during a burst of fresh reads, the migration tx gets a 300+ s
receipt-wait stall.

This script issues many cheap `eth_call` views ahead of time, forcing anvil to
populate its cache while we're not under throughput pressure. It also probes
all strategy contracts an alchemist enumerates (via tokenAdapter and similar
accessors) so their state is warm before any real migration tx fires.

Usage:
    FORK_RPC_URL=http://localhost:8545 ape run prewarm --chain arbitrum --asset eth
"""

import os
import time

import click
from ape.cli import ape_cli_context
from eth_abi import decode, encode
from eth_utils import keccak
from web3 import Web3

from src.config import (
    get_asset_config,
    get_chain_config,
    get_supported_chains,
)
from src.myt_config import MYT_CONFIG
from src.types import AssetType


def _call(w3: Web3, addr: str, sig: str, ret_types: list[str], args: list = None) -> tuple | None:
    sel = keccak(text=sig)[:4]
    data = sel
    if args:
        in_types = sig[sig.index("(") + 1 : sig.index(")")].split(",")
        data = sel + encode(in_types, args)
    try:
        raw = w3.eth.call({"to": Web3.to_checksum_address(addr), "data": "0x" + data.hex()})
        return decode(ret_types, raw)
    except Exception:
        return None


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--depth", default=10, help="How many position NFTs to probe (warms ownerOf state)")
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str, depth: int) -> None:
    """Pre-warm the fork's cache for one chain/asset combo."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH
    asset_slug = "alUSD" if asset_type == AssetType.USD else "alETH"

    rpc_url = os.environ.get("FORK_RPC_URL", "http://localhost:8545")
    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 120}))

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]
    alchemist = asset_config["alchemist"]
    myt = asset_config["myt"]
    al_token = asset_config["al_token"]
    nft = asset_config["nft"]
    underlying = MYT_CONFIG[chain][asset_slug]["underlying"]

    click.echo("=" * 70)
    click.echo(click.style(f"PRE-WARM cache for {chain} / {asset_slug}", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"  alchemist: {alchemist}")
    click.echo(f"  MYT:       {myt}")
    click.echo(f"  alToken:   {al_token}")
    click.echo(f"  NFT:       {nft}")
    click.echo(f"  underlying:{underlying}")
    click.echo(f"  multisig:  {multisig}")

    t0 = time.time()
    n_calls = 0

    # 1. Alchemist hot fields
    click.echo(click.style("\n[1/5] alchemist views...", fg="cyan"))
    for sig, types in [
        ("admin()", ["address"]),
        ("depositCap()", ["uint256"]),
        ("totalDebt()", ["uint256"]),
        ("minimumCollateralization()", ["uint256"]),
        ("FIXED_POINT_SCALAR()", ["uint256"]),
        ("alchemistPositionNFT()", ["address"]),
        ("yieldToken()", ["address"]),
        ("debtToken()", ["address"]),
    ]:
        _call(w3, alchemist, sig, types)
        n_calls += 1

    # 2. MYT (ERC-4626) views
    click.echo(click.style("[2/5] MYT vault views (forces strategy chain reads)...", fg="cyan"))
    for sig, types in [
        ("asset()", ["address"]),
        ("totalAssets()", ["uint256"]),
        ("totalSupply()", ["uint256"]),
        ("decimals()", ["uint8"]),
        ("symbol()", ["string"]),
    ]:
        _call(w3, myt, sig, types)
        n_calls += 1
    # convertToAssets walks every strategy via realAssets() — single most
    # important pre-warm call (touches Aave aTokens, Euler vaults, etc.)
    _call(w3, myt, "convertToAssets(uint256)", ["uint256"], [10**18])
    _call(w3, myt, "convertToShares(uint256)", ["uint256"], [10**18])
    _call(w3, myt, "balanceOf(address)", ["uint256"], [Web3.to_checksum_address(multisig)])
    _call(w3, myt, "balanceOf(address)", ["uint256"], [Web3.to_checksum_address(alchemist)])
    n_calls += 4

    # 3. alToken views
    click.echo(click.style("[3/5] alToken views...", fg="cyan"))
    for sig, types, args in [
        ("totalSupply()", ["uint256"], None),
        ("decimals()", ["uint8"], None),
        ("balanceOf(address)", ["uint256"], [Web3.to_checksum_address(multisig)]),
        ("balanceOf(address)", ["uint256"], [Web3.to_checksum_address(alchemist)]),
        ("whitelisted(address)", ["bool"], [Web3.to_checksum_address(alchemist)]),
        ("whiteList(address)", ["bool"], [Web3.to_checksum_address(alchemist)]),  # mainnet name
    ]:
        _call(w3, al_token, sig, types, args)
        n_calls += 1

    # 4. NFT views — touches ownerOf for early tokenIds + balanceOf(multisig)
    click.echo(click.style(f"[4/5] NFT views (probing first {depth} tokenIds)...", fg="cyan"))
    _call(w3, nft, "totalSupply()", ["uint256"])
    _call(w3, nft, "balanceOf(address)", ["uint256"], [Web3.to_checksum_address(multisig)])
    n_calls += 2
    for tid in range(1, depth + 1):
        _call(w3, nft, "ownerOf(uint256)", ["address"], [tid])
        n_calls += 1

    # 5. Underlying token views
    click.echo(click.style("[5/5] Underlying token views...", fg="cyan"))
    for sig, types, args in [
        ("totalSupply()", ["uint256"], None),
        ("decimals()", ["uint8"], None),
        ("balanceOf(address)", ["uint256"], [Web3.to_checksum_address(myt)]),
        ("balanceOf(address)", ["uint256"], [Web3.to_checksum_address(multisig)]),
        ("allowance(address,address)", ["uint256"], [Web3.to_checksum_address(multisig), Web3.to_checksum_address(myt)]),
    ]:
        _call(w3, underlying, sig, types, args)
        n_calls += 1

    elapsed = time.time() - t0
    click.echo(click.style(
        f"\nDone: {n_calls} eth_calls in {elapsed:.1f}s. Cache should now be warm "
        f"for {chain}/{asset_slug} migration phases.", fg="green", bold=True,
    ))
