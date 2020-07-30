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


def test_payment_amount_is_not_defaulted(client, account_keys):
    with pytest.raises(InternalError) as excinfo:
        _ = client.make_deploy(
            session_name="NotValidButGoodEnough",
            public_key=account_keys[ED25519_KEY_ALGORITHM]["public_pem"],
        )
    assert "No valid deploy payment options received." in str(excinfo.value)


def test_session_option_is_not_given(client, account_keys):
    private_key_pem = account_keys[ED25519_KEY_ALGORITHM]["private_pem"]
    with pytest.raises(InternalError) as excinfo:
        _ = client.make_deploy(public_key=private_key_pem, payment_amount=1000000)
    assert (
        "Must have one and only one session, session_hash, session_name, "
        "session_package_hash, or session_package_name provided"
    ) in str(excinfo.value)


def test_session_option_too_many_given(client, account_keys):
    private_key_pem = account_keys[ED25519_KEY_ALGORITHM]["private_pem"]
    with pytest.raises(InternalError) as excinfo:
        _ = client.make_deploy(
            public_key=private_key_pem,
            payment_amount=1000000,
            session_name="bob",
            session_hash="0000000000000000000000000000000000000000000000000000000000000000",
        )
    assert (
        "Must have one and only one session, session_hash, session_name, "
        "session_package_hash, or session_package_name provided"
    ) in str(excinfo.value)


def test_private_key_not_given(client, account_keys, fake_wasm):
    account_hash = account_keys[ED25519_KEY_ALGORITHM]["key_holder"].account_hash_hex
    with pytest.raises(InternalError) as excinfo:
        _ = client.deploy(
            session=fake_wasm.name, payment_amount=100000, from_addr=account_hash,
        )
    assert (
        "Must have either `private_key_pem_file`, `private_key_hex`, or `key_holder`"
        in str(excinfo.value)
    )


def test_private_key_hex_to_node_comm_failure(client, account_keys):
    key_holder = account_keys[ED25519_KEY_ALGORITHM]["key_holder"]
    with pytest.raises(InternalError) as excinfo:
        _ = client.deploy(
            session_name="bob",
            payment_amount=100000,
            private_key_hex=key_holder.private_key.hex(),
        )
    assert "failed to connect" in str(excinfo.value)
