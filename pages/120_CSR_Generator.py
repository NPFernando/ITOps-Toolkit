from __future__ import annotations

import streamlit as st

from utils.csr_generator import RSA_KEY_SIZES, generate_csr
from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_control_heading,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("CSR Generator")
st.set_page_config(page_title="CSR Generator", layout="wide")
apply_app_shell(active_page="CSR Generator")
mark_page_baseline(_baseline, "shell-ready")
mark_page_baseline(_baseline, "wave28-shell-mobile")


render_page_header(
    "CSR Generator",
    "Generate a new RSA key pair and a Certificate Signing Request from subject fields -- the reverse of CSR Decoder.",
    warning="Generated values are shown once and never transmitted or stored. Not for production key management -- this app has no way to protect a private key once it's rendered to the browser.",
)

with tool_form_panel("csr_generator"):
    render_form_intro("Enter subject fields", "Shared headings and one full-width action keep certificate setup consistent on small screens.")
    with st.form("csr-generator-form"):
        render_control_heading("Required field")
        common_name = st.text_input("Common Name", placeholder="example.com")
        render_control_heading("Organization details")
        organization = st.text_input("Organization", placeholder="Acme Inc")
        organizational_unit = st.text_input("Organizational Unit", placeholder="Engineering")
        render_control_heading("Location details")
        locality = st.text_input("Locality (city)")
        state = st.text_input("State/Province")
        render_control_heading("Certificate options")
        country = st.text_input("Country (2-letter)", placeholder="US", max_chars=2)
        san_input = st.text_input("Subject Alternative Names (comma-separated)", placeholder="example.com, www.example.com")
        rsa_key_size = st.selectbox("RSA key size", RSA_KEY_SIZES, index=0)
        render_control_heading("Primary action")
        submitted = st.form_submit_button("Generate CSR", use_container_width=True)

if submitted:
    san_domains = [d.strip() for d in san_input.split(",") if d.strip()]
    st.session_state["csr_generator_result"] = generate_csr(
        common_name, organization, organizational_unit, locality, state, country, san_domains, rsa_key_size
    )

result = st.session_state.get("csr_generator_result")

if result is None:
    render_empty_state("Ready to generate", "The private key and CSR appear here.")
    render_status_note(
        "Outcome: CSR generation ready",
        "No CSR generation has run yet. Enter certificate subject fields, then select Generate CSR to continue.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("csr_generator_result_panel", related_to="csr_generator"):
        render_section_heading("Generated CSR", eyebrow="Result")
        if not result["ok"]:
            render_status_note(
                "Outcome: CSR generation blocked",
                f"CSR generation did not complete. {result['error']} Provide a Common Name and valid optional fields, then generate again.",
                tone="warning",
            )
        else:
            render_status_note(
                "Outcome: CSR generation complete",
                "Generation complete. CSR and private key PEM output are ready below.",
                tone="success",
            )
            st.markdown("**Certificate Signing Request**")
            st.code(result["csr_pem"], language=None)
            st.markdown("**Private Key**")
            st.code(result["private_key_pem"], language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
