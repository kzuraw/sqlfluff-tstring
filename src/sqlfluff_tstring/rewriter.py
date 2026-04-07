import ast
from dataclasses import dataclass


@dataclass
class Replacement:
    tstring_node: ast.TemplateStr
    new_content: str


def _detect_quote_style(source: str, tstring_node: ast.TemplateStr) -> str:
    lines = source.splitlines(keepends=True)
    line = lines[tstring_node.lineno - 1]
    # Skip past any prefix characters and the 't' to find the quote
    col = tstring_node.col_offset
    while col < len(line) and line[col] in "rRbBtT":
        col += 1
    if line[col : col + 3] in ('"""', "'''"):
        return line[col : col + 3]
    return line[col]


def _get_source_range(source: str, node: ast.TemplateStr) -> tuple[int, int]:
    """Return (start_offset, end_offset) as character positions in source."""
    lines = source.splitlines(keepends=True)
    start = sum(len(lines[i]) for i in range(node.lineno - 1)) + node.col_offset
    if node.end_lineno is None or node.end_col_offset is None:
        raise ValueError(
            f"AST node at line {node.lineno} is missing end position metadata"
        )
    end = sum(len(lines[i]) for i in range(node.end_lineno - 1)) + node.end_col_offset
    return start, end


def apply_replacements(source: str, replacements: list[Replacement]) -> str:
    # Sort by position in reverse order so earlier replacements don't shift offsets
    sorted_replacements = sorted(
        replacements,
        key=lambda r: (r.tstring_node.lineno, r.tstring_node.col_offset),
        reverse=True,
    )

    result = source
    for replacement in sorted_replacements:
        start, end = _get_source_range(result, replacement.tstring_node)
        quote = _detect_quote_style(result, replacement.tstring_node)
        # Upgrade to triple quotes if content has newlines
        if "\n" in replacement.new_content and len(quote) == 1:
            quote = quote * 3
        # Wrap multiline content with leading/trailing newlines in triple-quoted strings
        content = replacement.new_content
        if len(quote) == 3 and "\n" in content:
            content = content.strip("\n")
            content = f"\n{content}\n"
        new_tstring = f"t{quote}{content}{quote}"
        result = result[:start] + new_tstring + result[end:]

    return result
