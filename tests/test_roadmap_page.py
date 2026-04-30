from __future__ import annotations

from streamlit.testing.v1 import AppTest

from utils import roadmap


ROADMAP_PAGE = "pages/10_Roadmap_Feedback.py"
ROADMAP_PAGE_TIMEOUT = 60


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "info", "error", "caption"):
        collection = getattr(app, collection_name, [])
        for item in collection:
            parts.append(str(getattr(item, "body", getattr(item, "value", ""))))
    return "\n".join(parts)


def test_roadmap_feedback_page_renders_hybrid_board_and_links(monkeypatch):
    def fake_board(repo_url=None):
        return roadmap.RoadmapBoard(
            (
                roadmap.RoadmapItem(
                    title="Seed export idea",
                    category="Reports",
                    status="Planned",
                    votes=5,
                    description="A seeded report idea.",
                    rationale="Curated by maintainers.",
                    source="seed",
                ),
                roadmap.RoadmapItem(
                    title="GitHub request",
                    category="Tools",
                    status="In Progress",
                    votes=2,
                    description="A public GitHub issue.",
                    rationale="Requested by a user.",
                    source="github",
                    url="https://github.com/NPFernando/ITOps-Toolkit/issues/42",
                    number=42,
                ),
                roadmap.RoadmapItem(
                    title="AI checklist idea",
                    category="AI Ideas",
                    status="AI Recommended",
                    votes=9,
                    description="A curated AI idea.",
                    rationale="Static recommendation.",
                    source="seed",
                ),
            )
        )

    monkeypatch.setattr(roadmap, "load_roadmap_board", fake_board)

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()

    assert not app.exception
    text = _page_text(app)

    assert "Roadmap & Feedback" in text
    assert "Submit idea" in text
    assert "Public-safe feedback only" in text
    assert "AI Recommended is curated" in text
    assert "does not call Azure/OpenAI" in text
    assert "Streamlit does not store feedback" in text
    assert "Tools" in text
    assert "Reports" in text
    assert "Complete" in text
    assert "Planned" in text
    assert "In Progress" in text
    assert "AI Recommended" in text
    assert "GitHub #42" in text
    assert "https://github.com/NPFernando/ITOps-Toolkit/issues/new" in text


def test_roadmap_feedback_page_renders_github_fallback_note(monkeypatch):
    def fake_board(repo_url=None):
        return roadmap.RoadmapBoard(
            roadmap.ROADMAP_ITEMS,
            "GitHub API rate limit reached. Showing seed roadmap data.",
        )

    monkeypatch.setattr(roadmap, "load_roadmap_board", fake_board)

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()

    assert not app.exception
    text = _page_text(app)
    assert "GitHub unavailable, showing seed data" in text
    assert "GitHub API rate limit reached" in text
