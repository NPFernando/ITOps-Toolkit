"""Domain registration (WHOIS/RDAP) lookup helpers."""

from __future__ import annotations

from typing import Any

import requests

from utils.dns_tools import normalize_domain

MAX_DOMAIN_LENGTH = 253
RDAP_URL = "https://rdap.org/domain/{domain}"
RDAP_TIMEOUT = 8
_HEADERS = {"User-Agent": "ITOpsToolkit/1.0 public-safe-checker", "Accept": "application/rdap+json"}

_EVENT_LABELS = {
    "registration": "Registered",
    "expiration": "Expires",
    "last changed": "Last updated",
    "last update of RDAP database": "RDAP database updated",
}


def _empty_result(domain: str) -> dict[str, Any]:
    return {
        "ok": False,
        "domain": domain,
        "query_name": normalize_domain(domain),
        "registrar": None,
        "status": [],
        "nameservers": [],
        "events": [],
        "error": None,
    }


def lookup_whois(domain: str) -> dict[str, Any]:
    """Look up domain registration details via RDAP (a structured, standardized WHOIS successor)."""
    result = _empty_result(domain)
    normalized = result["query_name"]

    if not normalized:
        result["error"] = "Enter a domain name."
        return result
    if len(normalized) > MAX_DOMAIN_LENGTH:
        result["error"] = f"Domain is longer than {MAX_DOMAIN_LENGTH} characters."
        return result
    if "." not in normalized:
        result["error"] = "Enter a valid domain name (e.g. example.com)."
        return result

    try:
        response = requests.get(RDAP_URL.format(domain=normalized), headers=_HEADERS, timeout=RDAP_TIMEOUT)
    except requests.RequestException as exc:
        result["error"] = f"WHOIS/RDAP lookup failed: {exc}"
        return result

    if response.status_code == 404:
        result["error"] = "No registration record found for that domain."
        return result
    if not response.ok:
        result["error"] = f"WHOIS/RDAP lookup failed with status {response.status_code}."
        return result

    try:
        data = response.json()
    except ValueError:
        result["error"] = "RDAP server returned an unexpected response."
        return result

    registrar = None
    for entity in data.get("entities", []):
        if "registrar" in entity.get("roles", []):
            registrar = _vcard_fn(entity.get("vcardArray"))
            break

    events = []
    for event in data.get("events", []):
        action = event.get("eventAction", "")
        events.append(
            {
                "label": _EVENT_LABELS.get(action, action.title() or "Event"),
                "date": event.get("eventDate", ""),
            }
        )

    nameservers = [ns.get("ldhName", "") for ns in data.get("nameservers", []) if ns.get("ldhName")]

    result.update(
        {
            "ok": True,
            "registrar": registrar,
            "status": data.get("status", []),
            "nameservers": sorted(nameservers),
            "events": events,
        }
    )
    return result


def _vcard_fn(vcard_array: Any) -> str | None:
    """Extract the 'fn' (formatted name) field from an RDAP vCard array, if present."""
    if not isinstance(vcard_array, list) or len(vcard_array) < 2:
        return None
    for field in vcard_array[1]:
        if isinstance(field, list) and len(field) >= 4 and field[0] == "fn":
            return field[3] or None
    return None
