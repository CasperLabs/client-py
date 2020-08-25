# -*- coding: utf-8 -*-
from casperlabs_client.abi import ABI
from casperlabs_client.consts import ED25519_KEY_ALGORITHM
from .common import WASM_DIRECTORY


def test_deploy_do_nothing_and_call_by_entry_point_and_version(
    casperlabs_client, faucet_funded_accounts
):
    key_holder, private_key_pem_path = faucet_funded_accounts[ED25519_KEY_ALGORITHM]

    deploy_hash = casperlabs_client.deploy(
        session=WASM_DIRECTORY / "test_payment_stored.wasm",
        payment_amount=10000000,
        private_key=private_key_pem_path,
    )
    result = casperlabs_client.show_deploy(
        deploy_hash, wait_for_processed=True, timeout_seconds=300
    )
    for block_info in result.processing_results:
        assert (
            not block_info.is_error
        ), f"block_info.is_error: {block_info.error_message}"
    assert len(result.processing_results) > 0, "No block_info returned"

    deploy_hash = casperlabs_client.deploy(
        session=WASM_DIRECTORY / "transfer_to_account_u512_stored.wasm",
        payment_name="test_payment_hash",
        payment_entry_point="pay",
        payment_args=ABI.args([ABI.big_int("amount", 10000000)]),
        private_key=private_key_pem_path,
    )
    result = casperlabs_client.show_deploy(
        deploy_hash, wait_for_processed=True, timeout_seconds=300
    )
    for block_info in result.processing_results:
        assert (
            not block_info.is_error
        ), f"block_info.is_error: {block_info.error_message}"
    assert len(result.processing_results) > 0, "No block_info returned"

    target_account = "1000000000000000000000000000000000000000000000000000000000000000"
    transfer_amount = 123
    session_args = ABI.args(
        [
            ABI.account("target", target_account,),
            ABI.big_int("amount", transfer_amount),
        ]
    )

    deploy_hash = casperlabs_client.deploy(
        session_name="transfer_to_account",
        session_entry_point="transfer",
        session_args=session_args,
        payment_amount=10000000,
        private_key=private_key_pem_path,
    )
    result = casperlabs_client.show_deploy(
        deploy_hash, wait_for_processed=True, timeout_seconds=300
    )
    for block_info in result.processing_results:
        assert (
            not block_info.is_error
        ), f"block_info.is_error: {block_info.error_message}"
    assert len(result.processing_results) > 0, "No block_info returned"

    block_hash = block_info.block_info.summary.block_hash.hex()
    balance = casperlabs_client.balance(target_account, block_hash)
    assert balance == transfer_amount, "Post transfer balance"
