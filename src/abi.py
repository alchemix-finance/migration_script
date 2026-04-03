"""ABI loading for V3 migration contracts."""

import json
from pathlib import Path
from typing import Any

from src.config import ALCHEMIST_ABI_PATH, ALTOKEN_ABI_PATH, ERC721_ABI_PATH


class ABILoadError(Exception):
    pass


def load_abi(abi_path: Path) -> list[dict[str, Any]]:
    if not abi_path.exists():
        raise ABILoadError(f"ABI file not found: {abi_path}")
    try:
        with open(abi_path) as f:
            abi = json.load(f)
    except json.JSONDecodeError as e:
        raise ABILoadError(f"Invalid JSON in {abi_path}: {e}")
    if not isinstance(abi, list):
        raise ABILoadError(f"ABI must be a list, got {type(abi).__name__}")
    return abi


def load_alchemist_abi() -> list[dict[str, Any]]:
    """Load AlchemistV3 ABI (setDepositCap, deposit, mint, burn)."""
    return load_abi(ALCHEMIST_ABI_PATH)


def load_erc721_abi() -> list[dict[str, Any]]:
    """Load ERC721 ABI (transferFrom)."""
    return load_abi(ERC721_ABI_PATH)


def load_altoken_abi() -> list[dict[str, Any]]:
    """Load alToken ABI (transfer, burn, balanceOf)."""
    return load_abi(ALTOKEN_ABI_PATH)


def get_function_selector(abi: list[dict[str, Any]], function_name: str) -> str:
    from eth_utils import keccak
    for entry in abi:
        if entry.get("type") == "function" and entry.get("name") == function_name:
            types = [inp["type"] for inp in entry.get("inputs", [])]
            sig = f"{function_name}({','.join(types)})"
            return "0x" + keccak(text=sig)[:4].hex()
    raise ValueError(f"Function '{function_name}' not found in ABI")


def validate_abis() -> dict[str, bool]:
    results = {}
    try:
        abi = load_alchemist_abi()
        names = {e.get("name") for e in abi if e.get("type") == "function"}
        results["alchemist_abi"] = all(
            f in names for f in ("setDepositCap", "deposit", "mint", "burn")
        )
    except ABILoadError:
        results["alchemist_abi"] = False

    try:
        abi = load_erc721_abi()
        names = {e.get("name") for e in abi if e.get("type") == "function"}
        results["erc721_abi"] = "transferFrom" in names
    except ABILoadError:
        results["erc721_abi"] = False

    try:
        abi = load_altoken_abi()
        names = {e.get("name") for e in abi if e.get("type") == "function"}
        results["altoken_abi"] = all(f in names for f in ("transfer", "burn"))
    except ABILoadError:
        results["altoken_abi"] = False

    return results
