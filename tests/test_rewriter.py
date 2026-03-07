import ast

from sqlfluff_tstring.rewriter import Replacement, apply_replacements


def _get_tstring(source: str) -> ast.TemplateStr:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.TemplateStr):
            return node
    raise ValueError("No TemplateStr found")


class TestApplyReplacements:
    def test_single_replacement(self):
        source = 'sql(t"select * from users")'
        tstr = _get_tstring(source)
        replacements = [Replacement(tstr, "SELECT * FROM users")]
        result = apply_replacements(source, replacements)
        assert result == 'sql(t"SELECT * FROM users")'

    def test_triple_quoted(self):
        source = 'sql(t"""select * from users""")'
        tstr = _get_tstring(source)
        replacements = [Replacement(tstr, "SELECT *\nFROM users")]
        result = apply_replacements(source, replacements)
        assert result == 'sql(t"""\nSELECT *\nFROM users\n""")'

    def test_single_quoted(self):
        source = "sql(t'select * from users')"
        tstr = _get_tstring(source)
        replacements = [Replacement(tstr, "SELECT * FROM users")]
        result = apply_replacements(source, replacements)
        assert result == "sql(t'SELECT * FROM users')"

    def test_multiple_replacements(self):
        source = 'x = sql(t"select 1")\ny = sql(t"select 2")'
        tree = ast.parse(source)
        tstrings = [n for n in ast.walk(tree) if isinstance(n, ast.TemplateStr)]
        replacements = [
            Replacement(tstrings[0], "SELECT 1"),
            Replacement(tstrings[1], "SELECT 2"),
        ]
        result = apply_replacements(source, replacements)
        assert result == 'x = sql(t"SELECT 1")\ny = sql(t"SELECT 2")'

    def test_preserves_surrounding_code(self):
        source = 'x = 1\nsql(t"select 1")\ny = 2'
        tstr = _get_tstring(source)
        replacements = [Replacement(tstr, "SELECT 1")]
        result = apply_replacements(source, replacements)
        assert result == 'x = 1\nsql(t"SELECT 1")\ny = 2'

    def test_upgrades_to_triple_quotes_on_newline(self):
        source = 'sql(t"select * from users")'
        tstr = _get_tstring(source)
        replacements = [Replacement(tstr, "SELECT *\nFROM users")]
        result = apply_replacements(source, replacements)
        assert result == 'sql(t"""\nSELECT *\nFROM users\n""")'

    def test_triple_quoted_single_line_no_wrapping(self):
        source = 'sql(t"""select 1""")'
        tstr = _get_tstring(source)
        replacements = [Replacement(tstr, "SELECT 1")]
        result = apply_replacements(source, replacements)
        assert result == 'sql(t"""SELECT 1""")'
