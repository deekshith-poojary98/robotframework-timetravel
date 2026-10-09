*** Settings ***
Documentation    Freeze time, create an OTP, advance five minutes, assert expiry.
Library          TimeTravel
Library          Collections

*** Variables ***
${OTP_TTL}       5 minutes

*** Keywords ***
Create OTP
    ${issued}=    Get Current Simulated Timestamp
    ${otp}=    Create Dictionary    code=123456    issued=${issued}
    RETURN    ${otp}

Verify OTP Is Expired
    [Arguments]    ${otp}
    ${now}=    Get Current Simulated Timestamp
    ${age}=    Evaluate    ${now} - ${otp}[issued]
    Should Be True    ${age} >= 300

*** Test Cases ***
OTP Expires After Five Minutes
    [Teardown]    Reset Time
    Freeze Time    2026-01-01T10:00:00+00:00
    ${otp}=    Create OTP
    Advance Time    ${OTP_TTL}
    Verify OTP Is Expired    ${otp}
