*** Settings ***
Documentation    Advance thirty-one days to verify subscription expiry.
Library          TimeTravel

*** Keywords ***
Create Subscription
    ${starts}=    Get Current Simulated Timestamp
    ${ends}=    Evaluate    ${starts} + 31 * 86400
    RETURN    ${ends}

Verify Subscription Is Expired
    [Arguments]    ${ends}
    ${now}=    Get Current Simulated Timestamp
    Should Be True    ${now} >= ${ends}

*** Test Cases ***
Subscription Expires After Thirty One Days
    [Teardown]    Reset Time
    Freeze Time    2026-01-01T00:00:00+00:00
    ${ends}=    Create Subscription
    Advance Time    31 days
    Verify Subscription Is Expired    ${ends}
