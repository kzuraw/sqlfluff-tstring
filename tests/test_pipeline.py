from pathlib import Path

from sqlfluff_tstring.pipeline import process_file


class TestProcessFile:
    def test_formats_simple_sql(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text('sql(t"select   *   from   users")')
        result = process_file(py_file)
        assert result.changed
        content = py_file.read_text()
        assert "select * from users" in content

    def test_check_only_does_not_write(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        original = 'sql(t"select   *   from   users")'
        py_file.write_text(original)
        result = process_file(py_file, check_only=True)
        assert result.changed
        assert py_file.read_text() == original

    def test_no_change_when_already_formatted(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text('sql(t"SELECT 1")')
        result = process_file(py_file)
        assert not result.changed

    def test_preserves_interpolation(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text(
            'sql(t"select * from users where id = {uid} and name = {name}")'
        )
        result = process_file(py_file)
        assert result.changed
        content = py_file.read_text()
        assert "{uid}" in content
        assert "{name}" in content

    def test_skips_non_sql_tstrings(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text('foo(t"select * from users")')
        result = process_file(py_file)
        assert not result.changed

    def test_handles_syntax_error(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text("def foo(:")
        result = process_file(py_file)
        assert not result.changed
        assert len(result.errors) > 0

    def test_multiple_sql_calls(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text(
            'sql(t"select   *   from   a")\nsql(t"select   *   from   b")'
        )
        result = process_file(py_file)
        assert result.changed
        content = py_file.read_text()
        assert "select * from a" in content
        assert "select * from b" in content

    def test_preserves_limit_offset_placeholders(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text(
            'sql(t"SELECT id, name FROM products '
            'WHERE category = {cat} '
            'ORDER BY price LIMIT {page_size} OFFSET {skip}")'
        )
        result = process_file(py_file)
        content = py_file.read_text()
        assert "{cat}" in content
        assert "{page_size}" in content
        assert "{skip}" in content

    def test_preserves_order_by_direction_placeholder(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text(
            'sql(t"SELECT id, title FROM articles '
            'ORDER BY {sort_col} {sort_dir}")'
        )
        result = process_file(py_file)
        content = py_file.read_text()
        assert "{sort_col}" in content
        assert "{sort_dir}" in content

    def test_many_placeholders_no_index_collision(self, tmp_path: Path):
        """11+ placeholders to test that :SQLFLUFF_VAR_1 doesn't match inside :SQLFLUFF_VAR_10."""
        py_file = tmp_path / "test.py"
        py_file.write_text(
            'sql(t"SELECT {col0}, {col1}, {col2}, {col3}, {col4}, '
            '{col5}, {col6}, {col7}, {col8}, {col9} '
            'FROM orders WHERE region = {region} '
            'LIMIT {n}")'
        )
        result = process_file(py_file)
        content = py_file.read_text()
        for i in range(10):
            assert f"{{col{i}}}" in content
        assert "{region}" in content
        assert "{n}" in content

    def test_join_with_multiple_where_clauses(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text(
            'sql(t"SELECT o.id, c.email, o.total '
            'FROM orders o '
            'JOIN customers c ON c.id = o.customer_id '
            'LEFT JOIN refunds r ON r.order_id = o.id '
            'WHERE o.status = {status} '
            'AND o.created_at >= {after} '
            'AND o.created_at < {before} '
            'ORDER BY o.created_at DESC '
            'LIMIT {limit} OFFSET {offset}")'
        )
        result = process_file(py_file)
        content = py_file.read_text()
        for placeholder in ["{status}", "{after}", "{before}", "{limit}", "{offset}"]:
            assert placeholder in content

    def test_empty_tstring_skipped(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text('sql(t"")')
        result = process_file(py_file)
        assert not result.changed
