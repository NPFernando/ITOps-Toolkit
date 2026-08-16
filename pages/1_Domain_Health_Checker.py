from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.dns_tools import MAX_DOMAIN_LENGTH, get_dns_summary, normalize_domain
from utils.http_tools import check_http_status
from utils.reporting import build_domain_health_html_report, build_domain_health_psa_note
from utils.scoring import calculate_risk_score
from utils.ssl_tools import get_certificate_info
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    display_rows_frame,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_download_panel,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("Domain Health Checker")
st.set_page_config(page_title="Domain Health Checker", layout="wide")
apply_app_shell(active_page="Domain Health Checker")
mark_page_baseline(_baseline, "shell-ready")


def _display_status(status: str) -> None:
    if status == "Healthy":
        render_status_note("Status: Healthy", "Signals look healthy in this section.", tone="success")
    elif status == "Warning":
        render_status_note("Status: Warning", "One or more checks need attention.", tone="warning")
    elif status == "Critical":
        render_status_note("Status: Critical", "An actionable issue was detected.", tone="warning")
    else:
        render_status_note("Status: Unknown", "Not enough data to confirm this section yet.", tone="neutral")


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
    posture = dns_summary.get("email_security_posture", {})
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
    for item in posture.get("rows", []):
        rows.append(
            {
                "section": "Email Security",
                "check": item.get("check", "Unknown"),
                "value": item.get("value", "Unknown"),
                "status": item.get("status", "Unknown"),
            }
        )
    return rows


