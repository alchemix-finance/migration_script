"""ABI loading utility for CDP migration contracts."""

import json
from pathlib import Path
from typing import Any

from src.config import CDP_ABI_PATH, CONTRACTS_DIR, ERC721_ABI_PATH


class ABILoadError(Exception):
    """Raised when ABI file cannot be loaded."""

    pass


def load_abi(abi_path: Path) -> list[dict[str, Any]]:
    """Load ABI from a JSON file.

    Args:
        abi_path: Path to the ABI JSON file

    Returns:
        Parsed ABI as a list of dictionaries

    Raises:
        ABILoadError: If the file cannot be loaded or parsed
    """
    if not abi_path.exists():
        raise ABILoadError(f"ABI file not found: {abi_path}")

    try:
        with open(abi_path, "r") as f:
            abi = json.load(f)
    except json.JSONDecodeError as e:
        raise ABILoadError(f"Invalid JSON in ABI file {abi_path}: {e}")
    except IOError as e:
        raise ABILoadError(f"Cannot read ABI file {abi_path}: {e}")

    if not isinstance(abi, list):
        raise ABILoadError(f"ABI must be a list, got {type(abi).__name__}")

    return abi


def load_cdp_abi() -> list[dict[str, Any]]:
    """Load the CDP contract ABI.

    The CDP ABI contains:
    - deposit(uint256 amount, address recipient, uint256 tokenId)
    - mint(uint256 tokenId, uint256 amount, address recipient)

    Returns:
        CDP contract ABI
    """
    return load_abi(CDP_ABI_PATH)


def load_erc721_abi() -> list[dict[str, Any]]:
    """Load the ERC721 NFT contract ABI.

    The ERC721 ABI contains:
    - transferFrom(address from, address to, uint256 tokenId)
    - safeTransferFrom(address from, address to, uint256 tokenId)
    - ownerOf(uint256 tokenId)

    Returns:
        ERC721 contract ABI
    """
    return load_abi(ERC721_ABI_PATH)


def get_function_selector(abi: list[dict[str, Any]], function_name: str) -> str:
    """Get the function selector (4-byte signature) for a function.

    Args:
        abi: Contract ABI
        function_name: Name of the function

    Returns:
        Function selector as hex string (e.g., "0x12345678")

    Raises:
        ValueError: If function not found in ABI
    """
    from eth_abi import encode
    from eth_utils import keccak

    for entry in abi:
        if entry.get("type") == "function" and entry.get("name") == function_name:
            inputs = entry.get("inputs", [])
            types = [inp["type"] for inp in inputs]
            signature = f"{function_name}({','.join(types)})"
            selector = keccak(text=signature)[:4]
            return "0x" + selector.hex()

    raise ValueError(f"Function '{function_name}' not found in ABI")


def validate_abis() -> dict[str, bool]:
    """Validate that all required ABI files exist and are valid.

    Returns:
        Dictionary mapping ABI name to validation status
    """
    results = {}

    # Check CDP ABI
    try:
        cdp_abi = load_cdp_abi()
        # Verify required functions exist
        function_names = {entry.get("name") for entry in cdp_abi if entry.get("type") == "function"}
        results["cdp_abi"] = "deposit" in function_names and "mint" in function_names
    except ABILoadError:
        results["cdp_abi"] = False

    # Check ERC721 ABI
    try:
        erc721_abi = load_erc721_abi()
        function_names = {entry.get("name") for entry in erc721_abi if entry.get("type") == "function"}
        results["erc721_abi"] = "transferFrom" in function_names
    except ABILoadError:
        results["erc721_abi"] = False

    return results


def list_available_abis() -> list[str]:
    """List all available ABI files in the contracts directory.

    Returns:
        List of ABI file names
    """
    if not CONTRACTS_DIR.exists():
        return []

    return [f.name for f in CONTRACTS_DIR.glob("*.json")]
