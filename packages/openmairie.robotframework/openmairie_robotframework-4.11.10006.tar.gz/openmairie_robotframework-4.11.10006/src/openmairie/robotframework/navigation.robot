*** Settings ***
Documentation     Actions navigation

*** Keywords ***
Depuis la page d'accueil
    [Tags]
    [Arguments]  ${expected_username}  ${password}
    [Documentation]    L'objet de ce 'Keyword' est de positionner l'utilisateur
    ...    sur la page de login ou son tableau de bord si on le fait se connecter.

    # Depuis la page d'accueil du projet, on vérifie si l'utilisateur est
    # authentifié à l'application en inspectant le titre de la page : soit
    # nous sommes sur la page de login et l'utilisateur n'est pas authentifié
    # soit nous sommes sur une autre page et l'utilisateur est authentifié.
    Go To  ${PROJECT_URL}
    La page ne doit pas contenir d'erreur
    ${is_not_authenticated} =  Run Keyword And Return Status
    ...  Le titre de la page doit être  ${OM_TITLE_LOGIN}
    ${is_authenticated} =  Evaluate  not ${is_not_authenticated}

    # On récupère le login de l'utilisateur authentifié pour le comparer à
    # celui de l'utilisateur attendu. La variable est initialisée à None dans
    # le cas où aucun utilisateur n'est actuellement authentifié.
    ${authenticated_username} =  Set Variable  None
    ${authenticated_username} =  Run Keyword If  ${is_authenticated}
    ...  Get Text  css=#actions li.action-login

    # Si l'utilisateur authentifié est celui attendu alors on sort du Keyword.
    Run Keyword If  "${authenticated_username}"=="${expected_username}"
    ...  Return From Keyword  L'utilisateur souhaité est déjà connecté.

    # Si l'utilisateur authentifié n'est pas celui attendu alors on le
    # déconnecte.
    Run Keyword If  ${is_authenticated}
    ...  Click Link  css=#actions a.actions-logout

    # On se connecte avec l'utilisateur attendu.
    S'authentifier  ${expected_username}  ${password}


Depuis la page de login
    [Tags]  global
    [Documentation]  Accède à la page de login.
    ...
    ...  L'utilisateur ne doit pas être connecté sinon le keyword va échouer.

    Go To  ${PROJECT_URL}
    Le titre de la page doit être  ${OM_TITLE_LOGIN}
    Title Should Be  ${TITLE}
    La page ne doit pas contenir d'erreur


Go To Dashboard
    [Tags]
    Click Link    css=#logo h1 a.logo
    Le titre de la page doit être  ${OM_TITLE_DASHBOARD}
    La page ne doit pas contenir d'erreur


Depuis le listing
    [Tags]  module_tab
    [Arguments]  ${obj}
    [Documentation]  Accède au listing.
    ...
    ...  *obj* est l'objet du listing.

    Go To  ${PROJECT_URL}${OM_ROUTE_TAB}&obj=${obj}
    La page ne doit pas contenir d'erreur


S'authentifier
    [Tags]
    [Arguments]    ${username}=${ADMIN_USER}    ${password}=${ADMIN_PASSWORD}
    Input Username    ${username}
    Input Password    ${password}
    #
    Click Element    login.action.connect
    #
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain    css=#actions a.actions-logout    Déconnexion
    #
    La page ne doit pas contenir d'erreur


Se déconnecter
    [Tags]
    Le titre de la page doit être  ${OM_TITLE_DASHBOARD}
    Click Link    css=#actions a.actions-logout
    Le titre de la page doit être  ${OM_TITLE_LOGIN}
    La page ne doit pas contenir d'erreur


Reconnexion
    [Tags]
    [Arguments]    ${username}=null    ${password}=null
    ${connected_login} =    Get Text    css=#actions ul.actions-list li.action-login
    # On se déconnecte si user logué différent
    Run Keyword If   '${username}' != '${connected_login}'    Se déconnecter
    # On se reconnecte si user spécifié et différent du logué
    Run Keyword If   '${username}' != 'null' and '${password}' != 'null' and '${username}' != '${connected_login}'    S'authentifier    ${username}    ${password}


Ouvrir le navigateur
    [Tags]  global
    [Arguments]    ${width}=1024    ${height}=768
    Open Browser    ${PROJECT_URL}    ${BROWSER}
    Set Window Size    ${width}    ${height}
    Set Selenium Speed    ${DELAY}
    Le titre de la page doit être  ${OM_TITLE_LOGIN}
    Title Should Be    ${TITLE}

Ouvrir le navigateur et s'authentifier
    [Tags]  global
    [Arguments]    ${username}=${ADMIN_USER}    ${password}=${ADMIN_PASSWORD}
    Ouvrir le navigateur
    S'authentifier    ${username}    ${password}

Fermer le navigateur
    [Tags]  global
    [Documentation]  Ferme le navigateur.

    Close Browser


