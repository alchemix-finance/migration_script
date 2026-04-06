"""Tests for transaction building module (V3 API)."""

import pytest
from eth_abi import decode
from eth_utils import keccak

from src.abi import load_alchemist_abi, load_altoken_abi, load_erc721_abi
from src.config import (
    GAS_BURN,
    GAS_DEPOSIT,
    GAS_LARGE_POSITION_SURCHARGE,
    GAS_MINT,
    GAS_SET_DEPOSIT_CAP,
    GAS_TRANSFER_ALTOKEN,
    GAS_TRANSFER_NFT,
    LARGE_POSITION_THRESHOLD,
)
from src.transactions import (
    TransactionBuildError,
    build_altoken_transfer_tx,
    build_burn_tx,
    build_deposit_tx,
    build_mint_tx,
    build_nft_transfer_tx,
    build_set_deposit_cap_tx,
    encode_function_call,
    validate_transaction_call,
)
from src.types import AssetType, PositionMigration, TransactionCall

# ---------------------------------------------------------------------------
# Constants used throughout tests
# ---------------------------------------------------------------------------

MULTISIG = "0x1111111111111111111111111111111111111111"
USER_ADDR = "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
ALCHEMIST = "0x2222222222222222222222222222222222222222"
NFT_ADDR = "0x3333333333333333333333333333333333333333"
AL_TOKEN = "0x4444444444444444444444444444444444444444"
ZERO_ADDR = "0x0000000000000000000000000000000000000000"

# Amounts deliberately below LARGE_POSITION_THRESHOLD (10**21) so that gas
# tests for "normal" positions pass without the surcharge.
DEPOSIT_AMOUNT = 100 * 10**18   # 100 tokens — well below 10**21
MINT_AMOUNT = 50 * 10**18       # 50 tokens — well below 10**21
CREDIT_AMOUNT = 30 * 10**18
BURN_AMOUNT = 40 * 10**18
TOKEN_ID = 42


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def alchemist_abi() -> list:
    """Load AlchemistV3 ABI."""
    return load_alchemist_abi()


@pytest.fixture
def erc721_abi() -> list:
    """Load ERC721 ABI."""
    return load_erc721_abi()


@pytest.fixture
def altoken_abi() -> list:
    """Load alToken ABI."""
    return load_altoken_abi()


@pytest.fixture
def debt_position() -> PositionMigration:
    """A typical debt user — has a deposit and minted debt."""
    return PositionMigration(
        user_address=USER_ADDR,
        asset_type=AssetType.USD,
        chain="mainnet",
        deposit_amount_wei=DEPOSIT_AMOUNT,
        mint_amount_wei=MINT_AMOUNT,
        credit_amount_wei=0,
    )


@pytest.fixture
def credit_position() -> PositionMigration:
    """A credit user — protocol owes them alAssets."""
    return PositionMigration(
        user_address=USER_ADDR,
        asset_type=AssetType.ETH,
        chain="optimism",
        deposit_amount_wei=2 * 10**18,
        mint_amount_wei=CREDIT_AMOUNT,   # temp mint, will be burned in Phase 3
        credit_amount_wei=CREDIT_AMOUNT,
    )


@pytest.fixture
def zero_debt_position() -> PositionMigration:
    """A user with no debt and no credit — deposit only."""
    return PositionMigration(
        user_address=USER_ADDR,
        asset_type=AssetType.USD,
        chain="mainnet",
        deposit_amount_wei=DEPOSIT_AMOUNT,
        mint_amount_wei=0,
        credit_amount_wei=0,
    )


@pytest.fixture
def large_position() -> PositionMigration:
    """A position exceeding LARGE_POSITION_THRESHOLD — attracts gas surcharge."""
    return PositionMigration(
        user_address=USER_ADDR,
        asset_type=AssetType.USD,
        chain="mainnet",
        deposit_amount_wei=LARGE_POSITION_THRESHOLD,      # exactly at threshold
        mint_amount_wei=LARGE_POSITION_THRESHOLD,
        credit_amount_wei=0,
    )


