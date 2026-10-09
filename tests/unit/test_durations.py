from __future__ import annotations

from datetime import timedelta

import pytest

from TimeTravel.durations import parse_duration
from TimeTravel.exceptions import InvalidDurationError


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("30 seconds", timedelta(seconds=30)),
        ("5 minutes", timedelta(minutes=5)),
        ("2 hours", timedelta(hours=2)),
        ("31 days", timedelta(days=31)),
        ("1 week", timedelta(weeks=1)),
        ("1 day 6 hours", timedelta(days=1, hours=6)),
        ("1.5 hours", timedelta(hours=1.5)),
        ("-2 hours", timedelta(hours=-2)),
        ("+10 minutes", timedelta(minutes=10)),
    ],
)
def test_parse_duration_valid(text: str, expected: timedelta) -> None:
    assert parse_duration(text) == expected


def test_parse_duration_rejects_zero() -> None:
    with pytest.raises(InvalidDurationError, match="non-zero"):
        parse_duration("0 seconds")


def test_parse_duration_rejects_unknown_unit() -> None:
    with pytest.raises(InvalidDurationError, match="Unsupported duration unit"):
        parse_duration("2 months")


def test_parse_duration_rejects_garbage() -> None:
    with pytest.raises(InvalidDurationError):
        parse_duration("soon")


def test_parse_duration_disallow_negative() -> None:
    with pytest.raises(InvalidDurationError, match="Negative"):
        parse_duration("-1 minute", allow_negative=False)


def test_parse_duration_accepts_timedelta() -> None:
    assert parse_duration(timedelta(seconds=3)) == timedelta(seconds=3)
