from __future__ import annotations

import streamlit as st

from utils.base32_tools import decode_base32_text, encode_base32_text
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Base32 Encoder/Decoder", layout="wide")
apply_app_shell(active_page="Base32 Encoder/Decoder")


render_page_header(
    "Base32 Encoder/Decoder",
    "Encode and decode Base32 (RFC 4648) text -- the encoding TOTP secrets use.",
    warning="Do not paste passwords, private keys, API keys, or production tokens.",
)

with tool_form_panel("base32_tool"):
    render_form_intro("Encode or decode", "Convert text to Base32 or decode valid Base32 back to text.")
    with st.form("base32-form"):
        text_input = st.text_area("Input", height=220)
        c1, c2 = st.columns(2)
        with c1:
            encode_clicked = st.form_submit_button("Encode")
        with c2:
            decode_clicked = st.form_submit_button("Decode")

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
        st.text_area("Result", value=encoded_result, height=220)

if decoded_result is not None:
    with tool_result_panel("base32_decoded", related_to="base32_tool"):
        render_section_heading("Decoded result", "Decoded text from valid Base32 input.")
        if decoded_result["ok"]:
            st.text_area("Result", value=decoded_result["result"], height=220)
        else:
            st.error(decoded_result["error"])
