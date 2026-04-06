# Alchemix V2 → V3 Migration Script

Python tooling for migrating Alchemix V2 CDP positions to V3 architecture. Reads position snapshots from CSV files, encodes the required V3 contract calls, batches them within per-chain gas and size limits, and proposes each batch as a Gnosis Safe multisig transaction.

---

## How it works

V2 positions cannot be migrated in-place. The protocol must:

1. Read a snapshot of all V2 positions (address, collateral, net debt) from a CSV.
2. For each user, deposit collateral as MYT shares into V3 (creates NFT positions).
3. Read the on-chain token IDs assigned to each position.
4. Mint alAssets against each debt user's position.
5. Team verifies all positions match the snapshot.
6. Transfer each position NFT to its original user.
7. Send alAsset credit to users the protocol owed (negative debt in V2).
8. Multisig burns remaining alAssets manually.

All transactions are proposed to a Gnosis Safe multisig. No private key is ever used directly — Safe signers approve and execute.

---

## Architecture

```
migration_script/
├── ape-config.yaml               # Apeworx project config (networks, plugins)
├── contracts/
│   ├── alchemist_abi.json        # AlchemistV3 ABI: setDepositCap, deposit, mint
│   ├── altoken_abi.json          # alToken ABI: transfer, burn
│   └── erc721_abi.json           # ERC721 ABI: transferFrom
├── data/
│   ├── alUSDValues-sum-and-debt-mainnet.csv
│   ├── alETHValues-sum-and-debt-mainnet.csv
│   ├── token_ids-alUSD-mainnet.json   # Written by read_ids.py
│   └── ...                       # One CSV per asset × chain
├── scripts/
│   ├── deposit.py                # Step 1 — deposit MYT, create NFT positions
│   ├── read_ids.py               # Step 2 — read token IDs from deposit events
│   ├── mint.py                   # Step 3 — mint alAsset debt using real token IDs
│   ├── verify.py                 # Step 4 — verify positions match snapshot
│   ├── distribute.py             # Step 5 — transfer NFTs to users
│   ├── credit.py                 # Step 6 — send alAsset credit to credit users
│   ├── migrate.py                # Preview all steps (no submission)
│   ├── batch.py                  # Batch statistics (no submission)
│   ├── preview.py                # Human-readable plan preview
│   └── validate.py               # CSV-only validation
├── src/
│   ├── abi.py                    # ABI file loading
│   ├── config.py                 # Chain/asset addresses, per-chain gas limits
│   ├── gas.py                    # Batch creation with gas + size + call-count limits
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
        ...
    },
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
| `debt` | integer (wei) | Positive = user owes alAssets. Negative = protocol owes user alAssets (credit). Zero = collateral-only. |

Rules:
- One row per user per asset. A user with both alUSD and alETH positions appears in two separate files.
- Duplicate addresses within a file are rejected.
- Rows with `underlyingValue = 0` are rejected (users with no collateral are not migrated).
- Values must be plain integers in wei — no scientific notation, no decimals.

> **Decimal precision:** Both USDCMYT and WETHMYT are standard 18-decimal ERC-4626 vault tokens. All values in the CSV are already in 18-decimal atomic units — no rescaling is applied.

---

## Migration Flow

The migration runs in **5 steps** per asset per chain. Each step targets ~50 calls per Safe batch, constrained by 90% of each chain's block gas limit and transaction size limit.

```
Step 1 — Deposit  (deposit.py)
  For each user:
    setDepositCap(currentCap + batchDepositSum)
    deposit(myt_shares, multisig, tokenId=0)       → creates NFT

Step 2 — Read Token IDs + Mint  (read_ids.py + mint.py)
  read_ids: queries NFT Transfer(from=0x0, to=multisig) events → token_ids JSON
  mint: for each DEBT user (not credit users):
    mint(tokenId, debt_amount, multisig)           → mints alAssets to multisig

Step 3 — Verify  (verify.py)
  Checks all positions match snapshot:
    - Every position has a token ID
    - Debt users have correct mint amounts
    - Credit users have ZERO debt (no mint was done against their position)
    - total_mint >= total_credit (enough alAssets to cover credit distribution)

Step 4 — Distribute NFTs  (distribute.py)
  For each user:
    ERC721.transferFrom(multisig, user, tokenId)

Step 5 — Credit Distribution  (credit.py)
  For each credit user:
    alToken.transfer(user, credit_amount)

