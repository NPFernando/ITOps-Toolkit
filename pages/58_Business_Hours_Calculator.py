from __future__ import annotations

import streamlit as st

from utils.business_hours import COMMON_TIMEZONES, DEFAULT_BUSINESS_END, DEFAULT_BUSINESS_START, MAX_INPUT_LENGTH, calculate_business_hours
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


st.set_page_config(page_title="Business Hours Calculator", layout="wide")
apply_app_shell(active_page="Business Hours Calculator")


st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stFormSubmitButton"] > button {
        min-height: 2.75rem;
        font-size: 1rem;
      }
      div[data-testid="stTextInput"] input,
      div[data-testid="stTimeInput"] input,
      div[data-testid="stSelectbox"] [data-baseweb="select"] {
        font-size: 1rem;
      }
      div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
        overflow-wrap: anywhere;
      }
      div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        overflow-wrap: anywhere;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "Business Hours Calculator",
    "Compute elapsed business hours between two timestamps, excluding weekends and holidays -- useful for SLA and ticket-response math.",
)

with tool_form_panel("business_hours"):
    render_form_intro("Calculate", "Enter a start and end timestamp, timezone, and business-hours window.")
    with st.form("business-hours-form"):
        start_col, end_col = st.columns(2)
        start_input = start_col.text_input("Start (ISO 8601)", placeholder="2026-08-07T16:00:00", max_chars=MAX_INPUT_LENGTH)
        end_input = end_col.text_input("End (ISO 8601)", placeholder="2026-08-10T10:00:00", max_chars=MAX_INPUT_LENGTH)

        timezone = st.selectbox("Timezone", COMMON_TIMEZONES, index=0)

        business_start_col, business_end_col = st.columns(2)
        business_start = business_start_col.time_input("Business hours start", value=DEFAULT_BUSINESS_START)
        business_end = business_end_col.time_input("Business hours end", value=DEFAULT_BUSINESS_END)

        holidays_input = st.text_input("Holidays (comma-separated, optional)", placeholder="2026-12-25, 2026-01-01")

        submitted = st.form_submit_button("Calculate", use_container_width=True)

if submitted:
    # Stored in session_state so results survive the sidebar's own reruns
    # (quick-search box, favorite stars) after the initial submit.
    st.session_state["business_hours_state"] = calculate_business_hours(start_input, end_input, timezone, business_start, business_end, holidays_input)

state = st.session_state.get("business_hours_state")

if state is None:
    render_empty_state("Ready to calculate", "Elapsed business hours appear here after calculation.")
    render_status_note(
        "Awaiting timestamps",
        "Enter start/end timestamps and submit to calculate elapsed business hours.",
        tone="neutral",
    )

if state is not None:
    with tool_result_panel("business_hours_result", related_to="business_hours"):
        render_section_heading("Elapsed business hours", eyebrow="Result")
        if not state["ok"]:
            st.error(state["error"])
            render_status_note(
                "Calculation failed",
                "Fix the input values and run the calculation again.",
                tone="warning",
            )
        else:
            hours_col, days_col = st.columns(2)
            hours_col.metric("Business hours", state["business_hours_display"])
            days_col.metric("Business days spanned", state["business_days_spanned"])
            st.caption(f"{state['business_hours']} decimal hours total.")
            render_status_note(
                "Calculation complete",
                f"{state['business_hours_display']} across {state['business_days_spanned']} business day(s).",
                tone="success",
            )
