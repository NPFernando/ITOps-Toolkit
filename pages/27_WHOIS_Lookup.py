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


st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stFormSubmitButton"] > button {
        min-height: 2.75rem;
        font-size: 1rem;
      }
      div[data-testid="stTextInput"] input {
        font-size: 1rem;
      }
      div[data-testid="stTable"] table th,
      div[data-testid="stTable"] table td {
        white-space: normal !important;
        word-break: break-word;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "WHOIS Lookup",
    "Look up domain registration details (registrar, key dates, name servers) via RDAP.",
    warning="Do not enter private hostnames or sensitive customer data.",
)

with tool_form_panel("whois_lookup"):
    render_form_intro("Enter a domain", "Looks up registration data via the RDAP protocol.")
    with st.form("whois-form"):
        domain_input = st.text_input("Domain", max_chars=MAX_DOMAIN_LENGTH, placeholder="example.com")
        submitted = st.form_submit_button("Look up", use_container_width=True)

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    with st.spinner("Querying RDAP..."):
        st.session_state["whois_lookup_result"] = lookup_whois(domain_input)

result = st.session_state.get("whois_lookup_result")

if result is None:
    render_empty_state("Ready to look up a domain", "Registrar, key dates, and name servers appear here.")

if result is not None:
    with tool_result_panel("whois_result", related_to="whois_lookup"):
        render_section_heading("Registration details", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.metric("Registrar", result["registrar"] or "Unknown")

            if result["events"]:
                st.dataframe([{"Event": e["label"], "Date": e["date"]} for e in result["events"]], width="stretch", hide_index=True)

            if result["nameservers"]:
                render_section_heading("Name servers", eyebrow="DNS")
                st.dataframe([{"Name server": ns} for ns in result["nameservers"]], width="stretch", hide_index=True)

            if result["status"]:
                render_section_heading("Domain status codes", eyebrow="EPP")
                st.dataframe([{"Status": status} for status in result["status"]], width="stretch", hide_index=True)
