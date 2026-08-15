from __future__ import annotations

import importlib.util
import os
import platform
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import streamlit as st

from utils import roadmap
from utils.ai_tools import azure_openai_missing_keys, optional_ai_configured
from utils.dev_baseline import DEV_BASELINE_ENV, dev_baseline_enabled, mark_page_baseline, render_page_baseline, start_page_baseline
from utils.dns_tools import resolve_records
from utils.github_issues import fetch_public_issues
from utils.http_tools import check_http_status
from utils.project_links import github_repository_slug, github_repository_url
from utils.ssl_tools import get_certificate_info
from utils.ui import TOOLS, apply_app_shell, render_page_header, render_section_heading, tool_result_panel


@st.cache_data(show_spinner=False, ttl=120)
def _cache_smoke_probe() -> str:
    return "ok"


def _status(value: bool, ok: str = "Available", not_ok: str = "Unavailable") -> str:
    return ok if value else not_ok


def _rows_table(rows: list[dict[str, str]]) -> None:
    st.dataframe(rows, width="stretch", hide_index=True)


def _safe_url_for_display(value: str) -> str:
    """Redact URL userinfo before rendering diagnostics details."""
    raw = (value or "").strip()
    if not raw:
        return "Not configured"
    try:
        parts = urlsplit(raw)
    except ValueError:
        return "Invalid URL format"
    if not parts.scheme or not parts.netloc:
        return "Invalid URL format"
    # Strip any embedded credentials from netloc while preserving host/port.
    netloc = parts.hostname or ""
    if parts.port is not None:
        netloc = f"{netloc}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def _status_bucket(status: str) -> str:
    normalized = str(status or "").strip().lower()
    fail_values = {"fail", "invalid", "missing", "unavailable", "no", "not installed"}
    warn_values = {"warning", "warn", "disabled", "not configured", "not detected"}
    if normalized in fail_values:
        return "fail"
    if normalized in warn_values:
        return "warn"
    return "pass"


def _adapter_capability_rows() -> list[dict[str, str]]:
    return [
        {
            "Check": "HTTP adapter callable",
            "Status": _status(callable(check_http_status), "Pass", "Fail"),
            "Details": "HTTP checker adapter import and callable contract.",
        },
        {
            "Check": "DNS adapter callable",
            "Status": _status(callable(resolve_records), "Pass", "Fail"),
            "Details": "DNS resolver adapter import and callable contract.",
        },
        {
            "Check": "SSL adapter callable",
            "Status": _status(callable(get_certificate_info), "Pass", "Fail"),
            "Details": "TLS certificate adapter import and callable contract.",
        },
        {
            "Check": "GitHub adapter callable",
            "Status": _status(callable(fetch_public_issues), "Pass", "Fail"),
            "Details": "Roadmap GitHub Issues adapter import and callable contract.",
        },
        {
            "Check": "AI adapter path available",
            "Status": "Pass" if optional_ai_configured() else "Warn",
            "Details": "Optional AI summary path. Not configured is acceptable for public-safe default operation.",
        },
    ]


_baseline = start_page_baseline("Health Diagnostics")
st.set_page_config(page_title="Health Diagnostics", page_icon=":material/monitor_heart:", layout="wide")
apply_app_shell(active_page="Health Diagnostics")
mark_page_baseline(_baseline, "shell-ready")

render_page_header(
    "Health Diagnostics",
    "Public-safe runtime checks for non-sensitive app health. No secrets or user payloads are shown.",
)

with tool_result_panel("health_diagnostics_runtime"):
    render_section_heading("Runtime basics", "Version and app-context signals that are safe to display.", eyebrow="Runtime")
    repo_slug = github_repository_slug()
    runtime_rows = [
            {"Check": "Streamlit version", "Status": st.__version__, "Details": "Installed runtime package version."},
            {"Check": "Python version", "Status": platform.python_version(), "Details": "Interpreter version for this app process."},
            {"Check": "App root detected", "Status": _status((Path.cwd() / "app.py").exists(), "Yes", "No"), "Details": str(Path.cwd())},
            {"Check": "Registered tools", "Status": str(len(TOOLS)), "Details": "Total tools currently registered in shared metadata."},
            {
                "Check": "Configured GitHub repo",
                "Status": _status(repo_slug is not None, "Valid", "Invalid"),
                "Details": _safe_url_for_display(github_repository_url()),
            },
        ]
    _rows_table(runtime_rows)

with tool_result_panel("health_diagnostics_integrations"):
    render_section_heading(
        "Optional integrations",
        "Availability indicators only. Credentials and secret values are never displayed.",
        eyebrow="Integrations",
    )
    missing_azure = azure_openai_missing_keys()
    integration_rows = [
            {
                "Check": "Azure OpenAI (optional)",
                "Status": _status(optional_ai_configured(), "Configured", "Not configured"),
                "Details": "Missing keys: none" if not missing_azure else f"Missing keys: {', '.join(missing_azure)}",
            },
            {
                "Check": "OpenAI SDK package",
                "Status": _status(importlib.util.find_spec("openai") is not None, "Installed", "Not installed"),
                "Details": "Package detection only; no network calls performed.",
            },
            {
                "Check": "Roadmap seed data file",
                "Status": _status(roadmap.ROADMAP_SEED_PATH.exists(), "Present", "Missing"),
                "Details": str(roadmap.ROADMAP_SEED_PATH),
            },
        ]
    _rows_table(integration_rows)

