from __future__ import annotations

import streamlit as st

from utils.yaml_formatter import MAX_INPUT_LENGTH, format_yaml
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="YAML Formatter", layout="wide")
apply_app_shell(active_page="YAML Formatter")


render_page_header(
    "YAML Formatter",
    "Paste YAML and get it consistently re-indented, or flagged with a clear error if it's not valid YAML.",
)

with tool_form_panel("yaml_formatter"):
    render_form_intro("Paste YAML", "Any valid YAML document.")
    with st.form("yaml-formatter-form"):
        yaml_input = st.text_area("YAML input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="key: value\nlist:\n  - a\n  - b")
        submitted = st.form_submit_button("Format")

if submitted:
    st.session_state["yaml_formatter_result"] = format_yaml(yaml_input)

result = st.session_state.get("yaml_formatter_result")

if result is None:
    render_empty_state("Ready to format", "The re-formatted YAML appears here.")

if result is not None:
    with tool_result_panel("yaml_formatter_result_panel", related_to="yaml_formatter"):
        render_section_heading("Formatted YAML", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="yaml")
