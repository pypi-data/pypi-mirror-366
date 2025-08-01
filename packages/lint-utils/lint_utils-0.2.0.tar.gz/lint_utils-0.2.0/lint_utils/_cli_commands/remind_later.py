from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from lint_utils.common.files import open_file
from lint_utils.common.std import report_info
from lint_utils.common.text_styling import to_bold, to_cyan, to_red
from lint_utils.config import LintUtilsConfig
from lint_utils.regex import DATE_PATTERN, LU_PATTERN
from lint_utils.rules import Rule

from .abc_ import BaseCommand
from .dto import CheckResult


@dataclass(frozen=True, slots=True, kw_only=True)
class _OverdueInfo:
    line_number: int
    overdue_date: date
    message: str | None = None


class RemindLaterCommand(BaseCommand):
    rule = Rule.remind_later

    def __init__(
        self,
        paths: Iterable[Path],
        config: LintUtilsConfig | None,
    ) -> None:
        self._paths = paths
        self._config = config

    def execute(self) -> CheckResult:
        files_count = 0
        errors_files_count = 0
        not_processed_files: list[str] = []
        today = datetime.now().astimezone().date()

        for path in self._paths:
            source = open_file(path)
            if source is None:
                not_processed_files.append(path.as_posix())
                continue

            infos = self._check_remind_later_rule(source, date_=today)
            self._report(infos, file_path=path)

            if infos:
                errors_files_count += 1

            files_count += 1

        return CheckResult(
            files_count=files_count,
            errors_files_count=errors_files_count,
            not_processed_files=not_processed_files,
        )

    def _check_remind_later_rule(
        self,
        source: str,
        *,
        date_: date,
    ) -> Sequence[_OverdueInfo]:
        results: list[_OverdueInfo] = []
        lines = source.split("\n")
        for number, line in enumerate(lines, start=1):
            if not (match := LU_PATTERN.search(line)):
                continue

            if self.rule not in match.group() or (
                not (raw_date_matches := DATE_PATTERN.search(line))
            ):
                continue

            if (
                (raw_date := raw_date_matches.group(1)) is None
                or ((overdue_date := _parse_date(raw_date)) is None)
                or overdue_date >= date_
            ):
                continue

            splitted = line.split("]:", maxsplit=1)
            message = splitted[1] if splitted else None
            results.append(
                _OverdueInfo(
                    overdue_date=overdue_date,
                    line_number=number,
                    message=message,
                )
            )

        return results

    def _report(self, infos: Sequence[_OverdueInfo], file_path: Path) -> None:
        if not infos:
            return

        msg = f"{to_bold(to_cyan(self.rule))} {to_bold('The reminder has expired')}"
        report_info(msg)

        for info in infos:
            full_path = f"{file_path.as_posix()}:{info.line_number}"
            parts = (
                full_path,
                f'"{to_bold(info.message.strip())}"' if info.message else None,
                to_bold(to_red(info.overdue_date.isoformat())),
            )
            line_msg = " ".join(part.strip() for part in parts if part)
            report_info(line_msg)
        report_info("")


def _parse_date(raw_date: str) -> date | None:
    try:
        return date.fromisoformat(raw_date)
    except ValueError:
        return None
