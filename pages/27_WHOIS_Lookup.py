from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)
from utils.whois_tools import MAX_DOMAIN_LENGTH, lookup_whois


_baseline = start_page_baseline("WHOIS Lookup")
st.set_page_config(page_title="WHOIS Lookup", layout="wide")
apply_app_shell(active_page="WHOIS Lookup")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "WHOIS Lookup",
    "Look up domain registration details (registrar, key dates, name servers) via RDAP.",
    warning="Do not enter private hostnames or sensitive customer data.",
)

with tool_form_panel("whois_lookup"):
    render_form_intro("Enter a domain", "Looks up registration data via the RDAP protocol.")
    with st.form("whois-form"):
        domain_input = st.text_input("Domain", max_chars=MAX_DOMAIN_LENGTH, placeholder="example.com")
        submitted = st.form_submit_button("Look up")

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
            render_failure_note(
                "WHOIS lookup",
                result["error"],
                remediation="Confirm the domain format and retry the lookup.",
            )
        else:
            has_registration_data = bool(result["registrar"] or result["events"] or result["nameservers"] or result["status"])
            if has_registration_data:
                render_status_note("WHOIS lookup completed", "Registration details were returned from RDAP.", tone="success")
            else:
                render_status_note(
                    "WHOIS lookup returned limited data",
                    "RDAP responded, but registrar, event history, nameservers, and status codes were empty.",
                    tone="neutral",
                )

            render_section_heading("Registration details", eyebrow="Data")
            st.metric("Registrar", result["registrar"] or "Unknown")

            if result["events"]:
                st.dataframe([{"Event": e["label"], "Date": e["date"]} for e in result["events"]], width="stretch", hide_index=True)
            else:
                render_status_note(
                    "Registration events unavailable",
                    "No registration event timeline was included in this RDAP response.",
                    tone="neutral",
                )

            if result["nameservers"]:
                render_section_heading("Name servers", eyebrow="DNS")
                st.dataframe([{"Name server": ns} for ns in result["nameservers"]], width="stretch", hide_index=True)
            else:
                render_status_note(
                    "Name server list unavailable",
                    "No authoritative name servers were listed in this RDAP response.",
                    tone="neutral",
                )

            if result["status"]:
                render_section_heading("Domain status codes", eyebrow="EPP")
                st.dataframe([{"Status": status} for status in result["status"]], width="stretch", hide_index=True)
            else:
                render_status_note(
                    "Domain status codes unavailable",
                    "No EPP domain status codes were returned for this lookup.",
                    tone="neutral",
                )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
