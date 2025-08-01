*** Settings ***
Documentation  Module 'Gen'.

*** Keywords ***
Depuis le module de génération
    [Tags]  module_gen
    [Documentation]  Accède à l'écran principal du module 'génération'.

    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}
    La page ne doit pas contenir d'erreur


Depuis l'assistant "Création d'état"
    [Tags]  module_gen
    [Documentation]  Accède à l'assistant de création d'état.

    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_etat
    La page ne doit pas contenir d'erreur


Depuis l'assistant "Création de lettre type"
    [Tags]  module_gen
    [Documentation]  Accède à l'assistant de création de lettre-type.

    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_lettretype
    La page ne doit pas contenir d'erreur


Depuis l'assistant "Création de sous-état"
    [Tags]  module_gen
    [Documentation]  Accède à l'assistant de création de sous-état.

    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_sousetat
    La page ne doit pas contenir d'erreur


Depuis l'assistant "Migration état, sous-état, lettre type"
    [Tags]  module_gen
    [Documentation]  Accède à l'assistant de migration d'ancien état, lettre-type
    ...  et sous-état.

    Go To  ${PROJECT_URL}${OM_ROUTE_MODULE_GEN}&view=editions_old
    La page ne doit pas contenir d'erreur


Générer tout
    [Tags]  module_gen
    [Documentation]  Vérifie que la regénération complète ne génère rien.
    ...
    ...  Le 'Framework' permet de générer automatiquement certains scripts en
    ...  fonction du modèle de données. Lors du développement la règle est la
    ...  suivante : toute modification du modèle de données doit entrainer
    ...  une regénération complète de tous les scripts. Pour vérifier à chaque
    ...  modification du code que la règle a bien été respectée, ce keyword
    ...  permet de lancer une génération complète. Si un fichier est généré
    ...  alors le test échoue.

    Depuis le module de génération
    Click Element  css=#gen-action-gen-all
    La page ne doit pas contenir d'erreur
    Page Should Not Contain    Erreur de droits d'écriture
    Page Should Not Contain    Génération de

