from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

import streamlit as st


DEV_BASELINE_ENV = "ITOPS_DEV_BASELINE"
_SESSION_HISTORY_KEY = "_itops_dev_baseline_history"
_TRUTHY = {"1", "true", "yes", "on"}


def dev_baseline_enabled() -> bool:
    value = os.getenv(DEV_BASELINE_ENV, "")
    return value.strip().lower() in _TRUTHY


@dataclass
class PageBaseline:
    surface: str
    started_at: float = field(default_factory=time.perf_counter)
    checkpoints: list[tuple[str, float]] = field(default_factory=list)

    def mark(self, label: str) -> None:
        elapsed_ms = (time.perf_counter() - self.started_at) * 1000
        self.checkpoints.append((label, elapsed_ms))


def start_page_baseline(surface: str) -> PageBaseline | None:
    if not dev_baseline_enabled():
        return None
    return PageBaseline(surface=surface)


def mark_page_baseline(baseline: PageBaseline | None, label: str) -> None:
    if baseline is not None:
        baseline.mark(label)


def render_page_baseline(baseline: PageBaseline | None) -> None:
    if baseline is None:
        return

    total_ms = (time.perf_counter() - baseline.started_at) * 1000
    now_utc = datetime.now(UTC).strftime("%H:%M:%S")
    sample = {"surface": baseline.surface, "render_ms": round(total_ms, 1), "captured_utc": now_utc}
    history = list(st.session_state.get(_SESSION_HISTORY_KEY, []))
    history.append(sample)
    st.session_state[_SESSION_HISTORY_KEY] = history[-20:]

    with st.sidebar.expander("Dev baseline metrics", expanded=False):
        st.caption(f"Enabled by {DEV_BASELINE_ENV}=1. Session-only timings; no user input is captured.")
        st.metric(f"{baseline.surface} render", f"{total_ms:.1f} ms")
        if baseline.checkpoints:
            st.caption("Checkpoints")
            checkpoint_rows = [
                {"label": label, "elapsed_ms": f"{elapsed_ms:.1f}"}
                for label, elapsed_ms in baseline.checkpoints
            ]
            st.dataframe(checkpoint_rows, width="stretch", hide_index=True)
        st.caption("Recent samples (this browser session)")
        st.dataframe(list(reversed(st.session_state[_SESSION_HISTORY_KEY][-8:])), width="stretch", hide_index=True)
