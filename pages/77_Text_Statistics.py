from __future__ import annotations

import streamlit as st

from utils.text_stats import MAX_INPUT_LENGTH, analyze_text
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Text Statistics", layout="wide")
apply_app_shell(active_page="Text Statistics")


render_page_header(
    "Text Statistics",
    "Paste text to see word, character, and sentence counts, plus the most frequent words. Sentence detection is approximate, not full NLP.",
)

with tool_form_panel("text_stats"):
    render_form_intro("Paste text", "Any block of prose, notes, or logs.")
    with st.form("text-stats-form"):
        text_input = st.text_area("Text", height=280, max_chars=MAX_INPUT_LENGTH)
        submitted = st.form_submit_button("Analyze")

if submitted:
    st.session_state["text_stats_result"] = analyze_text(text_input)

result = st.session_state.get("text_stats_result")

if result is None:
    render_empty_state("Ready to analyze", "Word/character/sentence counts and top words appear here.")

if result is not None:
    with tool_result_panel("text_stats_result_panel", related_to="text_stats"):
        render_section_heading("Statistics", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Words", result["word_count"])
            c2.metric("Characters", result["char_count"])
            c3.metric("Characters (no spaces)", result["char_count_no_spaces"])
            c4.metric("Sentences (approx.)", result["sentence_count"])
            if result["top_words"]:
                st.table([{"Word": w["word"], "Count": w["count"]} for w in result["top_words"]])
