# Limitations

TimeTravel is a **deterministic testing library** for Python code running in the
same process as Robot Framework. It is not a universal clock simulator.

## In scope (v1)

- Python-level time APIs supported by [`time-machine`](https://github.com/adamchainz/time-machine)
  (for example `time.time`, `time.localtime`, `datetime.datetime.now`)
- Frozen and shifted simulated time
- Ticking simulated time that advances with real wall time
- Timezone-aware inputs and naive-input interpretation via `Set Timezone`
- Robot Framework keywords and deterministic cleanup

## Not automatically supported

| Capability | Why |
|---|---|
| Accelerating the OS clock | Requires privileged system changes; out of scope |
| Database server clocks | Other processes have their own clocks |
| External apps / remote APIs | Only the current Python process is patched |
| Browser `Date` / `performance.now()` | JavaScript runtimes are separate |
| Sleeping threads waking early | Changing perceived time does not interrupt real `sleep` waits already in progress the way a true accelerator would |
| Every monotonic clock / timeout | Backend coverage is limited to what `time-machine` patches |
| Safe shared-process parallel tests | Clock state is process-global |

## Parallel execution

`time-machine` patches process-global time functions. Do **not** run concurrent
tests that share one Python process and both use TimeTravel. Prefer process
isolation (separate workers / separate interpreter processes).

## External time sources

If the application under test asks an external service for time, inject a clock
in production code (dependency injection) and stub that seam in tests. TimeTravel
cannot advance a remote OTP provider, payment processor, or license server.

## Acceleration

v1 does **not** provide `Accelerate Clock 100x`. Jumping the clock forward with
`Advance Time` is not the same as continuous accelerated ticking.
