from __future__ import annotations

import streamlit as st

from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel
from utils.windows_event_reference import search_events


st.set_page_config(page_title="Windows Event Reference", layout="wide")
apply_app_shell(active_page="Windows Event Reference")


render_page_header(
    "Windows Event Reference",
    "Look up common Windows Event Log IDs by number, log name, source, severity, or keyword.",
)

with tool_form_panel("windows_event_reference"):
    render_form_intro("Search events", "Search by event ID, log (System/Application/Security/...), source, or keyword.")
    query = st.text_input("Search", placeholder="4625, Security, service failed to start...")

results = search_events(query)
with tool_result_panel("windows_event_reference_result", related_to="windows_event_reference"):
    render_section_heading("Events", f"{len(results)} matching event(s).")
    if results:
        st.table(
            [
                {
                    "Event ID": entry.event_id,
                    "Log": entry.log,
                    "Source": entry.source,
                    "Severity": entry.severity,
                    "Summary": entry.summary,
                    "Common cause": entry.common_cause,
                }
                for entry in results
            ]
        )
    else:
        st.info("No events matched that search.")
