from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
from utils.ssl_tools import get_certificate_info
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    display_rows_frame,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="SSL Certificate Checker", layout="wide")
apply_app_shell(active_page="SSL Certificate Checker")


def _format_dt(value: Any) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S %Z")
    return "Unknown"


def _status(status: str) -> None:
    if status == "Healthy":
        st.success(status)
    elif status == "Warning":
        st.warning(status)
    elif status == "Critical":
        st.error(status)
    else:
        st.info(status or "Unknown")


render_page_header("SSL Certificate Checker", "Inspect a public TLS certificate without storing the result.")

with tool_form_panel("ssl_certificate"):
    render_form_intro("Check certificate", "Enter a public hostname and TLS port to inspect certificate status.")
    with st.form("ssl-form"):
        domain = st.text_input("Domain", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        port = st.number_input("Port", min_value=1, max_value=65535, value=443, step=1)
        submitted = st.form_submit_button("Check certificate")

if not submitted:
    render_empty_state("Ready to inspect TLS", "Certificate issuer, SANs, validity dates, and expiration status appear after the check.")

if submitted:
    ok, error = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
    normalized = normalize_domain(domain)
    if not ok:
        st.error(error)
    elif not normalized:
        st.error("Enter a domain name.")
    else:
        result = get_certificate_info(normalized, int(port))
        with tool_result_panel("ssl_result"):
            render_section_heading("Certificate result", "Connection status, expiration, issuer, and subject details.")
            _status(result["tls_status"])
            if result["error"]:
                st.error(result["error"])

            c1, c2, c3 = st.columns(3)
            c1.metric("TLS connection", "OK" if result["verification_ok"] else "Failed")
            c2.metric("Days remaining", result["days_remaining"] if result["days_remaining"] is not None else "Unknown")
            c3.metric("Port", result["port"])

            rows = [
                {"field": "Subject", "value": result["subject"].get("commonName", "Unknown")},
                {"field": "Issuer", "value": result["issuer"].get("commonName", "Unknown")},
                {"field": "Valid from", "value": _format_dt(result["valid_from"])},
                {"field": "Valid until", "value": _format_dt(result["valid_until"])},
                {"field": "Status", "value": result["tls_status"]},
            ]
            st.dataframe(display_rows_frame(rows), width="stretch", hide_index=True)

            if result["days_remaining"] is not None:
                if result["days_remaining"] < 0:
                    st.error("Certificate is expired.")
                elif result["days_remaining"] < 30:
                    st.warning("Certificate expires within 30 days.")

            with st.expander("Subject alternative names"):
                if result["san_names"]:
                    st.dataframe(pd.DataFrame({"SAN": result["san_names"]}), width="stretch", hide_index=True)
                else:
                    st.caption("No SAN names available.")
