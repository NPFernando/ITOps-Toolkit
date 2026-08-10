from __future__ import annotations

import streamlit as st

from utils.date_calculator import MAX_INPUT_LENGTH, UNITS, add_to_date, days_between
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Date Calculator", layout="wide")
apply_app_shell(active_page="Date Calculator")


render_page_header(
    "Date Calculator",
    "Add or subtract days/weeks/months from a date, or compute the number of calendar days between two dates.",
)

add_tab, between_tab = st.tabs(["Add/subtract", "Days between"])

with add_tab:
    with tool_form_panel("date_add"):
        render_form_intro("Add or subtract", "Enter a date and an amount to add (use a negative amount to subtract).")
        with st.form("date-add-form"):
            base_date = st.text_input("Date (YYYY-MM-DD)", placeholder="2026-08-10", max_chars=MAX_INPUT_LENGTH)
            c1, c2 = st.columns(2)
            amount = c1.number_input("Amount", value=0, step=1, min_value=-1_000_000, max_value=1_000_000)
            unit = c2.selectbox("Unit", UNITS)
            add_submitted = st.form_submit_button("Calculate")

    if add_submitted:
        st.session_state["date_add_result"] = add_to_date(base_date, int(amount), unit)

    add_result = st.session_state.get("date_add_result")

    if add_result is None:
        render_empty_state("Ready to calculate", "The resulting date appears here.")

    if add_result is not None:
        with tool_result_panel("date_add_result_panel", related_to="date_calculator"):
            render_section_heading("Result date", eyebrow="Result")
            if not add_result["ok"]:
                st.error(add_result["error"])
            else:
                st.metric("Date", add_result["result_date"])
                st.caption(f"Day of week: {add_result['weekday']}")

with between_tab:
    with tool_form_panel("date_between"):
        render_form_intro("Days between", "Enter two dates to see how many calendar days apart they are.")
        with st.form("date-between-form"):
            c1, c2 = st.columns(2)
            start_date = c1.text_input("Start date (YYYY-MM-DD)", placeholder="2026-01-01", max_chars=MAX_INPUT_LENGTH)
            end_date = c2.text_input("End date (YYYY-MM-DD)", placeholder="2026-08-10", max_chars=MAX_INPUT_LENGTH)
            between_submitted = st.form_submit_button("Calculate")

    if between_submitted:
        st.session_state["date_between_result"] = days_between(start_date, end_date)

    between_result = st.session_state.get("date_between_result")

    if between_result is None:
        render_empty_state("Ready to calculate", "The number of calendar days between the two dates appears here.")

    if between_result is not None:
        with tool_result_panel("date_between_result_panel", related_to="date_calculator"):
            render_section_heading("Days between", eyebrow="Result")
            if not between_result["ok"]:
                st.error(between_result["error"])
            else:
                st.metric("Calendar days", between_result["days"])