Burn — manual by multisig after all steps complete.
```

**Why deposits and mints are separate:**
`mint(tokenId, ...)` requires the real tokenId assigned by the contract at deposit time. MultiSend can't chain return values between calls, so we must deposit first, read the assigned tokenIds from events, then mint in a separate step.

**Credit user handling:**
Credit users (negative debt in V2) receive only a deposit — no mint against their position, so they have **zero debt** in V3. Their alAsset credit is distributed separately from the pool of alAssets minted for debt users. The multisig burns leftover alAssets manually after all steps complete.

---

## Commands

### Validate CSV only

```bash
ape run validate --chain mainnet --asset usd
```

### Preview full plan (no transactions submitted)

```bash
ape run migrate --chain mainnet --asset usd --verbose
ape run batch --chain mainnet --asset usd
```

### Step 1 — Deposit

```bash
ape run deposit --chain mainnet --asset usd --dry-run
ape run deposit --chain mainnet --asset usd --yes
```

### Step 2 — Read token IDs + Mint

```bash
ape run read_ids --chain mainnet --asset usd --from-block 12345678
ape run mint --chain mainnet --asset usd --dry-run
ape run mint --chain mainnet --asset usd --yes
```

### Step 3 — Verify

```bash
ape run verify --chain mainnet --asset usd
```

### Step 4 — Distribute NFTs

```bash
ape run distribute --chain mainnet --asset usd --dry-run
ape run distribute --chain mainnet --asset usd --yes
```

### Step 5 — Credit

```bash
ape run credit --chain mainnet --asset usd --dry-run
ape run credit --chain mainnet --asset usd --yes
```

Chains: `mainnet`, `optimism`, `arbitrum`

---

## Per-Chain Limits

Batches are constrained by three limits (whichever is hit first):

| Chain | Block Gas Limit | Max TX Size | Effective Gas (90%) | Max Calls/Batch |
|-------|----------------|-------------|--------------------:|----------------:|
| Ethereum Mainnet | 60M | 128 KB | 54,000,000 | 50 |
| Optimism | 30M | 120 KB | 27,000,000 | 50 |
| Arbitrum One | 32M | 118 KB | 28,800,000 | 50 |

At 50 calls per batch with typical gas costs (~175K per deposit, ~130K per mint, ~70K per transfer), gas utilization is 15-30% per batch. The 50-call limit keeps batches reviewable in the Safe UI.

---

## V3 Contract Interface Reference

| Contract | Function | Signature | Access |
|----------|----------|-----------|--------|
| AlchemistV3 | `setDepositCap` | `setDepositCap(uint256 value)` | `onlyAdmin` |
| AlchemistV3 | `deposit` | `deposit(uint256 amount, address recipient, uint256 tokenId)` | open |
| AlchemistV3 | `mint` | `mint(uint256 tokenId, uint256 amount, address recipient)` | NFT owner |
| AlchemistV3Position | `transferFrom` | `transferFrom(address from, address to, uint256 tokenId)` | ERC721 |
| alToken | `transfer` | `transfer(address to, uint256 amount) → bool` | ERC20 |

Key behaviors:
- `deposit(amount, recipient, 0)` — `tokenId=0` creates a new position and mints NFT to `recipient`. Actual tokenId emitted in `AlchemistV3PositionNFTMinted`.
- `mint(tokenId, amount, multisig)` — `msg.sender` must be NFT owner. alAssets land in multisig.
- `setDepositCap` — requires multisig to be admin on each AlchemistV3.

---

## Gas Estimates

| Operation | Gas |
|-----------|----:|
| `setDepositCap` | 35,000 |
| `deposit` (new position) | 175,000 |
| `deposit` (large, > 10²¹ wei) | 190,000 |
| `mint` | 130,000 |
| `mint` (large) | 145,000 |
| `alToken.transfer` (credit) | 65,000 |
| `ERC721.transferFrom` | 70,000 |

---

## Pre-Migration Checklist

- [ ] All AlchemistV3 contracts deployed and addresses filled into `src/config.py`
- [ ] `nft` address set in each asset config (read from `alchemist.alchemistPositionNFT()`)
- [ ] Migration multisig set as `admin` on each AlchemistV3
- [ ] Multisig funded with enough MYT shares to cover total deposit amounts
- [ ] Dry run passes: `ape run deposit --dry-run`, `ape run mint --dry-run`, `ape run distribute --dry-run`, `ape run credit --dry-run`
- [ ] Distribute and credit scripts not run until deposit + mint + verify are complete

---

## Chains Supported

| Chain | Chain ID | Multisig | Block Gas |
|-------|----------|----------|----------:|
| Ethereum Mainnet | 1 | `0xF56D660138815fC5d7a06cd0E1630225E788293D` | 60M |
| Optimism | 10 | `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d` | 30M |
| Arbitrum One | 42161 | `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b` | 32M |

---

## Security Notes

- The migration multisig temporarily holds all position NFTs and all minted alAssets. It must be a properly secured multi-signature wallet.
- Steps 4-5 (distribute + credit) should only execute **after team verification** that deposits and mints completed correctly.
- Token ID placeholder `999999` is used in preview/dry-run mode. Real execution requires `read_ids` to have captured the mapping first.
- Debt user positions carry their V2 debt on the NFT after migration. This is intentional — the debt is real and repays over time via yield.
- Credit users end up with **zero debt** on their position. Their alAsset credit is sent separately. The remaining minted alAssets are burned by the multisig.
