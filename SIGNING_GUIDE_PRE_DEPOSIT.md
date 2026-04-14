# Alchemix V3 Migration — Pre-Deposit Signing Guide

> **Audience**: Alchemix Safe signers who need to execute the pre-deposit phases (and one mainnet-only admin prereq) before the main deposit phase can run.
>
> **Scope**: Everything that must be signed **before** Phase 1 (`deposit.py`) runs. Does NOT cover Phase 1 itself or Phases 2–5.
>
> **Phases covered**: Prereq-1 (mainnet `acceptAdmin`), Phase A (approve underlying), Phase B (deposit into MYT), Phase C (approve MYT), Phase D (setWhitelist).

---

## TL;DR — What to sign, in what order, from which Safe

Each row is a Safe transaction. Safe addresses and chain IDs are exact. Bundle rows within the same Safe into a single multi-call Safe Transaction Builder batch when possible; cross-Safe rows must be separate transactions.

| # | Phase | Chain | Signer Safe | What you're authorizing |
|---|---|---|---|---|
| **Prereq-1** | — | Ethereum Mainnet | **Migration multisig `0xF56D660138815fC5d7a06cd0E1630225E788293D`** | `acceptAdmin()` on both V3 alchemists (admin transfer already queued by prior EOA). Required to unblock Phase 1 on mainnet only. |
| **D** | setWhitelist | Ethereum Mainnet | **ETH Ops Multisig `0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9`** (or BASE Ops `0x8392F6669292fA56123F71949B52d883aE57e225` — either has admin) | Revoke V2 alchemist from alToken whitelist, grant V3 alchemist. Two alTokens × 2 calls each = **4 calls**. |
| **D** | setWhitelist | Optimism | **OP Ops Multisig `0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a`** | Same as mainnet but on Optimism alTokens. 4 calls. |
| **D** | setWhitelist | Arbitrum | **ARB Ops Multisig `0x7e108711771DfdB10743F016D46d75A9379cA043`** | Only alETH token (alUSD already done). 2 calls. |
| **A, B, C** | approve_u / deposit_myt / approve_myt | Ethereum Mainnet | **Mainnet migration multisig `0xF56D660138815fC5d7a06cd0E1630225E788293D`** | Approve USDC to MYT (alUSD); deposit USDC → MYT; approve MYT to alchemist. Repeat for WETH/alETH. **6 calls** total across both assets. |
| **A, B, C** | approve_u / deposit_myt / approve_myt | Optimism | **Optimism migration multisig `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d`** | Same pattern on Optimism. 6 calls. |
| **A, B, C** | approve_u / deposit_myt / approve_myt | Arbitrum | **Arbitrum migration multisig `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b`** | Same pattern on Arbitrum alETH. alUSD is already fully done through Phase 1 on-chain, so skip for alUSD. |

**Execution order per chain**: Prereq-1 (mainnet only) → Phase D → Phase A → Phase B → Phase C. Phase D can actually happen at any time before Phase 2 (mint), so it's safe to batch it with A/B/C or run it independently; it just must be done before the production migration starts running Phase 2.

---

## Prereq-1 — Mainnet `acceptAdmin()`

_Mainnet only. Signer = mainnet migration multisig._

The V3 alchemist on mainnet had its admin role set by a prior EOA (`0xf456A36B04B0951Cd19d6D8aA0c0b3b0a07f9fF2`), and that EOA has already queued the migration multisig as `pendingAdmin`. To finalize, the migration multisig must call `acceptAdmin()` on each V3 alchemist proxy.

**Signer Safe**: `0xF56D660138815fC5d7a06cd0E1630225E788293D` (mainnet migration multisig)
**Safe UI**: `https://app.safe.global/home?safe=eth:0xF56D660138815fC5d7a06cd0E1630225E788293D`

Submit a **single Safe Transaction Builder batch** with these two calls:

