*** Settings ***
Documentation  Actions spécifiques aux collectivités.

*** Keywords ***
Depuis le listing des collectivités
    [Tags]  om_collectivite
    [Documentation]  Accède au listing des collectivités.

    Depuis le listing  om_collectivite


Depuis le tableau des collectivités
    [Tags]  om_collectivite
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis le listing des collectivités`.

    Depuis le listing des collectivités


Depuis le contexte de la collectivité
    [Tags]  om_collectivite
    [Documentation]  Accède à la fiche de consultation de la collectivité.
    [Arguments]  ${libelle}=null  ${om_collectivite}=null

    Depuis le listing des collectivités
    # On recherche la collectivité
    Run Keyword If    '${om_collectivite}' != 'null'    Use Simple Search    Collectivité    ${om_collectivite}    ELSE IF    '${libelle}' != 'null'    Use Simple Search    libellé    ${libelle}    ELSE    Fail
    # On clique sur la collectivité
    Run Keyword If    '${om_collectivite}' != 'null'    Click On Link    ${om_collectivite}    ELSE IF    '${libelle}' != 'null'    Click On Link    ${libelle}    ELSE    Fail


Ajouter la collectivité depuis le menu
    [Tags]  om_collectivite
    [Documentation]  Ajoute un enregistrement de type 'collectivité' (om_collectivite) via le listing.
    [Arguments]  ${libelle}  ${niveau}

    Depuis le listing des collectivités
    # On clique sur l'icone d'ajout
    Click On Add Button
    # On remplit le formulaire
    Saisir la collectivité  ${libelle}  ${niveau}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.


Saisir la collectivité
    [Tags]  om_collectivite
    [Documentation]  Permet de remplir le formulaire d'une collectivité.
    [Arguments]  ${libelle}  ${niveau}

    # On saisit le libellé
    Input Text  libelle  ${libelle}
    # On sélectionne le niveau
    Select From List By Label  niveau  ${niveau}
