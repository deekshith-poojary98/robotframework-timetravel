"""Robot Framework library entry point for TimeTravel."""

from __future__ import annotations

import importlib.metadata
from typing import Any

from robotlibcore import HybridCore

from TimeTravel.clock import ClockController
from TimeTravel.exceptions import TimeTravelError
from TimeTravel.keywords.assertions import AssertionKeywords
from TimeTravel.keywords.clock_control import ClockControlKeywords
from TimeTravel.keywords.timezone_control import TimezoneControlKeywords

try:
    _PACKAGE_VERSION = importlib.metadata.version("robotframework-timetravel")
except importlib.metadata.PackageNotFoundError:  # pragma: no cover - editable/source use
    _PACKAGE_VERSION = "0.1.0"

__version__ = _PACKAGE_VERSION


class TimeTravel(HybridCore):
    """Robot Framework library for deterministic time control.

    `TimeTravel` uses [time-machine](https://github.com/adamchainz/time-machine)
    to manipulate Python-level time APIs in the current process and exposes
    readable keywords for freezing, traveling, advancing, rewinding, and
    timezone-aware datetime interpretation.

    This library does **not** change remote services, databases, browsers, or
    other processes.

    By default the library auto-resets simulated time at the end of every test
    so frozen clocks do not leak between tests. Pass `auto_reset=${False}` to
    disable that behavior and manage cleanup yourself with [Reset Time].

    Examples:

    ```robotframework
    *** Settings ***
    Library    TimeTravel

    *** Test Cases ***
    OTP Expires After Five Minutes
        [Teardown]    Reset Time
        Freeze Time       2026-01-01T10:00:00+00:00
        Advance Time      5 minutes
        Simulated Time Should Be    2026-01-01T10:05:00+00:00
    ```
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_VERSION = _PACKAGE_VERSION
    ROBOT_LIBRARY_DOC_FORMAT = "MARKDOWN"
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, auto_reset: bool = True) -> None:
        """Initialize the TimeTravel library.

        Args:
            auto_reset: When `True` (default), reset simulated time after each test.
        """
        self.auto_reset = self._to_bool(auto_reset, name="auto_reset")
        self.clock = ClockController()
        self.ROBOT_LIBRARY_LISTENER = self
        libraries = [
            ClockControlKeywords(self),
            TimezoneControlKeywords(self),
            AssertionKeywords(self),
        ]
        super().__init__(libraries)

    def end_test(self, data: Any, result: Any) -> None:
        """Listener hook: reset clock state after each test when enabled."""
        if self.auto_reset:
            self.clock.reset()

    def close(self) -> None:
        """Restore real time when the library goes out of scope."""
        self.clock.reset()

    def __enter__(self) -> TimeTravel:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            f"TimeTravel(version={self.ROBOT_LIBRARY_VERSION}, "
            f"mode={self.clock.mode.value}, timezone={self.clock.get_timezone()})"
        )

    @staticmethod
    def _to_bool(value: Any, *, name: str) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "on"}:
                return True
            if lowered in {"false", "0", "no", "off"}:
                return False
        raise TimeTravelError(f"Argument '{name}' must be a boolean, got {value!r}.")
