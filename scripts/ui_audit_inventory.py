#!/usr/bin/env python3
"""Build a static UI/UX inventory for every Streamlit page.

The inventory intentionally uses Python's AST and lightweight source markers.
It does not import pages or execute external adapters, so it remains safe and
deterministic in CI.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
DEFAULT_OUTPUT = ROOT / "docs" / "ui-ux-audit-inventory.json"

CALL_MARKERS = {
    "shared_shell": "apply_app_shell",
    "page_header": "render_page_header",
    "form_intro": "render_form_intro",
    "empty_state": "render_empty_state",
    "status_note": "render_status_note",
    "failure_note": "render_failure_note",
    "safe_note": "render_safe_note",
    "result_panel": "tool_result_panel",
    "download_panel": "tool_download_panel",
    "form": "st.form",
    "form_submit": "st.form_submit_button",
    "button": "st.button",
    "download_button": "st.download_button",
    "session_state": "st.session_state",
}

DIRECT_NOTICE_MARKERS = {
    "error": "st.error",
    "warning": "st.warning",
    "info": "st.info",
    "success": "st.success",
}

ACTION_WORDS = {
    "check": "check",
    "lookup": "lookup",
    "look": "lookup",
    "run": "run",
    "generate": "generate",
    "build": "build",
    "convert": "convert",
    "format": "format",
    "validate": "validate",
    "scan": "scan",
    "decode": "decode",
    "encode": "encode",
    "calculate": "calculate",
    "compare": "compare",
    "search": "search",
    "submit": "submit",
    "process": "process",
}


def _call_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            names.append(function.id)
        elif isinstance(function, ast.Attribute):
            parent = function.value
            if isinstance(parent, ast.Name):
                names.append(f"{parent.id}.{function.attr}")
    return names


def _string_values(node: ast.AST) -> list[str]:
    values: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            values.append(child.value.strip())
    return values


def _action_labels(tree: ast.AST) -> list[str]:
    labels: list[str] = []
    target_functions = {"button", "form_submit_button", "download_button"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in target_functions or not node.args:
            continue
        label = node.args[0]
        if isinstance(label, ast.Constant) and isinstance(label.value, str):
            labels.append(label.value.strip())
    return labels


def _action_intents(labels: list[str]) -> list[str]:
    intents: set[str] = set()
    for label in labels:
        words = re.findall(r"[a-z]+", label.lower())
        for word in words:
            if word in ACTION_WORDS:
                intents.add(ACTION_WORDS[word])
    return sorted(intents)


def inspect_page(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
        parse_error = None
    except SyntaxError as exc:
        tree = ast.Module(body=[], type_ignores=[])
        parse_error = f"{exc.msg} (line {exc.lineno})"

    calls = set(_call_names(tree))
    action_labels = _action_labels(tree)
    direct_notices = [
        notice for notice, marker in DIRECT_NOTICE_MARKERS.items() if marker in calls
    ]
    custom_css = "<style" in source or "unsafe_allow_html=True" in source
    has_media_query = "@media" in source
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "page_id": path.stem,
        "parse_error": parse_error,
        "lines": len(source.splitlines()),
        "shared_patterns": {
            key: marker in calls for key, marker in CALL_MARKERS.items()
        },
        "direct_notices": direct_notices,
        "action_labels": action_labels,
        "action_intents": _action_intents(action_labels),
        "custom_css_or_html": custom_css,
        "page_media_queries": has_media_query,
        "source_strings": {
            "placeholder_count": source.count("placeholder="),
            "help_count": source.count("help="),
        },
    }


def build_inventory() -> dict[str, Any]:
    pages = [inspect_page(path) for path in sorted(PAGES.glob("*.py"))]
    pattern_counts = Counter(
        key
        for page in pages
        for key, present in page["shared_patterns"].items()
        if present
    )
    direct_notice_counts = Counter(
        notice for page in pages for notice in page["direct_notices"]
    )
    return {
        "schema_version": 1,
        "generated_from": "pages/*.py",
        "page_count": len(pages),
        "summary": {
            "pattern_counts": dict(sorted(pattern_counts.items())),
            "direct_notice_counts": dict(sorted(direct_notice_counts.items())),
            "pages_with_custom_css_or_html": sum(
                page["custom_css_or_html"] for page in pages
            ),
            "pages_with_parse_errors": sum(bool(page["parse_error"]) for page in pages),
        },
        "pages": pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the JSON inventory (default: docs/ui-ux-audit-inventory.json)",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    inventory = build_inventory()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Audited {inventory['page_count']} pages; "
        f"wrote {output.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
