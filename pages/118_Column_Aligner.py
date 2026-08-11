from __future__ import annotations

import streamlit as st

from utils.column_aligner import MAX_INPUT_LENGTH, align_columns
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Column Aligner", layout="wide")
apply_app_shell(active_page="Column Aligner")


render_page_header(
    "Column Aligner",
    "Align whitespace-separated columns of plain text -- like the Unix column -t command. Handy for tidying up pasted command output.",
)

with tool_form_panel("column_aligner"):
    render_form_intro("Paste columnar text", "Leave the delimiter blank to split on any run of whitespace.")
    with st.form("column-aligner-form"):
        text_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="USER PID CPU\nroot 1 0.0\nwww-data 1234 12.5")
        delimiter_input = st.text_input("Delimiter (optional)", placeholder="e.g. , or |")
        submitted = st.form_submit_button("Align")

if submitted:
    st.session_state["column_aligner_result"] = align_columns(text_input, delimiter_input)

result = st.session_state.get("column_aligner_result")

if result is None:
    render_empty_state("Ready to align", "The aligned columns appear here.")

if result is not None:
    with tool_result_panel("column_aligner_result_panel", related_to="column_aligner"):
        render_section_heading("Aligned output", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language=None)
