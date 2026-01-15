"""Tests for configuration module."""

import pytest
from src.config import (
    CHAINS,
    get_chain_config,
    get_cdp_contract_address,
    get_nft_contract_address,
    get_supported_chains,
    validate_chain_config,
)


class TestChainConfig:
    """Tests for chain configuration functions."""

    def test_all_chains_configured(self) -> None:
        """Verify all expected chains are in configuration."""
        expected_chains = {"mainnet", "optimism", "arbitrum"}
        assert set(CHAINS.keys()) == expected_chains

    def test_get_chain_config_mainnet(self) -> None:
        """Test getting mainnet configuration."""
        config = get_chain_config("mainnet")
        assert config["chain_id"] == 1
        assert "multisig" in config
        assert "cdp_usd" in config
        assert "cdp_eth" in config

    def test_get_chain_config_optimism(self) -> None:
        """Test getting optimism configuration."""
        config = get_chain_config("optimism")
        assert config["chain_id"] == 10

    def test_get_chain_config_arbitrum(self) -> None:
        """Test getting arbitrum configuration."""
        config = get_chain_config("arbitrum")
        assert config["chain_id"] == 42161

    def test_get_chain_config_case_insensitive(self) -> None:
        """Test that chain names are case insensitive."""
        config_lower = get_chain_config("mainnet")
        config_upper = get_chain_config("MAINNET")
        config_mixed = get_chain_config("Mainnet")
        assert config_lower == config_upper == config_mixed

    def test_get_chain_config_invalid_chain(self) -> None:
        """Test that invalid chain raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported chain"):
            get_chain_config("invalid_chain")

    def test_get_supported_chains(self) -> None:
        """Test getting list of supported chains."""
        chains = get_supported_chains()
        assert "mainnet" in chains
        assert "optimism" in chains
        assert "arbitrum" in chains
        assert len(chains) == 3


class TestContractAddresses:
    """Tests for contract address functions."""

    def test_get_cdp_contract_usd(self) -> None:
        """Test getting CDP contract for USD."""
        address = get_cdp_contract_address("mainnet", "USD")
        assert isinstance(address, str)

    def test_get_cdp_contract_eth(self) -> None:
        """Test getting CDP contract for ETH."""
        address = get_cdp_contract_address("mainnet", "ETH")
        assert isinstance(address, str)

    def test_get_cdp_contract_invalid_asset(self) -> None:
        """Test that invalid asset type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported asset type"):
            get_cdp_contract_address("mainnet", "INVALID")

    def test_get_nft_contract_usd(self) -> None:
        """Test getting NFT contract for USD."""
        address = get_nft_contract_address("mainnet", "USD")
        assert isinstance(address, str)

    def test_get_nft_contract_eth(self) -> None:
        """Test getting NFT contract for ETH."""
        address = get_nft_contract_address("mainnet", "ETH")
        assert isinstance(address, str)


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_validate_chain_config_returns_missing_fields(self) -> None:
        """Test that validation returns list of missing fields."""
        # Since we have placeholder addresses, all fields should be missing
        missing = validate_chain_config("mainnet")
        assert isinstance(missing, list)
        # With empty placeholder addresses, expect all fields to be missing
        expected_missing = [
            "multisig",
            "cdp_usd",
            "cdp_eth",
            "nft_usd",
            "nft_eth",
            "collateral_usd",
            "collateral_eth",
        ]
        assert set(missing) == set(expected_missing)
