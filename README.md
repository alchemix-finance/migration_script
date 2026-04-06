# Alchemix V2 → V3 Migration Script

Python tooling for migrating Alchemix V2 CDP positions to V3 architecture. Reads position snapshots from CSV files, encodes the required V3 contract calls, batches them by gas budget, and proposes each batch as a Gnosis Safe multisig transaction.

---

## How it works

V2 positions cannot be migrated in-place. The protocol must:

1. Read a snapshot of all V2 positions (address, collateral, net debt) from a CSV.
2. For each user, recreate their position in V3: deposit collateral as MYT shares, mint their debt as alAssets.
3. Distribute alAssets to users who had a credit balance (the protocol owed them).
4. Burn the alAssets held by the multisig against each debt position to clear it.
5. Transfer each position NFT to its original user.

All transactions are proposed to a Gnosis Safe multisig. No private key is ever used directly — Safe signers approve and execute.

---

## Architecture

```
migration_script/
├── ape-config.yaml               # Apeworx project config (networks, plugins)
├── contracts/
│   ├── alchemist_abi.json        # AlchemistV3 ABI: setDepositCap, deposit, mint, burn
│   ├── altoken_abi.json          # alToken ABI: transfer
│   └── erc721_abi.json           # ERC721 ABI: transferFrom (for NFT position transfer)
├── data/
│   ├── alUSDValues-sum-and-debt-mainnet.csv
│   ├── alETHValues-sum-and-debt-mainnet.csv
│   └── ...                       # One file per asset × chain
├── scripts/
│   ├── migrate.py                # Main entry point — full migration run
│   ├── batch.py                  # Show batch statistics only (no submission)
│   ├── preview.py                # Human-readable plan preview
│   └── validate.py               # CSV-only validation
├── src/
│   ├── abi.py                    # ABI file loading
│   ├── config.py                 # Chain/asset addresses and gas constants
│   ├── gas.py                    # Batch creation and gas bin-packing
│   ├── preview.py                # Formatted plan display
│   ├── safe.py                   # Gnosis Safe encoding and API client
│   ├── transactions.py           # Per-operation calldata builders
│   ├── types.py                  # Data models (CSVRow, PositionMigration, etc.)
│   └── validation.py             # CSV parsing and validation
└── tests/                        # pytest test suite
```

---

## Prerequisites

