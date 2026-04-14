"""Tests for configuration module (V3).

Original V1 intent was: verify per-chain contract address lookup and
configuration validation. V3 restructured the config so addresses live nested
under `ChainConfig[asset]["alchemist"|"myt"|"al_token"|"underlying"|"nft"]`
(see src/config.py). These tests preserve the original intent against the
current shape.
"""

import pytest

from src.config import (
    CHAINS,
    ChainConfigError,
    get_asset_config,
    get_chain_config,
    get_effective_gas_limit,
    get_effective_size_limit,
    get_supported_chains,
    is_valid_address,
    validate_asset_config,
    verify_asset_config,
)
from src.types import AssetType

EXPECTED_CHAIN_IDS = {"mainnet": 1, "optimism": 10, "arbitrum": 42161}
ASSET_CONFIG_KEYS = {"alchemist", "myt", "al_token", "underlying", "nft", "myt_decimals"}
CHAIN_CONFIG_KEYS = {"chain_id", "multisig", "usd", "eth"}


class TestChainConfig:
    """Verify the shape and contents of the per-chain configuration."""

    def test_all_chains_configured(self) -> None:
        assert set(CHAINS.keys()) == set(EXPECTED_CHAIN_IDS)

    @pytest.mark.parametrize("chain,cid", list(EXPECTED_CHAIN_IDS.items()))
    def test_chain_id_correct(self, chain: str, cid: int) -> None:
        assert get_chain_config(chain)["chain_id"] == cid

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAIN_IDS))
    def test_chain_config_has_required_top_level_keys(self, chain: str) -> None:
        config = get_chain_config(chain)
        assert set(config.keys()) >= CHAIN_CONFIG_KEYS
        assert isinstance(config["multisig"], str)

    def test_get_chain_config_case_insensitive(self) -> None:
        assert get_chain_config("mainnet") == get_chain_config("MAINNET")
        assert get_chain_config("mainnet") == get_chain_config("Mainnet")

    def test_get_chain_config_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported chain"):
            get_chain_config("goerli")

    def test_get_supported_chains(self) -> None:
        chains = get_supported_chains()
        assert set(chains) == set(EXPECTED_CHAIN_IDS)
        assert len(chains) == 3


class TestAssetConfig:
    """Verify per-asset (USD/ETH) subconfig — replaces the V2 cdp_usd/cdp_eth lookups."""

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAIN_IDS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_asset_config_has_required_keys(self, chain: str, asset: AssetType) -> None:
        asset_config = get_asset_config(chain, asset)
        assert set(asset_config.keys()) >= ASSET_CONFIG_KEYS

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAIN_IDS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_asset_addresses_populated(self, chain: str, asset: AssetType) -> None:
        """All V3 deployments have populated addresses — empty strings indicate a config bug."""
        asset_config = get_asset_config(chain, asset)
        for field in ("alchemist", "myt", "al_token", "nft"):
            value = asset_config.get(field, "")
            assert is_valid_address(value), f"{chain}/{asset.value}/{field} not a valid address: {value!r}"

    def test_myt_decimals_is_18(self) -> None:
        for chain in EXPECTED_CHAIN_IDS:
            for asset in (AssetType.USD, AssetType.ETH):
                assert get_asset_config(chain, asset)["myt_decimals"] == 18

    def test_addresses_distinct_per_asset(self) -> None:
        """Within a chain, alUSD and alETH addresses must not collide — they are different contracts."""
        for chain in EXPECTED_CHAIN_IDS:
            usd = get_asset_config(chain, AssetType.USD)
            eth = get_asset_config(chain, AssetType.ETH)
            for field in ("alchemist", "myt", "al_token"):
                assert usd[field] != eth[field], f"{chain} {field} is identical for USD and ETH"


class TestAddressValidation:
    """Tests for is_valid_address — replaces V2 is_valid_eth_address."""

    def test_valid_checksum_address(self) -> None:
        assert is_valid_address("0x1234567890AbcdEF1234567890aBcdef12345678")

    def test_valid_lowercase(self) -> None:
        assert is_valid_address("0x1234567890abcdef1234567890abcdef12345678")

    def test_zero_address(self) -> None:
        assert is_valid_address("0x" + "0" * 40)

    def test_missing_0x_prefix_rejected(self) -> None:
        assert not is_valid_address("1234567890abcdef1234567890abcdef12345678")

    def test_wrong_length_rejected(self) -> None:
        assert not is_valid_address("0x1234")
        assert not is_valid_address("0x" + "a" * 41)

    def test_non_hex_rejected(self) -> None:
        assert not is_valid_address("0xZZZZ567890abcdef1234567890abcdef12345678")

    def test_empty_rejected(self) -> None:
        assert not is_valid_address("")

    def test_none_rejected(self) -> None:
        assert not is_valid_address(None)  # type: ignore[arg-type]


class TestAssetConfigVerification:
    """Tests for verify_asset_config / validate_asset_config — replaces V2 validate_chain_config."""

    def test_verify_asset_config_passes_for_populated(self) -> None:
        """All live V3 deployments have populated addresses; verify raises nothing."""
        for chain in EXPECTED_CHAIN_IDS:
            for asset in (AssetType.USD, AssetType.ETH):
                verify_asset_config(chain, asset)  # must not raise

    def test_validate_asset_config_returns_empty_when_ok(self) -> None:
        for chain in EXPECTED_CHAIN_IDS:
            for asset in (AssetType.USD, AssetType.ETH):
                assert validate_asset_config(chain, asset) == []

    def test_chain_config_error_carries_context(self) -> None:
        """ChainConfigError exposes chain and missing_fields attributes."""
        err = ChainConfigError("mainnet", ["alchemist"])
        assert err.chain == "mainnet"
        assert err.missing_fields == ["alchemist"]
        assert "alchemist" in str(err)


class TestEffectiveLimits:
    """Tests for per-chain gas / size limit helpers."""

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAIN_IDS))
    def test_gas_limit_below_raw(self, chain: str) -> None:
        # Effective gas limit is 90% of the raw chain gas limit.
        from src.config import CHAIN_GAS_LIMITS, GAS_TARGET_PERCENT
        assert get_effective_gas_limit(chain) == int(
            CHAIN_GAS_LIMITS[chain] * GAS_TARGET_PERCENT
        )

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAIN_IDS))
    def test_size_limit_below_raw(self, chain: str) -> None:
        from src.config import CHAIN_TX_SIZE_LIMITS, SIZE_TARGET_PERCENT
        assert get_effective_size_limit(chain) == int(
            CHAIN_TX_SIZE_LIMITS[chain] * SIZE_TARGET_PERCENT
        )

    def test_unknown_chain_falls_back_to_default(self) -> None:
        # Helpers accept unknown chains and fall back rather than raising.
        assert get_effective_gas_limit("never-a-chain") > 0
        assert get_effective_size_limit("never-a-chain") > 0
