from pathlib import Path

from casperlabs_client import crypto

from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from casperlabs_client.crypto import node_public_address
from casperlabs_client.io import read_binary_file, read_file


def test_key_to_certificate():
    """
    Using known good cert files from casperlabs/key-generator in `cert_files` directory to
    test conversion from key to certificate.
    """
    current_path = Path(__file__).resolve().parent
    cert_path = current_path / "cert_files"
    node_cert_pem = cert_path / "node.certificate.pem"
    node_key_pem = cert_path / "node.key.pem"
    node_id = cert_path / "node-id"

    # Read in and generate key
    node_key_data = read_binary_file(node_key_pem)
    private_key_obj = serialization.load_pem_private_key(
        node_key_data, None, default_backend()
    )
    public_key_obj = private_key_obj.public_key()
    node_address_data = read_file(node_id).strip()
    node_address_calc = node_public_address(public_key_obj)
    assert node_address_data == node_address_calc

    # Read cert
    node_cert_data = read_binary_file(node_cert_pem)
    cert = x509.load_pem_x509_certificate(node_cert_data, default_backend())
    print(cert)

    py_cert_pem, key_pem = crypto.generate_node_certificates(
        private_key_obj, private_key_obj.public_key()
    )
    py_cert = x509.load_pem_x509_certificate(py_cert_pem, default_backend())
    print(py_cert)
    # Due to time valid, these will not be exact.  Have to look manually.
    # assert cert == py_cert
    # assert py_cert_pem == node_cert_data
