from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dkim_tools import MAX_SELECTOR_LENGTH, lookup_dkim
from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
from utils.text_tools import validate_length
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="DKIM Selector Lookup", layout="wide")
apply_app_shell(active_page="DKIM Selector Lookup")


render_page_header(
    "DKIM Selector Lookup",
    "Look up a DKIM TXT record for a domain and selector, and parse its public key/algorithm fields.",
)

with tool_form_panel("dkim_lookup"):
    render_form_intro("Look up a selector", "DKIM records are published per-selector, so both the domain and the selector are required.")
    with st.form("dkim-form"):
        domain_col, selector_col = st.columns(2)
        domain = domain_col.text_input("Domain", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        selector = selector_col.text_input("Selector", placeholder="google, selector1, default...", max_chars=MAX_SELECTOR_LENGTH)
        submitted = st.form_submit_button("Look up")

if not submitted:
    render_empty_state(
        "Ready to look up a DKIM selector",
        "Enter both the domain and the DKIM selector -- the selector isn't guessable from DNS alone, so it must come from mail server config or a Received/DKIM-Signature header.",
    )

if submitted:
    ok_domain, error_domain = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
    ok_selector, error_selector = validate_length(selector, MAX_SELECTOR_LENGTH, "Selector")
    normalized = normalize_domain(domain)
    if not ok_domain:
        st.error(error_domain)
    elif not ok_selector:
        st.error(error_selector)
    elif not normalized:
        st.error("Enter a domain name.")
    else:
        result = lookup_dkim(normalized, selector)
        with tool_result_panel("dkim_result", related_to="dkim_lookup"):
            render_section_heading("DKIM record", f"Queried {result['query_name'] or 'the selector record'}.")
            if result["status"] == "Healthy":
                st.success(result["status"])
            elif result["ok"]:
                st.warning(result["status"])
                st.warning(result["error"])
            else:
                st.error(result["status"])
                st.error(result["error"])

            if result["ok"]:
                rows = [{"field": key, "value": value} for key, value in result["fields"].items()]
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

                with st.expander("Raw record"):
                    st.code(result["raw_value"])
