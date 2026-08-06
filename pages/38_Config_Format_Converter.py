from __future__ import annotations

import streamlit as st

from utils.config_format_converter import FORMATS, MAX_INPUT_LENGTH, convert_config
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, render_status_note, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Config Format Converter", layout="wide")
apply_app_shell(active_page="Config Format Converter")


render_page_header(
    "Config Format Converter",
    "Convert a config snippet between JSON, YAML, TOML, and XML.",
)

render_status_note(
    "XML mapping is a convention, not a standard",
    "JSON/YAML/TOML share the same object model and convert losslessly. XML has no standard equivalent, so this tool uses one explicit convention: each key becomes a child element, lists become repeated elements, and scalars become element text. Attributes, mixed content, and value types (numbers/booleans become element text) are not preserved through an XML round trip.",
    tone="neutral",
)

with tool_form_panel("config_format_converter"):
    render_form_intro("Convert", "Paste config text and choose the source and target formats.")
    with st.form("config-format-form"):
        format_col_a, format_col_b = st.columns(2)
        from_format = format_col_a.selectbox("From", FORMATS, index=0)
        to_format = format_col_b.selectbox("To", FORMATS, index=1)
        text = st.text_area("Config text", height=280, max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Convert")

if submitted:
    # Stored in session_state (not rendered directly here) because the download
    # button below triggers its own rerun -- on that rerun `submitted` is False
    # again, which would otherwise collapse this whole results section right
    # after the click.
    st.session_state["config_format_state"] = {
        "result": convert_config(text, from_format, to_format),
        "from_format": from_format,
        "to_format": to_format,
    }

state = st.session_state.get("config_format_state")

if state is None:
    render_empty_state("Ready to convert", "The converted output appears here after conversion.")

if state is not None:
    result = state["result"]
    result_from = state["from_format"]
    result_to = state["to_format"]
    with tool_result_panel("config_format_result", related_to="config_format_converter"):
        render_section_heading(f"{result_from} -> {result_to}", "Converted output.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.code(result["output"], language=result_to.lower() if result_to != "TOML" else "toml")
            st.download_button(
                f"Download as .{result_to.lower()}",
                result["output"],
                file_name=f"converted.{result_to.lower()}",
                mime="text/plain",
            )
