from __future__ import annotations

import streamlit as st

from utils.timestamp_tools import (
    COMMON_TIMEZONES,
    EPOCH_UNITS,
    convert_timezone,
    datetime_to_epoch,
    epoch_to_datetime,
    now_timestamp,
)
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Timestamp Converter", layout="wide")
apply_app_shell(active_page="Timestamp Converter")


render_page_header(
    "Timestamp Converter",
    "Convert between Unix epoch, ISO 8601, and human-readable timestamps across timezones.",
)

now = now_timestamp("UTC")
with tool_result_panel("timestamp_now"):
    render_section_heading("Right now (UTC)", eyebrow="Reference")
    if now["ok"]:
        c1, c2 = st.columns(2)
        c1.metric("Epoch seconds", now["epoch_seconds"])
        c2.metric("ISO 8601", now["display"])
    else:
        st.error(now["error"] or "Could not read the current UTC timestamp.")

with tool_form_panel("epoch_to_date"):
    render_form_intro("Epoch to date", "Convert a Unix epoch value to a readable date and time.")
    with st.form("epoch-to-date-form"):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            epoch_input = st.text_input("Epoch value", placeholder="1735689600")
        with c2:
            unit = st.selectbox("Unit", EPOCH_UNITS)
        with c3:
            tz_a = st.selectbox("Timezone", COMMON_TIMEZONES, key="tz_a")
        epoch_submitted = st.form_submit_button("Convert epoch")

if epoch_submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `epoch_submitted`
    # is False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["timestamp_converter_epoch_result"] = epoch_to_datetime(epoch_input, unit, tz_a)

epoch_result = st.session_state.get("timestamp_converter_epoch_result")
if epoch_result is None:
    render_empty_state("Ready to convert epoch", "The readable date and time appear here after you convert an epoch value.")
if epoch_result is not None:
    result = epoch_result
    with tool_result_panel("epoch_result", related_to="timestamp_converter"):
        render_section_heading("Converted date", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.text_input("Display", value=result["display"], disabled=True)
            c2.text_input("ISO 8601", value=result["iso"], disabled=True)

with tool_form_panel("date_to_epoch"):
    render_form_intro("Date to epoch", "Convert a date/time value to its Unix epoch.")
    with st.form("date-to-epoch-form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            date_input = st.text_input("Date/time (ISO 8601)", placeholder="2026-08-05T14:30:00")
        with c2:
            tz_b = st.selectbox("Timezone", COMMON_TIMEZONES, key="tz_b")
        date_submitted = st.form_submit_button("Convert date/time")

if date_submitted:
    st.session_state["timestamp_converter_date_result"] = datetime_to_epoch(date_input, tz_b)

date_result = st.session_state.get("timestamp_converter_date_result")
if date_result is None:
    render_empty_state("Ready to convert date/time", "The Unix epoch appears here after you convert a date/time value.")
if date_result is not None:
    result = date_result
    with tool_result_panel("date_result", related_to="timestamp_converter"):
        render_section_heading("Converted epoch", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.text_input("Epoch seconds", value=str(result["epoch_seconds"]), disabled=True)
            c2.text_input("Epoch milliseconds", value=str(result["epoch_milliseconds"]), disabled=True)

with tool_form_panel("timezone_convert"):
    render_form_intro("Convert between timezones", "Reinterpret a date/time from one timezone into another.")
    with st.form("timezone-convert-form"):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            tz_date_input = st.text_input("Date/time (ISO 8601)", placeholder="2026-08-05T14:30:00", key="tz_date")
        with c2:
            tz_from = st.selectbox("From timezone", COMMON_TIMEZONES, key="tz_from")
        with c3:
            tz_to = st.selectbox("To timezone", COMMON_TIMEZONES, key="tz_to")
        tz_submitted = st.form_submit_button("Convert timezones")

if tz_submitted:
    st.session_state["timestamp_converter_timezone_result"] = convert_timezone(tz_date_input, tz_from, tz_to)

timezone_result = st.session_state.get("timestamp_converter_timezone_result")
if timezone_result is None:
    render_empty_state("Ready to convert timezones", "The reinterpreted date/time appears here after you convert between timezones.")
if timezone_result is not None:
    result = timezone_result
    with tool_result_panel("timezone_result", related_to="timestamp_converter"):
        render_section_heading("Converted time", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.text_input("Display", value=result["display"], disabled=True)
