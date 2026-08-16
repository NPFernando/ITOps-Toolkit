"""Decode a PEM-encoded Certificate Signing Request (CSR).

Complements SSL Certificate Checker (which inspects an issued cert, not the
request that preceded it) and RSA/SSH Key Pair Generator.
"""

from __future__ import annotations

from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, rsa

MAX_INPUT_LENGTH = 10_000


def _public_key_info(public_key: Any) -> tuple[str, int]:
    if isinstance(public_key, rsa.RSAPublicKey):
        return "RSA", public_key.key_size
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        return f"EC ({public_key.curve.name})", public_key.key_size
    return type(public_key).__name__, 0


def decode_csr(pem_text: str) -> dict[str, Any]:
    """Parse a PEM CSR and return its subject, SAN names, key info, and signature validity."""
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "subject": None,
        "san_names": [],
        "public_key_algorithm": None,
        "public_key_size": None,
        "signature_algorithm": None,
        "signature_valid": None,
    }

    value = (pem_text or "").strip()
    if not value:
        result["error"] = "Paste a PEM-encoded CSR."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        csr = x509.load_pem_x509_csr(value.encode())
    except ValueError as exc:
        result["error"] = f"Could not parse CSR: {exc}"
        return result

    san_names: list[str] = []
    try:
        san_extension = csr.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san_names = san_extension.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        pass

    algorithm, size = _public_key_info(csr.public_key())

    result.update(
        {
            "ok": True,
            "subject": csr.subject.rfc4514_string(),
            "san_names": san_names,
            "public_key_algorithm": algorithm,
            "public_key_size": size,
            "signature_algorithm": csr.signature_hash_algorithm.name if csr.signature_hash_algorithm else "unknown",
            "signature_valid": csr.is_signature_valid,
        }
    )
    return result
