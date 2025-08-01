from contextlib import suppress
from pathlib import Path


def open_file(file_path: Path) -> str | None:
    with (
        suppress(SyntaxError, OSError, UnicodeDecodeError),
        file_path.open("r", encoding="UTF-8") as file,
    ):
        return file.read()

    return None
