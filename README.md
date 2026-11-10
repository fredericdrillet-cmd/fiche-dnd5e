# Fiche de personnage & générateur D&D 5e (PyQt6) — version 2

> **Version web mobile** : voir [README_WEB.md](README_WEB.md) (lancement `python app.py`, déploiement Render, commandes Git).

## Lancer l'application
```bash
python -m venv .venv && source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements-desktop.txt                  # installe PyQt6 (version web : voir README_WEB.md)
python main.py
```
Python 3.10+ requis. `python main.py --check` vérifie le chargement des JSON sans ouvrir l'interface.
Tests : `python -m unittest discover tests` (112 tests : règles, données, thèmes WCAG, interface simulée).

## Architecture
```
main.py            point d'entrée
core/              logique métier — AUCUNE dépendance à l'interface
  rules.py           règles D&D 5e pures (modificateurs, achat de points, emplacements, vitesse en cases…)
  data_loader.py     lecture / réparation / croisement de tous les JSON
  character.py       modèle du personnage + sauvegarde JSON
  engine.py          calculs (PV, CA, compétences, armes, sorts, dons, inventaire…)
  settings.py        préférences (thème, taille du texte) dans ~/.dnd5e_fiche/settings.json
ui/                interface PyQt6 — un fichier par onglet
  theme.py           3 thèmes + audit de contraste WCAG        options_dialog.py   fenêtre Options
  main_window.py     en-tête, menus, import/export             common.py           tableaux & cases centrés
data/              base de données JSON (modifiable)
tools/             générateurs (listes de classes des sorts, etc.)
```

## Données JSON (dossier `data/`)
Les fichiers sont reconnus par leur **contenu** (nom libre) : classes, `Classes_Depart`, `Races`, `Historiques`,
`Compétences`, `Outils`, `Armes`, `Armures`, `Dons`, `Equipement`, `Langues`, `Magie-0…9`.
Ajoutés par moi : `Sorts_Listes.json` (classes ayant accès à chaque sort — vos Magie-N n'en contiennent pas) et
`Bonus_Raciaux.json` (bonus de caractéristiques, vitesses, sous-races). Modifiez-les librement.
Un JSON avec une virgule manquante entre deux objets (cas de `Dons.json`) est réparé automatiquement et signalé
dans Aide > À propos.

## Fonctionnalités récentes
- **Histoire & Portrait (RP)** : backstory, portrait importé (enregistré dans la sauvegarde JSON), notes de campagne.
- **Style de combat** (onglet Combat) : un sélecteur par style accordé (Guerrier niv. 1, Paladin/Rôdeur niv. 2,
  Champion niv. 10 pour le second), grisé tant que le niveau n'est pas atteint ; effets appliqués (Défense, Archerie, Duelliste).
  Les styles sont dans `data/Style_de_combat.json` (modifiable).
- **CA** : affichée sous forme de formule (`CA = 12 + Dex (max 2) + 2 (bouclier)`) puis calcul chiffré.
- **Point Buy** : boutons − / +, coût officiel (8=0 … 15=9), 27 points, bouton « Réinitialiser (8 partout) ».

## Thèmes — dix univers de jeux vidéo (Options > Préférences, liste déroulante en haut à droite, ou menu Options)
Porte de Baldur (BG3, **par défaut**) · The Witcher 3 · Skyrim · Dark Souls / Elden Ring · Diablo IV · Cyberpunk 2077 ·
Final Fantasy (Crystal Era) · Hollow Knight · Mass Effect · Zelda / RPG japonais.
Chaque thème = palette + typographie + style de cadre (ridge, double, biseauté…) + texture procédurale (grain de cuir,
runes, braises, lignes de balayage, grille holographique…) + dégradés `qlineargradient`. Équivalent des « variables CSS » :
toutes les couleurs sont des champs de `Theme` injectés dans une feuille de style unique (`ui/theme.py`).
Contrastes audités (WCAG AA ≥ 4,5:1) sur les deux extrémités des dégradés et texture à pleine intensité.
Pour ajouter un thème : copier une entrée de `THEMES` ; `python -m unittest discover tests` vérifie ses contrastes.

## Manifestations occultes
Sous-onglet « Manifestations occultes » de l'onglet Magie : sources = Occultiste (niveau) + dons « Initié aux arcanes
occultes ». Prérequis (pacte, niveau) vérifiés ; les manifestations qui accordent un sort (à volonté ou gratuit)
l'injectent dans le tableau « Sorts accordés » avec leur source. Données : `data/Manifestations_occultes.json`.

## Compteurs à sphères et objets magiques
- **Sphères interactives** (`ui/orbs.py`) : un seul composant pour la rage (Barbare), le ki (Moine, onglet Combat),
  les emplacements de sorts et de Pacte et les points de sorcellerie (onglet Magie). Sphère pleine = disponible ;
  un clic sur une sphère pleine la dépense, un clic sur une vide la récupère (molette et flèches aussi).
  Repos court : ki et Pacte ; repos long : tout. Les points de sorcellerie n'apparaissent que pour l'Ensorceleur
  (niveau 2+) ou avec un don de métamagie.
- **Objets magiques** (Inventaire > « Équipement & objets magiques ») : catalogue `data/objets_magiques.json`
  (filtres type, rareté, harmonisation), choix du bonus des objets « +1, +2 ou +3 », case « équipé », badge
  d'harmonisation (3 objets, 4 à 6 pour l'Artificier), prérequis vérifiés. Bonus de CA et de jets de sauvegarde
  appliqués automatiquement quand l'objet est équipé (et harmonisé s'il l'exige).

## Nouveautés v6

- **Compétences** : toute la ligne est cliquable (clic n'importe où = maîtrise, colonne « Expertise » = expertise) ; idem pour les sauvegardes, la préparation des sorts et l'équipement des objets magiques (cases dessinées, sans widgets).
- **Sorts raciaux** : section dédiée de l'onglet Magie, visible même pour une classe non lanceuse (Tieffelin, Drow, Gnome des forêts…), avec niveau d'obtention, utilisation (à volonté / 1 fois par repos long) et DD/attaque calculés avec la caractéristique de l'espèce.
- **Encombrement** (Inventaire) : capacité = Force × 7,5 kg (× 2 pour Puissante carrure), barre de charge et alerte visuelle ; case « Possède un Sac sans fond » qui lève la limite.
- **Onglets déplaçables** : glissez-déposez les onglets principaux ; l'ordre est mémorisé (menu Affichage > Réinitialiser l'ordre des onglets).
- **Forme sauvage** (onglet visible seulement pour un Druide) : sphères d'utilisations, bestiaire `monsters_db.json` filtré selon le niveau, le FP, le vol et la nage (Cercle de la Lune géré), liste à gauche, statblock complet à droite, bouton « Adopter cette forme ».
- **Performances** : seul l'onglet affiché est recalculé, calculs mis en cache pendant un rafraîchissement, clics sur les sphères traités sans reconstruire la fiche, sprites des sphères en cache.
- **Objets à paliers** séparés (`tools/split_magic_items.py`) : Potion de guérison / majeure / supérieure / suprême, forces de géant, parchemins par niveau, armes et armures +1/+2/+3…
- **Formules évaluées** (`core/formulas.py`) : « 1d10 + votre modificateur de Constitution » s'affiche « 1d10 + 3 (modificateur de Constitution) » ; DD et totaux calculés.
- **Textes de classe enrichis** (`tools/class_texts/<classe>.py`, appliqués par `python tools/apply_class_texts.py`) : descriptions paraphrasées et complètes des aptitudes officielles (PHB, Xanathar, Tasha) ; sous-classes communautaires réécrites avec des chiffres précis et équilibrés (ex. Pancratiaste : mains nues 1d6 puis 1d8 au niveau 10, Projection dévastatrice 2d8 + Force ; Chevalier de sang : dés de vie dépensés en dégâts nécrotiques, Armure de sang = niveau de guerrier + Constitution). Libellé unifié « Amélioration de caractéristique ou choix d'un don ».
- **Audit de conformité** : `AUDIT_REGLES.md` (régénéré par `python tools/audit_regles.py`) liste, sans rien modifier, les écarts des données de classes et d'espèces vs les règles officielles 5e.

## Nouveautés v7 (inspirées de Baldur's Gate 3 / Solasta)

- **Compétences d'arme** (`core/weapon_actions.py`) : à côté des dégâts de chaque arme (onglet Combat, et encart « Armes et compétences d'arme » de l'Inventaire), pastilles des bottes d'arme (PHB 2024) et des actions façon BG3 (Frappe du pommeau, Lacération, Perçage, Fauchage, Tir handicapant…). Survol = infobulle immédiate : type d'action, recharge, JS et **DD calculé** (8 + maîtrise + mod. d'attaque), effet en cas de réussite / d'échec.
- **Barre d'états actifs** (`core/effects.py`, plus de 120 effets) : buffs de sorts, débuffs, les 15 états du PHB, épuisement 1-6, états d'immersion (Alcoolisé, Saignement, En feu…), auras et aptitudes de classe. Ajout illimité depuis un sélecteur (catégorie + recherche), icônes dessinées par catégorie, survol = règles détaillées, clic = retrait. Les modificateurs chiffrés s'appliquent (CA, vitesse) et un récapitulatif rappelle les autres (avantages, résistances…).
- **Munitions** : pour une arme à distance, choix de la munition parmi celles de l'inventaire (munitions ordinaires, billes, « Munition +1 », flèches magiques…) ; le bonus magique s'ajoute à l'attaque et aux dégâts, le bouton « 🏹 Tirer » décompte le stock. Les munitions magiques ajoutées depuis le catalogue arrivent dans l'inventaire par lots de 10.
- **Repos interactifs** : fenêtre de repos court (1 heure : dés de vie dépensés un à un, PV mis à jour en direct, aptitudes rechargées) et long (8 heures : tout ce qui est restauré, épuisement -1, règle « un repos long par 24 h »). Horloge de jeu (« Jour 2, 16 h 00 »). Règle de survie optionnelle (Options) : un repos long consomme une ration.
- **Concentration** : lancer un sort (bouton « ✨ Lancer » ou double-clic) dépense le plus petit emplacement disponible ; un sort de concentration est signalé (🧠, bandeau dans Magie et Combat) et lancer un autre sort de concentration ouvre une confirmation avant de rompre le précédent.
- **Réactions** : encart dans Combat avec l'attaque d'opportunité, les sorts de réaction appris/préparés (Bouclier, Contresort…), les aptitudes (Parade de projectiles, Esquive instinctive, Égide projetée…), les dons et styles ; pastille Disponible / Utilisée, bouton « Nouveau round ».
- **Données corrigées** d'après l'audit : `python tools/apply_corrections.py` (idempotent) applique `tools/class_fixes/`, `tools/class_texts/` et `tools/race_fixes/` (noms et niveaux officiels, aptitudes manquantes, options de Tasha, listes de sorts, sources, bonus raciaux, traits). `AUDIT_REGLES.md` contient maintenant le journal des corrections et les écarts restants volontairement non corrigés.
- **Formules affichées en valeurs** : « 1d10 + 3 (mod. Constitution) », « DD = 8 + 3 (maîtrise) + 2 (mod. Constitution) = 13 », « votre niveau de personnage (7) » pour les traits raciaux.
- **Cercle de la Terre** : sélecteur « 🌍 Terrain du cercle » dans l'onglet Classes, affiché uniquement pour cette sous-classe (Arctique, Côte, Désert, Forêt, Marais, Montagne, Outreterre, Prairie). Les sorts de cercle (2 par palier aux niveaux de druide 3, 5, 7 et 9) suivent le terrain choisi et sont ajoutés automatiquement à l'onglet Magie ; le terrain est enregistré avec la fiche.

