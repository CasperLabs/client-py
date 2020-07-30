# -*- coding: utf-8 -*-
from pathlib import Path

from casperlabs_client import CasperLabsClient
from casperlabs_client.cli import cli


def test_cli_account_hash(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "account_hash")

    cli(
        "account-hash",
        "--public-key",
        "pkfile",
        "--file-path",
        "outpath",
        "--algorithm",
        "secp256k1",
        client=client,
    )

    client.account_hash.assert_called_with(
        public_key_pem_path="pkfile", algorithm="secp256k1"
    )


def test_cli_balance(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "balance")

    cli(
        "balance", "--address", "address", "--block-hash", "blockhash", client=client,
    )

    client.balance.assert_called_with("address", "blockhash")


def test_cli_deploy(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "deploy")

    cli(
        "deploy",
        "--from",
        "0000000000000000000000000000000000000000000000000000000000000000",
        "--private-key",
        "private_key_path",
        "--algorithm",
        "secp256k1",
        "--payment",
        "payment.wasm",
        "--payment-args",
        "paymentargs",
        "--payment-amount",
        1234,
        "--payment-hash",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "--payment-name",
        "paymentname",
        "--payment-package-hash",
        "2222222222222222222222222222222222222222222222222222222222222222",
        "--payment-package-name",
        "paymentpackagename",
        "--payment-entry-point",
        "paymententrypoint",
        "--payment-version",
        123,
        "--session",
        "session.wasm",
        "--session-args",
        "sessionargs",
        "--session-hash",
        "3333333333333333333333333333333333333333333333333333333333333333",
        "--session-name",
        "sessionname",
        "--session-package-hash",
        "44444444444444444444444444444444444444444444444444444444444444444",
        "--session-package-name",
        "sessionpackagename",
        "--session-entry-point",
        "sessionentrypoint",
        "--session-version",
        321,
        "--ttl-millis",
        987,
        "--dependencies",
        "one",
        "two",
        "--chain-name",
        "bob",
        client=client,
    )

    client.deploy.assert_called_with(
        from_addr="0000000000000000000000000000000000000000000000000000000000000000",
        private_key="private_key_path",
        algorithm="secp256k1",
        payment="payment.wasm",
        payment_args="paymentargs",
        payment_amount=1234,
        payment_hash="1111111111111111111111111111111111111111111111111111111111111111",
        payment_name="paymentname",
        payment_package_hash="2222222222222222222222222222222222222222222222222222222222222222",
        payment_package_name="paymentpackagename",
        payment_entry_point="paymententrypoint",
        payment_version=123,
        session="session.wasm",
        session_args="sessionargs",
        session_hash="3333333333333333333333333333333333333333333333333333333333333333",
        session_name="sessionname",
        session_package_hash="44444444444444444444444444444444444444444444444444444444444444444",
        session_package_name="sessionpackagename",
        session_entry_point="sessionentrypoint",
        session_version=321,
        ttl_millis=987,
        dependencies=["one", "two"],
        chain_name="bob",
    )


def test_cli_keygen(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "keygen")

    cli(
        "keygen", "/tmp", "--algorithm", "secp256k1", client=client,
    )

    client.keygen.assert_called_with(Path("/tmp"), "secp256k1")


