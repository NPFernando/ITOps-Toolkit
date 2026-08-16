from __future__ import annotations

import streamlit as st

from utils.text_tools import MAX_JSON_LENGTH, format_json_text, json_stats, search_json_paths
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_download_panel,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="JSON Formatter", layout="wide")
apply_app_shell(active_page="JSON Formatter")


render_page_header(
    "JSON Formatter",
    "Validate, format, minify, search, and explore JSON in a tree or text view.",
    warning="Do not paste secrets, production tokens, or sensitive customer data.",
)

with tool_form_panel("json_formatter"):
    render_form_intro("Process JSON", "Validate syntax, pretty-print JSON, or minify it for compact transport.")
    with st.form("json-form"):
        json_input = st.text_area("JSON input", height=260, max_chars=MAX_JSON_LENGTH, placeholder='{"status": "ok"}')
        c1, c2 = st.columns([3, 1])
        with c1:
            action = st.radio("Action", ["Validate JSON", "Format JSON", "Minify JSON"], horizontal=True)
        with c2:
            indent = st.selectbox("Indent", [2, 4])
        action_submitted = st.form_submit_button("Run JSON action")
        validate_clicked = action_submitted and action == "Validate JSON"
        format_clicked = action_submitted and action == "Format JSON"
        minify_clicked = action_submitted and action == "Minify JSON"

if validate_clicked or format_clicked or minify_clicked:
    # Stored in session_state (not rendered directly here) because the "Expand all"
    # toggle, the search box, and the export download button below all trigger their
    # own reruns -- on those reruns the transient *_clicked flags are False again,
    # which would otherwise collapse this whole results section the instant any of
    # them is touched.
    st.session_state["json_formatter_state"] = {
        "json_input": json_input,
        "result": format_json_text(json_input, minify=minify_clicked, indent=indent),
        "format_clicked": format_clicked,
        "minify_clicked": minify_clicked,
    }

state = st.session_state.get("json_formatter_state")

if state is None:
    render_empty_state("Ready to process JSON", "Validation status and formatted output appear here after you run an action.")

if validate_clicked or format_clicked or minify_clicked:
    result = format_json_text(json_input, minify=minify_clicked, indent=indent)
    with tool_result_panel("json_result"):
        render_section_heading("JSON result", "Validation status and transformed output.")
        if not result["ok"]:
            st.error(result["error"])
            error_line = result.get("line")
            if error_line:
                source_lines = json_input.splitlines()
                if 0 < error_line <= len(source_lines):
                    start = max(0, error_line - 2)
                    end = min(len(source_lines), error_line + 1)
                    snippet_lines = source_lines[start:end]
                    numbered = "\n".join(
                        f"{start + i + 1:>4} | {line}" for i, line in enumerate(snippet_lines)
                    )
                    st.code(numbered, language=None)
        else:
            st.success("Valid JSON")
            stats = json_stats(result["parsed"])
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Type", stats["type"])
            s2.metric("Top-level items", stats["top_level_count"] if stats["top_level_count"] is not None else "-")
            s3.metric("Max depth", stats["max_depth"])
            s4.metric("Total nodes", stats["node_count"])

            tree_tab, text_tab = st.tabs(["Tree view", "Text view"])
            with tree_tab:
                expand_all = st.toggle("Expand all", value=True, key="json_tree_expand_all")
                st.json(result["parsed"], expanded=expand_all)
            with text_tab:
                st.code(result["result"], language="json")

            render_section_heading("Search JSON", "Find keys or values containing a term, with their JSON path.", eyebrow="Navigate")
            search_query = st.text_input("Search keys and values", key="json_search_query")
            if search_query:
                matches = search_json_paths(result["parsed"], search_query)
                if matches:
                    st.table(
                        [
                            {"Path": m["path"], "Matched": m["match"], "Value": m["value"]}
                            for m in matches
                        ]
                    )
                    if len(matches) >= 200:
                        st.caption("Showing the first 200 matches.")
                else:
                    st.info("No keys or values matched that search.")

            if format_clicked or minify_clicked:
                file_name = "formatted.json" if format_clicked else "minified.json"
                with tool_download_panel("json_export"):
                    render_section_heading("Export", "Download the current in-memory JSON result.", eyebrow="Downloads")
                    st.download_button(
                        "Download JSON",
                        result["result"],
                        file_name=file_name,
                        mime="application/json",
                    )
