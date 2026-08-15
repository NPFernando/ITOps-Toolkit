from __future__ import annotations

import streamlit as st

from utils.http_tools import MAX_URL_LENGTH
from utils.url_parser import parse_url
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


st.set_page_config(page_title="URL Parser", layout="wide")
apply_app_shell(active_page="URL Parser")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stTextInput"] input {
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
    "URL Parser",
    "Break a URL down into its scheme, host, port, path, query parameters, and fragment.",
)

with tool_form_panel("url_parser"):
    render_form_intro("Enter a URL", "Paste a URL, with or without a scheme.")
    with st.form("url-parser-form"):
        url_input = st.text_input("URL", placeholder="https://example.com:8443/path?a=1&b=2#frag", max_chars=MAX_URL_LENGTH)
        submitted = st.form_submit_button("Parse", use_container_width=True)

if submitted:
    st.session_state["url_parser_result"] = parse_url(url_input)

result = st.session_state.get("url_parser_result")

if result is None:
    render_empty_state("Ready to parse", "The URL's components appear here after parsing.")

if result is not None:
    with tool_result_panel("url_parser_result_panel", related_to="url_parser"):
        render_section_heading("Parsed URL", eyebrow="Result")
        if not result["ok"]:
            render_failure_note("URL input", result["error"], remediation="Enter a valid URL and parse again.")
        else:
            render_status_note("URL parsed", "URL components extracted successfully.", tone="success")
            st.dataframe(
                [
                    {"Component": "Scheme", "Value": result["scheme"]},
                    {"Component": "Host", "Value": result["host"]},
                    {"Component": "Port", "Value": str(result["port"]) if result["port"] is not None else "default"},
                    {"Component": "Path", "Value": result["path"]},
                ],
                width="stretch",
                hide_index=True,
            )
            if result["fragment"]:
                st.caption(f"Fragment: {result['fragment']}")
            else:
                render_status_note("No fragment", "This URL does not include a #fragment section.", tone="neutral")
            if result["query_params"]:
                st.dataframe(
                    [{"Key": p["key"], "Value": p["value"]} for p in result["query_params"]],
                    width="stretch",
                    hide_index=True,
                )
            else:
                render_status_note("No query parameters", "This URL has no query string key/value pairs.", tone="neutral")
