from __future__ import annotations

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from utils.cert_chain_validator import validate_chain_order


def _build_cert(name: str, issuer_key=None, issuer_name=None):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
    signer_key = issuer_key or key
    issuer = issuer_name or subject
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(signer_key, hashes.SHA256())
    )
    return key, cert


def _pem(cert) -> str:
    return cert.public_bytes(serialization.Encoding.PEM).decode()


def test_correctly_ordered_chain_is_valid():
    root_key, root_cert = _build_cert("Root CA")
    _leaf_key, leaf_cert = _build_cert("example.com", issuer_key=root_key, issuer_name=root_cert.subject)

    result = validate_chain_order(_pem(leaf_cert) + _pem(root_cert))

    assert result["ok"] is True
    assert result["chain_valid"] is True
    assert result["links"][0]["names_match"] is True
    assert result["links"][0]["signature_verified"] is True


def test_wrong_order_is_detected():
    root_key, root_cert = _build_cert("Root CA")
    _leaf_key, leaf_cert = _build_cert("example.com", issuer_key=root_key, issuer_name=root_cert.subject)

    result = validate_chain_order(_pem(root_cert) + _pem(leaf_cert))

    assert result["ok"] is True
    assert result["chain_valid"] is False
    assert result["links"][0]["names_match"] is False


def test_signature_mismatch_detected_even_with_matching_names():
    # A chain where the subject/issuer names line up but the wrong key
    # actually signed it -- name matching alone can't catch this.
    root_key, root_cert = _build_cert("Root CA")
    other_key, _other_cert = _build_cert("Other CA")
    _leaf_key, leaf_cert = _build_cert("example.com", issuer_key=other_key, issuer_name=root_cert.subject)

    result = validate_chain_order(_pem(leaf_cert) + _pem(root_cert))

    assert result["chain_valid"] is False
    assert result["links"][0]["names_match"] is True
    assert result["links"][0]["signature_verified"] is False


def test_rejects_single_certificate():
    _key, cert = _build_cert("Root CA")

    result = validate_chain_order(_pem(cert))

    assert result["ok"] is False
    assert "at least two" in result["error"]


def test_rejects_empty_input():
    result = validate_chain_order("")

    assert result["ok"] is False


def test_rejects_invalid_pem():
    result = validate_chain_order("not a certificate")

    assert result["ok"] is False
    assert "Could not parse" in result["error"]
