from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.csv_diff import MAX_INPUT_LENGTH, diff_csv
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSV Diff Viewer", layout="wide")
apply_app_shell(active_page="CSV Diff Viewer")


render_page_header(
    "CSV Diff Viewer",
    "Structurally compare two CSVs by a key column -- added, removed, and changed rows, not a line-by-line diff.",
)

with tool_form_panel("csv_diff"):
    render_form_intro("Compare CSVs", "Paste two CSVs (with headers) and the column name to match rows on.")
    with st.form("csv-diff-form"):
        key_column = st.text_input("Key column", placeholder="id")
        col_a, col_b = st.columns(2)
        text_a = col_a.text_area("First CSV", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="id,name\n1,Alice")
        text_b = col_b.text_area("Second CSV", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="id,name\n1,Alicia")
        submitted = st.form_submit_button("Compare")

if submitted:
    st.session_state["csv_diff_result"] = diff_csv(text_a, text_b, key_column)

result = st.session_state.get("csv_diff_result")

if result is None:
    render_empty_state("Ready to compare", "Added, removed, and changed rows appear here after comparison.")

if result is not None:
    with tool_result_panel("csv_diff_result_panel", related_to="csv_diff"):
        render_section_heading("Differences", "Added, removed, and changed rows, matched by key column.")
        if not result["ok"]:
            st.error(result["error"])
        elif result["identical"]:
            st.success("The two CSVs are identical for the matched rows.")
        else:
            rows = []
            for diff in result["differences"]:
                if diff["type"] == "changed":
                    for field, values in diff["fields"].items():
                        rows.append({"Key": diff["key"], "Type": "changed", "Field": field, "Old value": values["old"], "New value": values["new"]})
                else:
                    rows.append({"Key": diff["key"], "Type": diff["type"], "Field": None, "Old value": None, "New value": None})
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
