*** Settings ***
Documentation     Fonctions et méthodes de traitement

*** Keywords ***

STR_PAD_LEFT
    [Tags]
    # ${input}      Chaîne d'entrée.
    # ${pad_length} Taille de la chaîne à retourner.
    # ${pad_string} Caractère pour combler les vides de la chaîne à retourner.
    [Arguments]    ${input}    ${pad_length}    ${pad_string}
    # On récupère le nombre de caractère de ${input}
    ${input_lenght} =    Get Length    ${input}
    # On convertit les variables en integer
    ${pad_length} =    Convert to Integer    ${pad_length}
    ${input_lenght} =    Convert to Integer    ${input_lenght}
    # On récupère le nombre de ${pad_string} à ajouter
    ${lenght} =    Evaluate    ${pad_length}-${input_lenght}
    # On déclare la variable à retourner
    ${result}    Set Variable
    # On concatène ${pad_string} pour chaque ${lenght}
    :FOR    ${INDEX}    IN RANGE    0    ${lenght}
    \    ${result} =    Catenate    SEPARATOR=    ${result}    ${pad_string}
    # On concatène au résultat ${input}
    ${result} =    Catenate    SEPARATOR=    ${result}    ${input}
    # On retourne la valeur
    [return]    ${result}

STR_REPLACE
    [Tags]
    # ${pattern}       Texte à remplacer.
    # ${replace_with}  Texte de remplacement.
    # ${string}        Chaîne à modifier.
    [Arguments]    ${pattern}    ${replace_with}    ${string}
    ${result} =    Replace String Using Regexp    ${string}    ${pattern}    ${replace_with}
    [return]    ${result}

Sans espace
    [Tags]
    [Arguments]  ${string}
    ${result} =  STR_REPLACE  ${SPACE}  ${EMPTY}  ${string}
    [return]  ${result}

Date du jour FR
    [Tags]
    ${ret} =  Date du jour au format dd/mm/yyyy
    [return]  ${ret}

Date du jour EN
    [Tags]
    ${ret} =  Date du jour au format yyyy-mm-dd
    [return]  ${ret}

Date du jour au format dd/mm/yyyy
    [Tags]
    ${yyyy} =  Get Time  year
    ${mm} =  Get Time  month
    ${dd} =  Get Time  day
    [return]  ${dd}/${mm}/${yyyy}

Date du jour au format yyyy-mm-dd
    [Tags]
    ${yyyy} =  Get Time  year
    ${mm} =  Get Time  month
    ${dd} =  Get Time  day
    [return]  ${yyyy}-${mm}-${dd}

Date du jour au format yyyymmdd
    [Tags]
    ${yyyy} =  Get Time  year
    ${mm} =  Get Time  month
    ${dd} =  Get Time  day
    [return]  ${yyyy}${mm}${dd}

Convertir une date du format dd/mm/yyyy au format yyyy-mm-dd
    [Tags]
    [Arguments]  ${string}

    ${yyyy} =  Get Substring  ${string}  -4
    ${mm} =  Get Substring  ${string}  3  5
    ${dd} =  Get Substring  ${string}  0  2
    [return]  ${yyyy}-${mm}-${dd}

# Appel une ressource REST fail sur =! 200 et retourne le message
Appeler le web service
    [Tags]
    [Documentation]  Appel une ressource REST et retourne son message,
    ...    fail si != de 200

    [Arguments]    ${methods}    ${ressource}    ${json}

    Run Keyword If    '${methods}' == 'null'    Fail    No HTTP method

    ${session} =    Catenate    http${PROJECT_NAME}

    Create Session    ${session}    ${PROJECT_URL}services/rest_entry.php
    ${headers} =    Create Dictionary    Content-Type=application/json
    ${resp} =    Run Keyword If    '${methods}' == 'Get'    Get Request    ${session}    /${ressource}    headers=${headers}
    ...    ELSE IF    '${methods}' == 'Post'    Post Request    ${session}    /${ressource}    data=${json}    headers=${headers}
    ...    ELSE IF    '${methods}' == 'Put'    Put Request    ${session}    /${ressource}    data=${json}    headers=${headers}
    ...    ELSE IF    '${methods}' == 'Delete'    Delete Request    ${session}    /${ressource}    data=${json}    headers=${headers}
    ...    ELSE    Fail    No HTTP method

    [return]    ${resp}

