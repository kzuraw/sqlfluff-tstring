from sqlfluff_tstring.formatter import format_sql


def test_simple_format():
    """Format a basic lowercase SQL statement."""
    sql = "select * from users"
    result = format_sql(sql)
    assert "select" in result.lower()
    assert "from" in result.lower()


def test_strips_trailing_newline():
    """Formatted output should not end with a trailing newline."""
    sql = "SELECT 1"
    result = format_sql(sql)
    assert not result.endswith("\n")


def test_multiline_output():
    """Long SQL gets split across multiple lines by sqlfluff."""
    sql = "select * from users where id = 1 and name = 'test'"
    result = format_sql(sql)
    assert "\n" in result


def test_with_placeholder():
    """Colon-style placeholders survive formatting."""
    sql = "SELECT * FROM users WHERE id = SQLFLUFF_VAR_0"
    result = format_sql(sql)
    assert "sqlfluff_var_0" in result.lower()


def test_dialect_override():
    """Passing a dialect parameter changes formatting behaviour."""
    sql = "SELECT 1"
    result = format_sql(sql, dialect="ansi")
    assert "SELECT" in result
