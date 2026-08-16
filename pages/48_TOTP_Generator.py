from __future__ import annotations

import streamlit as st

from utils.totp_tools import MAX_CODE_LENGTH, MAX_SECRET_LENGTH, current_code, generate_secret, verify_code
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="TOTP Generator", layout="wide")
apply_app_shell(active_page="TOTP Generator")


render_page_header(
    "TOTP Generator",
    "Generate and validate time-based one-time passcodes (TOTP) from a shared secret -- useful for testing MFA setups.",
    warning="Only use secrets you own or are authorized to test. Nothing entered here is stored.",
)

generate_tab, verify_tab = st.tabs(["Generate a code", "Verify a code"])

with generate_tab:
    with tool_form_panel("totp_generate"):
        render_form_intro("Enter or generate a secret", "Paste a base32 secret, or generate a new random one to test with.")
        if st.button("Generate a new random secret"):
            st.session_state["totp_secret_input"] = generate_secret()
        secret = st.text_input("Base32 secret", key="totp_secret_input", max_chars=MAX_SECRET_LENGTH, placeholder="JBSWY3DPEHPK3PXP")

    with tool_result_panel("totp_generate_result", related_to="totp_generator"):
        render_section_heading("Current code", "Regenerates automatically when the page reruns; refresh to get a new code near the end of the window.")
        if not secret.strip():
            render_empty_state("Ready for a secret", "The current code appears here as soon as you enter or generate a secret.")
        else:
            result = current_code(secret)
            if not result["ok"]:
                st.error(result["error"])
            else:
                c1, c2 = st.columns(2)
                c1.metric("Code", result["code"])
                c2.metric("Seconds remaining", result["seconds_remaining"])

with verify_tab:
    with tool_form_panel("totp_verify"):
        render_form_intro("Verify a code", "Check a 6-digit code against a secret, tolerating one 30-second window of clock drift.")
        with st.form("totp-verify-form"):
            verify_secret = st.text_input("Base32 secret", max_chars=MAX_SECRET_LENGTH, key="totp_verify_secret")
            verify_code_input = st.text_input("Code to verify", max_chars=MAX_CODE_LENGTH, placeholder="123456")
            submitted = st.form_submit_button("Verify")

    if submitted:
        st.session_state["totp_verify_result"] = verify_code(verify_secret, verify_code_input)

    verify_result = st.session_state.get("totp_verify_result")
    if verify_result is None:
        render_empty_state("Ready to verify", "The verification result appears here after you check a code.")
    if verify_result is not None:
        with tool_result_panel("totp_verify_result_panel", related_to="totp_generator"):
            if not verify_result["ok"]:
                render_failure_note(
                    "Verification input",
                    verify_result["error"],
                    remediation="Use a valid Base32 secret and a 6-digit code, then retry.",
                )
            elif verify_result["valid"]:
                render_status_note("Valid", "The code matches the secret within the allowed time window.", tone="success")
            else:
                render_status_note("Invalid", "The code does not match the secret.", tone="warning")
