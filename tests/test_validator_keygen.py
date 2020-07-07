# -*- coding: utf-8 -*-
from casperlabs_client import consts


def test_validator_key_files_are_created(validator_keys_directory):
    for filename in (
        consts.VALIDATOR_PRIVATE_KEY_FILENAME,
        consts.VALIDATOR_PUBLIC_KEY_FILENAME,
        consts.VALIDATOR_ID_HEX_FILENAME,
        consts.VALIDATOR_ID_FILENAME,
        consts.NODE_PRIVATE_KEY_FILENAME,
        consts.NODE_CERTIFICATE_FILENAME,
        consts.NODE_ID_FILENAME,
    ):
        file_path = validator_keys_directory / filename
        assert file_path.exists(), f"File {file_path} not found"
