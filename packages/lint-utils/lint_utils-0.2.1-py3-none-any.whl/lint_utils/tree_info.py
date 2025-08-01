import ast
from dataclasses import dataclass
from pathlib import Path

from lint_utils.common.files import open_file


@dataclass(frozen=True, slots=True, kw_only=True)
class TreeInfo:
    tree: ast.Module
    raw: str


def get_tree_info(file_path: Path) -> TreeInfo | None:
    source = open_file(file_path)
    if source is None:
        return None

    return TreeInfo(tree=ast.parse(source), raw=source)
