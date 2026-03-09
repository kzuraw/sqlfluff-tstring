from pathlib import Path

from syrupy import SnapshotAssertion

from sqlfluff_tstring.formatter import format_sql


def test_simple_format(snapshot: SnapshotAssertion):
    """Format a basic lowercase SQL statement."""
    sql = "select * from users"
    result = format_sql(sql)
    assert result == snapshot


def test_strips_trailing_newline(snapshot: SnapshotAssertion):
    """Formatted output should not end with a trailing newline."""
    sql = "SELECT 1"
    result = format_sql(sql)
    assert result == snapshot


def test_multiline_output(snapshot: SnapshotAssertion):
    """Long SQL gets split across multiple lines by sqlfluff."""
    sql = "select * from users where id = 1 and name = 'test'"
    result = format_sql(sql)
    assert result == snapshot


def test_with_placeholder(snapshot: SnapshotAssertion):
    """Python-style placeholders survive formatting."""
    sql = "SELECT * FROM users WHERE id = {_var0}"
    result = format_sql(sql, context={"_var0": "SQLFLUFF_VAR_0"})
    assert result == snapshot


def test_dialect_override(snapshot: SnapshotAssertion):
    """Passing a dialect parameter changes formatting behaviour."""
    sql = "SELECT 1"
    result = format_sql(sql, dialect="ansi")
    assert result == snapshot


def test_respects_sqlfluff_config_from_file_path(
    tmp_path: Path, snapshot: SnapshotAssertion
):
    """Rules from .sqlfluff near the target file are applied."""
    config = tmp_path / ".sqlfluff"
    config.write_text(
        "[sqlfluff]\n"
        "dialect = ansi\n"
        "[sqlfluff:rules:capitalisation.keywords]\n"
        "capitalisation_policy = upper\n"
    )
    dummy_py = tmp_path / "example.py"
    dummy_py.write_text("")

    result = format_sql("select 1", file_path=dummy_py)
    assert result == snapshot


def test_respects_sqlfluff_config_with_placeholders(
    tmp_path: Path, snapshot: SnapshotAssertion
):
    """Rules from .sqlfluff are applied even when placeholders are present."""
    config = tmp_path / ".sqlfluff"
    config.write_text(
        "[sqlfluff]\n"
        "dialect = ansi\n"
        "[sqlfluff:rules:capitalisation.keywords]\n"
        "capitalisation_policy = upper\n"
    )
    dummy_py = tmp_path / "example.py"
    dummy_py.write_text("")

    result = format_sql(
        "select * from users where id = {_var0}",
        context={"_var0": "SQLFLUFF_VAR_0"},
        file_path=dummy_py,
    )
    assert result == snapshot
