from __future__ import annotations

import streamlit as st

from utils.ipv6_tools import MAX_INPUT_LENGTH, convert_ipv6
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="IPv6 Compressor", layout="wide")
apply_app_shell(active_page="IPv6 Compressor")


st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stFormSubmitButton"] > button {
        min-height: 2.75rem;
        font-size: 1rem;
      }
      div[data-testid="stTextInput"] input {
        font-size: 1rem;
      }
      div[data-testid="stCodeBlock"] pre {
        white-space: pre-wrap;
        word-break: break-word;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "IPv6 Compressor",
    "Convert an IPv6 address between its compressed (::) and fully expanded form.",
)

with tool_form_panel("ipv6_compressor"):
    render_form_intro("Enter an IPv6 address", "Either form works -- compressed or fully expanded.")
    with st.form("ipv6-form"):
        address_input = st.text_input("IPv6 address", max_chars=MAX_INPUT_LENGTH, placeholder="2001:db8::1")
        submitted = st.form_submit_button("Convert")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["ipv6_compressor_result"] = convert_ipv6(address_input)

result = st.session_state.get("ipv6_compressor_result")

if result is None:
    render_empty_state("Ready to convert", "Both the compressed and expanded forms appear here after you submit.")

if result is not None:
    with tool_result_panel("ipv6_result", related_to="ipv6_compressor"):
        render_section_heading("Converted forms", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.write("Compressed address")
            st.code(result["compressed"], language="text")
            st.write("Expanded address")
            st.code(result["expanded"], language="text")
