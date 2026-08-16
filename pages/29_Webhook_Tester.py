from __future__ import annotations

import streamlit as st

from utils.http_tools import MAX_URL_LENGTH
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)
from utils.webhook_tools import ALLOWED_METHODS, MAX_BODY_LENGTH, MAX_HEADERS_LENGTH, send_request


st.set_page_config(page_title="Webhook Tester", layout="wide")
apply_app_shell(active_page="Webhook Tester")


render_page_header(
    "Webhook Tester",
    "Send a one-off HTTP request with a custom method, headers, and body -- useful for testing webhooks and APIs.",
    warning="Do not enter private hostnames, credentials, or sensitive data in the URL, headers, or body.",
)

with tool_form_panel("webhook_tester"):
    render_form_intro("Build a request", "Choose a method, enter a URL, and optionally add headers and a body.")
    with st.form("webhook-form"):
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
        submitted = st.form_submit_button("Send request")

if not submitted:
    render_empty_state("Ready to send a request", "Response status, headers, timing, and body appear here after the request completes.")

if submitted:
    with st.spinner("Sending request..."):
        result = send_request(url, method, headers_text, body_text)
    with tool_result_panel("webhook_result"):
        render_section_heading("Response", eyebrow="Result")
        if result["error"]:
            st.error(result["error"])
        if result["status_code"] is not None:
            if result["ok"]:
                st.success(f"{result['status_code']} {result['reason']}")
            else:
                st.warning(f"{result['status_code']} {result['reason']}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Status code", result["status_code"])
            c2.metric("Response time", f"{result['response_time_ms']} ms" if result["response_time_ms"] else "Unknown")
            c3.metric("Method", result["method"])

            if result["response_headers"]:
                with st.expander("Response headers", expanded=False):
                    st.table([{"Header": k, "Value": v} for k, v in result["response_headers"].items()])

            render_section_heading("Response body", eyebrow="Body")
            if result["response_body_truncated"]:
                st.caption("Response body truncated for display.")
            st.code(result["response_body"] or "(empty body)", language="text")
