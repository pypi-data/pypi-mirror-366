import re
from types import SimpleNamespace

from lint_utils.regex import LU_PATTERN


class Rule(SimpleNamespace):
    useless_field = "USL001"
    remind_later = "RL001"


def can_ignore_rule(code_lines: list[str], line_number: int, rule: str) -> bool:
    code_line = code_lines[line_number]

    match = re.search(LU_PATTERN, code_line)
    codes: tuple[str, ...] = ()
    if match:
        codes = tuple(str(code).strip() for code in match.group(1).split(","))

    return rule in codes and rule != Rule.remind_later
