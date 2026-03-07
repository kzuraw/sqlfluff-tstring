import sqlfluff


def format_sql(
    sql: str, config_path: str | None = None, dialect: str | None = None
) -> str:
    result = sqlfluff.fix(sql, dialect=dialect, config_path=config_path)
    return result.rstrip("\n")
