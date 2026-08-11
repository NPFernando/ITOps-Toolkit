from __future__ import annotations

import streamlit as st

from utils.base58_tool import MAX_INPUT_LENGTH, decode_base58, encode_base58
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Base58 Encoder/Decoder", layout="wide")
apply_app_shell(active_page="Base58 Encoder/Decoder")


render_page_header(
    "Base58 Encoder/Decoder",
    "Encode or decode text using the Bitcoin/IPFS Base58 alphabet (excludes 0, O, I, l).",
)

encode_tab, decode_tab = st.tabs(["Encode", "Decode"])

with encode_tab:
    with tool_form_panel("base58_encode"):
        render_form_intro("Enter text to encode", "")
        with st.form("base58-encode-form"):
            encode_input = st.text_area("Text", height=150, max_chars=MAX_INPUT_LENGTH, placeholder="Hello World")
            encode_submitted = st.form_submit_button("Encode")

    if encode_submitted:
        st.session_state["base58_encode_result"] = encode_base58(encode_input)

    encode_result = st.session_state.get("base58_encode_result")

    if encode_result is None:
        render_empty_state("Ready to encode", "The Base58 string appears here.")

    if encode_result is not None:
        with tool_result_panel("base58_encode_result_panel", related_to="base58_tool"):
            render_section_heading("Base58", eyebrow="Result")
            if not encode_result["ok"]:
                st.error(encode_result["error"])
            else:
                st.code(encode_result["output"], language=None)

with decode_tab:
    with tool_form_panel("base58_decode"):
        render_form_intro("Enter a Base58 string to decode", "")
        with st.form("base58-decode-form"):
            decode_input = st.text_area("Base58", height=150, max_chars=MAX_INPUT_LENGTH, placeholder="JxF12TrwUP45BMd")
            decode_submitted = st.form_submit_button("Decode")

    if decode_submitted:
        st.session_state["base58_decode_result"] = decode_base58(decode_input)

    decode_result = st.session_state.get("base58_decode_result")

    if decode_result is None:
        render_empty_state("Ready to decode", "The decoded text appears here.")

    if decode_result is not None:
        with tool_result_panel("base58_decode_result_panel", related_to="base58_tool"):
            render_section_heading("Decoded text", eyebrow="Result")
            if not decode_result["ok"]:
                st.error(decode_result["error"])
            else:
                st.code(decode_result["output"], language=None)
