import ast

from sqlfluff_tstring.rewriter import Replacement, apply_replacements


def _get_tstring(source: str) -> ast.TemplateStr:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.TemplateStr):
            return node
    raise ValueError("No TemplateStr found")


def test_single_replacement(snapshot):
    """Replace SQL content inside a single t-string."""
    source = 'sql(t"select * from users")'
    tstr = _get_tstring(source)
    replacements = [Replacement(tstr, "SELECT * FROM users")]
    result = apply_replacements(source, replacements)
    assert result == snapshot


def test_triple_quoted(snapshot):
    """Multiline content stays inside triple-quoted t-strings with wrapping newlines."""
    source = 'sql(t"""select * from users""")'
    tstr = _get_tstring(source)
    replacements = [Replacement(tstr, "SELECT *\nFROM users")]
    result = apply_replacements(source, replacements)
    assert result == snapshot


def test_single_quoted(snapshot):
    """Single-quoted t-strings are rewritten correctly."""
    source = "sql(t'select * from users')"
    tstr = _get_tstring(source)
    replacements = [Replacement(tstr, "SELECT * FROM users")]
    result = apply_replacements(source, replacements)
    assert result == snapshot


def test_multiple_replacements(snapshot):
    """Apply replacements to multiple t-strings in the same source."""
    source = 'x = sql(t"select 1")\ny = sql(t"select 2")'
    tree = ast.parse(source)
    tstrings = [n for n in ast.walk(tree) if isinstance(n, ast.TemplateStr)]
    replacements = [
        Replacement(tstrings[0], "SELECT 1"),
        Replacement(tstrings[1], "SELECT 2"),
    ]
    result = apply_replacements(source, replacements)
    assert result == snapshot


def test_preserves_surrounding_code(snapshot):
    """Code before and after the t-string is left unchanged."""
    source = 'x = 1\nsql(t"select 1")\ny = 2'
    tstr = _get_tstring(source)
    replacements = [Replacement(tstr, "SELECT 1")]
    result = apply_replacements(source, replacements)
    assert result == snapshot


def test_upgrades_to_triple_quotes_on_newline(snapshot):
    """Single-quoted t-strings auto-upgrade to triple quotes when content becomes multiline."""
    source = 'sql(t"select * from users")'
    tstr = _get_tstring(source)
    replacements = [Replacement(tstr, "SELECT *\nFROM users")]
    result = apply_replacements(source, replacements)
    assert result == snapshot


def test_triple_quoted_single_line_no_wrapping(snapshot):
    """Triple-quoted t-strings with single-line content don't get wrapping newlines."""
    source = 'sql(t"""select 1""")'
    tstr = _get_tstring(source)
    replacements = [Replacement(tstr, "SELECT 1")]
    result = apply_replacements(source, replacements)
    assert result == snapshot
