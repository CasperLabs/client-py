# -*- coding: utf-8 -*-
from casperlabs_client import CasperLabsClient


def test_make_deploy(account_keys_directory):
    deploy = CasperLabsClient().make_deploy(
        from_addr=b"00000000000000000000000000000000",
        session_name="contract_name",
        payment_amount=100000,
    )
    assert deploy
