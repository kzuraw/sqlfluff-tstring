# sqlfluff-tstring

Auto-format SQL inside Python t-strings using [sqlfluff](https://sqlfluff.com/).

Finds `sql(t"...")` calls in `.py` files and formats the embedded SQL, preserving interpolations. Uses hardcoded settings: PostgreSQL dialect, uppercase keywords, and 88-character line length.

Requires Python 3.14+ (PEP 750 t-strings).

## Installation

```bash
pip install sqlfluff-tstring
```

## Usage

```bash
# Format files in-place
sqlfluff-tstring src/

# Check mode (exit 1 if changes needed, for CI)
sqlfluff-tstring --check src/

# Show diff without writing
sqlfluff-tstring --diff src/
```

## What it does

Given a file like:

```python
from sql_tstring import sql

query = sql(t"select   *   from   users   where   id = {uid}   and   name = {name}")
```

Running `sqlfluff-tstring` produces:

```python
from sql_tstring import sql

query = sql(t"""
SELECT * FROM users
WHERE id = {uid} AND name = {name}
""")
```

- Interpolations (`{uid}`, `{name!r}`, `{val:.2f}`) are preserved through formatting
- Single quotes auto-upgrade to triple quotes when sqlfluff introduces newlines
- Multiline content in triple-quoted t-strings is wrapped with leading/trailing newlines
- Supports `sql(t"...")` and `obj.sql(t"...")` call patterns

## CLI options

```
sqlfluff-tstring [OPTIONS] [PATHS...]

positional arguments:
  paths              Files or directories to format (default: .)

options:
  --check            Exit 1 if changes needed (CI mode)
  --diff             Show diff, don't write changes
  -v, --verbose      Show unchanged files
  -q, --quiet        Suppress all output
```

Exit codes: `0` = success/no changes, `1` = changes needed (check mode).

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/ tests/
uv run ty check src/
```
