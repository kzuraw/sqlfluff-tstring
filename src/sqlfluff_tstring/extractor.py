import ast
from dataclasses import dataclass
from typing import cast


@dataclass
class PlaceholderMapping:
    index: int
    placeholder: str
    original_expr: str
    conversion: int
    format_spec: str | None


def extract_sql(
    tstring_node: ast.TemplateStr,
) -> tuple[str, list[PlaceholderMapping]]:
    sql_parts: list[str] = []
    mappings: list[PlaceholderMapping] = []
    placeholder_index = 0

    for value in tstring_node.values:
        if isinstance(value, ast.Constant):
            sql_parts.append(cast(str, value.value))
        elif isinstance(value, ast.Interpolation):
            placeholder = f"{{_var{placeholder_index}}}"
            sql_parts.append(placeholder)

            format_spec: str | None = None
            if value.format_spec is not None:
                # format_spec is a JoinedStr with Constant values
                spec_parts: list[str] = []
                for part in cast(ast.JoinedStr, value.format_spec).values:
                    if isinstance(part, ast.Constant):
                        spec_parts.append(cast(str, part.value))
                format_spec = "".join(spec_parts)

            mappings.append(
                PlaceholderMapping(
                    index=placeholder_index,
                    placeholder=placeholder,
                    original_expr=value.str,
                    conversion=value.conversion,
                    format_spec=format_spec,
                )
            )
            placeholder_index += 1

    return "".join(sql_parts), mappings


def build_context(mappings: list[PlaceholderMapping]) -> dict[str, str]:
    return {f"_var{m.index}": f"SQLFLUFF_VAR_{m.index}" for m in mappings}


def restore_interpolations(
    formatted_sql: str, mappings: list[PlaceholderMapping]
) -> str:
    result = formatted_sql
    for mapping in mappings:
        expr = mapping.original_expr
        suffix = ""
        if mapping.conversion != -1:
            suffix += f"!{chr(mapping.conversion)}"
        if mapping.format_spec is not None:
            suffix += f":{mapping.format_spec}"
        replacement = "{" + expr + suffix + "}"
        count = result.count(mapping.placeholder)
        if count == 0:
            raise ValueError(
                f"Placeholder {mapping.placeholder} not found in formatted SQL. "
                f"sqlfluff may have removed or restructured the placeholder. "
                f"Original expression: {mapping.original_expr}"
            )
        if count > 1:
            raise ValueError(
                f"Placeholder {mapping.placeholder} appears {count} times in formatted SQL. "
                f"sqlfluff may have duplicated the placeholder. "
                f"Original expression: {mapping.original_expr}"
            )
        result = result.replace(mapping.placeholder, replacement)
    return result
