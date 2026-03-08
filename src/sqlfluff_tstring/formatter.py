from pathlib import Path

import sqlfluff
from sqlfluff.core import FluffConfig


def format_sql(
    sql: str,
    config_path: str | None = None,
    dialect: str | None = None,
    context: dict[str, str] | None = None,
    file_path: Path | None = None,
) -> str:
    overrides = {"templater": "python", "dialect": dialect or "ansi"}

    # from_path auto-discovers .sqlfluff config files along the path to
    # the target file. It passes discovered config as configs= internally,
    # so we inject templater context afterward via set_value.
    config = FluffConfig.from_path(
        path=str(file_path) if file_path is not None else ".",
        extra_config_path=config_path,
        overrides=overrides,
        require_dialect=False,
    )

    if context:
        for key, value in context.items():
            config.set_value(["templater", "python", "context", key], value)

    result = sqlfluff.fix(sql, config=config)
    return result.rstrip("\n")
