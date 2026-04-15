import src.env  # Load .env on startup
#!/usr/bin/env python3
"""Phase 4: Transfer NFTs from multisig to users.

Usage:
    ape run distribute --chain mainnet --asset usd
    ape run distribute --chain mainnet --asset usd --dry-run

Run AFTER `ape run verify` confirms positions are correct.
"""

import click
from ape.cli import ape_cli_context

from src.config import (
    ChainConfigError,
    get_asset_config,
    get_chain_config,
    get_csv_path,
    get_supported_chains,
    load_token_id_map,
    validate_asset_config,
    verify_asset_config,
)
from src.gas import create_transfer_batches, format_batch_summary, verify_batch_gas_limits
from src.executor import make_executor
from src.safe import ProposeToSafe, format_safe_batch  # ProposeToSafe kept for legacy --mode propose
from src.types import AssetType
from src.validation import format_validation_errors, validate_csv_file


@click.command()
@click.option("--chain", type=click.Choice(get_supported_chains()), required=True)
@click.option("--asset", type=click.Choice(["usd", "eth"]), required=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--yes", "-y", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--mode", type=click.Choice(["json", "impersonate", "propose"]), default="json")
@click.option("--resume", is_flag=True, default=False,
              help="Skip positions whose NFT is already at the user (e.g. after a partial run).")
