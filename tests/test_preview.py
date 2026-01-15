"""Tests for the preview module."""

import pytest

from src.preview import (
    TransactionPreview,
    create_transaction_previews,
    format_address,
    format_batch_header,
    format_batch_totals,
    format_confirmation_prompt,
    format_execution_progress,
    format_final_summary,
    format_gas,
    format_position_summary,
    format_preview_footer,
    format_preview_header,
    format_transaction_line,
    format_wei_to_display,
)
from src.types import PositionMigration, TransactionBatch, TransactionCall


class TestFormatWeiToDisplay:
    """Tests for format_wei_to_display function."""

    def test_zero_value(self):
        """Test zero wei returns '0.0'."""
        assert format_wei_to_display(0) == "0.0"

    def test_one_wei(self):
        """Test one wei displays correctly."""
        result = format_wei_to_display(1)
        # Very small number - might be rounded to 0 or show very small decimal
        assert result == "0" or "0.0" in result

    def test_one_ether(self):
        """Test 1 ETH (10^18 wei) displays as 1."""
        result = format_wei_to_display(10**18)
        assert result == "1"

    def test_large_value_with_decimals(self):
        """Test large value with decimal places."""
        # 1234.567890 ETH
        wei = int(1234.567890 * 10**18)
        result = format_wei_to_display(wei)
        assert "1,234" in result
        assert "5678" in result

    def test_thousands_separator(self):
        """Test that large integer parts have commas."""
        # 1,000,000 tokens
        wei = 1_000_000 * 10**18
        result = format_wei_to_display(wei)
        assert "1,000,000" in result

    def test_trailing_zeros_removed(self):
        """Test that trailing zeros are removed from decimals."""
        # 1.5 ETH - should not show as 1.500000
        wei = int(1.5 * 10**18)
        result = format_wei_to_display(wei)
        assert result == "1.5"


class TestFormatGas:
    """Tests for format_gas function."""

    def test_small_gas(self):
        """Test small gas value."""
        assert format_gas(1000) == "1,000"

    def test_large_gas(self):
        """Test large gas value with commas."""
        assert format_gas(15_200_000) == "15,200,000"

    def test_zero_gas(self):
        """Test zero gas."""
        assert format_gas(0) == "0"


class TestFormatAddress:
    """Tests for format_address function."""

    def test_truncate_address(self):
        """Test address truncation."""
        addr = "0x1234567890123456789012345678901234567890"
        result = format_address(addr, truncate=True)
        assert result == "0x1234...7890"

    def test_full_address(self):
        """Test full address display."""
        addr = "0x1234567890123456789012345678901234567890"
        result = format_address(addr, truncate=False)
        assert result == addr

    def test_empty_address(self):
        """Test empty address returns placeholder."""
        assert format_address("") == "<not configured>"

    def test_none_address(self):
        """Test None-like address returns placeholder."""
        assert format_address(None) == "<not configured>"

    def test_short_address_not_truncated(self):
        """Test short address (non-standard) not truncated."""
        addr = "0x123"
        result = format_address(addr, truncate=True)
        # Short addresses don't match the 42-char check
        assert result == addr


class TestTransactionPreview:
    """Tests for TransactionPreview dataclass."""

    def test_create_preview(self):
        """Test creating a transaction preview."""
        preview = TransactionPreview(
            tx_type="deposit",
            target_address="0x1234567890123456789012345678901234567890",
            user_address="0xabcdef1234567890abcdef1234567890abcdef12",
            amount=1000 * 10**18,
            token_id=5,
            asset_type="USD",
            gas_estimate=150000,
        )
        assert preview.tx_type == "deposit"
        assert preview.token_id == 5
        assert preview.asset_type == "USD"


