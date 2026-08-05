from utils import color_tools


def test_parse_color_from_hex():
    result = color_tools.parse_color("#126bff")

    assert result["ok"] is True
    assert result["hex"] == "#126bff"
    assert result["rgb"] == "rgb(18, 107, 255)"
    assert result["hsl"] == "hsl(217, 100%, 54%)"


def test_parse_color_hex_without_hash_and_shorthand():
    assert color_tools.parse_color("126bff")["ok"] is True
    shorthand = color_tools.parse_color("#fff")
    assert shorthand["hex"] == "#ffffff"


def test_parse_color_from_rgb():
    result = color_tools.parse_color("rgb(18, 107, 255)")

    assert result["ok"] is True
    assert result["hex"] == "#126bff"


def test_parse_color_from_hsl():
    # HSL is percentage-rounded input, so the recovered RGB is "close to"
    # the original blue accent (#126bff), not byte-exact.
    result = color_tools.parse_color("hsl(217, 100%, 54%)")

    assert result["ok"] is True
    assert result["r"] < 30
    assert 95 <= result["g"] <= 115
    assert result["b"] == 255


def test_parse_color_round_trips_hex_to_hsl_to_rgb():
    # HSL is percentage-rounded, so a round trip can be off by ~1 unit per
    # channel -- assert "close", not byte-exact.
    original = color_tools.parse_color("#ff6a13")
    via_hsl = color_tools.parse_color(original["hsl"])

    assert via_hsl["ok"] is True
    for channel in "rgb":
        assert abs(original[channel] - via_hsl[channel]) <= 2


def test_parse_color_rejects_out_of_range_rgb():
    result = color_tools.parse_color("rgb(999, 1, 1)")

    assert result["ok"] is False
    assert "between 0 and 255" in result["error"]


def test_parse_color_rejects_out_of_range_hsl():
    result = color_tools.parse_color("hsl(400, 10%, 10%)")

    assert result["ok"] is False
    assert "0-360" in result["error"]


def test_parse_color_rejects_unparsable_input():
    result = color_tools.parse_color("not-a-color")

    assert result["ok"] is False
    assert "Could not parse" in result["error"]


def test_parse_color_requires_input():
    result = color_tools.parse_color("")

    assert result["ok"] is False
    assert "Enter a color" in result["error"]
