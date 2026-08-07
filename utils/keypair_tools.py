"""Generate disposable RSA or Ed25519 key pairs for test/throwaway use.

Not for production key management -- this app has no way to protect a
private key once it's rendered to the browser. Intended for spinning up
a quick test credential during troubleshooting.
"""

from __future__ import annotations

import base64
import hashlib
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

KEY_TYPES: tuple[str, ...] = ("RSA", "Ed25519")
RSA_KEY_SIZES: tuple[int, ...] = (2048, 3072, 4096)


def _ssh_fingerprint(openssh_public_bytes: bytes) -> str:
    blob_b64 = openssh_public_bytes.decode().split()[1]
    digest = hashlib.sha256(base64.b64decode(blob_b64)).digest()
    return "SHA256:" + base64.b64encode(digest).decode().rstrip("=")


def generate_keypair(key_type: str, rsa_key_size: int = 2048) -> dict[str, Any]:
    """Generate a key pair and return its PEM private key, OpenSSH public key, and fingerprint."""
    result: dict[str, Any] = {"ok": False, "private_key_pem": "", "public_key_openssh": "", "fingerprint": "", "error": None}

    if key_type not in KEY_TYPES:
        result["error"] = f"Unknown key type. Choose one of: {', '.join(KEY_TYPES)}."
        return result

    if key_type == "RSA":
        if rsa_key_size not in RSA_KEY_SIZES:
            result["error"] = f"Unsupported RSA key size. Choose one of: {', '.join(str(s) for s in RSA_KEY_SIZES)}."
            return result
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=rsa_key_size)
    else:
        private_key = ed25519.Ed25519PrivateKey.generate()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_openssh = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )

    result.update(
        {
            "ok": True,
            "private_key_pem": private_pem.decode(),
            "public_key_openssh": public_openssh.decode(),
            "fingerprint": _ssh_fingerprint(public_openssh),
        }
    )
    return result
