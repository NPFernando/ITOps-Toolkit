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


def test_compute_fingerprint_known_hosts_hostname_starting_with_ssh_dash():
    # Regression: a hostname that happens to start with "ssh-" (an ordinary
    # naming pattern, e.g. a bastion host) was previously mistaken for the
    # key-type token by a fixed-prefix heuristic, so the real key type was
    # never stripped and fingerprinting failed with a misleading
    # "Unsupported key type: b'ssh-bastion.corp.com'" error.
    plain = _sample_key_line()
    known_hosts_line = f"ssh-bastion.corp.com {plain}"

    plain_result = compute_fingerprint(plain)
    kh_result = compute_fingerprint(known_hosts_line)

    assert kh_result["ok"] is True
    assert kh_result["key_type"] == "ssh-rsa"
    assert kh_result["md5_fingerprint"] == plain_result["md5_fingerprint"]


def test_compute_fingerprint_cert_authority_marker_line():
    # Regression: "@cert-authority host type base64" has TWO leading
    # columns (marker + host), not one -- the old single-offset heuristic
    # left the hostname where the key-type token was expected.
    plain = _sample_key_line()
    marker_line = f"@cert-authority *.example.com {plain}"

    plain_result = compute_fingerprint(plain)
    result = compute_fingerprint(marker_line)

    assert result["ok"] is True
    assert result["md5_fingerprint"] == plain_result["md5_fingerprint"]


def test_compute_fingerprint_revoked_marker_line():
    plain = _sample_key_line()
    marker_line = f"@revoked badhost.example.com {plain}"

    plain_result = compute_fingerprint(plain)
    result = compute_fingerprint(marker_line)

    assert result["ok"] is True
    assert result["md5_fingerprint"] == plain_result["md5_fingerprint"]


def test_compute_fingerprint_hashed_known_hosts_line():
    # The HashKnownHosts-default OpenSSH format: a single hashed-hostname
    # column, "|1|salt|hash type base64 [comment]".
    plain = _sample_key_line()
    hashed_line = f"|1|F1E1KeoE/eEWtJqOTOkc3jP7DrY=|s1oPKl85/OCazF13N0Z6z5W3Zm0= {plain}"

    plain_result = compute_fingerprint(plain)
    result = compute_fingerprint(hashed_line)

    assert result["ok"] is True
    assert result["md5_fingerprint"] == plain_result["md5_fingerprint"]


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
