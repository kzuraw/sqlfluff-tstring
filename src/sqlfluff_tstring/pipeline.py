from dataclasses import dataclass, field
from pathlib import Path

from sqlfluff.core.errors import SQLBaseError, SQLFluffSkipFile

from sqlfluff_tstring.extractor import build_context, extract_sql, restore_interpolations
from sqlfluff_tstring.finder import find_sql_tstrings
from sqlfluff_tstring.formatter import format_sql
from sqlfluff_tstring.rewriter import Replacement, apply_replacements


@dataclass
class FileResult:
    path: Path
    original: str = ""
    formatted: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.original != self.formatted


def process_file(
    path: Path,
    check_only: bool = False,
    dialect: str | None = None,
    config_path: str | None = None,
) -> FileResult:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return FileResult(path=path, errors=[f"Could not read {path}: {e}"])

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

        context = build_context(mappings)
        try:
            formatted = format_sql(
                sql, dialect=dialect, config_path=config_path, context=context
            )
        except (SQLBaseError, SQLFluffSkipFile) as e:
            result.errors.append(f"sqlfluff error in {path}:{match.tstring_node.lineno}: {e}")
            continue

        try:
            restored = restore_interpolations(formatted, mappings)
        except ValueError as e:
            result.errors.append(f"Restore error in {path}:{match.tstring_node.lineno}: {e}")
            continue
        replacements.append(Replacement(match.tstring_node, restored))

    if replacements:
        new_source = apply_replacements(source, replacements)
        if new_source != source:
            result.formatted = new_source
            if not check_only:
                try:
                    path.write_text(new_source, encoding="utf-8")
                except OSError as e:
                    result.formatted = source
                    result.errors.append(f"Could not write {path}: {e}")

    return result
