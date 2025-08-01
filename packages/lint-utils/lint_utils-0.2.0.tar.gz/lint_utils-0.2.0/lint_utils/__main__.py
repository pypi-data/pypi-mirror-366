import sys
from collections.abc import Sequence
from pathlib import Path

import click

from lint_utils._cli_commands.check import CheckCommand
from lint_utils._cli_commands.remind_later import RemindLaterCommand
from lint_utils.common.std import report_error, report_info
from lint_utils.common.text_styling import pluralize, to_bold, to_green, to_red
from lint_utils.common.timer import Timer
from lint_utils.config import LintUtilsConfig, PyProject


@click.group()
def cli() -> None:
    pass


@cli.command("check")
@click.argument("args", nargs=-1)
def check(args: Sequence[str]) -> None:  # noqa: C901
    config = _get_config()
    files_count = 0
    errors_files_count = 0
    not_processed_files: list[str] = []

    if not args:
        report_error(to_red("Please provide the file or directory name"))
        return

    commands = (CheckCommand, RemindLaterCommand)

    with Timer() as timer:
        for raw_path in args:
            root_path = Path(raw_path)
            if not root_path.exists():
                report_error(
                    to_bold(
                        to_red(
                            f'Directory of file with name "{root_path.as_posix()}" doesn\'t exists'
                        )
                    )
                )
                return

            paths = root_path.rglob("*.py") if root_path.is_dir() else (root_path,)
            for command_cls in commands:
                command = command_cls(paths=paths, config=config)
                if command.can_skip_command:
                    continue

                result = command.execute()

                not_processed_files.extend(result.not_processed_files)
                files_count += result.files_count
                errors_files_count += result.errors_files_count

    if errors_files_count > 0:
        files_part = pluralize(errors_files_count, "file")
        msg = to_bold(to_red(f"Errors found in {errors_files_count} {files_part} 😱"))
        report_error(msg)
    else:
        report_info(to_bold(to_green("No errors found. All is well 🤗")))

    total_info = f"Processed {files_count} {pluralize(files_count, 'file')} at {timer.total_seconds}"
    report_info(to_bold(total_info))

    if errors_files_count > 0:
        sys.exit(1)


def _report_config_warning(
    lint_utils_path: Path,
    pyproject_path: Path,
) -> None:
    report_info(
        f"""Got two configs: {to_bold(lint_utils_path.as_posix())}, {to_bold(pyproject_path.as_posix())}
Applied {to_bold(to_green(pyproject_path.as_posix()))}
"""
    )


def _get_config() -> LintUtilsConfig | None:
    lint_utils_path = Path("lint_utils.toml")
    lint_utils_config = LintUtilsConfig.from_toml(lint_utils_path)
    pyproject_path = Path("pyproject.toml")
    pyproject = PyProject.from_toml(pyproject_path)
    if (
        pyproject
        and pyproject.tool
        and (lint_utils := pyproject.tool.lint_utils) is not None
    ):
        if lint_utils_config:
            _report_config_warning(
                lint_utils_path=lint_utils_path,
                pyproject_path=pyproject_path,
            )
        return lint_utils

    return lint_utils_config


if __name__ == "__main__":
    cli()
