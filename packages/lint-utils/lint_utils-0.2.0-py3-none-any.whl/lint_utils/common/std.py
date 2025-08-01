import sys


def report_error(message: str) -> None:
    sys.stderr.write(f"{message}\n")


def report_info(message: str) -> None:
    sys.stdout.write(f"{message}\n")
