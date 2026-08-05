import hashlib
import hmac

from utils import hash_tools


def test_generate_hashes_matches_stdlib():
    result = hash_tools.generate_hashes("hello world")

    assert result["ok"] is True
    assert result["digests"]["md5"] == hashlib.md5(b"hello world").hexdigest()
    assert result["digests"]["sha256"] == hashlib.sha256(b"hello world").hexdigest()
    assert result["digests"]["sha512"] == hashlib.sha512(b"hello world").hexdigest()
    assert set(result["digests"]) == set(hash_tools.HASH_ALGORITHMS)


def test_generate_hashes_empty_string_still_hashes():
    result = hash_tools.generate_hashes("")

    assert result["ok"] is True
    assert result["digests"]["sha256"] == hashlib.sha256(b"").hexdigest()


def test_generate_hashes_rejects_oversized_input():
    result = hash_tools.generate_hashes("a" * (hash_tools.MAX_INPUT_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_generate_hmac_matches_stdlib():
    result = hash_tools.generate_hmac("payload", "secret", "sha256")

    assert result["ok"] is True
    expected = hmac.new(b"secret", b"payload", "sha256").hexdigest()
    assert result["digest"] == expected


def test_generate_hmac_validation_errors():
    assert hash_tools.generate_hmac("x", "", "sha256")["error"] == "Enter a secret key."
    assert hash_tools.generate_hmac("x", "key", "sha1024")["error"] == "Unsupported algorithm: sha1024."
