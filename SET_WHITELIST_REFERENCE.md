# Alchemix V3 Migration — Phase D (`setWhitelist`) Reference

The V3 migration cannot mint alAssets (Phase 2) until each alToken's minter
whitelist is swapped from the V2 alchemist to the V3 alchemist. This is
**Phase D**, signed by the alToken **owner** (not the migration multisig) via
two calls per chain/asset:

```solidity
alToken.setWhitelist(V2_alchemist, false);   // revoke V2
alToken.setWhitelist(V3_alchemist, true);    // grant V3
```

Use [scripts/set_whitelist.py](scripts/set_whitelist.py) to emit the Safe
Transaction Builder JSON for each chain/asset. Output lands in
`out/<chain>_<asset>_set_whitelist_batch01.json` and must be uploaded to the
**alToken owner's** Safe, not the migration multisig.

---

## Per-chain summary

| Chain | Token Owner (Signer) | Whitelist Accessor |
|---|---|---|
| Ethereum Mainnet | `0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9` (ETH Ops Multisig) | `whiteList(address)` |
| Optimism | `0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a` (OP Ops Multisig) | `whitelisted(address)` |
| Arbitrum | `0x7e108711771DfdB10743F016D46d75A9379cA043` (ARB Ops Multisig) | `whitelisted(address)` |

## Per chain/asset — addresses

| Chain | Asset | alToken | V2 Alchemist (revoke) | V3 Alchemist (grant) |
|---|---|---|---|---|
| Mainnet | alUSD | `0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9` | `0x5C6374a2ac4EBC38DeA0Fc1F8716e5Ea1AdD94dd` | `0xeB83112d925268BeDe86654C13D423a987587e3E` |
| Mainnet | alETH | `0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6` | `0x062Bf725dC4cDF947aa79Ca2aaCCD4F385b13b5c` | `0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B` |
| Optimism | alUSD | `0xCB8FA9a76b8e203D8C3797bF438d8FB81Ea3326A` | `0x10294d57A419C8eb78C648372c5bAA27fD1484af` | `0x930750a3510E703535e943E826ABa3c364fFC1De` |
| Optimism | alETH | `0x3E29D3A9316dAB217754d13b28646B76607c5f04` | `0xe04Bb5B4de60FA2fBa69a93adE13A8B3B569d5B4` | `0xDeD3A04612FF12b57317abE38e68026Fc9D28114` |
| Arbitrum | alUSD | `0xCB8FA9a76b8e203D8C3797bF438d8FB81Ea3326A` | `0xb46eE2E4165F629b4aBCE04B7Eb4237f951AC66F` | `0x930750a3510E703535e943E826ABa3c364fFC1De` |
| Arbitrum | alETH | `0x17573150d67d820542EFb24210371545a4868B03` | `0x654e16a0b161b150F5d1C8a5ba6E7A7B7760703A` | `0xDeD3A04612FF12b57317abE38e68026Fc9D28114` |

## Current on-chain status

_Captured 2026-04-14._

| Chain | Asset | V2 Whitelisted | V3 Whitelisted | Action Needed |
|---|---|:---:|:---:|---|
| Mainnet | alUSD | ✅ | ❌ | 2-call swap |
| Mainnet | alETH | ✅ | ❌ | 2-call swap |
| Optimism | alUSD | ✅ | ❌ | 2-call swap |
| Optimism | alETH | ✅ | ❌ | 2-call swap |
| Arbitrum | alUSD | ❌ | ✅ | **Already done** |
| Arbitrum | alETH | ✅ | ❌ | 2-call swap |

## Sources

- **V2 alchemists**: [github.com/alchemix-finance/deployments](https://github.com/alchemix-finance/deployments) — `{chain}/AlchemistV2_{alUSD|alETH}.json`
- **V3 alchemists**: Alchemix V3 Operator Dashboard bundle, verified via on-chain `asset()` calls against each MYT ([src/myt_config.py](src/myt_config.py))
- **alToken owners**: live chain — `owner()` (L2s) / AccessControl `ADMIN` role members (mainnet)
- **Whitelist state**: live chain — `whiteList(addr)` (mainnet) / `whitelisted(addr)` (L2s)

## Usage

Generate JSON for Safe UI upload (5 combos — skip Arbitrum alUSD):

```bash
ape run set_whitelist --chain mainnet  --asset usd --mode json --yes
ape run set_whitelist --chain mainnet  --asset eth --mode json --yes
ape run set_whitelist --chain optimism --asset usd --mode json --yes
ape run set_whitelist --chain optimism --asset eth --mode json --yes
ape run set_whitelist --chain arbitrum --asset eth --mode json --yes
```

Each command writes `out/<chain>_<asset>_set_whitelist_batch01.json` containing
two transactions. Upload each file to the corresponding alToken owner's Safe
(ETH/OP/ARB Ops Multisig), not the migration multisig.
