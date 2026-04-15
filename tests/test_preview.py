"""Tests for the preview module (V3).

V1 had a `TransactionPreview` dataclass and 12 individual `format_*` helpers.
V3 preview is a single procedural function `print_migration_plan(plan,
chain_config, asset_config, verbose=False)` that prints to click.echo, backed
by private formatters `_fmt_wei`, `_fmt_gas`, `_addr`, `_batch_row`.

Per user direction: test the private formatters directly (they are the actual
correctness surface), plus capsys integration over print_migration_plan for
the rendering pipeline.
"""

from __future__ import annotations

import pytest

from src.preview import _addr, _batch_row, _fmt_gas, _fmt_wei, print_migration_plan
from src.types import (
    AssetType,
    MigrationPlan,
    PositionMigration,
    TransactionBatch,
    TransactionCall,
)


# ---------------------------------------------------------------------------
# Direct formatter tests
# ---------------------------------------------------------------------------


class TestFmtWei:
    def test_zero(self) -> None:
        assert _fmt_wei(0) == "0"

    def test_one_unit(self) -> None:
        assert _fmt_wei(10**18) == "1"

    def test_fractional(self) -> None:
        # 1.5 tokens exactly
        assert _fmt_wei(15 * 10**17) == "1.5"

    def test_trailing_zeros_stripped(self) -> None:
        # 1.500000 would show as "1.5"
        assert _fmt_wei(10**18) == "1"

    def test_large_amount_has_comma_separators(self) -> None:
        # 1,234,567.123456 tokens
        wei = 1_234_567 * 10**18 + 123_456_000_000_000_000
        out = _fmt_wei(wei)
        assert "," in out
        assert "1,234,567" in out

    def test_custom_decimals_scaling(self) -> None:
        # 1 USDC at 6 decimals
        assert _fmt_wei(10**6, decimals=6) == "1"
        assert _fmt_wei(15 * 10**5, decimals=6) == "1.5"


class TestFmtGas:
    def test_commas_inserted(self) -> None:
        assert _fmt_gas(1_000_000) == "1,000,000"

    def test_small_number_no_commas(self) -> None:
        assert _fmt_gas(42) == "42"

    def test_zero(self) -> None:
        assert _fmt_gas(0) == "0"


class TestAddr:
    def test_empty_returns_tbd_style(self) -> None:
        out = _addr("")
        assert "TBD" in out

    def test_zero_address_returns_tbd_style(self) -> None:
        out = _addr("0x" + "0" * 40)
        assert "TBD" in out

    def test_non_zero_returns_short_form(self) -> None:
        addr = "0xAAAABBBBCCCCDDDDEEEEFFFF1111222233334444"
        out = _addr(addr)
        # Should show "0xAAAA...4444" pattern (first 6 + last 4 chars).
        assert "0xAAAA" in out
        assert "4444" in out
        assert "..." in out


