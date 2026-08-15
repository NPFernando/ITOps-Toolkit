from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.iso8601_duration import MAX_INPUT_LENGTH, build_duration, parse_duration
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("ISO 8601 Duration Tool")
st.set_page_config(page_title="ISO 8601 Duration Tool", layout="wide")
apply_app_shell(active_page="ISO 8601 Duration Tool")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "ISO 8601 Duration Tool",
    "Parse an ISO 8601 duration (e.g. P3Y6M4DT12H30M5S) into plain English, or build one from individual units.",
)

parse_tab, build_tab = st.tabs(["Parse", "Build"])

with parse_tab:
    with tool_form_panel("iso8601_parse"):
        render_form_intro("Enter an ISO 8601 duration", "")
        with st.form("iso8601-parse-form"):
            duration_input = st.text_input("Duration", placeholder="P3Y6M4DT12H30M5S", max_chars=MAX_INPUT_LENGTH)
            parse_submitted = st.form_submit_button("Parse", use_container_width=True)

    if parse_submitted:
        st.session_state["iso8601_parse_result"] = parse_duration(duration_input)

    parse_result = st.session_state.get("iso8601_parse_result")

    if parse_result is None:
        render_empty_state("Ready to parse", "The plain-English description appears here.")
        render_status_note("Awaiting duration input", "Enter a duration string and parse it into plain English.", tone="neutral")

    if parse_result is not None:
        with tool_result_panel("iso8601_parse_result_panel", related_to="iso8601_duration"):
            render_section_heading("In plain English", eyebrow="Result")
            if not parse_result["ok"]:
                render_failure_note(
                    "ISO 8601 parse",
                    parse_result["error"],
                    remediation="Enter a valid ISO 8601 duration string (for example, PT15M) and parse again.",
                )
            else:
                st.code(parse_result["output"], language=None)
                render_status_note(
                    "Parsed successfully",
                    f"Duration parsed to plain-English units: {parse_result['output']}.",
                    tone="success",
                )

with build_tab:
    with tool_form_panel("iso8601_build"):
        render_form_intro("Enter individual duration units", "")
        with st.form("iso8601-build-form"):
            st.markdown('<div class="tool-panel-eyebrow">Date units</div>', unsafe_allow_html=True)
            years = st.number_input("Years", min_value=0.0, value=0.0, step=1.0)
            months = st.number_input("Months", min_value=0.0, value=0.0, step=1.0)
            weeks = st.number_input("Weeks", min_value=0.0, value=0.0, step=1.0)
            days = st.number_input("Days", min_value=0.0, value=0.0, step=1.0)
            st.markdown('<div class="tool-panel-eyebrow">Time units</div>', unsafe_allow_html=True)
            hours = st.number_input("Hours", min_value=0.0, value=0.0, step=1.0)
            minutes = st.number_input("Minutes", min_value=0.0, value=0.0, step=1.0)
            seconds = st.number_input("Seconds", min_value=0.0, value=0.0, step=1.0)
            build_submitted = st.form_submit_button("Build", use_container_width=True)

    if build_submitted:
        st.session_state["iso8601_build_result"] = build_duration(years, months, weeks, days, hours, minutes, seconds)

    build_result = st.session_state.get("iso8601_build_result")

    if build_result is None:
        render_empty_state("Ready to build", "The ISO 8601 duration string appears here.")
        render_status_note("Awaiting duration units", "Fill one or more units and build the ISO 8601 duration.", tone="neutral")

    if build_result is not None:
        with tool_result_panel("iso8601_build_result_panel", related_to="iso8601_duration"):
            render_section_heading("ISO 8601 duration", eyebrow="Result")
            if not build_result["ok"]:
                render_failure_note(
                    "ISO 8601 build",
                    build_result["error"],
                    remediation="Provide one or more non-negative duration units, then build again.",
                )
            else:
                st.code(build_result["output"], language=None)
                render_status_note(
                    "Built successfully",
                    f"Generated duration string: {build_result['output']}",
                    tone="success",
                )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
