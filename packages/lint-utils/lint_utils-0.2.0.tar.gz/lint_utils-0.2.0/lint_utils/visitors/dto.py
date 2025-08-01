from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class FileInfoDTO:
    source_code_lines: list[str]
    path: Path
