from __future__ import annotations

import streamlit as st

from utils.iban_validator import MAX_INPUT_LENGTH, validate_iban
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="IBAN Validator", layout="wide")
apply_app_shell(active_page="IBAN Validator")


render_page_header(
    "IBAN Validator",
    "Check an IBAN's structure (country-specific length) and mod-97 checksum.",
)

with tool_form_panel("iban_validator"):
    render_form_intro("Enter an IBAN", "Spaces are ignored.")
    with st.form("iban-validator-form"):
        iban_input = st.text_input("IBAN", placeholder="DE89 3704 0044 0532 0130 00", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Validate")

if submitted:
    st.session_state["iban_validator_result"] = validate_iban(iban_input)

result = st.session_state.get("iban_validator_result")

if result is None:
    render_empty_state("Ready to validate", "The validation result appears here.")

if result is not None:
    with tool_result_panel("iban_validator_result_panel", related_to="iban_validator"):
        render_section_heading("Result", eyebrow="Validation")
        if not result["ok"]:
            st.error(result["error"])
        elif result["valid"]:
            st.success(f"Valid IBAN -- {result['country']}: {result['formatted']}")
        else:
            st.error(f"Invalid checksum -- {result['country']}: {result['formatted']}")
