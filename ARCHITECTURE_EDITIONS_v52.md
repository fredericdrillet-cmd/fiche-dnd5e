# v52 — Éditions 2014 / 2024 / libre et règles de la table

Ce document décrit l'architecture retenue, ce qui est **livré dans cette étape** (étape 1) et ce qui reste à faire (étape 2), avec les décisions qui t'appartiennent. Cible : l'application **bureau** (PyQt6). Le moteur `core/` étant partagé, la version web bénéficie des mêmes règles sans interface dédiée pour l'instant.

## 1. Architecture

```
data/*.json              données actuelles de l'app (2014, auditées) — inchangées, édition implicite 2014
data/editions/*.json     nouvelles données de référence (2014 + 2024, champ `edition`, identifiants stables `id`)
core/editions.py         modes, filtrage, badge, catalogue `EditionCatalog`, multiclassage inter-éditions
core/house_rules.py      registre des règles de la table, valeurs par défaut par mode, résolution
core/character.py        `edition_mode`, `regles_optionnelles`, `inspiration` ; `edition` sur chaque entrée de classe
core/settings.py         `edition_defaut`, `regles_defaut` (valeurs des nouveaux personnages)
ui/rules_dialog.py       fenêtre « Règles de la table » (menu Options)
```

### État : où vivent le mode et les règles

| Donnée | Emplacement | Pourquoi |
|---|---|---|
| Mode d'édition (`"2014"`, `"2024"`, `"libre"`) | **dans le personnage** (`Character.edition_mode`) | Un personnage 2014 reste 2014 quand on en ouvre un autre ; la sauvegarde JSON est autonome (bureau et web lisent le même fichier). |
| Règles de la table (`{clé: bool}`) | **dans le personnage** (`Character.regles_optionnelles`) | Même raison ; une clé absente prend la valeur par défaut du mode. |
| Édition de chaque classe | **dans l'entrée de classe** (`{"nom", "niveau", …, "edition": 2024}`) | Indispensable au multiclassage inter-éditions (Guerrier 2024 + Roublard 2014). |
| Valeurs par défaut de la table | **préférences** (`edition_defaut`, `regles_defaut`) | Appliquées à chaque nouveau personnage (assistant de création et personnage vierge). |

L'équivalent d'un « store » dans cette application est le couple `Character` (état) + `Engine` (lecture et commandes). Les nouvelles commandes du moteur : `edition_mode`, `set_edition_mode()`, `house_rules()`, `rule_active(clé)`, `set_house_rule()`, `edition_problems()`.

### Fonctions de filtrage (`core/editions.py`)

| Fonction | Rôle |
|---|---|
| `normalize_mode(v)` | valeur enregistrée → `"2014"`, `"2024"` ou `"libre"` |
| `editions_of_mode(mode)` | éditions autorisées (`{2014}`, `{2024}`, `{2014, 2024}`) |
| `item_edition(item)` | édition d'un élément (champ `edition`, sinon 2014) |
| `allowed(item, mode)` / `filter_items(items, mode, dedupe=True)` | filtrage ; `dedupe` retire les réimpressions (`doublon_de`) |
| `badge(item, mode)` / `label(nom, item, mode)` | « 2024 » / « Guerrier [2024] » en mode libre seulement |
| `EditionCatalog.list(type, mode, **filtres)` | ex. `list("sous_classes", "libre", classe="Guerrier")` |
| `EditionCatalog.subclasses_of()`, `spells_for_class()`, `find()`, `get(id)`, `counts()` | liens et recherches |

### Multiclassage inter-éditions

Chaque classe compte **selon sa propre édition** (`editions.spell_slots`, utilisé par `Engine.spell_slots`) :

| Cas | 2014 | 2024 |
|---|---|---|
| Demi-incantateur (Paladin, Rôdeur) en multiclassage | moitié des niveaux, **arrondi inférieur** | moitié des niveaux, **arrondi supérieur** |
| Demi-incantateur seul | sorts à partir du niveau 2 | sorts **dès le niveau 1** |
| Tiers d'incantateur (Chevalier occulte, Escroc arcanique) | tiers, arrondi inférieur | idem |
| Artificier | moitié, arrondi supérieur | (classe absente de 2024) |

Exemple testé : Paladin 5 (2024) + Magicien 3 (2014) = niveau d'incantateur 3 + 3 = 6 → 4/3/3 emplacements ; la même chose en Paladin 2014 donne 2 + 3 = 5 → 4/3/2. Les prérequis de multiclassage sont identiques dans les deux éditions (13 dans les caractéristiques de la classe d'origine et de la nouvelle classe).

`validate_classes()` signale deux incohérences : une classe hors du mode actif, et **la même classe dans deux éditions** (interdit).

## 2. Règles de la table

