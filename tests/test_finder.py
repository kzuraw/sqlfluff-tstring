from sqlfluff_tstring.finder import find_sql_tstrings


def test_simple_sql_call():
    """Detect a plain sql(t"...") call."""
    source = 'sql(t"SELECT * FROM users")'
    matches = find_sql_tstrings(source)
    assert len(matches) == 1


def test_sql_call_with_interpolation():
    """Detect sql(t"...") containing an interpolation expression."""
    source = 'sql(t"SELECT * FROM users WHERE id = {uid}")'
    matches = find_sql_tstrings(source)
    assert len(matches) == 1


def test_attribute_sql_call():
    """Detect attribute-style calls like db.sql(t"...")."""
    source = 'db.sql(t"SELECT 1")'
    matches = find_sql_tstrings(source)
    assert len(matches) == 1


def test_no_match_regular_string():
    """Ignore sql() calls with regular strings instead of t-strings."""
    source = 'sql("SELECT 1")'
    matches = find_sql_tstrings(source)
    assert len(matches) == 0


def test_no_match_no_sql_call():
    """Ignore t-strings not wrapped in a sql() call."""
    source = 'foo(t"SELECT 1")'
    matches = find_sql_tstrings(source)
    assert len(matches) == 0


def test_multiple_matches():
    """Find all sql(t"...") calls when multiple exist in source."""
    source = """\
sql(t"SELECT 1")
sql(t"SELECT 2")
"""
    matches = find_sql_tstrings(source)
    assert len(matches) == 2


def test_triple_quoted():
    """Detect triple-quoted t-strings."""
    source = 'sql(t"""SELECT * FROM users""")'
    matches = find_sql_tstrings(source)
    assert len(matches) == 1


def test_empty_tstring():
    """Detect sql() with an empty t-string."""
    source = 'sql(t"")'
    matches = find_sql_tstrings(source)
    assert len(matches) == 1


def test_nested_in_function():
    """Detect sql(t"...") nested inside a function body."""
    source = """\
def query():
    return sql(t"SELECT * FROM users WHERE id = {uid}")
"""
    matches = find_sql_tstrings(source)
    assert len(matches) == 1
