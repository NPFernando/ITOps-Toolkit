from __future__ import annotations

import streamlit as st

from utils.text_tools import decode_base64_text, encode_base64_text
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Base64 Tool", layout="wide")
apply_app_shell(active_page="Base64 Tool")


render_page_header(
    "Base64 Tool",
    "Encode and decode Base64 text safely in your current session.",
    warning="Do not paste passwords, private keys, API keys, or production tokens.",
)

with tool_form_panel("base64_tool"):
    render_form_intro("Encode or decode", "Convert text to Base64 or decode valid Base64 back to text.")
    with st.form("base64-form"):
        text_input = st.text_area("Input", height=220)
        c1, c2 = st.columns(2)
        with c1:
            encode_clicked = st.form_submit_button("Encode")
        with c2:
            decode_clicked = st.form_submit_button("Decode")

if not (encode_clicked or decode_clicked):
    render_empty_state("Ready for Base64 input", "Encoded or decoded output appears here after you choose an action.")

if encode_clicked:
    with tool_result_panel("base64_encoded"):
        render_section_heading("Encoded result", "Base64 output generated from the current input.")
        st.text_area("Result", value=encode_base64_text(text_input), height=220)

if decode_clicked:
    result = decode_base64_text(text_input.strip())
    with tool_result_panel("base64_decoded"):
        render_section_heading("Decoded result", "Decoded text from valid Base64 input.")
        if result["ok"]:
            st.text_area("Result", value=result["result"], height=220)
        else:
            st.error(result["error"])
