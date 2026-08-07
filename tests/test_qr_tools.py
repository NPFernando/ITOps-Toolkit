from utils.qr_tools import MAX_TEXT_LENGTH, build_wifi_payload, generate_qr_code


def test_generate_qr_code_rejects_empty_input():
    result = generate_qr_code("")

    assert result["ok"] is False
    assert "Enter some text" in result["error"]


def test_generate_qr_code_rejects_oversized_input():
    result = generate_qr_code("x" * (MAX_TEXT_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_generate_qr_code_produces_png_bytes():
    result = generate_qr_code("https://example.com")

    assert result["ok"] is True
    assert result["png_bytes"].startswith(b"\x89PNG")


def test_build_wifi_payload_basic():
    result = build_wifi_payload("MyNetwork", "hunter22", "WPA")

    assert result["ok"] is True
    assert result["payload"] == "WIFI:T:WPA;S:MyNetwork;P:hunter22;H:false;;"


def test_build_wifi_payload_escapes_special_characters():
    result = build_wifi_payload("a;b", 'p"w:d', "WPA")

    assert result["ok"] is True
    assert result["payload"] == 'WIFI:T:WPA;S:a\\;b;P:p\\"w\\:d;H:false;;'


def test_build_wifi_payload_open_network_needs_no_password():
    result = build_wifi_payload("Guest", "", "nopass")

    assert result["ok"] is True
    assert "P:;" in result["payload"]


def test_build_wifi_payload_requires_ssid():
    result = build_wifi_payload("", "pw", "WPA")

    assert result["ok"] is False
    assert "network name" in result["error"]


def test_build_wifi_payload_requires_password_unless_open():
    result = build_wifi_payload("MyNetwork", "", "WPA")

    assert result["ok"] is False
    assert "Enter a password" in result["error"]


def test_build_wifi_payload_rejects_unknown_security_type():
    result = build_wifi_payload("MyNetwork", "pw", "WPA3")

    assert result["ok"] is False
    assert "Unknown security type" in result["error"]


def test_build_wifi_payload_hidden_flag():
    result = build_wifi_payload("MyNetwork", "hunter22", "WPA", hidden=True)

    assert "H:true;;" in result["payload"]
