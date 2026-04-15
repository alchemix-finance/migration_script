"""On-chain preflight checks for migration steps.

Each `check_*_done` function queries LIVE chain state (not ape's active
network — these always read from the production RPC so fork/live execution
both get consistent answers) and returns `(done, message, current_value)`:

- `done=True`   → step is already satisfied; scripts should skip execution.
- `done=False`  → step still needed.

Used to make the migration idempotent — steps already executed on chain
(e.g. Arbitrum approvals sent manually before this tool existed) are
detected and skipped automatically.
"""

from __future__ import annotations

import os
from typing import Any

_ERC20_VIEW_ABI: list[dict[str, Any]] = [
    {"type": "function", "name": "allowance", "stateMutability": "view",
     "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
     "outputs": [{"type": "uint256"}]},
    {"type": "function", "name": "balanceOf", "stateMutability": "view",
     "inputs": [{"name": "account", "type": "address"}],
     "outputs": [{"type": "uint256"}]},
]

_ERC721_VIEW_ABI: list[dict[str, Any]] = [
    {"type": "function", "name": "totalSupply", "stateMutability": "view",
     "inputs": [], "outputs": [{"type": "uint256"}]},
    {"type": "function", "name": "balanceOf", "stateMutability": "view",
     "inputs": [{"name": "owner", "type": "address"}],
     "outputs": [{"type": "uint256"}]},
]


def _rpc_url(chain: str) -> str:
    key = os.environ.get("WEB3_ALCHEMY_API_KEY", "")
    urls = {
        "mainnet": f"https://eth-mainnet.g.alchemy.com/v2/{key}" if key else "https://cloudflare-eth.com",
        "arbitrum": "https://arb1.arbitrum.io/rpc",
        "optimism": "https://mainnet.optimism.io",
    }
    return urls[chain.lower()]


def _contract(address: str, chain: str):
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(_rpc_url(chain), request_kwargs={"timeout": 15}))
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=_ERC20_VIEW_ABI)


def _checksum(addr: str) -> str:
    from web3 import Web3
    return Web3.to_checksum_address(addr)


def check_approve_underlying_done(
    chain: str, underlying: str, multisig: str, spender_myt: str, required: int,
) -> tuple[bool, str, int]:
    """Is underlying.allowance(multisig, myt) >= required?"""
    current = int(_contract(underlying, chain).functions.allowance(
        _checksum(multisig), _checksum(spender_myt)
    ).call())
    done = current >= required
    msg = (
        f"underlying.allowance(multisig, MYT) = {current:,} "
        f"({'>=' if done else '<'} required {required:,})"
    )
    return done, msg, current


def check_myt_balance_done(
    chain: str, myt: str, multisig: str, required: int,
) -> tuple[bool, str, int]:
    """Is myt.balanceOf(multisig) >= required? (Satisfied by any MYT on hand.)"""
    current = int(_contract(myt, chain).functions.balanceOf(_checksum(multisig)).call())
    done = current >= required
    msg = (
        f"MYT.balanceOf(multisig) = {current:,} "
        f"({'>=' if done else '<'} required {required:,})"
    )
    return done, msg, current


def check_approve_myt_done(
    chain: str, myt: str, multisig: str, alchemist: str, required: int,
) -> tuple[bool, str, int]:
    """Is myt.allowance(multisig, alchemist) >= required?"""
    current = int(_contract(myt, chain).functions.allowance(
        _checksum(multisig), _checksum(alchemist)
    ).call())
    done = current >= required
    msg = (
        f"MYT.allowance(multisig, Alchemist) = {current:,} "
        f"({'>=' if done else '<'} required {required:,})"
    )
    return done, msg, current


def check_whitelist_transition_done(
    chain: str, al_token: str, v2_alchemist: str, v3_alchemist: str,
    accessor: str = "whitelisted",
) -> tuple[bool, str, dict[str, bool]]:
    """Has the alToken whitelist been transitioned from V2 → V3 alchemist?

    `done` means: V3 is whitelisted AND V2 is NOT. Partial states (both true or
    both false) return done=False so the caller knows to run set_whitelist.

    Returns (done, message, {v2_whitelisted, v3_whitelisted}).
    """
    from web3 import Web3
    from eth_utils import keccak
    from eth_abi import encode
    w3 = Web3(Web3.HTTPProvider(_rpc_url(chain), request_kwargs={"timeout": 15}))
    sel = keccak(text=f"{accessor}(address)")[:4]
    def is_whitelisted(who: str) -> bool:
        data = sel + encode(["address"], [Web3.to_checksum_address(who)])
        raw = w3.eth.call({"to": Web3.to_checksum_address(al_token), "data": "0x" + data.hex()})
        return bool(int.from_bytes(raw, "big"))
    v2_wl = is_whitelisted(v2_alchemist)
    v3_wl = is_whitelisted(v3_alchemist)
    done = v3_wl and not v2_wl
    msg = f"V2 whitelisted: {v2_wl}, V3 whitelisted: {v3_wl}"
    return done, msg, {"v2_whitelisted": v2_wl, "v3_whitelisted": v3_wl}


def read_deposit_cap(chain: str, alchemist_address: str) -> int:
    """Read the current `depositCap()` value on the alchemist.

    Used to avoid emitting `setDepositCap(...)` calls that would lower the
    already-higher cap — V3 alchemist reverts on downward changes.

    Honors `FORK_RPC_URL` env var: when set (--mode impersonate runs), reads
    the fork's cap, which may differ from live (e.g. after partial Phase 1).
    """
    import os
    from web3 import Web3
    from eth_utils import keccak
    from eth_abi import decode
    rpc_url = os.environ.get("FORK_RPC_URL") or _rpc_url(chain)
    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 15}))
    sel = keccak(text="depositCap()")[:4]
    raw = w3.eth.call({"to": Web3.to_checksum_address(alchemist_address), "data": "0x" + sel.hex()})
    return int(decode(["uint256"], raw)[0])


def check_deposit_done(
    chain: str, nft_address: str, multisig: str, expected_positions: int,
) -> tuple[bool, str, dict[str, int]]:
    """Has the alchemist.deposit step already created all expected NFTs?

    Compares NFT.totalSupply() and NFT.balanceOf(multisig) against the number
    of positions in the CSV. Done when BOTH >= expected.

    Returns (done, message, stats) where stats = {total_supply, multisig_balance}.

    A partial state (totalSupply < expected) means deposit is incomplete.
    An already-distributed state (balanceOf(multisig) < totalSupply) means
    NFTs were already transferred out — the deposit step is still "done"
    but distribute has also run.
    """
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(_rpc_url(chain), request_kwargs={"timeout": 15}))
    c = w3.eth.contract(address=Web3.to_checksum_address(nft_address), abi=_ERC721_VIEW_ABI)
    total_supply = int(c.functions.totalSupply().call())
    multisig_balance = int(c.functions.balanceOf(Web3.to_checksum_address(multisig)).call())
    done = total_supply >= expected_positions
    msg = (
        f"NFT.totalSupply = {total_supply} (expected {expected_positions}); "
        f"multisig holds {multisig_balance}/{total_supply}"
    )
    return done, msg, {"total_supply": total_supply, "multisig_balance": multisig_balance}