| # | `to` | `value` | `data` | Function |
|---|---|---|---|---|
| 1 | `0xeB83112d925268BeDe86654C13D423a987587e3E` | 0 | `0xe9c714f2` | `acceptAdmin()` on mainnet alUSD alchemist |
| 2 | `0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B` | 0 | `0xe9c714f2` | `acceptAdmin()` on mainnet alETH alchemist |

**Verification** (after execution):
```bash
cast call --rpc-url $MAINNET_RPC 0xeB83112d925268BeDe86654C13D423a987587e3E "admin()(address)"
cast call --rpc-url $MAINNET_RPC 0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B "admin()(address)"
# Both must return 0xF56D660138815fC5d7a06cd0E1630225E788293D
```

After this, mainnet alchemist admin matches Arbitrum and Optimism (migration multisig = alchemist admin); Phase 1 on mainnet becomes unblocked.

---

## Phase D — setWhitelist (alToken minter swap)

_Per chain. Signer = the alToken owner for that chain._

The V3 alchemist cannot mint alAssets (Phase 2) until each alToken's minter whitelist is swapped from V2 → V3. Each alToken exposes `setWhitelist(address target, bool state)` callable by the alToken owner. Complete details and rationale: [SET_WHITELIST_REFERENCE.md](SET_WHITELIST_REFERENCE.md).

### Chain selectors

Function signature (all chains): `setWhitelist(address,bool)` — selector `0x53d6fd59`.

Calldata = selector + 32-byte address-padded target + 32-byte zero-padded bool (0x00 for false, 0x01 for true).

### Mainnet (ETH Ops Multisig signs)

**Signer Safe**: `0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9` (ETH Ops Multisig).
Alternative signer (also has ADMIN_ROLE): `0x8392F6669292fA56123F71949B52d883aE57e225`.
**Safe UI**: `https://app.safe.global/home?safe=eth:0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9`

Four calls in a single Safe batch:

| # | `to` | Function | target (address) | state |
|---|---|---|---|---|
| 1 | `0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9` (alUSD) | setWhitelist | `0x5C6374a2ac4EBC38DeA0Fc1F8716e5Ea1AdD94dd` (V2 revoke) | `false` |
| 2 | `0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9` (alUSD) | setWhitelist | `0xeB83112d925268BeDe86654C13D423a987587e3E` (V3 grant) | `true` |
| 3 | `0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6` (alETH) | setWhitelist | `0x062Bf725dC4cDF947aa79Ca2aaCCD4F385b13b5c` (V2 revoke) | `false` |
| 4 | `0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6` (alETH) | setWhitelist | `0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B` (V3 grant) | `true` |

### Optimism (OP Ops Multisig signs)

**Signer Safe**: `0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a` (OP Ops Multisig)
**Safe UI**: `https://app.safe.global/home?safe=oeth:0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a`

| # | `to` | Function | target | state |
|---|---|---|---|---|
| 1 | `0xCB8FA9a76b8e203D8C3797bF438d8FB81Ea3326A` (alUSD) | setWhitelist | `0x10294d57A419C8eb78C648372c5bAA27fD1484af` (V2) | `false` |
| 2 | `0xCB8FA9a76b8e203D8C3797bF438d8FB81Ea3326A` (alUSD) | setWhitelist | `0x930750a3510E703535e943E826ABa3c364fFC1De` (V3) | `true` |
| 3 | `0x3E29D3A9316dAB217754d13b28646B76607c5f04` (alETH) | setWhitelist | `0xe04Bb5B4de60FA2fBa69a93adE13A8B3B569d5B4` (V2) | `false` |
| 4 | `0x3E29D3A9316dAB217754d13b28646B76607c5f04` (alETH) | setWhitelist | `0xDeD3A04612FF12b57317abE38e68026Fc9D28114` (V3) | `true` |

### Arbitrum (ARB Ops Multisig signs — alETH only)

**Signer Safe**: `0x7e108711771DfdB10743F016D46d75A9379cA043` (ARB Ops Multisig)
**Safe UI**: `https://app.safe.global/home?safe=arb1:0x7e108711771DfdB10743F016D46d75A9379cA043`

