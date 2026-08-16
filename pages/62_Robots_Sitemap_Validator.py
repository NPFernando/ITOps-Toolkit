from __future__ import annotations

import streamlit as st

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
from utils.robots_validator import validate_robots_txt
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


st.set_page_config(page_title="robots.txt / Sitemap Validator", layout="wide")
apply_app_shell(active_page="robots.txt / Sitemap Validator")


render_page_header(
    "robots.txt / Sitemap Validator",
    "Fetch a domain's robots.txt, validate its directive syntax, and check that its referenced sitemaps are reachable and well-formed.",
    warning="Only check domains you own or have permission to test.",
)

with tool_form_panel("robots_validator"):
    render_form_intro("Validate robots.txt", "Enter a domain to fetch and check.")
    with st.form("robots-validator-form"):
        domain = st.text_input("Domain", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        submitted = st.form_submit_button("Validate")

if submitted:
    def _validate() -> str | None:
        if not normalize_domain(domain):
            return "Enter a domain name."
        return None

    run_validated_lookup(
        "robots_validator",
        _validate,
        lambda: validate_robots_txt(domain),
        spinner_text="Fetching robots.txt...",
    )

validation_error = st.session_state.get("robots_validator_validation_error")
stored = st.session_state.get("robots_validator_result")

if validation_error is None and stored is None:
    render_empty_state("Ready to validate", "Directive issues and sitemap validity appear here after a check.")

if validation_error is not None:
    st.error(validation_error)

if stored is not None:
    with tool_result_panel("robots_validator_result", related_to="robots_validator"):
        render_section_heading(stored["domain"], eyebrow="Result")
        if not stored["ok"]:
            st.error(stored["error"])
        else:
            if not stored["issues"]:
                st.success("No syntax issues found in robots.txt.")
            else:
                st.warning(f"{len(stored['issues'])} issue(s) found:")
                for issue in stored["issues"]:
                    st.caption(f"- {issue}")

            if stored["sitemaps"]:
                st.markdown("**Sitemaps referenced:**")
                for sitemap in stored["sitemaps"]:
                    if sitemap["ok"]:
                        st.success(f"{sitemap['url']} -- {sitemap['detail']}")
                    else:
                        st.error(f"{sitemap['url']} -- {sitemap['detail']}")
            else:
                st.caption("No Sitemap: entries found in robots.txt.")
