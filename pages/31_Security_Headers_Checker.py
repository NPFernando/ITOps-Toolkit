from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.http_tools import MAX_URL_LENGTH
from utils.security_headers import check_security_headers
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    run_validated_lookup,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Security Headers Checker", layout="wide")
apply_app_shell(active_page="Security Headers Checker")


render_page_header(
    "Security Headers Checker",
    "Grade a URL's response security headers -- HSTS, CSP, and more -- similar to securityheaders.com.",
    warning="Do not enter private hostnames or sensitive customer data.",
)

with tool_form_panel("security_headers"):
    render_form_intro("Check URL", "Enter a public URL to fetch and grade its response security headers.")
    with st.form("security-headers-form"):
        url = st.text_input("URL", placeholder="https://example.com", max_chars=MAX_URL_LENGTH)
        submitted = st.form_submit_button("Check headers")

if submitted:
    def _validate() -> str | None:
        ok, error = validate_length(url, MAX_URL_LENGTH, "URL")
        return None if ok else error

    run_validated_lookup(
        "security_headers", _validate, lambda: check_security_headers(url), spinner_text="Fetching headers..."
    )

validation_error = st.session_state.get("security_headers_validation_error")
result = st.session_state.get("security_headers_result")

if validation_error is None and result is None:
    render_empty_state(
        "Ready to check security headers",
        "A letter grade and a per-header breakdown appear after the check.",
        illustration="security",
    )

if validation_error is not None:
    st.error(validation_error)

if result is not None:
    with tool_result_panel("security_headers_result", related_to="security_headers"):
        render_section_heading("Security headers", "Grade and per-header breakdown for the final response.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Grade", result["grade"])
            c2.metric("Status code", result["status_code"])
            c3.metric("Response time", f"{result['response_time_ms']} ms" if result["response_time_ms"] else "Unknown")

            rows = [
                {
                    "header": check["header"],
                    "status": check["status"].upper(),
                    "value": check.get("value", ""),
                    "note": check["note"],
                }
                for check in result["checks"]
            ]
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

            render_section_heading("Recommendations", "Missing or weak headers to address.", eyebrow="Actions")
            issues = [check["note"] for check in result["checks"] if check["status"] != "pass"]
            if issues:
                for item in issues:
                    st.warning(item)
            else:
                st.success("All checked security headers are present and look sound.")