# ---------------------------------------------------------------------------
# TestEncodeFunctionCall
# ---------------------------------------------------------------------------


class TestEncodeFunctionCall:
    """Tests for the low-level encode_function_call helper."""

    def test_deposit_selector(self, alchemist_abi: list):
        """deposit() selector must match keccak('deposit(uint256,address,uint256)')[:4]."""
        calldata = encode_function_call(
            alchemist_abi, "deposit", [DEPOSIT_AMOUNT, MULTISIG, 0]
        )
        expected = keccak(text="deposit(uint256,address,uint256)")[:4]
        assert calldata[:4] == expected

    def test_deposit_arg_encoding(self, alchemist_abi: list):
        """deposit() calldata must decode to the exact args passed in."""
        amount = 9_999 * 10**18
        calldata = encode_function_call(
            alchemist_abi, "deposit", [amount, MULTISIG, TOKEN_ID]
        )
        decoded = decode(["uint256", "address", "uint256"], calldata[4:])
        assert decoded[0] == amount
        assert decoded[1].lower() == MULTISIG.lower()
        assert decoded[2] == TOKEN_ID

    def test_deposit_calldata_length(self, alchemist_abi: list):
        """deposit() calldata is exactly 4 + 3*32 = 100 bytes."""
        calldata = encode_function_call(
            alchemist_abi, "deposit", [DEPOSIT_AMOUNT, MULTISIG, 0]
        )
        assert len(calldata) == 4 + 3 * 32

    def test_mint_selector(self, alchemist_abi: list):
        """mint() selector must match keccak('mint(uint256,uint256,address)')[:4]."""
        calldata = encode_function_call(
            alchemist_abi, "mint", [TOKEN_ID, MINT_AMOUNT, MULTISIG]
        )
        expected = keccak(text="mint(uint256,uint256,address)")[:4]
        assert calldata[:4] == expected

    def test_mint_arg_encoding(self, alchemist_abi: list):
        """mint() calldata must decode to (tokenId, amount, recipient)."""
        calldata = encode_function_call(
            alchemist_abi, "mint", [TOKEN_ID, MINT_AMOUNT, MULTISIG]
        )
        decoded = decode(["uint256", "uint256", "address"], calldata[4:])
        assert decoded[0] == TOKEN_ID
        assert decoded[1] == MINT_AMOUNT
        assert decoded[2].lower() == MULTISIG.lower()

    def test_burn_selector(self, alchemist_abi: list):
        """burn() selector must match keccak('burn(uint256,uint256)')[:4]."""
        calldata = encode_function_call(alchemist_abi, "burn", [BURN_AMOUNT, TOKEN_ID])
        expected = keccak(text="burn(uint256,uint256)")[:4]
        assert calldata[:4] == expected

    def test_burn_arg_encoding(self, alchemist_abi: list):
        """burn() calldata must decode to (amount, recipientId)."""
        calldata = encode_function_call(alchemist_abi, "burn", [BURN_AMOUNT, TOKEN_ID])
        decoded = decode(["uint256", "uint256"], calldata[4:])
        assert decoded[0] == BURN_AMOUNT
        assert decoded[1] == TOKEN_ID

    def test_transfer_selector(self, altoken_abi: list):
        """transfer() selector must match keccak('transfer(address,uint256)')[:4]."""
        calldata = encode_function_call(
            altoken_abi, "transfer", [USER_ADDR, MINT_AMOUNT]
        )
        expected = keccak(text="transfer(address,uint256)")[:4]
        assert calldata[:4] == expected

    def test_transfer_from_selector(self, erc721_abi: list):
        """transferFrom() selector must match keccak('transferFrom(address,address,uint256)')[:4]."""
        calldata = encode_function_call(
            erc721_abi, "transferFrom", [MULTISIG, USER_ADDR, TOKEN_ID]
        )
        expected = keccak(text="transferFrom(address,address,uint256)")[:4]
        assert calldata[:4] == expected

    def test_unknown_function_raises(self, alchemist_abi: list):
        """Encoding an ABI-absent function name raises TransactionBuildError."""
        with pytest.raises(TransactionBuildError, match="not found in ABI"):
            encode_function_call(alchemist_abi, "liquidate", [])

    def test_wrong_arg_count_raises(self, alchemist_abi: list):
        """Passing the wrong number of args raises TransactionBuildError."""
        with pytest.raises(TransactionBuildError, match="expects 3 args"):
            encode_function_call(alchemist_abi, "deposit", [DEPOSIT_AMOUNT])

    def test_max_uint256_value(self, alchemist_abi: list):
        """Max uint256 round-trips correctly through ABI encoding."""
        max_val = 2**256 - 1
        calldata = encode_function_call(
            alchemist_abi, "deposit", [max_val, MULTISIG, 0]
        )
        decoded = decode(["uint256", "address", "uint256"], calldata[4:])
        assert decoded[0] == max_val

    def test_zero_values_encode_correctly(self, alchemist_abi: list):
        """All-zero args still produce well-formed calldata."""
        calldata = encode_function_call(
            alchemist_abi, "deposit", [0, ZERO_ADDR, 0]
        )
        assert len(calldata) == 4 + 3 * 32
        decoded = decode(["uint256", "address", "uint256"], calldata[4:])
        assert decoded[0] == 0
        assert decoded[2] == 0


