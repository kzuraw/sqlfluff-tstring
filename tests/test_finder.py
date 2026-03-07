from sqlfluff_tstring.finder import find_sql_tstrings


class TestFindSqlTStrings:
    def test_simple_sql_call(self):
        source = 'sql(t"SELECT * FROM users")'
        matches = find_sql_tstrings(source)
        assert len(matches) == 1

    def test_sql_call_with_interpolation(self):
        source = 'sql(t"SELECT * FROM users WHERE id = {uid}")'
        matches = find_sql_tstrings(source)
        assert len(matches) == 1

    def test_attribute_sql_call(self):
        source = 'db.sql(t"SELECT 1")'
        matches = find_sql_tstrings(source)
        assert len(matches) == 1

    def test_no_match_regular_string(self):
        source = 'sql("SELECT 1")'
        matches = find_sql_tstrings(source)
        assert len(matches) == 0

    def test_no_match_no_sql_call(self):
        source = 'foo(t"SELECT 1")'
        matches = find_sql_tstrings(source)
        assert len(matches) == 0

    def test_multiple_matches(self):
        source = """\
sql(t"SELECT 1")
sql(t"SELECT 2")
"""
        matches = find_sql_tstrings(source)
        assert len(matches) == 2

    def test_triple_quoted(self):
        source = 'sql(t"""SELECT * FROM users""")'
        matches = find_sql_tstrings(source)
        assert len(matches) == 1

    def test_empty_tstring(self):
        source = 'sql(t"")'
        matches = find_sql_tstrings(source)
        assert len(matches) == 1

    def test_nested_in_function(self):
        source = """\
def query():
    return sql(t"SELECT * FROM users WHERE id = {uid}")
"""
        matches = find_sql_tstrings(source)
        assert len(matches) == 1
