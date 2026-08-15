from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.number_to_words import MAX_INPUT_LENGTH, number_to_words
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


_baseline = start_page_baseline("Number to Words")
st.set_page_config(page_title="Number to Words", layout="wide")
apply_app_shell(active_page="Number to Words")
mark_page_baseline(_baseline, "shell-ready")


render_page_header(
    "Number to Words",
    "Spell out an integer in English words, e.g. 1042 -> one thousand forty-two.",
)

with tool_form_panel("number_to_words"):
    render_form_intro("Enter a whole number", "Supports positive, negative, and zero values within the tool limit.")
    with st.form("number-to-words-form"):
        number_input = st.text_input("Number", placeholder="1042", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Convert", use_container_width=True)

if submitted:
    st.session_state["number_to_words_result"] = number_to_words(number_input)

result = st.session_state.get("number_to_words_result")

if result is None:
    render_empty_state("Ready to convert", "The number spelled out in words appears here.")
    render_status_note(
        "Awaiting number input",
        "Enter an integer and select Convert to spell it out in words.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("number_to_words_result_panel", related_to="number_to_words"):
        render_section_heading("Conversion outcome", eyebrow="Result")
        if not result["ok"]:
            render_status_note(
                "Number conversion needs input fixes",
                f"{result['error']} Use a whole number and retry conversion.",
                tone="warning",
            )
        else:
            render_status_note(
                "Number converted to words",
                "Conversion complete. The English wording is ready to copy below.",
                tone="success",
            )
            st.code(result["output"], language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
