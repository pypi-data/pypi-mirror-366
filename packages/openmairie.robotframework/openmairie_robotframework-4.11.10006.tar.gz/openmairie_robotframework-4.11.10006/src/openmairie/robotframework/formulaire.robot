*** Settings ***
Documentation     Actions dans un formulaire

*** Keywords ***
Click Element Until New Element
    [Tags]
    [Documentation]    Clique sur un élément jusqu'à ce que le second élément
    ...                apparaisse dans le DOM (doit être absent avant le clic)
    [Arguments]    ${elm_clicked}  ${elm_probe}

    # vérifie que l'élément sonde est invisible
    Element Should Not Be Visible  ${elm_probe}

    # récupère les WebElements 'sonde' pour pouvoir les comparer ensuite
    ${webelements_st}  ${webelements} =  Run Keyword And Ignore Error  Get WebElements  ${elm_probe}
    
    # 3 essais de clic sur l'élément (passé en paramètre)
    :FOR  ${INDEX}  IN RANGE  1  4
    \
    \  # attente du succès du clic pendant 3 secondes max
    \  Wait Until Keyword Succeeds     3     ${RETRY_INTERVAL}    Click Element  ${elm_clicked}
    \
    \  # attente de l'apparition du second élément pendant quelques secondes
    \  ${probe_visible}=  Run Keyword And Return Status
    \  ...  Wait Until Keyword Succeeds  ${CLIC_CONFIRM_WAIT}  ${RETRY_INTERVAL}  Element Should Be Visible  ${elm_probe}
    \
    \  # récupère (à nouveau) les WebElements 'sonde'
    \  ${webelements_status}  ${webelements_new} =  Run Keyword And Ignore Error  Get WebElements  ${elm_probe}
    \
    \  # compare les WebElements 'sonde'
    \  ${webelements_diff}=  Run Keyword And Return Status  Should Not Be Equal  ${webelements}  ${webelements_new}
    \  
    \  # si l'élément sonde est devenu visible ou les WebElements sont différents, on sort de la boucle
    \  Run Keyword If  ${probe_visible} or ${webelements_diff}  Return From Keyword
    Run Keyword If  ${INDEX} == 3  Fail  Le clic sur '${elm_clicked}' a échoué

Click Element Until No More Element
    [Tags]
    [Documentation]    Clique sur un élément jusqu'à ce qu'il disparaisse du DOM
    ...                Il est aussi possible de spécifier un élément sonde qui
    ...                devra disparaître en lieu et place de l'élément cliqué
    [Arguments]    ${elm_clicked}  ${elm_probe}=None

    # Détermine s'il y a un autre élément sonde à utiliser à la place de l'élément
    # cliqué
    ${elm_gone}=  Set Variable If  ${elm_probe} is None  ${elm_clicked}
    ...                                                  ${elm_probe}

    # Vérifie que l'élément cliqué est visible
    Element Should Be Visible  ${elm_clicked}

    # Vérifie que l'élément sonde est visible
    Run Keyword If  ${elm_probe} is not None  Element Should Be Visible  ${elm_gone}

    # récupère les WebElements 'sonde' pour pouvoir les comparer ensuite
    ${webelements} =  Get WebElements  ${elm_gone}

    # 3 essais de clic sur l'élément (passé en paramètre)
    :FOR  ${INDEX}  IN RANGE  1  4
    \
    \  # attente du succès du clic pendant 3 secondes max
    \  Wait Until Keyword Succeeds     3     ${RETRY_INTERVAL}    Click Element  ${elm_clicked}
    \
    \  # attente de la disparition du second élément pendant quelques secondes
    \  ${probe_not_visible}=  Run Keyword And Return Status
    \  ...  Wait Until Keyword Succeeds  ${CLIC_CONFIRM_WAIT}  ${RETRY_INTERVAL}  Element Should Not Be Visible  ${elm_gone}
    \
    \  # récupère (à nouveau) les WebElements 'sonde'
    \  ${webelements_status}  ${webelements_new} =  Run Keyword And Ignore Error  Get WebElements  ${elm_gone}
    \
    \  # compare les WebElements 'sonde'
    \  ${webelements_diff}=  Run Keyword And Return Status  Should Not Be Equal  ${webelements}  ${webelements_new}
    \  
    \  # si on a détecté la disparition de l'élément sonde ou les WebElement sont différent, on sort de la boucle
    \  Run Keyword If  ${probe_not_visible} or ${webelements_diff}  Return From Keyword
    Run Keyword If  ${INDEX} == 3  Fail  Le clic sur '${elm_clicked}' a échoué

