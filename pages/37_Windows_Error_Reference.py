from __future__ import annotations

import streamlit as st

from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel
from utils.windows_error_reference import search_errors


st.set_page_config(page_title="Windows Error Reference", layout="wide")
apply_app_shell(active_page="Windows Error Reference")


render_page_header(
    "Windows Error Reference",
    "Look up Windows/Win32 error codes (decimal or hex) -- system errors, service control, RPC, HRESULT, and NTSTATUS/BSOD codes.",
)

with tool_form_panel("windows_error_reference"):
    render_form_intro("Search errors", "Search by decimal code, hex code (e.g. 0x80070005), category, or keyword.")
    query = st.text_input("Search", placeholder="5, 0xC0000005, RPC, access denied...")

results = search_errors(query)
with tool_result_panel("windows_error_reference_result", related_to="windows_error_reference"):
    render_section_heading("Errors", f"{len(results)} matching error(s).")
    if results:
        st.table(
            [
                {
                    "Code": entry.code,
                    "Hex": entry.hex_code,
                    "Category": entry.category,
                    "Name": entry.name,
                    "Description": entry.description,
                }
                for entry in results
            ]
        )
    else:
        st.info("No errors matched that search.")
