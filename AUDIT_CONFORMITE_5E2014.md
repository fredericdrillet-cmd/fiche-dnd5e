# Audit de conformité — règles de D&D 5e **édition 2014**

> **Objet** : comparer, règle par règle, ce que l'application Python (`fiche-dnd5e`, version 51) implémente avec les règles officielles de **D&D 5e 2014**. Les règles de l'édition **2024** ne servent pas de référence : tout ce qui en vient est signalé comme « en trop ».
> **Périmètre** : classes, sous-classes, historiques, espèces, compétences, langues, outils, dons, armes, armures, équipement de départ, magie (sorts, manifestations occultes, styles de combat, manœuvres, métamagie), tables de règles (`core/rules.py`) et bestiaire de la Forme sauvage.
> **Nature du document** : constats uniquement. **Aucune donnée ni aucun code n'a été modifié.** Les corrections sont listées au §13 pour que tu décides lesquelles appliquer.
> **Point de départ** : le fichier `docs/ECARTS-CLASSEUR.md` du dépôt `axeli7o/dndcharsheet`, recoupé au §12. Ce fichier décrit une *autre* application (TypeScript, fidèle à un classeur Excel) ; ses lignes servent ici de liste de points sensibles, pas de vérité.

---

## 0. Lecture rapide

### Bilan par domaine

