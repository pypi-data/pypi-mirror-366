*** Settings ***
Documentation     Ressources (librairies, ressources, variables et keywords)

# Librairies
Library           Collections
Library           OperatingSystem
Library           RequestsLibrary
Library           Selenium2Library
Library           String
Library           Selenium2Screenshots
Library           ArchiveLibrary
Library           DateTime
Library           Process

# # Mots-clefs Framework
# Resource          formulaire.robot
# Resource          menu.robot
# Resource          navigation.robot
# Resource          pdf.robot
# Resource          tableau.robot
# Resource          utils.robot
# Resource          module_gen.robot
# Resource          module_reqmo.robot
# Resource          module_import.robot
# Resource          module_sig_interne.robot

# # Mots-clefs objet Framework
# Resource          om_collectivite.robot
# Resource          om_droit.robot
# Resource          om_requete.robot
# Resource          om_lettretype.robot
# Resource          om_parametre.robot
# Resource          om_profil.robot
# Resource          om_sousetat.robot
# Resource          om_utilisateur.robot
# Resource          om_widget.robot
# Resource          om_etat.robot
# Resource          om_logo.robot

*** Variable ***
${TIMEOUT}         20 sec
${RETRY_INTERVAL}  0.2 sec
${CLIC_CONFIRM_WAIT}  10 sec
${OM_ROUTE_DASHBOARD}  app/index.php?module=dashboard
${OM_ROUTE_LOGIN}  app/index.php?module=login
${OM_ROUTE_LOGOUT}  app/index.php?module=logout
${OM_ROUTE_PASSWORD}  app/index.php?module=password
${OM_ROUTE_PASSWORD_RESET}  app/index.php?module=login&mode=password_reset
${OM_ROUTE_TAB}  app/index.php?module=tab
${OM_ROUTE_SOUSTAB}  app/index.php?module=soustab
${OM_ROUTE_FORM}  app/index.php?module=form
${OM_ROUTE_SOUSFORM}  app/index.php?module=sousform
${OM_ROUTE_MAP}  app/index.php?module=map
${OM_ROUTE_MODULE_EDITION}  app/index.php?module=edition
${OM_ROUTE_MODULE_GEN}  app/index.php?module=gen
${OM_ROUTE_MODULE_REQMO}  app/index.php?module=reqmo
${OM_ROUTE_MODULE_IMPORT}  app/index.php?module=import
${OM_PDF_TITLE}  index
${OM_IGNORE_CASE}  False
${OM_TITLE_LOGIN}  Veuillez Vous Connecter
${OM_TITLE_DASHBOARD}  Tableau De Bord

*** Keywords ***
Tests Setup
    [Tags]  om_resources
    # Définit les variables globales dates du jour
    ${DATE_DDMMYYYY} =  Date du jour FR
    ${DATE_YYYYMMDD} =  Date du jour EN
    ${DATE_FORMAT_YYYY-MM-DD} =  Date du jour au format yyyy-mm-dd
    ${DATE_FORMAT_YYYYMMDD} =  Date du jour au format yyyymmdd
    ${DATE_FORMAT_DD/MM/YYYY} =  Date du jour au format dd/mm/yyyy
    Set Global Variable  ${DATE_DDMMYYYY}
    Set Global Variable  ${DATE_YYYYMMDD}
    Set Global Variable  ${DATE_FORMAT_YYYY-MM-DD}
    Set Global Variable  ${DATE_FORMAT_YYYYMMDD}
    Set Global Variable  ${DATE_FORMAT_DD/MM/YYYY}

