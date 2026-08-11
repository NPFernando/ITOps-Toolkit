"""Encode/decode a non-negative integer to/from Base62 (0-9, A-Z, a-z).

Distinct from Integer Base Converter (bases 2-16, positional numeral
systems only) and Base58/Base32/Base64 (different alphabets and, for
Base58, different leading-zero handling). Base62 uses only alphanumerics
with no special characters, commonly used for URL-safe short IDs.
"""

from __future__ import annotations

from typing import Any

_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_INDEX = {char: i for i, char in enumerate(_ALPHABET)}
MAX_DIGITS = 50


def encode_base62(value: str) -> dict[str, Any]:
    """Encode a non-negative base-10 integer string as Base62."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    text = (value or "").strip()
    if not text:
        result["error"] = "Enter a non-negative integer."
        return result
    if not text.isdigit():
        result["error"] = "Enter a non-negative integer (digits only)."
        return result
    if len(text) > MAX_DIGITS:
        result["error"] = f"Number is longer than {MAX_DIGITS} digits."
        return result

    n = int(text)
    if n == 0:
        result.update({"ok": True, "output": _ALPHABET[0]})
        return result

    digits = []
    while n > 0:
        n, remainder = divmod(n, 62)
        digits.append(_ALPHABET[remainder])
    result.update({"ok": True, "output": "".join(reversed(digits))})
    return result


def decode_base62(encoded: str) -> dict[str, Any]:
    """Decode a Base62 string back into a base-10 integer string."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (encoded or "").strip()
    if not value:
        result["error"] = "Enter a Base62 string to decode."
        return result

    invalid_chars = sorted({char for char in value if char not in _INDEX})
    if invalid_chars:
        result["error"] = f"Not valid Base62 -- contains: {', '.join(invalid_chars)}."
        return result

    n = 0
    for char in value:
        n = n * 62 + _INDEX[char]
    result.update({"ok": True, "output": str(n)})
    return result
