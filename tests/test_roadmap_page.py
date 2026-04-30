from __future__ import annotations

from streamlit.testing.v1 import AppTest


ROADMAP_PAGE = "pages/10_Roadmap_Feedback.py"


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "info", "error", "caption"):
        collection = getattr(app, collection_name, [])
        for item in collection:
            parts.append(str(getattr(item, "body", getattr(item, "value", ""))))
    return "\n".join(parts)


def test_roadmap_feedback_page_renders_static_board_and_links():
    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=30)
    app.run()

    assert not app.exception
    text = _page_text(app)

    assert "Roadmap & Feedback" in text
    assert "Submit idea" in text
    assert "Public-safe feedback only" in text
    assert "AI Recommended is curated" in text
    assert "does not call Azure/OpenAI" in text
    assert "no ideas are stored by Streamlit" in text
    assert "Tools" in text
    assert "Security" in text
    assert "Implemented" in text
    assert "Planned" in text
    assert "In Progress" in text
    assert "AI Recommended" in text
    assert "https://github.com/NPFernando/ITOps-Toolkit/issues/new" in text