class TestCreateTransactionPreviews:
    """Tests for create_transaction_previews function."""

    @pytest.fixture
    def sample_positions(self):
        """Create sample positions for testing."""
        return [
            PositionMigration(
                user_address="0x1111111111111111111111111111111111111111",
                asset_type="USD",
                token_id=0,
                deposit_amount=5000 * 10**18,
                mint_amount=1000 * 10**18,
                chain="mainnet",
            ),
            PositionMigration(
                user_address="0x2222222222222222222222222222222222222222",
                asset_type="ETH",
                token_id=0,
                deposit_amount=2 * 10**18,
                mint_amount=1 * 10**18,
                chain="mainnet",
            ),
        ]

    @pytest.fixture
    def sample_chain_config(self):
        """Create sample chain config."""
        return {
            "multisig": "0x3333333333333333333333333333333333333333",
            "cdp_usd": "0x4444444444444444444444444444444444444444",
            "cdp_eth": "0x5555555555555555555555555555555555555555",
            "nft_usd": "0x6666666666666666666666666666666666666666",
            "nft_eth": "0x7777777777777777777777777777777777777777",
        }

    def test_creates_correct_number_of_previews(self, sample_positions, sample_chain_config):
        """Test that 3 previews are created per position."""
        previews = create_transaction_previews(sample_positions, sample_chain_config)
        # 2 positions * 3 tx types = 6 previews
        assert len(previews) == 6

    def test_preview_order(self, sample_positions, sample_chain_config):
        """Test that previews are in correct order: deposits, mints, transfers."""
        previews = create_transaction_previews(sample_positions, sample_chain_config)

        # First 2 should be deposits
        assert previews[0].tx_type == "deposit"
        assert previews[1].tx_type == "deposit"

        # Next 2 should be mints
        assert previews[2].tx_type == "mint"
        assert previews[3].tx_type == "mint"

        # Last 2 should be transfers
        assert previews[4].tx_type == "transfer"
        assert previews[5].tx_type == "transfer"

    def test_correct_contract_addresses(self, sample_positions, sample_chain_config):
        """Test that correct contract addresses are assigned."""
        previews = create_transaction_previews(sample_positions, sample_chain_config)

        # USD deposit should target cdp_usd
        usd_deposit = [p for p in previews if p.tx_type == "deposit" and p.asset_type == "USD"][0]
        assert usd_deposit.target_address == sample_chain_config["cdp_usd"]

        # ETH transfer should target nft_eth
        eth_transfer = [p for p in previews if p.tx_type == "transfer" and p.asset_type == "ETH"][0]
        assert eth_transfer.target_address == sample_chain_config["nft_eth"]

    def test_empty_positions_returns_empty_list(self, sample_chain_config):
        """Test that empty positions list returns empty previews."""
        previews = create_transaction_previews([], sample_chain_config)
        assert previews == []


class TestFormatTransactionLine:
    """Tests for format_transaction_line function."""

    def test_deposit_line(self):
        """Test formatting a deposit transaction line."""
        preview = TransactionPreview(
            tx_type="deposit",
            target_address="0x1234567890123456789012345678901234567890",
            user_address="0xabcdef1234567890abcdef1234567890abcdef12",
            amount=1000 * 10**18,
            token_id=5,
            asset_type="USD",
            gas_estimate=150000,
        )
        result = format_transaction_line(preview, 1)
        assert "deposit" in result
        assert "Token #5" in result
        assert "USD" in result

    def test_transfer_shows_dash_for_amount(self):
        """Test that transfer transactions show dash for amount."""
        preview = TransactionPreview(
            tx_type="transfer",
            target_address="0x1234567890123456789012345678901234567890",
            user_address="0xabcdef1234567890abcdef1234567890abcdef12",
            amount=0,
            token_id=5,
            asset_type="USD",
            gas_estimate=65000,
        )
        result = format_transaction_line(preview, 1)
        assert "transfer" in result
        # The dash should appear somewhere in the amount field
        assert "Amount:" in result and "-" in result


class TestFormatBatchHeader:
    """Tests for format_batch_header function."""

    def test_batch_header_content(self):
        """Test batch header contains expected information."""
        batch = TransactionBatch(batch_number=1)
        batch.add_call(TransactionCall(
            to="0x1234567890123456789012345678901234567890",
            data=b"test",
            gas_estimate=150000,
        ))

        result = format_batch_header(batch, 1)
        assert "Batch 1" in result
        assert "1 transaction" in result


class TestFormatPreviewHeader:
    """Tests for format_preview_header function."""

    def test_preview_header_content(self):
        """Test preview header contains expected information."""
        result = format_preview_header("mainnet", 10)
        assert "MIGRATION PREVIEW" in result
        assert "mainnet" in result
        assert "10" in result


