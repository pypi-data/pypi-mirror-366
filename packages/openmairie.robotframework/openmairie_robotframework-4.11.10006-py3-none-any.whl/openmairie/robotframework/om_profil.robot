*** Settings ***
Documentation     Actions spécifiques aux profils.

*** Keywords ***
Depuis le listing des profils
    [Tags]  om_profil
    [Documentation]  Accède au listing des profils.

    Depuis le listing  om_profil


Depuis le contexte du profil
    [Tags]  om_profil

    [Documentation]    Permet d'accéder au formulaire en consultation
    ...    d'un profil.

    [Arguments]    ${om_profil}=null    ${libelle}=null

    #
    Depuis le listing des profils
    # On recherche le profil
    Run Keyword If    '${om_profil}' != 'null'    Use Simple Search    profil    ${om_profil}    ELSE IF    '${libelle}' != 'null'    Use Simple Search    libellé    ${libelle}    ELSE    Fail
    # On clique sur le profil
    Run Keyword If    '${om_profil}' != 'null'    Click On Link    ${om_profil}    ELSE IF    '${libelle}' != 'null'    Click On Link    ${libelle}    ELSE    Fail


Saisir le profil
    [Tags]  om_profil

    [Documentation]    Permet de remplir le formulaire om_profil.

    [Arguments]    ${libelle}    ${hierarchie}=null

    # On saisit le libellé
    Input Text    css=#libelle    ${libelle}
    # On sélectionne le profil par son libellé
    Run Keyword If    '${hierarchie}' != 'null'    Input Text    css=#hierarchie    ${hierarchie}


Ajouter le profil depuis le menu
    [Tags]  om_profil

    [Documentation]  Ajoute un enregistrement de type 'profil' (om_profil) via le listing.

    [Arguments]    ${libelle}    ${hierarchie}=null

    #
    Depuis le listing des profils
    # On clique sur l'action Ajouter
    Click On Add Button
    #
    Saisir le profil    ${libelle}    ${hierarchie}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain    Vos modifications ont bien été enregistrées.
