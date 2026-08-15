from __future__ import annotations

import streamlit as st

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
from utils.robots_validator import validate_robots_txt
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    run_validated_lookup,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="robots.txt / Sitemap Validator", layout="wide")
apply_app_shell(active_page="robots.txt / Sitemap Validator")

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
    "robots.txt / Sitemap Validator",
    "Fetch a domain's robots.txt, validate its directive syntax, and check that its referenced sitemaps are reachable and well-formed.",
    warning="Only check domains you own or have permission to test.",
)

with tool_form_panel("robots_validator"):
    render_form_intro("Validate robots.txt", "Enter a domain to fetch and check.")
    with st.form("robots-validator-form"):
        domain = st.text_input("Domain", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        submitted = st.form_submit_button("Validate", use_container_width=True)

if submitted:
    normalized_domain = normalize_domain(domain)

    def _validate() -> str | None:
        if not normalized_domain:
            return "Enter a domain name."
        return None

    run_validated_lookup(
        "robots_validator",
        _validate,
        lambda: validate_robots_txt(normalized_domain),
        spinner_text="Fetching robots.txt...",
    )

validation_error = st.session_state.get("robots_validator_validation_error")
stored = st.session_state.get("robots_validator_result")

if validation_error is None and stored is None:
    render_empty_state("Ready to validate", "Directive issues and sitemap validity appear here after a check.")

if validation_error is not None:
    render_failure_note(
        "robots.txt input",
        validation_error,
        remediation="Enter a valid domain name and run the validation again.",
    )

if stored is not None:
    with tool_result_panel("robots_validator_result", related_to="robots_validator"):
        render_section_heading(stored["domain"], eyebrow="Result")
        if not stored["ok"]:
            render_failure_note(
                "robots.txt validation",
                stored["error"],
                remediation="Retry the check. If it keeps failing, verify robots.txt is publicly reachable.",
            )
        else:
            if not stored["issues"]:
                render_status_note("No syntax issues found", "robots.txt directives are syntactically valid.", tone="success")
            else:
                render_status_note(
                    "Syntax issues found",
                    f"{len(stored['issues'])} robots.txt directive issue(s) require review.",
                    tone="warning",
                )
                st.dataframe(
                    [{"Issue": issue} for issue in stored["issues"]],
                    width="stretch",
                    hide_index=True,
                )

            if stored["sitemaps"]:
                render_section_heading("Sitemap checks", f"{len(stored['sitemaps'])} sitemap reference(s) found.", eyebrow="Sitemaps")
                st.dataframe(
                    [
                        {
                            "Sitemap URL": sitemap["url"],
                            "Status": "OK" if sitemap["ok"] else "Error",
                            "Detail": sitemap["detail"],
                        }
                        for sitemap in stored["sitemaps"]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            else:
                render_status_note(
                    "No sitemap references",
                    "No Sitemap: entries were found in robots.txt.",
                    tone="neutral",
                )
