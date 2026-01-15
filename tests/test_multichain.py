"""Multi-chain integration tests for CDP migration.

This module tests the full multi-chain workflow including:
- Chain selection across all scripts
- Chain-specific configuration loading
- Verification of chain-specific addresses before execution
- Processing of chain-specific CSV files
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.config import (
    CHAINS,
    VALID_CHAINS,
    ChainConfigError,
    get_chain_config,
    get_csv_path,
    get_required_config_fields,
    get_supported_chains,
    is_valid_address,
    validate_chain_config,
    verify_chain_config,
)
from src.types import ChainName
from src.validation import validate_csv_file


class TestValidChains:
    """Tests for valid chain constants and types."""

    def test_valid_chains_constant(self) -> None:
        """Test that VALID_CHAINS contains expected chains."""
        assert VALID_CHAINS == ("mainnet", "optimism", "arbitrum")

    def test_chain_name_enum_matches_valid_chains(self) -> None:
        """Test that ChainName enum values match VALID_CHAINS."""
        enum_values = {chain.value for chain in ChainName}
        assert enum_values == set(VALID_CHAINS)

    def test_chains_dict_keys_match_valid_chains(self) -> None:
        """Test that CHAINS dict keys match VALID_CHAINS."""
        assert set(CHAINS.keys()) == set(VALID_CHAINS)


class TestChainConfigLoading:
    """Tests for chain-specific configuration loading."""

    @pytest.mark.parametrize("chain", VALID_CHAINS)
    def test_get_chain_config_all_chains(self, chain: str) -> None:
        """Test that configuration can be loaded for all valid chains."""
        config = get_chain_config(chain)
        assert "chain_id" in config
        assert "multisig" in config
        assert "cdp_usd" in config
        assert "cdp_eth" in config
        assert "nft_usd" in config
        assert "nft_eth" in config

    def test_mainnet_chain_id(self) -> None:
        """Test mainnet has correct chain ID."""
        config = get_chain_config("mainnet")
        assert config["chain_id"] == 1

    def test_optimism_chain_id(self) -> None:
        """Test optimism has correct chain ID."""
        config = get_chain_config("optimism")
        assert config["chain_id"] == 10

    def test_arbitrum_chain_id(self) -> None:
        """Test arbitrum has correct chain ID."""
        config = get_chain_config("arbitrum")
        assert config["chain_id"] == 42161

    def test_invalid_chain_raises_error(self) -> None:
        """Test that invalid chain raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported chain"):
            get_chain_config("polygon")


class TestAddressValidation:
    """Tests for address validation function."""

    def test_valid_address(self) -> None:
        """Test that valid addresses return True."""
        valid = "0x1234567890123456789012345678901234567890"
        assert is_valid_address(valid) is True

    def test_valid_address_lowercase(self) -> None:
        """Test that lowercase hex addresses are valid."""
        valid = "0xabcdef0123456789abcdef0123456789abcdef01"
        assert is_valid_address(valid) is True

    def test_valid_address_uppercase(self) -> None:
        """Test that uppercase hex addresses are valid."""
        valid = "0xABCDEF0123456789ABCDEF0123456789ABCDEF01"
        assert is_valid_address(valid) is True

    def test_empty_string_invalid(self) -> None:
        """Test that empty string is invalid."""
        assert is_valid_address("") is False

    def test_none_invalid(self) -> None:
        """Test that None is invalid."""
        assert is_valid_address(None) is False

    def test_missing_0x_prefix(self) -> None:
        """Test that address without 0x prefix is invalid."""
        assert is_valid_address("1234567890123456789012345678901234567890") is False

    def test_short_address(self) -> None:
        """Test that short address is invalid."""
        assert is_valid_address("0x123456") is False

    def test_long_address(self) -> None:
        """Test that long address is invalid."""
        assert is_valid_address("0x12345678901234567890123456789012345678901234") is False

    def test_non_hex_characters(self) -> None:
        """Test that address with non-hex characters is invalid."""
        assert is_valid_address("0xGGGG567890123456789012345678901234567890") is False


