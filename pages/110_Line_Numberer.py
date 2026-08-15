from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.line_numberer import MAX_INPUT_LENGTH, add_line_numbers
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


_baseline = start_page_baseline("Line Numberer")
st.set_page_config(page_title="Line Numberer", layout="wide")
apply_app_shell(active_page="Line Numberer")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Line Numberer",
    "Add line numbers to pasted text -- handy for referencing a specific line in a review or bug report.",
)

with tool_form_panel("line_numberer"):
    render_form_intro("Paste text", "")
    with st.form("line-numberer-form"):
        text_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="line one\nline two\nline three")
        start_at = st.number_input("Start at", min_value=0, value=1, step=1)
        separator = st.text_input("Separator", value=": ")
        submitted = st.form_submit_button("Add line numbers", use_container_width=True)

if submitted:
    st.session_state["line_numberer_result"] = add_line_numbers(text_input, int(start_at), separator)

result = st.session_state.get("line_numberer_result")

if result is None:
    render_empty_state("Ready to number", "The numbered text appears here.")
    render_status_note("Awaiting text input", "Paste text and select Add line numbers.", tone="neutral")

if result is not None:
    with tool_result_panel("line_numberer_result_panel", related_to="line_numberer"):
        render_section_heading("Numbered text", eyebrow="Result")
        if not result["ok"]:
            render_failure_note(
                "Line numbering",
                result["error"],
                remediation="Paste text input and retry numbering.",
            )
        else:
            render_status_note("Numbering complete", "Numbered text is ready to copy.", tone="success")
            st.code(result["output"], language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
