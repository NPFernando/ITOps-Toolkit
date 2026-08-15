from __future__ import annotations

import csv
import io
import json

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
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


InputMode = str
OutputMode = str


def _parse_items(raw_text: str, input_mode: InputMode) -> list[str]:
    text = (raw_text or "").strip()
    if not text:
        return []
    if input_mode == "Comma-separated":
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        return [item.strip() for row in rows for item in row if item.strip()]
    return [line.strip() for line in text.splitlines() if line.strip()]


def _format_items(items: list[str], output_mode: OutputMode) -> str:
    if output_mode == "Comma-separated":
        return ", ".join(items)
    if output_mode == "JSON array":
        return json.dumps(items, indent=2)
    return "\n".join(items)


def convert_list(raw_text: str, input_mode: InputMode, output_mode: OutputMode, dedupe: bool, sort_items: bool) -> dict[str, str | bool]:
    items = _parse_items(raw_text, input_mode)
    if dedupe:
        items = list(dict.fromkeys(items))
    if sort_items:
        items = sorted(items, key=str.casefold)
    if not items:
        return {"ok": False, "error": "Add at least one list item to convert.", "output": ""}
    return {"ok": True, "error": "", "output": _format_items(items, output_mode)}


_baseline = start_page_baseline("List Converter")
st.set_page_config(page_title="List Converter", layout="wide")
apply_app_shell(active_page="List Converter")
mark_page_baseline(_baseline, "shell-ready")

render_page_header("List Converter", "Convert between line lists, comma lists, and JSON arrays with mobile-friendly grouped controls.")

with tool_form_panel("list_converter"):
    render_form_intro("Choose list formats", "Use one full-width action after grouped format controls for consistent small-screen ergonomics.")
    with st.form("list-converter-form"):
        st.markdown('<div class="tool-panel-eyebrow">Input list</div>', unsafe_allow_html=True)
        list_input = st.text_area("List input", height=180, placeholder="alpha\nbeta\ngamma")
        st.markdown('<div class="tool-panel-eyebrow">Format settings</div>', unsafe_allow_html=True)
        input_mode = st.selectbox("Input format", options=("Line-separated", "Comma-separated"))
        output_mode = st.selectbox("Output format", options=("Line-separated", "Comma-separated", "JSON array"))
        dedupe = st.checkbox("Remove duplicate items", value=True)
        sort_items = st.checkbox("Sort output alphabetically", value=False)
        submitted = st.form_submit_button("Convert list", use_container_width=True)

if submitted:
    st.session_state["list_converter_result"] = convert_list(list_input, input_mode, output_mode, dedupe, sort_items)

result = st.session_state.get("list_converter_result")
if result is None:
    render_empty_state("Ready to convert", "Converted list output appears here after submission.")
    render_status_note(
        "Outcome: awaiting list conversion",
        "Paste list data, choose formats, then select Convert list.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("list_converter_result", related_to="list_converter"):
        render_section_heading("Converted output", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: list conversion blocked", str(result["error"]), tone="warning")
        else:
            render_status_note("Outcome: list conversion complete", "Copy the transformed list output below.", tone="success")
            st.code(str(result["output"]), language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
