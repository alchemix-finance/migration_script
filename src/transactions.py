"""Transaction builders for V3 migration.

All functions return TransactionCall objects with encoded calldata.

V3 function signatures:
  AlchemistV3.setDepositCap(uint256 value)
  AlchemistV3.deposit(uint256 amount, address recipient, uint256 tokenId) → uint256
  AlchemistV3.mint(uint256 tokenId, uint256 amount, address recipient)
  ERC721.transferFrom(address from, address to, uint256 tokenId)
  alToken.transfer(address to, uint256 amount) → bool

Key notes:
  - deposit(amount, recipient, 0): tokenId=0 triggers NFT auto-mint to recipient
  - mint(tokenId, amount, multisig): debt goes on position, alAssets to multisig
  - Remaining alAssets in multisig are burned manually by the multisig after migration
"""

from typing import Any

from eth_abi import encode
from eth_utils import keccak

from src.abi import load_alchemist_abi, load_altoken_abi, load_erc721_abi
from src.config import (
    GAS_DEPOSIT,
    GAS_LARGE_POSITION_SURCHARGE,
    GAS_MINT,
    GAS_SET_DEPOSIT_CAP,
    GAS_TRANSFER_ALTOKEN,
    GAS_TRANSFER_NFT,
    LARGE_POSITION_THRESHOLD,
)
from src.types import PositionMigration, TransactionCall


class TransactionBuildError(Exception):
    pass


def encode_function_call(
    abi: list[dict[str, Any]],
    function_name: str,
    args: list[Any],
) -> bytes:
    """Encode a function call into ABI calldata."""
    fn = None
    for entry in abi:
        if entry.get("type") == "function" and entry.get("name") == function_name:
            fn = entry
            break

    if fn is None:
        raise TransactionBuildError(f"Function '{function_name}' not found in ABI")

    param_types = [inp["type"] for inp in fn.get("inputs", [])]

    if len(args) != len(param_types):
        raise TransactionBuildError(
            f"'{function_name}' expects {len(param_types)} args, got {len(args)}"
        )

    sig = f"{function_name}({','.join(param_types)})"
    selector = keccak(text=sig)[:4]

    try:
        encoded = encode(param_types, args)
    except Exception as e:
        raise TransactionBuildError(f"Failed to encode args for '{function_name}': {e}")

    return selector + encoded


def _gas_for_deposit(amount_wei: int) -> int:
    gas = GAS_DEPOSIT
    if amount_wei >= LARGE_POSITION_THRESHOLD:
        gas += GAS_LARGE_POSITION_SURCHARGE
    return gas


def _gas_for_mint(amount_wei: int) -> int:
    gas = GAS_MINT
    if amount_wei >= LARGE_POSITION_THRESHOLD:
        gas += GAS_LARGE_POSITION_SURCHARGE
    return gas


def build_set_deposit_cap_tx(
    alchemist_address: str,
    new_cap_wei: int,
) -> TransactionCall:
    """Build setDepositCap(newCap) to raise the cap before a batch of deposits.

    Args:
        alchemist_address: AlchemistV3 contract address
        new_cap_wei: New deposit cap (must be >= current MYT balance of Alchemist)
    """
    abi = load_alchemist_abi()
    data = encode_function_call(abi, "setDepositCap", [new_cap_wei])
    return TransactionCall(
        to=alchemist_address,
        data=data,
        value=0,
        gas_estimate=GAS_SET_DEPOSIT_CAP,
        description=f"setDepositCap({new_cap_wei})",
    )


def build_deposit_tx(
    position: PositionMigration,
    alchemist_address: str,
    multisig: str,
) -> TransactionCall:
    """Build deposit(amount, multisig, 0).

    tokenId=0 causes the Alchemist to auto-mint a new NFT to the recipient (multisig).
    The actual tokenId will be emitted in the AlchemistV3PositionNFTMinted event.
    """
    abi = load_alchemist_abi()
    data = encode_function_call(
        abi, "deposit",
        [position.deposit_amount_wei, multisig, 0],
    )
    return TransactionCall(
        to=alchemist_address,
        data=data,
        value=0,
        gas_estimate=_gas_for_deposit(position.deposit_amount_wei),
        description=(
            f"deposit({position.deposit_amount_wei}, {multisig}, 0) "
            f"for user {position.user_address}"
        ),
    )


def build_mint_tx(
    position: PositionMigration,
    alchemist_address: str,
    multisig: str,
    token_id: int,
) -> TransactionCall:
    """Build mint(tokenId, amount, multisig).

    Mints alAssets against the position. alAssets land in the multisig.
    Requires: msg.sender == owner of tokenId (multisig).

    Args:
        token_id: The actual tokenId returned/emitted from the deposit step.
    """
    if position.mint_amount_wei == 0:
        raise TransactionBuildError("Cannot build mint tx for credit/zero-debt user")

    abi = load_alchemist_abi()
    data = encode_function_call(
        abi, "mint",
        [token_id, position.mint_amount_wei, multisig],
    )
    return TransactionCall(
        to=alchemist_address,
        data=data,
        value=0,
        gas_estimate=_gas_for_mint(position.mint_amount_wei),
        description=(
            f"mint({token_id}, {position.mint_amount_wei}, {multisig}) "
            f"for user {position.user_address}"
        ),
    )



def build_altoken_transfer_tx(
    al_token_address: str,
    recipient: str,
    amount_wei: int,
    user_address: str,
) -> TransactionCall:
    """Build alToken.transfer(recipient, amount) to send credit to a user.

    Credit users get alAssets equal to their V2 credit amount.
    These are sourced from the pool of alAssets minted during migration.
    """
    abi = load_altoken_abi()
    data = encode_function_call(
        abi, "transfer",
        [recipient, amount_wei],
    )
    return TransactionCall(
        to=al_token_address,
        data=data,
        value=0,
        gas_estimate=GAS_TRANSFER_ALTOKEN,
        description=f"alToken.transfer({recipient}, {amount_wei}) — credit for {user_address}",
    )


def build_nft_transfer_tx(
    nft_address: str,
    multisig: str,
    user_address: str,
    token_id: int,
) -> TransactionCall:
    """Build ERC721.transferFrom(multisig, user, tokenId).

    Transfers the position NFT from the migration multisig to the original user.
    Only called after all minting, burning, and credit distribution is verified.
    """
    abi = load_erc721_abi()
    data = encode_function_call(
        abi, "transferFrom",
        [multisig, user_address, token_id],
    )
    return TransactionCall(
        to=nft_address,
        data=data,
        value=0,
        gas_estimate=GAS_TRANSFER_NFT,
        description=f"transferFrom({multisig}, {user_address}, {token_id})",
    )


def validate_transaction_call(tx: TransactionCall) -> list[str]:
    errors = []
    if not tx.to:
        errors.append("'to' address is empty")
    elif not tx.to.startswith("0x") or len(tx.to) != 42:
        errors.append(f"Invalid 'to' address: {tx.to}")
    if not tx.data or len(tx.data) < 4:
        errors.append(f"Calldata too short: {len(tx.data) if tx.data else 0} bytes")
    if tx.gas_estimate <= 0:
        errors.append(f"Invalid gas estimate: {tx.gas_estimate}")
    if tx.value < 0:
        errors.append(f"Negative value: {tx.value}")
    return errors
