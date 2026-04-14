import src.env  # Load .env on startup
#!/usr/bin/env python3
"""Read token IDs from deposit events and map them to CSV positions.

Usage:
    ape run read_ids --chain mainnet --asset usd --from-block 12345678
    ape run read_ids --chain mainnet --asset usd --from-block 12345678 --to-block 12345700

Run this AFTER `ape run deposit` has fully executed on-chain.

Queries the AlchemistV3Position NFT contract for ERC721 Transfer events
where from=address(0) (mint) and to=multisig. These correspond 1:1 with
the deposit() calls, in the same order as the CSV.

Writes the mapping to: data/token_ids-{alUSD|alETH}-{chain}.json
This file is consumed by `ape run mint` and `ape run distribute`.
"""

import json
import os

import click
from eth_utils import keccak
from web3 import Web3

from src.config import (
    CHAINS,
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    get_token_ids_path,
)
from src.types import AssetType
from src.validation import validate_csv_file

# ERC721 Transfer(address indexed from, address indexed to, uint256 indexed tokenId)
TRANSFER_EVENT_TOPIC = "0x" + keccak(text="Transfer(address,address,uint256)").hex()
ZERO_ADDRESS_TOPIC = "0x" + "0" * 64


@click.command()
@click.option("--chain", "chain_name", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--from-block", type=int, required=True, help="Block number where deposit script started.")
@click.option("--to-block", type=int, default=None, help="End block (default: latest).")
def cli(chain_name: str, asset: str, from_block: int, to_block: int | None) -> None:
    """Read NFT mint events and map token IDs to CSV positions."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    chain_config = get_chain_config(chain_name)
    asset_config = get_asset_config(chain_name, asset_type)

    nft_address = asset_config.get("nft", "")
    if not nft_address:
        click.echo(click.style("Error: NFT address not configured in config.py", fg="red"))
        raise SystemExit(1)

    multisig = chain_config["multisig"]
    multisig_topic = "0x" + multisig[2:].lower().zfill(64)

    # Load CSV positions (same order as deposits)
    csv_path = get_csv_path(chain_name, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"Error: CSV not found: {csv_path}", fg="red"))
        raise SystemExit(1)

    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain_name, asset_type, myt_decimals=myt_decimals)
    if not result.is_valid:
        click.echo(click.style("Error: CSV validation failed", fg="red"))
        raise SystemExit(1)

    positions = result.positions
    click.echo(f"Loaded {len(positions)} positions from CSV")
    click.echo(f"Querying NFT events on {nft_address} from block {from_block}...")

    # Connect to RPC directly (avoids needing ape provider setup)
    alchemy_key = (
        os.environ.get("WEB3_ALCHEMY_API_KEY")
        or os.environ.get("ALCHEMY_API_KEY")
        or ""
    ).strip()
    chain_id = CHAINS[chain_name]["chain_id"]
    rpc_urls = {
        1: f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}",
        10: f"https://opt-mainnet.g.alchemy.com/v2/{alchemy_key}",
        42161: f"https://arb-mainnet.g.alchemy.com/v2/{alchemy_key}",
    }
    rpc_url = (
        os.environ.get("FORK_RPC_URL", "")
        or os.environ.get({1: "MAINNET_RPC_URL", 10: "OPTIMISM_RPC_URL", 42161: "ARBITRUM_RPC_URL"}.get(chain_id, ""), "")
        or rpc_urls.get(chain_id, "")
    )

    is_alchemy = "alchemy.com" in rpc_url

    if not rpc_url or (is_alchemy and not alchemy_key):
        click.echo(click.style("Error: WEB3_ALCHEMY_API_KEY (or ALCHEMY_API_KEY) not set", fg="red"))
        raise SystemExit(1)

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        click.echo(click.style("Error: could not connect to RPC", fg="red"))
        raise SystemExit(1)

    end_block = to_block or w3.eth.block_number
    click.echo(f"Block range: {from_block} → {end_block}")

    topics = [
        TRANSFER_EVENT_TOPIC,   # Transfer event
        ZERO_ADDRESS_TOPIC,     # from = address(0) (mint)
        multisig_topic,         # to = multisig
    ]

    # Non-Alchemy RPCs (e.g. local anvil fork) — use standard eth_getLogs.
    all_logs: list = []
    if not is_alchemy:
        click.echo(f"  Using standard eth_getLogs against {rpc_url}")
        logs_raw = w3.eth.get_logs({
            "fromBlock": from_block,
            "toBlock": end_block,
            "address": Web3.to_checksum_address(nft_address),
            "topics": topics,
        })
        for log in logs_raw:
            token_id = int.from_bytes(log["topics"][3], "big")
            all_logs.append({"tokenId": hex(token_id), "blockNum": log["blockNumber"], "logIndex": log["logIndex"]})
        # Preserve (block, logIndex) order so the mapping matches deposit order.
        all_logs.sort(key=lambda t: (t.get("blockNum", 0), t.get("logIndex", 0)))
        logs = all_logs
        click.echo(f"Found {len(logs)} NFT mint events")

        if len(logs) != len(positions):
            click.echo(click.style(
                f"MISMATCH: {len(logs)} events vs {len(positions)} CSV positions",
                fg="red",
            ))
            raise SystemExit(1)

        token_id_map = {}
        for transfer, position in zip(logs, positions):
            token_id = int(transfer["tokenId"], 16)
            token_id_map[position.user_address.lower()] = token_id
        output_path = get_token_ids_path(chain_name, asset_type)
        with open(output_path, "w") as f:
            json.dump(token_id_map, f, indent=2)
        click.echo(click.style(f"\nWrote {len(token_id_map)} token IDs to {output_path}", fg="green"))
        items = list(token_id_map.items())
        for addr, tid in items[:5]:
            click.echo(f"  {addr} → tokenId {tid}")
        if len(items) > 5:
            click.echo(f"  ... +{len(items) - 5} more")
        return

    # Use Alchemy's getAssetTransfers API to fetch all NFT mints in bulk
    # (avoids eth_getLogs block range limits on free tier)
    page_key = None

    while True:
        payload_body = {
            "fromBlock": hex(from_block),
            "toBlock": hex(end_block),
            "fromAddress": "0x0000000000000000000000000000000000000000",
            "toAddress": multisig,
            "contractAddresses": [nft_address],
            "category": ["erc721"],
            "withMetadata": False,
            "excludeZeroValue": False,
            "maxCount": "0x3e8",  # 1000 per page
        }
        if page_key:
            payload_body["pageKey"] = page_key

        payload = {
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [payload_body],
            "id": 1,
        }

        import ssl
        import certifi
        import urllib.request

        ctx = ssl.create_default_context(cafile=certifi.where())
        req = urllib.request.Request(
            rpc_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        result = json.loads(resp.read().decode())

        if "error" in result:
            click.echo(click.style(f"Alchemy API error: {result['error']}", fg="red"))
            raise SystemExit(1)

        transfers = result.get("result", {}).get("transfers", [])
        all_logs.extend(transfers)
        click.echo(f"  Fetched {len(transfers)} transfers (total: {len(all_logs)})")

        page_key = result.get("result", {}).get("pageKey")
        if not page_key:
            break

    logs = all_logs
    click.echo(f"Found {len(logs)} NFT mint events")

    if len(logs) != len(positions):
        click.echo(click.style(
            f"MISMATCH: {len(logs)} events vs {len(positions)} CSV positions",
            fg="red",
        ))
        if len(logs) < len(positions):
            click.echo("Not all deposit batches may have executed yet.")
        else:
            click.echo("More events than expected — check block range or NFT address.")
        raise SystemExit(1)

    # Extract token IDs from event logs (topics[3] = indexed tokenId)
    # Events are ordered by (blockNumber, logIndex), matching CSV/deposit order.
    token_id_map: dict[str, int] = {}
    for i, (transfer, position) in enumerate(zip(logs, positions)):
        # alchemy_getAssetTransfers returns tokenId as a hex string or decimal
        raw_token_id = transfer.get("tokenId", transfer.get("erc721TokenId", "0x0"))
        token_id = int(raw_token_id, 16) if isinstance(raw_token_id, str) and raw_token_id.startswith("0x") else int(raw_token_id)
        addr = position.user_address.lower()
        token_id_map[addr] = token_id

    # Write mapping
    output_path = get_token_ids_path(chain_name, asset_type)
    with open(output_path, "w") as f:
        json.dump(token_id_map, f, indent=2)

    click.echo(click.style(f"\nWrote {len(token_id_map)} token IDs to {output_path}", fg="green"))

    # Print first few for verification
    items = list(token_id_map.items())
    for addr, tid in items[:5]:
        click.echo(f"  {addr} → tokenId {tid}")
    if len(items) > 5:
        click.echo(f"  ... +{len(items) - 5} more")

    click.echo(click.style(
        f"\nNext: run `ape run mint --chain {chain_name} --asset {asset}` to mint alAssets.",
        fg="cyan",
    ))