| Domaine | Verdict global | Conformes | Écarts | Manquants (officiels 2014) | En trop (hors 2014) |
|---|---|---|---|---|---|
| **Classes** (13) | 🟢 très bon | 13 / 13 présentes, dés de vie, PV, jets de sauvegarde, armures | 5 listes de compétences polluées, 1 liste d'armes du druide | aucune | — |
| **Aptitudes de classe** niv. 1-20 | 🟢 très bon | noms et niveaux conformes pour les 13 classes | — | — | — |
| **Tables de règles** (`core/rules.py`) | 🟢 excellent | maîtrise, emplacements, pacte, sorts connus, mineurs, invocations, rage, ki, Forme sauvage, multiclassage | omissions mineures au multiclassage (outils, compétences) | — | — |
| **Sous-classes** (138 dans l'app) | 🟡 bon | toutes les sous-classes des PHB/XGE/TCE présentes sauf celles du §4 | totems, nom d'une source | **≈ 15** (Banneret, Chevalier-écho, Graviturgie, Longue Mort, Âme cobalt, Dragon ascendant, Parjure, Couronne, Batailleur, Esprits, Immortel…) | **27** « Création de la communauté » |
| **Historiques** (81) | 🔴 faible | 12 / 13 du PHB conformes | 8 écarts | ≥ 13 (9 du SCAG, 4 variantes du PHB) | **61** hors catalogue |
| **Espèces** (70) | 🟡 moyen | 13 PHB, 12 suppléments 2014 | 42 en version 2021-22 (MotM, Spelljammer, Ravenloft…) | **Demi-orque** (PHB), Aasimar fléau, Changeforme… | 3 non officielles |
| **Compétences / langues / outils** | 🟢 bon | 18 / 18 compétences, langues complètes | noms de langues | véhicules, jeux, instruments séparés | caractéristique par outil (2024) |
| **Dons** (86) | 🔴 faible | 36 | 16 | **14 du PHB**, 11 raciaux de XGE | **34** non rattachés à un don officiel |
| **Armes / armures** | 🟡 bon | 33 / 38 armes et 13 / 13 armures du PHB conformes | 5 armes avec une valeur fausse | Filet | **botte d'arme 2024** ; 4 armures « communauté » |
| **Équipement de départ** | 🟢 excellent | or et paquetages des 13 classes conformes | — | — | — |
| **Sorts** | 🟢 très bon | ≈ 488 sorts, 0 à 9 ; niveaux, écoles et listes de classe conformes sur l'échantillon | 2 listes de classe | 2 sorts du PHB (*Grêle d'épines*, *Purification de nourriture et d'eau*) + sorts de Wildemount | — |
| **Manifestations occultes** | 🟢 parfait | 54 / 54 (PHB 32, XGE 14, TCE 8), prérequis exacts | — | — | — |
| **Styles de combat, manœuvres, métamagie** | 🟢 parfait | 11 / 7 / 7 styles, 23 manœuvres, 10 options | précisions mineures | — | — |
| **Bestiaire** (Forme sauvage) | 🟢 parfait | CA, PV, vitesses conformes à l'échantillon | — | — | — |

Légende : 🟢 conforme · 🟡 acceptable avec réserves · 🔴 à reprendre. Niveaux de confiance des constats : 🟢 certain · 🟡 probable · 🔴 à vérifier dans le livre (voir §1).

### Les dix constats les plus importants

1. 🔴 **La « botte d'arme » est une règle de 2024.** `data/Armes.json` donne à chacune des 38 armes une botte (*Sape*, *Ralentissement*, *Renversement*, *Ouverture*…) : c'est la **Maîtrise des armes** du Manuel des joueurs 2024, qui n'existe pas en 2014. Elle apparaît sur la fiche de combat de **tous** les personnages (§2.1).
2. 🔴 **18 « actions d'arme » inspirées de Baldur's Gate 3** (*Lacération*, *Brise-crâne*, *Fauchage*, *Désarmement*…) sont attribuées à toutes les armes, avec DD et recharge. Règle maison, absente de 2014 (§2.2).
3. 🔴 **Demi-orque absent.** Espèce du Manuel des joueurs ; l'« Orc » présent vient de *Monstres du Multivers* (2022) (§6).
4. 🔴 **Historiques : 61 sur 81 n'existent pas dans les livres 2014** (dont des entrées humoristiques : « Idiot du village », « Crapule »…). Neuf des douze historiques du *Guide de l'aventurier pour la Côte des Épées* (SCAG) manquent (§5).
5. 🔴 **Dons : 14 dons du Manuel des joueurs manquent** (*Expert de la charge*, *Sentinelle*, *Tueur de mages*, *Guérisseur*, *Compétent*…) alors que 34 dons non officiels ou mal nommés sont présents, dont des doublons (*Tranchant* / *Acéré*, *Résilient* / *Résistant*) (§8).
6. 🟠 **Compétences de classe polluées** : *Discrétion* figure dans les listes du Barbare, du Guerrier, du Paladin, de l'Ensorceleur et de l'Occultiste, qui n'y ont pas droit (§3.2).
7. 🟠 **Druide** : maîtrise l'*arbalète légère* (non officiel) mais pas la *serpe* (officielle) (§3.3).
8. 🟠 **31 espèces suivent la version 2022** de *Monstres du Multivers* (bonus libres +2/+1, aptitudes « bonus de maîtrise fois par repos long »), pas les versions 2014 de Volo, Mordenkainen ou Éberron (§6).
9. 🟠 **27 sous-classes « Création de la communauté »**, **4 armures** et **3 espèces** non officielles sont mélangées au catalogue officiel (§2.3).
10. 🟢 **Points forts à conserver** : tous les calculs de `core/rules.py`, les 54 manifestations occultes, les 23 manœuvres, les styles de combat, la métamagie, les paquetages de départ, la majorité des textes de sous-classe et le bestiaire sont **fidèles à 2014**. Sur plusieurs points où `ECARTS-CLASSEUR.md` constate un écart de l'autre application, **ton application est correcte** (§12).

---

## 1. Méthode, sources et limites

**Référentiel « 2014 ».** Manuel des joueurs (PHB), Guide du maître (DMG), Manuel des monstres (MM) et les suppléments publiés sous les règles de l'édition 2014 : Guide de Xanathar (XGE), Chaudron de Tasha (TCE), Guide de l'aventurier pour la Côte des Épées (SCAG), Guide de Volo, Mordenkainen (MToF), Elemental Evil (EEPC), Éberron, Ravnica, Theros, Ravenloft, Wildemount, Fizban, etc. Les contenus de *Monstres du Multivers* (MotM, 2022) et de *Spelljammer* (2022) restent compatibles avec cette édition mais **modifient** les espèces (bonus libres, aptitudes liées au bonus de maîtrise) : ils sont étiquetés 🟠 plutôt que rejetés. Tout ce qui vient du Manuel des joueurs 2024 est « en trop ».

**Ce qui a été comparé.** Les valeurs *effectives* de l'application, obtenues en exécutant `Database` et `Engine` (compétences de classe fusionnées avec `SKILL_FIXES`, tables de `core/rules.py` appelées sur tous les niveaux), plus les JSON de `data/` et des extraits de texte. Les résultats ne reposent donc pas seulement sur la lecture des fichiers.

**Sources de vérité.** Les règles du Manuel des joueurs et des suppléments, telles que je les connais. Le site de référence AideDD n'était **pas joignable** depuis cette session (domaine hors de la liste autorisée), donc aucune vérification en ligne n'a été faite. D'où trois niveaux de confiance :

| Niveau | Sens |
|---|---|
| 🟢 | Règle certaine (Manuel des joueurs, tables connues) |
| 🟡 | Probable, à confirmer rapidement |
| 🔴 | Je ne peux pas trancher sans le livre (surtout les suppléments récents : Fizban, Strixhaven, Wildemount, Planescape…) |

**Non audité en détail** (à signaler pour être honnête) : la rédaction de chaque aptitude de classe (seuls les noms, niveaux et les textes cités dans `ECARTS-CLASSEUR.md` ont été lus), les ≈ 600 objets magiques (`objets_magiques.json`), les 102 invocations et familiers (`Familiers_Invocations.json`), `Equipement.json` hors paquetages, la description de chacun des 488 sorts.

**Rapport avec l'audit existant.** `AUDIT_REGLES.md` (1023 lignes, généré par `tools/audit_regles.py`) couvre les classes et les espèces ; il annonce 0 écart majeur restant. Le présent audit le **complète** : il couvre ce qu'il ignore (historiques, dons, armes, armures, sorts, tables de règles, contenu hors 2014) et relève des écarts qui subsistent *malgré* lui (§3.2, §3.3, §6).

---

## 2. Contenu hors règles 2014 (« en trop »)

### 2.1 La botte d'arme (Maîtrise des armes 2024) 🟢

- **Données** : `data/Armes.json`, champs `botte_arme` et `description_botte` sur les 38 armes. Valeurs : Ouverture (8), Ralentissement (7), Sape (6), Renversement (5), Coup double (4), Poussée (4), Écorchure (2), Enchaînement (2).
- **Code** : `core/data_loader.py:314-315` et `:620-621` (la botte est ajoutée à la description de l'arme), `core/engine.py:1393`, `core/weapon_actions.py:21` (`SRC_BOTTE = "PHB 2024 (botte)"`, l'application l'écrit elle-même), `ui/combat_tab.py:1811`.
- **Règle 2014** : **aucune** propriété de maîtrise d'arme. Les propriétés 2014 sont Allonge, Chargement, Deux mains, Finesse, Légère, Lourde, Lancer, Munitions, Polyvalente, Spéciale.
- **Effet** : toutes les armes affichent une botte et créent des actions passives (« Botte d'arme ») dans l'onglet Combat, quelle que soit la classe ; en 2024 seuls certains personnages (Barbare, Guerrier, Paladin, Rôdeur, Roublard) y ont accès et en choisissent un nombre limité.

### 2.2 Actions d'arme « façon Baldur's Gate 3 » 🟢

`core/weapon_actions.py` ajoute à chaque arme 1 à 3 actions spéciales (18 au catalogue, source « Inspiré de Baldur's Gate 3, adapté 5e ») : *Frappe du pommeau*, *Lacération*, *Fauchage*, *Perçage*, *Préparation*, *Brise-crâne*, *Frappe affaiblissante*, *Moulinet de taille*, *Charge*, *Tir handicapant*, *Tir mobile*, *Tir perforant*, *Ténacité*, *Désarmement*, *Briseur de dos*, *Arrêt-cœur*, *Moulinet*, *Coup cinglant*. Elles ont un DD (8 + maîtrise + modificateur d'attaque) et une recharge (repos court).
**Règle 2014** : aucune. Seules deux actions du catalogue sont officielles : *Lutte* (PHB) et *Bousculer* (DMG, action optionnelle).

### 2.3 Contenu « Création de la communauté » 🟢

| Type | Nombre | Éléments |
|---|---|---|
| Sous-classes | **27** | Barbare : Météore, Colosse des glaces · Barde : Commandants, Discorde · Clerc : Sang · Druide : Mutation, Sangsue · Ensorceleur : Lignée du sang, Magie cosmique · Guerrier : Chevalier de sang, Pancratiaste · Magicien : Magicien du sang, Liaison élémentaire, Gravure runique · Moine : Voie du sang, Voie de la tempête · Occultiste : Moissonneur, Protecteur astral · Paladin : Serment du sang, Serment des cendres · Rôdeur : Traqueur de sang, Artisan des pièges · Roublard : Lame d'ombre, Pistoléro · Artificier : Automaturge, Cartomancien, Horloger |
| Armures | **4** | Cuir de l'Ombre, Cuirasse renforcée de drakéide, Harnois en adamantite noir, Bouclier à pointes |
| Espèces | **3** | Kitsune et Myconide éveillé (« Favori de la communauté ») ; Conil (voir §6, c'est en réalité l'Harengon officiel) |

Rien de tout cela n'existe dans les livres 2014 (voir §14 pour savoir ce qui existe en ligne) ; un personnage « officiel 2014 » peut pourtant le choisir. **À distinguer** : *Domaine de l'Arcane* (Clerc) est **officiel** (SCAG) mais son nom porte le suffixe « (Communauté) » à tort.

### 2.4 Vocabulaire et mécaniques de 2024 🟡

- Le mot **« espèce »** (clé `especes` de `Races.json`, README, interface) est le vocabulaire 2024 ; le Manuel des joueurs 2014 parle de **race**. Cosmétique.
- `Outils.json` attribue une **caractéristique à chaque outil** (Matériel d'alchimiste → Intelligence, etc.). C'est une règle de 2024 ; en 2014 le MD choisit la caractéristique du test.

### 2.5 Règles de 2022 mêlées aux espèces 🟠

31 espèces suivent *Monstres du Multivers* : bonus « +2, +1 (ou +1, +1, +1) » au lieu des bonus fixes, aptitudes à « bonus de maîtrise fois par repos long », sorts d'espèce « 1 fois par repos long » au lieu des versions 2014. C'est de la 5e édition cohérente, mais **pas** celle de Volo / Mordenkainen / Éberron de 2014. Voir §6.

---

## 3. Classes

### 3.1 Base de chaque classe (dé de vie, PV, jets de sauvegarde, maîtrises)

Tout est conforme au Manuel des joueurs (et à Tasha pour l'Artificier) :

| Classe | Dé de vie | PV niv. 1 | Jets de sauvegarde | Armures | Armes | Verdict |
|---|---|---|---|---|---|---|
| Barbare | d12 | 12 | For, Con | légères, intermédiaires, boucliers | courantes, de guerre | ✅ |
| Barde | d8 | 8 | Dex, Cha | légères | courantes, arbalète de poing, épée longue, épée courte, rapière | ✅ |
| Clerc | d8 | 8 | Sag, Cha | légères, intermédiaires, boucliers | courantes | ✅ |
| Druide | d8 | 8 | Int, Sag | légères, intermédiaires, boucliers | liste de 10 armes | ⚠ §3.3 |
| Guerrier | d10 | 10 | For, Con | toutes, boucliers | courantes, de guerre | ✅ |
| Moine | d8 | 8 | For, Dex | aucune | courantes, épée courte | ✅ |
| Paladin | d10 | 10 | Sag, Cha | toutes, boucliers | courantes, de guerre | ✅ |
| Rôdeur | d10 | 10 | For, Dex | légères, intermédiaires, boucliers | courantes, de guerre | ✅ |
| Roublard | d8 | 8 | Dex, Int | légères | courantes, arbalète de poing, épée longue, épée courte, rapière | ✅ |
| Ensorceleur | d6 | 6 | Con, Cha | aucune | dagues, fléchettes, frondes, bâtons, arbalètes légères | ✅ |
| Magicien | d6 | 6 | Int, Sag | aucune | dagues, fléchettes, frondes, bâtons, arbalètes légères | ✅ |
| Occultiste | d8 | 8 | Sag, Cha | légères | courantes | ✅ |
| Artificier | d8 | 8 | Con, Int | légères, intermédiaires, boucliers | courantes | ✅ |

Les 13 classes officielles sont présentes. *Chasseur de sang* (Matthew Mercer) est une classe tierce : son absence est normale.

**Remarques mineures** : `Classes_Depart.json` appelle l'Occultiste « Sorcier » (alias géré par `CLASS_ALIASES`) ; le Clerc dit « armures moyennes » là où les autres classes disent « intermédiaires » (la fonction `armor_proficient` accepte les deux) ; `Compétences.json` écrit « Dressage », `Classes_Depart.json` « Dresseur de bêtes » (alias géré).

### 3.2 Compétences de classe — écarts effectifs 🟢

Obtenus par `Database.start_info()`, c'est-à-dire ce que l'interface propose réellement.

| Classe | Nombre à choisir | Liste officielle (PHB / TCE) | Écart dans l'app |
|---|---|---|---|
| Barbare | 2 ✅ | Dressage, Athlétisme, Intimidation, Nature, Perception, Survie | ⚠ **en trop : Discrétion** |
| Barde | 3 ✅ | Toutes | ✅ |
| Clerc | 2 ✅ | Histoire, Perspicacité, Médecine, Persuasion, Religion | ✅ |
| Druide | 2 ✅ | Arcanes, Dressage, Perspicacité, Médecine, Nature, Perception, Religion, Survie | ✅ |
| Guerrier | 2 ✅ | Acrobaties, Dressage, Athlétisme, Histoire, Perspicacité, Intimidation, Perception, Survie | ⚠ **en trop : Discrétion** |
| Moine | 2 ✅ | Acrobaties, Athlétisme, Histoire, Perspicacité, Religion, Discrétion | ✅ |
| Paladin | 2 ✅ | Athlétisme, Perspicacité, Intimidation, Médecine, Persuasion, Religion | ⚠ **en trop : Discrétion** |
| Rôdeur | 3 ✅ | Dressage, Athlétisme, Perspicacité, Investigation, Nature, Perception, Discrétion, Survie | ✅ |
| Roublard | 4 ✅ | Acrobaties, Athlétisme, Tromperie, Perspicacité, Intimidation, Investigation, Perception, Représentation, Persuasion, Escamotage, Discrétion | ✅ |
| Ensorceleur | 2 ✅ | Arcanes, Tromperie, Perspicacité, Intimidation, Persuasion, Religion | ⚠ **en trop : Discrétion** |
| Magicien | 2 ✅ | Arcanes, Histoire, Perspicacité, Investigation, Médecine, Religion | ✅ |
| Occultiste | 2 ✅ | Arcanes, Tromperie, Histoire, Intimidation, Investigation, Nature, Religion | ⚠ **en trop : Discrétion** |
| Artificier | 2 ✅ | Arcanes, Histoire, Investigation, Médecine, Nature, Perception, Escamotage | ✅ |

**Cause** : `Classes_Depart.json` contient *Discrétion* en trop pour ces cinq classes ; `SKILL_FIXES` (`core/data_loader.py`) ajoute les compétences manquantes (*Perspicacité*, *Tromperie*, *Dressage*, *Intimidation*) mais ne retire jamais la compétence en trop. Les « corrections appliquées » de `AUDIT_REGLES.md` n'ont pas touché ce fichier.
**Conséquence** : un Barbare, un Guerrier, un Paladin, un Ensorceleur ou un Occultiste peut choisir *Discrétion* comme compétence de classe.

### 3.3 Druide : liste d'armes 🟢

| | Officiel (PHB) | App |
|---|---|---|
| Armes maîtrisées | gourdin, dague, fléchette, javeline, masse d'armes, bâton, cimeterre, **serpe**, fronde, lance | gourdin, dague, fléchette, javeline, masse d'armes, bâton, cimeterre, fronde, lance, **arbalète légère** |
| Écart | | **manque la serpe** ; **arbalète légère en trop** |

Vérifié par `rules.weapon_proficient` : serpe → non maîtrisée, arbalète légère → maîtrisée.

### 3.4 Aptitudes de classe, niveau par niveau 🟢

Noms et niveaux relus pour les 13 classes, y compris les options de Tasha (marquées « option Tasha »). **Aucun écart** sur :

- les gains de caractéristique / dons (niveaux 4, 8, 12, 16, 19 ; Guerrier 6 et 14 en plus ; Roublard 10 en plus) ;
- l'Attaque supplémentaire (Barbare, Guerrier 5/11/20, Moine, Paladin, Rôdeur) ;
- les gains majeurs : Rage, Ki, Châtiment divin, Forme sauvage (niv. 2, 4, 8), Conduit divin (2, 6, 18), Intervention divine (10, 20), Magie des pactes, Arcanum mystique (11, 13, 15, 17), Restauration arcanique, Source de magie, Métamagie, Attaque sournoise, Action rusée, Talent fiable, etc. ;
- le niveau de choix de la sous-classe (`SUBCLASS_LEVEL` : Clerc 1, Ensorceleur 1, Occultiste 1, Druide 2, Magicien 2, les autres 3).

Cas d'attention :
- **Barbare, Voie totémique** : seuls l'Ours, l'Aigle et le Loup (PHB) existent ; *Élan* et *Tigre* (XGE) manquent 🟡.
- **Paladin** : « Conduit divin (1/repos) » est listé comme aptitude de classe au niveau 3. En 2014 le Conduit divin du paladin vient du **serment** ; l'aptitude de classe correspond à *Exploitation du pouvoir divin* (Tasha, option). Présentation sans conséquence de règle.

### 3.5 Tables de règles (`core/rules.py`) 🟢

Chaque table a été appelée sur les niveaux 1 à 20 et comparée aux valeurs du Manuel des joueurs :

| Table | Verdict |
|---|---|
| Bonus de maîtrise (+2 à +6) | ✅ |
| Modificateurs (score → mod.) | ✅ |
| Points d'expérience par niveau (0 … 355 000) | ✅ |
| Achat de points (27 points, 8-15, coûts 0-9) | ✅ |
| Emplacements d'incantateur complet (niv. 1-20) | ✅ |
| Demi-incantateurs (Paladin, Rôdeur) : niveau / 2 arrondi au supérieur seul, arrondi à l'inférieur en multiclassage ; Artificier : toujours arrondi au supérieur | ✅ |
| Tiers d'incantateur (Chevalier occulte, Arnaqueur arcanique) | ✅ |
| Emplacements de pacte (Occultiste) | ✅ |
| Sorts mineurs connus (Barde, Clerc, Druide, Ensorceleur, Magicien, Occultiste, Artificier, tiers) | ✅ |
| Sorts connus (Barde, Ensorceleur, Occultiste, Rôdeur, tiers) | ✅ |
| Sorts préparés (niveau + mod., ou niveau/2 + mod.) | ✅ |
| Manifestations occultes connues (2, 3, 4, 5, 6, 7, 8) | ✅ |
| Dé d'arts martiaux (d4 / d6 / d8 / d10 aux niveaux 1, 5, 11, 17) | ✅ |
| Points de ki, bonus de dégâts de rage (+2 / +3 / +4), rages par repos long (2 → 6, illimitées au 20) | ✅ |
| Forme sauvage : FP max, nage, vol, durée, utilisations (druide classique et Cercle de la Lune) | ✅ |
| Augmentation des sorts mineurs (niveaux 5, 11, 17) | ✅ |
| Prérequis de multiclassage (13 classes) | ✅ |
| Maîtrises gagnées au multiclassage (armures, armes) | ✅ |
| Déplacement du moine sans armure (+3 à +9 m) et du barbare (+3 m niv. 5, sans armure lourde) | ✅ |
| Capacité de charge : Force × 7,5 kg (15 livres converties à 0,5 kg), encombrement optionnel | ✅ (convention de la version française) |

**Omission mineure (multiclassage)** 🟡 : `MULTICLASS_PROFS` ne gère que les armures et les armes. Les gains du Manuel des joueurs en **outils et compétences** ne sont pas modélisés : Barde (1 compétence + 1 instrument), Rôdeur (1 compétence), Roublard (1 compétence + outils de voleur), Artificier (outils de voleur + outils de bricoleur).

### 3.6 Équipement de départ et or 🟢

Les 13 paquetages (`CLASS_KITS`, option « a » du PHB, option standard pour l'Artificier de Tasha) et l'or de départ (`STARTING_GOLD`) sont conformes (Barbare 2d4×10, Moine 5d4, Occultiste 4d4×10, Ensorceleur 3d4×10, etc.).

---

## 4. Sous-classes : présentes, manquantes, en trop

Sources officielles retenues : PHB, DMG, XGE, TCE, SCAG et suppléments publiés sous les règles 2014. Les noms français sont ceux de l'application.

| Classe | Présentes (officielles) | **Manquantes** (officielles 2014) | **En trop** (communauté) |
|---|---|---|---|
| **Barbare** | Berserker ; Totémique (Ours, Aigle, Loup) ; Gardien ancestral ; Tempêtes (Désert, Mer, Toundra) ; Zélote ; Bête ; Magie sauvage | **Batailleur** (SCAG, nains) 🟢 ; totems **Élan** et **Tigre** (XGE) 🟡 | Météore, Colosse des glaces |
| **Barde** | Savoir ; Vaillance ; Séduction ; Épées ; Murmures ; Éloquence ; Création | **Esprits** (Ravenloft) 🟢 | Commandants, Discorde |
| **Clerc** | Guerre ; Lumière ; Nature ; Ruse ; Savoir ; Tempête ; Vie ; Mort ; Forge ; Tombe ; Crépuscule ; Ordre ; Paix ; Arcane (SCAG) | aucune | Sang |
| **Druide** | Lune ; Terre ; Rêves ; Berger ; Astres ; Spores ; Fournaises | aucune | Mutation, Sangsue |
| **Ensorceleur** | Draconique ; Magie sauvage ; Âme divine ; Ombres ; Tempêtes ; Esprit aberrant ; Âme mécanique | **Sorcellerie lunaire** (Dragonlance) 🔴, **Âme de géant** (Bigby) 🔴 | Lignée du sang, Magie cosmique |
| **Guerrier** | Champion ; Maître de guerre ; Chevalier occulte ; Archer arcanique ; Cavalier ; Samouraï ; Chevalier runique ; Soldat psi | **Banneret / Chevalier du Dragon pourpre** (SCAG) 🟢 ; **Chevalier-écho** (Wildemount) 🟢 | Chevalier de sang, Pancratiaste |
| **Magicien** | 8 écoles ; Magie de guerre ; Chantelame ; Ordre des scribes ; Chronurgie | **Graviturgie** (Wildemount) 🟢 | Magicien du sang, Liaison élémentaire, Gravure runique |
| **Moine** | Paume ; Ombre ; Quatre éléments ; Âme solaire ; Kensei ; Maître ivre ; Astre intérieur ; Miséricorde | **Longue Mort** (SCAG) 🟢 ; **Âme cobalt** (Wildemount) 🟢 ; **Dragon ascendant** (Fizban) 🔴 | Voie du sang, Voie de la tempête |
| **Occultiste** | Archifée ; Fiélon ; Grand Ancien ; Céleste ; Lame maudite ; Génie (4 variantes) ; Insondable | **L'Immortel** (*Undying*, SCAG) 🟢 ; **Le Mort-vivant** (*Undead*, Ravenloft) 🔴 | Moissonneur, Protecteur astral |
| **Paladin** | Dévotion ; Anciens ; Vengeance ; Conquête ; Rédemption ; Gloire ; Guetteurs | **Parjure** (DMG) 🟢 ; **Couronne** (SCAG) 🟢 | Sang, Cendres |
| **Rôdeur** | Chasseur ; Maître des bêtes ; Traqueur des ténèbres ; Arpenteur de l'horizon ; Tueur de monstres ; Gardien des nuées ; Vagabond féérique | **Gardien draconique** (Fizban) 🔴 | Traqueur de sang, Artisan des pièges |
| **Roublard** | Voleur ; Assassin ; Arnaqueur arcanique ; Bretteur ; Conspirateur ; Éclaireur ; Enquêteur ; Lame psychique ; Fantôme | aucune | Lame d'ombre, Pistoléro |
| **Artificier** | Alchimiste ; Armurier ; Artilleur ; Forgeur d'armes | aucune | Automaturge, Cartomancien, Horloger |

**Niveaux des aptitudes de sous-classe** : relus pour toutes les sous-classes officielles présentes (aptitudes aux niveaux 3/6/10/14 ou 1/2/6/10/14/17/18 selon la classe, Serments aux niveaux 3/7/15/20, Domaines aux niveaux 1/2/6/8/17) ; **aucun écart** de niveau.

**Extrait du recoupement textuel** (§12) : *Athlète remarquable* niveau 7, *Bénédiction du dieu de la guerre* niveau 6, *Radiance de l'aube* jet de Constitution, *Atténuation des éléments* sans limite, *Halo de spores* 1d4 au niveau 2, *Élixir expérimental* niveau 3, *Manipulateur perspicace* niveau 9, *Paroles déstabilisantes* sur un jet de sauvegarde : tous **conformes** à 2014.

---

## 5. Historiques

**Bilan : 81 entrées = 12 conformes + 8 à corriger (1 historique du PHB, 1 variante du PHB, 6 approximations de suppléments) + 61 hors catalogue.** Tableau complet en annexe A.

### 5.1 Manuel des joueurs (13 historiques)

Présents : Acolyte, Artisan de guilde, Artiste, Charlatan, Criminel, Enfant des rues, Ermite, Héros du peuple, Marin, Noble, Sage, Sauvageon, Soldat. Compétences, outils, or et langues sont **conformes** pour 12. **Sauvageon** : langues « - » alors que la règle donne 1 langue au choix.

**Variantes du PHB** : *Pirate* présent mais avec Tromperie au lieu de Perception ; *Gladiateur*, *Espion*, *Marchand de guilde* et *Chevalier* absents 🟡.

### 5.2 Guide de l'aventurier pour la Côte des Épées (SCAG) et autres

Sur les 12 historiques du SCAG, seuls *Garde* (≈ City Watch), *Mercenaire* (≈ Mercenary Veteran) et *Chasseur de primes* (≈ Urban Bounty Hunter) ont un équivalent approximatif, avec des compétences fausses. **Manquent** : Artisan de clan, Érudit cloîtré, Courtisan, Agent de faction, Voyageur lointain, Héritier, Chevalier de l'ordre, Membre d'une tribu Uthgardt, Noble d'Eauprofonde 🟡. Hors SCAG, *Hanté* (Ravenloft) et *Pilleur de ruines* (≈ Archéologue, Tomb of Annihilation) sont présents mais figés ou inexacts.

### 5.3 Historiques hors catalogue (61)

Aucun historique officiel 2014 ne porte ces noms ni ces valeurs. Beaucoup dupliquent un historique existant : *Artisan*, *Artisan local*, *Membre de guilde*, *Commerçant* ≈ Artisan de guilde ; *Cambrioleur*, *Voleur à la tire*, *Miséreux*, *Orphelin* ≈ Enfant des rues / Criminel ; *Militaire*, *Officier*, *Patrouilleur* ≈ Soldat ; *Matelot* ≈ Marin ; *Noblesse de robe*, *Sang bleu* ≈ Noble. Quatre entrées sont incomplètes ou humoristiques (*Idiot du village* — langue « Gnéééé », outil « Le jeu du caillou » ; *Crapule*, *Bâtard*, *Solitaire*, sans or).

**À trancher** : si ces historiques sont voulus par ta table, ils doivent être étiquetés « maison » ; sinon ils sont à retirer.

---

## 6. Espèces

**Bilan : 70 espèces = 13 PHB + 12 suppléments officiels de l'époque 2014 + 42 en version 2021-22 (MotM, Spelljammer, Ravenloft, Dragonlance, Strixhaven : bonus libres) + 3 non officielles.** Tableau complet en annexe C.

### 6.1 Manquantes (officielles) 🟢

| Espèce | Source | Remarque |
|---|---|---|
| **Demi-orque** | PHB | Espèce de base ; seul l'« Orc » de MotM est présent. **Manque le plus visible.** |
| Aasimar fléau | Volo | Protecteur et déchu présents, pas le fléau |
| Changeforme (Shifter) | Éberron | Absent |
| Drakéide chromatique / métallique / gemme | Fizban | Variantes 2021 🔴 |
| Variantes de Tieffelin (lignées d'Asmodée, etc.) | MToF | En partie couvertes par les variantes « héritage infernal » |
| Halfelin des Lotusden, Elfe pâle | Wildemount | 🔴 |

### 6.2 Versions 2022 au lieu des versions 2014 🟠

31 espèces portent la source *Monstres du Multivers* — auxquelles s'ajoutent 11 espèces de Spelljammer, Dragonlance, Strixhaven et Ravenloft à bonus libres — (Aarakocra, Changelin, Duergar, Éladrin, Elfe des mers, Fadette, Féral, Firbolg, Genasi ×4, Githyanki, Githzerai, Gobelin, Gobelours, Goliath, Gnome des profondeurs, Hobgobelin, Homme lézard, Kenku, Kobold, Minotaure, Orc, Satyre, Shadar-kai, Tabaxi, Tortle, Triton, Yuan-ti…). Exemples d'écart avec 2014 :

| Espèce | Version dans l'app (2022) | Version 2014 |
|---|---|---|
| Goliath | +2/+1 libres ; Endurance de pierre = bonus de maîtrise fois par repos long | For +2, Con +1 ; Endurance de pierre = 1 fois par repos court ou long ; Athlète-né |
| Éladrin | +2/+1 libres ; Pas féérique = bonus de maîtrise fois par repos long | Dex +2, Cha +1 ; Pas féérique 1 fois par repos court ou long ; l'effet saisonnier du niveau 3 existe déjà en 2014 |
| Orc | +2/+1 libres, Charge d'adrénaline | For +2, Con +1, Int −2 ; Agressif, Menaçant |
| Kobold, Gobelin, Gobelours… | bonus libres, utilisations = bonus de maîtrise | bonus fixes, malus (Kobold For −2) |
| Gnome des profondeurs | vitesse 9 m | vitesse 7,5 m (MToF) |
| Duergar | vitesse 9 m | vitesse 7,5 m |

Le moteur gère bien les bonus libres : `race_rule()` propose « +2/+1 » ou « +1/+1/+1 » (testé sur l'Orc).

### 6.3 Conformes

Les 13 espèces du Manuel des joueurs (bonus, vitesses, langues, aptitudes) sont conformes, y compris : Nain des montagnes **For +2 / Con +2**, Nain des collines Con +2 / Sag +1, Elfe des bois **vitesse 10,5 m**, Drakéide (souffle 2d6 → 5d6 aux niveaux 6, 11, 16 ; Or/Rouge cône Dex, Vert cône Con poison), Gnome des forêts (Communication avec les petits animaux, trait 2014), Loxodon **CA 12 + Con**, Minotaure et Léonin **DD calculés**, Githzerai **sans bonus de CA**.

### 6.4 Autres remarques

- **Conil** est l'Harengon officiel (*The Wild Beyond the Witchlight*, 2021) renommé ; sa source « Création de la communauté » est fausse.
- **Kitsune** et **Myconide éveillé** n'existent dans aucun livre WotC.
- `Bonus_Raciaux.json` : 19 vitesses spéciales ; toutes les autres espèces reçoivent 9 m par défaut. Les vitesses relevées (Centaure 12 m, Dhampir 10,5 m, Genasi d'air 10,5 m, Léonin 10,5 m, Satyre 10,5 m, Nain 7,5 m, Halfelin 7,5 m, Gnome 7,5 m) sont conformes à la source utilisée.

---

## 7. Compétences, langues, outils

- **Compétences** 🟢 : 18 / 18, avec la bonne caractéristique pour chacune.
- **Langues** 🟢 : 8 standards + 8 exotiques, complètes. Noms à corriger : « Gobelours » désigne en réalité la langue **gobeline** ; « Geant » et « Celeste » sans accent ; « Profond » = le Profond.
- **Outils** 🟡 : 25 outils (17 outils d'artisan + 8 autres) : couverture correcte. **Manquent** les véhicules (terrestres, aquatiques) pourtant exigés par plusieurs historiques, et les jeux et instruments ne sont pas détaillés (une « boîte de jeux » et un « instrument de musique » génériques). **En trop** : la caractéristique associée à chaque outil (§2.4).

---

## 8. Dons

**Bilan : 86 entrées = 36 conformes + 16 avec écart + 34 non rattachés à un don officiel.** Tableau complet en annexe B.

### 8.1 Manuel des joueurs : 14 dons manquants 🟢

*Expert de la charge* (Charger), *Duelliste défensif*, *Lutteur*, *Guérisseur*, *Protection lourde*, *Chef inspirant*, *Protection légère*, *Linguiste*, *Tueur de mages*, *Protection intermédiaire*, *Sentinelle*, *Compétent*, *Discret* (Skulker), *Tireur de sorts* (Spell Sniper).

### 8.2 Xanathar : 11 dons raciaux manquants 🟡

Peur du dragon, Peau de dragon, Haute magie drow, Robustesse naine, Précision elfique, Disparition (Fade Away), Téléportation féérique, Flammes de Phlégéthos, Fureur orque, Seconde chance, Magie des elfes des bois. Présents : Prodige, Chance abondante, Constitution infernale, Agilité des courts-sur-pattes.

### 8.3 Dons présents avec écart (16)

Les principaux : **Dur à cuire** (description fausse, ce n'est pas *Durable*), **Maître des armures intermédiaires** (un +1 Force/Dextérité inventé), **Tranchant / Acéré** (doublons de *Slasher*, relance inventée), **Résistant** (doublon de *Résilient*), **Prodigieusement doué** (prérequis inventé), **Adepte des ombres** (décrit le mauvais sort), plus des sources erronées (*Esprit affûté* et *Maître des poisons*).

### 8.4 Dons non rattachés (34) 🔴

Entre autres : *Acolyte* et *Agent de Strixhaven*, *Artiste prodige*, *Audacieux*, *Connaisseur des glyphes*, *Initié aux arts martiaux*, *Agent secret*, *Chirurgien de combat* (ressemble à *Guérisseur*), *Maître des bêtes*, *Vigueur surhumaine*, *Résistance draconique* (le texte donne +1 à la CA : invention), *Érudit du feu*, *Perceptif*… Les dons liés à Fizban, Strixhaven, Éberron et Wildemount sont à confirmer dans les livres.

**Bon point** : quand un don est reconnaissable, ses valeurs sont celles de **2014** (*Chanceux* : 3 points ; *Alerte* : +5 à l'initiative ; *Attaquant sauvage* : relance un dé ; *Robuste* : +2 PV par niveau). Rien de 2024 ne s'y est glissé.

---

## 9. Armes, armures

### 9.1 Armes (38) — valeurs fausses 🟢

| Arme | App | Règle 2014 | Écart |
|---|---|---|---|
| **Lance d'arçon** (Lance) | 1d10 perforants | **1d12** perforants | dégâts |
| **Trident** | 1d8, polyvalente 1d10 | **1d6**, polyvalente 1d8 | dégâts |
| **Javeline** | 5 po | **5 pa** | prix |
| **Serpe** | 1 pa | **1 po** | prix |
| **Marteau de guerre** | 2,5 kg | 1 kg (2 lb) | poids |
| **Filet** | absent | arme de guerre à distance, spéciale | **manquant** |

Les autres armes (dégâts, propriétés, portées, prix) correspondent au Manuel des joueurs. Mousquet et pistolet sont des armes à feu **optionnelles du Guide du maître**, correctement étiquetées.

### 9.2 Armures (17 : 13 officielles + 4 communauté) 🟢

Les 12 armures du PHB et le bouclier sont **conformes** (CA, Force requise, désavantage en Discrétion, poids, prix). **En trop** : 4 éléments « Création de la communauté » (§2.3).

---

## 10. Magie

### 10.1 Sorts 🟢

- **488 sorts** : 44 sorts mineurs, 74 de niveau 1, 76 de niveau 2, 68 de niveau 3, 51 de niveau 4, 60 de niveau 5, 47 de niveau 6, 26 de niveau 7, 22 de niveau 8, 20 de niveau 9.
- **Complets** pour les sorts mineurs (PHB + XGE + TCE) et les niveaux 8 et 9.
- **Échantillon de 48 sorts** : niveau, école et liste de classe conformes, sauf deux listes :
  - *Mot de pouvoir mortel* : le **Barde** manque (PHB : Barde, Ensorceleur, Occultiste, Magicien) 🟡 ;
  - *Mur de feu* : l'**Artificier** est en trop (probable) 🟡.
- **Manquent** : *Grêle d'épines* et *Purification de nourriture et d'eau* (niveau 1, PHB) 🟢 ; les sorts de Wildemount (par ex. *Pulse Wave*, *Gravity Fissure*, *Magnify Gravity*) 🟡.
- Les écoles sont stockées avec une majuscule initiale (« Évocation ») : détail sans effet.
- *Infestation* est bien accessible à l'Occultiste (XGE).

### 10.2 Manifestations occultes 🟢

**54 / 54** : PHB 32, Xanathar 14, Tasha 8. Noms, sources, niveaux requis et pactes requis sont exacts (par exemple *Lame assoiffée* niveau 5 + Pacte de la lame, *Chaîne des carcères* niveau 15 + Pacte de la chaîne, *Lien du talisman* niveau 12).

### 10.3 Styles de combat 🟢

Guerrier 11 (PHB + Tasha), Paladin 7, Rôdeur 7, Barde des épées 2 : listes **complètes et conformes**. Une imprécision : *Interception* indique « 1d10 + modificateur (ou bonus de maîtrise) » ; la règle est « 1d10 + votre **bonus de maîtrise** ».

### 10.4 Manœuvres du Maître de guerre 🟢

**23 / 23** (PHB 16 + XGE 7). La manœuvre *Échange de position* (Bait and Switch) porte la source « (Tasha) » alors qu'elle vient de Xanathar ; effet conforme (« vous ou elle » ajoutez le dé).

### 10.5 Métamagie 🟢

10 options (PHB 8 + Tasha 2), coûts conformes, y compris *Sort jumeau* (niveau du sort, 1 pour un sort mineur).

---

## 11. Bestiaire de la Forme sauvage 🟢

`monsters_db.json` (88 créatures) : CA, PV, vitesses et FP de l'échantillon testé (loup, loup sanguinaire, ours brun et noir, lion, tigre, panthère, aigle et aigle géant, crocodile et crocodile géant, requin ×3, serpents, araignées, chevaux, éléphant, mammouth, rats, chat) correspondent au **Manuel des monstres 2014**.

---

## 12. Recoupement avec `ECARTS-CLASSEUR.md`

Légende : ✅ ton application suit la règle 2014 · ⚠ écart · ➖ absent de ton application. La colonne « Classeur / autre app » résume le constat du fichier.

### Dons

| Élément | Autre app (classeur) | Règle 2014 | **Ton app** |
|---|---|---|---|
| Expert de la charge | +5 pour toucher | +5 aux dégâts | ➖ don absent |
| Trancheur / Slasher | +1 dé de dégâts au critique | désavantage aux attaques de la cible | ⚠ doublon, effet inventé |
| Mobile | la cible ne provoque pas | vous ne provoquez pas | ✅ |
| Athlète | — | escalade sans coût supplémentaire | ✅ |
| Adepte élémentaire | ignore la résistance | + les 1 comptent comme 2 | ⚠ la 2ᵉ partie manque |
| Cogneur lourd / Briseur d'armes lourdes | toute arme | arme lourde | ✅ |
| Combattant monté | cible « moyenne » | plus petite que la monture | ✅ |
| Linguiste | prérequis lanceur | aucun | ➖ don absent |
| Observateur, Résilient | prérequis | aucun | ✅ aucun prérequis |
| Mage de guerre | aucun prérequis | savoir lancer un sort | ✅ prérequis présent |
| Maître des armures lourdes | aucun prérequis | armures lourdes | ✅ prérequis ; ⚠ condition d'armure absente du texte |
| Protection intermédiaire | aucun prérequis | armures légères | ➖ don absent |

### Espèces

| Élément | Autre app | Règle 2014 | **Ton app** |
|---|---|---|---|
| Goliath, Endurance de pierre | 1 / repos long | 1 / repos court ou long | ⚠ version 2022 (bonus de maîtrise / repos long) |
| Goliath, taille | « Grande » | Puissante carrure | ✅ taille Moyenne + compte comme Grand |
| Drakéide | Dex / Con mélangés | Dex (Or, Rouge), poison (Vert) | ✅ |
| Éladrin | sorts mineurs saisonniers, 1 / repos long | pas de sort mineur saisonnier ; Pas féérique au repos court | ⚠ pas de sort mineur saisonnier ✅ ; utilisations = bonus de maîtrise / repos long (version 2022) |
| Nain des montagnes | For +1 (liste) | For +2 | ✅ |
| Races « +2 ; +1 ou +1,+1,+1 » | +1,+1,+1 non proposé | (MotM) idem | ✅ proposé |
| Loxodon | 12 + Dex | 12 + Con | ✅ |
| Minotaure, Léonin | DD fixes | DD calculés | ✅ |
| Githzerai | +1 CA | pas de bonus | ✅ |
| Gnome des forêts | sort | trait « petits animaux » | ✅ trait |
| Haut-elfe, Kobold | sort mineur au choix | idem | ✅ |

### Classes et options

| Élément | Autre app | Règle 2014 | **Ton app** |
|---|---|---|---|
| Rôdeur, compétences | 2 (Classes2) / 3 | 3 | ✅ 3 |
| Arbalète de poing | à deux mains | une main, légère | ✅ |
| Guerrier, équipement | arc long | cotte de mailles | ✅ |
| Paladin, Perception divine | 1 / repos long | 1 + Cha / repos long | ✅ |
| Paladin, Châtiment divin | 1d8 + 1d8 | 2d8 + 1d8 / niveau (max 5d8) + 1d8 mort-vivant | ✅ |
| Technique supérieure | repos long | repos court ou long | ➖ non vérifié (style présent) |
| Chassé-croisé | à la créature et à vous | à vous ou à la créature | ✅ |
| Sort jumeau | niveau × 2 | niveau (1 si mineur) | ✅ |
| Attaque occulte | sans niveau | niveau 5 | ✅ niveau 5 |
| Archer arcanique | +4d6 dès le niveau 3 | 2d6 puis 4d6 au niveau 18 | ✅ |
| Ennemi juré | gnolls et orcs | deux races d'humanoïdes | ✅ |
| Maître des bêtes, Entraînement exceptionnel | pas d'Esquive | Esquive possible | ✅ Esquiver |

### Sous-classes

| Élément | Autre app | Règle 2014 | **Ton app** |
|---|---|---|---|
| Champion, Athlète accompli | niveau 3 | niveau 7 | ✅ 7 |
| Parjure | action bonus | action | ➖ sous-classe absente |
| Conquête, Rédemption | variantes | règle | ✅ (Persuasion, 9 m, après dégâts) |
| Conspirateur, Manipulateur perspicace | niveau 3 | niveau 9 | ✅ 9 |
| Voleur, Mains lestes | sans outils de voleur | + outils de voleur | ✅ |
| Bretteur, Jeu de jambes | toute attaque | corps à corps | ✅ |
| Enquêteur, Détecteur de mensonges | moins de 7 | 7 ou moins | ✅ |
| Domaine de la guerre | niveau 2 | niveau 6 | ✅ 6 |
| Domaine de la lumière | Sagesse | Constitution | ✅ Constitution |
| Atténuation des éléments | 1 / combat | sans limite | ✅ |
| Alchimiste, Élixir | niveau 6 | niveau 3 | ✅ 3 |
| Cercle des spores, Halo | niveau 6, 1d6 | niveau 2, 1d4 | ✅ |
| Éloquence, Paroles déstabilisantes | jet d'attaque | jet de sauvegarde | ✅ |
| Voies des tempêtes, auras | valeurs fixes | 2/3/4/5/6 progressif | ✅ |
| Servitude de la tombe | niveau 5 | (manifestation) niveau 5 | ✅ |

**Lecture** : sur ≈ 55 lignes contrôlées, ton application suit la règle 2014 pour **la grande majorité**. Les écarts restants sont soit des **absences** (dons, Parjure), soit des choix de **version 2022** (Goliath, Éladrin).

---

## 13. Recommandations (rien n'a été appliqué)

### Priorité 1 — règles de 2014 trahies
1. **Retirer ou rendre optionnelle la botte d'arme** (§2.1) : désactiver `botte_arme` par défaut (drapeau de réglage « règles de 2024 »), ou la supprimer de `Armes.json`.
2. **Marquer les 18 actions d'arme BG3 comme « règle maison »**, désactivées par défaut (§2.2).
3. **Corriger les compétences de classe** : retirer *Discrétion* des listes du Barbare, du Guerrier, du Paladin, de l'Ensorceleur et de l'Occultiste (`Classes_Depart.json`, §3.2).
4. **Corriger la liste d'armes du Druide** : ajouter la serpe, retirer l'arbalète légère (§3.3).
5. **Ajouter le Demi-orque** (§6.1).

### Priorité 2 — catalogues
6. **Dons** : ajouter les 14 dons manquants du PHB, corriger les 16 dons à écart, et trancher le sort des 34 non rattachés (retirer, ou étiqueter « maison ») (§8).
7. **Historiques** : ajouter les 9 historiques manquants du SCAG, corriger les 8 écarts, étiqueter ou retirer les 61 hors catalogue (§5).
8. **Armes** : corriger Lance d'arçon (1d12), Trident (1d6 / 1d8), prix de la Javeline et de la Serpe, poids du Marteau de guerre ; ajouter le Filet (§9.1).
9. **Étiqueter** les 27 sous-classes, 4 armures et 3 espèces « communauté » pour qu'on puisse les masquer en mode « officiel 2014 » ; corriger le nom de *Domaine de l'Arcane* et la source du *Conil* (§2.3).

### Priorité 3 — compléments
10. **Sous-classes manquantes** (§4) : Banneret, Chevalier-écho, Graviturgie, Longue Mort, Âme cobalt, Parjure, Couronne, Mort-vivant (SCAG), Batailleur, totems Élan et Tigre.
11. **Espèces** : décider si les 31 espèces MotM restent en version 2022 ; si l'objectif est « 2014 strict », prévoir les versions de Volo / Mordenkainen / Éberron.
12. **Sorts** : ajouter *Grêle d'épines* et *Purification de nourriture et d'eau* ; vérifier *Mot de pouvoir mortel* (Barde) et *Mur de feu* (Artificier).
13. **Multiclassage** : modéliser les gains d'outils et de compétences (§3.5).
14. **Vocabulaire** : « espèce » → « race » si tu veux coller au Manuel 2014 ; retirer la caractéristique par outil (§2.4).

### Un réglage global à envisager
Un réglage « **Référentiel de règles : 2014 strict / 2014 + suppléments récents / tout** » permettrait de garder le contenu non 2014 sans qu'il pollue une table qui joue 2014. Toutes les étiquettes de ce document (🟢 🟠 🔴, « communauté », « 2022 », « 2024 ») peuvent servir de champ `referentiel` dans les données.

---

## 14. Sous-classes « maison » : existence en ligne et propositions

> Complément demandé après la première version de l'audit. **Recherche web uniquement** : seules des recherches ont fonctionné, les pages elles-mêmes n'étaient pas lisibles depuis cette session (sites hors de la liste autorisée). Je ne peux donc ni comparer le texte de l'application à celui d'une source, ni juger l'équilibre ou la complétude niveau par niveau.

### 14.1 Les 27 sous-classes de l'application existent-elles en ligne ?

**Réponse courte** : pour **10 d'entre elles**, une sous-classe de même nom existe en ligne, mais le plus souvent **en plusieurs versions écrites par des auteurs différents**. Pour **4**, il existe une sous-classe proche. Pour **12**, je n'ai rien trouvé. **Aucune** n'est attribuée à un auteur ou à un lien dans l'application, donc je ne peux pas dire d'où vient son texte.

Légende : 🟢 une version de même nom existe · 🟡 sous-classe proche · 🔴 rien trouvé · ⚪ non vérifié. « Rien trouvé » ne prouve pas l'inexistence : le nom français peut traduire un titre anglais différent.

| Classe | Sous-classe (app) | Résultat | Ce que j'ai trouvé |
|---|---|---|---|
| Barbare | Voie du Météore | 🟢 | *Path of the Meteor*, au moins deux versions indépendantes sur GM Binder (dont une au format 2024) |
| Barbare | Voie du Colosse des glaces | 🟡 | rien sous ce nom ; proches : *Path of the Frozen Sea*, *Path of the Frozen Warrior* |
| Barde | Collège des Commandants | 🟡 | *College of Command* (LaserLlama), pas *Commanders* |
| Barde | Collège de la Discorde | 🟢 | *College of Discord*, au moins deux versions sur D&D Beyond |
| Clerc | Domaine du Sang | 🟢 | de nombreuses versions ; une est **publiée** : *Blood Domain* dans *Tal'Dorei Campaign Setting Reborn* (Darrington Press, 2022) |
| Druide | Cercle de la Mutation | 🟢 | *Circle of Mutation* sur D&D Wiki et dans *Grim Hollow* |
| Druide | Cercle de la Sangsue | 🔴 | rien ; le plus proche est *Circle of Ichor* (mécanique de « points de sangsue », page inachevée) |
| Ensorceleur | Lignée du sang | ⚪ | non recherché séparément |
| Ensorceleur | Magie cosmique | 🟢 | plusieurs « Cosmic Magic / Cosmic Sorcerer » (dont Mage Hand Press, format 2024) |
| Guerrier | Chevalier de sang | 🟢 | *Blood Knight*, plusieurs versions (D&D Wiki, D&D Beyond, World Anvil) |
| Guerrier | Pancratiaste | 🔴 | rien ; proche : *Pugilist* (Tome of Heroes) |
| Magicien | Magicien du sang | 🟡 | pas sous ce nom ; un sous-ensemble « hémocraftie » existe dans *Tal'Dorei Reborn* (nom exact non confirmé) et *Sangromancer* dans *Grim Hollow* |
| Magicien | Liaison élémentaire | 🔴 | rien |
| Magicien | Gravure runique | 🔴 | rien ; proches : *Rune Scribe*, *Runic Knight* |
| Moine | Voie du Sang | 🔴 | rien de convaincant |
| Moine | Voie de la Tempête | 🔴 | rien |
| Occultiste | Le Moissonneur | 🟢 | *Reaper: A Warlock Patron* (Zargo Games, itch.io, payant) et d'autres |
| Occultiste | Le Protecteur astral | 🟢 | *Astral Guardian*, sur D&D Beyond (homebrew) |
| Paladin | Serment du Sang | 🟢 | *Oath of Blood*, plusieurs versions sur D&D Beyond |
| Paladin | Serment des Cendres | 🔴 | rien |
| Rôdeur | Traqueur de sang | 🔴 | rien |
| Rôdeur | Artisan des pièges | 🔴 | rien ; *Trapper* existe seulement comme guilde du Chasseur de monstres de *Grim Hollow* |
| Roublard | Lame d'ombre | 🔴 | rien |
| Roublard | Pistoléro | 🔴 | rien |
| Artificier | Automaturge | 🟡 | *Automaton Creator*, *Mechanist*, *Animator*… mais pas ce nom |
| Artificier | Cartomancien | 🔴 | rien |
| Artificier | Horloger | 🟢 | *Clockmaker* / *Horologist*, plusieurs versions (D&D Beyond, ENWorld) |

**Ce que cela veut dire** : ces noms sont des thèmes très courants (« sang », « horloger », « tempête »). Ils correspondent à des idées répandues plus qu'à des œuvres identifiables. **Le risque** : sans attribution, tu ne peux pas savoir si le texte est une création originale, une traduction de la version d'un auteur, ou un texte tiré d'un livre commercial. Pour un livre publié (Tal'Dorei Reborn, Grim Hollow, Tome of Heroes), recopier le texte dans l'application demande l'accord de l'éditeur. Une étiquette « auteur, source, lien » par sous-classe lèverait le doute.

### 14.2 Propositions : deux sous-classes « communauté » par classe

**Aucun classement de popularité n'existe en ligne** (les recherches ne ramènent que des listes subjectives ou de faible qualité). Je n'ai donc pas pu classer par popularité. J'ai retenu des sous-classes issues de **trois livres édités** par des studios, plus aboutis que des créations isolées, et dont **l'existence et la classe ont été confirmées par recherche** :

| Livre | Éditeur | Édition de règles | Contenu retenu ici |
|---|---|---|---|
| *Tal'Dorei Campaign Setting Reborn* (2022) | Darrington Press (Critical Role) | 5e 2014 | 9 sous-classes ; confirmées : Voie du Juggernaut (Barbare), Collège de la Tragédie (Barde), Domaine du Sang et Domaine de la Lune (Clerc), Serment de la Haute Mer (Paladin) |
| *Grim Hollow Player's Guide* | Ghostfire Gaming | 5e 2014 (2020) ; **réédité aux règles 2024 en 2025** | 2 à 3 sous-classes par classe ; noms confirmés pour 12 classes (ci-dessous) |
| *Tome of Heroes* (2022) | Kobold Press | 5e 2014 | plus de 70 sous-classes ; confirmées : Cercle des Abeilles, Voie de l'Archer infaillible, Voie de l'Enfer, École de la Poudre noire, Pugilist, Collège des Ombres, Voie du Mouvement concordant |

| Classe | Proposition 1 | Proposition 2 | Remarque |
|---|---|---|---|
| **Barbare** | *Path of the Juggernaut* (Tal'Dorei Reborn) 🟢 | *Path of Hellfire* (Tome of Heroes) 🟢 | Alternatives Grim Hollow : voies des Fracturés, de l'Esprit primal, des Morts courroucés |
| **Barde** | *College of Tragedy* (Tal'Dorei Reborn) 🟢 | *College of Shadows* (Tome of Heroes) 🟢 | Grim Hollow : collèges des Aventuriers, des Fous, des Requiems |
| **Clerc** | *Blood Domain* (Tal'Dorei Reborn) 🟢 | *Moon Domain* (Tal'Dorei Reborn) 🟢 | L'app a déjà un Domaine du Sang : à remplacer si le texte est celui-ci ; Grim Hollow : domaines Éldritch, Inquisition, Purification |
| **Druide** | *Circle of Bees* (Tome of Heroes) 🟢 | *Circle of Mutation* (Grim Hollow) 🟢 | L'app a déjà un Cercle de la Mutation ; autres Grim Hollow : cercles du Sang, de l'Entropie |
| **Ensorceleur** | *Haunted* (Grim Hollow) 🟡 | *Apocalypse* (Grim Hollow) 🟡 | Troisième : *Wretched*. *Runechild* (Tal'Dorei Reborn) non confirmé 🔴 |
| **Guerrier** | *Pugilist* (Tome of Heroes) 🟢 | *Nightwatcher* ou *Bulwark Warrior* (Grim Hollow) 🟡 | *Living Crucible* : troisième option |
| **Magicien** | *School of Black Powder* (Tome of Heroes) 🟢 | *Plague Doctor* ou *Sangromancer* (Grim Hollow) 🟡 | *Daemonologist* : troisième option |
| **Moine** | *Way of the Unerring Arrow* (Tome of Heroes) 🟢 | *Way of Concordant Motion* (Tome of Heroes) 🟢 | *Way of the Cobalt Soul* est un contenu **officiel** de Wildemount (aussi reprise dans Tal'Dorei) : à ajouter côté officiel (§4) |
| **Occultiste** | *The Coven* ou *The First Vampire* (Grim Hollow) 🟡 | *The Parasite* (Grim Hollow) 🟡 | *Reaper* (Zargo Games, payant) en alternative |
| **Paladin** | *Oath of the Open Sea* (Tal'Dorei Reborn) 🟢 | *Oath of Zeal* ou *Oath of Pestilence* (Grim Hollow) 🟡 | *Oath of Slaughter* : troisième option |
| **Rôdeur** | *Primordial Archer* (Grim Hollow) 🟡 | *Vermin Lord* (Grim Hollow) 🟡 | *Green Reaper* : troisième option |
| **Roublard** | *Highway Rider* (Grim Hollow) 🟡 | *Misfortune Bringer* (Grim Hollow) 🟡 | *Sanguine Thief* : troisième option. Un test ENWorld juge « trop puissantes » les sous-classes de roublard de Tome of Heroes |
| **Artificier** | *Clockmaker / Horologist* (homebrew D&D Beyond) 🔴 | *Mechanist* ou *Animator* (D&D Wiki) 🔴 | **Aucune source éditée trouvée** pour cette classe : candidats d'auteurs isolés, à lire avant de choisir |

🟢 existence et classe confirmées · 🟡 nom trouvé dans les listes des guides de Grim Hollow (certaines listes sont celles de l'édition 2024) : à confirmer dans la version 2014 · 🔴 source non éditée ou non confirmée.

### 14.3 Réserves à connaître avant de choisir

1. **Pages non lues** : je n'ai vu que des titres et des résumés de recherche. Je n'ai pas pu vérifier la **complétude** (une sous-classe complète doit donner des aptitudes aux niveaux de sa classe : Guerrier 3, 7, 10, 15, 18 ; Magicien 2, 6, 10, 14 ; etc.) ni l'**équilibre**.
2. **Édition** : *Grim Hollow* existe en deux éditions. Les noms que j'ai pu confirmer viennent surtout de guides de l'édition **2024**. Pour un jeu en 2014, il faut la version de 2020. Certaines sous-classes proposées existent peut-être sous le même nom dans les deux versions avec des règles différentes.
3. **Droits** : ces trois livres sont des **produits commerciaux**. L'intégration du texte complet dans ton application nécessite l'accord des éditeurs. Le plus sûr est d'y mettre un résumé, le nom et la référence du livre.
4. **Style** : *Grim Hollow* est un cadre de **fantasy sombre** (vampires, sang, peste) ; *Tome of Heroes* est tourné vers Midgard. Ils ne conviennent pas à toutes les tables.
5. **Artificier** : c'est la classe où l'offre éditée est la plus mince.

### 14.4 Décisions à prendre (je n'ai rien modifié)

- Veux-tu **garder** les 27 sous-classes actuelles, en y ajoutant une étiquette de provenance, **ou les remplacer** par une sélection éditée ?
- Pour les propositions ci-dessus : quels livres possèdes-tu, ou peux-tu consulter ? Je ne peux rédiger fidèlement une aptitude que si tu me donnes le texte, ou si je peux le lire.

### 14.5 Sources consultées (résultats de recherche)

[Tal'Dorei Reborn sur D&D Beyond](https://www.dndbeyond.com/sources/tcsr) · [aperçu des 9 sous-classes](https://www.dndbeyond.com/posts/1549-preview-9-mighty-new-subclasses-from-taldorei) · [liste sur ComicBook](https://comicbook.com/gaming/news/critical-role-taldorei-reborn-subclasses-list) · [Grim Hollow Player's Guide](https://www.dndbeyond.com/sources/dnd/ghpg) · [guides Grim Hollow (Dungeonmister)](https://dungeonmister.com/grim-hollow/) · [Tome of Heroes (Kobold Press)](https://koboldpress.com/tome-of-heroes-5th-edition-character-options-for-your-game) · [avis ENWorld sur Tome of Heroes](https://www.enworld.org/threads/a-tome-of-heroes-review.691513/) · [Path of the Meteor](https://www.gmbinder.com/share/-MTDS56FjKw5pmbc2VSH) · [College of Discord](https://www.dndbeyond.com/classes/535090-college-of-discord) · [Blood Domain](https://www.dndbeyond.com/classes/601183-blood-domain) · [Circle of Mutation](https://dandwiki.com/wiki/Circle_of_Mutation_(5e_Subclass)) · [Cosmic Magic](https://magehandpress.com/2025/12/cosmic-magic-5e2024/) · [Blood Knight](https://www.dandwiki.com/wiki/Blood_Knight_(5e_Subclass)) · [Reaper (warlock)](https://zargogames.itch.io/reaper-a-warlock-patron) · [Astral Guardian](https://www.dndbeyond.com/classes/97568-astral-guardian) · [Oath of Blood](https://www.dndbeyond.com/subclasses/2280991-oath-of-blood) · [Clockmaker](https://www.dndbeyond.com/classes/2725879-clockmaker) · [archétypes de roublard (Nerdarchy)](https://nerdarchy.com/top-10-5e-dd-homebrew-roguish-archetypes-by-a-factor-of-three/)

---

## Annexes

Les trois annexes sont générées à partir de `data/Historiques.json`, `data/Dons.json` et `data/Races.json` ; le statut est mon classement (voir §1 pour les niveaux de confiance).

### Annexe A — Historiques (81)

| Historique (app) | Compétences | Langues | Outils | Or | Statut | Équivalent officiel 2014 | Remarque |
|---|---|---|---|---|---|---|---|
| Acolyte | Perspicacité + Religion | Deux au choix | - | 15 | ✅ conforme | Acolyte | Compétences, langues, outils et or conformes au PHB 2014. |
| Artisan | Athlétisme + Perspicacité | Commun | Deux ensembles d'outils d'artisan au choix | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Artisan de guilde | Perspicacité + Persuasion | Une au choix | Un type d'outil d'artisan | 15 | ✅ conforme | Guild Artisan | Compétences, langues, outils et or conformes au PHB 2014. |
| Artisan local | Athlétisme + Nature | Commun | Deux ensembles d'outils d'artisan au choix | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Artiste | Acrobaties + Représentation | Commun | Déguisement, un instrument de musique | 15 | ✅ conforme | Entertainer | Compétences, langues, outils et or conformes au PHB 2014. |
| Assassin | Discrétion + Perspicacité | Commun,+1 | Matériel d'empoisonneur | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Bandit de grand chemin | Intimidation + Survie | Commun, +1 au choix | Véhicules (terrestres) | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Bâtard | Histoire + Tromperie | — | Véhicules (terrestres), un ensemble d'outils d'artisan au ch | ∅ | ❓ hors catalogue | — | Or non renseigné, langues vides. |
| Brigand | Discrétion + Survie | Commun | Véhicules (terrestres), un type de jeu au choix | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Cambrioleur | Acrobaties + Discrétion | Commun | Outils de voleur, accessoires de déguisement | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Captif | Nature + Survie | Commun, celle de la tribu de captivité | Outil d'artisan | 5 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Charlatan | Escamotage + Tromperie | Commun | Déguisement, matériel de contrefaçon | 15 | ✅ conforme | Charlatan | Compétences, langues, outils et or conformes au PHB 2014. |
| Chasseur | Discrétion + Survie | Commun | Un type de jeu au choix, véhicules (terrestres) | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Chasseur de primes | Discrétion + Perspicacité | Commun | Outils de voleur, Type de jeu | 20 | ⚠ écart | ≈ Urban Bounty Hunter (SCAG) | Officiel : 2 compétences parmi Tromperie / Perspicacité / Persuasion / Discrétion, 2 outils au choix. Ici fixé à Discrétion + Perspicacité, outils de voleur + jeu. |
| Colporteur | Persuasion + Survie | Commun, +1 | Véhicules (terrestres) | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Commerçant | Perspicacité + Persuasion | Commun, +2 | — | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Crapule | Escamotage + Intimidation | — | — | ∅ | ❓ hors catalogue | — | Or non renseigné, ni langue ni outil. |
| Criminel | Discrétion + Tromperie | - | Outils de voleur, Type de jeu | 15 | ✅ conforme | Criminal | Compétences, langues, outils et or conformes au PHB 2014. |
| Cuisinier | Discrétion + Perspicacité | Commun,+1 | Ustensiles de cuisine | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Dévot | Perspicacité + Religion | Commun,+2 | — | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Éclaireur | Discrétion + Survie | Commun,+1 | Accessoires de déguisement | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Enfant des rues | Discrétion + Escamotage | - | Déguisement, outil de voleur | 10 | ✅ conforme | Urchin | Compétences, langues, outils et or conformes au PHB 2014. |
| Ermite | Médecine + Religion | Une au choix | Matériel d'herboriste | 5 | ✅ conforme | Hermit | Compétences, langues, outils et or conformes au PHB 2014. |
| Érudit | Arcanes + Histoire | Commun,+1 | Un au choix parmi : matériel de calligraphie, outils de cart | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Escroc | Persuasion + Tromperie | Commun | Deux au choix parmi un type de jeu, accessoires de faussaire | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Explorateur | Athlétisme + Survie | Commun, +1 | Véhicules (terrestres) | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Fugitif | Survie + Tromperie | Commun,+1 | Un type de jeu, outil d'artisan au choix | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Garde | Intimidation + Perspicacité | Commun,+1 | Un type de jeu au choix | 15 | ⚠ écart | ≈ City Watch (SCAG) | Officiel : Athlétisme + Perspicacité, 2 langues, pas d'outil. Ici Intimidation + Perspicacité, 1 jeu. |
| Gardien tribal | Perspicacité + Survie | Commun | Véhicules (terrestres), un instrument de musique au choix | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Gens du voyage | Représentation + Tromperie | Commun | Véhicules (terrestres), instrument de musique au choix | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Guide | Athlétisme + Survie | Commun | Véhicules (terrestres), un type de jeu au choix | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Habitant de la forêt | Nature + Survie | Commun, Sylvain | Matériel d'herboriste, outils de menuisier | 5 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Hanté | Arcanes + Survie | Deux langues, dont une exotique | — | 0 | ⚠ écart | Haunted One (Ravenloft) | Officiel : 2 compétences au choix parmi Arcanes / Investigation / Religion / Survie, 2 langues exotiques. Ici figé sur Arcanes + Survie ; or = 0. |
| Héros du peuple | Dressage + Survie | - | Outils d'artisan, véhicules terrestres | 10 | ✅ conforme | Folk Hero | Compétences, langues, outils et or conformes au PHB 2014. |
| Homme de Loi | Investigation + Perspicacité | Commun | Matériel de calligraphie, véhicules (terrestres) | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Homme-médecine | Médecine + Nature | Commun,+1 | Matériel d'herboriste | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Idiot du village | Discrétion + Représentation | Gnéééé | Le jeu du caillou | ∅ | ❓ hors catalogue | — | Langue « Gnéééé » et outil « Le jeu du caillou » : entrée humoristique, hors catalogue. |
| Initié | Investigation + Religion | Commun, +1 | Instrument de musique | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Inquisiteur | Intimidation + Religion | Commun,+1 | Matériel de calligraphie | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Itinérant | Représentation + Survie | Commun,+1 | Véhicules (terrestres) | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Journalier | Athlétisme + Survie | Commun | Véhicules (terrestres), un type d'outils | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Juriste | Histoire + Persuasion | Commun, +2 | - | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Laboureur | Athlétisme + Dressage | Commun | Véhicules (terrestres), un ensemble d'outils d'artisan au ch | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Limier | Investigation + Perspicacité | Commun | Accessoires de déguisement, outils de voleur | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Manouvrier | Athlétisme + Escamotage | Commun | Outils de menuisier | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Marin | Athlétisme + Perception | - | Outils de navigateurs, véhicules aquatiques | 10 | ✅ conforme | Sailor | Compétences, langues, outils et or conformes au PHB 2014. |
| Matelot | Acrobaties + Athlétisme | Commun | Véhicules (marins), instruments de navigation | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Médecin | Médecine + Nature | Commun | Matériel d'herboriste, matériel d'empoisonneur | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Membre de guilde | Perspicacité + Persuasion | Commun, +1 | Un ensemble d'outils d'artisan au choix | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Mendiant | Escamotage + Tromperie | Commun | Un instrument de musique, un type de jeu au choix | 5 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Mercenaire | Athlétisme + Tromperie | Commun | Véhicules (terrestres), un type de jeu au choix | 15 | ⚠ écart | ≈ Mercenary Veteran (SCAG) | Officiel : Athlétisme + **Persuasion**, 1 jeu, véhicules terrestres. Ici Athlétisme + Tromperie. |
| Militaire | Athlétisme + Intimidation | - | Véhicules (terrestres), un type de jeu au choix | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Miséreux | Discrétion + Escamotage | Commun | Un type de jeu au choix, outils de voleur | 5 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Naturaliste | Nature + Survie | Commun | Véhicules (terrestres), matériel d'herboriste | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Noble | Histoire + Persuasion | Une au choix | Un type de jeu | 25 | ✅ conforme | Noble | Compétences, langues, outils et or conformes au PHB 2014. |
| Noblesse de robe | Histoire + Perspicacité | Une au choix | Un instrument de musique au choix, un ensemble d'outils d'ar | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Noblesse d'épée | Athlétisme + Histoire | Une au choix | Véhicules (terrestres) | 20 | ⚠ écart | ≈ Knight of the Order / Chevalier (SCAG, PHB) | Officiel (Chevalier, variante de Noble) : Histoire + Persuasion. Ici Athlétisme + Histoire. |
| Officier | Athlétisme + Persuasion | Commun,+1 | Véhicules (terrestres) | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Orphelin | Discrétion + Escamotage | Commun | Un type de jeu au choix, accessoires de déguisement | 5 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Palefrenier | Dressage + Perspicacité | Commun | Véhicules (terrestres), outils de tanneur | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Patrouilleur | Perspicacité + Survie | Commun,+1 | Véhicules (terrestres) | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Pilleur de ruines | Histoire + Investigation | Commun,+1 | Outils de voleur | 15 | ⚠ écart | ≈ Archaeologist (Tomb of Annihilation) | Officiel : Histoire + Survie, outils de cartographe ou de navigateur, 1 langue. Ici Histoire + Investigation + outils de voleur. |
| Pirate | Athlétisme + Tromperie | Commun | Intrument de navigation, véhicules(marin) | 10 | ⚠ écart | Variante de Marin (PHB) | Compétences : Athlétisme + **Tromperie** ; la règle (variante Pirate) donne Athlétisme + **Perception**. |
| Précepteur | Histoire + Perspicacité | Commun,+2 | - | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Prédicateur | Religion + Représentation | Commun,+1 | Véhicules (terrestres) ou véhicules (marins) | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Primitif | Dressage + Survie | Commun,+1 | Véhicules (terrestres) ou un ensemble d'outils d'artisan | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Rebouteux | Médecine + Nature | Commun | Deux au choix parmi matériel d'herboriste, d'empoisonneur et | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Repenti | Religion + Tromperie | Commun | Accessoires de déguisement, Véhicules (terrestres) | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Sage | Arcanes + Histoire | Deux au choix | - | 10 | ✅ conforme | Sage | Compétences, langues, outils et or conformes au PHB 2014. |
| Saltimbanque | Représentation + Dressage | Commun, +1 | Un instrument de musique au choix, véhicules (terrestres) | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Sang bleu | Histoire + Persuasion | Commun,+1 | Véhicules (terrestres) | 20 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Sauvageon | Athlétisme + Survie | - | Un instrument de musique | 10 | ⚠ écart | Outlander (PHB) | Langues : « - » dans les données ; la règle donne **1 langue au choix**. Compétences, outil et or conformes. |
| Serveur | Athlétisme + Représentation | Commun,+1 | Ustensiles de cuisine | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Serviteur | Discrétion + Perspicacité | Commun,+1 | Outils de tisserand | 15 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Soldat | Athlétisme + Intimidation | - | Un type de jeu, véhicules terrestres | 10 | ✅ conforme | Soldier | Compétences, langues, outils et or conformes au PHB 2014. |
| Solitaire | Nature + Survie | Commun | Deux ensembles d'outils d'artisan au choix | ∅ | ❓ hors catalogue | — | Or non renseigné. |
| Trappeur | Discrétion + Survie | Commun | Un type de jeu, un ensemble d'outils d'artisans au choix | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Vagabond | Escamotage + Survie | Commun,+1 | Matériel d'herboriste | 5 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Villageois | Dressage + Nature | Commun | Véhicules (terrestres), un ensemble d'outils d'artisan au ch | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Voleur à la tire | Escamotage + Tromperie | Commun, argot des voleurs | Accessoires de déguisement | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |
| Voyageur | Persuasion + Survie | Deux au choix | — | 10 | ❓ hors catalogue | — | Aucun historique officiel 2014 de ce nom ou de ces valeurs (nom propre au projet ou doublon d'un historique existant). |

### Annexe B — Dons (86)

| Don (app) | Source indiquée | Prérequis | Augmentation | Statut | Équivalent officiel | Remarque |
|---|---|---|---|---|---|---|
| Acolyte de Strixhaven | Strixhaven : Un curriculum de chao | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Agent de Strixhaven | Strixhaven : Un curriculum de chao | Acolyte de Strixhaven | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Artiste prodige | Tasha's Cauldron of Everything (TC | Aucun | Dextérité ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Bénédiction du dragon | Fizban's Treasury of Dragons | Aucun | Force, Dextérité ou Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Connaisseur des plans | Tasha's Cauldron of Everything (TC | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Initié de la magie dragonne | Fizban's Treasury of Dragons | Aucun | Aucune | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Marque aberrante | Eberron : Rising from the Last War | Aucun | Intelligence, Sagesse ou Charisme +1 | ⚠ écart | Aberrant Dragonmark (Eberron) | Augmentation de caractéristique : la règle donne Constitution +1. |
| Marque de recherche | Eberron : Rising from the Last War | Humain ou autre race autorisée | Dextérité, Sagesse ou Intelligence +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Maître des ombres et de la nuit | Xanathar's Guide to Everything (XG | Aucun | Dextérité ou Sagesse +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Spécialiste des pièges | Guide de Xanathar sur le Tout | Maîtrise des outils de voleur | Dextérité ou Intelligence +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Artisan des métaux | Xanathar's Guide to Everything (XG | Maîtrise des outils de forgeron | Force ou Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Audacieux | Tasha's Cauldron of Everything (TC | Aucun | Dextérité ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Connaisseur des glyphes | Guide de l'Aventurier pour la Côte | Aucun | Intelligence +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Ensorceleur des arcanes | Tasha's Cauldron of Everything (TC | Aptitude à lancer des sorts | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Explorateur des souterrains | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Dungeon Delver | Effets principaux conformes. |
| Initié aux arts martiaux | Guide de l'Aventurier pour la Côte | Force ou Dextérité de 13 ou plus | Aucune | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Maître des bêtes | Xanathar's Guide to Everything (XG | Aucun | Sagesse +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Maître des poisons | Manuel des Joueurs (PHB) | Aucun | Aucune | ⚠ écart | Poisoner (TCE) | Source indiquée « Manuel des joueurs » ; c'est un don de **Tasha**. |
| Médium spirituel | Tasha's Cauldron of Everything (TC | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Résistant | Manuel des Joueurs (PHB) | Aucun | Augmente une caractéristique au choix de | ⚠ écart | (aucun) | **Doublon** de « Résilient » ; n'existe pas dans les livres. |
| Voyageur dimensionnel | Tasha's Cauldron of Everything (TC | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Acéré | Tasha's Cauldron of Everything (TC | Aucun | Force ou Dextérité +1 | ⚠ écart | Slasher (TCE) | **Doublon** de « Tranchant » ; effet inexact (saignement inventé). |
| Adepte de la pieuvre | Le Donjon du Mage Mad Mage / Suppl | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Adepte des ombres | Xanathar's Guide to Everything (XG | Aucun | Dextérité +1 | ⚠ écart | Shadow Touched (TCE) | Décrit le sort *Ténèbres* ; la règle donne *Invisibilité* + 1 sort de 1ᵉʳ niveau d'illusion ou nécromancie. |
| Affinité draconique | Fizban's Treasury of Dragons | Aucun | Force, Dextérité ou Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Agent secret | Guide de l'Aventurier pour la Côte | Aucun | Aucune | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Ambassadeur des profondeurs | Xanathar's Guide to Everything (XG | Gnome des profondeurs (Svirfneblin) | Dextérité ou Sagesse +1 | ⚠ écart | ≈ Svirfneblin Magic (MToF) | Source « Xanathar » erronée, augmentation de caractéristique inventée. |
| Ascendance ténébreuse | Mordenkainen présente : Les Monstr | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Bénédiction de la nature | Tasha's Cauldron of Everything (TC | Aucun | Sagesse +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Chirurgien de combat | Guide de l'Aventurier pour la Côte | Aucun | Aucune | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Connaissance ancestrale | Tasha's Cauldron of Everything (TC | Aucun | Intelligence +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Disciple des dragons | Fizban's Treasury of Dragons | Aucun | Force, Dextérité ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Émissaire des fées | The Wild Beyond the Witchlight | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Esprit affûté | Xanathar's Guide to Everything (XG | Aucun | Intelligence +1 | ⚠ écart | Keen Mind (PHB) | Source indiquée « Xanathar » ; c'est un don du **Manuel des joueurs**. |
| Explorateur robuste | Xanathar's Guide to Everything (XG | Aucun | Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Maître de la forge | Xanathar's Guide to Everything (XG | Maîtrise des outils de forgeron | Force ou Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Prodige | Xanathar's Guide to Everything (XG | Humain, Demi-elfe ou Demi-orc | Aucune | ✅ conforme | Prodigy (XGE) | Effets principaux conformes. |
| Résistance draconique | Fizban's Treasury of Dragons | Aucun | Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Vigueur surhumaine | Xanathar's Guide to Everything (XG | Aucun | Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Acteur | Manuel des Joueurs (PHB) | Aucun | Charisme +1 | ✅ conforme | Actor | Effets principaux conformes. |
| Adepte de métamagie | Tasha's Cauldron of Everything (TC | Aptitude à lancer des sorts ou magie de pacte | Aucune | ✅ conforme | Metamagic Adept (TCE) | Effets principaux conformes. |
| Adepte élémentaire | Manuel des Joueurs (PHB) | Capacité à lancer au moins un sort | Aucune | ⚠ écart | Elemental Adept (PHB) | Omet la 2ᵉ partie : les 1 aux dés de dégâts du type choisi comptent comme des 2. |
| Adepte martial | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Martial Adept | Effets principaux conformes. |
| Affamé de magie | Tasha's Cauldron of Everything (TC | Aucun | Intelligence, Sagesse ou Charisme +1 | ⚠ écart | Fey Touched (TCE) | Le 2ᵉ sort doit être de 1ᵉʳ niveau de **divination ou enchantement** (pas illusion). |
| Agilité des courts-sur-pattes | Xanathar's Guide to Everything (XG | Nain ou race de taille Petite | Force ou Dextérité +1 | ✅ conforme | Squat Nimbleness (XGE) | Effets principaux conformes. |
| Alerte | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Alert | Effets principaux conformes. |
| Amateur d'armes à feu | Tasha's Cauldron of Everything (TC | Aucun | Dextérité +1 | ✅ conforme | Gunner (TCE) | Effets principaux conformes. |
| Artisan des arcanes | Tasha's Cauldron of Everything (TC | Aucun | Aucune | ✅ conforme | Artificer Initiate (TCE) | Effets principaux conformes. |
| Athlète | Manuel des Joueurs (PHB) | Aucun | Force ou Dextérité +1 | ✅ conforme | Athlete | Effets principaux conformes. |
| Attaquant sauvage | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Savage Attacker | Effets principaux conformes. |
| Bagarreur de tavernes | Manuel des Joueurs (PHB) | Aucun | Force ou Constitution +1 | ✅ conforme | Tavern Brawler | Effets principaux conformes. |
| Briseur d'armes lourdes | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Great Weapon Master (nom français différent) | Effets principaux conformes. |
| Broyeur | Tasha's Cauldron of Everything (TC | Aucun | Force ou Constitution +1 | ✅ conforme | Crusher (TCE) | Effets principaux conformes. |
| Chance abondante | Xanathar's Guide to Everything (XG | Halfelin | Aucune | ✅ conforme | Bountiful Luck (XGE) | Effets principaux conformes. |
| Chanceux | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Lucky | Effets principaux conformes. |
| Chef cuisinier | Tasha's Cauldron of Everything (TC | Aucun | Constitution ou Sagesse +1 | ✅ conforme | Chef (TCE) | Effets principaux conformes. |
| Combattant à deux armes | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Dual Wielder | Effets principaux conformes. |
| Combattant monté | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Mounted Combatant | Effets principaux conformes. |
| Constitution infernale | Xanathar's Guide to Everything (XG | Tieffelin | Constitution +1 | ✅ conforme | Infernal Constitution (XGE) | Effets principaux conformes. |
| Dur à cuire | Manuel des Joueurs (PHB) | Aucun | Constitution +1 | ⚠ écart | Durable (PHB) | Description fausse : la règle donne Con +1 et un minimum de 2 × mod. Con aux dés de vie dépensés ; pas de dé de vie en action bonus. |
| Érudit du feu | Tasha's Cauldron of Everything (TC | Aucun | Intelligence +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Expert en arbalètes | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Crossbow Expert | Effets principaux conformes. |
| Fureur des dragons | Fizban's Treasury of Dragons | Aucun | Force, Dextérité ou Constitution +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Initié à la magie | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Magic Initiate | Effets principaux conformes. |
| Initié aux arcanes occultes | Tasha's Cauldron of Everything (TC | Aptitude à lancer des sorts ou magie de pacte | Aucune | ✅ conforme | Eldritch Adept (TCE) | Effets principaux conformes. |
| Initié au combat | Tasha's Cauldron of Everything (TC | Aptitude au combat | Aucune | ✅ conforme | Fighting Initiate (TCE) | Effets principaux conformes. |
| Inquisiteur rigoureux | Xanathar's Guide to Everything (XG | Aucun | Sagesse +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Lanceur de sorts | Manuel des Joueurs (PHB) | Capacité à lancer au moins un sort | Aucune | ✅ conforme | War Caster | Effets principaux conformes. |
| Maître d'armes | Manuel des Joueurs (PHB) | Aucun | Force ou Dextérité +1 | ✅ conforme | Weapon Master | Effets principaux conformes. |
| Maître des armes d'hast | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Polearm Master | Effets principaux conformes. |
| Maître des armures intermédiaires | Manuel des Joueurs (PHB) | Maîtrise des armures intermédiaires | Force ou Dextérité +1 | ⚠ écart | Medium Armor Master (PHB) | Ajoute un +1 Force/Dextérité qui n'existe pas (la règle n'a **aucune** augmentation de caractéristique). |
| Maître des armures lourdes | Manuel des Joueurs (PHB) | Maîtrise des armures lourdes | Force +1 | ⚠ écart | Heavy Armor Master (PHB) | Texte sans la condition « tant que vous portez une armure lourde ». |
| Maître des boucliers | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Shield Master | Effets principaux conformes. |
| Mobile | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Mobile | Effets principaux conformes. |
| Observateur | Manuel des Joueurs (PHB) | Aucun | Intelligence ou Sagesse +1 | ✅ conforme | Observant | Effets principaux conformes. |
| Perceptif | Tasha's Cauldron of Everything (TC | Aucun | Intelligence, Sagesse ou Charisme +1 | ❓ non rattaché | — | Aucun don de ce nom ou de cet effet dans le PHB, XGE ou TCE (supplément récent, don mal nommé ou invention) : à vérifier dans le livre. |
| Perçant | Tasha's Cauldron of Everything (TC | Aucun | Force ou Dextérité +1 | ⚠ écart | Piercer (TCE) | Effet de critique inexact (la règle : un dé de dégâts supplémentaire sur un critique perforant). |
| Percheur | Xanathar's Guide to Everything (XG | Aptitude à lancer des sorts | Intelligence ou Sagesse +1 | ⚠ écart | ≈ Spell Sniper (PHB) | Description sans rapport avec Spell Sniper (portée doublée, ignorer l'abri, sort mineur d'attaque). |
| Prodigieusement doué | Xanathar's Guide to Everything (XG | Humain | Augmente deux caractéristiques différent | ⚠ écart | Skill Expert (TCE) | Prérequis « Humain » inventé ; Skill Expert : +1 à une caractéristique, 1 compétence, 1 expertise, sans prérequis. |
| Résilient | Manuel des Joueurs (PHB) | Aucun | Augmente une caractéristique de +1 | ✅ conforme | Resilient | Effets principaux conformes. |
| Ritualiste | Manuel des Joueurs (PHB) | Intelligence ou Sagesse de 13 ou plus | Aucune | ✅ conforme | Ritual Caster | Effets principaux conformes. |
| Robuste | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Tough | Effets principaux conformes. |
| Télékinésiste | Tasha's Cauldron of Everything (TC | Aucun | Intelligence, Sagesse ou Charisme +1 | ✅ conforme | Telekinetic (TCE) | Effets principaux conformes. |
| Télépathe | Tasha's Cauldron of Everything (TC | Aucun | Intelligence, Sagesse ou Charisme +1 | ✅ conforme | Telepathic (TCE) | Effets principaux conformes. |
| Tireur d'élite | Manuel des Joueurs (PHB) | Aucun | Aucune | ✅ conforme | Sharpshooter | Effets principaux conformes. |
| Tranchant | Tasha's Cauldron of Everything (TC | Aucun | Force ou Dextérité +1 | ⚠ écart | Slasher (TCE) | Relance de dés inventée ; manque le désavantage aux attaques de la cible sur un critique tranchant. |

### Annexe C — Espèces (70)

| Espèce (app) | Source indiquée | Bonus de caractéristiques | Statut | Aptitudes |
|---|---|---|---|---|
| Aarakocra | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 3 |
| Aasimar protecteur | Guide de Volo | Cha +2, Sag +1 | 🟢 2014-époque (supplément officiel) | 6 |
| Aasimar déchu | Guide de Volo | Cha +2, For +1 | 🟢 2014-époque (supplément officiel) | 6 |
| Autognome | Spelljammer | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 7 |
| Centaure | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Changelin | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 3 |
| Conil | Création de la communauté | +2, +1 (ou +1, +1, +1) | 🔴 non officiel / à vérifier | 5 |
| Drakéide | Manuel des Joueurs | For +2, Cha +1 | 🟢 2014 (PHB) | 3 |
| Dhampir | Guide de Ravenloft | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 5 |
| Duergar | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Eladrin | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 6 |
| Elfe des mers | Monstres du Multivers | +2, +1 | 🟠 version 2022 (MotM) | 7 |
| Elfe astral | Spelljammer | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 6 |
| Fadette | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 3 |
| Féral | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Firbolg | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Forgelier | Eberron | Con +2, +1 | 🟢 2014-époque (supplément officiel) | 6 |
| Genasi d'air | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Genasi d'eau | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Genasi de feu | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Genasi de terre | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Giff | Spelljammer | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 4 |
| Githyanki | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 3 |
| Githzerai | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 3 |
| Gobelin | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Gobelours | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 6 |
| Goliath | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Gnome des forêts | Manuel des Joueurs | Int +2, Dex +1 | 🟢 2014 (PHB) | 5 |
| Gnome des profondeurs | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Gnome des roches | Manuel des Joueurs | Int +2, Con +1 | 🟢 2014 (PHB) | 5 |
| Grung | One Grung Above (DMs Guild, WotC) | Dex +2, Con +1 | 🟢 2014-époque (supplément officiel) | 8 |
| Hadozi | Spelljammer | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 5 |
| Halfelin Pied-léger | Manuel des Joueurs | Dex +2, Cha +1 | 🟢 2014 (PHB) | 5 |
| Halfelin robuste | Manuel des Joueurs | Dex +2, Con +1 | 🟢 2014 (PHB) | 5 |
| Hobgobelin | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Homme lézard | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 6 |
| Humain | Manuel des Joueurs | Toutes +1 | 🟢 2014 (PHB) | 2 |
| Humain variant | Manuel des Joueurs | +1, +1 | 🟢 2014 (PHB) | 3 |
| Hybride Simic | Ravnica | Con +2, +1 | 🟢 2014-époque (supplément officiel) | 3 |
| Kalashtar | Eberron | Sag +2, Cha +1 | 🟢 2014-époque (supplément officiel) | 4 |
| Kender | Dragonlance | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 4 |
| Kenku | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Kobold | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Léonin | Theros | Con +2, For +1 | 🟢 2014-époque (supplément officiel) | 4 |
| Locathah | L'Aube des Locathahs | For +2, Dex +1 | 🟢 2014-époque (supplément officiel) | 5 |
| Loxodon | Ravnica | Con +2, Sag +1 | 🟢 2014-époque (supplément officiel) | 5 |
| Minotaure | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Nain des collines | Manuel des Joueurs | Con +2, Sag +1 | 🟢 2014 (PHB) | 7 |
| Nain des montagnes | Manuel des Joueurs | Con +2, For +2 | 🟢 2014 (PHB) | 7 |
| Orc | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 4 |
| Owlin | Strixhaven | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 4 |
| Plasmoïde | Spelljammer | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 6 |
| Sang-Maudit | Guide de Ravenloft | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 5 |
| Satyre | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Shadar-kai | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 6 |
| Tabaxi | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Thri-kreen | Spelljammer | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 6 |
| Tieffelin | Manuel des Joueurs | Cha +2, Int +1 | 🟢 2014 (PHB) | 3 |
| Tieffelin féral | Guide de l'Aventurier pour la Côte des É | Dex +2, Int +1 | 🟢 2014-époque (supplément officiel) | 3 |
| Tortle | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 6 |
| Triton | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Vedalken | Ravnica | Int +2, Sag +1 | 🟢 2014-époque (supplément officiel) | 3 |
| Verdan | Acquisitions Incorporées | Cha +2, Con +1 | 🟢 2014-époque (supplément officiel) | 5 |
| Yuan-ti | Monstres du Multivers | +2, +1 (ou +1, +1, +1) | 🟠 version 2022 (MotM) | 5 |
| Revenant | Guide de Ravenloft | +2, +1 (ou +1, +1, +1) | 🟠 2021-22, bonus libres | 3 |
| Kitsune | Favori de la communauté | Dex +2, Cha +1 | 🔴 non officiel / à vérifier | 4 |
| Myconide éveillé | Favori de la communauté | Con +2, Sag +1 | 🔴 non officiel / à vérifier | 3 |
| Demi-elfe | Manuel des Joueurs | Cha +2, +1, +1 | 🟢 2014 (PHB) | 5 |
| Drow (Elfe noir) | Manuel des Joueurs | Dex +2, Cha +1 | 🟢 2014 (PHB) | 8 |
| Elfe | Manuel des Joueurs | Dex +2 | 🟢 2014 (PHB) | 5 |

---

_Audit réalisé avec Claude Code sur la version 51 de l'application (voir les dates de commit du dépôt). Aucun fichier de données ni de code n'a été modifié._
