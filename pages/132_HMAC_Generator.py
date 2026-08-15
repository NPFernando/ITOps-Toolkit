from __future__ import annotations

import hmac
import hashlib

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


HMAC_ALGORITHMS = ("md5", "sha1", "sha256", "sha512")


def generate_hmac_digest(message: str, secret: str, algorithm: str) -> dict[str, str | bool]:
    if not message:
        return {"ok": False, "error": "Message is required.", "digest": ""}
    if not secret:
        return {"ok": False, "error": "Secret key is required.", "digest": ""}
    if algorithm not in HMAC_ALGORITHMS:
        return {"ok": False, "error": "Unsupported algorithm selected.", "digest": ""}
    digest = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), getattr(hashlib, algorithm)).hexdigest()
    return {"ok": True, "error": "", "digest": digest}


_baseline = start_page_baseline("HMAC Generator")
st.set_page_config(page_title="HMAC Generator", layout="wide")
apply_app_shell(active_page="HMAC Generator")
mark_page_baseline(_baseline, "shell-ready")

render_page_header(
    "HMAC Generator",
    "Generate keyed message digests for webhook verification and signature checks.",
    warning="Do not paste production secrets unless your session is trusted.",
)

with tool_form_panel("hmac_generator"):
    render_form_intro("Enter message, secret, and algorithm", "Use one full-width submit action for predictable mobile ergonomics.")
    with st.form("hmac-generator-form"):
        st.markdown('<div class="tool-panel-eyebrow">Message payload</div>', unsafe_allow_html=True)
        message_input = st.text_area("Message", height=180)
        st.markdown('<div class="tool-panel-eyebrow">Signing secret</div>', unsafe_allow_html=True)
        secret_input = st.text_input("Secret key", type="password")
        st.markdown('<div class="tool-panel-eyebrow">Digest algorithm</div>', unsafe_allow_html=True)
        algorithm_input = st.selectbox("Algorithm", HMAC_ALGORITHMS)
        submitted = st.form_submit_button("Generate HMAC digest", use_container_width=True)

if submitted:
    st.session_state["hmac_generator_result"] = generate_hmac_digest(message_input, secret_input, algorithm_input)
    st.session_state["hmac_generator_algorithm"] = algorithm_input

result = st.session_state.get("hmac_generator_result")
if result is None:
    render_empty_state("Ready to sign", "The generated HMAC digest appears here.")
    render_status_note(
        "Awaiting message and secret",
        "Provide a message, secret key, and algorithm, then select Generate HMAC digest.",
        tone="neutral",
    )

if result is not None:
    with tool_result_panel("hmac_generator_result_panel", related_to="hmac_generator"):
        render_section_heading("HMAC result", eyebrow="Result")
        if not result["ok"]:
            render_status_note("Outcome: HMAC input validation required", str(result["error"]), tone="warning")
        else:
            used_algorithm = st.session_state.get("hmac_generator_algorithm", "sha256")
            render_status_note("Outcome: HMAC digest generated", f"HMAC-{used_algorithm.upper()} computed successfully.", tone="success")
            st.code(str(result["digest"]), language=None)

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
