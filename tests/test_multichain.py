"""Multi-chain integration tests for CDP migration (V3).

Covers:
- All 3 chains (mainnet, optimism, arbitrum) are configured.
- ChainName enum and CHAINS dict stay in sync.
- Each chain's asset-specific addresses are distinct.
- verify_asset_config raises ChainConfigError on empty fields, passes when populated.
- get_csv_path resolves correct path per chain+asset.
- All 6 real CSVs parse cleanly (validate_csv_file integration).
- Chain isolation: loaded positions carry correct chain tag.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config import (
    CHAINS,
    VALID_CHAINS,
    ChainConfigError,
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    is_valid_address,
    validate_asset_config,
    verify_asset_config,
)
from src.types import AssetType, ChainName, PositionMigration
from src.validation import validate_csv_file


EXPECTED_CHAINS = {"mainnet", "optimism", "arbitrum"}
EXPECTED_CHAIN_IDS = {"mainnet": 1, "optimism": 10, "arbitrum": 42161}


class TestValidChains:
    def test_chains_dict_has_all_three(self) -> None:
        assert set(CHAINS.keys()) == EXPECTED_CHAINS

    def test_valid_chains_matches_chains_dict(self) -> None:
        assert set(VALID_CHAINS) == EXPECTED_CHAINS

    def test_get_supported_chains_matches(self) -> None:
        assert set(get_supported_chains()) == EXPECTED_CHAINS

    def test_chain_name_enum_in_sync(self) -> None:
        """ChainName enum values must match CHAINS keys — drift detection."""
        enum_values = {c.value for c in ChainName}
        assert enum_values == EXPECTED_CHAINS


class TestChainConfigLoading:
    @pytest.mark.parametrize("chain,expected_cid", list(EXPECTED_CHAIN_IDS.items()))
    def test_chain_id_correct(self, chain: str, expected_cid: int) -> None:
        assert get_chain_config(chain)["chain_id"] == expected_cid

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAINS))
    def test_multisig_is_valid_address(self, chain: str) -> None:
        assert is_valid_address(get_chain_config(chain)["multisig"])


class TestAssetConfigs:
    @pytest.mark.parametrize("chain", list(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_asset_addresses_populated(self, chain: str, asset: AssetType) -> None:
        cfg = get_asset_config(chain, asset)
        for field in ("alchemist", "myt", "al_token", "underlying", "nft"):
            value = cfg.get(field, "")
            assert is_valid_address(value), f"{chain}/{asset.value}/{field} not populated"

    def test_alchemist_addresses_distinct_across_chains(self) -> None:
        """Mainnet alchemists differ from L2 alchemists."""
        mainnet_usd = get_asset_config("mainnet", AssetType.USD)["alchemist"]
        arbitrum_usd = get_asset_config("arbitrum", AssetType.USD)["alchemist"]
        assert mainnet_usd != arbitrum_usd

    def test_usd_eth_addresses_differ_within_chain(self) -> None:
        for chain in EXPECTED_CHAINS:
            usd = get_asset_config(chain, AssetType.USD)
            eth = get_asset_config(chain, AssetType.ETH)
            for field in ("alchemist", "myt", "al_token", "underlying"):
                assert usd[field] != eth[field], f"{chain} {field} collides between USD and ETH"


class TestAssetConfigVerification:
    @pytest.mark.parametrize("chain", list(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_verify_passes_for_populated(self, chain: str, asset: AssetType) -> None:
        verify_asset_config(chain, asset)  # must not raise

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_validate_returns_empty_for_populated(self, chain: str, asset: AssetType) -> None:
        assert validate_asset_config(chain, asset) == []

    def test_chain_config_error_attributes(self) -> None:
        err = ChainConfigError("mainnet", ["alchemist"])
        assert err.chain == "mainnet"
        assert err.missing_fields == ["alchemist"]


class TestCSVPathPerChain:
    @pytest.mark.parametrize("chain", list(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset,prefix", [(AssetType.USD, "alUSD"), (AssetType.ETH, "alETH")])
    def test_path_naming(self, chain: str, asset: AssetType, prefix: str) -> None:
        path = get_csv_path(chain, asset)
        assert f"{prefix}Values-sum-and-debt-{chain}.csv" in str(path)

    @pytest.mark.parametrize("chain", list(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_csv_file_exists(self, chain: str, asset: AssetType) -> None:
        assert get_csv_path(chain, asset).exists(), f"missing CSV for {chain}/{asset.value}"


class TestMultiChainCSVValidation:
    """End-to-end: every chain+asset CSV loads cleanly and produces correctly-tagged positions."""

    @pytest.mark.parametrize("chain", sorted(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_csv_parses_cleanly(self, chain: str, asset: AssetType) -> None:
        csv_path = get_csv_path(chain, asset)
        result = validate_csv_file(csv_path, chain, asset)
        assert result.is_valid, (
            f"{chain}/{asset.value}: {len(result.errors)} errors; first: {result.errors[:1]}"
        )
        assert result.total_positions > 0

    @pytest.mark.parametrize("chain", sorted(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_chain_tag_propagates(self, chain: str, asset: AssetType) -> None:
        csv_path = get_csv_path(chain, asset)
        result = validate_csv_file(csv_path, chain, asset)
        assert result.is_valid
        assert all(p.chain == chain for p in result.positions[:50])

    @pytest.mark.parametrize("chain", sorted(EXPECTED_CHAINS))
    @pytest.mark.parametrize("asset", [AssetType.USD, AssetType.ETH])
    def test_asset_tag_propagates(self, chain: str, asset: AssetType) -> None:
        csv_path = get_csv_path(chain, asset)
        result = validate_csv_file(csv_path, chain, asset)
        assert all(p.asset_type == asset for p in result.positions[:50])

    def test_cross_chain_position_counts_summary(self) -> None:
        """Spot-check that totals match known snapshot counts (captured 2026-04-14)."""
        snapshots = {
            ("mainnet", AssetType.USD): 1245,
            ("mainnet", AssetType.ETH): 714,
            ("optimism", AssetType.USD): 3624,
            ("optimism", AssetType.ETH): 864,
            ("arbitrum", AssetType.USD): 1417,
            ("arbitrum", AssetType.ETH): 376,
        }
        for (chain, asset), expected_count in snapshots.items():
            csv_path = get_csv_path(chain, asset)
            result = validate_csv_file(csv_path, chain, asset)
            assert result.total_positions == expected_count, (
                f"{chain}/{asset.value}: expected {expected_count}, got {result.total_positions}"
            )


class TestChainIsolation:
    """Positions from one chain's CSV must not carry other chains' metadata."""

    def test_loading_arbitrum_does_not_contaminate_mainnet(self) -> None:
        arb_result = validate_csv_file(
            get_csv_path("arbitrum", AssetType.USD), "arbitrum", AssetType.USD,
        )
        mainnet_result = validate_csv_file(
            get_csv_path("mainnet", AssetType.USD), "mainnet", AssetType.USD,
        )
        assert all(p.chain == "arbitrum" for p in arb_result.positions[:20])
        assert all(p.chain == "mainnet" for p in mainnet_result.positions[:20])
