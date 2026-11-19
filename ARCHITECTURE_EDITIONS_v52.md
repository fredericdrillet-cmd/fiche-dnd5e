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

### 4.3 Fait : compteurs et historique 2024

- **Compteurs à sphères** d'une fiche 2024 (`Engine._trackers_2024`) : rages, points de concentration (ex-ki), Formes sauvages, Second souffle, Conduit divin (Clerc et Paladin) et dé d'inspiration bardique lus dans les tables ; Sens divin retiré (c'est une option de Conduit divin en 2024) ; nouveau compteur « Ennemi juré (Marque du chasseur) » du Rôdeur.
- **Historique 2024** : les augmentations de caractéristiques (+2/+1 ou +1/+1/+1) se font **parmi les trois caractéristiques de l'historique** (`background_abilities()`, `race_rule()["choix"]`), et le **don d'origine** est accordé d'office (`origin_feat()`, compté dans `chosen_feats()`).
- **Passage en 2024** (`set_edition_mode`) : l'espèce et l'historique passent à leur équivalent (« Humain » → « Humain (2024) », « Acolyte » → « Acolyte (2024) »), et inversement.

### 4.4 Fait : styles de combat et bottes d'arme 2024

- **Styles de combat** : sur une fiche 2024, le sélecteur de l'onglet Combat propose les 10 dons « Style de combat » 2024 (`EditionView.styles_by_class`), plus *Combattant béni* (Paladin) et *Combattant druidique* (Rôdeur). Les styles de même nom gardent leurs effets (Défense, Archerie, Duel, Armes à deux mains…). *Technique supérieure* (Tasha) reste réservée au 2014.
- **Bottes d'arme** : `mastery_count()` (table : Guerrier 3 → 6, Barbare 2 → 4 ; 2 pour Paladin, Rôdeur, Roublard ; 0 sans l'aptitude), `mastery_weapons()` (choix du joueur, ou armes équipées par défaut), `set_mastery()`, `botte_allowed()`. Encart « Bottes d'arme » et fenêtre de choix (`ui/mastery_dialog.py`) dans l'onglet Combat. Fiche 2014 : toutes les armes maîtrisées si la règle de la table est active (décision Q4).

### 4.5 Fait : Occultiste et Métamagie 2024

- **Manifestations 2024** (`EditionView.manifestations`, `build_manifestations_2024`) : les 28 manifestations du Manuel 2024, prérequis analysés (niveau, pacte, autre manifestation, tour de magie) ; nombre lu dans la table (1 au niveau 1 → 10 au niveau 20).
- **Pacte** : en 2024, Pacte de la lame / de la chaîne / du grimoire sont des manifestations ; `ch.pacte` est déduit de la manifestation choisie, et il n'y a plus de choix séparé au niveau 3 (`pact_available()`, `pact_options()`, choix manquants).
- **Métamagie 2024** (`metamagic_table()`, `metamagic_known_count()`) : les 10 options 2024 avec leur coût, 2 options au niveau 2, 4 au niveau 10, 6 au niveau 17.

### 4.6 Fait : actions de classe 2024 (onglet Combat)

