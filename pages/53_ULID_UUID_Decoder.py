from __future__ import annotations

import streamlit as st

from utils.id_decoder import MAX_INPUT_LENGTH, decode_ulid, decode_uuid
from utils.ui import apply_app_shell, render_empty_state, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="ULID/UUID Decoder", layout="wide")
apply_app_shell(active_page="ULID/UUID Decoder")


render_page_header(
    "ULID/UUID Decoder",
    "Decode a ULID or UUID's embedded creation timestamp -- the reverse of ID Generator.",
)

ulid_tab, uuid_tab = st.tabs(["ULID", "UUID"])

with ulid_tab:
    with tool_form_panel("ulid_decoder"):
        render_form_intro("Enter a ULID", "26 characters, Crockford Base32-encoded -- updates live as you type.")
        ulid_input = st.text_input("ULID", max_chars=MAX_INPUT_LENGTH, placeholder="01ARZ3NDEKTSV4RRFFQ69G5FAV")

    with tool_result_panel("ulid_decode_result", related_to="ulid_uuid_decoder"):
        render_section_heading("Decoded ULID", eyebrow="Result")
        if not ulid_input.strip():
            render_empty_state("Ready for a ULID", "The embedded timestamp and randomness appear here as soon as you type.")
        else:
            result = decode_ulid(ulid_input)
            if not result["ok"]:
                st.error(result["error"])
            else:
                c1, c2 = st.columns(2)
                c1.metric("Created (UTC)", result["datetime_utc"])
                c2.metric("Epoch milliseconds", result["timestamp_ms"])
                st.caption(f"Randomness (hex): {result['randomness_hex']}")

with uuid_tab:
    with tool_form_panel("uuid_decoder"):
        render_form_intro("Enter a UUID", "Any RFC 4122 UUID -- updates live as you type.")
        uuid_input = st.text_input("UUID", max_chars=MAX_INPUT_LENGTH, placeholder="f47ac10b-58cc-4372-a567-0e02b2c3d479")

    with tool_result_panel("uuid_decode_result", related_to="ulid_uuid_decoder"):
        render_section_heading("Decoded UUID", eyebrow="Result")
        if not uuid_input.strip():
            render_empty_state("Ready for a UUID", "Version, variant, and (for v1/v7) the embedded timestamp appear here as soon as you type.")
        else:
            result = decode_uuid(uuid_input)
            if not result["ok"]:
                st.error(result["error"])
            else:
                if result["version"] is None:
                    st.metric("Version", "N/A")
                    st.caption("This UUID has no version bits set (nil or max UUID).")
                else:
                    st.metric("Version", result["version"])
                # Not an st.metric -- uuid.UUID.variant returns a full phrase
                # ("specified in RFC 4122", "reserved for NCS compatibility"),
                # not the short number/word every other metric here shows.
                st.caption(f"Variant: {result['variant']}")
                if result["timestamp_supported"]:
                    st.metric("Created (UTC)", result["datetime_utc"])
                elif result["version"] is not None:
                    st.info(f"UUID version {result['version']} does not embed a creation timestamp.")
