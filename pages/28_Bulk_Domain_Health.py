from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.bulk_domain_health import MAX_DOMAINS_PER_BATCH, parse_domain_list, run_bulk_health_check
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_download_panel,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Bulk Domain Health", layout="wide")
apply_app_shell(active_page="Bulk Domain Health")


render_page_header(
    "Bulk Domain Health",
    "Run the Domain Health Checker's core checks across a list of public domains at once.",
    warning="Do not upload private hostnames or sensitive customer data.",
)

with tool_form_panel("bulk_domain_health"):
    render_form_intro(
        "Upload or paste domains",
        f"One domain per line, or a CSV with the domain as the first column. Checks up to {MAX_DOMAINS_PER_BATCH} domains per run.",
    )
    with st.form("bulk-domain-health-form"):
        uploaded_file = st.file_uploader("CSV or text file", type=["csv", "txt"])
        pasted_text = st.text_area("Or paste domains here (one per line)", height=140, placeholder="example.com\nexample.org")
        include_dmarc = st.checkbox("Include DMARC check", value=True)
        submitted = st.form_submit_button("Run bulk check")

if not submitted:
    render_empty_state("Ready for a domain list", "Per-domain risk scores and status appear here after the batch check completes.")

if submitted:
    raw_text = uploaded_file.getvalue().decode("utf-8", errors="ignore") if uploaded_file is not None else ""
    domains = parse_domain_list(raw_text) or parse_domain_list(pasted_text)

    if not domains:
        st.error("Upload a file or paste at least one domain.")
    else:
        truncated = len(domains) > MAX_DOMAINS_PER_BATCH
        with st.spinner(f"Checking {min(len(domains), MAX_DOMAINS_PER_BATCH)} domains..."):
            results = run_bulk_health_check(domains, include_dmarc=include_dmarc)

        with tool_result_panel("bulk_domain_health_result"):
            render_section_heading("Batch results", eyebrow="Result")
            if truncated:
                st.warning(f"{len(domains)} domains were provided; only the first {MAX_DOMAINS_PER_BATCH} were checked.")

            frame = pd.DataFrame(results)
            st.dataframe(frame, width="stretch", hide_index=True)

            healthy = sum(1 for r in results if r["risk_status"] == "Healthy")
            warning = sum(1 for r in results if r["risk_status"] == "Warning")
            critical = sum(1 for r in results if r["risk_status"] == "Critical")
            errored = sum(1 for r in results if r["risk_status"] == "Unknown")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Healthy", healthy)
            m2.metric("Warning", warning)
            m3.metric("Critical", critical)
            m4.metric("Errored", errored)

        csv_data = frame.to_csv(index=False).encode("utf-8")
        with tool_download_panel("bulk_domain_health_export"):
            render_section_heading("Export", "Download the current in-memory results.", eyebrow="Downloads")
            st.download_button("Download results as CSV", csv_data, file_name="bulk-domain-health.csv", mime="text/csv")
