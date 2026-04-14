"""Unit tests for gas estimation and batching logic (V3).

V1 exposed `_greedy_bin_pack`, `OperationType`, `estimate_*_gas`, `create_batches`,
`BASE_GAS_*`, `GAS_BUFFER`, `GAS_LIMIT`, `GAS_PER_LARGE_POSITION`, `format_batch_summary`.
V3 refactored into asset-specific builders (`create_deposit_batches`,
`create_mint_batches`, `create_credit_batches`, `create_transfer_batches` plus
the new pre-deposit trio), gas constants live in `src.config` (`GAS_DEPOSIT`,
`GAS_MINT`, `GAS_LARGE_POSITION_SURCHARGE`, etc.), per-chain limits via
`get_effective_gas_limit`/`get_effective_size_limit`, and the packing predicate
is `_can_add_call`.

Direct tests of the correctness-surface internals (`_batch_calldata_size`,
`_can_add_call`, `_gas_deposit`, `_gas_mint`) plus integration over each
public batch builder and the migration plan top-level.
"""

from __future__ import annotations

import pytest

from src.config import (
    GAS_DEPOSIT,
    GAS_LARGE_POSITION_SURCHARGE,
    GAS_MINT,
    GAS_SET_DEPOSIT_CAP,
    GAS_TRANSFER_ALTOKEN,
    GAS_TRANSFER_NFT,
    LARGE_POSITION_THRESHOLD,
    MAX_CALLS_PER_BATCH,
    MULTISEND_CALL_BYTES,
    MULTISEND_WRAPPER_BYTES,
    get_effective_gas_limit,
    get_effective_size_limit,
)
from src.gas import (
    _batch_calldata_size,
    _can_add_call,
    _gas_deposit,
    _gas_mint,
    build_migration_plan,
    calculate_batch_statistics,
    create_approve_myt_batches,
    create_approve_underlying_batches,
    create_credit_batches,
    create_deposit_batches,
    create_mint_batches,
    create_myt_deposit_batches,
    create_transfer_batches,
    format_batch_summary,
    gas_per_position_in_deposit_batch,
    verify_batch_gas_limits,
)
from src.types import (
    AssetType,
    MigrationPlan,
    PositionMigration,
    TransactionBatch,
    TransactionCall,
)

MULTISIG = "0x1111111111111111111111111111111111111111"
ALCHEMIST = "0x2222222222222222222222222222222222222222"
NFT_ADDR = "0x3333333333333333333333333333333333333333"
AL_TOKEN = "0x4444444444444444444444444444444444444444"
MYT_ADDR = "0x5555555555555555555555555555555555555555"
UNDERLYING = "0x6666666666666666666666666666666666666666"


# ---------------------------------------------------------------------------
# Direct tests of correctness-surface internals
# ---------------------------------------------------------------------------


class TestGasConstants:
    def test_gas_constants_are_positive(self) -> None:
        for v in (GAS_DEPOSIT, GAS_MINT, GAS_SET_DEPOSIT_CAP, GAS_TRANSFER_ALTOKEN,
                  GAS_TRANSFER_NFT, GAS_LARGE_POSITION_SURCHARGE):
            assert v > 0

    def test_large_position_threshold_is_10_to_21(self) -> None:
        assert LARGE_POSITION_THRESHOLD == 10**21

    def test_max_calls_per_batch_is_positive(self) -> None:
        assert MAX_CALLS_PER_BATCH > 0


