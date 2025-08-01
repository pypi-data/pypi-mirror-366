def to_red(text: str) -> str:
    return f"\033[31m{text}\033[0m"


def to_cyan(text: str) -> str:
    return f"\033[36m{text}\033[0m"


def to_green(text: str) -> str:
    return f"\033[32m{text}\033[0m"


def to_bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def pluralize(count: int, singular: str, *, plural: str | None = None) -> str:
    if count == 1:
        return singular

    return f"{plural or singular + 's'}"
