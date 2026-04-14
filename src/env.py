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


def get_safe_api_timeout_seconds() -> float:
    """HTTP timeout (seconds) for Safe Transaction Service requests (GET nonce, POST proposal)."""
    raw = os.environ.get("SAFE_API_TIMEOUT", "").strip()
    if not raw:
        return 90.0
    try:
        t = float(raw)
    except ValueError as e:
        raise EnvironmentError(
            f"SAFE_API_TIMEOUT must be a number (got {raw!r})."
        ) from e
    return max(5.0, t)


def get_safe_proposal_start_nonce() -> int | None:
    """Next Safe tx nonce to use when proposing (must match Safe Transaction Service).

    If set, the Safe API is not queried for nonce (useful when SSL or timeouts block the API).
    Use the same value the Safe UI shows for the next transaction.
    """
    raw = os.environ.get("SAFE_PROPOSAL_START_NONCE", "").strip()
    if not raw:
        return None
    try:
        n = int(raw, 10)
    except ValueError as e:
        raise EnvironmentError(
            f"SAFE_PROPOSAL_START_NONCE must be a non-negative integer (got {raw!r})."
        ) from e
    if n < 0:
        raise EnvironmentError("SAFE_PROPOSAL_START_NONCE must be >= 0.")
    return n
