from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.id_generator import MAX_COUNT, generate_ulids, generate_uuids
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="ID Generator", layout="wide")
apply_app_shell(active_page="ID Generator")


render_page_header(
    "ID Generator",
    "Generate UUIDs (v4) or ULIDs in bulk. ULIDs sort lexicographically by creation time; UUIDs don't.",
)

with tool_form_panel("id_generator"):
    render_form_intro("Generate IDs", "Choose a type and how many to generate.")
    with st.form("id-generator-form"):
        id_type = st.radio("Type", ("UUID (v4)", "ULID"), horizontal=True)
        count = st.slider("Count", 1, MAX_COUNT, 10)
        submitted = st.form_submit_button("Generate")

if submitted:
    # Stored in session_state (not a local `result` gated on `submitted`) because
    # st.download_button triggers a rerun on click just like a plain widget outside
    # st.form -- on that rerun `submitted` is False again, which would otherwise make
    # the whole results section (download button included) disappear right after the
    # file downloads.
    st.session_state["id_generator_result"] = (
        generate_uuids(count) if id_type == "UUID (v4)" else generate_ulids(count)
    )
    st.session_state["id_generator_type"] = id_type
    st.session_state["id_generator_count"] = count

result = st.session_state.get("id_generator_result")
if result is None:
    render_empty_state("Ready to generate", "Generated IDs appear here after you generate them.")

if result is not None:
    result_type = st.session_state["id_generator_type"]
    result_count = st.session_state["id_generator_count"]
    with tool_result_panel("id_generator_result_panel", related_to="id_generator"):
        # Pluralized separately from the raw label -- "UUID (v4)" has its own
        # trailing parenthetical, so blindly appending "(s)" after the whole
        # label renders "10 UUID (v4)(s)" instead of "10 UUIDs (v4)".
        plural_labels = {"UUID (v4)": "UUIDs (v4)", "ULID": "ULIDs"}
        result_label = result_type if result_count == 1 else plural_labels[result_type]
        render_section_heading(f"{result_count} {result_label}", "Generated for this request only -- nothing is stored.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            ids_text = "\n".join(result["ids"])
            st.code(ids_text, language=None)
            st.dataframe(pd.DataFrame({"id": result["ids"]}), width="stretch", hide_index=True)
            st.download_button(
                "Download as .txt",
                ids_text,
                file_name=f"{'uuids' if result_type == 'UUID (v4)' else 'ulids'}.txt",
                mime="text/plain",
            )
