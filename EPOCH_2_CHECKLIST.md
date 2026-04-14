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

| Chain / Asset | validate | preview | A (approve_u) | B (deposit_myt) | C (approve_myt) | D (set_whitelist) | 1 (deposit) | read_ids | 2 (mint) | 3 (verify) | 4 (distribute) | 5 (credit) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| arbitrum / alETH (376 pos) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 376 ids @ 452,520,580 | ⚠️ tabled (row 105) | ⬜ | ⬜ | ⬜ |
| arbitrum / alUSD (1417 pos) | ⬜ | ⬜ | ⏭️ | ⏭️ | ⏭️ | ⏭️ | ⚠️ setDepositCap revert (tool bug #1) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| optimism / alETH (864 pos) | ⬜ | ⬜ | ✅ | ✅ | ✅ | ✅ | ⚠️ interrupted mid-run | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| optimism / alUSD (3624 pos) | ⬜ | ⬜ | ✅ | ✅ | ✅ | ✅ | ⚠️ interrupted mid-run (batch 34/48) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mainnet / alETH (714 pos) | ✅ | ⬜ | ✅ | ✅ | ✅ | ✅ | ✅ (10 batches on fork; Prereq 1b in prod) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mainnet / alUSD (1245 pos) | ✅ | ⬜ | ✅ | ✅ | ✅ | ✅ | ✅ (17 batches on fork; Prereq 1a in prod) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## Production prerequisites (from rehearsal findings)

Things the Alchemix team must do **before** each chain/asset combo can run in production, independent of this migration tool:

| # | Chain | Required prerequisite | Who signs | Status |
|---|---|---|---|---|
| 1a | mainnet | **`acceptAdmin()` on V3 alUSD alchemist** `0xeB83112d925268BeDe86654C13D423a987587e3E`. Already-queued: `pendingAdmin()` returns the migration multisig — this single call finalizes the handover. | Mainnet migration multisig `0xF56D660138815fC5d7a06cd0E1630225E788293D` | ⬜ |
| 1b | mainnet | **`acceptAdmin()` on V3 alETH alchemist** `0xfa995B6ABc387376C3e7De5f6d394Ab5B6beE26B`. Same setup as 1a — pendingAdmin already points at migration multisig. | Mainnet migration multisig `0xF56D660138815fC5d7a06cd0E1630225E788293D` | ⬜ |
| 2 | mainnet | **Phase D setWhitelist** on alUSD + alETH: revoke V2, grant V3. Two ADMIN_ROLE holders on each alToken — can sign with either. | ETH Ops Multisig `0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9` OR `0x8392F6669292fA56123F71949B52d883aE57e225` | ⬜ |
| 3 | optimism | **Phase D setWhitelist** on alUSD + alETH: revoke V2, grant V3. | OP Ops Multisig `0xC224bf25Dcc99236F00843c7D8C4194abE8AA94a` | ⬜ |
| 4 | arbitrum | **Phase D setWhitelist** on alETH only (alUSD already done). | ARB Ops Multisig `0x7e108711771DfdB10743F016D46d75A9379cA043` | ⬜ |
| 5 | arbitrum | **Row 105 policy decision** (underwater user `0x5cA51c0Bb6DbDf29465DAEB3F5Dbd37074133467`): skip, cap at 90%, or halt. | Alchemix team | ⬜ |

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

## Tool bugs surfaced in rehearsal

| # | Bug | Where | Impact | Fix |
|---|---|---|---|---|
| 1 | `setDepositCap` called with a value lower than the current live cap — V3 alchemist reverts `Unauthorized()`-style on downward change. Hits chains where deposits are already partially or fully done (arbitrum alUSD). | `src/gas.py::create_deposit_batches` starts `current_cap = current_deposit_cap_wei` (default `0`) and sets `new_cap = current_cap + batch_deposit_sum`. Live cap may already exceed that. | Blocks Phase 1 rerun on any chain where deposits are already partially complete, including arbitrum alUSD on-chain state. | Read on-chain `depositCap()` before batching; use `max(current_on_chain_cap, computed_new_cap)`, or skip the `setDepositCap` call entirely when on-chain cap is already sufficient. |
| 2 | `ForkImpersonator` uses `wait_for_transaction_receipt(timeout=60)` — too tight under concurrent fork load. | `src/executor.py::ForkImpersonator.propose_all_batches` | Caused spurious `TimeExhausted` errors in the first parallel rehearsal (3 chains × anvil). No effect on production execution (uses Safe API), only on fork testing. | Bump to 300s (or longer when many concurrent forks). |
| 3 | Arbitrum alETH CSV had a stray leading newline (mtime 2026-04-14 17:49), causing `csv.DictReader.fieldnames = []` and validation to fail with "Required column 'address' is missing from CSV header". | `data/alETHValues-sum-and-debt-arbitrum.csv` | Not a tool bug — a data corruption. Would need manual detection or a validator that tolerates leading blank lines. | Stripped with `sed -i '/./,$!d'`. Backup at `/tmp/alETH-arbitrum.csv.bak`. Consider adding a validator pass that rejects leading blank lines with a clear message, or that strips them. |

## Blocker log

| Date | Chain / Asset | Phase | Issue | Status |
|---|---|---|---|---|
| 2026-04-14 | arbitrum / alETH | Phase 2 (mint) | CSV row 105: `0x5cA51c...` debt/collateral = 206% > 90% V3 LTV cap | Tabled — business decision |
| 2026-04-14 | mainnet (alUSD + alETH) | Phase 1 (deposit) | `setDepositCap()` reverts `Unauthorized()`. Mainnet alchemist admin is EOA `0xf456A36B04B0951Cd19d6D8aA0c0b3b0a07f9fF2`, not the migration multisig. | **Resolution identified**: `pendingAdmin()` on both mainnet alchemists already returns the migration multisig — EOA already called `setPendingAdmin`. Finalize by having migration multisig call `acceptAdmin()` on each. See Prereq 1a/1b above. Fork rehearsal used the equivalent impersonated flow and Phase 1 then ran 17 batches successfully on mainnet alUSD. |
| 2026-04-14 | optimism (alUSD + alETH) | RPC | Optimism Mainnet not enabled on Alchemy app `49bq0i8n5m6b4hue` (`OPT_MAINNET is not enabled`). | ✅ Resolved — enabled on Alchemy dashboard; anvil forks cleanly from `opt-mainnet.g.alchemy.com`. |
| 2026-04-14 | arbitrum / alETH | CSV | Data file `alETHValues-sum-and-debt-arbitrum.csv` gained a leading newline, breaking `csv.DictReader.fieldnames`. | ✅ Stripped with `sed -i`; backup at `/tmp/alETH-arbitrum.csv.bak`. |
| 2026-04-14 | arbitrum / alUSD | Phase 1 | `setDepositCap()` reverts because tool computes a cap lower than the current live cap. | Tool bug #1 above; pending fix. |
| 2026-04-14 | parallel rehearsal | fork infra | 3 concurrent anvils on one machine caused `TimeExhausted` on `wait_for_transaction_receipt(timeout=60)` during heavy deposit batches. | Resolved by running rehearsals sequentially (one fork at a time). Timeout-bump recommended (tool bug #2). |

## Alchemist admin summary

| Chain | Current `admin()` | `pendingAdmin()` | Status |
|---|---|---|---|
| mainnet | `0xf456A36B04B0951Cd19d6D8aA0c0b3b0a07f9fF2` (EOA) | **migration multisig queued** (`0xF56D660138815fC5d7a06cd0E1630225E788293D`) | ⏳ Awaiting `acceptAdmin()` from migration multisig (Prereq 1a/1b) |
| optimism | `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d` | — | ✅ Already migration multisig |
| arbitrum | `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b` | — | ✅ Already migration multisig |

## Rollout order (smallest → largest blast radius)

Same as the top-level CHECKLIST:
1. Arbitrum alETH (376 positions) — 🟡 through Phase 1 + read_ids; Phase 2 tabled (row 105)
2. Arbitrum alUSD (1417) — ⚠️ tool bug #1 (setDepositCap lowering)
3. Optimism alETH (864) — Phases A–D ✅; Phase 1 interrupted
4. Mainnet alETH (714) — ✅ Phase 1 on fork; prod needs Prereq 1b
5. Mainnet alUSD (1245) — ✅ Phase 1 on fork; prod needs Prereq 1a
6. Optimism alUSD (3624) — Phases A–D ✅; Phase 1 interrupted at batch 34/48

## Rehearsal status as of 2026-04-14 (stopped early)

**Completed on fork (Phase 1 + earlier phases):**
- mainnet alUSD through Phase 1 (17 batches, 1245 NFTs)
- mainnet alETH through Phase 1 (10 batches, 714 NFTs)
- arbitrum alETH through Phase 1 + read_ids (376 NFTs, token IDs captured)
- optimism alUSD + alETH through Phase D (A, B, C, D all ✅)

**Not yet exercised on any fork**:
- Phase 2 (mint): attempted on arbitrum alETH only — hit row 105 underwater
- Phase 3 (verify): not yet run anywhere
- Phase 4 (distribute): not yet run anywhere
- Phase 5 (credit): not yet run anywhere
- Optimism Phase 1 (aborted mid-batch)

**Why stopped early:** 3-chain parallel rehearsal saturated anvil I/O. Reverted to sequential. Mainnet done, Optimism mid-Phase-1, Arbitrum not started sequentially. User stopped the run to avoid further wall-clock cost.

**What's needed to finish Epoch 2 when work resumes:**
1. Fix tool bug #1 (`create_deposit_batches` setDepositCap should not lower existing cap) before re-running Arbitrum alUSD.
2. Decide Arbitrum alETH row 105 policy (skip / cap / halt) before running Phase 2 anywhere.
3. Re-run full A→5 sequence per chain in this order: **mainnet** (re-establish fork state + admin accept), **optimism** (fresh run), **arbitrum** (only alETH unless bug #1 fixed).
4. Each full chain rehearsal is ~15–30 min depending on combo sizes; expect 1–2 hr total sequentially.
