from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.dns_tools import MAX_DOMAIN_LENGTH, get_dns_summary, normalize_domain
from utils.http_tools import check_http_status
from utils.scoring import calculate_risk_score
from utils.ssl_tools import get_certificate_info
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    display_rows_frame,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_download_panel,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Domain Health Checker", layout="wide")
apply_app_shell(active_page="Domain Health Checker")


def _display_status(status: str) -> None:
    if status == "Healthy":
        st.success(status)
    elif status == "Warning":
        st.warning(status)
    elif status == "Critical":
        st.error(status)
    else:
        st.info(status or "Unknown")


def _join(values: list[Any]) -> str:
    return "; ".join(str(value) for value in values) if values else "None found"


def _format_dt(value: Any) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S %Z")
    return "Unknown"


def _records_frame(label: str, records: list[dict[str, Any]]) -> None:
    st.markdown(f"**{label}**")
    if records:
        st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)
    else:
        st.caption("No records found.")


def _score_gauge(score: int, status: str) -> go.Figure:
    color = "#2e7d32" if status == "Healthy" else "#ed6c02" if status == "Warning" else "#d32f2f"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": color}},
        )
    )
    fig.update_layout(height=220, margin={"l": 20, "r": 20, "t": 20, "b": 20})
    return fig


def _csv_rows(dns_summary: dict[str, Any], ssl_result: dict[str, Any], http_result: dict[str, Any], risk: dict[str, Any]) -> list[dict[str, Any]]:
    lookups = dns_summary["lookups"]
    rows = [
        {"section": "Summary", "check": "Risk score", "value": risk["score"], "status": risk["status"]},
        {"section": "DNS", "check": "DNS status", "value": dns_summary["status"], "status": dns_summary["status"]},
        {"section": "DNS", "check": "A records", "value": _join(lookups["A"]["raw_values"]), "status": lookups["A"]["status"]},
        {"section": "DNS", "check": "AAAA records", "value": _join(lookups["AAAA"]["raw_values"]), "status": lookups["AAAA"]["status"]},
        {"section": "DNS", "check": "MX records", "value": _join(lookups["MX"]["raw_values"]), "status": lookups["MX"]["status"]},
        {"section": "DNS", "check": "TXT records", "value": _join(lookups["TXT"]["raw_values"]), "status": lookups["TXT"]["status"]},
        {"section": "DNS", "check": "SPF", "value": "Found" if dns_summary["spf_found"] else "Missing", "status": "Healthy" if dns_summary["spf_found"] else "Warning"},
        {"section": "SSL", "check": "TLS status", "value": ssl_result["tls_status"], "status": ssl_result["tls_status"]},
        {"section": "SSL", "check": "Days remaining", "value": ssl_result["days_remaining"], "status": ssl_result["tls_status"]},
        {"section": "HTTP", "check": "Status code", "value": http_result["status_code"], "status": "Healthy" if http_result["ok"] else "Warning"},
        {"section": "HTTP", "check": "Final URL", "value": http_result["final_url"], "status": "Healthy" if http_result["ok"] else "Warning"},
    ]
    if "DMARC" in lookups:
        rows.append(
            {
                "section": "DNS",
                "check": "DMARC",
                "value": "Found" if dns_summary["dmarc_found"] else "Missing",
                "status": "Healthy" if dns_summary["dmarc_found"] else "Warning",
            }
        )
    return rows


def _markdown_summary(domain: str, dns_summary: dict[str, Any], ssl_result: dict[str, Any], http_result: dict[str, Any], risk: dict[str, Any]) -> str:
    recommendations = risk["recommendations"] or ["No critical recommendations from the current checks."]
    return "\n".join(
        [
            f"# Domain Health Summary: {domain}",
            "",
            f"- Risk score: {risk['score']} ({risk['status']})",
            f"- DNS status: {dns_summary['status']}",
            f"- Email security status: {dns_summary['email_status']}",
            f"- HTTP status: {http_result.get('status_code') or 'Unknown'}",
            f"- Response time: {http_result.get('response_time_ms') or 'Unknown'} ms",
            f"- SSL days remaining: {ssl_result.get('days_remaining') if ssl_result.get('days_remaining') is not None else 'Unknown'}",
            "",
            "## Recommendations",
            *[f"- {item}" for item in recommendations],
            "",
        ]
    )


render_page_header(
    "Domain Health Checker",
    "Check public DNS, HTTPS, SSL, and basic email security signals.",
    warning="Do not enter private hostnames or sensitive customer data.",
)

