from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.ai_tools import analyze_logs_rule_based, optional_ai_configured, optional_ai_summary
from utils.text_tools import MAX_LOG_LENGTH
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


st.set_page_config(page_title="Log Troubleshooting Assistant", layout="wide")
apply_app_shell(active_page="Log Troubleshooting Assistant")


def _status(severity: str) -> None:
    if severity == "Critical":
        st.error(severity)
    elif severity == "Warning":
        st.warning(severity)
    else:
        st.info(severity)


render_page_header(
    "Log Troubleshooting Assistant",
    "Find common operational error patterns in pasted logs.",
    warning="Remove secrets before pasting logs. Do not paste passwords, API keys, tokens, or customer-sensitive data.",
)

with tool_form_panel("log_troubleshooting"):
    render_form_intro("Analyze logs", "Paste sanitized log text to match common operational failure patterns.")
    ai_available = optional_ai_configured()
    with st.form("log-form"):
        log_text = st.text_area("Log or error text", height=300, max_chars=MAX_LOG_LENGTH)
        use_ai_summary = st.checkbox(
            "Generate optional Azure AI summary",
            value=False,
            disabled=not ai_available,
            help="When enabled, only sanitized log text for this submission is sent to the configured Azure OpenAI deployment.",
        )
        submitted = st.form_submit_button("Analyze logs")
    if ai_available:
        render_status_note(
            "Azure AI summary available",
            "Optional and off by default. When checked, only sanitized logs from this submission are sent to Azure OpenAI.",
            tone="info",
        )
    else:
        render_status_note(
            "Azure AI summary unavailable",
            "Configure Azure OpenAI settings to enable optional summaries. Rule-based analysis still works.",
            tone="neutral",
        )

if not submitted:
    render_empty_state("Ready to analyze sanitized logs", "Findings, likely causes, commands, and safe next steps appear after analysis.")

if submitted:
    result = analyze_logs_rule_based(log_text)
    with tool_result_panel("log_result"):
        render_section_heading("Log analysis", "Rule-based findings and safe operational next steps.")
        if not result["ok"]:
            st.error(result["error"])
        else:
            ai_state = optional_ai_summary(result["sanitized"], findings=result["findings"], opted_in=use_ai_summary)
            if ai_state.get("enabled"):
                render_status_note(
                    "Optional Azure AI summary",
                    ai_state["summary"],
                    tone="ai",
                )
            else:
                status_tone = "warning" if ai_state.get("status") == "error" else "neutral"
                render_status_note(
                    "Optional Azure AI summary",
                    ai_state["message"],
                    tone=status_tone,
                )

            summary_rows = [
                {
                    "severity": item["severity"],
                    "likely_issue": item["likely_issue"],
                    "possible_cause": item["possible_cause"],
                }
                for item in result["findings"]
            ]
            st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)

            for item in result["findings"]:
                with st.expander(item["likely_issue"], expanded=True):
                    _status(item["severity"])
                    st.markdown("**Possible cause**")
                    st.write(item["possible_cause"])
                    st.markdown("**Commands to check**")
                    st.code("\n".join(item["commands_to_check"]), language="bash")
                    st.markdown("**Safe next steps**")
                    for step in item["safe_next_steps"]:
                        st.write(f"- {step}")
