# CDP Migration Tool

## Overview
Internal one-off tool for migrating DeFi CDP protocol positions to a new version. The tool reads position snapshots from CSV files, batches transactions for Gnosis Safe multisigs, and recreates positions (deposit → mint → transfer NFT) on the new protocol.

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: Apeworx
- **Target**: Gnosis Safe multisig transaction batching
- **Chains**: Ethereum Mainnet, Optimism, Arbitrum

## Project Structure
```
cdp-migration/
├── ape-config.yaml           # Apeworx configuration
├── contracts/                # ABI files
│   ├── cdp_abi.json          # deposit() and mint() functions
│   └── erc721_abi.json       # transferFrom() for NFT transfer
├── data/
│   ├── mainnet.csv           # Position snapshots per chain
│   ├── optimism.csv
│   └── arbitrum.csv
├── scripts/
│   ├── migrate.py            # Main migration script
│   ├── batch.py              # Transaction batching logic
│   ├── preview.py            # Human-readable preview
│   └── validate.py           # CSV validation
├── src/
│   ├── config.py             # Chain/asset configuration
│   ├── gas.py                # Dynamic gas estimation
│   ├── safe.py               # Gnosis Safe integration
│   └── types.py              # Data models
├── tests/
│   └── ...
├── logs/                     # Error logs (clean up when resolved)
├── .claude/
│   ├── agents/               # Subagent definitions
│   └── reports/              # Agent work reports
└── CLAUDE.md
```

## Configuration Schema

### Chain Configuration
```python
CHAINS = {
    "mainnet": {
        "chain_id": 1,
        "multisig": "",            # Temporary migration multisig
        "cdp_usd": "",             # CDP contract for USD positions (deposit/mint)
        "cdp_eth": "",             # CDP contract for ETH positions (deposit/mint)
        "nft_usd": "",             # NFT contract for USD positions (transfer)
        "nft_eth": "",             # NFT contract for ETH positions (transfer)
        "collateral_usd": "",      # USD collateral token address
        "collateral_eth": "",      # ETH collateral token address (or WETH)
    },
    "optimism": {
        "chain_id": 10,
        "multisig": "",
        "cdp_usd": "",
        "cdp_eth": "",
        "nft_usd": "",
        "nft_eth": "",
        "collateral_usd": "",
        "collateral_eth": "",
    },
    "arbitrum": {
        "chain_id": 42161,
        "multisig": "",
        "cdp_usd": "",
        "cdp_eth": "",
        "nft_usd": "",
        "nft_eth": "",
        "collateral_usd": "",
        "collateral_eth": "",
    },
}
```

### CSV Format
```csv
address,USD_debt,USD_underlyingValue,ETH_debt,ETH_underlyingValue
0x123...,1000.50,5000.00,0.5,2.0
```

---

## Contract Functions & ABIs

### Deposit Function
Deposits collateral and creates a position NFT.

```solidity
function deposit(uint256 amount, address recipient, uint256 tokenId) external returns (uint256)
```

**Parameters:**
- `amount`: Collateral amount to deposit (in wei)
- `recipient`: Address that will own the position (use multisig during migration, transfer later)
- `tokenId`: Sequential ID starting at 0 for each chain-asset pair

**ABI:**
```json
{
  "type": "function",
  "name": "deposit",
  "inputs": [
    { "name": "amount", "type": "uint256", "internalType": "uint256" },
    { "name": "recipient", "type": "address", "internalType": "address" },
    { "name": "tokenId", "type": "uint256", "internalType": "uint256" }
  ],
  "outputs": [
    { "name": "", "type": "uint256", "internalType": "uint256" }
  ],
  "stateMutability": "nonpayable"
}
```

### Mint Function
Mints debt against an existing position.

```solidity
function mint(uint256 tokenId, uint256 amount, address recipient) external
```

**Parameters:**
- `tokenId`: The position NFT ID (from deposit step)
- `amount`: Debt amount to mint (in wei)
- `recipient`: Address to receive the minted debt tokens

**ABI:**
```json
{
  "type": "function",
  "name": "mint",
  "inputs": [
    { "name": "tokenId", "type": "uint256", "internalType": "uint256" },
    { "name": "amount", "type": "uint256", "internalType": "uint256" },
    { "name": "recipient", "type": "address", "internalType": "address" }
  ],
  "outputs": [],
  "stateMutability": "nonpayable"
}
```

### NFT Transfer Function
Standard ERC721 transfer (or custom - TBD).

```solidity
function transferFrom(address from, address to, uint256 tokenId) external
```

**Parameters:**
- `from`: Current owner (multisig)
- `to`: Original user address from CSV
- `tokenId`: The position NFT ID

---

## Token ID Management

**Critical**: Each chain-asset combination maintains its own independent tokenId sequence starting at 0.

```
Mainnet USD:   tokenId 0, 1, 2, 3, ...
Mainnet ETH:   tokenId 0, 1, 2, 3, ...
Optimism USD:  tokenId 0, 1, 2, 3, ...
Optimism ETH:  tokenId 0, 1, 2, 3, ...
Arbitrum USD:  tokenId 0, 1, 2, 3, ...
Arbitrum ETH:  tokenId 0, 1, 2, 3, ...
```

