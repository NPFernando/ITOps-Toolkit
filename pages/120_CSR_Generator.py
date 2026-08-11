from __future__ import annotations

import streamlit as st

from utils.csr_generator import RSA_KEY_SIZES, generate_csr
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSR Generator", layout="wide")
apply_app_shell(active_page="CSR Generator")


render_page_header(
    "CSR Generator",
    "Generate a new RSA key pair and a Certificate Signing Request from subject fields -- the reverse of CSR Decoder.",
    warning="Generated values are shown once and never transmitted or stored. Not for production key management -- this app has no way to protect a private key once it's rendered to the browser.",
)

with tool_form_panel("csr_generator"):
    render_form_intro("Enter subject fields", "Only Common Name is required.")
    with st.form("csr-generator-form"):
        common_name = st.text_input("Common Name", placeholder="example.com")
        c1, c2 = st.columns(2)
        organization = c1.text_input("Organization", placeholder="Acme Inc")
        organizational_unit = c2.text_input("Organizational Unit", placeholder="Engineering")
        c3, c4, c5 = st.columns(3)
        locality = c3.text_input("Locality (city)")
        state = c4.text_input("State/Province")
        country = c5.text_input("Country (2-letter)", placeholder="US", max_chars=2)
        san_input = st.text_input("Subject Alternative Names (comma-separated)", placeholder="example.com, www.example.com")
        rsa_key_size = st.selectbox("RSA key size", RSA_KEY_SIZES, index=0)
        submitted = st.form_submit_button("Generate CSR")

if submitted:
    san_domains = [d.strip() for d in san_input.split(",") if d.strip()]
    st.session_state["csr_generator_result"] = generate_csr(
        common_name, organization, organizational_unit, locality, state, country, san_domains, rsa_key_size
    )

result = st.session_state.get("csr_generator_result")

if result is None:
    render_empty_state("Ready to generate", "The private key and CSR appear here.")

if result is not None:
    with tool_result_panel("csr_generator_result_panel", related_to="csr_generator"):
        render_section_heading("Generated CSR", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.markdown("**Certificate Signing Request**")
            st.code(result["csr_pem"], language=None)
            st.markdown("**Private Key**")
            st.code(result["private_key_pem"], language=None)
