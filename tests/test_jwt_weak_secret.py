from __future__ import annotations

import warnings

import jwt

from utils.jwt_weak_secret import check_weak_secret


def _encode(payload, secret, algorithm="HS256"):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return jwt.encode(payload, secret, algorithm=algorithm)


def test_check_weak_secret_finds_known_weak_secret():
    token = _encode({"sub": "1"}, "secret")

    result = check_weak_secret(token)

    assert result["ok"] is True
    assert result["applicable"] is True
    assert result["algorithm"] == "HS256"
    assert result["matched_secret"] == "secret"


def test_check_weak_secret_no_match_for_strong_secret():
    token = _encode({"sub": "1"}, "a-very-long-random-secret-nobody-would-guess-1234567890")

    result = check_weak_secret(token)

    assert result["ok"] is True
    assert result["applicable"] is True
    assert result["matched_secret"] is None


def test_check_weak_secret_reports_not_applicable_for_rs256():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    token = jwt.encode({"sub": "1"}, pem, algorithm="RS256")

    result = check_weak_secret(token)

    assert result["ok"] is True
    assert result["applicable"] is False
    assert result["alg_status"] == "asymmetric"
    assert result["algorithm"] == "RS256"
    assert result["matched_secret"] is None


def test_check_weak_secret_flags_alg_none_as_unsigned_not_asymmetric():
    # Regression: alg="none" is the classic unsigned-JWT forgery vector --
    # it must never be reported as "asymmetric, nothing to check", which
    # would be actively misleading for a security-focused checker.
    token = jwt.encode({"sub": "1"}, "", algorithm="none")

    result = check_weak_secret(token)

    assert result["ok"] is True
    assert result["applicable"] is False
    assert result["alg_status"] == "unsigned"
    assert result["algorithm"] == "none"


def test_check_weak_secret_flags_missing_alg_distinctly():
    # Regression: a header with no 'alg' claim at all must not render as the
    # literal string "Algorithm 'None' is asymmetric..." (the same bare-None
    # rendering bug class fixed for UUID variant in PR #89).
    import base64
    import json

    header = base64.urlsafe_b64encode(json.dumps({"typ": "JWT"}).encode()).rstrip(b"=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "1"}).encode()).rstrip(b"=")
    signature = base64.urlsafe_b64encode(b"x").rstrip(b"=")
    token = (header + b"." + payload + b"." + signature).decode()

    result = check_weak_secret(token)

    assert result["ok"] is True
    assert result["applicable"] is False
    assert result["alg_status"] == "missing"
    assert result["algorithm"] is None


def test_check_weak_secret_rejects_oversized_input():
    result = check_weak_secret("a" * 20_001)

    assert result["ok"] is False
    assert "20000 characters" in result["error"]


def test_check_weak_secret_rejects_empty_input():
    result = check_weak_secret("")

    assert result["ok"] is False
    assert result["error"] == "Enter a JWT token."


def test_check_weak_secret_rejects_malformed_token():
    result = check_weak_secret("not-a-jwt")

    assert result["ok"] is False
    assert "Could not decode JWT" in result["error"]


def test_check_weak_secret_checks_hs384_and_hs512():
    for algorithm in ("HS384", "HS512"):
        token = _encode({"sub": "1"}, "admin", algorithm)
        result = check_weak_secret(token)
        assert result["matched_secret"] == "admin"
