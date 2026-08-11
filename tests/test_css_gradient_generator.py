from __future__ import annotations

from utils.css_gradient_generator import build_gradient


def test_linear_gradient_basic():
    result = build_gradient("#ff0000\n#0000ff", "linear", "90deg")

    assert result["ok"] is True
    assert result["output"] == "background: linear-gradient(90deg, #ff0000, #0000ff);"


def test_radial_gradient_with_positions():
    result = build_gradient("#ff0000, 0%\n#00ff00, 50%\n#0000ff, 100%", "radial", "circle at center")

    assert result["ok"] is True
    assert result["output"] == "background: radial-gradient(circle at center, #ff0000 0%, #00ff00 50%, #0000ff 100%);"


def test_short_hex_colors_accepted():
    result = build_gradient("#f00\n#00f", "linear", "90deg")

    assert result["ok"] is True


def test_rejects_invalid_color():
    result = build_gradient("notacolor\n#000000", "linear", "90deg")

    assert result["ok"] is False
    assert "hex color" in result["error"]


def test_rejects_fewer_than_two_stops():
    result = build_gradient("#fff", "linear", "90deg")

    assert result["ok"] is False
    assert "at least two" in result["error"]


def test_rejects_too_many_stops():
    stops = "\n".join(f"#{i:06x}" for i in range(11))
    result = build_gradient(stops, "linear", "90deg")

    assert result["ok"] is False
    assert "at most" in result["error"]


def test_rejects_unknown_gradient_type():
    result = build_gradient("#fff\n#000", "conic", "90deg")

    assert result["ok"] is False
    assert "Unknown gradient type" in result["error"]


def test_ignores_blank_lines():
    result = build_gradient("#ff0000\n\n#0000ff\n", "linear", "90deg")

    assert result["ok"] is True
