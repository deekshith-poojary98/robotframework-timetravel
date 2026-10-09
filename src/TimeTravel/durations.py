"""Duration parsing for Robot Framework keyword arguments."""

from __future__ import annotations

import re
from datetime import timedelta

from TimeTravel.exceptions import InvalidDurationError

_UNIT_SECONDS: dict[str, int] = {
    "second": 1,
    "seconds": 1,
    "minute": 60,
    "minutes": 60,
    "hour": 3600,
    "hours": 3600,
    "day": 86400,
    "days": 86400,
    "week": 604800,
    "weeks": 604800,
}

_TOKEN_RE = re.compile(
    r"^\s*(?P<sign>[+-])?\s*"
    r"(?P<body>(?:\d+(?:\.\d+)?)\s*[A-Za-z]+(?:\s+(?:\d+(?:\.\d+)?)\s*[A-Za-z]+)*)\s*$"
)
_PART_RE = re.compile(r"(\d+(?:\.\d+)?)\s*([A-Za-z]+)")


def parse_duration(
    value: str | timedelta,
    *,
    allow_negative: bool = True,
    allow_zero: bool = False,
) -> timedelta:
    """Parse a duration string such as ``5 minutes`` or ``1 day 6 hours``.

    Accepted units: seconds, minutes, hours, days, weeks (singular or plural).
    Months and years are rejected because their lengths are calendar-dependent.
    """
    if isinstance(value, timedelta):
        if not allow_negative and value.total_seconds() < 0:
            raise InvalidDurationError("Negative durations are not allowed for this operation.")
        if not allow_zero and value.total_seconds() == 0:
            raise InvalidDurationError("Duration must be non-zero.")
        return value

    if not isinstance(value, str) or not value.strip():
        raise InvalidDurationError(
            f"Duration must be a non-empty string such as '5 minutes', got {value!r}."
        )

    match = _TOKEN_RE.match(value)
    if match is None:
        raise InvalidDurationError(
            f"Invalid duration {value!r}. "
            "Use forms like '30 seconds', '5 minutes', '2 hours', '31 days', or '1 day 6 hours'."
        )

    sign = -1 if match.group("sign") == "-" else 1
    body = match.group("body")
    parts = _PART_RE.findall(body)
    consumed = "".join(f"{amount}{unit}" for amount, unit in parts)
    normalized_body = re.sub(r"\s+", "", body)
    if not parts or consumed != normalized_body:
        raise InvalidDurationError(
            f"Invalid duration {value!r}. "
            "Use forms like '30 seconds', '5 minutes', '2 hours', '31 days', or '1 day 6 hours'."
        )

    total_seconds = 0.0
    for amount_text, unit_text in parts:
        unit = unit_text.lower()
        if unit not in _UNIT_SECONDS:
            raise InvalidDurationError(
                f"Unsupported duration unit {unit_text!r} in {value!r}. "
                "Supported units: seconds, minutes, hours, days, weeks."
            )
        total_seconds += float(amount_text) * _UNIT_SECONDS[unit]

    if total_seconds == 0 and not allow_zero:
        raise InvalidDurationError(f"Duration must be non-zero, got {value!r}.")

    delta = timedelta(seconds=sign * total_seconds)
    if not allow_negative and delta.total_seconds() < 0:
        raise InvalidDurationError(
            f"Negative durations are not allowed for this operation, got {value!r}."
        )
    return delta
