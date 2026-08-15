from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.markdown_toc_generator import MAX_INPUT_LENGTH, generate_toc
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


_baseline = start_page_baseline("Markdown TOC Generator")
st.set_page_config(page_title="Markdown TOC Generator", layout="wide")
apply_app_shell(active_page="Markdown TOC Generator")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Markdown TOC Generator",
    "Paste Markdown and get a linked table of contents built from its headings.",
    warning="Anchor slugs follow GitHub's algorithm. Only # ATX-style headings are recognized, not underlined Setext-style headings, and headings inside fenced code blocks are skipped.",
)

with tool_form_panel("markdown_toc_generator"):
    render_form_intro("Paste Markdown and choose heading range", "Use heading levels to control which sections appear in the generated TOC.")
    with st.form("markdown-toc-form"):
        markdown_input = st.text_area(
            "Markdown",
            height=280,
            max_chars=MAX_INPUT_LENGTH,
            placeholder="# Title\n\n## Section One\n\n### Subsection\n\n## Section Two",
        )
        min_level = st.number_input("Min heading level", min_value=1, max_value=6, value=1)
        max_level = st.number_input("Max heading level", min_value=1, max_value=6, value=3)
        submitted = st.form_submit_button("Generate TOC", use_container_width=True)

if submitted:
    st.session_state["markdown_toc_result"] = generate_toc(markdown_input, int(min_level), int(max_level))

result = st.session_state.get("markdown_toc_result")

if result is None:
    render_empty_state("Ready to generate", "The table of contents appears here.")
    render_status_note(
        "Awaiting Markdown input",
        "Paste Markdown content and select Generate TOC to build heading links.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("markdown_toc_result_panel", related_to="markdown_toc_generator"):
        render_section_heading("TOC outcome", eyebrow="Result")
        if not result["ok"]:
            render_status_note(
                "TOC generation needs input fixes",
                f"{result['error']} Confirm the heading levels and input content, then retry.",
                tone="warning",
            )
        else:
            render_status_note(
                "Table of contents ready",
                f"Generated {result['heading_count']} linked heading(s). Copy the output below.",
                tone="success",
            )
            st.code(result["output"], language="markdown")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
