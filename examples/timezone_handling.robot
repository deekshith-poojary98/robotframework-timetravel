*** Settings ***
Documentation    Interpret naive datetimes in a configured IANA timezone.
Library          TimeTravel

*** Test Cases ***
Naive Instant In Kolkata
    [Teardown]    Reset Time
    Set Timezone    Asia/Kolkata
    Freeze Time    2026-01-01T05:30:00
    ${now}=    Get Current Simulated Time
    Should Start With    ${now}    2026-01-01T05:30:00+05:30
    ${tz}=    Get Current Timezone
    Should Be Equal    ${tz}    Asia/Kolkata