@ape_cli_context()
def cli(
    cli_ctx,
    chain: str,
    asset: str,
    verbose: bool,
    yes: bool,
    dry_run: bool,
    mode: str,
    resume: bool,
) -> None:
    """Phase 4: Transfer NFTs from multisig to users."""
    asset_type = AssetType.USD if asset == "usd" else AssetType.ETH

    click.echo("=" * 70)
    click.echo(click.style("ALCHEMIX V3 MIGRATION — DISTRIBUTE NFTs", fg="white", bold=True))
    click.echo("=" * 70)
    click.echo(f"Chain:  {click.style(chain, fg='cyan')}")
    click.echo(f"Asset:  {click.style(asset_type.value, fg='cyan')}")
    if dry_run:
        click.echo(click.style("Mode:   DRY RUN", fg="yellow"))

    chain_config = get_chain_config(chain)
    asset_config = get_asset_config(chain, asset_type)
    multisig = chain_config["multisig"]

    click.echo(f"Multisig: {multisig or click.style('<not configured>', fg='yellow')}")
    click.echo("-" * 70)

    csv_path = get_csv_path(chain, asset_type)
    if not csv_path.exists():
        click.echo(click.style(f"\nError: CSV not found: {csv_path}", fg="red"))
        raise SystemExit(1)
    click.echo(f"Data file: {csv_path}")

    # Validate CSV
    click.echo(click.style("\n[1/4] Validating CSV...", fg="cyan", bold=True))

    myt_decimals = asset_config.get("myt_decimals", 18)
    result = validate_csv_file(csv_path, chain, asset_type, myt_decimals=myt_decimals)

    if not result.is_valid:
        click.echo(click.style(format_validation_errors(result.errors), fg="red"))
        click.echo(click.style("Aborted: CSV validation failed.", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("Validation OK", fg="green"))
    click.echo(f"  Total positions: {result.total_positions}")

    if not result.positions:
        click.echo(click.style("No positions found.", fg="yellow"))
        raise SystemExit(0)

    # Load token ID mapping
    try:
        token_id_map = load_token_id_map(chain, asset_type)
    except FileNotFoundError as e:
        if not dry_run:
            click.echo(click.style(f"\nError: {e}", fg="red"))
            raise SystemExit(1)
        token_id_map = None
        click.echo(click.style("Warning: no token ID map — transfers will use placeholder 999999", fg="yellow"))

    if token_id_map is not None:
        click.echo(f"Loaded {len(token_id_map)} token IDs from mapping")

    if not dry_run:
        try:
            verify_asset_config(chain, asset_type)
        except ChainConfigError as e:
            click.echo(click.style(f"\nError: {e}", fg="red"))
            click.echo(click.style("Use --dry-run to test without configured addresses.", fg="blue"))
            raise SystemExit(1)
    else:
        missing = validate_asset_config(chain, asset_type)
        if missing:
            click.echo(click.style(f"Warning: missing config: {', '.join(missing)}", fg="yellow"))

    nft = asset_config.get("nft", "") or "0x" + "0" * 40

    # --resume: query ownerOf(tokenId) for each position; drop the ones whose
    # NFT is already at the user (already-distributed). Targets the FORK_RPC_URL
    # if set, else the chain's default Alchemy RPC. Read-only.
    positions_to_distribute = result.positions
    if resume and token_id_map is not None:
        click.echo(click.style("\n[1.5/4] --resume: filtering already-distributed positions...", fg="cyan", bold=True))
        import os
        from web3 import Web3
        from eth_utils import keccak
        from eth_abi import encode, decode
        from src.preflight import _rpc_url
        rpc_url = os.environ.get("FORK_RPC_URL") or _rpc_url(chain)
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 60}))
        owner_sel = keccak(text="ownerOf(uint256)")[:4]
        kept: list = []
        already: int = 0
        for p in result.positions:
            tid = token_id_map.get(p.user_address.lower())
            if tid is None:
                kept.append(p)
                continue
            try:
                raw = w3.eth.call({
                    "to": Web3.to_checksum_address(nft),
                    "data": "0x" + (owner_sel + encode(["uint256"], [tid])).hex(),
                })
                cur_owner = decode(["address"], raw)[0]
            except Exception:
                kept.append(p)
                continue
            if cur_owner.lower() == p.user_address.lower():
                already += 1
            else:
                kept.append(p)
        click.echo(f"  already at user: {already} of {len(result.positions)}")
        click.echo(f"  remaining to transfer: {len(kept)}")
        positions_to_distribute = kept
        if not positions_to_distribute:
            click.echo(click.style("All NFTs already distributed. Nothing to do.", fg="yellow"))
            raise SystemExit(0)

    # Build transfer batches
    click.echo(click.style("\n[2/4] Building transfer batches...", fg="cyan", bold=True))

    batches = create_transfer_batches(
        positions=positions_to_distribute,
        nft_address=nft,
        multisig=multisig,
        token_id_map=token_id_map,
        chain=chain,
    )

    ok, errors = verify_batch_gas_limits(batches, chain=chain)
    if not ok:
        for err in errors:
            click.echo(click.style(f"  {err}", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(f"Transfer batches: {len(batches)}", fg="green"))
    for batch in batches:
        click.echo(f"  Batch {batch.batch_number}: {len(batch.calls)} txns, {batch.total_gas:,} gas")
        if verbose:
            for call in batch.calls[:5]:
                click.echo(f"    {call.description[:90]}")
            if len(batch.calls) > 5:
                click.echo(f"    ... +{len(batch.calls) - 5} more")

    # Preview
    click.echo(click.style("\n[3/4] Batch summary...", fg="cyan", bold=True))
    click.echo(format_batch_summary(batches, chain=chain))

    # Confirm + Execute
    click.echo(click.style("\n[4/4] Confirmation...", fg="cyan", bold=True))
    if not yes:
        click.echo(
            click.style("\nWARNING: ", fg="red", bold=True) +
            f"About to propose {len(batches)} NFT transfer Safe tx(s) on {chain} ({asset_type.value})."
        )
        if dry_run:
            click.echo(click.style("DRY RUN: skipping actual submission.", fg="yellow"))
        elif not click.confirm("Proceed with NFT transfers?"):
            click.echo(click.style("Cancelled.", fg="yellow"))
            raise SystemExit(0)

    if dry_run:
        click.echo(click.style("\nDRY RUN: skipping Safe proposal.", fg="yellow"))
        for batch in batches:
            click.echo(
                f"  [transfer ] Batch {batch.batch_number}: "
                f"{len(batch.calls)} txns, {batch.total_gas:,} gas"
            )
        click.echo(click.style("\nDry run complete. Run without --dry-run to execute.", fg="blue"))
        return

    chain_id = chain_config["chain_id"]
    safe_txs = format_safe_batch(batches, chain_id=chain_id)
    proposer = make_executor(
        mode, batches=batches, safe_address=multisig, chain_id=chain_id,
        chain=chain, asset_type=asset_type, step_name="distribute",
    )

    # Checkpoint mode: propose first batch, pause for verification, then continue
    all_results = []
    first_batch = [safe_txs[0]]
    remaining_batches = safe_txs[1:]

    click.echo(click.style("\n[CHECKPOINT] Proposing first batch...", fg="yellow", bold=True))
    first_results = proposer.propose_all_batches(first_batch)
    all_results.extend(first_results)

    first_ok = sum(1 for r in first_results if r.get("status") in ("success", "stubbed"))
    if first_ok == 0:
        click.echo(click.style("First batch proposal failed. Aborting.", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(
        "\n[CHECKPOINT] First batch proposed. Verify in Safe UI before continuing.",
        fg="yellow", bold=True,
    ))
    click.echo(f"  Safe: https://app.safe.global/transactions/queue?safe=eth:{multisig}")
    click.echo(f"  Verify: cross-reference the CSV data in the batch calldata.")
    click.echo(f"  Remaining batches: {len(remaining_batches)}")

    if not yes and not click.confirm(click.style("Verified first batch. Continue with remaining?", fg="yellow")):
        click.echo(click.style("Aborted. First batch still proposed — cancel in Safe UI if needed.", fg="red"))
        raise SystemExit(1)

    if remaining_batches:
        click.echo(click.style("\nProposing remaining batches...", fg="cyan"))
        remaining_results = proposer.propose_all_batches(remaining_batches)
        all_results.extend(remaining_results)

    ok_count = sum(1 for r in all_results if r.get("status") in ("success", "stubbed"))
    fail_count = len(all_results) - ok_count

    status = (
        click.style("SUCCESS", fg="green", bold=True) if fail_count == 0
        else click.style(f"PARTIAL ({ok_count}/{len(all_results)})", fg="yellow", bold=True)
    )

    click.echo(f"\nStatus: {status}")
    click.echo(f"Proposed: {ok_count}/{len(all_results)} transfer batches")
    click.echo(click.style(
        f"\nNext: run `ape run credit --chain {chain} --asset {asset}` to send credits.",
        fg="cyan",
    ))

    if fail_count > 0:
        raise SystemExit(1)
