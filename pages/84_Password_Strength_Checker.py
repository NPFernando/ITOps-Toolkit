from __future__ import annotations

import streamlit as st

from utils.password_entropy import MAX_INPUT_LENGTH, estimate_entropy
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, render_status_note, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Password Strength Checker", layout="wide")
apply_app_shell(active_page="Password Strength Checker")


render_page_header(
    "Password Strength Checker",
    "Paste a password to see an estimated entropy and rough strength category.",
    warning="Do not paste a password you actually use anywhere.",
)

render_status_note(
    "Character-pool estimate, not a cracking-time model",
    "This measures entropy from character-set diversity and length only. It does not check against known-common passwords, dictionary words, or predictable patterns (e.g. \"P@ssw0rd1\" scores well here despite being a common, easily-guessed password). Treat a high score as a lower bound, not a guarantee.",
    tone="neutral",
)

with tool_form_panel("password_entropy"):
    render_form_intro("Enter a password", "Checked locally in your session -- never sent anywhere or stored.")
    with st.form("password-entropy-form"):
        password_input = st.text_input("Password", type="password", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Check")

if submitted:
    st.session_state["password_entropy_result"] = estimate_entropy(password_input)

result = st.session_state.get("password_entropy_result")

if result is None:
    render_empty_state("Ready to check", "Estimated entropy and strength category appear here.")

if result is not None:
    with tool_result_panel("password_entropy_result_panel", related_to="password_entropy"):
        render_section_heading("Result", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Entropy (bits)", result["entropy_bits"])
            c2.metric("Strength", result["strength_label"])
            st.caption(f"Character pool size: {result['pool_size']}")
