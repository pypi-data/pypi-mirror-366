*** Settings ***
Documentation  Actions spécifiques aux utilisateurs.

*** Keywords ***
Depuis le listing des utilisateurs
    [Tags]  om_utilisateur
    [Documentation]  Accède au listing des utilisateurs.

    Depuis le listing  om_utilisateur


Depuis le contexte de l'utilisateur
    [Tags]  om_utilisateur
    [Documentation]  Accède à la fiche de consultation de l'utilisateur.
    [Arguments]  ${login}=null  ${email}=null

    Depuis le listing des utilisateurs
    # On recherche l'utilisateur
    Run Keyword If    '${login}' != 'null'    Use Simple Search    login    ${login}    ELSE IF    '${email}' != 'null'    Use Simple Search    email    ${email}    ELSE    Fail
    # On clique sur l'utilisateur
    Run Keyword If    '${login}' != 'null'    Click On Link    ${login}    ELSE IF    '${email}' != 'null'    Click On Link    ${email}    ELSE    Fail


Depuis le formulaire d'ajout d'un utilisateur
    [Tags]  om_utilisateur
    [Documentation]  Accède au formulaire d'ajout d'un enregistrement de type 'utilisateur' (om_utilisateur).

    Go To  ${PROJECT_URL}${OM_ROUTE_FORM}&obj=om_utilisateur&action=0
    La page ne doit pas contenir d'erreur


Ajouter l'utilisateur
    [Tags]  om_utilisateur
    [Documentation]  Ajoute un enregistrement de type 'utilisateur' (om_utilisateur).
    [Arguments]  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}=null

    Depuis le formulaire d'ajout d'un utilisateur
    # On remplit le formulaire
    Saisir l'utilisateur  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.


Ajouter l'utilisateur depuis le menu
    [Tags]  om_utilisateur
    [Documentation]  Ajoute un enregistrement de type 'utilisateur' (om_utilisateur) via le listing.
    [Arguments]  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}=null

    Depuis le listing des utilisateurs
    # On clique sur l'icone d'ajout
    Click On Add Button
    # On remplit le formulaire
    Saisir l'utilisateur  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.


Modifier l'utilisateur
    [Tags]  om_utilisateur
    [Documentation]  Modifie un enregistrement de type 'utilisateur' (om_utilisateur).
    [Arguments]  ${nom}  ${email}  ${login}  ${password}  ${profil}  ${collectivite}=null

    Depuis le contexte de l'utilisateur  ${login}  ${email}
    # On clique sur l'icone d'ajout
    Click On Form Portlet Action  om_utilisateur  modifier
    # On remplit le formulaire
    Saisir l'utilisateur  ${nom}  ${email}  null  ${password}  ${profil}  ${collectivite}
    # On valide le formulaire
    Click On Submit Button
    # On vérifie le message de validation
    Valid Message Should Contain  Vos modifications ont bien été enregistrées.


Saisir l'utilisateur
    [Tags]  om_utilisateur
    [Documentation]  Permet de remplir le formulaire d'un utilisateur.
    [Arguments]  ${nom}=null  ${email}=null  ${login}=null  ${password}=null  ${profil}=null  ${collectivite}=null

    # On saisit le nom
    Run Keyword If  '${nom}' != 'null'  Input Text  nom  ${nom}
    # On saisit l'email
    Run Keyword If  '${email}' != 'null'  Input Text  email  ${email}
    # On saisit le login
    Run Keyword If  '${login}' != 'null'  Input Text  login  ${login}
    # On saisit le mot de passe
    Run Keyword If  '${password}' != 'null'  Input Text  pwd  ${password}
    # On sélectionne la collectivité
    Run Keyword If  '${collectivite}' != 'null'  Select From List By Label  om_collectivite  ${collectivite}
     # On sélectionne le profil
    Run Keyword If  '${profil}' != 'null'  Select From List By Label  om_profil  ${profil}

Supprimer l'utilisateur
    [Tags]  om_utilisateur
    [Documentation]  Supprime un enregistrement de type 'utilisateur' (om_utilisateur).
    [Arguments]    ${utilisateur}

    # On accède à l'enregistrement
    Depuis le contexte de l'utilisateur    ${utilisateur}
    # On clique sur le bouton supprimer
    Click On Form Portlet Action    om_utilisateur    supprimer
    # On valide le formulaire
    Click On Submit Button




Depuis le tableau des utilisateurs
    [Tags]  om_utilisateur
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis le listing des utilisateurs`.

    Depuis le listing des utilisateurs

