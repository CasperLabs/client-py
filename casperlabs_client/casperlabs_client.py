#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import functools
from pathlib import Path
import time
import warnings
from typing import List, Union

# Monkey patching of google.protobuf.text_encoding.CEscape
# to get keys and signatures in hex when printed
import google.protobuf.text_format

from .consts import ED25519_KEY_ALGORITHM
from .reformat import optional_base64_base16_to_bytes

CEscape = google.protobuf.text_format.text_encoding.CEscape


def _hex(text, as_utf8):
    try:
        if len(text) in (32, 64, 20):
            return text.hex()
        else:
            return CEscape(text, as_utf8)
    except TypeError:
        return CEscape(text, as_utf8)


google.protobuf.text_format.text_encoding.CEscape = _hex

# Hack to fix the relative imports problems with grpc #
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
# end of hack #

from . import io, common, vdag, abi, key_holders
from .insecure_grpc_service import InsecureGRPCService
from .secure_grpc_service import SecureGRPCService
from .query_state import key_variant
from .deploy import DeployData, sign_deploy

from grpc._channel import _Rendezvous

# ~/CasperLabs/protobuf/io/casperlabs/node/api/control.proto
from . import control_pb2_grpc, consts, crypto

# ~/CasperLabs/protobuf/io/casperlabs/node/api/casper.proto
from . import casper_pb2 as casper
from . import casper_pb2_grpc

# ~/CasperLabs/protobuf/io/casperlabs/casper/consensus/info.proto
from . import info_pb2 as info

# ~/CasperLabs/protobuf/io/casperlabs/node/api/diagnostics.proto
from . import diagnostics_pb2_grpc
from . import empty_pb2


class InternalError(Exception):
    """
    The only exception that API calls can throw.
    Internal errors like gRPC exceptions will be caught
    and this exception thrown instead, so the user does
    not have to worry about handling any other exceptions.
    """

    # TODO: Is there a reason we need to hide error types?
    def __init__(self, status="", details=""):
        super(InternalError, self).__init__()
        self.status = status
        self.details = details

    def __str__(self):
        return f"{self.status}: {self.details}"


