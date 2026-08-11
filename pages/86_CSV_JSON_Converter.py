from __future__ import annotations

import streamlit as st

from utils.csv_json_converter import MAX_INPUT_LENGTH, csv_to_json, json_to_csv
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="CSV / JSON Converter", layout="wide")
apply_app_shell(active_page="CSV / JSON Converter")


render_page_header(
    "CSV / JSON Converter",
    "Convert CSV/TSV (with a header row) to a JSON array of objects, or the reverse.",
)

_DELIMITERS = {"Comma (CSV)": ",", "Tab (TSV)": "\t"}

to_json_tab, to_csv_tab = st.tabs(["CSV to JSON", "JSON to CSV"])

with to_json_tab:
    with tool_form_panel("csv_to_json"):
        render_form_intro("Paste CSV or TSV", "Include a header row.")
        with st.form("csv-to-json-form"):
            delimiter_label = st.selectbox("Delimiter", list(_DELIMITERS.keys()), key="csv_to_json_delimiter")
            csv_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder="name,age\nAlice,30\nBob,25")
            to_json_submitted = st.form_submit_button("Convert to JSON")

    if to_json_submitted:
        st.session_state["csv_to_json_result"] = csv_to_json(csv_input, _DELIMITERS[delimiter_label])

    to_json_result = st.session_state.get("csv_to_json_result")

    if to_json_result is None:
        render_empty_state("Ready to convert", "The JSON array appears here.")

    if to_json_result is not None:
        with tool_result_panel("csv_to_json_result_panel", related_to="csv_json_converter"):
            render_section_heading("JSON", eyebrow="Result")
            if not to_json_result["ok"]:
                st.error(to_json_result["error"])
            else:
                st.code(to_json_result["output"], language="json")
                st.download_button("Download as .json", to_json_result["output"], file_name="data.json", mime="application/json")

with to_csv_tab:
    with tool_form_panel("json_to_csv"):
        render_form_intro("Paste a JSON array of objects", "Every object should be a flat mapping of field names to values.")
        with st.form("json-to-csv-form"):
            delimiter_label2 = st.selectbox("Delimiter", list(_DELIMITERS.keys()), key="json_to_csv_delimiter")
            json_input = st.text_area("Input", height=280, max_chars=MAX_INPUT_LENGTH, placeholder='[{"name": "Alice", "age": 30}]')
            to_csv_submitted = st.form_submit_button("Convert to CSV")

    if to_csv_submitted:
        st.session_state["json_to_csv_result"] = json_to_csv(json_input, _DELIMITERS[delimiter_label2])

    to_csv_result = st.session_state.get("json_to_csv_result")

    if to_csv_result is None:
        render_empty_state("Ready to convert", "The CSV output appears here.")

    if to_csv_result is not None:
        with tool_result_panel("json_to_csv_result_panel", related_to="csv_json_converter"):
            render_section_heading("CSV", eyebrow="Result")
            if not to_csv_result["ok"]:
                st.error(to_csv_result["error"])
            else:
                st.code(to_csv_result["output"], language=None)
                st.download_button("Download as .csv", to_csv_result["output"], file_name="data.csv", mime="text/csv")