Arbitrum alUSD is **already** transitioned (V2 revoked, V3 granted) per on-chain check — skip it.

| # | `to` | Function | target | state |
|---|---|---|---|---|
| 1 | `0x17573150d67d820542EFb24210371545a4868B03` (alETH) | setWhitelist | `0x654e16a0b161b150F5d1C8a5ba6E7A7B7760703A` (V2) | `false` |
| 2 | `0x17573150d67d820542EFb24210371545a4868B03` (alETH) | setWhitelist | `0xDeD3A04612FF12b57317abE38e68026Fc9D28114` (V3) | `true` |

### Phase D verification (all chains)

```bash
# For each chain + asset:
cast call --rpc-url $RPC $AL_TOKEN "whiteList(address)(bool)" $V2_ALCHEMIST   # mainnet alTokens use whiteList (capital L)
cast call --rpc-url $RPC $AL_TOKEN "whitelisted(address)(bool)" $V3_ALCHEMIST  # L2 alTokens use whitelisted
# Expected: V2 → false, V3 → true
```

---

## Phases A, B, C — Pre-deposit (migration multisig signs)

_Per chain, per asset. Signer = that chain's migration multisig._

These three phases move underlying tokens into the MYT vault so the migration multisig holds enough MYT shares to back every Phase 1 deposit.

- **Phase A** — `underlying.approve(MYT, total_amount)` — let the MYT pull underlying
- **Phase B** — `MYT.deposit(total_amount, migration_multisig)` — mint MYT shares to the multisig
- **Phase C** — `MYT.approve(alchemist, total_MYT)` — let the alchemist pull MYT during Phase 1 deposits

### Ready-to-upload JSON files

Pre-generated Safe Transaction Builder JSON is in [out/](out/) — each file has the exact calldata encoded. Upload via Safe UI → Transaction Builder → Import File.

| Chain / Asset | Phase A file | Phase B file | Phase C file |
|---|---|---|---|
| Mainnet alUSD | `out/mainnet_alUSD_approve_underlying_batch01.json` | `out/mainnet_alUSD_deposit_myt_batch01.json` | `out/mainnet_alUSD_approve_myt_batch01.json` |
| Mainnet alETH | `out/mainnet_alETH_approve_underlying_batch01.json` | `out/mainnet_alETH_deposit_myt_batch01.json` | `out/mainnet_alETH_approve_myt_batch01.json` |
| Optimism alUSD | `out/optimism_alUSD_approve_underlying_batch01.json` | `out/optimism_alUSD_deposit_myt_batch01.json` | `out/optimism_alUSD_approve_myt_batch01.json` |
| Optimism alETH | `out/optimism_alETH_approve_underlying_batch01.json` | `out/optimism_alETH_deposit_myt_batch01.json` | `out/optimism_alETH_approve_myt_batch01.json` |
| Arbitrum alETH | `out/arbitrum_alETH_approve_underlying_batch01.json` | `out/arbitrum_alETH_deposit_myt_batch01.json` | `out/arbitrum_alETH_approve_myt_batch01.json` |
| Arbitrum alUSD | skip | skip | skip |

Arbitrum alUSD has already been processed through Phase 1 — preflight will report "deposits already complete" if you attempt to re-run A/B/C there, so skip it.

### Per-chain signer Safes

| Chain | Signer Safe |
|---|---|
| Mainnet | `0xF56D660138815fC5d7a06cd0E1630225E788293D` |
| Optimism | `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d` |
| Arbitrum | `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b` |

### Amount sanity check (per combo)

These are the sums the JSON files encode, for comparison against your own expectations:

