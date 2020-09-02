# -*- coding: utf-8 -*-
from pathlib import Path

from casperlabs_client import CasperLabsClient
from casperlabs_client.commands.common_options import (
    ALGORITHM_OPTION,
    DIRECTORY_FOR_WRITE_OPTION,
)
from casperlabs_client.decorators import guarded_command

NAME: str = "keygen"
HELP: str = """Generates account keys into existing directory

Usage: casperlabs-client keygen <existing output directory>
Command will override existing files!

Generated files:
   public_key.pem  # public key in pem format
   secret_key.pem  # secret key in pem format
   public_key_hex  # public key in hex format with leading algorithm byte
"""
OPTIONS = (DIRECTORY_FOR_WRITE_OPTION, ALGORITHM_OPTION)


@guarded_command
def method(casperlabs_client: CasperLabsClient, args):
    directory = Path(args.get("directory")).resolve()
    algorithm = args.get("algorithm")
    casperlabs_client.keygen(directory, algorithm)
    print(f"Keys successfully created in directory: {str(directory.absolute())}")
