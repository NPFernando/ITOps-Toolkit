"""Validate that a pasted PEM certificate bundle is a correctly ordered, cryptographically linked chain.

Complements PEM Bundle Splitter (splits a bundle, doesn't check ordering)
and SSL Certificate Checker (a single live cert, not a pasted chain). Checks
two things per adjacent pair: the subject/issuer names line up (leaf,
then its issuer, then that issuer's issuer, ...) AND the earlier cert's
signature actually verifies against the later cert's public key -- name
matching alone can't catch a chain where the names look right but the
wrong key signed it.
"""

from __future__ import annotations

from typing import Any

from cryptography import x509
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa

MAX_INPUT_LENGTH = 100_000


def _verify_signed_by(cert: x509.Certificate, issuer_public_key: Any) -> bool | None:
    """Return True/False if verifiable, or None if this key type isn't supported here."""
    try:
        if isinstance(issuer_public_key, rsa.RSAPublicKey):
            issuer_public_key.verify(cert.signature, cert.tbs_certificate_bytes, padding.PKCS1v15(), cert.signature_hash_algorithm)
        elif isinstance(issuer_public_key, ec.EllipticCurvePublicKey):
            issuer_public_key.verify(cert.signature, cert.tbs_certificate_bytes, ec.ECDSA(cert.signature_hash_algorithm))
        elif isinstance(issuer_public_key, ed25519.Ed25519PublicKey):
            issuer_public_key.verify(cert.signature, cert.tbs_certificate_bytes)
        else:
            return None
        return True
    except (InvalidSignature, UnsupportedAlgorithm):
        return False


def validate_chain_order(pem_text: str) -> dict[str, Any]:
    """Check that a PEM bundle's certificates form a correctly ordered, signed chain."""
    result: dict[str, Any] = {"ok": False, "error": None, "certificates": None, "links": None, "chain_valid": None}

    value = (pem_text or "").strip()
    if not value:
        result["error"] = "Paste a PEM certificate chain."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        certs = x509.load_pem_x509_certificates(value.encode())
    except ValueError as exc:
        result["error"] = f"Could not parse certificate bundle: {exc}"
        return result

    if len(certs) < 2:
        result["error"] = "Paste at least two certificates (a chain needs a leaf and at least one issuer)."
        return result

    certificates = [{"index": i, "subject": cert.subject.rfc4514_string(), "issuer": cert.issuer.rfc4514_string()} for i, cert in enumerate(certs, start=1)]

    links = []
    chain_valid = True
    for i in range(len(certs) - 1):
        current, next_cert = certs[i], certs[i + 1]
        names_match = current.issuer == next_cert.subject
        signature_ok = _verify_signed_by(current, next_cert.public_key())

        if not names_match:
            note = f"Certificate {i + 1}'s issuer does not match certificate {i + 2}'s subject."
        elif signature_ok is False:
            note = f"Certificate {i + 1}'s signature does NOT verify against certificate {i + 2}'s public key."
        elif signature_ok is None:
            note = "Signature check skipped (unsupported key type for verification here); names match."
        else:
            note = "OK"

        if not names_match or signature_ok is False:
            chain_valid = False

        links.append({"from_index": i + 1, "to_index": i + 2, "names_match": names_match, "signature_verified": signature_ok, "note": note})

    result.update({"ok": True, "certificates": certificates, "links": links, "chain_valid": chain_valid})
    return result
