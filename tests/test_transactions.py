"""Tests for transaction building module."""

import pytest
from eth_abi import decode
from eth_utils import keccak

from src.abi import load_cdp_abi, load_erc721_abi
from src.config import ChainConfig
from src.transactions import (
    TransactionBuildError,
    build_deposit_tx,
    build_mint_tx,
    build_position_transactions,
    build_transfer_tx,
    encode_function_call,
    validate_transaction_call,
)
from src.types import PositionMigration, TransactionCall


# Test fixtures
@pytest.fixture
def sample_position() -> PositionMigration:
    """Create a sample position for testing."""
    return PositionMigration(
        user_address="0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        asset_type="USD",
        token_id=1,
        deposit_amount=5000 * 10**18,  # 5000 tokens in wei
        mint_amount=1000 * 10**18,  # 1000 debt in wei
        chain="mainnet",
    )


@pytest.fixture
def sample_eth_position() -> PositionMigration:
    """Create a sample ETH position for testing."""
    return PositionMigration(
        user_address="0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        asset_type="ETH",
        token_id=0,
        deposit_amount=2 * 10**18,  # 2 ETH in wei
        mint_amount=int(0.5 * 10**18),  # 0.5 debt in wei
        chain="mainnet",
    )


@pytest.fixture
def sample_chain_config() -> ChainConfig:
    """Create a sample chain configuration for testing."""
    return {
        "chain_id": 1,
        "multisig": "0x1111111111111111111111111111111111111111",
        "cdp_usd": "0x2222222222222222222222222222222222222222",
        "cdp_eth": "0x3333333333333333333333333333333333333333",
        "nft_usd": "0x4444444444444444444444444444444444444444",
        "nft_eth": "0x5555555555555555555555555555555555555555",
        "collateral_usd": "0x6666666666666666666666666666666666666666",
        "collateral_eth": "0x7777777777777777777777777777777777777777",
    }


@pytest.fixture
def cdp_abi() -> list:
    """Load CDP ABI for testing."""
    return load_cdp_abi()


@pytest.fixture
def erc721_abi() -> list:
    """Load ERC721 ABI for testing."""
    return load_erc721_abi()


