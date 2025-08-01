*** Settings ***
Documentation     Actions spécifiques aux éléments de la table 'om_requete.

*** Keywords ***
Depuis le listing des requêtes
    [Tags]  om_requete
    [Documentation]  Accède au listing des requêtes.

    Depuis le listing  om_requete


Depuis le tableau des requêtes
    [Tags]  om_requete
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis le listing des requêtes`.

    Depuis le listing des requêtes


Ajouter la requête
    [Tags]  om_requete
    [Documentation]  Ajoute un enregistrement de type 'requête' (om_requete).
    [Arguments]  ${code}=null  ${libelle}=null  ${description}=null  ${type}=null  ${requete}=null  ${merge_fields}=null  ${classe}=null  ${methode}=null

    Depuis le listing des requêtes
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir la requête  ${code}  ${libelle}  ${description}  ${type}  ${requete}  ${merge_fields}  ${classe}  ${methode}
    # On valide le formulaire
    Click On Submit Button


Saisir la requête
    [Tags]  om_requete
    [Documentation]  Remplit le formulaire
    [Arguments]  ${code}=null  ${libelle}=null  ${description}=null  ${type}=null  ${requete}=null  ${merge_fields}=null  ${classe}=null  ${methode}=null

    Run Keyword If  '${code}' != 'null'  Input Text    code    ${code}
    Run Keyword If  '${libelle}' != 'null'  Input Text    libelle    ${libelle}
    Run Keyword If  '${description}' != 'null'  Input Text    description    ${description}

    Run Keyword If  '${type}' != 'null'  Select From List By Value    type    ${type}
    Sleep  1

    Run Keyword If  '${requete}' != 'null'  Input Text    requete    ${requete}
    Run Keyword If  '${merge_fields}' != 'null'  Input Text    merge_fields    ${merge_fields}
    Run Keyword If  '${classe}' != 'null'  Input Text    classe    ${classe}
    Run Keyword If  '${methode}' != 'null'  Input Text    methode    ${methode}
