from __future__ import annotations

import streamlit as st

from utils.keypair_tools import KEY_TYPES, RSA_KEY_SIZES, generate_keypair
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


st.set_page_config(page_title="RSA/SSH Key Pair Generator", layout="wide")
apply_app_shell(active_page="RSA/SSH Key Pair Generator")


render_page_header(
    "RSA/SSH Key Pair Generator",
    "Generate a disposable RSA or Ed25519 key pair for test/throwaway use -- not for production key management.",
    warning="Nothing here is stored. This runs in a shared public app -- never reuse a key generated here for anything real.",
)

with tool_form_panel("keypair_generator"):
    render_form_intro("Generate a key pair", "Choose a key type, then click generate.")
    col_type, col_size = st.columns(2)
    key_type = col_type.selectbox("Key type", KEY_TYPES)
    rsa_key_size = col_size.selectbox("RSA key size (bits)", RSA_KEY_SIZES, disabled=key_type != "RSA")
    generate_clicked = st.button("Generate key pair", icon=":material/vpn_key:")

if generate_clicked:
    st.session_state["keypair_result"] = generate_keypair(key_type, rsa_key_size)

result = st.session_state.get("keypair_result")

if result is None:
    render_empty_state("Ready to generate", "A key pair and fingerprint appear here after you generate one.")

if result is not None:
    with tool_result_panel("keypair_result_panel", related_to="keypair_generator"):
        render_section_heading("Result", "Private key (PEM), public key (OpenSSH authorized_keys format), and fingerprint.")
        if not result["ok"]:
            render_failure_note("Key generation", result["error"], remediation="Choose a supported key type and retry.")
        else:
            render_status_note("Key pair generated", "Disposable key pair created successfully.", tone="success")
            st.caption(f"Fingerprint: {result['fingerprint']}")
            st.text_area("Public key (OpenSSH / authorized_keys)", result["public_key_openssh"], height=100)
            st.text_area("Private key (PEM)", result["private_key_pem"], height=280)
            st.download_button("Download private key", result["private_key_pem"], file_name="id_key", mime="application/x-pem-file")
            st.download_button("Download public key", result["public_key_openssh"], file_name="id_key.pub", mime="text/plain")
