*** Settings ***
Documentation  Module 'SIG interne'.

*** Keywords ***
Activer l'option 'SIG interne'
    [Tags]  module_sig_interne
    [Documentation]  Active l'option 'SIG interne'.

    Ajouter le paramètre depuis le menu  option_localisation  sig_interne  null


Désactiver l'option 'SIG interne'
    [Tags]  module_sig_interne
    [Documentation]  Désactive l'option 'SIG interne'.

    Supprimer le paramètre  option_localisation  sig_interne


Depuis le listing des étendues
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Accède au listing des étendues.

    Depuis le listing  om_sig_extent


Depuis le contexte de l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Accède à la fiche de consultation de l'étendue.
    [Arguments]  ${om_sig_extent}

    Depuis le listing des étendues
    # On recherche l'enregistrement
    Use Simple Search  om_sig_extent  ${om_sig_extent}
    # On clique sur le résultat
    Click On Link  ${om_sig_extent}
    # On vérifie qu'il n'y a pas d'erreur
    La page ne doit pas contenir d'erreur


Ajouter l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Ajoute un enregistrement de type 'étendue' (om_sig_extent).
    ...
    ...  Exemple :
    ...
    ...  | &{values} =  Create Dictionary
    ...  | ...  nom=testetendue01
    ...  | ...  extent=5.2267,43.2199,5.5756,43.3676
    ...  | ...  valide=true
    ...  | Ajouter l'étendue  ${values}
    ...
    [Arguments]  ${values}

    Depuis le listing des étendues
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir l'étendue  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Modifier l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Modifie l'enregistrement
    [Arguments]  ${om_sig_extent}  ${values}

    # On accède à l'enregistrement
    Depuis le contexte de l'étendue  ${om_sig_extent}
    # On clique sur le bouton modifier
    Click On Form Portlet Action  om_sig_extent  modifier
    # On saisit des valeurs
    Saisir l'étendue  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Supprimer l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Supprime l'enregistrement
    [Arguments]  ${om_sig_extent}

    # On accède à l'enregistrement
    Depuis le contexte de l'étendue  ${om_sig_extent}
    # On clique sur le bouton supprimer
    Click On Form Portlet Action  om_sig_extent  supprimer
    # On valide le formulaire
    Click On Submit Button


Saisir l'étendue
    [Tags]  om_sig_extent  module_sig_interne
    [Documentation]  Remplit le formulaire
    [Arguments]  ${values}

    Si "nom" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "extent" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "valide" existe dans "${values}" on execute "Set Checkbox" dans le formulaire


Depuis le listing des flux
    [Tags]  om_sig_flux  module_sig_interne
    [Documentation]  Accède au listing des flux.

    Depuis le listing  om_sig_flux


Ajouter le flux
    [Tags]  om_sig_flux  module_sig_interne
    [Documentation]  Ajoute un enregistrement de type 'flux' (om_sig_flux).
    ...
    ...  Exemple :
    ...
    ...  | &{values} =  Create Dictionary
    ...  | ...  id=testflux01
    ...  | ...  libelle=Libelle
    ...  | ...  attribution=...
    ...  | ...  cache_type=WMS
    ...  | ...  chemin=...
    ...  | ...  couches=...
    ...  | ...  cache_gfi_chemin=...
    ...  | ...  cache_gfi_couches=...
    ...  | Ajouter le flux  ${values}
    ...
    [Arguments]  ${values}

    Depuis le listing des flux
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir le flux  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Saisir le flux
    [Tags]  om_sig_flux  module_sig_interne
    [Documentation]  Remplit le formulaire de type 'flux' (om_sig_flux).
    [Arguments]  ${values}
    Si "libelle" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "om_collectivite" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "id" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "attribution" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "chemin" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "couches" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "cache_type" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "cache_gfi_chemin" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "cache_gfi_couches" existe dans "${values}" on execute "Input Text" dans le formulaire


Depuis le listing des cartes
    [Tags]  om_sig_map  module_sig_interne
    [Documentation]  Accède au listing des cartes.

    Depuis le listing  om_sig_map


Ajouter la carte
    [Tags]  om_sig_map  module_sig_interne
    [Arguments]  ${values}
    [Documentation]  Ajoute un enregistrement de type 'carte' (om_sig_map).
    ...
    ...  Exemple :
    ...  | &{values} = | Create Dictionary
    ...  | ... | id=testcarte01
    ...  | ... | libelle=Libelle
    ...  | ... | actif=true
    ...  | ... | projection_externe=lambert93
    ...  | ... | zoom=10
    ...  | ... | fond_osm=true
    ...  | ... | fond_default=osm
    ...  | ... | util_recherche=true
    ...  | ... | om_sig_extent=testetendu01
    ...  | ... | librairie_cartographie=openlayers2
    ...  | ... | url=...
    ...  | ... | om_sql=SELECT ST_asText('01010000206A080000C6DE4AFF7E552B412CF66CF750D35741') as geom, '2' as titre, '3' as description, 4 as idx, '5' as plop
    ...  | Ajouter la carte | ${values}
    ...

    Depuis le listing des cartes
    # On clique sur le bouton ajouter
    Click On Add Button
    # On saisit des valeurs
    Saisir la carte  ${values}
    # On valide le formulaire
    Click On Submit Button
    Valid Message Should Be  Vos modifications ont bien été enregistrées.


Saisir la carte
    [Tags]  om_sig_map  module_sig_interne
    [Arguments]  ${values}
    [Documentation]  Remplit le formulaire

    Si "om_collectivite" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "id" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "libelle" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "actif" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "zoom" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "fond_osm" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "fond_bing" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "fond_sat" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "layer_info" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "projection_externe" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "librairie_cartographie" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "url" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "om_sql" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "util_idx" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "util_reqmo" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "util_recherche" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "source_flux" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "fond_default" existe dans "${values}" on execute "Select From List By Label" dans le formulaire
    Si "om_sig_extent" existe dans "${values}" on sélectionne la valeur sur l'autocomplete "om_sig_extent" dans le formulaire
    Si "restrict_extent" existe dans "${values}" on execute "Set Checkbox" dans le formulaire
    Si "sld_marqueur" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "sld_data" existe dans "${values}" on execute "Input Text" dans le formulaire
    Si "point_centrage" existe dans "${values}" on execute "Input Text" dans le formulaire

