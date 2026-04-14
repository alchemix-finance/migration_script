# CDP Migration — Full Action Checklist

> **Terminology**
> - **Epoch** = a stage in _our work_ on this tool (prep, code changes, dry run, production, etc.). Replaces earlier "Phase 0 / 1 / 1.5 / 2 / 3 / 4 / 5" naming.
> - **Phase** = an actual on-chain action in the migration. The original spec had five: **Phase 1** (deposit) → **Phase 2** (mint) → **Phase 3** (verify) → **Phase 4** (distribute) → **Phase 5** (credit). We added pre-deposit prerequisites, labelled **Phase A / B / C / D**, that run before Phase 1 and Phase 2 respectively.
>
> **Migration phase map**
> | Phase | Action | Script |
> |---|---|---|
> | **A** | Approve underlying → MYT | `approve_underlying.py` |
> | **B** | Deposit underlying into MYT vault | `deposit_myt.py` |
> | **C** | Approve MYT → Alchemist | `approve_myt.py` |
> | **D** | Set alToken minter whitelist (V2 → V3) | `set_whitelist.py` |
> | **1** | Alchemist deposit (creates NFT positions) | `deposit.py` |
> | **2** | Mint alAssets for debt users | `mint.py` |
> | **3** | Verify positions match snapshot | `verify.py` |
> | **4** | Distribute NFTs to users | `distribute.py` |
> | **5** | Credit alAssets to credit users | `credit.py` |
>
> Phase D can be executed at any time before Phase 2, and is signed by a different Safe (the alToken owner) than Phases A/B/C/1/2/4/5 (which are signed by the migration multisig). See [SET_WHITELIST_REFERENCE.md](SET_WHITELIST_REFERENCE.md) for Phase D details.

## Epoch 0: Environment & Config Prep ✅
- [x] Fix `.env` parse errors on lines 37–39
    - _Reason_: `dotenv` was failing to parse three commented-by-indentation URLs as `KEY=VALUE`. Prefixed with `#` so the loader skips them.
- [x] Alchemy key sourced from shell `WEB3_ALCHEMY_API_KEY` (no `.env` entry needed)
    - _Reason_: user already has the key set at system level; duplicating it in `.env` would go stale and add a rotation hazard.
- [x] Confirmed proposer private key NOT needed — production uses JSON upload to Safe UI
    - _Reason_: production path uploads Safe Transaction Builder JSON to the UI; multisig owners sign there. A proposer key would be a no-op and an unnecessary secret to manage.
- [x] Fetched MYT vault + underlying token addresses for all 6 chain/asset combos
    - _Reason_: the dashboard JS bundle gave vault+alchemist+transmuter+allocator; underlyings had to come from the vaults' on-chain `asset()` accessor for authoritativeness.
- [x] Created `src/myt_config.py` with alchemist/transmuter/myt/allocator/underlying per chain/asset
    - _Reason_: one canonical reference including decimals; used by preflight checks and new scripts.
- [x] Documented migration multisigs per chain
- [x] Confirmed `src/config.py` addresses (alchemist, NFT, MYT, al_token) match `src/myt_config.py`; fixed multisig mapping in `src/myt_config.py`
    - _Reason_: my dashboard-bundle parsing extracted context from before each address; it shifted the chain label by one entry. `src/config.py` is authoritative (corroborated by the onchainden Arbitrum Safe URL `arb1:0xee1a…`).

## Epoch 1: Code Changes ✅
- [x] Add `build_erc20_approve_tx()` to `src/transactions.py`
    - _Reason_: `approve(address,uint256)` is standard across all ERC20s, so one builder handles both underlying→MYT (Phase A) and MYT→Alchemist (Phase C). Keeps the builder ABI inline (no new JSON file) since it's trivial.
- [x] Add `build_erc4626_deposit_tx()` to `src/transactions.py`
    - _Reason_: MYT vaults are ERC-4626 with `deposit(assets, receiver)`. Inline ABI over a new JSON file because it's one function and not referenced elsewhere. Used by Phase B.
