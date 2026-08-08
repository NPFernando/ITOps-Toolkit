from __future__ import annotations

import streamlit as st

from utils.file_integrity import find_matching_algorithm, hash_bytes
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="File Integrity Comparator", layout="wide")
apply_app_shell(active_page="File Integrity Comparator")


render_page_header(
    "File Integrity Comparator",
    "Compare two files, or check one file against an expected hash, to confirm a download wasn't corrupted or tampered with.",
)

with tool_form_panel("file_integrity"):
    render_form_intro(
        "Compare files",
        "Upload a second file to compare directly, or paste an expected hash to check against. Either or both.",
    )
    with st.form("file-integrity-form"):
        file_a = st.file_uploader("File A", key="file_integrity_a")
        file_b = st.file_uploader("File B (optional)", key="file_integrity_b")
        expected_hash = st.text_input("Expected hash (optional)", placeholder="e.g. a SHA-256 value from a download page")
        submitted = st.form_submit_button("Compare")

if submitted:
    if file_a is None:
        st.session_state["file_integrity_state"] = {"error": "Upload at least File A."}
    else:
        result_a = hash_bytes(file_a.getvalue())
        state: dict = {"error": None, "file_a_name": file_a.name, "result_a": result_a}
        if file_b is not None:
            state["file_b_name"] = file_b.name
            state["result_b"] = hash_bytes(file_b.getvalue())
        if expected_hash.strip():
            state["expected_hash"] = expected_hash.strip()
            state["matched_algorithm"] = find_matching_algorithm(result_a.get("digests", {}), expected_hash) if result_a["ok"] else None
        st.session_state["file_integrity_state"] = state

state = st.session_state.get("file_integrity_state")

if state is None:
    render_empty_state("Ready to compare", "Hashes and a match/mismatch verdict appear here after comparison.")

if state is not None:
    with tool_result_panel("file_integrity_result", related_to="file_integrity"):
        render_section_heading("Result", "MD5, SHA-1, SHA-256, and SHA-512 digests.")
        if state.get("error"):
            st.error(state["error"])
        else:
            result_a = state["result_a"]
            if not result_a["ok"]:
                st.error(result_a["error"])
            else:
                st.markdown(f"**{state['file_a_name']}** ({result_a['size_bytes']:,} bytes)")
                for algo, digest in result_a["digests"].items():
                    st.code(f"{algo}: {digest}", language=None)

                if "result_b" in state:
                    result_b = state["result_b"]
                    st.markdown(f"**{state['file_b_name']}** ({result_b.get('size_bytes', 0):,} bytes)")
                    if not result_b["ok"]:
                        st.error(result_b["error"])
                    else:
                        for algo, digest in result_b["digests"].items():
                            st.code(f"{algo}: {digest}", language=None)
                        if result_a["digests"] == result_b["digests"]:
                            st.success("Files are identical -- all digests match.")
                        else:
                            st.error("Files differ -- digests do not match.")

                if "expected_hash" in state:
                    # Always checked against File A only -- named explicitly so this
                    # isn't misread as confirming File B when both are supplied.
                    if state["matched_algorithm"]:
                        st.success(f"File A matches the expected hash ({state['matched_algorithm'].upper()}).")
                    else:
                        st.error("File A does not match the expected hash against any computed algorithm.")
