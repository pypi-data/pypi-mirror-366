from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class CheckResult:
    files_count: int
    errors_files_count: int
    not_processed_files: list[str]
