import argparse
import difflib
import sys
from pathlib import Path

from sqlfluff_tstring.pipeline import process_file

SKIP_DIRS = {"__pycache__", ".venv", ".git", "node_modules", ".tox", ".mypy_cache"}


def _collect_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            print(f"Error: path not found: {path}", file=sys.stderr)
            sys.exit(2)
        if path.is_file():
            if path.suffix == ".py":
                files.append(path)
            else:
                print(f"Warning: skipping non-Python file: {path}", file=sys.stderr)
        elif path.is_dir():
            for py_file in sorted(path.rglob("*.py")):
                if not any(part in SKIP_DIRS for part in py_file.parts):
                    files.append(py_file)
    return files


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="sqlfluff-tstring",
        description="Format SQL inside Python t-strings using sqlfluff",
    )
    parser.add_argument("paths", nargs="*", type=Path, default=[Path(".")])
    parser.add_argument(
        "--check", action="store_true", help="Exit 1 if changes needed (CI mode)"
    )
    parser.add_argument(
        "--diff", action="store_true", help="Show diff, don't write changes"
    )
    parser.add_argument("--config", help="Path to .sqlfluff config file")
    parser.add_argument("--dialect", help="Override SQL dialect")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args(argv)
    check_only = args.check or args.diff

    files = _collect_files(args.paths)
    if not files and not args.quiet:
        print("No Python files found.", file=sys.stderr)
        sys.exit(0)

    any_changed = False
    for path in files:
        result = process_file(
            path, check_only=check_only, dialect=args.dialect, config_path=args.config
        )

        if result.changed:
            any_changed = True
            if not args.quiet:
                print(f"{'Would reformat' if check_only else 'Reformatted'}: {path}")

            if args.diff:
                diff = difflib.unified_diff(
                    result.original.splitlines(keepends=True),
                    result.formatted.splitlines(keepends=True),
                    fromfile=str(path),
                    tofile=str(path),
                )
                sys.stdout.writelines(diff)

        elif args.verbose and not args.quiet:
            print(f"Unchanged: {path}")

        for error in result.errors:
            if not args.quiet:
                print(f"Warning: {error}", file=sys.stderr)

    if args.check and any_changed:
        sys.exit(1)
