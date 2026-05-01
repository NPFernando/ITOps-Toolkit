"""Standalone HTML report generation helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from html import escape
from typing import Any


def _value(value: Any, fallback: str = "Unknown") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S %Z")
    return str(value)


def _safe(value: Any, fallback: str = "Unknown") -> str:
    return escape(_value(value, fallback), quote=True)


def _status_class(status: Any) -> str:
    normalized = _value(status, "Unknown").lower()
    if normalized == "healthy":
        return "healthy"
    if normalized == "warning":
        return "warning"
    if normalized == "critical":
        return "critical"
    return "unknown"


def _status_badge(status: Any) -> str:
    text = _safe(status)
    return f'<span class="badge badge-{_status_class(status)}">{text}</span>'


def _metric_card(label: str, value: Any, status: Any | None = None) -> str:
    status_html = _status_badge(status) if status is not None else ""
    return (
        '<div class="metric-card">'
        f"<span>{escape(label)}</span>"
        f"<strong>{_safe(value)}</strong>"
        f"{status_html}"
        "</div>"
    )


def _table_rows(rows: list[tuple[str, Any, Any | None]]) -> str:
    if not rows:
        return '<tr><td colspan="3">No data available.</td></tr>'
    output = []
    for label, value, status in rows:
        status_html = _status_badge(status) if status is not None else ""
        output.append(
            "<tr>"
            f"<th>{escape(label)}</th>"
            f"<td>{_safe(value)}</td>"
            f"<td>{status_html}</td>"
            "</tr>"
        )
    return "".join(output)


def _list_items(values: list[Any], empty_text: str) -> str:
    items = [f"<li>{_safe(item)}</li>" for item in values if _value(item, "")]
    if not items:
        return f"<li>{escape(empty_text)}</li>"
    return "".join(items)


def _record_values(lookup: dict[str, Any] | None) -> str:
    if not lookup:
        return "None found"
    values = lookup.get("raw_values") or []
    return "; ".join(_value(item) for item in values) if values else "None found"


def _summary_rows_html(summary_rows: list[dict[str, Any]]) -> str:
    if not summary_rows:
        return '<tr><td colspan="4">No summary rows available.</td></tr>'
    output = []
    for row in summary_rows:
        output.append(
            "<tr>"
            f"<td>{_safe(row.get('section'))}</td>"
            f"<td>{_safe(row.get('check'))}</td>"
            f"<td>{_safe(row.get('value'))}</td>"
            f"<td>{_status_badge(row.get('status'))}</td>"
            "</tr>"
        )
    return "".join(output)


def _posture_rows_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="4">No email security posture rows available.</td></tr>'
    output = []
    for row in rows:
        output.append(
            "<tr>"
            f"<td>{_safe(row.get('check'))}</td>"
            f"<td>{_safe(row.get('value'))}</td>"
            f"<td>{_status_badge(row.get('status'))}</td>"
            f"<td>{_safe(row.get('recommendation'), '')}</td>"
            "</tr>"
        )
    return "".join(output)


def build_domain_health_html_report(
    domain: str,
    dns_summary: dict[str, Any],
    ssl_result: dict[str, Any],
    http_result: dict[str, Any],
    risk: dict[str, Any],
    summary_rows: list[dict[str, Any]],
    generated_at: datetime | None = None,
) -> str:
    """Build an escaped, standalone Domain Health HTML report."""
    timestamp = generated_at or datetime.now(UTC)
    lookups = dns_summary.get("lookups", {})
    posture = dns_summary.get("email_security_posture", {})
    recommendations = list(
        dict.fromkeys(
            (risk.get("recommendations") or [])
            + (http_result.get("recommendations") or [])
            + (posture.get("recommendations") or [])
        )
    )
    deductions = risk.get("deductions") or []

    metrics = [
        _metric_card("Risk score", risk.get("score"), risk.get("status")),
        _metric_card("DNS status", dns_summary.get("status"), dns_summary.get("status")),
        _metric_card("Email security", dns_summary.get("email_status"), dns_summary.get("email_status")),
        _metric_card("Email posture", posture.get("status"), posture.get("status")),
        _metric_card("HTTP status", http_result.get("status_code") or "Failed", "Healthy" if http_result.get("ok") else "Warning"),
        _metric_card("Response time", f"{http_result.get('response_time_ms')} ms" if http_result.get("response_time_ms") else "Unknown"),
        _metric_card("SSL days", ssl_result.get("days_remaining"), ssl_result.get("tls_status")),
    ]
    dns_rows = [
        ("DNS status", dns_summary.get("status"), dns_summary.get("status")),
        ("Email security status", dns_summary.get("email_status"), dns_summary.get("email_status")),
        ("A records", _record_values(lookups.get("A")), lookups.get("A", {}).get("status")),
        ("AAAA records", _record_values(lookups.get("AAAA")), lookups.get("AAAA", {}).get("status")),
        ("MX records", _record_values(lookups.get("MX")), lookups.get("MX", {}).get("status")),
        ("SPF record", "Found" if dns_summary.get("spf_found") else "Missing", "Healthy" if dns_summary.get("spf_found") else "Warning"),
        (
            "DMARC record",
            "Found" if dns_summary.get("dmarc_found") else "Missing" if dns_summary.get("dmarc_found") is not None else "Not checked",
            "Healthy" if dns_summary.get("dmarc_found") else "Warning" if dns_summary.get("dmarc_found") is False else "Unknown",
        ),
    ]
    ssl_rows = [
        ("TLS status", ssl_result.get("tls_status"), ssl_result.get("tls_status")),
        ("Subject", (ssl_result.get("subject") or {}).get("commonName"), None),
        ("Issuer", (ssl_result.get("issuer") or {}).get("commonName"), None),
        ("Valid from", ssl_result.get("valid_from"), None),
        ("Valid until", ssl_result.get("valid_until"), None),
        ("Days remaining", ssl_result.get("days_remaining"), ssl_result.get("tls_status")),
        ("Error", ssl_result.get("error") or "None", ssl_result.get("tls_status") if ssl_result.get("error") else None),
    ]
    http_rows = [
        ("Final URL", http_result.get("final_url"), None),
        ("Status code", http_result.get("status_code"), "Healthy" if http_result.get("ok") else "Warning"),
        ("Reason", http_result.get("reason"), None),
        ("Response time", f"{http_result.get('response_time_ms')} ms" if http_result.get("response_time_ms") else "Unknown", None),
        ("Uses HTTPS", "Yes" if http_result.get("uses_https") else "No", "Healthy" if http_result.get("uses_https") else "Warning"),
        ("Error", http_result.get("error") or "None", "Warning" if http_result.get("error") else None),
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Domain Health Report - {_safe(domain)}</title>
<style>
:root {{ color-scheme: light; }}
body {{ margin: 0; font-family: Arial, sans-serif; color: #07142f; background: #eef5ff; }}
.page {{ max-width: 1040px; margin: 0 auto; padding: 32px; }}
.hero {{ border: 1px solid #cddaf0; border-radius: 8px; padding: 24px; background: #ffffff; }}
.kicker {{ color: #126bff; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }}
h1 {{ margin: 8px 0 8px; font-size: 34px; line-height: 1.1; }}
h2 {{ margin: 28px 0 10px; font-size: 20px; }}
p {{ color: #334765; line-height: 1.55; }}
.meta {{ color: #52637f; font-size: 13px; }}
.notice {{ margin-top: 16px; border: 1px solid #ffd0ad; border-radius: 8px; padding: 12px 14px; background: #fff5ee; color: #334765; }}
.metrics {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }}
.metric-card {{ border: 1px solid #d9e5f7; border-radius: 8px; padding: 14px; background: #f9fbff; }}
.metric-card span {{ display: block; color: #60728f; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
.metric-card strong {{ display: block; margin-top: 6px; font-size: 22px; }}
.badge {{ display: inline-block; margin-top: 8px; border-radius: 8px; padding: 3px 8px; font-size: 11px; font-weight: 700; text-transform: uppercase; }}
.badge-healthy {{ color: #126b35; background: #dff7e8; }}
.badge-warning {{ color: #8a4300; background: #fff0d7; }}
.badge-critical {{ color: #9f1d1d; background: #ffe2e2; }}
.badge-unknown {{ color: #3f516b; background: #e7eef8; }}
table {{ width: 100%; border-collapse: collapse; overflow: hidden; border: 1px solid #d9e5f7; border-radius: 8px; background: #ffffff; }}
th, td {{ border-bottom: 1px solid #e4ecf8; padding: 10px 12px; text-align: left; vertical-align: top; font-size: 14px; }}
th {{ width: 28%; color: #243854; background: #f6f9ff; }}
tr:last-child th, tr:last-child td {{ border-bottom: 0; }}
ul {{ margin: 0; padding-left: 22px; color: #334765; line-height: 1.55; }}
.footer {{ margin-top: 28px; color: #60728f; font-size: 12px; }}
@media (max-width: 720px) {{ .page {{ padding: 16px; }} .metrics {{ grid-template-columns: 1fr; }} h1 {{ font-size: 28px; }} }}
</style>
</head>
<body>
<main class="page">
<section class="hero">
<div class="kicker">ITOps Toolkit</div>
<h1>Domain Health Report</h1>
<p>Public troubleshooting snapshot for <strong>{_safe(domain)}</strong>.</p>
<div class="meta">Generated {_safe(timestamp)}. Results are from a one-time in-memory check and are not stored by the toolkit.</div>
<div class="notice"><strong>Public-safe report:</strong> remove customer-sensitive context before sharing externally.</div>
<div class="metrics">{''.join(metrics)}</div>
</section>
<section>
<h2>DNS And Email Security</h2>
<table><tbody>{_table_rows(dns_rows)}</tbody></table>
</section>
<section>
<h2>Email Security Posture</h2>
<table>
<thead><tr><th>Check</th><th>Value</th><th>Status</th><th>Recommendation</th></tr></thead>
<tbody>{_posture_rows_html(posture.get("rows") or [])}</tbody>
</table>
</section>
<section>
<h2>SSL Certificate</h2>
<table><tbody>{_table_rows(ssl_rows)}</tbody></table>
</section>
<section>
<h2>HTTP Reachability</h2>
<table><tbody>{_table_rows(http_rows)}</tbody></table>
</section>
<section>
<h2>Score Deductions</h2>
<ul>{_list_items([f"-{item.get('points')} points: {item.get('reason')}" for item in deductions], "No score deductions.")}</ul>
</section>
<section>
<h2>Recommendations</h2>
<ul>{_list_items(recommendations, "No major recommendations from the current checks.")}</ul>
</section>
<section>
<h2>Summary Rows</h2>
<table>
<thead><tr><th>Section</th><th>Check</th><th>Value</th><th>Status</th></tr></thead>
<tbody>{_summary_rows_html(summary_rows)}</tbody>
</table>
</section>
<div class="footer">Generated by ITOps Toolkit. This report is standalone HTML with inline styles only.</div>
</main>
</body>
</html>
"""


__all__ = ["build_domain_health_html_report"]
