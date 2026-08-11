from __future__ import annotations

from utils.csr_decoder import decode_csr
from utils.csr_generator import generate_csr


def test_generates_valid_csr():
    result = generate_csr("example.com", organization="Acme Inc", country="US")

    assert result["ok"] is True
    assert "BEGIN CERTIFICATE REQUEST" in result["csr_pem"]
    assert "BEGIN PRIVATE KEY" in result["private_key_pem"]


def test_generated_csr_decodes_correctly():
    result = generate_csr("example.com", organization="Acme Inc", country="US", san_domains=["example.com", "www.example.com"])
    decoded = decode_csr(result["csr_pem"])

    assert decoded["ok"] is True
    assert decoded["signature_valid"] is True
    assert "CN=example.com" in decoded["subject"]
    assert "O=Acme Inc" in decoded["subject"]
    assert decoded["san_names"] == ["example.com", "www.example.com"]


def test_rejects_empty_common_name():
    result = generate_csr("")

    assert result["ok"] is False
    assert "Common Name" in result["error"]


def test_rejects_invalid_country_length():
    result = generate_csr("example.com", country="USA")

    assert result["ok"] is False
    assert "2-letter code" in result["error"]


def test_rejects_unsupported_key_size():
    result = generate_csr("example.com", rsa_key_size=1024)

    assert result["ok"] is False
    assert "Unsupported RSA key size" in result["error"]


def test_no_san_extension_when_none_given():
    result = generate_csr("example.com")
    decoded = decode_csr(result["csr_pem"])

    assert decoded["san_names"] == []
