from __future__ import annotations

from pathlib import Path


def test_readme_release_and_azure_docs_links_exist():
    readme = Path("README.md").read_text(encoding="utf-8")
    required_docs = [
        "docs/azure-ai-setup.md",
        "docs/release-checklist.md",
        "docs/release-notes-template.md",
        "docs/screenshot-guide.md",
    ]

    for doc_path in required_docs:
        assert f"]({doc_path})" in readme
        assert Path(doc_path).is_file()
