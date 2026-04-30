from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.http_tools import MAX_URL_LENGTH, check_http_status
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    display_rows_frame,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="HTTP Status Checker", layout="wide")
apply_app_shell(active_page="HTTP Status Checker")


render_page_header("HTTP Status Checker", "Check status, redirects, timing, and selected response headers.")

with tool_form_panel("http_status"):
    render_form_intro("Check URL", "Enter a public URL or domain to inspect status, timing, redirects, and selected headers.")
    with st.form("http-form"):
        url = st.text_input("URL", placeholder="https://example.com", max_chars=MAX_URL_LENGTH)
        submitted = st.form_submit_button("Check URL")

if not submitted:
    render_empty_state("Ready to check HTTP", "Response status, selected headers, redirects, and recommendations appear after the check.")

if submitted:
    ok, error = validate_length(url, MAX_URL_LENGTH, "URL")
    if not ok:
        st.error(error)
    else:
        result = check_http_status(url)
        with tool_result_panel("http_result"):
            render_section_heading("HTTP result", "Status, timing, HTTPS state, and final URL.")
            if result["ok"]:
                st.success("Healthy")
            elif result["error"]:
                st.error(result["error"])
            else:
                st.warning("Warning")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status code", result["status_code"] or "Failed")
            c2.metric("Reason", result["reason"] or "Unknown")
            c3.metric("Response time", f"{result['response_time_ms']} ms" if result["response_time_ms"] else "Unknown")
            c4.metric("HTTPS", "Yes" if result["uses_https"] else "No")

            rows = [
                {"field": "Final URL", "value": result["final_url"] or "Unknown"},
                {"field": "Input URL", "value": result["url"]},
                {"field": "Status code", "value": result["status_code"] or "Unknown"},
                {"field": "Reason", "value": result["reason"] or "Unknown"},
            ]
            st.dataframe(display_rows_frame(rows), width="stretch", hide_index=True)

            render_section_heading("Selected headers", "Security and response headers returned by the final URL.", eyebrow="Headers")
            if result["headers"]:
                st.dataframe(
                    pd.DataFrame([{"header": key, "value": value} for key, value in result["headers"].items()]),
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.caption("No selected headers returned.")

            if result["redirect_chain"]:
                with st.expander("Redirect chain"):
                    st.dataframe(pd.DataFrame(result["redirect_chain"]), width="stretch", hide_index=True)

            render_section_heading("Recommendations", "Header, HTTPS, and status recommendations from this check.", eyebrow="Actions")
            if result["recommendations"]:
                for item in result["recommendations"]:
                    st.warning(item)
            else:
                st.success("No header or HTTPS recommendations from this check.")
