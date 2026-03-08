import ast

from sqlfluff_tstring.extractor import extract_sql, restore_interpolations


def _get_tstring(source: str) -> ast.TemplateStr:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.TemplateStr):
            return node
    raise ValueError("No TemplateStr found")


def test_extract_plain_sql():
    """Extract SQL with no interpolations — returns raw text and empty mappings."""
    tstr = _get_tstring('t"SELECT * FROM users"')
    sql, mappings = extract_sql(tstr)
    assert sql == "SELECT * FROM users"
    assert mappings == []


def test_extract_single_interpolation():
    """Single interpolation replaced with :SQLFLUFF_VAR_0 placeholder."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    assert sql == "SELECT * FROM users WHERE id = :SQLFLUFF_VAR_0"
    assert len(mappings) == 1
    assert mappings[0].placeholder == ":SQLFLUFF_VAR_0"
    assert mappings[0].original_expr == "uid"


def test_extract_multiple_interpolations():
    """Multiple interpolations get sequential placeholder indices."""
    tstr = _get_tstring('t"SELECT * FROM {table} WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    assert sql == "SELECT * FROM :SQLFLUFF_VAR_0 WHERE id = :SQLFLUFF_VAR_1"
    assert len(mappings) == 2
    assert mappings[0].original_expr == "table"
    assert mappings[1].original_expr == "uid"


def test_extract_conversion():
    """Interpolation with !r conversion is preserved in mapping."""
    tstr = _get_tstring('t"SELECT {val!r}"')
    sql, mappings = extract_sql(tstr)
    assert mappings[0].conversion == ord("r")


def test_extract_format_spec():
    """Interpolation with format spec is preserved in mapping."""
    tstr = _get_tstring('t"SELECT {val:.2f}"')
    sql, mappings = extract_sql(tstr)
    assert mappings[0].format_spec == ".2f"


def test_restore_simple():
    """Restore replaces placeholders back with original interpolation expressions."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == "SELECT * FROM users WHERE id = {uid}"


def test_restore_with_conversion():
    """Restore preserves !r conversion syntax."""
    tstr = _get_tstring('t"SELECT {val!r}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == "SELECT {val!r}"


def test_restore_with_format_spec():
    """Restore preserves :.2f format spec syntax."""
    tstr = _get_tstring('t"SELECT {val:.2f}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == "SELECT {val:.2f}"


def test_restore_with_conversion_and_format_spec():
    """Restore preserves both conversion and format spec together."""
    tstr = _get_tstring('t"SELECT {val!r:.2f}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == "SELECT {val!r:.2f}"


def test_restore_limit_offset():
    """LIMIT/OFFSET placeholders are extracted and restored correctly."""
    tstr = _get_tstring(
        't"SELECT * FROM users LIMIT {limit} OFFSET {offset}"'
    )
    sql, mappings = extract_sql(tstr)
    assert sql == "SELECT * FROM users LIMIT :SQLFLUFF_VAR_0 OFFSET :SQLFLUFF_VAR_1"
    restored = restore_interpolations(sql, mappings)
    assert restored == "SELECT * FROM users LIMIT {limit} OFFSET {offset}"


def test_restore_preserves_formatting():
    """Restore works on sqlfluff-reformatted SQL (added newlines)."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    formatted = "SELECT *\nFROM users\nWHERE id = :SQLFLUFF_VAR_0"
    restored = restore_interpolations(formatted, mappings)
    assert restored == "SELECT *\nFROM users\nWHERE id = {uid}"
