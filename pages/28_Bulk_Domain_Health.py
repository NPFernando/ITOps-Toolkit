from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.bulk_domain_health import MAX_DOMAINS_PER_BATCH, parse_domain_list, run_bulk_health_check
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_download_panel,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("Bulk Domain Health")
st.set_page_config(page_title="Bulk Domain Health", layout="wide")
apply_app_shell(active_page="Bulk Domain Health")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Bulk Domain Health",
    "Run the Domain Health Checker's core checks across a list of public domains at once.",
    warning="Do not upload private hostnames or sensitive customer data.",
)

with tool_form_panel("bulk_domain_health"):
    render_form_intro(
        "Run a bulk domain check",
        f"Upload or paste one public domain per line, or provide a CSV with the domain in the first column. Checks up to {MAX_DOMAINS_PER_BATCH} domains per run.",
    )
    with st.form("bulk-domain-health-form"):
        uploaded_file = st.file_uploader("CSV or text file", type=["csv", "txt"])
        pasted_text = st.text_area("Or paste domains here (one per line)", height=140, placeholder="example.com\nexample.org")
        include_dmarc = st.checkbox("Include DMARC check", value=True)
        submitted = st.form_submit_button("Run checks", use_container_width=True)

if submitted:
    # Stored in session_state (not rendered directly here) because the export
    # panel's download button below triggers its own rerun -- on that rerun
    # `submitted` is False again, which would otherwise collapse this whole
    # results section right after the click (and, for the validation error,
    # would otherwise vanish the instant any widget outside this st.form is
    # touched, e.g. the sidebar's quick-search box).
    raw_text = uploaded_file.getvalue().decode("utf-8", errors="ignore") if uploaded_file is not None else ""
    domains = parse_domain_list(raw_text) or parse_domain_list(pasted_text)

    if not domains:
        st.session_state["bulk_domain_health_validation_error"] = "Upload a file or paste at least one domain."
        st.session_state["bulk_domain_health_state"] = None
    else:
        truncated = len(domains) > MAX_DOMAINS_PER_BATCH
        with st.spinner(f"Checking {min(len(domains), MAX_DOMAINS_PER_BATCH)} domains..."):
            results = run_bulk_health_check(domains, include_dmarc=include_dmarc)
        st.session_state["bulk_domain_health_validation_error"] = None
        st.session_state["bulk_domain_health_state"] = {"results": results, "truncated": truncated, "total_domains": len(domains)}

validation_error = st.session_state.get("bulk_domain_health_validation_error")
state = st.session_state.get("bulk_domain_health_state")

if validation_error is None and state is None:
    render_empty_state("Ready for a domain list", "Per-domain risk scores and status appear here after the batch check completes.")

if validation_error is not None:
    st.error(validation_error)

if state is not None:
    results = state["results"]
    with tool_result_panel("bulk_domain_health_result"):
        render_section_heading("Batch results", eyebrow="Result")
        if state["truncated"]:
            st.warning(f"{state['total_domains']} domains were provided; only the first {MAX_DOMAINS_PER_BATCH} were checked.")

        csv_data = frame.to_csv(index=False).encode("utf-8")
        with tool_download_panel("bulk_domain_health_export", related_to="bulk_domain_health"):
            render_section_heading("Export", "Download the current in-memory results.", eyebrow="Downloads")
            st.download_button("Download results as CSV", csv_data, file_name="bulk-domain-health.csv", mime="text/csv")