class TestVerifyChainConfig:
    """Tests for chain configuration verification."""

    def test_verify_raises_for_empty_multisig(self) -> None:
        """Test that missing multisig raises ChainConfigError."""
        # With default empty configs, should raise error
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config("mainnet")
        assert "multisig" in exc_info.value.missing_fields

    def test_verify_raises_for_usd_fields_when_has_usd(self) -> None:
        """Test that missing USD fields raise error when has_usd_positions=True."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config("mainnet", has_usd_positions=True, has_eth_positions=False)
        missing = exc_info.value.missing_fields
        assert "cdp_usd" in missing
        assert "nft_usd" in missing

    def test_verify_raises_for_eth_fields_when_has_eth(self) -> None:
        """Test that missing ETH fields raise error when has_eth_positions=True."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config("mainnet", has_usd_positions=False, has_eth_positions=True)
        missing = exc_info.value.missing_fields
        assert "cdp_eth" in missing
        assert "nft_eth" in missing

    def test_verify_skips_usd_fields_when_no_usd(self) -> None:
        """Test that USD fields are not checked when has_usd_positions=False."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config("mainnet", has_usd_positions=False, has_eth_positions=True)
        missing = exc_info.value.missing_fields
        # Should NOT include USD fields
        assert "cdp_usd" not in missing
        assert "nft_usd" not in missing

    def test_verify_skips_eth_fields_when_no_eth(self) -> None:
        """Test that ETH fields are not checked when has_eth_positions=False."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config("mainnet", has_usd_positions=True, has_eth_positions=False)
        missing = exc_info.value.missing_fields
        # Should NOT include ETH fields
        assert "cdp_eth" not in missing
        assert "nft_eth" not in missing

    def test_verify_require_all_checks_everything(self) -> None:
        """Test that require_all=True checks all address fields."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config(
                "mainnet",
                has_usd_positions=False,
                has_eth_positions=False,
                require_all=True,
            )
        missing = exc_info.value.missing_fields
        assert "cdp_usd" in missing
        assert "cdp_eth" in missing
        assert "nft_usd" in missing
        assert "nft_eth" in missing

    @patch.dict(
        "src.config.CHAINS",
        {
            "mainnet": {
                "chain_id": 1,
                "multisig": "0x1234567890123456789012345678901234567890",
                "cdp_usd": "0x2234567890123456789012345678901234567890",
                "cdp_eth": "0x3234567890123456789012345678901234567890",
                "nft_usd": "0x4234567890123456789012345678901234567890",
                "nft_eth": "0x5234567890123456789012345678901234567890",
                "collateral_usd": "0x6234567890123456789012345678901234567890",
                "collateral_eth": "0x7234567890123456789012345678901234567890",
            }
        },
    )
    def test_verify_passes_with_valid_config(self) -> None:
        """Test that verify passes when all required addresses are set."""
        # Should not raise any exception
        verify_chain_config("mainnet", has_usd_positions=True, has_eth_positions=True)


class TestChainConfigError:
    """Tests for ChainConfigError exception."""

    def test_error_contains_chain(self) -> None:
        """Test that error contains chain name."""
        error = ChainConfigError("mainnet", ["multisig"])
        assert error.chain == "mainnet"

    def test_error_contains_missing_fields(self) -> None:
        """Test that error contains missing fields list."""
        error = ChainConfigError("mainnet", ["multisig", "cdp_usd"])
        assert error.missing_fields == ["multisig", "cdp_usd"]

    def test_error_message_format(self) -> None:
        """Test that error message is properly formatted."""
        error = ChainConfigError("optimism", ["multisig", "cdp_usd"])
        assert "optimism" in str(error)
        assert "multisig" in str(error)
        assert "cdp_usd" in str(error)

    def test_custom_message(self) -> None:
        """Test that custom message overrides default."""
        error = ChainConfigError("mainnet", ["multisig"], message="Custom error")
        assert str(error) == "Custom error"


class TestGetRequiredConfigFields:
    """Tests for get_required_config_fields function."""

    def test_always_includes_multisig(self) -> None:
        """Test that multisig is always required."""
        fields = get_required_config_fields(has_usd_positions=False, has_eth_positions=False)
        assert "multisig" in fields

    def test_includes_usd_fields_when_has_usd(self) -> None:
        """Test that USD fields are included when has_usd_positions=True."""
        fields = get_required_config_fields(has_usd_positions=True, has_eth_positions=False)
        assert "cdp_usd" in fields
        assert "nft_usd" in fields

    def test_includes_eth_fields_when_has_eth(self) -> None:
        """Test that ETH fields are included when has_eth_positions=True."""
        fields = get_required_config_fields(has_usd_positions=False, has_eth_positions=True)
        assert "cdp_eth" in fields
        assert "nft_eth" in fields

    def test_includes_all_when_both(self) -> None:
        """Test that all fields are included when both position types exist."""
        fields = get_required_config_fields(has_usd_positions=True, has_eth_positions=True)
        assert "multisig" in fields
        assert "cdp_usd" in fields
        assert "nft_usd" in fields
        assert "cdp_eth" in fields
        assert "nft_eth" in fields


class TestCSVPathPerChain:
    """Tests for chain-specific CSV path resolution."""

    @pytest.mark.parametrize("chain", VALID_CHAINS)
    def test_csv_path_format(self, chain: str) -> None:
        """Test that CSV path is correctly formatted for each chain."""
        path = get_csv_path(chain)
        assert path.name == f"{chain}.csv"
        assert path.parent.name == "data"

    def test_mainnet_csv_exists(self, project_root: Path) -> None:
        """Test that mainnet.csv exists in data directory."""
        csv_path = project_root / "data" / "mainnet.csv"
        assert csv_path.exists(), f"Expected {csv_path} to exist"

    def test_optimism_csv_exists(self, project_root: Path) -> None:
        """Test that optimism.csv exists in data directory."""
        csv_path = project_root / "data" / "optimism.csv"
        assert csv_path.exists(), f"Expected {csv_path} to exist"

    def test_arbitrum_csv_exists(self, project_root: Path) -> None:
        """Test that arbitrum.csv exists in data directory."""
        csv_path = project_root / "data" / "arbitrum.csv"
        assert csv_path.exists(), f"Expected {csv_path} to exist"


class TestMultiChainCSVValidation:
    """Tests for validating CSV files across all chains."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Return the project root directory."""
        return Path(__file__).parent.parent

    def test_validate_mainnet_csv(self, project_root: Path) -> None:
        """Test that mainnet.csv validates successfully."""
        csv_path = project_root / "data" / "mainnet.csv"
        if csv_path.exists():
            result = validate_csv_file(csv_path, "mainnet")
            assert result.is_valid, f"Validation errors: {result.errors}"
            assert result.total_positions > 0

    def test_validate_optimism_csv(self, project_root: Path) -> None:
        """Test that optimism.csv validates successfully."""
        csv_path = project_root / "data" / "optimism.csv"
        if csv_path.exists():
            result = validate_csv_file(csv_path, "optimism")
            assert result.is_valid, f"Validation errors: {result.errors}"
            assert result.total_positions > 0

    def test_validate_arbitrum_csv(self, project_root: Path) -> None:
        """Test that arbitrum.csv validates successfully."""
        csv_path = project_root / "data" / "arbitrum.csv"
        if csv_path.exists():
            result = validate_csv_file(csv_path, "arbitrum")
            assert result.is_valid, f"Validation errors: {result.errors}"
            assert result.total_positions > 0

    def test_positions_have_correct_chain(self, project_root: Path) -> None:
        """Test that positions from validation have correct chain assigned."""
        for chain in VALID_CHAINS:
            csv_path = project_root / "data" / f"{chain}.csv"
            if csv_path.exists():
                result = validate_csv_file(csv_path, chain)
                for position in result.positions:
                    assert position.chain == chain