# ---------------------------------------------------------------------------
# TestBuildSetDepositCapTx
# ---------------------------------------------------------------------------


class TestBuildSetDepositCapTx:
    """Tests for build_set_deposit_cap_tx."""

    def test_to_address(self):
        """Transaction targets the alchemist contract."""
        tx = build_set_deposit_cap_tx(ALCHEMIST, 10**24)
        assert tx.to == ALCHEMIST

    def test_correct_selector(self):
        """Calldata starts with keccak('setDepositCap(uint256)')[:4]."""
        tx = build_set_deposit_cap_tx(ALCHEMIST, 10**24)
        expected = keccak(text="setDepositCap(uint256)")[:4]
        assert tx.data[:4] == expected

    def test_correct_cap_value(self):
        """Cap value round-trips correctly through calldata."""
        new_cap = 7_777 * 10**18
        tx = build_set_deposit_cap_tx(ALCHEMIST, new_cap)
        decoded = decode(["uint256"], tx.data[4:])
        assert decoded[0] == new_cap

    def test_gas_estimate(self):
        """Gas estimate equals GAS_SET_DEPOSIT_CAP."""
        tx = build_set_deposit_cap_tx(ALCHEMIST, 10**24)
        assert tx.gas_estimate == GAS_SET_DEPOSIT_CAP

    def test_value_is_zero(self):
        """No ETH is sent with this call."""
        tx = build_set_deposit_cap_tx(ALCHEMIST, 10**24)
        assert tx.value == 0

    def test_description_contains_cap(self):
        """Description mentions the cap value."""
        new_cap = 12345
        tx = build_set_deposit_cap_tx(ALCHEMIST, new_cap)
        assert str(new_cap) in tx.description


# ---------------------------------------------------------------------------
# TestBuildDepositTx
# ---------------------------------------------------------------------------


