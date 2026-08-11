from __future__ import annotations

import streamlit as st

from utils.http_methods_reference import search_http_methods
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="HTTP Methods Reference", layout="wide")
apply_app_shell(active_page="HTTP Methods Reference")


render_page_header(
    "HTTP Methods Reference",
    "Look up HTTP methods and their safe/idempotent/cacheable properties per RFC 9110.",
)

with tool_form_panel("http_methods_reference"):
    render_form_intro("Search methods", "Search by method name or keyword.")
    query = st.text_input("Search", placeholder="GET, idempotent, preflight...")

results = search_http_methods(query)
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
    else:
        st.info("No HTTP methods matched that search.")
