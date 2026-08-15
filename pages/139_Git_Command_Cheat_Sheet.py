from __future__ import annotations

import streamlit as st

from utils.dev_baseline import mark_page_baseline, render_page_baseline, start_page_baseline
from utils.ui import (
    apply_app_shell,
    render_control_heading,
    render_empty_state,
    render_form_intro,
    render_page_header,
    render_section_heading,
    render_status_note,
    tool_form_panel,
    tool_result_panel,
)


_GIT_COMMANDS: tuple[dict[str, str], ...] = (
    {"category": "Setup", "command": "git config --global user.name \"Jane Ops\"", "description": "Set commit author name."},
    {"category": "Setup", "command": "git config --global user.email \"jane@example.com\"", "description": "Set commit author email."},
    {"category": "Daily", "command": "git status -sb", "description": "Compact status for branch and file changes."},
    {"category": "Daily", "command": "git pull --rebase", "description": "Update branch while keeping a linear history."},
    {"category": "Daily", "command": "git add -p", "description": "Interactively stage partial changes."},
    {"category": "Branching", "command": "git switch -c feature/my-change", "description": "Create and switch to a new branch."},
    {"category": "Branching", "command": "git branch --merged", "description": "List branches already merged."},
    {"category": "Recovery", "command": "git restore --staged <file>", "description": "Unstage a file without losing edits."},
    {"category": "Recovery", "command": "git reflog", "description": "Inspect recent HEAD movements for recovery."},
    {"category": "Recovery", "command": "git reset --hard HEAD~1", "description": "Drop latest commit and local changes (destructive)."},
)


def _filter_commands(query: str, category: str) -> list[dict[str, str]]:
    needle = (query or "").strip().lower()
    rows = [row for row in _GIT_COMMANDS if category == "All" or row["category"] == category]
    if not needle:
        return rows
    return [row for row in rows if needle in row["command"].lower() or needle in row["description"].lower()]


_baseline = start_page_baseline("Git Command Cheat Sheet")
st.set_page_config(page_title="Git Command Cheat Sheet", layout="wide")
apply_app_shell(active_page="Git Command Cheat Sheet")
mark_page_baseline(_baseline, "shell-ready")
mark_page_baseline(_baseline, "wave27-shell-mobile")
mark_page_baseline(_baseline, "wave28-shell-mobile")
mark_page_baseline(_baseline, "wave29-shell-mobile")

render_page_header("Git Command Cheat Sheet", "Filter practical Git commands by category and copy snippets quickly on mobile or desktop.")

categories = ("All", "Setup", "Daily", "Branching", "Recovery")
with tool_form_panel("git_command_cheat_sheet"):
    render_form_intro("Filter command catalog", "Grouped filters and a full-width apply action keep the reference easy to use on small screens.")
    with st.form("git-command-cheat-sheet-form"):
        render_control_heading("Search")
        query = st.text_input("Search command or description", placeholder="status, rebase, reflog")
        render_control_heading("Category")
        category = st.selectbox("Command category", options=categories)
        render_control_heading("Primary action")
        submitted = st.form_submit_button("Show matching commands", use_container_width=True)

if submitted or "git_command_cheat_sheet_result" not in st.session_state:
    st.session_state["git_command_cheat_sheet_result"] = {
        "rows": _filter_commands(query if submitted else "", category if submitted else "All"),
        "submitted": submitted,
    }

result = st.session_state.get("git_command_cheat_sheet_result", {"rows": [], "submitted": False})
rows = result["rows"]
was_submitted = bool(result["submitted"])
with tool_result_panel("git_command_cheat_sheet_results", related_to="git_command_cheat_sheet"):
    render_section_heading("Command list", eyebrow="Reference")
    if not rows:
        render_empty_state("No commands matched", "Try another search phrase or reset category to All.")
        render_status_note(
            "Outcome: command filtering blocked",
            "No commands matched the current search and category. Adjust keywords or switch category to All.",
            tone="warning",
        )
    else:
        if was_submitted:
            render_status_note(
                "Outcome: command list filtered",
                f"Showing {len(rows)} matching command(s). Scan entries below and copy what you need.",
                tone="success",
            )
        else:
            render_status_note(
                "Outcome: command reference ready",
                f"Showing {len(rows)} commands. Apply filters to narrow the list.",
                tone="neutral",
            )
        for row in rows:
            st.markdown(f"**{row['category']}** — {row['description']}")
            st.code(row["command"], language="bash")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