## Nouveautés v8 (finitions « AAA »)

- **Onglet conservé** : changer de classe (ex. passer en Druide) ne fait plus sauter l'affichage vers un autre onglet ; l'onglet « Forme sauvage » est simplement affiché / masqué, sans reconstruire la barre (ordre personnalisé respecté).
- **Combat épuré et réordonné** : PV (sans mode « fixe / jets » ni bouton de lancer de dés de vie : PV moyens fixes, dés de vie dépensés en repos court) avec Classe d'armure et Style de combat → statistiques (Initiative, Vitesse, Maîtrise, Perception passive) → ressources de classe → réactions → effets actifs et concentration → armes CaC puis à distance → sorts mineurs.
- **Ressources ↔ états** : dépenser une Rage active l'état « Rage » (la récupérer le retire) ; adopter une Forme sauvage active l'état correspondant, qui disparaît à la fin de la forme (retirer l'état met fin à la forme).
- **Effets qui modifient la fiche** : Rage = bonus de dégâts (+2/+3/+4 selon le niveau) aux attaques de Force au corps à corps ; Armure du mage = CA de base 13 + Dex sans armure ; Chant de la lame = + modificateur d'Intelligence (min. +1) à la CA sans armure intermédiaire / lourde ni bouclier ; Peau d'écorce = CA minimale 16.
- **Onglet Magie restructuré** : colonne « Emplacements de sorts » plus étroite (et défilante), bibliothèque au centre, à droite des sections empilées et redimensionnables (sorts du personnage, sorts raciaux, sorts accordés, détail), chacune avec sa propre barre de défilement fluide (défilement au pixel).
- **Caractéristiques, Compétences** : une seule vue défilante, caractéristiques (achat de points, 4d6, manuel) en haut, compétences et jets de sauvegarde juste en dessous.
- **Progression, Dons** : rendu ~50 fois plus rapide (infobulles et catalogue mis en cache), dons triés par ordre alphabétique strict.
- **Libellés** : plus de caractère « & » dans les titres d'onglets (Qt l'affichait comme un « _ ») : « Race, Historique, Langues », « Progression, Dons »…

## Nouveautés v9 (effets dynamiques, potions, résistances)

