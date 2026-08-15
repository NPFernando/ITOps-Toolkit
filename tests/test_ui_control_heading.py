from utils import ui


def test_render_control_heading_renders_shared_tool_panel_eyebrow(monkeypatch):
    captured: dict[str, object] = {}

    def fake_markdown(value: str, unsafe_allow_html: bool = False) -> None:
        captured["value"] = value
        captured["unsafe_allow_html"] = unsafe_allow_html

    monkeypatch.setattr(ui.st, "markdown", fake_markdown)

    ui.render_control_heading("Keyword search")

    assert captured["unsafe_allow_html"] is True
    assert 'class="tool-panel-eyebrow"' in str(captured["value"])
    assert "Keyword search" in str(captured["value"])