def api(function):
    """
    Decorator of API functions that protects user code from
    unknown exceptions raised by gRPC or internal API errors.
    It will catch all exceptions and throw InternalError.

    :param function: function to be decorated
    :return: decorated function
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (SyntaxError, TypeError, InternalError):
            raise
        except _Rendezvous as e:
            raise InternalError(str(e.code()), e.details())
        except Exception as e:
            raise InternalError(details=str(e)) from e

    return wrapper


class CasperLabsClient:
    """
    gRPC CasperLabs client.
    """

    def __init__(
        self,
        host: str = consts.DEFAULT_HOST,
        port: int = consts.DEFAULT_PORT,
        port_internal: int = consts.DEFAULT_INTERNAL_PORT,
        node_id: str = None,
        certificate_file: str = None,
    ):
        """
        CasperLabs client's constructor.

        :param host: Hostname or IP of node on which gRPC service is running
        :param port: Port used for external gRPC API
        :param port_internal: Port used for internal gRPC API
        :param node_id: node_id of the node, for gRPC encryption
        :param certificate_file: Certificate file for TLS
        """
        self.host = host
        self.port = port
        self.port_internal = port_internal
        self.node_id = node_id
        self.certificate_file = certificate_file

        if node_id:
            self.casper_service = SecureGRPCService(
                host, port, casper_pb2_grpc.CasperServiceStub, node_id, certificate_file
            )
            self.control_service = SecureGRPCService(
                # We currently assume that if node_id is given then
                # we get certificate_file too. This is unlike in the Scala client
                # where node_id is all that's needed for configuring secure connection.
                # The reason for this is that currently it doesn't seem to be possible
                # to open a secure grpc connection in Python without supplying any
                # certificate on the client side.
                host,
                port_internal,
                control_pb2_grpc.ControlServiceStub,
                node_id,
                certificate_file,
            )
            self.diagnostics_service = SecureGRPCService(
                host,
                port,
                diagnostics_pb2_grpc.DiagnosticsStub,
                node_id,
                certificate_file,
            )

        else:
            self.casper_service = InsecureGRPCService(
                host, port, casper_pb2_grpc.CasperServiceStub
            )
            self.control_service = InsecureGRPCService(
                host, port_internal, control_pb2_grpc.ControlServiceStub
            )
            self.diagnostics_service = InsecureGRPCService(
                host, port, diagnostics_pb2_grpc.DiagnosticsStub
            )

    @api
    def make_deploy(
        self,
        from_addr: Union[bytes, str] = None,
        public_key: Union[Path, str] = None,
        public_key_hex: str = None,
        algorithm: str = ED25519_KEY_ALGORITHM,
        payment: Union[Path, str] = None,
        payment_args: bytes = None,
        payment_amount: int = None,
        payment_hash: bytes = None,
        payment_name: str = None,
        payment_package_hash: bytes = None,
        payment_package_name: str = None,
        payment_entry_point: str = None,
        payment_version: int = None,
        session: Union[Path, str] = None,
        session_args: bytes = None,
        session_hash: bytes = None,
        session_name: str = None,
        session_package_hash: bytes = None,
        session_package_name: str = None,
        session_entry_point: str = None,
        session_version: int = None,
        ttl_millis: int = 0,
        dependencies: list = None,
        chain_name: str = None,
        transfer_args: bytes = None,
    ):
        """
        Create a protobuf deploy object.

        :param from_addr: Account hash to use for deployment, generated from private_key or private_key_hex if omitted.
                          Default payment will use the main purse of this account, unless custom payment is provided.
        :param public_key: Path to a file with public key. Assumed to be ed25519 unless algorithm is given.
        :param public_key_hex: Public key (base16/hex encoded). Assumed to be ed25519 unless algorithm is given.
        :param algorithm: Algorithm used for generating keys, defaults to ed25519. See consts.SUPPORTED_KEY_ALGORITHMS
        :param payment: Path to the file with payment code as compiled wasm.
        :param payment_args: List of encoded arguments of payment contract
        :param payment_amount: Amount to be used with standard payment. Will pull from main purse.
        :param payment_hash: Hash (base16/hex encoded) of the stored contract to be called for payment.
        :param payment_name: Name of the stored contract to be called for payment.
        :param payment_package_hash Hash of the package to be called in the payment.
        :param payment_package_name Name of the package to be called in the payment.
        :param payment_entry_point: Name of Entrypoint in contract or package to call.
                                    Defaults to `call` if not given.
        :param payment_version: Version of the payment contract or package to use, defaults to latest if omitted
        :param session: Path to the file with session code as compiled wasm.
        :param session_args: List of encoded arguments of session contract
        :param session_hash: Hash (base16/hex encoded) of the stored contract (associated with the executing account)
                             to be called in the session.
        :param session_name: Name of the stored contract (associated with the executing account) to be called in the
                             session.
        :param session_package_hash Hash of the package to be called in the session.
        :param session_package_name Name of the package to be called in the session.
        :param session_entry_point: Name of Entrypoint in contract to call. Defaults to `call` if not given.
        :param session_version: Version of the session contract or package to use, defaults to latest if omitted
        :param ttl_millis: Time to live. Time (in milliseconds) that the deploy will remain valid for.
        :param dependencies: List of deploy hashes (hex/base16 encoded) which must be executed before this deploy.
        :param chain_name: Name of the chain to optionally restrict the deploy from being accidentally included anywhere else.
        :param transfer_args: Should not be used, call transfer method instead.
        :return: protobuf deploy object which must be signed before sending
        """
        deploy_data = DeployData.from_args(
            dict(
                from_addr=from_addr,
                public_key=public_key,
                public_key_hex=public_key_hex,
                algorithm=algorithm,
                payment=payment,
                payment_args=payment_args,
                payment_amount=payment_amount,
                payment_hash=payment_hash,
                payment_name=payment_name,
                payment_package_hash=payment_package_hash,
                payment_package_name=payment_package_name,
                payment_entry_point=payment_entry_point,
                payment_version=payment_version,
                session=session,
                session_args=session_args,
                session_hash=session_hash,
                session_name=session_name,
                session_package_hash=session_package_hash,
                session_package_name=session_package_name,
                session_entry_point=session_entry_point,
                session_version=session_version,
                ttl_millis=ttl_millis,
                dependencies=dependencies,
                chain_name=chain_name,
                transfer_args=transfer_args,
            )
        )
        return deploy_data.make_protobuf()

    @api
    def sign_deploy(
        self,
        private_key_pem_file: Union[str, Path] = None,
        private_key_hex: str = None,
        algorithm: str = ED25519_KEY_ALGORITHM,
        key_holder=None,
        deploy: bytes = None,
        deploy_file: Union[str, Path] = None,
    ):
        """
        Sign a deploy with the given key.  Source of deploy may be deploy object or file containing deploy.
        Must provide one of the private key values or a key_holder object.
        Must provide one of the deploy values.

        :param private_key_pem_file: File containing Private key
        :param private_key_hex: Private key in hex
        :param algorithm: Algorithm used for generating keys, defaults to ed25519. See consts.SUPPORTED_KEY_ALGORITHMS
        :param key_holder: KeyHolder object as alternative to pem file and algorithm
        :param deploy: Deploy as object
        :param deploy_file: File containing deploy

        :return: signed deploy object
        """
        if deploy is None:
            if deploy_file is None:
                raise ValueError("Must have either `deploy` or `deploy_file`")
            deploy = io.read_deploy_file(deploy_file)
        private_key = bytes.fromhex(private_key_hex) if private_key_hex else None
        if not any((private_key_pem_file, private_key, key_holder)):
            raise ValueError(
                "Must have either `private_key_pem_file`, `private_key_hex`, or `key_holder`"
            )
        if not key_holder:
            key_holder = key_holders.key_holder_object(
                algorithm,
                private_key_pem_path=private_key_pem_file,
                private_key=private_key,
            )
        return sign_deploy(deploy, key_holder)

    @api
    def deploy(
        self,
        from_addr: Union[bytes, str] = None,
        private_key: Union[Path, str] = None,
        private_key_hex: str = None,
        algorithm: str = ED25519_KEY_ALGORITHM,
        payment: Union[Path, str] = None,
        payment_args: bytes = None,
        payment_amount: int = None,
        payment_hash: bytes = None,
        payment_name: str = None,
        payment_package_hash: bytes = None,
        payment_package_name: str = None,
        payment_entry_point: str = None,
        payment_version: int = None,
        session: Union[Path, str] = None,
        session_args: bytes = None,
        session_hash: bytes = None,
        session_name: str = None,
        session_package_hash: bytes = None,
        session_package_name: str = None,
        session_entry_point: str = None,
        session_version: int = None,
        ttl_millis: int = 0,
        dependencies=None,
        chain_name: str = None,
        transfer_args: bytes = None,
    ) -> str:
        """
        Create a deploy on the network.

        This is equivalent to performing `make_deploy`, `sign_deploy`, and `send_deploy`.

        :param from_addr: Account hash to use for deployment, generated from private_key or private_key_hex if omitted.
                          Default payment will use the main purse of this account, unless custom payment is provided.
        :param private_key: Path to a file with private key. Assumed to be ed25519 unless algorithm is given.
        :param private_key_hex: Private key (base16/hex encoded). Assumed to be ed25519 unless algorithm is given.
        :param algorithm: Algorithm used for generating keys, defaults to ed25519. See consts.SUPPORTED_KEY_ALGORITHMS
        :param payment: Path to the file with payment code as compiled wasm.
        :param payment_args: List of encoded arguments of payment contract
        :param payment_amount: Amount to be used with standard payment. Will pull from main purse.
        :param payment_hash: Hash (base16/hex encoded) of the stored contract to be called for payment.
        :param payment_name: Name of the stored contract to be called for payment.
        :param payment_package_hash Hash of the package to be called in the payment.
        :param payment_package_name Name of the package to be called in the payment.
        :param payment_entry_point: Name of Entrypoint in contract or package to call.
                                    Defaults to `call` if not given.
        :param payment_version: Version of the payment contract or package to use, defaults to latest if omitted
        :param session: Path to the file with session code as compiled wasm.
        :param session_args: List of encoded arguments of session contract
        :param session_hash: Hash (base16/hex encoded) of the stored contract (associated with the executing account)
                             to be called in the session.
        :param session_name: Name of the stored contract (associated with the executing account) to be called in the
                             session.
        :param session_package_hash Hash of the package to be called in the session.
        :param session_package_name Name of the package to be called in the session.
        :param session_entry_point: Name of Entrypoint in contract to call. Defaults to `call` if not given.
        :param session_version: Version of the session contract or package to use, defaults to latest if omitted
        :param ttl_millis: Time to live. Time (in milliseconds) that the deploy will remain valid for.
        :param dependencies: List of deploy hashes (hex/base16 encoded) which must be executed before this deploy.
        :param chain_name: Name of the chain to optionally restrict the deploy from being accidentally included anywhere else.
        :param transfer_args: Should not be used, call transfer method instead.
        :return: deploy_hash (base16/hex encoded)
        """

        # Using from_args to get validation on build of object
        deploy_data = DeployData.from_args(
            dict(
                from_addr=from_addr,
                private_key=private_key,
                private_key_hex=private_key_hex,
                algorithm=algorithm,
                payment=payment,
                payment_args=payment_args,
                payment_amount=payment_amount,
                payment_hash=payment_hash,
                payment_name=payment_name,
                payment_package_hash=payment_package_hash,
                payment_package_name=payment_package_name,
                payment_entry_point=payment_entry_point,
                payment_version=payment_version,
                session=session,
                session_args=session_args,
                session_hash=session_hash,
                session_name=session_name,
                session_package_hash=session_package_hash,
                session_package_name=session_package_name,
                session_entry_point=session_entry_point,
                session_version=session_version,
                transfer_args=transfer_args,
                ttl_millis=ttl_millis,
                dependencies=dependencies,
                chain_name=chain_name,
            )
        )

        deploy_proto = deploy_data.make_protobuf()

        signed_deploy = self.sign_deploy(
            deploy=deploy_proto, key_holder=deploy_data.key_holder
        )
        self.send_deploy(signed_deploy)
        return signed_deploy.deploy_hash.hex()

    @api
    def transfer(
        self,
        amount: int,
        target_account: Union[str, bytes] = None,
        target_purse: Union[str, bytes] = None,
        source_purse: Union[str, bytes] = None,
        from_addr: Union[str, bytes] = None,
        private_key: str = None,
        private_key_hex: str = None,
        algorithm: str = ED25519_KEY_ALGORITHM,
        payment: str = None,
        payment_args: bytes = None,
        payment_amount: int = None,
        payment_hash: bytes = None,
        payment_name: str = None,
        payment_package_hash: bytes = None,
        payment_package_name: str = None,
        payment_entry_point: str = None,
        payment_version: int = None,
        ttl_millis: int = 0,
        dependencies=None,
        chain_name: str = None,
    ) -> str:
        """
        Transfer between account purses.

        :param amount: Amount to transfer
        :param target_account: Target account hash (base16/hex encoded), will use main purse.
        :param target_purse: URef of target purse (base16/hex encoded).
        :param source_purse: URef of source purse (base16/hex encoded). If omitted, will use main purse of account.
        :param from_addr: Account hash to use for deployment, generated from private_key or private_key_hex if omitted.
                          Default payment will use the main purse of this account, unless custom payment is provided.
        :param private_key: Path to a file with private key. Assumed to be ed25519 unless algorithm is given.
        :param private_key_hex: Private key (base16/hex encoded). Assumed to be ed25519 unless algorithm is given.
        :param algorithm: Algorithm used for generating keys, defaults to ed25519. See consts.SUPPORTED_KEY_ALGORITHMS
        :param payment: Path to the file with payment code as compiled wasm.
        :param payment_args: List of encoded arguments of payment contract
        :param payment_amount: Amount to be used with standard payment. Will pull from main purse.
        :param payment_hash: Hash (base16/hex encoded) of the stored contract to be called for payment.
        :param payment_name: Name of the stored contract to be called for payment.
        :param payment_package_hash Hash of the package to be called in the payment.
        :param payment_package_name Name of the package to be called in the payment.
        :param payment_entry_point: Name of Entrypoint in contract or package to call.
                                    Defaults to `call` if not given.
        :param payment_version: Version of the payment contract or package to use, defaults to latest if omitted
        :param ttl_millis: Time to live. Time (in milliseconds) that the deploy will remain valid for.
        :param dependencies: List of deploy hashes (hex/base16 encoded) which must be executed before this deploy.
        :param chain_name: Name of the chain to optionally restrict the deploy from being accidentally included anywhere else.
        :return: deploy_hash (base16/hex encoded) of transfer
        """
        if len(list(filter(None, (target_purse, target_account)))) != 1:
            raise ValueError("must include either target_account or target_purse")

        target_account_bytes = optional_base64_base16_to_bytes(
            target_account, "target_account"
        )
        target_purse_bytes = optional_base64_base16_to_bytes(
            target_purse, "target_purse"
        )
        source_purse_bytes = optional_base64_base16_to_bytes(
            source_purse, "source_purse"
        )

        target_send_bytes = target_account_bytes or target_purse_bytes

        arg_list = [
            abi.ABI.fixed_list("target", target_send_bytes),
            abi.ABI.u512("amount", amount),
        ]
        if source_purse_bytes:
            arg_list.append(abi.ABI.fixed_list("source", source_purse_bytes))

        transfer_args = abi.ABI.args(arg_list)
        return self.deploy(
            from_addr=from_addr,
            private_key=private_key,
            private_key_hex=private_key_hex,
            algorithm=algorithm,
            payment=payment,
            payment_args=payment_args,
            payment_amount=payment_amount,
            payment_hash=payment_hash,
            payment_name=payment_name,
            payment_package_hash=payment_package_hash,
            payment_package_name=payment_package_name,
            payment_entry_point=payment_entry_point,
            payment_version=payment_version,
            ttl_millis=ttl_millis,
            dependencies=dependencies,
            chain_name=chain_name,
            transfer_args=transfer_args,
        )

    @api
    def send_deploy(self, deploy=None, deploy_file=None) -> str:
        """
        Sends deploy to network from either deploy protobuf object or file.

        :param deploy: Protobuf deploy object
        :param deploy_file: File holding Protobuf deploy object
        :return: deploy hash (base16/hex encoded)
        """
        if deploy is None:
            if deploy_file is None:
                raise ValueError("Must have either deploy or deploy_file.")
            deploy = io.read_deploy_file(deploy_file)
        self.casper_service.Deploy(casper.DeployRequest(deploy=deploy))
        return deploy.deploy_hash.hex()

    @api
    def show_blocks(self, depth: int = 1, max_rank: int = 0, full_view: bool = True):
        """
        Get slices of the DAG, going backwards, rank by rank.

        :param depth: How many of the top ranks of the DAG to show.
        :param max_rank: Maximum rank to go back from. 0 means go from the current tip of the DAG.
        :param full_view: Full view if True, otherwise basic.
        :return: Generator of block info objects.
        """
        yield from self.casper_service.StreamBlockInfos_stream(
            casper.StreamBlockInfosRequest(
                depth=depth,
                max_rank=max_rank,
                view=(
                    full_view and info.BlockInfo.View.FULL or info.BlockInfo.View.BASIC
                ),
            )
        )

    @api
    def showBlocks(self, depth: int = 1, max_rank=0, full_view=True):
        """DEPRECATED: Call `show_blocks`"""
        warnings.warn(
            "showBlocks is deprecated and replaced with show_blocks.",
            DeprecationWarning,
        )
        for block_info_request in self.show_blocks(depth, max_rank, full_view):
            yield block_info_request

    @api
    def show_block(self, block_hash_base16: str, full_view=True):
        """
        Returns object describing a block on the network.

        :param block_hash_base16: hash of the block to be retrieved
        :param full_view: full view if True, otherwise basic
        :return: object representing the retrieved block
        """
        return self.casper_service.GetBlockInfo(
            casper.GetBlockInfoRequest(
                block_hash_base16=block_hash_base16,
                view=(
                    full_view and info.BlockInfo.View.FULL or info.BlockInfo.View.BASIC
                ),
            )
        )

    @api
    def showBlock(self, block_hash_base16: str, full_view=True):
        """DEPRECATED: call `show_block`"""
        warnings.warn(
            "showBlock is deprecated and replaced with show_block.", DeprecationWarning
        )
        return self.show_block(block_hash_base16, full_view)

    @api
    def visualize_dag(
        self,
        depth: int,
        out: str = None,
        show_justification_lines: bool = False,
        stream: str = None,
        delay_in_seconds=consts.VISUALIZE_DAG_STREAM_DELAY,
    ):
        """
        Visualize network dag.

        :param depth: Depth in terms of block height.
        :param out: Output image filename, outputs to stdout if not specified.
                    Must end with one of the png, svg, svg_standalone, xdot, plain, plain_ext, ps, ps2, json, json0
        :param show_justification_lines: If justification lines should be shown.
        :param stream: Subscribe to changes. 'out' must be specified.
                       Valid values are 'single-output', 'multiple-outputs'
        :param delay_in_seconds: Delay in seconds when polling for updates (streaming)
        :return: Yields generated DOT source or file name when out provided.
                 Generates endless stream of file names if stream is not None.
        """
        block_infos = list(self.show_blocks(depth, full_view=False))
        dot_dag_description = vdag.generate_dot(block_infos, show_justification_lines)
        if not out:
            yield dot_dag_description
            return

        parts = out.split(".")
        file_format = parts[-1]
        file_name_base = ".".join(parts[:-1])

        iteration = -1

        def file_name():
            nonlocal iteration, file_format
            if not stream or stream == "single-output":
                return out
            else:
                iteration += 1
                return f"{file_name_base}_{iteration}.{file_format}"

        yield vdag.call_dot(dot_dag_description, file_name(), file_format)
        previous_block_hashes = set(b.summary.block_hash for b in block_infos)
        while stream:
            time.sleep(delay_in_seconds)
            block_infos = list(self.show_blocks(depth, full_view=False))
            block_hashes = set(b.summary.block_hash for b in block_infos)
            if block_hashes != previous_block_hashes:
                dot_dag_description = vdag.generate_dot(
                    block_infos, show_justification_lines
                )
                yield vdag.call_dot(dot_dag_description, file_name(), file_format)
                previous_block_hashes = block_hashes

    @api
    def visualizeDag(
        self,
        depth: int,
        out: str = None,
        show_justification_lines: bool = False,
        stream: str = None,
        delay_in_seconds=5,
    ):
        """DEPRECATED: call `visualize_dag`"""
        warnings.warn(
            "visualizeDag is deprecated and replaced with visualize_dag.",
            DeprecationWarning,
        )
        for output in self.visualize_dag(
            depth, out, show_justification_lines, stream, delay_in_seconds
        ):
            yield output

    @api
    def query_state(self, block_hash: str, key: str, path: str, key_type: str):
        """
        Query a value in the global state.

        :param block_hash: Hash of the block (base16/hex encoding) of which to query.
        :param key: Base key (base16/hex encoded).
        :param path: Path to the value to query. Must be of the form 'key1/key2/.../key[n]'
        :param key_type: Type of base key. Must be one of 'hash', 'uref', 'address' or 'local'.
                         For 'local' key type, 'key' value format is {seed}:{rest},
                         where both parts are base16/hex encoded.
        :return: QueryStateResponse object
        """
        q = casper.StateQuery(key_variant=key_variant(key_type), key_base16=key)
        q.path_segments.extend([name for name in path.split("/") if name])
        return self.casper_service.GetBlockState(
            casper.GetBlockStateRequest(block_hash_base16=block_hash, query=q)
        )

    @api
    def queryState(self, blockHash: str, key: str, path: str, keyType: str):
        """DEPRECATED: call `query_state`"""
        warnings.warn(
            "queryState is deprecated and replaced with query_state.",
            DeprecationWarning,
        )
        return self.query_state(blockHash, key, path, keyType)

    @api
    def keygen(
        self,
        directory: Union[Path, str],
        algorithm: str = ED25519_KEY_ALGORITHM,
        filename_prefix: str = consts.DEFAULT_KEY_FILENAME_PREFIX,
    ) -> None:
        """
        Generates account keys into existing directory.
        Existing files in directory will be overwritten.

        :param directory: output directory, must exist
        :param algorithm: Algorithm used for generating keys, defaults to ed25519. See consts.SUPPORTED_KEY_ALGORITHMS
        :param filename_prefix: Prefix to use for files, default is 'account'
        :return: None

        Generated files:
           {filename_prefix}-id           # Hash of public key to use in the system (base64 encoded)
           {filename_prefix}-id-hex       # Hash of public key to use in the system (base16/hex encoded)
           {filename_prefix}-pk           # Public key (base64 encoded)
           {filename_prefix}-pk-hex       # Public key (base16/hex encoded)
           {filename_prefix}-private.pem  # private key pem file
           {filename_prefix}-public.pem   # public key pen file
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Destination directory: {directory} does not exists.")

        key_holder_generator = key_holders.class_from_algorithm(algorithm)
        key_holder = key_holder_generator.generate()
        key_holder.save_pem_files(directory, filename_prefix)
        key_holder.save_hex_base64_files(directory, filename_prefix)

    @api
    def balance(self, address: str, block_hash: str) -> int:
        """
        Return balance of the main purse of an account

        :param address: Public key hash address of account.
        :param block_hash: Hash of block from which to return balance.
        :return: purse balance as int
        """
        # TODO: Should add ability to get balance of other purse with URef
        value = self.query_state(block_hash, address, "", "address")
        try:
            account = value.account
        except AttributeError:
            raise InternalError(
                "balance", f"Expected Account type value under {address}."
            )

        purse_addr_hex = account.main_purse.uref.hex()

        balance_u_ref = self.query_state(block_hash, purse_addr_hex, "", "hash")
        balance_u_ref_hex = balance_u_ref.cl_value.value.key.uref.uref.hex()
        balance = self.query_state(block_hash, balance_u_ref_hex, "", "uref")
        balance_str_value = balance.cl_value.value.u512.value
        return int(balance_str_value)

    @api
    def show_deploy(
        self,
        deploy_hash: str,
        full_view: bool = False,
        wait_for_processed: bool = False,
        delay: int = consts.STATUS_CHECK_DELAY,
        timeout_seconds: int = consts.STATUS_TIMEOUT,
    ):
        """
        Retrieve information about a single deploy by hash.

        :param deploy_hash: Hash of deploy (base16/hex encoded).
        :param full_view: Show full view of deploy, default False
        :param wait_for_processed: Block return of method until deploy is not pending, default False.
        :param delay: Delay between status checks while waiting, default consts.STATUS_CHECK_DELAY
        :param timeout_seconds: Time to wait, default consts.STATUS_TIMEOUT
                                Exception is raised if still pending when timeout occurs.
        :return: deploy_info
        """
        start_time = time.time()
        while True:
            deploy_info = self.casper_service.GetDeployInfo(
                casper.GetDeployInfoRequest(
                    deploy_hash_base16=deploy_hash,
                    view=common.deploy_info_view(full_view),
                )
            )
            if (
                wait_for_processed
                and deploy_info.status.state == info.DeployInfo.State.PENDING
            ):
                if time.time() - start_time > timeout_seconds:
                    raise Exception(
                        f"Timed out waiting for deploy {deploy_hash} to be processed"
                    )
                time.sleep(delay)
                continue
            return deploy_info

    @api
    def showDeploy(
        self,
        deploy_hash_base16: str,
        full_view: bool = False,
        wait_for_processed: bool = False,
        delay: int = consts.STATUS_CHECK_DELAY,
        timeout_seconds: int = consts.STATUS_TIMEOUT,
    ):
        """DEPRECATED: call `show_deploy`"""
        warnings.warn(
            "showDeploy is deprecated and replaced with show_deploy.",
            DeprecationWarning,
        )
        return self.show_deploy(
            deploy_hash_base16, full_view, wait_for_processed, delay, timeout_seconds
        )

    @api
    def show_deploys(self, block_hash_base16: str, full_view=True):
        """
        Get the processed deploys within a block.
        """
        yield from self.casper_service.StreamBlockDeploys_stream(
            casper.StreamBlockDeploysRequest(
                block_hash_base16=block_hash_base16,
                view=common.deploy_info_view(full_view),
            )
        )

    @api
    def showDeploys(self, block_hash_base16: str, full_view=True):
        """DEPRECATED: use `show_deploys`"""
        warnings.warn(
            "showDeploys is deprecated and replaced with show_deploys.",
            DeprecationWarning,
        )
        for block_deploys in self.show_deploy(block_hash_base16, full_view):
            yield block_deploys

    @api
    def stream_events(
        self,
        all: bool = False,
        block_added: bool = False,
        block_finalized: bool = False,
        deploy_added: bool = False,
        deploy_discarded: bool = False,
        deploy_requeued: bool = False,
        deploy_processed: bool = False,
        deploy_finalized: bool = False,
        deploy_orphaned: bool = False,
        account_public_key_hashes: List[str] = None,
        deploy_hashes: List[str] = None,
        min_event_id: int = 0,
        max_event_id: int = 0,
    ):
        """
        Generator of events from a node.  Allows replay or subscription to all future events.

        :param all: subscribe to all events, ignores other event values passed.
        :param block_added: subscribe to block added event.
        :param block_finalized: subscribe to block finalized event.
        :param deploy_added: subscribe to deploy added event.
        :param deploy_discarded: subscribe to deploy discarded event.
        :param deploy_requeued: subscribe to deploy requeued event.
        :param deploy_processed: subscribe to deploy processed event.
        :param deploy_finalized: subscribe to deploy finalized event.
        :param deploy_orphaned: subscribe to deploy orphaned event.
        :param account_public_key_hashes: list of account public key hashes (hex/base16 encoded) to use as a filter.
        :param deploy_hashes: list of deploy_hashes (hex/base16 encoded) to use as a filter.
        :param min_event_id: Value of 0 will subscribe to future events.
                             Non-zero values, will replay all past events from that ID, without subscribing to new.
                             To catch up with events from the beginning, start from 1.
        :param max_event_id: Id to stop replaying past events.
        :return: generator

        .. see also::
            See StreamEventsRequest in
                https://github.com/CasperLabs/CasperLabs/protobuf/io/casperlabs/node/api/casper.proto
            for description of types of events.
        """
        if not any(
            (
                all,
                block_added,
                block_finalized,
                deploy_added,
                deploy_discarded,
                deploy_requeued,
                deploy_processed,
                deploy_finalized,
                deploy_orphaned,
            )
        ):
            raise ValueError("No events given to subscribe.")

        if all:
            block_added = True
            block_finalized = True
            deploy_added = True
            deploy_discarded = True
            deploy_requeued = True
            deploy_processed = True
            deploy_finalized = True
            deploy_orphaned = True

        if account_public_key_hashes is None:
            account_public_key_hashes = []
        if deploy_hashes is None:
            deploy_hashes = []

        deploy_filter = casper.StreamEventsRequest.DeployFilter(
            account_public_key_hashes=[
                bytes.fromhex(pk) for pk in account_public_key_hashes
            ],
            deploy_hashes=[bytes.fromhex(h) for h in deploy_hashes],
        )

        yield from self.casper_service.StreamEvents_stream(
            casper.StreamEventsRequest(
                block_added=block_added,
                block_finalized=block_finalized,
                deploy_added=deploy_added,
                deploy_discarded=deploy_discarded,
                deploy_requeued=deploy_requeued,
                deploy_processed=deploy_processed,
                deploy_finalized=deploy_finalized,
                deploy_orphaned=deploy_orphaned,
                deploy_filter=deploy_filter,
                min_event_id=min_event_id,
                max_event_id=max_event_id,
            )
        )

    @staticmethod
    @api
    def validator_keygen(directory: Union[Path, str]) -> None:
        """
        Generate validator and node keys.

        :param directory: Directory in which to create files. Must exist.

        Generated files:
           node-id               # node ID as in casperlabs://c0a6c82062461c9b7f9f5c3120f44589393edf31@<NODE ADDRESS>?protocol=40400&discovery=40404
                                 # derived from node.key.pem
           node.certificate.pem  # TLS certificate used for node-to-node interaction encryption
                                 # derived from node.key.pem
           node.key.pem          # secp256r1 private key
           validator-pk          # validator public key in base64 format
           validator-pk-hex      # validator public key in hex/base16
           validator-id          # validator account hash in base64 format
           validator-id-hex      # validator account hash in hex/base16
           validator-private.pem # ed25519 private key
           validator-public.pem  # ed25519 public key
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Destination directory: {directory} does not exists.")

        node_private_path = directory / consts.NODE_PRIVATE_KEY_FILENAME
        node_cert_path = directory / consts.NODE_CERTIFICATE_FILENAME
        node_id_path = directory / consts.NODE_ID_FILENAME

        key_pair = key_holders.ED25519Key.generate()
        key_pair.save_pem_files(directory, consts.VALIDATOR_FILENAME_PREFIX)
        key_pair.save_hex_base64_files(directory, consts.VALIDATOR_FILENAME_PREFIX)

        private_key, public_key = crypto.generate_secp256r1_key_pair()
        node_cert, key_pem = crypto.generate_node_certificates(private_key, public_key)

        io.write_binary_file(node_private_path, key_pem)
        io.write_binary_file(node_cert_path, node_cert)
        io.write_file(node_id_path, crypto.node_public_address(public_key))

    @api
    def wait_for_deploy_processed(
        self,
        deploy_hash,
        on_error_raise=True,
        delay=consts.STATUS_CHECK_DELAY,
        timeout_seconds=consts.STATUS_TIMEOUT,
    ):
        """
        Block up to `timeout_seconds` while `info.DeployInfo.State` is PENDING.


        :param deploy_hash: base16 (hex) deploy hash to wait for processing
        :param on_error_raise: raise and exception if the execution of the deploy is_error
        :param delay: delay between checks in milliseconds
        :param timeout_seconds: time to raise exception to exit if state is still PENDING
        :return: result of deploy


        """
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout_seconds:
                raise Exception(
                    f"Timed out waiting for deploy {deploy_hash} to be processed"
                )

            result = self.show_deploy(deploy_hash, full_view=False)
            if result.status.state != info.DeployInfo.State.PENDING:
                break
            time.sleep(delay)

        if on_error_raise:
            if len(result.processing_results) == 0:
                raise Exception(f"Deploy {deploy_hash} status: {result.status}")

            last_processing_result = result.processing_results[0]
            if last_processing_result.is_error:
                raise Exception(
                    f"Deploy {deploy_hash} execution error: {last_processing_result.error_message}"
                )
        return result

    @api
    def show_peers(self) -> List:
        """ Return list of nodes connected to current node. """
        return list(self.diagnostics_service.ListPeers(empty_pb2.Empty()).peers)

    @api
    def account_hash(
        self, algorithm: str, public_key: bytes = None, public_key_pem_path: str = None
    ) -> bytes:
        """ Create account hash based on algorithm and public key or public_key_path

        :param algorithm: Algorithm used for generating keys, defaults to ed25519. See consts.SUPPORTED_KEY_ALGORITHMS
        :param public_key:          Public Key as bytes
        :param public_key_pem_path: File path to public_key pem file
        """
        key_holder = key_holders.key_holder_object(
            algorithm=algorithm,
            public_key=public_key,
            public_key_pem_path=public_key_pem_path,
        )
        return key_holder.account_hash
