"""File hash / integrity comparison -- verify a download wasn't corrupted or tampered with."""

from __future__ import annotations

import hashlib
from typing import Any

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB, generous for installers/patches without risking memory pressure
HASH_ALGORITHMS: tuple[str, ...] = ("md5", "sha1", "sha256", "sha512")


def hash_bytes(data: bytes) -> dict[str, Any]:
    """Hash ``data`` with every algorithm in HASH_ALGORITHMS."""
    result: dict[str, Any] = {"ok": False, "digests": {}, "size_bytes": len(data), "error": None}
    if len(data) > MAX_FILE_SIZE_BYTES:
        result["error"] = f"File is larger than {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        return result

    result.update({"ok": True, "digests": {algo: hashlib.new(algo, data).hexdigest() for algo in HASH_ALGORITHMS}})
    return result


def find_matching_algorithm(digests: dict[str, str], expected: str) -> str | None:
    """Return the algorithm name whose digest matches ``expected`` (case-insensitive), or None."""
    needle = (expected or "").strip().lower()
    if not needle:
        return None
    for algo, digest in digests.items():
        if digest.lower() == needle:
            return algo
    return None
