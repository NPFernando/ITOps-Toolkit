from __future__ import annotations

import streamlit as st

from utils.html_entity_tools import MAX_INPUT_LENGTH, decode_html_entities, encode_html_entities
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="HTML Entity Encoder/Decoder", layout="wide")
apply_app_shell(active_page="HTML Entity Encoder/Decoder")


render_page_header(
    "HTML Entity Encoder/Decoder",
    "Encode text to HTML entities, or decode HTML entities (including numeric character references) back to plain text.",
)

with tool_form_panel("html_entity_tool"):
    render_form_intro("Encode or decode", "Convert text to HTML entities, or decode entity-encoded text.")
    with st.form("html-entity-form"):
        text_input = st.text_area("Input", height=220, max_chars=MAX_INPUT_LENGTH)
        c1, c2 = st.columns(2)
        with c1:
            encode_clicked = st.form_submit_button("Encode")
        with c2:
            decode_clicked = st.form_submit_button("Decode")

if encode_clicked:
    st.session_state["html_entity_tool_encoded"] = encode_html_entities(text_input)
if decode_clicked:
    st.session_state["html_entity_tool_decoded"] = decode_html_entities(text_input)

encoded_result = st.session_state.get("html_entity_tool_encoded")
decoded_result = st.session_state.get("html_entity_tool_decoded")

if encoded_result is None and decoded_result is None:
    render_empty_state("Ready for input", "Encoded or decoded output appears here after you choose an action.")

if encoded_result is not None:
    with tool_result_panel("html_entity_encoded", related_to="html_entity_tool"):
        render_section_heading("Encoded result", "HTML-entity-encoded output generated from the current input.")
        st.text_area("Result", value=encoded_result, height=220)

if decoded_result is not None:
    with tool_result_panel("html_entity_decoded", related_to="html_entity_tool"):
        render_section_heading("Decoded result", "Decoded text from HTML entities.")
        if decoded_result["ok"]:
            st.text_area("Result", value=decoded_result["result"], height=220)
        else:
            st.error(decoded_result["error"])
