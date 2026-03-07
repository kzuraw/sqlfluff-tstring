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

    def test_empty_tstring_skipped(self, tmp_path: Path):
        py_file = tmp_path / "test.py"
        py_file.write_text('sql(t"")')
        result = process_file(py_file)
        assert not result.changed
