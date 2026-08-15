from __future__ import annotations

import streamlit as st

from utils.regex_reference import search_patterns
from utils.ui import (
    apply_app_shell,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Regex Cheat Sheet", layout="wide")
apply_app_shell(active_page="Regex Cheat Sheet")


render_page_header(
    "Regex Cheat Sheet",
    "Common regex patterns to start from -- email, IPv4/IPv6, URL, phone number, UUID, hex color, and more.",
)

with tool_form_panel("regex_cheat_sheet"):
    render_form_intro("Search regex patterns", "Search by name, pattern, or keyword.")
    query = st.text_input("Search", placeholder="email, IPv4, hex color, slug...")

results = search_patterns(query)
with tool_result_panel("regex_cheat_sheet_result", related_to="regex_cheat_sheet"):
    render_section_heading("Regex patterns", f"{len(results)} matching pattern(s).", eyebrow="Result")
    if results:
        if query.strip():
            render_status_note(
                "Filtered results ready",
                f"{len(results)} pattern(s) match your search query.",
                tone="success",
            )
        else:
            render_status_note(
                "Showing full reference",
                "All built-in regex patterns are visible. Use Search to narrow the list.",
                tone="neutral",
            )
        st.table(
            [
                {"Name": entry.name, "Pattern": entry.pattern, "Description": entry.description}
                for entry in results
            ]
        )
    else:
        st.info("No matching patterns found for that search.")
        render_status_note(
            "No pattern matches",
            "Try a broader keyword, remove punctuation, or clear the search box.",
            tone="warning",
        )
