from __future__ import annotations

import streamlit as st

from utils.markdown_toc_generator import MAX_INPUT_LENGTH, generate_toc
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Markdown TOC Generator", layout="wide")
apply_app_shell(active_page="Markdown TOC Generator")


render_page_header(
    "Markdown TOC Generator",
    "Paste Markdown and get a linked table of contents built from its headings.",
    warning="Anchor slugs follow GitHub's algorithm. Only # ATX-style headings are recognized, not underlined Setext-style headings, and headings inside fenced code blocks are skipped.",
)

with tool_form_panel("markdown_toc_generator"):
    render_form_intro("Paste Markdown", "Headings from # to ######.")
    with st.form("markdown-toc-form"):
        markdown_input = st.text_area(
            "Markdown",
            height=280,
            max_chars=MAX_INPUT_LENGTH,
            placeholder="# Title\n\n## Section One\n\n### Subsection\n\n## Section Two",
        )
        c1, c2 = st.columns(2)
        min_level = c1.number_input("Min heading level", min_value=1, max_value=6, value=1)
        max_level = c2.number_input("Max heading level", min_value=1, max_value=6, value=3)
        submitted = st.form_submit_button("Generate TOC")

if submitted:
    st.session_state["markdown_toc_result"] = generate_toc(markdown_input, int(min_level), int(max_level))

result = st.session_state.get("markdown_toc_result")

if result is None:
    render_empty_state("Ready to generate", "The table of contents appears here.")

if result is not None:
    with tool_result_panel("markdown_toc_result_panel", related_to="markdown_toc_generator"):
        render_section_heading("Table of contents", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="markdown")
