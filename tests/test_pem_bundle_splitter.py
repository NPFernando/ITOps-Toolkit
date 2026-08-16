from __future__ import annotations

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from utils.pem_bundle_splitter import split_pem_bundle


def _make_cert(cn, valid_before_days_ago=1, valid_after_days=30):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=valid_before_days_ago))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=valid_after_days))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode()


def _make_not_yet_valid_cert(cn):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=60))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode()


def test_split_pem_bundle_two_certs():
    bundle = _make_cert("leaf.example.com") + _make_cert("intermediate.example.com")

    result = split_pem_bundle(bundle)

    assert result["ok"] is True
    assert len(result["certificates"]) == 2
    assert result["certificates"][0]["subject"] == "CN=leaf.example.com"
    assert result["certificates"][1]["subject"] == "CN=intermediate.example.com"
    assert result["certificates"][0]["index"] == 1
    assert result["certificates"][1]["index"] == 2


def test_split_pem_bundle_detects_expired_cert():
    bundle = _make_cert("expired.example.com", valid_before_days_ago=100, valid_after_days=-5)

    result = split_pem_bundle(bundle)

    assert result["ok"] is True
    assert result["certificates"][0]["is_expired"] is True


def test_split_pem_bundle_detects_valid_cert():
    bundle = _make_cert("valid.example.com")

    result = split_pem_bundle(bundle)

    assert result["certificates"][0]["is_expired"] is False
    assert result["certificates"][0]["is_not_yet_valid"] is False


def test_split_pem_bundle_detects_not_yet_valid_cert():
    # Regression: a cert whose validity period starts in the future was
    # previously indistinguishable from a currently-valid one (only
    # not_valid_after was checked) -- any TLS client would reject this cert
    # today, so it must not be silently reported as fine.
    bundle = _make_not_yet_valid_cert("future.example.com")

    result = split_pem_bundle(bundle)

    assert result["ok"] is True
    assert result["certificates"][0]["is_not_yet_valid"] is True
    assert result["certificates"][0]["is_expired"] is False


def test_split_pem_bundle_single_cert():
    bundle = _make_cert("only.example.com")

    result = split_pem_bundle(bundle)

    assert result["ok"] is True
    assert len(result["certificates"]) == 1


def test_split_pem_bundle_rejects_empty_input():
    result = split_pem_bundle("")

    assert result["ok"] is False
    assert result["error"] == "Paste a PEM certificate bundle."


def test_split_pem_bundle_rejects_invalid_pem():
    result = split_pem_bundle("not a certificate")

    assert result["ok"] is False
    assert "Could not parse certificate bundle" in result["error"]


def test_split_pem_bundle_rejects_oversized_input():
    result = split_pem_bundle("a" * 50_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
