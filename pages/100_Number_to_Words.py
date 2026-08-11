from __future__ import annotations

import streamlit as st

from utils.number_to_words import MAX_INPUT_LENGTH, number_to_words
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Number to Words", layout="wide")
apply_app_shell(active_page="Number to Words")


render_page_header(
    "Number to Words",
    "Spell out an integer in English words, e.g. 1042 -> one thousand forty-two.",
)

with tool_form_panel("number_to_words"):
    render_form_intro("Enter a whole number", "")
    with st.form("number-to-words-form"):
        number_input = st.text_input("Number", placeholder="1042", max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Convert")

if submitted:
    st.session_state["number_to_words_result"] = number_to_words(number_input)

result = st.session_state.get("number_to_words_result")

if result is None:
    render_empty_state("Ready to convert", "The number spelled out in words appears here.")

if result is not None:
    with tool_result_panel("number_to_words_result_panel", related_to="number_to_words"):
        render_section_heading("In words", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            st.success(result["output"])
