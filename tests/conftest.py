# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

import pytest
import tempfile
from casperlabs_client import CasperLabsClient, key_holders
from casperlabs_client.consts import (
    SUPPORTED_KEY_ALGORITHMS,
    PUBLIC_KEY_FILENAME,
    PRIVATE_KEY_FILENAME,
    PUBLIC_KEY_HEX_FILENAME,
)


@pytest.fixture(scope="session")
def fake_wasm():
    with tempfile.NamedTemporaryFile() as f:
        yield f


@pytest.fixture(scope="session")
def account_keys_directory():
    with tempfile.TemporaryDirectory() as directory:
        for key_algorithm in SUPPORTED_KEY_ALGORITHMS:
            client = CasperLabsClient()
            client.keygen(directory, algorithm=key_algorithm)
            for file_name in (
                PUBLIC_KEY_FILENAME,
                PUBLIC_KEY_HEX_FILENAME,
                PRIVATE_KEY_FILENAME,
            ):
                shutil.move(
                    Path(directory) / file_name,
                    Path(directory) / f"{key_algorithm}{file_name}",
                )
        yield Path(directory)


@pytest.fixture(scope="session")
def validator_keys_directory():
    with tempfile.TemporaryDirectory() as directory:
        client = CasperLabsClient()
        client.validator_keygen(directory)
        yield Path(directory)


def key_paths(algorithm, directory):
    return (
        directory / f"{algorithm}{PRIVATE_KEY_FILENAME}",
        directory / f"{algorithm}{PUBLIC_KEY_FILENAME}",
    )


@pytest.fixture(scope="session")
def account_keys(account_keys_directory):
    algorithm_keys = {}
    for algorithm in SUPPORTED_KEY_ALGORITHMS:
        private_pem_path, public_pem_path = key_paths(algorithm, account_keys_directory)
        key_holder = key_holders.class_from_algorithm(algorithm).from_private_key_path(
            private_pem_path
        )
        keys_files = {
            "private_pem": private_pem_path,
            "public_pem": public_pem_path,
            "key_holder": key_holder,
        }
        algorithm_keys[algorithm] = keys_files
    return algorithm_keys


# Scoping this per call as we mock it.
@pytest.fixture
def client():
    return CasperLabsClient()
