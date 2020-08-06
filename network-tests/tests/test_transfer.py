# -*- coding: utf-8 -*-
import pytest

from casperlabs_client.consts import SUPPORTED_KEY_ALGORITHMS
from casperlabs_client.key_holders import class_from_algorithm


@pytest.mark.parametrize("algorithm", SUPPORTED_KEY_ALGORITHMS)
def test_transfer_creates_new_account_with_all_supported_key_types(
    casperlabs_client, faucet_funded_accounts, algorithm
):
    key_holder, private_key_pem_path = faucet_funded_accounts[algorithm]
    new_account = class_from_algorithm(algorithm).generate()
    transfer_amount = 1000
    deploy_hash = casperlabs_client.transfer(
        target_account=new_account.account_hash_hex,
        amount=transfer_amount,
        private_key=private_key_pem_path,
        algorithm=algorithm,
        payment_amount=1000000,
    )
    result = casperlabs_client.show_deploy(
        deploy_hash, wait_for_processed=True, timeout_seconds=300
    )
    for block_info in result.processing_results:
        assert (
            not block_info.is_error
        ), f"block_info.is_error: {block_info.error_message}"
    assert len(result.processing_results) > 0, "No block_info returned"
    block_hash = result.processing_results[0].block_info.summary.block_hash
    new_balance = casperlabs_client.balance(
        new_account.account_hash_hex, block_hash.hex()
    )
    assert new_balance == transfer_amount
