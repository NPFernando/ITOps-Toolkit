from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain, resolve_records
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="DNS Record Checker", layout="wide")
apply_app_shell(active_page="DNS Record Checker")


EXPLANATIONS = {
    "A": "Maps a hostname to IPv4 addresses.",
    "AAAA": "Maps a hostname to IPv6 addresses.",
    "MX": "Identifies mail servers for the domain.",
    "TXT": "Stores text records used for verification, email security, and service configuration.",
    "NS": "Lists authoritative nameservers.",
    "CNAME": "Aliases one hostname to another canonical hostname.",
    "SOA": "Shows zone authority and serial metadata.",
    "DMARC": "Shows email authentication policy at _dmarc.domain.",
    "SPF": "Shows which senders are allowed to send mail for the domain.",
}


render_page_header(
    "DNS Record Checker",
    "Look up public DNS records and view friendly explanations.",
    warning="Do not enter private hostnames or sensitive customer data.",
)

with tool_form_panel("dns_records"):
    render_form_intro("Look up DNS records", "Choose a public domain and record type to inspect.")
    with st.form("dns-form"):
        domain = st.text_input("Domain", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        record_type = st.selectbox("Record type", list(EXPLANATIONS.keys()))
        submitted = st.form_submit_button("Look up records")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    ok, error = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
    normalized = normalize_domain(domain)
    if not ok:
        st.session_state["dns_records_validation_error"] = error
        st.session_state["dns_records_result"] = None
    elif not normalized:
        st.session_state["dns_records_validation_error"] = "Enter a domain name."
        st.session_state["dns_records_result"] = None
    else:
        st.session_state["dns_records_validation_error"] = None
        st.session_state["dns_records_result"] = {
            "record_type": record_type,
            "data": resolve_records(normalized, record_type),
        }

validation_error = st.session_state.get("dns_records_validation_error")
stored = st.session_state.get("dns_records_result")

if validation_error is None and stored is None:
    render_empty_state("Ready to query DNS", "Record results, raw values, and the queried name appear after lookup.")

if validation_error is not None:
    st.error(validation_error)

if stored is not None:
    result = stored["data"]
    with tool_result_panel("dns_result", related_to="dns_records"):
        render_section_heading(f"{stored['record_type']} records", EXPLANATIONS[stored["record_type"]])

        if result["ok"]:
            st.success(result["status"])
            st.dataframe(pd.DataFrame(result["records"]), width="stretch", hide_index=True)
        else:
            st.warning(result["status"])
            st.error(result["error"])

        with st.expander("Raw values"):
            if result["raw_values"]:
                st.code("\n".join(result["raw_values"]))
            else:
                st.caption("No raw values returned.")

        st.caption(f"Queried name: {result['query_name']}")
