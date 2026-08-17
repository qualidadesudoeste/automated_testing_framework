"""Operadores declarativos seguros compartilhados por regras e APIs."""

from __future__ import annotations

import operator
import re
from typing import Any, Callable


OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "contains": lambda actual, expected: expected in actual,
    "not_contains": lambda actual, expected: expected not in actual,
    "is_true": lambda actual, _expected: actual is True,
    "is_false": lambda actual, _expected: actual is False,
    "exists": lambda actual, _expected: actual is not None,
    "matches": lambda actual, expected: re.search(str(expected), str(actual)) is not None,
    "starts_with": lambda actual, expected: str(actual).startswith(str(expected)),
    "ends_with": lambda actual, expected: str(actual).endswith(str(expected)),
    "between": lambda actual, expected: expected[0] <= actual <= expected[1],
    "length_eq": lambda actual, expected: len(actual) == int(expected),
    "is_null": lambda actual, _expected: actual is None,
    "not_null": lambda actual, _expected: actual is not None,
    "sorted_asc": lambda actual, _expected: list(actual) == sorted(actual),
    "sorted_desc": lambda actual, _expected: list(actual) == sorted(actual, reverse=True),
    "unique": lambda actual, _expected: len(actual) == len(set(actual)),
}


def resolve(value: Any, path: str) -> tuple[bool, Any]:
    current = value
    if not path:
        return False, current
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return True, None
    return False, current

