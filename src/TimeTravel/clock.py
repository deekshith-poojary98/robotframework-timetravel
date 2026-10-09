"""Internal clock controller backed by ``time-machine``."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import time_machine

from TimeTravel.exceptions import ClockStateError, InvalidDateTimeError
from TimeTravel.timezones import resolve_timezone, timezone_name


class ClockMode(str, Enum):
    IDLE = "idle"
    FROZEN = "frozen"
    TICKING = "ticking"


class ClockController:
    """Manage a single process-local time-machine traveller.

    Lifecycle rules
    ---------------
    * ``freeze`` / ``start_ticking`` while already active replace the current
      simulated instant and mode (previous traveller is stopped first).
    * ``travel_to`` while idle starts a frozen clock at the destination.
    * ``travel_to`` while active replaces the simulated instant and keeps the
      current mode unless ``tick`` is provided.
    * ``pause`` / ``resume`` toggle frozen vs ticking at the current instant.
    * ``shift`` / advance / rewind require an active clock.
    * ``reset`` restores real time and is safe to call repeatedly.
    """

    def __init__(self) -> None:
        self._travel: time_machine.travel | None = None
        self._traveller: time_machine.Traveller | None = None
        self._mode: ClockMode = ClockMode.IDLE
        self._interpretation_tz: ZoneInfo = ZoneInfo("UTC")

    @property
    def mode(self) -> ClockMode:
        return self._mode

    @property
    def active(self) -> bool:
        return self._mode is not ClockMode.IDLE

    @property
    def interpretation_timezone(self) -> ZoneInfo:
        return self._interpretation_tz

    def set_timezone(self, name: str) -> str:
        self._interpretation_tz = resolve_timezone(name)
        return timezone_name(self._interpretation_tz)

    def get_timezone(self) -> str:
        return timezone_name(self._interpretation_tz)

    def freeze(self, when: datetime) -> datetime:
        return self._start(when, tick=False)

    def freeze_at_timestamp(self, timestamp: float) -> datetime:
        return self._start_from_timestamp(timestamp, tick=False)

    def start_ticking(self, when: datetime) -> datetime:
        return self._start(when, tick=True)

    def start_ticking_at_timestamp(self, timestamp: float) -> datetime:
        return self._start_from_timestamp(timestamp, tick=True)

    def freeze_at_real_time(self) -> datetime:
        return self.freeze(self.real_now())

    def travel_to(self, when: datetime, *, tick: bool | None = None) -> datetime:
        if not self.active or self._traveller is None:
            if tick is True:
                return self.start_ticking(when)
            return self.freeze(when)
        use_tick = self._mode is ClockMode.TICKING if tick is None else tick
        self._traveller.move_to(when, tick=use_tick)
        self._mode = ClockMode.TICKING if use_tick else ClockMode.FROZEN
        return self.now()

    def travel_to_timestamp(self, timestamp: float, *, tick: bool | None = None) -> datetime:
        when = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return self.travel_to(when, tick=tick)

    def pause(self) -> datetime:
        self._require_active("Pause Time")
        return self.travel_to(self._current_destination_datetime(), tick=False)

    def resume_ticking(self) -> datetime:
        self._require_active("Resume Ticking Time")
        return self.travel_to(self._current_destination_datetime(), tick=True)

    def shift(self, delta: timedelta) -> datetime:
        self._require_active("Shift Time")
        assert self._traveller is not None
        self._traveller.shift(delta)
        return self.now()

    def advance_to_next_weekday(self, weekday: str, *, keep_time: bool = True) -> datetime:
        """Move forward to the next matching weekday (never stays on today)."""
        self._require_active("Advance To Next Weekday")
        target_wd = _parse_weekday(weekday)
        current = self.now()
        days_ahead = (target_wd - current.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        destination = current + timedelta(days=days_ahead)
        if not keep_time:
            destination = destination.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.travel_to(destination)

    def now(self) -> datetime:
        """Return the perceived current time in the interpretation timezone."""
        current = datetime.now(timezone.utc)
        return current.astimezone(self._interpretation_tz)

    def now_in(self, timezone_name_value: str) -> datetime:
        return datetime.now(timezone.utc).astimezone(resolve_timezone(timezone_name_value))

    def timestamp(self) -> float:
        return datetime.now(timezone.utc).timestamp()

    def timestamp_ns(self) -> int:
        if self._traveller is not None:
            return self._traveller.time_ns()
        import time

        return time.time_ns()

    def real_now(self) -> datetime:
        if time_machine.escape_hatch.is_travelling():
            return time_machine.escape_hatch.datetime.datetime.now(timezone.utc).astimezone(
                self._interpretation_tz
            )
        return datetime.now(timezone.utc).astimezone(self._interpretation_tz)

    def real_timestamp(self) -> float:
        if time_machine.escape_hatch.is_travelling():
            return float(time_machine.escape_hatch.time.time())
        return datetime.now(timezone.utc).timestamp()

    def is_travelling(self) -> bool:
        return bool(time_machine.escape_hatch.is_travelling()) or self.active

    def reset(self) -> None:
        """Stop the simulated clock and restore default interpretation timezone."""
        self.stop_clock()
        self._interpretation_tz = ZoneInfo("UTC")

    def stop_clock(self) -> None:
        """Stop the simulated clock without changing the interpretation timezone."""
        if self._travel is not None:
            try:
                self._travel.stop()
            except IndexError:
                pass
        self._travel = None
        self._traveller = None
        self._mode = ClockMode.IDLE

    def _start(self, when: datetime, *, tick: bool) -> datetime:
        if when.tzinfo is None:
            raise ClockStateError("Clock destinations must be timezone-aware.")
        self.stop_clock()
        travel = time_machine.travel(when, tick=tick)
        self._traveller = travel.start()
        self._travel = travel
        self._mode = ClockMode.TICKING if tick else ClockMode.FROZEN
        return self.now()

    def _start_from_timestamp(self, timestamp: float, *, tick: bool) -> datetime:
        if not isinstance(timestamp, (int, float)):
            raise InvalidDateTimeError(f"Timestamp must be a number, got {timestamp!r}.")
        when = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        return self._start(when, tick=tick)

    def _current_destination_datetime(self) -> datetime:
        """Current simulated instant, keeping time-machine's destination TZ name."""
        assert self._traveller is not None
        current_utc = datetime.now(timezone.utc)
        tzname = getattr(self._traveller, "_destination_tzname", None)
        if isinstance(tzname, str) and tzname:
            try:
                return current_utc.astimezone(ZoneInfo(tzname))
            except ZoneInfoNotFoundError:
                pass
        return current_utc

    def _require_active(self, operation: str) -> None:
        if not self.active:
            raise ClockStateError(
                f"{operation} requires an active simulated clock. "
                "Call 'Freeze Time', 'Travel To Time', or 'Start Ticking Time' first."
            )


_WEEKDAYS = {
    "mon": 0,
    "monday": 0,
    "tue": 1,
    "tues": 1,
    "tuesday": 1,
    "wed": 2,
    "wednesday": 2,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "thursday": 3,
    "fri": 4,
    "friday": 4,
    "sat": 5,
    "saturday": 5,
    "sun": 6,
    "sunday": 6,
}


def _parse_weekday(value: str) -> int:
    key = value.strip().lower()
    if key not in _WEEKDAYS:
        raise InvalidDateTimeError(
            f"Invalid weekday {value!r}. Use names like 'Monday' or abbreviations like 'Mon'."
        )
    return _WEEKDAYS[key]
