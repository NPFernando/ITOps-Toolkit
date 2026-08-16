from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.csv_diff import MAX_INPUT_LENGTH, diff_csv
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


st.set_page_config(page_title="CSV Diff Viewer", layout="wide")
apply_app_shell(active_page="CSV Diff Viewer")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stFormSubmitButton"] > button {
        min-height: 2.75rem;
        font-size: 1rem;
      }
      div[data-testid="stTextInput"] input,
      div[data-testid="stTextArea"] textarea {
        font-size: 1rem;
      }
      div[data-testid="stAlert"] p,
      div[data-testid="stDataFrame"] [role="gridcell"],
      div[data-testid="stDataFrame"] [role="columnheader"] {
        overflow-wrap: anywhere;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
        submitted = st.form_submit_button("Compare", use_container_width=True)

if submitted:
    st.session_state["csv_diff_result"] = diff_csv(text_a, text_b, key_column)

result = st.session_state.get("csv_diff_result")

if result is None:
    render_empty_state("Ready to compare", "Added, removed, and changed rows appear here after comparison.")
    render_status_note(
        "Awaiting CSV inputs",
        "Provide both CSV datasets and a key column, then run comparison.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("csv_diff_result_panel", related_to="csv_diff"):
        render_section_heading("Differences", "Added, removed, and changed rows, matched by key column.")
        if not result["ok"]:
            st.error(result["error"])
            render_status_note(
                "Comparison failed",
                "Resolve the input error and run compare again.",
                tone="warning",
            )
        else:
            duplicates = result["duplicate_keys"]
            if duplicates["first_csv"]:
                st.warning(f"First CSV has duplicate key value(s): {', '.join(duplicates['first_csv'])}. Only the last matching row for each is compared.")
            if duplicates["second_csv"]:
                st.warning(f"Second CSV has duplicate key value(s): {', '.join(duplicates['second_csv'])}. Only the last matching row for each is compared.")

            if result["identical"]:
                st.success("The two CSVs are identical for the matched rows.")
                render_status_note(
                    "No differences found",
                    "Matched rows are identical across both CSV inputs.",
                    tone="success",
                )
            else:
                rows = []
                for diff in result["differences"]:
                    if diff["type"] == "changed":
                        for field, values in diff["fields"].items():
                            rows.append({"Key": diff["key"], "Type": "changed", "Field": field, "Old value": values["old"], "New value": values["new"]})
                    else:
                        rows.append({"Key": diff["key"], "Type": diff["type"], "Field": None, "Old value": None, "New value": None})
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
                render_status_note(
                    "Differences found",
                    f"{len(result['differences'])} row-level difference(s) detected between the two CSV inputs.",
                    tone="warning" if duplicates["first_csv"] or duplicates["second_csv"] else "success",
                )
