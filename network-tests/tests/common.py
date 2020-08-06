# -*- coding: utf-8 -*-
import os
from pathlib import Path

from casperlabs_client import CasperLabsClient
from casperlabs_client.abi import ABI

THIS_DIRECTORY = Path(os.path.dirname(os.path.realpath(__file__)))
NETWORK_TESTS_ROOT = THIS_DIRECTORY.parent
PROJECT_DIR = THIS_DIRECTORY.parent.parent

WASM_DIRECTORY = NETWORK_TESTS_ROOT / "wasm"
HACK_DOCKER_DIRECTORY = PROJECT_DIR / "hack" / "docker"

KEYS_DIRECTORY = HACK_DOCKER_DIRECTORY / "keys"
FAUCET_PRIVATE_KEY_PEM_PATH = KEYS_DIRECTORY / "faucet-account" / "account-private.pem"

CASPERLABS_CONFIG_DIRECTORY = HACK_DOCKER_DIRECTORY / ".casperlabs"
ACCOUNTS_CSV = CASPERLABS_CONFIG_DIRECTORY / "chainspec" / "genesis" / "accounts.csv"


def get_valid_block_hash(casperlabs_client: CasperLabsClient):
    """ Get a valid block hash from current hack/docker network in bytes """
    block_generator = casperlabs_client.show_blocks(depth=8)
    block = list(block_generator)[-1]
    block_hash = block.summary.block_hash
    return block_hash


def get_valid_block_hash_hex(casperlabs_client: CasperLabsClient):
    """ Get a valid block hash from current hack/docker network in hex"""
    return get_valid_block_hash(casperlabs_client).hex()


def faucet_fund_account(casperlabs_client, account_hash_hex, amount=10000000000):
    faucet_wasm_path = WASM_DIRECTORY / "faucet.wasm"
    assert faucet_wasm_path.exists(), (
        f"Needed wasm file: {faucet_wasm_path} does not exist.\n"
        "It should be built in `build_contracts_in_buildenv.sh`."
    )
    session_args = ABI.args(
        [ABI.account("target", account_hash_hex), ABI.big_int("amount", amount)]
    )

    deploy_hash = casperlabs_client.deploy(
        private_key=FAUCET_PRIVATE_KEY_PEM_PATH,
        session=faucet_wasm_path,
        session_args=session_args,
        payment_amount=10000000,
    )
    result = casperlabs_client.show_deploy(deploy_hash, wait_for_processed=True)
    assert (
        len(result.processing_results) > 0
    ), "No processing results from faucet transfer"
    block_hash = result.processing_results[0].block_info.summary.block_hash
    result = casperlabs_client.balance(account_hash_hex, block_hash.hex())
    assert result > 0, "balance of new account is not correct"
