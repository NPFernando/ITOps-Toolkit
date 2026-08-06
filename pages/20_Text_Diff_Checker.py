from __future__ import annotations

from html import escape

import streamlit as st

from utils.diff_tools import MAX_INPUT_LENGTH, compare_text
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Text Diff Checker", layout="wide")
apply_app_shell(active_page="Text Diff Checker")


render_page_header(
    "Text Diff Checker",
    "Compare two blocks of text and see exactly what changed, line by line.",
)

with tool_form_panel("text_diff"):
    render_form_intro("Paste two versions", "The original on the left, the changed version on the right.")
    with st.form("diff-form"):
        c1, c2 = st.columns(2)
        with c1:
            original_input = st.text_area("Original", height=260, max_chars=MAX_INPUT_LENGTH)
        with c2:
            changed_input = st.text_area("Changed", height=260, max_chars=MAX_INPUT_LENGTH)
        ignore_whitespace = st.checkbox("Ignore leading/trailing whitespace per line", value=False)
        submitted = st.form_submit_button("Compare")

if not submitted:
    render_empty_state("Ready to compare", "A line-by-line diff appears here after you compare two versions.")

if submitted:
    result = compare_text(original_input, changed_input, ignore_whitespace)
    with tool_result_panel("diff_result", related_to="text_diff_checker"):
        render_section_heading("Diff", f"{result['added']} added, {result['removed']} removed.")
        if not result["ok"]:
            st.error(result["error"])
        elif not result["lines"]:
            st.info("Both inputs are empty.")
        else:
            c1, c2 = st.columns(2)
            c1.metric("Similarity", f"{result['similarity']}%")
            c2.metric("Lines changed", result["added"] + result["removed"])

            colors = {
                "added": ("rgba(34, 186, 79, 0.16)", "+"),
                "removed": ("rgba(255, 106, 19, 0.16)", "-"),
                "equal": ("transparent", " "),
            }
            rows_html = []
            for line in result["lines"]:
                bg, prefix = colors[line["type"]]
                rows_html.append(
                    f'<div style="background:{bg}; padding:0.1rem 0.5rem; '
                    f'font-family:monospace; white-space:pre-wrap;">{prefix} {escape(line["text"])}</div>'
                )
            st.markdown(
                f'<div style="border:1px solid var(--itops-surface-border); border-radius:8px; '
                f'padding:0.5rem; max-height:480px; overflow-y:auto;">{"".join(rows_html)}</div>',
                unsafe_allow_html=True,
            )
