from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dns_propagation import PUBLIC_RESOLVERS, SUPPORTED_RECORD_TYPES, check_propagation
from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
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


st.set_page_config(page_title="DNS Propagation Checker", layout="wide")
apply_app_shell(active_page="DNS Propagation Checker")


render_page_header(
    "DNS Propagation Checker",
    f"Query the same record across {len(PUBLIC_RESOLVERS)} public resolvers ({', '.join(name for name, _ in PUBLIC_RESOLVERS)}) to catch propagation lag or mismatched answers.",
    warning="Do not enter private hostnames or sensitive customer data.",
)

with tool_form_panel("dns_propagation"):
    render_form_intro("Check propagation", "Choose a domain and record type to query across multiple public resolvers.")
    with st.form("dns-propagation-form"):
        domain = st.text_input("Domain", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        record_type = st.selectbox("Record type", SUPPORTED_RECORD_TYPES)
        submitted = st.form_submit_button("Check propagation")

if submitted:
    def _validate() -> str | None:
        ok, error = validate_length(domain, MAX_DOMAIN_LENGTH, "Domain")
        if not ok:
            return error
        if not normalize_domain(domain):
            return "Enter a domain name."
        return None

    run_validated_lookup(
        "dns_propagation",
        _validate,
        lambda: {"record_type": record_type, "data": check_propagation(normalize_domain(domain), record_type)},
        spinner_text="Querying resolvers...",
    )

validation_error = st.session_state.get("dns_propagation_validation_error")
stored = st.session_state.get("dns_propagation_result")

if validation_error is None and stored is None:
    render_empty_state("Ready to check propagation", "Per-resolver answers and a consistency check appear after the query.")

if validation_error is not None:
    st.error(validation_error)

if stored is not None:
    result = stored["data"]
    with tool_result_panel("dns_propagation_result", related_to="dns_propagation"):
        render_section_heading(f"{stored['record_type']} records across resolvers", "Same query sent directly to each public resolver.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            if result["consistent"] is True:
                st.success("Resolvers agree -- answers are consistent.")
            elif result["consistent"] is False:
                st.warning("Resolvers disagree -- this may indicate propagation lag or a recent change.")
            else:
                st.warning("No resolver returned an answer.")

            for entry in result["resolvers"]:
                with st.expander(f"{entry['resolver_name']} ({entry['resolver_ip']}) -- {entry['status']}", expanded=True):
                    if entry["ok"]:
                        st.dataframe(pd.DataFrame(entry["records"]), width="stretch", hide_index=True)
                    else:
                        st.error(entry["error"])