Vérifier le code retour du web service et retourner son message
    [Tags]

    [Arguments]    ${methods}    ${ressource}    ${json}    ${code}
    ${resp} =    Appeler le web service    ${methods}    ${ressource}    ${json}
    Should be Equal    '${resp.status_code}'    '${code}'

    ${data} =    To Json    ${resp.content}
    [return]    ${data['message']}

Vérifier le code retour du web service et vérifier que son message contient
    [Tags]
    [Documentation]  XXX Si le message reçu ou à vérifier contient des
    ...  apostrophes il va y avoir une erreur sur le Should Contain

    [Arguments]    ${methods}    ${ressource}    ${json}    ${code}    ${message}
    ${resp} =    Appeler le web service    ${methods}    ${ressource}    ${json}
    Should be Equal    '${resp.status_code}'    '${code}'

    ${data} =    To Json    ${resp.content}
    ${is_message_exist} =    Run Keyword And Return Status    Get From Dictionary    ${data}    message
    Run Keyword If    ${is_message_exist}    Should Contain    ${data['message']}    ${message}

Vérifier le code retour et la réponse JSON du web service
    [Tags]

    [Arguments]    ${methods}    ${ressource}    ${json}    ${code}    ${json_return}
    ${resp} =    Appeler le web service    ${methods}    ${ressource}    ${json}

    Should be Equal    '${resp.status_code}'    '${code}'
    Should be Equal  '${json_return}'  '${resp.content}'

Vérifier le code retour du web service et vérifier que son message est
    [Tags]

    [Arguments]    ${methods}    ${ressource}    ${json}    ${code}    ${message}
    ${resp} =    Appeler le web service    ${methods}    ${ressource}    ${json}
    Should be Equal    '${resp.status_code}'    '${code}'
    ${data} =    To Json    ${resp.content}
    ${is_message_exist} =    Run Keyword And Return Status    Get From Dictionary    ${data}    message
    Run Keyword If    ${is_message_exist}    Should be Equal    '${data['message']}'    '${message}'


Si "${key}" existe dans "${collection}" on execute "${keyword}" dans le formulaire
    [Tags]

    ${exist} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${collection}    ${key}
    Run Keyword If    ${exist} == True    ${keyword}    ${key}    ${collection.${key}}

Si "${key}" existe dans "${collection}" on attend que l'élément soit visible
    [Tags]

    ${exist} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${collection}    ${key}
    Run Keyword If    ${exist} == True    Wait Until Element is Visible    ${key}

Si "${key}" existe dans "${collection}" on execute "${keyword}" dans "${subform}"
    [Tags]

    ${exist} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${collection}    ${key}
    Run Keyword If    ${exist} == True    ${keyword}    css=#sousform-${subform} #${key}    ${collection.${key}}

Si "${key}" existe dans "${collection}" on execute "${keyword}" sur "${locator:[^"]+}"
    [Tags]

    [Documentation]  Ajout d'une regex sur le 4ème argument, afin que RobotFramework ne
    ...  confonde pas ce mot-clé avec les mots-clés semblables.

    ${exist} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${collection}    ${key}
    Run Keyword If    ${exist} == True    Get Value From Dictionary  ${collection}  ${key}
    Run Keyword If    ${exist} == True    ${keyword}    ${locator}    ${value}

Si "${key}" existe dans "${collection}" on execute "${keyword}" sur "${locator}" sans valeur
    [Tags]

    [Documentation]  Ce mot-clé sert dans le cas d'un appel à un mot-clé ${keyword} avec un
    ...  seul paramètre : locator. Par ex :
    ...  Si "" existe dans "" on execute "Click Element" sur "".

    ${exist} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${collection}    ${key}
    Run Keyword If    ${exist} == True    ${keyword}    ${locator}

Si "${key}" existe dans "${collection}" on execute "${keyword:[^"]+}"
    [Tags]

    [Documentation]  Ce mot-clé sert dans le cas d'un appel à un mot-clé ${keyword} avec un
    ...  seul paramètre : value. Par ex : Si "" existe dans "" on execute "Saisir...".
    ...  Ajout d'une regex sur le 3ème argument, afin que RobotFramework ne confonde pas
    ...  ce mot-clé avec les mots-clés semblables.

    ${exist} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${collection}    ${key}
    Run Keyword If    ${exist} == True    Get Value From Dictionary  ${collection}  ${key}
    Run Keyword If    ${exist} == True    ${keyword}    ${value}