class TestMultiChainWorkflow:
    """Integration tests for multi-chain workflow."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Return the project root directory."""
        return Path(__file__).parent.parent

    def test_full_workflow_mainnet(self, project_root: Path) -> None:
        """Test full workflow for mainnet chain."""
        chain = "mainnet"

        # 1. Load chain config
        config = get_chain_config(chain)
        assert config["chain_id"] == 1

        # 2. Get CSV path
        csv_path = get_csv_path(chain)
        assert csv_path.name == "mainnet.csv"

        # 3. Validate CSV (if exists)
        if csv_path.exists():
            result = validate_csv_file(csv_path, chain)
            assert result.is_valid

            # 4. Check what config would be needed
            has_usd = result.usd_token_count > 0
            has_eth = result.eth_token_count > 0
            required = get_required_config_fields(has_usd, has_eth)

            # Multisig is always required
            assert "multisig" in required

    def test_full_workflow_optimism(self, project_root: Path) -> None:
        """Test full workflow for optimism chain."""
        chain = "optimism"

        # 1. Load chain config
        config = get_chain_config(chain)
        assert config["chain_id"] == 10

        # 2. Get CSV path
        csv_path = get_csv_path(chain)
        assert csv_path.name == "optimism.csv"

        # 3. Validate CSV (if exists)
        if csv_path.exists():
            result = validate_csv_file(csv_path, chain)
            assert result.is_valid

    def test_full_workflow_arbitrum(self, project_root: Path) -> None:
        """Test full workflow for arbitrum chain."""
        chain = "arbitrum"

        # 1. Load chain config
        config = get_chain_config(chain)
        assert config["chain_id"] == 42161

        # 2. Get CSV path
        csv_path = get_csv_path(chain)
        assert csv_path.name == "arbitrum.csv"

        # 3. Validate CSV (if exists)
        if csv_path.exists():
            result = validate_csv_file(csv_path, chain)
            assert result.is_valid

    @pytest.mark.parametrize("chain", VALID_CHAINS)
    def test_chain_isolation(self, chain: str, project_root: Path) -> None:
        """Test that each chain's workflow is isolated from others."""
        csv_path = project_root / "data" / f"{chain}.csv"
        if not csv_path.exists():
            pytest.skip(f"CSV not found for {chain}")

        result = validate_csv_file(csv_path, chain)

        # Verify all positions belong to this chain
        for position in result.positions:
            assert position.chain == chain, f"Position chain mismatch: expected {chain}, got {position.chain}"


