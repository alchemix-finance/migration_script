# Alchemix V2 → V3 Migration Script

Python tooling for migrating Alchemix V2 CDP positions to V3. Reads position snapshots from CSV, encodes V3 contract calls, batches them within gas/size limits, and proposes each batch as a signed Gnosis Safe multisig transaction.

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/alchemix-finance/migration_script
cd migration_script
pip install eth-ape
ape plugins install alchemy etherscan
pip install python-dotenv

# 2. Set up environment
cp .env.example .env
# Edit .env — fill in your Alchemy API key, proposer PK, and proposer address

# 3. Run migration (example: mainnet alUSD)
ape run deposit   --chain mainnet --asset usd
ape run read_ids  --chain mainnet --asset usd --from-block <block>
ape run mint      --chain mainnet --asset usd
ape run verify    --chain mainnet --asset usd
ape run distribute --chain mainnet --asset usd
ape run credit    --chain mainnet --asset usd
```

Each script with Safe proposals runs in **checkpoint mode**: it proposes the first batch, prints the Safe UI link, and pauses. You verify the batch in the Safe UI against the CSV data. If it looks good, confirm in terminal and remaining batches proceed. If not, the script aborts cleanly.

---

## Environment Setup

Copy `.env.example` to `.env` and fill in three things:

```bash
# Get from https://dashboard.alchemy.com/
# Can also be exported system-wide; the ape-alchemy plugin reads this name natively.
WEB3_ALCHEMY_API_KEY=your_alchemy_api_key

# The private key of the proposer account (must be a Safe owner on each multisig)
# 64 hex chars, no 0x prefix
PROPOSER_PRIVATE_KEY=abcdef1234567890abcdef...

# The address of the proposer (derived from the key above)
PROPOSER_ADDRESS=0xYourAddressHere
```

That's it. Contract addresses are already configured in `src/config.py` for all three chains.

---

## Migration Flow

Run these in order, **per asset per chain**. Steps 1 and 3 require on-chain execution before proceeding.

```
Step 1: deposit.py    — Deposit MYT into alchemist, creates NFT positions
          ↓ (wait for on-chain execution)
Step 2: read_ids.py   — Read token IDs from NFT Transfer events
          ↓
Step 3: mint.py       — Mint alAssets against debt users' positions
          ↓ (wait for on-chain execution)
Step 4: verify.py     — Verify all positions match the CSV snapshot
          ↓ (DO NOT proceed if verify fails)
Step 5: distribute.py — Transfer NFTs to users
          ↓ (wait for on-chain execution)
Step 6: credit.py     — Send alAsset credit to credit users

