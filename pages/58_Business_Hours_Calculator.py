from __future__ import annotations

import streamlit as st

from utils.business_hours import COMMON_TIMEZONES, DEFAULT_BUSINESS_END, DEFAULT_BUSINESS_START, MAX_INPUT_LENGTH, calculate_business_hours
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Business Hours Calculator", layout="wide")
apply_app_shell(active_page="Business Hours Calculator")


render_page_header(
    "Business Hours Calculator",
    "Compute elapsed business hours between two timestamps, excluding weekends and holidays -- useful for SLA and ticket-response math.",
)

with tool_form_panel("business_hours"):
    render_form_intro("Calculate", "Enter a start and end timestamp, timezone, and business-hours window.")
    with st.form("business-hours-form"):
        col1, col2 = st.columns(2)
        start_input = col1.text_input("Start (ISO 8601)", placeholder="2026-08-07T16:00:00", max_chars=MAX_INPUT_LENGTH)
        end_input = col2.text_input("End (ISO 8601)", placeholder="2026-08-10T10:00:00", max_chars=MAX_INPUT_LENGTH)

        timezone = st.selectbox("Timezone", COMMON_TIMEZONES, index=0)

        hours_col1, hours_col2 = st.columns(2)
        business_start = hours_col1.time_input("Business hours start", value=DEFAULT_BUSINESS_START)
        business_end = hours_col2.time_input("Business hours end", value=DEFAULT_BUSINESS_END)

        holidays_input = st.text_input("Holidays (comma-separated, optional)", placeholder="2026-12-25, 2026-01-01")

        submitted = st.form_submit_button("Calculate")

if submitted:
    # Stored in session_state so results survive the sidebar's own reruns
    # (quick-search box, favorite stars) after the initial submit.
    st.session_state["business_hours_state"] = calculate_business_hours(start_input, end_input, timezone, business_start, business_end, holidays_input)

state = st.session_state.get("business_hours_state")

if state is None:
    render_empty_state("Ready to calculate", "Elapsed business hours appear here after calculation.")

if state is not None:
    with tool_result_panel("business_hours_result", related_to="business_hours"):
        render_section_heading("Elapsed business hours", eyebrow="Result")
        if not state["ok"]:
            st.error(state["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Business hours", state["business_hours_display"])
            c2.metric("Business days spanned", state["business_days_spanned"])
            st.caption(f"{state['business_hours']} decimal hours total.")
