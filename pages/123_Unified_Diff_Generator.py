from __future__ import annotations

import streamlit as st

from utils.unified_diff_generator import MAX_INPUT_LENGTH, generate_unified_diff
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Unified Diff Generator", layout="wide")
apply_app_shell(active_page="Unified Diff Generator")


render_page_header(
    "Unified Diff Generator",
    "Generate a real unified diff (patch) from two texts -- applicable with the patch or git apply command.",
)

with tool_form_panel("unified_diff_generator"):
    render_form_intro("Paste the original and changed text", "")
    with st.form("unified-diff-form"):
        col_a, col_b = st.columns(2)
        original_input = col_a.text_area("Original", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="line1\nline2\nline3")
        changed_input = col_b.text_area("Changed", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="line1\nCHANGED\nline3")
        c1, c2 = st.columns(2)
        original_name = c1.text_input("Original file name", value="a")
        changed_name = c2.text_input("Changed file name", value="b")
        context_lines = st.slider("Context lines", 0, 10, 3)
        submitted = st.form_submit_button("Generate diff")

if submitted:
    st.session_state["unified_diff_result"] = generate_unified_diff(original_input, changed_input, original_name, changed_name, context_lines)

result = st.session_state.get("unified_diff_result")

if result is None:
    render_empty_state("Ready to generate", "The unified diff appears here.")

if result is not None:
    with tool_result_panel("unified_diff_result_panel", related_to="unified_diff_generator"):
        render_section_heading("Unified diff", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        elif result["identical"]:
            st.success("The two texts are identical.")
        else:
            st.code(result["output"], language="diff")
            st.download_button("Download as .patch", result["output"], file_name="change.patch", mime="text/x-diff")