def test_cli_make_deploy(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "make_deploy")

    cli(
        "make-deploy",
        "--public-key",
        "public_key_path",
        "--from",
        "0000000000000000000000000000000000000000000000000000000000000000",
        "--algorithm",
        "secp256k1",
        "--payment",
        "payment.wasm",
        "--payment-args",
        "paymentargs",
        "--payment-amount",
        1234,
        "--payment-hash",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "--payment-name",
        "paymentname",
        "--payment-package-hash",
        "2222222222222222222222222222222222222222222222222222222222222222",
        "--payment-package-name",
        "paymentpackagename",
        "--payment-entry-point",
        "paymententrypoint",
        "--payment-version",
        123,
        "--session",
        "session.wasm",
        "--session-args",
        "sessionargs",
        "--session-hash",
        "3333333333333333333333333333333333333333333333333333333333333333",
        "--session-name",
        "sessionname",
        "--session-package-hash",
        "44444444444444444444444444444444444444444444444444444444444444444",
        "--session-package-name",
        "sessionpackagename",
        "--session-entry-point",
        "sessionentrypoint",
        "--session-version",
        321,
        "--ttl-millis",
        987,
        "--dependencies",
        "one",
        "two",
        "--chain-name",
        "bob",
        client=client,
    )

    client.make_deploy.assert_called_with(
        from_addr="0000000000000000000000000000000000000000000000000000000000000000",
        public_key="public_key_path",
        algorithm="secp256k1",
        payment="payment.wasm",
        payment_args="paymentargs",
        payment_amount=1234,
        payment_hash="1111111111111111111111111111111111111111111111111111111111111111",
        payment_name="paymentname",
        payment_package_hash="2222222222222222222222222222222222222222222222222222222222222222",
        payment_package_name="paymentpackagename",
        payment_entry_point="paymententrypoint",
        payment_version=123,
        session="session.wasm",
        session_args="sessionargs",
        session_hash="3333333333333333333333333333333333333333333333333333333333333333",
        session_name="sessionname",
        session_package_hash="44444444444444444444444444444444444444444444444444444444444444444",
        session_package_name="sessionpackagename",
        session_entry_point="sessionentrypoint",
        session_version=321,
        ttl_millis=987,
        dependencies=["one", "two"],
        chain_name="bob",
    )


def test_cli_query_state(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "query_state")

    cli(
        "query-state",
        "--block-hash",
        "3333333333333333333333333333333333333333333333333333333333333333",
        "--key",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "--path",
        "path/path",
        "--type",
        "uref",
        client=client,
    )

    client.query_state.assert_called_with(
        "3333333333333333333333333333333333333333333333333333333333333333",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "path/path",
        "uref",
    )


def test_cli_send_deploy(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "send_deploy")

    cli(
        "send-deploy", "--deploy-path", "deploypath", client=client,
    )

    client.send_deploy.assert_called_with(deploy_file="deploypath")


def test_cli_show_block(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "show_block")

    cli(
        "show-block",
        "1111111111111111111111111111111111111111111111111111111111111111",
        client=client,
    )

    client.show_block.assert_called_with(
        "1111111111111111111111111111111111111111111111111111111111111111",
        full_view=True,
    )


def test_cli_show_blocks(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "show_blocks")

    cli(
        "show-blocks", "--depth", 10, client=client,
    )

    client.show_blocks.assert_called_with(
        10, full_view=False,
    )


def test_cli_show_deploy(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "show_deploy")

    cli(
        "show-deploy",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "--wait-for-processed",
        "--timeout-seconds",
        123,
        client=client,
    )

    client.show_deploy.assert_called_with(
        "1111111111111111111111111111111111111111111111111111111111111111",
        full_view=False,
        wait_for_processed=True,
        timeout_seconds=123,
    )


def test_cli_show_deploys(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "show_deploys")

    cli(
        "show-deploys",
        "1111111111111111111111111111111111111111111111111111111111111111",
        client=client,
    )

    client.show_deploys.assert_called_with(
        "1111111111111111111111111111111111111111111111111111111111111111",
        full_view=False,
    )


def test_cli_show_peers(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "show_peers")

    cli(
        "show-peers", client=client,
    )

    client.show_peers.assert_called_with()


def test_cli_sign_deploy(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "sign_deploy")

    cli(
        "sign-deploy",
        "--private-key",
        "private_key_path",
        "--algorithm",
        "secp256k1",
        "--signed-deploy-path",
        "signeddeploypath",
        "--deploy-path",
        "deploypath",
        client=client,
    )

    client.sign_deploy.assert_called_with(
        private_key_pem_file="private_key_path",
        algorithm="secp256k1",
        deploy=None,
        deploy_file="deploypath",
    )


