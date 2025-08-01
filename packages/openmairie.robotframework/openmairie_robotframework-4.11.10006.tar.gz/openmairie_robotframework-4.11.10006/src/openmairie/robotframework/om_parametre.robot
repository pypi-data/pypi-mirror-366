*** Settings ***
Documentation  Actions spécifiques aux paramètres.

*** Keywords ***
Depuis le listing des paramètres
    [Tags]  om_parametre
    [Documentation]  Accède au listing des paramètres.

    Depuis le listing  om_parametre


Depuis le tableau des paramètres
    [Tags]  om_parametre
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis le listing des paramètres`.

    Depuis le listing des paramètres


Depuis le contexte du paramètre
    [Tags]  om_parametre
    [Documentation]  Accède à la fiche de consultation du paramètre.
    [Arguments]  ${libelle}=null  ${valeur}=null

    Depuis le listing des paramètres
    # On recherche le paramètre
    Run Keyword If    '${valeur}' != 'null'    Use Simple Search    valeur    ${valeur}    ELSE IF    '${libelle}' != 'null'    Use Simple Search    libellé    ${libelle}    ELSE    Fail
    # On clique sur le paramètre
    Run Keyword If    '${valeur}' != 'null'    Click On Link    ${valeur}    ELSE IF    '${libelle}' != 'null'    Click On Link    ${libelle}    ELSE    Fail


Ajouter le paramètre depuis le menu
    [Tags]  om_parametre
    [Documentation]  Ajoute un enregistrement de type 'paramètre' (om_parametre) via le listing.
    [Arguments]  ${libelle}  ${valeur}  ${collectivite}

    Depuis le listing des paramètres
    # On clique sur l'icone d'ajout
    Click On Add Button
    # On remplit le formulaire
    Saisir le paramètre  ${libelle}  ${valeur}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Modifier le paramètre
    [Tags]  om_parametre
    [Documentation]  Permet de modifier un paramètre
    [Arguments]  ${libelle}  ${valeur}  ${collectivite}=null

    Depuis le listing des paramètres
    # On recherche puis on clique sur le paramètre souhaité
    Depuis le contexte du paramètre  ${libelle}
    # On clique sur le bouton modifier
    Click On Form Portlet Action  om_parametre  modifier
    # On remplit le formulaire
    Saisir le paramètre  ${libelle}  ${valeur}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Saisir le paramètre
    [Tags]  om_parametre
    [Documentation]  Permet de remplir le formulaire d'un paramètre.
    [Arguments]  ${libelle}  ${valeur}  ${collectivite}

    # On saisit le libellé
    Input Text  libelle  ${libelle}
    # On saisit la valeur
    Input Text  valeur  ${valeur}
    # On sélectionne la collectivité si définie
    Run Keyword If  '${collectivite}' != 'null'  Select From List By Label  om_collectivite  ${collectivite}

Supprimer le paramètre
    [Tags]  om_parametre
    [Documentation]  Permet de supprimer le paramètre
    [Arguments]  ${libelle}=null  ${valeur}=null

    # On accède à l'enregistrement
    Depuis le contexte du paramètre  ${libelle}  ${valeur}
    # On clique sur le bouton supprimer
    Click On Form Portlet Action  om_parametre  supprimer
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  La suppression a été correctement effectuée.
