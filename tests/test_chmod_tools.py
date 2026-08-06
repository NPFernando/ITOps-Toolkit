from utils.chmod_tools import octal_to_symbolic, symbolic_to_octal


def test_octal_to_symbolic_basic():
    result = octal_to_symbolic("755")

    assert result["ok"] is True
    assert result["symbolic"] == "rwxr-xr-x"
    assert result["setuid"] is False


def test_octal_to_symbolic_handles_leading_zero():
    result = octal_to_symbolic("0644")

    assert result["ok"] is True
    assert result["symbolic"] == "rw-r--r--"


def test_octal_to_symbolic_setuid_with_exec_shows_lowercase_s():
    result = octal_to_symbolic("4755")

    assert result["symbolic"] == "rwsr-xr-x"
    assert result["setuid"] is True


def test_octal_to_symbolic_setuid_without_exec_shows_uppercase_s():
    result = octal_to_symbolic("4644")

    assert result["symbolic"] == "rwSr--r--"
    assert result["setuid"] is True


def test_octal_to_symbolic_sticky_without_exec_shows_uppercase_t():
    result = octal_to_symbolic("1644")

    assert result["symbolic"] == "rw-r--r-T"
    assert result["sticky"] is True


def test_octal_to_symbolic_combined_special_bits():
    result = octal_to_symbolic("6755")

    assert result["symbolic"] == "rwsr-sr-x"
    assert result["setuid"] is True
    assert result["setgid"] is True


def test_octal_to_symbolic_rejects_invalid_input():
    assert octal_to_symbolic("")["ok"] is False
    assert octal_to_symbolic("999")["ok"] is False
    assert octal_to_symbolic("75")["ok"] is False
    assert octal_to_symbolic("abc")["ok"] is False


def test_symbolic_to_octal_basic():
    result = symbolic_to_octal("rwxr-xr-x")

    assert result["ok"] is True
    assert result["octal"] == "755"


def test_symbolic_to_octal_ignores_leading_file_type_char():
    result = symbolic_to_octal("-rwxr-xr-x")

    assert result["ok"] is True
    assert result["octal"] == "755"

    result_dir = symbolic_to_octal("drwxr-xr-x")
    assert result_dir["ok"] is True
    assert result_dir["octal"] == "755"


def test_symbolic_to_octal_setuid_lowercase_s():
    result = symbolic_to_octal("rwsr-xr-x")

    assert result["octal"] == "4755"
    assert result["setuid"] is True


def test_symbolic_to_octal_setuid_uppercase_s_without_exec():
    result = symbolic_to_octal("rwSr--r--")

    assert result["octal"] == "4644"
    assert result["setuid"] is True


def test_symbolic_to_octal_sticky_uppercase_t():
    result = symbolic_to_octal("rw-r--r-T")

    assert result["octal"] == "1644"
    assert result["sticky"] is True


def test_symbolic_to_octal_rejects_invalid_input():
    assert symbolic_to_octal("")["ok"] is False
    assert symbolic_to_octal("rwxrwx")["ok"] is False
    assert symbolic_to_octal("not-permissions")["ok"] is False


def test_round_trip_octal_to_symbolic_to_octal():
    for octal in ("755", "644", "4755", "2755", "1755", "6755"):
        symbolic = octal_to_symbolic(octal)["symbolic"]
        back = symbolic_to_octal(symbolic)["octal"]
        assert back == octal
