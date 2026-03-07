import sqlfluff
from sqlfluff.core import FluffConfig


def format_sql(
    sql: str, config_path: str | None = None, dialect: str | None = None
) -> str:
    overrides = {"templater": "placeholder", "dialect": dialect or "ansi"}

    config = FluffConfig(
        extra_config_path=config_path,
        overrides=overrides,
        configs={"templater": {"placeholder": {"param_style": "colon"}}},
        require_dialect=False,
    )

    result = sqlfluff.fix(sql, config=config)
    return result.rstrip("\n")