| Chain / Asset | Phase A approve amount | Phase B MYT deposit | Phase C approve to alchemist |
|---|---|---|---|
| Mainnet alUSD | 4,520,719 USDC (6d scale) | 4,520,719 USDC | 4,520,719 e18 MYT shares |
| Mainnet alETH | 11,323.49 WETH (18d) | 11,323.49 WETH | 11,323.49 e18 MYT shares |
| Optimism alUSD | 280,099 USDC | 280,099 USDC | 280,099 e18 MYT |
| Optimism alETH | 854.21 WETH | 854.21 WETH | 854.21 e18 MYT |
| Arbitrum alETH | 118.33 WETH | 118.33 WETH | 118.33 e18 MYT |

### Phase A/B/C verification

Between executions, or after all three per combo, run:

```bash
# Phase A check — underlying → MYT allowance
cast call --rpc-url $RPC $UNDERLYING "allowance(address,address)(uint256)" \
  $MIGRATION_MULTISIG $MYT
# Expect >= total_amount

# Phase B check — MYT shares held by multisig
cast call --rpc-url $RPC $MYT "balanceOf(address)(uint256)" $MIGRATION_MULTISIG
# Expect = total_amount (minting is 1:1 for these ERC-4626 vaults at migration time)

# Phase C check — MYT → alchemist allowance
cast call --rpc-url $RPC $MYT "allowance(address,address)(uint256)" \
  $MIGRATION_MULTISIG $ALCHEMIST
# Expect >= total_amount
```

---

## Overall execution sequence (recommended)

Per chain, in this order:

1. **(Mainnet only)** Prereq-1 — mainnet migration multisig signs `acceptAdmin()` batch.
2. **Phase D** — alToken-owner Safe signs setWhitelist batch (ETH Ops / OP Ops / ARB Ops).
3. **Phase A, B, C** — migration multisig signs (can be one batch per asset or all six calls bundled).

These are the prerequisites before **Phase 1** (`deposit.py`). Phase 1 is the largest phase (1245–3624 deposit calls per combo depending on chain/asset) and will be delivered in separate JSON files once all pre-deposit phases are confirmed complete on-chain.

---

## Quick-reference address index

| Label | Address |
|---|---|
| Mainnet migration multisig | `0xF56D660138815fC5d7a06cd0E1630225E788293D` |
| Optimism migration multisig | `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d` |
| Arbitrum migration multisig | `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b` |
| ETH Ops Multisig (mainnet alToken admin) | `0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9` |
| BASE Ops Multisig (alt mainnet alToken admin) | `0x8392F6669292fA56123F71949B52d883aE57e225` |
| OP Ops Multisig (optimism alToken owner) | `0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a` |
| ARB Ops Multisig (arbitrum alToken owner) | `0x7e108711771DfdB10743F016D46d75A9379cA043` |
| Mainnet alUSD alchemist (V3) | `0xeB83112d925268BeDe86654C13D423a987587e3E` |
| Mainnet alETH alchemist (V3) | `0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B` |
| Optimism alUSD alchemist (V3) | `0x930750a3510E703535e943E826ABa3c364fFC1De` |
| Optimism alETH alchemist (V3) | `0xDeD3A04612FF12b57317abE38e68026Fc9D28114` |
| Arbitrum alUSD alchemist (V3) | `0x930750a3510E703535e943E826ABa3c364fFC1De` |
| Arbitrum alETH alchemist (V3) | `0xDeD3A04612FF12b57317abE38e68026Fc9D28114` |

---

## References (in this repo)

- [SET_WHITELIST_REFERENCE.md](SET_WHITELIST_REFERENCE.md) — deeper dive on Phase D including V2 addresses and whitelist-accessor differences per chain
- [CHECKLIST.md](CHECKLIST.md) — overall migration epoch/phase structure (tooling perspective)
- [EPOCH_2_CHECKLIST.md](EPOCH_2_CHECKLIST.md) — fork-rehearsal verification matrix showing which phases have been proven to work
- [src/myt_config.py](src/myt_config.py) — V3 alchemist/MYT/underlying addresses per chain/asset (data source of truth for JSON generation)
- [src/config.py](src/config.py) — chain + asset config with migration multisig per chain
- [out/](out/) — pre-generated Safe Transaction Builder JSON for every A/B/C/D pre-deposit call
