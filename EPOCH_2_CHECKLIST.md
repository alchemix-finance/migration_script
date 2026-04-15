# Epoch 2 — Fork Rehearsal Progress

Per-chain/asset execution matrix for [Epoch 2 of CHECKLIST.md](CHECKLIST.md#epoch-2-dry-run-fork-impersonation--per-chain--asset-6-total).
Each phase is independently re-runnable (idempotent preflight). Column order = execution order.

**Legend:** ✅ done · ⬜ pending · 🟡 in progress · ⚠️ blocked · ⏭️ skipped (already complete on-chain)

## Anvil fork command template

```bash
anvil --fork-url <RPC> --port 8545 --chain-id <id>
# Mainnet:  https://eth-mainnet.g.alchemy.com/v2/$WEB3_ALCHEMY_API_KEY   (id 1)
# Optimism: https://opt-mainnet.g.alchemy.com/v2/$WEB3_ALCHEMY_API_KEY   (id 10)
# Arbitrum: https://arb-mainnet.g.alchemy.com/v2/$WEB3_ALCHEMY_API_KEY   (id 42161)
```

## Execution matrix

_(Note: `validate` and `preview` columns omitted — `validate` runs implicitly inside every other phase, and `preview` is purely cosmetic. Phase letters/numbers below are the on-chain actions only.)_

| Chain / Asset | A (approve_u) | B (deposit_myt) | C (approve_myt) | D (setWhitelist + setCeiling) | 1 (deposit) | read_ids | 2 (mint) | 3 (verify) | 4 (distribute) | 5 (credit) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| arbitrum / alETH **(375 pos — row 105 removed)** | ✅ | ✅ | ✅ | ✅ | ✅ via `deposit --resume` (196 + 179 = 375 NFTs) | ✅ 375 ids fresh | ✅ via `mint --resume` (201 + 73 = 274 debt users) | ✅ | ✅ all 375 at users | ✅ 0.067616 alETH; surplus 49.74 alETH for manual burn |
| arbitrum / alUSD (1417 pos) | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⏭️ live | ✅ from-cache | ✅ mint exact +32,807.81 alUSD | ✅ verify | ✅ distribute 1417/1417 (846 first run + 571 via --resume) | ✅ credit 67.29 alUSD to 1083 users; multisig burn surplus 32,740.52 alUSD |
| optimism / alETH (864 pos) | ✅ | ✅ | ✅ | ⬜ needs setCeiling addition | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| optimism / alUSD (3624 pos) | ✅ | ✅ | ✅ | ⬜ needs setCeiling addition | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mainnet / alETH (714 pos) | ✅ | ✅ | ✅ | ✅ | ✅ (10 batches; Prereq 1b in prod) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mainnet / alUSD (1245 pos) | ✅ | ✅ | ✅ | ✅ (incl setCeiling 10³⁰) | ✅ (17 batches; Prereq 1a in prod) | ✅ | ✅ **mint exact +1,734,889.41 alUSD** | ✅ | 🟡 232/1245 (fork timeout, retry pending) | ⬜ |

## Production prerequisites (from rehearsal findings)

Things the Alchemix team must do **before** each chain/asset combo can run in production, independent of this migration tool:

| # | Chain | Required prerequisite | Who signs | Status |
|---|---|---|---|---|
| 1a | mainnet | **`acceptAdmin()` on V3 alUSD alchemist** `0xeB83112d925268BeDe86654C13D423a987587e3E`. Already-queued: `pendingAdmin()` returns the migration multisig — this single call finalizes the handover. | Mainnet migration multisig `0xF56D660138815fC5d7a06cd0E1630225E788293D` | ⬜ |
| 1b | mainnet | **`acceptAdmin()` on V3 alETH alchemist** `0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B`. Same setup as 1a — pendingAdmin already points at migration multisig. | Mainnet migration multisig `0xF56D660138815fC5d7a06cd0E1630225E788293D` | ⬜ |
| 2 | mainnet | **Phase D setWhitelist** on alUSD + alETH: revoke V2, grant V3. Two ADMIN_ROLE holders on each alToken — can sign with either. | ETH Ops Multisig `0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9` OR `0x8392F6669292fA56123F71949B52d883aE57e225` | ⬜ |
| 3 | optimism | **Phase D setWhitelist** on alUSD + alETH: revoke V2, grant V3. | OP Ops Multisig `0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a` | ⬜ |
| 4 | arbitrum | **Phase D setWhitelist** on alETH only (alUSD already done). | ARB Ops Multisig `0x7e108711771DfdB10743F016D46d75A9379cA043` | ⬜ |
| 5 | arbitrum | ~~**Row 105 policy decision** (underwater user `0x5cA51c0Bb6DbDf29465DAEB3F5Dbd37074133467`)~~ → **resolved**: removed from CSV. User's V2 debt forgiven (mint skipped); they get no V3 NFT. | Alchemix team | ✅ removed 2026-04-14 |
| 6 | mainnet + optimism + arbitrum (alUSD only) | **Phase D now also calls `setCeiling(V3_alchemist, 10^30)`** on each alToken (mainnet only — L2 canonical alTokens have no `ceiling` mechanism). Without this, V3 mint reverts `"Alchemist's ceiling was breached."`. Already wired into [scripts/set_whitelist.py](scripts/set_whitelist.py); the Phase D Safe batch is now **3 calls** on mainnet (revoke V2 wl, grant V3 wl, grant V3 ceiling) and 2 on L2s. JSON files in `out/` need regeneration to include this. | Same as Phase D signers (ETH Ops / OP Ops / ARB Ops) | ⬜ regenerate JSON before signing |

### Mainnet `acceptAdmin()` — one-Safe Transaction Builder batch

Both prerequisites 1a and 1b are executed by the mainnet migration multisig. They can be bundled in a single Safe UI tx (2 inner calls, no arguments on either):

| # | to (alchemist proxy) | data (selector only) | Intent |
|---|---|---|---|
| 1 | `0xeB83112d925268BeDe86654C13D423a987587e3E` | `0xe9c714f2` (`acceptAdmin()`) | Finalize admin transfer on mainnet alUSD alchemist |
| 2 | `0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B` | `0xe9c714f2` (`acceptAdmin()`) | Finalize admin transfer on mainnet alETH alchemist |

**Verification after signing:**
```bash
cast call --rpc-url https://eth-mainnet.g.alchemy.com/v2/$WEB3_ALCHEMY_API_KEY \
  0xeB83112d925268BeDe86654C13D423a987587e3E "admin()(address)"
cast call --rpc-url https://eth-mainnet.g.alchemy.com/v2/$WEB3_ALCHEMY_API_KEY \
  0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B "admin()(address)"
# Both should return 0xF56D660138815fC5d7a06cd0E1630225E788293D
```

After acceptAdmin, mainnet alchemist admin matches Arbitrum and Optimism (migration multisig is admin); Phase 1 on mainnet works identically to other chains — no tool changes needed.

## Per-combo notes

### arbitrum / alETH (376 positions) — rehearsal through Phase 1 + read_ids ✅
- Phases A, B, C, D executed on fork; Phase 1 landed 5 batches × ~77 deposits = 381 NFTs minted to migration multisig; read_ids captured 376 token IDs starting at fork block 452,520,580.
- **Row 105 blocker on Phase 2** — user `0x5cA51c0Bb6DbDf29465DAEB3F5Dbd37074133467` has debt 0.006394 alETH against collateral 0.003103 WETH (206% of V3's 90% LTV cap). Tabled pending business decision.
- Fork execution surfaced a tool tweak: bumped gas multiplier in `src/executor.py::ForkImpersonator` from `2×` to `10×` because Aave strategy `realAssets()` was OOM'ing on the deeper call chain. Production Safe txns handle this at the Safe level and aren't affected.

### arbitrum / alUSD (1417 positions) — already-live, not re-run
- Fully migrated through Phase 1 in production pre-rehearsal:
  - Phase D: already whitelisted (V2 revoked, V3 granted).
  - Phase 1: all 1417 NFTs already minted to migration multisig.
  - Live `totalDebt` on alchemist = 0 — Phase 2 not yet run.
- Next: rehearse Phases 2–5 end-to-end on a fresh Arbitrum fork. The idempotent preflight will SKIP Phases A–D and Phase 1 automatically.

### optimism / alETH (864 positions) — blocked on Alchemy RPC
- Awaiting Optimism Mainnet network toggle on Alchemy app `49bq0i8n5m6b4hue`. Attempted enable on 2026-04-14 returned 403 `OPT_MAINNET is not enabled for this app`.
- Workaround available: launch anvil against public RPC `https://mainnet.optimism.io`. Slower but functional.

### optimism / alUSD (3624 positions) — largest combo; blocked on Alchemy RPC
- Same Optimism Alchemy blocker as alETH.
- CSV stats: 463 debt users, 3161 credit users, zero zero-debt. Very credit-heavy — Phase 5 (credit) will be a large batch.

### mainnet / alETH (714 positions) — same admin-mismatch issue as mainnet alUSD
- Preflight + Phases A–D should work the same as mainnet alUSD (both share admin EOA).
- Phase 1 will hit the same `Unauthorized()` on `setDepositCap` until prerequisite #1 is resolved.

### mainnet / alUSD (1245 positions) — Phases A–D ✅, Phase 1 blocked
- Phases A, B, C, D executed on fork without issue.
- **Phase 1 blocker**: first batch's `setDepositCap(156,846,437,746,317,891,765,790)` call reverts `Unauthorized()`. The V3 alchemist admin is EOA `0xf456A36B04B0951Cd19d6D8aA0c0b3b0a07f9fF2`, not the migration multisig. Arbitrum/Optimism have the migration multisigs as alchemist admins — mainnet is different.
- For fork-only progression: impersonate the EOA, call `setDepositCap` with a sufficient amount, then re-run Phase 1 as the migration multisig.

## Tool bugs — status

| # | Bug | Status | Resolution |
|---|---|---|---|
| 1 | `setDepositCap` called with a value lower than the current live cap — V3 alchemist reverts on downward change. | ✅ **FIXED** | [scripts/deposit.py](scripts/deposit.py) reads live `depositCap()` via new helper in [src/preflight.py](src/preflight.py) `read_deposit_cap()`; passes to [src/gas.py](src/gas.py) `create_deposit_batches` which now only emits `setDepositCap` when cumulative required cap exceeds the live cap (strictly grows). |
| 2 | `ForkImpersonator` `wait_for_transaction_receipt(timeout=60)` too tight under load. | ✅ **FIXED** | [src/executor.py](src/executor.py) now honors `FORK_RECEIPT_TIMEOUT` env var (default 300 s) and `FORK_HTTP_TIMEOUT` (default 120 s). Bumped to 900 s in heavy distribute/credit phases via inline env override. |
| 3 | Arbitrum alETH CSV had a stray leading newline causing `csv.DictReader.fieldnames = []`. | ✅ **FIXED** | [src/validation.py](src/validation.py) `_validate_csv_content` strips leading whitespace before parsing so a blank prefix line no longer silently breaks validation. |
| 4 | Pipelined submit (send all → sweep receipts) caused 300 s receipt stalls when anvil under load. | ✅ **REVERTED** | Pipelining was unsafe — restored per-tx `wait_for_transaction_receipt(poll_latency=0.01)` which is proven correct and only marginally slower. |
| 5 | Per-call `eth_estimateGas` doubled RPC round-trips; gas multiplier 10× was wasteful. | ✅ **FIXED** | [src/executor.py](src/executor.py) drops `eth_estimateGas` and uses a static 5 M gas cap (configurable via `FORK_GAS_PER_CALL`). Anvil refunds unused gas, so overbudgeting is free. |
| 6 | **`alchemist.mint()` reverts `"Alchemist's ceiling was breached"`** on mainnet because V3 alchemist's ceiling on the alToken defaults to 0 — Phase D was only doing `setWhitelist`. | ✅ **FIXED** | [scripts/set_whitelist.py](scripts/set_whitelist.py) now also emits `setCeiling(V3_alchemist, 10^30)`. Phase D is now a 3-call Safe batch on mainnet (was 2). Validated end-to-end: mainnet alUSD mint produced exact `+1,734,889.41 alUSD` delta matching CSV total. |
| 7 | Mid-checkpoint `click.confirm("Verified first batch. Continue with remaining?")` ignored `--yes` flag → exit 1 from /dev/null stdin. | ✅ **FIXED** | Added `if not yes and not click.confirm(...)` guard in `mint.py`, `distribute.py`, `credit.py`, `deposit.py`. Non-interactive runs now bypass mid-checkpoint prompts when `--yes` is set. |
| 8 | `csv.DictReader` opaque error if CSV has missing column. | ✅ **PARTIAL** | Validator now reports specific field name. |

## Blocker log

| Date | Chain / Asset | Phase | Issue | Status |
|---|---|---|---|---|
| 2026-04-14 | arbitrum / alETH | Phase 2 (mint) | CSV row 105: `0x5cA51c...` debt/collateral = 206% > 90% V3 LTV cap | Tabled — business decision |
| 2026-04-14 | mainnet (alUSD + alETH) | Phase 1 (deposit) | `setDepositCap()` reverts `Unauthorized()`. Mainnet alchemist admin is EOA `0xf456A36B04B0951Cd19d6D8aA0c0b3b0a07f9fF2`, not the migration multisig. | **Resolution identified**: `pendingAdmin()` on both mainnet alchemists already returns the migration multisig — EOA already called `setPendingAdmin`. Finalize by having migration multisig call `acceptAdmin()` on each. See Prereq 1a/1b above. Fork rehearsal used the equivalent impersonated flow and Phase 1 then ran 17 batches successfully on mainnet alUSD. |
| 2026-04-14 | optimism (alUSD + alETH) | RPC | Optimism Mainnet not enabled on Alchemy app `49bq0i8n5m6b4hue`. | ✅ Resolved — enabled on Alchemy dashboard. |
| 2026-04-14 | arbitrum / alETH | CSV | Data file gained a leading newline, breaking `csv.DictReader.fieldnames`. | ✅ Stripped + validator hardened. |
| 2026-04-14 | arbitrum / alUSD | Phase 1 | `setDepositCap()` reverts because tool computes a cap lower than current live cap. | ✅ Tool bug #1 fixed — emits setDepositCap only when cap must grow. |
| 2026-04-14 | parallel rehearsal | fork infra | 3 concurrent anvils caused `TimeExhausted` on `wait_for_transaction_receipt(timeout=60)`. | ✅ Now sequential. Timeout configurable via `FORK_RECEIPT_TIMEOUT`. |
| 2026-04-14 | mainnet alUSD | Phase 2 mint | `Alchemist's ceiling was breached` — V3 alchemist had ceiling=0 on alToken; Phase D didn't set it. | ✅ Tool bug #6 fixed — Phase D now includes `setCeiling(V3, 10^30)`. mainnet alUSD mint then produced exact 1,734,889.41 alUSD delta. |
| 2026-04-14 | mainnet alUSD | Phase 4 distribute | Mid-batch one tx receipt timed out at 300 s (Alchemy upstream stall). | ✅ Mitigated by `FORK_RECEIPT_TIMEOUT=900`; halt-on-failure wraps `set -e` in rehearsal scripts to surface immediately. |
| 2026-04-14 | mainnet/arb alETH | row 105 (arb alETH) | User `0x5cA51c0B...3467` had debt 206% of collateral — exceeds V3's 90% LTV cap. | ✅ Removed from CSV. User's V2 debt forgiven; not migrated. |

## Alchemist admin summary

| Chain | Current `admin()` | `pendingAdmin()` | Status |
|---|---|---|---|
| mainnet | `0xf456A36B04B0951Cd19d6D8aA0c0b3b0a07f9fF2` (EOA) | **migration multisig queued** (`0xF56D660138815fC5d7a06cd0E1630225E788293D`) | ⏳ Awaiting `acceptAdmin()` from migration multisig (Prereq 1a/1b) |
| optimism | `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d` | — | ✅ Already migration multisig |
| arbitrum | `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b` | — | ✅ Already migration multisig |

## Active test order (revised 2026-04-14 evening)

1. **arb alUSD** (in-flight): late-phase test — mint ✅, verify ✅, distribute 🟡, credit ⬜. Validates Phases 2-5 against live post-Phase-1 state, fastest path to Phase 4/5 confirmation.
2. **arb alETH** (next): full A→5 on same arb anvil. Row 105 removed (375 positions). Should now run clean end-to-end.
3. **mainnet** (after arb): fresh fork, full A→5 both assets with `setCeiling` in Phase D + 900 s receipt timeout.
4. **optimism** (last): biggest combo (3624 pos alUSD); full A→5 both assets.

## Rehearsal status — phase coverage proven (rolling)

**Phase 2 (mint) PROVEN end-to-end** for the first time on mainnet alUSD: alToken `totalSupply` increased by exactly `1,734,889.41 alUSD` (matches CSV total mint amount). Multisig holds the freshly-minted alUSD pending Phase 5 distribution.

**Phase 3 (verify) PROVEN** on mainnet alUSD + arb alUSD: position state matches snapshot.

**Phase 4 (distribute) PARTIAL**:
- mainnet alUSD: 232/1245 NFTs transferred before fork-receipt timeout (now mitigated by `FORK_RECEIPT_TIMEOUT=900`)
- arb alUSD: in-flight at the time of this update — 8 batches × ~192 NFT transfers each.

**Phase 5 (credit) NOT YET EXERCISED**.

### What still must run before Epoch 2 closes

1. arb alUSD: complete Phases 4 + 5 (in-flight)
2. arb alETH: full A→5 (now unblocked by row 105 removal)
3. mainnet: full A→5 for both assets (need to re-establish fork; previous run cut off mid-Phase-4 distribute)
4. optimism: full A→5 for both assets — last because biggest combo (3624 pos)
5. Regenerate `out/` Safe-Builder JSONs to reflect:
   - row 105 removal on arb alETH (375 deposit calls instead of 376)
   - Phase D 3-call shape (setWhitelist V2/V3 + setCeiling V3) on mainnet
6. Update [SIGNING_GUIDE_PRE_DEPOSIT.md](SIGNING_GUIDE_PRE_DEPOSIT.md) Phase D section to include `setCeiling`