def _markdown_summary(domain: str, dns_summary: dict[str, Any], ssl_result: dict[str, Any], http_result: dict[str, Any], risk: dict[str, Any]) -> str:
    posture = dns_summary.get("email_security_posture", {})
    recommendations = list(
        dict.fromkeys(risk["recommendations"] + http_result.get("recommendations", []) + posture.get("recommendations", []))
    ) or ["No critical recommendations from the current checks."]
    return "\n".join(
        [
            f"# Domain Health Summary: {domain}",
            "",
            f"- Risk score: {risk['score']} ({risk['status']})",
            f"- DNS status: {dns_summary['status']}",
            f"- Email security status: {dns_summary['email_status']}",
            f"- Email posture status: {posture.get('status', 'Unknown')}",
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
        domain_col, options_col = st.columns([1.3, 1], gap="medium")
        domain = domain_col.text_input("Domain name", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        check_www = options_col.checkbox("Check www subdomain", value=True)
        include_dmarc = options_col.checkbox("Include DMARC check", value=True)
        submitted = st.form_submit_button("Run health check", use_container_width=True)

if submitted:
    ok, error = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
    normalized = normalize_domain(domain)
    if not ok:
        render_failure_note("Domain input", error, remediation="Provide a valid public domain and run the check again.")
    elif not normalized:
        render_failure_note("Domain input", "Enter a domain name.", remediation="Provide a valid public domain and run the check again.")
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
            # Computed once here (not in the render section below) because the
            # render section runs on every rerun while results are showing --
            # touching the sidebar search, expanding another section, or
            # clicking any of the download buttons further down would otherwise
            # re-fire these two live network calls every single time.
            www_result = None
            if check_www and not normalized.startswith("www."):
                www_domain = f"www.{normalized}"
                www_result = {
                    "dns": get_dns_summary(www_domain, include_dmarc=False),
                    "http": check_http_status(www_domain),
                }
        # Stored in session_state (not rendered directly here) because the export
        # panel's download buttons and incident-message tabs below trigger reruns
        # of their own -- on those reruns `submitted` is False again, which would
        # otherwise collapse this whole results section right after a click.
        st.session_state["domain_health_state"] = {
            "normalized": normalized,
            "dns_summary": dns_summary,
            "ssl_result": ssl_result,
            "http_result": http_result,
            "risk": risk,
            "check_www": check_www,
            "include_dmarc": include_dmarc,
            "www_result": www_result,
        }

state = st.session_state.get("domain_health_state")

        rows = _csv_rows(dns_summary, ssl_result, http_result, risk)
        csv_data = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        markdown_data = _markdown_summary(normalized, dns_summary, ssl_result, http_result, risk)
        html_data = build_domain_health_html_report(normalized, dns_summary, ssl_result, http_result, risk, rows)
        with tool_download_panel("domain_exports", related_to="domain_health"):
            render_section_heading("Export", "Download the current in-memory results.", eyebrow="Downloads")
            export_col_a, export_col_b, export_col_c = st.columns(3)
            export_col_a.download_button("Download results as CSV", csv_data, file_name=f"{normalized}-health.csv", mime="text/csv")
            export_col_b.download_button(
                "Download summary as Markdown",
                markdown_data,
                file_name=f"{normalized}-health.md",
                mime="text/markdown",
            )
            st.code(psa_note, language=None)
            st.download_button(
                "Download PSA note (.txt)",
                psa_note,
                file_name=f"{normalized}-health-ticket-note.txt",
                mime="text/plain",
            )

if state is not None:
    normalized = state["normalized"]
    dns_summary = state["dns_summary"]
    ssl_result = state["ssl_result"]
    http_result = state["http_result"]
    risk = state["risk"]
    include_dmarc = state["include_dmarc"]

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

    posture = dns_summary.get("email_security_posture", {"rows": [], "recommendations": [], "status": "Unknown"})
    render_section_heading(
        "Email Security Posture",
        "DNS-only checks for DNSSEC, SPF, DMARC, MTA-STS, and SMTP TLS reporting.",
    )
    _display_status(posture["status"])
    if posture["rows"]:
        st.dataframe(pd.DataFrame(posture["rows"]), width="stretch", hide_index=True)
    else:
        st.caption("No email security posture rows were generated.")
    if posture["recommendations"]:
        for item in posture["recommendations"]:
            st.warning(item)
    else:
        st.success("No email security posture recommendations from the current DNS checks.")

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

    www_result = state.get("www_result")
    if www_result is not None:
        with st.expander("www subdomain check"):
            st.metric("www DNS status", www_result["dns"]["status"])
            st.metric("www HTTP status", www_result["http"]["status_code"] or "Failed")
            if www_result["http"]["error"]:
                st.warning(www_result["http"]["error"])

    render_section_heading("Recommendations", "Prioritized fixes from the current checks.", eyebrow="Actions")
    combined_recommendations = list(dict.fromkeys(risk["recommendations"] + http_result["recommendations"] + posture["recommendations"]))
    if combined_recommendations:
        for item in combined_recommendations:
            st.warning(item)
    else:
        st.success("No major recommendations from the current checks.")

    rows = _csv_rows(dns_summary, ssl_result, http_result, risk)
    csv_data = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
    markdown_data = _markdown_summary(normalized, dns_summary, ssl_result, http_result, risk)
    html_data = build_domain_health_html_report(normalized, dns_summary, ssl_result, http_result, risk, rows)
    psa_note = build_domain_health_psa_note(normalized, dns_summary, ssl_result, http_result, risk)
    with tool_download_panel("domain_exports", related_to="domain_health"):
        render_section_heading("Export", "Download the current in-memory results.", eyebrow="Downloads")
        export_col_a, export_col_b, export_col_c = st.columns(3)
        export_col_a.download_button("Download results as CSV", csv_data, file_name=f"{normalized}-health.csv", mime="text/csv")
        export_col_b.download_button(
            "Download summary as Markdown",
            markdown_data,
            file_name=f"{normalized}-health.md",
            mime="text/markdown",
        )
        export_col_c.download_button(
            "Download HTML report",
            html_data,
            file_name=f"{normalized}-health-report.html",
            mime="text/html",
        )

        render_section_heading(
            "PSA / ticket note",
            "Plain text, no markdown symbols -- ready to paste into a ConnectWise, Autotask, or Halo ticket note.",
            eyebrow="MSP export",
        )
        st.code(psa_note, language=None)
        st.download_button(
            "Download PSA note (.txt)",
            psa_note,
            file_name=f"{normalized}-health-ticket-note.txt",
            mime="text/plain",
        )

        render_section_heading(
            "Incident message",
            "Ready to paste into a Slack or Teams channel for a live incident update.",
            eyebrow="Chat export",
        )
        incident_tabs = st.tabs([target.title() for target in INCIDENT_MESSAGE_TARGETS])
        for tab, target in zip(incident_tabs, INCIDENT_MESSAGE_TARGETS, strict=True):
            with tab:
                incident_message = build_domain_health_incident_message(normalized, dns_summary, ssl_result, http_result, risk, target)
                st.code(incident_message["message"], language=None)
