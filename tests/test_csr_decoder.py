from __future__ import annotations

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.x509.oid import NameOID

from utils.csr_decoder import decode_csr


def _make_rsa_csr(cn="example.com", san=None, key_size=2048):
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    builder = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)]))
    if san:
        builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(name) for name in san]), critical=False)
    csr = builder.sign(key, hashes.SHA256())
    return csr.public_bytes(serialization.Encoding.PEM).decode()


def test_decode_csr_rsa_with_san():
    pem = _make_rsa_csr(san=["example.com", "www.example.com"])

    result = decode_csr(pem)

    assert result["ok"] is True
    assert result["subject"] == "CN=example.com"
    assert result["san_names"] == ["example.com", "www.example.com"]
    assert result["public_key_algorithm"] == "RSA"
    assert result["public_key_size"] == 2048
    assert result["signature_algorithm"] == "sha256"
    assert result["signature_valid"] is True


def test_decode_csr_no_san():
    pem = _make_rsa_csr()

    result = decode_csr(pem)

    assert result["ok"] is True
    assert result["san_names"] == []


def test_decode_csr_ec_key():
    key = ec.generate_private_key(ec.SECP256R1())
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ec.example.com")])).sign(key, hashes.SHA256())
    pem = csr.public_bytes(serialization.Encoding.PEM).decode()

    result = decode_csr(pem)

    assert result["ok"] is True
    assert "EC" in result["public_key_algorithm"]
    assert result["public_key_size"] == 256


def test_decode_csr_ed25519_key_reports_none_size_not_zero():
    # Regression: Ed25519PublicKey has no .key_size attribute -- the old
    # code's fallback branch reported a fabricated "0", indistinguishable
    # from a real (broken) 0-bit key. None is the honest signal (rendered
    # as "N/A" in the UI), and the algorithm name must be the clean
    # "Ed25519", not the raw Python class name "Ed25519PublicKey".
    key = ed25519.Ed25519PrivateKey.generate()
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ed25519.example.com")])).sign(key, None)
    pem = csr.public_bytes(serialization.Encoding.PEM).decode()

    result = decode_csr(pem)

    assert result["ok"] is True
    assert result["public_key_algorithm"] == "Ed25519"
    assert result["public_key_size"] is None
    assert result["signature_algorithm"] == "EdDSA (no separate hash)"


def test_decode_csr_rejects_empty_input():
    result = decode_csr("")

    assert result["ok"] is False
    assert result["error"] == "Paste a PEM-encoded CSR."


def test_decode_csr_rejects_invalid_pem():
    result = decode_csr("not a csr")

    assert result["ok"] is False
    assert "Could not parse CSR" in result["error"]


def test_decode_csr_rejects_oversized_input():
    result = decode_csr("a" * 10_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
