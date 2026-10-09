"""Datetime parsing and formatting helpers."""

from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from TimeTravel.exceptions import InvalidDateTimeError
from TimeTravel.timezones import ensure_aware


def parse_datetime(value: str | datetime | date, *, default_tz: ZoneInfo) -> datetime:
    """Parse an ISO-8601 datetime or date into a timezone-aware ``datetime``.

    Naive values are interpreted in ``default_tz``. Aware values keep their own
    timezone and are not silently reinterpreted.
    """
    if isinstance(value, datetime):
        return ensure_aware(value, default_tz)
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day, tzinfo=default_tz)

    if not isinstance(value, str) or not value.strip():
        raise InvalidDateTimeError(
            f"Datetime must be a non-empty ISO-8601 string, got {value!r}."
        )

    text = value.strip()
    # Support a single space separator commonly used in tests.
    normalized = text.replace(" ", "T", 1) if "T" not in text and " " in text else text
    try:
        if len(normalized) == 10 and normalized[4] == "-" and normalized[7] == "-":
            parsed_date = date.fromisoformat(normalized)
            return datetime(
                parsed_date.year, parsed_date.month, parsed_date.day, tzinfo=default_tz
            )
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise InvalidDateTimeError(
            f"Invalid datetime {value!r}. Use ISO-8601 forms such as "
            "'2026-01-01T10:00:00+00:00', '2026-01-01T10:00:00', or '2026-01-01'."
        ) from exc

    return ensure_aware(parsed, default_tz)


def format_datetime(value: datetime) -> str:
    """Format an aware datetime as ISO-8601."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
