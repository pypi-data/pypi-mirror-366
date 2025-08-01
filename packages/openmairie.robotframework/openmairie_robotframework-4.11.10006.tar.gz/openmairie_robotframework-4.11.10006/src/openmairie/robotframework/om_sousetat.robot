*** Settings ***
Documentation     Actions spécifiques aux sous-états

*** Keywords ***
Depuis le contexte du sous état
    [Tags]  om_sousetat
    [Documentation]  Accède au formulaire
    [Arguments]    ${om_sousetat}

    # On accède au tableau
    Depuis le listing  om_sousetat
    # On recherche l'enregistrement
    Use Simple Search    Tous    ${om_sousetat}
    # On clique sur le résultat
    Click On Link    ${om_sousetat}
    # On vérifie qu'il n'y a pas d'erreur
    La page ne doit pas contenir d'erreur


Depuis le listing des sous-états de la collectivité
    [Tags]  om_sousetat
    [Documentation]  ...
    [Arguments]  ${collectivite_libelle}
    #
    Depuis le contexte de la collectivité  ${collectivite_libelle}
    #
    On clique sur l'onglet  om_sousetat  sous état


Ajouter le sous état
    [Tags]  om_sousetat
    [Documentation]  Ajoute un enregistrement de type 'sous état' (om_sousetat).
    [Arguments]    ${om_collectivite}=null    ${id}=null    ${libelle}=null    ${actif}=null    ${titre}=null    ${titrehauteur}=null    ${titrefont}=null    ${titreattribut}=null    ${titretaille}=null    ${titrebordure}=null    ${titrealign}=null    ${titrefond}=null    ${titrefondcouleur}=null    ${titretextecouleur}=null    ${intervalle_debut}=null    ${intervalle_fin}=null    ${entete_flag}=null    ${entete_fond}=null    ${entete_orientation}=null    ${entete_hauteur}=null    ${entetecolone_bordure}=null    ${entetecolone_align}=null    ${entete_fondcouleur}=null    ${entete_textecouleur}=null    ${tableau_largeur}=null    ${tableau_bordure}=null    ${tableau_fontaille}=null    ${bordure_couleur}=null    ${se_fond1}=null    ${se_fond2}=null    ${cellule_fond}=null    ${cellule_hauteur}=null    ${cellule_largeur}=null    ${cellule_bordure_un}=null    ${cellule_bordure}=null    ${cellule_align}=null    ${cellule_fond_total}=null    ${cellule_fontaille_total}=null    ${cellule_hauteur_total}=null    ${cellule_fondcouleur_total}=null    ${cellule_bordure_total}=null    ${cellule_align_total}=null    ${cellule_fond_moyenne}=null    ${cellule_fontaille_moyenne}=null    ${cellule_hauteur_moyenne}=null    ${cellule_fondcouleur_moyenne}=null    ${cellule_bordure_moyenne}=null    ${cellule_align_moyenne}=null    ${cellule_fond_nbr}=null    ${cellule_fontaille_nbr}=null    ${cellule_hauteur_nbr}=null    ${cellule_fondcouleur_nbr}=null    ${cellule_bordure_nbr}=null    ${cellule_align_nbr}=null    ${cellule_numerique}=null    ${cellule_total}=null    ${cellule_moyenne}=null    ${cellule_compteur}=null    ${om_sql}=null

    # On accède au tableau
    Depuis le listing  om_sousetat
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir le sous état    ${om_collectivite}    ${id}    ${libelle}    ${actif}    ${titre}    ${titrehauteur}    ${titrefont}    ${titreattribut}    ${titretaille}    ${titrebordure}    ${titrealign}    ${titrefond}    ${titrefondcouleur}    ${titretextecouleur}    ${intervalle_debut}    ${intervalle_fin}    ${entete_flag}    ${entete_fond}    ${entete_orientation}    ${entete_hauteur}    ${entetecolone_bordure}    ${entetecolone_align}    ${entete_fondcouleur}    ${entete_textecouleur}    ${tableau_largeur}    ${tableau_bordure}    ${tableau_fontaille}    ${bordure_couleur}    ${se_fond1}    ${se_fond2}    ${cellule_fond}    ${cellule_hauteur}    ${cellule_largeur}    ${cellule_bordure_un}    ${cellule_bordure}    ${cellule_align}    ${cellule_fond_total}    ${cellule_fontaille_total}    ${cellule_hauteur_total}    ${cellule_fondcouleur_total}    ${cellule_bordure_total}    ${cellule_align_total}    ${cellule_fond_moyenne}    ${cellule_fontaille_moyenne}    ${cellule_hauteur_moyenne}    ${cellule_fondcouleur_moyenne}    ${cellule_bordure_moyenne}    ${cellule_align_moyenne}    ${cellule_fond_nbr}    ${cellule_fontaille_nbr}    ${cellule_hauteur_nbr}    ${cellule_fondcouleur_nbr}    ${cellule_bordure_nbr}    ${cellule_align_nbr}    ${cellule_numerique}    ${cellule_total}    ${cellule_moyenne}    ${cellule_compteur}    ${om_sql}
    # On valide le formulaire
    Click On Submit Button


