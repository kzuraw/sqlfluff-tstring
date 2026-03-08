import ast

import pytest

from sqlfluff_tstring.extractor import extract_sql, restore_interpolations


def _get_tstring(source: str) -> ast.TemplateStr:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.TemplateStr):
            return node
    raise ValueError("No TemplateStr found")


def test_extract_plain_sql(snapshot):
    """Extract SQL with no interpolations — returns raw text and empty mappings."""
    tstr = _get_tstring('t"SELECT * FROM users"')
    sql, mappings = extract_sql(tstr)
    assert sql == snapshot
    assert mappings == []


def test_extract_single_interpolation(snapshot):
    """Single interpolation replaced with {_var0} placeholder."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    assert sql == snapshot
    assert len(mappings) == 1
    assert mappings[0].placeholder == "{_var0}"
    assert mappings[0].original_expr == "uid"


def test_extract_multiple_interpolations(snapshot):
    """Multiple interpolations get sequential placeholder indices."""
    tstr = _get_tstring('t"SELECT * FROM {table} WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    assert sql == snapshot
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


def test_restore_simple(snapshot):
    """Restore replaces placeholders back with original interpolation expressions."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == snapshot


def test_restore_with_conversion(snapshot):
    """Restore preserves !r conversion syntax."""
    tstr = _get_tstring('t"SELECT {val!r}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == snapshot


def test_restore_with_format_spec(snapshot):
    """Restore preserves :.2f format spec syntax."""
    tstr = _get_tstring('t"SELECT {val:.2f}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == snapshot


def test_restore_with_conversion_and_format_spec(snapshot):
    """Restore preserves both conversion and format spec together."""
    tstr = _get_tstring('t"SELECT {val!r:.2f}"')
    sql, mappings = extract_sql(tstr)
    restored = restore_interpolations(sql, mappings)
    assert restored == snapshot


def test_restore_limit_offset(snapshot):
    """LIMIT/OFFSET placeholders are extracted and restored correctly."""
    tstr = _get_tstring(
        't"SELECT * FROM users LIMIT {limit} OFFSET {offset}"'
    )
    sql, mappings = extract_sql(tstr)
    assert sql == snapshot
    restored = restore_interpolations(sql, mappings)
    assert restored == snapshot


def test_restore_preserves_formatting(snapshot):
    """Restore works on sqlfluff-reformatted SQL (added newlines)."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    sql, mappings = extract_sql(tstr)
    formatted = "SELECT *\nFROM users\nWHERE id = {_var0}"
    restored = restore_interpolations(formatted, mappings)
    assert restored == snapshot


def test_restore_raises_on_missing_placeholder():
    """ValueError raised when a placeholder is missing from formatted SQL."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    _, mappings = extract_sql(tstr)
    with pytest.raises(ValueError, match="not found in formatted SQL"):
        restore_interpolations("SELECT * FROM users", mappings)


def test_restore_raises_on_duplicate_placeholder():
    """ValueError raised when a placeholder appears more than once."""
    tstr = _get_tstring('t"SELECT * FROM users WHERE id = {uid}"')
    _, mappings = extract_sql(tstr)
    with pytest.raises(ValueError, match="appears 2 times"):
        restore_interpolations("SELECT {_var0} FROM users WHERE id = {_var0}", mappings)
