from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dkim_tools import MAX_SELECTOR_LENGTH, lookup_dkim
from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
from utils.text_tools import validate_length
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


st.set_page_config(page_title="DKIM Selector Lookup", layout="wide")
apply_app_shell(active_page="DKIM Selector Lookup")


render_page_header(
    "DKIM Selector Lookup",
    "Look up a DKIM TXT record for a domain and selector, and parse its public key/algorithm fields.",
    warning="Do not enter private hostnames or sensitive customer data.",
)

with tool_form_panel("dkim_lookup"):
    render_form_intro("Look up a selector", "DKIM records are published per-selector, so both the domain and the selector are required.")
    with st.form("dkim-form"):
        domain_col, selector_col = st.columns(2)
        domain = domain_col.text_input("Domain", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        selector = selector_col.text_input("Selector", placeholder="google, selector1, default...", max_chars=MAX_SELECTOR_LENGTH)
        submitted = st.form_submit_button("Look up selector", use_container_width=True)

if submitted:
    normalized_domain = normalize_domain(domain)
    normalized_selector = selector.strip()

    def _validate() -> str | None:
        ok_domain, error_domain = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
        if not ok_domain:
            return error_domain
        ok_selector, error_selector = validate_length(selector, MAX_SELECTOR_LENGTH, "Selector")
        if not ok_selector:
            return error_selector
        if not normalized_domain:
            return "Enter a domain name."
        if not normalized_selector:
            return "Enter a DKIM selector."
        return None

    run_validated_lookup(
        "dkim_lookup",
        _validate,
        lambda: lookup_dkim(normalized_domain, normalized_selector),
        spinner_text="Querying DKIM record...",
    )

validation_error = st.session_state.get("dkim_lookup_validation_error")
result = st.session_state.get("dkim_lookup_result")

if validation_error is None and result is None:
    render_empty_state(
        "Ready to look up a DKIM selector",
        "Enter both the domain and the DKIM selector -- the selector isn't guessable from DNS alone, so it must come from mail server config or a Received/DKIM-Signature header.",
    )

if validation_error is not None:
    render_failure_note(
        "DKIM input",
        validation_error,
        remediation="Provide a valid public domain and DKIM selector, then retry the lookup.",
    )

if result is not None:
    with tool_result_panel("dkim_result", related_to="dkim_lookup"):
        render_section_heading("DKIM record", f"Queried {result['query_name'] or 'the selector record'}.")
        if result["status"] == "Healthy":
            render_status_note("Status: Healthy", "The selector record was found and parsed successfully.", tone="success")
        elif result["ok"]:
            render_status_note(f"Status: {result['status']}", "The selector record was found, but it needs review.", tone="warning")
            if result["error"]:
                render_failure_note(
                    "DKIM selector lookup",
                    result["error"],
                    remediation="Review the warning details, then update the selector record if needed.",
                    mode="persistent",
                )
        else:
            render_failure_note(
                f"DKIM lookup: {result['status']}",
                result["error"],
                remediation="Confirm the selector/domain and retry. If it still fails, verify DNS publication.",
            )

        if result["ok"]:
            rows = [{"field": key, "value": value} for key, value in result["fields"].items()]
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

            with st.expander("Raw record"):
                st.code(result["raw_value"])
