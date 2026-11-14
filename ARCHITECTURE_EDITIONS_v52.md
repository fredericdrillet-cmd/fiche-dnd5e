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

## 4. Étape 2 — reste à faire

1. **Classes 2024 dans le moteur.** Le moteur identifie une classe par son nom (« Paladin ») dans les tables de sorts, ressources, actions de classe et montée de niveau. Pour faire coexister « Paladin 2014 » et « Paladin 2024 », chaque appel doit passer par l'édition de l'entrée de classe. Gros chantier, à faire classe par classe, avec tests (tables 2024 : sorts préparés pour tous les incantateurs, maîtrises d'armes, Second souffle, Rage, etc.).
2. **Convertisseur `tools/import_editions.py`** : transforme les fiches de `data/editions/` (sous-classes, dons, historiques, races, sorts, armes, armures) dans les formats actuels de l'app, avec le champ `edition` ; l'app peut alors les filtrer dans ses sélecteurs.
3. **Sélecteurs** (race, classe, sous-classe, don, historique, sort, équipement) : filtrage par `filter_items(…, mode)` et badge `label(…)` en mode libre ; dans « Niveau supérieur », choix de l'édition d'une nouvelle classe en mode libre.
4. **Historiques 2024** : ils donnent les augmentations de caractéristiques et un don d'origine (les races 2024 n'en donnent plus) ; l'assistant de création doit l'appliquer en mode 2024.
5. **Version web** : fenêtre « Règles de la table » et opérations `set_edition_mode` / `set_house_rule`.

## 5. Décisions prises

1. **Données 2014** : on garde les données actuelles, les plus complètes (classes 2014 et leurs aptitudes). Les nouvelles données ne servent qu'à **compléter** : sous-classes, dons, historiques, sorts et objets 2014 manquants, et tout le contenu 2024.
2. **Contenu « communauté »** : les 27 sous-classes restent proposées **dans tous les modes**, avec une mention discrète « non officielle » (info-bulle des menus de sous-classe, info-bulle de « Niveau supérieur », source affichée dans la fiche pédagogique de classe). Fonctions : `Database.is_unofficial()`, `Database.subclass_tips()`.
3. **Règles de la table** : seule l'inspiration héroïque est retenue pour la troisième règle (pas de règle de « jets de sauvegarde universels »).
4. **Versions** : la v51 est conservée telle quelle sur la branche `version-51` (pull request #3 vers `main`) ; la v52 vit sur sa propre branche (pull request #2, construite au-dessus de `version-51`). Chaque branche a son propre exécutable Windows (CI à chaque envoi).

Point encore à vérifier dans le livre : le texte exact du Manuel 2024 sur l'administration d'une potion à un allié (la règle de la table suit ta définition : soi-même = action bonus, allié = action).