- **Modificateurs appliqués à toute la fiche** (`core/mechanics.py`) : chaque état, sort, potion ou objet équipé modifie en temps réel la CA, les caractéristiques, les jets d'attaque, les jets de sauvegarde, les compétences et la vitesse (ex. Passage sans trace : +10 en Discrétion ; Bénédiction : +1d4 aux attaques et JS ; Empoisonné : désavantage aux attaques et tests ; Paralysé : échec automatique aux JS de Force et Dextérité ; Hâte : +2 CA, vitesse ×2, avantage aux JS de Dextérité ; Aide : +5 PV max ; Épuisement 4 : PV max ÷ 2).
- **Avantage / désavantage visibles** : colonne « Av. / Désav. » dans les compétences et les jets de sauvegarde (▲ Avantage, ▼ Désavantage, ✖ Échec auto), ▲/▼ sur les jets d'attaque et l'initiative. Armure lourde → désavantage en Discrétion ; armure non maîtrisée → désavantage aux tests, JS et attaques de Force / Dextérité ; Agrandissement → avantage en Force et Athlétisme. Avantage et désavantage s'annulent (PHB).
- **Infobulles de calcul « style Pathfinder »** (fond opaque) : CA, initiative, vitesse, perception passive, caractéristiques, compétences, sauvegardes et attaques détaillent chaque source (« Modificateur de Dextérité +3 · Maîtrise +2 · Passage sans trace +10 = +15 »).
- **Objets équipés** : ceinturons de force de géant, gantelets de puissance d'ogre, bandeau d'intelligence, amulette de santé, ceinturon des nains, bottes et cape elfiques, pierres de Ioun de caractéristique (harmonisation respectée).
- **Potions utilisables** (« 🧪 Utiliser / boire » dans l'Inventaire et le panneau des objets magiques) : soins (2d4+2 → 10d4+20), force de géant (Force 21 à 29), vitesse (effet de Hâte), vitalité / élixir de santé (purge du poison, des maladies, de l'épuisement), antitoxine, héroïsme, résistance (type au choix), invisibilité, vol, agrandissement, diminution, escalade, forme gazeuse, invulnérabilité… L'objet est consommé et l'état apparaît dans la barre.
- **Résistances et immunités** : 13 types de dégâts × résistance / immunité dans la bibliothèque ; les traits raciaux (Tieffelin : feu, Nain : poison…) et d'aptitudes de classe (Pureté du corps, Âme de la forge, auras du paladin…) s'affichent en permanence (🔒) ; les retirer demande confirmation (Oui / Non). Récapitulatif des résistances et immunités sous la barre d'états.
- **Repos** : les effets temporaires expirent automatiquement (repos court : effets d'une heure au plus, rage, potions ; repos long : tous les effets temporaires), la fenêtre de repos les liste ; les traits permanents sont conservés. Bouton « 🧹 Retirer les effets temporaires ».
- **Magie** : case « Sorts préparés seulement » pour filtrer la liste des sorts du personnage.

## Nouveautés v10 — lancer de d20 animé (style Baldur's Gate 3)

- **Déclencheurs** : petite icône de d20 (couleur du thème) à côté de chaque caractéristique (colonne « Test »), de chaque compétence et jet de sauvegarde (colonne « Jet »), de chaque arme (onglet Combat), des sorts mineurs d'attaque et, dans l'onglet Magie, bouton « 🎲 Jet d'attaque » pour les sorts marqués 🎲.
- **Fenêtre de lancer** (`ui/dice_dialog.py`) : fond flouté semi-transparent, grand d20 dessiné aux couleurs du thème actif, chiffre qui défile pendant 2 secondes en ralentissant (et le dé qui tourne), puis se fige. 20 naturel = vert vif + halo, 1 naturel = rouge vif (résultat brut uniquement).
- **Bonus et malus** : listés dès l'ouverture avec leur provenance (« +3 (Modificateur de Force) », « +10 (Passage sans trace) », « Désavantage — Armure : Harnois »…), ils ne s'appliquent au total qu'une fois le d20 figé, un par un. Avantage / désavantage : deux d20 côte à côte, chacun avec sa propre animation ; une fois figés, le dé retenu (le meilleur avec avantage, le moins bon avec désavantage) est entouré d'un anneau doré « ✔ Retenu », l'autre est grisé et barré « ✖ Écarté » ; les deux s'annulent (PHB).
- **Contrôle** : bouton « Continuer » (activé une fois le total affiché) et « Passer l'animation ». Animation pilotée par un QTimer (~60 images/s), sans bloquer l'interface. Le tirage est logique pure dans `core/dice.py` (testable).

## Nouveautés v11

- **Concentration** : icône 🧠 « Concentration (nom du sort) » dans la barre d'états (clic = rompre), bandeau en haut de l'onglet Magie avec bouton « Rompre la concentration », 🧠 sur la ligne du sort (sorts de classe, raciaux, accordés). Un repos court ou long met fin à la concentration (listée dans la fenêtre de repos).
- **Ascendance draconique** : encart « Capacités de combat raciales et de lignage » sous les sorts mineurs (onglet Combat), visible seulement si la race a des capacités de combat (armes naturelles, souffle, réactions chiffrées) ou pour un Ensorceleur de lignée draconique. Choix de la couleur du dragon : le souffle est recalculé (type de dégâts, ligne de 1,50 × 9 m ou cône de 4,50 m, JS de Dextérité ou de Constitution, DD 8 + maîtrise + Con, 2d6 → 5d6), sphère d'utilisation (recharge au repos court) et Résistance draconique ajoutée comme trait permanent 🔒. Lignée de l'Ensorceleur : type de l'Affinité élémentaire (+ Charisme aux dégâts au niveau 6).
- **Sorts accordés par le MJ** : bouton « ＋ Ajouter un sort (Accordé par le MJ) » dans la section « Sorts accordés » (avec les manifestations occultes) : sort de la bibliothèque ou nom libre, utilisation (à volonté, 1/repos long, avec vos emplacements…) et note narrative ; filtre par source, bouton « Retirer », lançable par double-clic, pris en compte dans les réactions.

## Nouveautés v12 — Forme sauvage complète

- **Bannière persistante** en haut de la fiche (« 🐾 Forme active : Ours brun — PV de la bête 34 / 34 — CA 11 ») avec bouton « ✕ Reprendre sa forme normale » ; la forme prend aussi fin au repos court ou long et quand les PV de la bête tombent à 0. Les statistiques du druide sont alors restaurées.
- **Substitution officielle** : Force, Dextérité et Constitution de la bête ; Intelligence, Sagesse, Charisme, maîtrises (JS, compétences) du druide conservées ; compétence : le meilleur bonus entre la bête et le druide ; CA et vitesse de la bête.
- **PV tampon** : la bête a ses propres PV ; les dégâts excédentaires à 0 PV sont reportés sur les PV normaux du druide (onglet Combat : « 💥 Subir ces dégâts »).
- **Combat** : armes et sorts mineurs masqués, remplacés par les attaques de la bête (bonus, dégâts, portée) avec lancer de d20 animé utilisant la FOR/DEX et la maîtrise (selon le FP) de la créature.
- **Magie** : sorts grisés et lancement refusé sous forme sauvage (avant le niveau 18) ; la concentration en cours est maintenue.
- **Cercle de la Lune** : « 🌙 Soin du Cercle de la Lune (action bonus) » : un emplacement de niveau N rend Nd8 PV à la bête.

## Nouveautés v13 — sort Métamorphose (sur soi)

- **Déclenchement** : lancer « Métamorphose » depuis l'onglet Magie (bouton « Lancer » / double-clic) ou ajouter l'état « Métamorphose » dans la barre d'états ouvre le même tableau de bêtes que la Forme sauvage (liste filtrable + statblock) ; bêtes de FP ≤ niveau du personnage.
- **Concentration** : le sort dépense un emplacement de niveau 4+ et prend la concentration (toute autre concentration est rompue, avec confirmation) ; à chaque dégât subi, rappel du JS de Constitution (DD 10 ou moitié des dégâts) ; rompre la concentration met fin à la transformation.
- **Règles du sort** : les 6 caractéristiques (y compris INT, SAG, CHA) et les PV sont ceux de la bête, les maîtrises du personnage ne s'appliquent plus ; sorts indisponibles. PV tampon, report des dégâts excédentaires sur les PV normaux (inconscience à 0).
- **Interface** : bannière « 🦋 État actif : Métamorphose (Ours brun) » avec « ✕ Mettre fin à la Métamorphose » ; onglet Combat avec les attaques de la bête (dés animés, modificateurs de la créature) ; fin aussi au repos court ou long.

## Nouveautés v14 — sorts de buff intelligents (style BG3)

- **Double-clic sur un sort de buff** (Hâte, Bénédiction, Bouclier de la foi, Agrandissement, Aide, Héroïsme, Peau d'écorce, Amélioration de caractéristique…) : sort personnel ou de zone centrée sur vous (Bouclier, Flou, Passage sans trace, Esprits gardiens…) → appliqué d'office ; sinon fenêtre « Cible du sort : Sur soi / Sur un allié / autre » ; choix de la variante si le sort en a plusieurs.
- **Emplacements** : niveau exact en priorité ; s'il est épuisé, proposition d'utiliser un emplacement de niveau supérieur (ou de Pacte) ; déduction immédiate du compteur.
- **Sur soi** : l'effet entre dans les états actifs et ses bonus s'appliquent à la fiche (Hâte : +2 CA, vitesse ×2, avantage aux JS de Dextérité ; Bénédiction : +1d4 aux attaques et JS…). **Sur un allié** : emplacement dépensé, concentration suivie, aucun bonus sur votre fiche.
- **Concentration** : indicateur actif dans tous les cas (« sur un allié » / « sur vous ») ; quand elle cesse, l'effet lié est retiré (fin de Hâte : Léthargie).

## Nouveautés v15 — transformations strictes à l'écran

- **En-tête (en haut à droite)** : sous Forme sauvage ou Métamorphose, les badges PV et CA affichent ceux de la bête, précédés de l'icône 🐺 (🦋 pour Métamorphose) ; survol : « État actif : Forme Sauvage - Ours brun ». Les PV du personnage sont masqués et réapparaissent à la fin.
- **Icône animale** sur tout ce qui est remplacé : PV et CA de l'onglet Combat, FOR / DEX / CON (et INT / SAG / CHA sous Métamorphose) dans l'onglet Caractéristiques, avec infobulle.
- **Onglet Combat** : encart « 🐺 Attaques de la bête » placé entre les armes de corps à corps et les armes à distance, visible uniquement pendant la transformation ; armes et sorts mineurs grisés « indisponible sous forme animale ». Le champ PV agit sur les PV de la bête.
- **Onglet Magie** entièrement grisé avec le message « Magie indisponible sous cette forme » (concentration maintenue et rappelée).
- **Fin** (bouton, repos, PV de la bête à 0) : PV, CA, caractéristiques, magie et encarts reviennent à l'état d'origine (moins les dégâts excédentaires).

## Nouveautés v16 — finitions d'interface
- **Formes sauvages** : plus aucune mention « valeurs estimées / statblock incomplet » (attaques et jets de dés).
- **Sous-classe** : la note « (choix au niveau N) » occupe une largeur réservée en permanence — rien ne se décale.
- **Barre d'état** : « ✔ Fiche cohérente » légèrement décalée vers la gauche.
- **Alignements** : boutons d20 à taille fixe, centrés dans leur colonne « Jet » et gardant leur place quand ils sont masqués (sorts mineurs sans jet d'attaque, armes, attaques de bête).
- **Caractéristiques** : six cartes côte à côte (FOR, DEX, CON, INT, SAG, CHA) — valeur finale, modificateur en pastille, dé de test, valeur de base (achat de points / tirage / saisie), coût, et bonus Race | Amél. | Divers alignés sur une ligne.
- **Magie — tableau de bord en 3 colonnes** : à gauche les emplacements (compteur de sorts mineurs à volonté, niveaux 1 à 9, pacte, repos) ; au centre la liste des sorts groupée par niveau (titres « Sorts mineurs », « Niveau 1 »…) avec une colonne **Statut** (✔ Préparé, Ⓒ Concentration, 🧠 Concentration active, 🎲 Attaque, 🔒 Indisponible sous forme animale) et la bibliothèque dans un second onglet ; à droite le détail du sort (temps d'incantation, portée, composantes, durée, description) et les boutons Lancer / Jet d'attaque (double-clic = lancer).

## Nouveautés v17 — ergonomie
- **Magie** : sphères d'emplacements plus petites (14 px), colonne de gauche plus étroite ; boutons Repos court / long retirés (toujours disponibles dans l'onglet Combat).
- **Combat** : encarts Armes CaC, Armes à distance et Sorts mineurs à hauteur adaptative — vides, ils ne montrent qu'un sélecteur (sans en-têtes) ; chaque arme / sort ajouté fait apparaître sa ligne complète et une nouvelle ligne de choix.
- **Bibliothèque de sorts** : recherche instantanée sans accents ni majuscules, filtre par école, pastilles de niveau en un clic (Tous, Mineurs, 1 à 9 selon votre niveau max), option « Masquer mes sorts », compteur de résultats, et rappel du quota en tête (« Sorts mineurs : x / y · Sorts connus : x / y (reste n) », en rouge si dépassé).
- **Dons** : colonne « Source » retirée du catalogue (la source reste dans le détail du don et dans la recherche).

## Nouveautés v18 — sortie, performances, sauvegarde
- **Modale de sortie** (fermeture, Nouveau, Ouvrir) quand des modifications ne sont pas enregistrées : « Des modifications n'ont pas été enregistrées. » avec **[Enregistrer]** (sauvegarde puis continue ; si « Enregistrer sous » est annulé, on reste sur la fiche) · **[Ne pas enregistrer et quitter]** · **[Annuler]** (ou Échap).
- **Ajout / retrait de sorts instantané** : plus de recalcul global de la fiche ; seuls la liste « Mes sorts », la ligne concernée de la bibliothèque (✔ + vert) et les compteurs sont mis à jour, les autres onglets étant recalculés à leur ouverture (~25× moins de travail mesuré).
- **Boutons contextuels** : « Lancer le sort », « Jet d'attaque » et « Retirer » sont désactivés dans la Bibliothèque et ne s'activent que dans « Mes sorts » (sur un sort sélectionné, hors forme animale).
- **Intégrité de la sauvegarde** : tout l'état vit dans le modèle `Character` et est écrit dans le JSON (forme sauvage / Métamorphose et PV de la bête, concentration et sa cible, effets actifs et potions, emplacements dépensés y compris surclassés, pacte, ressources, sorts par classe et préparation, sorts du MJ, munitions, objets magiques, temps de jeu, réaction, jets contre la mort…). Tests d'aller-retour enregistrer → rouvrir vérifiant une égalité champ par champ.

## Nouveautés v19 — actions de classe, dés de dégâts, bibliothèque légale
- **Actions & capacités de classe** (onglet Combat, encart au-dessus des armes de corps à corps, visible seulement si la classe en possède) : données dans `data/Actions_Classes.json` (éditable : classe, sous-classe, niveau, type, coût, jet, formule, état appliqué) — Rage / Attaque téméraire (Barbare), Frappe à mains nues / Déluge de coups / Défense patiente / Pas du vent / Coup étourdissant (Moine), Second souffle / Sursaut d'activité / Manœuvres (Maître de guerre, 16 manœuvres), Sens divin / Châtiment divin / Conduit divin (Paladin), Renvoi des morts-vivants / Conduit divin (Clerc), Attaque sournoise / Action astucieuse / Esquive instinctive (Roublard), Inspiration bardique (Barde).
- **Sphères de ressources** : Rage, Ki, Dés de supériorité (4d8 au niveau 3 → 5 au 7, d10 au 10, 6 au 15, d12 au 18), Second souffle, Sursaut d'activité, Conduit divin, Inspiration bardique (d6 → d12), Sens divin. Récupération au repos court / long selon la règle.
- **Bouton « Utiliser »** : dépense immédiate de la sphère (ou d'un emplacement pour le Châtiment, niveau au choix), état appliqué (Rage, Défense patiente…), puis jet animé (d20 d'attaque à mains nues, dé de dégâts / de supériorité / d'inspiration, soins du Second souffle appliqués aux PV). Ressource épuisée → action grisée avec la raison (🔒).
- **Dés de dégâts animés** (d4, d6, d8, d10, d12 dessinés, d20 existant) : clic sur les dégâts des armes, sorts mineurs, attaques de bête, actions de classe et sur « 🎲 Dégâts » du détail d'un sort (onglet Mes sorts) → autant de dés à l'écran que la formule en demande (8d6 = huit d6), arrêt, somme + bonus fixe = total.
- **Bibliothèque restreinte** : uniquement la liste de la classe et les niveaux de sort atteints ; « 📜 Ajout manuel par le MJ » lève les deux restrictions.

## Nouveautés v20 — Imposition des mains en jauge
- Réserve du Paladin (5 × niveau, jusqu'à 100 PV) affichée en **jauge** dans l'encart Actions de classe : remplissage aux couleurs du thème, « restant / total PV », graduations tous les 5 points ; clic sur la jauge, molette ou flèches pour corriger à la main.
- Action « 🤲 Imposition des mains » : nombre de PV + cible (Sur soi / Sur un allié / Guérir maladie ou poison — 5 PV). Sur soi, les PV sont rendus immédiatement et seuls les PV manquants sont pris dans la réserve ; la guérison retire l'état Empoisonné. Réserve vide → action grisée. Récupération au repos long.

## Nouveautés v21 — finitions CRPG
- **Capacités de classe** : titre « Actions, capacités de classe » (le « & » était avalé par Qt comme raccourci clavier) ; colonne **Effet** à droite du bouton : mention courte de la manœuvre choisie (avec son DD), de l'Action astucieuse, ou de l'option de **Conduit divin propre au serment / domaine** (options lues dans la sous-classe : Arme sacrée, Vœu d'hostilité, Préservation de la vie…, Arme sacrée et Vœu appliqués comme états) ; raison du verrouillage 🔒 sinon.
- **Infobulles** nettoyées : plus aucune balise brute (`<br/>`, `<i>`) ; seules quelques balises de mise en forme sont interprétées, le reste est échappé.
- **Chant de la lame** (Magicien Chantelame, niv. 2) : sphères = bonus de maîtrise / repos long ; « Utiliser » l'active, « Mettre fin » le coupe sans coût ; refusé avec armure intermédiaire / lourde ou bouclier. La **Rage** fonctionne de même (bascule).
- **Passifs de classe** : sous-section de l'encart (Rage implacable, Évasion, Aura de protection, Critique amélioré…) — nom en pastille, description complète en infobulle. Liste par classe dans `data/Actions_Classes.json` (`passifs`) + capacités passives de sous-classe détectées automatiquement.
- **Actions d'armes** (Sape, Brise-crâne, Frappe affaiblissante…) : un clic lance le d20 d'attaque de l'arme équipée, avec rappel du JS / DD et de l'effet.
- **Réactions synchronisées** : Esquive instinctive, manœuvres Riposte / Parade et options de Conduit divin « par votre réaction » cochent automatiquement la réaction du round ; si elle est déjà utilisée, ces capacités sont verrouillées jusqu'au nouveau round.
- **Jets de sauvegarde** condensés (3 × 2, ● maîtrise, ▲/▼, d20) sous le Style de combat dans l'onglet Combat.
- **Dés animés** : libellés d4 → d12 lisibles (plus de troncature). **Magie** : colonne des emplacements plus large, volet de détail plus étroit.
- **Sorts à PV temporaires** (Simulacre de vie, Armure d'Agathys) : choix du niveau d'emplacement, jet animé, résultat injecté dans les PV temporaires (sans cumul : le plus haut est gardé).
- **Sorts accordés / manifestations** lançables avec « Lancer le sort » ; **Armure de mage** : avertissement si une armure est portée (le sort serait sans effet).
- **Changement de classe** : confirmation puis réinitialisation des spécificités de l'ancienne classe (sorts, concentration, états de classe, ressources, forme sauvage, manifestations / pacte, emplacements). **Option Multiclassage** (onglet Classes) : sans elle, une seule classe ; la désactiver retire les classes secondaires (confirmation). Les anciennes sauvegardes multiclassées l'activent automatiquement.

## Nouveautés v22 — sphères et espèces
- **Magie** : sphères d'emplacements agrandies (22 px, plus faciles à cliquer) dans la colonne élargie.
- **Espèces retirées** : Changeling ténébreux, Demi-dragon, Golem miniature, Harengon (doublon du Conil), Naïade, Orc cendré, Mort-vivant (doublon du Revenant), Elfe sylvestre (doublon de l'Elfe des bois). Les anciennes fiches sont converties au chargement (Elfe sylvestre → Elfe / Elfe des bois, Harengon → Conil, Mort-vivant → Revenant).
- **Espèces ajoutées** (Manuel des Joueurs ; règle libre de Tasha disponible) : **Demi-elfe** (Cha +2 et +1 à deux autres caractéristiques, vision 18 m, ascendance féerique, polyvalence), **Drow (Elfe noir)** (Dex +2, Cha +1, vision 36 m, sensibilité au soleil, magie drow au Charisme, armes drow, traits elfes), **Elfe** avec sous-espèces **Haut-elfe** (Int +1, armes elfiques, sort mineur de magicien, langue) et **Elfe des bois** (Sag +1, vitesse 10,5 m, armes elfiques, cachette naturelle).
- Les sous-espèces peuvent désormais être décrites directement dans `Races.json` (`sous_races` : bonus, traits, vitesse) ; modifications reproductibles via `tools/race_fixes/especes_v22.py` (`python tools/apply_corrections.py`).
- **Automatisations raciales** (toutes espèces) : maîtrises d'armes raciales prises en compte (armes elfiques, drow, naines…), compétence nommée cochée au choix de l'espèce (Sens aiguisés → Perception), Ascendance féerique affichée comme trait permanent, bonus libres limités aux caractéristiques non fixes (Demi-elfe).

## Nouveautés v23 — illustrations de races
- **Onglet Race** : illustration carrée de **8 cm × 8 cm** (taille calculée en centimètres réels d'après la résolution de l'écran, ≈ 302 px à 96 dpi, nette en HiDPI), placée sous le choix de la race et au-dessus des traits, centrée, dans un cadre ornementé aux couleurs du thème (double filet, losanges d'angle, vignettage). Mise à jour immédiate au changement de race ou de sous-race.
- **Images** : `data/images/races/<nom-de-la-race>.png|jpg` (aussi `.jpeg`, `.webp`). Recherche tolérante (accents, majuscules, tirets, apostrophes) : sous-espèce d'abord (`elfe-des-bois.png`), puis race, puis race sans parenthèse (`drow.jpg` pour « Drow (Elfe noir) »), puis début du nom (`myconide.jpg` pour « Myconide éveillé »). Image absente : médaillon avec l'initiale et « Illustration à venir ».
- **Mise à l'échelle** : `python tools/prepare_race_images.py <dossier>` recadre au centre en carré parfait (sans déformation), redimensionne toutes les images à 512 × 512, garde la transparence des illustrations détourées (PNG) et applique la convention de nommage. L'affichage recadre aussi en « cover » toute image ajoutée sans préparation.

## Nouveautés v24 — affordance, armes polyvalentes, races, thèmes
- **Interrupteurs visibles** : la maîtrise d'arme devient une pastille cliquable « ✦ Maîtrisée / ○ Non maîtrisée » (pointillés au repos, liseré au survol, verte une fois activée, infobulle « détectée automatiquement / forcée ») ; même style pour « ⚔ Multiclassage : activé / désactivé » (onglet Classes).
- **Armes polyvalentes** (Épée longue, Bâton de combat, Trident, Lance, Hache d'armes, Marteau de guerre, Pic de guerre) : commutateur « ✋ 1 main / 🙌 2 mains » dans la colonne Dégâts ; dégâts affichés et dés animés suivent la prise (le style Duel ne s'applique qu'à une main) ; prise à deux mains bloquée si un bouclier est porté ; choix enregistré avec l'arme.
- **Races** : « Enfant de la lune » retiré (doublon du Féral, anciennes fiches converties). Changer de race retire les langues et compétences que l'ancienne race avait accordées (le Commun et les compétences d'historique ou cochées à la main sont conservés) puis applique celles de la nouvelle. **Transe** (Elfe, Drow, Eladrin… toute race avec le trait Transe) : repos long de 4 heures.
- **Thèmes** : Skyrim adopte la typographie de BG3. Les neuf autres thèmes (BG3 inchangé) ont des palettes retravaillées et une couche de finitions : lueur propre au thème au survol et au focus (boutons, champs, listes, onglets, barres de défilement), titres d'encarts soulignés, info-bulles et fenêtres arrondies. Contrastes WCAG AA vérifiés pour tous, interrupteurs compris.

## Nouveautés v25 — francisation, Lame psychique, Humain variant, dons du MJ
- **Francisation** (`tools/francisation.py`, relancée par `apply_corrections.py`) : plus aucun doublon VO dans les données affichées — Lame psychique, Bretteur, Conspirateur, Éclaireur, Enquêteur, Fantôme, Cercle des Fournaises, Soldat psi, La Lame maudite, Profond, Commun des profondeurs, « Création de la communauté » au lieu de « Homebrew », « Moulinet ». Les anciennes fiches sont migrées au chargement (sous-classes, langues).
- **Lame psychique** (Roublard) : sphères de dés psioniques (2 × bonus de maîtrise ; d6 → d8 au niv. 5 → d10 au 11 → d12 au 17). Actions : Lames psychiques et seconde lame (jet d'attaque + dégâts psychiques), Savoir-faire renforcé et Frappes autoguidées (dé lancé d'abord, dépensé seulement si le jet réussit), Murmures psychiques (1re utilisation gratuite), Téléportation psychique (3 m × le dé), Voile psychique (niv. 13), Rupture spirituelle (niv. 17, 3 dés), Récupération psionique (1 dé, une fois par repos court). Actions grisées quand la réserve est vide.
- **Multiclassage** : bouton dimensionné sur son libellé le plus long (en gras) — plus de troncature.
- **Humain / Humain variant** : traits explicites (le panneau ne garde plus ceux de la race précédente) ; Humain variant = +1 / +1 sur deux caractéristiques différentes (rappel « au choix » tant qu'elles ne sont pas réparties), compétence au choix, et emplacement « don de départ » dans l'onglet Dons.
- **Don accordé par le MJ** (onglet Progression, dons) : bouton « 📜 Don accordé par le MJ » (recherche, présélection du don sélectionné dans le catalogue) ; le don devient un emplacement supplémentaire dont les bonus s'appliquent automatiquement ; bouton « ✖ Retirer ».

## Nouveautés v26 — Familiers, Compagnons, Invocations
- **Nouvel onglet « 🐉 Familiers, Compagnons, Invocations »**, couplé à `data/Familiers_Invocations.json` (95 entités : 23 familiers, 9 compagnons de classe, 63 invocations). Ménagerie active à gauche, fiche détaillée à droite.
- **[ + Ajouter une entité ]** : fenêtre de choix filtrable (Familiers / Compagnons de classe / Invocations + recherche), aperçu du profil, entités recommandées (★) en tête. Chaque entité ajoutée peut être renommée (nom personnalisé) ou retirée.
- **Détection contextuelle** (`core/companions.py`) :
  - Druide du Cercle des Fournaises (niv. 2+) : Esprit du feu sauvage ajouté d'office, retiré si la classe ou la sous-classe change (les entités ajoutées à la main sont conservées) ;
  - Rôdeur Maître des bêtes (Bêtes de la terre / de la mer / du ciel), Gardien des drakes (Compagnon drake), Artificier Forgeur d'armes (Défenseur d'acier) ou Artilleur (Canon occulte), Occultiste de la Lame maudite niv. 6 (Spectre maudit) : avertissement « Votre classe / sous-classe vous permet de lier un compagnon spécifique… » avec bouton « Voir les recommandés ★ » ; il disparaît dès qu'un compagnon recommandé est lié ;
  - Pacte de la chaîne : rappel des quatre familiers supérieurs (Diablotin, Esprit follet, Pseudodragon, Quasit).
- **Fiche dynamique** : CA, jauge et compteur de PV (actuels / max, PV temporaires), vitesses, perception passive, FOR → CHA. Les compagnons de classe et invocations (Tasha) sont recalculés depuis le bonus de maîtrise, le niveau de classe, la caractéristique d'incantation du personnage et le niveau du sort d'invocation (formules du fichier, évaluateur sécurisé) ; capacités débloquées par niveau ajoutées aux traits.
- **Jets** : clic sur une caractéristique (test), sur « JS » (sauvegarde), sur une compétence, sur le d20 d'une attaque puis sur ses dégâts (animation multi-dés). Traits et réactions avec infobulles.
- **Sauvegarde** : `menagerie` dans le JSON du personnage (identifiant, nom personnalisé, PV actuels et temporaires, état, niveau du sort) ; PV bornés au maximum recalculé au chargement.

## Nouveautés v27 — actions de race, styles de combat, vision dans le noir, mini-fiche des entités
- **Actions de race dans l'onglet Combat** (`core/race_actions.py`) : les traits actifs de l'espèce et de la sous-espèce (action, action bonus, réaction ou utilisations limitées : Fureur des petits, Endurance de pierre, Pas féerique, Mains guérisseuses, Souffle…) rejoignent l'encart, qui s'intitule alors « Actions, capacités de classe et de race » (sinon « Actions, capacités de classe »). Bouton « Utiliser », sphères d'utilisations, verrouillage à épuisement, recharge au repos court ou long selon le trait, réaction du round consommée pour les traits de réaction (qui apparaissent aussi dans l'encart Réactions). Les sorts innés restent dans l'onglet Magie, la Transe et les traits de repos sont exclus. Changement d'espèce : actions et compteurs remplacés et remis à zéro immédiatement.
- **Styles de combat** : le style choisi n'apparaît plus dans les réactions. Les styles passifs (Défense, Duel, Archerie, Armes à deux mains…) sont listés dans les capacités permanentes (« Style de combat : Duel ») ; seuls Protection et Interception restent des réactions.
- **Encart Vision** à côté de la Perception passive : « Vision dans le noir — 🌑 18 m » (36 m pour une vision supérieure), lue dans les traits de l'espèce ou le sort actif, sinon « Vision — 👁 Normale ». Les cinq encarts (Initiative, Vitesse, Maîtrise, Perception passive, Vision) ont la même largeur, sans dépassement.
- **Mini-fiche des entités** : grille d'actions réalignée (d20 + bonus, icône de dé + formule + type, supplément, sauvegarde ; « — » dans les cases vides, lignes de hauteur constante). Texte des PV de la jauge en noir gras, cerné d'un halo clair pour rester lisible sur la partie verte comme sur la partie vide.

## Nouveautés v28 — choix manquants (création impossible à rater)
- **Moteur `missing_choices()`** (`core/missing.py`) : compte chaque OUBLI et le rattache à son onglet et à son encart.
  - Caractéristiques : valeurs tirées non assignées, bonus raciaux libres.
  - Compétences de classe et d'espèce (Demi-elfe, Humain variant…) ; expertises (2 par aptitude « Expertise »).
  - Sous-classe au niveau requis.
  - Langues « au choix » de l'espèce et de l'historique ; couleur du dragon ancestral (Drakéide).
  - Style de combat ou modèle d'armure.
  - Sorts mineurs, sorts connus, grimoire du magicien (6 + 2 par niveau), sorts à préparer ; faveur de pacte ; manifestations occultes.
  - Améliorations de caractéristiques ou dons laissés vides.
  Les excès et prérequis non remplis restent des **incohérences** (`warnings()`).
- **Pastilles d'onglet** : « Magie ③ » en couleur d'ornement, retirée à zéro ; infobulle « N choix à faire dans cet onglet ».
- **Barre d'état** : « ○ N choix à faire » et « ⚠ N incohérence(s) » (ou « ✔ Fiche complète et cohérente »), cliquables : la liste s'ouvre et mène à l'onglet concerné.
- **Titres d'encarts** : « Compétences — ○ 2 à choisir », « Langues — ○ 3 à choisir », « Style de combat… », « Sorts du personnage… », « Emplacements débloqués », « Bonus raciaux… » ; sous-classe « ○ à choisir » dans l'onglet Classes.
- **Rappels non bloquants** : la fenêtre « Modifications non enregistrées » et le message d'enregistrement indiquent « 3 choix restent à faire (Magie, …) ».
- **Après un repos long** : proposition d'ouvrir l'onglet Magie pour revoir les sorts préparés (Clerc, Druide, Paladin, Artificier, Magicien).

## Nouveautés v29 — montée de niveau guidée et frise 1 → 20
- **Assistant « ▲ Niveau supérieur »** (bouton de l'en-tête, menu Fichier, Ctrl+L) — `ui/levelup_dialog.py`, `core/levelup.py`. Cinq étapes, avec à gauche des pastilles ○ / ✔ :
  1. **Classe à monter** : classes du personnage, et nouvelles classes si le multiclassage est activé, avec l'avertissement de prérequis (« Magicien demande Intelligence 13 »).
  2. **Points de vie gagnés** : moyenne fixe du dé de vie + Constitution + bonus.
  3. **Aptitudes gagnées** et prochain palier.
  4. **Choix du niveau** faits dans l'assistant : sous-classe, amélioration de caractéristiques ou don (dons dont les prérequis sont remplis en tête, ✔ / ⚠), style de combat, faveur de pacte. Les sorts, compétences, langues… sont listés « à faire ensuite » et signalés par les pastilles d'onglet (v28).
  5. **Récapitulatif avant / après** : PV max, maîtrise, dés de vie, emplacements, DD et attaque de sort, ressources, caractéristiques.
- « Confirmer » reste grisé tant qu'un choix de l'étape 4 manque (motif en infobulle). Seuls les choix de CE niveau bloquent ; un oubli antérieur ne bloque pas.
- Tout se fait sur une copie du personnage : « Annuler » ne change rien. Le compteur « Niveau global » reste disponible pour un changement direct (mode MJ).
- **Frise de progression 1 → 20** en tête de chaque onglet de classe : ✦ aptitude · ◆ sous-classe · ▲ amélioration ou don · ✧ nouveau niveau de sort ; niveau actuel encadré, niveaux à venir atténués, infobulle par niveau.

## Nouveautés v30 — combat : barre du tour, réactions programmables, surclassement direct
- **Encart « ⚔ Ce tour-ci »** (onglet Combat, sous la ligne Initiative / Vitesse / Maîtrise / Perception / Vision) — `core/turn.py`.
  - Tout ce qui est jouable réuni en tuiles : armes équipées ; sorts mineurs, préparés ou connus, raciaux, accordés (selon leur temps d'incantation) ; actions de classe et de race ; réactions ; actions communes (Foncer, Se désengager, Esquiver, Aider, Se cacher, Bousculer, Saisir, Utiliser un objet, Chercher, Interagir, Parler).
  - Filtres **Tout / Action / Action bonus / Réaction / Gratuit**, avec le nombre de tuiles de chaque catégorie.
  - Un clic utilise la tuile : il dépense l'action, l'action bonus ou la réaction, puis lance l'attaque (d20 animé), les dés ou le sort. Si le lancement du sort est annulé, l'action est rendue.
  - Une tuile est grisée, avec le motif en infobulle, si son coût est déjà dépensé ce tour ou si sa ressource est épuisée (emplacement, sphère).
  - **Attaque supplémentaire** : 2 attaques (3 et 4 pour le Guerrier aux niveaux 11 et 20) dans la même action Attaquer, avec le décompte « attaque 2 / 3 ».
- **Pied de tour** : voyants ● / ○ Action, Bonus, Réaction (cliquables pour corriger), déplacement en mètres avec « reste x m » (doublé par Foncer), bouton de la réaction automatique, « ⟳ Nouveau round » qui remet tout à zéro.
- **Réactions programmables** (encart Réactions) : chaque réaction se règle sur **Demander**, **Automatique** ou **Désactivée**.
  - Automatique : réaction par défaut, une seule à la fois, marquée ★ en tête de la barre et accessible d'un clic dans le pied de tour.
  - Désactivée : masquée de la barre, grisée dans l'encart.
  - Le réglage est enregistré avec le personnage.
- **Surclassement direct** (onglet Magie) : sélecteur « Emplacement niveau N » sous le détail du sort, limité aux niveaux encore disponibles. Le sort est lancé avec cet emplacement, sans fenêtre de confirmation.

## Nouveautés v31 — mannequin d'équipement
- **Mannequin** (onglet Inventaire, à gauche du sac) — `core/equipment.py`, `ui/paperdoll.py`. Douze cases autour du portrait du personnage : tête, amulette, cape ou robe, armure, gants ou bracelets, ceinture, bottes, deux anneaux, main principale, main secondaire, distance.
  - Les objets magiques portables (89 objets reconnus par leur type ou leur nom : anneaux, bottes, capes, amulettes, heaumes…) occupent une case.
  - **Un objet par case** : équiper un objet dans une case occupée déséquipe l'ancien. Les anciennes fiches qui portent trop d'objets d'un type sont signalées (« 3 anneaux équipés pour 2 emplacements ») dans les incohérences.
  - Infobulle de chaque case : rareté et harmonisation (◉ harmonisé, ○ harmonisation requise).
- **Jeux d'armes mêlée / distance** : bouton du mannequin ; les armes du jeu actif passent en tête de la barre du tour.
- **Comparaison « équipé / survolé »** (Ajouter un objet) : pour une armure, CA avant / après, désavantage en Discrétion et Force requise ; pour une arme, dégâts moyens actuels contre ceux de l'arme survolée.

## Nouveautés v32 — mannequin centré sur le personnage, cases alimentées par l'inventaire
- **Portrait du personnage au centre du mannequin**, celui de l'onglet « Histoire, Portrait » (le portrait de l'espèce n'y figure plus). Sans portrait, un clic mène à l'onglet pour l'importer.
- **Chaque case propose les objets de l'inventaire selon son rôle** :
  - Armure : les armures du sac.
  - Main principale : les armes de corps à corps.
  - Main secondaire : les boucliers et les armes légères.
  - Distance : les armes à distance.
  - Tête, amulette, cape, gants, ceinture, bottes, anneaux : les objets magiques du bon type.
- « ✖ Vider la case » range l'objet, qui reste dans l'inventaire.
- Ce qui est équipé ici devient l'armure, le bouclier et les armes de l'onglet Combat (une seule source).
- **Arme à deux mains** : la main secondaire se libère (bouclier rangé) et ne peut plus être occupée tant qu'elle est tenue.

## Nouveautés v33 — ajout rapide d'objets magiques, objets sur mesure, inventaire allégé
- **⚡ Ajout rapide** (Inventaire › Équipement, objets magiques) : on tape quelques lettres (« Anneau de… », « Bottes… », « epee » sans accent, mots dans le désordre). Les objets officiels correspondants s'affichent, ceux qui commencent par la saisie en premier.
  - L'objet choisi est pré-rempli : type, rareté, harmonisation (et la condition, ex. « par un lanceur de sorts »), description, source.
  - Entrée ou « Ajouter » l'ajoute immédiatement, avec le choix +1 / +2 / +3 pour les objets variables.
  - Catalogue : 390 objets (342 du Guide du maître, 48 du Guide complet de Xanathar). Les sources sont affichées en français.
- **✚ Objet sur mesure** : une seule fenêtre. Seul le nom est obligatoire ; le reste a des valeurs par défaut (type « Objet merveilleux », rareté « peu commun », case « Harmonisation requise », description courte, poids, bonus de CA).
  - Si la saisie rapide ne correspond à aucun objet officiel, « Ajouter » ouvre ce formulaire avec le nom déjà rempli.
  - La fiche est enregistrée avec le personnage, compte dans la charge (poids) et occupe sa case du mannequin (anneau, broche…).
- **Badge d'harmonisation** sur chaque objet : « ✦ Harmonisé » / « ◇ Non harmonisé », un clic bascule. Limite de 3 objets (plus pour l'Artificier) : au-delà, le badge est grisé et indique « 3 / 3 : déharmonisez d'abord un autre objet ».
- **Inventaire allégé** : l'encart « Traits, idéaux, liens, défauts » quitte l'Inventaire pour l'onglet « Histoire, Portrait » (sous le portrait). L'espace libéré revient aux maîtrises d'outils et aux notes d'équipement.

## Nouveautés v34 — flux d'attaque, liens Combat / Inventaire, nettoyages visuels
- **« L'attaque touche-t-elle ? »** : après le d20 de toucher (tuile de la barre du tour, bouton d20 d'une arme, action d'arme, attaque à mains nues d'une action de classe), une fenêtre affiche le d20 et le total.
  - **Oui** : les dés de dégâts animés de l'arme sont lancés, avec la prise 1 main / 2 mains.
  - **Non** : on ferme.
  - Sur un 20 naturel, coup critique : les dés de dégâts sont doublés (« 1d8+3 » → « 2d8+3 »). Un 1 naturel rate toujours, sans question.
- **Arme choisie dans l'onglet Combat** absente du sac : ajoutée automatiquement à l'inventaire. Même chose pour l'armure et le bouclier.
- **Attaque d'opportunité** : plus de réglage Demander / Automatique / Désactivée (jouée à la table). Les autres réactions gardent le leur.
- **Inventaire** :
  - L'encart « Jeu d'armes actif » est retiré.
  - La case « Harmonisation requise » de l'objet sur mesure est bien visible, sur sa propre ligne, avec une case de 18 px contrastée.
  - Les 12 cases du mannequin et le portrait vide passent à la ligne au lieu d'être tronqués, et sont un peu plus grands (150 × 66 px).
- **Histoire, Portrait** : notes de campagne plus grandes que l'histoire du personnage.
- **Langues** :
  - « Halphen » devient « Halfelin » (données et anciennes fiches).
  - Plus aucune mention de fichiers .json dans l'interface.
  - Cases à cocher contrastées, langue connue en gras, clic sur toute la ligne.
- **Magie** : les encarts « Mes sorts », « Sorts raciaux » et « Sorts accordés » ont un fond opaque et une hauteur minimale. Au redimensionnement, plus rien n'apparaît en transparence.

## Nouveautés v35 — molette neutralisée, style « Technique supérieure »
- **La molette ne sert plus qu'à faire défiler** (`ui/wheel_guard.py`, filtre installé sur toute l'application) :
  - Au-dessus d'une liste déroulante, d'un compteur numérique (même avec le focus), d'une barre d'onglets ou d'un curseur, la molette ne change plus rien. Elle fait défiler la page ou le conteneur parent.
  - Les sphères de ressources et les jauges (Imposition des mains, PV des entités) n'ont plus de réglage à la molette : clic et flèches du clavier uniquement.
  - Les barres de défilement, listes, tableaux et textes défilent normalement.
- **Technique supérieure** (style de combat du Guerrier, Tasha) :
  - Une fois le style choisi, une liste « Manœuvre » apparaît à côté du style (onglet Combat), avec les manœuvres officielles du Maître de guerre et leur description en infobulle. Tant qu'aucune n'est choisie, elle est signalée comme choix à faire.
  - La manœuvre apparaît dans « Actions, capacités de classe » (« Manœuvre : Riposte »…), avec son DD (8 + maîtrise + For ou Dex). Elle est jouable depuis l'encart et la barre du tour. Riposte et Parade consomment la réaction du round.
  - **1 dé de supériorité d6** à part (sphère « Dé de supériorité (Technique supérieure) »), en plus des dés du Maître de guerre. Il est dépensé à l'utilisation et récupéré au repos court ou long.
  - Si le style est remplacé, la manœuvre, l'action et le dé disparaissent.
  - Description du style corrigée : il n'y a pas de « DD 14 » fixe, et le dé revient au repos court ou long.

## Nouveautés v51 — multiclassage sans blocage, en-tête épuré, mises en page compactes
- **Bug corrigé — « Choix du niveau (1) » fantôme** (ex. Occultiste 1 → Paladin 1) :
  - en Mode guidé, un prérequis de multiclassage non rempli était compté comme un choix du niveau, invisible sur la page, et bloquait « Confirmer » ;
  - désormais une classe aux prérequis non remplis n'est plus proposée : elle est listée « 🔒 » avec la raison (Mode libre : proposée avec un avertissement) ;
  - le compteur ne compte que les choix de LA classe montée à ce niveau (sous-classe, amélioration, style, sorts, pacte, manifestations) : 0 choix → « ✔ » et validation immédiate.
- **En-tête** : « Vitesse » et « Maîtrise » retirées (elles sont dans l'onglet Combat) ; restent PV, CA et Initiative (avec son d20).
- **Onglet Combat** : les cinq encarts (Initiative, Vitesse, Maîtrise, Perception passive, Vision dans le noir) sont alignés sur une grille, à hauteur fixe identique.
- **Onglet Caractéristiques & Compétences** :
  - cartes de caractéristiques moins hautes, tables de compétences et de sauvegardes en lignes compactes, légende raccourcie ;
  - texte « Valeurs choisies dans l'assistant… » déplacé en infobulle ;
  - but : tenir sur un écran 1080p sans défilement.
- Rapport : `RAPPORT_CORRECTIFS_v51.md`.

## Nouveautés v50 — fenêtres maximisables, création incomplète confirmée, en-têtes selon le mode
- **Fenêtres** :
  - l'assistant de création et « Niveau supérieur » sont de vraies fenêtres (barre de titre, boutons Réduire / Agrandir / Fermer), redimensionnables ; bouton « ⛶ Plein écran » dans l'assistant ;
  - toutes les pages défilent, donc rien n'est coupé en fenêtre réduite ;
  - la fenêtre principale descend jusqu'à 1024 × 640.
- **Création incomplète** : « ✔ Créer le personnage » ouvre la modale « Création de personnage incomplète » avec la liste des choix manquants.
  - « Poursuivre la création » ramène à la première étape incomplète ; « Valider malgré tout » crée la fiche.
- **Cases à cocher** : « Sac sans fond » sur sa propre ligne, page Équipement défilante ; fenêtre Options défilante ; cases dessinées de façon visible quel que soit le thème.
- **Multiclassage** : l'interrupteur de l'onglet Classes est retiré. « Niveau supérieur » propose toujours les autres classes ; en Mode guidé, les prérequis de caractéristiques officiels bloquent « Confirmer » (Mode libre : accord du MJ).
- **Mode guidé** : classe, sous-classe et niveau en texte statique stylé (badges) dans l'en-tête de la fiche et dans l'onglet Classes. Le **Mode libre** rétablit les sélecteurs.
- Rapport : `RAPPORT_CORRECTIFS_v50.md`.

## Nouveautés v49 — aide pédagogique (BG3), recommandations de caractéristiques, inspecteur de sorts
- **Fiche pédagogique de classe** dans l'assistant de création (étape Classe) et dans « Niveau supérieur » (étape Classe) :
  - concept, style de jeu, mécaniques clés ;
  - caractéristiques recommandées, dé de vie, maîtrises ;
  - liste des sous-classes avec le niveau de déblocage. Un clic déplie la fiche d'une sous-classe : source, orientation (🔮 Magie, ⚔ Offensive, 🛡 Défense…), pouvoirs principaux par niveau, sorts accordés ; un second clic la replie.
  - Dans « Niveau supérieur », le sélecteur de sous-classe affiche un résumé au survol et la fiche de la sous-classe choisie.
- **Recommandations de caractéristiques** : badges « ⭐ [Principale] » / « ✦ [Secondaire] » sur les cartes de caractéristiques, avec infobulle expliquant pourquoi.
  - Ils s'adaptent à la sous-classe : Arnaqueur arcanique et Chevalier occulte → Intelligence ; Bretteur → Charisme ; Lame maudite → Charisme principal…
  - Dans l'assistant, une « sous-classe visée » peut être indiquée avant son niveau de déblocage.
- **Identité** (étape 7 de l'assistant) : « [ Importer un portrait ] » (png, jpg, jpeg… réduit au format de la fiche) et zone « Passé du personnage ». Les deux sont repris dans l'onglet « Histoire, Portrait », modifiables à tout moment.
- **Sélection des sorts** (création et montée de niveau) :
  - un clic affiche la fiche détaillée : école, incantation, portée, composantes, durée, concentration, rituel, texte complet ;
  - le double-clic ou le bouton « ✚ Apprendre le sort » / « ✚ Préparer » apprend le sort, dans la limite des quotas.
- Rapport : `RAPPORT_ARCHITECTURE_v49.md`.

## Nouveautés v48 — création façon Baldur's Gate 3, Mode guidé / Mode libre, sauvegarde automatique
- **Assistant de création niveau 1** (Fichier > Nouveau personnage, ouvert aussi au premier lancement), sur une copie de la fiche, avec un résumé dynamique à droite :
  1. Race / Sous-race ;
  2. Classe — sous-classe de niveau 1, style de combat, compétences et expertises ;
  3. Historique et langues ;
  4. Caractéristiques ;
  5. Sorts et tours de magie, avec la magie raciale ;
  6. Équipement ;
  7. Identité — nom, joueur, alignement.
- **Magie raciale pour toutes les classes** :
  - encart « ✦ Magie raciale — [Sort Racial] » dans l'onglet Magie (visible aussi pour un Guerrier) ;
  - sort mineur au choix du Haut-elfe (liste du magicien) ;
  - tuiles « … [Sort Racial] » dans « Sorts et magie » de l'onglet Combat.
- **Équipement de départ** :
  - l'équipement de l'historique est offert ;
  - ensuite, au choix : le paquetage de classe standard (équipé automatiquement), ou la boutique — budget = or de la classe (moyenne ou jet de dés) + or de l'historique, le reste allant dans la bourse.
- **En-tête** : champ Alignement retiré (il est désormais dans « Histoire, Portrait » et dans l'assistant) ; le nom du joueur prend la place libérée.
- **Mode guidé (par défaut)** :
  - nom du personnage verrouillé ;
  - niveau global, ajout, retrait et changement de classe uniquement par « ▲ Niveau supérieur » ; onglet Classes en lecture seule ;
  - onglet Race remplacé par l'encart « Résumé de la race » à côté du portrait ;
  - caractéristiques brutes remplacées par un résumé.
  
  « Activer le Mode libre » (Options) déverrouille tout. Un écran verrouillé réapparaît tant qu'un choix doit y être fait.
- **Sauvegarde automatique** : copie de sécurité 1,5 s après chaque modification. Au lancement, le dernier personnage est rouvert (modifications non enregistrées comprises).
- **Menu Fichier** : Nouveau personnage… / Charger… / Sauvegarder / Sauvegarder sous….
- Rapport : `RAPPORT_ARCHITECTURE_v48.md`.

## Nouveautés v47 — exécutable Windows autonome
- **`core/paths.py`** :
  - `get_resource_path()` lit les données dans `sys._MEIPASS` (exécutable PyInstaller), sinon dans le dossier du projet ;
  - `user_data_dir()` / `working_copy()` : dossier inscriptible (%APPDATA%\Fiche_DnD5E) pour toute donnée modifiable.
  - `main.py` et les images d'espèces l'utilisent ; `--check --check-file` vérifie les données depuis l'exécutable sans console.
- **`build_executable.py`** (commentaires et journal en français) :
  - vérifications, tests, PyInstaller `--onefile --windowed` avec `data/` et `assets/` embarqués et l'icône ;
  - placement dans `dist/Fiche_Personnage_DnD5E.exe` (remplace l'ancien), lancement de vérification, journal `dist/journal_build.txt` ;
  - `--simulation` affiche la commande sans compiler.
- **`compiler_windows.bat`** : compilation en un double-clic (installe PyInstaller et PyQt6 si besoin). v47.1 : fins de ligne Windows (CRLF), texte ASCII, recherche automatique d'Anaconda / Miniconda (environnement activé), puis de Python dans le PATH.
- **`.github/workflows/build-exe.yml`** : compilation automatique sur un serveur Windows de GitHub à chaque envoi ; le `.exe` est téléchargeable dans « Actions ».
- **Icône de l'application** : `assets/app_icon.ico` (d20 doré), générée par `tools/make_icon.py`.
- Rapport : `RAPPORT_BUILD_v47.md`.

## Nouveautés v46 — dégâts expliqués, armes polyvalentes automatiques, inventaire aligné
- **Calcul détaillé des dégâts** dans la ligne d'arme (infobulle), la tuile d'attaque et la fenêtre de dés.
  - Exemple : « 1d8 - 1 (Mod. FOR) + 3 (Objet magique : Épée longue +3) = 1d8 + 2 ».
  - Sources détaillées : caractéristique, objet magique, style Duel, Rage, munition magique, dés ajoutés (Faveur divine, dé de supériorité…).
  - La fenêtre de dés explique le bonus fixe (« -1 (Mod. FOR) + 3 (…) = +2 ») au lieu d'afficher « Bonus fixe : +2 ».
- **Armes polyvalentes** (Épée longue, Bâton de combat, Marteau de guerre, Hache d'armes…) : prise automatique.
  - Main secondaire libre → à deux mains (dé supérieur).
  - Bouclier ou seconde arme → à une main.
  - Libellé « Épée longue (à deux mains) » sur la tuile et dans la fenêtre de dégâts.
  - Recalcul immédiat quand on équipe ou retire un bouclier / une arme secondaire ; l'ancien commutateur manuel devient un indicateur.
- **Inventaire** : quantités centrées pour tous les objets (mondains et magiques).
- Rapport : `RAPPORT_CORRECTIFS_v46.md`.

## Nouveautés v45 — objets magiques équipables, initiative, Forme sauvage, dons d'armures
- **Assistant de niveau (multiclassage Occultiste → Guerrier)** : plus de chevauchement. Le vidage des choix supprime aussi les grilles imbriquées, et seuls les choix de la classe qui monte sont affichés (Faveur de pacte et manifestations : Occultiste uniquement).
- **Repos long** : fenêtre élargie (760 px minimum), libellés lisibles.
- **Dons de maîtrise d'armures** : « Maîtrise des armures légères / intermédiaires (+ boucliers) / lourdes » ajoutés au catalogue.
  - Les maîtrises sont mises à jour et l'origine est affichée : « Armures lourdes (Accordé par le Don : Maîtrise des armures lourdes) ».
  - Les avertissements et le blocage des sorts disparaissent dès que la maîtrise est acquise.
- **Initiative** : dé d20 cliquable dans l'en-tête et dans l'onglet Combat.
  - Jet de 1d20 + modificateur : Dextérité, Alerte +5, Touche-à-tout / Athlète remarquable, Embusqué redoutable, Audace désinvolte, Prescience de bataille, Esprit tactique, Conscience temporelle, effets actifs ; avantage avec Instinct sauvage.
  - Détail dans la fenêtre de dés ; dernier jet gardé sur la fiche.
- **Forme sauvage / Métamorphose** : tuiles « Morsure — Loup »… dans « Attaques ».
  - Déroulé habituel : d20, « L'attaque touche-t-elle ? », dégâts de la bête.
  - Les attaques d'arme sont masquées pendant la forme et reviennent dès la fin de la transformation.
- **Armes, armures et boucliers magiques** :
  - à l'ajout (Arme +2, Armure +1, Bouclier +3, Épée ardente, Bouclier expressif…), sélecteur de l'objet de base filtré selon le catalogue (« toute épée », « harnois »…) ;
  - nom explicite : « Épée à deux mains +2 », « Harnois +1 » ;
  - équipés dans la case du mannequin : +X au toucher et aux dégâts, ou +X à la CA, aussitôt ; retirés si l'objet quitte la case ou n'est pas harmonisé quand il l'exige.
- **Inventaire principal** : les objets magiques y sont listés (✨, couleur dorée, état équipé / harmonisé) avec un bouton « ✨ Équiper / déséquiper » ; badge ✨ sur le mannequin.
- **Capacités activables des objets** : groupe « 💎 Objets magiques » dans « Ce tour-ci ».
  - Une tuile par capacité (action, action bonus, réaction) ou par sort lancé, badge « [Objet Magique : Nom] ».
  - Les charges se décomptent et sont rechargées au repos long ; un sort lancé par l'objet suit la résolution habituelle.
- Rapport : `RAPPORT_CORRECTIFS_v45.md`.

## Nouveautés v44 — échange de sorts au niveau supérieur, préparation au repos long
- **Assistant de niveau — « Remplacer un sort connu »** (étape « Nouveaux sorts ») pour Barde, Ensorceleur, Occultiste, Rôdeur, Chevalier occulte et Arnaqueur arcanique, quand cette classe gagne le niveau :
  - étape 1 « Oublier » : un seul sort connu de niveau 1 ou plus, parmi ceux appris avant ce niveau (les sorts accordés et ceux du niveau en cours sont exclus) ;
  - étape 2 « Remplacer » : débloquée ensuite ; liste de la classe jusqu'au niveau de sort maximal, recherche et filtre d'école, infobulles ;
  - Chevalier occulte (Abjuration / Évocation) et Arnaqueur arcanique (Enchantement / Illusion) : écoles imposées, sauf si le sort oublié occupait un emplacement libre (n'importe quelle école) ;
  - résumé « ✔ Échange : A → B », bouton « Annuler l'échange » ; un sort oublié sans remplaçant bloque « Confirmer ».
- **Repos long — « Sorts pour la journée à venir »** :
  - `[ Changer les sorts préparés ]` pour Clerc, Druide, Paladin (et Artificier, Magicien) : fenêtre cochable, filtres, jauge « Préparés : n / max » avec la formule, sorts de domaine / serment rappelés hors quota ; au-delà du quota la case refuse de se cocher ;
  - `[ Changer un tour de magie ]` pour le Magicien (Tasha, Formules de sorts mineurs) : tour de magie à oublier, remplaçant de la liste du Magicien, aperçu des textes ;
  - les choix sont appliqués à la fin du repos (« Se reposer ») ; « Annuler » les abandonne. La question « Revoir mes sorts ? » posée après le repos disparaît.
- Rapport : `RAPPORT_CORRECTIFS_v44.md`.

## Nouveautés v43 — maîtrises, bibliothèque de sorts, manifestations dans l'assistant
- **Bibliothèque de sorts** :
  - fond opaque (encart, liste et pages des onglets) : plus de texte en transparence ;
  - double-clic ou bouton : un sort ✔ déjà appris est retiré, un sort non appris est ajouté (bouton « Ajouter ✚ / Retirer ✖ » selon la sélection).
- **Maîtrises** :
  - encart « Maîtrises — armes et armures » dans l'onglet Classes : ce que la classe apporte (départ ou multiclassage) et le total du personnage ;
  - les maîtrises de sous-classe sont prises en compte (Domaine de la Guerre, Collège de la Vaillance, Lame maudite…).
- **Armure ou bouclier non maîtrisé** :
  - ⚠ sur l'objet (inventaire, mannequin) et à côté de la CA (onglet Combat, en-tête), avec l'infobulle officielle ;
  - désavantage aux tests, jets de sauvegarde et attaques de Force et de Dextérité ;
  - **aucun sort possible** : tuiles grisées « Impossible de lancer un sort tout en portant une armure non maîtrisée. », alerte au lancement. La gestion des sorts reste possible.
- **Arme non maîtrisée** : ⚠ (inventaire, mannequin, ligne d'arme, tuile d'attaque), infobulle « Le bonus de maîtrise ne s'applique pas au jet de toucher. », jet = 1d20 + mod. seulement.
- **Assistant de niveau (Occultiste)** : choix des manifestations occultes à l'étape « Choix du niveau ».
  - Le quota est respecté et seules les manifestations aux prérequis remplis sont proposées.
  - Infobulle au survol (texte complet, sort accordé, prérequis, source), aperçu dynamique et résumé « ✔ Choisie ».
  - Pas de doublon ; « Confirmer » attend ces choix.
- Rapport : `RAPPORT_CORRECTIFS_v43.md`.

## Nouveautés v42 — fenêtre « Niveau supérieur » et styles de combat expliqués
- **Fenêtre de montée de niveau** :
  - taille par défaut adaptée à l'écran (jusqu'à 75 % de la largeur et 85 % de la hauteur, 1200 × 820 visés, jamais plus grande que l'écran) ;
  - poignée de redimensionnement en bas à droite ; colonne des étapes élargie ;
  - pages Classe, Points de vie, Choix du niveau et Nouveaux sorts défilantes (les textes ne sont plus coupés).
- **Styles de combat** : une carte par choix (style ou modèle d'armure).
  - Infobulle au survol de chaque style de la liste : texte mécanique complet et ce que la fiche applique.
  - Aperçu dynamique « 👁 Aperçu » pendant la navigation dans la liste.
  - Résumé « ✔ Style choisi » sous le sélecteur après la sélection.
- **Textes complets des 13 styles** (PHB et Tasha) dans `core/fighting_styles.py` : Archerie, Armes à deux mains, Combat à deux armes, Défense, Duel, Protection, Arme de lancer, Combat à mains nues, Combat en aveugle, Interception, Technique supérieure, Combattant béni, Combattant druidique. Ils sont aussi utilisés par l'onglet Combat et les passifs.
- `main.py` ignore les modules « core » / « ui » d'un autre projet restés en mémoire dans Spyder.
- Rapport : `RAPPORT_CORRECTIFS_v42.md`.

## Nouveautés v41 — grimoire de l'assistant, tuiles groupées, déplacement en cases
- **Assistant de niveau, étape « Nouveaux sorts »** :
  - deux onglets par classe, **Tours de magie (X / Y)** et **Sorts de niveau 1+ (A / B)**, avec des compteurs indépendants ;
  - filtres en temps réel : boutons de niveau (Tous, Niveau 1, 2…), école (8 écoles), cases **Rituel (R)** et **Concentration (C)**, recherche ;
  - colonne « Vos sorts » : case **Préparé** et jauge « Préparés : n / max » (limite de la classe). Les classes à sorts connus sont toujours prêtes ;
  - Clerc, Druide, Paladin et Artificier préparent directement dans leur liste.
- **Combat, « Ce tour-ci »** :
  - tuiles en groupes : 🗡️ Attaques, ✨ Sorts et magie, ⚡ Réactions, 🏃 Actions génériques (plus 🎖️ Capacités de classe et de race pour Rage, Second souffle…) ; le filtre par coût reste disponible ;
  - déplacement en cases : saisie en cases, « Déplacement : reste 6 cases (9 m) (vitesse 6 cases (9 m)) ».
- **Encart « Réactions » supprimé** : les réactions sont des tuiles du groupe ⚡. La réaction du round se suit au voyant « Réaction » du pied de tour (infobulle : nom de la réaction ; clic : annuler).
- **Mains nues** : attaque innée, jamais ajoutée à l'inventaire ; les anciennes entrées « Mains nues » du sac sont retirées.
- Rapport : `RAPPORT_CORRECTIFS_v41.md`.

## Nouveautés v40 — assistant de niveau, sorts à sauvegarde, réactions, potions
- **Assistant « Niveau supérieur »** :
  - nouvelle étape **« Nouveaux sorts »** avec le quota exact de la classe à ce niveau : sorts mineurs, sorts connus, grimoire du magicien (+2) ;
  - liste des sorts apprenables (liste de classe, niveau maximal, écoles imposées) avec recherche et description au survol ; double-clic pour apprendre ou retirer ;
  - « Confirmer » attend aussi ces choix. La préparation quotidienne (Clerc, Druide, Paladin…) reste dans l'onglet Magie.
- **Dons** : infobulle au survol de chaque don de la liste (effet, prérequis, bonus, source) et résumé sous le sélecteur une fois choisi.
- **Amélioration de caractéristiques** :
  - une carte par emplacement (plus de chevauchement de sélecteurs), pages 4 et 5 avec barre de défilement ;
  - « +1 à deux caractéristiques » impose deux caractéristiques différentes (la seconde liste exclut la première ; le moteur refuse les doublons) ;
  - aperçu « Force 15 → 16 » et alerte au-delà de 20.
- **Sorts à jet de sauvegarde** :
  - sous les dégâts (détail du sort, tuile du Combat, fenêtre de résolution) : « Jet de sauvegarde de Dextérité : DD 15 » et « Succès = 1/2 dégâts », « Succès = 0 dégât » ou « Dégâts même en cas de succès » ;
  - après le jet de dégâts : total en cas d'échec et moitié en cas de réussite ;
  - règle par sort dans `data/Regles_sorts.json` (« js_succes ») : les sorts de niveau 1+ infligent la moitié en cas de réussite, les sorts mineurs rien ; exceptions vérifiées (Désintégration, Catapulte, Châtiments, Métal brûlant…).
- **Réactions** : plus de réglage Demander / Automatique / Désactivée. Chaque réaction est une tuile cliquable qui consomme la réaction du round.
- **Règle optionnelle** : tuile « Boire une potion (Action bonus) » quand l'inventaire contient une potion (choix de la potion, effet appliqué, potion retirée). Administrer une potion à un allié reste l'action « Utiliser un objet ».
- Rapport : `RAPPORT_CORRECTIFS_v40.md`.

## Nouveautés v39 — tuiles d'action et résolution unifiée du Combat
- **Armes du mannequin** :
  - tuile « Attaque — arme (main principale) » ; « Attaque à mains nues » si la main principale est vide ;
  - tuile d'action bonus « Attaque en main secondaire » après l'action Attaquer (armes légères ou don Combattant à deux armes) : d20 distinct, dégâts sans modificateur sauf s'il est négatif ou avec le style Combat à deux armes.
- **Effets de dégâts** : inconditionnels ajoutés aux dés, conditionnels (Marque du chasseur, Maléfice) proposés après un coup qui touche.
- **Sorts depuis le Combat** : choix du niveau d'emplacement (dégâts recalculés, pacte d'office), puis lancement, puis attaque de sort (un jet par rayon) ou fenêtre « DD N de sauvegarde de X » (échec / réussite), puis dégâts ou soins au niveau dépensé. Même flux pour « Lancer » dans l'onglet Magie.
- **Maître de guerre** : choix des manœuvres (Options de sous-classe), une tuile par manœuvre, dé de supériorité décompté et combiné aux dégâts de l'arme ; 7 manœuvres de Tasha ajoutées (`tools/maneuver_fixes.py`).
- **Roublard** : Attaque sournoise (Finesse ou distance, 1 fois par tour, arme + Xd6) ; Action astucieuse en trois tuiles.
- **Ensorceleur** : choix des options de métamagie, une tuile par option, points de sorcellerie décomptés.
- **Plus de 100 tuiles d'aptitudes actives** de classes et sous-classes (PHB, Xanathar, Tasha) dans `core/class_tiles.py` : compteurs automatiques, DD calculés, armes naturelles, grisage « Uniquement en rage », « Déjà utilisée ce tour ».
  - Exemples : Frénésie, auras de tempête, Forme de la bête, Mots cinglants, Fioritures, Prêtre de guerre, Courroux de la tempête, Forme sauvage (choix de la bête), Forme étoilée, Halo de spores, Inflexible, Esprit combatif, Main de guérison, Malédiction de la Lame maudite, Ennemi juré, Tueur de colosses, Présage, Canon occulte…
- Rapport complet : `RAPPORT_AUDIT_v39.md` (correspondance classe / sous-classe → tuiles).

## Nouveautés v38 — surclassement dynamique et Magie des pactes
- **Sort lancé à un niveau supérieur** :
  - le sélecteur « Emplacement » recalcule à chaque changement le détail du sort : description réécrite (dés, valeurs fixes, nombre de projectiles ou de rayons mis en évidence), encart « Dégâts (niveau N) », soins et PV temporaires ;
  - par exemple, Mains brûlantes au niveau 3 affiche « Dégâts (niveau 3) : 5d6 de feu » et le texte « … infligeant 5d6 dégâts de feu … ».
- **Jets de dés** : le clic sur les dégâts lance les dés du niveau choisi (5d6, pas 3d6). Le bouton « Jet d'attaque » enchaîne d20 → « L'attaque touche-t-elle ? » → dégâts au niveau effectif. La note du jet d'attaque indique aussi ce niveau.
- **Lancement** : le message indique l'emplacement réellement dépensé et les dégâts ou soins correspondants (« emplacement de Pacte, niveau 3, niveau supérieur — Dégâts : 4d10 feu »).
- **Magie des pactes (Occultiste)** :
  - les sorts d'occultiste sont surclassés d'office au niveau des emplacements de Pacte (niveau 5 : sorts de niveau 1 et 2 lancés au niveau 3) ;
  - liste « Mes sorts » : « 1 ⇒ 3 » ; sélecteur verrouillé sur le niveau du pacte (infobulle « Magie des pactes ») ;
  - description, dégâts, jets, tuiles du tour (« sort niv. 1 ⇒ 3 », « emplacement de Pacte niv. 3 ») et lancement depuis le Combat suivent ce niveau ;
  - les sorts accordés par une manifestation qui dépense un emplacement d'occultiste aussi.
  - En multiclasse, seuls les sorts appris comme occultiste sont surclassés d'office ; ceux des autres classes gardent leur niveau, surclassable au sélecteur.

## Nouveautés v37 — audit des manifestations occultes et des sorts
- **Décharge occulte** (tuile du tour, encart des sorts mineurs, infobulles) :
  - Décharge déchirante ajoute le modificateur de Charisme à chaque rayon (« 3 × 1d10+4 »), et non plus « +1 ».
  - 1 rayon, puis 2 / 3 / 4 aux niveaux 5 / 11 / 17 (niveau de personnage). Le jet de dégâts indique le total si tous les rayons touchent et la valeur par rayon.
  - Lance occulte : portée 90 m. Décharge répulsive (3 m par rayon), Étreinte de Hadar (attire de 3 m, 1 fois par tour) et Lance de léthargie (−3 m de vitesse, 1 fois par tour) apparaissent sur la tuile.
  - Ces manifestations exigent de connaître Décharge occulte.
- **54 manifestations réécrites** (`tools/invocation_fixes.py`, idempotent, relancé par `apply_corrections.py`) :
  - textes officiels VF, source (PHB, Xanathar, Tasha) et prérequis structurés (niveau, pacte, sort mineur, Maléfice) ;
  - sorts accordés explicites : à volonté, ou 1 fois par repos long avec ou sans emplacement d'occultiste, suivi par un compteur.
- **Répercussions sur la fiche** :
  - Vision du diable : encart Vision à 36 m, ténèbres magiques comprises (✦).
  - Présence captivante : maîtrise de Tromperie et de Persuasion.
  - Armure d'ombres : Armure de mage à volonté sur soi, sans emplacement, avec la CA 13 + Dex.
  - Lame assoiffée : 2 attaques par action Attaquer. Buveuse de vie et Arme de pacte améliorée apparaissent dans les passifs, avec leur valeur.
  - Don des profondeurs : vitesse de nage dans l'infobulle de la vitesse, Respiration aquatique 1 fois par repos long.
  - Esprit occulte : avantage aux JS de Constitution pour la concentration.
  - Actions du Combat :
    - Attaque occulte : emplacement de Pacte, (1 + niveau)d8 de force.
    - Tombe de Levistus : 10 PV temporaires par niveau, repos court.
    - Voile de mouches : mod. de Charisme, repos court.
    - Maléfice accablant / implacable.
    - Regard fantomatique, Maître des ombres, Perception transférée.
    - Réprimande, Protection et Lien du talisman : bonus de maîtrise.
    - Présent des sauveurs, Engagement du maître.
  - Chaîne des carcères : Immobilisation de monstre à volonté (céleste, fiélon, élémentaire).
- **Livre des secrets anciens** (onglet Magie, Manifestations) :
  - inscrire 2 rituels de niveau 1 de n'importe quelle classe (choix manquant tant qu'ils ne sont pas choisis) ;
  - puis d'autres rituels jusqu'à la moitié du niveau d'occultiste ;
  - ils se lancent uniquement comme rituels depuis « Sorts accordés ».
- **Sorts** (`tools/spell_rules.py` → `data/Regles_sorts.json`, surcouche lue au chargement) :
  - durée officielle pour les 482 sorts du corpus ;
  - Rappel à la vie et Réincarnation ne sont plus des rituels ;
  - dés de base, type et jet corrigés (Éclair, Blessure, Rayon empoisonné, Fouet épineux…) ;
  - surclassement exact par niveau d'emplacement : dés, projectiles, cibles, durée. Lame d'ombres et Arme élémentaire suivent des paliers.
  - Le détail du sort affiche les dégâts et soins au niveau choisi, avec la règle « Au niveau supérieur ».
- **Modificateur aux dégâts** seulement quand une règle le dit :
  - le sort lui-même : soins, Arme spirituelle, Pierre magique, Gourdin magique ;
  - Décharge déchirante ;
  - Incantation puissante (Clerc), Évocation renforcée (Magicien), Affinité élémentaire (Ensorceleur draconique).
  - Pierre magique et Gourdin magique ne gagnent pas de dés aux niveaux 5 / 11 / 17. Lame retentissante, Lame aux flammes vertes et Glas suivent leur échelle propre.
- Rapport complet : `RAPPORT_AUDIT_v37.md`.

## Nouveautés v36 — sous-classes du Guerrier, montures, écoles imposées, langues
- **Interface**
  - Onglet Combat : « ⏳ Jour & Heure : Jour 1, 09:00 ».
  - Infobulle de la CA dans l'en-tête : « CA de base (Armure de cuir clouté : 12) + Mod. Dextérité (+3) + Bouclier (+2) = 17 ».
  - Infobulle du bouton « ▲ Niveau supérieur » : « Cliquez ici pour lancer l'assistant de montée de niveau pas à pas… ».
- **Langues : « Langues choisies : X / Y »** (vert si juste, ornement s'il en manque, alerte au-delà), avec le détail des sources en infobulle.
  - Le quota compte les langues fixes de l'espèce et de l'historique, les langues au choix de l'espèce et de l'historique, les dons (Connaissance ancestrale, Prodige…) et les aptitudes de classe qui en accordent.
  - Il manque des langues : choix à faire. Il y en a trop : incohérence. La fiche n'est jamais bloquée.
- **Chevalier runique** (Tasha), encart « Options de sous-classe » de l'onglet Combat :
  - Choix des runes : 2 au niveau 3, 3 au 7, 4 au 10, 5 au 15 (colline et tempête dès le niveau 7).
  - Effets officiels, passifs dans les passifs de classe, actions jouables à 1 utilisation par repos court ou long (2 au niveau 15), DD = 8 + maîtrise + Con.
  - Puissance des géants : bonus de maîtrise par repos long ; 1d6, 1d8 au niveau 10 (Grande stature), 1d10 au niveau 18.
  - Bouclier runique (niveau 7).
- **Soldat psi** (Tasha) : dés d'énergie psionique (2 × maîtrise ; d6, d8, d10, d12), tous récupérés au repos long. Actions :
  - Champ protecteur, Frappe psionique (dé + Int) ;
  - Mouvement télékinétique et Bond psi : gratuits une fois par repos, sinon un dé ;
  - Récupération psionique : 1 dé, une fois par repos court ;
  - Esprit gardé (10), Rempart de force (15), Maître télékinétique (18).
- **Archer arcanique** (Xanathar) : options de Tir arcanique (2 au niveau 3, +1 aux niveaux 7, 10, 15, 18), 2 utilisations par repos court ou long, une action par option avec ses dés (doublés au niveau 18) et son DD (8 + maîtrise + Int).
- **Onglet « Ménagerie & Montures »** :
  - 7 montures (`tools/add_mounts.py`, idempotent, relancé par `apply_corrections.py`) : Cheval de selle, Cheval de trait, Cheval de guerre (Charge piétinante), Poney, Mule (Bête de somme, Pied sûr), Chameau, Mâtin. Profils du Manuel des monstres, prix du Manuel des joueurs.
  - Filtre « Montures », bouton « 🐴 Ajouter une monture ».
  - Conseil « Né en selle » pour le Guerrier Cavalier tant qu'aucune monture n'est liée.
- **Écoles imposées** :
  - Chevalier occulte : Évocation et Abjuration. Arnaqueur arcanique : Enchantement et Illusion.
  - Sorts libres de toute école aux niveaux 3, 8, 14 et 20 (1 à 4). Les sorts mineurs restent libres.
  - Bibliothèque : sorts hors école grisés avec le motif quand les sorts libres sont épuisés, ajout refusé (sauf en mode MJ), compteur « sorts libres x / y ». Un dépassement est signalé comme incohérence.
  - Arnaqueur arcanique : Main de mage connue d'office (retirée si la sous-classe change) et action « Main de mage arcanique » (Passe-passe à distance, action bonus).
