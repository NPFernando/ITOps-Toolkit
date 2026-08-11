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

# Recognized OpenSSH key-type tokens -- used to detect (and strip) a leading
# hostname column in a known_hosts-style line, which load_ssh_public_key
# does not accept directly (it expects "type base64 [comment]", not
# "host type base64 [comment]").
_KEY_TYPE_PREFIXES = ("ssh-", "ecdsa-sha2-", "sk-ssh-", "sk-ecdsa-sha2-")


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
    if len(tokens) >= 2 and not tokens[0].startswith(_KEY_TYPE_PREFIXES):
        # known_hosts-style line: "host[,host2] type base64 [comment]" --
        # drop the leading host column.
        tokens = tokens[1:]
    if len(tokens) < 2:
        result["error"] = "Could not parse a key -- expected 'type base64-blob [comment]'."
        return result

    key_type, key_blob = tokens[0], tokens[1]
    comment = " ".join(tokens[2:]) if len(tokens) > 2 else None

    try:
        load_ssh_public_key(f"{key_type} {key_blob}".encode())
    except (ValueError, UnsupportedAlgorithm) as exc:
        result["error"] = f"Could not parse SSH public key: {exc}"
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
