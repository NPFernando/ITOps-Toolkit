from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.http_methods_reference import search_http_methods
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("HTTP Methods Reference")
st.set_page_config(page_title="HTTP Methods Reference", layout="wide")
apply_app_shell(active_page="HTTP Methods Reference")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "HTTP Methods Reference",
    "Look up HTTP methods and their safe/idempotent/cacheable properties per RFC 9110.",
)

with tool_form_panel("http_methods_reference"):
    render_form_intro("Search methods", "Search by method name or keyword.")
    with st.form("http-methods-reference-form"):
        query = st.text_input("Search", placeholder="GET, idempotent, preflight...")
        submitted = st.form_submit_button("Search methods", use_container_width=True)

if submitted:
    st.session_state["http_methods_reference_result"] = search_http_methods(query)

results = st.session_state.get("http_methods_reference_result")

if results is None:
    render_empty_state("Ready to search", "Search results appear here.")
    render_status_note("Awaiting search", "Enter a method or keyword and select Search methods.", tone="neutral")
else:
    with tool_result_panel("http_methods_reference_result", related_to="http_methods_reference"):
        render_section_heading("HTTP methods", f"{len(results)} matching method(s).")
        if results:
            st.table(
                [
                    {
                        "Method": entry.method,
                        "Safe": "Yes" if entry.safe else "No",
                        "Idempotent": "Yes" if entry.idempotent else "No",
                        "Cacheable": "Yes" if entry.cacheable else "No",
                        "Description": entry.description,
                    }
                    for entry in results
                ]
            )
            render_status_note("Search complete", "Matching HTTP methods are listed in the results table.", tone="success")
        else:
            render_status_note("No matches found", "No methods matched that search term. Try a method name like GET or POST.", tone="warning")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
