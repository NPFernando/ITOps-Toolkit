from __future__ import annotations

import streamlit as st

from utils.unified_diff_generator import MAX_INPUT_LENGTH, generate_unified_diff
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


_baseline = start_page_baseline("Unified Diff Generator")
st.set_page_config(page_title="Unified Diff Generator", layout="wide")
apply_app_shell(active_page="Unified Diff Generator")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Unified Diff Generator",
    "Generate a real unified diff (patch) from two texts -- applicable with the patch or git apply command.",
)

with tool_form_panel("unified_diff_generator"):
    render_form_intro("Paste the original and changed text", "Use the left box for the baseline and the right box for the updated version.")
    with st.form("unified-diff-form"):
        original_input = st.text_area("Original", height=240, max_chars=MAX_INPUT_LENGTH, placeholder="line1\nline2\nline3")
        changed_input = st.text_area("Changed", height=240, max_chars=MAX_INPUT_LENGTH, placeholder="line1\nCHANGED\nline3")
        original_name = st.text_input("Original file name", value="a")
        changed_name = st.text_input("Changed file name", value="b")
        context_lines = st.slider("Context lines", 0, 10, 3)
        submitted = st.form_submit_button("Generate diff", use_container_width=True)

if submitted:
    st.session_state["unified_diff_result"] = generate_unified_diff(original_input, changed_input, original_name, changed_name, context_lines)

result = st.session_state.get("unified_diff_result")

if result is None:
    render_empty_state("Ready to generate", "The unified diff appears here.")
    render_status_note(
        "Ready for text comparison",
        "Paste original and changed text, then select Generate diff to create unified patch output.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("unified_diff_result_panel", related_to="unified_diff_generator"):
        render_section_heading("Unified diff", eyebrow="Result")
        if not result["ok"]:
            render_status_note(
                "Diff generation needs input fixes",
                f"{result['error']} Review the text inputs and file names, then generate the diff again.",
                tone="warning",
            )
        elif result["identical"]:
            render_status_note(
                "No differences found",
                "Both inputs are identical, so no patch output was generated.",
                tone="neutral",
            )
        else:
            render_status_note(
                "Patch output ready",
                "Unified diff generation succeeded. Review the patch below or download it as a .patch file.",
                tone="success",
            )
            st.code(result["output"], language="diff")
            st.download_button("Download as .patch", result["output"], file_name="change.patch", mime="text/x-diff")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
