"""Bcrypt hash generation and verification.

Complements the existing Hash Generator, which only covers fixed-digest
algorithms (MD5/SHA family) -- bcrypt is a salted, adaptive-cost scheme,
useful when testing an application's own auth/password storage.
"""

from __future__ import annotations

from typing import Any

import bcrypt

MIN_ROUNDS = 4
MAX_ROUNDS = 15  # 16 already takes several seconds per hash; cap before it becomes a DoS vector on a shared public app
MAX_PASSWORD_BYTES = 72  # bcrypt's own hard limit


def hash_password(password: str, rounds: int = 12) -> dict[str, Any]:
    """Hash ``password`` with bcrypt at the given cost factor."""
    result: dict[str, Any] = {"ok": False, "hash": None, "error": None}
    if not password:
        result["error"] = "Enter a password to hash."
        return result
    if not MIN_ROUNDS <= rounds <= MAX_ROUNDS:
        result["error"] = f"Rounds must be between {MIN_ROUNDS} and {MAX_ROUNDS}."
        return result

    encoded = password.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        result["error"] = f"Password is longer than {MAX_PASSWORD_BYTES} bytes -- bcrypt truncates or rejects longer input."
        return result

    digest = bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=rounds))
    result.update({"ok": True, "hash": digest.decode("ascii")})
    return result


def verify_password(password: str, existing_hash: str) -> dict[str, Any]:
    """Verify ``password`` against an existing bcrypt hash."""
    result: dict[str, Any] = {"ok": False, "matches": False, "error": None}
    if not password:
        result["error"] = "Enter a password to verify."
        return result
    if not existing_hash:
        result["error"] = "Enter an existing bcrypt hash to verify against."
        return result

    encoded_password = password.encode("utf-8")
    if len(encoded_password) > MAX_PASSWORD_BYTES:
        result["error"] = f"Password is longer than {MAX_PASSWORD_BYTES} bytes -- bcrypt truncates or rejects longer input."
        return result

    try:
        matches = bcrypt.checkpw(encoded_password, existing_hash.strip().encode("ascii"))
    except ValueError:
        result["error"] = "Not a valid bcrypt hash."
        return result

    result.update({"ok": True, "matches": matches})
    return result
