from pathlib import Path

from sqlfluff_tstring.pipeline import process_file


def test_formats_simple_sql(tmp_path: Path):
    """Format a basic sql(t"...") with extra whitespace."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"select   *   from   users")')
    result = process_file(py_file)
    assert result.changed
    content = py_file.read_text()
    assert "SELECT * FROM users" in content


def test_check_only_does_not_write(tmp_path: Path):
    """check_only=True reports changes without modifying the file."""
    py_file = tmp_path / "test.py"
    original = 'sql(t"select   *   from   users")'
    py_file.write_text(original)
    result = process_file(py_file, check_only=True)
    assert result.changed
    assert py_file.read_text() == original


def test_no_change_when_already_formatted(tmp_path: Path):
    """Already-formatted SQL is left untouched."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"SELECT 1")')
    result = process_file(py_file)
    assert not result.changed


def test_preserves_interpolation(tmp_path: Path):
    """Interpolation expressions survive the format round-trip."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"select * from users where id = {uid} and name = {name}")')
    result = process_file(py_file)
    assert result.changed
    content = py_file.read_text()
    assert "{uid}" in content
    assert "{name}" in content


def test_skips_non_sql_tstrings(tmp_path: Path):
    """t-strings not inside sql() calls are ignored."""
    py_file = tmp_path / "test.py"
    py_file.write_text('foo(t"select * from users")')
    result = process_file(py_file)
    assert not result.changed


def test_handles_syntax_error(tmp_path: Path):
    """Files with Python syntax errors produce errors, not crashes."""
    py_file = tmp_path / "test.py"
    py_file.write_text("def foo(:")
    result = process_file(py_file)
    assert not result.changed
    assert len(result.errors) > 0


def test_multiple_sql_calls(tmp_path: Path):
    """All sql(t"...") calls in a file are formatted."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"select   *   from   a")\nsql(t"select   *   from   b")')
    result = process_file(py_file)
    assert result.changed
    content = py_file.read_text()
    assert "SELECT * FROM a" in content
    assert "SELECT * FROM b" in content


def test_preserves_limit_offset_placeholders(tmp_path: Path):
    """LIMIT/OFFSET interpolation placeholders are preserved after formatting."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        'sql(t"SELECT id, name FROM products '
        "WHERE category = {cat} "
        'ORDER BY price LIMIT {page_size} OFFSET {skip}")'
    )
    process_file(py_file)
    content = py_file.read_text()
    assert "{cat}" in content
    assert "{page_size}" in content
    assert "{skip}" in content


def test_preserves_order_by_direction_placeholder(tmp_path: Path):
    """ORDER BY direction interpolation placeholders are preserved."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        'sql(t"SELECT id, title FROM articles ORDER BY {sort_col} {sort_dir}")'
    )
    process_file(py_file)
    content = py_file.read_text()
    assert "{sort_col}" in content
    assert "{sort_dir}" in content


def test_many_placeholders_no_index_collision(tmp_path: Path):
    """11+ placeholders don't collide (e.g. :SQLFLUFF_VAR_1 vs :SQLFLUFF_VAR_10)."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        'sql(t"SELECT {col0}, {col1}, {col2}, {col3}, {col4}, '
        "{col5}, {col6}, {col7}, {col8}, {col9} "
        "FROM orders WHERE region = {region} "
        'LIMIT {n}")'
    )
    process_file(py_file)
    content = py_file.read_text()
    for i in range(10):
        assert f"{{col{i}}}" in content
    assert "{region}" in content
    assert "{n}" in content


def test_join_with_multiple_where_clauses(tmp_path: Path):
    """Complex JOIN query with multiple WHERE placeholders preserved."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        'sql(t"SELECT o.id, c.email, o.total '
        "FROM orders o "
        "JOIN customers c ON c.id = o.customer_id "
        "LEFT JOIN refunds r ON r.order_id = o.id "
        "WHERE o.status = {status} "
        "AND o.created_at >= {after} "
        "AND o.created_at < {before} "
        "ORDER BY o.created_at DESC "
        'LIMIT {limit} OFFSET {offset}")'
    )
    process_file(py_file)
    content = py_file.read_text()
    for placeholder in ["{status}", "{after}", "{before}", "{limit}", "{offset}"]:
        assert placeholder in content


def test_empty_tstring_skipped(tmp_path: Path):
    """Empty t-strings are left unchanged."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"")')
    result = process_file(py_file)
    assert not result.changed


def test_idempotent_multiline(tmp_path: Path):
    """Formatting an already-formatted multiline t-string is idempotent."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        'sql(t"select * from users where active = 1 order by name")'
    )
    process_file(py_file)
    first_pass = py_file.read_text()
    process_file(py_file)
    second_pass = py_file.read_text()
    assert first_pass == second_pass
