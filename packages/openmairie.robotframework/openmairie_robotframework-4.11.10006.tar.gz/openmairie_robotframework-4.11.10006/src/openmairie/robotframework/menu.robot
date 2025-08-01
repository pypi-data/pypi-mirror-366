*** Settings ***
Documentation     Actions menu

*** Keywords ***
Click On Menu Rubrik
    [Tags]
    [Arguments]    ${rubrikclass}
    Click Element    css=#menu ul#menu-list li.rubrik h3 > a.${rubrikclass}-20
    Sleep    1
    La page ne doit pas contenir d'erreur

Open Menu
    [Tags]
    [Arguments]    ${rubrikclass}
    Go To Dashboard
    Click On Menu Rubrik    ${rubrikclass}

Submenu In Menu Should Be Selected
    [Tags]
    [Arguments]  ${rubrikclass}  ${elemclass}
    Run Keyword If  "${rubrikclass}" != "${NULL}"  Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Be Visible  css=#menu ul#menu-list h3.ui-accordion-header.ui-state-active a.${rubrikclass}-20
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Be Visible  css=#menu ul#menu-list li.rubrik ul.rubrik li.elem.ui-state-focus.${elemclass}

Menu Should Contain Submenu
    [Tags]
    [Arguments]    ${elemclass}
    Page Should Contain Element    css=#menu-list a.${elemclass}-16

Menu Should Not Contain Submenu
    [Tags]
    [Arguments]    ${elemclass}
    Page Should Not Contain Element    css=#menu-list a.${elemclass}-16

Page Should Contain Menu
    [Tags]
    [Arguments]    ${rubrikclass}
    Page Should Contain Element    css=#menu-list a.${rubrikclass}-20

Page Should Not Contain Menu
    [Tags]
    [Arguments]    ${rubrikclass}
    Page Should Not Contain Element    css=#menu-list a.${rubrikclass}-20

Go To Submenu
    [Tags]
    [Arguments]    ${elemclass}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Click Element    css=#menu ul#menu-list li.rubrik ul.rubrik li.elem a.${elemclass}-16
    La page ne doit pas contenir d'erreur

Go To Submenu In Menu
    [Tags]
    [Arguments]    ${rubrikclass}    ${elemclass}
    ${present}=  Run Keyword And Return Status    Element Should Be Visible   css=#menu ul#menu-list li.rubrik ul.rubrik li.elem a.${elemclass}-16
    Run Keyword If    "${present}" == "False"    Click On Menu Rubrik    ${rubrikclass}
    Go To Submenu    ${elemclass}
    Submenu In Menu Should Be Selected    ${rubrikclass}    ${elemclass}