class TestChainSpecificAddressVerification:
    """Tests for chain-specific address verification before execution."""

    def test_verify_requires_multisig_for_all_chains(self) -> None:
        """Test that multisig is required for all chains."""
        for chain in VALID_CHAINS:
            with pytest.raises(ChainConfigError) as exc_info:
                verify_chain_config(chain, has_usd_positions=False, has_eth_positions=False)
            # Even with no positions, multisig should be required
            assert "multisig" in exc_info.value.missing_fields

    @pytest.mark.parametrize("chain", VALID_CHAINS)
    def test_verify_usd_only_positions(self, chain: str) -> None:
        """Test verification when only USD positions exist."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config(chain, has_usd_positions=True, has_eth_positions=False)

        missing = exc_info.value.missing_fields
        # Should require USD contracts but not ETH
        assert "cdp_usd" in missing
        assert "nft_usd" in missing
        assert "cdp_eth" not in missing
        assert "nft_eth" not in missing

    @pytest.mark.parametrize("chain", VALID_CHAINS)
    def test_verify_eth_only_positions(self, chain: str) -> None:
        """Test verification when only ETH positions exist."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config(chain, has_usd_positions=False, has_eth_positions=True)

        missing = exc_info.value.missing_fields
        # Should require ETH contracts but not USD
        assert "cdp_eth" in missing
        assert "nft_eth" in missing
        assert "cdp_usd" not in missing
        assert "nft_usd" not in missing

    @pytest.mark.parametrize("chain", VALID_CHAINS)
    def test_verify_mixed_positions(self, chain: str) -> None:
        """Test verification when both USD and ETH positions exist."""
        with pytest.raises(ChainConfigError) as exc_info:
            verify_chain_config(chain, has_usd_positions=True, has_eth_positions=True)

        missing = exc_info.value.missing_fields
        # Should require all contracts
        assert "multisig" in missing
        assert "cdp_usd" in missing
        assert "nft_usd" in missing
        assert "cdp_eth" in missing
        assert "nft_eth" in missing