Si "${key}" existe dans "${collection}" on execute "${keyword}" sur la liste dans le formulaire
    [Tags]

    ${exist} =    Run Keyword And Return Status    Dictionary Should Contain Key    ${collection}    ${key}
    Return From Keyword If  ${exist} != True  0
    Get Value From Dictionary  ${collection}  ${key}
    @{value} =    Convert To List    ${value}
    Run Keyword  ${keyword}    ${key}    @{value}


Si "${key}" existe dans "${collection}" on sélectionne la valeur sur l'autocomplete "${autocomplete}" dans le formulaire
    [Tags]

    ${exist} =  Run Keyword And Return Status  Dictionary Should Contain Key  ${collection}  ${key}
    Return From Keyword If  ${exist} != True  0
    Get Value From Dictionary  ${collection}  ${key}
    Input Text  css=#autocomplete-${autocomplete}-search    ${value}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Click On Link  ${value}


Get Value From Dictionary
    [Tags]

    [Arguments]  ${collection}  ${key}

    ${value} =  Get From Dictionary  ${collection}  ${key}
    Set Suite Variable  ${value}


Input Datepicker From Css Selector
    [Tags]
    [Arguments]    ${selector}    ${date}

    # On clique sur l'image du datepicker
    Click Image    ${selector} + .ui-datepicker-trigger
    # On récupère le jour
    ${day} =    Get Substring    ${date}    0    2
    # On récupère le mois
    ${month} =     Get Substring    ${date}    3    5
    # On récupère l'année
    ${year} =    Get Substring    ${date}    6
    # Récupère le premier chiffre de la date
    ${day_first_character} =    Get Substring    ${day}    0    1
    # Récupère le deuxième chiffre de la date
    ${day_second_character} =    Get Substring    ${day}    1    2
    # On fait -1 sur le mois pour avoir la value du datepicker
    ${month} =    Convert to Integer    ${month}
    ${datepicker_month} =    Evaluate    ${month}-1
    ${datepicker_month} =    Convert to String    ${datepicker_month}
    # On sélectionne le mois
    Wait Until Keyword Succeeds     10 sec     ${RETRY_INTERVAL}    Select From List By Value    css=.ui-datepicker-month    ${datepicker_month}
    # On sélectionne l'année
    Select From List By Value    css=.ui-datepicker-year    ${year}
    # On sélectionne le jour, sur un caractère ou deux selon la valeur du premier
    Run keyword If    '${day_first_character}' == '0'    Click Link    ${day_second_character}    ELSE    Click Link    ${day}
    # On attend le temps que le datepicker ne soit plus affiché
    Sleep     1


