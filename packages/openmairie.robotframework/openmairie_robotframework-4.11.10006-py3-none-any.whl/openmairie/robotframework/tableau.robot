*** Settings ***
Documentation     Actions dans un tableau

*** Keywords ***
Click On Search Button
    [Tags]
    Click Element    css=#adv-search-submit
    La page ne doit pas contenir d'erreur

Click On Simple Search Button
    [Tags]
    Click Element    css=div.tab-search form button
    La page ne doit pas contenir d'erreur

Elements From Column Should Be
    [Tags]
    [Arguments]    ${column}    ${messagetext}
    Element Text Should Be    css=td.col-${column}    ${messagetext}

Elements From Column Should Contain
    [Tags]
    [Arguments]    ${column}    ${messagetext}
    Element Should Contain    css=td.col-${column}    ${messagetext}

Click On Link
    [Tags]
    [Arguments]    ${link}
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Click Link      ${link}
    Sleep    1
    La page ne doit pas contenir d'erreur

Get Object In Tab
    [Tags]
    ${url}    Get Location
    ${getParams}    Fetch From Right    ${url}    obj=
    # on ne garde que ce qui est avant le premier "&" rencontré
    ${objInTab}    ${otherGetParams} =    Split String    ${getParams}    &    1
    [Return]  ${objInTab}

Total Results Should Be Equal
    [Tags]
    [Arguments]    ${totalAttendu}
    ${nombreResultats} =    Get Total Results
    Should Be Equal As Integers    ${nombreResultats}    ${totalAttendu}

Total Results In Tab Should Be Equal
    [Tags]
    [Arguments]    ${totalAttendu}  ${obj}
    ${nombreResultats} =    Get Total Results In Tab  ${obj}
    Should Be Equal As Integers    ${nombreResultats}    ${totalAttendu}

Total Results In Subform Should Be Equal
    [Tags]
    [Arguments]    ${totalAttendu}    ${obj}
    ${nombreResultats} =    Get Text    css=#sousform-${obj} .tab-pagination .pagination-nb span.pagination-text
    ${nombreResultats} =    Fetch From Right    ${nombreResultats}    sur
    Should Be Equal As Integers    ${nombreResultats}    ${totalAttendu}

Get Total Results
    [Tags]
    ${objInTab} =  Get Object In Tab
    ${nombreResultats} =    Get Text    css=#tab-${objInTab} .tab-pagination .pagination-nb span.pagination-text
    ${nombreResultats} =    Fetch From Right    ${nombreResultats}    sur
    ${nombreResultats} =    Convert to Integer    ${nombreResultats}
    [Return]  ${nombreResultats}

Get Total Results In Tab
    [Tags]
    [Arguments]    ${objInTab}
    ${nombreResultats} =    Get Text    css=#tab-${objInTab} .tab-pagination .pagination-nb span.pagination-text
    ${nombreResultats} =    Fetch From Right    ${nombreResultats}    sur
    ${nombreResultats} =    Convert to Integer    ${nombreResultats}
    [Return]  ${nombreResultats}

Get Pagination Text
    [Tags]
    [Documentation]    Permet de récupérer le nombre d'enregistrements par page.
    ${pagination_text} =    Get Text    css=div.tab-pagination div.pagination-nb span.pagination-text
    [return]    ${pagination_text}

Pagination Text Not Should Be
    [Tags]
    [Documentation]    Permet de vérifier le nombre d'enregistrement d'une page.
    [Arguments]    ${pagination_expected}
    ${pagination_text} =    Get Pagination Text
    Should Not Be Equal    ${pagination_text}    ${pagination_expected}

Tab Should Not Contain Add Button
    [Tags]
    Page Should Not Contain Element    css=#action-tab-om_collectivite-corner-ajouter

Use Simple Search
    [Tags]
    [Arguments]    ${label_select}    ${search_text}
    # On sélectionne le champ sur lequel faire la recherche simple
    Select From List By Label    css=div.tab-search form select    ${label_select}
    # On saisit le texte recherché
    Input Text    css=div.tab-search form input    ${search_text}
    # On clique sur le bouton "Recherche"
    Click On Simple Search Button

L'action ajouter doit être disponible
    [Tags]
    Page Should Contain Element    css=span.add-16

L'action ajouter ne doit pas être disponible
    [Tags]
    Page Should Not Contain Element    css=span.add-16

Select Pagination
    [Tags]
    [Documentation]    Permet de sélectionner une page du listing par la valeur.
    ...    Dépend du nombre d'enregistrement par page.
    [Arguments]    ${premier}
    # On sélectionne la page du listing
    Select From List By Value    css=div.tab-pagination div.pagination-select select    ${premier}
    # On vérifie qu'il n'y a pas d'erreur
    La page ne doit pas contenir d'erreur

Valid Message Should Be In Tab
    [Tags]
    [Arguments]    ${messagetext}
    Element Text Should Be  css=.tab-message div.message.ui-state-valid p span.text  ${messagetext}

Valid Message Should Be In Subtab
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Text Should Be  css=.soustab-message div.message.ui-state-valid p span.text  ${messagetext}

Valid Message Should Contain In Tab
    [Tags]
    [Arguments]    ${messagetext}
    Element Should Contain  css=.tab-message div.message.ui-state-valid p span.text  ${messagetext}

Valid Message Should Contain In Subtab
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=.soustab-message div.message.ui-state-valid p span.text  ${messagetext}
