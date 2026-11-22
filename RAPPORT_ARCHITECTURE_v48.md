# Rapport d'architecture UI/UX v48 — création façon Baldur's Gate 3

## 1. Assistant de création niveau 1 (`ui/creation_wizard.py`)

### Ouverture et principe
- **Ouverture** : *Fichier > Nouveau personnage…* (Ctrl+N), et automatiquement au premier lancement quand aucun personnage n'est à rouvrir.
- **Copie de travail** : tout se fait sur une copie (`Engine` neuf). *Annuler* ne touche pas la fiche ; *✔ Créer le personnage* la remplace. Le personnage n'est pas encore enregistré, mais la sauvegarde automatique le protège.
- **Disposition** :
  ```
  ┌ Étapes ○/✔ ─┬──────────── Page de l'étape ─────────────┬─ Résumé dynamique ──┐
  │ 1 Race       │ (panneaux de la fiche réutilisés)        │ nom, race, classe,   │
  │ 2 Classe     │                                          │ historique, carac.,  │
  │ …            │                                          │ PV / CA / vitesse,   │
  │ 7 Identité   │                                          │ compétences, sorts,  │
  └──────────────┴──────────────────────────────────────────┴ équipement, ○ reste ┘
  ```

### Étapes
| Étape | Contenu |
|---|---|
| 1. Race / Sous-race | Panneau Race de la fiche : illustration, traits survolables |
| 2. Classe | Dé de vie, PV, maîtrises ; sous-classe de niveau 1 (Clerc, Ensorceleur, Occultiste) ; style de combat ; compétences et expertises |
| 3. Historique | Panneau Historique + Langues de la fiche |
| 4. Caractéristiques | Panneau Caractéristiques (achat de points, dés, saisie) et bonus raciaux |
| 5. Sorts | Tours de magie et sorts de niveau 1 avec quotas ; magie raciale [Sort Racial] |
| 6. Équipement | Paquetage de classe ou boutique (§ 3) |
| 7. Identité | Nom du personnage, joueur, alignement ; liste des choix encore ouverts |

### Réutilisation des écrans
- **Principe** : les écrans Race, Historique, Caractéristiques et Compétences sont les panneaux de la fiche, branchés sur la copie par un hôte léger (`WizardHost`). Ils fournissent `engine`, `changed()`, `mark_dirty()`, `statusBar()`…
- **Conséquence** : aucune règle n'est dupliquée, et tout ce que la fiche sait faire (bonus raciaux libres, achat de points, langues au choix) fonctionne dans l'assistant.
- **Choix ouverts** : jamais bloquants. Les pastilles ○ des étapes et la page Identité les listent. Ils restent signalés sur la fiche après la création.

## 2. Magie raciale pour les classes non lanceuses (`core/creation.py`, `ui/magic_tab.py`, `core/turn.py`)
- **Sorts raciaux** : `racial_spells()` lisait déjà les sorts raciaux des traits (Tieffelin : Thaumaturgie, puis Représailles infernales et Ténèbres ; Githyanki : Main de mage… ; Drow (Elfe noir) : Lumières dansantes…).
- **Sort mineur au choix (nouveau)** : un trait « sort mineur de votre choix de la liste du magicien » (Haut-elfe) ouvre un emplacement de choix, enregistré dans `ch.sorts_raciaux`. Les sorts proposés sont les tours de magie de cette liste ; l'Intelligence est la caractéristique d'incantation. Tant que le choix manque, la pastille ○ « 1 sort mineur racial à choisir » s'affiche.
- **Onglet Magie** : l'encart « ✦ Magie raciale — [Sort Racial] » est visible quelle que soit la classe, avec le sélecteur du Haut-elfe et la mention **[Sort Racial]** sur chaque sort.
- **Onglet Combat** : les sorts raciaux disponibles donnent des tuiles dans « ✨ Sorts et magie », d'origine « sort mineur [Sort Racial] ». Exemple vérifié : un Guerrier tieffelin a sa tuile Thaumaturgie.
- **Gnome des roches** : ses traits (Ruse gnomique, Bricoleur) ne contiennent pas de sort dans les données. C'est le Gnome des forêts qui a *Illusion mineure*, et elle est déjà gérée.

## 3. Matériel d'historique et boutique
- **Équipement de l'historique** : toujours offert. Il est lu dans `inventaire_historique` et croisé avec le catalogue.
- **Paquetage de classe** : version standard (option « a » du Manuel des joueurs, `CLASS_KITS`), plus l'or de l'historique.
  - Exemple, Guerrier : cotte de mailles, épée longue, bouclier, arbalète légère et 20 carreaux, paquetage d'exploration souterraine.
  - Armure, bouclier et armes sont **équipés automatiquement** (`auto_equip`), comme dans BG3.
