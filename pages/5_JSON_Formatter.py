from __future__ import annotations

import streamlit as st

from utils.text_tools import MAX_JSON_LENGTH, format_json_text
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_download_panel,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="JSON Formatter", layout="wide")
apply_app_shell(active_page="JSON Formatter")


render_page_header(
    "JSON Formatter",
    "Validate, format, minify, and download JSON.",
    warning="Do not paste secrets, production tokens, or sensitive customer data.",
)

with tool_form_panel("json_formatter"):
    render_form_intro("Process JSON", "Validate syntax, pretty-print JSON, or minify it for compact transport.")
    with st.form("json-form"):
        json_input = st.text_area("JSON input", height=260, max_chars=MAX_JSON_LENGTH, placeholder='{"status": "ok"}')
        action = st.radio("Action", ["Validate JSON", "Format JSON", "Minify JSON"], horizontal=True)
        action_submitted = st.form_submit_button("Run JSON action")
        validate_clicked = action_submitted and action == "Validate JSON"
        format_clicked = action_submitted and action == "Format JSON"
        minify_clicked = action_submitted and action == "Minify JSON"

if not (validate_clicked or format_clicked or minify_clicked):
    render_empty_state("Ready to process JSON", "Validation status and formatted output appear here after you run an action.")

if validate_clicked or format_clicked or minify_clicked:
    result = format_json_text(json_input, minify=minify_clicked)
    with tool_result_panel("json_result"):
        render_section_heading("JSON result", "Validation status and transformed output.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.success("Valid JSON")
            if format_clicked or minify_clicked:
                st.text_area("Result", value=result["result"], height=320)
                file_name = "formatted.json" if format_clicked else "minified.json"
                with tool_download_panel("json_export"):
                    render_section_heading("Export", "Download the current in-memory JSON result.", eyebrow="Downloads")
                    st.download_button(
                        "Download JSON",
                        result["result"],
                        file_name=file_name,
                        mime="application/json",
                    )
