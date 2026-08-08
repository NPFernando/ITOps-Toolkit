"""Decode ULIDs and UUIDs -- extract embedded creation timestamps where present.

ULID (https://github.com/ulid/spec): a 128-bit identifier -- 48-bit
millisecond timestamp + 80 bits of randomness -- encoded as 26 characters of
Crockford's Base32. Decoded directly against the spec (no new dependency),
the inverse of utils/id_generator.py's generation logic.

UUID v1 embeds a 60-bit timestamp (100-nanosecond intervals since the
Gregorian reform epoch, 1582-10-15) across its time_low/time_mid/
time_hi_and_version fields -- stdlib's uuid.UUID.time already computes this
per RFC 4122, so only the epoch-offset conversion to Unix time is needed
here. UUID v7 (RFC 9562) embeds a 48-bit Unix millisecond timestamp as its
top 48 bits; Python 3.12 (pinned in this repo) has no stdlib uuid7() to lean
on, so it's extracted manually via a bit shift.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

MAX_INPUT_LENGTH = 64  # comfortably above a 36-char UUID or 26-char ULID

_CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_CROCKFORD_INDEX = {char: index for index, char in enumerate(_CROCKFORD_ALPHABET)}
# Per the Crockford Base32 spec, decoders should accept these common
# misreadings/typos as their canonical equivalents.
_CROCKFORD_ALIASES = {"I": "1", "L": "1", "O": "0"}
_ULID_MAX_TIMESTAMP_MS = (1 << 48) - 1

# 100ns intervals between the Gregorian reform epoch (1582-10-15, what UUID
# v1 timestamps count from) and the Unix epoch (1970-01-01).
_UUID_V1_EPOCH_OFFSET_100NS = 0x01B21DD213814000


def decode_ulid(value: str) -> dict[str, Any]:
    """Decode a ULID into its embedded timestamp and randomness."""
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "timestamp_ms": None,
        "datetime_utc": None,
        "randomness_hex": None,
    }
    cleaned = (value or "").strip().upper()
    if not cleaned:
        result["error"] = "Enter a ULID."
        return result
    if len(cleaned) != 26:
        result["error"] = f"A ULID is exactly 26 characters (got {len(cleaned)})."
        return result

    normalized = "".join(_CROCKFORD_ALIASES.get(char, char) for char in cleaned)
    invalid_chars = sorted({char for char in normalized if char not in _CROCKFORD_INDEX})
    if invalid_chars:
        result["error"] = f"Not valid Crockford Base32 -- unexpected character(s): {', '.join(invalid_chars)}."
        return result

    timestamp_part, randomness_part = normalized[:10], normalized[10:]
    timestamp_ms = 0
    for char in timestamp_part:
        timestamp_ms = timestamp_ms * 32 + _CROCKFORD_INDEX[char]
    if timestamp_ms > _ULID_MAX_TIMESTAMP_MS:
        result["error"] = "Timestamp portion exceeds the valid 48-bit range."
        return result

    randomness = 0
    for char in randomness_part:
        randomness = randomness * 32 + _CROCKFORD_INDEX[char]

    try:
        parsed_dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)
    except (OverflowError, OSError, ValueError):
        result["error"] = "Timestamp portion is out of range for a valid date."
        return result

    result.update(
        {
            "ok": True,
            "timestamp_ms": timestamp_ms,
            "datetime_utc": parsed_dt.isoformat(),
            "randomness_hex": format(randomness, "020x"),
        }
    )
    return result


def decode_uuid(value: str) -> dict[str, Any]:
    """Decode a UUID's version/variant, and its embedded timestamp for v1/v7."""
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "version": None,
        "variant": None,
        "timestamp_supported": False,
        "datetime_utc": None,
    }
    cleaned = (value or "").strip()
    if not cleaned:
        result["error"] = "Enter a UUID."
        return result

    try:
        parsed = uuid.UUID(cleaned)
    except ValueError:
        result["error"] = "Not a valid UUID."
        return result

    result["ok"] = True
    result["version"] = parsed.version
    result["variant"] = str(parsed.variant)

    if parsed.version == 1:
        unix_100ns = parsed.time - _UUID_V1_EPOCH_OFFSET_100NS
        try:
            dt = datetime.fromtimestamp(unix_100ns / 1e7, tz=UTC)
        except (OverflowError, OSError, ValueError):
            return result
        result["timestamp_supported"] = True
        result["datetime_utc"] = dt.isoformat()
    elif parsed.version == 7:
        unix_ms = parsed.int >> 80
        try:
            dt = datetime.fromtimestamp(unix_ms / 1000, tz=UTC)
        except (OverflowError, OSError, ValueError):
            return result
        result["timestamp_supported"] = True
        result["datetime_utc"] = dt.isoformat()

    return result
