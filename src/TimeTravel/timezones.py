"""Timezone helpers."""

from __future__ import annotations

from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from TimeTravel.exceptions import InvalidTimezoneError


def resolve_timezone(name: str) -> ZoneInfo:
    """Resolve an IANA timezone identifier such as ``UTC`` or ``Asia/Kolkata``."""
    if not isinstance(name, str) or not name.strip():
        raise InvalidTimezoneError(
            f"Timezone must be a non-empty IANA name such as 'UTC' or 'Asia/Kolkata', got {name!r}."
        )
    try:
        return ZoneInfo(name.strip())
    except ZoneInfoNotFoundError as exc:
        raise InvalidTimezoneError(
            f"Unknown timezone {name!r}. Use an IANA identifier such as "
            "'UTC', 'Asia/Kolkata', or 'America/New_York'."
        ) from exc


def timezone_name(tz: tzinfo) -> str:
    """Return a stable name for a timezone object when available."""
    key = getattr(tz, "key", None)
    if isinstance(key, str):
        return key
    if tz is not None and str(tz) == "UTC":
        return "UTC"
    return str(tz)


def ensure_aware(value: datetime, default_tz: ZoneInfo) -> datetime:
    """Attach ``default_tz`` to naive datetimes; leave aware datetimes unchanged."""
    if value.tzinfo is None:
        return value.replace(tzinfo=default_tz)
    return value
