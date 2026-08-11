from __future__ import annotations

import streamlit as st

from utils.basic_auth_tool import MAX_INPUT_LENGTH, build_basic_auth_header, parse_basic_auth_header
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Basic Auth Header Tool", layout="wide")
apply_app_shell(active_page="Basic Auth Header Tool")


render_page_header(
    "Basic Auth Header Tool",
    "Build or parse an HTTP Authorization: Basic header (RFC 7617).",
)

build_tab, parse_tab = st.tabs(["Build header", "Parse header"])

with build_tab:
    with tool_form_panel("basic_auth_build"):
        render_form_intro("Enter a username and password", "")
        with st.form("basic-auth-build-form"):
            c1, c2 = st.columns(2)
            username_input = c1.text_input("Username", max_chars=MAX_INPUT_LENGTH)
            password_input = c2.text_input("Password", type="password", max_chars=MAX_INPUT_LENGTH)
            build_submitted = st.form_submit_button("Build header")

    if build_submitted:
        st.session_state["basic_auth_build_result"] = build_basic_auth_header(username_input, password_input)

    build_result = st.session_state.get("basic_auth_build_result")

    if build_result is None:
        render_empty_state("Ready to build", "The Authorization header value appears here.")

    if build_result is not None:
        with tool_result_panel("basic_auth_build_result_panel", related_to="basic_auth_tool"):
            render_section_heading("Authorization header", eyebrow="Result")
            if not build_result["ok"]:
                st.error(build_result["error"])
            else:
                st.code(build_result["output"], language=None)

with parse_tab:
    with tool_form_panel("basic_auth_parse"):
        render_form_intro("Paste a header value", "Either the bare Base64 token or the full \"Basic ...\" value.")
        with st.form("basic-auth-parse-form"):
            header_input = st.text_input("Header value", placeholder="Basic YWxpY2U6cGFzc3dvcmQ=", max_chars=MAX_INPUT_LENGTH)
            parse_submitted = st.form_submit_button("Parse header")

    if parse_submitted:
        st.session_state["basic_auth_parse_result"] = parse_basic_auth_header(header_input)

    parse_result = st.session_state.get("basic_auth_parse_result")

    if parse_result is None:
        render_empty_state("Ready to parse", "The decoded username/password appear here.")

    if parse_result is not None:
        with tool_result_panel("basic_auth_parse_result_panel", related_to="basic_auth_tool"):
            render_section_heading("Decoded credentials", eyebrow="Result")
            if not parse_result["ok"]:
                st.error(parse_result["error"])
            else:
                c1, c2 = st.columns(2)
                c1.metric("Username", parse_result["username"])
                c2.metric("Password", parse_result["password"])
