# Pre-Deposit Upload Checklist (Epoch 4)

Tick each box as the JSON is **uploaded/proposed** to the Safe. Add execution timestamp once signers execute. Status verification commands at the bottom.

> **Within a chain**: Prereq-1 → D → A → B → C. A/B/C strictly sequential per asset.
> **Across chains**: independent — run in parallel if signers are available.

---

## Mainnet (chain id 1)

### Prereq-1 — `acceptAdmin()` (Mainnet migration multisig)
Safe: `0xF56D660138815fC5d7a06cd0E1630225E788293D` · [Safe UI](https://app.safe.global/home?safe=eth:0xF56D660138815fC5d7a06cd0E1630225E788293D)
*(No JSON file — build manually in Transaction Builder, 2 calls, value 0, data `0xe9c714f2`)*

- [ ] **Proposed** — call 1: `to=0xeB83112d925268BeDe86654C13D423a987587e3E` (alUSD alchemist), call 2: `to=0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B` (alETH alchemist)  · safeTxHash: `__________`
- [ ] **Executed** · txHash: `__________` · date: `__________`

### Phase D — setWhitelist (ETH Ops Multisig)
Safe: `0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9` · [Safe UI](https://app.safe.global/home?safe=eth:0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9)

- [ ] Proposed [mainnet_alUSD_set_whitelist_batch01.json](out/mainnet_alUSD_set_whitelist_batch01.json) · safeTxHash: `__________`
- [ ] Executed · txHash: `__________`
- [ ] Proposed [mainnet_alETH_set_whitelist_batch01.json](out/mainnet_alETH_set_whitelist_batch01.json) · safeTxHash: `__________`
- [ ] Executed · txHash: `__________`

### Phases A → B → C — Mainnet migration multisig
Safe: `0xF56D660138815fC5d7a06cd0E1630225E788293D`

**alUSD** (4,520,719 USDC)
- [ ] A — Proposed [mainnet_alUSD_approve_underlying_batch01.json](out/mainnet_alUSD_approve_underlying_batch01.json) · safeTxHash: `__________`
- [ ] A — Executed · txHash: `__________`
- [ ] B — Proposed [mainnet_alUSD_deposit_myt_batch01.json](out/mainnet_alUSD_deposit_myt_batch01.json) · safeTxHash: `__________`
- [ ] B — Executed · txHash: `__________`
- [ ] C — Proposed [mainnet_alUSD_approve_myt_batch01.json](out/mainnet_alUSD_approve_myt_batch01.json) · safeTxHash: `__________`
- [ ] C — Executed · txHash: `__________`

**alETH** (11,323.49 WETH)
- [ ] A — Proposed [mainnet_alETH_approve_underlying_batch01.json](out/mainnet_alETH_approve_underlying_batch01.json) · safeTxHash: `__________`
- [ ] A — Executed · txHash: `__________`
- [ ] B — Proposed [mainnet_alETH_deposit_myt_batch01.json](out/mainnet_alETH_deposit_myt_batch01.json) · safeTxHash: `__________`
- [ ] B — Executed · txHash: `__________`
- [ ] C — Proposed [mainnet_alETH_approve_myt_batch01.json](out/mainnet_alETH_approve_myt_batch01.json) · safeTxHash: `__________`
- [ ] C — Executed · txHash: `__________`

---

## Optimism (chain id 10)

### Phase D — setWhitelist (OP Ops Multisig)
Safe: `0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a` · [Safe UI](https://app.safe.global/home?safe=oeth:0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a)

- [ ] Proposed [optimism_alUSD_set_whitelist_batch01.json](out/optimism_alUSD_set_whitelist_batch01.json) · safeTxHash: `__________`
- [ ] Executed · txHash: `__________`
- [ ] Proposed [optimism_alETH_set_whitelist_batch01.json](out/optimism_alETH_set_whitelist_batch01.json) · safeTxHash: `__________`
- [ ] Executed · txHash: `__________`

### Phases A → B → C — Optimism migration multisig
Safe: `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d` · [Safe UI](https://app.safe.global/home?safe=oeth:0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d)

**alUSD** (280,099 USDC)
- [ ] A — Proposed [optimism_alUSD_approve_underlying_batch01.json](out/optimism_alUSD_approve_underlying_batch01.json) · safeTxHash: `__________`
- [ ] A — Executed · txHash: `__________`
- [ ] B — Proposed [optimism_alUSD_deposit_myt_batch01.json](out/optimism_alUSD_deposit_myt_batch01.json) · safeTxHash: `__________`
- [ ] B — Executed · txHash: `__________`
- [ ] C — Proposed [optimism_alUSD_approve_myt_batch01.json](out/optimism_alUSD_approve_myt_batch01.json) · safeTxHash: `__________`
- [ ] C — Executed · txHash: `__________`

**alETH** (854.21 WETH)
- [ ] A — Proposed [optimism_alETH_approve_underlying_batch01.json](out/optimism_alETH_approve_underlying_batch01.json) · safeTxHash: `__________`
- [ ] A — Executed · txHash: `__________`
- [ ] B — Proposed [optimism_alETH_deposit_myt_batch01.json](out/optimism_alETH_deposit_myt_batch01.json) · safeTxHash: `__________`
- [ ] B — Executed · txHash: `__________`
- [ ] C — Proposed [optimism_alETH_approve_myt_batch01.json](out/optimism_alETH_approve_myt_batch01.json) · safeTxHash: `__________`
- [ ] C — Executed · txHash: `__________`

---

## Arbitrum (chain id 42161) — alETH only

### Phase D — setWhitelist (ARB Ops Multisig)
Safe: `0x7e108711771DfdB10743F016D46d75A9379cA043` · [Safe UI](https://app.safe.global/home?safe=arb1:0x7e108711771DfdB10743F016D46d75A9379cA043)

- [ ] Proposed [arbitrum_alETH_set_whitelist_batch01.json](out/arbitrum_alETH_set_whitelist_batch01.json) · safeTxHash: `__________`
- [ ] Executed · txHash: `__________`

### Phases A → B → C — Arbitrum migration multisig
Safe: `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b` · [Safe UI](https://app.safe.global/home?safe=arb1:0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b)

**alETH** (118.33 WETH)
- [ ] A — Proposed [arbitrum_alETH_approve_underlying_batch01.json](out/arbitrum_alETH_approve_underlying_batch01.json) · safeTxHash: `__________`
- [ ] A — Executed · txHash: `__________`
- [ ] B — Proposed [arbitrum_alETH_deposit_myt_batch01.json](out/arbitrum_alETH_deposit_myt_batch01.json) · safeTxHash: `__________`
- [ ] B — Executed · txHash: `__________`
- [ ] C — Proposed [arbitrum_alETH_approve_myt_batch01.json](out/arbitrum_alETH_approve_myt_batch01.json) · safeTxHash: `__________`
- [ ] C — Executed · txHash: `__________`

---

## Status verification

### Queued (proposed but not yet executed) — Safe Transaction Service API

```bash
# Per Safe — list all pending (queued) transactions:
# Mainnet:
curl -s "https://safe-transaction-mainnet.safe.global/api/v1/safes/<SAFE>/multisig-transactions/?executed=false&trusted=true" | jq '.results[] | {nonce, safeTxHash, to, confirmations: (.confirmations | length), confirmationsRequired}'

# Optimism:
curl -s "https://safe-transaction-optimism.safe.global/api/v1/safes/<SAFE>/multisig-transactions/?executed=false&trusted=true" | jq '.results[] | {nonce, safeTxHash, to, confirmations: (.confirmations | length), confirmationsRequired}'

# Arbitrum:
curl -s "https://safe-transaction-arbitrum.safe.global/api/v1/safes/<SAFE>/multisig-transactions/?executed=false&trusted=true" | jq '.results[] | {nonce, safeTxHash, to, confirmations: (.confirmations | length), confirmationsRequired}'
```

### Executed — on-chain effect checks

```bash
# Prereq-1 — admin handover (mainnet):
cast call --rpc-url $MAINNET_RPC 0xeB83112d925268BeDe86654C13D423a987587e3E "admin()(address)"
cast call --rpc-url $MAINNET_RPC 0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B "admin()(address)"
# expect: 0xF56D660138815fC5d7a06cd0E1630225E788293D

# Phase D — whitelist swap (per chain/asset):
cast call --rpc-url $RPC $AL_TOKEN "whiteList(address)(bool)"   $V2_ALCHEMIST   # mainnet alTokens (capital L)
cast call --rpc-url $RPC $AL_TOKEN "whitelisted(address)(bool)" $V3_ALCHEMIST   # L2 alTokens
# expect: V2=false, V3=true

# Phase A — underlying allowance migration multisig → MYT:
cast call --rpc-url $RPC $UNDERLYING "allowance(address,address)(uint256)" $MIGRATION_MULTISIG $MYT
# expect >= total

# Phase B — MYT shares held by migration multisig:
cast call --rpc-url $RPC $MYT "balanceOf(address)(uint256)" $MIGRATION_MULTISIG
# expect = total

# Phase C — MYT allowance migration multisig → alchemist:
cast call --rpc-url $RPC $MYT "allowance(address,address)(uint256)" $MIGRATION_MULTISIG $ALCHEMIST
# expect >= total
```

Address sources: [src/myt_config.py](src/myt_config.py) and [src/config.py](src/config.py).
