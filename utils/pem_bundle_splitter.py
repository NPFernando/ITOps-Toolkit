"""Split a multi-certificate PEM bundle into individual certificates.

Complements SSL Certificate Checker -- a common troubleshooting need when a
server's chain file has certs in the wrong order or an unexpected extra/
missing intermediate, which is hard to eyeball from one long PEM blob.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cryptography import x509

MAX_INPUT_LENGTH = 50_000


def split_pem_bundle(pem_text: str) -> dict[str, Any]:
    """Parse a PEM bundle and return each certificate's subject, issuer, and expiry."""
    result: dict[str, Any] = {"ok": False, "error": None, "certificates": []}

    value = (pem_text or "").strip()
    if not value:
        result["error"] = "Paste a PEM certificate bundle."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        certs = x509.load_pem_x509_certificates(value.encode())
    except ValueError as exc:
        result["error"] = f"Could not parse certificate bundle: {exc}"
        return result

    if not certs:
        result["error"] = "No certificates found in the pasted bundle."
        return result

    now = datetime.now(UTC)
    certificates = []
    for index, cert in enumerate(certs, start=1):
        not_valid_before = cert.not_valid_before_utc
        not_valid_after = cert.not_valid_after_utc
        certificates.append(
            {
                "index": index,
                "subject": cert.subject.rfc4514_string(),
                "issuer": cert.issuer.rfc4514_string(),
                "not_valid_before": not_valid_before.isoformat(),
                "not_valid_after": not_valid_after.isoformat(),
                "is_expired": not_valid_after < now,
                "is_not_yet_valid": not_valid_before > now,
            }
        )

    result.update({"ok": True, "certificates": certificates})
    return result