class TestGasDeposit:
    """Direct tests of _gas_deposit — the large-position surcharge rule."""

    def _pos(self, deposit_wei: int, mint_wei: int = 0) -> PositionMigration:
        return PositionMigration(
            user_address="0x" + "1" * 40,
            asset_type=AssetType.USD,
            chain="mainnet",
            deposit_amount_wei=deposit_wei,
            mint_amount_wei=mint_wei,
            credit_amount_wei=0,
        )

    def test_normal_position_no_surcharge(self) -> None:
        p = self._pos(deposit_wei=10**20)  # below threshold
        assert _gas_deposit(p) == GAS_DEPOSIT

    def test_large_position_surcharge_applied(self) -> None:
        p = self._pos(deposit_wei=LARGE_POSITION_THRESHOLD + 1)
        assert _gas_deposit(p) == GAS_DEPOSIT + GAS_LARGE_POSITION_SURCHARGE

    def test_exactly_at_threshold_triggers_surcharge(self) -> None:
        p = self._pos(deposit_wei=LARGE_POSITION_THRESHOLD)
        assert _gas_deposit(p) == GAS_DEPOSIT + GAS_LARGE_POSITION_SURCHARGE

    def test_public_alias_matches_internal(self) -> None:
        p = self._pos(deposit_wei=5 * 10**22)
        assert gas_per_position_in_deposit_batch(p) == _gas_deposit(p)


class TestGasMint:
    """Direct tests of _gas_mint — surcharge keyed on mint_amount_wei, not deposit."""

    def _pos(self, mint_wei: int) -> PositionMigration:
        return PositionMigration(
            user_address="0x" + "1" * 40,
            asset_type=AssetType.USD,
            chain="mainnet",
            deposit_amount_wei=10**18,
            mint_amount_wei=mint_wei,
            credit_amount_wei=0,
        )

    def test_normal_mint_no_surcharge(self) -> None:
        assert _gas_mint(self._pos(10**18)) == GAS_MINT

    def test_large_mint_surcharge(self) -> None:
        assert _gas_mint(self._pos(LARGE_POSITION_THRESHOLD)) == GAS_MINT + GAS_LARGE_POSITION_SURCHARGE


class TestBatchCalldataSize:
    """Direct tests of _batch_calldata_size — encodes multisend wire size."""

    def test_empty_calls_returns_wrapper_size(self) -> None:
        assert _batch_calldata_size([]) == MULTISEND_WRAPPER_BYTES

    def test_single_empty_call(self) -> None:
        c = TransactionCall(to="0x" + "0" * 40, data=b"", gas_estimate=1)
        assert _batch_calldata_size([c]) == MULTISEND_WRAPPER_BYTES + MULTISEND_CALL_BYTES

    def test_single_call_with_data(self) -> None:
        c = TransactionCall(to="0x" + "0" * 40, data=b"\x01" * 36, gas_estimate=1)
        assert _batch_calldata_size([c]) == MULTISEND_WRAPPER_BYTES + MULTISEND_CALL_BYTES + 36

    def test_multiple_calls_sum_correctly(self) -> None:
        calls = [
            TransactionCall(to="0x" + "0" * 40, data=b"\x01" * 36, gas_estimate=1),
            TransactionCall(to="0x" + "0" * 40, data=b"\x01" * 68, gas_estimate=1),
        ]
        expected = MULTISEND_WRAPPER_BYTES + 2 * MULTISEND_CALL_BYTES + 36 + 68
        assert _batch_calldata_size(calls) == expected


