from __future__ import annotations

import streamlit as st

from utils.m365_sku_reference import search_skus
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="M365 SKU Decoder", layout="wide")
apply_app_shell(active_page="M365 SKU Decoder")


st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      div[data-testid="stTextInput"] input {
        font-size: 1rem;
      }
      div[data-testid="stTable"] table th,
      div[data-testid="stTable"] table td {
        white-space: normal !important;
        word-break: break-word;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


render_page_header(
    "M365 SKU Decoder",
    "Convert Microsoft 365 license SKU strings and GUIDs to readable product names.",
)

with tool_form_panel("m365_sku_decoder"):
    render_form_intro("Search SKUs", "Search by SKU string (e.g. SPE_E3), GUID, or product name.")
    query = st.text_input("Search", placeholder="SPE_E3, 05e9a617-..., Business Premium...")

results = search_skus(query)
with tool_result_panel("m365_sku_decoder_result", related_to="m365_sku_decoder"):
    render_section_heading("SKUs", f"{len(results)} matching SKU(s).")
    if results:
        st.dataframe(
            [
                {"SKU string": entry.sku_string, "GUID": entry.guid, "Product name": entry.product_name}
                for entry in results
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No SKUs matched that search.")
