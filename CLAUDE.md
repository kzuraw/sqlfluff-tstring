# CLAUDE.md

CLI tool that auto-formats SQL inside Python t-strings (`sql(t"...")`) using sqlfluff. Requires Python 3.14+ (PEP 750 t-strings).

## Commands

```bash
uv sync            # install deps
uv run pytest      # run all tests
uv run ruff check  # lint
uv run ty check    # typecheck
```

## Architecture

The formatting pipeline flows through four modules in `src/sqlfluff_tstring/`:

1. **finder.py** - AST visitor finds `sql(t"...")` and `obj.sql(t"...")` calls, returns `SqlTStringMatch` (tstring node + call node)
2. **extractor.py** - Walks `ast.TemplateStr` values, replaces `ast.Interpolation` nodes with `:SQLFLUFF_VAR_N` placeholders, records `PlaceholderMapping` for each
3. **formatter.py** - Passes placeholder-substituted SQL through `sqlfluff.fix()` using colon param_style templater
4. **rewriter.py** - Applies formatted SQL back into source text using AST position info; auto-upgrades single quotes to triple quotes when newlines are introduced; wraps multiline content with leading/trailing newlines

**pipeline.py** orchestrates: find matches → extract → format → restore interpolations → apply replacements → write file. Returns `FileResult` with original/formatted text and errors.

**cli.py** handles arg parsing, file collection (skips `__pycache__`, `.venv`, `.git`, etc.), and output modes (in-place, `--check`, `--diff`).

## Key design details

- Interpolations are preserved by replacing them with sqlfluff-compatible colon-style placeholders (`:SQLFLUFF_VAR_0`), then restored after formatting
- The `restore_interpolations` function raises `ValueError` if a placeholder goes missing after formatting (sqlfluff restructured/removed it)
- Replacements are applied in reverse source order to avoid offset shifting
- The tool uses sqlfluff's `placeholder` templater with `colon` param_style
