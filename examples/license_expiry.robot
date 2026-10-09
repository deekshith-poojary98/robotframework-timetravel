*** Settings ***
Documentation    Rewind and advance around a license validity window.
Library          TimeTravel

*** Keywords ***
License Valid At
    [Arguments]    ${not_before}    ${not_after}
    ${now}=    Get Current Simulated Timestamp
    Should Be True    ${now} >= ${not_before}
    Should Be True    ${now} < ${not_after}

*** Test Cases ***
License Window
    [Teardown]    Reset Time
    Freeze Time    2026-01-15T00:00:00+00:00
    ${not_before}=    Get Current Simulated Timestamp
    ${not_after}=    Evaluate    ${not_before} + 14 * 86400
    License Valid At    ${not_before}    ${not_after}
    Advance Time    14 days
    ${now}=    Get Current Simulated Timestamp
    Should Be True    ${now} >= ${not_after}
