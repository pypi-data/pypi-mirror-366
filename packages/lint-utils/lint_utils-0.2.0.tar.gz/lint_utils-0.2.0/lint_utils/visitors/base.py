import ast
from typing import ClassVar, Protocol

from lint_utils.config import LintUtilsConfig
from lint_utils.visitors.dto import FileInfoDTO


class HasRuleProtocol(Protocol):
    rule: ClassVar[str]

    _config: LintUtilsConfig | None
    _file_info: FileInfoDTO


class BaseVisitor(HasRuleProtocol, ast.NodeVisitor):
    @property
    def can_skip_visitor(self) -> bool:
        if self._config is None:
            return False

        can_skip = self.rule in self._config.lint.ignore
        return can_skip or self._file_info.path.as_posix() in self._config.exclude
