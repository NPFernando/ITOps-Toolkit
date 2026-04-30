from __future__ import annotations

import streamlit as st

from utils.text_tools import decode_jwt_unverified
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="JWT Decoder", layout="wide")
apply_app_shell(active_page="JWT Decoder")


render_page_header(
    "JWT Decoder",
    "Decode JWT header and payload locally without signature verification.",
    warning="Do not paste production tokens. This tool decodes locally and does not verify signatures.",
)

with tool_form_panel("jwt_decoder"):
    render_form_intro("Decode token", "Paste a non-production JWT to inspect its header and payload locally.")
    with st.form("jwt-form"):
        token = st.text_area("JWT token", height=180, max_chars=20_000)
        submitted = st.form_submit_button("Decode token")

if not submitted:
    render_empty_state("Ready to decode a JWT", "Issuer, audience, timestamps, header, and payload appear after decoding.")

if submitted:
    result = decode_jwt_unverified(token)
    with tool_result_panel("jwt_result"):
        render_section_heading("Decoded token", "Unverified header and payload values from the pasted token.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            audience = result["audience"]
            audience_text = ", ".join(audience) if isinstance(audience, list) else audience
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Issuer", result["issuer"] or "Unknown")
            c2.metric("Audience", audience_text or "Unknown")
            c3.metric("Issued at", result["issued_at"] or "Unknown")
            c4.metric("Expires at", result["expires_at"] or "Unknown")

            left, right = st.columns(2)
            with left:
                render_section_heading("Header", eyebrow="JWT")
                st.json(result["header"])
            with right:
                render_section_heading("Payload", eyebrow="JWT")
                st.json(result["payload"])
