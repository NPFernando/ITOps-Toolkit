from __future__ import annotations

import streamlit as st

from utils.http_tools import MAX_URL_LENGTH
from utils.url_parser import parse_url
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="URL Parser", layout="wide")
apply_app_shell(active_page="URL Parser")


render_page_header(
    "URL Parser",
    "Break a URL down into its scheme, host, port, path, query parameters, and fragment.",
)

with tool_form_panel("url_parser"):
    render_form_intro("Enter a URL", "Paste a URL, with or without a scheme.")
    with st.form("url-parser-form"):
        url_input = st.text_input("URL", placeholder="https://example.com:8443/path?a=1&b=2#frag", max_chars=MAX_URL_LENGTH)
        submitted = st.form_submit_button("Parse")

if submitted:
    st.session_state["url_parser_result"] = parse_url(url_input)

result = st.session_state.get("url_parser_result")

if result is None:
    render_empty_state("Ready to parse", "The URL's components appear here after parsing.")

if result is not None:
    with tool_result_panel("url_parser_result_panel", related_to="url_parser"):
        render_section_heading("Parsed URL", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Scheme", result["scheme"])
            c2.metric("Host", result["host"])
            c3.metric("Port", result["port"] if result["port"] is not None else "default")
            st.caption(f"Path: {result['path']}")
            if result["fragment"]:
                st.caption(f"Fragment: {result['fragment']}")
            if result["query_params"]:
                st.table([{"Key": p["key"], "Value": p["value"]} for p in result["query_params"]])
            else:
                st.caption("No query parameters.")