class TestBuildDepositTx:
    """Tests for build_deposit_tx."""

    def test_to_is_alchemist(self, debt_position: PositionMigration):
        """Transaction targets the alchemist address supplied."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        assert tx.to == ALCHEMIST

    def test_correct_selector(self, debt_position: PositionMigration):
        """Calldata selector matches deposit(uint256,address,uint256)."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        expected = keccak(text="deposit(uint256,address,uint256)")[:4]
        assert tx.data[:4] == expected

    def test_arg_order_amount_recipient_tokenid(self, debt_position: PositionMigration):
        """Encoded args follow the order (amount, recipient, tokenId=0)."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        decoded = decode(["uint256", "address", "uint256"], tx.data[4:])
        assert decoded[0] == debt_position.deposit_amount_wei
        assert decoded[1].lower() == MULTISIG.lower()
        assert decoded[2] == 0   # tokenId=0 triggers auto-mint

    def test_recipient_is_multisig_not_user(self, debt_position: PositionMigration):
        """Deposit recipient must be the multisig, not the user."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        decoded = decode(["uint256", "address", "uint256"], tx.data[4:])
        assert decoded[1].lower() == MULTISIG.lower()
        assert decoded[1].lower() != USER_ADDR.lower()

    def test_value_is_zero(self, debt_position: PositionMigration):
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        assert tx.value == 0

    def test_gas_normal_position(self, debt_position: PositionMigration):
        """Normal position (below threshold) gets GAS_DEPOSIT."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        assert tx.gas_estimate == GAS_DEPOSIT

    def test_gas_large_position(self, large_position: PositionMigration):
        """Position at or above LARGE_POSITION_THRESHOLD gets surcharge."""
        tx = build_deposit_tx(large_position, ALCHEMIST, MULTISIG)
        assert tx.gas_estimate == GAS_DEPOSIT + GAS_LARGE_POSITION_SURCHARGE

    def test_description_contains_user(self, debt_position: PositionMigration):
        """Description mentions the user address."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        assert debt_position.user_address.lower() in tx.description.lower()

    def test_description_contains_amount(self, debt_position: PositionMigration):
        """Description mentions the deposit amount."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        assert str(debt_position.deposit_amount_wei) in tx.description

    def test_returns_transaction_call(self, debt_position: PositionMigration):
        """Return type is TransactionCall."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        assert isinstance(tx, TransactionCall)


# ---------------------------------------------------------------------------
# TestBuildMintTx
# ---------------------------------------------------------------------------


