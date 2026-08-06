"""DNS propagation checker: the same query against several public resolvers."""

from __future__ import annotations

from typing import Any

import dns.exception
import dns.resolver

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain, record_to_row


PUBLIC_RESOLVERS: tuple[tuple[str, str], ...] = (
    ("Google", "8.8.8.8"),
    ("Cloudflare", "1.1.1.1"),
    ("Quad9", "9.9.9.9"),
)
SUPPORTED_RECORD_TYPES: tuple[str, ...] = ("A", "AAAA", "MX", "TXT", "NS", "CNAME")


def _resolver_for(nameserver: str, timeout: float = 3.0, lifetime: float = 5.0) -> dns.resolver.Resolver:
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [nameserver]
    resolver.timeout = timeout
    resolver.lifetime = lifetime
    return resolver


def _query_one(domain: str, record_type: str, nameserver: str) -> dict[str, Any]:
    try:
        answers = _resolver_for(nameserver).resolve(domain, record_type)
    except dns.resolver.NXDOMAIN:
        return {"ok": False, "status": "NXDOMAIN", "records": [], "values": [], "error": "Domain does not exist."}
    except dns.resolver.NoAnswer:
        return {"ok": False, "status": "No Answer", "records": [], "values": [], "error": "No matching records were found."}
    except dns.exception.Timeout:
        return {"ok": False, "status": "Timeout", "records": [], "values": [], "error": "Query timed out."}
    except dns.resolver.NoNameservers:
        return {"ok": False, "status": "Nameserver Error", "records": [], "values": [], "error": "Resolver could not answer this query."}
    except dns.exception.DNSException as exc:
        return {"ok": False, "status": "DNS Error", "records": [], "values": [], "error": str(exc)}

    records = [record_to_row(record, record_type) for record in answers]
    values = sorted(str(record.get("value", "")) for record in records)
    return {"ok": True, "status": "Answered", "records": records, "values": values, "error": None}


def _empty_result(domain: str, record_type: str) -> dict[str, Any]:
    return {"ok": False, "domain": domain, "record_type": record_type, "resolvers": [], "consistent": None, "error": None}


def check_propagation(domain: str, record_type: str) -> dict[str, Any]:
    """Query the same DNS record across several public resolvers and compare answers."""
    normalized = normalize_domain(domain)
    requested_type = (record_type or "").upper().strip()
    result = _empty_result(normalized, requested_type)

    if not normalized:
        result["error"] = "Enter a domain name."
        return result
    if len(normalized) > MAX_DOMAIN_LENGTH:
        result["error"] = f"Domain is longer than {MAX_DOMAIN_LENGTH} characters."
        return result
    if requested_type not in SUPPORTED_RECORD_TYPES:
        result["error"] = f"Unsupported record type. Choose one of: {', '.join(SUPPORTED_RECORD_TYPES)}."
        return result

    resolver_results = []
    for name, ip in PUBLIC_RESOLVERS:
        outcome = _query_one(normalized, requested_type, ip)
        outcome["resolver_name"] = name
        outcome["resolver_ip"] = ip
        resolver_results.append(outcome)

    answered_value_sets = {tuple(r["values"]) for r in resolver_results if r["ok"]}
    consistent = len(answered_value_sets) <= 1 if answered_value_sets else None

    result.update({"ok": True, "resolvers": resolver_results, "consistent": consistent})
    return result
