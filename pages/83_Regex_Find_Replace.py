from __future__ import annotations

import streamlit as st

from utils.regex_replace import FLAG_OPTIONS, MAX_PATTERN_LENGTH, MAX_REPLACEMENT_LENGTH, MAX_TEXT_LENGTH, find_and_replace
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Regex Find & Replace", layout="wide")
apply_app_shell(active_page="Regex Find & Replace")


render_page_header(
    "Regex Find & Replace",
    "Paste text and a regex pattern with a replacement (backreferences like \\1 supported), and see the substituted output.",
    warning="Pattern evaluation runs with a hard timeout to protect against runaway patterns, "
    "but avoid pasting anything sensitive.",
)

with tool_form_panel("regex_replace"):
    render_form_intro("Enter a pattern, replacement, and text", "The substituted output appears after you run it.")
    with st.form("regex-replace-form"):
        pattern_input = st.text_input("Pattern", placeholder=r"(\w+) (\w+)", max_chars=MAX_PATTERN_LENGTH)
        replacement_input = st.text_input("Replacement", placeholder=r"\2 \1", max_chars=MAX_REPLACEMENT_LENGTH)
        text_input = st.text_area("Text", height=220, max_chars=MAX_TEXT_LENGTH)
        flag_names = st.multiselect("Flags", FLAG_OPTIONS)
        submitted = st.form_submit_button("Replace")

if submitted:
    st.session_state["regex_replace_result"] = find_and_replace(pattern_input, replacement_input, text_input, tuple(flag_names))

result = st.session_state.get("regex_replace_result")

if result is None:
    render_empty_state("Ready to replace", "The substituted output appears here after you run it.")

if result is not None:
    with tool_result_panel("regex_replace_result_panel", related_to="regex_replace"):
        render_section_heading("Result", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.caption(f"{result['replacement_count']} replacement(s) made.")
            st.text_area("Output", value=result["output"], height=220)
