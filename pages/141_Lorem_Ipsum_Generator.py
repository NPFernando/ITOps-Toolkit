from __future__ import annotations

import hashlib
import random

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_control_heading,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_WORD_BANK: tuple[str, ...] = (
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
    "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis",
    "nostrud", "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute",
    "irure", "in", "reprehenderit", "voluptate", "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
    "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id",
)


def _seed_to_int(seed_text: str) -> int:
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def generate_lorem(unit: str, count: int, seed_text: str) -> str:
    rng = random.Random(_seed_to_int(seed_text) if seed_text else None)

    def sentence(word_count: int) -> str:
        words = [rng.choice(_WORD_BANK) for _ in range(max(3, word_count))]
        words[0] = words[0].capitalize()
        return " ".join(words) + "."

    if unit == "Words":
        return " ".join(rng.choice(_WORD_BANK) for _ in range(count))
    if unit == "Sentences":
        return " ".join(sentence(rng.randint(7, 13)) for _ in range(count))

    paragraphs: list[str] = []
    for _ in range(count):
        sentence_count = rng.randint(3, 5)
        paragraphs.append(" ".join(sentence(rng.randint(7, 13)) for _ in range(sentence_count)))
    return "\n\n".join(paragraphs)


_baseline = start_page_baseline("Lorem Ipsum Generator")
st.set_page_config(page_title="Lorem Ipsum Generator", layout="wide")
apply_app_shell(active_page="Lorem Ipsum Generator")
mark_page_baseline(_baseline, "shell-ready")
mark_page_baseline(_baseline, "wave27-shell-mobile")
mark_page_baseline(_baseline, "wave29-shell-mobile")
mark_page_baseline(_baseline, "wave30-shell-mobile")
mark_page_baseline(_baseline, "wave31-shell-mobile")

render_page_header("Lorem Ipsum Generator", "Generate deterministic placeholder text by words, sentences, or paragraphs.")

with tool_form_panel("lorem_ipsum_generator"):
    render_form_intro("Set lorem output", "Grouped controls plus one full-width action keep mobile drafting fast and predictable.")
    with st.form("lorem-ipsum-generator-form"):
        render_control_heading("Output shape")
        unit = st.selectbox("Generate by", options=("Words", "Sentences", "Paragraphs"), key="lorem_unit")
        default_count = 24 if unit == "Words" else 3
        count = st.number_input("Count", min_value=1, max_value=100, value=default_count, key="lorem_count")
        render_control_heading("Deterministic seed")
        seed_text = st.text_input("Deterministic seed (optional)", placeholder="wave-25", key="lorem_seed")
        render_control_heading("Primary action")
        submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)

if submitted:
    st.session_state["lorem_ipsum_result"] = generate_lorem(unit=unit, count=int(count), seed_text=seed_text.strip())

result = st.session_state.get("lorem_ipsum_result")
with tool_result_panel("lorem_ipsum_result", related_to="lorem_ipsum_generator"):
    render_section_heading("Generated text", eyebrow="Result")
    if result is None:
        render_empty_state("Ready to generate", "Generated lorem ipsum text appears here after submission.")
        render_status_note(
            "Outcome: lorem generation awaiting input",
            "Choose output shape and count, then select Generate lorem ipsum.",
            tone="neutral",
        )
    else:
        render_status_note(
            "Outcome: lorem text generated",
            "Placeholder text is ready to copy from the output block below. Reuse the same seed to reproduce this exact output.",
            tone="success",
        )
        st.code(str(result), language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