def test_cli_stream_events(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "stream_events")

    cli(
        "stream-events",
        "--all",
        "--block-added",
        "--block-finalized",
        "--deploy-added",
        "--deploy-discarded",
        "--deploy-requeued",
        "--deploy-processed",
        "--deploy-finalized",
        "--deploy-orphaned",
        "--account-hash",
        "0000000000000000000000000000000000000000000000000000000000000000",
        "--account-hash",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "--deploy-hash",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "--deploy-hash",
        "3333333333333333333333333333333333333333333333333333333333333333",
        "--format",
        "json",
        "--min-event-id",
        1,
        "--max-event-id",
        2,
        client=client,
    )

    client.stream_events.assert_called_with(
        all=True,
        block_added=True,
        block_finalized=True,
        deploy_added=True,
        deploy_discarded=True,
        deploy_requeued=True,
        deploy_processed=True,
        deploy_finalized=True,
        deploy_orphaned=True,
        account_public_key_hashes=[
            "0000000000000000000000000000000000000000000000000000000000000000",
            "1111111111111111111111111111111111111111111111111111111111111111",
        ],
        deploy_hashes=[
            "1111111111111111111111111111111111111111111111111111111111111111",
            "3333333333333333333333333333333333333333333333333333333333333333",
        ],
        min_event_id=1,
        max_event_id=2,
    )


def test_cli_transfer(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "transfer")

    cli(
        "transfer",
        "--amount",
        12345,
        "--target-account",
        "9999999999999999999999999999999999999999999999999999999999999999",
        "--target-purse",
        "8888888888888888888888888888888888888888888888888888888888888888",
        "--source-purse",
        "7777777777777777777777777777777777777777777777777777777777777777",
        "--from",
        "0000000000000000000000000000000000000000000000000000000000000000",
        "--private-key",
        "private_key_path",
        "--algorithm",
        "secp256k1",
        "--payment",
        "payment.wasm",
        "--payment-args",
        "paymentargs",
        "--payment-amount",
        1234,
        "--payment-hash",
        "1111111111111111111111111111111111111111111111111111111111111111",
        "--payment-name",
        "paymentname",
        "--payment-package-hash",
        "2222222222222222222222222222222222222222222222222222222222222222",
        "--payment-package-name",
        "paymentpackagename",
        "--payment-entry-point",
        "paymententrypoint",
        "--payment-version",
        123,
        "--ttl-millis",
        987,
        "--dependencies",
        "one",
        "two",
        "--chain-name",
        "bob",
        client=client,
    )

    client.transfer.assert_called_with(
        amount=12345,
        target_account="9999999999999999999999999999999999999999999999999999999999999999",
        target_purse="8888888888888888888888888888888888888888888888888888888888888888",
        source_purse="7777777777777777777777777777777777777777777777777777777777777777",
        from_addr="0000000000000000000000000000000000000000000000000000000000000000",
        private_key="private_key_path",
        algorithm="secp256k1",
        payment="payment.wasm",
        payment_args="paymentargs",
        payment_amount=1234,
        payment_hash="1111111111111111111111111111111111111111111111111111111111111111",
        payment_name="paymentname",
        payment_package_hash="2222222222222222222222222222222222222222222222222222222222222222",
        payment_package_name="paymentpackagename",
        payment_entry_point="paymententrypoint",
        payment_version=123,
        ttl_millis=987,
        dependencies=["one", "two"],
        chain_name="bob",
    )


def test_cli_validator_keygen(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "validator_keygen")

    cli(
        "validator-keygen", "/tmp", client=client,
    )

    client.validator_keygen.assert_called_with(Path("/tmp"))


def test_cli_visualize_dag(client: CasperLabsClient, mocker):
    mocker.patch.object(client, "visualize_dag")

    cli(
        "vdag",
        "--depth",
        100,
        "--out",
        "out.dot",
        "--show-justification-lines",
        "--stream",
        "single-output",
        client=client,
    )

    client.visualize_dag.assert_called_with(100, "out.dot", True, "single-output")
