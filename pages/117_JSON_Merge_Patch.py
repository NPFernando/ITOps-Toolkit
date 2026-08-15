from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.json_merge_patch import MAX_INPUT_LENGTH, merge_json
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_baseline = start_page_baseline("JSON Merge Patch")
st.set_page_config(page_title="JSON Merge Patch", layout="wide")
apply_app_shell(active_page="JSON Merge Patch")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "JSON Merge Patch",
    "Merge two JSON documents per RFC 7396 -- useful for layering an environment-specific override onto a base config.",
    warning="A null value in the patch deletes that key from the target; any other value replaces it outright; objects are merged recursively. Arrays are replaced wholesale, never merged element-by-element.",
)

with tool_form_panel("json_merge_patch"):
    render_form_intro("Paste the target JSON and the patch to apply", "")
    with st.form("json-merge-patch-form"):
        st.markdown('<div class="tool-panel-eyebrow">Target JSON</div>', unsafe_allow_html=True)
        target_input = st.text_area("Target JSON", height=280, max_chars=MAX_INPUT_LENGTH, placeholder='{"a": "b", "c": {"d": "e"}}')
        st.markdown('<div class="tool-panel-eyebrow">Patch JSON</div>', unsafe_allow_html=True)
        patch_input = st.text_area("Patch JSON", height=280, max_chars=MAX_INPUT_LENGTH, placeholder='{"a": "z", "c": {"d": null}}')
        submitted = st.form_submit_button("Merge", use_container_width=True)

if submitted:
    st.session_state["json_merge_patch_result"] = merge_json(target_input, patch_input)

result = st.session_state.get("json_merge_patch_result")

if result is None:
    render_empty_state("Ready to merge", "The merged JSON appears here.")
    render_status_note(
        "Ready for JSON input",
        "No merge has run yet. Provide target and patch JSON, then select Merge.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("json_merge_patch_result_panel", related_to="json_merge_patch"):
        render_section_heading("Merged JSON", eyebrow="Result")
        if not result["ok"]:
            render_failure_note(
                "JSON merge patch",
                result["error"],
                remediation="Provide valid target and patch JSON documents, then merge again.",
            )
        else:
            st.code(result["output"], language="json")
            render_status_note(
                "JSON merge patch applied",
                "Patch merged successfully using RFC 7396 rules.",
                tone="success",
            )

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
