from __future__ import annotations

from utils.robots_meta_builder import build_robots_meta


def test_default_directives():
    result = build_robots_meta()

    assert result["ok"] is True
    assert result["output"] == '<meta name="robots" content="index, follow">'


def test_noindex_nofollow():
    result = build_robots_meta("noindex", "nofollow")

    assert result["ok"] is True
    assert "noindex" in result["output"]
    assert "nofollow" in result["output"]


def test_optional_flags_included():
    result = build_robots_meta(noarchive=True, nosnippet=True, noimageindex=True)

    assert "noarchive" in result["output"]
    assert "nosnippet" in result["output"]
    assert "noimageindex" in result["output"]


def test_numeric_directives():
    result = build_robots_meta(max_snippet=-1, max_video_preview=0)

    assert "max-snippet:-1" in result["output"]
    assert "max-video-preview:0" in result["output"]


def test_max_image_preview():
    result = build_robots_meta(max_image_preview="large")

    assert "max-image-preview:large" in result["output"]


def test_rejects_unknown_indexing_value():
    result = build_robots_meta(indexing="bogus")

    assert result["ok"] is False
    assert "Unknown indexing" in result["error"]


def test_rejects_unknown_max_image_preview_value():
    result = build_robots_meta(max_image_preview="huge")

    assert result["ok"] is False
    assert "Unknown max-image-preview" in result["error"]
