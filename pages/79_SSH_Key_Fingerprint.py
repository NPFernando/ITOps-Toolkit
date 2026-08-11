from __future__ import annotations

import streamlit as st

from utils.ssh_fingerprint import MAX_INPUT_LENGTH, compute_fingerprint
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="SSH Key Fingerprint", layout="wide")
apply_app_shell(active_page="SSH Key Fingerprint")


render_page_header(
    "SSH Key Fingerprint",
    "Paste a public SSH key (or a known_hosts line) to see its MD5 and SHA256 fingerprints, matching ssh-keygen -lf's output.",
)

with tool_form_panel("ssh_fingerprint"):
    render_form_intro("Paste a public key", "A standard 'ssh-rsa AAAA... comment' line, or a known_hosts line.")
    with st.form("ssh-fingerprint-form"):
        key_input = st.text_area("SSH public key", height=150, max_chars=MAX_INPUT_LENGTH, placeholder="ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB... user@host")
        submitted = st.form_submit_button("Compute fingerprint")

if submitted:
    st.session_state["ssh_fingerprint_result"] = compute_fingerprint(key_input)

result = st.session_state.get("ssh_fingerprint_result")

if result is None:
    render_empty_state("Ready to compute", "MD5 and SHA256 fingerprints appear here.")

if result is not None:
    with tool_result_panel("ssh_fingerprint_result_panel", related_to="ssh_fingerprint"):
        render_section_heading("Fingerprints", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.metric("Key type", result["key_type"])
            st.caption("MD5:")
            st.code(result["md5_fingerprint"], language=None)
            st.caption("SHA256:")
            st.code(result["sha256_fingerprint"], language=None)
            if result["comment"]:
                st.caption(f"Comment: {result['comment']}")
