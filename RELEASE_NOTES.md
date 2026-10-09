# Release Notes

## robotframework-timetravel v0.1.0

**Release Date:** October 10, 2026

### Overview

`robotframework-timetravel` v0.1.0 is the first public release of a deterministic
time-control library for Robot Framework.

Built on top of Python's `time-machine`, the library provides readable keywords
for freezing, traveling, advancing, and rewinding perceived time while testing
OTP expiry, JWT lifetime, licenses, subscriptions, scheduled dates, retry
windows, and timezone-sensitive rules — without writing Python mocking code in
every suite.

---

## Highlights

### Clock Control Keywords

* `Freeze Time`, `Freeze At Timestamp`, `Freeze At Real Time`
* `Travel To Time`, `Travel To Timestamp`
* `Advance Time`, `Rewind Time`, `Shift Time`
* `Start Ticking Time`, `Pause Time`, `Resume Ticking Time`
* `Advance To Next Weekday`
* `Get Current Simulated Time`, `Get Current Simulated Timestamp`, `Get Current Simulated Timestamp Ns`
* `Get Clock Mode`, `Time Travel Is Active`
* `Get Real Time`, `Get Real Timestamp` (via `time-machine` escape hatch)
* `Reset Time`

### Timezone / Calendar Keywords

* `Set Timezone`, `Get Current Timezone`
* `Convert Datetime To Timezone`
* `Get Current Simulated Time In Timezone`
* `Format Simulated Time`, `Get Simulated Weekday`

### Assertion Keywords

* `Simulated Time Should Be`
* `Simulated Time Should Be After` / `Before`
* `Simulated Timestamp Should Equal`
* `Time Until Should Be`
* `Fail If Time Travel Is Active`

### Lifecycle Safety

* Explicit clock state management with clear errors for invalid operations
* Idempotent `Reset Time`
* Optional auto-reset after every test to prevent frozen-clock leakage
* GLOBAL library scope with Robot Framework listener cleanup

### Testing and Packaging

* Unit, integration, and Robot Framework acceptance coverage
* Executable examples for OTP, JWT, subscription, license, and timezone scenarios
* Wheel and source distribution packaging
* CI matrix for Python 3.11–3.14

### Documented Limitations

* Process-local Python clock manipulation only
* No OS / database / browser / remote-API clock acceleration
* Not safe for concurrent tests sharing one process
* No continuous `Accelerate Clock 100x` keyword in v1

See [`docs/limitations.md`](docs/limitations.md) for details.