class TestEncodeFunctionCall:
    """Tests for encode_function_call function."""

    def test_encode_deposit_function(self, cdp_abi: list):
        """Test encoding deposit function call."""
        amount = 5000 * 10**18
        recipient = "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        token_id = 1

        calldata = encode_function_call(
            abi=cdp_abi,
            function_name="deposit",
            args=[amount, recipient, token_id],
        )

        # Verify selector (first 4 bytes)
        expected_selector = keccak(text="deposit(uint256,address,uint256)")[:4]
        assert calldata[:4] == expected_selector

        # Verify calldata length: 4 (selector) + 32*3 (3 params)
        assert len(calldata) == 4 + 32 * 3

        # Decode and verify arguments (addresses are returned checksummed)
        decoded = decode(["uint256", "address", "uint256"], calldata[4:])
        assert decoded[0] == amount
        assert decoded[1].lower() == recipient.lower()
        assert decoded[2] == token_id

    def test_encode_mint_function(self, cdp_abi: list):
        """Test encoding mint function call."""
        token_id = 5
        amount = 1000 * 10**18
        recipient = "0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"

        calldata = encode_function_call(
            abi=cdp_abi,
            function_name="mint",
            args=[token_id, amount, recipient],
        )

        # Verify selector
        expected_selector = keccak(text="mint(uint256,uint256,address)")[:4]
        assert calldata[:4] == expected_selector

        # Decode and verify arguments (addresses are returned checksummed)
        decoded = decode(["uint256", "uint256", "address"], calldata[4:])
        assert decoded[0] == token_id
        assert decoded[1] == amount
        assert decoded[2].lower() == recipient.lower()

    def test_encode_transfer_from_function(self, erc721_abi: list):
        """Test encoding transferFrom function call."""
        from_addr = "0x1111111111111111111111111111111111111111"
        to_addr = "0x2222222222222222222222222222222222222222"
        token_id = 42

        calldata = encode_function_call(
            abi=erc721_abi,
            function_name="transferFrom",
            args=[from_addr, to_addr, token_id],
        )

        # Verify selector
        expected_selector = keccak(text="transferFrom(address,address,uint256)")[:4]
        assert calldata[:4] == expected_selector

        # Decode and verify arguments
        decoded = decode(["address", "address", "uint256"], calldata[4:])
        assert decoded[0] == from_addr
        assert decoded[1] == to_addr
        assert decoded[2] == token_id

    def test_function_not_found_raises_error(self, cdp_abi: list):
        """Test that encoding a non-existent function raises error."""
        with pytest.raises(TransactionBuildError) as exc_info:
            encode_function_call(
                abi=cdp_abi,
                function_name="nonExistentFunction",
                args=[],
            )
        assert "not found in ABI" in str(exc_info.value)

    def test_wrong_argument_count_raises_error(self, cdp_abi: list):
        """Test that wrong argument count raises error."""
        with pytest.raises(TransactionBuildError) as exc_info:
            encode_function_call(
                abi=cdp_abi,
                function_name="deposit",
                args=[100],  # Only 1 arg, needs 3
            )
        assert "expects 3 arguments" in str(exc_info.value)
        assert "got 1" in str(exc_info.value)

    def test_encode_zero_value_arguments(self, cdp_abi: list):
        """Test encoding with zero values."""
        calldata = encode_function_call(
            abi=cdp_abi,
            function_name="deposit",
            args=[0, "0x0000000000000000000000000000000000000000", 0],
        )

        # Should still produce valid calldata
        assert len(calldata) == 4 + 32 * 3

    def test_encode_large_values(self, cdp_abi: list):
        """Test encoding with large uint256 values."""
        large_amount = 2**256 - 1  # Max uint256
        calldata = encode_function_call(
            abi=cdp_abi,
            function_name="deposit",
            args=[large_amount, "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", 0],
        )

        decoded = decode(["uint256", "address", "uint256"], calldata[4:])
        assert decoded[0] == large_amount


