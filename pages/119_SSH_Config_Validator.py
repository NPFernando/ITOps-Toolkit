from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ssh_config_validator import MAX_INPUT_LENGTH, lint_ssh_config
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


_baseline = start_page_baseline("SSH Config Validator")
st.set_page_config(page_title="SSH Config Validator", layout="wide")
apply_app_shell(active_page="SSH Config Validator")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "SSH Config Validator",
    "Lint ~/.ssh/config content for structural mistakes -- directives before any Host block, empty Host blocks, duplicate Host patterns.",
    warning="Checks structure only, not individual directive names -- OpenSSH has ~100 valid ssh_config keywords, and an incomplete allowlist would flag valid but less common ones as errors.",
)

with tool_form_panel("ssh_config_validator"):
    render_form_intro("Paste ~/.ssh/config content", "Paste the full file to lint Host-block structure and ordering.")
    with st.form("ssh-config-validator-form"):
        st.markdown('<div class="tool-panel-eyebrow">SSH config content</div>', unsafe_allow_html=True)
        config_input = st.text_area("Config", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="Host prod\n    HostName 1.2.3.4\n    User admin")
        submitted = st.form_submit_button("Lint", use_container_width=True)

if submitted:
    st.session_state["ssh_config_validator_result"] = lint_ssh_config(config_input)

result = st.session_state.get("ssh_config_validator_result")

if result is None:
    render_empty_state("Ready to lint", "Any structural issues appear here.")
    render_status_note(
        "Ready for SSH config input",
        "No lint check has run yet. Paste ~/.ssh/config content, then select Lint.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("ssh_config_validator_result_panel", related_to="ssh_config_validator"):
        render_section_heading("Lint results", eyebrow="Result")
        if not result["ok"]:
            render_failure_note(
                "SSH config lint",
                result["error"],
                remediation="Fix malformed config content, then run Lint again.",
            )
        elif not result["issues"]:
            render_status_note(
                "SSH config structure looks valid",
                "Lint complete: no structural Host-block issues were detected.",
                tone="success",
            )
        else:
            render_status_note(
                "SSH config has structural issues",
                f"Lint found {len(result['issues'])} structural issue(s). Review each line item before using this config.",
                tone="warning",
            )
            st.table([{"Line": issue["line"], "Issue": issue["message"]} for issue in result["issues"]])

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
