from sqlfluff_tstring.formatter import format_sql


class TestFormatSql:
    def test_simple_format(self):
        sql = "select * from users"
        result = format_sql(sql)
        assert "select" in result.lower()
        assert "from" in result.lower()

    def test_strips_trailing_newline(self):
        sql = "SELECT 1"
        result = format_sql(sql)
        assert not result.endswith("\n")

    def test_multiline_output(self):
        sql = "select * from users where id = 1 and name = 'test'"
        result = format_sql(sql)
        assert "\n" in result

    def test_with_placeholder(self):
        sql = "SELECT * FROM users WHERE id = SQLFLUFF_VAR_0"
        result = format_sql(sql)
        assert "sqlfluff_var_0" in result.lower()

    def test_dialect_override(self):
        sql = "SELECT 1"
        result = format_sql(sql, dialect="ansi")
        assert "SELECT" in result