**Assignment Logic:**
1. Process CSV rows in order
2. For each row, if `USD_underlyingValue > 0`, assign next USD tokenId
3. For each row, if `ETH_underlyingValue > 0`, assign next ETH tokenId
4. Track assigned tokenIds for use in mint and transfer steps

**Example CSV Processing:**
```
Row 1: 0xAAA, USD_underlying=5000 → USD tokenId=0
Row 1: 0xAAA, ETH_underlying=2.0  → ETH tokenId=0
Row 2: 0xBBB, USD_underlying=0    → (skip USD)
Row 2: 0xBBB, ETH_underlying=1.5  → ETH tokenId=1
Row 3: 0xCCC, USD_underlying=3000 → USD tokenId=1
```

**Data Structure:**
```python
@dataclass
class PositionMigration:
    user_address: str
    asset_type: Literal["USD", "ETH"]
    token_id: int
    deposit_amount: int      # underlyingValue in wei
    mint_amount: int         # debt in wei
    chain: str
```

---

## Commands
```bash
# Install dependencies
ape plugins install safe gnosis

# Validate CSV data
ape run validate --chain mainnet

# Preview batched transactions (human-readable)
ape run preview --chain mainnet

# Execute migration (prompts for confirmation after preview)
ape run migrate --chain mainnet
```

## Code Style
Follow Apeworx documentation conventions:
- Use `ape` CLI for all blockchain interactions
- Use `@ape.cli` decorators for scripts
- Prefer `ContractInstance` over raw web3 calls
- Use type hints throughout
- Use `click` for CLI argument parsing (ape standard)
- Keep functions focused and single-purpose

## Gas Batching Rules
- **Target**: Pack transactions to maximize batch size under ~16M gas limit
- **Estimation**: Dynamically estimate gas per transaction
- **Strategy**: Greedy bin-packing - add transactions until limit approached
- **Buffer**: Reserve 5% headroom below gas limit for safety

## Transaction Flow Per Position

For each position migration (one per user-asset pair):

### Step 1: Deposit
```python
cdp_contract.deposit(
    amount=position.deposit_amount,      # underlyingValue in wei
    recipient=chain_config["multisig"],  # Multisig holds NFT initially
    tokenId=position.token_id            # Sequential per chain-asset
)
```

### Step 2: Mint
```python
cdp_contract.mint(
    tokenId=position.token_id,           # Same tokenId from deposit
    amount=position.mint_amount,         # debt in wei
    recipient=position.user_address      # Debt tokens go directly to user
)
```

### Step 3: Transfer NFT
```python
nft_contract.transferFrom(
    from_=chain_config["multisig"],      # Multisig is current owner
    to=position.user_address,            # Original user gets NFT
    tokenId=position.token_id
)
```

### Batching Strategy
- Process ALL deposits first, then ALL mints, then ALL transfers
- This groups similar operations for more predictable gas estimation
- Each batch stays under ~16M gas (with 5% buffer)

## Error Handling
- **Invalid CSV data**: Halt entire batch immediately, do not proceed
- **Validation errors**: Log detailed error with row number and field
- **Transaction failures**: Log full context for debugging

## Logging
- Keep detailed error logs in `logs/` during development
- Clean up resolved error logs as issues are fixed
- Do not accumulate stale debugging data

---

# Agent Workflow

## Report Protocol
After completing work, agents must create a report in `.claude/reports/` with:
- Filename: `{PR-number}_{task-name}_{timestamp}.md`
- What was done
- Files created/modified
- Any issues encountered
- Notes for subsequent agents

Subsequent agents should reference prior reports when relevant.

## PR Breakdown

### PR 1: Project Scaffolding
- Initialize ape project structure
- Create configuration module with chain/asset mappings
- Set up data models and types
- Add placeholder ABI loading

### PR 2: CSV Validation
- CSV parser with strict validation
- Halt on any invalid row
- Human-readable validation error messages
- Unit tests for validation logic

### PR 3: Gas Estimation & Batching
- Dynamic gas estimation per operation type
- Greedy bin-packing algorithm for batch optimization
- Batch size verification against 16M limit
- Unit tests for batching logic

### PR 4: Transaction Building
- Deposit transaction builder
- Mint transaction builder
- NFT transfer transaction builder
- Integration with ABI files

### PR 5: Gnosis Safe Integration
- Safe SDK integration
- Transaction proposal formatting
- Batch propagation to Safe

### PR 6: Preview & Execution Flow
- Human-readable transaction preview
- Confirmation prompt before execution
- Progress reporting during execution
- Final summary output

### PR 7: Multi-chain Support
- Chain selection CLI argument
- Chain-specific configuration loading
- Verification of chain-specific addresses

---

# Subagent Instructions

## For Code Review Agent
Reference: `.claude/agents/code-reviewer.md`
- Review all code changes against this CLAUDE.md
- Verify Apeworx conventions are followed
- Check error handling matches spec (halt on invalid CSV)
- Ensure gas batching logic is sound
- Flag any hardcoded values that should be configurable

## For Test Agent
Reference: `.claude/agents/test-runner.md`
- Run full test suite after changes
- Verify CSV validation catches edge cases
- Test batching algorithm with various position counts
- Mock gas estimation for deterministic tests

## For Implementation Agents
- Read prior reports in `.claude/reports/` before starting
- Create report when done
- Follow PR breakdown for scope
- Do not exceed PR scope without explicit approval
