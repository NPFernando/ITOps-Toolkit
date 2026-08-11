"""Build a DNS CAA (Certification Authority Authorization) record.

The reverse relationship of Email Record Builder (SPF/DMARC/DKIM) --
CAA is a different DNS record type entirely (RFC 8659), restricting which
CAs may issue certificates for a domain. Not covered by any existing tool.
"""

from __future__ import annotations

from typing import Any

TAGS: tuple[str, ...] = ("issue", "issuewild", "iodef")


def build_caa_record(tag: str, value: str, critical: bool = False) -> dict[str, Any]:
    """Build a CAA record's flag/tag/value in both zone-file and generic-record forms."""
    result: dict[str, Any] = {"ok": False, "error": None, "record": None, "zone_line": None}

    if tag not in TAGS:
        result["error"] = f"Unknown tag. Choose one of: {', '.join(TAGS)}."
        return result

    value = (value or "").strip()
    if not value:
        if tag == "issue" or tag == "issuewild":
            result["error"] = f"Enter a CA domain (e.g. letsencrypt.org), or ';' to issue no certificates for {tag}."
        else:
            result["error"] = "Enter a contact URI (e.g. mailto:security@example.com)."
        return result

    flag = 128 if critical else 0
    record = f'{flag} {tag} "{value}"'
    result.update({"ok": True, "record": record, "zone_line": f"@ CAA {record}"})
    return result
