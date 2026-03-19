import sqlfluff
from sqlfluff.core import FluffConfig


def format_sql(
    sql: str,
    context: dict[str, str] | None = None,
) -> str:
    config = FluffConfig(
        overrides={
            "dialect": "postgres",
            "templater": "python",
            "max_line_length": 88,
        },
        extra_config_path=None,
        require_dialect=False,
    )

    capitalisation_rules = [
        "capitalisation.keywords",
        "capitalisation.functions",
        "capitalisation.literals",
        "capitalisation.types",
    ]
    for rule in capitalisation_rules:
        config.set_value(
            ["rules", rule, "capitalisation_policy"],
            "upper",
        )

    if context:
        for key, value in context.items():
            config.set_value(["templater", "python", "context", key], value)

    result = sqlfluff.fix(sql, config=config)
    return result.rstrip("\n")