- [x] Add batching fns to `src/gas.py`:
    - `create_approve_underlying_batches()` / `create_myt_deposit_batches()` / `create_approve_myt_batches()` (Phases A/B/C)
    - `compute_underlying_total()` helper
    - _Reason_: each phase is a single call, not per-user, so each "batch" has one transaction. Returning `list[TransactionBatch]` still keeps the API uniform with `create_deposit_batches` etc. so the executor and preview pipelines don't need special cases. `compute_underlying_total` rescales CSV's 18-decimal `underlyingValue` to the real underlying's decimals (critical for 6-decimal USDC).
- [x] Add `GAS_ERC20_APPROVE` and `GAS_ERC4626_DEPOSIT` constants to `src/config.py`
    - _Reason_: keeps gas estimates centralized alongside existing operation gas constants.
- [x] Create three new scripts: `approve_underlying.py`, `deposit_myt.py`, `approve_myt.py` (Phases A/B/C)
    - _Reason_: user chose one-script-per-phase to match existing convention and Safe UI upload granularity. Each script mirrors `credit.py`'s validate → build → preview → confirm → execute shape.
- [x] Implement Safe Transaction Builder JSON export (`JsonExporter` in `src/executor.py`)
    - _Reason_: this is the production dispatch path. Flat transaction entries (not delegatecall-packed multisend) so the Safe UI preview stays human-readable and reviewers don't have to decode packed bytes.
- [x] Implement fork impersonation executor (`ForkImpersonator` in `src/executor.py`)
    - _Reason_: fork rehearsals need direct execution as the multisig; ape's account auto-impersonation on foundry/anvil forks makes this a drop-in alternative to real Safe signing.
- [x] Implement `make_executor(mode, ...)` factory in `src/executor.py`
    - _Reason_: swap target for existing scripts' one-line `proposer = ProposeToSafe(...)` — returned object satisfies the same `propose_all_batches(safe_txs)` contract, so script logic is untouched. Cursor-based iteration supports checkpoint flows that call `propose_all_batches([safe_tx])` one at a time.
