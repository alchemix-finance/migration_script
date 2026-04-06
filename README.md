# Alchemix V2 → V3 Migration Script

Python tooling for migrating Alchemix V2 CDP positions to V3 architecture. Reads position snapshots from CSV files, encodes the required V3 contract calls, batches them by gas budget, and proposes each batch as a Gnosis Safe multisig transaction.

---

## How it works

V2 positions cannot be migrated in-place. The protocol must:

1. Read a snapshot of all V2 positions (address, collateral, net debt) from a CSV.
2. For each user, recreate their position in V3: deposit collateral as MYT shares, mint their debt as alAssets into the multisig.
3. Team verifies all on-chain positions match the snapshot.
4. Distribute alAssets to users who had a credit balance (the protocol owed them).
5. Transfer each position NFT to its original user.
6. Burn the remaining alAssets held by the multisig directly on the alToken contract.

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
│   ├── phase1.py                 # Script 1 — deposit + mint (run first)
│   ├── phase2.py                 # Script 2 — credits + NFT transfers + burn (run after verification)
│   ├── migrate.py                # Preview both phases combined (no submission)
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
            "nft":        "",   # AlchemistV3Position — read from alchemist.alchemistPositionNFT()
        },
        "eth": {
            "alchemist": "",    # AlchemistV3 for alETH — fill in after deployment
            "myt":        "",   # WETH MYT vault token address
            "al_token":   "",   # alETH token address
            "underlying": "",   # WETH address
            "nft":        "",   # AlchemistV3Position — read from alchemist.alchemistPositionNFT()
        },
    },
    ...
}
```

> **Note:** The NFT contract address (`AlchemistV3Position`) is a **separate contract** from `AlchemistV3`. Read it from `alchemist.alchemistPositionNFT()` after deployment and set it in the config before running.

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
0xAAA...,1000000000000000000,1000500000000000000
0xBBB...,15000000000000000000,3000000000000000000
0xCCC...,2000000000000000000,-250000000000000000
0xDDD...,8000000000000000000,0
```

| Column | Type | Description |
|--------|------|-------------|
| `address` | `0x...` (42 chars) | User's Ethereum address |
| `underlyingValue` | integer (wei) | Collateral in MYT shares at migration time |
| `debt` | integer (wei) | Positive = user owes alAssets. Negative = protocol owes user alAssets (credit balance). Zero = collateral-only position. |

Rules:
- One row per user per asset. A user with both alUSD and alETH positions appears in two separate files.
- Duplicate addresses within a file are rejected.
- Rows with `underlyingValue = 0` are rejected (users with no collateral are not migrated).
- Values must be plain integers in wei — no scientific notation, no decimals.

> **Decimal precision:** Both USDCMYT and WETHMYT are standard 18-decimal ERC-4626 vault tokens. All values in the CSV are already in 18-decimal atomic units — no rescaling is applied.

---

## Migration Flow

The migration runs as **two scripts** per asset per chain. Each script produces one or more Safe multisig transactions, batched to stay under ~14.4M gas (90% of the 16M block gas limit).

```
Script 1 — Deposit + Mint  (phase1.py)
  For each user:
    setDepositCap(currentCap + batchDepositSum)
    deposit(myt_shares, multisig, tokenId=0)       → mints NFT, emits AlchemistV3PositionNFTMinted
    mint(tokenId, mint_amount, multisig)?           → if user has debt or credit, mints alAssets to multisig

  After Script 1: team verifies all on-chain positions match snapshot data.

Script 2 — Distribute + Burn  (phase2.py)
  Credit distribution:
    alToken.transfer(user_address, credit_amount)  → for each credit user

  NFT transfers:
    ERC721.transferFrom(multisig, user_address, tokenId)   → for all users
    ⚠ Token IDs are PLACEHOLDERS — must be patched first (see below)

  Final burn:
    alToken.burn(remaining_balance)                → burns leftover alAssets on the alToken contract directly
    (fallback: alToken.transfer(0x000...000, remaining_balance) via --burn-fallback flag)
```

**What ends up where:**
- Debt users receive their NFT with debt equal to their V2 debt. The corresponding alTokens minted by the multisig are burned in the final burn step.
- Credit users receive their NFT and a direct alToken transfer equal to their credit. They can use those tokens to repay their position debt themselves.

### Token ID Patching (Critical Manual Step)

Token IDs are assigned by the AlchemistV3 contract on-chain at deposit time. They are not predictable before Script 1 executes. The script uses `999999` as a placeholder in the Script 2 transfer batch calldata.

