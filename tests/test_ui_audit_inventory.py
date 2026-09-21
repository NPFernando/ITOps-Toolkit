from __future__ import annotations

import json
from pathlib import Path

def load_inventory() -> dict:
    path = Path(__file__).resolve().parents[1] / "docs" / "ui-ux-audit-inventory.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_ui_inventory_covers_the_committed_page_set():
    inventory = load_inventory()
    page_dir = Path(__file__).resolve().parents[1] / "pages"
    source_paths = {
        path.relative_to(page_dir.parent).as_posix()
        for path in page_dir.glob("*.py")
    }

    assert {page["path"] for page in inventory["pages"]} == source_paths
    assert inventory["page_count"] == len(source_paths)
    assert inventory["summary"]["pages_with_parse_errors"] == 0
    assert len({page["path"] for page in inventory["pages"]}) == inventory["page_count"]


def test_ui_inventory_exposes_shared_pattern_and_notice_gaps():
    inventory = load_inventory()
    summary = inventory["summary"]

    assert summary["pattern_counts"]["shared_shell"] == inventory["page_count"]
    assert summary["pattern_counts"]["page_header"] > 0
    assert summary["direct_notice_counts"].get("error", 0) == 0
    assert summary["direct_notice_counts"]["warning"] > 0
