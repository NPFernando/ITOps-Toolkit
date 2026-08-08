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

if encode_clicked:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns the transient
    # *_clicked flags are False again, which would otherwise collapse this whole
    # results section the instant any of them is touched.
    st.session_state["base64_tool_encoded"] = encode_base64_text(text_input)
if decode_clicked:
    st.session_state["base64_tool_decoded"] = decode_base64_text(text_input)

encoded_result = st.session_state.get("base64_tool_encoded")
decoded_result = st.session_state.get("base64_tool_decoded")

if encoded_result is None and decoded_result is None:
    render_empty_state("Ready for Base64 input", "Encoded or decoded output appears here after you choose an action.")

if encoded_result is not None:
    with tool_result_panel("base64_encoded", related_to="base64_tool"):
        render_section_heading("Encoded result", "Base64 output generated from the current input.")
        st.text_area("Result", value=encoded_result, height=220)

if decoded_result is not None:
    with tool_result_panel("base64_decoded", related_to="base64_tool"):
        render_section_heading("Decoded result", "Decoded text from valid Base64 input.")
        if decoded_result["ok"]:
            st.text_area("Result", value=decoded_result["result"], height=220)
        else:
            st.error(decoded_result["error"])
