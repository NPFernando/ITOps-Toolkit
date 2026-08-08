from __future__ import annotations

import streamlit as st

from utils.password_tools import (
    MAX_LENGTH,
    MAX_WORDS,
    MIN_LENGTH,
    MIN_WORDS,
    WORDLIST,
    generate_passphrase,
    generate_password,
)
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Password Generator", layout="wide")
apply_app_shell(active_page="Password Generator")


render_page_header(
    "Password Generator",
    "Generate a strong random password or a diceware-style passphrase, entirely in your current session.",
    warning="Generated values are shown once and never transmitted or stored. Copy them somewhere safe.",
)

with tool_form_panel("password_generator"):
    render_form_intro("Choose a style", "Generate a random-character password or a word-based passphrase.")
    with st.form("password-form"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Password**")
            length = st.slider("Length", MIN_LENGTH, MAX_LENGTH, 20)
            use_upper = st.checkbox("Uppercase (A-Z)", value=True)
            use_lower = st.checkbox("Lowercase (a-z)", value=True)
            use_digits = st.checkbox("Digits (0-9)", value=True)
            use_symbols = st.checkbox("Symbols (!@#$...)", value=True)
            exclude_ambiguous = st.checkbox("Exclude ambiguous characters (I l 1 O 0)", value=False)
            password_clicked = st.form_submit_button("Generate password")
        with c2:
            st.markdown("**Passphrase**")
            word_count = st.slider("Word count", MIN_WORDS, MAX_WORDS, 4)
            separator = st.text_input("Separator", value="-", max_chars=5)
            capitalize = st.checkbox("Capitalize each word", value=True)
            include_number = st.checkbox("Append a random number", value=True)
            passphrase_clicked = st.form_submit_button("Generate passphrase")

if password_clicked:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns the transient
    # *_clicked flags are False again, which would otherwise collapse this whole
    # results section the instant any of them is touched.
    st.session_state["password_generator_password_result"] = generate_password(
        length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous
    )
if passphrase_clicked:
    st.session_state["password_generator_passphrase_result"] = generate_passphrase(word_count, separator, capitalize, include_number)

password_result = st.session_state.get("password_generator_password_result")
passphrase_result = st.session_state.get("password_generator_passphrase_result")

if password_result is None and passphrase_result is None:
    render_empty_state("Ready to generate", "A password or passphrase appears here after you generate one.")

if password_result is not None:
    with tool_result_panel("password_result", related_to="password_generator"):
        render_section_heading("Generated password", "Copy this now -- it is not stored or logged.")
        if not password_result["ok"]:
            st.error(password_result["error"])
        else:
            st.code(password_result["password"], language=None)
            st.caption(f"~{password_result['entropy_bits']} bits of entropy from a {password_result['pool_size']}-character set.")

if passphrase_result is not None:
    with tool_result_panel("passphrase_result", related_to="password_generator"):
        render_section_heading("Generated passphrase", "Copy this now -- it is not stored or logged.")
        if not passphrase_result["ok"]:
            st.error(passphrase_result["error"])
        else:
            st.code(passphrase_result["passphrase"], language=None)
            st.caption(f"~{passphrase_result['entropy_bits']} bits of entropy from a {len(WORDLIST)}-word list.")