with tool_result_panel("health_diagnostics_feature_flags"):
    render_section_heading("Feature flags", "Non-sensitive baseline flags and runtime toggles.", eyebrow="Flags")
    feature_rows = [
            {
                "Check": f"{DEV_BASELINE_ENV}",
                "Status": _status(dev_baseline_enabled(), "Enabled", "Disabled"),
                "Details": "Controls session-only render timing metrics in the sidebar.",
            },
            {
                "Check": "Streamlit cache_data support",
                "Status": _status(callable(getattr(st, "cache_data", None)), "Enabled", "Unavailable"),
                "Details": "Required for in-process read-only caching helpers.",
            },
            {
                "Check": "Pytest runtime context",
                "Status": _status(bool(os.getenv("PYTEST_CURRENT_TEST")), "Detected", "Not detected"),
                "Details": "Used only for safe test-isolated cache keys in selected pages.",
            },
        ]
    _rows_table(feature_rows)

with tool_result_panel("health_diagnostics_smoke"):
    render_section_heading(
        "Safe smoke checks",
        "Zero-secret probes that validate local runtime wiring without external payloads.",
        eyebrow="Smoke",
    )
    cache_probe_ok = _cache_smoke_probe() == "ok"
    try:
        seed_items = roadmap.load_seed_items()
        seed_result = "Pass"
        seed_details = f"Loaded {len(seed_items)} roadmap seed item(s)."
    except Exception as exc:  # pragma: no cover - exercised in tests via normal pass path
        seed_result = "Fail"
        seed_details = f"{type(exc).__name__}: {exc}"
    smoke_rows = [
            {
                "Check": "Cache probe",
                "Status": "Pass" if cache_probe_ok else "Fail",
                "Details": "st.cache_data function call returned expected sentinel value.",
            },
            {
                "Check": "Roadmap seed parse",
                "Status": seed_result,
                "Details": seed_details,
            },
            {
                "Check": "GitHub URL parsing",
                "Status": "Pass" if github_repository_slug() is not None else "Fail",
                "Details": "Repository URL parsed into owner/repo format.",
            },
        ]
    _rows_table(smoke_rows)

with tool_result_panel("health_diagnostics_adapter_capability"):
    render_section_heading("Adapter capabilities", "Import/callable probes for key runtime adapters.", eyebrow="Adapters")
    capability_rows = _adapter_capability_rows()
    _rows_table(capability_rows)

with tool_result_panel("health_diagnostics_reliability_score"):
    render_section_heading("Reliability score", "Pass/Warn/Fail summary from diagnostics checks.", eyebrow="Score")
    all_rows = [*runtime_rows, *integration_rows, *feature_rows, *smoke_rows, *capability_rows]
    pass_count = sum(1 for row in all_rows if _status_bucket(row["Status"]) == "pass")
    warn_count = sum(1 for row in all_rows if _status_bucket(row["Status"]) == "warn")
    fail_count = sum(1 for row in all_rows if _status_bucket(row["Status"]) == "fail")
    overall = "Fail" if fail_count else "Warn" if warn_count else "Pass"
    _rows_table(
        [
            {"Check": "Pass checks", "Status": str(pass_count), "Details": "Checks currently passing."},
            {"Check": "Warn checks", "Status": str(warn_count), "Details": "Checks that need optional follow-up."},
            {"Check": "Fail checks", "Status": str(fail_count), "Details": "Checks requiring action before release confidence."},
            {"Check": "Overall", "Status": overall, "Details": "Aggregated diagnostics posture."},
        ]
    )

with tool_result_panel("health_diagnostics_remediation_hints"):
    render_section_heading("Remediation hints", "Suggested next steps for Warn/Fail checks.", eyebrow="Actions")
    hints = {
        "Azure OpenAI (optional)": "Configure Azure settings only if AI summaries are required for this deployment.",
        "Configured GitHub repo": "Set a valid GitHub repository URL override or keep the default repository link.",
        "Roadmap seed parse": "Validate data/roadmap_seed.json structure and restore valid JSON content.",
        "GitHub URL parsing": "Use a valid GitHub repository URL in owner/repo form.",
        "AI adapter path available": "Optional path; configure Azure values to enable AI summaries.",
    }
    flagged = [row for row in all_rows if _status_bucket(row["Status"]) in {"warn", "fail"}]
    if flagged:
        _rows_table(
            [
                {
                    "Check": row["Check"],
                    "Status": row["Status"],
                    "Details": hints.get(row["Check"], "Review this check and align configuration or adapter behavior."),
                }
                for row in flagged
            ]
        )
    else:
        st.caption("No remediation items. All checks are passing.")

mark_page_baseline(_baseline, "content-rendered")
render_page_baseline(_baseline)
