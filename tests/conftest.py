import ast

import pytest


@pytest.fixture
def parse_source():
    """Helper to parse Python source and return the AST tree."""

    def _parse(source: str) -> ast.Module:
        return ast.parse(source)

    return _parse
