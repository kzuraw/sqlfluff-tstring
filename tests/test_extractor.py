import ast

from sqlfluff_tstring.extractor import extract_sql, restore_interpolations


def _get_tstring(source: str) -> ast.TemplateStr:
    tree = ast.parse(source)
    # Walk to find the TemplateStr node
    for node in ast.walk(tree):
        if isinstance(node, ast.TemplateStr):
            return node
    raise ValueError("No TemplateStr found")


class TestExtractSql:
    def test_plain_sql(self):
        tstr = _get_tstring('t"SELECT * FROM users"')
        sql, mappings = extract_sql(tstr)
        assert sql == "SELECT * FROM users"
        assert mappings == []

    def test_single_interpolation(self):
        tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
        sql, mappings = extract_sql(tstr)
        assert sql == "SELECT * FROM users WHERE id = :SQLFLUFF_VAR_0"
        assert len(mappings) == 1
        assert mappings[0].placeholder == ":SQLFLUFF_VAR_0"
        assert mappings[0].original_expr == "uid"

    def test_multiple_interpolations(self):
        tstr = _get_tstring('t"SELECT * FROM {table} WHERE id = {uid}"')
        sql, mappings = extract_sql(tstr)
        assert sql == "SELECT * FROM :SQLFLUFF_VAR_0 WHERE id = :SQLFLUFF_VAR_1"
        assert len(mappings) == 2
        assert mappings[0].original_expr == "table"
        assert mappings[1].original_expr == "uid"

    def test_conversion(self):
        tstr = _get_tstring('t"SELECT {val!r}"')
        sql, mappings = extract_sql(tstr)
        assert mappings[0].conversion == ord("r")

    def test_format_spec(self):
        tstr = _get_tstring('t"SELECT {val:.2f}"')
        sql, mappings = extract_sql(tstr)
        assert mappings[0].format_spec == ".2f"


class TestRestoreInterpolations:
    def test_simple_restore(self):
        tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
        sql, mappings = extract_sql(tstr)
        restored = restore_interpolations(sql, mappings)
        assert restored == "SELECT * FROM users WHERE id = {uid}"

    def test_restore_with_conversion(self):
        tstr = _get_tstring('t"SELECT {val!r}"')
        sql, mappings = extract_sql(tstr)
        restored = restore_interpolations(sql, mappings)
        assert restored == "SELECT {val!r}"

    def test_restore_with_format_spec(self):
        tstr = _get_tstring('t"SELECT {val:.2f}"')
        sql, mappings = extract_sql(tstr)
        restored = restore_interpolations(sql, mappings)
        assert restored == "SELECT {val:.2f}"

    def test_restore_with_both(self):
        tstr = _get_tstring('t"SELECT {val!r:.2f}"')
        sql, mappings = extract_sql(tstr)
        restored = restore_interpolations(sql, mappings)
        assert restored == "SELECT {val!r:.2f}"

    def test_restore_limit_offset(self):
        tstr = _get_tstring(
            't"SELECT * FROM users LIMIT {limit} OFFSET {offset}"'
        )
        sql, mappings = extract_sql(tstr)
        assert sql == "SELECT * FROM users LIMIT :SQLFLUFF_VAR_0 OFFSET :SQLFLUFF_VAR_1"
        restored = restore_interpolations(sql, mappings)
        assert restored == "SELECT * FROM users LIMIT {limit} OFFSET {offset}"

    def test_restore_preserves_formatting(self):
        tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
        sql, mappings = extract_sql(tstr)
        # Simulate sqlfluff adding newlines
        formatted = "SELECT *\nFROM users\nWHERE id = :SQLFLUFF_VAR_0"
        restored = restore_interpolations(formatted, mappings)
        assert restored == "SELECT *\nFROM users\nWHERE id = {uid}"