class TestBuildMintTx:
    """Tests for build_mint_tx."""

    def test_to_is_alchemist(self, debt_position: PositionMigration):
        """Transaction targets the alchemist address supplied."""
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        assert tx.to == ALCHEMIST

    def test_correct_selector(self, debt_position: PositionMigration):
        """Calldata selector matches mint(uint256,uint256,address)."""
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        expected = keccak(text="mint(uint256,uint256,address)")[:4]
        assert tx.data[:4] == expected

    def test_arg_order_tokenid_amount_recipient(self, debt_position: PositionMigration):
        """Encoded args follow the order (tokenId, amount, recipient)."""
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        decoded = decode(["uint256", "uint256", "address"], tx.data[4:])
        assert decoded[0] == TOKEN_ID
        assert decoded[1] == debt_position.mint_amount_wei
        assert decoded[2].lower() == MULTISIG.lower()

    def test_recipient_is_multisig_not_user(self, debt_position: PositionMigration):
        """CRITICAL: mint recipient must be the multisig (not the user).

        alAssets go to the multisig so it can later call burn() to clear
        position debt in Phase 3. Sending to the user here would break
        the burn phase since the multisig would have no alAssets to burn.
        """
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        decoded = decode(["uint256", "uint256", "address"], tx.data[4:])
        assert decoded[2].lower() == MULTISIG.lower()
        assert decoded[2].lower() != debt_position.user_address.lower()

    def test_token_id_is_passed_through(self, debt_position: PositionMigration):
        """The explicit token_id arg (from deposit event) is encoded."""
        for tid in (1, 99, 10_000):
            tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, tid)
            decoded = decode(["uint256", "uint256", "address"], tx.data[4:])
            assert decoded[0] == tid

    def test_value_is_zero(self, debt_position: PositionMigration):
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        assert tx.value == 0

    def test_gas_normal_position(self, debt_position: PositionMigration):
        """Normal mint_amount_wei gets GAS_MINT."""
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        assert tx.gas_estimate == GAS_MINT

    def test_gas_large_mint(self, large_position: PositionMigration):
        """Large mint_amount_wei gets GAS_MINT + surcharge."""
        tx = build_mint_tx(large_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        assert tx.gas_estimate == GAS_MINT + GAS_LARGE_POSITION_SURCHARGE

    def test_zero_mint_amount_raises(self, zero_debt_position: PositionMigration):
        """Building a mint tx for a zero-debt position raises TransactionBuildError."""
        with pytest.raises(TransactionBuildError):
            build_mint_tx(zero_debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)

    def test_credit_position_mint(self, credit_position: PositionMigration):
        """Credit users with mint_amount_wei > 0 can have a mint tx built."""
        tx = build_mint_tx(credit_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        decoded = decode(["uint256", "uint256", "address"], tx.data[4:])
        assert decoded[1] == credit_position.mint_amount_wei

    def test_returns_transaction_call(self, debt_position: PositionMigration):
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        assert isinstance(tx, TransactionCall)


# ---------------------------------------------------------------------------
# TestBuildBurnTx
# ---------------------------------------------------------------------------


class TestBuildBurnTx:
    """Tests for build_burn_tx."""

    def test_to_is_alchemist(self):
        """Transaction targets the alchemist address supplied."""
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        assert tx.to == ALCHEMIST

    def test_correct_selector(self):
        """Calldata selector matches burn(uint256,uint256)."""
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        expected = keccak(text="burn(uint256,uint256)")[:4]
        assert tx.data[:4] == expected

    def test_arg_order_amount_recipientid(self):
        """Encoded args follow the order (amount, recipientId)."""
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        decoded = decode(["uint256", "uint256"], tx.data[4:])
        assert decoded[0] == BURN_AMOUNT
        assert decoded[1] == TOKEN_ID

    def test_calldata_length(self):
        """burn() calldata is 4 + 2*32 = 68 bytes."""
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        assert len(tx.data) == 4 + 2 * 32

    def test_gas_estimate(self):
        """Gas estimate equals GAS_BURN."""
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        assert tx.gas_estimate == GAS_BURN

    def test_value_is_zero(self):
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        assert tx.value == 0

    def test_description_mentions_user(self):
        """Description mentions the user address for traceability."""
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        assert USER_ADDR.lower() in tx.description.lower()

    def test_different_token_ids_encode_correctly(self):
        """Different token IDs are encoded correctly into the second argument."""
        for tid in (1, 7, 100):
            tx = build_burn_tx(tid, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
            decoded = decode(["uint256", "uint256"], tx.data[4:])
            assert decoded[1] == tid


# ---------------------------------------------------------------------------
# TestBuildAltokenTransferTx
# ---------------------------------------------------------------------------


class TestBuildAltokenTransferTx:
    """Tests for build_altoken_transfer_tx."""

    def test_to_is_altoken_address(self):
        """Transaction targets the al_token address, not the recipient."""
        tx = build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR)
        assert tx.to == AL_TOKEN

    def test_correct_selector(self):
        """Calldata selector matches transfer(address,uint256)."""
        tx = build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR)
        expected = keccak(text="transfer(address,uint256)")[:4]
        assert tx.data[:4] == expected

    def test_arg_order_recipient_amount(self):
        """Encoded args follow the order (to, amount)."""
        tx = build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR)
        decoded = decode(["address", "uint256"], tx.data[4:])
        assert decoded[0].lower() == USER_ADDR.lower()
        assert decoded[1] == CREDIT_AMOUNT

    def test_calldata_length(self):
        """transfer() calldata is 4 + 2*32 = 68 bytes."""
        tx = build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR)
        assert len(tx.data) == 4 + 2 * 32

    def test_gas_estimate(self):
        """Gas estimate equals GAS_TRANSFER_ALTOKEN."""
        tx = build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR)
        assert tx.gas_estimate == GAS_TRANSFER_ALTOKEN

    def test_value_is_zero(self):
        tx = build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR)
        assert tx.value == 0

    def test_arbitrary_recipient(self):
        """Any valid recipient address is encoded correctly."""
        other = "0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
        tx = build_altoken_transfer_tx(AL_TOKEN, other, CREDIT_AMOUNT, USER_ADDR)
        decoded = decode(["address", "uint256"], tx.data[4:])
        assert decoded[0].lower() == other.lower()

    def test_returns_transaction_call(self):
        tx = build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR)
        assert isinstance(tx, TransactionCall)


# ---------------------------------------------------------------------------
# TestBuildNftTransferTx
# ---------------------------------------------------------------------------


