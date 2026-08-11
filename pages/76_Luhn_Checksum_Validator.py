from __future__ import annotations

import streamlit as st

from utils.luhn_validator import MAX_INPUT_LENGTH, validate_luhn
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Luhn Checksum Validator", layout="wide")
apply_app_shell(active_page="Luhn Checksum Validator")


render_page_header(
    "Luhn Checksum Validator",
    "Validate a credit card number, IMEI, or other Luhn-checksummed number, and see the check digit for its payload.",
)

with tool_form_panel("luhn_validator"):
    render_form_intro("Enter a number", "Spaces and hyphens are ignored.")
    with st.form("luhn-validator-form"):
        number_input = st.text_input("Number", placeholder="4532 0151 1283 0366", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Validate")

if submitted:
    st.session_state["luhn_validator_result"] = validate_luhn(number_input)

result = st.session_state.get("luhn_validator_result")

if result is None:
    render_empty_state("Ready to validate", "Validity and the computed check digit appear here.")

if result is not None:
    with tool_result_panel("luhn_validator_result_panel", related_to="luhn_validator"):
        render_section_heading("Result", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Luhn valid", "Yes" if result["is_valid"] else "No")
            c2.metric("Check digit for payload", result["check_digit"])
            st.caption(f"Digits: {result['digits_only']}")
