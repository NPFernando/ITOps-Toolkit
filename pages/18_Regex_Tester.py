from __future__ import annotations

import streamlit as st

from utils.regex_tools import FLAG_OPTIONS, MAX_PATTERN_LENGTH, MAX_TEXT_LENGTH, test_regex
from utils.ui import (
    apply_app_shell,
    display_rows_frame,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Regex Tester", layout="wide")
apply_app_shell(active_page="Regex Tester")


render_page_header(
    "Regex Tester",
    "Test a regular expression against sample text and see every match, its position, and captured groups.",
    warning="Pattern evaluation runs with a hard timeout to protect against runaway patterns, "
    "but avoid pasting anything sensitive.",
)

with tool_form_panel("regex_tester"):
    render_form_intro("Enter a pattern and text", "Matches, positions, and capture groups appear after you run it.")
    with st.form("regex-form"):
        pattern_input = st.text_input("Pattern", placeholder=r"\d+", max_chars=MAX_PATTERN_LENGTH)
        text_input = st.text_area("Test text", height=180, max_chars=MAX_TEXT_LENGTH)
        flag_names = st.multiselect("Flags", FLAG_OPTIONS)
        submitted = st.form_submit_button("Run pattern")

if not submitted:
    render_empty_state("Ready to test a pattern", "Matches and capture groups appear here after you run a pattern.")

if submitted:
    result = test_regex(pattern_input, text_input, tuple(flag_names))
    with tool_result_panel("regex_result", related_to="regex_tester"):
        render_section_heading("Matches", f"{result['match_count']} match(es) found.")
        if not result["ok"]:
            st.error(result["error"])
        elif not result["matches"]:
            st.info("No matches found.")
        else:
            rows = [
                {
                    "Match": m["match"],
                    "Start": m["start"],
                    "End": m["end"],
                    "Groups": ", ".join(g for g in m["groups"] if g is not None) or "-",
                }
                for m in result["matches"]
            ]
            st.dataframe(display_rows_frame(rows), width="stretch", hide_index=True)
            if result["truncated"]:
                st.caption(f"Showing the first {result['match_count']} matches.")