class TestCanAddCall:
    """Direct tests of _can_add_call — decides every batch boundary."""

    def _call(self, gas: int, data_len: int = 36) -> TransactionCall:
        return TransactionCall(to="0x" + "0" * 40, data=b"\x01" * data_len, gas_estimate=gas)

    def test_can_add_when_below_all_limits(self) -> None:
        batch = TransactionBatch(batch_number=1)
        call = self._call(gas=10_000)
        assert _can_add_call(batch, call, gas_limit=1_000_000, size_limit=10_000, max_calls=10)

    def test_reject_when_over_gas_limit(self) -> None:
        batch = TransactionBatch(batch_number=1)
        batch.total_gas = 900_000
        call = self._call(gas=200_000)
        assert not _can_add_call(batch, call, gas_limit=1_000_000, size_limit=10_000, max_calls=10)

    def test_reject_when_over_size_limit(self) -> None:
        batch = TransactionBatch(batch_number=1)
        call = self._call(gas=1, data_len=10_000)
        # wrapper + call_overhead + 10_000 = way over size_limit=500
        assert not _can_add_call(batch, call, gas_limit=10_000_000, size_limit=500, max_calls=10)

    def test_reject_when_at_max_calls(self) -> None:
        batch = TransactionBatch(batch_number=1)
        for _ in range(5):
            batch.calls.append(self._call(gas=10))
        call = self._call(gas=10)
        assert not _can_add_call(batch, call, gas_limit=10**9, size_limit=10**9, max_calls=5)

    def test_boundary_exactly_at_gas_limit_accepted(self) -> None:
        batch = TransactionBatch(batch_number=1)
        batch.total_gas = 500_000
        call = self._call(gas=500_000)
        # total would be exactly == gas_limit; 500k + 500k = 1M, predicate uses >
        assert _can_add_call(batch, call, gas_limit=1_000_000, size_limit=10**6, max_calls=10)


# ---------------------------------------------------------------------------
# Integration — public batch builders respect per-chain limits
# ---------------------------------------------------------------------------


def _mk_position(deposit_wei: int = 10**18, mint_wei: int = 0, credit_wei: int = 0,
                 addr: str = "0x1111111111111111111111111111111111111111") -> PositionMigration:
    return PositionMigration(
        user_address=addr,
        asset_type=AssetType.USD,
        chain="mainnet",
        deposit_amount_wei=deposit_wei,
        mint_amount_wei=mint_wei,
        credit_amount_wei=credit_wei,
    )


def _mk_positions(n: int, **kwargs) -> list[PositionMigration]:
    out = []
    for i in range(n):
        addr = "0x" + format(i + 1, "040x")
        out.append(_mk_position(addr=addr, **kwargs))
    return out


class TestCreateDepositBatches:
    def test_empty_positions_returns_no_batches(self) -> None:
        assert create_deposit_batches([], ALCHEMIST, MULTISIG, chain="mainnet") == []

    def test_single_small_position_one_batch(self) -> None:
        batches = create_deposit_batches(
            _mk_positions(1), ALCHEMIST, MULTISIG, chain="mainnet",
        )
        assert len(batches) == 1
        # setDepositCap is inserted at slot 0.
        assert batches[0].calls[0].to == ALCHEMIST
        assert batches[0].calls[0].gas_estimate == GAS_SET_DEPOSIT_CAP
        # one deposit after that.
        assert len(batches[0].calls) == 2
        assert batches[0].batch_type == "deposit"

    def test_every_batch_under_chain_gas_limit(self) -> None:
        positions = _mk_positions(200)
        batches = create_deposit_batches(positions, ALCHEMIST, MULTISIG, chain="mainnet")
        limit = get_effective_gas_limit("mainnet")
        for b in batches:
            assert b.total_gas <= limit

    def test_every_batch_under_chain_size_limit(self) -> None:
        positions = _mk_positions(200)
        batches = create_deposit_batches(positions, ALCHEMIST, MULTISIG, chain="mainnet")
        size_limit = get_effective_size_limit("mainnet")
        for b in batches:
            assert _batch_calldata_size(b.calls) <= size_limit

    def test_sum_of_deposit_calls_equals_input(self) -> None:
        positions = _mk_positions(100)
        batches = create_deposit_batches(positions, ALCHEMIST, MULTISIG, chain="mainnet")
        total_deposit_calls = sum(len(b.calls) - 1 for b in batches)  # minus setDepositCap each
        assert total_deposit_calls == 100


