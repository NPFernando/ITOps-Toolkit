"""Convert an RSA public key between JWK (JSON Web Key) and PEM format.

Useful when working with a JWKS endpoint (e.g. an OIDC provider's
/.well-known/jwks.json) and needing a PEM key for a tool that doesn't
speak JWK directly. Distinct from every other JWT tool in this app, which
work with tokens, not the keys used to verify them. RSA only -- EC/OKP
JWKs are a different coordinate system and deliberately out of scope.
"""

from __future__ import annotations

import base64
import binascii
import json
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

MAX_INPUT_LENGTH = 20_000


def _b64url_uint(n: int) -> str:
    length = max((n.bit_length() + 7) // 8, 1)
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()


def _decode_b64url_uint(value: str) -> int:
    padding = "=" * (-len(value) % 4)
    return int.from_bytes(base64.urlsafe_b64decode(value + padding), "big")


def jwk_to_pem(jwk_text: str) -> dict[str, Any]:
    """Convert an RSA public JWK (JSON) into a PEM public key."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (jwk_text or "").strip()
    if not value:
        result["error"] = "Paste a JWK."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        jwk = json.loads(value)
    except json.JSONDecodeError as exc:
        result["error"] = f"Invalid JSON: {exc}"
        return result

    if not isinstance(jwk, dict):
        result["error"] = "JWK must be a JSON object."
        return result
    if jwk.get("kty") != "RSA":
        result["error"] = f"Only kty=\"RSA\" is supported, got {jwk.get('kty')!r}."
        return result
    if "n" not in jwk or "e" not in jwk:
        result["error"] = "JWK is missing required RSA fields 'n' and/or 'e'."
        return result

    try:
        n, e = _decode_b64url_uint(jwk["n"]), _decode_b64url_uint(jwk["e"])
    except (binascii.Error, ValueError, TypeError) as exc:
        result["error"] = f"Could not decode 'n'/'e' as base64url integers: {exc}"
        return result

    public_key = rsa.RSAPublicNumbers(e, n).public_key()
    pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    result.update({"ok": True, "output": pem.decode()})
    return result


def pem_to_jwk(pem_text: str, key_id: str = "") -> dict[str, Any]:
    """Convert a PEM RSA public key into a JWK (JSON)."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (pem_text or "").strip()
    if not value:
        result["error"] = "Paste a PEM public key."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        public_key = serialization.load_pem_public_key(value.encode())
    except ValueError as exc:
        result["error"] = f"Could not parse PEM public key: {exc}"
        return result

    if not isinstance(public_key, RSAPublicKey):
        result["error"] = "Only RSA public keys are supported."
        return result

    numbers = public_key.public_numbers()
    jwk = {"kty": "RSA", "n": _b64url_uint(numbers.n), "e": _b64url_uint(numbers.e), "use": "sig"}
    if key_id.strip():
        jwk["kid"] = key_id.strip()

    result.update({"ok": True, "output": json.dumps(jwk, indent=2)})
    return result
