import re

LU_PATTERN = re.compile(r"lu:\s*([A-Z]+\d+(?:,\s*[A-Z]+\d+)*)")
DATE_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2})\]")
