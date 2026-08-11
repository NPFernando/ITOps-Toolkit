from __future__ import annotations

import streamlit as st

from utils.jwt_claims_reference import search_jwt_claims
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="JWT Claims Reference", layout="wide")
apply_app_shell(active_page="JWT Claims Reference")


render_page_header(
    "JWT Claims Reference",
    "Look up what a JWT claim name means -- registered (RFC 7519) claims plus common OAuth 2.0/OpenID Connect conventions.",
)

with tool_form_panel("jwt_claims_reference"):
    render_form_intro("Search claims", "Search by claim key, name, or keyword.")
    query = st.text_input("Search", placeholder="exp, subject, oauth...")

results = search_jwt_claims(query)
with tool_result_panel("jwt_claims_reference_result", related_to="jwt_claims_reference"):
    render_section_heading("JWT claims", f"{len(results)} matching claim(s).")
    if results:
        st.table([{"Claim": entry.claim, "Name": entry.name, "Category": entry.category, "Description": entry.description} for entry in results])
    else:
        st.info("No JWT claims matched that search.")
