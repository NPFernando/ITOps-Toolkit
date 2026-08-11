from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from utils.ssh_fingerprint import compute_fingerprint


def _sample_key_line(comment="user@host"):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = key.public_key()
    line = pub.public_bytes(encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH).decode()
    return f"{line} {comment}" if comment else line


def test_compute_fingerprint_plain_key():
    result = compute_fingerprint(_sample_key_line())

    assert result["ok"] is True
    assert result["key_type"] == "ssh-rsa"
    assert result["comment"] == "user@host"
    assert result["md5_fingerprint"].count(":") == 15
    assert result["sha256_fingerprint"].startswith("SHA256:")


def test_compute_fingerprint_known_hosts_style_line_strips_hostname():
    plain = _sample_key_line()
    known_hosts_line = f"example.com {plain}"

    plain_result = compute_fingerprint(plain)
    kh_result = compute_fingerprint(known_hosts_line)

    assert kh_result["ok"] is True
    assert kh_result["md5_fingerprint"] == plain_result["md5_fingerprint"]
    assert kh_result["sha256_fingerprint"] == plain_result["sha256_fingerprint"]


def test_compute_fingerprint_no_comment():
    result = compute_fingerprint(_sample_key_line(comment=""))

    assert result["ok"] is True
    assert result["comment"] is None


def test_compute_fingerprint_rejects_empty_input():
    result = compute_fingerprint("")

    assert result["ok"] is False
    assert result["error"] == "Paste a public SSH key."


def test_compute_fingerprint_rejects_single_token():
    result = compute_fingerprint("justoneword")

    assert result["ok"] is False
    assert "expected 'type base64-blob" in result["error"]


def test_compute_fingerprint_rejects_malformed_base64():
    result = compute_fingerprint("ssh-rsa notvalidbase64!!!")

    assert result["ok"] is False
    assert "Could not parse SSH public key" in result["error"]


def test_compute_fingerprint_rejects_oversized_input():
    result = compute_fingerprint("a" * 4001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