class TestBuildNftTransferTx:
    """Tests for build_nft_transfer_tx."""

    def test_to_is_nft_address(self):
        """Transaction targets the NFT contract."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        assert tx.to == NFT_ADDR

    def test_correct_selector(self):
        """Calldata selector matches transferFrom(address,address,uint256)."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        expected = keccak(text="transferFrom(address,address,uint256)")[:4]
        assert tx.data[:4] == expected

    def test_arg_order_from_to_tokenid(self):
        """Encoded args follow the order (from=multisig, to=user, tokenId)."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        decoded = decode(["address", "address", "uint256"], tx.data[4:])
        assert decoded[0].lower() == MULTISIG.lower()   # from
        assert decoded[1].lower() == USER_ADDR.lower()  # to
        assert decoded[2] == TOKEN_ID

    def test_from_is_multisig_not_user(self):
        """CRITICAL: 'from' must be the multisig (current owner), not the user."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        decoded = decode(["address", "address", "uint256"], tx.data[4:])
        assert decoded[0].lower() == MULTISIG.lower()
        assert decoded[0].lower() != USER_ADDR.lower()

    def test_to_is_user_not_multisig(self):
        """NFT destination is the original user."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        decoded = decode(["address", "address", "uint256"], tx.data[4:])
        assert decoded[1].lower() == USER_ADDR.lower()
        assert decoded[1].lower() != MULTISIG.lower()

    def test_calldata_length(self):
        """transferFrom() calldata is 4 + 3*32 = 100 bytes."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        assert len(tx.data) == 4 + 3 * 32

    def test_gas_estimate(self):
        """Gas estimate equals GAS_TRANSFER_NFT."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        assert tx.gas_estimate == GAS_TRANSFER_NFT

    def test_value_is_zero(self):
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        assert tx.value == 0

    def test_various_token_ids(self):
        """Token ID is encoded correctly for several values."""
        for tid in (0, 1, 999, 2**64):
            tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, tid)
            decoded = decode(["address", "address", "uint256"], tx.data[4:])
            assert decoded[2] == tid

    def test_returns_transaction_call(self):
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        assert isinstance(tx, TransactionCall)


# ---------------------------------------------------------------------------
# TestValidateTransactionCall
# ---------------------------------------------------------------------------


class TestValidateTransactionCall:
    """Tests for validate_transaction_call."""

    def _valid_tx(self, **overrides) -> TransactionCall:
        """Return a known-valid TransactionCall, optionally overriding fields."""
        fields = dict(
            to="0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            data=b"\x12\x34\x56\x78",   # 4-byte selector
            value=0,
            gas_estimate=100_000,
        )
        fields.update(overrides)
        return TransactionCall(**fields)

    def test_valid_transaction_has_no_errors(self):
        """A well-formed TransactionCall produces an empty error list."""
        errors = validate_transaction_call(self._valid_tx())
        assert errors == []

    def test_empty_to_address(self):
        """Empty 'to' triggers an error."""
        errors = validate_transaction_call(self._valid_tx(to=""))
        assert any("'to' address is empty" in e for e in errors)

    def test_invalid_to_address_no_prefix(self):
        """'to' without 0x prefix triggers an error."""
        errors = validate_transaction_call(self._valid_tx(to="deadbeef" * 5))
        assert len(errors) > 0

    def test_invalid_to_address_wrong_length(self):
        """'to' that is too short (but starts with 0x) triggers an error."""
        errors = validate_transaction_call(self._valid_tx(to="0x1234"))
        assert any("Invalid 'to' address" in e for e in errors)

    def test_empty_calldata(self):
        """Empty calldata triggers an error."""
        errors = validate_transaction_call(self._valid_tx(data=b""))
        assert any("Calldata too short" in e or "calldata" in e.lower() for e in errors)

    def test_calldata_too_short(self):
        """Calldata shorter than 4 bytes triggers an error."""
        errors = validate_transaction_call(self._valid_tx(data=b"\x00\x01\x02"))
        assert any("Calldata too short" in e for e in errors)

    def test_zero_gas_estimate(self):
        """Zero gas estimate triggers an error."""
        errors = validate_transaction_call(self._valid_tx(gas_estimate=0))
        assert any("Invalid gas estimate" in e for e in errors)

    def test_negative_gas_estimate(self):
        """Negative gas estimate triggers an error."""
        errors = validate_transaction_call(self._valid_tx(gas_estimate=-1))
        assert any("Invalid gas estimate" in e for e in errors)

    def test_negative_value(self):
        """Negative ETH value triggers an error."""
        errors = validate_transaction_call(self._valid_tx(value=-1))
        assert any("Negative value" in e for e in errors)

    def test_zero_value_is_allowed(self):
        """value=0 is valid (most calls send no ETH)."""
        errors = validate_transaction_call(self._valid_tx(value=0))
        assert errors == []

    def test_multiple_errors_all_reported(self):
        """Multiple bad fields all appear in the error list."""
        bad_tx = TransactionCall(to="", data=b"", value=-1, gas_estimate=0)
        errors = validate_transaction_call(bad_tx)
        assert len(errors) >= 3   # to, data, gas, value

    def test_builder_output_passes_validation(self, debt_position: PositionMigration):
        """Transactions produced by the builder functions pass validation."""
        txs = [
            build_deposit_tx(debt_position, ALCHEMIST, MULTISIG),
            build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID),
            build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR),
            build_altoken_transfer_tx(AL_TOKEN, USER_ADDR, CREDIT_AMOUNT, USER_ADDR),
            build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID),
            build_set_deposit_cap_tx(ALCHEMIST, 10**24),
        ]
        for tx in txs:
            assert validate_transaction_call(tx) == [], (
                f"Unexpected validation errors for {tx.description}: "
                f"{validate_transaction_call(tx)}"
            )


# ---------------------------------------------------------------------------
# TestMigrationDesignInvariants
# ---------------------------------------------------------------------------


class TestMigrationDesignInvariants:
    """High-level invariants that enforce correct migration sequencing."""

    def test_deposit_uses_token_id_zero_for_auto_mint(
        self, debt_position: PositionMigration
    ):
        """deposit() always passes tokenId=0 to trigger NFT auto-mint by the contract."""
        tx = build_deposit_tx(debt_position, ALCHEMIST, MULTISIG)
        decoded = decode(["uint256", "address", "uint256"], tx.data[4:])
        assert decoded[2] == 0, "tokenId must be 0 so the contract auto-mints the NFT"

    def test_mint_recipient_is_multisig_for_burn_phase(
        self, debt_position: PositionMigration
    ):
        """Minted alAssets must land in the multisig so Phase 3 burn() can clear debt."""
        tx = build_mint_tx(debt_position, ALCHEMIST, MULTISIG, TOKEN_ID)
        decoded = decode(["uint256", "uint256", "address"], tx.data[4:])
        recipient = decoded[2].lower()
        assert recipient == MULTISIG.lower(), (
            "Mint recipient must be the multisig — the multisig calls burn() in Phase 3"
        )

    def test_nft_transfer_direction_multisig_to_user(self):
        """NFT transfer must be FROM multisig TO user (not the other way)."""
        tx = build_nft_transfer_tx(NFT_ADDR, MULTISIG, USER_ADDR, TOKEN_ID)
        decoded = decode(["address", "address", "uint256"], tx.data[4:])
        assert decoded[0].lower() == MULTISIG.lower(), "'from' must be multisig"
        assert decoded[1].lower() == USER_ADDR.lower(), "'to' must be user"

    def test_burn_positions_amount_before_token_id(self):
        """burn(amount, recipientId): amount is first, tokenId is second."""
        tx = build_burn_tx(TOKEN_ID, BURN_AMOUNT, ALCHEMIST, USER_ADDR)
        decoded = decode(["uint256", "uint256"], tx.data[4:])
        # decoded[0] = amount, decoded[1] = tokenId (the position's recipientId)
        assert decoded[0] == BURN_AMOUNT
        assert decoded[1] == TOKEN_ID