- **Boutique** :
  - **Budget** : or de départ de la classe (table « richesse de départ », par exemple 5d4 × 10 po pour un Guerrier). Par défaut, c'est la moyenne ; « 🎲 Lancer l'or de départ » tire les dés. S'y ajoute l'or de l'historique.
  - **Catalogue** : prix convertis en po (pa et pc comprises), filtres par catégorie et recherche. Les objets trop chers sont grisés et refusés.
  - **Panier** : un double-clic retire un exemplaire. Après un nouveau jet plus faible, le panier est réduit automatiquement.
  - **Validation** : les achats rejoignent l'inventaire principal ; le reste est versé dans la bourse en po / pa / pc.

## 4. Interface principale
- **En-tête** : le champ Alignement est retiré, et le champ Joueur s'agrandit à la place. L'alignement se règle dans *Histoire, Portrait*, sous le portrait, et dans l'assistant (étape Identité). Il reste utilisé pour les conditions d'harmonisation des objets magiques.
- **Onglet Race** : remplacé par l'encart **« ☗ Résumé de la race »** à côté du portrait (race, sous-race, historique, langues, sorts raciaux [Sort Racial], traits). Il reste disponible en Mode libre, ou tant qu'un choix de langue y est en attente, pour ne jamais rendre un choix impossible.
- **Onglet Caractéristiques & Compétences** : en Mode guidé, les sélecteurs bruts sont remplacés par un résumé en lecture seule (valeur et modificateur). Les compétences restent affichées et cochables. Les sélecteurs réapparaissent en Mode libre, ou si une ancienne fiche a encore un choix de caractéristique à faire.
- **Onglet Classes** : en Mode guidé, c'est un résumé consultatif (aptitudes, frise de progression, maîtrises).
  - Classe, niveau, retrait et ajout de classe sont verrouillés : on passe par « ▲ Niveau supérieur », multiclassage compris (bouton « Multiclassage » conservé).
  - La sous-classe reste sélectionnable tant qu'elle est à choisir.

## 5. Mode guidé et Mode libre
- **Réglage** : *Options > Mode d'édition de la fiche > « Activer le Mode libre »* (enregistré dans les préférences). Il est désactivé par défaut.
- **Mode guidé** : le nom du personnage est en lecture seule, le compteur de niveau global est grisé, et les écrans décrits au § 4 sont verrouillés.
- **Mode libre** : toute la fiche redevient modifiable, comme avant la v48.

## 6. Sauvegarde automatique et menu Fichier
- **Copie de sécurité** : 1,5 s après chaque modification, une copie est écrite dans `%APPDATA%\Fiche_DnD5E\sauvegarde_auto.json`. Elle indique le fichier d'origine et la présence de modifications non enregistrées. Le fichier du joueur n'est jamais écrasé sans son accord.
- **Au lancement** : si la copie contient des modifications non enregistrées (ou un personnage jamais sauvegardé), elle est rouverte. Sinon, c'est le **dernier fichier sauvegardé** (`dernier_fichier` dans les préférences). Sinon, l'assistant de création s'ouvre.
- **« Ne pas enregistrer » en quittant** : la copie de sécurité est supprimée.
- **Menu Fichier** : *Nouveau personnage… (assistant de création)*, *Charger…*, *Sauvegarder*, *Sauvegarder sous…*, puis *Niveau supérieur…* et *Quitter*.

## 7. Exécutable
Le `.exe` n'est **pas joint**, pour la même raison qu'en v47 : cet environnement est un serveur Linux, sans PyInstaller ni PyQt6. Le code est prêt à compiler. Sous Windows, un double-clic sur `compiler_windows.bat` (corrigé en v47.1) produit `dist\Fiche_Personnage_DnD5E.exe` ; le flux GitHub le fait aussi automatiquement.

## 8. Fichiers et validation
- **Nouveaux** : `core/creation.py`, `ui/creation_wizard.py`, `tests/test_v48_creation.py` (14 tests).
- **Modifiés** :
  - moteur : `core/engine.py`, `core/character.py` (`sorts_raciaux`), `core/missing.py`, `core/turn.py`, `core/settings.py` ;
  - interface : `ui/main_window.py`, `ui/options_dialog.py`, `ui/stats_tab.py`, `ui/classes_tab.py`, `ui/rp_tab.py`, `ui/magic_tab.py`, `ui/race_tab.py`.
- **Anciens tests** : trois tests vérifiant l'édition directe tournent désormais en Mode libre (`test_v15`, `test_v16`, `test_v21`).
- **Résultat** : **584 tests OK**, 4 ignorés.
- **Limite** : ces tests passent par une interface simulée (sans PyQt6 réel). La mise en page de l'assistant (trois colonnes, défilement) et de l'encart de race reste à vérifier à l'écran.
