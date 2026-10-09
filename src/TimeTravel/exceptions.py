"""Public exceptions for the TimeTravel library."""

from __future__ import annotations


class TimeTravelError(Exception):
    """Base error for invalid TimeTravel operations or inputs."""


class InvalidDurationError(TimeTravelError):
    """Raised when a duration string cannot be parsed."""


class InvalidDateTimeError(TimeTravelError):
    """Raised when a datetime string cannot be parsed."""


class InvalidTimezoneError(TimeTravelError):
    """Raised when a timezone identifier is not valid."""


class ClockStateError(TimeTravelError):
    """Raised when a keyword is used in an invalid clock lifecycle state."""
