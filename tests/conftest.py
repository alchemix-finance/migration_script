"""Pytest configuration and fixtures for CDP migration tests."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_csv_content() -> str:
    """Return sample CSV content for testing."""
    return """address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0xAAA0000000000000000000000000000000000001,1000.50,5000.00,0.5,2.0
0xBBB0000000000000000000000000000000000002,0,0,1.5,3.0
0xCCC0000000000000000000000000000000000003,3000.00,15000.00,0,0
"""


@pytest.fixture
def sample_addresses() -> list[str]:
    """Return sample Ethereum addresses for testing."""
    return [
        "0xAAA0000000000000000000000000000000000001",
        "0xBBB0000000000000000000000000000000000002",
        "0xCCC0000000000000000000000000000000000003",
    ]
