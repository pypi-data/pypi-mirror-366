import ast
import itertools
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, TypeAlias

from lint_utils.common.std import report_info
from lint_utils.common.text_styling import to_bold, to_cyan, to_red
from lint_utils.config import LintUtilsConfig
from lint_utils.rules import Rule, can_ignore_rule
from lint_utils.tree_info import TreeInfo
from lint_utils.visitors.base import BaseVisitor
from lint_utils.visitors.dto import FileInfoDTO

FuncDef: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True, slots=True, kw_only=True)
class FieldInfo:
    class_name: str
    name: str
    line: int
    col_offset: int
    assigned_to: str | None = None


class UselessFieldVisitor(BaseVisitor):
    rule: ClassVar[str] = Rule.useless_field

    def __init__(
        self,
        file_info: FileInfoDTO,
        config: LintUtilsConfig | None = None,
    ) -> None:
        super().__init__()

        self._file_info = file_info
        self._class_name: str | None = None
        self._base_class_names: list[str] | None = None
        self._field_definitions: dict[str, FieldInfo] = {}
        self._config = config

        self._excluded_classes: Iterable[str] = ()
        self._excluded_base_classes: Iterable[str] = ()

        if self._config:
            self._excluded_classes = self._config.exclude_classes.get(self.rule, ())
            self._excluded_base_classes = self._config.exclude_base_classes.get(
                self.rule, ()
            )

    @property
    def useless_fields(self) -> Mapping[str, FieldInfo]:
        return self._field_definitions

    @property
    def class_name(self) -> str:
        if self._class_name:
            return self._class_name

        raise ValueError

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:  # noqa: ANN401, N802
        self._class_name = node.name
        self._base_class_names = self._get_parent_class_names(node)

        if self._is_class_excluded:
            return

        for item in node.body:
            if not isinstance(item, FuncDef):
                continue

            if item.name == "__init__":
                self._process_init_assignment(item)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> Any:  # noqa: ANN401, N802
        root_node = _find_root_node(node)
        key = self._build_field_key(_get_field_name(root_node))
        field = self._field_definitions.get(key, None)

        if field is None:
            return self.generic_visit(node)

        if isinstance(node.ctx, ast.Load):
            del self._field_definitions[key]

        if isinstance(node.ctx, ast.Store) and node.lineno > field.line:
            del self._field_definitions[key]

        return self.generic_visit(node)

    @property
    def _is_class_excluded(self) -> bool:
        if self._config is None or self._config.lint is None:
            return False

        all_excluded_classes = list(
            itertools.chain(self._excluded_classes, self._excluded_base_classes)
        )

        is_excluded = False
        if self._base_class_names:
            is_excluded = any(
                cls in all_excluded_classes for cls in self._base_class_names
            )

        return is_excluded or self.class_name in all_excluded_classes

    def _get_parent_class_names(self, node: ast.ClassDef) -> list[str] | None:
        return [base.id for base in node.bases if isinstance(base, ast.Name)]

    def _process_init_assignment(self, method: FuncDef) -> None:
        for item in method.body:
            match item:
                case ast.Assign():
                    target = item.targets[0]
                    if not isinstance(target, ast.Attribute):
                        continue

                    field_info = FieldInfo(
                        class_name=self.class_name,
                        name=_get_field_name(target),
                        line=target.lineno,
                        col_offset=target.col_offset,
                        assigned_to=_get_assigned_to(item),
                    )

                case ast.AnnAssign():
                    target = item.target
                    if not isinstance(target, ast.Attribute):
                        continue

                    field_info = FieldInfo(
                        class_name=self.class_name,
                        name=_get_field_name(target),
                        line=target.lineno,
                        col_offset=target.col_offset,
                        assigned_to=_get_assigned_to(item),
                    )

                case _:
                    continue

            if can_ignore_rule(
                self._file_info.source_code_lines,
                line_number=field_info.line - 1,
                rule=self.rule,
            ):
                continue

            self._field_definitions[self._build_field_key(field_info.name)] = field_info

    def _build_field_key(self, field_name: str) -> str:
        return f"{self._class_name}_{field_name}"


def _get_field_name(node: ast.Attribute) -> str:
    if isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"

    return node.attr


def _get_assigned_to(attr: ast.Assign | ast.AnnAssign) -> str | None:
    if not isinstance(attr.value, ast.Name):
        return None

    return attr.value.id


def _find_root_node(node: ast.Attribute) -> ast.Attribute:
    if isinstance(node.value, ast.Attribute):
        return _find_root_node(node.value)

    return node


def check_useless_field(  # noqa: C901
    info: TreeInfo,
    *,
    file_path: Path,
    config: LintUtilsConfig | None = None,
) -> bool:
    has_errors = []
    for module in ast.walk(info.tree):
        if not isinstance(module, ast.Module):
            continue

        for item in module.body:
            if not isinstance(item, ast.ClassDef):
                continue

            visitor = UselessFieldVisitor(
                file_info=FileInfoDTO(
                    source_code_lines=info.raw.split("\n"),
                    path=file_path,
                ),
                config=config,
            )
            if visitor.can_skip_visitor:
                continue

            visitor.visit(item)

            if visitor.useless_fields:
                msg = f"{to_bold(to_cyan(visitor.rule))} Unused object class fields found in class {to_bold(visitor.class_name)}"
                report_info(msg)
                for field_info in visitor.useless_fields.values():
                    full_path = f"{file_path.as_posix()}:{field_info.line}:{field_info.col_offset + 1}"
                    line_msg = f"{full_path} {to_bold(to_red(field_info.name))}"
                    report_info(line_msg)
                report_info("")

                has_errors.append(True)

            has_errors.append(False)

    return any(has_errors)
