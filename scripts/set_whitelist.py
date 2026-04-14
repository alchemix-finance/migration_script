import src.env  # load .env
#!/usr/bin/env python3
"""Phase D: Swap the alToken minter whitelist from V2 → V3 alchemist.

Usage:
    ape run set_whitelist --chain arbitrum --asset eth --mode json
    ape run set_whitelist --chain arbitrum --asset eth --mode impersonate

The V3 alchemist cannot mint alAssets until the alToken owner calls:
    alToken.setWhitelist(V2_alchemist, false)
    alToken.setWhitelist(V3_alchemist, true)

This script emits both calls as a Safe batch. The SIGNER of these calls is
the alToken owner (different per chain — see src/myt_config.py
AL_TOKEN_OWNER) — NOT the migration multisig. Make sure the JSON is uploaded
to the correct Safe UI.
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    ChainConfigError,
    get_asset_config,
    get_chain_config,
    get_supported_chains,
    verify_asset_config,
)
from src.executor import make_executor
from src.gas import format_batch_summary, verify_batch_gas_limits
from src.myt_config import AL_TOKEN_OWNER, V2_ALCHEMIST, WHITELIST_ACCESSOR
from src.safe import format_safe_batch
from src.transactions import build_erc20_approve_tx  # selector encoding helper re-used via Any ABI
from src.types import AssetType, TransactionBatch, TransactionCall


def _encode_set_whitelist(target: str, state: bool) -> bytes:
    """Encode setWhitelist(address,bool)."""
    from src.transactions import encode_function_call
    abi = [{
        "type": "function", "name": "setWhitelist", "stateMutability": "nonpayable",
        "inputs": [{"name": "target", "type": "address"}, {"name": "state", "type": "bool"}],
        "outputs": [],
    }]
    return encode_function_call(abi, "setWhitelist", [target, state])


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--mode", type=click.Choice(["json", "impersonate", "propose"]), default="json")
@click.option("--yes", "-y", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--verbose", "-v", is_flag=True, default=False)
@ape_cli_context()
def cli(cli_ctx, chain: str, asset: str, mode: str, yes: bool, dry_run: bool, verbose: bool) -> None:
    """Revoke whitelist from V2 alchemist, grant to V3 alchemist on the alToken."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH
    asset_slug = "alUSD" if asset_type == AssetType.USD else "alETH"

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — PHASE D (alToken minter whitelist swap)",
                            fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain: {click.style(chain, fg='cyan')}  Asset: {click.style(asset_slug, fg='cyan')}  Mode: {click.style(mode, fg='magenta', bold=True)}")

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)

    al_token = asset_config["al_token"]
    v3_alchemist = asset_config["alchemist"]
    v2_alchemist = V2_ALCHEMIST[chain][asset_slug]
    owner = AL_TOKEN_OWNER[chain]
    accessor = WHITELIST_ACCESSOR[chain]

    click.echo(f"alToken:       {al_token}")
    click.echo(f"Owner (signer): {owner}")
    click.echo(f"V2 alchemist (revoke): {v2_alchemist}")
    click.echo(f"V3 alchemist (grant):  {v3_alchemist}")
    click.echo("-" * 70)

    # Preflight: read on-chain whitelist state.
    try:
        from src.preflight import check_whitelist_transition_done
        done, msg, state = check_whitelist_transition_done(
            chain=chain, al_token=al_token,
            v2_alchemist=v2_alchemist, v3_alchemist=v3_alchemist,
            accessor=accessor,
        )
        click.echo(click.style("\n[1/3] On-chain whitelist state:", fg="cyan", bold=True))
        click.echo(f"  {msg}")
        if done:
            click.echo(click.style("SKIPPED — transition already complete on-chain.", fg="yellow", bold=True))
            return
    except Exception as e:
        click.echo(click.style(f"  preflight check failed ({e}); proceeding.", fg="yellow"))
        state = {"v2_whitelisted": True, "v3_whitelisted": False}  # assume worst case

    if not dry_run:
        try:
            verify_asset_config(chain, asset_type)
        except ChainConfigError as e:
            click.echo(click.style(f"Config error: {e}", fg="red"))
            raise SystemExit(1)

    # Build the 2-call batch: skip the revoke if V2 isn't actually whitelisted.
    click.echo(click.style("\n[2/3] Building setWhitelist batch...", fg="cyan", bold=True))
    batch = TransactionBatch(batch_number=1, batch_type="set_whitelist")
    if state["v2_whitelisted"]:
        batch.add_call(TransactionCall(
            to=al_token,
            data=_encode_set_whitelist(v2_alchemist, False),
            value=0,
            gas_estimate=55_000,
            description=f"setWhitelist({v2_alchemist}, false) — revoke V2",
        ))
    else:
        click.echo("  V2 already not whitelisted — skipping revoke call.")
    if not state["v3_whitelisted"]:
        batch.add_call(TransactionCall(
            to=al_token,
            data=_encode_set_whitelist(v3_alchemist, True),
            value=0,
            gas_estimate=55_000,
            description=f"setWhitelist({v3_alchemist}, true) — grant V3",
        ))
    else:
        click.echo("  V3 already whitelisted — skipping grant call.")
    if not batch.calls:
        click.echo(click.style("Nothing to do.", fg="yellow", bold=True))
        return

    batches = [batch]
    ok, errors = verify_batch_gas_limits(batches, chain=chain)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)
    click.echo(format_batch_summary(batches, chain=chain))
    for call in batch.calls:
        click.echo(f"  → {call.description}")

    click.echo(click.style("\n[3/3] Execution...", fg="cyan", bold=True))
    if dry_run:
        click.echo(click.style("DRY RUN — not submitting.", fg="yellow"))
        return
    if not yes and not click.confirm(f"Proceed with {mode}? (signer must be {owner})"):
        click.echo("Cancelled.")
        raise SystemExit(0)

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(batches, chain_id=chain_id)
    executor = make_executor(
        mode,  # type: ignore[arg-type]
        batches=batches,
        safe_address=owner,  # NOTE: alToken owner, not migration multisig
        chain_id=chain_id,
        chain=chain,
        asset_type=asset_type,
        step_name="set_whitelist",
    )
    results = executor.propose_all_batches(safe_txs)
    ok_count = sum(1 for r in results if r.get("status") in ("success", "stubbed"))
    status = click.style("SUCCESS", fg="green", bold=True) if ok_count == len(results) else click.style("PARTIAL", fg="yellow", bold=True)
    click.echo(f"\nStatus: {status}  ({ok_count}/{len(results)})")
    for r in results:
        if r.get("path"):
            click.echo(f"  JSON: {r['path']}")
