"""Environment variable loading for migration scripts.

Loads .env file if present, provides typed access to configuration values.
The proposer private key is needed for signing Safe transaction proposals.
RPC endpoints are handled by Apeworx plugins (Alchemy, etc).
"""

import os
from pathlib import Path

# Load .env file on import
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv not installed — rely on shell env vars


def get_proposer_private_key() -> str:
    """Get the proposer's private key from environment.

    Returns:
        Hex-encoded private key (without 0x prefix)

    Raises:
        EnvironmentError: If PROPOSER_PRIVATE_KEY is not set
    """
    key = os.environ.get("PROPOSER_PRIVATE_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "PROPOSER_PRIVATE_KEY not set. "
            "Create .env from .env.example and fill in the proposer key."
        )
    if key.startswith("0x"):
        key = key[2:]
    if len(key) != 64:
        raise EnvironmentError(
            f"PROPOSER_PRIVATE_KEY must be 64 hex chars (got {len(key)}). "
            "Check your .env file."
        )
    return key


def get_proposer_address() -> str:
    """Get the proposer's Ethereum address from environment.

    Returns:
        Checksummed Ethereum address

    Raises:
        EnvironmentError: If PROPOSER_ADDRESS is not set
    """
    addr = os.environ.get("PROPOSER_ADDRESS", "").strip()
    if not addr:
        raise EnvironmentError(
            "PROPOSER_ADDRESS not set. "
            "Create .env from .env.example and fill in the proposer address."
        )
    if not addr.startswith("0x") or len(addr) != 42:
        raise EnvironmentError(
            f"PROPOSER_ADDRESS must be a valid 42-char hex address (got '{addr}')."
        )
    return addr


def get_safe_api_url(chain: str) -> str | None:
    """Get custom Safe Transaction Service URL for a chain, if configured."""
    key = f"SAFE_API_URL_{chain.upper()}"
    return os.environ.get(key, "").strip() or None
