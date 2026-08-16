from __future__ import annotations

import streamlit as st

from utils.csr_decoder import MAX_INPUT_LENGTH, decode_csr
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSR Decoder", layout="wide")
apply_app_shell(active_page="CSR Decoder")


render_page_header(
    "CSR Decoder",
    "Decode a PEM-encoded Certificate Signing Request -- subject, SAN entries, public key info, and signature validity.",
    warning="Do not paste private keys -- a CSR contains only the public key and requested subject.",
)

with tool_form_panel("csr_decoder"):
    render_form_intro("Paste a CSR", "PEM-encoded, beginning with -----BEGIN CERTIFICATE REQUEST-----.")
    with st.form("csr-decoder-form"):
        pem_input = st.text_area("CSR (PEM)", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----")
        submitted = st.form_submit_button("Decode")

if submitted:
    st.session_state["csr_decoder_result"] = decode_csr(pem_input)

result = st.session_state.get("csr_decoder_result")

if result is None:
    render_empty_state("Ready to decode", "Subject, SAN entries, key info, and signature validity appear here.")

if result is not None:
    with tool_result_panel("csr_decoder_result_panel", related_to="csr_decoder"):
        render_section_heading("Decoded CSR", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.caption(f"Subject: {result['subject']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Public key", result["public_key_algorithm"])
            c2.metric("Key size", result["public_key_size"] if result["public_key_size"] is not None else "N/A")
            c3.metric("Signature", "Valid" if result["signature_valid"] else "Invalid")
            st.caption(f"Signature algorithm: {result['signature_algorithm']}")
            if result["san_names"]:
                st.table([{"SAN": name} for name in result["san_names"]])
            else:
                st.caption("No Subject Alternative Names.")
