# -*- coding: utf-8 -*-


def test_validator_key_files_are_created(validator_keys_directory):
    expected_files = (
        "node-id",
        "node.certificate.pem",
        "node.key.pem",
        "secret_key.pem",
        "public_key.pem",
        "public_key_hex",
    )
    for filename in expected_files:
        file_path = validator_keys_directory / filename
        assert file_path.exists(), f"File {file_path} not found"
