from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.timestamp_tools import COMMON_TIMEZONES
from utils.world_clock import MAX_INPUT_LENGTH, world_clock
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="World Clock", layout="wide")
apply_app_shell(active_page="World Clock")


render_page_header(
    "World Clock",
    "Enter one date/time and see the equivalent local time across major world timezones -- useful for planning a meeting or a maintenance window.",
)

with tool_form_panel("world_clock"):
    render_form_intro("Enter a date/time and its timezone", "e.g. 2026-03-05T14:30")
    with st.form("world-clock-form"):
        c1, c2 = st.columns(2)
        value_input = c1.text_input("Date/time", placeholder="2026-03-05T14:30", max_chars=MAX_INPUT_LENGTH)
        tz_input = c2.selectbox("Source timezone", COMMON_TIMEZONES)
        submitted = st.form_submit_button("Show world clock")

if submitted:
    st.session_state["world_clock_result"] = world_clock(value_input, tz_input)

result = st.session_state.get("world_clock_result")

if result is None:
    render_empty_state("Ready to convert", "The time across major world timezones appears here.")

if result is not None:
    with tool_result_panel("world_clock_result_panel", related_to="world_clock"):
        render_section_heading("Local time by zone", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Timezone": z["zone"],
                            "Local time": z["local_time"],
                            "Day offset": z["day_offset"],
                        }
                        for z in result["zones"]
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
