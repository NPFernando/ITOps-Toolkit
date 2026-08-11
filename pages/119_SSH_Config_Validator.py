from __future__ import annotations

import streamlit as st

from utils.ssh_config_validator import MAX_INPUT_LENGTH, lint_ssh_config
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="SSH Config Validator", layout="wide")
apply_app_shell(active_page="SSH Config Validator")


render_page_header(
    "SSH Config Validator",
    "Lint ~/.ssh/config content for structural mistakes -- directives before any Host block, empty Host blocks, duplicate Host patterns.",
    warning="Checks structure only, not individual directive names -- OpenSSH has ~100 valid ssh_config keywords, and an incomplete allowlist would flag valid but less common ones as errors.",
)

with tool_form_panel("ssh_config_validator"):
    render_form_intro("Paste ~/.ssh/config content", "")
    with st.form("ssh-config-validator-form"):
        config_input = st.text_area("Config", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="Host prod\n    HostName 1.2.3.4\n    User admin")
        submitted = st.form_submit_button("Lint")

if submitted:
    st.session_state["ssh_config_validator_result"] = lint_ssh_config(config_input)

result = st.session_state.get("ssh_config_validator_result")

if result is None:
    render_empty_state("Ready to lint", "Any structural issues appear here.")

if result is not None:
    with tool_result_panel("ssh_config_validator_result_panel", related_to="ssh_config_validator"):
        render_section_heading("Lint results", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        elif not result["issues"]:
            st.success("No structural issues found.")
        else:
            st.table([{"Line": issue["line"], "Issue": issue["message"]} for issue in result["issues"]])
