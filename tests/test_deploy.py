# -*- coding: utf-8 -*-
import pytest

from casperlabs_client import InternalError
from casperlabs_client.consts import ED25519_KEY_ALGORITHM
from tests.conftest import key_paths


def test_simple_deploy_build_to_node_comm_failure(client, account_keys_directory):
    private_key_pem_path, _ = key_paths(ED25519_KEY_ALGORITHM, account_keys_directory)
    with pytest.raises(InternalError) as excinfo:
        _ = client.deploy(
            from_addr=b"12121212121212121212121212121212",
            session_name="contract_name",
            private_key=private_key_pem_path,
            payment_amount=100000,
        )
    assert "failed to connect" in str(excinfo.value)


def test_payment_amount_is_not_defaulted(client, account_keys_directory):
    private_key_pem_path, public_key_pem_path = key_paths(
        ED25519_KEY_ALGORITHM, account_keys_directory
    )

    with pytest.raises(InternalError) as excinfo:
        _ = client.make_deploy(
            session_name="NotValidButGoodEnough", public_key=public_key_pem_path,
        )
    assert "No valid deploy payment options received." in str(excinfo.value)