`ClassActionsMixin._actions_2024()` transforme les tuiles d'une fiche 2024 (décision Q7) :
- **Châtiment divin** : sort en action bonus juste après avoir touché, une fois par tour, + une tuile « Châtiment divin (gratuit) » (1 par repos long, compteur `chatiment_gratuit`) ; *Sens divin* retiré.
- **Second souffle** (utilisations de la table, Déplacement tactique au niveau 5) ; **Fougue** (sauf l'action Magie) ; **Rage** (durée et prolongation 2024).
- **Points de concentration** : Déluge de coups (3 frappes au niveau 10), Défense patiente et Pas du vent en version **gratuite** et à 1 point, Coup étourdissant (effet en cas de réussite), frappe à mains nues en action bonus sans condition, *Parade de projectiles* → **Déviation d'assaut**.
- **Frappe malicieuse** (Roublard 5 : Poison, Croc-en-jambe, Repli ; niveau 14 : Hébétement, Assommer, Aveugler ; 2 effets au niveau 11), avec le DD.
- Les autres aptitudes gardent leur mécanisme et leur nom actuels.

### 4.7 Fait : version web

- **Serveur** (`web/service.py`) : opérations `set_edition` (2014 / 2024 ; le mode libre est refusé), `set_house_rule`, `set_masteries` ; la fiche renvoie `edition` (mode, classes de l'édition, règles de la table avec leur état, bottes d'arme) ; le catalogue indique l'édition des espèces, historiques, dons et sorts.
- **Interface** (`web/static/app.js`) : *Nouveau personnage* demande « Édition 2014 / 2024 » (aussi au premier lancement) ; listes d'espèces, d'historiques, de classes, de dons et de sorts (mode MJ) filtrées selon l'édition de la fiche ; menu ☰ → **⚖ Règles de la table** : changer d'édition, cocher / décocher les 4 règles, choisir les bottes d'arme.

### 4.8 Fait : aptitudes 2024 calculées (`core/features_2024.py`)

- **Sorcellerie innée** (Ensorceleur 1) : compteur de 2 utilisations par repos long et tuile en action bonus qui active l'effet « Sorcellerie innée » (1 minute, bascule) ; tant qu'il dure, DD des sorts d'ensorceleur +1 (`casters()`) et avantage aux attaques de sorts d'ensorceleur (`spell_attack_spec`). Niveau 7 : seconde tuile payée 2 points de sorcellerie (*Sorcellerie incarnée*).
- **Ordre divin** (Clerc 1 : Protecteur / Thaumaturge) et **Ordre primitif** (Druide 1 : Gardien / Magicien) : ensembles de choix `ordre_divin` / `ordre_primitif` dans `option_sets()` (encart des options de l'onglet « En partie », choix manquant tant qu'il n'est pas fait, web compris). Protecteur / Gardien : maîtrises d'armures (lourdes / intermédiaires) et d'armes de guerre (`proficiency_sources`). Thaumaturge / Magicien : un tour de magie de plus et modificateur de Sagesse (minimum +1) aux tests d'Arcanes et de Religion / de Nature (`modifier_sources`).
- **Prérequis des dons 2024** (`feat_status_2024`) : « Niveau 4+ », « Force ou Dextérité 13+ », formations aux armures et au bouclier, aptitude Style de combat, Incantation / Magie des pactes. Les **Faveurs épiques** (« Niveau 19+ ») ne sont plus proposées comme valides avant le niveau 19. Les prérequis 2014 gardent leur ancienne lecture.

### 4.9 Fait : effets appliqués automatiquement (dons et aptitudes de classe)

Principe : dès qu'un don est choisi ou qu'un niveau débloque une aptitude, tout ce que la fiche sait chiffrer est appliqué ; les choix du joueur passent par `option_sets()` (choix manquants comptés).

- **`core/feat_effects.py`** (`FeatEffectsMixin`, registre `REG` par nom de base et édition — « Robuste (2024) » → « robuste ») :
  - passifs : initiative (Vigilant), PV par niveau (Robuste), vitesse (Mobile, Faveur de vitesse), PV max (Faveur de vigueur), Dex max 3 des armures intermédiaires, dé d4 à mains nues (Bagarreur de tavernes), + bonus de maîtrise aux dégâts des armes lourdes (Cogneur lourd), +1 botte d'arme (Maître d'armes), avantage de concentration (Mage de guerre), réaction (Duelliste défensif), vision véritable / aveugle ;
  - maîtrises : armures et armes (Protection…, Formation aux armes de guerre), JS (Résilient / Résistant, caractéristique choisie), compétences et expertise (Doué, Expert, Observateur, Esprit affûté, Faveur de compétence), outils (Doué, Façonneur, Musicien, Chef cuisinier, Empoisonneur — affichés dans l'onglet Équipement) ;
  - **sorts accordés** (`granted_spells`, catégorie « Dons ») : Initié à la magie 2014 / 2024 (liste, caractéristique, 2 tours de magie, 1 sort de niveau 1), Affinité féérique, Faveur des ombres, Émissaire des fées, Adepte des ombres, Télékinésiste, Télépathe, Haute magie drow, Téléportation féerique ; lancer gratuit 1 fois par repos (compteur interne), DD et attaque avec la caractéristique du don ;
  - compteurs et tuiles : points de chance (3 en 2014, bonus de maîtrise en 2024), Faveur du destin (2d4, revient à l'initiative), Faveur de récupération (réserve de 10 d10 ; *Dernier rempart* appliqué tout seul à 0 PV), Performance stimulante (PV temporaires appliqués), Récupération rapide (dé de vie dépensé) ;
  - Faveurs épiques : +1 jusqu'à 30, prérequis niveau 19, résistances au choix ;
  - choix affichés dans l'onglet **Progression** (encart « Choix des dons »).
- **`core/class_auto.py`** (`ClassAutoMixin`, 2014 et 2024 ; les « options Tasha » ne s'appliquent jamais d'office) : maîtrise de tous les JS (Âme diamantée, Survivant discipliné), Esprit fuyant (Sag ; Sag et Cha en 2024), avantage aux JS de Dex (Sens du danger), Nomade (+3 m), Sens bestiaux, Corps et esprit (+4 Dex / Sag, max 25), Champion primitif 2024 (max 25), +1d8 radiants des armes de corps à corps (Châtiment divin amélioré / Frappes radiantes), Frappe divine 2014 (1d8 → 2d8, une fois par tour), Frappes bénies et Fureur élémentaire 2024 (choix : frappe une fois par tour ou Incantation puissante sur les tours de magie), Connaissance primitive (compétence), expertises d'Explorateur habile et d'Érudit, ressources rendues à l'initiative (Inspiration supérieure, Concentration parfaite, Yo perfectionné, Rage persistante) et au repos court (Restauration d'ensorceleur).

### 4.10 Fait : sous-classes 2024, sorts 2024, jet contre la mort

- **Sorts toujours préparés des sous-classes 2024** (domaines, cercles, serments, protecteurs, sorcelleries, Vagabond féerique, Traqueur des ténèbres) : tables lues dans le texte de l'aptitude « Sorts du … » quel que soit leur format (`features_2024.subclass_spells_2024`, table `SPELL_ALIASES_2024` pour les noms traduits autrement) ; Cercle de la Terre 2024 : choix de la terre (aride, polaire, tempérée, tropicale).
- **Sous-classes renommées** : `SUBCLASS_EQUIV_2024` / `sub_norm_of()` (Âme acérée → Lame psychique, Abjurateur → École d'abjuration, Credo de l'Ombre → Voie de l'ombre…) ; les tuiles, compteurs et dés psioniques 2014 s'appliquent aux sous-classes 2024.
- **Passifs de sous-classes** (`class_auto.py`, 2014 et 2024) : critique sur 19-20 / 18-20 (Champion, `RollSpec.crit_min`), avantage à l'initiative (Athlète accompli, Assassinat 2024), + Sagesse à l'initiative (Embuscade effrayante), Vision ombreuse, JS de Sagesse (Esprit de fer / Mental d'acier), résistances (Défenses psychiques, Bouclier mental, Âme radieuse, Résistance fiélonne au choix), Aura de célérité (+3 m), Pirouettes éblouissantes (CA 10 + Dex + Cha), Maîtrises supplémentaires du Collège du savoir (3 compétences), Instruments de miséricorde, Disciple de la vie (+2 + niveau du sort aux soins), Fureur divine du Zélote pendant la rage.
- **Sorts 2024** : soins, jet de sauvegarde, demi-dégâts, surclassement lus dans le texte 2024 (`rules.parse_spell_mechanics_2024`), complétés par les règles auditées du sort 2014 équivalent (projectiles, modificateur…).
- **Jet contre la mort** (onglet « En partie », bouton 🎲 à 0 PV) : 10+ réussite, 1 = deux échecs, 20 = 1 PV ; avantage avec Gaillard ; dégâts reçus à 0 PV = un échec ; mort instantanée si les dégâts restants atteignent le maximum de PV.

### 4.11 Fait : sous-classes 2024 sans équivalent 2014 (`core/subclass_2024.py`)

- **Tuiles** (champ `ed: 2024`, reconnues par le nom 2024 de la sous-classe) : Force vivifiante, Branches de l'Arbre, Voyage au gré de l'arbre (Arbre-Monde) ; Déplacement exaltant, Pirouettes coordonnées (Danse) ; Aval de la terre (2d6 → 4d6), Sanctuaire de dame Nature (Terre) ; Courroux des mers (effet actif) ; Lien élémentaire, Décharge élémentaire (Éléments) ; Halo de lumière (Lumière) ; Surcharge magique (Évocateur).
- **Effets automatiques** : PV temporaires de la Vitalité de l'arbre à l'entrée en rage ; choix du Cœur sauvage (Rage du prédateur, Aspect de faune, Puissance de la faune) avec la résistance de l'Ours en rage et la vision de la Chouette ; Protégé de dame Nature (résistance selon la terre choisie) ; Enfant des tempêtes (résistances pendant le Courroux des mers seulement) ; Avatar de bataille ; dé d'inspiration aux frappes à mains nues (Danse) ; outils de l'Assassin et Frappes surprises (+ niveau de roublard, proposé aux dégâts) ; Champion : Inspiration héroïque et Ralliement héroïque au début du tour (nouveau round), jets contre la mort avec avantage et 18-20 comptés comme 20 ; Évocation améliorée.
- **Conduit divin 2024** : les options sont les aptitudes de la sous-classe qui dépensent « une utilisation de votre Conduit divin » (Préservation de la vie, Radiance de l'aube, Frappe guidée, Arme sacrée, Vœu d'hostilité…).
- Correctif : « tant qu'elle est active » est reconnu comme une condition, donc pas d'effet permanent (seul changement constaté sur toutes les sous-classes : Enfant des tempêtes).

### 4.12 Fait : règles de jeu appliquées au lancer et aux PV (2014 et 2024)

- **Type de dégâts** dans la saisie rapide des PV (onglet « En partie » : liste des types + case « magique ») : `damage_after_defenses()` applique les réductions (Maître des armures lourdes : 2014 -3 contre les attaques non magiques, 2024 - bonus de maîtrise), puis immunité, résistance (moitié, arrondi inférieur) ou vulnérabilité (double). Sans type, rien ne change.
- **Planchers des lancers** (`RollSpec.d20_min` / `total_min`, affichés « Talent fiable : d20 3 → 10 ») : Talent fiable (Roublard 11 en 2014, 7 en 2024, compétences maîtrisées) ; Puissance indomptable (Barbare 18 : tests de Force, et JS de Force en 2024).
- **JS de Dextérité** : rappel d'Évasion / Dérobade / Esquive totale / Esquive cavalière (réussite = aucun dégât, échec = moitié).
- **Faveur de mémoire des sorts** : 1d4 lancé à chaque emplacement de niveau 1 à 4 dépensé (`cast_spell`) ; emplacement rendu si le dé égale le niveau.
- **Immunités aux états** (`condition_immunities`, `effect_blocked`) : Aura de dévotion (charmé), Aura de courage (effrayé), Pureté du corps 2014 (empoisonné, malade), Protégé de dame Nature (empoisonné ; et malade en 2014), Rage aveugle en rage (charmé et effrayé, retirés à l'entrée en rage). L'état ne peut pas être ajouté ; l'interface dit pourquoi.
- **Textes 2024 des sous-classes renommées** (`TILE_FEATURE_2024`) : sur une fiche 2024, une tuile 2014 prend le nom, le texte et le niveau de l'aptitude 2024 équivalente (Présence féerique → Foulée des fées, Moi illusoire → Double illusoire…) ; Frénésie 2024 (dés de dégâts en plus avec Attaque téméraire) remplace l'attaque en action bonus de 2014.

### 4.13 Reste à faire

- Effets sur d'autres créatures ou sur le décor (téléportation, illusions, déplacements des alliés) : la tuile rappelle l'effet, il n'y a rien à calculer sur la fiche.

## 5. Décisions prises

1. **Données 2014** : on garde les données actuelles, les plus complètes (classes 2014 et leurs aptitudes). Les nouvelles données ne servent qu'à **compléter** : sous-classes, dons, historiques, sorts et objets 2014 manquants, et tout le contenu 2024.
2. **Contenu « communauté »** : les 27 sous-classes restent proposées **dans tous les modes**, avec une mention discrète « non officielle » (info-bulle des menus de sous-classe, info-bulle de « Niveau supérieur », source affichée dans la fiche pédagogique de classe). Fonctions : `Database.is_unofficial()`, `Database.subclass_tips()`.
3. **Règles de la table** : seule l'inspiration héroïque est retenue pour la troisième règle (pas de règle de « jets de sauvegarde universels »).
4. **Une édition par fiche** : l'édition se choisit à la création ; le mode libre est masqué.
5. **Versions** : la v51 est conservée telle quelle sur la branche `version-51` (pull request #3 vers `main`) ; la v52 vit sur sa propre branche (pull request #2, construite au-dessus de `version-51`). Chaque branche a son propre exécutable Windows (CI à chaque envoi).

Point encore à vérifier dans le livre : le texte exact du Manuel 2024 sur l'administration d'une potion à un allié (la règle de la table suit ta définition : soi-même = action bonus, allié = action).
