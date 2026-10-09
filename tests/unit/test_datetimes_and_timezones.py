from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from TimeTravel.datetimes import parse_datetime
from TimeTravel.exceptions import InvalidDateTimeError, InvalidTimezoneError
from TimeTravel.timezones import resolve_timezone


def test_parse_aware_datetime_keeps_zone() -> None:
    value = parse_datetime("2026-01-01T10:00:00+00:00", default_tz=ZoneInfo("Asia/Kolkata"))
    assert value.hour == 10
    assert value.utcoffset().total_seconds() == 0
    assert value.tzinfo is not ZoneInfo("Asia/Kolkata")


def test_parse_naive_datetime_uses_default_tz() -> None:
    value = parse_datetime("2026-01-01T10:00:00", default_tz=ZoneInfo("Asia/Kolkata"))
    assert value.tzinfo == ZoneInfo("Asia/Kolkata")
    assert value.hour == 10


def test_parse_date_only() -> None:
    value = parse_datetime("2026-01-01", default_tz=ZoneInfo("UTC"))
    assert value == datetime(2026, 1, 1, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_parse_space_separator() -> None:
    value = parse_datetime("2026-01-01 10:00:00", default_tz=ZoneInfo("UTC"))
    assert value.hour == 10


def test_parse_invalid_datetime() -> None:
    with pytest.raises(InvalidDateTimeError):
        parse_datetime("not-a-date", default_tz=ZoneInfo("UTC"))


def test_resolve_timezone() -> None:
    assert resolve_timezone("America/New_York").key == "America/New_York"


def test_resolve_timezone_invalid() -> None:
    with pytest.raises(InvalidTimezoneError):
        resolve_timezone("Not/AZone")


def test_dst_spring_forward_offset_preserved_for_aware_input() -> None:
    # America/New_York 2026-03-08 02:30 does not exist locally; fromisoformat with
    # an explicit offset must not be reinterpreted.
    value = parse_datetime(
        "2026-03-08T02:30:00-05:00", default_tz=ZoneInfo("America/New_York")
    )
    assert value.utcoffset().total_seconds() == -5 * 3600
