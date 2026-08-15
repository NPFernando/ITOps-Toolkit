from __future__ import annotations

import streamlit as st

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
from utils.windows_error_reference import search_errors


st.set_page_config(page_title="Windows Error Reference", layout="wide")
apply_app_shell(active_page="Windows Error Reference")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stTextInput"] input {
        font-size: 1rem;
      }
      div[data-testid="stDataFrame"] [data-testid="stTable"] td,
      div[data-testid="stDataFrame"] [data-testid="stTable"] th {
        white-space: normal !important;
        word-break: break-word;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "Windows Error Reference",
    "Look up Windows/Win32 error codes (decimal or hex) -- system errors, service control, RPC, HRESULT, and NTSTATUS/BSOD codes.",
)

with tool_form_panel("windows_error_reference"):
    render_form_intro("Search errors", "Search by decimal code, hex code (e.g. 0x80070005), category, or keyword.")
    with st.form("windows-error-search-form"):
        query_input = st.text_input("Search", placeholder="5, 0xC0000005, RPC, access denied...")
        submitted = st.form_submit_button("Search reference", use_container_width=True)

if submitted:
    normalized_query = query_input.strip()
    if normalized_query:
        st.session_state["windows_error_reference_query"] = normalized_query
        st.session_state["windows_error_reference_validation_error"] = None
    else:
        st.session_state["windows_error_reference_query"] = None
        st.session_state["windows_error_reference_validation_error"] = "Enter a code or keyword to search."

query = st.session_state.get("windows_error_reference_query")
validation_error = st.session_state.get("windows_error_reference_validation_error")

if validation_error:
    render_failure_note(
        "Windows error search input",
        validation_error,
        remediation="Enter a decimal code, hex code, category, or keyword and run the search again.",
    )
elif query is None:
    render_empty_state("Ready to search errors", "Matching Windows error references appear here after you run a search.")

if query is not None:
    results = search_errors(query)
    with tool_result_panel("windows_error_reference_result", related_to="windows_error_reference"):
        render_section_heading("Errors", f"{len(results)} matching error(s).")
        if results:
            render_status_note("Matches found", "Windows error references matched the current search.", tone="success")
            st.dataframe(
                [
                    {
                        "Code": entry.code,
                        "Hex": entry.hex_code,
                        "Category": entry.category,
                        "Name": entry.name,
                        "Description": entry.description,
                    }
                    for entry in results
                ],
                width="stretch",
                hide_index=True,
            )
        else:
            render_status_note("No matches found", "No Windows errors matched that search. Try another code or keyword.", tone="neutral")
