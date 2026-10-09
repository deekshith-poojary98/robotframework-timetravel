from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from TimeTravel.clock import ClockController, ClockMode
from TimeTravel.exceptions import ClockStateError


@pytest.fixture
def clock() -> ClockController:
    controller = ClockController()
    yield controller
    controller.reset()


def _utc(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def test_freeze_sets_frozen_mode(clock: ClockController) -> None:
    clock.freeze(_utc(2026, 1, 1, 10))
    assert clock.mode is ClockMode.FROZEN
    assert clock.now().replace(microsecond=0) == datetime(
        2026, 1, 1, 10, tzinfo=timezone.utc
    )


def test_repeated_freeze_replaces_instant(clock: ClockController) -> None:
    clock.freeze(_utc(2026, 1, 1, 10))
    clock.freeze(_utc(2026, 2, 1, 10))
    assert clock.now().month == 2


def test_travel_while_idle_starts_frozen(clock: ClockController) -> None:
    clock.travel_to(_utc(2026, 3, 1, 8))
    assert clock.mode is ClockMode.FROZEN
    assert clock.now().month == 3


def test_travel_while_active_replaces_instant(clock: ClockController) -> None:
    clock.freeze(_utc(2026, 1, 1, 10))
    clock.travel_to(_utc(2026, 6, 1, 12))
    assert clock.mode is ClockMode.FROZEN
    assert clock.now() == datetime(2026, 6, 1, 12, tzinfo=timezone.utc)


def test_shift_requires_active_clock(clock: ClockController) -> None:
    with pytest.raises(ClockStateError, match="active simulated clock"):
        clock.shift(timedelta(minutes=5))


def test_advance_and_rewind(clock: ClockController) -> None:
    clock.freeze(_utc(2026, 1, 1, 10))
    clock.shift(timedelta(minutes=5))
    assert clock.now().minute == 5
    clock.shift(timedelta(minutes=-5))
    assert clock.now().minute == 0


def test_reset_is_idempotent(clock: ClockController) -> None:
    clock.freeze(_utc(2026, 1, 1, 10))
    clock.reset()
    clock.reset()
    assert clock.mode is ClockMode.IDLE


def test_start_ticking_mode(clock: ClockController) -> None:
    clock.start_ticking(_utc(2026, 1, 1, 10))
    assert clock.mode is ClockMode.TICKING


def test_timezone_configuration(clock: ClockController) -> None:
    assert clock.get_timezone() == "UTC"
    assert clock.set_timezone("Asia/Kolkata") == "Asia/Kolkata"
    clock.freeze(_utc(2026, 1, 1, 0))
    assert clock.now().hour == 5
    assert clock.now().tzinfo.key == "Asia/Kolkata"  # type: ignore[union-attr]