Click Element Until New Window
    [Tags]
    [Documentation]    Clique sur un élément jusqu'à ce qu'une nouvelle fenêtre apparaisse
    [Arguments]    ${elm_clicked}

    # Vérifie que l'élément est visible
    Element Should Be Visible  ${elm_clicked}

    # compte le nombre de fenêtre actuelles
    ${current_windows}=  Get Window Handles
    ${windows_count}=  Get Length  ${current_windows}

    # 3 essais de clic sur l'élément (passé en paramètre)
    :FOR  ${INDEX}  IN RANGE  1  4
    \
    \  # attente du succès du clic pendant 3 secondes max
    \  Wait Until Keyword Succeeds     3     ${RETRY_INTERVAL}    Click Element  ${elm_clicked}
    \
    \  # temporisation minimale
    \  Sleep  1
    \
    \  # re-comptage du nombre de fenêtres ouvertes
    \  ${new_windows}=  Get Window Handles
    \  ${new_count}=  Get Length  ${new_windows}
    \
    \  # si on a détecté l'apparition d'une nouvelle fenêtre
    \  Run Keyword If  ${new_count} > ${windows_count}  Return From Keyword
    Run Keyword If  ${INDEX} == 3  Fail  Le clic sur '${elm_clicked}' a échoué

One Of Messages Should Be
    [Tags]
    [Documentation]  Réussi si le texte passé en paramètre est retrouvé dans l'un
    ...              des messages (dans #form-message ou .message)
    [Arguments]      ${message}
    
    ${msg_class_message}=  Run Keyword And Return Status  Element Should Contain  css=div.message    ${message}
    ${msg_form_message}=   Run Keyword And Return Status  Element Should Contain  css=#form-message  ${message}
    Should Be True  ${msg_class_message} or ${msg_form_message}

No Message Should Be
    [Tags]
    [Documentation]  Réussi si le texte passé en paramètre n'est retrouvé dans
    ...              aucun des messages (dans #form-message ou .message)
    [Arguments]      ${message}
    
    ${msg_found}=  Run Keyword And Return Status  One Of Messages Should Be  ${message}
    Run Keyword If  ${msg_found}  Capture Page Screenshot
    Should Be True  not ${msg_found}

Click Element Until Message
    [Tags]
    [Documentation]  Clique sur un élément jusqu'à ce qu'un message apparaisse
    [Arguments]      ${elm_clicked}  ${message}  ${elm_message}=None

    # Vérifie que l'élément à cliquer est visible
    Element Should Be Visible  ${elm_clicked}

    # Vérifie qu'aucun message ne contient actuellement le message recherché
    No Message Should Be  ${message}

    # 3 essais de clic sur l'élément (passé en paramètre)
    :FOR  ${INDEX}  IN RANGE  1  4
    \
    \  # attente du succès du clic pendant 3 secondes max
    \  Wait Until Keyword Succeeds     3     ${RETRY_INTERVAL}    Click Element  ${elm_clicked}
    \
    \  # attente de l'apparition du message pendant quelques secondes
    \  ${msg_found}=  Run Keyword And Return Status
    \  ...  Run Keyword If  len("${elm_message}") > 0
    \  ...     Wait Until Keyword Succeeds  ${CLIC_CONFIRM_WAIT}  ${RETRY_INTERVAL}  One Of Messages Should Be  ${message}
    \  ...  ELSE
    \  ...     Wait Until Keyword Succeeds  ${CLIC_CONFIRM_WAIT}  ${RETRY_INTERVAL}  Element Should Contain  ${elm_message}  ${message}
    \
    \  # si on a détecté le message, on sort de la boucle
    \  Run Keyword If  ${msg_found}  Return From Keyword
    Run Keyword If  ${INDEX} == 3  Fail  Le clic sur '${elm_clicked}' a échoué

Click On Add Button
    [Tags]
    Click Element Until No More Element    css=span.add-16
    La page ne doit pas contenir d'erreur

Click On Add Button JS
    [Tags]
    Click On Add Button

Click On Submit Button
    [Tags]
    Click Element Until No More Element  css=#formulaire div.formControls input[type="submit"]
    La page ne doit pas contenir d'erreur

Click On Submit Button Until Message
    [Tags]
    [Documentation]  Clic sur le bouton de confirmation jusqu'à ce qu'un message
    ...              apparaisse
    [Arguments]  ${message}
    Click Element Until Message  css=#formulaire div.formControls input[type="submit"]  ${message}

Click On Submit Button In Subform
    [Tags]
    Click Element Until No More Element  css=#sformulaire div.formControls input[type="submit"]
    La page ne doit pas contenir d'erreur

Click On Submit Button In Subform Until Message
    [Tags]
    [Documentation]  Clic sur le bouton de confirmation jusqu'à ce qu'un message
    ...              apparaisse
    [Arguments]  ${message}
    Click Element Until Message  css=#sformulaire div.formControls input[type="submit"]  ${message}

Click On Submit Button In Overlay
    [Tags]
    [Arguments]    ${obj}
    Click Element Until No More Element  css=#form-${obj}-overlay div.formControls input[type="submit"]
    La page ne doit pas contenir d'erreur

Click On Back Button
    [Tags]
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Click Element    css=a.retour
    Sleep    1
    La page ne doit pas contenir d'erreur

Click On Back Button In Subform
    [Tags]
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Click Element    css=#sformulaire a.retour
    Sleep    1
    La page ne doit pas contenir d'erreur

Click On Back Button In Overlay
    [Tags]
    [Arguments]    ${obj}
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Click Element    css=#form-${obj}-overlay form a.retour
    Sleep    1
    La page ne doit pas contenir d'erreur

Click On Form Tab
    [Tags]
    Click Element Until No More Element  main
    La page ne doit pas contenir d'erreur

Click On Httpclick Element
    [Tags]
    [Documentation]    Clique sur un champ de type httpclick.
    [Arguments]    ${element_id}
    Click Element Until No More Element  css=.field-type-httpclick #${element_id}
    La page ne doit pas contenir d'erreur

Click On Tab
    [Tags]
    [Documentation]    Clique sur l'onglet passé en paramètre.
    [Arguments]    ${tab}    ${tab_title}
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li a#    ${tab}
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Tab Title Should Be    ${tab}    ${tab_title}
    ${tab_container_id}=  Set Variable  css=#formulaire .ui-tabs-panel #sousform-${tab}
    Click Element Until New Element  ${locator}  ${tab_container_id}
    La page ne doit pas contenir d'erreur

First Tab Title Should Be
    [Tags]
    [Arguments]    ${messagetext}
    Element Text Should Be    css=#formulaire ul.ui-tabs-nav li a    ${messagetext}

Tab Title Should Be
    [Tags]
    [Documentation]    Vérifie le titre de l'onglet.
    [Arguments]    ${tab}    ${tab_title}
    ${locator} =    Catenate    SEPARATOR=    css=#formulaire ul.ui-tabs-nav li a#    ${tab}
    Wait Until Keyword Succeeds     ${TIMEOUT}     ${RETRY_INTERVAL}    Element Text Should Be    ${locator}    ${tab_title}

Input Username
    [Tags]
    [Arguments]    ${username}
    Input Text    login    ${username}

Input Password
    [Tags]
    [Arguments]    ${password}
    Input Text    password    ${password}

Input HTML
    [Tags]
    [Arguments]    ${field}    ${value}
    Select Frame    ${field}_ifr
    Set Focus To Element  tinymce
    Input Text    tinymce    ${value}
    Unselect Frame

HTML Should Contain
    [Tags]
    [Arguments]    ${field}    ${expected}
    Wait Until Keyword Succeeds    ${TIMEOUT}    ${RETRY_INTERVAL}    Select Frame    id=${field}_ifr
    Wait Until Keyword Succeeds    ${TIMEOUT}    ${RETRY_INTERVAL}    Element Should Contain    css=#tinymce    ${expected}
    Unselect frame

HTML Should Not Contain
    [Tags]
    [Arguments]    ${field}    ${non_expected}
    Wait Until Keyword Succeeds    ${TIMEOUT}    ${RETRY_INTERVAL}    Select Frame    id=${field}_ifr
    Set Focus To Element  tinymce
    ${reel_content} =  Get Text  tinymce
    Should Not Contain  ${reel_content}  ${non_expected}
    Unselect frame

Numeric Value Should Be
    [Tags]
    [Arguments]    ${champ}    ${valeurAttendue}
    ${valeurRecuperee} =    Get Text    css=#${champ}
    Should Be Equal As Integers    ${valeurAttendue}    ${valeurRecuperee}

Form Value Should Be
    [Tags]
    [Arguments]    ${champ}    ${valeurAttendue}
    ${valeurRecuperee} =    Get Value    ${champ}
    Should Be Equal    ${valeurAttendue}    ${valeurRecuperee}

Form Field Attribute Should Be
    [Tags]
    [Documentation]    Vérifie la valeur de l'attribut du champ.
    [Arguments]    ${champ}    ${attribute}    ${expected_value}
    ${get_value} =    Get Element Attribute    css=#${champ}  ${attribute}
    Should Be Equal    ${expected_value}    ${get_value}

Numeric Static Value Should Be
    [Tags]
    [Arguments]    ${champ}    ${valeurAttendue}
    ${valeurRecuperee} =    Get Text    ${champ}
    Should Be Equal As Integers    ${valeurAttendue}    ${valeurRecuperee}

Form Static Value Should Be
    [Tags]
    [Arguments]    ${champ}    ${valeurAttendue}
    ${valeurRecuperee} =    Get Text    ${champ}
    Should Be Equal    ${valeurAttendue}    ${valeurRecuperee}

Selected List Label Should Be
    [Tags]
    [Documentation]    Vérifie le libellé de l'option sélectionné.
    [Arguments]    ${field}    ${expected_value}
    ${fied_value} =    Get Selected List Label    ${field}
    Should Be Equal    ${expected_value}    ${fied_value}

Select List Should Be
    [Tags]
    [Arguments]    ${champ}    ${listeAttendue}
    ${listeRecuperee} =    Get List Items    ${champ}
    Lists Should Be Equal    ${listeAttendue}    ${listeRecuperee}

Select List Should Contain List
    [Tags]
    [Documentation]    Vérifie que la liste contient les élements passés en paramètre
    [Arguments]    ${champ}    ${listeAttendue}
    ${listeRecuperee} =    Get List Items    ${champ}
    :FOR    ${valeur}    IN    @{listeAttendue}
    \    List Should Contain Value    ${listeRecuperee}    ${valeur}

Select List Should Not Contain List
    [Tags]
    [Documentation]    Vérifie que la liste ne contient pas les élements passés en paramètre
    [Arguments]    ${champ}    ${listeInnatendue}
    ${listeRecuperee} =    Get List Items    ${champ}
    :FOR    ${valeur}    IN    @{listeInnatendue}
    \    List Should Not Contain Value    ${listeRecuperee}    ${valeur}

Link Value Should Be
    [Tags]
    [Documentation]    Vérifie le texte du lien.
    [Arguments]    ${field}    ${expected_value}
    ${get_value} =    Get Text    css=#link_${field}
    Should Be Equal    ${expected_value}    ${get_value}

Message Should Be
    [Tags]
    [Arguments]    ${messagetext}
    Element Text Should Be    css=div.message p span.text   ${messagetext}

Message Should Be In Subform
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Text Should Be  css=#sformulaire div.message p span.text  ${messagetext}

Message Should Contain
    [Tags]
    [Arguments]    ${messagetext}
    Element Should Contain    css=div.message p span.text   ${messagetext}

Message Should Contain In Subform
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=#sformulaire div.message p span.text  ${messagetext}

Error Message Should Be
    [Tags]
    [Arguments]    ${messagetext}
    Element Text Should Be    css=div.message.ui-state-error p span.text   ${messagetext}

Error Message Should Be In Subform
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Text Should Be  css=#sformulaire div.message.ui-state-error p span.text  ${messagetext}

Error Message Should Contain
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=div.message.ui-state-error p span.text  ${messagetext}

Error Message Should Contain In Subform
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=#sformulaire div.message.ui-state-error p span.text  ${messagetext}

Valid Message Should Be
    [Tags]
    [Arguments]    ${messagetext}
    Element Text Should Be    css=div.message.ui-state-valid p span.text   ${messagetext}

Valid Message Should Be In Subform
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Text Should Be  css=#sformulaire div.message.ui-state-valid p span.text  ${messagetext}

Valid Message Should Contain
    [Tags]
    [Arguments]    ${messagetext}
    Element Should Contain    css=div.message.ui-state-valid p span.text   ${messagetext}

Valid Message Should Contain In Subform
    [Tags]
    [Arguments]    ${messagetext}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=#sformulaire div.message.ui-state-valid p span.text  ${messagetext}

Get Object In Form
    [Tags]
    ${url}    Get Location
    ${url}    Fetch From Right    ${url}    obj=
    ${objInForm}    Fetch From Left    ${url}    &
    Set Suite Variable    ${objInForm}

Add File
    [Tags]
    [Arguments]  ${field}  ${file}
    Click Element Until New Element  css=#${field}_upload + a.upload > span.ui-icon  css=.ui-dialog #upload-container
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Choose File  css=#upload-form > input.champFormulaire    ${PATH_BIN_FILES}${file}
    Click Element Until No More Element  css=form#upload-form input.ui-button
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Textfield Value Should Be  css=#${field}_upload    ${file}

Add File and Expect Error Message Be
    [Tags]
    [Arguments]  ${field}  ${file}  ${message}
    Click Element Until New Element  css=#${field}_upload + a.upload > span.ui-icon  css=.ui-dialog #upload-container
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Choose File  css=#upload-form > input.champFormulaire    ${PATH_BIN_FILES}${file}
    Click Element Until Message  css=form#upload-form input.ui-button  ${message}  css=#upload-container div.message.ui-state-error p span.text
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=#upload-container div.message.ui-state-error p span.text  ${message}
    Click Element Until No More Element  css=form#upload-form a.linkjsclosewindow

Add File and Expect Error Message Contain
    [Tags]
    [Arguments]  ${field}  ${file}  ${message}
    Click Element Until New Element  css=#${field}_upload + a.upload > span.ui-icon  css=.ui-dialog #upload-container
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Choose File  css=#upload-form > input.champFormulaire    ${PATH_BIN_FILES}${file}
    Click Element Until Message  css=form#upload-form input.ui-button  ${message}  css=#upload-container div.message.ui-state-error p span.text
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  css=#upload-container div.message.ui-state-error p span.text  ${message}
    Click Element Until No More Element  css=form#upload-form a.linkjsclosewindow

Form Actions Should Be
    [Tags]
    [Arguments]    ${actions}
    ${length}    Get Length    ${actions}
    Log    Length = ${length}
    Xpath Should Match X Times    //div[@id="portlet-actions"]/ul/li    ${length}

    :FOR    ${index}    IN    @{actions}
    \    Element Should Contain    css=#portlet-actions ul.portlet-list   ${index}


Portlet Action Should Be In Form
    [Tags]
    [Arguments]    ${obj}    ${action}
    Page Should Contain Element    css=#form-container #portlet-actions #action-form-${obj}-${action}

Portlet Action Should Not Be In Form
    [Tags]
    [Arguments]    ${obj}    ${action}
    Page Should Not Contain Element    css=#form-container #portlet-actions #action-form-${obj}-${action}

Portlet Action Should Be In SubForm
    [Tags]
    [Arguments]    ${obj}    ${action}
    Page Should Contain Element    css=#sousform-container #portlet-actions #action-sousform-${obj}-${action}

Portlet Action Should Not Be In SubForm
    [Tags]
    [Arguments]    ${obj}    ${action}
    Page Should Not Contain Element    css=#sousform-container #portlet-actions #action-sousform-${obj}-${action}

Click On Portlet Action
    [Tags]
    [Arguments]  ${obj}  ${action}  ${sousform}=False  ${mode}=None  ${message}=None
    # si le mode de confirmation est
    #   new_window: vérifie qu'une nouvelle fenêtre est apparue
    #   modale    : vérifie qu'une fenêtre modale est apparue
    #   message   : vérifie qu'un message est apparu
    #   *         : vérifie que l'élément cliqué a disparu
    ${selector} =  Set Variable If  ${sousform}  css=#action-sousform-${obj}-${action}
    ...                                          css=#action-form-${obj}-${action}
    Run Keyword If  '${mode}' == 'new_window'  Click Element Until New Window       ${selector}
    ...    ELSE IF  '${mode}' == 'modale'      Click Element Until New Element      ${selector}  css=.ui-widget-overlay
    ...    ELSE IF  '${mode}' == 'message'     Click Element Until Message          ${selector}  ${message}
    ...    ELSE                                Click Element Until No More Element  ${selector}
    La page ne doit pas contenir d'erreur

Click On Form Portlet Action
    [Tags]
    [Arguments]    ${obj}    ${action}    ${mode}=None    ${message}=None
    Click On Portlet Action  ${obj}  ${action}  False  ${mode}  ${message}

Click On SubForm Portlet Action
    [Tags]
    [Arguments]    ${obj}    ${action}    ${mode}=None    ${message}=None
    Click On Portlet Action  ${obj}  ${action}  True  ${mode}  ${message}

Input Datepicker
    [Tags]
    [Arguments]    ${champ}    ${date}
    # On clique sur l'image du datepicker
    Click Image    css=input#${champ} + .ui-datepicker-trigger
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
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Not Be Visible  ui-datepicker-div

Input Hour Minute
    [Tags]
    [Arguments]    ${champ}    ${hour}=null    ${minute}=null
    # On sélectionne l'heure
    Run Keyword If    '${hour}' != 'null'    Select From List By Label    css=#${champ}_heure    ${hour}
    # On sélectionne la minute
    Run Keyword If    '${minute}' != 'null'    Select From List By Label    css=#${champ}_minute    ${minute}

Input Value With JS
    [Tags]
    [Arguments]    ${champ}    ${value}
    # On écrit la valeur directement dans l'attribut de l'input
    Execute JavaScript    window.jQuery("#${champ}").val('${value}');
    # On déclenche l'évènement onchange
    Execute JavaScript    window.jQuery("#${champ}").trigger("change");

Input Value With JS Failed
    [Tags]
    [Arguments]    ${champ}    ${value}    ${error}
    #
    Input Value With JS    ${champ}    ${value}
    # Vérification de l'erreur
    ${alert} =    Get Alert Message
    Should Be Equal As Strings    ${alert}    ${error}

Select Value With JS
    [Tags]
    [Arguments]  ${champ}  ${value}
    # On écrit la valeur directement dans l'attribut de l'input
    Execute JavaScript  window.jQuery("#${champ} option[value='${value}']").prop('selected', true);
    # On déclenche l'évènement onchange
    Execute JavaScript  window.jQuery("#${champ}").trigger("change");

Select Value With JS Failed
    [Tags]
    [Arguments]  ${champ}  ${value}  ${error}
    #
    Select Value With JS  ${champ}  ${value}
    # Vérification de l'erreur
    ${alert} =  Get Alert Message
    Should Be Equal As Strings  ${alert}  ${error}

Disable Event
    [Tags]
    [Arguments]  ${element}  ${event}
    Execute JavaScript  window.jQuery("#${element}").prop("${event}", null).attr("${event}", null);

Breadcrumb Should Be
    [Tags]
    [Arguments]    ${value}
    Element Text Should Be    css=#title h2    ${value}

Breadcrumb Should Contain
    [Tags]
    [Arguments]    ${value}
    Element Should Contain    css=#title h2    ${value}

Selected Tab Title Should Be
    [Tags]
    [Arguments]    ${id}    ${libelle}
    Element Text Should Be    css=li.ui-tabs-selected #${id}    ${libelle}

Select Checkbox From List
    [Tags]
    [Documentation]    Sélectionne une liste de case à cocher.
    [Arguments]    @{list_checkbox}
    :FOR    ${checkbox}    IN    @{list_checkbox}
    \    Select Checkbox    ${checkbox}

Form Value Should Contain From List
    [Tags]
    [Documentation]    Vérifie la présence d'élément dans un champ de formulaire
    ...    depuis une liste.
    [Arguments]    ${field}    @{list_expected}
    :FOR    ${element}    IN    @{list_expected}
    \    Element Should Contain    ${field}    ${element}

Form HTML Should Contain From List
    [Tags]
    [Documentation]    Vérifie la présence d'élément dans un champ HTML de
    ...    formulaire depuis une liste.
    [Arguments]    ${field}    @{list_expected}
    Select Frame    ${field}_ifr
    Set Focus To Element  tinymce
    :FOR    ${element}    IN    @{list_expected}
    \    Element Should Contain    tinymce    ${element}
    Unselect frame

Open Fieldset
    [Tags]
    [Documentation]    Déplie un fieldset et attend qu'il soit ouvert
    [Arguments]    ${obj}    ${fieldset}
    Click Element Until New Element  css=#fieldset-form-${obj}-${fieldset} > legend.collapsible  css=#fieldset-form-${obj}-${fieldset} > .fieldsetContent
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Not Be Visible  css=#fieldset-form-${obj}-${fieldset} > legend.collapsed
    Sleep  0.5

Open Fieldset In Subform
    [Tags]
    [Documentation]    Déplie un fieldset et attend qu'il soit ouvert
    [Arguments]    ${obj}    ${fieldset}
    Click Element Until New Element  css=#fieldset-sousform-${obj}-${fieldset} > legend.collapsible  css=#fieldset-sousform-${obj}-${fieldset} > .fieldsetContent
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Not Be Visible  css=#fieldset-sousform-${obj}-${fieldset} > legend.collapsed
    Sleep  0.5

Select Multiple By Label
    [Tags]
    [Documentation]    Sélectionne une liste de libellés si non vide
    [Arguments]  ${champ}  ${list}
    ${length} =  Get Length  ${list}
    Run Keyword If  ${length} > 0  Select From List By Label  ${champ}  @{list}

Element Should Contain In Subform
    [Tags]
    [Arguments]  ${element}  ${string}
    Wait Until Element Is Visible  ${element}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Element Should Contain  ${element}  ${string}

Element Text Should Not Be
    [Tags]
    [Arguments]  ${element}  ${non_expected}
    Wait Until Element Is Visible  ${element}
    ${reel_content} =  Get Text  ${element}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Should Not Be Equal As Strings  ${reel_content}  ${non_expected}

Element Should Not Contain
    [Tags]
    [Arguments]  ${element}  ${non_expected}
    Wait Until Element Is Visible  ${element}
    ${reel_content} =  Get Text  ${element}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${RETRY_INTERVAL}  Should Not Contain  ${reel_content}  ${non_expected}

Set Checkbox
    [Tags]
    [Arguments]  ${element}  ${value}='true'
    Run Keyword If  '${value}' == 'true'  Select Checkbox  ${element}
    Run Keyword If  '${value}' == 'false'  Unselect Checkbox  ${element}

Element Must Be Disabled
    [Tags]
    [Arguments]  ${element_id}
    ${value} =  Get Element Attribute  ${element_id}  disabled
    Should Be Equal  ${value}  true

Element Must Be Enabled
    [Tags]
    [Arguments]  ${element_id}
    ${value} =  Get Element Attribute  ${element_id}  disabled
    Should Be Equal  ${value}  ${None}

Element should contain X times
    [Tags]
    [Arguments]  ${locator}  ${string}  ${count}
    Wait Until Element Is Visible  ${locator}
    ${reel_content} =  Get Text  ${locator}
    Should Contain X Times  ${reel_content}  ${string}  ${count}

Get Mandatory Value
    [Tags]
    [Arguments]  ${locator}
    :FOR  ${i}  IN RANGE  20
    \  ${value_not_empty} =  Get Value  ${locator}
    \  # Renvoie la valeur si elle n'est pas vide
    \  Return From Keyword If  "${value_not_empty}" != "${null}"  ${value_not_empty}
    \  Sleep  1
    \  ${i} =  Set Variable  ${i} + 1
    Fail

Element Should Contain From List
    [Tags]
    [Documentation]    Vérifie la présence d'une liste de string dans un élément.
    [Arguments]    ${element}    ${list_expected}
    :FOR    ${text}    IN    @{list_expected}
    \    Element Should Contain    ${element}    ${text}


Le portlet d'action ne doit pas être présent dans le sous-formulaire
    [Documentation]  Vérifie que le portlet d'action n'est pas affiché.

    Page Should Not Contain Element  css=#sousform-container div#portlet-actions

Sélection de valeur(s)
    [Tags]
    [Documentation]
    ...  Identifie si l'élément ``locator`` est une liste à choix unique ou multiple
    ...  puis sélectionne la ou les options par ``labels``.
    ...
    ...  ``labels`` doit être de type _string_ dans le cas d'une liste à choix unique.
    ...  En cas de liste à choix multiple, les éventuelles anciennes options sont
    ...  déselectionnées et ``labels`` doit être de type _string_ ou _list_.
    ...
    ...  Exemple dans le cas d'une liste à choix unique :
    ...
    ...  | ${locator} =  Set Variable  om_sql
    ...  | ${labels} =  Set Variable  Requête A (req_a)
    ...  | Sélection de valeur(s)  ${locator}  ${labels}
    ...
    ...  Exemple dans le cas d'une liste à choix multiple :
    ...
    ...  | ${locator} =  Set Variable  om_sql
    ...  | ${labels} =  Create List  Requête A (req_a)  Requête B (req_b)
    ...  | Sélection de valeur(s)  ${locator}  ${labels}

    [Arguments]  ${locator}  ${labels}

    # On détermine le type de requête
    ${selecttype} =  Get Element Attribute  ${locator}  multiple

    # Dans le cas d'une requête multiple
    Run Keyword If  '${selecttype}' == 'true'  Sélection de valeur(s) dans un select multiple  ${locator}  ${labels}
    # Dans le cas d'une requête simple
    ...    ELSE                                Sélection de valeur dans un select simple  ${locator}  ${labels}

Sélection de valeur(s) dans un select multiple
    [Tags]
    [Documentation]
    ...  Sélectionne une ou plusieurs options par ``labels`` au sein d'une
    ...  liste à choix multiple ``locator``.
    [Arguments]  ${locator}  ${labels}

    # On détermine le type de l'argument $labels
    ${is_string} =  Run Keyword And Return Status  Should Be String  ${labels}
    ${is_list} =  Run Keyword If  ${is_string} != True  Evaluate  type(${labels}).__name__ == "list"

    # Si l'argument $labels est une string
    ${labels_list} =  Run Keyword If  ${is_string}  Create List  ${labels}
    # Si l'argument $labels est une liste
    ...    ELSE IF  ${is_list}  Set Variable  ${labels}
    # Autrement on retourne un fail
    ...    ELSE  Fail  La variable \${labels} doit être de type string ou list.

    # On s'assure que la valeur par défaut soit désélectionnée
    Unselect All From List  ${locator}
    # On sélectionne chaque valeur de la liste
    Select Multiple By Label  ${locator}  ${labels_list}

Sélection de valeur dans un select simple
    [Tags]
    [Documentation]
    ...  Sélectionne une option par ``labels`` au sein d'une liste à choix
    ...  unique ``locator``.
    [Arguments]  ${locator}  ${label}

    # On vérifie que l'argument $label est une string
    ${is_string} =  Run Keyword And Return Status  Should Be String  ${label}
    # Si c'est le cas, on sélectionne la valeur
    Run Keyword If  ${is_string} = True  Select From List By Label  ${locator}  ${label}
    # Autrement on retourne un fail
    ...    ELSE  Fail  La variable \${label} doit être de type string.
