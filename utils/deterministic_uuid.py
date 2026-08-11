"""Generate a namespace-based (v3/v5) UUID -- the same input always produces the same UUID.

Distinct from the existing ID Generator, which only generates random v1/v4/v7
UUIDs -- v3 (MD5) and v5 (SHA-1) are deterministic, useful for generating a
stable ID from an external identifier (e.g. a URL or DNS name) without a
database.
"""

from __future__ import annotations

import uuid
from typing import Any

MAX_INPUT_LENGTH = 500
VERSIONS: tuple[int, ...] = (3, 5)

NAMESPACES: dict[str, uuid.UUID] = {
    "DNS": uuid.NAMESPACE_DNS,
    "URL": uuid.NAMESPACE_URL,
    "OID": uuid.NAMESPACE_OID,
    "X.500": uuid.NAMESPACE_X500,
}


def generate_deterministic_uuid(namespace_name: str, name: str, version: int) -> dict[str, Any]:
    """Generate a v3 (MD5) or v5 (SHA-1) UUID from a namespace + name pair."""
    result: dict[str, Any] = {"ok": False, "error": None, "result": None}

    if namespace_name not in NAMESPACES:
        result["error"] = f"Unknown namespace: {namespace_name}."
        return result
    if version not in VERSIONS:
        result["error"] = f"Unsupported version: {version}. Use 3 or 5."
        return result

    name = (name or "").strip()
    if not name:
        result["error"] = "Enter a name to hash."
        return result
    if len(name) > MAX_INPUT_LENGTH:
        result["error"] = f"Name is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    namespace = NAMESPACES[namespace_name]
    generated = uuid.uuid3(namespace, name) if version == 3 else uuid.uuid5(namespace, name)

    result.update({"ok": True, "result": str(generated)})
    return result
