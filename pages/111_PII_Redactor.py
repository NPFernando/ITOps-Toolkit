from __future__ import annotations

import streamlit as st

from utils.pii_redactor import LABELS, MAX_INPUT_LENGTH, redact
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


st.set_page_config(page_title="PII Redactor", layout="wide")
apply_app_shell(active_page="PII Redactor")


render_page_header(
    "PII Redactor",
    "Redact common sensitive-looking patterns from pasted text before sharing it in a ticket, log, or chat.",
    warning="Regex-based heuristics, not a real PII detector -- it will miss context-dependent PII (a bare name, an address) and can false-positive on numbers that only look like a credit card or SSN. Review the output before sharing.",
)

with tool_form_panel("pii_redactor"):
    render_form_intro("Paste text and choose what to redact", "Select one or more pattern types to replace with redaction tokens.")
    with st.form("pii-redactor-form"):
        text_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="Contact alice@example.com or 555-123-4567.")
        selected = st.multiselect("Redact", list(LABELS.keys()), default=list(LABELS.keys()), format_func=lambda k: LABELS[k])
        submitted = st.form_submit_button("Redact", use_container_width=True)

if submitted:
    st.session_state["pii_redactor_result"] = redact(text_input, selected)

result = st.session_state.get("pii_redactor_result")

if result is None:
    render_empty_state("Ready to redact", "The redacted text appears here.")
    render_status_note("Awaiting text input", "Paste text, choose pattern types, and submit to redact detected matches.", tone="neutral")

if result is not None:
    with tool_result_panel("pii_redactor_result_panel", related_to="pii_redactor"):
        render_section_heading("Redacted text", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
            render_status_note("Redaction failed", "Fix the input or redaction selections, then run again.", tone="warning")
        else:
            st.code(result["output"], language=None)
            counts = {LABELS[k]: v for k, v in result["counts"].items() if v > 0}
            if counts:
                st.caption("Redacted: " + ", ".join(f"{label} ({count})" for label, count in counts.items()))
            render_status_note("Redaction complete", f"Applied {sum(result['counts'].values())} replacement(s).", tone="success")
