from __future__ import annotations

import streamlit as st

from utils.log_duration import MAX_INPUT_LENGTH, calculate_log_duration
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Log Timestamp Duration Calculator", layout="wide")
apply_app_shell(active_page="Log Timestamp Duration Calculator")


render_page_header(
    "Log Timestamp Duration Calculator",
    "Compute the elapsed duration between two log timestamps -- auto-detects ISO 8601, Apache/nginx access log, and syslog formats.",
)

with tool_form_panel("log_duration"):
    render_form_intro("Calculate", "Paste a start and end timestamp from log lines. Formats can be mixed.")
    with st.form("log-duration-form"):
        col1, col2 = st.columns(2)
        start_input = col1.text_input("Start timestamp", placeholder="2026-08-07T16:00:00Z", max_chars=MAX_INPUT_LENGTH)
        end_input = col2.text_input("End timestamp", placeholder="07/Aug/2026:17:00:00 +0000", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Calculate")

if submitted:
    st.session_state["log_duration_state"] = calculate_log_duration(start_input, end_input)

state = st.session_state.get("log_duration_state")

if state is None:
    render_empty_state("Ready to calculate", "The detected format for each timestamp and the elapsed duration appear here after calculation.")

if state is not None:
    with tool_result_panel("log_duration_result", related_to="log_duration"):
        render_section_heading("Elapsed duration", eyebrow="Result")
        if not state["ok"]:
            st.error(state["error"])
        else:
            st.metric("Duration", state["duration_display"])
            st.caption(f"Start detected as {state['start_format']}. End detected as {state['end_format']}.")
            if "syslog" in (state["start_format"] or "") or "syslog" in (state["end_format"] or ""):
                st.caption("syslog timestamps have no year field -- the current year was assumed.")
