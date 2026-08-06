"""DKIM selector lookup, complementing the existing SPF/DMARC DNS checks."""

from __future__ import annotations

from typing import Any

import dns.exception
import dns.resolver

from utils.dns_tools import MAX_DOMAIN_LENGTH, get_resolver, normalize_domain, txt_to_string


MAX_SELECTOR_LENGTH = 63  # DNS label length limit


def _normalize_selector(selector: str) -> str:
    return (selector or "").strip().strip(".")


def _parse_dkim_record(value: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in value.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        key, _, val = part.partition("=")
        fields[key.strip().lower()] = val.strip()
    return fields


def _empty_result(domain: str, selector: str) -> dict[str, Any]:
    return {
        "ok": False,
        "domain": domain,
        "selector": selector,
        "query_name": None,
        "raw_value": None,
        "fields": {},
        "status": "Unknown",
        "error": None,
    }


def lookup_dkim(domain: str, selector: str) -> dict[str, Any]:
    """Look up a DKIM TXT record at <selector>._domainkey.<domain>."""
    normalized_domain = normalize_domain(domain)
    normalized_selector = _normalize_selector(selector)
    result = _empty_result(normalized_domain, normalized_selector)

    if not normalized_domain:
        result["error"] = "Enter a domain name."
        return result
    if len(normalized_domain) > MAX_DOMAIN_LENGTH:
        result["error"] = f"Domain is longer than {MAX_DOMAIN_LENGTH} characters."
        return result
    if not normalized_selector:
        result["error"] = "Enter a DKIM selector (e.g. \"google\", \"selector1\", \"s1\")."
        return result
    if len(normalized_selector) > MAX_SELECTOR_LENGTH:
        result["error"] = f"Selector is longer than {MAX_SELECTOR_LENGTH} characters."
        return result

    query_name = f"{normalized_selector}._domainkey.{normalized_domain}"
    result["query_name"] = query_name

    try:
        answers = get_resolver().resolve(query_name, "TXT")
    except dns.resolver.NXDOMAIN:
        result["status"] = "NXDOMAIN"
        result["error"] = f"No DKIM record found for selector \"{normalized_selector}\" on this domain."
        return result
    except dns.resolver.NoAnswer:
        result["status"] = "No Answer"
        result["error"] = f"No TXT record found at {query_name}."
        return result
    except dns.exception.Timeout:
        result["status"] = "Timeout"
        result["error"] = "DNS lookup timed out."
        return result
    except dns.resolver.NoNameservers:
        result["status"] = "Nameserver Error"
        result["error"] = "Nameservers could not answer this query."
        return result
    except dns.exception.DNSException as exc:
        result["status"] = "DNS Error"
        result["error"] = str(exc)
        return result

    values = [txt_to_string(record) for record in answers]
    dkim_values = [v for v in values if "v=dkim1" in v.lower() or "p=" in v.lower()]
    raw_value = dkim_values[0] if dkim_values else (values[0] if values else "")

    if not raw_value:
        result["status"] = "No Answer"
        result["error"] = f"No DKIM record found for selector \"{normalized_selector}\" on this domain."
        return result

    fields = _parse_dkim_record(raw_value)

    result.update(
        {
            "ok": True,
            "raw_value": raw_value,
            "fields": fields,
            "status": "Healthy" if fields.get("p") else "Warning",
        }
    )
    if not fields.get("p"):
        result["error"] = "Record found, but no public key (p=) is present -- this selector may be revoked."
    return result
