from __future__ import annotations

import streamlit as st

from utils.text_tools import MAX_URL_LENGTH, decode_url_text, encode_url_text
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="URL Encoder/Decoder", layout="wide")
apply_app_shell(active_page="URL Encoder/Decoder")


render_page_header(
    "URL Encoder/Decoder",
    "Percent-encode or decode URL components and query strings safely in your current session.",
)

with tool_form_panel("url_encoder_decoder"):
    render_form_intro("Encode or decode", "Convert text to percent-encoded form, or decode a percent-encoded string.")
    with st.form("url-form"):
        text_input = st.text_area("Input", height=180, max_chars=MAX_URL_LENGTH)
        plus_for_space = st.checkbox("Use + for spaces (application/x-www-form-urlencoded)", value=False)
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
    st.session_state["url_encoder_decoder_encoded"] = encode_url_text(text_input, plus_for_space)
if decode_clicked:
    st.session_state["url_encoder_decoder_decoded"] = decode_url_text(text_input, plus_for_space)

encoded_result = st.session_state.get("url_encoder_decoder_encoded")
decoded_result = st.session_state.get("url_encoder_decoder_decoded")

if encoded_result is None and decoded_result is None:
    render_empty_state("Ready for input", "Encoded or decoded output appears here after you choose an action.")

if encode_clicked:
    result = encode_url_text(text_input, plus_for_space)
    with tool_result_panel("url_encoded", related_to="url_encoder_decoder"):
        render_section_heading("Encoded result", "Percent-encoded output generated from the current input.")
        if not encoded_result["ok"]:
            st.error(encoded_result["error"])
        else:
            st.text_area("Result", value=encoded_result["result"], height=180)

if decode_clicked:
    result = decode_url_text(text_input, plus_for_space)
    with tool_result_panel("url_decoded", related_to="url_encoder_decoder"):
        render_section_heading("Decoded result", "Decoded text from the current input.")
        if not decoded_result["ok"]:
            st.error(decoded_result["error"])
        else:
            st.text_area("Result", value=decoded_result["result"], height=180)
