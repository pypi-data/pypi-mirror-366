*** Settings ***
Documentation     Actions spécifiques aux droits.

*** Keywords ***
Depuis le listing des droits
    [Tags]  om_droit
    [Documentation]  Accède au listing des droits.

    Depuis le listing  om_droit


Depuis le listing des droit du profil
    [Tags]  om_droit  om_profil

    [Documentation]    Permet d'accéder au listing des droits depuis le
    ...    formulaire d'un profil.

    [Arguments]    ${om_profil}=null    ${om_profil_libelle}=null

    #
    Depuis le contexte du profil    ${om_profil}    ${om_profil_libelle}
    # On clique sur l'onglets des droits
    Click On Tab    om_droit    droit


Saisir le droit
    [Tags]  om_droit

    [Documentation]    Permet de remplir le formulaire om_droit.

    [Arguments]    ${libelle}    ${om_profil}=null

    # On saisit le libellé
    Input Text    css=#libelle    ${libelle}
    # On sélectionne le profil par son libellé
    Run Keyword If    '${om_profil}' != 'null'    Select From List By Label    css=#om_profil    ${om_profil}


Ajouter le droit depuis le menu
    [Tags]  om_droit

    [Documentation]  Ajoute un enregistrement de type 'droit' (om_droit) via le listing.

    [Arguments]    ${libelle}    ${om_profil}

    #
    Depuis le listing des droits
    # On clique sur l'action Ajouter
    Click On Add Button
    #
    Saisir le droit    ${libelle}    ${om_profil}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Valid Message Should Contain    Vos modifications ont bien été enregistrées.


Ajouter le droit depuis le profil
    [Tags]  om_droit  om_profil

    [Documentation]  Ajoute un enregistrement de type 'droit' (om_droit) via le listing dans le contexte d'un profil.

    [Arguments]    ${om_droit_libelle}    ${om_profil}=null    ${om_profil_libelle}=null

    #
    Depuis le listing des droit du profil    ${om_profil}    ${om_profil_libelle}
    # On clique sur l'action Ajouter
    Click On Add Button JS
    #
    Saisir le droit    ${om_droit_libelle}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain    Vos modifications ont bien été enregistrées.
