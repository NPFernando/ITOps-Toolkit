from __future__ import annotations

import streamlit as st

from utils.email_record_builder import (
    DMARC_ALIGNMENT_MODES,
    DMARC_POLICIES,
    SPF_ALL_MECHANISMS,
    build_dkim_record,
    build_dmarc_record,
    build_spf_record,
)
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Email Record Builder", layout="wide")
apply_app_shell(active_page="Email Record Builder")


render_page_header(
    "Email Record Builder",
    "Build SPF, DMARC, and DKIM TXT record strings from simple inputs -- the reverse of the existing checks.",
)

spf_tab, dmarc_tab, dkim_tab = st.tabs(["SPF", "DMARC", "DKIM"])

with spf_tab:
    with tool_form_panel("spf_builder"):
        render_form_intro("Build an SPF record", "List authorized senders; the record authorizes exactly what you add here.")
        with st.form("spf-form"):
            includes_raw = st.text_area("Include domains (one per line)", placeholder="_spf.google.com\nsendgrid.net", height=100)
            ip4_raw = st.text_area("IPv4 addresses/CIDRs (one per line)", placeholder="203.0.113.10\n198.51.100.0/24", height=80)
            ip6_raw = st.text_area("IPv6 addresses/CIDRs (one per line)", height=80)
            all_mechanism = st.selectbox("All mechanism", list(SPF_ALL_MECHANISMS), format_func=lambda m: f"{m} -- {SPF_ALL_MECHANISMS[m]}")
            spf_submitted = st.form_submit_button("Build SPF record")

    if spf_submitted:
        includes = [line for line in includes_raw.splitlines() if line.strip()]
        ip4 = [line for line in ip4_raw.splitlines() if line.strip()]
        ip6 = [line for line in ip6_raw.splitlines() if line.strip()]
        result = build_spf_record(includes, ip4, ip6, all_mechanism)
        with tool_result_panel("spf_result", related_to="email_record_builder"):
            render_section_heading("SPF record", "Publish this as a TXT record at the domain root.")
            if not result["ok"]:
                st.error(result["error"])
            else:
                st.code(result["record"], language=None)
                for warning in result["warnings"]:
                    st.warning(warning)

with dmarc_tab:
    with tool_form_panel("dmarc_builder"):
        render_form_intro("Build a DMARC record", "Publish the result at _dmarc.<domain>.")
        with st.form("dmarc-form"):
            policy = st.selectbox("Policy (p=)", DMARC_POLICIES, index=0)
            subdomain_policy = st.selectbox("Subdomain policy (sp=)", ("Same as policy", *DMARC_POLICIES))
            rua_raw = st.text_input("Aggregate report addresses (rua, comma-separated)", placeholder="dmarc-reports@example.com")
            ruf_raw = st.text_input("Forensic report addresses (ruf, comma-separated, optional)")
            pct = st.slider("Percentage of mail subject to policy (pct=)", 0, 100, 100)
            adkim_col, aspf_col = st.columns(2)
            adkim = adkim_col.selectbox("DKIM alignment (adkim=)", DMARC_ALIGNMENT_MODES)
            aspf = aspf_col.selectbox("SPF alignment (aspf=)", DMARC_ALIGNMENT_MODES)
            dmarc_submitted = st.form_submit_button("Build DMARC record")

    if dmarc_submitted:
        rua = [addr.strip() for addr in rua_raw.split(",") if addr.strip()]
        ruf = [addr.strip() for addr in ruf_raw.split(",") if addr.strip()]
        sp = None if subdomain_policy == "Same as policy" else subdomain_policy
        result = build_dmarc_record(policy, rua, ruf, sp, pct, adkim, aspf)
        with tool_result_panel("dmarc_result", related_to="email_record_builder"):
            render_section_heading("DMARC record", "Publish this as a TXT record at _dmarc.<domain>.")
            if not result["ok"]:
                st.error(result["error"])
            else:
                st.code(result["record"], language=None)
                for warning in result["warnings"]:
                    st.warning(warning)

with dkim_tab:
    with tool_form_panel("dkim_builder"):
        render_form_intro("Format a DKIM record", "Paste an existing public key (this does not generate a key pair) to get the correctly formatted TXT record.")
        with st.form("dkim-builder-form"):
            domain_col, selector_col = st.columns(2)
            domain = domain_col.text_input("Domain", placeholder="example.com")
            selector = selector_col.text_input("Selector", placeholder="default")
            public_key = st.text_area("Public key (base64, PEM headers/newlines are stripped automatically)", height=150)
            dkim_submitted = st.form_submit_button("Build DKIM record")

    if dkim_submitted:
        result = build_dkim_record(selector, domain, public_key)
        with tool_result_panel("dkim_builder_result", related_to="email_record_builder"):
            render_section_heading("DKIM record", "Publish this TXT record at the shown name.")
            if not result["ok"]:
                st.error(result["error"])
            else:
                st.caption(f"Record name: {result['query_name']}")
                st.code(result["record"], language=None)
                for warning in result["warnings"]:
                    st.warning(warning)
