# -*- coding: utf-8 -*-
import base64
from abc import ABC, abstractmethod
from typing import Union
from pathlib import Path

from casperlabs_client import crypto, consts, io


class KeyHolder(ABC):
    """ Abstract class for loading, generating and handling public/private key holders """

    def __init__(
        self,
        private_key_pem: bytes = None,
        private_key=None,
        public_key_pem: bytes = None,
        public_key=None,
        algorithm: str = None,
    ):
        if not any((private_key, private_key_pem, public_key, public_key_pem)):
            raise ValueError("No public or private key information provided.")
        self._private_key_pem = private_key_pem
        self._private_key = private_key
        self._public_key_pem = public_key_pem
        self._public_key = public_key
        self._algorithm = algorithm

    @abstractmethod
    def _hex_prefix(self) -> str:
        """ Returns proper byte prefix in hex for algorithm """
        pass

    @property
    def algorithm(self):
        """ String representation of the key algorithm """
        return self._algorithm

    @property
    def private_key_pem(self) -> bytes:
        """ Returns or generates private key pem data from other internal fields """
        if self._private_key_pem is None:
            if self._private_key is None:
                raise ValueError("Must have either _private_key or _private_key_pem.")
            self._private_key_pem = self._private_key_pem_from_private_key()
        return self._private_key_pem

    @abstractmethod
    def _private_key_pem_from_private_key(self) -> bytes:
        pass

    @property
    def private_key(self) -> bytes:
        """ Returns or generates private key bytes from other internal fields """
        if self._private_key is None:
            if self._private_key_pem is None:
                raise ValueError("Must have either _private_key or _private_key_pem.")
            self._private_key = self._private_key_from_private_key_pem()
        return self._private_key

    @property
    def private_key_hex(self) -> str:
        """ Returns or generates private key in hex encoding from other internal fields """
        return f"{self._hex_prefix()}{self.private_key.hex()}"

    @property
    def private_key_base64(self) -> str:
        """ Returns or generates private key in base64 encoding from other internal fields """
        return base64.b64encode(self.private_key).decode("UTF-8")

    @abstractmethod
    def _private_key_from_private_key_pem(self) -> bytes:
        pass

    @property
    def public_key_pem(self) -> bytes:
        """ Returns or generates public key pem data from other internal fields """
        if self._public_key_pem is None:
            self._public_key_pem = self._public_key_pem_from_public_key()
        return self._public_key_pem

    @abstractmethod
    def _public_key_pem_from_public_key(self) -> bytes:
        pass

    @property
    def public_key(self) -> bytes:
        """ Returns or generates public key bytes from other internal fields """
        if self._public_key is None:
            if self._public_key_pem:
                self._public_key = self._public_key_from_public_key_pem()
            elif self.private_key:
                self._public_key = self._public_key_from_private_key()
            else:
                raise ValueError("No values given to derive public key")
        return self._public_key

    @property
    def public_key_hex(self) -> str:
        """ Returns or generates public key in hex encoding from other internal fields """
        return self.public_key.hex()

    @property
    def public_key_base64(self) -> str:
        """ Returns or generates public key in base64 encoding from other internal fields """
        return base64.b64encode(self.public_key).decode("UTF-8")

    @abstractmethod
    def _public_key_from_public_key_pem(self):
        pass

    @abstractmethod
    def _public_key_from_private_key(self):
        pass

    def save_key_files(self, save_directory: Union[str, Path]) -> None:
        """
        Save key pairs out as public and private pem files.

        :param save_directory:   str or Path to directory for saving pem files.

        Generated files:
            public_key.pem  # public key in pem format
            secret_key.pem  # secret key in pem format
            public_key_hex  # public key in hex format with leading algorithm byte
        """
        private_path = Path(save_directory) / consts.PRIVATE_KEY_FILENAME
        io.write_binary_file(private_path, self.private_key_pem)

        public_path = Path(save_directory) / consts.PUBLIC_KEY_FILENAME
        io.write_binary_file(public_path, self.public_key_pem)

        public_hex_path = Path(save_directory) / consts.PUBLIC_KEY_HEX_FILENAME
        io.write_file(public_hex_path, self.public_key_hex)

    @staticmethod
    @abstractmethod
    def from_private_key_path(private_key_pem_path: Union[str, Path]) -> "KeyHolder":
        pass

    @staticmethod
    @abstractmethod
    def from_public_key_path(public_key_pem_path: Union[str, Path]) -> "KeyHolder":
        pass

    @abstractmethod
    def sign(self, data: bytes) -> bytes:
        pass

    @property
    def account_hash(self) -> bytes:
        """ Generate hash of public key and key algorithm for use as primary identifier in the system as bytes """
        # account hash is the one place where algorithm is used in upper case.
        return crypto.blake2b_hash(
            self.algorithm.upper().encode("UTF-8") + b"\x00" + self.public_key
        )

    @property
    def account_hash_hex(self) -> str:
        """ Generate hash of public key and key algorithm for use as primary identifier in the system as hex str """
        return self.account_hash.hex()

    @property
    def account_hash_base64(self) -> str:
        """ Generate hash of public key and key algorithm for use as primary identifier in the system as base64 str """
        return base64.b64encode(self.account_hash).decode("UTF-8")
