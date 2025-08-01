*** Settings ***
Documentation  Actions spécifiques aux lettres-types.

*** Keywords ***
Depuis le listing des lettres-types
    [Tags]  om_lettretype
    [Documentation]  Accède au listing des lettres-types.

    Depuis le listing  om_lettretype


Depuis le tableau des lettres-types
    [Tags]  om_lettretype
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis le listing des lettres-types`.

    Depuis le listing des lettres-types


Depuis le contexte de la lettre-type
    [Tags]  om_lettretype
    [Documentation]  Accède à la fiche de consultation de la lettre type.
    [Arguments]  ${id}=null  ${libelle}=null

    Depuis le listing des lettres-types
    # On recherche la lettre-type
    Run Keyword If    '${id}' != 'null'    Use Simple Search    id    ${id}    ELSE IF    '${libelle}' != 'null'    Use Simple Search    libellé    ${libelle}    ELSE    Fail
    # On clique sur la lettre-type
    Run Keyword If    '${id}' != 'null'    Click On Link    ${id}    ELSE IF    '${libelle}' != 'null'    Click On Link    ${libelle}    ELSE    Fail


Depuis le listing des lettres-types de la collectivité
    [Tags]  om_lettretype  om_collectivite
    [Documentation]  ...
    [Arguments]  ${collectivite_libelle}
    #
    Depuis le contexte de la collectivité  ${collectivite_libelle}
    #
    On clique sur l'onglet  om_lettretype  lettre type


Ajouter la lettre-type dans le contexte de la collectivité
    [Tags]  om_lettretype  om_collectivite
    [Documentation]  Ajoute un enregistrement de type 'lettre type' (om_lettretype) via le listing dans le contexte d'une collectivité.
    [Arguments]  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}=null  ${collectivite_libelle}=null  ${logo}=null
    #
    Depuis le listing des lettres-types de la collectivité  ${collectivite_libelle}
    # On clique sur l'action Ajouter
    Click On Add Button JS
    # On remplit le formulaire
    Saisir la lettre-type  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}  null  ${logo}
    # On valide le formulaire
    Click On Submit Button In Subform
    # On vérifie le message de validation
    Valid Message Should Contain In Subform  Vos modifications ont bien été enregistrées.


Modifier la lettre-type dans le contexte de la collectivité
    [Tags]  om_lettretype  om_collectivite
    [Documentation]  Permet de modifier une lettre-type
    [Arguments]  ${id}  ${libelle}=null  ${titre}=null  ${corps}=null  ${sql}=null  ${actif}=null  ${collectivite_libelle}=null  ${logo}=null
    #
    Depuis le contexte de la lettre-type dans le contexte de la collectivité  ${id}  ${libelle}  ${collectivite_libelle}
    #
    Click On SubForm Portlet Action    om_lettretype    modifier
    #
    Click On Submit Button In SubForm
    Valid Message Should Be    Vos modifications ont bien été enregistrées.
    Click On Back Button In Subform


Depuis le contexte de la lettre-type dans le contexte de la collectivité
    [Tags]  om_lettretype  om_collectivite
    [Documentation]  Accède à la fiche de consultation de la lettre type dans le contexte d'une collectivité.
    [Arguments]  ${id}=null  ${libelle}=null  ${collectivite_libelle}=null
    #
    Depuis le listing des lettres-types de la collectivité  ${collectivite_libelle}
    #
    Click On Link    ${id}
    #
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=#fieldset-sousform-om_lettretype-edition #id  ${id}


Ajouter la lettre-type depuis le menu
    [Tags]  om_lettretype
    [Documentation]  Ajoute un enregistrement de type 'lettre type' (om_lettretype) via le listing.
    [Arguments]  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}=null  ${collectivite}=null  ${logo}=null

    Depuis le listing des lettres-types
    # On clique sur l'icone d'ajout
    Click On Add Button
    # On remplit le formulaire
    Saisir la lettre-type  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}  ${collectivite}  ${logo}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Modifier la lettre-type
    [Tags]  om_lettretype
    [Documentation]  Permet de modifier une lettre-type
    [Arguments]  ${id}  ${libelle}=null  ${titre}=null  ${corps}=null  ${sql}=null  ${actif}=null  ${collectivite}=null  ${logo}=null

    Depuis le listing des lettres-types
    # On recherche puis on clique sur la lettre-type souhaitée
    Depuis le contexte de la lettre-type  ${id}
    # On clique sur le bouton modifier
    Click On Form Portlet Action  om_lettretype  modifier
    # On remplit le formulaire
    Saisir la lettre-type  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}  ${collectivite}  ${logo}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.

Saisir la lettre-type
    [Tags]  om_lettretype
    [Documentation]  Permet de remplir le formulaire d'une lettre-type.
    [Arguments]  ${id}  ${libelle}  ${titre}  ${corps}  ${sql}  ${actif}  ${collectivite}  ${logo}

    # On saisit l'id
    Run Keyword If  '${id}' != 'null'  Input Text  id  ${id}
    # On saisit le libellé
    Run Keyword If  '${libelle}' != 'null'  Input Text  css=input#libelle  ${libelle}
    # On saisit le titre
    Run Keyword If  '${titre}' != 'null'  Input HTML  titre_om_htmletat  ${titre}
    # On saisit le corps
    Run Keyword If  '${corps}' != 'null'  Input HTML  corps_om_htmletatex  ${corps}
    # On sélectionne la requête
    Run Keyword If  "${sql}" != "null"  Sélection de valeur(s)  om_sql  ${sql}
    # On coche actif si spécifié
    Run Keyword If  '${actif}' == 'true'  Select Checkbox  actif
    # On décoche actif si spécifié
    Run Keyword If  '${actif}' == 'false'  Unselect Checkbox  actif
    # On sélectionne la collectivité
    Run Keyword If  '${collectivite}' != 'null'  Select From List By Label  om_collectivite  ${collectivite}
    # On ouvre le fielset "Paramètres généraux de l'édition" si on doit modifier des valeurs
    Run Keyword If  '${logo}' != 'null'  Click Element  css=#fieldset-form-om_lettretype-parametres-generaux-de-l_edition legend
    # On sélectionne le logo
    Run Keyword If  '${logo}' != 'null'  Select From List By Label  logo  ${logo}
