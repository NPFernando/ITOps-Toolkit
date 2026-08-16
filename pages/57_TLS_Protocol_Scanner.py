from __future__ import annotations

import streamlit as st

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
from utils.tls_scanner import MAX_PORT, scan_tls
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    run_validated_lookup,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="TLS Protocol Scanner", layout="wide")
apply_app_shell(active_page="TLS Protocol Scanner")


render_page_header(
    "TLS Protocol Scanner",
    "Connect to a host and report which TLS protocol versions it accepts -- a lightweight SSL Labs-style check.",
    warning="Only scan hosts you own or have permission to test.",
)

render_status_note(
    "SSLv3/TLSv1.0/TLSv1.1 aren't testable here",
    "This environment's TLS library has those three protocol versions compiled out entirely, so they can't be tested regardless of what the target server supports. They're reported as \"Not testable\" -- distinct from \"Rejected\", which means the server itself declined the connection.",
    tone="neutral",
)

_STATUS_LABELS = {
    "accepted": "Accepted",
    "rejected": "Rejected",
    "not_testable": "Not testable",
    "connection_error": "Connection error",
}

with tool_form_panel("tls_scanner"):
    render_form_intro("Scan a host", "Enter a host and port to probe.")
    with st.form("tls-scanner-form"):
        host = st.text_input("Host", placeholder="example.com", max_chars=MAX_DOMAIN_LENGTH)
        port = st.number_input("Port", min_value=1, max_value=MAX_PORT, value=443, step=1)
        submitted = st.form_submit_button("Scan")

if submitted:
    def _validate() -> str | None:
        if not normalize_domain(host):
            return "Enter a host name."
        return None

    run_validated_lookup(
        "tls_scanner",
        _validate,
        lambda: scan_tls(host, int(port)),
        spinner_text="Probing TLS versions...",
    )

validation_error = st.session_state.get("tls_scanner_validation_error")
stored = st.session_state.get("tls_scanner_result")

if validation_error is None and stored is None:
    render_empty_state("Ready to scan", "Accepted, rejected, and untestable protocol versions appear here after a scan.")

if validation_error is not None:
    st.error(validation_error)

if stored is not None:
    with tool_result_panel("tls_scanner_result", related_to="tls_scanner"):
        render_section_heading(f"{stored['host']}:{stored['port']}", eyebrow="Result")
        if not stored["ok"]:
            st.error(stored["error"])
        else:
            st.table(
                [
                    {"Protocol": row["version"], "Status": _STATUS_LABELS[row["status"]], "Detail": row["detail"]}
                    for row in stored["results"]
                ]
            )
