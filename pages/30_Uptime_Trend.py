from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from utils.http_tools import MAX_URL_LENGTH
from utils.latency_trend import MAX_CHECKS, MAX_INTERVAL_SECONDS, MIN_CHECKS, run_latency_trend
from utils.reporting import INCIDENT_MESSAGE_TARGETS, build_uptime_incident_message
from utils.ui import (
    apply_app_shell,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    tool_form_panel,
    tool_result_panel,
)


st.set_page_config(page_title="Uptime Trend", layout="wide")
apply_app_shell(active_page="Uptime Trend")


def _trend_figure(samples: list[dict]) -> go.Figure:
    ok_x = [s["index"] for s in samples if s["ok"]]
    ok_y = [s["response_time_ms"] for s in samples if s["ok"]]
    fail_x = [s["index"] for s in samples if not s["ok"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ok_x, y=ok_y, mode="lines+markers", name="Response time (ms)", line={"color": "#1668f4"}))
    if fail_x:
        fig.add_trace(
            go.Scatter(
                x=fail_x,
                y=[0] * len(fail_x),
                mode="markers",
                name="Failed check",
                marker={"color": "#d32f2f", "size": 12, "symbol": "x"},
            )
        )
    fig.update_layout(
        height=320,
        margin={"l": 40, "r": 20, "t": 20, "b": 40},
        xaxis_title="Check #",
        yaxis_title="Response time (ms)",
    )
    return fig


render_page_header(
    "Uptime Trend",
    "Run a short, one-off series of checks against a URL and see the latency trend for this session only.",
    warning="Do not use against third-party sites you do not own or have permission to test. Nothing here is stored between visits.",
)

with tool_form_panel("uptime_trend"):
    render_form_intro(
        "Run a probe",
        f"Runs {MIN_CHECKS}-{MAX_CHECKS} sequential checks in-memory, with an optional delay between each. Results disappear when you leave the page.",
    )
    with st.form("uptime-trend-form"):
        url = st.text_input("URL", placeholder="https://example.com", max_chars=MAX_URL_LENGTH)
        c1, c2 = st.columns(2)
        checks = c1.slider("Number of checks", MIN_CHECKS, MAX_CHECKS, 8)
        interval_seconds = c2.slider("Delay between checks (seconds)", 0.0, MAX_INTERVAL_SECONDS, 1.0, step=0.5)
        submitted = st.form_submit_button("Run probe")

if submitted:
    # Stored in session_state (not rendered directly here) because the sidebar's
    # quick-search box, favorite-star buttons, and any other widget outside this
    # page's st.form trigger reruns of their own -- on those reruns `submitted` is
    # False again, which would otherwise collapse this whole results section the
    # instant any of them is touched. `url` is captured alongside the result so the
    # incident message always matches what was actually probed.
    with st.spinner(f"Running {checks} checks..."):
        st.session_state["uptime_trend_result"] = run_latency_trend(url, checks, interval_seconds)
    st.session_state["uptime_trend_url"] = url

result = st.session_state.get("uptime_trend_result")

if result is None:
    render_empty_state("Ready to run a probe", "A latency trend chart and uptime summary appear here after the probe completes.")

if result is not None:
    url = st.session_state["uptime_trend_url"]
    with tool_result_panel("uptime_trend_result", related_to="uptime_trend"):
        render_section_heading("Trend result", eyebrow="Result")
        if not result["ok"]:
            st.error(result["error"])
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Uptime", f"{result['uptime_pct']}%")
            m2.metric("Avg latency", f"{result['avg_latency_ms']} ms" if result["avg_latency_ms"] is not None else "N/A")
            m3.metric("Min latency", f"{result['min_latency_ms']} ms" if result["min_latency_ms"] is not None else "N/A")
            m4.metric("Max latency", f"{result['max_latency_ms']} ms" if result["max_latency_ms"] is not None else "N/A")

            st.plotly_chart(_trend_figure(result["samples"]), width="stretch")

            with st.expander("Raw samples"):
                st.table(
                    [
                        {
                            "Check": s["index"],
                            "Status": s["status_code"] or "Failed",
                            "Response time (ms)": s["response_time_ms"] if s["response_time_ms"] is not None else "-",
                            "Error": s["error"] or "",
                        }
                        for s in result["samples"]
                    ]
                )

            render_section_heading(
                "Incident message",
                "Ready to paste into a Slack or Teams channel for a live incident update.",
                eyebrow="Chat export",
            )
            incident_tabs = st.tabs([target.title() for target in INCIDENT_MESSAGE_TARGETS])
            for tab, target in zip(incident_tabs, INCIDENT_MESSAGE_TARGETS, strict=True):
                with tab:
                    incident_message = build_uptime_incident_message(url, result, target)
                    st.code(incident_message["message"], language=None)
