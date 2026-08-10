"""Base32 (RFC 4648) encode/decode -- the encoding TOTP secrets use."""

from __future__ import annotations

import base64
import binascii
import re
from typing import Any

MAX_INPUT_LENGTH = 20_000


def encode_base32_text(value: str) -> str:
    return base64.b32encode((value or "").encode("utf-8")).decode("ascii")


def decode_base32_text(value: str) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": False, "error": None, "result": None}
    if len(value or "") > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    # Strips all whitespace, not just the ends -- matches decode_base64_text's
    # handling of wrapped/multi-line input copy-pasted from a text file.
    cleaned = re.sub(r"\s+", "", value or "").upper()
    if not cleaned:
        result["error"] = "Enter Base32 text to decode."
        return result

    try:
        decoded = base64.b32decode(cleaned.encode("ascii"), casefold=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        result["error"] = f"Invalid Base32 input: {exc}"
        return result

    result.update({"ok": True, "result": decoded.decode("utf-8", errors="replace")})
    return result
