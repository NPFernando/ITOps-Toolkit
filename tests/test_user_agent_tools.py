from utils import user_agent_tools


def test_parse_user_agent_chrome_on_windows():
    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    result = user_agent_tools.parse_user_agent(ua)

    assert result["ok"] is True
    assert result["browser"] == "Chrome"
    assert result["browser_version"] == "128.0.0.0"
    assert result["os"] == "Windows"
    assert result["os_version"] == "10/11"
    assert result["device_type"] == "Desktop"
    assert result["is_bot"] is False


def test_parse_user_agent_edge_not_misdetected_as_chrome():
    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
    )
    result = user_agent_tools.parse_user_agent(ua)

    assert result["browser"] == "Edge"


def test_parse_user_agent_mobile_safari_on_ios():
    ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    )
    result = user_agent_tools.parse_user_agent(ua)

    assert result["browser"] == "Safari"
    assert result["os"] == "iOS"
    assert result["os_version"] == "17.4"
    assert result["device_type"] == "Mobile"


def test_parse_user_agent_android_chrome_is_mobile():
    ua = (
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
    )
    result = user_agent_tools.parse_user_agent(ua)

    assert result["os"] == "Android"
    assert result["os_version"] == "14"
    assert result["device_type"] == "Mobile"


def test_parse_user_agent_detects_common_bots():
    assert user_agent_tools.parse_user_agent("curl/8.4.0")["bot_name"] == "curl"
    assert user_agent_tools.parse_user_agent("python-requests/2.31.0")["bot_name"] == "python-requests"
    assert user_agent_tools.parse_user_agent(
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    )["bot_name"] == "Googlebot"


def test_parse_user_agent_bot_sets_device_type_bot():
    result = user_agent_tools.parse_user_agent("curl/8.4.0")

    assert result["is_bot"] is True
    assert result["device_type"] == "Bot"


def test_parse_user_agent_requires_input():
    result = user_agent_tools.parse_user_agent("")

    assert result["ok"] is False
    assert "Enter a User-Agent" in result["error"]


def test_parse_user_agent_rejects_oversized_input():
    oversized = "a" * (user_agent_tools.MAX_INPUT_LENGTH + 1)

    result = user_agent_tools.parse_user_agent(oversized)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_parse_user_agent_unrecognized_string_still_returns_ok():
    result = user_agent_tools.parse_user_agent("SomeCustomClient/1.0")

    assert result["ok"] is True
    assert result["browser"] is None
    assert result["os"] is None
    assert result["is_bot"] is False
