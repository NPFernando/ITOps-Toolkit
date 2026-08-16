from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.cve_tools import MAX_QUERY_LENGTH, lookup_cve
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
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="CVE Lookup", layout="wide")
apply_app_shell(active_page="CVE Lookup")

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
      section.main div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        gap: 0.5rem;
      }
      section.main div[data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
      }
      div[data-testid="stExpander"] .streamlit-expanderContent p,
      div[data-testid="stExpander"] .streamlit-expanderContent li {
        word-break: break-word;
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
    "CVE Lookup",
    "Search the NIST National Vulnerability Database by CVE ID or keyword.",
    warning="This queries the public NVD database -- do not enter sensitive or internal-only product names.",
)

with tool_form_panel("cve_lookup"):
    render_form_intro("Search CVEs", "Enter an exact CVE ID (e.g. CVE-2021-44228) or a keyword to search by.")
    with st.form("cve-form"):
        query = st.text_input("CVE ID or keyword", placeholder="CVE-2021-44228 or \"log4j remote code execution\"", max_chars=MAX_QUERY_LENGTH)
        submitted = st.form_submit_button("Search", use_container_width=True)

if submitted:
    def _validate() -> str | None:
        ok, error = validate_length(query, MAX_QUERY_LENGTH, "Query")
        return None if ok else error

    run_validated_lookup("cve_lookup", _validate, lambda: lookup_cve(query), spinner_text="Searching NVD...")

validation_error = st.session_state.get("cve_lookup_validation_error")
result = st.session_state.get("cve_lookup_result")

if validation_error is None and result is None:
    render_empty_state(
        "Ready to search CVEs",
        "Severity, description, and references appear after a search.",
        illustration="security",
    )

if validation_error is not None:
    render_failure_note(
        "CVE search input",
        validation_error,
        remediation="Enter a CVE ID or keyword and rerun the search.",
        mode="persistent",
    )

if result is not None:
    with tool_result_panel("cve_result", related_to="cve_lookup"):
        render_section_heading("Results", f"{result['total_results']} total result(s) from NVD.")
        if not result["ok"]:
            render_failure_note(
                "CVE lookup",
                result["error"],
                remediation="Retry the search or refine the query.",
            )
        else:
            if result["total_results"] > 0:
                render_status_note(
                    "CVE lookup completed",
                    f"Found {result['total_results']} matching result(s) from NVD.",
                    tone="success",
                )
            else:
                render_status_note(
                    "No CVEs matched this query",
                    "No records were returned by NVD. Try a broader keyword or verify the CVE ID format.",
                    tone="warning",
                )
            for entry in result["results"]:
                cvss = entry["cvss"]
                with st.expander(entry["id"], expanded=len(result["results"]) == 1):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Status", entry["status"] or "Unknown")
                    c2.metric("CVSS score", cvss["base_score"] if cvss else "Unknown")
                    c3.metric("Severity", cvss["base_severity"] if cvss else "Unknown")

                    st.markdown("**Description**")
                    st.write(entry["description"] or "No description available.")

                    rows = [
                        {"field": "Published", "value": entry["published"] or "Unknown"},
                        {"field": "Last modified", "value": entry["last_modified"] or "Unknown"},
                    ]
                    if cvss:
                        rows.append({"field": "CVSS vector", "value": cvss["vector_string"] or "Unknown"})
                    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

                    if entry["references"]:
                        st.markdown("**References**")
                        for url in entry["references"]:
                            st.markdown(f"- {url}")
