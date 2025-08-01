*** Settings ***
Documentation  Module 'Import'.

*** Keywords ***
Depuis l'écran principal du module 'Import'
    [Tags]  module_import
    [Documentation]  Accède à l'écran principal du module 'import'.

    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_IMPORT}
    La page ne doit pas contenir d'erreur


Depuis l'import
    [Tags]  module_import
    [Arguments]  ${obj}

    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_IMPORT}&obj=${obj}
    La page ne doit pas contenir d'erreur


Click On Submit Button In Import CSV
    [Tags]  module_import

    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Click Element  css=#form-csv-import form div.formControls input
    Sleep  1
    La page ne doit pas contenir d'erreur

