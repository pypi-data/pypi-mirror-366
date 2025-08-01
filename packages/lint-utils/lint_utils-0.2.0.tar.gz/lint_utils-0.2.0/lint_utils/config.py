from collections.abc import Mapping
from pathlib import Path
from typing import TypeVar

import msgspec

from lint_utils.common.std import report_error


class Base(
    msgspec.Struct,
    omit_defaults=True,
    forbid_unknown_fields=False,
):
    pass


_T = TypeVar("_T", bound=Base)


class LintConfig(Base):
    ignore: list[str] = msgspec.field(default_factory=list)


class LintUtilsConfig(Base, rename="kebab"):
    lint: LintConfig = msgspec.field(default_factory=LintConfig)
    exclude: list[str] = msgspec.field(default_factory=list)
    exclude_classes: Mapping[str, list[str]] = msgspec.field(default_factory=dict)
    exclude_base_classes: Mapping[str, list[str]] = msgspec.field(default_factory=dict)

    @classmethod
    def from_toml(cls, path: Path) -> "LintUtilsConfig | None":
        tool = _from_toml(Tool, path=path)
        if tool is None:
            return None

        return tool.lint_utils


class Tool(Base, rename="kebab"):
    lint_utils: LintUtilsConfig | None = None


class PyProject(Base):
    tool: Tool | None = None

    @classmethod
    def from_toml(cls, path: Path) -> "PyProject | None":
        return _from_toml(PyProject, path=path)


def _from_toml(model: type[_T], *, path: Path) -> _T | None:
    try:
        with path.open("r", encoding="UTF-8") as file:
            return msgspec.toml.decode(file.read(), type=model)
    except OSError as exc:
        if isinstance(exc, FileNotFoundError):
            return None

        msg = f"There was a problem parsing the file {path.name}. Error: {exc!r}"
        report_error(msg)

    return None
