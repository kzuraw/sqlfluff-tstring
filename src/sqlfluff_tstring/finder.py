import ast
from dataclasses import dataclass


@dataclass
class SqlTStringMatch:
    tstring_node: ast.TemplateStr
    call_node: ast.Call


class SqlTStringFinder(ast.NodeVisitor):
    def __init__(self) -> None:
        self.matches: list[SqlTStringMatch] = []

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_sql_call(node) and node.args:
            first_arg = node.args[0]
            if isinstance(first_arg, ast.TemplateStr):
                self.matches.append(SqlTStringMatch(first_arg, node))
        self.generic_visit(node)

    def _is_sql_call(self, node: ast.Call) -> bool:
        func = node.func
        if isinstance(func, ast.Name) and func.id == "sql":
            return True
        if isinstance(func, ast.Attribute) and func.attr == "sql":
            return True
        return False


def find_sql_tstrings(source: str) -> list[SqlTStringMatch]:
    tree = ast.parse(source)
    finder = SqlTStringFinder()
    finder.visit(tree)
    return finder.matches
