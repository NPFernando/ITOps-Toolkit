from utils.sql_formatter import MAX_INPUT_LENGTH, format_sql


def test_format_sql_rejects_empty_input():
    result = format_sql("")

    assert result["ok"] is False
    assert "Enter a SQL query" in result["error"]


def test_format_sql_rejects_oversized_input():
    result = format_sql("x" * (MAX_INPUT_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_format_sql_rejects_unknown_keyword_case():
    result = format_sql("select 1", keyword_case="madeup")

    assert result["ok"] is False
    assert "Unknown keyword case" in result["error"]


def test_format_sql_rejects_invalid_indent_width():
    assert format_sql("select 1", indent_width=0)["ok"] is False
    assert format_sql("select 1", indent_width=9)["ok"] is False


def test_format_sql_reindents_and_uppercases_keywords():
    result = format_sql("select id, name from users where active=1", keyword_case="upper")

    assert result["ok"] is True
    assert "SELECT id,\n" in result["formatted"]
    assert "FROM users" in result["formatted"]
    assert "WHERE active=1" in result["formatted"]


def test_format_sql_lowercase_keyword_case():
    result = format_sql("SELECT id FROM users", keyword_case="lower")

    assert "select id" in result["formatted"]
    assert "from users" in result["formatted"]


def test_format_sql_respects_indent_width():
    nested_sql = "select id from (select id, name from users where active=1) as sub"
    result_narrow = format_sql(nested_sql, indent_width=1)
    result_wide = format_sql(nested_sql, indent_width=4)

    assert result_narrow["formatted"] != result_wide["formatted"]


def test_format_sql_never_errors_on_non_sql_text():
    """sqlparse is a lenient formatter, not a validator -- it accepts any text
    without raising, though it still uppercases recognized keywords (e.g. NOT)
    even in an otherwise plain sentence."""
    result = format_sql("just some plain words with no sql in them")

    assert result["ok"] is True
    assert "plain words" in result["formatted"]
