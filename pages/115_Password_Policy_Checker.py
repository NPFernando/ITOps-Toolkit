from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.password_policy_checker import MAX_INPUT_LENGTH, check_password_policy
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


_baseline = start_page_baseline("Password Policy Checker")
st.set_page_config(page_title="Password Policy Checker", layout="wide")
apply_app_shell(active_page="Password Policy Checker")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Password Policy Checker",
    "Check a password against a configurable complexity policy -- pass/fail per rule, not an entropy estimate.",
    warning="Generated/typed values are never transmitted or stored. Checked entirely in your current session.",
)

with tool_form_panel("password_policy_checker"):
    render_form_intro("Enter a password and choose the policy", "")
    with st.form("password-policy-form"):
        password_input = st.text_input("Password", type="password", max_chars=MAX_INPUT_LENGTH)
        min_length = st.slider("Minimum length", 1, 64, 12)
        st.markdown('<div class="tool-panel-eyebrow">Character rules</div>', unsafe_allow_html=True)
        require_upper = st.checkbox("Uppercase", value=True)
        require_lower = st.checkbox("Lowercase", value=True)
        require_digit = st.checkbox("Digit", value=True)
        require_symbol = st.checkbox("Symbol", value=True)
        disallow_whitespace = st.checkbox("No whitespace", value=True)
        submitted = st.form_submit_button("Check", use_container_width=True)

if submitted:
    st.session_state["password_policy_result"] = check_password_policy(
        password_input, min_length, require_upper, require_lower, require_digit, require_symbol, disallow_whitespace
    )

result = st.session_state.get("password_policy_result")

if result is None:
    render_empty_state("Ready to check", "Pass/fail for each policy rule appears here.")
    render_status_note("Awaiting password input", "Enter a password and run the policy check.", tone="neutral")

if result is not None:
    with tool_result_panel("password_policy_result_panel", related_to="password_policy_checker"):
        render_section_heading("Policy check", eyebrow="Result")
        if not result["ok"]:
            render_failure_note(
                "Password policy check",
                result["error"],
                remediation="Enter a password and valid policy settings, then run the check again.",
            )
        else:
            if result["compliant"]:
                render_status_note("Compliant", "The password satisfies every selected policy rule.", tone="success")
            else:
                failed_rule_count = sum(1 for rule in result["rules"] if not rule["passed"])
                render_status_note(
                    "Not compliant",
                    f"{failed_rule_count} rule(s) failed. Review each rule and adjust the password or policy settings.",
                    tone="warning",
                )
            st.table(
                [{"Outcome": "Pass" if rule["passed"] else "Fail", "Rule": rule["rule"]} for rule in result["rules"]]
            )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
