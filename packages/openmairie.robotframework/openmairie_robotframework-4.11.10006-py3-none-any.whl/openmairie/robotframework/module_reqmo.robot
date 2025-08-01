*** Settings ***
Documentation  Module 'Reqmo'.

*** Keywords ***
Depuis l'écran principal du module 'Reqmo'
    [Tags]  module_reqmo
    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_REQMO}
    La page ne doit pas contenir d'erreur


Click On Submit Button In Reqmo
    [Tags]  module_reqmo
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Click Element    css=#reqmo-form form div.formControls input
    Sleep    1
    La page ne doit pas contenir d'erreur