class TestCreateMintBatches:
    def test_no_mintable_positions_empty(self) -> None:
        positions = [_mk_position(mint_wei=0) for _ in range(5)]
        assert create_mint_batches(
            positions, ALCHEMIST, MULTISIG, token_id_map={}, chain="mainnet",
        ) == []

    def test_only_debt_users_get_mint_calls(self) -> None:
        positions = [
            _mk_position(addr="0x" + "1" * 40, mint_wei=10**18),
            _mk_position(addr="0x" + "2" * 40, mint_wei=0, credit_wei=10**17),
            _mk_position(addr="0x" + "3" * 40, mint_wei=5 * 10**18),
        ]
        token_id_map = {"0x" + "1" * 40: 0, "0x" + "3" * 40: 1}
        batches = create_mint_batches(
            positions, ALCHEMIST, MULTISIG, token_id_map=token_id_map, chain="mainnet",
        )
        total_calls = sum(len(b.calls) for b in batches)
        assert total_calls == 2

    def test_missing_token_id_raises(self) -> None:
        positions = [_mk_position(mint_wei=10**18, addr="0x" + "a" * 40)]
        with pytest.raises(ValueError, match="No token ID"):
            create_mint_batches(
                positions, ALCHEMIST, MULTISIG, token_id_map={}, chain="mainnet",
            )


class TestCreateCreditBatches:
    def test_empty_returns_no_batches(self) -> None:
        assert create_credit_batches([], AL_TOKEN, chain="mainnet") == []

    def test_all_calls_go_to_altoken(self) -> None:
        positions = _mk_positions(5, credit_wei=10**17)
        batches = create_credit_batches(positions, AL_TOKEN, chain="mainnet")
        for b in batches:
            for c in b.calls:
                assert c.to == AL_TOKEN

    def test_under_gas_limit(self) -> None:
        positions = _mk_positions(300, credit_wei=10**17)
        batches = create_credit_batches(positions, AL_TOKEN, chain="mainnet")
        for b in batches:
            assert b.total_gas <= get_effective_gas_limit("mainnet")


class TestCreateTransferBatches:
    def test_transfer_calls_target_nft(self) -> None:
        positions = _mk_positions(3)
        token_id_map = {p.user_address.lower(): i for i, p in enumerate(positions)}
        batches = create_transfer_batches(
            positions, NFT_ADDR, MULTISIG, token_id_map=token_id_map, chain="mainnet",
        )
        for b in batches:
            for c in b.calls:
                assert c.to == NFT_ADDR


# ---------------------------------------------------------------------------
# calculate_batch_statistics / verify_batch_gas_limits / format_batch_summary
# ---------------------------------------------------------------------------


class TestCalculateBatchStatistics:
    def test_empty_list_returns_zeros(self) -> None:
        stats = calculate_batch_statistics([], chain="mainnet")
        assert stats == {
            "total_batches": 0, "total_transactions": 0, "total_gas": 0,
            "avg_gas_per_batch": 0, "max_gas_batch": 0, "min_gas_batch": 0,
            "gas_utilization_percent": 0.0,
        }

    def test_aggregates_over_batches(self, make_batch) -> None:
        b1 = make_batch(n_calls=3, per_call_gas=100_000)
        b2 = make_batch(n_calls=5, per_call_gas=100_000, batch_number=2)
        stats = calculate_batch_statistics([b1, b2], chain="mainnet")
        assert stats["total_batches"] == 2
        assert stats["total_transactions"] == 8
        assert stats["total_gas"] == 800_000
        assert stats["avg_gas_per_batch"] == 400_000
        assert stats["max_gas_batch"] == 500_000
        assert stats["min_gas_batch"] == 300_000


class TestVerifyBatchGasLimits:
    def test_valid_batches_pass(self, make_batch) -> None:
        b = make_batch(n_calls=3, per_call_gas=100_000)
        ok, errors = verify_batch_gas_limits([b], chain="mainnet")
        assert ok is True
        assert errors == []

    def test_batch_over_limit_reported(self) -> None:
        b = TransactionBatch(batch_number=1, batch_type="deposit")
        b.total_gas = 10**10  # absurdly over any chain's limit
        ok, errors = verify_batch_gas_limits([b], chain="mainnet")
        assert ok is False
        assert len(errors) == 1
        assert "exceeds gas limit" in errors[0]


