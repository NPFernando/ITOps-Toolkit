from __future__ import annotations

import streamlit as st

from utils.line_ending_converter import MAX_INPUT_LENGTH, convert_line_endings
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Line Ending Converter", layout="wide")
apply_app_shell(active_page="Line Ending Converter")


render_page_header(
    "Line Ending Converter",
    "Convert pasted text between CRLF (Windows), LF (Unix/Mac), and CR (classic Mac) line endings.",
)

with tool_form_panel("line_ending_converter"):
    render_form_intro("Paste text", "Choose which line ending to convert to.")
    with st.form("line-ending-converter-form"):
        text_input = st.text_area("Input", height=220, max_chars=MAX_INPUT_LENGTH)
        c1, c2, c3 = st.columns(3)
        with c1:
            crlf_clicked = st.form_submit_button("Convert to CRLF")
        with c2:
            lf_clicked = st.form_submit_button("Convert to LF")
        with c3:
            cr_clicked = st.form_submit_button("Convert to CR")

if crlf_clicked:
    st.session_state["line_ending_converter_result"] = convert_line_endings(text_input, "CRLF")
if lf_clicked:
    st.session_state["line_ending_converter_result"] = convert_line_endings(text_input, "LF")
if cr_clicked:
    st.session_state["line_ending_converter_result"] = convert_line_endings(text_input, "CR")

result = st.session_state.get("line_ending_converter_result")

if result is None:
    render_empty_state("Ready to convert", "The converted text appears here.")

if result is not None:
    with tool_result_panel("line_ending_converter_result_panel", related_to="line_ending_converter"):
        render_section_heading("Converted text", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.caption(f"Detected input style: {result['detected_input_style']}")
            st.text_area("Result", value=result["output"], height=220)
