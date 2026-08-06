"""Build SPF, DMARC, and DKIM TXT record strings from simple inputs.

The reverse of the existing SPF/DMARC checks (utils.dns_tools) and DKIM
selector lookup (utils.dkim_tools) -- those read a record that already
exists; this builds the record string to publish.
"""

from __future__ import annotations

from typing import Any


SPF_ALL_MECHANISMS: dict[str, str] = {
    "-all": "Fail -- reject mail from senders not listed (recommended once SPF is fully configured).",
    "~all": "SoftFail -- mark unlisted senders as suspicious but don't hard-reject (safer while rolling out SPF).",
    "?all": "Neutral -- no explicit policy for unlisted senders.",
    "+all": "Pass -- allow mail from any sender (not recommended; defeats the purpose of SPF).",
}
MAX_SPF_LOOKUPS = 10  # RFC 7208 hard limit on include/a/mx/ptr/exists/redirect mechanisms

DMARC_POLICIES: tuple[str, ...] = ("none", "quarantine", "reject")
DMARC_ALIGNMENT_MODES: tuple[str, ...] = ("relaxed", "strict")


def build_spf_record(includes: list[str], ip4: list[str], ip6: list[str], all_mechanism: str = "-all") -> dict[str, Any]:
    """Build an SPF TXT record from allowed senders."""
    if all_mechanism not in SPF_ALL_MECHANISMS:
        return {"ok": False, "record": "", "warnings": [], "error": f"Unknown 'all' mechanism. Choose one of: {', '.join(SPF_ALL_MECHANISMS)}."}

    parts = ["v=spf1"]
    for addr in ip4:
        parts.append(f"ip4:{addr}")
    for addr in ip6:
        parts.append(f"ip6:{addr}")
    for domain in includes:
        parts.append(f"include:{domain}")
    parts.append(all_mechanism)

    record = " ".join(parts)
    warnings = []
    lookup_count = len(includes)
    if lookup_count > MAX_SPF_LOOKUPS:
        warnings.append(f"{lookup_count} include mechanisms exceed the {MAX_SPF_LOOKUPS}-lookup SPF limit (RFC 7208) -- this record will fail validation on most receivers.")
    if len(record) > 255:
        warnings.append(f"Record is {len(record)} characters; a single SPF TXT string longer than 255 characters must be split into multiple quoted strings.")
    if not includes and not ip4 and not ip6:
        warnings.append("No senders (include/ip4/ip6) were added -- this record authorizes nothing.")

    return {"ok": True, "record": record, "warnings": warnings, "error": None}


def build_dmarc_record(
    policy: str,
    rua: list[str],
    ruf: list[str] | None = None,
    subdomain_policy: str | None = None,
    pct: int = 100,
    adkim: str = "relaxed",
    aspf: str = "relaxed",
) -> dict[str, Any]:
    """Build a DMARC TXT record (published at _dmarc.<domain>)."""
    ruf = ruf or []
    if policy not in DMARC_POLICIES:
        return {"ok": False, "record": "", "warnings": [], "error": f"Unknown policy. Choose one of: {', '.join(DMARC_POLICIES)}."}
    if subdomain_policy is not None and subdomain_policy not in DMARC_POLICIES:
        return {"ok": False, "record": "", "warnings": [], "error": f"Unknown subdomain policy. Choose one of: {', '.join(DMARC_POLICIES)}."}
    if adkim not in DMARC_ALIGNMENT_MODES or aspf not in DMARC_ALIGNMENT_MODES:
        return {"ok": False, "record": "", "warnings": [], "error": f"Alignment modes must be one of: {', '.join(DMARC_ALIGNMENT_MODES)}."}
    if not 0 <= pct <= 100:
        return {"ok": False, "record": "", "warnings": [], "error": "pct must be between 0 and 100."}

    parts = ["v=DMARC1", f"p={policy}"]
    if subdomain_policy:
        parts.append(f"sp={subdomain_policy}")
    if rua:
        parts.append("rua=" + ",".join(f"mailto:{addr}" for addr in rua))
    if ruf:
        parts.append("ruf=" + ",".join(f"mailto:{addr}" for addr in ruf))
    if pct != 100:
        parts.append(f"pct={pct}")
    if adkim != "relaxed":
        parts.append(f"adkim={adkim[0]}")
    if aspf != "relaxed":
        parts.append(f"aspf={aspf[0]}")

    record = "; ".join(parts)
    warnings = []
    if not rua:
        warnings.append("No rua (aggregate report) address set -- you won't receive DMARC reports to monitor this policy.")
    if policy == "reject" and pct == 100:
        warnings.append("p=reject at pct=100 immediately rejects all failing mail -- confirm SPF/DKIM are fully validated first, or start with p=none/quarantine.")

    return {"ok": True, "record": record, "warnings": warnings, "error": None}


def build_dkim_record(selector: str, domain: str, public_key: str, key_type: str = "rsa") -> dict[str, Any]:
    """Format an existing DKIM public key into a publishable TXT record and record name.

    This does not generate a key pair -- paste an existing public key (e.g. from
    `openssl rsa -pubout` with headers/newlines stripped) to get the correctly
    formatted TXT record and its DNS name.
    """
    selector = (selector or "").strip()
    domain = (domain or "").strip()
    key = "".join((public_key or "").split())  # strip all whitespace/newlines from a pasted PEM body

    if not selector:
        return {"ok": False, "record": "", "query_name": "", "warnings": [], "error": "Enter a DKIM selector."}
    if not domain:
        return {"ok": False, "record": "", "query_name": "", "warnings": [], "error": "Enter a domain."}
    if not key:
        return {"ok": False, "record": "", "query_name": "", "warnings": [], "error": "Paste a public key (base64, PEM headers/newlines are stripped automatically)."}

    record = f"v=DKIM1; k={key_type}; p={key}"
    query_name = f"{selector}._domainkey.{domain}"

    warnings = []
    if len(record) > 255:
        warnings.append(f"Record is {len(record)} characters; DNS providers typically split long TXT values into multiple quoted 255-character strings automatically.")

    return {"ok": True, "record": record, "query_name": query_name, "warnings": warnings, "error": None}
