"""Pre-deposit phase status checker.

Walks the pre-deposit checklist (Prereq-1, Phase D, Phases A/B/C) for every
chain/asset combo and reports two layers of status per row:

    QUEUED   — proposed in Safe Transaction Service but not yet executed
    EXECUTED — on-chain effect (admin / whitelist / allowance / balance) is in place

Usage:
    python scripts/check_pre_deposit_status.py
    python scripts/check_pre_deposit_status.py --chain mainnet
    python scripts/check_pre_deposit_status.py --chain arbitrum --asset eth

Reads RPC URLs from MAINNET_RPC_URL / OPTIMISM_RPC_URL / ARBITRUM_RPC_URL,
falling back to https://{eth,opt,arb}-mainnet.g.alchemy.com/v2/$WEB3_ALCHEMY_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import CHAINS  # noqa: E402
from src.myt_config import (  # noqa: E402
    AL_TOKEN_OWNER,
    MYT_CONFIG,
    V2_ALCHEMIST,
    WHITELIST_ACCESSOR,
)

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
RESET = "\033[0m"

OK = f"{GREEN}OK{RESET}"
PEND = f"{YELLOW}PEND{RESET}"
MISS = f"{RED}MISS{RESET}"
NA = f"{DIM}n/a{RESET}"

# Safe Transaction Service base URLs
SAFE_TX_SERVICE = {
    "mainnet": "https://safe-transaction-mainnet.safe.global",
    "optimism": "https://safe-transaction-optimism.safe.global",
    "arbitrum": "https://safe-transaction-arbitrum.safe.global",
}

# acceptAdmin() selector
ACCEPT_ADMIN_SELECTOR = "0xe9c714f2"
# setWhitelist(address,bool) selector
SET_WHITELIST_SELECTOR = "0x53d6fd59"

# Pre-deposit totals (per SIGNING_GUIDE_PRE_DEPOSIT.md "Amount sanity check").
# Stored in raw on-chain units to compare against allowance/balanceOf.
TOTALS_RAW: dict[tuple[str, str], int] = {
    ("mainnet", "alUSD"): 4_520_719 * 10**6,           # USDC 6d
    ("mainnet", "alETH"): 11_323_490_000_000_000_000_000,  # 11,323.49e18
    ("optimism", "alUSD"): 280_099 * 10**6,
    ("optimism", "alETH"): 854_210_000_000_000_000_000,
    ("arbitrum", "alETH"): 118_330_000_000_000_000_000,
}
MYT_TOTAL_RAW: dict[tuple[str, str], int] = {
    ("mainnet", "alUSD"): 4_520_719 * 10**18,          # MYT shares always 18d
    ("mainnet", "alETH"): 11_323_490_000_000_000_000_000,
    ("optimism", "alUSD"): 280_099 * 10**18,
    ("optimism", "alETH"): 854_210_000_000_000_000_000,
    ("arbitrum", "alETH"): 118_330_000_000_000_000_000,
}


def rpc_url(chain: str) -> str | None:
    explicit = os.getenv(f"{chain.upper()}_RPC_URL")
    if explicit:
        return explicit
    api_key = os.getenv("WEB3_ALCHEMY_API_KEY") or os.getenv("ALCHEMY_API_KEY")
    if not api_key:
        return None
    sub = {"mainnet": "eth", "optimism": "opt", "arbitrum": "arb"}[chain]
    return f"https://{sub}-mainnet.g.alchemy.com/v2/{api_key}"


def http_get(url: str, timeout: int = 15) -> Any:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def rpc_call(url: str, to: str, data: str) -> str:
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"],
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode())
    if "error" in resp:
        raise RuntimeError(resp["error"])
    return resp["result"]


def addr_pad(addr: str) -> str:
    return "0x" + addr.lower().replace("0x", "").rjust(64, "0")


def parse_addr(hex_word: str) -> str:
    return "0x" + hex_word.lower().replace("0x", "").rjust(64, "0")[-40:]


def parse_uint(hex_word: str) -> int:
    return int(hex_word, 16) if hex_word and hex_word != "0x" else 0


def parse_bool(hex_word: str) -> bool:
    return parse_uint(hex_word) != 0


def keccak_selector(sig: str) -> str:
    """Compute the 4-byte selector for a function signature using web3.keccak."""
    try:
        from eth_utils import keccak
    except ImportError:  # pragma: no cover
        from Crypto.Hash import keccak as _k  # type: ignore[import-untyped]
        h = _k.new(digest_bits=256)
        h.update(sig.encode())
        return "0x" + h.hexdigest()[:8]
    return "0x" + keccak(text=sig).hex()[:8]


# Pre-compute selectors we need
SEL_ADMIN = keccak_selector("admin()")
SEL_ALLOWANCE = keccak_selector("allowance(address,address)")
SEL_BALANCE_OF = keccak_selector("balanceOf(address)")


@dataclass
class CheckRow:
    label: str
    safe: str
    chain: str
    queued: str          # OK / PEND / MISS / NA
    executed: str        # OK / PEND / MISS / NA
    detail: str = ""


# --------------------------- Safe Transaction Service ---------------------------

_safe_queue_cache: dict[str, list[dict]] = {}


def fetch_safe_queue(chain: str, safe: str) -> list[dict]:
    key = f"{chain}:{safe.lower()}"
    if key in _safe_queue_cache:
        return _safe_queue_cache[key]
    base = SAFE_TX_SERVICE[chain]
    url = f"{base}/api/v1/safes/{safe}/multisig-transactions/?trusted=true&limit=100"
    try:
        data = http_get(url)
        results = data.get("results", [])
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError):
        results = []
    _safe_queue_cache[key] = results
    return results


def find_proposed(
    chain: str, safe: str, predicate
) -> tuple[bool, bool]:
    """Return (queued, executed) booleans for any tx matching predicate."""
    queue = fetch_safe_queue(chain, safe)
    queued = False
    executed = False
    for tx in queue:
        try:
            if predicate(tx):
                if tx.get("isExecuted"):
                    executed = True
                else:
                    queued = True
        except Exception:
            continue
    return queued, executed


def safe_pred_acceptadmin(tx: dict) -> bool:
    # Could be a single-call acceptAdmin or a multisend batch containing both.
    data = (tx.get("data") or "").lower()
    if not data:
        return False
    return ACCEPT_ADMIN_SELECTOR in data


def safe_pred_setwhitelist_for_token(token: str):
    token_lc = token.lower()
    def _p(tx: dict) -> bool:
        data = (tx.get("data") or "").lower()
        if not data or SET_WHITELIST_SELECTOR.lower() not in data:
            return False
        # Check the inner `to` matches the alToken — for multisend, the alToken
        # address appears as a 20-byte chunk in the call data.
        return token_lc.replace("0x", "") in data
    return _p


def safe_pred_to_data(to: str, selector: str | None = None):
    to_lc = to.lower()
    def _p(tx: dict) -> bool:
        if (tx.get("to") or "").lower() != to_lc:
            return False
        if selector and not (tx.get("data") or "").lower().startswith(selector.lower()):
            return False
        return True
    return _p


def safe_pred_inner_call(target: str, selector: str):
    """Match either a direct call or a multisend that contains the target+selector."""
    target_lc = target.lower().replace("0x", "")
    sel_lc = selector.lower().replace("0x", "")
    def _p(tx: dict) -> bool:
        data = (tx.get("data") or "").lower()
        if not data:
            return False
        # Direct
        if (tx.get("to") or "").lower() == "0x" + target_lc and data.startswith("0x" + sel_lc):
            return True
        # Multisend payload contains the target as a 20-byte chunk + the selector
        return target_lc in data and sel_lc in data
    return _p


# --------------------------------- on-chain probes ---------------------------------

def check_admin(rpc: str, alchemist: str, expected: str) -> bool:
    raw = rpc_call(rpc, alchemist, SEL_ADMIN)
    return parse_addr(raw).lower() == expected.lower()


def check_whitelist(rpc: str, al_token: str, target: str, accessor_sig: str) -> bool:
    sel = keccak_selector(f"{accessor_sig}(address)")
    raw = rpc_call(rpc, al_token, sel + addr_pad(target)[2:])
    return parse_bool(raw)


def check_allowance(rpc: str, token: str, owner: str, spender: str, min_amount: int) -> tuple[bool, int]:
    data = SEL_ALLOWANCE + addr_pad(owner)[2:] + addr_pad(spender)[2:]
    raw = rpc_call(rpc, token, data)
    val = parse_uint(raw)
    return val >= min_amount, val


def check_balance(rpc: str, token: str, holder: str, min_amount: int) -> tuple[bool, int]:
    data = SEL_BALANCE_OF + addr_pad(holder)[2:]
    raw = rpc_call(rpc, token, data)
    val = parse_uint(raw)
    return val >= min_amount, val


# --------------------------------- driver ---------------------------------

def build_rows(chain: str, only_asset: str | None) -> list[CheckRow]:
    rows: list[CheckRow] = []
    cfg = CHAINS[chain]
    multisig = cfg["multisig"]
    rpc = rpc_url(chain)
    if not rpc:
        rows.append(CheckRow(
            label=f"[{chain}] RPC not configured", safe="-", chain=chain,
            queued=NA, executed=NA, detail="set MAINNET_RPC_URL etc. or WEB3_ALCHEMY_API_KEY",
        ))
        return rows

    # Prereq-1 (mainnet only)
    if chain == "mainnet":
        admin_ok = True
        for asset in ("alUSD", "alETH"):
            alch = MYT_CONFIG["mainnet"][asset]["alchemist"]  # type: ignore[index]
            try:
                ok = check_admin(rpc, alch, multisig)
            except Exception as e:
                ok = False
                detail = f"rpc err: {e}"
            else:
                detail = ""
            admin_ok = admin_ok and ok
        q, e = find_proposed(chain, multisig, safe_pred_acceptadmin)
        rows.append(CheckRow(
            label="Prereq-1 acceptAdmin (alUSD+alETH)", safe=multisig, chain=chain,
            queued=OK if q or e else MISS, executed=OK if admin_ok else MISS,
            detail="both admins == migration multisig" if admin_ok else "admin still EOA on at least one alchemist",
        ))

    # Phase D — setWhitelist per asset
    assets_for_chain: list[str]
    if only_asset:
        assets_for_chain = [only_asset]
    else:
        assets_for_chain = ["alUSD", "alETH"]
    # Arbitrum alUSD already done — informational only
    for asset in assets_for_chain:
        if chain == "arbitrum" and asset == "alUSD":
            rows.append(CheckRow(
                label=f"Phase D ({asset})", safe="-", chain=chain,
                queued=NA, executed=NA, detail="already complete on-chain (skip)",
            ))
            continue
        al_token = MYT_CONFIG[chain][asset]["al_token"] if "al_token" in MYT_CONFIG[chain][asset] else CHAINS[chain]["usd" if asset == "alUSD" else "eth"]["al_token"]  # type: ignore[index]
        v3_alch = MYT_CONFIG[chain][asset]["alchemist"]  # type: ignore[index]
        v2_alch = V2_ALCHEMIST[chain][asset]
        accessor = WHITELIST_ACCESSOR[chain]
        ops_safe = AL_TOKEN_OWNER[chain]
        try:
            v2_state = check_whitelist(rpc, str(al_token), v2_alch, accessor)
            v3_state = check_whitelist(rpc, str(al_token), str(v3_alch), accessor)
            executed_ok = (not v2_state) and v3_state
            detail = f"V2={v2_state} V3={v3_state}"
        except Exception as ex:
            executed_ok = False
            detail = f"rpc err: {ex}"
        q, e = find_proposed(chain, ops_safe, safe_pred_setwhitelist_for_token(str(al_token)))
        rows.append(CheckRow(
            label=f"Phase D setWhitelist ({asset})", safe=ops_safe, chain=chain,
            queued=OK if q or e else MISS, executed=OK if executed_ok else MISS,
            detail=detail,
        ))

    # Phase A/B/C per asset
    for asset in assets_for_chain:
        if chain == "arbitrum" and asset == "alUSD":
            rows.append(CheckRow(
                label=f"Phase A/B/C ({asset})", safe="-", chain=chain,
                queued=NA, executed=NA, detail="alUSD live-done; skip",
            ))
            continue
        ac = MYT_CONFIG[chain][asset]
        underlying = str(ac["underlying"])
        myt = str(ac["myt"])
        alchemist = str(ac["alchemist"])
        u_total = TOTALS_RAW.get((chain, asset))
        m_total = MYT_TOTAL_RAW.get((chain, asset))
        if u_total is None or m_total is None:
            continue

        # Phase A — underlying allowance migration multisig → MYT
        try:
            ok_a, val_a = check_allowance(rpc, underlying, multisig, myt, u_total)
            detail_a = f"allowance={val_a} (need ≥ {u_total})"
        except Exception as ex:
            ok_a = False
            detail_a = f"rpc err: {ex}"
        q, e = find_proposed(chain, multisig, safe_pred_inner_call(underlying, "0x095ea7b3"))  # approve
        rows.append(CheckRow(
            label=f"Phase A approve_u ({asset})", safe=multisig, chain=chain,
            queued=OK if q or e else MISS, executed=OK if ok_a else MISS, detail=detail_a,
        ))

        # Phase B — MYT.balanceOf(multisig) ≥ total
        try:
            ok_b, val_b = check_balance(rpc, myt, multisig, m_total)
            detail_b = f"balance={val_b} (need ≥ {m_total})"
        except Exception as ex:
            ok_b = False
            detail_b = f"rpc err: {ex}"
        # ERC4626.deposit(uint256,address) selector
        deposit_sel = keccak_selector("deposit(uint256,address)")
        q, e = find_proposed(chain, multisig, safe_pred_inner_call(myt, deposit_sel))
        rows.append(CheckRow(
            label=f"Phase B deposit_myt ({asset})", safe=multisig, chain=chain,
            queued=OK if q or e else MISS, executed=OK if ok_b else MISS, detail=detail_b,
        ))

        # Phase C — MYT allowance migration multisig → alchemist
        try:
            ok_c, val_c = check_allowance(rpc, myt, multisig, alchemist, m_total)
            detail_c = f"allowance={val_c} (need ≥ {m_total})"
        except Exception as ex:
            ok_c = False
            detail_c = f"rpc err: {ex}"
        # Match approve(spender=alchemist) on the MYT contract
        q, e = find_proposed(chain, multisig, safe_pred_inner_call(myt, "0x095ea7b3"))
        rows.append(CheckRow(
            label=f"Phase C approve_myt ({asset})", safe=multisig, chain=chain,
            queued=OK if q or e else MISS, executed=OK if ok_c else MISS, detail=detail_c,
        ))

    return rows


def print_rows(rows: list[CheckRow]) -> None:
    print(f"{'CHAIN':<10} {'PHASE / CHECK':<38} {'QUEUED':<6}  {'EXEC':<6}  DETAIL")
    print("-" * 110)
    for r in rows:
        print(f"{r.chain:<10} {r.label:<38} {r.queued:<6}  {r.executed:<6}  {r.detail}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check pre-deposit phase status")
    parser.add_argument("--chain", choices=list(CHAINS.keys()), help="Limit to one chain")
    parser.add_argument("--asset", choices=["usd", "eth"], help="Limit to one asset (usd|eth)")
    args = parser.parse_args()

    chains = [args.chain] if args.chain else list(CHAINS.keys())
    asset_label = None
    if args.asset:
        asset_label = "alUSD" if args.asset == "usd" else "alETH"

    all_rows: list[CheckRow] = []
    for c in chains:
        all_rows.extend(build_rows(c, asset_label))
    print_rows(all_rows)


if __name__ == "__main__":
    main()
