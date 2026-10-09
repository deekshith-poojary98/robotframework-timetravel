from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest

from TimeTravel.clock import ClockController


@pytest.fixture
def clock() -> ClockController:
    controller = ClockController()
    yield controller
    controller.reset()


def test_python_time_apis_observe_frozen_instant(clock: ClockController) -> None:
    clock.freeze(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    assert datetime.now(timezone.utc) == datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    assert time.time() == datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc).timestamp()
    # Frozen: real sleep does not advance perceived time.
    time.sleep(0.05)
    assert datetime.now(timezone.utc) == datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)


def test_advance_changes_perceived_time(clock: ClockController) -> None:
    from datetime import timedelta

    clock.freeze(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    clock.shift(timedelta(minutes=5))
    assert datetime.now(timezone.utc) == datetime(2026, 1, 1, 10, 5, tzinfo=timezone.utc)


def test_timestamp_consistency(clock: ClockController) -> None:
    clock.freeze(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    assert clock.timestamp() == time.time()


def test_ticking_progresses(clock: ClockController) -> None:
    clock.start_ticking(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    first = time.time()
    time.sleep(0.05)
    second = time.time()
    assert second - first >= 0.04


def test_reset_restores_real_time(clock: ClockController) -> None:
    clock.freeze(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    clock.reset()
    # Real time should be near "now", not 2026-01-01 unless this test is run then.
    assert datetime.now(timezone.utc).year != 2026 or abs(time.time() - clock.timestamp()) < 1
    # Stronger check: after reset, sleeping advances time.time().
    before = time.time()
    time.sleep(0.05)
    assert time.time() - before >= 0.04


def test_cleanup_after_exception(clock: ClockController) -> None:
    clock.freeze(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        clock.reset()
    before = time.time()
    time.sleep(0.02)
    assert time.time() - before >= 0.015


def test_sequential_operations_do_not_leak(clock: ClockController) -> None:
    clock.freeze(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    clock.reset()
    clock.freeze(datetime(2027, 6, 15, 8, 0, tzinfo=timezone.utc))
    assert datetime.now(timezone.utc) == datetime(2027, 6, 15, 8, 0, tzinfo=timezone.utc)
    clock.reset()
    assert abs(time.time() - datetime.now(timezone.utc).timestamp()) < 1


def test_named_timezone_destination(clock: ClockController) -> None:
    from zoneinfo import ZoneInfo

    clock.set_timezone("Asia/Kolkata")
    clock.freeze(datetime(2026, 1, 1, 5, 30, tzinfo=ZoneInfo("Asia/Kolkata")))
    assert datetime.now(timezone.utc) == datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
