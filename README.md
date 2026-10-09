<div align="center">

<h1>TimeTravel</h1>

<h3>Stop sleeping through expiry tests. Start controlling time.</h3>

<p>
<i>A modern Robot Framework library for deterministic time-dependent testing.</i>
</p>

<br>

<a href="https://badge.fury.io/py/robotframework-timetravel">
    <img src="https://badge.fury.io/py/robotframework-timetravel.svg" alt="PyPI version">
</a>

<img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">

<img src="https://img.shields.io/badge/robotframework-7.5%2B-blue" alt="Robot Framework 7.5+">

<img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License">

<a href="https://github.com/deekshith-poojary98/robotframework-timetravel/actions/workflows/code-checks.yml">
    <img src="https://github.com/deekshith-poojary98/robotframework-timetravel/actions/workflows/code-checks.yml/badge.svg" alt="CI Tests">
</a>

<a href="https://github.com/deekshith-poojary98/robotframework-timetravel/actions/workflows/generate-docs.yml">
    <img src="https://github.com/deekshith-poojary98/robotframework-timetravel/actions/workflows/generate-docs.yml/badge.svg" alt="Docs Build">
</a>

</div>
<br>

`robotframework-timetravel` lets Robot Framework tests freeze, travel, advance,
and rewind perceived time using [`time-machine`](https://github.com/adamchainz/time-machine).

It is designed for deterministic expiry and scheduling scenarios without writing
Python mocking glue in every suite.

You can find the keyword documentation [here](https://deekshith-poojary98.github.io/robotframework-timetravel/)

Perfect for:

- OTP expiration
- JWT and access-token lifetime
- License and subscription renewals
- Scheduled jobs and future dates
- Retry windows and cooldown periods
- Timezone-sensitive business rules

---

## Why TimeTravel?

Traditional Robot Framework time checks often become:

```robot
${expires}=    Evaluate    time.time() + 300    modules=time
Sleep    5 minutes
Should Be True    ${True}
```

That is slow, brittle, and hard to repeat.

With TimeTravel:

```robot
Freeze Time    2026-01-01T10:00:00+00:00
Create OTP
Advance Time    5 minutes
Verify OTP Is Expired
```

No long sleeps. No flaky wall-clock races. No ad-hoc Python mocks.

---

## Architecture

TimeTravel is built around:

- A thin Robot Framework keyword layer on `robotframework-pythonlibcore`
- An internal `ClockController` with explicit lifecycle semantics
- `time-machine` as the process-local clock backend
- Duration and datetime parsers with clear validation errors
- Optional auto-reset after each test

```
Robot Framework Keywords
  ↓
ClockController lifecycle
  ↓
time-machine traveller
  ↓
Python time / datetime APIs in this process
```

---

## Feature Matrix

| Category | Keywords |
| --- | --- |
| Clock control | `Freeze Time`, `Freeze At Timestamp`, `Freeze At Real Time`, `Travel To Time`, `Travel To Timestamp`, `Advance Time`, `Rewind Time`, `Shift Time`, `Start Ticking Time`, `Pause Time`, `Resume Ticking Time`, `Advance To Next Weekday`, `Reset Time` |
| Inspection | `Get Current Simulated Time`, `Get Current Simulated Timestamp`, `Get Current Simulated Timestamp Ns`, `Get Clock Mode`, `Time Travel Is Active`, `Get Real Time`, `Get Real Timestamp` |
| Timezone / calendar | `Set Timezone`, `Get Current Timezone`, `Convert Datetime To Timezone`, `Get Current Simulated Time In Timezone`, `Format Simulated Time`, `Get Simulated Weekday` |
| Assertions | `Simulated Time Should Be`, `Simulated Time Should Be After`, `Simulated Time Should Be Before`, `Simulated Timestamp Should Equal`, `Time Until Should Be`, `Fail If Time Travel Is Active` |

Implementation note:

- `src/TimeTravel/keywords/clock_control.py` — clock control and inspection
- `src/TimeTravel/keywords/timezone_control.py` — timezone/calendar helpers
- `src/TimeTravel/keywords/assertions.py` — assertion keywords

---

## Quick Start

Install from PyPI:

```bash
pip install robotframework-timetravel
```

Install from the repository:

```bash
pip install .
```

Install development dependencies:

```bash
pip install -e ".[dev]"
# or
pip install -r requirements.txt
pip install -e .
```

---

## Simple Example

```robot
*** Settings ***
Library    TimeTravel

*** Test Cases ***
OTP Expires After Five Minutes
    [Teardown]    Reset Time
    Freeze Time    2026-01-01T10:00:00+00:00
    Create OTP
    Advance Time    5 minutes
    Verify OTP Is Expired
```

By default TimeTravel auto-resets at the end of every test. Disable with:

```robot
Library    TimeTravel    auto_reset=${False}
```

---

## Datetime and Duration Inputs

Accepted datetimes:

- `2026-01-01T10:00:00+00:00`
- `2026-01-01T10:00:00`
- `2026-01-01 10:00:00`
- `2026-01-01`

Naive values are interpreted in the timezone from `Set Timezone` (default `UTC`).
Aware values keep their own timezone.

Accepted durations:

- `30 seconds`
- `5 minutes`
- `2 hours`
- `31 days`
- `1 week`
- `1 day 6 hours`
- `-2 hours` (for `Shift Time` only)

---

## Lifecycle Semantics

| Situation | Behavior |
| --- | --- |
| `Freeze Time` / `Start Ticking Time` while active | Replaces the current clock |
| `Travel To Time` while idle | Starts a frozen clock |
| `Travel To Time` while active | Replaces the instant; keeps frozen/ticking mode |
| Advance / Rewind / Shift while idle | Clear error |
| `Reset Time` | Restores real time and interpretation timezone `UTC` |
| End of test (`auto_reset=${True}`) | Implicit `Reset Time` |

---

## Limitations

This library manipulates Python-level time in the **current process** only.

It does **not**:

- Accelerate the operating-system clock
- Advance database-server clocks
- Control browser JavaScript `Date`
- Make concurrent tests safe when they share process-global clock state

See [`docs/limitations.md`](docs/limitations.md) for the full list.

---

## Examples

See [`examples/`](examples/):

- `otp_expiry.robot`
- `jwt_expiry.robot`
- `subscription_expiry.robot`
- `license_expiry.robot`
- `timezone_handling.robot`

---

## Running Tests

```bash
pytest
```

```bash
PYTHONPATH=src robot tests/acceptance.robot
```

```bash
./build.sh
```

---

## License

[Apache-2.0](LICENSE)
