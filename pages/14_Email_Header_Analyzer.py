from __future__ import annotations

import streamlit as st

from utils.email_header_tools import parse_email_headers
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Email Header Analyzer", layout="wide")
apply_app_shell(active_page="Email Header Analyzer")


render_page_header(
    "Email Header Analyzer",
    "Parse raw email headers into a summary, the Received hop chain, and authentication results.",
    warning="Only header text is inspected here -- no network calls are made and no external verification is performed.",
)

with tool_form_panel("email_header_analyzer"):
    render_form_intro("Paste raw headers", "Paste the full raw header block from an email (not the message body).")
    with st.form("email-header-form"):
        headers_input = st.text_area("Raw email headers", height=260)
        submitted = st.form_submit_button("Analyze headers")

if not submitted:
    render_empty_state("Ready to analyze headers", "Summary fields, hop chain, and auth results appear here.")

if submitted:
    result = parse_email_headers(headers_input)
    with tool_result_panel("email_header_result"):
        render_section_heading("Header summary", "Common fields found in the pasted headers.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            if result["summary"]:
                st.table([{"Field": field, "Value": value} for field, value in result["summary"].items()])
            else:
                st.info("No recognized summary fields were found.")

            render_section_heading("Received hop chain", f"{result['hop_count']} hop(s), oldest first.", eyebrow="Routing")
            if result["received_hops"]:
                st.table(
                    [
                        {
                            "Hop": hop["hop"],
                            "From": hop["from"] or "-",
                            "By": hop["by"] or "-",
                            "Timestamp": hop["timestamp"] or "-",
                            "Delay (s)": hop["delay_seconds"] if hop["delay_seconds"] is not None else "-",
                        }
                        for hop in result["received_hops"]
                    ]
                )
            else:
                st.info("No Received headers were found.")

            render_section_heading("Authentication-Results", eyebrow="Authentication")
            if result["authentication_results"]:
                for entry in result["authentication_results"]:
                    st.code(entry, language=None)
            else:
                st.info("No Authentication-Results headers were found.")
