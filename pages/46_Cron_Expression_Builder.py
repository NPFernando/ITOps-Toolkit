from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.cron_builder import FIELD_MODES, build_cron_expression
from utils.ui import apply_app_shell, render_form_intro, render_page_header, render_section_heading, tool_form_panel, tool_result_panel


st.set_page_config(page_title="Cron Expression Builder", layout="wide")
apply_app_shell(active_page="Cron Expression Builder")


render_page_header(
    "Cron Expression Builder",
    "Build a 5-field cron expression from simple controls -- the reverse of Cron Explainer.",
)

WEEKDAY_LABELS = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}
MONTH_LABELS = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def _field_controls(label: str, key: str, low: int, high: int, value_labels: dict[int, str] | None = None):
    mode = st.selectbox(f"{label} mode", FIELD_MODES, key=f"cron_builder_{key}_mode")
    step = 0
    values: list[int] = []
    if mode == "Every N":
        step = st.number_input(f"Every N {label.lower()}(s)", min_value=1, max_value=high, value=1, key=f"cron_builder_{key}_step")
    elif mode == "Specific":
        options = list(range(low, high + 1))
        format_func = (lambda v: value_labels[v]) if value_labels else None
        values = st.multiselect(f"Specific {label.lower()} value(s)", options, format_func=format_func, key=f"cron_builder_{key}_values")
    return mode, step, values


with tool_form_panel("cron_builder"):
    render_form_intro("Build a schedule", "Choose how each field should behave.")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        minute_mode, minute_step, minute_values = _field_controls("Minute", "minute", 0, 59)
    with col2:
        hour_mode, hour_step, hour_values = _field_controls("Hour", "hour", 0, 23)
    with col3:
        day_mode, day_step, day_values = _field_controls("Day of month", "day", 1, 31)
    with col4:
        month_mode, month_step, month_values = _field_controls("Month", "month", 1, 12, MONTH_LABELS)
    with col5:
        weekday_mode, weekday_step, weekday_values = _field_controls("Weekday", "weekday", 0, 6, WEEKDAY_LABELS)

result = build_cron_expression(
    minute_mode, int(minute_step), minute_values,
    hour_mode, int(hour_step), hour_values,
    day_mode, int(day_step), day_values,
    month_mode, int(month_step), month_values,
    weekday_mode, int(weekday_step), weekday_values,
)

with tool_result_panel("cron_builder_result", related_to="cron_builder"):
    render_section_heading("Result", "Resulting cron expression, readable description, and next run times.")
    if not result["ok"]:
        st.error(result["error"])
    else:
        st.code(result["expression"], language=None)
        st.info(result["description"])
        if result["next_runs"]:
            st.dataframe(pd.DataFrame({"run_time": result["next_runs"]}), width="stretch", hide_index=True)
