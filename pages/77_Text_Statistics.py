from __future__ import annotations

import streamlit as st

from utils.text_stats import MAX_INPUT_LENGTH, analyze_text
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_failure_note,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Text Statistics", layout="wide")
apply_app_shell(active_page="Text Statistics")


render_page_header(
    "Text Statistics",
    "Paste text to see word, character, and sentence counts, plus the most frequent words. Sentence detection is approximate, not full NLP.",
)

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stFormSubmitButton"] > button {
        width: 100%;
        min-height: 2.75rem;
      }
      div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        overflow-wrap: anywhere;
      }
      div[data-testid="stTable"] {
        overflow-x: auto;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
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
    render_status_note("Awaiting text input", "Paste text and analyze to calculate counts and repeated terms.", tone="neutral")

if result is not None:
    with tool_result_panel("text_stats_result_panel", related_to="text_stats"):
        render_section_heading("Statistics", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
            render_failure_note(
                "Text analysis",
                result["error"],
                remediation="Paste non-empty text content, then run analysis again.",
            )
        else:
            c1, c2 = st.columns(2)
            c1.metric("Words", result["word_count"])
            c2.metric("Characters", result["char_count"])
            c3, c4 = st.columns(2)
            c3.metric("Characters (no spaces)", result["char_count_no_spaces"])
            c4.metric("Sentences (approx.)", result["sentence_count"])
            if result["top_words"]:
                st.table([{"Word": w["word"], "Count": w["count"]} for w in result["top_words"]])
            render_status_note(
                "Analysis complete",
                f"Computed {result['word_count']} word(s) across {result['sentence_count']} sentence(s).",
                tone="success",
            )
