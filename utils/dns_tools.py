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
    elif requested_type == "MTA_STS":
        query_type = "TXT"
        query_name = f"_mta-sts.{normalized}"
    elif requested_type == "TLS_RPT":
        query_type = "TXT"
        query_name = f"_smtp._tls.{normalized}"
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
    elif requested_type == "MTA_STS":
        records = [record for record in records if str(record.get("value", "")).lower().startswith("v=stsv1")]
    elif requested_type == "TLS_RPT":
        records = [record for record in records if str(record.get("value", "")).lower().startswith("v=tlsrptv1")]

    if not records:
        labels = {
            "SPF": "SPF",
            "DMARC": "DMARC",
            "MTA_STS": "MTA-STS",
            "TLS_RPT": "TLS-RPT",
        }
        label = labels.get(requested_type, requested_type)
        return _error_result(normalized, requested_type, query_name, "No Answer", f"No {label} record was found.")

    result["ok"] = True
    result["records"] = records
    result["raw_values"] = [str(record.get("value", "")) for record in records]
    result["status"] = "Healthy"
    return result


def _first_raw_value(lookup: dict[str, Any] | None) -> str:
    values = (lookup or {}).get("raw_values") or []
    return str(values[0]) if values else ""


def _policy_value(record: str, key: str) -> str | None:
    prefix = f"{key.lower()}="
    for part in record.split(";"):
        value = part.strip()
        if value.lower().startswith(prefix):
            return value.split("=", 1)[1].strip().lower()
    return None


def _posture_row(check: str, value: str, status: str, recommendation: str = "") -> dict[str, str]:
    return {
        "check": check,
        "value": value,
        "status": status,
        "recommendation": recommendation,
    }


def analyze_email_security_posture(lookups: dict[str, dict[str, Any]], include_dmarc: bool = True) -> dict[str, Any]:
    """Analyze DNS-only email security posture from existing lookup results."""
    rows: list[dict[str, str]] = []
    recommendations: list[str] = []

    def add_row(check: str, value: str, status: str, recommendation: str = "") -> None:
        rows.append(_posture_row(check, value, status, recommendation))
        if recommendation:
            recommendations.append(recommendation)

    dnssec_present = bool((lookups.get("DS") or {}).get("records") or (lookups.get("DNSKEY") or {}).get("records"))
    add_row(
        "DNSSEC",
        "DS or DNSKEY found" if dnssec_present else "No DS or DNSKEY found",
        "Healthy" if dnssec_present else "Warning",
        "" if dnssec_present else "Publish DNSSEC DS records at the registrar and DNSKEY records in the zone.",
    )

    spf_lookup = lookups.get("SPF") or {}
    spf_records = [str(value) for value in (spf_lookup.get("raw_values") or [])]
    if not spf_records:
        add_row("SPF policy", "Missing", "Warning", "Publish an SPF record for authorized mail senders.")
    elif len(spf_records) > 1:
        add_row("SPF policy", "Multiple SPF records", "Warning", "Keep exactly one SPF record; multiple SPF records can fail validation.")
    else:
        spf_value = spf_records[0].lower()
        if "+all" in spf_value:
            add_row("SPF policy", "+all allows any sender", "Critical", "Replace SPF +all with a restrictive all mechanism after validating senders.")
        elif "?all" in spf_value:
            add_row("SPF policy", "?all neutral policy", "Warning", "Use ~all or -all instead of ?all after validating authorized senders.")
        elif "~all" in spf_value:
            add_row("SPF policy", "~all softfail", "Warning", "Consider moving SPF from ~all to -all after validating all authorized senders.")
        elif "-all" in spf_value:
            add_row("SPF policy", "-all hardfail", "Healthy")
        else:
            add_row("SPF policy", "No all mechanism", "Warning", "Add an SPF all mechanism such as ~all or -all.")

    if include_dmarc:
        dmarc_value = _first_raw_value(lookups.get("DMARC"))
        if not dmarc_value:
            add_row("DMARC policy", "Missing", "Warning", "Publish a DMARC record at _dmarc with at least p=none and reporting.")
        else:
            policy = _policy_value(dmarc_value, "p")
            if policy == "reject":
                add_row("DMARC policy", "p=reject", "Healthy")
            elif policy == "quarantine":
                add_row("DMARC policy", "p=quarantine", "Healthy")
            elif policy == "none":
                add_row("DMARC policy", "p=none monitoring", "Warning", "Move DMARC from p=none toward quarantine or reject after reviewing reports.")
            else:
                add_row("DMARC policy", "Missing p= policy", "Warning", "Add a DMARC p= policy value such as p=none, p=quarantine, or p=reject.")

            rua = _policy_value(dmarc_value, "rua")
            add_row(
                "DMARC aggregate reports",
                "rua present" if rua else "rua missing",
                "Healthy" if rua else "Warning",
                "" if rua else "Add a DMARC rua= mailbox so aggregate reports can be reviewed.",
            )
    else:
        add_row("DMARC policy", "Not checked", "Unknown")

    mta_sts_value = _first_raw_value(lookups.get("MTA_STS"))
    add_row(
        "MTA-STS TXT",
        "v=STSv1 found" if mta_sts_value.lower().startswith("v=stsv1") else "Missing",
        "Healthy" if mta_sts_value.lower().startswith("v=stsv1") else "Warning",
        "" if mta_sts_value.lower().startswith("v=stsv1") else "Publish _mta-sts TXT with v=STSv1 and host the HTTPS policy file.",
    )

    tls_rpt_value = _first_raw_value(lookups.get("TLS_RPT"))
    add_row(
        "SMTP TLS reporting",
        "v=TLSRPTv1 found" if tls_rpt_value.lower().startswith("v=tlsrptv1") else "Missing",
        "Healthy" if tls_rpt_value.lower().startswith("v=tlsrptv1") else "Warning",
        "" if tls_rpt_value.lower().startswith("v=tlsrptv1") else "Publish _smtp._tls TXT with v=TLSRPTv1 to receive SMTP TLS reports.",
    )

    statuses = {row["status"] for row in rows}
    status = "Critical" if "Critical" in statuses else "Warning" if "Warning" in statuses else "Healthy"
    return {
        "status": status,
        "rows": rows,
        "recommendations": list(dict.fromkeys(recommendations)),
    }


def get_dns_summary(domain: str, include_dmarc: bool = True) -> dict[str, Any]:
    """Return DNS records and email security indicators for a domain."""
    normalized = normalize_domain(domain)
    lookups = {
        "A": resolve_records(normalized, "A"),
        "AAAA": resolve_records(normalized, "AAAA"),
        "MX": resolve_records(normalized, "MX"),
        "TXT": resolve_records(normalized, "TXT"),
        "SPF": resolve_records(normalized, "SPF"),
        "DS": resolve_records(normalized, "DS"),
        "DNSKEY": resolve_records(normalized, "DNSKEY"),
        "MTA_STS": resolve_records(normalized, "MTA_STS"),
        "TLS_RPT": resolve_records(normalized, "TLS_RPT"),
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

    email_security_posture = analyze_email_security_posture(lookups, include_dmarc=include_dmarc)
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
        "email_security_posture": email_security_posture,
    }
