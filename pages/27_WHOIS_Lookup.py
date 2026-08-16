from __future__ import annotations

import streamlit as st

from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)
from utils.whois_tools import MAX_DOMAIN_LENGTH, lookup_whois


st.set_page_config(page_title="WHOIS Lookup", layout="wide")
apply_app_shell(active_page="WHOIS Lookup")


render_page_header(
    "WHOIS Lookup",
    "Look up domain registration details (registrar, key dates, name servers) via RDAP.",
)

with tool_form_panel("whois_lookup"):
    render_form_intro("Enter a domain", "Looks up registration data via the RDAP protocol.")
    with st.form("whois-form"):
        domain_input = st.text_input("Domain", max_chars=MAX_DOMAIN_LENGTH, placeholder="example.com")
        submitted = st.form_submit_button("Look up")

if not submitted:
    render_empty_state("Ready to look up a domain", "Registrar, key dates, and name servers appear here.")

if submitted:
    with st.spinner("Querying RDAP..."):
        result = lookup_whois(domain_input)
    with tool_result_panel("whois_result"):
        render_section_heading("Registration details", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.metric("Registrar", result["registrar"] or "Unknown")

            if result["events"]:
                st.table([{"Event": e["label"], "Date": e["date"]} for e in result["events"]])

            if result["nameservers"]:
                render_section_heading("Name servers", eyebrow="DNS")
                st.table([{"Name server": ns} for ns in result["nameservers"]])

            if result["status"]:
                render_section_heading("Domain status codes", eyebrow="EPP")
                st.write(", ".join(result["status"]))
