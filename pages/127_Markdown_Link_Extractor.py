from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.markdown_link_extractor import MAX_INPUT_LENGTH, extract_links
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


st.set_page_config(page_title="Markdown Link Extractor", layout="wide")
apply_app_shell(active_page="Markdown Link Extractor")


render_page_header(
    "Markdown Link Extractor",
    "Extract every link from Markdown text -- inline links, reference-style links, and bare autolinks.",
)

with tool_form_panel("markdown_link_extractor"):
    render_form_intro("Paste Markdown text", "Include inline links, reference links, or autolinks to extract into a table.")
    with st.form("markdown-link-extractor-form"):
        markdown_input = st.text_area("Markdown", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="Check out [Google](https://google.com).")
        submitted = st.form_submit_button("Extract links", use_container_width=True)

if submitted:
    st.session_state["markdown_link_extractor_result"] = extract_links(markdown_input)

result = st.session_state.get("markdown_link_extractor_result")

if result is None:
    render_empty_state("Ready to extract", "Every link found appears here.")
    render_status_note("Awaiting Markdown input", "Paste Markdown text and run extraction to list all detected links.", tone="neutral")

if result is not None:
    with tool_result_panel("markdown_link_extractor_result_panel", related_to="markdown_link_extractor"):
        render_section_heading("Links found", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
            render_status_note("Extraction failed", "Update the Markdown input and run extraction again.", tone="warning")
        else:
            st.dataframe(
                pd.DataFrame([{"Text": link["text"], "URL": link["url"], "Type": link["type"]} for link in result["links"]]),
                width="stretch",
                hide_index=True,
            )
            render_status_note("Extraction complete", f"Found {len(result['links'])} link(s) in the provided Markdown.", tone="success")