**After Script 1 executes:**

1. Query all `AlchemistV3PositionNFTMinted(address indexed to, uint256 indexed tokenId)` events from the Script 1 transactions.
2. Match each event's `to` address (the multisig) and `tokenId` to the corresponding user by deposit order.
3. Replace every `999999` placeholder in the Script 2 transfer batches with the real tokenId.
4. Re-verify the patched calldata before signing and submitting Script 2.

> There is currently no automated tooling for this step. It must be done manually or via a separate script before Script 2 is proposed to Safe.

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
ape run migrate --chain mainnet --asset usd        # combined preview of both scripts
```

### Script 1 — Deposit + Mint

```bash
# Dry run first
ape run phase1 --chain mainnet --asset usd --dry-run

# Execute (auto-confirm)
ape run phase1 --chain mainnet --asset usd --yes
```

### Script 2 — Distribute + Burn

Run only after Script 1 is complete and team has verified on-chain positions.

```bash
# Dry run first
ape run phase2 --chain mainnet --asset usd --dry-run

# Execute
ape run phase2 --chain mainnet --asset usd --yes

# If alToken.burn() is unavailable, fall back to transfer to zero address
ape run phase2 --chain mainnet --asset usd --yes --burn-fallback
```

Chains: `mainnet`, `optimism`, `arbitrum`

---

## V3 Contract Interface Reference

All calldata is encoded against these verified v3 signatures (confirmed against `y-monorepo` branch):

| Contract | Function | Signature | Access |
|----------|----------|-----------|--------|
| AlchemistV3 | `setDepositCap` | `setDepositCap(uint256 value)` | `onlyAdmin` |
| AlchemistV3 | `deposit` | `deposit(uint256 amount, address recipient, uint256 tokenId) → (uint256 tokenId, uint256 debtValue)` | open |
| AlchemistV3 | `mint` | `mint(uint256 tokenId, uint256 amount, address recipient)` | NFT owner |
| AlchemistV3Position | `transferFrom` | `transferFrom(address from, address to, uint256 tokenId)` | ERC721 standard |
| alToken | `transfer` | `transfer(address to, uint256 amount) → bool` | ERC20 standard |
| alToken | `burn` | `burn(uint256 amount) → bool` | ERC20Burnable — any holder |

Key behaviors:
- `deposit(amount, recipient, 0)` — passing `tokenId=0` creates a new position and mints the NFT to `recipient`. The actual tokenId is emitted in `AlchemistV3PositionNFTMinted`.
- `mint(tokenId, amount, multisig)` — `msg.sender` must be the NFT owner (multisig during migration). alAssets land in the multisig, not the user.
- `alToken.burn(amount)` — burns alAssets held by the caller (multisig) directly on the alToken contract. Does NOT interact with AlchemistV3 and does not affect position debt. Used in Script 2 to destroy the leftover alAssets minted for debt users.
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
| `alToken.transfer` (credit) | 65,000 |
| `ERC721.transferFrom` | 70,000 |
| `alToken.burn` (final burn) | 35,000 |

Batches target 90% of 16M gas = **14,400,000 gas** per Safe transaction.

---

## Pre-Migration Checklist

- [ ] All AlchemistV3 contracts deployed and addresses filled into `src/config.py`
- [ ] `nft` address set in each asset config (read from `alchemist.alchemistPositionNFT()`)
- [ ] Migration multisig set as `admin` on each AlchemistV3 (`setAdmin(multisig)`)
- [ ] Multisig funded with enough MYT shares to cover total deposit amounts (or pre-approved)
- [ ] Dry run passes on all chains and assets: `ape run phase1 --dry-run` and `ape run phase2 --dry-run`
- [ ] Team has a plan for patching token IDs from Script 1 events before Script 2 NFT transfers
- [ ] Script 2 is not submitted until Script 1 is fully confirmed and positions are verified on-chain

---

## Running Tests

```bash
pip install pytest eth-ape
pytest tests/ -v
```

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
- Script 2 (NFT transfers and burn) should only be executed **after team verification** that Script 1 has completed correctly and all on-chain positions match the snapshot data.
- Token ID placeholder `999999` is intentionally invalid — any accidentally submitted Script 2 transfer batch with unpatched IDs will revert on-chain.
- `alToken.burn()` does not interact with AlchemistV3 and does not clear position debt. Debt user positions will carry their V2 debt on the NFT after migration. This is intentional — the burned alTokens are the supply side; the debt side lives on the user's position.
