from __future__ import annotations

import streamlit as st

from utils.base62_tool import decode_base62, encode_base62
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Base62 Encoder/Decoder", layout="wide")
apply_app_shell(active_page="Base62 Encoder/Decoder")


render_page_header(
    "Base62 Encoder/Decoder",
    "Encode a non-negative integer to Base62 (0-9, A-Z, a-z), or decode one back -- commonly used for URL-safe short IDs.",
)

encode_tab, decode_tab = st.tabs(["Encode", "Decode"])

with encode_tab:
    with tool_form_panel("base62_encode"):
        render_form_intro("Enter a non-negative integer", "")
        with st.form("base62-encode-form"):
            number_input = st.text_input("Number", placeholder="12345")
            encode_submitted = st.form_submit_button("Encode")

    if encode_submitted:
        st.session_state["base62_encode_result"] = encode_base62(number_input)

    encode_result = st.session_state.get("base62_encode_result")

    if encode_result is None:
        render_empty_state("Ready to encode", "The Base62 string appears here.")

    if encode_result is not None:
        with tool_result_panel("base62_encode_result_panel", related_to="base62_tool"):
            render_section_heading("Base62", eyebrow="Result")
            if not encode_result["ok"]:
                st.error(encode_result["error"])
            else:
                st.code(encode_result["output"], language=None)

with decode_tab:
    with tool_form_panel("base62_decode"):
        render_form_intro("Enter a Base62 string to decode", "")
        with st.form("base62-decode-form"):
            encoded_input = st.text_input("Base62", placeholder="3D7")
            decode_submitted = st.form_submit_button("Decode")

    if decode_submitted:
        st.session_state["base62_decode_result"] = decode_base62(encoded_input)

    decode_result = st.session_state.get("base62_decode_result")

    if decode_result is None:
        render_empty_state("Ready to decode", "The decoded integer appears here.")

    if decode_result is not None:
        with tool_result_panel("base62_decode_result_panel", related_to="base62_tool"):
            render_section_heading("Decoded integer", eyebrow="Result")
            if not decode_result["ok"]:
                st.error(decode_result["error"])
            else:
                st.code(decode_result["output"], language=None)
