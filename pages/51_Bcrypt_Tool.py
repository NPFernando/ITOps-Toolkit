from __future__ import annotations

import streamlit as st

from utils.bcrypt_tools import MAX_ROUNDS, MIN_ROUNDS, hash_password, verify_password
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


st.set_page_config(page_title="Bcrypt Tool", layout="wide")
apply_app_shell(active_page="Bcrypt Tool")


render_page_header(
    "Bcrypt Tool",
    "Hash a value with bcrypt, or verify a value against an existing bcrypt hash.",
    warning="Nothing entered here is stored. Higher round counts take noticeably longer -- start at 10-12 unless you need to test a specific cost factor.",
)

hash_tab, verify_tab = st.tabs(["Hash", "Verify"])

with hash_tab:
    with tool_form_panel("bcrypt_hash"):
        render_form_intro("Hash a value", "Choose a cost factor (rounds) -- higher is slower but more resistant to brute force.")
        with st.form("bcrypt-hash-form"):
            password = st.text_input("Value to hash", type="password")
            rounds = st.slider("Rounds", MIN_ROUNDS, MAX_ROUNDS, 12)
            hash_submitted = st.form_submit_button("Hash")

    if hash_submitted:
        with st.spinner("Hashing..."):
            st.session_state["bcrypt_hash_result"] = hash_password(password, rounds)

    hash_result = st.session_state.get("bcrypt_hash_result")
    if hash_result is None:
        render_empty_state("Ready to hash", "The bcrypt hash appears here after you hash a value.")
    if hash_result is not None:
        with tool_result_panel("bcrypt_hash_result_panel", related_to="bcrypt_tool"):
            render_section_heading("Result", "Bcrypt hash, including the embedded salt and cost factor.")
            if not hash_result["ok"]:
                st.error(hash_result["error"])
            else:
                st.code(hash_result["hash"], language=None)

with verify_tab:
    with tool_form_panel("bcrypt_verify"):
        render_form_intro("Verify a value", "Check a value against an existing bcrypt hash.")
        with st.form("bcrypt-verify-form"):
            verify_password_input = st.text_input("Value to verify", type="password", key="bcrypt_verify_password")
            existing_hash = st.text_input("Existing bcrypt hash", placeholder="$2b$12$...")
            verify_submitted = st.form_submit_button("Verify")

    if verify_submitted:
        st.session_state["bcrypt_verify_result"] = verify_password(verify_password_input, existing_hash)

    verify_result = st.session_state.get("bcrypt_verify_result")
    if verify_result is None:
        render_empty_state("Ready to verify", "The verification result appears here after you check a value.")
    if verify_result is not None:
        with tool_result_panel("bcrypt_verify_result_panel", related_to="bcrypt_tool"):
            if not verify_result["ok"]:
                st.error(verify_result["error"])
            elif verify_result["matches"]:
                render_status_note("Match", "The value matches the hash.", tone="success")
            else:
                render_status_note("No match", "The value does not match the hash.", tone="warning")
