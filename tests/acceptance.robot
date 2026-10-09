*** Settings ***
Library    TimeTravel    auto_reset=${True}
Library    Collections
Library    DateTime

*** Test Cases ***
Freeze And Advance
    Freeze Time    2026-01-01T10:00:00+00:00
    Simulated Time Should Be    2026-01-01T10:00:00+00:00
    Advance Time    5 minutes
    Simulated Time Should Be    2026-01-01T10:05:00+00:00
    Time Until Should Be    2026-01-01T10:10:00+00:00    5 minutes

Travel To Exact Instant
    Travel To Time    2026-06-01T12:30:00+00:00
    Simulated Time Should Be    2026-06-01T12:30:00+00:00

Backward Time Travel
    Freeze Time    2026-01-01T10:00:00+00:00
    Rewind Time    2 hours
    Simulated Time Should Be    2026-01-01T08:00:00+00:00
    Shift Time    -30 minutes
    Simulated Time Should Be    2026-01-01T07:30:00+00:00

Timestamp Destinations And Pause Resume
    ${ts}=    Convert Date    2026-01-01 10:00:00    epoch    exclude_millis=True
    Freeze At Timestamp    ${ts}
    ${mode}=    Get Clock Mode
    Should Be Equal    ${mode}    frozen
    Resume Ticking Time
    ${mode}=    Get Clock Mode
    Should Be Equal    ${mode}    ticking
    Pause Time
    ${mode}=    Get Clock Mode
    Should Be Equal    ${mode}    frozen

Real Time Escape Hatch
    Freeze Time    2026-01-01T10:00:00+00:00
    ${real}=    Get Real Time
    Should Not Start With    ${real}    2026-01-01T10:00:00
    ${active}=    Time Travel Is Active
    Should Be True    ${active}

Weekday And Timezone Helpers
    Freeze Time    2026-01-01T10:00:00+00:00
    ${day}=    Get Simulated Weekday
    Should Be Equal    ${day}    Thursday
    Advance To Next Weekday    Monday
    ${day}=    Get Simulated Weekday
    Should Be Equal    ${day}    Monday
    ${kolkata}=    Get Current Simulated Time In Timezone    Asia/Kolkata
    Should Start With    ${kolkata}    2026-01-05T15:30:00
    ${ny}=    Convert Datetime To Timezone    2026-01-05T10:00:00+00:00    America/New_York
    Should Contain    ${ny}    2026-01-05T05:00:00

Invalid Duration Fails
    Freeze Time    2026-01-01T10:00:00+00:00
    Run Keyword And Expect Error    *Unsupported duration unit*    Advance Time    2 months

Invalid Datetime Fails
    Run Keyword And Expect Error    *Invalid datetime*    Freeze Time    not-a-date

Timezone Conversion
    Set Timezone    Asia/Kolkata
    ${tz}=    Get Current Timezone
    Should Be Equal    ${tz}    Asia/Kolkata
    Freeze Time    2026-01-01T05:30:00
    ${now}=    Get Current Simulated Time
    Should Start With    ${now}    2026-01-01T05:30:00+05:30

Repeated Reset Is Safe
    Freeze Time    2026-01-01T10:00:00+00:00
    Reset Time
    Reset Time
    Fail If Time Travel Is Active

Independent Sequential Tests Part A
    Freeze Time    2026-01-01T10:00:00+00:00
    ${now}=    Get Current Simulated Time
    Should Start With    ${now}    2026-01-01T10:00:00

Independent Sequential Tests Part B
    Travel To Time    2027-02-02T11:00:00+00:00
    ${now}=    Get Current Simulated Time
    Should Start With    ${now}    2027-02-02T11:00:00

Test Failure Followed By Cleanup
    Freeze Time    2026-01-01T10:00:00+00:00
    Run Keyword And Expect Error    Boom    Fail    Boom

After Failure Clock Is Not Leaked
    Travel To Time    2028-01-01T00:00:00+00:00
    ${now}=    Get Current Simulated Time
    Should Start With    ${now}    2028-01-01T00:00:00

Keyword Documentation Exists
    Keyword Should Exist    Freeze Time
    Keyword Should Exist    Freeze At Timestamp
    Keyword Should Exist    Freeze At Real Time
    Keyword Should Exist    Travel To Time
    Keyword Should Exist    Travel To Timestamp
    Keyword Should Exist    Advance Time
    Keyword Should Exist    Rewind Time
    Keyword Should Exist    Shift Time
    Keyword Should Exist    Start Ticking Time
    Keyword Should Exist    Pause Time
    Keyword Should Exist    Resume Ticking Time
    Keyword Should Exist    Advance To Next Weekday
    Keyword Should Exist    Get Current Simulated Time
    Keyword Should Exist    Get Current Simulated Timestamp
    Keyword Should Exist    Get Current Simulated Timestamp Ns
    Keyword Should Exist    Get Clock Mode
    Keyword Should Exist    Time Travel Is Active
    Keyword Should Exist    Get Real Time
    Keyword Should Exist    Get Real Timestamp
    Keyword Should Exist    Reset Time
    Keyword Should Exist    Set Timezone
    Keyword Should Exist    Get Current Timezone
    Keyword Should Exist    Convert Datetime To Timezone
    Keyword Should Exist    Get Current Simulated Time In Timezone
    Keyword Should Exist    Format Simulated Time
    Keyword Should Exist    Get Simulated Weekday
    Keyword Should Exist    Simulated Time Should Be
    Keyword Should Exist    Simulated Time Should Be After
    Keyword Should Exist    Simulated Time Should Be Before
    Keyword Should Exist    Simulated Timestamp Should Equal
    Keyword Should Exist    Time Until Should Be
    Keyword Should Exist    Fail If Time Travel Is Active
