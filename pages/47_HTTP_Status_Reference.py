from __future__ import annotations

import streamlit as st

from utils.http_status_reference import search_statuses
from utils.ui import (
    apply_app_shell,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="HTTP Status Reference", layout="wide")
apply_app_shell(active_page="HTTP Status Reference")

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
    "HTTP Status Reference",
    "Look up HTTP status codes by number, category, or keyword -- a quick lookup when a code shows up in a log.",
)

with tool_form_panel("http_status_reference"):
    render_form_intro("Search status codes", "Search by code, category (1xx-5xx), or keyword.")
    with st.form("http-status-reference-form"):
        query_input = st.text_input("Search", placeholder="404, 5xx, rate limiting...")
        submitted = st.form_submit_button("Search", use_container_width=True)
        st.caption("Keyboard tip: focus Search and press Enter or Space to submit.")

if submitted:
    st.session_state["http_status_reference_query"] = query_input

query = st.session_state.get("http_status_reference_query", "")

results = search_statuses(query)
with tool_result_panel("http_status_reference_result", related_to="http_status_reference"):
    render_section_heading("Status codes", f"{len(results)} matching code(s).")
    if results:
        st.dataframe(
            [
                {"Code": entry.code, "Category": entry.category, "Name": entry.name, "Description": entry.description}
                for entry in results
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        render_status_note("No matching status codes", "No status codes matched that search.", tone="neutral")
