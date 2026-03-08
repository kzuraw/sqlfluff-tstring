import pytest
from syrupy.extensions.single_file import SingleFileSnapshotExtension, WriteMode


class TextSnapshotExtension(SingleFileSnapshotExtension):
    _write_mode = WriteMode.TEXT
    file_extension = "txt"

    def serialize(self, data, *, exclude=None, include=None, matcher=None):
        return str(data)


@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(TextSnapshotExtension)
