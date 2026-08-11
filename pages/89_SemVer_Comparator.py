from __future__ import annotations

import streamlit as st

from utils.semver_tools import MAX_INPUT_LENGTH, compare_versions, parse_semver, sort_versions
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="SemVer Comparator", layout="wide")
apply_app_shell(active_page="SemVer Comparator")


render_page_header(
    "SemVer Comparator",
    "Compare two Semantic Versioning 2.0.0 version strings, or sort a whole list by precedence.",
)

compare_tab, sort_tab = st.tabs(["Compare two versions", "Sort a list"])

with compare_tab:
    with tool_form_panel("semver_compare"):
        render_form_intro("Enter two versions", "Both must be valid SemVer 2.0.0 strings, e.g. 1.2.3-beta.1+build.5.")
        with st.form("semver-compare-form"):
            c1, c2 = st.columns(2)
            version_a = c1.text_input("Version A", placeholder="1.2.3")
            version_b = c2.text_input("Version B", placeholder="1.10.0")
            compare_submitted = st.form_submit_button("Compare")

    if compare_submitted:
        parsed_a, parsed_b = parse_semver(version_a), parse_semver(version_b)
        if not parsed_a["ok"]:
            compare_result = {"ok": False, "error": parsed_a["error"]}
        elif not parsed_b["ok"]:
            compare_result = {"ok": False, "error": parsed_b["error"]}
        else:
            cmp = compare_versions(parsed_a, parsed_b)
            if cmp < 0:
                verdict = f"{version_a.strip()} is older than {version_b.strip()}"
            elif cmp > 0:
                verdict = f"{version_a.strip()} is newer than {version_b.strip()}"
            else:
                verdict = f"{version_a.strip()} has the same precedence as {version_b.strip()}"
            compare_result = {"ok": True, "verdict": verdict}
        st.session_state["semver_compare_result"] = compare_result

    compare_result = st.session_state.get("semver_compare_result")

    if compare_result is None:
        render_empty_state("Ready to compare", "The precedence result appears here.")

    if compare_result is not None:
        with tool_result_panel("semver_compare_result_panel", related_to="semver_tools"):
            render_section_heading("Comparison", eyebrow="Result")
            if not compare_result["ok"]:
                st.error(compare_result["error"])
            else:
                st.success(compare_result["verdict"])

with sort_tab:
    with tool_form_panel("semver_sort"):
        render_form_intro("Paste a list of versions", "One version per line.")
        with st.form("semver-sort-form"):
            versions_input = st.text_area(
                "Versions",
                height=200,
                max_chars=MAX_INPUT_LENGTH,
                placeholder="1.2.3\n1.10.0\n1.2.3-beta.1\n2.0.0",
            )
            descending = st.checkbox("Descending (newest first)", value=False)
            sort_submitted = st.form_submit_button("Sort")

    if sort_submitted:
        versions = [line for line in versions_input.splitlines() if line.strip()]
        st.session_state["semver_sort_result"] = sort_versions(versions, descending)

    sort_result = st.session_state.get("semver_sort_result")

    if sort_result is None:
        render_empty_state("Ready to sort", "The sorted version list appears here.")

    if sort_result is not None:
        with tool_result_panel("semver_sort_result_panel", related_to="semver_tools"):
            render_section_heading("Sorted versions", eyebrow="Result")
            if not sort_result["ok"]:
                st.error(sort_result["error"])
            else:
                st.code("\n".join(sort_result["sorted"]), language=None)
