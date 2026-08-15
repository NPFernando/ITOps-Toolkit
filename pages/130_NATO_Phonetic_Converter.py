from __future__ import annotations

import streamlit as st

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


NATO_ALPHABET = {
    "A": "Alpha",
    "B": "Bravo",
    "C": "Charlie",
    "D": "Delta",
    "E": "Echo",
    "F": "Foxtrot",
    "G": "Golf",
    "H": "Hotel",
    "I": "India",
    "J": "Juliett",
    "K": "Kilo",
    "L": "Lima",
    "M": "Mike",
    "N": "November",
    "O": "Oscar",
    "P": "Papa",
    "Q": "Quebec",
    "R": "Romeo",
    "S": "Sierra",
    "T": "Tango",
    "U": "Uniform",
    "V": "Victor",
    "W": "Whiskey",
    "X": "X-ray",
    "Y": "Yankee",
    "Z": "Zulu",
}


def nato_convert(value: str) -> str:
    words: list[str] = []
    for char in value:
        upper = char.upper()
        if upper in NATO_ALPHABET:
            words.append(NATO_ALPHABET[upper])
        elif char.isspace():
            words.append("/")
        else:
            words.append(char)
    return " ".join(words).strip()


_baseline = start_page_baseline("NATO Phonetic Converter")
st.set_page_config(page_title="NATO Phonetic Converter", layout="wide")
apply_app_shell(active_page="NATO Phonetic Converter")
mark_page_baseline(_baseline, "shell-ready")

render_page_header(
    "NATO Phonetic Converter",
    "Convert text into NATO words for clear read-aloud communication over calls or radio.",
)

with tool_form_panel("nato_phonetic_converter"):
    render_form_intro("Enter source text", "Letters convert to NATO words, spaces become slash separators, and numbers/symbols stay unchanged.")
    with st.form("nato-phonetic-form"):
        st.markdown('<div class="tool-panel-eyebrow">Input text</div>', unsafe_allow_html=True)
        input_text = st.text_area("Text to convert", height=200, placeholder="Srv-42")
        submitted = st.form_submit_button("Convert to NATO phonetic", use_container_width=True)

if submitted:
    st.session_state["nato_phonetic_result"] = nato_convert(input_text)

result = st.session_state.get("nato_phonetic_result")
if result is None:
    render_empty_state("Ready to convert", "Phonetic output appears here after conversion.")
    render_status_note(
        "Awaiting source text",
        "Enter text and select Convert to NATO phonetic to generate read-aloud NATO spelling.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("nato_phonetic_result_panel", related_to="nato_phonetic_converter"):
        render_section_heading("Phonetic output", eyebrow="Result")
        if not result:
            render_status_note("Outcome: input required", "Enter text to generate phonetic output.", tone="warning")
        else:
            render_status_note("Outcome: conversion complete", "NATO spelling generated successfully.", tone="success")
            st.code(result, language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
