from __future__ import annotations

import streamlit as st

from utils.timezone_abbreviation_reference import search_timezone_abbreviations
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Timezone Abbreviation Reference", layout="wide")
apply_app_shell(active_page="Timezone Abbreviation Reference")


render_page_header(
    "Timezone Abbreviation Reference",
    "Look up timezone abbreviations (EST, IST, CST...) and their UTC offset.",
    warning="Many abbreviations are genuinely ambiguous -- e.g. \"CST\" and \"IST\" each have multiple real-world meanings at different UTC offsets. Every meaning is listed as its own row rather than picking one.",
)

with tool_form_panel("timezone_abbreviation_reference"):
    render_form_intro("Search abbreviations", "Search by abbreviation, offset, or full name.")
    query = st.text_input("Search", placeholder="CST, UTC+05:30, pacific...")

results = search_timezone_abbreviations(query)
with tool_result_panel("timezone_abbreviation_reference_result", related_to="timezone_abbreviation_reference"):
    render_section_heading("Timezone abbreviations", f"{len(results)} matching entr{'y' if len(results) == 1 else 'ies'}.")
    if results:
        st.table([{"Abbreviation": entry.abbreviation, "UTC offset": entry.utc_offset, "Name": entry.name} for entry in results])
    else:
        st.info("No timezone abbreviations matched that search.")
