# Rapport des correctifs UI v50

## 1. Plein écran et adaptabilité
**Cause** : l'assistant de création (comme « Niveau supérieur ») était une modale **sans cadre** (`FramelessWindowHint`) à fond transparent. Sans barre de titre, Windows ne propose ni bouton Agrandir ni redimensionnement par les bords. De plus, les pages Race et Historique n'avaient pas de défilement : en petite fenêtre, leur contenu était écrasé.

**Correctifs** :
- **Vraies fenêtres** : les deux assistants sont désormais des fenêtres (`Qt.Window` + `WindowTitleHint`, `WindowSystemMenuHint`, `WindowMinMaxButtonsHint`, `WindowCloseButtonHint`), avec titre, boutons Réduire / Agrandir / Fermer et redimensionnement libre. La poignée en bas à droite est conservée.
- **Bouton « ⛶ Plein écran »** dans l'assistant de création : il bascule entre fenêtre maximisée et « 🗗 Taille normale ».
- **Taille de départ** : 85 % de l'écran, jamais plus grande que lui.
- **Défilement** : toutes les pages de l'assistant défilent, y compris Race et Historique.
- **Fenêtre principale** : taille minimale ramenée de 1280 × 720 à 1024 × 640 ; elle reste maximisable.

## 2. Validation d'un personnage incomplet
- **Liste des manques** : `incomplete_items()` regroupe les choix manquants du moteur (compétences, expertises, style, langues, sorts, bonus de caractéristiques…). S'y ajoutent l'équipement (boutique choisie sans aucun achat) et l'identité (nom vide).
- **Modale de confirmation** : si la liste n'est pas vide, « ✔ Créer le personnage » ouvre la modale du thème (fond flouté) :
  - **Titre** : « Création de personnage incomplète » ;
  - **Message** : le texte demandé, suivi de la liste « À finaliser » ;
  - **Boutons** :
    - **[ Poursuivre la création ]** (par défaut) ramène l'assistant à la **première étape incomplète** ;
    - **[ Valider malgré tout ]** crée la fiche, et les manques restent signalés par les pastilles ○.

## 3. Cases à cocher visibles
- **Cause** : la feuille de style ne dessine pas la case des `QCheckBox` (seul le libellé est stylé). Selon le thème, la case se confondait avec le fond. Dans l'Inventaire, la case « Sac sans fond » partageait aussi sa ligne avec le long libellé de charge, qui la poussait hors champ.
- **Correctifs** :
  - **Inventaire** :
    - « 🎒 Possède un Sac sans fond » a sa propre ligne, sous la charge (libellé à la ligne si besoin) ;
    - la case est dessinée de façon contrastée (`indicator_qss` : 18 px, bordure d'ornement, fond d'accent une fois cochée) ;
    - la page Équipement défile (largeur minimale de 1000 px conservée).
  - **Options** :
    - contenu dans une zone défilante, boutons Annuler / Valider toujours visibles en bas ;
    - cases « Règle de survie » et « Activer le Mode libre » au même style contrasté, avec une hauteur minimale ;
    - fenêtre de 820 × 760 au départ, 560 px de haut au minimum.
- **Thème BG3** : le style global du thème n'est pas modifié. La correction ne s'applique qu'à ces cases, pour respecter la consigne de ne pas toucher au thème.

## 4. Onglet Classes et multiclassage
- **Interrupteur retiré** : le bouton « ⚔ Multiclassage : activé / désactivé » n'est plus affiché.
- **Multiclassage par « Niveau supérieur »** : `level_up_options()` propose **toujours** les autres classes.
  - **Prérequis officiels** : ils sont vérifiés (13 dans la caractéristique de la classe visée ET dans celle de chaque classe actuelle).
  - **Mode guidé** : un prérequis non rempli bloque « Confirmer », avec le motif en infobulle.
  - **Mode libre** : l'avertissement reste, mais le choix est permis (accord du MJ).
- **Ajout direct d'une classe** dans l'onglet Classes : il n'existe qu'en Mode libre.

## 5. En-tête selon le mode
- **Mode guidé (par défaut)** :
  - **En-tête de la fiche** : le compteur « Niveau global » est remplacé par un badge statique « ⚔ **Guerrier** 3 · *Champion* — Niveau 3 », une entrée par classe en multiclassage, avec une infobulle explicative.
  - **Onglet Classes** : la ligne de sélecteurs (Classe, Niveau, Sous-classe, Retirer) est remplacée par des badges stylés (classe en couleur d'accent, niveau, sous-classe ou « sous-classe au niveau N ») et la mention « Lecture seule — « ▲ Niveau supérieur » pour progresser ».
  - **Ancienne fiche sans sous-classe** : si la sous-classe reste à choisir, le sélecteur réapparaît pour ce seul choix.
- **Mode libre** : les sélecteurs interactifs (classe, sous-classe, niveau par classe, niveau global) sont rétablis.

## 6. Exécutable
Le `.exe` n'est toujours pas joint : cet environnement de développement est un serveur Linux, sans PyInstaller ni PyQt6. Sous Windows, `compiler_windows.bat` le génère dans `dist\Fiche_Personnage_DnD5E.exe`.

## 7. Fichiers et validation
- **Modifiés** :
  - interface : `ui/creation_wizard.py`, `ui/levelup_dialog.py`, `ui/main_window.py`, `ui/classes_tab.py`, `ui/inventory_tab.py`, `ui/options_dialog.py` ;
  - moteur : `core/levelup.py`.
- **Tests** :
  - nouveaux : `tests/test_v50_ui_fixes.py` (8 tests) ;
  - mis à jour : `test_v29` et `test_v21` (multiclassage sans interrupteur).
- **Résultat** : **601 tests OK**, 4 ignorés.
- **Limite** : ces tests utilisent une interface simulée. Le comportement de maximisation sous Windows et le rendu des cases restent à vérifier à l'écran.
