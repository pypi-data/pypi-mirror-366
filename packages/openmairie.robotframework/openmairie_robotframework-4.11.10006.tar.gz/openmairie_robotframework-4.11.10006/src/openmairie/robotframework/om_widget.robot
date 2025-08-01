*** Settings ***
Documentation  Actions spécifiques aux widgets dashboard.

*** Keywords ***
Depuis la composition du tableau de bord
    [Tags]

    Go To    ${PROJECT_URL}${OM_ROUTE_FORM}&obj=om_dashboard&action=4&idx=0
    La page ne doit pas contenir d'erreur


Ajouter un widget
    [Documentation]  Ajoute un widget depuis le formulaire d'ajout
    ...
    ...  Exemple :
    ...
    ...  | &{information_widget}=  Create Dictionary
    ...  | ...  libelle=Reprise Sur Abandon | DATE DE HIER
    ...  | ...  type=file - le contenu du widget provient d'un script sur le serveur
    ...  | ...  script=reprise_sur_abandon 
    ...  | ...  arguments=datecreation_min=today -1 day
    ...  
    ...  OU
    ...  
    ...  | &{information_widget}=  Create Dictionary
    ...  | ...  libelle=Reprise Sur Abandon | DATE DE HIER
    ...  | ...  type=web - le contenu du widget provient du champs texte ci-dessous
    ...  | ...  lien=[LIEN]
    ...  | ...  texte=datecreation_min=today -1 day
    ...
    [Arguments]  ${values}

    # Depuis le formulaire d'ajout d'un widget on renseigne les valeurs en parametres et on soumet le formulaire.
    Go To  ${PROJECT_URL}${OM_ROUTE_FORM}&obj=om_widget&action=0&retour=form
    Saisir les valeurs dans le formulaire d'un widget  ${values}
    Click On Submit Button
    La page ne doit pas contenir d'erreur
    ${widget_id} =  Get Text  css=#om_widget
    [Return]  ${widget_id}

Supprimer un widget
    [Documentation]  Supprime un widget passé en parametre
    ...
    ...  Exemple :
    ...
    ...  Supprimer un widget  ${widget_id}
    ...
    [Arguments]  ${id}

    # Depuis un widget on le supprime
    Go To  ${PROJECT_URL}${OM_ROUTE_FORM}&obj=om_widget&action=3&idx=${id}
    Click Element  css=#action-form-om_widget-supprimer
    Click On Submit Button
    La page ne doit pas contenir d'erreur

Supprimer un widget depuis le tableau de bord
    [Documentation]  Supprime un widget passé en parametre du tableau de bord
    ...
    ...  Exemple :
    ...
    ...  Supprimer un widget depuis le tableau de bord  ${profil}  ${widget_id}
    ...
    [Arguments]  ${profil}  ${widget_id}

    # Depuis la composition du tableau de bord on supprime un widget
    Depuis la composition du tableau de bord
    Select From List By Label  om_profil  ${profil}
    Click Element  css=#widget_${widget_id} .ui-icon.ui-icon-closethick

Saisir les valeurs dans le formulaire d'un widget
    [Documentation]  Remplit le formulaire
    ...
    ...  Exemple :
    ...
    ...  | &{information_widget}=  Create Dictionary
    ...  | ...  libelle=Reprise Sur Abandon | DATE DE HIER
    ...  | ...  type=file - le contenu du widget provient d'un script sur le serveur
    ...  | ...  script=reprise_sur_abandon 
    ...  | ...  arguments=datecreation_min=today -1 day
    ...  
    ...  OU
    ...  
    ...  | &{information_widget}=  Create Dictionary
    ...  | ...  libelle=Reprise Sur Abandon | DATE DE HIER
    ...  | ...  type=web - le contenu du widget provient du champs texte ci-dessous
    ...  | ...  lien=[LIEN]
    ...  | ...  texte=datecreation_min=today -1 day
    ...
    [Arguments]  ${values}
    
    Si "libelle" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "type" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "script" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "arguments" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "lien" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "texte" existe dans "${values}" on execute "Input Text" dans le formulaire


Ajouter le widget au tableau de bord
    [Tags]
    [Arguments]  ${profil}  ${widget}

    # On ouvre le tableau de composition
    Depuis la composition du tableau de bord
    # On sélectionne le profil
    Select From List By Label  om_profil  ${profil}
    # On clique le bouton "+"
    Wait Until Element Is Visible  css=a > span.add-25
    Click Element  css=a > span.add-25
    # On sélectionne le widget
    Wait Until Element Is Visible  css=select[name="widget"]
    Select From List By Label  css=select[name="widget"]  ${widget}
    # On valide l'ajout
    Click Element  css=#widget_add_form > input[type=button]
    # On vérifie l'ajout
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Page Should Contain  ${widget}


Ajouter le widget depuis le tableau de bord
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Ajouter un widget`.
    [Arguments]  ${libelle}  ${type}  ${champ1}  ${champ2}

    # Déplacement depuis le tableau de bord au sous-menu widget
    Go To Submenu In Menu    administration    om_widget
    Le titre de la page doit être  Administration > Tableaux De Bord > Widget
    First Tab Title Should Be    widget
    Submenu In Menu Should Be Selected    administration    om_widget

    # Ajout d'un nouveau widget
    Click Element    css=#action-tab-om_widget-corner-ajouter
    La page ne doit pas contenir d'erreur

    # Vérifie que l'on se trouve au bon endroit
    Le titre de la page doit être  Administration > Tableaux De Bord > Widget
    First Tab Title Should Be    widget
    Submenu In Menu Should Be Selected    administration    om_widget

    # Utilise le keyword Saisir widget
    Saisir le widget    ${libelle}  ${type}  ${champ1}  ${champ2}

    # Valide la saisie
    Click On Submit Button
    La page ne doit pas contenir d'erreur
    Valid Message Should Be    Vos modifications ont bien été enregistrées.

    Click On Back Button
    Le titre de la page doit être  Administration > Tableaux De Bord > Widget
    First Tab Title Should Be    widget
    Submenu In Menu Should Be Selected    administration    om_widget



Saisir le widget
    [Documentation]  *DEPRECATED* Remplacé par le keyword `Saisir les valeurs dans le formulaire d'un widget`.
    [Arguments]  ${libelle}  ${type}  ${champ1}  ${champ2}

    # Si les champ de type web sont compléter, Saisie d'un widget de type web
    Run Keyword If    '${type}' == 'web'    Select From List By Value   css=#type    ${type}
    Run Keyword If    '${type}' == 'web'    Input Text    css=#libelle    ${libelle}
    Run Keyword If    '${type}' == 'web'    Input Text    css=#lien    ${champ1}
    Run Keyword If    '${type}' == 'web'    Input Text    css=#texte    ${champ2}

    # Si les champ de type file sont compléter, Saisie d'un widget de type file
    Run Keyword If    '${type}' == 'file'    Select From List By Value    css=#type    ${type}
    Run Keyword If    '${type}' == 'file'    Input Text    css=#libelle    ${libelle}
    Run Keyword If    '${type}' == 'file'    Select From List By Value    css=#script    ${champ1}
    Run Keyword If    '${type}' == 'file'    Input Text    css=#arguments    ${champ2}


Depuis le contexte du widget
    [Documentation]  Accède au formulaire
    [Arguments]  ${om_widget}

    # On accède au tableau
    Depuis le listing  om_widget
    # On recherche l'enregistrement
    Use Simple Search  Tous  ${om_widget}
    # On clique sur le résultat
    Click On Link  ${om_widget}
    # On vérifie qu'il n'y a pas d'erreur
    La page ne doit pas contenir d'erreur
