from __future__ import annotations

import streamlit as st

from utils.json_merge_patch import MAX_INPUT_LENGTH, merge_json
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="JSON Merge Patch", layout="wide")
apply_app_shell(active_page="JSON Merge Patch")


render_page_header(
    "JSON Merge Patch",
    "Merge two JSON documents per RFC 7396 -- useful for layering an environment-specific override onto a base config.",
    warning="A null value in the patch deletes that key from the target; any other value replaces it outright; objects are merged recursively. Arrays are replaced wholesale, never merged element-by-element.",
)

with tool_form_panel("json_merge_patch"):
    render_form_intro("Paste the target JSON and the patch to apply", "")
    with st.form("json-merge-patch-form"):
        col_a, col_b = st.columns(2)
        target_input = col_a.text_area("Target JSON", height=280, max_chars=MAX_INPUT_LENGTH, placeholder='{"a": "b", "c": {"d": "e"}}')
        patch_input = col_b.text_area("Patch JSON", height=280, max_chars=MAX_INPUT_LENGTH, placeholder='{"a": "z", "c": {"d": null}}')
        submitted = st.form_submit_button("Merge")

if submitted:
    st.session_state["json_merge_patch_result"] = merge_json(target_input, patch_input)

result = st.session_state.get("json_merge_patch_result")

if result is None:
    render_empty_state("Ready to merge", "The merged JSON appears here.")

if result is not None:
    with tool_result_panel("json_merge_patch_result_panel", related_to="json_merge_patch"):
        render_section_heading("Merged JSON", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language="json")