- Python 3.11+
- [Apeworx](https://docs.apeworx.io/) (`pip install eth-ape`)
- Ape plugins: `ape plugins install alchemy etherscan`
- Access to an Alchemy RPC endpoint for each chain
- The migration multisig address set as an **admin** on each AlchemistV3 contract before running

---

## Installation

```bash
git clone https://github.com/alchemix-finance/migration_script
cd migration_script
pip install eth-ape
ape plugins install alchemy etherscan
```

---

## Configuration

Before running, fill in all contract addresses in `src/config.py`:

```python
CHAINS = {
    "mainnet": {
        "chain_id": 1,
        "multisig": "0xF56D660138815fC5d7a06cd0E1630225E788293D",  # ← already set
        "usd": {
            "alchemist": "",    # AlchemistV3 for alUSD — fill in after deployment
            "myt":        "",   # USDC MYT vault token address
            "al_token":   "",   # alUSD token address
            "underlying": "",   # USDC address
        },
        "eth": {
            "alchemist": "",    # AlchemistV3 for alETH — fill in after deployment
            "myt":        "",   # WETH MYT vault token address
            "al_token":   "",   # alETH token address
            "underlying": "",   # WETH address
        },
    },
    ...
}
```

> **Note:** The NFT contract address (`AlchemistV3Position`) is read from
> `alchemist.alchemistPositionNFT()` on-chain. It is **not** the same address as the
> `AlchemistV3` contract. See [Bug #1](#known-bugs-to-fix-before-production) below.

---

## CSV Format

One CSV per asset per chain. File naming convention:

```
data/alUSDValues-sum-and-debt-{chain}.csv
data/alETHValues-sum-and-debt-{chain}.csv
```

Schema:

```csv
address,underlyingValue,debt
0xAAA...,5000.00,1000.50
0xBBB...,15000.00,3000.00
0xCCC...,2000.00,-250.00
0xDDD...,8000.00,0
```

| Column | Type | Description |
|--------|------|-------------|
| `address` | `0x...` (42 chars) | User's Ethereum address |
| `underlyingValue` | decimal ≥ 0 | Collateral in MYT shares at migration time |
| `debt` | decimal | Positive = user owes alAssets. Negative = protocol owes user alAssets (credit balance). Zero = collateral-only position. |

Rules:
- One row per user per asset. A user with both alUSD and alETH positions appears in two separate files.
- Duplicate addresses within a file are rejected.
- Rows with `underlyingValue = 0` are rejected (users with no collateral are not migrated).
- A row cannot have both positive debt and negative debt simultaneously.

> **Decimal precision:** Values are converted to wei using 18 decimal places by default.
> For USDC-backed positions (6 decimals), ensure CSV values are already in MYT share
> units (18-decimal) rather than raw USDC units. See [Bug #4](#known-bugs-to-fix-before-production).

---

## Migration Flow

The migration proceeds in four phases per asset per chain. Each phase becomes one or more Safe multisig transactions, batched to stay under ~14.4M gas (90% of the 16M block gas limit).

```
Phase 1 — Deposit + Mint
  For each user:
    setDepositCap(currentCap + batchDepositSum)
    deposit(myt_shares, multisig, tokenId=0)   → mints new NFT, emits AlchemistV3PositionNFTMinted
    mint(tokenId, debt_amount, multisig)?       → if debt > 0, mints alAssets to multisig

Phase 2 — Credit Distribution
  For each credit user:
    alToken.transfer(user_address, credit_amount)  → sends alAssets from multisig to user

Phase 3 — Burn Debt
  For each debt user:
    alchemist.burn(debt_amount, tokenId)           → burns alAssets from multisig, clears position debt
    ⚠ Token IDs are PLACEHOLDERS — must be patched first (see below)

Phase 4 — NFT Transfer
  For each user:
    ERC721.transferFrom(multisig, user_address, tokenId)
    ⚠ Token IDs are PLACEHOLDERS — must be patched first (see below)
```

### Token ID Patching (Critical Manual Step)

Token IDs are assigned by the AlchemistV3 contract on-chain at deposit time. They are not predictable before Phase 1 executes. The script uses `999999` as a placeholder in Phase 3 and Phase 4 calldata.

**After Phase 1 executes:**

1. Query all `AlchemistV3PositionNFTMinted(address indexed to, uint256 indexed tokenId)` events from the Phase 1 transactions.
2. Match each event's `to` address (the multisig) and `tokenId` to the corresponding user by deposit order.
3. Replace every `999999` placeholder in the Phase 3 (burn) and Phase 4 (transfer) batches with the real tokenId.
4. Re-verify the patched calldata before signing and submitting Phase 3 and Phase 4.

> There is currently no automated tooling for this step. It must be done manually or via a separate script before Phase 3 and Phase 4 are proposed to Safe.

---

## Commands

### Validate CSV only

```bash
ape run validate --chain mainnet --asset usd
ape run validate --chain mainnet --asset eth
```

### Preview batch plan (no transactions submitted)

```bash
ape run batch --chain mainnet --asset usd
ape run batch --chain mainnet --asset usd --verbose
```

### Full dry run (builds plan, no Safe proposals)

```bash
ape run migrate --chain mainnet --asset usd --dry-run
ape run migrate --chain mainnet --asset eth --dry-run --verbose
```

### Execute migration

```bash
# USD positions on mainnet
ape run migrate --chain mainnet --asset usd

# With auto-confirm (no interactive prompt)
ape run migrate --chain mainnet --asset usd --yes

# ETH positions
ape run migrate --chain mainnet --asset eth
```

Chains: `mainnet`, `optimism`, `arbitrum`

---

## V3 Contract Interface Reference

All calldata is encoded against these verified v3 signatures (confirmed against `y-monorepo` branch):

| Function | Signature | Access |
|----------|-----------|--------|
| `setDepositCap` | `setDepositCap(uint256 value)` | `onlyAdmin` |
| `deposit` | `deposit(uint256 amount, address recipient, uint256 tokenId) → (uint256 tokenId, uint256 debtValue)` | open |
| `mint` | `mint(uint256 tokenId, uint256 amount, address recipient)` | NFT owner |
| `burn` | `burn(uint256 amount, uint256 recipientId) → uint256` | open (burns caller's alAssets) |
| `transferFrom` (NFT) | `transferFrom(address from, address to, uint256 tokenId)` | ERC721 standard |
| `alToken.transfer` | `transfer(address to, uint256 amount) → bool` | ERC20 standard |

Key behaviors:
- `deposit(amount, recipient, 0)` — passing `tokenId=0` creates a new position and mints the NFT to `recipient`. The actual tokenId is emitted in `AlchemistV3PositionNFTMinted`.
- `mint(tokenId, amount, multisig)` — `msg.sender` must be the NFT owner (multisig during migration). alAssets land in the multisig, not the user.
- `burn(amount, tokenId)` — burns alAssets held by `msg.sender` (multisig) against a specific position's unearmarked debt. Cannot be called in the same block as `mint`.
- `setDepositCap` — requires multisig to be set as admin on each AlchemistV3 before the migration starts.

---

## Gas Budget

| Operation | Gas estimate |
|-----------|-------------|
| `setDepositCap` | 35,000 |
| `deposit` (new position) | 175,000 |
| `deposit` (large, > 10²¹ wei) | 190,000 |
| `mint` | 130,000 |
| `mint` (large) | 145,000 |
| `burn` | 120,000 |
| `alToken.transfer` | 65,000 |
| `ERC721.transferFrom` | 70,000 |

Batches target 90% of 16M gas = **14,400,000 gas** per Safe transaction.

---

## Known Bugs to Fix Before Production

The following issues were identified during code review against the v3 contracts. **None of these will cause data loss** (all failures are reverts), but they will cause the migration to halt partway through.

### Bug #1 — NFT address is wrong (Phase 4 will fail entirely)

**File:** `migrate.py:142`, `batch.py:59`

```python
# Current (WRONG):
nft = alchemist  # "same as alchemist for now"

# Fix:
from web3 import Web3
w3 = Web3(...)
alchemist_contract = w3.eth.contract(address=alchemist, abi=ALCHEMIST_ABI)
nft = alchemist_contract.functions.alchemistPositionNFT().call()
```

`AlchemistV3Position` is a **separate ERC721 contract** from `AlchemistV3`. Sending `transferFrom` to the alchemist address will revert because `AlchemistV3` has no `transferFrom` method. Phase 4 will fail 100% of the time without this fix.

### Bug #2 — alAsset balance math is wrong (Phase 3 will run short)

**File:** `gas.py:create_burn_batches`

Phase 1 mints `total_mint_wei` alAssets into the multisig.
Phase 2 sends `total_credit_wei` of those alAssets to credit users.
Phase 3 then tries to burn `total_mint_wei` — but the multisig only holds `total_mint_wei − total_credit_wei`.

**Shortfall = `total_credit_wei`**. If any credit users exist, Phase 3 burn calls will fail for the last `total_credit_wei` worth of positions.

Fix options:
- **Option A (recommended):** Add an extra Phase 1 deposit+mint for `total_credit_wei` into a dedicated "protocol reserve" NFT position, then burn it in Phase 3.
- **Option B:** Reduce each debt user's burn amount proportionally to keep total burns ≤ available balance (leaves residual debt on some positions, not recommended).

### Bug #3 — `deposit()` ABI return type is wrong (cosmetic, no runtime failure)

**File:** `contracts/alchemist_abi.json`

The ABI declares `deposit` as returning `[uint256]` (one value). The actual contract returns `(uint256 tokenId, uint256 debtValue)` — a two-element tuple. Since the script never reads the deposit return value (it uses event logs instead), this causes no runtime error, but the ABI is technically incorrect and would break any code that tries to decode the return.

Fix: update the ABI outputs to `[{"name": "tokenId", "type": "uint256"}, {"name": "debtValue", "type": "uint256"}]`.

### Bug #4 — USDC token decimals hardcoded to 18

**File:** `validation.py:position_from_row`, `validate_csv_file`

`convert_to_wei` uses `token_decimals=18` by default. If `underlyingValue` in the CSV represents USDC amounts (6 decimals) rather than MYT shares (18 decimals), USD position deposits will be 10¹² times larger than intended, causing immediate revert from the deposit cap check.

Verify that all CSV `underlyingValue` figures are in MYT share units (18-decimal), or add a per-asset `token_decimals` parameter to the config and pass `6` for USD-backed assets.

### Bug #5 — `burn()` only clears unearmarked debt

**File:** `AlchemistV3.sol:526` (contract constraint, not a script bug)

```solidity
_checkState((debt = _accounts[recipientId].debt - _accounts[recipientId].earmarked) > 0);
```

If significant time passes between Phase 1 (mint) and Phase 3 (burn), the Transmuter may have earmarked some debt. If all of a position's debt is earmarked, `burn()` reverts. With a fresh V3 deployment and rapid execution of all phases, earmarked amounts should be zero. This is a timing risk, not a hard bug, but phases should be executed without extended delays.

### Bug #6 — Safe nonce stub always returns 0

**File:** `safe.py:ProposeToSafe.get_next_nonce`

```python
def get_next_nonce(self) -> int:
    return 0  # STUB
```

Every batch will be proposed with nonce `0`. The Safe Transaction Service will accept only the first; all subsequent proposals with nonce `0` will be rejected. This must be replaced with a real API call before any production use:

```python
# GET https://safe-transaction-{chain}.safe.global/api/v1/safes/{safe_address}/
# Response: { "nonce": N }
```

### Bug #7 — Test suite tests a deleted API

**File:** `tests/test_transactions.py`

The tests import `load_cdp_abi`, `build_position_transactions`, `build_transfer_tx`, and `_create_deposit_call` — functions that were removed during the v2→v3 refactor. Running `pytest` fails immediately. The test suite needs to be rewritten against the current API (`load_alchemist_abi`, `build_nft_transfer_tx`, etc.).

---

## Pre-Migration Checklist

- [ ] All AlchemistV3 contracts deployed and addresses filled into `src/config.py`
- [ ] Migration multisig set as `admin` on each AlchemistV3 (`setAdmin(multisig)`)
- [ ] Multisig funded with enough MYT shares to cover total deposit amounts (or pre-approved)
- [ ] Bug #1 fixed: NFT address resolved from `alchemist.alchemistPositionNFT()`
- [ ] Bug #2 fixed: alAsset balance math accounts for credit distributions
- [ ] Bug #4 confirmed: CSV values are in MYT share units (18-decimal) not raw USDC
- [ ] Bug #6 fixed: Safe nonce fetched from Safe Transaction Service API
- [ ] Dry run passes on all chains and assets: `ape run migrate --dry-run`
- [ ] Team has a plan for patching token IDs from Phase 1 events before Phase 3/4

---

## Running Tests

```bash
pip install pytest eth-ape
pytest tests/ -v
```

> **Note:** The test suite currently fails due to Bug #7 above (stale imports). Fix the tests before running on the current codebase.

---

## Chains Supported

| Chain | Chain ID | Multisig |
|-------|----------|----------|
| Ethereum Mainnet | 1 | `0xF56D660138815fC5d7a06cd0E1630225E788293D` |
| Optimism | 10 | `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d` |
| Arbitrum One | 42161 | `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b` |

---

## Security Notes

- The migration multisig temporarily holds all position NFTs and all minted alAssets. It must be a properly secured multi-signature wallet with a threshold high enough to prevent unilateral action.
- Phase 4 (NFT transfers to users) should only be executed **after team verification** that Phase 1, 2, and 3 have completed correctly.
- Token ID placeholder `999999` is intentionally invalid — any accidentally submitted Phase 3 or Phase 4 batch with unpatched IDs will revert on-chain.
- The `ProposeToSafe` API is currently stubbed. No transactions will actually be sent to the Safe Transaction Service without completing Bug #6.
