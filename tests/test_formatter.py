from sqlfluff_tstring.formatter import format_sql


def test_simple_format(snapshot):
    """Format a basic lowercase SQL statement."""
    sql = "select * from users"
    result = format_sql(sql)
    assert result == snapshot


def test_strips_trailing_newline(snapshot):
    """Formatted output should not end with a trailing newline."""
    sql = "SELECT 1"
    result = format_sql(sql)
    assert result == snapshot


def test_multiline_output(snapshot):
    """Long SQL gets split across multiple lines by sqlfluff."""
    sql = "select * from users where id = 1 and name = 'test'"
    result = format_sql(sql)
    assert result == snapshot


def test_with_placeholder(snapshot):
    """Python-style placeholders survive formatting."""
    sql = "SELECT * FROM users WHERE id = {_var0}"
    result = format_sql(sql, context={"_var0": "SQLFLUFF_VAR_0"})
    assert result == snapshot


def test_dialect_override(snapshot):
    """Passing a dialect parameter changes formatting behaviour."""
    sql = "SELECT 1"
    result = format_sql(sql, dialect="ansi")
    assert result == snapshot
