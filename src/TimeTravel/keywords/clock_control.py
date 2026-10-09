"""Clock-control keywords for TimeTravel."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from robot.api import logger
from robot.api.deco import keyword

from TimeTravel.datetimes import format_datetime, parse_datetime
from TimeTravel.durations import parse_duration
from TimeTravel.exceptions import InvalidDateTimeError, TimeTravelError

if TYPE_CHECKING:
    from TimeTravel.library import TimeTravel


class ClockControlKeywords:
    """Keywords for freezing, traveling, and shifting simulated time."""

    def __init__(self, ctx: TimeTravel) -> None:
        self.ctx = ctx

    @keyword("Freeze Time")
    def freeze_time(self, at: str) -> str:
        """Freeze perceived time at `at`.

        `at` is an ISO-8601 datetime or date. Naive values are interpreted in
        the timezone configured by [Set Timezone] (default `UTC`).

        If a simulated clock is already active, it is replaced.

        Args:
            at: Destination datetime or date.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            Freeze Time    2026-01-01T10:00:00
        ```
        """
        when = self._parse_datetime(at)
        current = self.ctx.clock.freeze(when)
        logger.info(f"Froze time at {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Freeze At Timestamp")
    def freeze_at_timestamp(self, timestamp: Any) -> str:
        """Freeze perceived time at a Unix `timestamp` (seconds).

        Args:
            timestamp: Unix timestamp in seconds.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze At Timestamp    1767261600
        ```
        """
        current = self.ctx.clock.freeze_at_timestamp(self._parse_timestamp(timestamp))
        logger.info(f"Froze time at timestamp {timestamp} -> {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Freeze At Real Time")
    def freeze_at_real_time(self) -> str:
        """Freeze perceived time at the current real wall-clock instant.

        Uses `time-machine` escape hatch when already travelling so the
        destination is true wall time, not the simulated clock.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze At Real Time
        ```
        """
        current = self.ctx.clock.freeze_at_real_time()
        logger.info(f"Froze time at real wall clock {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Travel To Time")
    def travel_to_time(self, at: str) -> str:
        """Move the simulated clock to `at`.

        If no clock is active, starts a frozen clock at `at`.
        If a clock is already active, replaces the simulated instant and keeps
        the current frozen/ticking mode.

        Args:
            at: Destination datetime or date.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Travel To Time    2026-06-01T12:00:00+00:00
        ```
        """
        when = self._parse_datetime(at)
        current = self.ctx.clock.travel_to(when)
        logger.info(f"Traveled to {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Travel To Timestamp")
    def travel_to_timestamp(self, timestamp: Any) -> str:
        """Move the simulated clock to a Unix `timestamp` (seconds).

        Args:
            timestamp: Unix timestamp in seconds.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Travel To Timestamp    1767225600
        ```
        """
        current = self.ctx.clock.travel_to_timestamp(self._parse_timestamp(timestamp))
        logger.info(f"Traveled to timestamp {timestamp} -> {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Advance Time")
    def advance_time(self, duration: str) -> str:
        """Move the simulated clock forward by `duration`.

        Requires an active simulated clock. Duration must be non-negative.

        Args:
            duration: Non-negative duration such as `5 minutes`.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time     2026-01-01T10:00:00+00:00
            Advance Time    5 minutes
            Advance Time    1 day 6 hours
        ```
        """
        delta = parse_duration(duration, allow_negative=False)
        current = self.ctx.clock.shift(delta)
        logger.info(f"Advanced time by {duration} to {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Rewind Time")
    def rewind_time(self, duration: str) -> str:
        """Move the simulated clock backward by `duration`.

        Requires an active simulated clock. Duration must be non-negative; the
        clock moves backward by that amount.

        Args:
            duration: Non-negative duration such as `2 hours`.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            Rewind Time    2 hours
        ```
        """
        delta = parse_duration(duration, allow_negative=False)
        current = self.ctx.clock.shift(-delta)
        logger.info(f"Rewound time by {duration} to {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Shift Time")
    def shift_time(self, duration: str) -> str:
        """Move the simulated clock by a signed `duration`.

        Use a leading `-` to move backward, for example `-2 hours`.
        Requires an active simulated clock.

        Args:
            duration: Signed duration such as `-30 minutes` or `2 hours`.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            Shift Time     -30 minutes
            Shift Time     2 hours
        ```
        """
        delta = parse_duration(duration, allow_negative=True)
        current = self.ctx.clock.shift(delta)
        logger.info(f"Shifted time by {duration} to {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Start Ticking Time")
    def start_ticking_time(self, at: str) -> str:
        """Start simulated time at `at` and let it progress with real wall time.

        If a simulated clock is already active, it is replaced.

        Args:
            at: Destination datetime or date.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Start Ticking Time    2026-01-01T10:00:00+00:00
        ```
        """
        when = self._parse_datetime(at)
        current = self.ctx.clock.start_ticking(when)
        logger.info(f"Started ticking time at {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Pause Time")
    def pause_time(self) -> str:
        """Freeze the clock at the current simulated instant.

        Requires an active simulated clock. Equivalent to switching the
        `time-machine` traveller to `tick=False` at the current destination.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Start Ticking Time    2026-01-01T10:00:00+00:00
            Pause Time
        ```
        """
        current = self.ctx.clock.pause()
        logger.info(f"Paused time at {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Resume Ticking Time")
    def resume_ticking_time(self) -> str:
        """Resume natural ticking from the current simulated instant.

        Requires an active simulated clock.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time            2026-01-01T10:00:00+00:00
            Resume Ticking Time
        ```
        """
        current = self.ctx.clock.resume_ticking()
        logger.info(f"Resumed ticking at {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Advance To Next Weekday")
    def advance_to_next_weekday(self, weekday: str, keep_time: bool = True) -> str:
        """Advance to the next `weekday`, never staying on today.

        `weekday` accepts names like `Monday` or abbreviations like `Mon`.
        When `keep_time` is true (default), the current time-of-day is kept.
        When false, the destination is midnight in the interpretation timezone.

        Args:
            weekday: Target weekday name or abbreviation.
            keep_time: Keep the current time-of-day when `True`.

        Returns:
            The simulated datetime as an ISO-8601 string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time                2026-01-01T10:00:00+00:00
            Advance To Next Weekday    Monday
            Advance To Next Weekday    Friday    keep_time=${False}
        ```
        """
        keep = self.ctx._to_bool(keep_time, name="keep_time")
        current = self.ctx.clock.advance_to_next_weekday(weekday, keep_time=keep)
        logger.info(f"Advanced to next {weekday}: {format_datetime(current)}")
        return format_datetime(current)

    @keyword("Get Current Simulated Time")
    def get_current_simulated_time(self) -> str:
        """Return the perceived current datetime as an ISO-8601 string.

        The value is expressed in the configured interpretation timezone.

        Returns:
            ISO-8601 datetime string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${now}=        Get Current Simulated Time
        ```
        """
        return format_datetime(self.ctx.clock.now())

    @keyword("Get Current Simulated Timestamp")
    def get_current_simulated_timestamp(self) -> float:
        """Return the perceived current Unix timestamp in seconds.

        Returns:
            Unix timestamp in seconds.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${ts}=         Get Current Simulated Timestamp
        ```
        """
        return self.ctx.clock.timestamp()

    @keyword("Get Current Simulated Timestamp Ns")
    def get_current_simulated_timestamp_ns(self) -> int:
        """Return the perceived current Unix timestamp in nanoseconds.

        Returns:
            Unix timestamp in nanoseconds.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${ns}=         Get Current Simulated Timestamp Ns
        ```
        """
        return self.ctx.clock.timestamp_ns()

    @keyword("Get Clock Mode")
    def get_clock_mode(self) -> str:
        """Return the clock mode: `idle`, `frozen`, or `ticking`.

        Returns:
            Current clock mode.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${mode}=       Get Clock Mode
        ```
        """
        return self.ctx.clock.mode.value

    @keyword("Time Travel Is Active")
    def time_travel_is_active(self) -> bool:
        """Return `True` when a simulated clock is currently active.

        Returns:
            Whether time travel is active.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${active}=     Time Travel Is Active
        ```
        """
        return self.ctx.clock.active

    @keyword("Get Real Time")
    def get_real_time(self) -> str:
        """Return the real wall-clock datetime, even while time-travelling.

        Uses `time-machine` escape hatch when a traveller is active.

        Returns:
            Real wall-clock datetime as ISO-8601.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${real}=       Get Real Time
        ```
        """
        return format_datetime(self.ctx.clock.real_now())

    @keyword("Get Real Timestamp")
    def get_real_timestamp(self) -> float:
        """Return the real wall-clock Unix timestamp in seconds.

        Returns:
            Real wall-clock Unix timestamp.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${real_ts}=    Get Real Timestamp
        ```
        """
        return self.ctx.clock.real_timestamp()

    @keyword("Reset Time")
    def reset_time(self) -> None:
        """Restore real-time behavior and release active clock control.

        Also restores the interpretation timezone to `UTC`.

        Safe to call multiple times. Does not restore an independent clock if
        other code in the same process is also manipulating time.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            [Teardown]    Reset Time
            Freeze Time     2026-01-01T10:00:00+00:00
            Advance Time    5 minutes
        ```
        """
        self.ctx.clock.reset()
        logger.info("Reset simulated time to real time")

    def _parse_datetime(self, value: str) -> datetime:
        try:
            return parse_datetime(value, default_tz=self.ctx.clock.interpretation_timezone)
        except TimeTravelError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise TimeTravelError(str(exc)) from exc

    @staticmethod
    def _parse_timestamp(value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise InvalidDateTimeError(f"Timestamp must be a number, got {value!r}.")
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise InvalidDateTimeError(f"Timestamp must be a number, got {value!r}.") from exc