class TestFormatPositionSummary:
    """Tests for format_position_summary function."""

    def test_position_summary_with_both_types(self):
        """Test position summary shows both USD and ETH."""
        result = format_position_summary(
            usd_count=5,
            eth_count=3,
            total_usd_collateral=5000 * 10**18,
            total_eth_collateral=10 * 10**18,
            total_usd_debt=1000 * 10**18,
            total_eth_debt=2 * 10**18,
        )
        assert "USD Positions: " in result
        assert "ETH Positions: " in result
        assert "5" in result
        assert "3" in result

    def test_position_summary_usd_only(self):
        """Test position summary with only USD positions."""
        result = format_position_summary(
            usd_count=5,
            eth_count=0,
            total_usd_collateral=5000 * 10**18,
            total_eth_collateral=0,
            total_usd_debt=1000 * 10**18,
            total_eth_debt=0,
        )
        assert "USD Positions:" in result
        assert "ETH Positions:" not in result


class TestFormatBatchTotals:
    """Tests for format_batch_totals function."""

    def test_batch_totals_with_batches(self):
        """Test batch totals formatting."""
        batch1 = TransactionBatch(batch_number=1)
        batch1.add_call(TransactionCall(
            to="0x1234567890123456789012345678901234567890",
            data=b"test",
            gas_estimate=150000,
        ))
        batch2 = TransactionBatch(batch_number=2)
        batch2.add_call(TransactionCall(
            to="0x1234567890123456789012345678901234567890",
            data=b"test",
            gas_estimate=120000,
        ))

        result = format_batch_totals([batch1, batch2])
        assert "Total Batches:" in result
        assert "Total Transactions:" in result
        assert "Total Gas:" in result

    def test_batch_totals_empty_list(self):
        """Test batch totals with empty list."""
        result = format_batch_totals([])
        assert "Total Batches:" in result
        assert "0" in result


class TestFormatConfirmationPrompt:
    """Tests for format_confirmation_prompt function."""

    def test_confirmation_prompt_content(self):
        """Test confirmation prompt contains expected information."""
        result = format_confirmation_prompt(
            chain="mainnet",
            total_positions=10,
            total_batches=2,
            total_gas=1000000,
        )
        assert "WARNING" in result
        assert "2 transaction" in result
        assert "mainnet" in result
        assert "10 position" in result


class TestFormatExecutionProgress:
    """Tests for format_execution_progress function."""

    def test_progress_without_hash(self):
        """Test progress message without transaction hash."""
        result = format_execution_progress(
            batch_index=1,
            total_batches=5,
            status="Processing...",
        )
        assert "[1/5]" in result
        assert "Processing..." in result

    def test_progress_with_hash(self):
        """Test progress message with transaction hash."""
        result = format_execution_progress(
            batch_index=2,
            total_batches=5,
            status="Completed",
            tx_hash="0x1234567890123456789012345678901234567890",
        )
        assert "[2/5]" in result
        assert "Hash:" in result


class TestFormatFinalSummary:
    """Tests for format_final_summary function."""

    def test_success_summary(self):
        """Test final summary for successful migration."""
        result = format_final_summary(
            chain="mainnet",
            total_positions=10,
            total_batches=2,
            successful_batches=2,
            failed_batches=0,
            batch_results=[
                {"status": "stubbed", "nonce": 0},
                {"status": "stubbed", "nonce": 1},
            ],
        )
        assert "SUCCESS" in result
        assert "mainnet" in result
        assert "10" in result
        assert "2/2" in result

    def test_partial_success_summary(self):
        """Test final summary for partial success."""
        result = format_final_summary(
            chain="mainnet",
            total_positions=10,
            total_batches=2,
            successful_batches=1,
            failed_batches=1,
            batch_results=[
                {"status": "stubbed", "nonce": 0},
                {"status": "error", "nonce": None},
            ],
        )
        assert "PARTIAL SUCCESS" in result

    def test_failed_summary(self):
        """Test final summary for failed migration."""
        result = format_final_summary(
            chain="mainnet",
            total_positions=10,
            total_batches=2,
            successful_batches=0,
            failed_batches=2,
            batch_results=[
                {"status": "error", "nonce": None},
                {"status": "error", "nonce": None},
            ],
        )
        assert "FAILED" in result


class TestFormatPreviewFooter:
    """Tests for format_preview_footer function."""

    def test_footer_returns_string(self):
        """Test that footer returns a string with separator."""
        result = format_preview_footer()
        assert isinstance(result, str)
        assert "=" in result
