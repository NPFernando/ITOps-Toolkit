"""Base58 encode/decode (Bitcoin/IPFS alphabet).

Distinct from Base32/Base64 (fixed-width, positional encodings) and Integer
Base Converter (arbitrary numeric base 2-16 of a single integer) -- Base58
uses a specific 58-character alphabet that excludes visually ambiguous
characters (0, O, I, l) and needs explicit leading-zero-byte handling,
which a generic base converter doesn't do.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 100_000

_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_INDEX = {char: i for i, char in enumerate(_ALPHABET)}


def encode_base58(text: str) -> dict[str, Any]:
    """Encode UTF-8 text as a Base58 string."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    if not text:
        result["error"] = "Enter text to encode."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    data = text.encode("utf-8")
    n = int.from_bytes(data, "big")
    digits = ""
    while n > 0:
        n, remainder = divmod(n, 58)
        digits = _ALPHABET[remainder] + digits

    leading_zero_bytes = len(data) - len(data.lstrip(b"\x00"))
    result.update({"ok": True, "output": "1" * leading_zero_bytes + digits})
    return result


def decode_base58(encoded: str) -> dict[str, Any]:
    """Decode a Base58 string back into UTF-8 text."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (encoded or "").strip()
    if not value:
        result["error"] = "Enter a Base58 string to decode."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    invalid_chars = sorted({char for char in value if char not in _INDEX})
    if invalid_chars:
        result["error"] = f"Not valid Base58 -- contains: {', '.join(invalid_chars)}."
        return result

    n = 0
    for char in value:
        n = n * 58 + _INDEX[char]
    body = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""

    leading_ones = len(value) - len(value.lstrip("1"))
    data = b"\x00" * leading_ones + body

    try:
        result.update({"ok": True, "output": data.decode("utf-8")})
    except UnicodeDecodeError:
        result["error"] = "Decoded bytes are not valid UTF-8 text (this may be binary data)."
    return result
