from __future__ import annotations

import streamlit as st

from utils.text_tools import JWT_ENCODE_ALGORITHMS, MAX_JSON_LENGTH, encode_jwt
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="JWT Encoder", layout="wide")
apply_app_shell(active_page="JWT Encoder")


render_page_header(
    "JWT Encoder",
    "Build and sign a JWT from a JSON payload and a secret, entirely in your current session.",
    warning="Do not paste production secrets or real signing keys. Use throwaway values for local testing only.",
)

with tool_form_panel("jwt_encoder"):
    render_form_intro("Payload and secret", "Enter a JSON object payload, a secret key, and an HMAC algorithm.")
    with st.form("jwt-encoder-form"):
        payload_input = st.text_area(
            "Payload (JSON object)", height=180, max_chars=MAX_JSON_LENGTH, placeholder='{"sub": "user123"}'
        )
        c1, c2 = st.columns(2)
        with c1:
            secret_input = st.text_input("Secret", type="password")
        with c2:
            algorithm = st.selectbox("Algorithm", JWT_ENCODE_ALGORITHMS)
        submitted = st.form_submit_button("Generate token")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["jwt_encoder_result"] = encode_jwt(payload_input, secret_input, algorithm)

result = st.session_state.get("jwt_encoder_result")

if result is None:
    render_empty_state("Ready to sign a token", "A signed JWT appears here after you submit a payload and secret.")

if submitted:
    result = encode_jwt(payload_input, secret_input, algorithm)
    with tool_result_panel("jwt_encode_result", related_to="jwt_encoder"):
        render_section_heading("Signed token", "Copy this now -- it is not stored or logged.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["token"], language=None)
