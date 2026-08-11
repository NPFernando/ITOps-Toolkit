"""Compute MD5 and SHA256 fingerprints for an SSH public key, matching ssh-keygen -lf's output.

Complements RSA/SSH Key Pair Generator -- useful for verifying a key you
already have against a fingerprint shown elsewhere (e.g. a GitHub deploy
key or a server's host key).
"""

from __future__ import annotations

import base64
import binascii
import hashlib
from typing import Any

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.serialization import load_ssh_public_key

MAX_INPUT_LENGTH = 4_000

# A plain public key line is "type base64 [comment]" (offset 0). A
# known_hosts line prepends one hostname column, "host type base64
# [comment]" (offset 1). A known_hosts line with a @cert-authority/@revoked
# marker prepends two, "@marker host type base64 [comment]" (offset 2).
# Rather than guessing which format was pasted from a fixed set of
# recognized key-type prefixes (which breaks on a hostname that happens to
# start with "ssh-", or a marker line, or any future key type), try each
# offset and use the first one load_ssh_public_key actually accepts.
_MAX_LEADING_COLUMNS = 2


def compute_fingerprint(key_text: str) -> dict[str, Any]:
    """Parse an SSH public key (plain or known_hosts-style line) and compute its fingerprints."""
    result: dict[str, Any] = {"ok": False, "error": None, "key_type": None, "md5_fingerprint": None, "sha256_fingerprint": None, "comment": None}

    value = (key_text or "").strip()
    if not value:
        result["error"] = "Paste a public SSH key."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    tokens = value.split()

    key_type: str | None = None
    key_blob: str | None = None
    comment: str | None = None
    last_error: Exception | None = None
    for offset in range(min(_MAX_LEADING_COLUMNS, max(len(tokens) - 2, 0)) + 1):
        candidate = tokens[offset:]
        if len(candidate) < 2:
            continue
        try:
            load_ssh_public_key(f"{candidate[0]} {candidate[1]}".encode())
        except (ValueError, UnsupportedAlgorithm) as exc:
            last_error = exc
            continue
        key_type, key_blob = candidate[0], candidate[1]
        comment = " ".join(candidate[2:]) if len(candidate) > 2 else None
        break

    if key_type is None or key_blob is None:
        result["error"] = f"Could not parse SSH public key: {last_error}" if last_error else "Could not parse a key -- expected 'type base64-blob [comment]'."
        return result

    try:
        raw = base64.b64decode(key_blob, validate=True)
    except binascii.Error as exc:
        result["error"] = f"Could not decode key data: {exc}"
        return result

    md5_hex = hashlib.md5(raw).hexdigest()
    md5_fingerprint = ":".join(md5_hex[i : i + 2] for i in range(0, len(md5_hex), 2))
    sha256_fingerprint = "SHA256:" + base64.b64encode(hashlib.sha256(raw).digest()).decode().rstrip("=")

    result.update(
        {
            "ok": True,
            "key_type": key_type,
            "md5_fingerprint": md5_fingerprint,
            "sha256_fingerprint": sha256_fingerprint,
            "comment": comment,
        }
    )
    return result
