from __future__ import annotations

import streamlit as st

from utils.xml_formatter import MAX_INPUT_LENGTH, format_xml
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="XML Formatter", layout="wide")
apply_app_shell(active_page="XML Formatter")


render_page_header(
    "XML Formatter",
    "Pretty-print, minify, or validate arbitrary XML.",
)

with tool_form_panel("xml_formatter"):
    render_form_intro("Process XML", "Paste XML and choose an action.")
    with st.form("xml-formatter-form"):
        xml_input = st.text_area("XML input", height=260, max_chars=MAX_INPUT_LENGTH, placeholder="<root><item>value</item></root>")
        action = st.radio("Action", ["Format XML", "Minify XML", "Validate XML"], horizontal=True)
        submitted = st.form_submit_button("Run")
        format_clicked = submitted and action == "Format XML"
        minify_clicked = submitted and action == "Minify XML"
        validate_clicked = submitted and action == "Validate XML"

if format_clicked:
    st.session_state["xml_formatter_state"] = {"action": "Format XML", "result": format_xml(xml_input, minify=False)}
if minify_clicked:
    st.session_state["xml_formatter_state"] = {"action": "Minify XML", "result": format_xml(xml_input, minify=True)}
if validate_clicked:
    st.session_state["xml_formatter_state"] = {"action": "Validate XML", "result": format_xml(xml_input, minify=True)}

state = st.session_state.get("xml_formatter_state")

if state is None:
    render_empty_state("Ready to process", "Formatted, minified, or validation output appears here.")

if state is not None:
    result = state["result"]
    with tool_result_panel("xml_formatter_result_panel", related_to="xml_formatter"):
        render_section_heading(state["action"], eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        elif state["action"] == "Validate XML":
            st.success("Valid XML.")
        else:
            st.code(result["output"], language="xml")
