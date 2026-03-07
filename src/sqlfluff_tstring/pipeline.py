import warnings
from dataclasses import dataclass, field
from pathlib import Path

from sqlfluff_tstring.extractor import extract_sql, restore_interpolations
from sqlfluff_tstring.finder import find_sql_tstrings
from sqlfluff_tstring.formatter import format_sql
from sqlfluff_tstring.rewriter import Replacement, apply_replacements


@dataclass
class FileResult:
    path: Path
    changed: bool = False
    original: str = ""
    formatted: str = ""
    errors: list[str] = field(default_factory=list)


def process_file(
    path: Path,
    check_only: bool = False,
    dialect: str | None = None,
    config_path: str | None = None,
) -> FileResult:
    source = path.read_text()
    result = FileResult(path=path, original=source, formatted=source)

    try:
        matches = find_sql_tstrings(source)
    except SyntaxError as e:
        result.errors.append(f"Syntax error: {e}")
        return result

    if not matches:
        return result

    replacements: list[Replacement] = []
    for match in matches:
        sql, mappings = extract_sql(match.tstring_node)
        if not sql.strip():
            continue

        try:
            formatted = format_sql(sql, dialect=dialect, config_path=config_path)
        except Exception as e:
            msg = f"sqlfluff error in {path}:{match.tstring_node.lineno}: {e}"
            warnings.warn(msg, stacklevel=1)
            result.errors.append(msg)
            continue

        restored = restore_interpolations(formatted, mappings)
        replacements.append(Replacement(match.tstring_node, restored))

    if replacements:
        new_source = apply_replacements(source, replacements)
        if new_source != source:
            result.changed = True
            result.formatted = new_source
            if not check_only:
                path.write_text(new_source)

    return result
