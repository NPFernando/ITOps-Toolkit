from __future__ import annotations

import streamlit as st

from utils.jwk_pem_converter import MAX_INPUT_LENGTH, jwk_to_pem, pem_to_jwk
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="JWK / PEM Converter", layout="wide")
apply_app_shell(active_page="JWK / PEM Converter")


render_page_header(
    "JWK / PEM Converter",
    "Convert an RSA public key between JWK (JSON Web Key) and PEM format -- useful when working with a JWKS endpoint.",
    warning="RSA public keys only -- EC/OKP JWKs use a different coordinate system and aren't supported here.",
)

jwk_to_pem_tab, pem_to_jwk_tab = st.tabs(["JWK to PEM", "PEM to JWK"])

with jwk_to_pem_tab:
    with tool_form_panel("jwk_to_pem"):
        render_form_intro("Paste a JWK", "")
        with st.form("jwk-to-pem-form"):
            jwk_input = st.text_area("JWK", height=200, max_chars=MAX_INPUT_LENGTH, placeholder='{"kty": "RSA", "n": "...", "e": "AQAB"}')
            jwk_submitted = st.form_submit_button("Convert to PEM")

    if jwk_submitted:
        st.session_state["jwk_to_pem_result"] = jwk_to_pem(jwk_input)

    jwk_result = st.session_state.get("jwk_to_pem_result")

    if jwk_result is None:
        render_empty_state("Ready to convert", "The PEM public key appears here.")

    if jwk_result is not None:
        with tool_result_panel("jwk_to_pem_result_panel", related_to="jwk_pem_converter"):
            render_section_heading("PEM public key", eyebrow="Result")
            if not jwk_result["ok"]:
                st.error(jwk_result["error"])
            else:
                st.code(jwk_result["output"], language=None)

with pem_to_jwk_tab:
    with tool_form_panel("pem_to_jwk"):
        render_form_intro("Paste a PEM public key", "")
        with st.form("pem-to-jwk-form"):
            pem_input = st.text_area("PEM public key", height=200, max_chars=MAX_INPUT_LENGTH, placeholder="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----")
            key_id_input = st.text_input("Key ID (kid, optional)")
            pem_submitted = st.form_submit_button("Convert to JWK")

    if pem_submitted:
        st.session_state["pem_to_jwk_result"] = pem_to_jwk(pem_input, key_id_input)

    pem_result = st.session_state.get("pem_to_jwk_result")

    if pem_result is None:
        render_empty_state("Ready to convert", "The JWK appears here.")

    if pem_result is not None:
        with tool_result_panel("pem_to_jwk_result_panel", related_to="jwk_pem_converter"):
            render_section_heading("JWK", eyebrow="Result")
            if not pem_result["ok"]:
                st.error(pem_result["error"])
            else:
                st.code(pem_result["output"], language="json")
