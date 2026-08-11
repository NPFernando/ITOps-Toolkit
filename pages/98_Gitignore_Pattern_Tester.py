from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.gitignore_tester import MAX_INPUT_LENGTH, MAX_PATH_LENGTH, check_paths
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title=".gitignore Pattern Tester", layout="wide")
apply_app_shell(active_page=".gitignore Pattern Tester")


render_page_header(
    ".gitignore Pattern Tester",
    "Paste .gitignore content and test whether specific paths would be ignored.",
    warning="Implements gitignore's core glob rules (*, ?, [...], **, leading/trailing /, ! negation) but not git's rule that a file can't be re-included with ! if a parent directory is already excluded -- test the parent directory separately if your patterns rely on that.",
)

with tool_form_panel("gitignore_tester"):
    render_form_intro("Paste .gitignore content and paths to test", "One path per line, e.g. src/app.log")
    with st.form("gitignore-tester-form"):
        col1, col2 = st.columns(2)
        gitignore_input = col1.text_area(".gitignore content", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="*.log\n!important.log\n/build/\ndoc/**/*.txt")
        paths_input = col2.text_area("Paths to test", height=280, max_chars=MAX_PATH_LENGTH * 20, placeholder="app.log\nimportant.log\nbuild/output.js\nsrc/app.log")
        submitted = st.form_submit_button("Check paths")

if submitted:
    st.session_state["gitignore_tester_result"] = check_paths(gitignore_input, paths_input)

result = st.session_state.get("gitignore_tester_result")

if result is None:
    render_empty_state("Ready to check", "Ignored/not-ignored status for each path appears here.")

if result is not None:
    with tool_result_panel("gitignore_tester_result_panel", related_to="gitignore_tester"):
        render_section_heading("Results", eyebrow="Per-path status")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Path": row["path"],
                            "Ignored": "Yes" if row["ignored"] else "No",
                            "Matched pattern": row["matched_pattern"] or "(no match)",
                        }
                        for row in result["results"]
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
