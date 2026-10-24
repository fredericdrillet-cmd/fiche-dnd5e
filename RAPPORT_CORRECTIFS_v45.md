# Rapport d'audit et correctifs v45

## 1. Assistant de niveau : superposition Faveur de pacte / Style de combat

### Cause
1. À l'ouverture, l'assistant construit l'étape « Choix du niveau » pour la **première classe proposée**, ici l'Occultiste. La Faveur de pacte est placée dans une **grille imbriquée** (`QGridLayout` insérée dans la page).
2. Quand on sélectionne Guerrier, la page est vidée par `clear_layout()`. Cette fonction ne détruisait que les widgets **directs** de la page, pas ceux des sous-layouts. Le libellé et la liste « Faveur de pacte » restaient donc vivants et visibles.
3. La nouvelle carte « Style de combat » venait se dessiner par-dessus ces widgets restants.

### Correctifs
- **`ui/game_widgets.clear_layout`** :
  - parcourt récursivement les sous-layouts ;
  - masque chaque widget **immédiatement** (`hide()`), le détache (`setParent(None)`) puis le détruit (`deleteLater()`).
  
  Le correctif profite aussi aux autres écrans reconstruits : tuiles du tour, effets, compagnons.
- **`ui/levelup_dialog._build_choices`** :
  - la Faveur de pacte et les manifestations occultes ne s'affichent **que si le niveau est pris en Occultiste** ;
  - les styles de combat proposés sont uniquement ceux de la classe qui monte ;
  - un niveau de Guerrier n'affiche donc que les choix du Guerrier.

## 2. Repos long
La carte fait au moins 760 px de large et la fenêtre au moins 820 px (620 et 680 px pour le repos court). Les listes « Rechargé à la fin du repos » et « Sorts pour la journée à venir » ne sont plus tronquées ni renvoyées à la ligne inutilement.

## 3. Dons de maîtrise d'armures
- **Dons ajoutés** : `Dons.json` ne contenait pas « Maîtrise des armures légères », « … intermédiaires » ni « … lourdes ». Ils sont ajoutés au chargement (`EXTRA_FEATS`) sans modifier votre fichier.
- **Maîtrises accordées** : `FEAT_PROFICIENCIES` associe chaque don à ses maîtrises. « Intermédiaires » donne aussi les boucliers. Les variantes de nom « Armuré » et « Cuirassé » sont reconnues.
- **Nouvelle source** : `proficiency_sources()` crée une source de mode `don`. Elle est prise en compte dans les maîtrises d'armures, donc par les avertissements ⚠, le désavantage et le blocage des sorts.
- **Affichage de l'origine** dans l'encart « Maîtrises » de l'onglet Classes, par exemple « Armures lourdes (Accordé par le Don : Maîtrise des armures lourdes) ».

## 4. Jet d'initiative interactif
- **`core/initiative.py`**, méthode `initiative_detail()`. Le modificateur additionne :
  - la Dextérité ;
  - les dons (Alerte +5) ;
  - Touche-à-tout ou Athlète remarquable (le plus élevé des deux) ;
  - Embusqué redoutable (+ Sag), Audace désinvolte (+ Cha), Prescience de bataille (+ Cha, minimum 1), Esprit tactique et Conscience temporelle (+ Int) ;
  - les effets actifs.
  
  Instinct sauvage et Maître de l'embuscade donnent l'avantage. `Engine.initiative()` utilise désormais ce calcul.
- **Dé cliquable** dans l'en-tête (badge « Init +X ») et dans l'encart Initiative de l'onglet Combat. Le clic lance 1d20 + modificateur dans la fenêtre de dés animée, avec le détail du calcul ligne par ligne. Le dernier jet est gardé (`initiative_jet`), affiché sous la valeur et rappelé dans la barre d'état.

## 5. Forme sauvage (et Métamorphose)
- **Tuiles de la bête** : `turn_actions()` génère une tuile `bete:N` par attaque de la bête (par exemple « Morsure — Loup ») dans le groupe « Attaques ». Elles sont limitées par l'action Attaquer comme les armes.
- **Déroulé de l'attaque** : jet de toucher calculé avec la FOR/DEX et la maîtrise de la bête, question « L'attaque touche-t-elle ? », puis dégâts de la bête (doublés en cas de critique).
- **Fin de la transformation** : pendant la forme, les attaques d'arme, à mains nues et en main secondaire sont masquées. Quand la forme prend fin (bouton, 0 PV ou repos), les tuiles de la bête disparaissent et les actions habituelles reviennent, puisque les tuiles sont recalculées à chaque rafraîchissement.

## 6. Objets magiques : liaison avec l'équipement
### Modèle (`core/magic_gear.py`)
- **Entrée d'inventaire** :
  `{"nom": "Arme +2", "base": "Épée à deux mains", "uid": "mg1", "bonus", "equipe", "harmonise"}`
