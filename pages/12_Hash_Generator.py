from __future__ import annotations

import streamlit as st

from utils.hash_tools import HMAC_ALGORITHMS, generate_hashes, generate_hmac
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Hash Generator", layout="wide")
apply_app_shell(active_page="Hash Generator")


render_page_header(
    "Hash Generator",
    "Generate MD5/SHA/SHA-3 digests and HMAC signatures from text, entirely in your current session.",
    warning="Do not paste passwords, private keys, or production secrets.",
)

with tool_form_panel("hash_generator"):
    render_form_intro("Enter text", "Hash text with common algorithms, or compute an HMAC with a secret key.")
    with st.form("hash-form"):
        text_input = st.text_area("Input text", height=180)
        secret_input = st.text_input("HMAC secret (optional)", type="password")
        c1, c2 = st.columns(2)
        with c1:
            hash_clicked = st.form_submit_button("Generate hashes")
        with c2:
            hmac_algorithm = st.selectbox("HMAC algorithm", HMAC_ALGORITHMS, label_visibility="collapsed")
            hmac_clicked = st.form_submit_button("Generate HMAC")

if not (hash_clicked or hmac_clicked):
    render_empty_state("Ready for input", "Digests or an HMAC signature appear here after you submit text.")

if hash_clicked:
    result = generate_hashes(text_input)
    with tool_result_panel("hash_result"):
        render_section_heading("Digests", "Hex-encoded digests for the entered text.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            for algorithm, digest in result["digests"].items():
                st.text_input(algorithm.upper(), value=digest, disabled=True)

if hmac_clicked:
    result = generate_hmac(text_input, secret_input, hmac_algorithm)
    with tool_result_panel("hmac_result"):
        render_section_heading("HMAC", f"HMAC-{hmac_algorithm.upper()} of the entered text.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.text_input("HMAC digest", value=result["digest"], disabled=True)
