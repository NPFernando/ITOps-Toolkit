from __future__ import annotations

import streamlit as st

from utils.curl_builder import build_curl_command
from utils.http_tools import MAX_URL_LENGTH
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)
from utils.webhook_tools import ALLOWED_METHODS, MAX_BODY_LENGTH, MAX_HEADERS_LENGTH


st.set_page_config(page_title="curl Command Builder", layout="wide")
apply_app_shell(active_page="curl Command Builder")


render_page_header(
    "curl Command Builder",
    "Build a copy-pasteable curl command from a method, URL, headers, and body -- the reverse of Webhook Tester.",
    warning="Do not enter private hostnames, credentials, or sensitive data in the URL, headers, or body.",
)

with tool_form_panel("curl_builder"):
    render_form_intro("Build a curl command", "Choose a method, enter a URL, and optionally add headers and a body.")
    with st.form("curl-builder-form"):
        method_col, url_col = st.columns([1, 4])
        method = method_col.selectbox("Method", ALLOWED_METHODS)
        url = url_col.text_input("URL", placeholder="https://example.com/webhook", max_chars=MAX_URL_LENGTH)
        headers_text = st.text_area(
            "Headers (one per line, Key: Value)",
            height=100,
            max_chars=MAX_HEADERS_LENGTH,
            placeholder="Content-Type: application/json",
        )
        body_text = st.text_area("Body (POST/PUT/PATCH/DELETE only)", height=140, max_chars=MAX_BODY_LENGTH)
        submitted = st.form_submit_button("Build command")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched.
    st.session_state["curl_builder_result"] = build_curl_command(url, method, headers_text, body_text)

result = st.session_state.get("curl_builder_result")

if result is None:
    render_empty_state("Ready to build a command", "The generated curl command appears here after you build one.")
    render_status_note(
        "Awaiting inputs",
        "Pick a method, provide a URL, and submit to generate a shell-ready command.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("curl_builder_result_panel", related_to="curl_builder"):
        render_section_heading("Generated curl command", "Copy this into a terminal, script, or ticket.", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
            render_status_note(
                "Command not generated",
                "Fix the highlighted validation issue, then build the command again.",
                tone="warning",
            )
        else:
            st.code(result["command"], language="bash")
            render_status_note(
                "Command ready for copy",
                "Use keyboard focus or your pointer to copy the generated command block.",
                tone="success",
            )