Saisir le sous état
    [Tags]  om_sousetat
    [Documentation]  Remplit le formulaire
    [Arguments]    ${om_collectivite}=null    ${id}=null    ${libelle}=null    ${actif}=null    ${titre}=null    ${om_sql}=null    ${titrehauteur}=null    ${titrefont}=null    ${titreattribut}=null    ${titretaille}=null    ${titrebordure}=null    ${titrealign}=null    ${titrefond}=null    ${titrefondcouleur}=null    ${titretextecouleur}=null    ${intervalle_debut}=null    ${intervalle_fin}=null    ${entete_flag}=null    ${entete_fond}=null    ${entete_orientation}=null    ${entete_hauteur}=null    ${entetecolone_bordure}=null    ${entetecolone_align}=null    ${entete_fondcouleur}=null    ${entete_textecouleur}=null    ${tableau_largeur}=null    ${tableau_bordure}=null    ${tableau_fontaille}=null    ${bordure_couleur}=null    ${se_fond1}=null    ${se_fond2}=null    ${cellule_fond}=null    ${cellule_hauteur}=null    ${cellule_largeur}=null    ${cellule_bordure_un}=null    ${cellule_bordure}=null    ${cellule_align}=null    ${cellule_fond_total}=null    ${cellule_fontaille_total}=null    ${cellule_hauteur_total}=null    ${cellule_fondcouleur_total}=null    ${cellule_bordure_total}=null    ${cellule_align_total}=null    ${cellule_fond_moyenne}=null    ${cellule_fontaille_moyenne}=null    ${cellule_hauteur_moyenne}=null    ${cellule_fondcouleur_moyenne}=null    ${cellule_bordure_moyenne}=null    ${cellule_align_moyenne}=null    ${cellule_fond_nbr}=null    ${cellule_fontaille_nbr}=null    ${cellule_hauteur_nbr}=null    ${cellule_fondcouleur_nbr}=null    ${cellule_bordure_nbr}=null    ${cellule_align_nbr}=null    ${cellule_numerique}=null    ${cellule_total}=null    ${cellule_moyenne}=null    ${cellule_compteur}=null

    Run Keyword If  '${om_collectivite}' != 'null'  Select From List By Value    om_collectivite    ${om_collectivite}
    Run Keyword If  '${id}' != 'null'  Input Text    id    ${id}
    Run Keyword If  '${libelle}' != 'null'  Input Text    libelle    ${libelle}
    # On coche actif si spécifié
    Run Keyword If  '${actif}' == 'true'  Select Checkbox  actif
    # On décoche actif si spécifié
    Run Keyword If  '${actif}' == 'false'  Unselect Checkbox  actif
    Run Keyword If  '${titre}' != 'null'  Input Text    titre    ${titre}
    Run Keyword If  '${titrehauteur}' != 'null'  Input Text    titrehauteur    ${titrehauteur}
    Run Keyword If  '${titrefont}' != 'null'  Input Text    titrefont    ${titrefont}
    Run Keyword If  '${titreattribut}' != 'null'  Input Text    titreattribut    ${titreattribut}
    Run Keyword If  '${titretaille}' != 'null'  Input Text    titretaille    ${titretaille}
    Run Keyword If  '${titrebordure}' != 'null'  Input Text    titrebordure    ${titrebordure}
    Run Keyword If  '${titrealign}' != 'null'  Input Text    titrealign    ${titrealign}
    Run Keyword If  '${titrefond}' != 'null'  Input Text    titrefond    ${titrefond}
    Run Keyword If  '${titrefondcouleur}' != 'null'  Input Text    titrefondcouleur    ${titrefondcouleur}
    Run Keyword If  '${titretextecouleur}' != 'null'  Input Text    titretextecouleur    ${titretextecouleur}
    Run Keyword If  '${intervalle_debut}' != 'null'  Input Text    intervalle_debut    ${intervalle_debut}
    Run Keyword If  '${intervalle_fin}' != 'null'  Input Text    intervalle_fin    ${intervalle_fin}
    Run Keyword If  '${entete_flag}' != 'null'  Input Text    entete_flag    ${entete_flag}
    Run Keyword If  '${entete_fond}' != 'null'  Input Text    entete_fond    ${entete_fond}
    Run Keyword If  '${entete_orientation}' != 'null'  Input Text    entete_orientation    ${entete_orientation}
    Run Keyword If  '${entete_hauteur}' != 'null'  Input Text    entete_hauteur    ${entete_hauteur}
    Run Keyword If  '${entetecolone_bordure}' != 'null'  Input Text    entetecolone_bordure    ${entetecolone_bordure}
    Run Keyword If  '${entetecolone_align}' != 'null'  Input Text    entetecolone_align    ${entetecolone_align}
    Run Keyword If  '${entete_fondcouleur}' != 'null'  Input Text    entete_fondcouleur    ${entete_fondcouleur}
    Run Keyword If  '${entete_textecouleur}' != 'null'  Input Text    entete_textecouleur    ${entete_textecouleur}
    Run Keyword If  '${tableau_largeur}' != 'null'  Input Text    tableau_largeur    ${tableau_largeur}
    Run Keyword If  '${tableau_bordure}' != 'null'  Input Text    tableau_bordure    ${tableau_bordure}
    Run Keyword If  '${tableau_fontaille}' != 'null'  Input Text    tableau_fontaille    ${tableau_fontaille}
    Run Keyword If  '${bordure_couleur}' != 'null'  Input Text    bordure_couleur    ${bordure_couleur}
    Run Keyword If  '${se_fond1}' != 'null'  Input Text    se_fond1    ${se_fond1}
    Run Keyword If  '${se_fond2}' != 'null'  Input Text    se_fond2    ${se_fond2}
    Run Keyword If  '${cellule_fond}' != 'null'  Input Text    cellule_fond    ${cellule_fond}
    Run Keyword If  '${cellule_hauteur}' != 'null'  Input Text    cellule_hauteur    ${cellule_hauteur}
    Run Keyword If  '${cellule_largeur}' != 'null'  Input Text    cellule_largeur    ${cellule_largeur}
    Run Keyword If  '${cellule_bordure_un}' != 'null'  Input Text    cellule_bordure_un    ${cellule_bordure_un}
    Run Keyword If  '${cellule_bordure}' != 'null'  Input Text    cellule_bordure    ${cellule_bordure}
    Run Keyword If  '${cellule_align}' != 'null'  Input Text    cellule_align    ${cellule_align}
    Run Keyword If  '${cellule_fond_total}' != 'null'  Input Text    cellule_fond_total    ${cellule_fond_total}
    Run Keyword If  '${cellule_fontaille_total}' != 'null'  Input Text    cellule_fontaille_total    ${cellule_fontaille_total}
    Run Keyword If  '${cellule_hauteur_total}' != 'null'  Input Text    cellule_hauteur_total    ${cellule_hauteur_total}
    Run Keyword If  '${cellule_fondcouleur_total}' != 'null'  Input Text    cellule_fondcouleur_total    ${cellule_fondcouleur_total}
    Run Keyword If  '${cellule_bordure_total}' != 'null'  Input Text    cellule_bordure_total    ${cellule_bordure_total}
    Run Keyword If  '${cellule_align_total}' != 'null'  Input Text    cellule_align_total    ${cellule_align_total}
    Run Keyword If  '${cellule_fond_moyenne}' != 'null'  Input Text    cellule_fond_moyenne    ${cellule_fond_moyenne}
    Run Keyword If  '${cellule_fontaille_moyenne}' != 'null'  Input Text    cellule_fontaille_moyenne    ${cellule_fontaille_moyenne}
    Run Keyword If  '${cellule_hauteur_moyenne}' != 'null'  Input Text    cellule_hauteur_moyenne    ${cellule_hauteur_moyenne}
    Run Keyword If  '${cellule_fondcouleur_moyenne}' != 'null'  Input Text    cellule_fondcouleur_moyenne    ${cellule_fondcouleur_moyenne}
    Run Keyword If  '${cellule_bordure_moyenne}' != 'null'  Input Text    cellule_bordure_moyenne    ${cellule_bordure_moyenne}
    Run Keyword If  '${cellule_align_moyenne}' != 'null'  Input Text    cellule_align_moyenne    ${cellule_align_moyenne}
    Run Keyword If  '${cellule_fond_nbr}' != 'null'  Input Text    cellule_fond_nbr    ${cellule_fond_nbr}
    Run Keyword If  '${cellule_fontaille_nbr}' != 'null'  Input Text    cellule_fontaille_nbr    ${cellule_fontaille_nbr}
    Run Keyword If  '${cellule_hauteur_nbr}' != 'null'  Input Text    cellule_hauteur_nbr    ${cellule_hauteur_nbr}
    Run Keyword If  '${cellule_fondcouleur_nbr}' != 'null'  Input Text    cellule_fondcouleur_nbr    ${cellule_fondcouleur_nbr}
    Run Keyword If  '${cellule_bordure_nbr}' != 'null'  Input Text    cellule_bordure_nbr    ${cellule_bordure_nbr}
    Run Keyword If  '${cellule_align_nbr}' != 'null'  Input Text    cellule_align_nbr    ${cellule_align_nbr}
    Run Keyword If  '${cellule_numerique}' != 'null'  Input Text    cellule_numerique    ${cellule_numerique}
    Run Keyword If  '${cellule_total}' != 'null'  Input Text    cellule_total    ${cellule_total}
    Run Keyword If  '${cellule_moyenne}' != 'null'  Input Text    cellule_moyenne    ${cellule_moyenne}
    Run Keyword If  '${cellule_compteur}' != 'null'  Input Text    cellule_compteur    ${cellule_compteur}
    #Run Keyword If  '${om_sql}' != 'null'  Input Text    om_sql    ${om_sql}
    ${condition} =  Run Keyword And Return Status  Should Not Be Equal As Strings  ${om_sql}  null
    Run Keyword If  ${condition}  Input Text  om_sql  ${om_sql}
