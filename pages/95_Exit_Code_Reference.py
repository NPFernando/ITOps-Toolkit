from __future__ import annotations

import streamlit as st

from utils.exit_code_reference import search_exit_codes
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Exit Code Reference", layout="wide")
apply_app_shell(active_page="Exit Code Reference")


render_page_header(
    "Exit Code Reference",
    "Look up Linux/Bash process exit codes -- a quick lookup when a script or CI job fails with an unfamiliar code.",
)

with tool_form_panel("exit_code_reference"):
    render_form_intro("Search exit codes", "Search by code or keyword.")
    query = st.text_input("Search", placeholder="137, sigkill, permission...")

results = search_exit_codes(query)
with tool_result_panel("exit_code_reference_result", related_to="exit_code_reference"):
    render_section_heading("Exit codes", f"{len(results)} matching code(s).")
    if results:
        st.table([{"Code": entry.code, "Meaning": entry.meaning, "Detail": entry.detail} for entry in results])
    else:
        st.info("No exit codes matched that search.")
