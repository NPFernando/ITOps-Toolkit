"""DNS lookup helpers with Streamlit-safe error envelopes."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import dns.exception
import dns.resolver


MAX_DOMAIN_LENGTH = 253


def normalize_domain(domain: str) -> str:
    """Normalize user-entered domain text without performing DNS work."""
    value = (domain or "").strip().lower()
    if "://" in value:
        value = urlparse(value).netloc
    value = value.split("/")[0].split("?")[0].strip().rstrip(".")
    if "@" in value:
        value = value.rsplit("@", 1)[-1]
    if ":" in value and not value.startswith("["):
        value = value.split(":", 1)[0]
    try:
        value = value.encode("idna").decode("ascii")
    except UnicodeError:
        return value
    return value


def _base_result(domain: str, record_type: str, query_name: str | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "domain": domain,
        "query_name": query_name or domain,
        "record_type": record_type,
        "records": [],
        "raw_values": [],
        "status": "Unknown",
        "error": None,
    }


def _get_resolver(timeout: float = 3.0, lifetime: float = 5.0) -> dns.resolver.Resolver:
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = lifetime
    return resolver


def _txt_to_string(record: Any) -> str:
    if hasattr(record, "strings"):
        return "".join(part.decode("utf-8", errors="replace") for part in record.strings)
    return str(record).strip('"')


def _record_to_row(record: Any, record_type: str) -> dict[str, Any]:
    if record_type in {"A", "AAAA"}:
        return {"type": record_type, "value": record.address}
    if record_type == "MX":
        return {
            "type": "MX",
            "preference": record.preference,
            "exchange": str(record.exchange).rstrip("."),
            "value": f"{record.preference} {str(record.exchange).rstrip('.')}",
        }
    if record_type == "TXT":
        return {"type": "TXT", "value": _txt_to_string(record)}
    if record_type == "NS":
        return {"type": "NS", "value": str(record.target).rstrip(".")}
    if record_type == "CNAME":
        return {"type": "CNAME", "value": str(record.target).rstrip(".")}
    if record_type == "SOA":
        return {
            "type": "SOA",
            "primary_ns": str(record.mname).rstrip("."),
            "responsible_party": str(record.rname).rstrip("."),
            "serial": record.serial,
            "refresh": record.refresh,
            "retry": record.retry,
            "expire": record.expire,
            "minimum": record.minimum,
            "value": str(record),
        }
    return {"type": record_type, "value": str(record)}


def _error_result(domain: str, record_type: str, query_name: str, status: str, message: str) -> dict[str, Any]:
    result = _base_result(domain, record_type, query_name)
    result["status"] = status
    result["error"] = message
    return result


def resolve_records(domain: str, record_type: str) -> dict[str, Any]:
    """Resolve one DNS record type and return a serializable result dict."""
    normalized = normalize_domain(domain)
    requested_type = (record_type or "").upper().strip()

    if not normalized:
        return _error_result(normalized, requested_type, normalized, "Invalid", "Enter a domain name.")
    if len(normalized) > MAX_DOMAIN_LENGTH:
        return _error_result(
            normalized,
            requested_type,
            normalized,
            "Invalid",
            f"Domain is longer than {MAX_DOMAIN_LENGTH} characters.",
        )

    query_type = requested_type
    query_name = normalized
    if requested_type == "DMARC":
        query_type = "TXT"
        query_name = f"_dmarc.{normalized}"
    elif requested_type == "SPF":
        query_type = "TXT"

    result = _base_result(normalized, requested_type, query_name)

    try:
        answers = _get_resolver().resolve(query_name, query_type)
    except dns.resolver.NXDOMAIN:
        return _error_result(normalized, requested_type, query_name, "NXDOMAIN", "Domain does not exist.")
    except dns.resolver.NoAnswer:
        return _error_result(normalized, requested_type, query_name, "No Answer", "No matching DNS records were found.")
    except dns.exception.Timeout:
        return _error_result(normalized, requested_type, query_name, "Timeout", "DNS lookup timed out.")
    except dns.resolver.NoNameservers:
        return _error_result(
            normalized,
            requested_type,
            query_name,
            "Nameserver Error",
            "Nameservers could not answer this query.",
        )
    except dns.exception.DNSException as exc:
        return _error_result(normalized, requested_type, query_name, "DNS Error", str(exc))

    records = [_record_to_row(record, query_type) for record in answers]
    if requested_type == "SPF":
        records = [record for record in records if str(record.get("value", "")).lower().startswith("v=spf1")]
    elif requested_type == "DMARC":
        records = [record for record in records if str(record.get("value", "")).lower().startswith("v=dmarc1")]

    if not records:
        label = "SPF" if requested_type == "SPF" else "DMARC" if requested_type == "DMARC" else requested_type
        return _error_result(normalized, requested_type, query_name, "No Answer", f"No {label} record was found.")

    result["ok"] = True
    result["records"] = records
    result["raw_values"] = [str(record.get("value", "")) for record in records]
    result["status"] = "Healthy"
    return result


def get_dns_summary(domain: str, include_dmarc: bool = True) -> dict[str, Any]:
    """Return DNS records and email security indicators for a domain."""
    normalized = normalize_domain(domain)
    lookups = {
        "A": resolve_records(normalized, "A"),
        "AAAA": resolve_records(normalized, "AAAA"),
        "MX": resolve_records(normalized, "MX"),
        "TXT": resolve_records(normalized, "TXT"),
        "SPF": resolve_records(normalized, "SPF"),
    }
    if include_dmarc:
        lookups["DMARC"] = resolve_records(normalized, "DMARC")

    a_found = bool(lookups["A"]["records"])
    aaaa_found = bool(lookups["AAAA"]["records"])
    mx_found = bool(lookups["MX"]["records"])
    spf_found = bool(lookups["SPF"]["records"])
    dmarc_found = bool(lookups.get("DMARC", {}).get("records")) if include_dmarc else None

    if lookups["A"]["status"] == "NXDOMAIN" or lookups["AAAA"]["status"] == "NXDOMAIN":
        dns_status = "Critical"
    elif a_found or aaaa_found:
        dns_status = "Healthy"
    elif any(item["status"] == "Timeout" for item in lookups.values()):
        dns_status = "Unknown"
    else:
        dns_status = "Warning"

    if mx_found and spf_found and (dmarc_found or not include_dmarc):
        email_status = "Healthy"
    elif mx_found or spf_found or dmarc_found:
        email_status = "Warning"
    else:
        email_status = "Critical"

    return {
        "domain": normalized,
        "lookups": lookups,
        "status": dns_status,
        "email_status": email_status,
        "a_found": a_found,
        "aaaa_found": aaaa_found,
        "mx_found": mx_found,
        "spf_found": spf_found,
        "dmarc_found": dmarc_found,
    }
