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


# Deterministic, embedded subset for offline-safe generation/validation checks.
_WORDS: tuple[str, ...] = (
    "abandon", "ability", "about", "above", "absent", "absorb", "abstract", "access", "accident", "account", "achieve", "acoustic",
    "acquire", "across", "action", "actor", "adapt", "add", "address", "adjust", "admit", "adult", "advance", "advice",
    "aerobic", "affair", "afford", "afraid", "again", "agent", "agree", "ahead", "aim", "air", "airport", "aisle",
    "alarm", "album", "alert", "alien", "all", "allow", "almost", "alone", "alpha", "already", "also", "alter",
    "always", "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger", "angle", "angry",
)

_ALLOWED_COUNTS: tuple[int, ...] = (12, 15, 18, 21, 24)


def _seed_to_int(seed_text: str) -> int:
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def generate_mnemonic(word_count: int, seed_text: str) -> str:
    rng = random.Random(_seed_to_int(seed_text) if seed_text else None)
    return " ".join(rng.choice(_WORDS) for _ in range(word_count))


def validate_mnemonic(phrase: str) -> dict[str, object]:
    words = [item.strip().lower() for item in (phrase or "").split() if item.strip()]
    if not words:
        return {"ok": False, "error": "Enter a mnemonic phrase to validate.", "unknown": []}
    if len(words) not in _ALLOWED_COUNTS:
        return {"ok": False, "error": "Mnemonic must contain 12, 15, 18, 21, or 24 words.", "unknown": []}
    unknown = [word for word in words if word not in _WORDS]
    if unknown:
        return {"ok": False, "error": "Mnemonic contains words outside the embedded BIP39 subset.", "unknown": unknown}
    return {"ok": True, "error": "", "unknown": []}


_baseline = start_page_baseline("BIP39 Mnemonic Generator Validator")
st.set_page_config(page_title="BIP39 Mnemonic Generator Validator", layout="wide")
apply_app_shell(active_page="BIP39 Mnemonic Generator Validator")
mark_page_baseline(_baseline, "shell-ready")
mark_page_baseline(_baseline, "wave27-shell-mobile")
mark_page_baseline(_baseline, "wave28-shell-mobile")
mark_page_baseline(_baseline, "wave29-shell-mobile")

render_page_header(
    "BIP39 Mnemonic Generator Validator",
    "Generate deterministic mnemonic phrases (for testing) and validate phrase shape against an embedded BIP39 subset.",
)

with tool_form_panel("bip39_mnemonic_generator_validator"):
    render_form_intro("Configure mnemonic generation", "Grouped controls and a single full-width action keep generation predictable on phones.")
    with st.form("bip39-mnemonic-generator-form"):
        render_control_heading("Generation settings")
        word_count = st.selectbox("Word count", options=_ALLOWED_COUNTS, index=0)
        seed_text = st.text_input("Deterministic seed (optional)", placeholder="release-wave-23")
        render_control_heading("Primary action")
        submitted_generate = st.form_submit_button("Generate mnemonic", use_container_width=True)

with tool_form_panel("bip39_mnemonic_validator"):
    render_form_intro("Validate mnemonic phrase", "Validation only checks word count and membership in the embedded subset.")
    with st.form("bip39-mnemonic-validator-form"):
        render_control_heading("Mnemonic phrase")
        phrase_input = st.text_area("Mnemonic phrase", height=140, placeholder="abandon ability about ...")
        render_control_heading("Primary action")
        submitted_validate = st.form_submit_button("Validate mnemonic", use_container_width=True)

if submitted_generate:
    phrase = generate_mnemonic(word_count=word_count, seed_text=seed_text.strip())
    st.session_state["bip39_mnemonic_generated"] = phrase

if submitted_validate:
    st.session_state["bip39_mnemonic_validation"] = validate_mnemonic(phrase_input)

phrase = st.session_state.get("bip39_mnemonic_generated")
validation = st.session_state.get("bip39_mnemonic_validation")

if phrase is None and validation is None:
    render_empty_state("Ready for mnemonic operations", "Generated phrases and validation outcomes appear here after submission.")
    render_status_note(
        "Outcome: mnemonic tools ready",
        "Generate a phrase or validate a phrase to view outcomes.",
        tone="neutral",
    )

with tool_result_panel("bip39_generated_phrase", related_to="bip39_mnemonic_generator_validator"):
    render_section_heading("Generated mnemonic", eyebrow="Result")
    if phrase is None:
        render_empty_state("No mnemonic generated yet", "Choose a word count, optionally add a seed, then generate a phrase.")
        render_status_note("Outcome: generation awaiting input", "Set options, then choose Generate mnemonic.", tone="neutral")
    else:
        render_status_note(
            "Outcome: mnemonic generation complete",
            "A phrase is ready. Reusing the same seed reproduces the same output.",
            tone="success",
        )
        st.code(str(phrase), language=None)

with tool_result_panel("bip39_validation_result", related_to="bip39_mnemonic_validator"):
    render_section_heading("Validation result", eyebrow="Result")
    if validation is None:
        render_empty_state("No validation run yet", "Paste a phrase and choose Validate mnemonic.")
        render_status_note("Outcome: validation awaiting input", "Validation results appear here after you submit a phrase.", tone="neutral")
    elif not validation["ok"]:
        detail = str(validation["error"])
        if validation.get("unknown"):
            detail += " Unknown words: " + ", ".join(str(item) for item in validation["unknown"])
        render_status_note("Outcome: mnemonic validation blocked", detail, tone="warning")
    else:
        render_status_note("Outcome: mnemonic validation complete", "Word count and embedded subset checks passed for this phrase.", tone="success")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
