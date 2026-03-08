import subprocess
import sys
from pathlib import Path


def test_format_file(tmp_path: Path):
    """Run the CLI to format a file in-place."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"select   *   from   users")')
    result = subprocess.run(
        [sys.executable, "-m", "sqlfluff_tstring", str(py_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    content = py_file.read_text()
    assert "select * from users" in content


def test_check_mode_returns_1(tmp_path: Path):
    """--check exits 1 when the file needs formatting."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"select   *   from   users")')
    result = subprocess.run(
        [sys.executable, "-m", "sqlfluff_tstring", "--check", str(py_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_check_mode_returns_0_when_formatted(tmp_path: Path):
    """--check exits 0 when the file is already formatted."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"SELECT 1")')
    result = subprocess.run(
        [sys.executable, "-m", "sqlfluff_tstring", "--check", str(py_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_diff_mode(tmp_path: Path):
    """--diff prints a unified diff without modifying the file."""
    py_file = tmp_path / "test.py"
    py_file.write_text('sql(t"select   *   from   users")')
    result = subprocess.run(
        [sys.executable, "-m", "sqlfluff_tstring", "--diff", str(py_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "---" in result.stdout or "@@" in result.stdout
    # Diff mode should not write changes
    assert py_file.read_text() == 'sql(t"select   *   from   users")'


def test_directory_walk(tmp_path: Path):
    """Passing a directory formats all .py files recursively."""
    subdir = tmp_path / "pkg"
    subdir.mkdir()
    py_file = subdir / "mod.py"
    py_file.write_text('sql(t"select   1")')
    result = subprocess.run(
        [sys.executable, "-m", "sqlfluff_tstring", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
