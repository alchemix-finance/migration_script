"""Pytest configuration and shared fixtures for CDP migration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.types import AssetType, PositionMigration, TransactionBatch, TransactionCall


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


# --- CSV fixtures ----------------------------------------------------------

# V3 CSV schema: address,underlyingValue,debt (one CSV per chain+asset, not
# combined). Values are already at MYT-decimal scale (18d for all current V3
# MYT vaults). Positive debt = debt user; negative debt = credit user.
V3_SAMPLE_CSV = """address,underlyingValue,debt
0xAAA0000000000000000000000000000000000001,5000.0,1000.5
0xBBB0000000000000000000000000000000000002,3000.0,-25.0
0xCCC0000000000000000000000000000000000003,15000.0,0
"""


@pytest.fixture
def sample_csv_content() -> str:
    """V3-format CSV content covering a debt user, credit user, and zero-debt user."""
    return V3_SAMPLE_CSV


@pytest.fixture
def tmp_csv(tmp_path: Path, sample_csv_content: str) -> Path:
    """Write sample_csv_content to a tmp file and return its path."""
    p = tmp_path / "sample.csv"
    p.write_text(sample_csv_content)
    return p


def _write_csv(tmp_path: Path, content: str, name: str = "sample.csv") -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


@pytest.fixture
def write_csv(tmp_path: Path):
    """Factory fixture: write arbitrary CSV content to a tmp file and return the path."""

    def _factory(content: str, name: str = "sample.csv") -> Path:
        return _write_csv(tmp_path, content, name)

    return _factory


@pytest.fixture
def sample_addresses() -> list[str]:
    """Sample Ethereum addresses used across validation/config tests."""
    return [
        "0xAAA0000000000000000000000000000000000001",
        "0xBBB0000000000000000000000000000000000002",
        "0xCCC0000000000000000000000000000000000003",
    ]


# --- PositionMigration factory --------------------------------------------

DEBT_USER = "0x1111111111111111111111111111111111111111"
CREDIT_USER = "0x2222222222222222222222222222222222222222"


def _make_position(
    *,
    user_address: str = DEBT_USER,
    asset_type: AssetType = AssetType.USD,
    chain: str = "mainnet",
    deposit_amount_wei: int = 100 * 10**18,
    mint_amount_wei: int = 50 * 10**18,
    credit_amount_wei: int = 0,
    token_id: int = 0,
) -> PositionMigration:
    return PositionMigration(
        user_address=user_address,
        asset_type=asset_type,
        chain=chain,
        deposit_amount_wei=deposit_amount_wei,
        mint_amount_wei=mint_amount_wei,
        credit_amount_wei=credit_amount_wei,
        token_id=token_id,
    )


@pytest.fixture
def make_position():
    """Factory: build a PositionMigration with sensible defaults, overridable per-test."""
    return _make_position


@pytest.fixture
def debt_position() -> PositionMigration:
    """Typical debt user: positive deposit, positive mint, zero credit."""
    return _make_position(user_address=DEBT_USER, mint_amount_wei=50 * 10**18, credit_amount_wei=0)


@pytest.fixture
def credit_position() -> PositionMigration:
    """Typical credit user: positive deposit, zero mint, positive credit."""
    return _make_position(
        user_address=CREDIT_USER, mint_amount_wei=0, credit_amount_wei=30 * 10**18,
    )


@pytest.fixture
def zero_debt_position() -> PositionMigration:
    """Zero-debt user (has collateral but no debt or credit)."""
    return _make_position(
        user_address="0x3333333333333333333333333333333333333333",
        mint_amount_wei=0,
        credit_amount_wei=0,
    )


# --- Batch / call factories -----------------------------------------------

def _make_call(
    *,
    to: str = "0x4444444444444444444444444444444444444444",
    data: bytes = b"\x00" * 36,
    value: int = 0,
    gas_estimate: int = 50_000,
    description: str = "test",
) -> TransactionCall:
    return TransactionCall(
        to=to, data=data, value=value, gas_estimate=gas_estimate, description=description,
    )


@pytest.fixture
def make_call():
    """Factory: build a synthetic TransactionCall."""
    return _make_call


@pytest.fixture
def make_batch(make_call):
    """Factory: build a TransactionBatch containing N synthetic calls."""

    def _factory(n_calls: int = 1, batch_type: str = "deposit", batch_number: int = 1,
                 per_call_gas: int = 50_000, per_call_data_len: int = 36) -> TransactionBatch:
        b = TransactionBatch(batch_number=batch_number, batch_type=batch_type)
        for i in range(n_calls):
            b.add_call(_make_call(
                data=b"\x01" * per_call_data_len,
                gas_estimate=per_call_gas,
                description=f"call {i}",
            ))
        return b

    return _factory
