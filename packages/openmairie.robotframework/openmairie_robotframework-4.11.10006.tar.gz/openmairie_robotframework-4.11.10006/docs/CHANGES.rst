Changelog
=========

4.11.10006 (2025-07-31)
-----------------------

- Ajout de trois Keyword 'Créer un fichier', 
  'Créer un fichier texte' et 'Créer un fichier binaire'
  pour créer des fichiers de façon programmée dans robotframework.
  [onosworthy]


4.11.10005 (2025-03-31)
-----------------------

- feat: add keyword 'Selection de valeur(s)' managing single and multiple select fields
  [epontagnier]


4.11.10004 (2024-06-20)
-----------------------

- feat: Add keywords "Supprimer un widget depuis le tableau de bord",
  "Supprimer un widget" and change "Ajouter un widget".
  [Rasseum]


4.11.10003 (2024-06-06)
-----------------------

- feat: Add keywords "Ajouter un widget", "Saisir les valeurs dans le
  formulaire d'un widget" and deprecate keywords "Ajouter le widget depuis le
  tableau de bord", "Saisir le widget".
  [Rasseum, flohcim]


4.11.10002 (2024-03-21)
-----------------------

- feat: Add vars '${OM_IGNORE_CASE}', '${OM_TITLE_LOGIN}', '${OM_TITLE_DASHBOARD}'
  to allow case flexibility on page titles in apps.
  [ebrodin, SebastienDethyreReal, flohcim]


4.11.10001 (2024-02-02)
-----------------------

- feat: Update 'Saisir la carte' keyword to align with the new version (removal of the 
  'retour' field and addition of the 'librairie_cartographie' field).
  [flohcim]


4.10.10001 (2023-10-11)
-----------------------

- Add keywords 'Le titre de la page doit être' and
  'Le titre de la page doit contenir' and deprecate keywords
  'Page Title Should Be' and 'Page Title Should Contain' adding ignore_case
  parameter.
  [flohcim]


4.9.10009 (2022-05-11)
----------------------

- Utils: fixed download problem with curl version since 7.72
  [flohcim]


4.9.10008 (2019-06-20)
----------------------

- Formulaire: clic timeout of 5sec replaced by new var CLIC_CONFIRM_WAIT
  [mbideau]


4.9.10007 (2019-04-01)
----------------------

- Formulaire: fixed 'Click...Until' keywords using a list of WebElements instead of
  the first found WebElement
  [mbideau]


4.9.10006 (2019-04-01)
----------------------

- PDF: fixed typo on keyword 'PDF Move Page To'"
  [mbideau]

- Formulaire: semantic change: 'Click...Confirmed By' replaced by 'Click...Until'
  [mbideau]


4.9.10005 (2019-03-28)
----------------------

- Added 9 keywords in 'formulaire.robot':
  4 'Click Element Confirmed By <some_action>',
  2 'Click On Submit Button (In Subform) Confirmed By Message',
  2 to check messages content,
  1 'Click On Portlet Action';
  and modified many other keywords to use them.
  [mbideau]


4.9.10004 (2019-02-25)
----------------------

- Fixed PDF keywords 'PDF Page Number Should (Not) Contain' that failed when page
  content were not loaded (async), by moving to required page before testing its
  content (added new Keyword: PDF Move Page To).
  [mbideau]


4.9.10003 (2018-12-13)
----------------------

- Fixed "Click On Submit Button" and "Click On Submit Button In Subform" by
  retrying multiple times to click if no validation message apparead within a timeout.
  [mbideau]


4.9.10002 (2018-11-28)
----------------------

- More documentation.
  [flohcim]

- Replace deprecated keywords call by new keywords.
  [flohcim]


4.9.10001 (2018-11-19)
----------------------

- Deprecate 'Ajouter le état...' and add 'Ajouter l'état...' to replace it.
  [flohcim]

- Add 'Depuis le contexte de l'état dans le contexte de la collectivité' keyword.
  [flohcim]


4.8.10006 (2018-05-02)
----------------------

- Replace deprecated keywords call by new keywords.
  [flohcim]

- Correct tag 'om_reqmo'. The correct name is 'module_reqmo'.
  [flohcim]


4.8.10005 (2018-04-28)
----------------------

- Rename field 'Identifiant' by 'id' in keywords 'Depuis le contexte de la
  lettre-type' and 'Depuis le contexte de l'état'.
  [flohcim]

- Add keywords 'La page ne doit pas contenir d'erreur', 'Depuis le listing',
  'Depuis la page de login', 'Depuis le formulaire d'ajout d'un utilisateur'.
  [flohcim]

- More documentation.
  [flohcim]


4.8.10004 (2018-04-26)
----------------------

- Correct problem with keyword 'Depuis l'assistant "Migration état, sous-état, lettre type"'.
  [flohcim]


4.8.10003 (2018-04-26)
----------------------

- Add keywords 'Depuis le listing des états', 'Depuis le listing des lettres-types',
  'Depuis le listing des paramètres', 'Depuis le listing des utilisateurs'.
  [flohcim]

- Add documentation.
  [flohcim]


4.8.10002 (2018-04-25)
----------------------

- Add keyword 'Depuis le listing des collectivitÃ©s'.
  [flohcim]

- Add documentation.
  [flohcim]


4.8.10001 (2018-04-18)
----------------------

- Remove Warning "Using 'Get Element Attribute' without explicit attribute is deprecated.".
  [flohcim]


4.7.10001 (2017-11-23)
----------------------

- Initial release as a python package.
  [cerini_j, flohcim, fmichon, jcerini, jymadier, KBurles, mbroquet, nhaye,
  NHaye, nmeucci, oc1n, softime, stimezouaght, tiazma, vpihour]

