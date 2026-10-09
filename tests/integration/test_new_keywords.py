from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest

from TimeTravel import TimeTravel
from TimeTravel.exceptions import ClockStateError, TimeTravelError


@pytest.fixture
def lib() -> TimeTravel:
    library = TimeTravel(auto_reset=False)
    yield library
    library.reset_time()


def test_pause_and_resume(lib: TimeTravel) -> None:
    lib.start_ticking_time("2026-01-01T10:00:00+00:00")
    assert lib.get_clock_mode() == "ticking"
    lib.pause_time()
    assert lib.get_clock_mode() == "frozen"
    frozen = lib.get_current_simulated_timestamp()
    time.sleep(0.05)
    assert lib.get_current_simulated_timestamp() == frozen
    lib.resume_ticking_time()
    assert lib.get_clock_mode() == "ticking"
    time.sleep(0.05)
    assert lib.get_current_simulated_timestamp() > frozen


def test_pause_and_resume_preserve_named_timezone_localtime(lib: TimeTravel) -> None:
    """Pause/Resume must not rewrite destination TZ to UTC (breaks localtime)."""
    import os

    lib.set_timezone("Asia/Kolkata")
    lib.start_ticking_time("2026-01-01T05:30:00")
    assert os.environ.get("TZ") == "Asia/Kolkata"
    assert time.localtime().tm_hour == 5

    lib.pause_time()
    assert lib.get_clock_mode() == "frozen"
    assert os.environ.get("TZ") == "Asia/Kolkata"
    assert time.localtime().tm_hour == 5

    lib.resume_ticking_time()
    assert lib.get_clock_mode() == "ticking"
    assert os.environ.get("TZ") == "Asia/Kolkata"
    assert time.localtime().tm_hour == 5


def test_timestamp_destinations(lib: TimeTravel) -> None:
    ts = datetime(2026, 1, 1, 10, tzinfo=timezone.utc).timestamp()
    lib.freeze_at_timestamp(ts)
    assert lib.get_current_simulated_timestamp() == ts
    lib.travel_to_timestamp(ts + 3600)
    assert lib.get_current_simulated_timestamp() == ts + 3600


def test_real_time_escape_hatch(lib: TimeTravel) -> None:
    import time_machine

    lib.freeze_time("2026-01-01T10:00:00+00:00")
    real_ts = lib.get_real_timestamp()
    sim_ts = lib.get_current_simulated_timestamp()
    assert sim_ts == datetime(2026, 1, 1, 10, tzinfo=timezone.utc).timestamp()
    assert real_ts != sim_ts
    # time.time() is patched; compare against escape hatch wall clock.
    assert abs(real_ts - time_machine.escape_hatch.time.time()) < 2
    assert not lib.get_real_time().startswith("2026-01-01T10:00:00")


def test_freeze_at_real_time(lib: TimeTravel) -> None:
    before = time.time()
    lib.freeze_at_real_time()
    assert abs(lib.get_current_simulated_timestamp() - before) < 2
    assert lib.get_clock_mode() == "frozen"


def test_weekday_and_assertions(lib: TimeTravel) -> None:
    # 2026-01-01 is Thursday
    lib.freeze_time("2026-01-01T10:00:00+00:00")
    assert lib.get_simulated_weekday() == "Thursday"
    lib.advance_to_next_weekday("Monday")
    assert lib.get_simulated_weekday() == "Monday"
    assert lib.get_current_simulated_time().startswith("2026-01-05T10:00:00")
    lib.simulated_time_should_be("2026-01-05T10:00:00+00:00")
    lib.simulated_time_should_be_after("2026-01-01T10:00:00+00:00")
    lib.simulated_time_should_be_before("2026-01-06T00:00:00+00:00")


def test_timezone_helpers(lib: TimeTravel) -> None:
    lib.freeze_time("2026-01-01T00:00:00+00:00")
    assert lib.convert_datetime_to_timezone(
        "2026-01-01T00:00:00+00:00", "Asia/Kolkata"
    ).startswith("2026-01-01T05:30:00")
    assert lib.get_current_simulated_time_in_timezone("Asia/Kolkata").startswith(
        "2026-01-01T05:30:00"
    )
    assert "Thursday" in lib.format_simulated_time("%A")


def test_time_until_and_active_checks(lib: TimeTravel) -> None:
    lib.freeze_time("2026-01-01T10:00:00+00:00")
    assert lib.time_travel_is_active() is True
    lib.time_until_should_be("2026-01-01T10:05:00+00:00", "5 minutes")
    lib.reset_time()
    assert lib.time_travel_is_active() is False
    lib.fail_if_time_travel_is_active()
    with pytest.raises(ClockStateError):
        lib.pause_time()


def test_timestamp_ns(lib: TimeTravel) -> None:
    lib.freeze_time("2026-01-01T10:00:00+00:00")
    ns = lib.get_current_simulated_timestamp_ns()
    assert ns == int(lib.get_current_simulated_timestamp() * 1_000_000_000)


def test_assertion_failure(lib: TimeTravel) -> None:
    lib.freeze_time("2026-01-01T10:00:00+00:00")
    with pytest.raises(TimeTravelError, match="should be"):
        lib.simulated_time_should_be("2026-01-01T11:00:00+00:00")
