# -*- coding: utf-8 -*-
from casperlabs_client import consts


def test_account_key_files_are_created(account_keys_directory):
    for key_algorithm in consts.SUPPORTED_KEY_ALGORITHMS:
        for file_suffix in (
            consts.PUBLIC_KEY_FILENAME,
            consts.PUBLIC_KEY_HEX_FILENAME,
            consts.PRIVATE_KEY_FILENAME,
        ):
            file_path = account_keys_directory / f"{key_algorithm}{file_suffix}"
            assert file_path.exists(), f"File {file_path} not found."