with tool_form_panel("domain_health"):
    render_form_intro(
        "Run health check",
        "Enter a public domain to check DNS, TLS, HTTP reachability, and email security signals.",
    )
    with st.form("domain-health-form"):
        domain = st.text_input("Domain name", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        col_a, col_b = st.columns(2)
        check_www = col_a.checkbox("Check www subdomain", value=True)
        include_dmarc = col_b.checkbox("Include DMARC check", value=True)
        submitted = st.form_submit_button("Run health check")

if not submitted:
    render_empty_state(
        "Ready for a public domain",
        "Results, recommendations, and exports appear here after the health check completes.",
    )

if submitted:
    ok, error = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
    normalized = normalize_domain(domain)
    if not ok:
        st.error(error)
    elif not normalized:
        st.error("Enter a domain name.")
    else:
        with st.spinner("Running public checks..."):
            dns_summary = get_dns_summary(normalized, include_dmarc=include_dmarc)
            ssl_result = get_certificate_info(normalized)
            http_result = check_http_status(normalized)
            dmarc_for_score = bool(dns_summary["dmarc_found"]) if include_dmarc else True
            risk = calculate_risk_score(
                http_ok=bool(http_result["ok"]),
                ssl_ok=bool(ssl_result["ok"]),
                ssl_days_remaining=ssl_result["days_remaining"],
                mx_found=bool(dns_summary["mx_found"]),
                spf_found=bool(dns_summary["spf_found"]),
                dmarc_found=dmarc_for_score,
            )

        with tool_result_panel("domain_summary"):
            render_section_heading("Summary", "Overall reachability, TLS, DNS, email security, and risk score.")
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("HTTP status", http_result["status_code"] or "Failed")
            m2.metric("Response time", f"{http_result['response_time_ms']} ms" if http_result["response_time_ms"] else "Unknown")
            m3.metric("SSL days", ssl_result["days_remaining"] if ssl_result["days_remaining"] is not None else "Unknown")
            m4.metric("DNS status", dns_summary["status"])
            m5.metric("Email security", dns_summary["email_status"])
            m6.metric("Risk score", risk["score"], risk["status"])

            gauge_col, status_col = st.columns([1, 2])
            with gauge_col:
                st.plotly_chart(_score_gauge(risk["score"], risk["status"]), width="stretch")
            with status_col:
                st.markdown("**Overall status**")
                _display_status(risk["status"])
                if risk["deductions"]:
                    st.dataframe(pd.DataFrame(risk["deductions"]), width="stretch", hide_index=True)
                else:
                    st.caption("No score deductions.")

        render_section_heading("DNS", "Resolved address, mail, text, SPF, and DMARC records.")
        lookups = dns_summary["lookups"]
        _display_status(dns_summary["status"])
        _records_frame("A records", lookups["A"]["records"])
        _records_frame("AAAA records", lookups["AAAA"]["records"])
        _records_frame("MX records", lookups["MX"]["records"])
        _records_frame("TXT records", lookups["TXT"]["records"])
        col_spf, col_dmarc = st.columns(2)
        col_spf.metric("SPF record", "Found" if dns_summary["spf_found"] else "Missing")
        col_dmarc.metric(
            "DMARC record",
            "Found" if dns_summary["dmarc_found"] else "Missing" if include_dmarc else "Not checked",
        )

        render_section_heading("SSL", "Certificate validity, issuer, subject, and expiration state.")
        _display_status(ssl_result["tls_status"])
        if ssl_result["error"]:
            st.error(ssl_result["error"])
        cert_rows = [
            {"field": "Subject", "value": ssl_result["subject"].get("commonName", "Unknown")},
            {"field": "Issuer", "value": ssl_result["issuer"].get("commonName", "Unknown")},
            {"field": "Valid from", "value": _format_dt(ssl_result["valid_from"])},
            {"field": "Valid until", "value": _format_dt(ssl_result["valid_until"])},
            {"field": "Days remaining", "value": ssl_result["days_remaining"] if ssl_result["days_remaining"] is not None else "Unknown"},
        ]
        st.dataframe(display_rows_frame(cert_rows), width="stretch", hide_index=True)
        if ssl_result["days_remaining"] is not None and ssl_result["days_remaining"] < 30:
            st.warning("SSL certificate expires in less than 30 days.")

        render_section_heading("HTTP", "Final URL, response status, timing, and redirect information.")
        if http_result["error"]:
            st.error(http_result["error"])
        http_rows = [
            {"field": "Final URL", "value": http_result["final_url"] or "Unknown"},
            {"field": "Status code", "value": http_result["status_code"] or "Unknown"},
            {"field": "Reason", "value": http_result["reason"] or "Unknown"},
            {"field": "Response time", "value": f"{http_result['response_time_ms']} ms" if http_result["response_time_ms"] else "Unknown"},
        ]
        st.dataframe(display_rows_frame(http_rows), width="stretch", hide_index=True)
        if http_result["redirect_chain"]:
            with st.expander("Redirect chain"):
                st.dataframe(pd.DataFrame(http_result["redirect_chain"]), width="stretch", hide_index=True)

        if check_www and not normalized.startswith("www."):
            with st.expander("www subdomain check"):
                www_domain = f"www.{normalized}"
                www_dns = get_dns_summary(www_domain, include_dmarc=False)
                www_http = check_http_status(www_domain)
                st.metric("www DNS status", www_dns["status"])
                st.metric("www HTTP status", www_http["status_code"] or "Failed")
                if www_http["error"]:
                    st.warning(www_http["error"])

        render_section_heading("Recommendations", "Prioritized fixes from the current checks.", eyebrow="Actions")
        combined_recommendations = list(dict.fromkeys(risk["recommendations"] + http_result["recommendations"]))
        if combined_recommendations:
            for item in combined_recommendations:
                st.warning(item)
        else:
            st.success("No major recommendations from the current checks.")

        rows = _csv_rows(dns_summary, ssl_result, http_result, risk)
        csv_data = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        markdown_data = _markdown_summary(normalized, dns_summary, ssl_result, http_result, risk)
        with tool_download_panel("domain_exports"):
            render_section_heading("Export", "Download the current in-memory results.", eyebrow="Downloads")
            export_col_a, export_col_b = st.columns(2)
            export_col_a.download_button("Download results as CSV", csv_data, file_name=f"{normalized}-health.csv", mime="text/csv")
            export_col_b.download_button(
                "Download summary as Markdown",
                markdown_data,
                file_name=f"{normalized}-health.md",
                mime="text/markdown",
            )
