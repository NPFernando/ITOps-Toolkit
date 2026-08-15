from __future__ import annotations

import streamlit as st

from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel
from utils.windows_event_reference import search_events


st.set_page_config(page_title="Windows Event Reference", layout="wide")
apply_app_shell(active_page="Windows Event Reference")


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
      details[data-testid="stExpander"] summary p {
        overflow-wrap: anywhere;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "Windows Event Reference",
    "Look up common Windows Event Log IDs by number, log name, source, severity, or keyword.",
)

with tool_form_panel("windows_event_reference"):
    render_form_intro("Search events", "Search by event ID, log (System/Application/Security/...), source, or keyword.")
    with st.form("windows-event-search-form"):
        query_input = st.text_input(
            "Search",
            placeholder="4625, Security, service failed to start...",
            help="Search by event ID, log, source, severity, or summary keyword.",
        )
        submitted = st.form_submit_button("Search", use_container_width=True)

if submitted:
    st.session_state["windows_event_reference_query"] = query_input

query = st.session_state.get("windows_event_reference_query", "")
results = search_events(query)
with tool_result_panel("windows_event_reference_result", related_to="windows_event_reference"):
    render_section_heading("Events", f"{len(results)} matching event(s).")
    if results:
        st.caption("Matching Windows Event Log references")
        for entry in results:
            title = f"{entry.event_id} · {entry.log} · {entry.severity}"
            with st.expander(title, expanded=len(results) <= 3):
                st.markdown(f"**Source:** {entry.source}")
                st.markdown(f"**Summary:** {entry.summary}")
                st.markdown(f"**Common cause:** {entry.common_cause}")
    else:
        st.info("No events matched that search.")
