*** Settings ***
Documentation  'om_logo'

*** Keywords ***
Depuis le listing des logos
    [Tags]  om_logo
    [Documentation]  Accède au listing des logos.
    Depuis le listing  om_logo

Depuis le contexte du logo
    [Tags]  om_logo
    [Documentation]  Accède à la fiche de consultation du logo.
    ...
    ...  *om_logo* est le libellé du logo
    [Arguments]    ${om_logo}

    # On accède au tableau
    Depuis le listing des logos
    # On recherche l'enregistrement
    Use Simple Search    Tous    ${om_logo}
    # On clique sur le résultat
    Click On Link    ${om_logo}
    # On vérifie qu'il n'y a pas d'erreur
    La page ne doit pas contenir d'erreur

Ajouter le logo
    [Tags]  om_logo
    [Documentation]  Ajoute un enregistrement de type 'logo' (om_logo).
    [Arguments]    ${id}    ${libelle}    ${fichier}    ${description}=null    ${resolution}=null    ${actif}=null    ${om_collectivite}=null

    # On accède au tableau
    Depuis le listing  om_logo
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir le logo    ${id}    ${libelle}    ${fichier}    ${description}    ${resolution}    ${actif}    ${om_collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.


Modifier le logo
    [Tags]  om_logo
    [Documentation]  Modifie l'enregistrement
    [Arguments]    ${id}=null    ${libelle}=null    ${fichier}=null   ${description}=null    ${resolution}=null    ${actif}=null    ${om_collectivite}=null

    # On accède à l'enregistrement
    Depuis le contexte du logo    ${id}
    # On clique sur le bouton modifier
    Click On Form Portlet Action    om_logo    modifier
    # On saisit des valeurs
    Saisir le logo    ${id}    ${libelle}    ${fichier}    ${description}    ${resolution}    ${actif}    ${om_collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Supprimer le logo
    [Tags]  om_logo
    [Documentation]  Supprime l'enregistrement
    [Arguments]    ${logo}

    # On accède à l'enregistrement
    Depuis le contexte du logo    ${logo}
    # On clique sur le bouton supprimer
    Click On Form Portlet Action    om_logo    supprimer
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  La suppression a été correctement effectuée.

Saisir le logo
    [Tags]  om_logo
    [Documentation]  Remplit le formulaire
    [Arguments]    ${id}=null    ${libelle}=null    ${fichier}=null    ${description}=null    ${resolution}=null    ${actif}=null    ${om_collectivite}=null

    Run Keyword If  '${id}' != 'null'  Input Text    id    ${id}
    Run Keyword If  '${libelle}' != 'null'  Input Text    libelle    ${libelle}
    Run Keyword If  '${description}' != 'null'  Input Text    description    ${description}
    Run Keyword If  '${fichier}' != 'null'  Add File    fichier    ${fichier}
    Run Keyword If  '${resolution}' != 'null'  Input Text    resolution    ${resolution}
    Run Keyword If  '${actif}' != 'null'  Select Checkbox    actif
    Run Keyword If  '${om_collectivite}' != 'null'  Select From List By Value    om_collectivite    ${om_collectivite}
