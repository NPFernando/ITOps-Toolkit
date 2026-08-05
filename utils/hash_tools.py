"""Hash and HMAC generation helpers."""

from __future__ import annotations

import hashlib
import hmac as hmac_module
from typing import Any

MAX_INPUT_LENGTH = 200_000

HASH_ALGORITHMS = ("md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256", "sha3_512")
HMAC_ALGORITHMS = ("md5", "sha1", "sha256", "sha384", "sha512")


def generate_hashes(text: str) -> dict[str, Any]:
    """Hash ``text`` with every algorithm in HASH_ALGORITHMS."""
    result: dict[str, Any] = {"ok": False, "digests": {}, "error": None}
    if text is None:
        text = ""
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    data = text.encode("utf-8")
    digests: dict[str, str] = {}
    for algo in HASH_ALGORITHMS:
        digests[algo] = hashlib.new(algo, data).hexdigest()
    result.update({"ok": True, "digests": digests})
    return result


def generate_hmac(text: str, secret: str, algorithm: str) -> dict[str, Any]:
    """Compute an HMAC of ``text`` keyed by ``secret`` using ``algorithm``."""
    result: dict[str, Any] = {"ok": False, "digest": None, "error": None}
    if algorithm not in HMAC_ALGORITHMS:
        result["error"] = f"Unsupported algorithm: {algorithm}."
        return result
    if not secret:
        result["error"] = "Enter a secret key."
        return result
    if text is None:
        text = ""
    if len(text) > MAX_INPUT_LENGTH or len(secret) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    digest = hmac_module.new(secret.encode("utf-8"), text.encode("utf-8"), algorithm).hexdigest()
    result.update({"ok": True, "digest": digest})
    return result
