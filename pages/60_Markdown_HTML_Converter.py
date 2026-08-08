from __future__ import annotations

import streamlit as st

from utils.markdown_converter import DIRECTIONS, MAX_INPUT_LENGTH, convert_markdown
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Markdown/HTML Converter", layout="wide")
apply_app_shell(active_page="Markdown/HTML Converter")


render_page_header(
    "Markdown/HTML Converter",
    "Convert text between Markdown and HTML.",
)

with tool_form_panel("markdown_converter"):
    render_form_intro("Convert", "Paste text and choose a direction.")
    with st.form("markdown-converter-form"):
        direction = st.selectbox("Direction", DIRECTIONS, index=0)
        text = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Convert")

if submitted:
    # Stored in session_state (not rendered directly here) because the
    # download button below triggers its own rerun -- on that rerun
    # `submitted` is False again, which would otherwise collapse this whole
    # results section right after the click.
    st.session_state["markdown_converter_state"] = {
        "result": convert_markdown(text, direction),
        "direction": direction,
    }

state = st.session_state.get("markdown_converter_state")

if state is None:
    render_empty_state("Ready to convert", "The converted output appears here after conversion.")

if state is not None:
    result = state["result"]
    direction = state["direction"]
    with tool_result_panel("markdown_converter_result", related_to="markdown_converter"):
        render_section_heading(direction, "Converted output.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            output_language = "html" if direction == "Markdown to HTML" else "markdown"
            output_extension = "html" if direction == "Markdown to HTML" else "md"
            st.code(result["output"], language=output_language)
            st.download_button(
                f"Download as .{output_extension}",
                result["output"],
                file_name=f"converted.{output_extension}",
                mime="text/plain",
            )