class TestFormatBatchSummary:
    def test_output_mentions_batch_count_and_gas(self, make_batch) -> None:
        batches = [
            make_batch(n_calls=3, per_call_gas=100_000, batch_number=1),
            make_batch(n_calls=2, per_call_gas=200_000, batch_number=2),
        ]
        text = format_batch_summary(batches, chain="mainnet")
        assert "Total batches:" in text
        assert "Total transactions:" in text
        assert "Total gas:" in text


# ---------------------------------------------------------------------------
# Pre-deposit batch builders
# ---------------------------------------------------------------------------


class TestPreDepositBatchBuilders:
    def test_approve_underlying_one_call(self) -> None:
        batches = create_approve_underlying_batches(UNDERLYING, MYT_ADDR, 10**18, chain="mainnet")
        assert len(batches) == 1
        assert len(batches[0].calls) == 1
        assert batches[0].batch_type == "approve_underlying"
        assert batches[0].calls[0].to == UNDERLYING

    def test_myt_deposit_one_call(self) -> None:
        batches = create_myt_deposit_batches(MYT_ADDR, MULTISIG, 10**18, chain="mainnet")
        assert len(batches) == 1
        assert batches[0].batch_type == "deposit_myt"
        assert batches[0].calls[0].to == MYT_ADDR

    def test_approve_myt_one_call(self) -> None:
        batches = create_approve_myt_batches(MYT_ADDR, ALCHEMIST, 10**18, chain="mainnet")
        assert len(batches) == 1
        assert batches[0].batch_type == "approve_myt"
        assert batches[0].calls[0].to == MYT_ADDR

    def test_all_empty_on_zero_amount(self) -> None:
        assert create_approve_underlying_batches(UNDERLYING, MYT_ADDR, 0, "mainnet") == []
        assert create_myt_deposit_batches(MYT_ADDR, MULTISIG, 0, "mainnet") == []
        assert create_approve_myt_batches(MYT_ADDR, ALCHEMIST, 0, "mainnet") == []


# ---------------------------------------------------------------------------
# build_migration_plan top-level
# ---------------------------------------------------------------------------


class TestBuildMigrationPlan:
    def _positions(self) -> list[PositionMigration]:
        return [
            _mk_position(addr="0x" + "1" * 40, deposit_wei=10**18, mint_wei=10**17),
            _mk_position(addr="0x" + "2" * 40, deposit_wei=2 * 10**18, mint_wei=0, credit_wei=10**16),
        ]

    def test_minimal_call_populates_only_4_batch_lists(self) -> None:
        plan = build_migration_plan(
            positions=self._positions(),
            chain="mainnet",
            alchemist_address=ALCHEMIST,
            al_token_address=AL_TOKEN,
            nft_address=NFT_ADDR,
            multisig=MULTISIG,
        )
        assert isinstance(plan, MigrationPlan)
        # Deposit and transfer always populated; mint requires token_id_map; credit populated for credit users.
        assert plan.deposit_batches
        assert plan.transfer_batches
        assert plan.credit_batches
        assert plan.mint_batches == []
        # Pre-deposit lists not populated without myt/underlying.
        assert plan.approve_underlying_batches == []
        assert plan.myt_deposit_batches == []
        assert plan.approve_myt_batches == []

    def test_with_myt_underlying_populates_all_7_batch_lists(self) -> None:
        plan = build_migration_plan(
            positions=self._positions(),
            chain="mainnet",
            alchemist_address=ALCHEMIST,
            al_token_address=AL_TOKEN,
            nft_address=NFT_ADDR,
            multisig=MULTISIG,
            myt_address=MYT_ADDR,
            underlying_address=UNDERLYING,
            underlying_decimals=18,
            myt_decimals=18,
        )
        assert plan.approve_underlying_batches
        assert plan.myt_deposit_batches
        assert plan.approve_myt_batches
        assert plan.deposit_batches
        assert plan.transfer_batches
        assert plan.credit_batches
