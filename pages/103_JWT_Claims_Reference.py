from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.jwt_claims_reference import search_jwt_claims
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


_baseline = start_page_baseline("JWT Claims Reference")
st.set_page_config(page_title="JWT Claims Reference", layout="wide")
apply_app_shell(active_page="JWT Claims Reference")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "JWT Claims Reference",
    "Look up what a JWT claim name means -- registered (RFC 7519) claims plus common OAuth 2.0/OpenID Connect conventions.",
)

with tool_form_panel("jwt_claims_reference"):
    render_form_intro("Search claims", "Search by claim key, name, or keyword.")
    with st.form("jwt-claims-reference-form"):
        query_input = st.text_input("Search", placeholder="exp, subject, oauth...")
        submitted = st.form_submit_button("Search claims", use_container_width=True)

if submitted:
    st.session_state["jwt_claims_query"] = query_input.strip()
    st.session_state["jwt_claims_submitted"] = True

if not st.session_state.get("jwt_claims_submitted", False):
    render_empty_state("Ready to search", "Matching JWT claim definitions appear here.")
    render_status_note(
        "Awaiting claim search",
        "Enter a claim key or keyword, then select Search claims to review matching definitions.",
        tone="neutral",
    )
else:
    query = st.session_state.get("jwt_claims_query", "")
    results = search_jwt_claims(query)
    with tool_result_panel("jwt_claims_reference_result", related_to="jwt_claims_reference"):
        render_section_heading("Search outcome", f"{len(results)} matching claim(s).")
        if results:
            render_status_note(
                "Matching claims found",
                f"Found {len(results)} claim definition(s) for the current search.",
                tone="success",
            )
            st.table([{"Claim": entry.claim, "Name": entry.name, "Category": entry.category, "Description": entry.description} for entry in results])
        else:
            render_status_note(
                "No claims matched this search",
                "Try a broader query such as exp, subject, issuer, or oauth.",
                tone="warning",
            )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
