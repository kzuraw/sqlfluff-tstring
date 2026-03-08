from pathlib import Path

import pytest

from sqlfluff_tstring.pipeline import process_file

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    "fixture",
    sorted(FIXTURES.glob("*.py")),
    ids=lambda p: p.stem,
)
def test_format_fixture(fixture: Path, tmp_path: Path, snapshot):
    """Format a fixture file and verify the output matches the snapshot."""
    target = tmp_path / fixture.name
    target.write_text(fixture.read_text())
    result = process_file(target)
    assert not result.errors
    assert result.formatted == snapshot