Télécharger un fichier
    [Tags]
    [Arguments]  ${COOKIE_NAME}  ${URL}  ${OUTPUT_DIR}  ${FILENAME}=null
    [Documentation]  Mot-clé permettant de télécharger un fichier dans le contexte d'une
    ...  application openMairie. Le paramètre "cookie" est le nom du cookie de session du
    ...  navigateur, par exemple "openads".

    # Récupération de la valeur du cookie de session
    ${COOKIE} =  Get Cookie  ${COOKIE_NAME}
    # Téléchargement du fichier dans le dossier tests/ et log de la sortie console
    ${rc}  ${output}  Run and Return RC And Output  curl --header "Cookie: ${COOKIE_NAME}=${COOKIE.value}" -O -J -w "filename_effective:'%\{filename_effective\}'" "${URL}"
    Log  ${output}
    # Extraction du nom de fichier tel qu'il est nommé sur le serveur
    ${match}  ${group1}  ${OUTPUT_NAME} =  Should Match Regexp  ${output}  (filename_effective:')([^\']*)
    # Si le nom de fichier a été passé en paramètre, on renomme le fichier et on affecte
    # le nouveau nom à la variable OUTPUT_NAME
    Run Keyword If  '${FILENAME}' != 'null'  Move File  ${OUTPUT_NAME}  ${FILENAME}
    ${OUTPUT_NAME} =  Set Variable If  '${FILENAME}' != 'null'  ${FILENAME}  ${OUTPUT_NAME}
    # Déplacement du fichier vers le chemin passé en paramètre
    Move File  ${OUTPUT_NAME}  ${OUTPUT_DIR}
    [Return]  ${OUTPUT_DIR}  ${OUTPUT_NAME}


Le fichier doit exister
    [Tags]  utils
    [Documentation]  Vérifie que le fichier dont le chemin est passé en
    ...  paramètre existe sur le système de fichiers.
    [Arguments]  ${chemin_vers_le_fichier}
    File Should Exist  ${chemin_vers_le_fichier}


Le fichier doit contenir
    [Tags]  utils
    [Documentation]  Vérifie que la chaine à vérifier passée en paramètre est
    ...  bien présente dans le contenu du fichier dont le chemin est aussi
    ...  passé en paramètre.
    [Arguments]  ${chemin_vers_le_fichier}  ${chaine_a_verifier}
    ${contenu_du_fichier} =  Get File  ${chemin_vers_le_fichier}
    Should Contain  ${contenu_du_fichier}  ${chaine_a_verifier}


Le fichier ne doit pas contenir
    [Tags]  utils
    [Documentation]  Vérifie que la chaine à vérifier passée en paramètre
    ...  n'est pas présente dans le contenu du fichier dont le chemin est aussi
    ...  passé en paramètre.
    [Arguments]  ${chemin_vers_le_fichier}  ${chaine_a_verifier}
    ${contenu_du_fichier} =  Get File  ${chemin_vers_le_fichier}
    Should Not Contain  ${contenu_du_fichier}  ${chaine_a_verifier}


Les métadonnées (clé/valeur) doivent être présentes dans le fichier
    [Tags]  utils
    [Arguments]  ${md}  ${chemin_vers_le_fichier}
    #
    ${content_file} =  Get File  ${chemin_vers_le_fichier}
    ${items}=  Get Dictionary Items  ${md}
    :FOR  ${key}  ${value}  IN  @{items}
    \  ${ret} =  Get Lines Containing String  ${content_file}  ${key}=
    \  Should Be Equal  ${ret}  ${key}=${value}


Les métadonnées (clé) ne doivent pas être présentes dans le fichier
    [Tags]  utils
    [Arguments]  ${md}  ${chemin_vers_le_fichier}
    :FOR    ${valeur}    IN    @{md}
    \    Le fichier ne doit pas contenir  ${chemin_vers_le_fichier}  ${valeur}=


Récupérer le chemin vers le fichier correspondant à l'uid
    [Tags]  utils
    [Arguments]  ${uid}
    ${uid_folder_level_1} =  Get Substring  ${uid}  0  2
    ${uid_folder_level_2} =  Get Substring  ${uid}  0  4
    ${path} =  Set Variable  ..${/}var${/}filestorage${/}${uid_folder_level_1}${/}${uid_folder_level_2}${/}${uid}
    [Return]  ${path}


Récupérer le chemin vers le fichier de métadonnées correspondant à l'uid
    [Tags]  utils
    [Arguments]  ${uid}
    ${uid_folder_level_1} =  Get Substring  ${uid}  0  2
    ${uid_folder_level_2} =  Get Substring  ${uid}  0  4
    ${path} =  Set Variable  ..${/}var${/}filestorage${/}${uid_folder_level_1}${/}${uid_folder_level_2}${/}${uid}.info
    [Return]  ${path}


Activer l'option de réinitialisation du mot de passe
    Append To File
    ...  ${EXECDIR}${/}..${/}dyn${/}config.inc.php
    ...  <?php $config["password_reset"] = true; ?>
    # Si une temporisation n'est pas ajouté la modification n'est pas prise en
    # compte
    Sleep  3


Désactiver l'option de réinitialisation du mot de passe
    Append To File
    ...  ${EXECDIR}${/}..${/}dyn${/}config.inc.php
    ...  <?php $config["password_reset"] = false; ?>
    # Si une temporisation n'est pas ajouté la modification n'est pas prise en
    # compte
    Sleep  3

Créer un fichier binaire
    [Documentation]  Crée un fichier binaire de la taille définie en octets,
    ...    rempli de zéros.
    ...    
    ...    Ouvre ou crée un fichier binaire et y écrit des octets valant zéro.
    ...    
    ...    Le processus s'arrête dès que la taille du fichier atteint ou dépasse (en octets) la valeur demandée.
    ...    
    ...    Le fichier est écrasé s'il existe déja.
    ...    
    ...    Cela est utile notamment pour simuler des fichiers à manipuler
    ...    (uploads, tests de volumétrie, validation d’extensions, etc...)
    ...    
    ...    Exemple :
    ...    
    ...    ${chemin_fichier} =  Set Variable  /tmp/exemple.bin
    ...    
    ...    ${taille_octets} =  Set Variable  4096
    ...    
    ...    Créer un fichier binaire  ${chemin_fichier}  ${taille_octets}
    [Arguments]    ${chemin_fichier}    ${taille_octets}=1048576
    Run Process    python    -c
    ...    with open('${chemin_fichier}', 'wb') as f: f.write(b'0' * ${taille_octets})
    ...    shell=True

Créer un fichier texte
    [Documentation]  Crée un fichier texte de taille définie en octets,
    ...    rempli de lignes numérotées.
    ...    
    ...    Ouvre ou crée un fichier texte, ligne par ligne, chaque ligne étant numérotée sous la forme :
    ...    « Ligne X - Lorem ipsum dolor sit amet. »
    ...    
    ...    Le processus s'arrête dès que la taille du fichier atteint ou dépasse (en octets) la valeur demandée.
    ...    
    ...    Le fichier est écrasé s’il existe déjà.
    ...    
    ...    Cela est utile notamment pour simuler des fichiers à manipuler
    ...    (uploads, tests de volumétrie, validation d’extensions, etc...)
    ...    
    ...    Attention, la taille du fichier peut être inexacte à quelques octets près (jusqu'à 40/50 octets en plus de la taille paramétrée).
    ...    
    ...    Exemple:
    ...    
    ...    ${chemin_fichier} =  Set Variable  /tmp/exemple.txt
    ...    
    ...    ${taille_octets} =  Set Variable  5000
    ...    
    ...    Créer un fichier texte  ${chemin_fichier}  ${taille_octets}
    [Arguments]    ${chemin_fichier}    ${taille_octets}=1048576
    ${taille_actuelle}=    Set Variable    0
    # Suppression du fichier si il existe déjà pour être sur de la taille du fichier créé.
    # Le keyword 'Remove File' ne lève pas d'erreur si le fichier n'existe pas.
    Remove file  ${chemin_fichier}
    :FOR    ${i}    IN RANGE    0    10000000
    \    Append To File    ${chemin_fichier}    Ligne ${i} - Lorem ipsum dolor sit amet.\n
    \    ${taille_actuelle}=    Get File Size    ${chemin_fichier}
    \    Exit For Loop If    ${taille_actuelle} >= ${taille_octets}

Créer un fichier
    [Documentation]  Crée un fichier de taille définie en octets,
    ...    on peut choisir de créer soit un fichier binaire, soit un fichier texte.
    ...    
    ...    Ouvre ou crée un fichier du type voulu de la taille (en octets) demandée :
    ...    - "binaire" : contient des octets à zéro.
    ...    - "texte" : contient des lignes numérotées sous la forme « Ligne X - Lorem ipsum dolor sit amet. »
    ...    
    ...    Le processus s'arrête dès que la taille du fichier atteint ou dépasse (en octets) la valeur demandée.
    ...    
    ...    Le fichier est écrasé s’il existe déjà.
    ...    
    ...    Cela est utile notamment pour simuler des fichiers à manipuler
    ...    (uploads, tests de volumétrie, validation d’extensions, etc...)
    ...    
    ...    Attention, en type "texte" la taille du fichier peut être inexacte à quelques octets près (jusqu'à 40/50 octets en plus de la taille paramétrée).
    ...    
    ...    Exemple :
    ...    
    ...    ${chemin_fichier} =  Set Variable  /tmp/exemple.txt
    ...    
    ...    ${taille_octets} =  Set Variable  2048
    ...    
    ...    ${type} =  Set Variable  texte
    ...    
    ...    Créer un fichier  ${chemin_fichier}  ${taille_octets}  ${type}
    [Arguments]    ${chemin_fichier}    ${taille_octets}=1048576    ${type}=binaire
    Run Keyword If    '${type}' == 'binaire'    Créer un fichier binaire  ${chemin_fichier}  ${taille_octets}
    ...    ELSE    Créer un fichier texte  ${chemin_fichier}  ${taille_octets}
    ${exists}=    Run Keyword And Return Status    File Should Exist    ${chemin_fichier}
    Run Keyword If    ${exists}    Log    Le fichier ${chemin_fichier} à bien été crée
    Run Keyword Unless    ${exists}    Log    Le fichier ${chemin_fichier} n'a pas bien été crée