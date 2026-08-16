"""TOTP (time-based one-time passcode) generation and validation, via pyotp."""

from __future__ import annotations

import time
from typing import Any

import pyotp

TOTP_PERIOD_SECONDS = 30
MAX_SECRET_LENGTH = 128
MAX_CODE_LENGTH = 16


def generate_secret() -> str:
    """Generate a new random base32 TOTP secret."""
    return pyotp.random_base32()


def current_code(secret: str) -> dict[str, Any]:
    """Generate the current TOTP code for ``secret`` and the seconds remaining in this window."""
    result: dict[str, Any] = {"ok": False, "code": None, "seconds_remaining": None, "error": None}
    cleaned = (secret or "").strip().replace(" ", "")
    if not cleaned:
        result["error"] = "Enter a base32 secret (or generate a new one)."
        return result
    if len(cleaned) > MAX_SECRET_LENGTH:
        result["error"] = f"Secret is longer than {MAX_SECRET_LENGTH} characters."
        return result

    try:
        totp = pyotp.TOTP(cleaned, interval=TOTP_PERIOD_SECONDS)
        code = totp.now()
    except Exception:
        result["error"] = "Invalid base32 secret."
        return result

    seconds_remaining = TOTP_PERIOD_SECONDS - int(time.time()) % TOTP_PERIOD_SECONDS
    result.update({"ok": True, "code": code, "seconds_remaining": seconds_remaining})
    return result


def verify_code(secret: str, code: str) -> dict[str, Any]:
    """Verify ``code`` against ``secret``, tolerating one period of clock drift either way."""
    result: dict[str, Any] = {"ok": False, "valid": False, "error": None}
    cleaned_secret = (secret or "").strip().replace(" ", "")
    cleaned_code = (code or "").strip()

    if not cleaned_secret:
        result["error"] = "Enter a base32 secret."
        return result
    if len(cleaned_secret) > MAX_SECRET_LENGTH:
        result["error"] = f"Secret is longer than {MAX_SECRET_LENGTH} characters."
        return result
    if not cleaned_code:
        result["error"] = "Enter a code to verify."
        return result
    if len(cleaned_code) > MAX_CODE_LENGTH:
        result["error"] = f"Code is longer than {MAX_CODE_LENGTH} characters."
        return result

    try:
        totp = pyotp.TOTP(cleaned_secret, interval=TOTP_PERIOD_SECONDS)
        valid = totp.verify(cleaned_code, valid_window=1)
    except Exception:
        result["error"] = "Invalid base32 secret."
        return result

    result.update({"ok": True, "valid": bool(valid)})
    return result
