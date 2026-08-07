from __future__ import annotations

import streamlit as st

from utils.http_status_reference import search_statuses
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="HTTP Status Reference", layout="wide")
apply_app_shell(active_page="HTTP Status Reference")


render_page_header(
    "HTTP Status Reference",
    "Look up HTTP status codes by number, category, or keyword -- a quick lookup when a code shows up in a log.",
)

with tool_form_panel("http_status_reference"):
    render_form_intro("Search status codes", "Search by code, category (1xx-5xx), or keyword.")
    query = st.text_input("Search", placeholder="404, 5xx, rate limiting...")

results = search_statuses(query)
with tool_result_panel("http_status_reference_result", related_to="http_status_reference"):
    render_section_heading("Status codes", f"{len(results)} matching code(s).")
    if results:
        st.table(
            [
                {"Code": entry.code, "Category": entry.category, "Name": entry.name, "Description": entry.description}
                for entry in results
            ]
        )
    else:
        st.info("No status codes matched that search.")
