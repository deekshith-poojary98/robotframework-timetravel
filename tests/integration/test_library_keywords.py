from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest

from TimeTravel import TimeTravel
from TimeTravel.exceptions import ClockStateError, InvalidDurationError, TimeTravelError


@pytest.fixture
def lib() -> TimeTravel:
    library = TimeTravel(auto_reset=False)
    yield library
    library.reset_time()


def test_freeze_advance_rewind_keywords(lib: TimeTravel) -> None:
    assert lib.freeze_time("2026-01-01T10:00:00+00:00").startswith("2026-01-01T10:00:00")
    assert lib.advance_time("5 minutes").startswith("2026-01-01T10:05:00")
    assert lib.rewind_time("5 minutes").startswith("2026-01-01T10:00:00")
    assert lib.shift_time("-1 hours").startswith("2026-01-01T09:00:00")


def test_travel_and_getters(lib: TimeTravel) -> None:
    lib.freeze_time("2026-01-01T10:00:00+00:00")
    lib.travel_to_time("2026-06-01T12:00:00+00:00")
    assert lib.get_current_simulated_time().startswith("2026-06-01T12:00:00")
    assert lib.get_current_simulated_timestamp() == datetime(
        2026, 6, 1, 12, tzinfo=timezone.utc
    ).timestamp()


def test_invalid_inputs(lib: TimeTravel) -> None:
    with pytest.raises(InvalidDurationError):
        lib.freeze_time("2026-01-01T10:00:00+00:00")
        lib.advance_time("two minutes")
    with pytest.raises(TimeTravelError):
        lib.freeze_time("yesterday")


def test_advance_before_start_fails(lib: TimeTravel) -> None:
    with pytest.raises(ClockStateError):
        lib.advance_time("1 minute")


def test_timezone_keywords(lib: TimeTravel) -> None:
    assert lib.set_timezone("Asia/Kolkata") == "Asia/Kolkata"
    assert lib.get_current_timezone() == "Asia/Kolkata"
    lib.freeze_time("2026-01-01T05:30:00")
    assert lib.get_current_simulated_time().startswith("2026-01-01T05:30:00")
    assert datetime.now(timezone.utc) == datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_listener_end_test_resets(lib: TimeTravel) -> None:
    auto = TimeTravel(auto_reset=True)
    auto.freeze_time("2026-01-01T10:00:00+00:00")
    auto.end_test(None, None)
    before = time.time()
    time.sleep(0.02)
    assert time.time() - before >= 0.015


def test_start_ticking_keyword(lib: TimeTravel) -> None:
    lib.start_ticking_time("2026-01-01T10:00:00+00:00")
    first = lib.get_current_simulated_timestamp()
    time.sleep(0.05)
    second = lib.get_current_simulated_timestamp()
    assert second - first >= 0.04