class TestBuildDepositTx:
    """Tests for build_deposit_tx function."""

    def test_build_deposit_tx_basic(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test building a basic deposit transaction."""
        tx = build_deposit_tx(sample_position, sample_chain_config)

        # Verify transaction structure
        assert isinstance(tx, TransactionCall)
        assert tx.to == sample_chain_config["cdp_usd"]  # USD position -> cdp_usd
        assert len(tx.data) == 4 + 32 * 3  # selector + 3 params
        assert tx.value == 0
        assert tx.gas_estimate > 0

        # Verify calldata encodes correct values
        decoded = decode(["uint256", "address", "uint256"], tx.data[4:])
        assert decoded[0] == sample_position.deposit_amount
        assert decoded[1] == sample_chain_config["multisig"]
        assert decoded[2] == sample_position.token_id

    def test_build_deposit_tx_eth_position(
        self,
        sample_eth_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test building deposit tx for ETH position uses cdp_eth contract."""
        tx = build_deposit_tx(sample_eth_position, sample_chain_config)

        assert tx.to == sample_chain_config["cdp_eth"]

    def test_build_deposit_tx_has_description(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that deposit tx includes a description."""
        tx = build_deposit_tx(sample_position, sample_chain_config)

        assert "deposit(" in tx.description
        assert str(sample_position.deposit_amount) in tx.description
        assert sample_chain_config["multisig"] in tx.description
        assert str(sample_position.token_id) in tx.description

    def test_build_deposit_tx_no_multisig_raises_error(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that missing multisig raises error."""
        sample_chain_config["multisig"] = ""

        with pytest.raises(TransactionBuildError) as exc_info:
            build_deposit_tx(sample_position, sample_chain_config)
        assert "multisig" in str(exc_info.value).lower()


class TestBuildMintTx:
    """Tests for build_mint_tx function."""

    def test_build_mint_tx_basic(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test building a basic mint transaction."""
        tx = build_mint_tx(sample_position, sample_chain_config)

        # Verify transaction structure
        assert isinstance(tx, TransactionCall)
        assert tx.to == sample_chain_config["cdp_usd"]
        assert len(tx.data) == 4 + 32 * 3
        assert tx.value == 0
        assert tx.gas_estimate > 0

        # Verify calldata encodes correct values (addresses returned checksummed)
        decoded = decode(["uint256", "uint256", "address"], tx.data[4:])
        assert decoded[0] == sample_position.token_id
        assert decoded[1] == sample_position.mint_amount
        assert decoded[2].lower() == sample_position.user_address.lower()

    def test_build_mint_tx_recipient_is_user(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that mint recipient is the user, not the multisig."""
        tx = build_mint_tx(sample_position, sample_chain_config)

        decoded = decode(["uint256", "uint256", "address"], tx.data[4:])
        # The recipient should be the user address (compare case-insensitive)
        assert decoded[2].lower() == sample_position.user_address.lower()
        # Not the multisig
        assert decoded[2].lower() != sample_chain_config["multisig"].lower()

    def test_build_mint_tx_eth_position(
        self,
        sample_eth_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test building mint tx for ETH position uses cdp_eth contract."""
        tx = build_mint_tx(sample_eth_position, sample_chain_config)

        assert tx.to == sample_chain_config["cdp_eth"]

    def test_build_mint_tx_has_description(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that mint tx includes a description."""
        tx = build_mint_tx(sample_position, sample_chain_config)

        assert "mint(" in tx.description
        assert str(sample_position.token_id) in tx.description
        assert str(sample_position.mint_amount) in tx.description


class TestBuildTransferTx:
    """Tests for build_transfer_tx function."""

    def test_build_transfer_tx_basic(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test building a basic transfer transaction."""
        tx = build_transfer_tx(sample_position, sample_chain_config)

        # Verify transaction structure
        assert isinstance(tx, TransactionCall)
        assert tx.to == sample_chain_config["nft_usd"]
        assert len(tx.data) == 4 + 32 * 3
        assert tx.value == 0
        assert tx.gas_estimate > 0

        # Verify calldata encodes correct values (addresses returned checksummed)
        decoded = decode(["address", "address", "uint256"], tx.data[4:])
        assert decoded[0].lower() == sample_chain_config["multisig"].lower()  # from
        assert decoded[1].lower() == sample_position.user_address.lower()  # to
        assert decoded[2] == sample_position.token_id

    def test_build_transfer_tx_from_multisig_to_user(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that transfer is from multisig to user."""
        tx = build_transfer_tx(sample_position, sample_chain_config)

        decoded = decode(["address", "address", "uint256"], tx.data[4:])
        assert decoded[0].lower() == sample_chain_config["multisig"].lower()
        assert decoded[1].lower() == sample_position.user_address.lower()

    def test_build_transfer_tx_eth_position(
        self,
        sample_eth_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test building transfer tx for ETH position uses nft_eth contract."""
        tx = build_transfer_tx(sample_eth_position, sample_chain_config)

        assert tx.to == sample_chain_config["nft_eth"]

    def test_build_transfer_tx_has_description(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that transfer tx includes a description."""
        tx = build_transfer_tx(sample_position, sample_chain_config)

        assert "transferFrom(" in tx.description
        assert sample_chain_config["multisig"] in tx.description
        assert sample_position.user_address in tx.description
        assert str(sample_position.token_id) in tx.description

    def test_build_transfer_tx_no_multisig_raises_error(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that missing multisig raises error."""
        sample_chain_config["multisig"] = ""

        with pytest.raises(TransactionBuildError) as exc_info:
            build_transfer_tx(sample_position, sample_chain_config)
        assert "multisig" in str(exc_info.value).lower()


class TestBuildPositionTransactions:
    """Tests for build_position_transactions function."""

    def test_build_all_three_transactions(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test building all three transactions for a position."""
        deposit_tx, mint_tx, transfer_tx = build_position_transactions(
            sample_position, sample_chain_config
        )

        # Verify we got all three transactions
        assert isinstance(deposit_tx, TransactionCall)
        assert isinstance(mint_tx, TransactionCall)
        assert isinstance(transfer_tx, TransactionCall)

        # Verify they target different contracts for USD
        assert deposit_tx.to == sample_chain_config["cdp_usd"]
        assert mint_tx.to == sample_chain_config["cdp_usd"]
        assert transfer_tx.to == sample_chain_config["nft_usd"]

        # Verify all have calldata
        assert len(deposit_tx.data) > 4
        assert len(mint_tx.data) > 4
        assert len(transfer_tx.data) > 4

    def test_build_position_transactions_uses_same_token_id(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that all three transactions use the same token ID."""
        deposit_tx, mint_tx, transfer_tx = build_position_transactions(
            sample_position, sample_chain_config
        )

        # Decode token IDs from each transaction
        deposit_decoded = decode(["uint256", "address", "uint256"], deposit_tx.data[4:])
        mint_decoded = decode(["uint256", "uint256", "address"], mint_tx.data[4:])
        transfer_decoded = decode(["address", "address", "uint256"], transfer_tx.data[4:])

        # Token ID should be consistent
        assert deposit_decoded[2] == sample_position.token_id  # Last param of deposit
        assert mint_decoded[0] == sample_position.token_id  # First param of mint
        assert transfer_decoded[2] == sample_position.token_id  # Last param of transfer


class TestValidateTransactionCall:
    """Tests for validate_transaction_call function."""

    def test_validate_valid_transaction(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that a valid transaction passes validation."""
        tx = build_deposit_tx(sample_position, sample_chain_config)
        errors = validate_transaction_call(tx)

        assert errors == []

    def test_validate_empty_to_address(self):
        """Test that empty 'to' address is detected."""
        tx = TransactionCall(
            to="",
            data=b"\x00\x01\x02\x03",
            value=0,
            gas_estimate=100000,
        )
        errors = validate_transaction_call(tx)

        assert any("'to' address is empty" in e for e in errors)

    def test_validate_invalid_to_address_format(self):
        """Test that invalid address format is detected."""
        tx = TransactionCall(
            to="not_an_address",
            data=b"\x00\x01\x02\x03",
            value=0,
            gas_estimate=100000,
        )
        errors = validate_transaction_call(tx)

        assert any("Invalid 'to' address format" in e for e in errors)

    def test_validate_wrong_address_length(self):
        """Test that wrong address length is detected."""
        tx = TransactionCall(
            to="0x1234",  # Too short
            data=b"\x00\x01\x02\x03",
            value=0,
            gas_estimate=100000,
        )
        errors = validate_transaction_call(tx)

        assert any("Invalid 'to' address length" in e for e in errors)

    def test_validate_empty_calldata(self):
        """Test that empty calldata is detected."""
        tx = TransactionCall(
            to="0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            data=b"",
            value=0,
            gas_estimate=100000,
        )
        errors = validate_transaction_call(tx)

        assert any("calldata is empty" in e for e in errors)

    def test_validate_calldata_too_short(self):
        """Test that calldata shorter than 4 bytes is detected."""
        tx = TransactionCall(
            to="0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            data=b"\x00\x01\x02",  # Only 3 bytes
            value=0,
            gas_estimate=100000,
        )
        errors = validate_transaction_call(tx)

        assert any("Calldata too short" in e for e in errors)

    def test_validate_zero_gas_estimate(self):
        """Test that zero gas estimate is detected."""
        tx = TransactionCall(
            to="0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            data=b"\x00\x01\x02\x03",
            value=0,
            gas_estimate=0,
        )
        errors = validate_transaction_call(tx)

        assert any("Invalid gas estimate" in e for e in errors)

    def test_validate_negative_value(self):
        """Test that negative value is detected."""
        tx = TransactionCall(
            to="0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            data=b"\x00\x01\x02\x03",
            value=-1,
            gas_estimate=100000,
        )
        errors = validate_transaction_call(tx)

        assert any("Negative transaction value" in e for e in errors)

    def test_validate_multiple_errors(self):
        """Test that multiple errors are all reported."""
        tx = TransactionCall(
            to="",
            data=b"",
            value=-1,
            gas_estimate=0,
        )
        errors = validate_transaction_call(tx)

        # Should report all errors
        assert len(errors) >= 4


class TestFunctionSelectors:
    """Tests for function selector computation."""

    def test_deposit_selector(self, cdp_abi: list):
        """Test deposit function selector matches expected."""
        calldata = encode_function_call(
            abi=cdp_abi,
            function_name="deposit",
            args=[0, "0x0000000000000000000000000000000000000000", 0],
        )

        # Compute expected selector
        expected = keccak(text="deposit(uint256,address,uint256)")[:4]
        assert calldata[:4] == expected

    def test_mint_selector(self, cdp_abi: list):
        """Test mint function selector matches expected."""
        calldata = encode_function_call(
            abi=cdp_abi,
            function_name="mint",
            args=[0, 0, "0x0000000000000000000000000000000000000000"],
        )

        expected = keccak(text="mint(uint256,uint256,address)")[:4]
        assert calldata[:4] == expected

    def test_transfer_from_selector(self, erc721_abi: list):
        """Test transferFrom function selector matches expected."""
        calldata = encode_function_call(
            abi=erc721_abi,
            function_name="transferFrom",
            args=[
                "0x0000000000000000000000000000000000000000",
                "0x0000000000000000000000000000000000000000",
                0,
            ],
        )

        expected = keccak(text="transferFrom(address,address,uint256)")[:4]
        assert calldata[:4] == expected


class TestTransactionIntegration:
    """Integration tests for transaction building with gas module."""

    def test_gas_module_uses_transaction_encoding(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that gas module's _create_*_call functions now use encoding."""
        from src.gas import _create_deposit_call, _create_mint_call, _create_transfer_call

        # Create calls using gas module functions
        deposit_call = _create_deposit_call(
            sample_position,
            sample_chain_config["cdp_usd"],
            sample_chain_config["multisig"],
        )
        mint_call = _create_mint_call(
            sample_position,
            sample_chain_config["cdp_usd"],
        )
        transfer_call = _create_transfer_call(
            sample_position,
            sample_chain_config["nft_usd"],
            sample_chain_config["multisig"],
        )

        # Verify all have non-empty calldata now
        assert len(deposit_call.data) > 4
        assert len(mint_call.data) > 4
        assert len(transfer_call.data) > 4

        # Verify calldata starts with valid selector (4 bytes)
        assert len(deposit_call.data) >= 4
        assert len(mint_call.data) >= 4
        assert len(transfer_call.data) >= 4

    def test_transaction_builders_match_gas_module(
        self,
        sample_position: PositionMigration,
        sample_chain_config: ChainConfig,
    ):
        """Test that transaction builders produce equivalent calldata to gas module."""
        from src.gas import _create_deposit_call

        # Build using transactions module
        tx_module_call = build_deposit_tx(sample_position, sample_chain_config)

        # Build using gas module
        gas_module_call = _create_deposit_call(
            sample_position,
            sample_chain_config["cdp_usd"],
            sample_chain_config["multisig"],
        )

        # Calldata should match
        assert tx_module_call.data == gas_module_call.data

        # Target address should match
        assert tx_module_call.to == gas_module_call.to
