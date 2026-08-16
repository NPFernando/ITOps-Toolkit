from __future__ import annotations

import streamlit as st

from utils.base32_tools import MAX_INPUT_LENGTH, decode_base32_text, encode_base32_text
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


st.set_page_config(page_title="Base32 Encoder/Decoder", layout="wide")
apply_app_shell(active_page="Base32 Encoder/Decoder")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stTextArea"] textarea {
        font-size: 1rem;
      }
      div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 2.75rem;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "Base32 Encoder/Decoder",
    "Encode and decode Base32 (RFC 4648) text -- the encoding TOTP secrets use.",
    warning="Do not paste passwords, private keys, API keys, or production tokens.",
)

with tool_form_panel("base32_tool"):
    render_form_intro("Encode or decode", "Convert text to Base32 or decode valid Base32 back to text.")
    with st.form("base32-form"):
        text_input = st.text_area("Input", height=220, max_chars=MAX_INPUT_LENGTH)
        encode_clicked = st.form_submit_button("Encode", use_container_width=True)
        decode_clicked = st.form_submit_button("Decode", use_container_width=True)

if encode_clicked:
    st.session_state["base32_tool_encoded"] = encode_base32_text(text_input)
if decode_clicked:
    st.session_state["base32_tool_decoded"] = decode_base32_text(text_input)

encoded_result = st.session_state.get("base32_tool_encoded")
decoded_result = st.session_state.get("base32_tool_decoded")

if encoded_result is None and decoded_result is None:
    render_empty_state("Ready for Base32 input", "Encoded or decoded output appears here after you choose an action.")

if encoded_result is not None:
    with tool_result_panel("base32_encoded", related_to="base32_tool"):
        render_section_heading("Encoded result", "Base32 output generated from the current input.")
        render_status_note("Encoded", "Input text was encoded to Base32.", tone="success")
        st.text_area("Result", value=encoded_result, height=220)

if decoded_result is not None:
    with tool_result_panel("base32_decoded", related_to="base32_tool"):
        render_section_heading("Decoded result", "Decoded text from valid Base32 input.")
        if decoded_result["ok"]:
            render_status_note("Decoded", "Base32 input decoded successfully.", tone="success")
            st.text_area("Result", value=decoded_result["result"], height=220)
        else:
            render_failure_note("Base32 decode", decoded_result["error"], remediation="Provide valid Base32 text and decode again.")
