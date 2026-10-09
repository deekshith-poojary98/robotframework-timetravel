*** Settings ***
Documentation    Travel forward past a JWT expiry window.
Library          TimeTravel

*** Keywords ***
Issue JWT
    ${iat}=    Get Current Simulated Timestamp
    ${exp}=    Evaluate    ${iat} + 3600
    RETURN    ${exp}

Verify JWT Is Expired
    [Arguments]    ${exp}
    ${now}=    Get Current Simulated Timestamp
    Should Be True    ${now} >= ${exp}

*** Test Cases ***
JWT Expires After One Hour
    [Teardown]    Reset Time
    Freeze Time    2026-01-01T09:00:00+00:00
    ${exp}=    Issue JWT
    Advance Time    1 hour
    Verify JWT Is Expired    ${exp}
