*** Settings ***
Documentation  Actions sur un PDF visionné depuis Firefox.

*** Keywords ***
Open PDF
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    [Arguments]  ${window}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Select Window  ${window}.php
    La page ne doit pas contenir d'erreur

Close PDF
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    Close Window
    Select Window

Previous Page PDF
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Click Element  css=#previous

Next Page PDF
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Click Element  css=#next

PDF Move Page To
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    [Arguments]  ${page_number}
    # vide le champ texte à coup de backspaces car le keyword Clear Input Text
    # a un comportement aléatoire et ici ne fonctionne pas du tout
    # @see: https://www.queryxchange.com/q/27_53518481/robot-framework-clear-element-text-keyword-is-not-working/
    ${currentPageNumber}=  Get Element Attribute  css=#pageNumber  value
    ${backspacesCount}=    Get Length      ${currentPageNumber}
    Run Keyword If  ${currentPageNumber} != ''
    ...  Repeat Keyword  ${backspacesCount +1}  Press Key  css=#pageNumber   \\08
    # saisi le numéro de page dans le champs texte
    Input Text  css=#pageNumber  ${page_number}
    # valide le changement de page
    Press Key  css=#pageNumber   \\13

PDF Page Number Should Contain
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    [Arguments]  ${page_number}  ${text}
    PDF Move Page To  ${page_number}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=#pageContainer${page_number}  ${text}

PDF Page Number Should Not Contain
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    [Arguments]  ${page_number}  ${text}
    PDF Move Page To  ${page_number}
    Element Should Not Contain  css=#pageContainer${page_number}  ${text}

PDF Pages Number Should Be
    [Tags]
    [Documentation]  Spécifique à la visionneuse de firefox
    [Arguments]  ${total}
    ${over} =  Convert to Integer  ${total}
    ${over} =  Evaluate  ${over}+1
    Page Should Contain Element  css=#pageContainer${total}
    Page Should Not Contain Element  css=#pageContainer${over}
