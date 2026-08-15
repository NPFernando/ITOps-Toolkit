from __future__ import annotations

import streamlit as st

from utils.http_header_parser import MAX_INPUT_LENGTH, parse_headers_block
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="HTTP Header Parser", layout="wide")
apply_app_shell(active_page="HTTP Header Parser")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stTextArea"] textarea {
        font-size: 1rem;
      }
      div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 2.75rem;
      }
      div[data-testid="stDataFrame"] [data-testid="stTable"] td,
      div[data-testid="stDataFrame"] [data-testid="stTable"] th {
        white-space: normal !important;
        word-break: break-word;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "HTTP Header Parser",
    "Paste raw HTTP request or response headers (e.g. copied from browser devtools) and see them parsed and explained -- no network call.",
)

with tool_form_panel("http_header_parser"):
    render_form_intro("Paste headers", "One 'Name: value' pair per line. An optional request/status line at the top is detected automatically.")
    with st.form("http-header-parser-form"):
        text = st.text_area(
            "Headers",
            height=280,
            max_chars=MAX_INPUT_LENGTH,
            placeholder="HTTP/1.1 200 OK\nContent-Type: application/json\nCache-Control: no-cache",
        )
        submitted = st.form_submit_button("Parse", use_container_width=True)

if submitted:
    st.session_state["http_header_parser_result"] = parse_headers_block(text)

result = st.session_state.get("http_header_parser_result")

if result is None:
    render_empty_state("Ready to parse", "Parsed headers, with brief explanations for well-known ones, appear here.")

if result is not None:
    with tool_result_panel("http_header_parser_result_panel", related_to="http_header_parser"):
        render_section_heading("Parsed headers", eyebrow="Result")
        if not result["ok"]:
            render_failure_note("Header input", result["error"], remediation="Use one 'Name: value' pair per line and parse again.")
        else:
            render_status_note("Headers parsed", f"Parsed {len(result['headers'])} header(s).", tone="success")
            if result["request_line"]:
                st.caption(f"Request/status line: {result['request_line']}")
            else:
                render_status_note("No request/status line", "Only header pairs were detected in this input.", tone="neutral")
            st.dataframe(
                [{"Header": h["name"], "Value": h["value"], "What it does": h["explanation"]} for h in result["headers"]],
                width="stretch",
                hide_index=True,
            )
