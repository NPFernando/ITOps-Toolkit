"""Bulk UUID (v4) and ULID generation.

ULID (https://github.com/ulid/spec): a 128-bit identifier -- 48-bit
millisecond timestamp + 80 bits of randomness -- encoded as 26 characters
of Crockford's Base32, so IDs generated later sort lexicographically after
earlier ones. Implemented directly against the spec (stdlib `time` +
`secrets` only, no new dependency) since Python's stdlib has no ULID type.
"""

from __future__ import annotations

import secrets
import time
import uuid

MAX_COUNT = 500
_CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _encode_crockford(value: int, length: int) -> str:
    chars = []
    for _ in range(length):
        value, remainder = divmod(value, 32)
        chars.append(_CROCKFORD_ALPHABET[remainder])
    return "".join(reversed(chars))


def generate_ulid(timestamp_ms: int | None = None) -> str:
    """Generate one ULID. ``timestamp_ms`` is exposed for deterministic tests."""
    ms = timestamp_ms if timestamp_ms is not None else time.time_ns() // 1_000_000
    randomness = int.from_bytes(secrets.token_bytes(10), "big")
    return _encode_crockford(ms, 10) + _encode_crockford(randomness, 16)


def generate_uuids(count: int) -> dict[str, object]:
    """Generate ``count`` UUIDv4 strings."""
    if not 1 <= count <= MAX_COUNT:
        return {"ok": False, "ids": [], "error": f"Count must be between 1 and {MAX_COUNT}."}
    return {"ok": True, "ids": [str(uuid.uuid4()) for _ in range(count)], "error": None}


def generate_ulids(count: int) -> dict[str, object]:
    """Generate ``count`` ULIDs."""
    if not 1 <= count <= MAX_COUNT:
        return {"ok": False, "ids": [], "error": f"Count must be between 1 and {MAX_COUNT}."}
    return {"ok": True, "ids": [generate_ulid() for _ in range(count)], "error": None}
