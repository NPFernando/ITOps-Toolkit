from __future__ import annotations

import streamlit as st

from utils.line_sorter import MAX_INPUT_LENGTH, SORT_MODES, sort_and_dedupe_lines
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Sort & Dedupe Lines", layout="wide")
apply_app_shell(active_page="Sort & Dedupe Lines")


render_page_header(
    "Sort & Dedupe Lines",
    "Paste text and sort its lines, remove duplicates, and/or drop blank lines -- like sort -u over pasted text.",
)

with tool_form_panel("line_sorter"):
    render_form_intro("Paste text", "One item per line.")
    with st.form("line-sorter-form"):
        text_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="banana\napple\napple\ncherry")
        sort_mode = st.selectbox("Sort", SORT_MODES)
        c1, c2, c3 = st.columns(3)
        dedupe = c1.checkbox("Remove duplicates", value=True)
        case_insensitive = c2.checkbox("Case-insensitive", value=False)
        remove_blank = c3.checkbox("Remove blank lines", value=True)
        submitted = st.form_submit_button("Process")

if submitted:
    st.session_state["line_sorter_result"] = sort_and_dedupe_lines(text_input, sort_mode, dedupe, case_insensitive, remove_blank)

result = st.session_state.get("line_sorter_result")

if result is None:
    render_empty_state("Ready to process", "The cleaned/sorted lines appear here.")

if result is not None:
    with tool_result_panel("line_sorter_result_panel", related_to="line_sorter"):
        render_section_heading("Result", eyebrow="Output")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Lines", result["line_count"])
            c2.metric("Removed", result["removed_count"])
            st.code(result["output"], language=None)
            st.download_button("Download as .txt", result["output"], file_name="lines.txt", mime="text/plain")