class TestBatchRow:
    def _batch(self, gas: int, n_calls: int = 1, number: int = 1, btype: str = "deposit") -> TransactionBatch:
        b = TransactionBatch(batch_number=number, batch_type=btype)
        for i in range(n_calls):
            b.add_call(TransactionCall(to="0x" + "0" * 40, data=b"", gas_estimate=gas // n_calls or 1))
        b.total_gas = gas  # force exact for utilization calc
        return b

    def test_output_contains_batch_number_and_type(self) -> None:
        b = self._batch(gas=1_000_000, n_calls=3, number=7, btype="mint")
        row = _batch_row(b, gas_limit=10_000_000)
        assert "Batch" in row
        assert "7" in row
        assert "mint" in row

    def test_output_contains_txn_count(self) -> None:
        b = self._batch(gas=1_000_000, n_calls=42)
        row = _batch_row(b, gas_limit=10_000_000)
        assert "42" in row

    def test_output_contains_gas_with_commas(self) -> None:
        b = self._batch(gas=1_000_000, n_calls=1)
        row = _batch_row(b, gas_limit=10_000_000)
        assert "1,000,000" in row

    def test_output_contains_utilization_percent(self) -> None:
        b = self._batch(gas=5_000_000, n_calls=1)
        row = _batch_row(b, gas_limit=10_000_000)
        assert "50" in row  # 50% utilization
        assert "%" in row


# ---------------------------------------------------------------------------
# Integration: print_migration_plan via capsys
# ---------------------------------------------------------------------------


def _mk_position(deposit_wei=10**18, mint_wei=0, credit_wei=0, addr="0x1111111111111111111111111111111111111111") -> PositionMigration:
    return PositionMigration(
        user_address=addr,
        asset_type=AssetType.USD,
        chain="mainnet",
        deposit_amount_wei=deposit_wei,
        mint_amount_wei=mint_wei,
        credit_amount_wei=credit_wei,
    )


def _mk_batch(n_calls: int, btype: str, number: int = 1) -> TransactionBatch:
    b = TransactionBatch(batch_number=number, batch_type=btype)
    for i in range(n_calls):
        b.add_call(TransactionCall(
            to="0x" + "0" * 40,
            data=b"\x00" * 36,
            gas_estimate=100_000,
            description=f"call {i}",
        ))
    return b


def _minimal_plan(*, with_pre_deposit: bool = False, verbose_batches: bool = False) -> MigrationPlan:
    plan = MigrationPlan(chain="mainnet", asset_type=AssetType.USD)
    plan.positions = [
        _mk_position(addr="0x" + "1" * 40, mint_wei=10**17),
        _mk_position(addr="0x" + "2" * 40, mint_wei=0, credit_wei=10**16),
    ]
    plan.deposit_batches = [_mk_batch(3, "deposit")]
    plan.transfer_batches = [_mk_batch(2, "transfer")]
    plan.credit_batches = [_mk_batch(1, "credit")]
    if with_pre_deposit:
        plan.approve_underlying_batches = [_mk_batch(1, "approve_underlying")]
        plan.myt_deposit_batches = [_mk_batch(1, "deposit_myt")]
        plan.approve_myt_batches = [_mk_batch(1, "approve_myt")]
    return plan


CHAIN_CONFIG = {
    "chain_id": 1,
    "multisig": "0xABCD567890abcdef1234567890abcdef12345678",
    "usd": {},
    "eth": {},
}
ASSET_CONFIG = {
    "alchemist": "0x1111222233334444555566667777888899990000",
    "al_token": "0xAAAAAAAABBBBBBBBCCCCCCCCDDDDDDDDEEEEEEEE",
    "myt": "0x9999888877776666555544443333222211110000",
    "underlying": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "nft": "0x5555666677778888999900001111222233334444",
    "myt_decimals": 18,
}


class TestPrintMigrationPlanIntegration:
    def test_every_section_header_rendered(self, capsys) -> None:
        plan = _minimal_plan(with_pre_deposit=True)
        print_migration_plan(plan, CHAIN_CONFIG, ASSET_CONFIG)
        out = capsys.readouterr().out
        assert "MIGRATION PLAN" in out
        assert "Position Summary" in out
        assert "Phase A" in out
        assert "Phase B" in out
        assert "Phase C" in out
        assert "Phase D" in out
        assert "Phase 1 — Alchemist deposit" in out
        assert "Phase 2 — Mint" in out
        assert "Phase 3 — Verify" in out
        assert "Phase 4 — Distribute NFTs" in out
        assert "Phase 5 — Credit" in out
        assert "Totals" in out

    def test_empty_pre_deposit_sections_render_as_none(self, capsys) -> None:
        """Without myt/underlying, pre-deposit lists are empty — preview must not crash."""
        plan = _minimal_plan(with_pre_deposit=False)
        print_migration_plan(plan, CHAIN_CONFIG, ASSET_CONFIG)
        out = capsys.readouterr().out
        assert "(none)" in out  # at least the pre-deposit and mint sections
        assert "Phase A" in out

    def test_totals_count_all_batch_lists(self, capsys) -> None:
        plan = _minimal_plan(with_pre_deposit=True)
        print_migration_plan(plan, CHAIN_CONFIG, ASSET_CONFIG)
        out = capsys.readouterr().out
        # Deposit=1, transfer=2 batches total, credit=1, pre-deposit=1+1+1.
        # Check the individual totals lines are printed.
        assert "ApproveUnderlying:" in out
        assert "DepositMYT:" in out
        assert "ApproveMYT:" in out
        assert "Deposit batches:" in out
        assert "Transfer batches:" in out
        assert "Credit batches:" in out

    def test_multisig_address_shown_in_short_form(self, capsys) -> None:
        plan = _minimal_plan()
        print_migration_plan(plan, CHAIN_CONFIG, ASSET_CONFIG)
        out = capsys.readouterr().out
        # Addr format: 0xABCD...5678
        assert "0xABCD" in out

    def test_verbose_mode_prints_call_descriptions(self, capsys) -> None:
        plan = _minimal_plan()
        print_migration_plan(plan, CHAIN_CONFIG, ASSET_CONFIG, verbose=True)
        out = capsys.readouterr().out
        # Non-verbose wouldn't include call descriptions; verbose should.
        assert "call 0" in out

    def test_tbd_shown_for_empty_multisig(self, capsys) -> None:
        chain_with_empty_multisig = {**CHAIN_CONFIG, "multisig": ""}
        plan = _minimal_plan()
        print_migration_plan(plan, chain_with_empty_multisig, ASSET_CONFIG)
        out = capsys.readouterr().out
        assert "TBD" in out
