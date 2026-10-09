"""Timezone and calendar helper keywords for TimeTravel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from robot.api import logger
from robot.api.deco import keyword

from TimeTravel.datetimes import format_datetime, parse_datetime
from TimeTravel.timezones import resolve_timezone

if TYPE_CHECKING:
    from TimeTravel.library import TimeTravel


class TimezoneControlKeywords:
    """Keywords for timezone configuration and datetime presentation helpers."""

    def __init__(self, ctx: TimeTravel) -> None:
        self.ctx = ctx

    @keyword("Set Timezone")
    def set_timezone(self, timezone: str) -> str:
        """Configure the timezone used to interpret naive datetime inputs.

        Accepts IANA identifiers such as `UTC`, `Asia/Kolkata`, or
        `America/New_York`.

        This does not by itself claim to change the operating-system timezone.
        When freezing or traveling to a timezone-aware instant with a named
        zone, the `time-machine` backend may temporarily set process `TZ`
        while the clock is active.

        Args:
            timezone: IANA timezone name.

        Returns:
            The configured timezone name.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Set Timezone    Asia/Kolkata
            Set Timezone    America/New_York
        ```
        """
        name = self.ctx.clock.set_timezone(timezone)
        logger.info(f"Set interpretation timezone to {name}")
        return name

    @keyword("Get Current Timezone")
    def get_current_timezone(self) -> str:
        """Return the configured interpretation timezone.

        Returns:
            Current interpretation timezone name.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Set Timezone    Asia/Kolkata
            ${tz}=          Get Current Timezone
        ```
        """
        return self.ctx.clock.get_timezone()

    @keyword("Convert Datetime To Timezone")
    def convert_datetime_to_timezone(self, value: str, timezone: str) -> str:
        """Convert an ISO-8601 datetime into `timezone` and return ISO-8601.

        Aware inputs keep their absolute instant. Naive inputs are interpreted
        using the library's configured interpretation timezone first.

        Args:
            value: ISO-8601 datetime string.
            timezone: Target IANA timezone name.

        Returns:
            Converted ISO-8601 datetime string.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            ${ny}=    Convert Datetime To Timezone    2026-01-01T00:00:00+00:00    America/New_York
        ```
        """
        when = parse_datetime(value, default_tz=self.ctx.clock.interpretation_timezone)
        converted = when.astimezone(resolve_timezone(timezone))
        return format_datetime(converted)

    @keyword("Get Current Simulated Time In Timezone")
    def get_current_simulated_time_in_timezone(self, timezone: str) -> str:
        """Return the current simulated instant expressed in `timezone`.

        Does not change the configured interpretation timezone.

        Args:
            timezone: IANA timezone name used for presentation.

        Returns:
            Simulated datetime in the requested timezone.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T00:00:00+00:00
            ${local}=      Get Current Simulated Time In Timezone    Asia/Kolkata
        ```
        """
        return format_datetime(self.ctx.clock.now_in(timezone))

    @keyword("Format Simulated Time")
    def format_simulated_time(self, format: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
        """Format the current simulated time with `strftime` `format`.

        Args:
            format: `strftime` format string.

        Returns:
            Formatted simulated time.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${text}=       Format Simulated Time
            ${text}=       Format Simulated Time    %A %Y-%m-%d
        ```
        """
        return self.ctx.clock.now().strftime(format)

    @keyword("Get Simulated Weekday")
    def get_simulated_weekday(self) -> str:
        """Return the English weekday name for the current simulated time.

        Returns:
            Weekday name such as `Thursday`.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time    2026-01-01T10:00:00+00:00
            ${day}=        Get Simulated Weekday
        ```
        """
        return self.ctx.clock.now().strftime("%A")
