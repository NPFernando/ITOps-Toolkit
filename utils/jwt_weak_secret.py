"""Test a JWT's HMAC signature against a small built-in list of common weak secrets.

Deliberately not a brute-force tool or a user-suppliable-wordlist tool -- a
fixed, small (~20-entry) built-in list, matching the roadmap item's explicit
scope: catch the "someone left the tutorial default secret in prod" class of
mistake, not perform real cryptanalysis.
"""

from __future__ import annotations

import warnings
from typing import Any

import jwt

HMAC_ALGORITHMS: tuple[str, ...] = ("HS256", "HS384", "HS512")

COMMON_WEAK_SECRETS: tuple[str, ...] = (
    "secret",
    "password",
    "123456",
    "changeme",
    "admin",
    "your-256-bit-secret",
    "supersecret",
    "test",
    "secretkey",
    "jwt_secret",
    "mysecret",
    "qwerty",
    "letmein",
    "topsecret",
    "default",
    "key",
    "jwtsecret",
    "s3cr3t",
    "abc123",
    "changethis",
)


def check_weak_secret(token: str) -> dict[str, Any]:
    """Check whether ``token``'s signature matches a common weak secret."""
    result: dict[str, Any] = {"ok": False, "error": None, "algorithm": None, "applicable": False, "matched_secret": None}

    token_value = (token or "").strip()
    if not token_value:
        result["error"] = "Enter a JWT token."
        return result

    try:
        header = jwt.get_unverified_header(token_value)
    except jwt.PyJWTError as exc:
        result["error"] = f"Could not decode JWT: {exc}"
        return result

    algorithm = header.get("alg")
    result["ok"] = True
    result["algorithm"] = algorithm

    if algorithm not in HMAC_ALGORITHMS:
        result["applicable"] = False
        return result

    result["applicable"] = True
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for candidate in COMMON_WEAK_SECRETS:
            try:
                jwt.decode(
                    token_value,
                    candidate,
                    algorithms=[algorithm],
                    options={"verify_exp": False, "verify_aud": False, "verify_iat": False, "verify_iss": False},
                )
            except jwt.InvalidSignatureError:
                continue
            except jwt.PyJWTError:
                continue
            result["matched_secret"] = candidate
            break

    return result
