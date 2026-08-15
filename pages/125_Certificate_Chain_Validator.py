from __future__ import annotations

import streamlit as st

from utils.cert_chain_validator import MAX_INPUT_LENGTH, validate_chain_order
from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("Certificate Chain Validator")
st.set_page_config(page_title="Certificate Chain Validator", layout="wide")
apply_app_shell(active_page="Certificate Chain Validator")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Certificate Chain Validator",
    "Check that a pasted PEM certificate bundle is a correctly ordered, cryptographically linked chain.",
    warning="Checks name matching and signature verification between each adjacent pair -- not full trust-path validation (no CA trust store, revocation, or expiry policy checks).",
)

with tool_form_panel("cert_chain_validator"):
    render_form_intro("Paste a PEM certificate chain", "Leaf certificate first, then each issuer in order.")
    with st.form("cert-chain-validator-form"):
        pem_input = st.text_area("Certificate chain", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----")
        submitted = st.form_submit_button("Validate chain", use_container_width=True)

if submitted:
    st.session_state["cert_chain_validator_result"] = validate_chain_order(pem_input)

result = st.session_state.get("cert_chain_validator_result")

if result is None:
    render_empty_state("Ready to validate", "Chain ordering and signature verification results appear here.")
    render_status_note("Awaiting certificate input", "Paste a PEM chain and run validation to verify order and signatures.", tone="neutral")

if result is not None:
    with tool_result_panel("cert_chain_validator_result_panel", related_to="cert_chain_validator"):
        render_section_heading("Chain validation", eyebrow="Result")
        if not result["ok"]:
            render_status_note(
                "Cannot validate certificate chain yet",
                f"{result['error']} Provide at least two valid PEM certificates ordered from leaf to issuer, then validate again.",
                tone="warning",
            )
        else:
            if result["chain_valid"]:
                render_status_note("Validation complete", "Chain ordering and signatures are consistent across all certificate links.", tone="success")
            else:
                render_status_note("Chain needs attention", "At least one certificate link failed name matching or signature verification.", tone="warning")
            st.table(
                [
                    {
                        "Link": f"{link['from_index']} -> {link['to_index']}",
                        "Names match": "Yes" if link["names_match"] else "No",
                        "Signature verified": {True: "Yes", False: "No", None: "N/A"}[link["signature_verified"]],
                        "Note": link["note"],
                    }
                    for link in result["links"]
                ]
            )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
