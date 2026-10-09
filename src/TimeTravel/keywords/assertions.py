"""Assertion keywords for simulated time."""

from __future__ import annotations

from datetime import timezone
from typing import TYPE_CHECKING, Any

from robot.api import logger
from robot.api.deco import keyword

from TimeTravel.datetimes import parse_datetime
from TimeTravel.durations import parse_duration
from TimeTravel.exceptions import TimeTravelError

if TYPE_CHECKING:
    from TimeTravel.library import TimeTravel


class AssertionKeywords:
    """Readable assertions for expiry and scheduling checks."""

    def __init__(self, ctx: TimeTravel) -> None:
        self.ctx = ctx

    @keyword("Simulated Time Should Be")
    def simulated_time_should_be(self, expected: str) -> None:
        """Fail unless the current simulated instant equals `expected`.

        Comparison is performed on absolute UTC instants.

        Args:
            expected: Expected ISO-8601 datetime.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time                  2026-01-01T10:00:00+00:00
            Simulated Time Should Be     2026-01-01T10:00:00+00:00
        ```
        """
        actual = self.ctx.clock.now().astimezone(timezone.utc)
        expected_dt = parse_datetime(
            expected, default_tz=self.ctx.clock.interpretation_timezone
        ).astimezone(timezone.utc)
        if actual.replace(microsecond=0) != expected_dt.replace(microsecond=0):
            raise TimeTravelError(
                f"Simulated time should be {expected_dt.isoformat()}, "
                f"got {actual.isoformat()}."
            )
        logger.info(f"Simulated time is {actual.isoformat()} as expected")

    @keyword("Simulated Time Should Be After")
    def simulated_time_should_be_after(self, expected: str) -> None:
        """Fail unless the current simulated instant is strictly after `expected`.

        Args:
            expected: ISO-8601 datetime that must be earlier than now.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time                       2026-01-01T10:00:00+00:00
            Advance Time                      5 minutes
            Simulated Time Should Be After    2026-01-01T10:00:00+00:00
        ```
        """
        actual = self.ctx.clock.now().astimezone(timezone.utc)
        expected_dt = parse_datetime(
            expected, default_tz=self.ctx.clock.interpretation_timezone
        ).astimezone(timezone.utc)
        if not actual > expected_dt:
            raise TimeTravelError(
                f"Simulated time should be after {expected_dt.isoformat()}, "
                f"got {actual.isoformat()}."
            )

    @keyword("Simulated Time Should Be Before")
    def simulated_time_should_be_before(self, expected: str) -> None:
        """Fail unless the current simulated instant is strictly before `expected`.

        Args:
            expected: ISO-8601 datetime that must be later than now.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time                        2026-01-01T10:00:00+00:00
            Simulated Time Should Be Before    2026-01-01T11:00:00+00:00
        ```
        """
        actual = self.ctx.clock.now().astimezone(timezone.utc)
        expected_dt = parse_datetime(
            expected, default_tz=self.ctx.clock.interpretation_timezone
        ).astimezone(timezone.utc)
        if not actual < expected_dt:
            raise TimeTravelError(
                f"Simulated time should be before {expected_dt.isoformat()}, "
                f"got {actual.isoformat()}."
            )

    @keyword("Simulated Timestamp Should Equal")
    def simulated_timestamp_should_equal(
        self, expected: Any, tolerance: str = "0 seconds"
    ) -> None:
        """Fail unless the simulated Unix timestamp equals `expected` within `tolerance`.

        Args:
            expected: Expected Unix timestamp.
            tolerance: Allowed absolute difference, for example `1 seconds`.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time                         2026-01-01T10:00:00+00:00
            ${ts}=                              Get Current Simulated Timestamp
            Simulated Timestamp Should Equal    ${ts}
            Simulated Timestamp Should Equal    ${ts}    tolerance=1 seconds
        ```
        """
        try:
            expected_ts = float(expected)
        except (TypeError, ValueError) as exc:
            raise TimeTravelError(
                f"Expected timestamp must be a number, got {expected!r}."
            ) from exc
        delta = parse_duration(tolerance, allow_negative=False, allow_zero=True)
        actual = self.ctx.clock.timestamp()
        if abs(actual - expected_ts) > delta.total_seconds():
            raise TimeTravelError(
                f"Simulated timestamp {actual} is not within {tolerance} of {expected_ts}."
            )

    @keyword("Time Until Should Be")
    def time_until_should_be(
        self, target: str, expected_duration: str, tolerance: str = "1 seconds"
    ) -> None:
        """Fail unless the duration from now until `target` matches `expected_duration`.

        Useful for asserting remaining TTL / cooldown windows.

        Args:
            target: Future (or past) ISO-8601 datetime.
            expected_duration: Expected duration until `target`.
            tolerance: Allowed difference from `expected_duration`.

        Examples:

        ```robotframework
        *** Settings ***
        Library    TimeTravel

        *** Test Cases ***
        Example
            Freeze Time             2026-01-01T10:00:00+00:00
            Time Until Should Be    2026-01-01T10:05:00+00:00    5 minutes
            Time Until Should Be    2026-01-01T10:05:00+00:00    5 minutes    tolerance=0 seconds
        ```
        """
        now = self.ctx.clock.now().astimezone(timezone.utc)
        target_dt = parse_datetime(
            target, default_tz=self.ctx.clock.interpretation_timezone
        ).astimezone(timezone.utc)
        actual_seconds = (target_dt - now).total_seconds()
        expected_seconds = parse_duration(
            expected_duration, allow_negative=True, allow_zero=True
        ).total_seconds()
        tol_seconds = parse_duration(
            tolerance, allow_negative=False, allow_zero=True
        ).total_seconds()
        if abs(actual_seconds - expected_seconds) > tol_seconds:
            raise TimeTravelError(
                f"Time until {target} is {actual_seconds} seconds, "
                f"expected {expected_seconds} seconds (±{tol_seconds})."
            )

    @keyword("Fail If Time Travel Is Active")
    def fail_if_time_travel_is_active(self) -> None:
        """Fail when a simulated clock is still active.

        Handy in suite teardown to catch cleanup leaks when auto-reset is disabled.

        Examples:

        ```robotframework
        *** Settings ***
        Library           TimeTravel    auto_reset=${False}
        Suite Teardown    Fail If Time Travel Is Active

        *** Test Cases ***
        Example
            [Teardown]    Reset Time
            Freeze Time    2026-01-01T10:00:00+00:00
        ```
        """
        if self.ctx.clock.active:
            raise TimeTravelError(
                f"Expected real time, but clock mode is '{self.ctx.clock.mode.value}'."
            )
