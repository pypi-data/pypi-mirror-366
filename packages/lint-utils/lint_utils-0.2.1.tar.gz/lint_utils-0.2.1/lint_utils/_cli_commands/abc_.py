from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

from lint_utils.config import LintUtilsConfig

from .dto import CheckResult


class BaseCommand(ABC):
    rule: ClassVar[str]

    def __init__(
        self,
        paths: Iterable[Path],
        config: LintUtilsConfig | None,
    ) -> None:
        self._paths = paths
        self._config = config

    @abstractmethod
    def execute(self) -> CheckResult:
        raise NotImplementedError

    @property
    def can_skip_command(self) -> bool:
        if self._config is None:
            return False

        return self.rule in self._config.lint.ignore
