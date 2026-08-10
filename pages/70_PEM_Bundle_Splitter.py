from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.pem_bundle_splitter import MAX_INPUT_LENGTH, split_pem_bundle
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="PEM Bundle Splitter", layout="wide")
apply_app_shell(active_page="PEM Bundle Splitter")


render_page_header(
    "PEM Bundle Splitter",
    "Paste a multi-certificate PEM bundle (e.g. a full chain file) and see each certificate's subject, issuer, and expiration separately.",
)

with tool_form_panel("pem_bundle_splitter"):
    render_form_intro("Paste a PEM bundle", "One or more PEM-encoded certificates, back to back.")
    with st.form("pem-bundle-splitter-form"):
        pem_input = st.text_area("Certificate bundle (PEM)", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----")
        submitted = st.form_submit_button("Split")

if submitted:
    st.session_state["pem_bundle_splitter_result"] = split_pem_bundle(pem_input)

result = st.session_state.get("pem_bundle_splitter_result")

if result is None:
    render_empty_state("Ready to split", "Each certificate's subject, issuer, and expiration appear here.")

if result is not None:
    with tool_result_panel("pem_bundle_splitter_result_panel", related_to="pem_bundle_splitter"):
        render_section_heading("Certificates found", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.caption(f"{len(result['certificates'])} certificate(s) found.")
            rows = [
                {
                    "#": c["index"],
                    "Subject": c["subject"],
                    "Issuer": c["issuer"],
                    "Valid from": c["not_valid_before"],
                    "Expires": c["not_valid_after"],
                    "Status": "Not yet valid" if c["is_not_yet_valid"] else "Expired" if c["is_expired"] else "Valid",
                }
                for c in result["certificates"]
            ]
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            if any(c["is_expired"] for c in result["certificates"]):
                st.warning("At least one certificate in this bundle has expired.")
            if any(c["is_not_yet_valid"] for c in result["certificates"]):
                st.warning("At least one certificate in this bundle is not yet valid -- its validity period starts in the future.")
