from __future__ import annotations

import re
from pathlib import Path

from utils.ui import TOOLS


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = PROJECT_ROOT / "pages"
LINK_PATTERN = re.compile(r"!?\[.*?\]\(([^)]+)\)")


def _local_markdown_links(path: Path) -> list[str]:
    links: list[str] = []
    for match in LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
        value = match.strip()
        if not value or value.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append(value.split("#", 1)[0].split("?", 1)[0])
    return links


def test_tool_metadata_paths_match_existing_pages():
    tool_paths = {tool.path for tool in TOOLS}
    page_paths = {str(path.relative_to(PROJECT_ROOT)) for path in PAGES_DIR.glob("*.py")}

    # Roadmap is a standalone page, not part of the TOOLS metadata list.
    assert tool_paths <= page_paths
    assert page_paths - tool_paths == {"pages/10_Roadmap_Feedback.py"}


def test_docs_links_resolve_for_key_operational_docs():
    docs_to_check = (
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "assets" / "README.md",
        PROJECT_ROOT / "docs" / "assets" / "INDEX.md",
        PROJECT_ROOT / "docs" / "release-notes-template.md",
        PROJECT_ROOT / "docs" / "release-checklist.md",
        PROJECT_ROOT / "docs" / "ops-runbook.md",
    )

    missing: list[str] = []
    for doc in docs_to_check:
        for link in _local_markdown_links(doc):
            target = (doc.parent / link).resolve()
            if not target.exists():
                missing.append(f"{doc.relative_to(PROJECT_ROOT)} -> {link}")

    assert not missing, f"Broken local doc links:\n" + "\n".join(missing)


def test_asset_index_entries_exist_on_disk():
    index_path = PROJECT_ROOT / "docs" / "assets" / "INDEX.md"
    content = index_path.read_text(encoding="utf-8")
    referenced = re.findall(r"`((?:icons|posters|illustrations)/[^`]+)`", content)

    missing = []
    for rel in referenced:
        if not (PROJECT_ROOT / "docs" / "assets" / rel).exists():
            missing.append(rel)

    assert not missing, f"Missing assets referenced in index: {missing}"
