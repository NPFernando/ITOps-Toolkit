from utils.config_format_converter import MAX_INPUT_LENGTH, convert_config


def test_convert_config_rejects_empty_input():
    result = convert_config("", "JSON", "YAML")

    assert result["ok"] is False
    assert "Enter some config text" in result["error"]


def test_convert_config_rejects_oversized_input():
    result = convert_config("x" * (MAX_INPUT_LENGTH + 1), "JSON", "YAML")

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_convert_config_rejects_unknown_format():
    result = convert_config('{"a": 1}', "JSON", "INI")

    assert result["ok"] is False
    assert "Formats must be one of" in result["error"]


def test_convert_config_rejects_invalid_source():
    result = convert_config("not valid json {{{", "JSON", "YAML")

    assert result["ok"] is False
    assert "Could not parse input as JSON" in result["error"]


def test_convert_config_json_to_yaml():
    result = convert_config('{"name": "web01", "port": 8080}', "JSON", "YAML")

    assert result["ok"] is True
    assert "name: web01" in result["output"]
    assert "port: 8080" in result["output"]


def test_convert_config_yaml_to_json():
    result = convert_config("name: web01\nport: 8080\n", "YAML", "JSON")

    assert result["ok"] is True
    assert '"name": "web01"' in result["output"]
    assert '"port": 8080' in result["output"]


def test_convert_config_json_to_toml():
    result = convert_config('{"name": "web01", "port": 8080}', "JSON", "TOML")

    assert result["ok"] is True
    assert 'name = "web01"' in result["output"]
    assert "port = 8080" in result["output"]


def test_convert_config_toml_list_at_top_level_rejected():
    result = convert_config("[1, 2, 3]", "JSON", "TOML")

    assert result["ok"] is False
    assert "top-level object" in result["error"]


def test_convert_config_json_to_xml_round_trips_keys():
    result = convert_config('{"name": "web01", "tags": ["prod", "east"]}', "JSON", "XML")

    assert result["ok"] is True
    assert "<name>web01</name>" in result["output"]
    assert result["output"].count("<tags>") == 2


def test_convert_config_xml_to_json():
    xml_input = "<root><name>web01</name><port>8080</port></root>"
    result = convert_config(xml_input, "XML", "JSON")

    assert result["ok"] is True
    assert '"name": "web01"' in result["output"]


def test_convert_config_xml_round_trip_preserves_structure():
    original = '{"host": "example.com", "tags": ["a", "b"]}'
    to_xml = convert_config(original, "JSON", "XML")
    back_to_json = convert_config(to_xml["output"], "XML", "JSON")

    assert to_xml["ok"] is True
    assert back_to_json["ok"] is True
    assert '"host": "example.com"' in back_to_json["output"]
    assert '"a"' in back_to_json["output"] and '"b"' in back_to_json["output"]


def test_convert_config_rejects_invalid_xml():
    result = convert_config("<not><closed>", "XML", "JSON")

    assert result["ok"] is False
    assert "Could not parse input as XML" in result["error"]
