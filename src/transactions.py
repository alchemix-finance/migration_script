"""Transaction building for CDP migration.

This module provides transaction builders that encode function calls
for the CDP protocol migration:
- build_deposit_tx: Create deposit transaction for collateral
- build_mint_tx: Create mint transaction for debt
- build_transfer_tx: Create NFT transfer transaction

All builders use the ABI files in contracts/ to properly encode calldata.
"""

from typing import Any

from eth_abi import encode
from eth_utils import keccak

from src.abi import load_cdp_abi, load_erc721_abi
from src.config import ChainConfig
from src.gas import estimate_deposit_gas, estimate_mint_gas, estimate_transfer_gas
from src.types import PositionMigration, TransactionCall


class TransactionBuildError(Exception):
    """Raised when a transaction cannot be built."""

    pass


def encode_function_call(
    abi: list[dict[str, Any]],
    function_name: str,
    args: list[Any],
) -> bytes:
    """Encode a function call using the provided ABI.

    This creates the calldata for a smart contract function call by:
    1. Computing the 4-byte function selector from the function signature
    2. ABI-encoding the function arguments
    3. Concatenating selector + encoded args

    Args:
        abi: Contract ABI as a list of function/event definitions
        function_name: Name of the function to call
        args: List of arguments to pass to the function

    Returns:
        Encoded calldata as bytes

    Raises:
        TransactionBuildError: If function not found in ABI or encoding fails
    """
    # Find the function in the ABI
    function_def = None
    for entry in abi:
        if entry.get("type") == "function" and entry.get("name") == function_name:
            function_def = entry
            break

    if function_def is None:
        raise TransactionBuildError(f"Function '{function_name}' not found in ABI")

    # Extract parameter types
    inputs = function_def.get("inputs", [])
    param_types = [inp["type"] for inp in inputs]

    # Validate argument count
    if len(args) != len(param_types):
        raise TransactionBuildError(
            f"Function '{function_name}' expects {len(param_types)} arguments, "
            f"got {len(args)}"
        )

    # Compute function selector: first 4 bytes of keccak256(signature)
    signature = f"{function_name}({','.join(param_types)})"
    selector = keccak(text=signature)[:4]

    # Encode arguments
    try:
        encoded_args = encode(param_types, args)
    except Exception as e:
        raise TransactionBuildError(
            f"Failed to encode arguments for '{function_name}': {e}"
        )

    # Return selector + encoded arguments
    return selector + encoded_args


def build_deposit_tx(
    position: PositionMigration,
    chain_config: ChainConfig,
) -> TransactionCall:
    """Build a deposit transaction for a position.

    The deposit function creates a new CDP position by:
    1. Transferring collateral to the contract
    2. Creating position state in storage
    3. Minting a position NFT to the recipient

    Function signature:
        deposit(uint256 amount, address recipient, uint256 tokenId) -> uint256

    Args:
        position: The position to deposit collateral for
        chain_config: Chain configuration containing contract addresses

    Returns:
        TransactionCall with encoded calldata and gas estimate

    Raises:
        TransactionBuildError: If transaction cannot be built
    """
    # Get the appropriate CDP contract address based on asset type from chain_config
    if position.asset_type == "USD":
        cdp_contract = chain_config.get("cdp_usd", "")
    else:
        cdp_contract = chain_config.get("cdp_eth", "")

    if not cdp_contract:
        raise TransactionBuildError(
            f"No CDP contract address configured for {position.chain}/{position.asset_type}"
        )

    # Multisig receives the NFT initially
    multisig = chain_config["multisig"]
    if not multisig:
        raise TransactionBuildError(
            f"No multisig address configured for {position.chain}"
        )

    # Load CDP ABI and encode the deposit call
    cdp_abi = load_cdp_abi()

    # deposit(amount, recipient, tokenId)
    calldata = encode_function_call(
        abi=cdp_abi,
        function_name="deposit",
        args=[
            position.deposit_amount,  # amount: uint256
            multisig,  # recipient: address
            position.token_id,  # tokenId: uint256
        ],
    )

    # Estimate gas for this operation
    gas_estimate = estimate_deposit_gas(position)

    return TransactionCall(
        to=cdp_contract,
        data=calldata,
        value=0,
        gas_estimate=gas_estimate,
        description=(
            f"deposit({position.deposit_amount}, {multisig}, {position.token_id}) "
            f"for user {position.user_address}"
        ),
    )


