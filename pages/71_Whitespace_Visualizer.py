from __future__ import annotations

import streamlit as st

from utils.whitespace_visualizer import MAX_INPUT_LENGTH, visualize_whitespace
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Whitespace Visualizer", layout="wide")
apply_app_shell(active_page="Whitespace Visualizer")


render_page_header(
    "Whitespace Visualizer",
    "Paste text to find non-breaking spaces, zero-width characters, and other invisible characters that commonly cause silent copy-paste bugs.",
)

with tool_form_panel("whitespace_visualizer"):
    render_form_intro("Paste text", "Any pasted text -- a config value, a line of code, a paragraph.")
    with st.form("whitespace-visualizer-form"):
        text_input = st.text_area("Text", height=220, max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Check")

if submitted:
    st.session_state["whitespace_visualizer_result"] = visualize_whitespace(text_input)

result = st.session_state.get("whitespace_visualizer_result")

if result is None:
    render_empty_state("Ready to check", "Flagged invisible characters, with their line/column position, appear here.")

if result is not None:
    with tool_result_panel("whitespace_visualizer_result_panel", related_to="whitespace_visualizer"):
        render_section_heading("Result", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        elif not result["findings"]:
            st.success("No invisible or lookalike characters found.")
        else:
            st.warning(f"{len(result['findings'])} character(s) flagged:")
            st.table([{"Line": f["line"], "Column": f["column"], "Codepoint": f["codepoint"], "Name": f["name"]} for f in result["findings"]])
            st.caption("Annotated text (flagged characters shown as [NAME]):")
            st.code(result["annotated_text"])
