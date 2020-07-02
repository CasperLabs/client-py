# -*- coding: utf-8 -*-
from casperlabs_client import CasperLabsClient, consts, reformat
from casperlabs_client.commands.common_options import (
    FROM_OPTION,
    CHAINNAME_OPTION,
    DEPENDENCIES_OPTION,
    TTL_MILLIS_OPTION,
    private_key_option,
    WAIT_PROCESSED_OPTION,
    TIMEOUT_SECONDS_OPTION,
    ALGORITHM_OPTION,
    PAYMENT_OPTIONS,
)
from casperlabs_client.decorators import guarded_command


NAME: str = "transfer"
HELP: str = "Transfers funds between accounts"
OPTIONS = [
    [
        ("-a", "--amount"),
        dict(
            required=True,
            default=None,
            type=int,
            help="Amount of motes to transfer. Note: a mote is the smallest, indivisible unit of a token.",
        ),
    ],
    [
        ("-t", "--target-account"),
        dict(
            required=False,
            type=str,
            help="base64 or base16 representation of target account's public key",
        ),
    ],
    [
        ("--target-purse",),
        dict(
            required=False,
            type=str,
            help="base64 or base16 representation of target purse URef",
        ),
    ],
    [
        ("--source-purse",),
        dict(
            required=False,
            type=str,
            help="base64 or base16 representation of source purse URef",
        ),
    ],
    FROM_OPTION,
    CHAINNAME_OPTION,
    DEPENDENCIES_OPTION,
    TTL_MILLIS_OPTION,
    WAIT_PROCESSED_OPTION,
    TIMEOUT_SECONDS_OPTION,
    ALGORITHM_OPTION,
    private_key_option(required=True),
] + PAYMENT_OPTIONS


@guarded_command
def method(casperlabs_client: CasperLabsClient, args: dict):
    deploy_hash = casperlabs_client.transfer(
        amount=args.get("amount"),
        target_account=args.get("target_account"),
        target_purse=args.get("target_purse"),
        source_purse=args.get("source_purse"),
        from_addr=args.get("from_addr"),
        private_key=args.get("private_key"),
        ttl_millis=args.get("ttl_millis"),
        dependencies=args.get("dependencies"),
        chain_name=args.get("chain_name"),
        algorithm=args.get("algorithm"),
        payment=args.get("payment"),
        payment_amount=args.get("payment_amount"),
        payment_args=args.get("payment_args"),
        payment_hash=args.get("payment_hash"),
        payment_name=args.get("payment_name"),
        payment_entry_point=args.get("payment_entry_point"),
        payment_package_hash=args.get("payment_package_hash"),
        payment_package_name=args.get("payment_package_name"),
    )
    print(f"Success! Deploy {deploy_hash} deployed")
    if args.get("wait_for_processed", False):
        deploy_info = casperlabs_client.showDeploy(
            deploy_hash,
            full_view=False,
            wait_for_processed=True,
            timeout_seconds=args.get("timeout_seconds", consts.STATUS_TIMEOUT),
        )
        print(reformat.hexify(deploy_info))