Le titre de la page doit être
    [Tags]  global
    [Arguments]  ${message}  ${ignore_case}=${OM_IGNORE_CASE}
    [Documentation]  Vérifie le titre de la page.
    ...
    ...  L'élément qui correspond au titre de la page : <div id="title"><h2>TITRE DE LA PAGE</h2></div>
    ...
    ...  **message** est la chaîne de caractères à vérifier.
    ...  **ignore_case** est un booléen qui indique si on s'attache à la casse.

    Wait Until Element Is Visible  css=#title h2
    Element Text Should Be  css=#title h2  ${message}  ignore_case=${ignore_case}


Le titre de la page doit contenir
    [Tags]  global
    [Arguments]  ${message}  ${ignore_case}=${OM_IGNORE_CASE}
    [Documentation]  Vérifie que le titre de la page contient.
    ...
    ...  L'élément qui correspond au titre de la page : <div id="title"><h2>TITRE DE LA PAGE</h2></div>
    ...
    ...  **message** est la chaîne de caractères à vérifier.
    ...  **ignore_case** est un booléen qui indique si on s'attache à la casse.

    Wait Until Element Is Visible  css=#title h2
    Element Should Contain  css=#title h2  ${message}  ignore_case=${ignore_case}


Page SubTitle Should Contain
    [Tags]
    [Arguments]    ${subcontainer_id}    ${messagetext}
    Wait Until Element Is Visible    css=#${subcontainer_id} div.subtitle h3
    Element Should Contain    css=#${subcontainer_id} div.subtitle h3    ${messagetext}

Page SubTitle Should Be
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Element Is Visible    css=div.subtitle h3
    Element Text Should Be    css=div.subtitle h3    ${messagetext}


La page ne doit pas contenir d'erreur
    [Tags]  global
    [Documentation]  Vérifie qu'aucune erreur n'est présente sur la page.
    ...
    ...  Les chaînes de caractères considérées comme 'erreur' sont :
    ...  - *Erreur de base de données*
    ...  - *Fatal error*
    ...  - *Parse error*
    ...  - *Notice*
    ...  - *Warning*

    Page Should Not Contain    Erreur de base de données.
    Page Should Not Contain    Fatal error
    Page Should Not Contain    Parse error
    Page Should Not Contain    Notice
    Page Should Not Contain    Warning


L'onglet doit être présent
    [Tags]
    [Documentation]
    [Arguments]    ${id}=null    ${libelle}=null

    #
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li a#    ${id}
    #
    Element Text Should Be    ${locator}    ${libelle}


L'onglet doit être sélectionné
    [Tags]
    [Documentation]
    [Arguments]    ${id}=null    ${libelle}=null

    #
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li.ui-tabs-selected a#    ${id}
    #
    Element Text Should Be    ${locator}    ${libelle}


On clique sur l'onglet
    [Tags]
    [Documentation]
    [Arguments]    ${id}=null    ${libelle}=null

    #
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li a#    ${id}
    #
    L'onglet doit être présent    ${id}    ${libelle}
    #
    Click Element    ${locator}
    #
    L'onglet doit être sélectionné    ${id}    ${libelle}
    #
    Sleep    1
    #
    La page ne doit pas contenir d'erreur


Sélectionner la fenêtre et vérifier l'URL puis fermer la fenêtre
    [Tags]

    [Documentation]  Permet de vérifier que la nouvelle fenêtre de Firefox qui a pour
    ...  titre ${identifiant_fenetre} pointe bien sur ${URL}.
    ...  Si ${correspondance_exacte} vaut false alors ${URL} est une liste et on vérifie
    ...  que l'url en contient chaque élément.

    [Arguments]  ${identifiant_fenetre}  ${URL}  ${correspondance_exacte}=true

    # Sélection de la nouvelle fenêtre
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Select Window  ${identifiant_fenetre}
    Run Keyword If  '${correspondance_exacte}' == 'true'   Location Should Be  ${URL}
    Run Keyword If  '${correspondance_exacte}' == 'false'  L'URL doit contenir  ${URL}
    # Fermeture de la nouvelle fenêtre
    Close Window
    # Sélection de la fenêtre courante
    Select Window

L'URL doit contenir
    [Arguments]    ${text_list}
    [Documentation]  Permet de vérifier ce que contient l'URL

    :FOR  ${text}  IN  @{text_list}
    \    Location Should Contain  ${text}


L'onglet ne doit pas être présent
    [Documentation]  Vérifie que l'onglet n'est pas affiché.
    [Arguments]  ${id}=null

    ${locator} =  Catenate  SEPARATOR=  css=#formulaire ul.ui-tabs-nav li a#  ${id}
    Element Should Not Be Visible  ${locator}




Go To Login Page
    [Tags]  global
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis la page de login`.

    Depuis la page de login


Go To Tab
    [Tags]  module_tab
    [Arguments]  ${obj}
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Depuis le listing`.

    Depuis le listing  ${obj}


Page Should Not Contain Errors
    [Tags]  utils
    [Documentation]  *DEPRECATED* Remplacé par le keyword `La page ne doit pas contenir d'erreur`.

    La page ne doit pas contenir d'erreur


Page Title Should Be
    [Tags]
    [Arguments]  ${messagetext}
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Le titre de la page doit être`.

    Le titre de la page doit être  ${messagetext}


Page Title Should Contain
    [Tags]
    [Arguments]    ${messagetext}
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Le titre de la page doit contenir`.

    Le titre de la page doit contenir  ${messagetext}


