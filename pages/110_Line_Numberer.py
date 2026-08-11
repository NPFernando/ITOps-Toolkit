from __future__ import annotations

import streamlit as st

from utils.line_numberer import MAX_INPUT_LENGTH, add_line_numbers
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Line Numberer", layout="wide")
apply_app_shell(active_page="Line Numberer")


render_page_header(
    "Line Numberer",
    "Add line numbers to pasted text -- handy for referencing a specific line in a review or bug report.",
)

with tool_form_panel("line_numberer"):
    render_form_intro("Paste text", "")
    with st.form("line-numberer-form"):
        text_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="line one\nline two\nline three")
        c1, c2 = st.columns(2)
        start_at = c1.number_input("Start at", min_value=0, value=1, step=1)
        separator = c2.text_input("Separator", value=": ")
        submitted = st.form_submit_button("Add line numbers")

if submitted:
    st.session_state["line_numberer_result"] = add_line_numbers(text_input, int(start_at), separator)

result = st.session_state.get("line_numberer_result")

if result is None:
    render_empty_state("Ready to number", "The numbered text appears here.")

if result is not None:
    with tool_result_panel("line_numberer_result_panel", related_to="line_numberer"):
        render_section_heading("Numbered text", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language=None)
