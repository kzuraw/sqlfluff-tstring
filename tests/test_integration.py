from pathlib import Path

import pytest

from sqlfluff_tstring.pipeline import process_file

FIXTURES = Path(__file__).parent / "fixtures"
_fixture_files = sorted(FIXTURES.glob("*.py"))
assert _fixture_files, f"No fixture files found in {FIXTURES}"


@pytest.mark.parametrize(
    "fixture",
    _fixture_files,
    ids=lambda p: p.stem,
)
def test_format_fixture(fixture: Path, tmp_path: Path, snapshot):
    """Format a fixture file and verify the output matches the snapshot."""
    target = tmp_path / fixture.name
    target.write_text(fixture.read_text())
    result = process_file(target)
    assert not result.errors, f"process_file returned errors: {result.errors}"
    assert result.formatted == snapshot