- [x] Add idempotency preflight in `src/preflight.py`
    - `check_approve_underlying_done`, `check_myt_balance_done`, `check_approve_myt_done`, `check_deposit_done`
    - _Reason_: user flagged that Arbitrum already had partial execution. Preflight reads live chain state via direct web3 RPCs (independent of ape's active network) so identical logic works on fork or production. Each new script short-circuits with "SKIPPED" when the phase is already satisfied (e.g., Arbitrum alUSD has 1417 NFTs → all pre-deposit phases skip).
- [x] Add `--mode {json, impersonate, propose}` flag to `deposit.py`/`mint.py`/`distribute.py`/`credit.py`
    - _Reason_: surgical swap only — new CLI option, new parameter in `cli()`, and one-line construction swap at the executor call site. Keeps validation/batching/checkpoint logic identical to pre-change.
- [x] Fix executor cursor bug
    - _Reason_: existing scripts call `propose_all_batches([safe_tx])` per iteration in checkpoint mode. Initial JsonExporter zipped `self.batches` fresh each call, overwriting batch01 five times. Cursor now advances across calls so each invocation consumes the next N batches.

### Zero-change confirmation for existing scripts
Confirmed via `git diff` across `deposit.py`, `mint.py`, `distribute.py`, `credit.py`. Changes were limited to three surgical categories; the following logic was verified **unchanged**:
- **Validation**: `validate_csv_file`, error printing, halt-on-error, wei scaling, `verify_asset_config`, missing-config warnings.
- **Batching**: `create_*_batches()` calls and arguments, `verify_batch_gas_limits`, per-batch gas/size/calls computation.
- **Confirmation**: `--yes` handling, `click.confirm()` prompts, abort paths, dry-run short-circuit.
- **Checkpoint**: per-batch pauses, Safe UI URL printing, intermediate success/fail counting, cross-reference verification messages, final status printing and exit codes.

Only 3 changes per script:
1. Added `from src.executor import make_executor` import.
2. Added one `@click.option("--mode", ...)` and one `mode: str` parameter to `cli()`.
3. Replaced `proposer = ProposeToSafe(...)` with `proposer = make_executor(mode, batches=batches, ...)`. The returned object satisfies the same `propose_all_batches(safe_txs)` interface, so all downstream call sites are unchanged.

### Still pending
- [x] Extend `src/preview.py` with Phase A/B/C sections for the new pre-deposit phases
    - _Reason_: users need a full plan view that reflects the added phases; also drove adding 3 optional fields to `MigrationPlan` and `myt_address`/`underlying_address` params to `build_migration_plan()` so the preview renders them without forcing every caller to supply them.
- [x] Write tests for new builders, executor, preflight
    - _Reason_: regression safety for selector/decoding, batch builder shape, ceil rescaling for 6-decimal USDC, JSON schema validity, cursor advancement, factory dispatch, preflight surface. Legacy tests in the suite are pre-existing-broken (stale imports for removed symbols) and not in scope here.

## Epoch 1.5: Test Suite Repair ✅
Eight test files were out of sync on clean `main` — pre-existing breakage from `PR1: Project scaffolding` (2026-01-15) that was never re-synced with 17 subsequent src refactor commits. All honored the original test intent by porting to the current V3 API, including direct tests of internal correctness-surface helpers.

- [x] **`tests/test_transactions.py`** — surgical edit: delete `TestBuildBurnTx`, drop `GAS_BURN`/`build_burn_tx` imports. **73 tests pass**.
- [x] **`tests/test_config.py`** — full rewrite against V3 `ChainConfig`/`AssetConfig` nested shape. **42 tests pass.** Surfaced a real defect: `src/config.py` had empty `underlying` fields for mainnet and optimism asset configs, and Arbitrum alUSD had `underlying` mis-set to the MYT address. Fixed in-source.
- [x] **`tests/conftest.py`** — added shared fixtures: `make_position`, `debt_position`, `credit_position`, `zero_debt_position`, `make_call`, `make_batch`, `write_csv`, `project_root`, `sample_csv_content`, `tmp_csv`, `sample_addresses`.
- [x] **`tests/test_types.py`** — ported V1 `usd_debt`/`eth_debt`/`deposit_amount`/`usd_positions` fields to V3 single-asset `underlying_value`/`debt` and `*_wei` suffix. **17 tests pass**.
- [x] **`tests/test_validation.py`** — direct tests of public helpers (`is_valid_eth_address`, `parse_decimal`, `parse_non_negative_decimal`, `validate_headers`, `validate_row`, `convert_to_wei`, `position_from_row`, `validate_csv_string`, `format_validation_errors`) + integration via `validate_csv_file` including all 6 real CSVs. **55 tests pass**.
- [x] **`tests/test_gas.py`** — direct tests of `_batch_calldata_size`, `_can_add_call`, `_gas_deposit`, `_gas_mint` + integration tests for all 7 `create_*_batches` builders + `calculate_batch_statistics`/`verify_batch_gas_limits`/`format_batch_summary`/`build_migration_plan`. **41 tests pass**.
- [x] **`tests/test_multichain.py`** — rewritten against `verify_asset_config`/`validate_asset_config`; 6-fold integration test + chain isolation tests + snapshot position-count spot checks. **63 tests pass**.
- [x] **`tests/test_preview.py`** — direct tests of `_fmt_wei`/`_fmt_gas`/`_addr`/`_batch_row` + `capsys` integration on `print_migration_plan` including the new Phase A/B/C sections. **22 tests pass**.
- [x] **`tests/test_safe.py`** — surgical edits. `test_meta_included` rewritten to assert display-helper fields (V3 moved meta to `serialize_batch_for_display`). 7 network-dependent tests rewritten with `monkeypatch.setenv("SAFE_PROPOSAL_START_NONCE", ...)` to bypass the live Safe API. **52 tests pass**.
- [x] **Verification**: `pytest tests/ -q` → **382 passed, 0 failed, 0 errors** across 10 test files.
- [x] **Verification**: `ape run preview --chain arbitrum --asset eth` renders all Phase A–5 sections. `ape run approve_underlying --chain arbitrum --asset usd --mode json --yes` still short-circuits with "SKIPPED — deposits already complete" per the idempotency preflight.

## Epoch 2: Dry Run (Fork Impersonation) — per chain × asset (6 total)
Order: Arbitrum alETH → Arbitrum alUSD → Optimism alETH → Mainnet alETH → Mainnet alUSD → Optimism alUSD

For each chain × asset (idempotent — phases already done on-chain will SKIP automatically):
- [ ] `ape run validate --chain <c> --asset <a>`
- [ ] `ape run preview --chain <c> --asset <a>`
- [ ] Phase A: `ape run approve_underlying --mode impersonate`
- [ ] Phase B: `ape run deposit_myt --mode impersonate`
- [ ] Phase C: `ape run approve_myt --mode impersonate`
- [ ] Phase D: `ape run set_whitelist --mode impersonate` _(signer = alToken owner, not migration multisig)_
- [ ] Phase 1: `ape run deposit --mode impersonate`
- [ ] `ape run read_ids`
- [ ] Phase 2: `ape run mint --mode impersonate`
- [ ] Phase 3: `ape run verify`
- [ ] Phase 4: `ape run distribute --mode impersonate`
- [ ] Phase 5: `ape run credit --mode impersonate`

## Epoch 3: Generate JSON for Safe UI — per chain × asset
- [ ] Phase A: `approve_underlying --mode json` → `out/<chain>_<asset>_approve_underlying_batch01.json`
- [ ] Phase B: `deposit_myt --mode json` → `out/<chain>_<asset>_deposit_myt_batch01.json`
- [ ] Phase C: `approve_myt --mode json` → `out/<chain>_<asset>_approve_myt_batch01.json`
- [ ] Phase D: `set_whitelist --mode json` → `out/<chain>_<asset>_set_whitelist_batch01.json` _(upload to alToken owner's Safe)_
- [ ] Phase 1: `deposit --mode json` → `out/<chain>_<asset>_deposit_batch0N.json` (multiple batches)
- [ ] Phase 2: `mint --mode json` → `out/<chain>_<asset>_mint_batch0N.json` (after tokenIds known)
- [ ] Phase 4: `distribute --mode json` → `out/<chain>_<asset>_distribute_batch0N.json`
- [ ] Phase 5: `credit --mode json` → `out/<chain>_<asset>_credit_batch0N.json`

## Epoch 4: Production Execution — per chain × asset
No private key — upload JSON to Safe UI, signers execute. Per cycle:
1. [ ] Phase A: Upload + execute: approve underlying → MYT
2. [ ] Phase B: Upload + execute: deposit underlying → MYT (mints MYT to multisig)
3. [ ] Phase C: Upload + execute: approve MYT → alchemist
4. [ ] Phase D: Upload + execute (on alToken-owner Safe): setWhitelist(V2, false) + setWhitelist(V3, true)
5. [ ] Phase 1: Upload + execute: alchemist.deposit batches (creates NFT positions)
6. [ ] Run `read_ids` to capture on-chain tokenIds
7. [ ] Phase 2: Upload + execute: mint batches (debt users)
8. [ ] Phase 3: Run `verify` — halt on mismatch
9. [ ] Phase 4: Upload + execute: distribute NFTs to users
10. [ ] Phase 5: Upload + execute: credit alAsset transfers

## Epoch 5: Post-Migration
- [ ] Final `verify` sweep across all 6 chain/asset combos
- [ ] Reconcile snapshot totals vs on-chain balances
- [ ] Archive `out/` JSONs + logs
- [ ] Announce completion / un-pause or drain old protocol

---

## Reference — Key Addresses
See [src/myt_config.py](src/myt_config.py) for full contract bundles per chain/asset.
See [SET_WHITELIST_REFERENCE.md](SET_WHITELIST_REFERENCE.md) for Phase D details.

**Migration multisigs** (authoritative from [src/config.py](src/config.py)):
- Mainnet:  `0xF56D660138815fC5d7a06cd0E1630225E788293D`
- Optimism: `0x3Dda174aa9E897e18b8E10e6Ce39c2a52398181d`
- Arbitrum: `0xeE1Aa1C3D0622fCeD823c7720cf9E8079558484b`

## Rollout Order (smallest → largest blast radius)
1. Arbitrum alETH (376 positions)
2. Arbitrum alUSD (1417) — **deposits already complete on-chain; preflight skips**
3. Optimism alETH (864)
4. Mainnet alETH (714)
5. Mainnet alUSD (1245)
6. Optimism alUSD (3624)

**Grand total: 8240 positions**
