from __future__ import annotations

import streamlit as st

from utils.jwt_weak_secret import MAX_INPUT_LENGTH, check_weak_secret
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, render_status_note, tool_form_panel, tool_result_panel


st.set_page_config(page_title="JWT Weak-Secret Checker", layout="wide")
apply_app_shell(active_page="JWT Weak-Secret Checker")


render_page_header(
    "JWT Weak-Secret Checker",
    "Test a JWT's HMAC signature against a small built-in list of common weak secrets.",
    warning="Only test tokens you're authorized to inspect.",
)

render_status_note(
    "Not a brute-force tool",
    "This checks against a fixed, small (~20-entry) built-in list of common weak secrets -- it catches the \"tutorial default secret left in prod\" class of mistake, not real cryptanalysis. A \"no match\" result is not proof the secret is strong.",
    tone="neutral",
)

with tool_form_panel("jwt_weak_secret"):
    render_form_intro("Enter a JWT", "Paste a token to check its signature against common weak secrets.")
    with st.form("jwt-weak-secret-form"):
        token = st.text_input("JWT", placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Check")

if submitted:
    st.session_state["jwt_weak_secret_result"] = check_weak_secret(token)

result = st.session_state.get("jwt_weak_secret_result")

if result is None:
    render_empty_state("Ready to check", "A match (or no match) against the built-in weak-secret list appears here.")

if result is not None:
    with tool_result_panel("jwt_weak_secret_result_panel", related_to="jwt_weak_secret"):
        render_section_heading("Result", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        elif result["alg_status"] == "missing":
            st.warning("This token's header has no usable 'alg' value -- the algorithm can't be determined.")
        elif result["alg_status"] == "unsigned":
            st.error("This token uses alg=\"none\" -- it is UNSIGNED and can be trivially forged. If any verifier accepts this token as-is, that is a critical misconfiguration.")
        elif result["alg_status"] == "asymmetric":
            st.info(f"Algorithm '{result['algorithm']}' is asymmetric -- there's no shared secret to check.")
        elif result["matched_secret"] is not None:
            st.error(f"Weak secret found: '{result['matched_secret']}'. This token's signature can be forged.")
        else:
            st.success("No match from this small built-in list -- not proof the secret is strong.")