def build_mint_tx(
    position: PositionMigration,
    chain_config: ChainConfig,
) -> TransactionCall:
    """Build a mint transaction for a position.

    The mint function borrows against an existing position by:
    1. Checking the position's collateralization ratio
    2. Updating the position's debt in storage
    3. Minting debt tokens to the recipient

    Function signature:
        mint(uint256 tokenId, uint256 amount, address recipient)

    Args:
        position: The position to mint debt against
        chain_config: Chain configuration containing contract addresses

    Returns:
        TransactionCall with encoded calldata and gas estimate

    Raises:
        TransactionBuildError: If transaction cannot be built
    """
    # Get the appropriate CDP contract address based on asset type from chain_config
    if position.asset_type == "USD":
        cdp_contract = chain_config.get("cdp_usd", "")
    else:
        cdp_contract = chain_config.get("cdp_eth", "")

    if not cdp_contract:
        raise TransactionBuildError(
            f"No CDP contract address configured for {position.chain}/{position.asset_type}"
        )

    # Load CDP ABI and encode the mint call
    cdp_abi = load_cdp_abi()

    # mint(tokenId, amount, recipient)
    # Note: debt tokens go directly to the user, not the multisig
    calldata = encode_function_call(
        abi=cdp_abi,
        function_name="mint",
        args=[
            position.token_id,  # tokenId: uint256
            position.mint_amount,  # amount: uint256
            position.user_address,  # recipient: address
        ],
    )

    # Estimate gas for this operation
    gas_estimate = estimate_mint_gas(position)

    return TransactionCall(
        to=cdp_contract,
        data=calldata,
        value=0,
        gas_estimate=gas_estimate,
        description=(
            f"mint({position.token_id}, {position.mint_amount}, {position.user_address})"
        ),
    )


def build_transfer_tx(
    position: PositionMigration,
    chain_config: ChainConfig,
) -> TransactionCall:
    """Build an NFT transfer transaction for a position.

    The transfer function moves the position NFT from the multisig
    to the original user who owned the position.

    Function signature:
        transferFrom(address from, address to, uint256 tokenId)

    Args:
        position: The position whose NFT should be transferred
        chain_config: Chain configuration containing contract addresses

    Returns:
        TransactionCall with encoded calldata and gas estimate

    Raises:
        TransactionBuildError: If transaction cannot be built
    """
    # Get the appropriate NFT contract address based on asset type from chain_config
    if position.asset_type == "USD":
        nft_contract = chain_config.get("nft_usd", "")
    else:
        nft_contract = chain_config.get("nft_eth", "")

    if not nft_contract:
        raise TransactionBuildError(
            f"No NFT contract address configured for {position.chain}/{position.asset_type}"
        )

    # Multisig is the current owner of the NFT
    multisig = chain_config["multisig"]
    if not multisig:
        raise TransactionBuildError(
            f"No multisig address configured for {position.chain}"
        )

    # Load ERC721 ABI and encode the transfer call
    erc721_abi = load_erc721_abi()

    # transferFrom(from, to, tokenId)
    calldata = encode_function_call(
        abi=erc721_abi,
        function_name="transferFrom",
        args=[
            multisig,  # from: address (current owner)
            position.user_address,  # to: address (original user)
            position.token_id,  # tokenId: uint256
        ],
    )

    # Estimate gas for this operation
    gas_estimate = estimate_transfer_gas(position)

    return TransactionCall(
        to=nft_contract,
        data=calldata,
        value=0,
        gas_estimate=gas_estimate,
        description=(
            f"transferFrom({multisig}, {position.user_address}, {position.token_id})"
        ),
    )


def build_position_transactions(
    position: PositionMigration,
    chain_config: ChainConfig,
) -> tuple[TransactionCall, TransactionCall, TransactionCall]:
    """Build all three transactions for migrating a single position.

    This is a convenience function that builds the complete set of
    transactions needed to migrate one position:
    1. deposit - create position with collateral
    2. mint - borrow against position
    3. transfer - transfer NFT to user

    Args:
        position: The position to migrate
        chain_config: Chain configuration containing contract addresses

    Returns:
        Tuple of (deposit_tx, mint_tx, transfer_tx)

    Raises:
        TransactionBuildError: If any transaction cannot be built
    """
    deposit_tx = build_deposit_tx(position, chain_config)
    mint_tx = build_mint_tx(position, chain_config)
    transfer_tx = build_transfer_tx(position, chain_config)

    return deposit_tx, mint_tx, transfer_tx


def validate_transaction_call(tx: TransactionCall) -> list[str]:
    """Validate a transaction call for common issues.

    Args:
        tx: The transaction call to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check 'to' address
    if not tx.to:
        errors.append("Transaction 'to' address is empty")
    elif not tx.to.startswith("0x"):
        errors.append(f"Invalid 'to' address format: {tx.to}")
    elif len(tx.to) != 42:
        errors.append(f"Invalid 'to' address length: {len(tx.to)} (expected 42)")

    # Check calldata
    if not tx.data:
        errors.append("Transaction calldata is empty")
    elif len(tx.data) < 4:
        errors.append(f"Calldata too short: {len(tx.data)} bytes (minimum 4 for selector)")

    # Check gas estimate
    if tx.gas_estimate <= 0:
        errors.append(f"Invalid gas estimate: {tx.gas_estimate}")

    # Check value is non-negative
    if tx.value < 0:
        errors.append(f"Negative transaction value: {tx.value}")

    return errors