- **Nom affiché** : « Épée à deux mains +2 » pour un objet +X ; « Épée ardente (Épée longue) » pour un objet nommé.
- **Objet de base** : `magic_base_options()` filtre selon la précision du catalogue.
  - « toute épée » donne épées, rapière et cimeterre ;
  - « toute épée qui inflige des dégâts tranchants » exclut la rapière ;
  - « harnois » ne propose que le harnois ;
  - « intermédiaire ou lourde mais pas de peau » exclut l'armure de peaux ;
  - une précision générale propose tout.

### Équipement et application du bonus
- **Équiper** : `equip_magic_gear()` place l'objet de base dans la bonne case (main principale ou distance, armure, main secondaire pour un bouclier). La case reçoit `bonus`, `objet` (uid) et `affichage`.
- **Bonus appliqué par les calculs existants** :
  - arme : +X au toucher (ligne « Arme magique ») et aux dégâts ;
  - armure : `armure["bonus"]` ;
  - bouclier : `armure["bonus_bouclier"]`.
- **Pas de double comptage** : `magic_item_bonuses()` ignore ces objets, puisque le bonus est déjà porté par la case.
- **`sync_magic_gear()`**, à chaque normalisation :
  - rompt le lien si la case a changé d'objet ou si l'objet a été retiré ;
  - met le bonus à 0 si l'objet exige une harmonisation qui n'est pas faite ;
  - met à jour l'état « équipé » de l'objet ;
  - retirer l'objet de l'inventaire vide aussi sa case.

### Interface
- **Ajout** : depuis le catalogue ou l'ajout rapide, un sélecteur « objet de base » s'ouvre ; il est choisi d'office s'il n'y a qu'une possibilité.
- **Inventaire principal** : les objets magiques sont listés après les objets courants, avec ✨, nom en couleur dorée, état (équipé, case, harmonisation) et avertissement ⚠ si l'objet n'est pas maîtrisé. Les boutons « ✨ Équiper / déséquiper », « Utiliser » et « Retirer la ligne » fonctionnent sur ces lignes.
- **Mannequin** : chaque case propose les objets magiques compatibles et affiche un badge ✨ quand l'objet porté est magique.
- **Panneau objets magiques** : nom explicite et bonus « +2 toucher / dégâts » ou « +1 CA ».

### Capacités activables (tuiles de combat)
- **Détection** : `magic_item_powers()` analyse la description des objets actifs (équipés, et harmonisés si nécessaire). Elle repère :
  - l'économie d'action à sa première mention (action, action bonus, réaction) ;
  - les charges (« possède 7 charges ») ;
  - les sorts lancés, y compris les listes « l'un des sorts suivants : mains brûlantes (1 de charge), boule de feu (3 charges)… ».
- **Tuiles** : groupe « 💎 Objets magiques », une tuile par capacité ou par sort.
  - Badge `[Objet Magique : Nom]` et charges restantes affichées.
  - Tuile grisée si les charges manquent, ou en armure non maîtrisée pour un sort.
- **Utilisation** :
  - l'économie d'action est dépensée et les charges sont décomptées ;
  - un sort suit la résolution habituelle (attaque, DD, dégâts, soins), sans emplacement ;
  - sinon l'effet de l'objet est rappelé dans une fenêtre ;
  - les charges sont rechargées au repos long (« à l'aube »).
- **Exemple** : Bouclier expressif équipé, tuile « Utiliser — Bouclier expressif (Bouclier) » en action bonus.

## 7. Fichiers
- **Nouveaux** : `core/magic_gear.py`, `core/initiative.py`, `tests/test_v45_items_init_wildshape.py` (17 tests).
- **Modifiés** :
  - moteur : `core/engine.py`, `core/equipment.py`, `core/proficiencies.py`, `core/data_loader.py`, `core/turn.py`, `core/combat_flow.py`, `core/engine_extras.py`, `core/character.py` ;
  - interface : `ui/game_widgets.py`, `ui/levelup_dialog.py`, `ui/rest_dialog.py`, `ui/combat_tab.py`, `ui/main_window.py`, `ui/dice_dialog.py`, `ui/inventory_tab.py`, `ui/magic_items_panel.py`, `ui/paperdoll.py`, `ui/classes_tab.py`.
- **Ancien test mis à jour** : `test_v41` (liste des groupes de tuiles, qui compte désormais le groupe « objets »).

## 8. Validation et limites
- **Tests** : la suite complète passe, **554 tests OK** et 4 ignorés.
- **Interface simulée** : les tests utilisent un faux module Qt, et PyQt6 n'a pas pu être installé ici. Il reste à vérifier dans l'application réelle :
  - la disparition effective de la superposition dans l'assistant ;
  - la largeur de la fenêtre de repos ;
  - l'apparence des dés d20 et des lignes ✨.
- **Lecture des descriptions** : la détection des capacités d'objet repose sur le texte des descriptions. Un objet au texte inhabituel peut ne pas produire de tuile ou être classé dans une autre économie d'action. Les sorts lancés par un objet sont résolus avec le DD du personnage ; si l'objet impose son propre DD (par exemple « sauvegarde DD 15 »), il figure dans l'infobulle de la tuile.
