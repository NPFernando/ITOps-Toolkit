from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain, resolve_records
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    run_validated_lookup,
    tool_download_panel,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("DNS Record Checker")
st.set_page_config(page_title="DNS Record Checker", layout="wide")
apply_app_shell(active_page="DNS Record Checker")
mark_page_baseline(_baseline, "shell-ready")


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
    def _validate() -> str | None:
        ok, error = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
        if not ok:
            return error
        if not normalize_domain(domain):
            return "Enter a domain name."
        return None

    run_validated_lookup(
        "dns_records",
        _validate,
        lambda: {"record_type": record_type, "data": resolve_records(normalize_domain(domain), record_type)},
        spinner_text="Querying DNS...",
    )

validation_error = st.session_state.get("dns_records_validation_error")
stored = st.session_state.get("dns_records_result")

if validation_error is None and stored is None:
    render_empty_state(
        "Ready to query DNS",
        "Record results, raw values, and the queried name appear after lookup.",
        illustration="network",
    )

if validation_error is not None:
    render_failure_note("DNS input", validation_error, remediation="Provide a valid public domain and retry the lookup.")

if stored is not None:
    result = stored["data"]
    with tool_result_panel("dns_result", related_to="dns_records"):
        render_section_heading(f"{stored['record_type']} records", EXPLANATIONS[stored["record_type"]])

        if result["ok"]:
            render_status_note("DNS lookup completed", "Public DNS records were returned.", tone="success")
            st.dataframe(pd.DataFrame(result["records"]), width="stretch", hide_index=True)
        else:
            render_status_note(f"DNS status: {result['status']}", "DNS records were not returned for this query.", tone="warning")
            render_failure_note(
                "DNS lookup",
                result.get("error"),
                remediation="Confirm the record type and domain delegation, then retry after DNS propagation.",
            )

        with st.expander("Raw values"):
            if result["raw_values"]:
                st.code("\n".join(result["raw_values"]))
            else:
                st.caption("No raw values returned.")

        st.caption(f"Queried name: {result['query_name']}")

    records_csv = pd.DataFrame(result["records"]).to_csv(index=False).encode("utf-8")
    raw_values = "\n".join(result["raw_values"]) if result["raw_values"] else "No raw values returned."
    with tool_download_panel("dns_downloads", related_to="dns_records"):
        render_section_heading("Export", "Download current in-memory lookup output.", eyebrow="Downloads")
        col_a, col_b = st.columns(2)
        col_a.download_button(
            "Download records as CSV",
            records_csv,
            file_name=f"dns-{stored['record_type'].lower()}-records.csv",
            mime="text/csv",
        )
        col_b.download_button(
            "Download raw values (.txt)",
            raw_values,
            file_name=f"dns-{stored['record_type'].lower()}-raw-values.txt",
            mime="text/plain",
        )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