| Clé | Règle | Défaut 2014 | Défaut 2024 / libre | Effet dans l'app |
|---|---|---|---|---|
| `potion_action_bonus` | Potion en action bonus (soi-même ; un allié reste une action) | non | oui | tuile « Boire une potion (Action bonus) » de l'onglet Combat |
| `maitrises_armes_2014` | Bottes d'arme 2024 sur l'arsenal 2014, **si l'arme est maîtrisée** | non | oui | botte affichée sur l'arme et action « Botte d'arme » |
| `inspiration_heroique` | Inspiration héroïque 2024 (relance d'un dé) au lieu de l'avantage 2014 | non | oui | tuiles « Recevoir / Utiliser l'inspiration », texte selon la règle |
| `actions_arme_bg3` | Actions d'arme façon Baldur's Gate 3 (règle maison) | oui | oui | actions spéciales de chaque arme |

**Anciennes sauvegardes** : elles restent en mode 2014 et gardent exactement le comportement des versions précédentes (potion en action bonus, bottes et actions d'arme actives). Un **nouveau** personnage 2014 n'a plus la potion en action bonus ni les bottes, conformément à l'audit `AUDIT_CONFORMITE_5E2014.md` (§2.1). Le registre `HR.RULES` accueille de nouvelles règles sans autre changement : la fenêtre se construit à partir de lui.

**Fenêtre** : Options → *Règles de la table…* : choix du mode, alertes d'incohérence des classes, cases à cocher par catégorie avec description et origine, bouton « Valeurs par défaut du mode », case « Utiliser ces réglages pour les nouveaux personnages ».

## 3. Données reçues : constats

- 18 manuels, 2014 et 2024 séparés par `edition`, identifiants stables (`classe-fighter-2024-phb24`) : excellente base pour relier les éléments.
- **Champs en texte libre** pour les bases de classe (compétences : « Choisissez-en 2 : … », armures, armes, jets de sauvegarde, équipement) : il faut un analyseur pour les transformer en listes que le moteur sait utiliser.
- **Aptitudes de classe 2014 moins détaillées que les données actuelles** (aptitudes listées par classe ; l'app compte aussi chaque amélioration et les options de Tasha) :

| Classe 2014 | Nouvelles données | App actuelle | Sous-classes nouvelles | Sous-classes officielles de l'app |
|---|---|---|---|---|
| Clerc | 6 | 22 | 14 | 14 |
| Ensorceleur | 6 | 15 | 9 | 7 |
| Magicien | 6 | 11 | 14 | 12 |
| Guerrier | 7 | 16 | 10 | 8 |
| Occultiste | 7 | 15 | 9 | 10 |
| Druide | 8 | 17 | 7 | 7 |
| Barde | 11 | 27 | 9 | 7 |
| Rôdeur | 13 | 28 | 8 | 7 |
| Roublard | 13 | 20 | 11 | 9 |
| Barbare | 14 | 20 | 10 | 11 |
| Paladin | 14 | 21 | 10 | 7 |
| Moine | 22 | 27 | 11 | 8 |
| Artificier (ERLW / TCE) | 20 / 13 | 17 | 7 | 4 |

  En revanche, les **sous-classes 2014** des nouvelles données sont souvent plus nombreuses : elles comblent une partie des manques relevés par l'audit (§4).
- Les 2024 ont 4 sous-classes par classe (Manuel des joueurs 2024) ; pas d'Artificier 2024.

## 4. Étape 2

### 4.1 Fait : fusion des données et filtrage des choix

`core/edition_import.py` fusionne `data/editions/` dans la base **à chaque chargement** (aucun fichier de `data/` n'est réécrit). Bilan affiché par `stats_text()` :

| Type | Ajouté | Règle |
|---|---|---|
| Sorts | 28 sorts 2014 manquants (*Grêle d'épines*, *Purification de nourriture et d'eau*, sorts de Wildemount, d'Acquisitions Inc., de Strixhaven…) + 391 sorts 2024 | 7 sorts 2014 ne sont que d'autres traductions de sorts déjà présents (*Piques argentées* = *Barbes argentées*…) : écartés |
| Dons | dons 2014 manquants (dons raciaux de Xanathar, Chef inspirant, Sentinelle, Tueur de mages…) + 75 dons 2024 | les dons de Theros (piété, bénédictions), les faveurs épiques et les dons sombres sont écartés ; **13 dons de l'app au texte faux** reçoivent le texte officiel, avec leur nom d'app (audit §8.3) |
| Historiques | 38 historiques 2014 officiels manquants (SCAG, variantes du PHB, Ravenloft…) + 16 historiques 2024 | 2024 : `caracteristiques_2024` et `don_origine` sont enregistrés |
| Sous-classes | les **14 sous-classes 2014 officielles manquantes** de l'audit (Parjure, Couronne, Chevalier de l'Écho, Banneret, Graviturgie, Longue Mort, Dragon ascendant, L'Immortel, Le Mort-vivant, Batailleur, Voie du géant, Esprits, Sorcellerie lunaire, Gardien de drake) | les autres sous-classes des nouvelles données sont des traductions de sous-classes déjà présentes |
| Espèces | 10 espèces 2024 (Aasimar, Drakéide, Nain, Elfe, Gnome, Goliath, Halfelin, Humain, Orc, Tieffelin) | bonus « +2/+1 ou +1/+1/+1 » au choix en attendant que l'historique 2024 les fournisse ; vitesse lue dans les données (Goliath 10,5 m) |
| Armes | Filet | armes et armures communes aux deux éditions |

**Noms** : un élément 2024 dont le nom existe déjà en 2014 prend le suffixe « (2024) » (*Boule de feu (2024)*, *Elfe (2024)*), car le moteur identifie tout par le nom.

**Filtrage** (`Engine.race_options()`, `background_options()`, `feat_options()`, `available_spells()`) : espèces et historiques (onglet Race), catalogue de dons (onglet Progression), dons de « Niveau supérieur », bibliothèque de sorts. L'espèce et l'historique actuels du personnage restent toujours visibles. En mode libre, une info-bulle discrète indique l'édition et la source (`Engine.edition_tips()`).

### 4.2 Fait : classes et sous-classes 2024 (une édition par fiche)

Décision : **l'édition se choisit à la création du personnage** (fenêtre « Édition 2014 / Édition 2024 » avant l'assistant) et **toute la fiche reste dans cette édition**. Le mode libre existe toujours dans le moteur, mais il n'est plus proposé dans l'interface.

- `edition_import.build_classes_2024()` construit les 12 classes 2024 au format du moteur : dé de vie, jets de sauvegarde, compétences au choix, armures, armes (Moine et Roublard : seulement les armes de guerre Légère / Finesse), aptitudes **niveau par niveau** d'après la table (améliorations répétées, « Faveur épique » au niveau 19 traitée comme une amélioration ou un don), 4 sous-classes par classe, table de progression.
- `EditionView` : une fiche 2024 voit cette base (`Engine.db` est une propriété qui choisit la vue selon l'édition). Tout le code qui lit `self.db.classes`, `subclasses()`, `start_info()` obtient donc les classes 2024 sans autre changement.
- Règles 2024 lues dans la table : **sorts préparés et sorts mineurs** pour tous les incantateurs (`casters()`), demi-incantateurs dès le niveau 1, **sous-classe au niveau 3** pour toutes les classes (`Engine.subclass_level()`), **dé d'arts martiaux** d6 → d12 (`Engine.martial_arts_die()`), **ressources** affichées (rages, Second souffle, points de concentration, Conduit divin, Formes sauvages, bottes maîtrisées…).
- PV au niveau 1 : maximum du dé de vie. Pas d'Artificier en 2024.

### 4.3 Reste à faire

1. **Compteurs à sphères 2024** (Conduit divin 2/3/4, Formes sauvages 2/3/4, Second souffle 2→4, Ennemi juré…) : les sphères suivent encore les nombres de 2014 ; la table est affichée dans les ressources.
2. **Historique 2024 complet** : augmentations de caractéristiques limitées à ses trois caractéristiques et don d'origine (aujourd'hui : bonus au choix sur l'espèce).
3. **Styles de combat 2024** (dons de la catégorie « Style de combat ») et **nombre de bottes** maîtrisées à choisir ; **Armes de l'Occultiste 2024** (manifestations dès le niveau 1, Arcanum).
4. **Mécaniques nommées** : certaines aptitudes 2024 portent un nouveau nom (« Châtiment de paladin », « Frappe malicieuse », « Points de concentration ») ; les tuiles d'action spécialisées de l'onglet Combat les reconnaissent encore mal.
5. **Version web** : choix de l'édition à la création et fenêtre « Règles de la table ».

## 5. Décisions prises

1. **Données 2014** : on garde les données actuelles, les plus complètes (classes 2014 et leurs aptitudes). Les nouvelles données ne servent qu'à **compléter** : sous-classes, dons, historiques, sorts et objets 2014 manquants, et tout le contenu 2024.
2. **Contenu « communauté »** : les 27 sous-classes restent proposées **dans tous les modes**, avec une mention discrète « non officielle » (info-bulle des menus de sous-classe, info-bulle de « Niveau supérieur », source affichée dans la fiche pédagogique de classe). Fonctions : `Database.is_unofficial()`, `Database.subclass_tips()`.
3. **Règles de la table** : seule l'inspiration héroïque est retenue pour la troisième règle (pas de règle de « jets de sauvegarde universels »).
4. **Une édition par fiche** : l'édition se choisit à la création ; le mode libre est masqué.
5. **Versions** : la v51 est conservée telle quelle sur la branche `version-51` (pull request #3 vers `main`) ; la v52 vit sur sa propre branche (pull request #2, construite au-dessus de `version-51`). Chaque branche a son propre exécutable Windows (CI à chaque envoi).

Point encore à vérifier dans le livre : le texte exact du Manuel 2024 sur l'administration d'une potion à un allié (la règle de la table suit ta définition : soi-même = action bonus, allié = action).
