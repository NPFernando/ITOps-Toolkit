from __future__ import annotations

import streamlit as st

from utils.password_policy_checker import MAX_INPUT_LENGTH, check_password_policy
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Password Policy Checker", layout="wide")
apply_app_shell(active_page="Password Policy Checker")


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
        c1, c2, c3, c4, c5 = st.columns(5)
        require_upper = c1.checkbox("Uppercase", value=True)
        require_lower = c2.checkbox("Lowercase", value=True)
        require_digit = c3.checkbox("Digit", value=True)
        require_symbol = c4.checkbox("Symbol", value=True)
        disallow_whitespace = c5.checkbox("No whitespace", value=True)
        submitted = st.form_submit_button("Check")

if submitted:
    st.session_state["password_policy_result"] = check_password_policy(
        password_input, min_length, require_upper, require_lower, require_digit, require_symbol, disallow_whitespace
    )

result = st.session_state.get("password_policy_result")

if result is None:
    render_empty_state("Ready to check", "Pass/fail for each policy rule appears here.")

if result is not None:
    with tool_result_panel("password_policy_result_panel", related_to="password_policy_checker"):
        render_section_heading("Policy check", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            if result["compliant"]:
                st.success("Meets the policy.")
            else:
                st.error("Does not meet the policy.")
            for rule in result["rules"]:
                st.markdown(f"**{'Pass' if rule['passed'] else 'Fail'}** -- {rule['rule']}")
