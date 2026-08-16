"""WCAG AA contrast regression checks for the dark-theme tokens used as body text.

These caught a real accessibility bug: the dark-theme "muted" token measured
3.79:1 against its background (below the 4.5:1 AA minimum for normal text),
and the "NEW" badge's white-on-green text measured as low as 1.4:1.
"""

from utils.ui import _THEME_TOKENS


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _luminance(rgb: tuple[int, int, int]) -> float:
    def linearize(channel: int) -> float:
        c = channel / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    lum_a, lum_b = _luminance(_hex_to_rgb(hex_a)), _luminance(_hex_to_rgb(hex_b))
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


def test_dark_theme_muted_text_meets_aa_against_bg_and_panel():
    muted = _THEME_TOKENS["dark"]["muted"]
    assert contrast_ratio(muted, _THEME_TOKENS["dark"]["bg"]) >= 4.5
    assert contrast_ratio(muted, _THEME_TOKENS["dark"]["panel"]) >= 4.5


def test_light_theme_muted_text_meets_aa_against_bg():
    muted = _THEME_TOKENS["light"]["muted"]
    assert contrast_ratio(muted, _THEME_TOKENS["light"]["bg"]) >= 4.5


def test_dark_theme_muted_text_meets_aa_against_surface_strong():
    # Roadmap page text (vote pill, item category/status/source badges, card
    # captions) was hardcoded to #667790/#64758e/#3d4f68 (2.98:1-1.68:1
    # against the dark bg) and was switched to the shared "muted" token --
    # confirm it clears AA against the roadmap's surface-strong background too.
    muted = _THEME_TOKENS["dark"]["muted"]
    assert contrast_ratio(muted, _THEME_TOKENS["dark"]["surface-strong"]) >= 4.5


def test_dark_theme_blue_text_meets_aa_against_bg_and_panel():
    # #e06c75 measured 4.38:1 against "bg" -- just below WCAG AA's 4.5:1
    # minimum for normal text. This token backs several small/body-text spots
    # (.section-bolt, .feature-blue, .tool-panel-eyebrow, .roadmap-status-badge).
    blue = _THEME_TOKENS["dark"]["blue"]
    assert contrast_ratio(blue, _THEME_TOKENS["dark"]["bg"]) >= 4.5
    assert contrast_ratio(blue, _THEME_TOKENS["dark"]["panel"]) >= 4.5


def test_new_badge_text_meets_aa_against_green_gradient_stops():
    # The badge background is `linear-gradient(135deg, green, color-mix(green, #000 15%))`
    # -- check both stops, since darkening the green toward black is the worst case.
    badge_text = "#04140a"
    for mode in ("dark", "light"):
        green = _THEME_TOKENS[mode]["green"]
        r, g, b = _hex_to_rgb(green)
        darkened = f"#{round(r * 0.85):02x}{round(g * 0.85):02x}{round(b * 0.85):02x}"
        assert contrast_ratio(badge_text, green) >= 4.5
        assert contrast_ratio(badge_text, darkened) >= 4.5