After all steps: multisig burns remaining alAssets manually.
```

### Checkpoint Mode

Steps 1, 3, 5, and 6 all propose batches to the Safe. Instead of dumping everything at once, each script:

1. Proposes the **first batch** and prints the Safe UI link
2. Pauses and asks you to verify in Safe UI
3. You cross-reference the calldata against your CSV
4. Confirm → remaining batches go through. Deny → clean abort.

This means if the first batch looks wrong, you catch it before 50 more get queued.

### Three User Types

The CSV has three kinds of users, handled differently:

| Type | Debt value | What happens |
|------|-----------|--------------|
| **Debt user** | Positive | Deposit + Mint + NFT transfer. Carries debt into V3. |
| **Credit user** | Negative | Deposit only + alAsset transfer. Zero V3 debt. Protocol owed them. |
| **Zero-debt** | Zero | Deposit only + NFT transfer. Pure collateral position. |

---

## Commands

### Validate CSV (no chain interaction)

```bash
ape run validate --chain mainnet --asset usd
```

### Step 1 — Deposit MYT

```bash
ape run deposit --chain mainnet --asset usd
```

### Step 2 — Read Token IDs

After deposits land on chain, capture the token IDs:

```bash
ape run read_ids --chain mainnet --asset usd --from-block 12345678
```

Use the block number where the first deposit batch was executed.

### Step 3 — Mint

```bash
ape run mint --chain mainnet --asset usd
```

Requires the token ID file from Step 2 to exist.

### Step 4 — Verify

```bash
ape run verify --chain mainnet --asset usd
```

Checks that every position has a token ID, debt amounts match, credit users have zero debt, and total minted >= total credit. **Do not proceed past this step if it fails.**

### Step 5 — Distribute NFTs

```bash
ape run distribute --chain mainnet --asset usd
```

### Step 6 — Credit

```bash
ape run credit --chain mainnet --asset usd
```

### Preview (no submission)

```bash
ape run migrate --chain mainnet --asset usd --verbose
```

Shows the full plan without proposing anything to the Safe.

**Supported chains:** `mainnet`, `optimism`, `arbitrum`
**Supported assets:** `usd`, `eth`

---

## CSV Format

One CSV per asset per chain at `data/alUSDValues-sum-and-debt-{chain}.csv` or `data/alETHValues-sum-and-debt-{chain}.csv`.

```csv
address,underlyingValue,debt
0xAAA...,1000000000000000000,1000500000000000000
0xBBB...,15000000000000000000,3000000000000000000
0xCCC...,2000000000000000000,-250000000000000000
```

| Column | Description |
|--------|-------------|
| `address` | User's Ethereum address (42 chars) |
| `underlyingValue` | Collateral in MYT shares, 18-decimal wei |
| `debt` | Net debt. Positive = owes alAssets. Negative = protocol owes them. Zero = collateral only. |

All values are 18-decimal integers (wei). No scientific notation, no decimals.

---

## Batch Constraints

Batches are limited by gas, calldata size, and call count. Whichever limit is hit first triggers a new batch.

| Chain | Effective Gas Limit | Max TX Size |
|-------|--------------------:|------------:|
| Mainnet | 13,500,000 (90% of 15M) | 128 KB |
| Optimism | 13,500,000 | 120 KB |
| Arbitrum | 13,500,000 | 118 KB |

Each deposit batch starts with a `setDepositCap` call that raises the cap by the batch's total deposit amount. This means deposits can't front-run each other between batches.

---

## Contract Addresses

All addresses are in `src/config.py`. Summarized here:

### Mainnet

| Contract | alUSD | alETH |
|----------|-------|-------|
| Alchemist | `0xeB83...7e3E` | `0xfa99...E26B` |
| MYT Vault | `0x9B44...4bA5` | `0x29bc...c43D` |
| alToken | `0xBC6D...60E9` | `0x0100...7Ee6` |
| NFT | `0x872a...9bEB` | `0x15da...263d` |

### Optimism

| Contract | alUSD | alETH |
|----------|-------|-------|
| Alchemist | `0x9307...C1De` | `0xDeD3...8114` |
| MYT Vault | `0xAf51...cA41` | `0x91b8...f822` |
| alToken | `0xCB8F...326A` | `0x3E29...5f04` |
| NFT | `0xF700...4aD33` | `0x763F...3059` |

### Arbitrum

| Contract | alUSD | alETH |
|----------|-------|-------|
| Alchemist | `0x9307...C1De` | `0xDeD3...8114` |
| MYT Vault | `0xEba6...9f651` | `0xfe8F...B195C` |
| alToken | `0xCB8F...326A` | `0x1757...68B03` |
| NFT | `0xF700...4aD33` | `0x763F...3059` |

**Multisigs:** Mainnet `0xF56D...293D` · Optimism `0x3Dda...181d` · Arbitrum `0xeE1A...8484b`

---

## Pre-Migration Checklist

- [ ] `.env` created with Alchemy key, proposer PK, and proposer address
- [ ] Proposer address is a signer on all 3 migration multisigs
- [ ] Multisig holds enough MYT shares to cover total deposits for each asset
- [ ] Multisig is set as `admin` on each AlchemistV3
- [ ] Run `ape run validate --chain <chain> --asset <asset>` for all combinations
- [ ] Dry run: `ape run migrate --chain <chain> --asset <asset> --verbose`

---

## Architecture

```
migration_script/
├── .env.example          # Environment template
├── ape-config.yaml       # Apeworx config (networks, plugins)
├── contracts/            # ABIs (alchemist, erc721, altoken)
├── data/                 # CSVs + token ID JSONs (written by read_ids)
├── scripts/
│   ├── deposit.py        # Step 1 — deposit MYT, create NFTs
│   ├── read_ids.py       # Step 2 — read token IDs from events
│   ├── mint.py           # Step 3 — mint alAssets for debt users
│   ├── verify.py         # Step 4 — verify positions match CSV
│   ├── distribute.py     # Step 5 — transfer NFTs to users
│   ├── credit.py         # Step 6 — send alAsset credit
│   ├── migrate.py        # Preview all steps (no submission)
│   ├── batch.py          # Batch statistics
│   └── validate.py       # CSV validation only
├── src/
│   ├── config.py         # Chain addresses, gas limits, helpers
│   ├── env.py            # .env loader and typed accessors
│   ├── gas.py            # Multi-constraint batch creation
│   ├── safe.py           # Safe encoding, signing, and API client
│   ├── transactions.py   # ABI-encoded calldata builders
│   ├── types.py          # Data models (CSVRow, PositionMigration, etc.)
│   └── validation.py     # CSV parsing and decimal handling
└── tests/                # pytest suite
```

---

## Security Notes

- The proposer PK signs Safe transaction hashes locally. The key never leaves your machine.
- All transactions go through Gnosis Safe multisig. The proposer only *suggests* transactions — Safe owners must approve and execute.
- Checkpoint mode means you verify the first batch in Safe UI before the rest proceed.
- Token IDs are captured from on-chain events, not hardcoded. The `read_ids` step validates that event count matches CSV position count.
- The multisig temporarily holds all NFTs and minted alAssets during migration. Steps 5-6 distribute them to users.

---

## V3 Contract Interface

| Function | Signature | Access |
|----------|-----------|--------|
| `setDepositCap` | `setDepositCap(uint256)` | admin only |
| `deposit` | `deposit(uint256 amount, address recipient, uint256 tokenId)` | open |
| `mint` | `mint(uint256 tokenId, uint256 amount, address recipient)` | NFT owner |
| `transferFrom` | `transferFrom(address from, address to, uint256 tokenId)` | ERC721 |
| `transfer` | `transfer(address to, uint256 amount) → bool` | ERC20 |

`deposit(amount, recipient, 0)` creates a new position (tokenId=0 means "create new"). The actual token ID is emitted in the `AlchemistV3PositionNFTMinted` event.
