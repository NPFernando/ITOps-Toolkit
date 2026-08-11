from __future__ import annotations

import streamlit as st

from utils.pattern_extractor import FLAG_OPTIONS, MAX_PATTERN_LENGTH, MAX_TEXT_LENGTH, extract_matches
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


st.set_page_config(page_title="Text Pattern Extractor", layout="wide")
apply_app_shell(active_page="Text Pattern Extractor")


render_page_header(
    "Text Pattern Extractor",
    "Paste text and a regex pattern, and get back only the matching lines -- like grep -E over pasted text.",
    warning="Pattern evaluation runs with a hard timeout to protect against runaway patterns, "
    "but avoid pasting anything sensitive.",
)

with tool_form_panel("pattern_extractor"):
    render_form_intro("Enter a pattern and text", "Matching lines appear after you run it.")
    with st.form("pattern-extractor-form"):
        pattern_input = st.text_input("Pattern", placeholder=r"^error:", max_chars=MAX_PATTERN_LENGTH)
        text_input = st.text_area("Text", height=280, max_chars=MAX_TEXT_LENGTH)
        flag_names = st.multiselect("Flags", FLAG_OPTIONS)
        submitted = st.form_submit_button("Extract matching lines")

if submitted:
    st.session_state["pattern_extractor_result"] = extract_matches(pattern_input, text_input, tuple(flag_names))

result = st.session_state.get("pattern_extractor_result")

if result is None:
    render_empty_state("Ready to extract", "Matching lines appear here after you run a pattern.")

if result is not None:
    with tool_result_panel("pattern_extractor_result_panel", related_to="pattern_extractor"):
        render_section_heading("Matching lines", f"{result['match_count']} line(s) matched.")
        if not result["ok"]:
            st.error(result["error"])
        elif not result["matching_lines"]:
            st.info("No matching lines found.")
        else:
            rows = [
                {
                    "Line #": m["line_number"],
                    "Line": m["line"],
                    "Groups": ", ".join(g for g in m["groups"] if g is not None) or "-",
                }
                for m in result["matching_lines"]
            ]
            st.dataframe(display_rows_frame(rows), width="stretch", hide_index=True)
            if result["truncated"]:
                st.caption(f"Showing the first {result['match_count']} matching lines.")
