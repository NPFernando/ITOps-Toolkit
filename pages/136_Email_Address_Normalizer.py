from __future__ import annotations

import re

import streamlit as st

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


_EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")


def _split_addresses(raw_text: str) -> list[str]:
    normalized = raw_text.replace("\n", ",").replace(";", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def _normalize_email(address: str, strip_plus: bool, gmail_dot_canonical: bool) -> str:
    local, domain = address.split("@", 1)
    domain = domain.lower()
    local = local.lower()
    if strip_plus and "+" in local:
        local = local.split("+", 1)[0]
    if gmail_dot_canonical and domain in {"gmail.com", "googlemail.com"}:
        local = local.replace(".", "")
    return f"{local}@{domain}"


def normalize_addresses(raw_text: str, strip_plus: bool, gmail_dot_canonical: bool, dedupe: bool) -> dict[str, object]:
    parts = _split_addresses(raw_text)
    if not parts:
        return {"ok": False, "error": "Enter one or more email addresses.", "normalized": [], "invalid": []}

    normalized: list[str] = []
    invalid: list[str] = []
    for part in parts:
        if _EMAIL_RE.match(part):
            normalized.append(_normalize_email(part, strip_plus=strip_plus, gmail_dot_canonical=gmail_dot_canonical))
        else:
            invalid.append(part)

    if dedupe:
        normalized = list(dict.fromkeys(normalized))

    return {
        "ok": bool(normalized),
        "error": "No valid email addresses found." if not normalized else "",
        "normalized": normalized,
        "invalid": invalid,
    }


_baseline = start_page_baseline("Email Address Normalizer")
st.set_page_config(page_title="Email Address Normalizer", layout="wide")
apply_app_shell(active_page="Email Address Normalizer")
mark_page_baseline(_baseline, "shell-ready")

render_page_header("Email Address Normalizer", "Normalize email lists into lowercase canonical forms without storing user input.")

with tool_form_panel("email_address_normalizer"):
    render_form_intro("Paste email addresses", "Group parsing options and use one full-width action for predictable mobile handling.")
    with st.form("email-normalizer-form"):
        st.markdown('<div class="tool-panel-eyebrow">Email list input</div>', unsafe_allow_html=True)
        addresses_input = st.text_area("Email addresses", height=180, placeholder="Alice+alerts@Example.com\nbob.smith@gmail.com")
        st.markdown('<div class="tool-panel-eyebrow">Normalization options</div>', unsafe_allow_html=True)
        strip_plus = st.checkbox("Strip plus tags from local part", value=True)
        gmail_dot_canonical = st.checkbox("Canonicalize Gmail dots", value=True)
        dedupe = st.checkbox("Deduplicate normalized addresses", value=True)
        submitted = st.form_submit_button("Normalize addresses", use_container_width=True)

if submitted:
    st.session_state["email_normalizer_result"] = normalize_addresses(
        addresses_input,
        strip_plus=strip_plus,
        gmail_dot_canonical=gmail_dot_canonical,
        dedupe=dedupe,
    )

result = st.session_state.get("email_normalizer_result")
if result is None:
    render_empty_state("Ready to normalize", "Normalized email output appears here after submission.")
    render_status_note(
        "Outcome: awaiting email normalization",
        "Paste one or more addresses, choose options, then select Normalize addresses.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("email_normalizer_result_panel", related_to="email_address_normalizer"):
        render_section_heading("Normalized addresses", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: email normalization blocked", str(result["error"]), tone="warning")
        else:
            normalized = result["normalized"]
            invalid = result["invalid"]
            render_status_note(
                "Outcome: email normalization complete",
                f"Normalized {len(normalized)} address(es). Invalid entries: {len(invalid)}.",
                tone="success",
            )
            st.code("\n".join(str(item) for item in normalized), language=None)
            if invalid:
                render_status_note("Outcome: invalid entries skipped", "\n".join(str(item) for item in invalid), tone="warning")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
