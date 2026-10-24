# Audit de conformité des données — règles officielles D&D 5e

_Généré le 10/10/2026 par `tools/audit_regles.py`._

Périmètre : fichiers de progression des classes (`data/<Classe>.json`) et des espèces (`data/Races.json`, `data/Bonus_Raciaux.json`), comparés au Manuel des joueurs (PHB), au Guide complet de Xanathar (XGE), au Chaudron de Tasha (TCE) et, pour les espèces, aux ouvrages indiqués dans leur champ source.

Les corrections ont été **appliquées aux fichiers JSON** par `python tools/apply_corrections.py` (idempotent) : noms et niveaux d'aptitudes, aptitudes manquantes, options du Chaudron de Tasha, listes de sorts de sous-classe, sources, bonus raciaux, langues, traits, vitesses, descriptions chiffrées.
Restent listés ci-dessous les écarts **volontairement non corrigés** (renommer une sous-classe ou une espèce casserait les fiches sauvegardées, sous-classes officielles scindées, sorts absents de la base…).

Légende : 🔴 **majeur** = règle fausse qui change le jeu · 🟠 **mineur** = imprécision, nom, faute · 🔵 **info** = remarque.

## Synthèse

| Fichier | Corrigés | Restants 🔴 | Restants 🟠 | Restants 🔵 |
|---|---|---|---|---|
| Artificier | 38 | 0 | 0 | 2 |
| Barbare | 36 | 0 | 0 | 4 |
| Barde | 32 | 0 | 0 | 1 |
| Clerc | 83 | 0 | 0 | 2 |
| Druide | 38 | 0 | 0 | 3 |
| Ensorceleur | 37 | 0 | 0 | 3 |
| Guerrier | 40 | 0 | 0 | 3 |
| Magicien | 62 | 0 | 0 | 1 |
| Moine | 38 | 0 | 0 | 1 |
| Occultiste | 38 | 0 | 0 | 6 |
| Paladin | 53 | 0 | 0 | 0 |
| Roublard | 29 | 0 | 0 | 1 |
| Rôdeur | 45 | 0 | 0 | 4 |
| Espèces | 220 | 0 | 0 | 34 |
| **Total** | **789** | **0** | **0** | **65** |

## Écarts restants

### Artificier — 2 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Artificier | Classe issue de Tasha : aucune « capacité de classe optionnelle » à ajouter (rien à corriger) | Option d'arme à feu (maîtrise) au choix du MJ uniquement | relecture |
| 🔵 info | Forgeur d'armes | Nom de sous-classe non officiel : non renommée pour ne pas casser les fiches existantes (sorts, source et aptitudes corrigés) | Forgeron de guerre (Battle Smith) | relecture |

### Barbare — 4 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Sous-classes | Voie du géant (Bigby) et Battlerager (SCAG) absentes : hors périmètre PHB/XGE/TCE, non ajoutées | Sous-classes officielles hors PHB/XGE/TCE non incluses | relecture |
| 🔵 info | Voie des tempêtes (Désert/Mer/Toundra) | Scindée en trois sous-classes ; nom officiel non utilisé : non fusionnée ni renommée pour ne pas casser les fiches existantes | Une seule sous-classe « Voie du héraut des tempêtes » ; l'environnement peut changer à chaque niveau de barbare | relecture |
| 🔵 info | Voie totémique | Totems Élan et Tigre (SCAG) absents : non ajoutés car il faudrait créer de nouvelles sous-classes scindées (structure actuelle conservée) | Options supplémentaires du Sword Coast Adventurer's Guide | relecture |
| 🔵 info | Voie totémique (Ours/Aigle/Loup) | Scindée en trois sous-classes distinctes : non fusionnée pour ne pas casser les fiches existantes | Officiellement une seule sous-classe (Voie du guerrier totémique) avec choix d'animal indépendant aux niv. 3, 6 et 14 | relecture |

### Barde — 1 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Barde / Sorts de barde supplémentaires (option Tasha) | « Antipathie/Sympathie » (niv. 8) cité dans le texte mais sort absent de la base de sorts | TCE ajoute Antipathie/Sympathie à la liste de sorts de barde | relecture |

### Clerc — 2 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Domaine de l'Arcane (Communauté) / nom | Sous-classe officielle (SCAG) nommée « Domaine de l'Arcane (Communauté) » | Nom officiel : Domaine des Arcanes — non renommée pour ne pas casser les fiches sauvegardées (source et sorts corrigés) | relecture |
| 🔵 info | Domaine du Sang (Communauté) / nature | Sous-classe homebrew (communauté), sans équivalent officiel | Conservée telle quelle ; seuls les sorts invalides ont été remplacés par des sorts de la base (Lien sanglant -> Flétrissement, Cécité/Surdité -> Compulsion pour équilibrer les paliers) | relecture |

### Druide — 3 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Cercle des Astres / nom | Nom « Cercle des Astres » | Circle of Stars : traduction usuelle « Cercle des Étoiles » ; non renommé pour ne pas casser les fiches existantes | relecture |
| 🔵 info | Cercle des Fournaises (Wildfire) / nom | Nom mêlant français et anglais | Circle of Wildfire : « Cercle du Feu sauvage » ; non renommé pour ne pas casser les fiches existantes | relecture |
| 🔵 info | Forme sauvage améliorée (Nage) / (Vol) | Présentées comme des aptitudes distinctes | Ce sont les paliers de la table de Forme sauvage (PHB) ; conservées comme repères de niveau (4 et 8) pour l'onglet Forme sauvage, non fusionnées | relecture |

### Ensorceleur — 3 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Aptitudes fusionnées (ex. Ancêtre dragon & Résilience draconique) | Deux aptitudes officielles du même niveau regroupées en une seule entrée : non scindées pour ne pas casser les fiches existantes | Les aptitudes sont distinctes dans les livres mais de même niveau | relecture |
| 🔵 info | Lignée draconique / Ailes draconiques | Nom VF habituel « Ailes de dragon » : non renommé (même incertitude), règle décrite exacte | Dragon Wings (niveau 14) | relecture |
| 🔵 info | Magie sauvage / noms d'aptitudes | Pic de magie sauvage, Comme par hasard et Torrent arcanique diffèrent des noms habituels de la VF (Montée de magie sauvage, Plier la chance, Bombardement de sorts) : non renommés, traduction officielle non vérifiable ici, règles décrites exactes | Wild Magic Surge, Tides of Chaos, Bend Luck, Controlled Chaos, Spell Bombardment | relecture |

### Guerrier — 3 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Archer arcanique | Pas d'entrée au niveau 10 : non corrigé, aucune aptitude officielle à ce niveau | Le niveau 10 n'apporte qu'une option de Tir arcanique supplémentaire (mentionnée dans Tir arcanique) | relecture |
| 🔵 info | Chevalier de Sang / sorts_domaine | Liste de sorts sans aptitude d'incantation : conservée telle quelle (homebrew validé) | Aucune aptitude ne permet de lancer ces sorts ; liste purement indicative | relecture |
| 🔵 info | Guerrier Psi (Soldat psi) | Nom de sous-classe double : non renommée pour ne pas casser les fiches existantes | Nom officiel FR : « Soldat psi » (Psi Warrior) | relecture |

### Magicien — 1 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Tradition d'arcanes | Graviturgie (Guide de Wildemount) absente : non ajoutée (aucune opération d'ajout de sous-classe) | Tradition officielle de Wildemount, au même titre que la Chronurgie | relecture |

### Moine — 1 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Voie de la Paume | Nom non officiel : sous-classe non renommée pour ne pas casser les fiches existantes | Voie de la Main ouverte (PHB) | relecture |

### Occultiste — 6 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Invocations occultes | Nom non officiel (VF : « Manifestations occultes ») : non renommée, le logiciel gère les manifestations occultes par un panneau dédié indépendant du nom de l'aptitude | PHB : « Manifestations occultes » (Eldritch Invocations), niveau 2 | relecture |
| 🔵 info | La Lame maudite (Magelame) | Nom de sous-classe erroné (« Magelame » = Bladesinger du magicien) : non renommée pour ne pas casser les fiches existantes | XGE : « La Lame maudite » (Hexblade) | relecture |
| 🔵 info | Le Génie | Sous-classe éclatée en 4 entrées (dao, djinn, éfrit, maride) : non fusionnée pour ne pas casser les fiches existantes | TCE : un seul patron, le type de génie étant choisi au niveau 1 | relecture |
| 🔵 info | Magie des pactes | Nom légèrement différent de la VF (« Magie de pacte ») : non renommée (nom utilisé par le moteur d'incantation) | PHB : « Magie de pacte » (Pact Magic) | relecture |
| 🔵 info | Pacte divin | Nom non officiel : non renommée (le logiciel s'appuie sur « Pacte divin » pour le choix du pacte) | PHB : « Faveur de pacte » (Pact Boon), obtenue au niveau 3 | relecture |
| 🔵 info | Sous-classes | Patrons officiels absents : ajout de sous-classes hors du périmètre des corrections (pas d'opération de création) | L'Immortel (SCAG) et Le Mort-vivant (Van Richten) ne figurent pas dans les données | relecture |

### Roublard — 1 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Lame psychique / Soulknife | Nom de sous-classe mêlant français et anglais : non renommée pour ne pas casser les fiches existantes | Lame psychique (Soulknife, TCE) | relecture |

### Rôdeur — 4 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Gardien des nuées | Nom de la sous-classe non officiel : non renommée pour ne pas casser les fiches existantes (aptitudes renommées Essaim rassemblé / Essaim puissant / Dispersion de l'essaim) | Tasha (FR) : Gardien de l'essaim (Swarmkeeper) | relecture |
| 🔵 info | Rôdeur / sous-classes | Cavalier draconique (Drakewarden, Fizban) absent : les FIXES ne permettent pas de créer une sous-classe, ajout laissé à une évolution des données | Fizban's Treasury of Dragons : archétype officiel optionnel | relecture |
| 🔵 info | Vagabond féérique | Orthographe « féérique » du nom de sous-classe : non renommée pour ne pas casser les fiches existantes | « féerique » | relecture |
| 🔵 info | sorts_domaine (toutes sous-classes) | Format conservé : niveaux stockés comme éléments de liste ('1'…'5') entre les noms de sorts, car Engine.domain_spells (et ses tests) lit ce format « paires » pour le rôdeur ; tools/check_fixes.py signale ces marqueurs comme sorts absents | Format à normaliser (paires nom/niveau ou dictionnaire) en même temps que le moteur | relecture |

### Espèces et sous-races — 34 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔵 info | Anciennes fiches | Espèces retirées encore présentes dans des sauvegardes | Converties au chargement : Elfe sylvestre -> Elfe (Elfe des bois), Harengon -> Conil, Mort-vivant -> Revenant | relecture |
| 🔵 info | Ascendance féerique (PHB 2014) | Le PHB parle d'avantage contre le fait d'être charmé et d'immunité au sommeil magique | Repris tel quel ; affiché comme trait permanent dans la barre d'états | relecture |
| 🔵 info | Autognome / vitesse | 9 m inscrit dans vitesses (redondant) | Aucune opération de suppression ; valeur correcte | relecture |
| 🔵 info | Bonus_Raciaux.json / vitesses spéciales | Vol (Aarakocra, Fadette, Aasimar protecteur), nage (Elfe des mers) et escalade (Dhampir) restent textuels | Aucun champ de vitesse spéciale dans le format de données ; décrites dans les traits | relecture |
| 🔵 info | Changeling ténébreux / source | Homebrew ; langue Ombrelante absente de Langues.json | Rééquilibré sans audit officiel | relecture |
| 🔵 info | Conil / source | Homebrew, doublon du Harengon | Chiffres alignés sur le Harengon | relecture |
| 🔵 info | Demi-dragon / source | Homebrew | Souffle aligné sur le drakéide | relecture |
| 🔵 info | Demi-elfe / Polyvalence | Deux compétences au choix | À cocher dans l'onglet Compétences | relecture |
| 🔵 info | Drakéide / taille | Taille absente, pas de vision dans le noir | Conforme au MdJ 2014 (Moyenne) ; non bloquant | relecture |
| 🔵 info | Elfe sylvestre | Conforme au MdJ | Seule la description de Cachette naturelle a été précisée | relecture |
| 🔵 info | Enfant de la lune / source | Homebrew, recoupe le Féral | Chiffres rééquilibrés | relecture |
| 🔵 info | Githyanki, Githzerai / carac. d'incantation | rules.RACE_SPELL_ABILITY fige Int (Githyanki) et Sag (Githzerai) ; hors périmètre de ce module | MotM : Int, Sag ou Cha au choix (indiqué dans le texte du trait) | relecture |
| 🔵 info | Grung, Kalashtar / langues exotiques | Grung et Quori sans entrée dans Langues.json | Langues de cadre de campagne, notées en texte libre | relecture |
| 🔵 info | Halfelins, Gobelin / langues | « Halfelin » absent de Langues.json (fichier hors périmètre) | Langue standard MdJ : Halfelin | relecture |
| 🔵 info | Haut-elfe / sort mineur | Choix libre dans la liste du magicien | À ajouter via « Sorts accordés » (onglet Magie) ; Intelligence | relecture |
| 🔵 info | Humain, Humain variant | Conformes au MdJ : aucune correction | Manuel des joueurs | relecture |
| 🔵 info | Kitsune, Golem miniature / source | Espèces non officielles : chiffres rééquilibrés, non auditées comme officielles | Aucune source 5e officielle | relecture |
| 🔵 info | Kobold / vitesse | Entrée 9 m redondante dans Bonus_Raciaux.json (idem Minotaure, Tortle) | Valeur juste : laissée telle quelle | relecture |
| 🔵 info | Locathah / langues | « Aquan » absent de Langues.json | Officiel (Locathah Rising) : conservé, noté en langue libre par le logiciel | relecture |
| 🔵 info | Léonin, Loxodon, Vedalken / langues | Langues propres absentes de Langues.json | Officielles : conservées, notées en texte libre | relecture |
| 🔵 info | Mort-vivant, Orc cendré, Myconide éveillé, Naïade / source | Non officiel | Homebrew : chiffres rééquilibrés, non audités comme officiels | relecture |
| 🔵 info | Naïade / caractéristique d'incantation | Le logiciel prend la meilleure de Int/Sag/Cha | Homebrew : Sagesse indiquée dans le texte ; pas d'entrée dans RACE_SPELL_ABILITY (hors périmètre) | relecture |
| 🔵 info | Revenant / Héritage ancestral | Option VRGR non modélisée | Option facultative (garder des traits de l'ancienne espèce) laissée au MJ | relecture |
| 🔵 info | Revenant / nom | Revenant | Nom officiel : Reborn ; espèce non renommée (contrainte) | relecture |
| 🔵 info | Règle de Tasha (origine personnalisée) | +2 / +1 (ou +1/+1/+1) au choix à la place des bonus fixes | Option « Règle libre » de l'onglet Caractéristiques, valable pour les nouvelles espèces | relecture |
| 🔵 info | Tieffelin / version | Version MdJ 2014 (Cha +2, Int +1) | Conforme à la source indiquée | relecture |
| 🔵 info | Tieffelin féral / variantes | Toutes les options listées dans un seul trait (au choix) | Le moteur affiche les sorts « au choix » : le joueur n'en retient qu'une option | relecture |
| 🔵 info | Transe | 4 heures de méditation = bénéfices de 8 heures de sommeil (repos long de 8 h toujours requis pour ses autres effets) | Texte du PHB ; aucune automatisation du temps de repos | relecture |
| 🔵 info | Triton, Yuan-ti / caractéristique d'incantation | core/rules.py RACE_SPELL_ABILITY impose Charisme (Volo) | MotM : Int, Sag ou Cha au choix ; correction hors périmètre (fichier de code) | relecture |
| 🔵 info | Vitesses secondaires (nage, vol, escalade) | Non modélisées par Bonus_Raciaux.json (marche seule) | Indiquées en mètres dans les traits Owlin, Tabaxi, Triton, Locathah, Naïade, Tieffelin féral | relecture |
| 🔵 info | Vitesses spéciales (nage, escalade) | Le moteur ne modélise que la marche ; nage/escalade décrites dans les traits | Bonus_Raciaux.json ne gère qu'une vitesse par espèce | relecture |
| 🔵 info | Yuan-ti / Amitié avec les animaux | Le logiciel classe un sort de niveau 1 en « 1 fois / repos long » | MotM : à volonté sur les serpents ; texte exact, limitation du moteur | relecture |
| 🔵 info | Yuan-ti / version | Résistance au poison = MotM (Volo : immunité) | MotM 2022 | relecture |
| 🔵 info | rules.RACE_SPELL_ABILITY | Duergar (Int) et Firbolg (Sag) restent figés dans le code | Hors périmètre (fichier interdit) ; les traits indiquent Int/Sag/Cha au choix | relecture |

## Journal des corrections appliquées

### Artificier (corrigé) — 38 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Alchimiste / Ingrédients revigorants | 2d6+1 PV temporaires fixe, Restauration partielle 1 fois | 2d6 + mod. Int PV temporaires ; Restauration partielle gratuite mod. Int fois par repos long | corrigé |
| 🔴 majeur | Alchimiste / sorts_domaine | Liste fausse (Rayon de maladresse, Soin, Fléau, Restauration partielle, Porte dimensionnelle, Liberté de mouvement, Restauration suprême, Soins de groupe…) | Mot de guérison, Rayon empoisonné ; Flèche acide de Melf, Sphère de feu ; Forme gazeuse, Mot de guérison de groupe ; Flétrissement, Protection contre la mort ; Brume mortelle, Rappel à la vie | corrigé |
| 🔴 majeur | Alchimiste / Élixir expérimental | 3 élixirs dès le niveau 3, aucune création via emplacement | 1 élixir (2 au niv. 6, 3 au niv. 15) + création par action en dépensant un emplacement (effet choisi) | corrigé |
| 🔴 majeur | Alchimiste / Érudit alchimique | Bonus fixe de +1 | + modificateur d'Intelligence (min +1) à un jet de soins ou de dégâts acide/feu/nécrotique/poison | corrigé |
| 🔴 majeur | Armurier / sorts_domaine | Déguisement et Aide au lieu de Vague tonnante et Image miroir | Projectile magique, Vague tonnante ; Image miroir, Fracassement ; Motif hypnotique, Éclair ; Bouclier de feu, Invisibilité supérieure ; Passe-muraille, Mur de force | corrigé |
| 🔴 majeur | Artilleur / Canon explosif | DD fixe de 14 | DD = 8 + bonus de maîtrise + modificateur d'Intelligence ; 3d8 force, rayon 6 m | corrigé |
| 🔴 majeur | Artilleur / Canon occulte | Seulement 1 fois par repos long, sans dégâts ni PV | 1 gratuit par repos long puis via emplacement de niveau 1+ ; PV = 5 × niveau d'artificier ; 2d8 | corrigé |
| 🔴 majeur | Artilleur / sorts_domaine | Mains brûlantes au lieu de Vague tonnante, Passe-muraille au lieu de Mur de force | Bouclier, Vague tonnante ; Rayon ardent, Fracassement ; Boule de feu, Mur de vent ; Tempête de grêle, Mur de feu ; Cône de froid, Mur de force | corrigé |
| 🔴 majeur | Bricolage magique | Limité à 1 objet enchanté à la fois | Nombre d'objets = modificateur d'Intelligence (minimum 1) ; action, outils en main, objet Très petit | corrigé |
| 🔴 majeur | Forgeur d'armes / Apte au combat | Maîtrise des « armures de guerre » | Maîtrise des armes de guerre (aucune armure supplémentaire) | corrigé |
| 🔴 majeur | Forgeur d'armes / Décharge arcanique | Placée au niveau 15 avec 4d6, sans limite d'utilisations | Niveau 9 : 2d6 (4d6 au niveau 15), mod. Int fois par repos long, 1 fois par tour | corrigé |
| 🔴 majeur | Forgeur d'armes / Défenseur amélioré | Déviation : 1d4+1 dégâts fixe | 1d4 + modificateur d'Intelligence dégâts de force ; Décharge arcanique passe à 4d6 | corrigé |
| 🔴 majeur | Forgeur d'armes / sorts_domaine | Liste fausse (Châtiment incandescent, Arme magique, Revitalisation, Protection contre l'énergie, Divination, Liberté de mouvement, Colonne de feu, Châtiment d'aveuglement) | Héroïsme, Bouclier ; Châtiment révélateur, Lien de protection ; Aura de vitalité, Invocation de projectiles ; Aura de pureté, Bouclier de feu ; Châtiment du ban (Banishing Smite), Soins de groupe | corrigé |
| 🔴 majeur | Infusion d'objets | 4 infusions et jusqu'à 6 objets infusés dès le niveau 2 | Connues/actives : 4/2 (niv. 2), 6/3 (6), 8/4 (10), 10/5 (14), 12/6 (18) | corrigé |
| 🔴 majeur | Objet de stockage de sort | Sort utilisable 2 fois, « 1 fois par repos long » | Utilisations = 2 × modificateur d'Intelligence (min 2) ; rechargé/remplacé à la fin d'un repos long | corrigé |
| 🔴 majeur | Éclair de génie | Bonus fixe de +1, 1 fois par repos long | Réaction : + modificateur d'Intelligence au jet, utilisations = mod. Int (min 1) par repos long | corrigé |
| 🟠 mineur | Adepte des objets magiques | « peu courant ou inférieur » : réduction également du coût en ressources | Objets courants et peu courants : quart du temps, moitié du coût en po | corrigé |
| 🟠 mineur | Alchimiste / Maîtrise chimique | « Restauration suprême et soins » | Restauration supérieure et Guérison (Heal), 1 fois chacun par repos long | corrigé |
| 🟠 mineur | Alchimiste / sorts_domaine | Entrée inexistante « Flacon de feu alchimique (sorts d'altération) » | Aucun sort de ce nom en 5e | corrigé |
| 🟠 mineur | Armurier / Armure parachevée | Aucun effet précis | Gardien : attraction 7,50 m (JS Force) + attaque, PB fois/repos long ; Infiltrateur : lueur, avantage, +1d6 foudre | corrigé |
| 🟠 mineur | Armurier / Modèle d'armure | Aucun chiffre (gantelets, lance-foudre, champ défensif) | Gantelets 1d8 tonnerre ; lance-foudre 1d6 (+1d6 1/tour) 27/90 m ; PV temp. = niveau d'artificier, PB fois/repos long | corrigé |
| 🟠 mineur | Armurier / sorts_domaine | Noms anglais (Disguise self, Magic missile, Hypnotic pattern, Lightning bolt, Greater invisibility, Fire shield, Passwall, Wall of force) | Noms français officiels | corrigé |
| 🟠 mineur | Artilleur / Arme à feu arcanique | « arme de bois » | Baguette, bâton ou sceptre gravé | corrigé |
| 🟠 mineur | Artilleur / Position fortifiée | Les deux canons créés « en coûtant 1 sort » | Même action mais pas le même emplacement de sort | corrigé |
| 🟠 mineur | Artilleur / sorts_domaine | Noms anglais (Shatter, Wind wall, Ice storm, Wall of fire, Passwall) | Noms français officiels | corrigé |
| 🟠 mineur | Automaturge / sorts_domaine | Noms anglais (Alarm, Detect magic, Find traps, Levitate, Tiny servant, Arcane eye, Creation, Wall of force) | Alarme, Détection de la magie, Sens des pièges, Lévitation, Serviteur miniature, Oeil magique, Création, Mur de force (noms de la base de sorts) | corrigé |
| 🟠 mineur | Automaturge / sorts_domaine | « Control solids » n'existe pas | Remplacé par Façonnage de la pierre | corrigé |
| 🟠 mineur | Cartomancien / sorts_domaine | « Dissonance cacophonique » n'est pas un nom de sort | Murmures dissonants (Dissonant Whispers) | corrigé |
| 🟠 mineur | Cartomancien / sorts_domaine | Noms anglais (Silent image, Augury, Locate object, Major image, Arcane eye, Geas, Scrying) | Image silencieuse, Augure, Localisation d'objet, Image majeure, Oeil magique, Quête, Scrutation | corrigé |
| 🟠 mineur | Cartomancien / sorts_domaine | Divination (niveau 4) placée au niveau 9 (sorts de niveau 3 max) | Remplacée par Clignotement (niveau 3) | corrigé |
| 🟠 mineur | Forgeur d'armes / Défenseur d'acier | Statistiques absentes | CA 15, PV = 5 × niveau d'artificier + 2 + mod. Int, Déchirure 1d8 + PB, Réparation 2d8 + PB 3/jour | corrigé |
| 🟠 mineur | Horloger / sorts_domaine | Noms anglais (Longstrider, Sanctuary, Blur, Calm emotions, Haste, Slow, Freedom of movement, Dimension door) | Grande foulée, Sanctuaire, Flou, Apaisement des émotions, Hâte, Lenteur, Liberté de mouvement, Porte dimensionnelle | corrigé |
| 🟠 mineur | Horloger / sorts_domaine | « Temporal stasis » inexistant et Time stop (Arrêt du temps, niveau 9) inaccessible au niveau 17 | Remplacés par Immobilisation de monstre et Passe-muraille (niveau 5) | corrigé |
| 🟠 mineur | Incantation | Ne précise ni sorts mineurs, ni nombre de sorts préparés, ni DD | 2/3/4 sorts mineurs (niv. 1/10/14) ; préparés = mod. Int + moitié du niveau ; outils requis comme focaliseur | corrigé |
| 🟠 mineur | Infusion d'objets | Nom non officiel « Influx d'objet » (renommé) | Infusion d'objets (Infuse Item, Tasha) | corrigé |
| 🟠 mineur | Le bon outil pour la tâche | Nom non officiel « Outil de circonstance » (renommé) | Le bon outil pour la tâche (The Right Tool for the Job) | corrigé |
| 🟠 mineur | Âme de l'artifice | Ne précise pas réaction ni « sans être tué sur le coup » | Réaction quand vous tombez à 0 PV sans mourir : terminer une infusion pour rester à 1 PV | corrigé |
| 🟠 mineur | Éclair de génie | Nom non officiel « Trait de génie » (renommé) | Éclair de génie (Flash of Genius) | corrigé |

### Barbare (corrigé) — 36 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Capacités de classe optionnelles | Connaissance primitive (TCE) absente | Niv. 3 et niv. 10 : maîtrise d'une compétence de la liste du barbare | corrigé |
| 🔴 majeur | Capacités de classe optionnelles | Bond instinctif (TCE) absent | Niv. 7 : en entrant en rage, déplacement de la moitié de la vitesse avec la même action bonus | corrigé |
| 🔴 majeur | Rage | Aucun nombre d'utilisations indiqué | 2 rages, 3 au niv. 3, 4 au niv. 6, 5 au niv. 12, 6 au niv. 17, illimitées au niv. 20 ; récupération au repos long | corrigé |
| 🔴 majeur | Rage | Bonus aux dégâts non chiffré | +2 aux dégâts (Force, corps à corps), +3 au niv. 9, +4 au niv. 16 | corrigé |
| 🔴 majeur | Rage | Restrictions absentes | Pas d'armure lourde ; impossible de lancer des sorts ou de se concentrer pendant la rage | corrigé |
| 🔴 majeur | Voie de la Bête / Forme de la bête | Morsure rend 6 PV fixes | PV rendus = bonus de maîtrise, une fois par tour, si moins de la moitié des PV max | corrigé |
| 🔴 majeur | Voie de la Bête / Fureur contagieuse | DD fixe de 14 ; utilisations absentes | DD 8 + maîtrise + Constitution ; utilisations = bonus de maîtrise par repos long | corrigé |
| 🔴 majeur | Voie de la Bête / Hallali | 1 seule créature ; 6 utilisations fixes | Créatures consentantes = modificateur de Constitution (min. 1) à 9 m ; utilisations = bonus de maîtrise par repos long | corrigé |
| 🔴 majeur | Voie de la Magie sauvage / Accès sauvage | DD fixe de 14 | DD = 8 + bonus de maîtrise + modificateur de Constitution | corrigé |
| 🔴 majeur | Voie de la Magie sauvage / Conscience magique | 6 utilisations fixes | Utilisations = bonus de maîtrise par repos long | corrigé |
| 🔴 majeur | Voie de la Magie sauvage / Magie galvanisante | 6 utilisations fixes | Utilisations = bonus de maîtrise par repos long | corrigé |
| 🔴 majeur | Voie des tempêtes - Désert / Aura des tempêtes (Désert) | 6 dégâts de feu fixes | 2 dégâts de feu, 3 au niv. 5, 4 au niv. 10, 5 au niv. 15, 6 au niv. 20 | corrigé |
| 🔴 majeur | Voie des tempêtes - Désert / Tempête déchaînée (Désert) | 10 dégâts de feu fixes | Dégâts de feu = moitié du niveau de barbare (réaction, JS Dex DD 8 + maîtrise + Con) | corrigé |
| 🔴 majeur | Voie des tempêtes - Mer / Aura des tempêtes (Mer) | 4d6 dégâts de foudre dès le niv. 3 | 1d6, 2d6 au niv. 10, 3d6 au niv. 15, 4d6 au niv. 20 ; DD 8 + maîtrise + Constitution | corrigé |
| 🔴 majeur | Voie des tempêtes - Toundra / Aura des tempêtes (Toundra) | 6 PV temporaires fixes | 2 PV temporaires, 3 au niv. 5, 4 au niv. 10, 5 au niv. 15, 6 au niv. 20 | corrigé |
| 🔴 majeur | Voie du Berserker / Présence intimidante | DD fixe de 14 dans les données | DD = 8 + bonus de maîtrise + modificateur de Charisme (PHB), portée 9 m, effrayé jusqu'à la fin du prochain tour | corrigé |
| 🔴 majeur | Voie du Gardien ancestral / Bouclier spirituel | Réduction fixe de 3d6 | 2d6 au niv. 6, 3d6 au niv. 10, 4d6 au niv. 14 | corrigé |
| 🔴 majeur | Voie du Zélote / Enragé par-delà la mort | Mort « si 3 échecs ou à la fin de la rage » | Pas de mort par échecs pendant la rage ; mort à la fin de la rage seulement si toujours à 0 PV | corrigé |
| 🔴 majeur | Voie du Zélote / Guerrier des dieux | Aptitude de niveau 3 manquante | Niv. 3 : les sorts de résurrection lancés sur vous ne requièrent aucune composante matérielle | corrigé |
| 🔴 majeur | Voie du Zélote / Présence zélatrice | Portée de 6 cases (9 m) | Portée de 18 m (60 ft) | corrigé |
| 🔴 majeur | Voie totémique / Chercheur spirituel | Aptitude de niveau 3 manquante | Niv. 3 : Sens animal et Communication avec les animaux en rituels | corrigé |
| 🟠 mineur | Instinct sauvage | « Ne peut plus être surpris » | Le barbare peut être surpris, mais agit normalement au 1er tour s'il entre en rage avant toute autre action | corrigé |
| 🟠 mineur | Rage | Durée et conditions de fin absentes | 1 minute ; fin anticipée si inconscient, ou sans attaque ni dégâts subis depuis le dernier tour, ou au choix (action bonus) | corrigé |
| 🟠 mineur | Rage | Type de dégâts « impact » | Terme officiel français : dégâts contondants | corrigé |
| 🟠 mineur | Rage implacable | Réinitialisation du DD non précisée | Le DD revient à 10 après un repos court ou long | corrigé |
| 🟠 mineur | Sens du danger | Conditions d'application absentes | Ne fonctionne pas si le barbare est aveuglé, assourdi ou neutralisé | corrigé |
| 🟠 mineur | Voie de la Bête / Forme de la bête | Griffes et queue infligent des « dégâts magiques » | Griffes : tranchants ; queue : perforants (allonge 3 m) ; caractère magique acquis au niv. 6 | corrigé |
| 🟠 mineur | Voie de la Bête / Âme bestiale | Armes naturelles magiques non mentionnées | Niv. 6 : les armes naturelles comptent comme magiques ; choix du bienfait après chaque repos court ou long | corrigé |
| 🟠 mineur | Voie de la Magie sauvage / Riposte capricieuse | Déclencheur « attaqué » | Déclencheur : subir des dégâts ou rater un jet de sauvegarde pendant la rage | corrigé |
| 🟠 mineur | Voie des tempêtes - Mer / Tempête déchaînée (Mer) | Déclencheur « une créature vous touche » | Déclencheur : lorsque VOUS touchez une créature dans l'aura (réaction), JS Force ou à terre | corrigé |
| 🟠 mineur | Voie des tempêtes - Toundra / Tempête déchaînée (Toundra) | Déclencheur « une créature vous touche » | Déclencheur : à chaque activation de l'aura, une créature dans l'aura fait un JS Force ou vitesse 0 | corrigé |
| 🟠 mineur | Voie du Berserker / Représailles | Déclencheur « dégâts au corps à corps » | Déclencheur : dégâts infligés par une créature située à 1,50 m ou moins (quelle que soit l'attaque) | corrigé |
| 🟠 mineur | Voie du Gardien ancestral / Consulter les esprits | « 1 fois par repos » imprécis | Une utilisation, récupérée après un repos court ou long ; sans emplacement ni composantes matérielles | corrigé |
| 🟠 mineur | Voie totémique - Aigle / Harmonisation totémique (Aigle) | « Voler pour 1 tour » | Vitesse de vol égale à la vitesse au sol pendant la rage, uniquement durant votre tour | corrigé |
| 🟠 mineur | Voie totémique - Loup / Harmonisation totémique (Loup) | Condition de toucher absente | Action bonus pour jeter à terre une créature de taille G ou inférieure après l'avoir touchée au corps à corps | corrigé |
| 🔵 info | Voie du Zélote / Fureur divine | « moitié de votre niveau » sans préciser la classe | 1d6 + moitié du niveau de barbare | corrigé |

### Barde (corrigé) — 32 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Barde / Inspiration bardique (d6) | Aucun nombre d'utilisations ni portée indiqués | Utilisations = modificateur de Charisme (min. 1) par repos long ; cible à 18 m qui peut vous entendre | corrigé |
| 🔴 majeur | Collège de l'Éloquence / Discours universel | Une seule créature, sans durée ni limite | Créatures = modificateur de Charisme à 18 m, 1 heure, 1/repos long ou emplacement de sort | corrigé |
| 🔴 majeur | Collège de l'Éloquence / Inspiration contagieuse | 1 fois par repos long | Utilisations = modificateur de Charisme (min. 1) par repos long, déclenchée par une réussite | corrigé |
| 🔴 majeur | Collège de l'Éloquence / Paroles déstabilisantes | Malus appliqué à un jet d'attaque | Malus au prochain jet de sauvegarde de la cible avant le début de votre prochain tour | corrigé |
| 🔴 majeur | Collège de la Création / Crescendo créatif | Limité à 2 objets | Objets = modificateur de Charisme (min. 2), sans limite de valeur en po | corrigé |
| 🔴 majeur | Collège de la Création / Créativité concrète | Valeur max 400 po, taille M, durée 6 h fixes | Valeur 20 × niveau de barde po, taille M/G/TG selon le niveau, durée = bonus de maîtrise heures | corrigé |
| 🔴 majeur | Collège de la Création / Grain de potentiel | PV temp. = dé + 1 ; dégâts de tonnerre sans sauvegarde ni zone | PV temp. = dé + modificateur de Charisme ; tonnerre sur la cible et créatures à 1,50 m, JS de Constitution | corrigé |
| 🔴 majeur | Collège de la Séduction / Apparence inspirante | 14 PV temporaires fixes à une seule cible | 5/8/11/14 PV temp. (niv. 3/5/10/15) à un nombre de créatures = modificateur de Charisme, à 18 m, action bonus | corrigé |
| 🔴 majeur | Collège de la Séduction / Majesté inébranlable | Liée à Apparence majestueuse, sauvegarde non précisée | Aptitude autonome : action bonus, 1 min, JS de Charisme contre le DD des sorts, 1/repos court ou long | corrigé |
| 🔴 majeur | Collège de la Séduction / Représentation envoûtante | 1 créature, durée 1 min, 1 fois par repos long | Prestation d'1 min, humanoïdes = modificateur de Charisme à 18 m, charme 1 h, 1/repos court ou long | corrigé |
| 🔴 majeur | Collège de la Séduction / sorts_domaine | Liste de 10 sorts de collège présente | Le Collège de la Séduction (XGE) n'accorde aucun sort supplémentaire | corrigé |
| 🔴 majeur | Collège des Murmures / Lame psychique | 8d6 dégâts dès le niveau 3 | 2d6 (niv. 3), 3d6 (niv. 5), 5d6 (niv. 10), 8d6 (niv. 15), une fois par round | corrigé |
| 🔴 majeur | Collège des Murmures / sorts_domaine | Liste de 10 sorts de collège présente | Le Collège des Murmures (XGE) n'accorde aucun sort supplémentaire | corrigé |
| 🔴 majeur | Collège des Épées / sorts_domaine | Liste de 10 sorts de collège présente | Le Collège des Épées (XGE) n'accorde aucun sort supplémentaire | corrigé |
| 🟠 mineur | Barde / Capacités de classe optionnelles | Option de Tasha absente : Sorts de barde supplémentaires (niv. 1) | TCE ajoute des sorts à la liste de barde (ex. Couleurs dansantes, Mot de guérison de groupe…) | corrigé |
| 🟠 mineur | Barde / Capacités de classe optionnelles | Option de Tasha absente : Inspiration magique (niv. 2) | Le dé d'Inspiration peut s'ajouter aux soins ou aux dégâts d'un sort lancé par son détenteur | corrigé |
| 🟠 mineur | Barde / Capacités de classe optionnelles | Option de Tasha absente : Polyvalence bardique (niv. 4) | À chaque amélioration de caractéristique, échanger une compétence d'Expertise ou un sort mineur | corrigé |
| 🟠 mineur | Barde / Secrets magiques | Ne précise pas que les sorts mineurs sont éligibles ni le décompte | Sorts mineurs compris ; comptent dans les sorts connus, niveau lançable requis | corrigé |
| 🟠 mineur | Collège de l'Éloquence / Faconde | « inférieur à 9 » | Résultat de 9 ou moins compté comme 10 | corrigé |
| 🟠 mineur | Collège de la Discorde / sorts_domaine | « Cri de banshee » inexistant ; « Mot de pouvoir douleur » est un sort de niveau 7 | Remplacer par des sorts valides du niveau correspondant | corrigé |
| 🟠 mineur | Collège de la Séduction / Apparence majestueuse | Durée et limite d'utilisation absentes | 1 minute (concentration), Injonction en action bonus chaque tour, 1/repos long | corrigé |
| 🟠 mineur | Collège de la Séduction / sorts_domaine | « Calme emotions » (anglais/coquille) et « Dissimulation » (sort inexistant) | Calme émotions ; pas de sort « Dissimulation » en 5e | corrigé |
| 🟠 mineur | Collège de la Vaillance / Maîtrises supérieures | Nom différent de la traduction officielle | Maîtrises supplémentaires | corrigé |
| 🟠 mineur | Collège des Commandants / sorts_domaine | « Claire-voie » et « Ralliement de masse » : sorts inexistants | Clairvoyance ? ; aucun sort « Ralliement de masse » en 5e | corrigé |
| 🟠 mineur | Collège des Murmures / Mots de terreur | Condition de conversation seul à seul d'1 minute omise | Humanoïde seul avec vous pendant au moins 1 minute, JS de Sagesse | corrigé |
| 🟠 mineur | Collège des Murmures / Voile de murmure | Capture de l'ombre (réaction, mort à 9 m) omise | Réaction quand un humanoïde meurt à 9 m ; déguisement 1 h ; Tromperie + 5 | corrigé |
| 🟠 mineur | Collège des Murmures / sorts_domaine | « Disguise self », « Invisible » (anglais/erroné), « Sonde mentale » (inexistant) | Déguisement ; Invisibilité ; pas de sort « Sonde mentale » en 5e | corrigé |
| 🟠 mineur | Collège des Épées / Maîtrises supérieures | Nom non officiel et focaliseur d'arme omis | Maîtrises supplémentaires ; une arme de corps à corps maîtrisée peut servir de focaliseur | corrigé |
| 🟠 mineur | Collège des Épées / Moulinet | Effets Tranchant et Mobile imprécis (1 cible / 1 case) | Tranchant : autre créature à 1,50 m ; Mobile : 1,50 m + 30 cm par point du dé puis déplacement en réaction | corrigé |
| 🟠 mineur | Collège des Épées / Style de combat | Style nommé « Duelliste » | Style « Duel » | corrigé |
| 🟠 mineur | Collège des Épées / sorts_domaine | « Skin of stone » (anglais) et « Entrave » (sort inexistant) | Peau de pierre ; Immobilisation de personne | corrigé |
| 🔵 info | Barde / Secrets magiques supplémentaires, Secrets magiques ultimes | Noms inventés pour les niveaux 14 et 18 | Le PHB répète simplement « Secrets magiques » aux niveaux 14 et 18 | corrigé |

### Clerc (corrigé) — 83 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Clerc / Intervention divine | Aucun délai après une réussite, ni coût en action ni réessai après repos long | Action ; après une réussite, 7 jours d'attente ; après un échec, nouvel essai après un repos long | corrigé |
| 🔴 majeur | Domaine de l'Arcane (Communauté) / sorts_domaine | Projectiles magiques, Fracassement, Protection contre l'énergie, « Œil mystique », Bannissement, Création | Arcanes (SCAG) : Détection de la magie, Projectile magique, Arme magique, Aura magique de Nystul, Dissipation de la magie, Cercle magique, Œil magique, Coffre secret de Léomund, Lien planaire, Cercle de téléportation | corrigé |
| 🔴 majeur | Domaine de l'Ordre / Impact divin | +2d8 dès le niveau 8 | 1d8 psychiques au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine de l'Ordre / La loi incarnée | 1 utilisation par repos long | Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long | corrigé |
| 🔴 majeur | Domaine de l'Ordre / sorts_domaine | « Lueur de vérité » (inexistant) et « Mots d'éloquence » (inexistant) | Héroïsme, Injonction, Immobilisation de personne, Zone de vérité, Lenteur, Communication à distance, Compulsion, Localisation de créature, Communion, Domination de personne | corrigé |
| 🔴 majeur | Domaine de la Forge / Impact divin | +2d8 dès le niveau 8 | 1d8 feu au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine de la Forge / sorts_domaine | Colonne de feu, Châtiment d'aveuglement, « Arme chauffée », « Protections élémentaires » | Identification, Châtiment incandescent, Chauffer le métal, Arme magique, Arme élémentaire, Protection contre l'énergie, Fabrication, Mur de feu, Animation d'objets, Création | corrigé |
| 🔴 majeur | Domaine de la Guerre / Conduit divin : Dieu de la guerre | Obtenu au niveau 2 | Bénédiction du dieu de la guerre : niveau 6 | corrigé |
| 🔴 majeur | Domaine de la Guerre / Impact divin | +2d8 dès le niveau 8 | 1d8 au niveau 8, 2d8 au niveau 14 ; dégâts du type de l'arme | corrigé |
| 🔴 majeur | Domaine de la Guerre / Prêtre de guerre | 1 utilisation par repos long | Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long | corrigé |
| 🔴 majeur | Domaine de la Guerre / sorts_domaine | Fracassement, Fléau d'insectes et « Colonne de feu » dans la liste | Faveur divine, Bouclier de la foi, Arme magique, Arme spirituelle, Manteau du croisé, Esprits gardiens, Liberté de mouvement, Peau de pierre, Colonne de flamme, Immobilisation de monstre | corrigé |
| 🔴 majeur | Domaine de la Lumière / Conduit divin : Radiance de l'aube | Jet de sauvegarde de Sagesse | Jet de sauvegarde de Constitution ; 2d10 + niveau de clerc radiants, moitié si réussite | corrigé |
| 🔴 majeur | Domaine de la Lumière / Illumination protectrice | 2 utilisations par repos long | Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long | corrigé |
| 🔴 majeur | Domaine de la Lumière / sorts_domaine | « Flamme colossale » (inexistant) et « Colonne de feu » ; « Lueur féérique » mal orthographié | Mains brûlantes, Lueur féerique, Sphère de feu, Rayon ardent, Boule de feu, Lumière du jour, Gardien de la foi, Mur de feu, Colonne de flamme, Scrutation | corrigé |
| 🔴 majeur | Domaine de la Mort / Conduit divin : Caresse de la mort | +45 dégâts nécrotiques fixes | Toucher de la mort : 5 + 2 × niveau de clerc dégâts nécrotiques, sur une attaque au corps à corps qui touche | corrigé |
| 🔴 majeur | Domaine de la Mort / Impact divin | +2d8 dès le niveau 8 | 1d8 nécrotiques au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine de la Mort / sorts_domaine | Faux repos, Frayeur, Peur, Fléau, Fléau d'insectes, « Vampirisme », « Rayon d'affaiblissement » | Simulacre de vie, Rayon empoisonné, Cécité/Surdité, Rayon affaiblissant, Animation des morts, Caresse du vampire, Flétrissement, Protection contre la mort, Brume mortelle, Contagion | corrigé |
| 🔴 majeur | Domaine de la Nature / Atténuation des éléments | Limité à 1 fois par combat | Réaction, sans limite d'utilisations (acide, froid, feu, foudre, tonnerre ; vous ou créature à 9 m) | corrigé |
| 🔴 majeur | Domaine de la Nature / Impact divin | +2d8 dès le niveau 8 (« attaque d'énergie ») | Attaque d'arme : 1d8 froid, feu ou foudre au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine de la Nature / sorts_domaine | Noms faux ou sorts erronés (Parler avec les animaux, Murailles de ronces, Domination d'animal, Lianes étouffantes, Communion avec la nature) | Amitié avec les animaux, Communication avec les animaux, Peau d'écorce, Croissance d'épines, Croissance végétale, Mur de vent, Domination de bête, Liane avide, Fléau d'insectes, Passage par les arbres | corrigé |
| 🔴 majeur | Domaine de la Paix / Conduit divin : Baume de la paix | Soins de 2d6 + 1 | 2d6 + modificateur de Sagesse (min. 1) par créature croisée à 1,50 m | corrigé |
| 🔴 majeur | Domaine de la Paix / Lien de hardiesse | 6 créatures fixes ; durée et utilisations absentes | Bonus de maîtrise créatures, 10 minutes, bonus de maîtrise utilisations par repos long ; 1d4 une fois par tour | corrigé |
| 🔴 majeur | Domaine de la Paix / sorts_domaine | Bénédiction, « Warding Bond » (anglais), « Don de balistique » (inexistant), Protection contre la mort, Divination, « Sanctuaire protecteur », Rappel à la vie, Communion | Héroïsme, Sanctuaire, Aide, Lien de protection, Lueur d'espoir, Communication à distance, Aura de pureté, Sanctuaire privé de Mordenkainen, Restauration supérieure, Lien télépathique de Rary | corrigé |
| 🔴 majeur | Domaine de la Ruse / Impact divin | +2d8 dès le niveau 8 | 1d8 poison au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine de la Ruse / sorts_domaine | Désorientation, Silence, Clairvoyance, Dissimulation à la place des sorts officiels | Charme-personne, Déguisement, Image miroir, Passage sans trace, Clignotement, Dissipation de la magie, Porte dimensionnelle, Métamorphose, Domination de personne, Modification de mémoire | corrigé |
| 🔴 majeur | Domaine de la Tempête / Fureur de l'ouragan | 2 utilisations par repos long | Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long | corrigé |
| 🔴 majeur | Domaine de la Tempête / Impact divin | +2d8 dès le niveau 8 | 1d8 tonnerre au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine de la Tempête / sorts_domaine | « Tempête de sleet » (anglais), « Rafale de vent », Liberté de mouvement, « Insectes dévorants » | Nappe de brouillard, Vague tonnante, Bourrasque, Fracassement, Appel de la foudre, Tempête de neige, Contrôle de l'eau, Tempête de grêle, Vague destructrice, Fléau d'insectes | corrigé |
| 🔴 majeur | Domaine de la Tombe / Conduit divin : Chemin de la tombe | Vulnérabilité à tous les dégâts sans limite | Vulnérabilité aux dégâts de la prochaine attaque qui touche seulement (malédiction jusqu'à la fin de votre prochain tour) | corrigé |
| 🔴 majeur | Domaine de la Tombe / Sentinelle au seuil de la mort | 2 utilisations par repos | Réaction ; un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long | corrigé |
| 🔴 majeur | Domaine de la Tombe / sorts_domaine | Bénédiction, Sanctuaire, Repos éternel, Animation des morts, Fléau (mal placé), Contagion, « Mortaise suprême » (inexistant), « Rappeler à la vie » | Fléau, Simulacre de vie, Doux repos, Rayon affaiblissant, Retour à la vie, Caresse du vampire, Bannissement, Protection contre la mort, Coquille antivie, Rappel à la vie | corrigé |
| 🔴 majeur | Domaine de la Vie / Conduit divin : Survivance | Soigne 100 PV fixes sur une cible | Préservation de la vie : 5 × niveau de clerc PV répartis à 9 m, max. moitié des PV max de chaque cible | corrigé |
| 🔴 majeur | Domaine de la Vie / Impact divin | +2d8 dès le niveau 8 | 1d8 radiants au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine de la Vie / sorts_domaine | Esprits gardiens, Divination, « Restauration suprême », « Fanal d'espoir » ; manque Retour à la vie, Protection contre la mort, Gardien de la foi | Bénédiction, Soins, Restauration partielle, Arme spirituelle, Lueur d'espoir, Retour à la vie, Protection contre la mort, Gardien de la foi, Soins de groupe, Rappel à la vie | corrigé |
| 🔴 majeur | Domaine du Crépuscule / Foulée nocturne | 6 utilisations par repos long ; nom | Foulée crépusculaire : bonus de maîtrise fois par repos long, vol 1 minute | corrigé |
| 🔴 majeur | Domaine du Crépuscule / Impact divin | +2d8 dès le niveau 8 | 1d8 radiants au niveau 8, 2d8 au niveau 14 | corrigé |
| 🔴 majeur | Domaine du Crépuscule / sorts_domaine | Invisibilité, Vol, Sphère d'invisibilité, Aura de pureté, « Ombre trompeuse », Cercle de téléportation | Lueur féerique, Sommeil, Rayon de lune, Voir l'invisible, Aura de vitalité, Petite hutte de Léomund, Aura de vie, Invisibilité supérieure, Cercle de pouvoir, Double illusoire | corrigé |
| 🔴 majeur | Domaine du Savoir / sorts_domaine | Détection des pensées, Clairvoyance, Langues, Divination, « Œil mystique », « Légende » | Injonction, Identification, Augure, Suggestion, Antidétection, Communication avec les morts, Œil magique, Confusion, Mythes et légendes, Scrutation | corrigé |
| 🟠 mineur | Clerc / Capacités de classe optionnelles (Tasha) | Absente : Sorts de clerc supplémentaires (niveau 1) | Ajoute à la liste du clerc : Aura de vitalité, Linceul spirituel (3), Aura de vie, Aura de pureté (4), Rayon de soleil (6), Explosion solaire (8), Mot de pouvoir guérisseur (9) | corrigé |
| 🟠 mineur | Clerc / Capacités de classe optionnelles (Tasha) | Absente : Conduit divin : Canalisation de puissance divine (niveau 2) | Action bonus + Conduit divin : récupère un emplacement de niveau ≤ moitié du bonus de maîtrise (arrondi sup.) ; 1/2/3 fois par repos long (niv. 2/6/18) | corrigé |
| 🟠 mineur | Clerc / Capacités de classe optionnelles (Tasha) | Absente : Sorts mineurs polyvalents (niveau 4) | À chaque Amélioration de caractéristique, remplacer un sort mineur de clerc par un autre | corrigé |
| 🟠 mineur | Clerc / Capacités de classe optionnelles (Tasha) | Absente : Frappes bénies (niveau 8) | Remplace Frappe divine / Incantation puissante : 1d8 dégâts radiants une fois par tour (sort mineur ou arme) | corrigé |
| 🟠 mineur | Clerc / Conduit divin : Renvoi des morts-vivants | Omet la fin sur dégâts et les restrictions d'action | Renvoyé 1 minute ou jusqu'à subir des dégâts ; pas de réaction ; action limitée à Foncer/se libérer (DD des sorts) | corrigé |
| 🟠 mineur | Clerc / Destruction des morts-vivants | Faute de frappe « Détruction » dans les 5 entrées (FP 1/2 à FP 4) | Nom officiel : « Destruction des morts-vivants » | corrigé |
| 🟠 mineur | Clerc / Intervention divine garantie | Ne rappelle pas le délai de 7 jours après réussite | Au niveau 20 la réussite est automatique, mais le délai de 7 jours s'applique toujours | corrigé |
| 🟠 mineur | Domaine de l'Arcane (Communauté) / aptitudes | Noms et effets approximatifs (Domptage d'énergie, Bannières profanes, Soins épurateurs) | Initié aux arcanes (Arcanes + 2 sorts mineurs de magicien), Abjuration arcanique, Briseur de sorts, Incantation puissante, Maîtrise des arcanes | corrigé |
| 🟠 mineur | Domaine de l'Arcane (Communauté) / source | Champ "source" absent/vide | Domaine des Arcanes officiel : Sword Coast Adventurer's Guide (SCAG) | corrigé |
| 🟠 mineur | Domaine de l'Ordre / Maîtrises sup. & Voie de l'autorité | Maîtrise de compétence absente | Armures lourdes + Intimidation ou Persuasion | corrigé |
| 🟠 mineur | Domaine de l'Ordre / source | Champ "source" absent/vide | Tasha's Cauldron of Everything (TCE) | corrigé |
| 🟠 mineur | Domaine de la Forge / Saint de la forge et du feu | Résistance sans restriction | Résistance contondant/perforant/tranchant des attaques non magiques, en armure lourde | corrigé |
| 🟠 mineur | Domaine de la Forge / source | Champ "source" absent/vide | Xanathar's Guide to Everything (XGE) | corrigé |
| 🟠 mineur | Domaine de la Guerre / Avatar de bataille | Résistance sans restriction | Résistance contondant/perforant/tranchant des armes non magiques uniquement | corrigé |
| 🟠 mineur | Domaine de la Guerre / source | Champ "source" absent/vide | Manuel des joueurs (PHB) | corrigé |
| 🟠 mineur | Domaine de la Lumière / source | Champ "source" absent/vide | Manuel des joueurs (PHB) | corrigé |
| 🟠 mineur | Domaine de la Mort / Destruction inéluctable | S'applique à tous les dégâts nécrotiques | Seulement aux dégâts nécrotiques des sorts de clerc et du Conduit divin | corrigé |
| 🟠 mineur | Domaine de la Mort / source | Champ "source" absent/vide | Guide du maître (DMG) | corrigé |
| 🟠 mineur | Domaine de la Nature / source | Champ "source" absent/vide | Manuel des joueurs (PHB) | corrigé |
| 🟠 mineur | Domaine de la Paix / Incantation puissante | « Ajoute des dégâts » imprécis | Ajoute le modificateur de Sagesse aux dégâts des sorts mineurs de clerc | corrigé |
| 🟠 mineur | Domaine de la Paix / Maîtrises sup. & Lien de hardiesse | Maîtrise Instrument de paix absente | Maîtrise d'Intuition, Persuasion ou Représentation | corrigé |
| 🟠 mineur | Domaine de la Paix / source | Champ "source" absent/vide | Tasha's Cauldron of Everything (TCE) | corrigé |
| 🟠 mineur | Domaine de la Ruse / Conduit divin : Linceul d'ombre | Durée non précisée | Invisible jusqu'à la fin de votre prochain tour (fin si attaque ou sort) | corrigé |
| 🟠 mineur | Domaine de la Ruse / Faveur du filou | Nom et cible imprécis | Bénédiction du filou : créature consentante autre que vous, avantage Discrétion 1 heure | corrigé |
| 🟠 mineur | Domaine de la Ruse / source | Champ "source" absent/vide | Manuel des joueurs (PHB) | corrigé |
| 🟠 mineur | Domaine de la Tempête / Choc foudroyant | Pas de limite de taille | Repousse de 3 m une créature de taille Grande ou inférieure | corrigé |
| 🟠 mineur | Domaine de la Tempête / source | Champ "source" absent/vide | Manuel des joueurs (PHB) | corrigé |
| 🟠 mineur | Domaine de la Tombe / Cercle de la mort & Yeux de la tombe | Nom « Cercle de la mort » ; utilisations de Yeux de la tombe et portée d'Épargner les mourants absentes | Cercle de mortalité ; Épargner les mourants à 9 m par action bonus ; Yeux de la tombe modificateur de Sagesse fois par repos long | corrigé |
| 🟠 mineur | Domaine de la Tombe / source | Champ "source" absent/vide | Xanathar's Guide to Everything (XGE) | corrigé |
| 🟠 mineur | Domaine de la Vie / Guérisseur béni | Ne précise pas que la cible doit être une autre créature | Se déclenche en soignant une créature autre que vous avec un sort de niveau 1+ | corrigé |
| 🟠 mineur | Domaine de la Vie / source | Champ "source" absent/vide | Manuel des joueurs (PHB) | corrigé |
| 🟠 mineur | Domaine du Crépuscule / Conduit divin : Sanctuaire du crépuscule | Aucune valeur de PV temporaires | 1d6 + niveau de clerc PV temporaires (ou fin de charme/terreur), sphère 9 m, 1 minute | corrigé |
| 🟠 mineur | Domaine du Crépuscule / Maîtrises sup., Yeux de la nuit & Faveur de vigilance | Avantage permanent à l'initiative ; partage de vision non chiffré | Bénédiction de vigilance : action, avantage au prochain jet d'initiative d'une créature ; partage 1 h, 1/repos long | corrigé |
| 🟠 mineur | Domaine du Crépuscule / source | Champ "source" absent/vide | Tasha's Cauldron of Everything (TCE) | corrigé |
| 🟠 mineur | Domaine du Sang (Communauté) / sorts_domaine | « Lien sanglant » inexistant ; « Vampirisme » et « Rayon d'affaiblissement » mal nommés | Remplacer par un sort officiel (ex. Flétrissement) ; noms officiels Caresse du vampire, Rayon affaiblissant | corrigé |
| 🟠 mineur | Domaine du Sang (Communauté) / sorts_domaine (ordre) | Sorts non rangés par niveau (le logiciel débloque les sorts par paires : niveaux 1, 2, 3, 4, 5) | Liste homebrew réordonnée : Fléau, Frayeur / Rayon affaiblissant, Immobilisation de personne / Toucher du vampire, Peur / Flétrissement, Compulsion / Contagion, Fléau d'insectes | corrigé |
| 🟠 mineur | Domaine du Sang (Communauté) / source | Champ "source" absent/vide | Homebrew / communauté (à indiquer) | corrigé |
| 🟠 mineur | Domaine du Savoir / Conduit divin : Lecture des pensées | Portée et lien avec Suggestion absents | Créature à 18 m, sauvegarde de Sagesse ; pensées 1 minute puis Suggestion gratuite (échec automatique) | corrigé |
| 🟠 mineur | Domaine du Savoir / source | Champ "source" absent/vide | Manuel des joueurs (PHB) | corrigé |
| 🔵 info | Clerc / Frappe divine / Incantation puissante (niveau 8) | Aptitude de domaine dupliquée dans les capacités de base | Dans le PHB, Frappe divine ou Incantation puissante est une aptitude du domaine (déjà présente dans chaque sous-classe) | corrigé |
| 🔵 info | Clerc / Frappe divine améliorée (niveau 14) | Palier de domaine placé dans les capacités de base | Le passage à 2d8 au niveau 14 fait partie de l'aptitude Frappe divine de chaque domaine concerné | corrigé |
| 🔵 info | Clerc / Incantation | Description sans nombre de sorts mineurs/préparés, DD ni bonus d'attaque | 3/4/5 sorts mineurs (niv. 1/4/10) ; sorts préparés = modificateur de Sagesse + niveau de clerc ; DD 8 + maîtrise + Sagesse ; rituels | corrigé |
| 🔵 info | Clerc / domaines / Impact divin | Aptitude de niveau 8 nommée « Impact divin » dans 10 domaines | Nom officiel : Frappe divine (1d8 au niveau 8, 2d8 au niveau 14) | corrigé |
| 🔵 info | Clerc / domaines / noms d'aptitudes | Noms non officiels (Dieu de la guerre, Illumination améliorée, Auréole, Cordialité avec la faune et la flore, Faveur du filou, Faveur érudite, Savoir ancestral, Choc foudroyant, Enfant de la tempête, Survivance, Caresse de la mort, Foulée nocturne, Règne de l'ordre, La loi incarnée) | Bénédiction du dieu de la guerre, Illumination protectrice améliorée, Couronne de lumière, Charme des animaux et des plantes, Bénédiction du filou, Bénédictions du savoir, Savoir des âges, Frappe de l'éclair, Né de la tempête, Préservation de la vie, Toucher de la mort, Foulée crépusculaire, Exigence de l'ordre, Incarnation de la loi | corrigé |
| 🔵 info | Domaine de l'Ordre / Courroux de l'ordre | « 1 fois/tour » conforme | Limité à une malédiction par tour (pas de limite par repos) ; +2d8 psychiques sur la prochaine attaque d'un allié | corrigé |

### Druide (corrigé) — 38 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Cercle de la Terre / Sorts de cercle | Choix du terrain non modélisé (liste Forêt imposée) | Champ « terrains » (8 listes officielles du PHB) + sélecteur « Terrain » dans l'onglet Classes ; les sorts de cercle suivent le terrain choisi | corrigé |
| 🔴 majeur | Cercle de la Terre / sorts_domaine | Liste unique ne correspondant à aucun terrain (Nappe de brouillard et Lien avec les bêtes sont du niveau 1, Fléau et Rappel à la vie absents des listes) | Remplacée par la liste officielle du terrain Forêt (Peau d'écorce, Pattes d'araignée, Appel de la foudre, Croissance végétale, Divination, Liberté de mouvement, Communion avec la nature, Passage par les arbres) | corrigé |
| 🔴 majeur | Cercle des Astres / Présage cosmique | 6 utilisations par repos long | Utilisations = bonus de maîtrise par repos long ; réaction, 9 m, ±1d6 | corrigé |
| 🔴 majeur | Cercle des Astres / sorts_domaine | Liste de sorts inventée, dont « Périple planétaire » (inexistant) | Le Cercle des Étoiles (TCE) n'a pas de sorts de cercle ; seule Éclair traçant (toujours préparé via la Carte stellaire) est conservé | corrigé |
| 🔴 majeur | Cercle des Fournaises (Wildfire) / Convocation des fournaises | DD fixe de 14 | DD = 8 + bonus de maîtrise + modificateur de Sagesse (DD des sorts) | corrigé |
| 🔴 majeur | Cercle des Fournaises (Wildfire) / Flammes cautérisantes | 6 utilisations par repos long | Utilisations = bonus de maîtrise par repos long ; 2d10 + modificateur de Sagesse | corrigé |
| 🔴 majeur | Cercle des Fournaises (Wildfire) / sorts_domaine | Châtiment incandescent, Boule de feu, Mur de feu hors liste ; manquent Soins, Croissance végétale, Retour à la vie, Aura de vie, Bouclier de feu, Colonne de flamme, Soins de groupe | Niv. 2 Mains brûlantes, Soins ; niv. 3 Sphère de feu, Rayon ardent ; niv. 5 Croissance végétale, Retour à la vie ; niv. 7 Aura de vie, Bouclier de feu ; niv. 9 Colonne de flamme, Soins de groupe | corrigé |
| 🔴 majeur | Cercle des Rêves / Baume de la cour d'été | Réserve fixe de 10d6 | Réserve de d6 égale au niveau de druide ; au plus la moitié du niveau de druide en dés par action bonus ; portée 36 m ; 1 PV temporaire par dé ; recharge au repos long | corrigé |
| 🔴 majeur | Cercle des Rêves / Chemins secrets | 1 fois par repos long ; action bonus pour les deux usages | Utilisations = modificateur de Sagesse (min. 1) par repos long ; téléportation d'autrui par une action et au contact | corrigé |
| 🔴 majeur | Cercle des Rêves / sorts_domaine | Liste de sorts de cercle inventée | Le Cercle des Rêves (XGE) n'a pas de sorts de cercle : liste vidée | corrigé |
| 🔴 majeur | Cercle des Spores / Animation fongique | 1 fois par repos long | Utilisations = modificateur de Sagesse (min. 1) par repos long (TCE) | corrigé |
| 🔴 majeur | Cercle des Spores / sorts_domaine | « Fléau d'immunité » inexistant ; Fléau d'insectes hors liste ; manquent Doux repos, Confusion, Brume mortelle, Contagion | Liste officielle : Cécité/Surdité, Doux repos (« Préservation des morts » dans la base), Animation des morts, Forme gazeuse, Flétrissement, Confusion, Brume mortelle, Contagion | corrigé |
| 🔴 majeur | Cercle du Berger / Esprit protecteur | Limité à l'aura du totem de la licorne ; soins non chiffrés | Fonctionne avec n'importe quel Totem spirituel ; soins = moitié du niveau de druide (XGE) | corrigé |
| 🔴 majeur | Cercle du Berger / sorts_domaine | Liste de sorts de cercle inventée | Le Cercle du Berger (XGE) n'a pas de sorts de cercle : liste vidée | corrigé |
| 🟠 mineur | Archidruide | Omet les composantes matérielles | Ignore aussi les composantes matérielles sans coût et non consommées (PHB) | corrigé |
| 🟠 mineur | Cercle de la Lune / Forme sauvage de combat & Formes du cercle | Omet la progression de FP au-delà du niveau 2 ; « Guérison sauvage » n'est pas un nom officiel | Formes du cercle : FP 1 au niv. 2, puis niveau de druide / 3 (arrondi inférieur) dès le niv. 6 ; soins 1d8 par niveau d'emplacement inclus dans Forme sauvage de combat ; renommée « Formes du cercle » | corrigé |
| 🟠 mineur | Cercle de la Lune / Mille formes | Nom « Mille visages » non officiel | Thousand Forms : « Mille formes » (PHB) ; renommée | corrigé |
| 🟠 mineur | Cercle de la Mutation / sorts_domaine | « Faux repos » et « Altération » n'existent pas | Remplacés par Simulacre de vie (False Life) et Modification d'apparence (Alter Self) | corrigé |
| 🟠 mineur | Cercle de la Sangsue / sorts_domaine | « Vampirism » en anglais ; « Rayon d'affaiblissement » absent de la base | Remplacés par Toucher du vampire (Vampiric Touch) et Rayon affaiblissant (Ray of Enfeeblement) | corrigé |
| 🟠 mineur | Cercle de la Terre / Ressourcement | Omet la limite d'usage et l'arrondi | Une fois par repos long ; moitié du niveau arrondie au supérieur ; aucun emplacement de niveau 6+ | corrigé |
| 🟠 mineur | Cercle de la Terre / Sanctuaire de dame nature | DD et immunité de 24 h non précisés | JS de Sagesse contre le DD des sorts ; en cas de réussite immunité 24 h | corrigé |
| 🟠 mineur | Cercle des Astres / Carte stellaire & Forme stellaire | Éclair traçant « gratuitement » sans limite | Éclair traçant sans emplacement un nombre de fois égal au bonus de maîtrise par repos long ; Forme stellaire par une action bonus, 10 minutes | corrigé |
| 🟠 mineur | Cercle des Astres / Constellation scintillante | Omet le vol du Dragon | Archer/Calice 2d8 ; Dragon : vitesse de vol 6 m et surplace | corrigé |
| 🟠 mineur | Cercle des Fournaises (Wildfire) / Convocation des fournaises | Profil de l'esprit absent ; « durée 1 h » comme aura de dégâts | Esprit : CA 13, PV 5 + 5 × niveau de druide, vol 9 m, Graine de flamme et Téléportation ardente ; les 2d6 ne s'appliquent qu'à l'apparition | corrigé |
| 🟠 mineur | Cercle des Fournaises (Wildfire) / Flammes cautérisantes | Nom non officiel « Cautère spectrale » | Cauterizing Flames : « Flammes cautérisantes » ; renommée | corrigé |
| 🟠 mineur | Cercle des Fournaises (Wildfire) / Lien amélioré | +1d8 à tout sort de dégâts | Seulement aux sorts infligeant des dégâts de feu ou rendant des PV | corrigé |
| 🟠 mineur | Cercle des Fournaises (Wildfire) / Renaissance flamboyante | Limite d'usage non précisée | Une fois par repos long | corrigé |
| 🟠 mineur | Cercle des Rêves / sorts_domaine | Faute de frappe « Calme des emotions » | Sans objet : la liste inventée a été vidée | corrigé |
| 🟠 mineur | Cercle des Spores / Symbiote & Halo de spores | Sort mineur Contact glacial absent ; PV temporaires et progression du Halo non chiffrés | Contact glacial (niv. 2) ; Symbiote = 4 PV temporaires par niveau de druide ; Halo 1d4/1d6/1d8/1d10 (niv. 2/6/10/14) | corrigé |
| 🟠 mineur | Cercle du Berger / Invocation loyale | « Indice de Puissance » | « Facteur de puissance » (FP) | corrigé |
| 🟠 mineur | Cercle du Berger / Langage de la forêt & Totem spirituel | Esprit « Aigle » ; utilisation non précisée | Esprits Ours, Faucon, Licorne ; 1 fois par repos court ou long ; aura de 9 m, 1 minute | corrigé |
| 🟠 mineur | Compagnon sauvage (option Tasha) | « Esprit familier sous forme de bête » sans détails | Action + 1 utilisation de Forme sauvage : sort Appel de familier sans composante matérielle, familier de type fée, durée = moitié du niveau de druide en heures (TCE) ; renommée « (option Tasha) » | corrigé |
| 🟠 mineur | Forme sauvage | Description très incomplète ; « action bonus ou action » ambigu | Action (action bonus seulement pour le Cercle de la Lune) ; 2 utilisations par repos court ou long ; durée = moitié du niveau de druide en heures ; FP 1/4 (ni vol ni nage) niv. 2, 1/2 (pas de vol) niv. 4, 1 niv. 8 ; PV de la bête, report des dégâts excédentaires, pas de sorts | corrigé |
| 🟠 mineur | Polyvalence des sorts mineurs (option Tasha) | Option de classe absente | TCE, niveau 4 (à chaque Amélioration de caractéristique) : remplacer un sort mineur de druide par un autre ; ajoutée | corrigé |
| 🟠 mineur | Sorts de bête | « À l'exception des composantes matérielles coûteuses » | Sous forme de bête, aucune composante matérielle ne peut être fournie (PHB) | corrigé |
| 🔵 info | Cercle de la Mutation / sorts_domaine | « Métamorphose suprême » est un sort de niveau 9 | Remplacé par Réincarnation (niveau 5, thème de transformation) | corrigé |
| 🔵 info | Incantation | Aucune donnée chiffrée | Sorts mineurs 2/3/4 (niv. 1/4/10) ; sorts préparés = modificateur de Sagesse + niveau de druide ; DD 8 + maîtrise + Sagesse ; rituels | corrigé |
| 🔵 info | Sorts de druide supplémentaires (option Tasha) | Option de classe non mentionnée | TCE ajoute des sorts à la liste du druide ; ajoutée au niveau 1 avec la liste étendue | corrigé |

### Ensorceleur (corrigé) — 37 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Capacités de classe optionnelles (TCE) | Guidage magique absent | Niveau 5 : si vous ratez un test de caractéristique, 1 point de sorcellerie pour relancer le d20 (nouveau résultat obligatoire) | corrigé |
| 🔴 majeur | Esprit aberrant / sorts_domaine | Noms faux/inexistants (Désorientation, Armure de mage, Calme des émotions, Tentacules de noirs éboulis, Invocation de béhémoth, Télépathie, Moisson d'esprit) | Bras d'Hadar, Murmures dissonants, Éclat mental ; Apaisement des émotions, Détection des pensées ; Faim d'Hadar, Communication à distance ; Tentacules noirs d'Evard, Invocation d'aberration ; Lien télépathique de Rary, Télékinésie | corrigé |
| 🔴 majeur | Magie des ombres / Chien de mauvais augure | Coût en points absent et 10 PV temporaires fixes | Action bonus, 3 points ; PV temporaires = moitié du niveau d'ensorceleur ; désavantage aux JS contre vos sorts | corrigé |
| 🔴 majeur | Magie des ombres / sorts_domaine | Liste de 10 sorts inventée | Magie des ombres (XGE) n'a pas de liste de sorts étendue (seulement Ténèbres) | corrigé |
| 🔴 majeur | Sorcellerie des tempêtes / Cœur de la tempête & Guide des tempêtes | Dégâts fixes de 10 | Dégâts = moitié du niveau d'ensorceleur | corrigé |
| 🔴 majeur | Sorcellerie des tempêtes / Fureur de la tempête | Dégâts fixes de 20 et DD non précisé | Dégâts de foudre = niveau d'ensorceleur ; JS Force contre DD des sorts | corrigé |
| 🔴 majeur | Sorcellerie des tempêtes / sorts_domaine | Liste de 10 sorts inventée | Sorcellerie des tempêtes (XGE) n'a pas de liste de sorts étendue | corrigé |
| 🔴 majeur | Sorcellerie des tempêtes / Âme du vent | 3 créatures fixes ; vitesse de vol personnelle non précisée | Vol 18 m ; 3 + modificateur de Charisme créatures à 9 m, vol 9 m pendant 1 h ; 1 fois par repos court ou long | corrigé |
| 🔴 majeur | Âme divine / sorts_domaine | Liste de 10 sorts de domaine inventée | Aucune liste étendue : un seul sort d'affinité (Soins, Blessure, Bénédiction, Fléau ou Protection contre le mal et le bien) + accès à la liste de clerc | corrigé |
| 🔴 majeur | Âme mécanique / sorts_domaine | Liste fausse (Compréhension des langues, Zone de vérité, Œil mystique, Bannissement, Création) | Alarme, Protection contre le mal et le bien ; Aide, Restauration partielle ; Dissipation de la magie, Protection contre l'énergie ; Liberté de mouvement, Invocation de créature artificielle ; Mur de force, Restauration supérieure | corrigé |
| 🔴 majeur | Âme mécanique / Équilibre restauré & Sorts d'ordre | 6 utilisations fixes, portée absente | Rétablir l'équilibre : utilisations = bonus de maîtrise par repos long, portée 18 m | corrigé |
| 🟠 mineur | Esprit aberrant / Discours télépathique & Sorts psioniques | Distance 1,5 km et durée 20 min fixes | Distance = modificateur de Charisme en miles (×1,5 km) ; durée = niveau d'ensorceleur en minutes | corrigé |
| 🟠 mineur | Esprit aberrant / Distortion implosive | Faute de frappe « Distortion » ; DD et attraction absents | Distorsion implosive : JS Force contre DD des sorts, 3d10 force + attraction, moitié si réussite | corrigé |
| 🟠 mineur | Esprit aberrant / Magie psionique & Défense psychique | Noms non officiels | Sorcellerie psionique (niveau 6) et Défenses psychiques | corrigé |
| 🟠 mineur | Lignée draconique / Ailes draconiques | Vitesse de vol et durée non précisées | Vitesse de vol = vitesse actuelle, jusqu'à congédiement (action bonus), incompatible avec une armure non adaptée | corrigé |
| 🟠 mineur | Lignée draconique / Ancêtre dragon & Résilience draconique | Table des ancêtres et types de dégâts absente | 10 dragons : noir/cuivre acide, bleu/bronze foudre, airain/or/rouge feu, vert poison, argent/blanc froid | corrigé |
| 🟠 mineur | Lignée draconique / Présence draconique | Action et concentration non mentionnées ; immunité 24 h absente | Action, 5 points, aura 18 m, 1 min avec concentration ; réussite = immunité 24 h | corrigé |
| 🟠 mineur | Lignée du Sang / sorts_domaine | Noms invalides : « Vampirisme » | Nom français : Caresse du vampire ; niveaux incohérents (Fléau de niveau 1, Domination de monstre de niveau 8 en fin de liste) | corrigé |
| 🟠 mineur | Magie Cosmique / sorts_domaine | Noms invalides : « Lueur féérique », « Colonne de feu » | Noms français : Lueur féerique, Colonne de flamme | corrigé |
| 🟠 mineur | Magie des ombres / Chien de mauvais augure | « inflige -5 PV si fin de tour dedans » ambigu | Le chien subit 5 dégâts de force s'il finit son tour dans un objet | corrigé |
| 🟠 mineur | Magie des ombres / Yeux de ténèbres & Force de la tombe | Ténèbres appris au niveau 1 ; exceptions radiant/critique absentes | Ténèbres au niveau 3 ; Force de la tombe sans effet contre dégâts radiants ou coup critique | corrigé |
| 🟠 mineur | Magie sauvage / Comme par hasard | Réaction non mentionnée | Réaction, 2 points, 1d4 après le jet | corrigé |
| 🟠 mineur | Magie sauvage / Pic de magie sauvage & Marée du chaos | « 1 fois/tour jet de 1d20 » | Le d20 est lancé, à la discrétion du MD, après un sort d'ensorceleur de niveau 1+ ; table Excès sur un 1 | corrigé |
| 🟠 mineur | Métamagie | Options de Tasha (Sort chercheur, Sort transmuté) non mentionnées | TCE ajoute Sort chercheur (2 points) et Sort transmuté (1 point) | corrigé |
| 🟠 mineur | Métamagie supplémentaire (niveau 17) | Texte inventé (combinaisons libres avec la création d'emplacements) | Niveau 17 : une option de Métamagie de plus, mêmes règles (une option par sort sauf Sort renforcé/chercheur) | corrigé |
| 🟠 mineur | Sorcellerie des tempêtes / Langage du vent & Magie tumultueuse | Dialectes du primordial non mentionnés | Compréhension de l'aquatique, de l'aérien, de l'igné et du terreux | corrigé |
| 🟠 mineur | Sorcellerie des tempêtes / sorts_domaine | Nom anglais/mixte « Tempête de sleet » | Nom français : Tempête de neige (Sleet Storm) | corrigé |
| 🟠 mineur | Source de magie | Pas de table de coût de l'Incantation flexible ni d'action bonus | Action bonus ; emplacement de niveau 1/2/3/4/5 = 2/3/5/6/7 points, niveau 5 maximum ; points = niveau d'ensorceleur | corrigé |
| 🟠 mineur | Versatilité magique (Optionnel - TCE) | Obtenue au niveau 5 et permettant de changer un sort connu | Niveau 4 : à chaque niveau d'Amélioration de caractéristiques, remplace une option de Métamagie ou un tour de magie | corrigé |
| 🟠 mineur | Âme divine / Ailes d'outre-monde | Vitesse de vol non précisée | Vitesse de vol de 9 m | corrigé |
| 🟠 mineur | Âme divine / Magie divine & Favori des dieux | Affinité et sort associé non décrits ; récupération « 1/repos » imprécise | Choix d'affinité ; Favori des dieux 2d4, 1 fois par repos court ou long | corrigé |
| 🟠 mineur | Âme divine / Rétablissement céleste | Action bonus non mentionnée | Action bonus, sous la moitié des PV max | corrigé |
| 🟠 mineur | Âme mécanique / Bastion de loi | Nom | Bastion de la loi | corrigé |
| 🟠 mineur | Âme mécanique / Chevauchée méca. | Nom abrégé | Cavalcade mécanique | corrigé |
| 🟠 mineur | Âme mécanique / Transe harmonique | Nom et seuil « inférieur à 9 » | Transe d'ordre : un résultat de 9 ou moins compte comme 10 | corrigé |
| 🟠 mineur | Âme mécanique / Équilibre restauré & Sorts d'ordre | Noms non officiels | Magie mécanique (sorts toujours connus) et Rétablir l'équilibre (réaction) | corrigé |
| 🔵 info | Capacités de classe optionnelles (TCE) | Sorts supplémentaires de la liste d'ensorceleur de Tasha non signalés | TCE étend la liste de sorts d'ensorceleur (ex. Bouclier de feu, Lame aux flammes vertes…) | corrigé |

### Guerrier (corrigé) — 40 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Cavalier / Charge féroce | « Mise à terre en cas de réussite au JS » : logique inversée, pas de DD | À terre en cas d'échec au JS de Force DD 8 + maîtrise + mod. de Force, 1/tour | corrigé |
| 🔴 majeur | Champion / Coup critique amélioré & Athlète accompli | Bonus d'athlète donné dès le niveau 3 | Niveau 3 : Critique amélioré seul ; Athlète remarquable au niveau 7 | corrigé |
| 🔴 majeur | Champion / Coup critique supérieur & Survivant | Survivant au niveau 15, 5 PV fixes, « moins de la moitié » | Survivant au niveau 18 : 5 + modificateur de Constitution PV si PV ≤ moitié et ≥ 1 | corrigé |
| 🔴 majeur | Chevalier runique / Maîtrise des outils, Langue des géants & Puissance des géants | Taille Gigantesque, +1d10 dégâts, 6 utilisations/repos long | Taille Grande, +1d6 (1d8 au niv. 10, 1d10 au niv. 18), utilisations = bonus de maîtrise/repos long | corrigé |
| 🔴 majeur | Chevalier runique / Sculpteur de runes | Aucune rune connue au niveau 3 dans les données | Sculpteur de runes au niveau 3 : 2 runes (3/4/5 aux niveaux 7/10/15), DD 8 + maîtrise + mod. de Constitution | corrigé |
| 🔴 majeur | Guerrier Psi (Soldat psi) / Pouvoirs psioniques | 12 dés d12 fixes | 2 × bonus de maîtrise dés ; d6 (d8 niv. 5, d10 niv. 11, d12 niv. 17) | corrigé |
| 🔴 majeur | Samouraï / Courtisan élégant | Ajoute le modificateur de Charisme | Ajoute le modificateur de Sagesse aux tests de Persuasion | corrigé |
| 🔴 majeur | Samouraï / Maîtrise supplémentaire | Esprit combatif absent au niveau 3 (placé au niveau 15) | Esprit combatif au niveau 3 : action bonus, avantage + 5/10/15 PV temporaires, 3/repos long | corrigé |
| 🟠 mineur | Archer arcanique / Tir arcanique & Connaissances de l'archer | « Arcane » et options/DD absents | Arcanes ou Nature ; 2 options connues (+1 aux niv. 7, 10, 15, 18) ; DD 8 + maîtrise + mod. d'Intelligence | corrigé |
| 🟠 mineur | Archer arcanique / Tir arcanique amélioré | Seul « 4d6 » mentionné | Toutes les options gagnent des dégâts (2d6→4d6, 1d6→2d6) | corrigé |
| 🟠 mineur | Archer arcanique / Tir récurrent (Implacable) | Nom inexact | « Tir infaillible » (Ever-Ready Shot), regain d'une utilisation en lançant l'initiative | corrigé |
| 🟠 mineur | Capacités de classe optionnelles (Tasha) | Absentes des données | Polyvalence martiale (niveau 4, puis à chaque Amélioration de caractéristique) : échanger un style ou une manœuvre | corrigé |
| 🟠 mineur | Cavalier / Manœuvre défensive | Nom inexact, résistance et utilisations absentes | « Manœuvre d'interposition » : +1d8 CA puis résistance ; mod. de Constitution (min 1)/repos long | corrigé |
| 🟠 mineur | Cavalier / Maîtrise supplémentaire, Né sur un cheval & Marque tenace | Noms inexacts, utilisations et bonus de dégâts absents | « Né en selle », « Marque inébranlable » : attaque bonus avec avantage + moitié du niveau de guerrier, mod. de Force/repos long | corrigé |
| 🟠 mineur | Cavalier / On ne passe pas (Inébranlable) | Nom inexact, déplacement dans l'allonge non mentionné | « Tenir la ligne » : attaque d'opportunité même en se désengageant, vitesse 0 si elle touche | corrigé |
| 🟠 mineur | Champion / Athlète remarquable | Description vague | + moitié du bonus de maîtrise (arrondi sup.) aux tests For/Dex/Con sans maîtrise ; saut en longueur + mod. de Force (pieds) | corrigé |
| 🟠 mineur | Champion / Survivant (Maîtrise) | Aptitude au nom inventé, sans effet défini | Niveau 18 : Survivant (régénération 5 + modificateur de Constitution) | corrigé |
| 🟠 mineur | Chevalier de Sang / sorts_domaine | « Vampirism » (nom anglais inexistant) | Remplacer par « Toucher du vampire » (Vampiric Touch, niveau 3) | corrigé |
| 🟠 mineur | Chevalier de Sang / sorts_domaine | « Rayon d'affaiblissement » absent de la base de sorts | Nom exact dans la base : « Rayon affaiblissant » (Ray of Enfeeblement, niveau 2) | corrigé |
| 🟠 mineur | Chevalier occulte / Fragilisation occulte (Frappe arcanique) | Nom et durée imprécis | « Frappe occulte » : désavantage au prochain JS contre vos sorts avant la fin de votre prochain tour | corrigé |
| 🟠 mineur | Chevalier occulte / Incantation & Arme occulte | « Arme occulte », DD et progression des sorts absents | « Lien avec une arme » (rituel 1 h, 2 armes) ; DD 8 + maîtrise + mod. d'Intelligence | corrigé |
| 🟠 mineur | Chevalier runique / Bouclier runique | Utilisations absentes | Bonus de maîtrise par repos long | corrigé |
| 🟠 mineur | Chevalier runique / Grande carrure | « Augmentation permanente de la taille de base » | « Grande stature » : +3d4 pouces de taille (pas de catégorie) et dégâts de Puissance des géants en d8 | corrigé |
| 🟠 mineur | Chevalier runique / Mastodonte runique | Nom inexact, d10 et taille Très grande absents | « Colosse runique » : d10, taille Très grande possible, +1,50 m d'allonge | corrigé |
| 🟠 mineur | Guerrier Psi (Soldat psi) / Applications télékinétiques | Nom et effets imprécis | « Adepte télékinétique » : Bond psi + Poussée télékinétique (JS de Force) | corrigé |
| 🟠 mineur | Guerrier Psi (Soldat psi) / Esprit blindé & Bulle de protection | Rempart de force annoncé au niveau 10 | Niveau 10 : Esprit gardé seul ; Rempart de force au niveau 15 | corrigé |
| 🟠 mineur | Guerrier Psi (Soldat psi) / Rempart de force supérieur | Nom inexact | « Rempart de force » : abri partiel, mod. d'Intelligence créatures, 1 minute | corrigé |
| 🟠 mineur | Indomptable | Typo « niv 13 » et nouveau résultat obligatoire non précisé | Relance d'un JS raté, nouveau résultat obligatoire ; 1/repos long, 2 au niveau 13, 3 au niveau 17 | corrigé |
| 🟠 mineur | Maître de guerre / Dés de supériorité améliorés (d10 / d12) | Laisse entendre le d12 dès le niveau 10 | d10 au niveau 10, d12 au niveau 18 | corrigé |
| 🟠 mineur | Maître de guerre / Maîtrise des dés de supériorité | Aptitude au nom inventé | Niveau 18 : Supériorité martiale améliorée (dés d12) | corrigé |
| 🟠 mineur | Maître de guerre / Observation de l'ennemi | Nom et contenu imprécis | « Connaître son ennemi » : 2 critères parmi For, Dex, Con, CA, PV actuels, niveaux totaux, niveaux de guerrier | corrigé |
| 🟠 mineur | Maître de guerre / Supériorité martiale & Disciple martial | Nombre de dés (4) et de manœuvres (3), DD et récupération absents | 4 dés d8 (5 au niv. 7, 6 au niv. 15), repos court ou long ; DD 8 + maîtrise + mod. For ou Dex ; « Disciple de la guerre » | corrigé |
| 🟠 mineur | Samouraï / Combativité & Frappe fulgurante | Nom « Frappe fulgurante » et Combativité placée au niveau 15 | « Frappe éclair » au niveau 15 ; Esprit combatif au niveau 3 | corrigé |
| 🟠 mineur | Samouraï / Solide face à la mort | Nom inexact | « Force avant la mort » : réaction, tour supplémentaire immédiat | corrigé |
| 🟠 mineur | Samouraï / Volonté inébranlable | Nom inexact | « Esprit infatigable » (Tireless Spirit) | corrigé |
| 🟠 mineur | Style de combat | Noms « Duelliste » et « Combat à deux mains » | Noms officiels : « Duel » et « Arme à deux mains » (Combat à deux armes est un autre style) | corrigé |
| 🟠 mineur | Style de combat | Styles de Tasha non mentionnés | TCE ajoute Combat aveugle, Interception, Arme de lancer, Combat à mains nues, Technique supérieure | corrigé |
| 🔵 info | Chevalier occulte / sorts_domaine | Liste fixe de 8 sorts | Pas de sorts imposés : sorts de magicien au choix (abjuration/évocation sauf niveaux 3, 8, 14, 20) | corrigé |
| 🔵 info | Maître de guerre / Relance de supériorité (Implacable) | Déclencheur « début du combat » | Se déclenche quand vous lancez l'initiative sans dé de supériorité restant | corrigé |
| 🔵 info | Sursaut d'activité | Limite d'une utilisation par tour non mentionnée | 2 utilisations au niveau 17, mais une seule par tour | corrigé |

### Magicien (corrigé) — 62 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Chantelame / Formation martiale et artistique & Chant de la lame | 6 utilisations fixes par repos long | Un nombre de fois égal au bonus de maîtrise par repos long (TCE) ; bonus CA = modificateur d'Intelligence (min +1) | corrigé |
| 🔴 majeur | Magie de la Chronurgie / Stase momentanée | Cible « paralysée » ; ni portée ni utilisations | Créature G ou inférieure à 18 m, neutralisée et vitesse 0 jusqu'à la fin de votre prochain tour ; modificateur d'Intelligence utilisations par repos long | corrigé |
| 🔴 majeur | Ordre des scribes / Érudition réifiée | 6 utilisations fixes par repos long ; nom non officiel (renommée « Esprit manifesté ») | Lancer depuis l'esprit un nombre de fois égal au bonus de maîtrise par repos long (+ en dépensant un emplacement) | corrigé |
| 🔴 majeur | Prospérité des rituels (Optionnel) | Aptitude inventée, donnée au niveau 3 et marquée optionnelle : supprimée (déjà couverte par Incantation) | L'incantation rituelle fait partie de l'Incantation du magicien dès le niveau 1 (PHB) | corrigé |
| 🔴 majeur | École d'Abjuration / Abjurateur érudit & Égide arcanique | Égide fixe de 20 PV temporaires | PV max de l'égide = 2 × niveau de magicien + modificateur d'Intelligence ; regagne 2 × niveau du sort à chaque abjuration ; ce ne sont pas des PV temporaires | corrigé |
| 🔴 majeur | École d'Enchantement / Altération mémorielle | Durée oubliée fixe de 8 h | Oubli de 1 + modificateur de Charisme heures (minimum 1), JS d'Intelligence, dans la limite de la durée du sort | corrigé |
| 🔴 majeur | École d'Enchantement / Enchanteur érudit & Regard hypnotique | Limité à 1 fois par repos long ; DD non précisé | Usage illimité ; une même créature n'est plus affectable avant un repos long après la fin de l'effet ou une réussite ; DD des sorts, neutralisée, 1 minute max | corrigé |
| 🔴 majeur | École de la Nécromancie / Serviteurs morts-vivants | Bonus « aux jets d'attaque » ; PV max non chiffrés | PV max + niveau de magicien et bonus de maîtrise ajouté aux jets de dégâts avec une arme | corrigé |
| 🟠 mineur | Capacités de classe optionnelles (TCE) | Formules de sorts mineurs absente : ajoutée au niveau 3 (option Tasha) | Niveau 3 (Tasha) : à la fin d'un repos long, remplacer un sort mineur de magicien connu par un autre | corrigé |
| 🟠 mineur | Chantelame / Chant de victoire | Attaque d'arme en action bonus après un sort absente | TCE : après avoir lancé un sort par une action, une attaque d'arme par une action bonus | corrigé |
| 🟠 mineur | Chantelame / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | La Chantelame n'a pas de liste de sorts de sous-classe | corrigé |
| 🟠 mineur | Chantelame / sorts_domaine | Noms invalides : « Longstrider » (anglais), « Châtiment planaire » (liste vidée) | « Grande foulée » ; « Châtiment planaire » n'existe pas | corrigé |
| 🟠 mineur | Gravure runique / sorts_domaine | Noms invalides : « Glyphe de garde » / « Glyphe de protection » en double, « Œil mystique » | « Glyphe de protection » (nom de la base) ; doublon remplacé par « Protection contre une énergie » ; « Oeil magique » | corrigé |
| 🟠 mineur | Liaison élémentaire / sorts_domaine | Noms invalides : « Colonne de feu », « Essaim de météores » | « Colonne de flamme » ; « Nuée de météores » | corrigé |
| 🟠 mineur | Magicien du Sang / Maîtrise de l'hémomancie | Faute « Vos sorts ignorant » | « Vos sorts ignorent » | corrigé |
| 🟠 mineur | Magicien du Sang / Pacte de sang | Faute de frappe « touquez » | « touchez » | corrigé |
| 🟠 mineur | Magicien du Sang / sorts_domaine | Noms invalides : « Vampirisme », « Faux repos », « Rayon d'affaiblissement », « Drain de vie » | Remplacés par « Toucher du vampire », « Mort simulée », « Rayon affaiblissant », « Énervation » (noms de la base) | corrigé |
| 🟠 mineur | Magie de guerre / Surtension | Stock maximal et dégâts non chiffrés | Maximum = modificateur d'Intelligence (min 1) ; dégâts de force = moitié du niveau de magicien, une fois par tour | corrigé |
| 🟠 mineur | Magie de guerre / Voile de déviation | Nombre de cibles, portée et dégâts absents ; nom non officiel (renommée) | « Linceul déflecteur » : jusqu'à 3 créatures à 18 m, dégâts de force = moitié du niveau de magicien | corrigé |
| 🟠 mineur | Magie de guerre / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | La Magie de guerre (XGE) n'a pas de liste de sorts de sous-classe | corrigé |
| 🟠 mineur | Magie de la Chronurgie / Abri d'arcanes & Altération convergente | Noms non officiels : renommées | « Suspension arcanique » (Arcane Abeyance) ; « Avenir convergent » (Convergent Future) | corrigé |
| 🟠 mineur | Magie de la Chronurgie / Conscience temporelle & Altération du sort | « 2/repos » imprécis ; nom (renommée « Conscience temporelle & Déphasage chronal ») | « Déphasage chronal » : réaction, 9 m, deux utilisations par repos long | corrigé |
| 🟠 mineur | Magie de la Chronurgie / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | La Chronurgie (Wildemount) n'a pas de liste de sorts de sous-classe | corrigé |
| 🟠 mineur | Magie de la Chronurgie / sorts_domaine | Noms invalides : « Don des alouettes », « Synapse » (liste vidée) | Sorts inexistants | corrigé |
| 🟠 mineur | Ordre des scribes / Union avec le verbe | Coût de 3d6 niveaux de sorts et limite 1/repos long non précisés | Réaction, annule les dégâts, perte de sorts du grimoire totalisant 3d6 niveaux pendant 1d6 repos longs | corrigé |
| 🟠 mineur | Ordre des scribes / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | L'Ordre des scribes n'a pas de liste de sorts de sous-classe | corrigé |
| 🟠 mineur | Ordre des scribes / sorts_domaine | Nom invalide : « Langue arcanique » (liste vidée) | Sort inexistant | corrigé |
| 🟠 mineur | Ordre des scribes / source | Source en anglais « Tasha's Cauldron of Everything » : corrigée | « Chaudron des Merveilles de Tasha », comme les autres entrées | corrigé |
| 🟠 mineur | Restauration arcanique | « moitié du niveau de magicien » sans arrondi ni limite d'1 fois par jour | Niveaux cumulés ≤ moitié du niveau de magicien arrondie au supérieur, aucun emplacement de niveau 6+, une fois par jour après un repos court | corrigé |
| 🟠 mineur | Signature magique | Nom non officiel : renommée « Sorts de prédilection » | « Sorts de prédilection » (Signature Spells) : deux sorts de niveau 3, une fois chacun par repos court ou long | corrigé |
| 🟠 mineur | École d'Abjuration / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École d'Abjuration / sorts_domaine | Noms invalides : « Sphère résilient de Otiluke », « Anticipation » (liste vidée) | « Sphère résiliente d'Otiluke » ; « Anticipation » n'existe pas (Contingence ?) | corrigé |
| 🟠 mineur | École d'Abjuration / École projetée | Nom erroné : renommée | « Égide projetée » (Projected Ward) | corrigé |
| 🟠 mineur | École d'Enchantement / Détournement d'hostilité | Nom erroné : renommée ; « l'assaillant rate » inexact | « Charme instinctif » : réaction, JS Sagesse, l'attaque est redirigée vers la créature la plus proche | corrigé |
| 🟠 mineur | École d'Enchantement / Enchantement bifide | Nom erroné : renommée ; ne précise pas « niveau 1+ » ni la portée | « Enchantement partagé » : sort d'enchantement de niveau 1+ à cible unique, seconde cible à portée | corrigé |
| 🟠 mineur | École d'Enchantement / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École d'Enchantement / sorts_domaine | Noms invalides : « Ennemi suprême », « Forme animale » (liste vidée) | Sorts inexistants ou hors liste du magicien (Formes animales est un sort de druide) | corrigé |
| 🟠 mineur | École d'Illusion / Réalité chimérique | Nom : renommée ; ne précise pas que l'objet ne peut infliger de dégâts | « Réalité illusoire » : objet inanimé non magique, 1 minute, ne peut blesser personne | corrigé |
| 🟠 mineur | École d'Illusion / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École d'Illusion / sorts_domaine | Noms invalides : « Mot de mire », « Illusion pathologique » (liste vidée) | Sorts inexistants (Illusion programmée ?) | corrigé |
| 🟠 mineur | École d'Évocation / Sort mineur appuyé | Nom erroné : renommée | « Sort mineur puissant » (Potent Cantrip) | corrigé |
| 🟠 mineur | École d'Évocation / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École d'Évocation / Évocateur érudit & Façonneur de sorts | Nombre de créatures protégées non précisé | 1 + niveau du sort créatures choisies | corrigé |
| 🟠 mineur | École d'Évocation / Évocation améliorée | Nom : renommée ; ne précise pas « un seul jet de dégâts » | « Évocation renforcée » : modificateur d'Intelligence ajouté à un jet de dégâts d'un sort d'évocation de magicien | corrigé |
| 🟠 mineur | École de Divination / Présage renforcé | Nom erroné : renommée | « Présage supérieur » (Greater Portent) | corrigé |
| 🟠 mineur | École de Divination / Troisième œil | Sens choisi « après un repos » | Action pour activer ; dure jusqu'à un repos court ou long ; vision dans le noir 18 m, éthérée 18 m, lecture des langues, ou voir l'invisible 3 m | corrigé |
| 🟠 mineur | École de Divination / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École de Divination / sorts_domaine | Noms invalides : « Langue arcanique », « Pré Cognition » (liste vidée) | Sorts inexistants (Don des langues ? Prémonition ?) | corrigé |
| 🟠 mineur | École de l'Invocation / Invocateur érudit & Menue invocation | Taille, portée et durée incomplètes | Action, objet ≤ 90 cm de côté et ≤ 5 kg, à 3 m, dure 1 heure ou jusqu'à ce qu'il subisse des dégâts | corrigé |
| 🟠 mineur | École de l'Invocation / Invocation consciencieuse & Convocations coriaces | Noms non officiels : renommées | « Invocation focalisée » (Focused Conjuration) ; « Convocations durables » (Durable Summons) | corrigé |
| 🟠 mineur | École de l'Invocation / Permutation | Nom erroné : renommée ; taille de l'allié non précisée | « Transposition bienveillante » : échange avec une créature consentante de taille P ou M | corrigé |
| 🟠 mineur | École de l'Invocation / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École de l'Invocation / sorts_domaine | Noms invalides : « Trou de serrure », « Flèche acidulée de Melf » (liste vidée) | Sort inexistant ; « Flèche acide de Melf » | corrigé |
| 🟠 mineur | École de la Nécromancie / Contrôle des morts-vivants | Portée, avantage selon l'Intelligence et relance horaire absents ; nom non officiel (renommée) | « Commandement des morts-vivants » : action, 18 m, JS Charisme ; avantage si Int ≥ 8, nouvelle sauvegarde chaque heure si Int ≥ 12 | corrigé |
| 🟠 mineur | École de la Nécromancie / Insensibilité à la non-vie | Nom non officiel : renommée | « Endurci contre la non-vie » (Inured to Undeath) | corrigé |
| 🟠 mineur | École de la Nécromancie / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École de la Nécromancie / sorts_domaine | Noms invalides : « Pulsion de mort », « cercle de la mort », « Drain de vie » (liste vidée) | Sorts inexistants ; « Cercle de mort » | corrigé |
| 🟠 mineur | École de la Transmutation / sorts_domaine | Liste de sorts inventée : liste remplacée par [] (aucune liste de sorts de sous-classe officielle) | les écoles du Manuel des joueurs n'ont pas de liste de sorts de sous-classe (sorts toujours préparés) | corrigé |
| 🟠 mineur | École de la Transmutation / sorts_domaine | Noms invalides : « Fait d'armes », « Création de nourriture », « Flottement », « Statue », « Porte des étoiles » (liste vidée) | Sorts inexistants ou incomplets (« Création de nourriture et d'eau », sort de clerc) | corrigé |
| 🔵 info | Maîtrise des sorts | Ne précise pas le lancement au niveau le plus bas ni le changement par 8 h d'étude | Sorts lancés à leur niveau le plus bas sans emplacement ; remplaçables après 8 heures d'étude | corrigé |
| 🔵 info | École d'Évocation / Surcharge magique | Dégâts de contrecoup non chiffrés | 2d12 nécrotiques par niveau du sort à la 2e utilisation, +1d12 par niveau à chaque utilisation suivante, ignorent résistance/immunité | corrigé |
| 🔵 info | École de la Nécromancie / Sinistre moisson | Restriction une fois par tour et exclusion morts-vivants/créatures artificielles absentes | Une fois par tour ; ne fonctionne pas sur morts-vivants ni créatures artificielles | corrigé |

### Moine (corrigé) — 38 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Capacités de classe optionnelles (Tasha) | Arme dédiée absente des données | TCE, niveau 2 : après un repos court ou long, une arme maîtrisée (ni lourde ni spéciale) devient une arme de moine | corrigé |
| 🔴 majeur | Capacités de classe optionnelles (Tasha) | Attaque alimentée par le ki (« Ki dédié ») absente | TCE, niveau 3 : après avoir dépensé du ki par une action, une attaque d'arme ou à mains nues par une action bonus | corrigé |
| 🔴 majeur | Capacités de classe optionnelles (Tasha) | Guérison accélérée (« Récupération adaptée ») absente | TCE, niveau 4 : action, 2 ki, récupérer un dé d'arts martiaux + bonus de maîtrise PV | corrigé |
| 🔴 majeur | Capacités de classe optionnelles (Tasha) | Visée concentrée (« Frappe concentrée ») absente | TCE, niveau 5 : après un jet d'attaque raté, 1 à 3 ki pour +2 par point dépensé | corrigé |
| 🔴 majeur | Voie de l'Astre intérieur / Astre intérieur accompli | Effet non décrit | Action bonus, 5 ki, 10 min : +2 CA et trois attaques avec les bras lors de l'action Attaquer | corrigé |
| 🔴 majeur | Voie de l'Astre intérieur / Bras astraux | Coût (1 ki, action bonus, 10 min) et dégâts d'invocation absents | Action bonus, 1 ki, 10 minutes ; JS Dex ou 2 dés d'arts martiaux de force à 3 m | corrigé |
| 🔴 majeur | Voie de l'Astre intérieur / Corps de l'astre intérieur | « Résistances élémentaires » inventées | Détournement d'énergie (réaction, 1d10 + Sagesse + niveau de moine) et Bras renforcés (+1 dé d'arts martiaux) | corrigé |
| 🔴 majeur | Voie de l'Astre intérieur / Visage astral | Avantage en Intimidation/Persuasion | Avantage en Intuition et Intimidation ; vision astrale 36 m ; durée 10 minutes | corrigé |
| 🔴 majeur | Voie de l'Âme solaire / Bouclier solaire | Dégâts « automatiques » non chiffrés | Réaction : 5 + modificateur de Sagesse dégâts radiants à l'attaquant au CàC | corrigé |
| 🔴 majeur | Voie de la Paume / Paume vibratoire | Durée fixe de 20 jours | Durée = niveau de moine en jours ; déclenchement par une action | corrigé |
| 🔴 majeur | Voie des Quatre Éléments / sorts_domaine | « Fléau d'éléments » ne fait pas partie des disciplines | Sorts des disciplines : Mains brûlantes, Vague tonnante, Immobilisation de personne, Bourrasque, Fracassement, Boule de feu, Forme gazeuse, Vol, Cône de froid, Peau de pierre, Mur de feu, Mur de pierre | corrigé |
| 🔴 majeur | Voie du Maître ivre / Chance de l'ivrogne | Coût de 1 ki | 2 points de ki pour annuler le désavantage | corrigé |
| 🟠 mineur | Arts martiaux | Progression du dé non précisée | d4 (1), d6 (5), d8 (11), d10 (17) ; armes de moine = épée courte + armes courantes de CàC non lourdes/à deux mains | corrigé |
| 🟠 mineur | Chute lente | Nom non officiel | Chute ralentie (PHB) : réaction, réduit les dégâts de 5 × niveau de moine | corrigé |
| 🟠 mineur | Défense sans armure | Abréviations « mod. » dans le texte | CA = 10 + modificateur de Dextérité + modificateur de Sagesse | corrigé |
| 🟠 mineur | Déplacement sans armure | Valeurs non chiffrées et course verticale/sur liquides (niv. 9) omise | +3 m (2), +4,50 m (6), +6 m (10), +7,50 m (14), +9 m (18) | corrigé |
| 🟠 mineur | Ki / Énergie spirituelle | Nom double ; DD du ki et récupération (repos court) absents | Ki : DD = 8 + bonus de maîtrise + modificateur de Sagesse ; récupéré par repos court ou long | corrigé |
| 🟠 mineur | Parade de projectiles | Formule de réduction et coût du renvoi absents | Réduction 1d10 + modificateur de Dextérité + niveau de moine ; renvoi pour 1 ki | corrigé |
| 🟠 mineur | Pureté du corps | Immunité aux dégâts de poison non précisée | Immunité aux maladies, aux dégâts de poison et à l'état empoisonné | corrigé |
| 🟠 mineur | Voie de l'Âme solaire / Rayon de soleil radiant | Dégâts et remplacement des attaques non précisés | Dé d'arts martiaux + Dextérité radiants, 9 m ; 1 ki pour deux rayons en action bonus | corrigé |
| 🟠 mineur | Voie de l'Âme solaire / Vague brûlante | Action bonus et plafond de ki absents | Action bonus, 2 ki, +1 ki par niveau, max moitié du niveau de moine | corrigé |
| 🟠 mineur | Voie de l'Âme solaire / Éruption solaire ardente | « 2d6+ » ambigu ; coût en ki non précisé | 2d6 radiants sans ki, +2d6 par ki (max 3 ki), aucun dégât si réussite | corrigé |
| 🟠 mineur | Voie de la Miséricorde / Caresse médicale | Maladie omise ; durée de l'empoisonnement absente | Met fin à une maladie ou un état ; empoisonné jusqu'à la fin de votre prochain tour | corrigé |
| 🟠 mineur | Voie de la Miséricorde / Instrument de charité, Main guérisseuse & Main meurtrissante | Dégâts de Main meurtrissante non chiffrés ; masque omis | Dé d'arts martiaux + Sagesse nécrotiques, 1 ki, une fois par tour | corrigé |
| 🟠 mineur | Voie de la Miséricorde / Main de l'ultime miséricorde | PV de retour non précisés | Revient avec 4d10 + modificateur de Sagesse PV | corrigé |
| 🟠 mineur | Voie de la Paume / Ataraxie | « Entre deux combats » imprécis | Sanctuaire à la fin d'un repos long, jusqu'au prochain repos long ; DD = DD du ki | corrigé |
| 🟠 mineur | Voie de la Paume / Plénitude physique | Action non précisée | Action ; 3 × niveau de moine PV, 1/repos long | corrigé |
| 🟠 mineur | Voie de la Paume / Technique de la paume | Données : coût de 1 ki | Aucun ki supplémentaire : l'effet s'applique à chaque frappe du Déluge de coups qui touche | corrigé |
| 🟠 mineur | Voie des Quatre Éléments / Discipline élémentaire avancée | Décrite comme « sorts de zone majeurs » | Niveau 11 : simple discipline supplémentaire (Flammes du phénix, Posture de brume, Chevaucher le vent) | corrigé |
| 🟠 mineur | Voie des Quatre Éléments / Incantation élémentaire renforcée | Aptitude de niveau 5 inventée (règle incluse dans Disciple des éléments) | Plafond de ki par sort : 2/3/4/5/6 aux niveaux 3/5/9/13/17 | corrigé |
| 🟠 mineur | Voie du Kensei / Armes du kensei, Parade agile & Tir du kensei | Bonus de Tir du kensei non chiffré | Action bonus : +1d4 dégâts aux attaques à distance d'arme de kensei | corrigé |
| 🟠 mineur | Voie du Kensei / Lame affûtée | Action bonus non mentionnée | Action bonus, 1 à 3 ki, 1 minute | corrigé |
| 🟠 mineur | Voie du Kensei / Précision infaillible | « Relance automatiquement » imprécis | Une fois par tour, relance possible d'une attaque ratée avec une arme de moine | corrigé |
| 🟠 mineur | Voie du Maître ivre / Chancellements éméchés | Réaction non mentionnée pour Réorientation | 1 ki + réaction | corrigé |
| 🟠 mineur | Voie du Sang / sorts_domaine | « Rayon d'affaiblissement » n'est pas le nom VF officiel | Rayon affaiblissant | corrigé |
| 🟠 mineur | Voie du Sang / sorts_domaine | « Vampirisme » n'est pas un sort existant (remplacé par Toucher du vampire, nom de la base de sorts) | Caresse du vampire | corrigé |
| 🟠 mineur | Évasion | Nom différent de la VF officielle | Dérobade (PHB VF) | corrigé |
| 🔵 info | Voie de la Paume / sorts_domaine | Liste « Sanctuaire » alors que la voie n'a pas de liste de sorts | Sanctuaire n'est obtenu que via Ataraxie (niveau 11) | corrigé |

### Occultiste (corrigé) — 38 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | L'Archifée / Présence féerique | Récupération au repos long | 1 fois par repos court ou long ; action, cube de 3 m, JS Sagesse, effet jusqu'à la fin de votre prochain tour | corrigé |
| 🔴 majeur | L'Archifée / sorts_domaine | Liste fausse : Calme des émotions (nom invalide), Invisibilité, Fléau d'insectes, Porte dimensionnelle, Domination de monstre, Création | Lueurs féeriques, Sommeil / Apaisement des émotions, Force fantasmagorique / Clignotement, Croissance végétale / Domination de bête, Invisibilité supérieure / Domination de personne, Apparence trompeuse | corrigé |
| 🔴 majeur | L'Archifée / Échappatoire brumeuse | Récupération au repos long | 1 fois par repos court ou long ; invisible jusqu'au début de votre prochain tour | corrigé |
| 🔴 majeur | L'Insondable / Plongeon abyssal | Récupération au repos long | 1 fois par repos court ou long ; créatures à 9 m | corrigé |
| 🔴 majeur | L'Insondable / Tentacule abyssal | 2d8 dès le niveau 1 ; utilisations absentes | 1d8 froid (2d8 au niv. 10), vitesse -3 m ; utilisations = bonus de maîtrise par repos long | corrigé |
| 🔴 majeur | L'Insondable / Tentacule gardien | Réduction de 2d8 dès le niveau 6 | Réaction, réduction de 1d8 (2d8 au niv. 10) à 3 m du tentacule | corrigé |
| 🔴 majeur | L'Insondable / Tentacules agrippants | 20 PV temporaires fixes | PV temporaires = niveau d'occultiste ; concentration non rompue par les dégâts | corrigé |
| 🔴 majeur | L'Insondable / sorts_domaine | Noms invalides (Tentacules de noirs éboulis, Ascension, Implosion) ; Nappe de brouillard, Fléau, Immobilisation de personne, Clairvoyance, Forme gazeuse, Invocation d'élémentaires mineurs hors liste | Création ou destruction d'eau, Vague tonnante / Bourrasque, Silence / Éclair, Tempête de neige / Contrôle de l'eau, Convocation d'élémentaire / Main de Bigby, Cône de froid | corrigé |
| 🔴 majeur | La Lame maudite / Armure de maléfices | Jet d'un d6 (4+) | Réaction, jet d'un d20 : sur 4 ou plus, l'attaque échoue | corrigé |
| 🔴 majeur | La Lame maudite / Malédiction de la Lame | Récupération au repos long ; durée et portée absentes | Action bonus, 9 m, 1 minute ; +bonus de maîtrise aux dégâts ; 1 fois par repos court ou long | corrigé |
| 🔴 majeur | La Lame maudite / sorts_domaine | Noms invalides (Marque du reître, Pinte d'obscurité, Rapidité, Fléau d'animation, Conflit) ; Clairvoyance, Invisibilité supérieure, Flétrissement hors liste | Bouclier, Châtiment courroucé / Flou, Châtiment révélateur / Clignotement, Arme élémentaire / Assassin imaginaire, Châtiment débilitant / Châtiment du ban, Cône de froid | corrigé |
| 🔴 majeur | Le Céleste / Lumière guérisseuse | Réserve fixe de 20d6 et 1d6 max par utilisation | Réserve = 1 + niveau d'occultiste d6 ; max par usage = modificateur de Charisme (min 1) ; repos long | corrigé |
| 🔴 majeur | Le Céleste / Persévérance céleste | Valeurs fixes (20 et 10 PV temporaires) | Niveau d'occultiste + mod. Charisme pour vous ; moitié du niveau + mod. Charisme pour 5 créatures | corrigé |
| 🔴 majeur | Le Céleste / Vengeance ardente | Déclenché par un jet réussi ; 41 PV fixes | À la place d'un jet contre la mort : récupère la moitié des PV max ; 2d8 + mod. Charisme radiants à 9 m, aveuglés ; 1/repos long | corrigé |
| 🔴 majeur | Le Céleste / sorts_domaine | Noms invalides (Restaurer l'innocence, Revitalisation, Colonne de feu) ; Bénédiction, Aide, Rappel à la vie hors liste | Soins, Éclair traçant / Sphère de feu, Restauration partielle / Lumière du jour, Retour à la vie / Gardien de la foi, Mur de feu / Colonne de flamme, Restauration supérieure | corrigé |
| 🔴 majeur | Le Fiélon / sorts_domaine | « Commandement » et « Colonne de feu » invalides ; Forme gazeuse et Immolation hors liste | Mains brûlantes, Injonction / Cécité/Surdité, Rayon ardent / Boule de feu, Nuage nauséabond / Bouclier de feu, Mur de feu / Colonne de flamme, Sanctification | corrigé |
| 🔴 majeur | Le Grand Ancien / sorts_domaine | Noms invalides (Désorientation, Chuchotements dissonants, Force fantasmatique, Rapidité, Tentacules de noirs éboulis, Moisson d'esprit) ; Télépathie (8e) hors liste ; Domination de personne mal placée | Murmures dissonants, Fou rire de Tasha / Détection des pensées, Force fantasmagorique / Clairvoyance, Communication à distance / Domination de bête, Tentacules noirs d'Evard / Domination de personne, Télékinésie | corrigé |
| 🔴 majeur | Le Génie (Dao - Terre) / sorts_domaine | Création de nourriture et Passage par la pierre invalides ; Immobilisation de personne, Divination hors liste | Sanctuaire / Croissance d'épines / Fusion dans la pierre / Façonnage de la pierre / Mur de pierre | corrigé |
| 🔴 majeur | Le Génie (Djinn - Air) / sorts_domaine | « Onde de choc » invalide ; Forme gazeuse, Liberté de mouvement, Domination de monstre hors liste | Vague tonnante / Bourrasque / Mur de vent / Invisibilité supérieure / Apparence trompeuse | corrigé |
| 🔴 majeur | Le Génie (Maride - Eau) / sorts_domaine | Raz-de-marée, Tempête de grêle, Cercle de téléportation hors liste | Nappe de brouillard / Flou / Tempête de neige / Contrôle de l'eau / Cône de froid | corrigé |
| 🔴 majeur | Le Génie (Éfrit - Feu) / sorts_domaine | « Colonne de feu » invalide ; Immolation hors liste | Mains brûlantes / Rayon ardent / Boule de feu / Bouclier de feu / Colonne de flamme | corrigé |
| 🔴 majeur | Le Génie / sorts_domaine | Sorts communs à tous les génies absents des 4 listes | Détection du mal et du bien (1), Force fantasmagorique (2), Création de nourriture et d'eau (3), Assassin imaginaire (4), Création (5), Souhait (9) | corrigé |
| 🟠 mineur | Capacités de classe optionnelles | Option de Tasha absente | TCE : Polyvalence de l'occultiste (niv. 4, 8, 12, 16, 19 : remplacer un sort mineur, l'arcanum ou la faveur de pacte) | corrigé |
| 🟠 mineur | Invocations occultes | Nombre d'invocations connues absent | 2 au niv. 2, 3 au niv. 5, 4 au niv. 7, 5 au niv. 9, 6 au niv. 12, 7 au niv. 15, 8 au niv. 18 | corrigé |
| 🟠 mineur | L'Archifée / Sombre délire | Portée, durée et recharge absentes | Action, 18 m, JS Sagesse, charmé ou effrayé 1 minute (concentration), 1/repos court ou long | corrigé |
| 🟠 mineur | L'Archifée / sorts_domaine | Noms anglais : « Faerie Fire », « Sleep » | Lueurs féeriques, Sommeil | corrigé |
| 🟠 mineur | La Lame maudite / Maître des malédictions | Nom inexact | XGE : « Maître des maléfices » (Master of Hexes), cible à 9 m, sans regain de PV | corrigé |
| 🟠 mineur | La Lame maudite / Spectre maudit | Restrictions et statistiques absentes | Humanoïde tué ; PV temp = moitié du niveau d'occultiste ; +mod. Charisme à l'attaque ; 1/repos long | corrigé |
| 🟠 mineur | Le Céleste / Âme rayonnante | Bonus appliqué à tous les dégâts | Mod. Charisme ajouté à un seul jet de dégâts radiants ou de feu du sort, contre une cible | corrigé |
| 🟠 mineur | Le Fiélon / Bénédiction du ténébreux | Formule abrégée (« mod. Charisme ») | PV temporaires = modificateur de Charisme + niveau d'occultiste (minimum 1) | corrigé |
| 🟠 mineur | Le Grand Ancien / Asservissement | « Créature » au lieu d'humanoïde | Toucher (action) un humanoïde neutralisé ; charmé jusqu'à Délivrance des malédictions ou nouvel usage | corrigé |
| 🟠 mineur | Le Grand Ancien / Bouclier mental | « Immunité à la télépathie » imprécis | Vos pensées ne peuvent être lues sans votre accord ; résistance psychique ; renvoi des dégâts psychiques | corrigé |
| 🟠 mineur | Le Génie / Vaisseau du Génie | Refuge confondu avec le repos court de 10 min (aptitude de niveau 10) | Niv. 1 : vaisseau (CA = DD des sorts, PV = niveau + bonus de maîtrise), Refuge en bouteille 2 × bonus de maîtrise heures, 1/repos long | corrigé |
| 🟠 mineur | Le Moissonneur / sorts_domaine | Noms inexistants : « Faux repos », « Rayon d'affaiblissement », « Pulsion de mort » ; 6 sorts au lieu de 10 | Suggestion : Simulacre de vie, Rayon empoisonné / Rayon affaiblissant, Cécité/Surdité / Animation des morts, Mort simulée / Flétrissement, Protection contre la mort / Brume mortelle, Contagion | corrigé |
| 🟠 mineur | Le Protecteur astral / sorts_domaine | Noms invalides : « Lueur féérique », « Flottement », « Levitation », « Force fantasmatique », « Œil mystique », « Anticipation », « Périple planétaire » | Suggestion : Lueurs féeriques, Feuille morte / Lévitation, Force fantasmagorique / Clairvoyance, Clignotement / Porte dimensionnelle, Oeil magique / Télékinésie, Cercle de téléportation | corrigé |
| 🟠 mineur | Magie des pactes | Ni nombre d'emplacements, ni niveau, ni sorts connus indiqués | 1 emplacement (niv. 1), 2 (niv. 2), 3 (niv. 11), 4 (niv. 17) ; niveau 1er→5e max (5e au niv. 9) ; récupération repos court | corrigé |
| 🟠 mineur | Maître des arcanes | Nom non officiel | PHB : « Maître de l'occulte » (Eldritch Master), niveau 20, 1 minute, récupère tous les emplacements, 1/repos long | corrigé |
| 🔵 info | Pacte divin | Pacte du Talisman (Tasha) mêlé aux pactes du PHB sans mention de source | Pacte du Talisman : TCE, +1d4 à un test raté, bonus de maîtrise fois par repos long | corrigé |

### Paladin (corrigé) — 53 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Serment de Conquête / Aura de conquête | 10 dégâts psychiques fixes | Dégâts psychiques = moitié du niveau de paladin ; aura 3 m (9 m au niv. 18) | corrigé |
| 🔴 majeur | Serment de Conquête / sorts | Niv. 3 : Frayeur ; niv. 5 : Cécité/Surdité | Niv. 3 : Armure d'Agathys, Injonction ; niv. 5 : Immobilisation de personne, Arme spirituelle | corrigé |
| 🔴 majeur | Serment de Conquête / sorts | Niv. 9 : Forme spirituelle | Niv. 9 : Malédiction, Peur | corrigé |
| 🔴 majeur | Serment de Conquête / sorts | Niv. 13 : Domination de personne, Sanctuaire | Niv. 13 : Domination de bête, Peau de pierre | corrigé |
| 🔴 majeur | Serment de Conquête / sorts | Niv. 17 : Domination de monstre | Niv. 17 : Brume mortelle (Cloudkill), Domination de personne | corrigé |
| 🔴 majeur | Serment de Dévotion / sorts | Niv. 5 : Aide, « Restaurer l'innocence » (inexistant) | Niv. 5 : Restauration partielle, Zone de vérité | corrigé |
| 🔴 majeur | Serment de Dévotion / sorts | Niv. 9 : Lumière du jour, Réflexion | Niv. 9 : Lueur d'espoir, Dissipation de la magie | corrigé |
| 🔴 majeur | Serment de Rédemption / Protection spirituelle | 1d6 + 10 au début du tour — renommée « Esprit protecteur » | Esprit protecteur : 1d6 + moitié du niveau de paladin à la fin du tour, si ≤ moitié des PV et > 0 | corrigé |
| 🔴 majeur | Serment de Rédemption / sorts | Liste presque entièrement fausse, sorts inexistants (Apaisement, Sanctuaire suprême, Calme absolu) et sort mineur (Résistance) | 3 : Sanctuaire, Sommeil ; 5 : Apaisement des émotions, Immobilisation de personne ; 9 : Contresort, Motif hypnotique ; 13 : Sphère résiliente d'Otiluke, Peau de pierre ; 17 : Immobilisation de monstre, Mur de force | corrigé |
| 🔴 majeur | Serment de Rédemption / Émissaire de la rédemption | Limité à 1/repos long | Permanent ; perdu contre une créature attaquée/ciblée jusqu'au prochain repos long | corrigé |
| 🔴 majeur | Serment de Vengeance / sorts | Niv. 3 : Frayeur, « Marque du reître » | Niv. 3 : Fléau, Marque du chasseur | corrigé |
| 🔴 majeur | Serment de Vengeance / sorts | Niv. 5 : Rayon d'affaiblissement | Niv. 5 : Immobilisation de personne, Foulée brumeuse | corrigé |
| 🔴 majeur | Serment de Vengeance / sorts | Niv. 17 : « Scinder » (inexistant) | Niv. 17 : Immobilisation de monstre, Scrutation | corrigé |
| 🔴 majeur | Serment de la Gloire / Défense glorieuse | 1/repos long | Utilisations = mod. Charisme (min 1) / repos long ; réaction, cible à 3 m | corrigé |
| 🔴 majeur | Serment de la Gloire / sorts | Guide (sort mineur), « Longstrider » (anglais), « Magie de guerre », Divination, « Périple planétaire », « Don des héros » | 3 : Éclair traçant, Héroïsme ; 5 : Amélioration de caractéristique, Arme magique ; 9 : Hâte, Protection contre une énergie ; 13 : Compulsion, Liberté de mouvement ; 17 : Communion, Colonne de flamme | corrigé |
| 🔴 majeur | Serment des Anciens / Champion antique | « Désavantage aux sorts ennemis » (effet inversé) | Les ennemis à 3 m ont un désavantage aux JS contre vos sorts de paladin et Conduit divin ; action, 1 min | corrigé |
| 🔴 majeur | Serment des Anciens / sorts | Niv. 3 : Enchevêtrement ; « Parler avec les animaux » | Niv. 3 : Frappe piégeuse, Communication avec les animaux | corrigé |
| 🔴 majeur | Serment des Anciens / sorts | Niv. 5 : Immobilisation de personne au lieu de Foulée brumeuse | Niv. 5 : Rayon de lune, Foulée brumeuse | corrigé |
| 🔴 majeur | Serment des Anciens / sorts | Niv. 13 : Liberté de mouvement, Forme animale | Niv. 13 : Tempête de grêle, Peau de pierre | corrigé |
| 🔴 majeur | Serment des Anciens / sorts | Niv. 17 : « Rejeton de la nature » | Niv. 17 : Communion avec la nature, Passage par les arbres | corrigé |
| 🔴 majeur | Serment des Guetteurs / Aura de la sentinelle | Bonus = mod. Charisme (ou +6) à 9 m dès le niveau 7 | Bonus d'initiative = bonus de maîtrise, rayon 3 m (9 m au niveau 18) | corrigé |
| 🔴 majeur | Serment des Guetteurs / sorts | Détection du mal et du bien, « Fausse alarme », Aide, Zone de vérité, Clairvoyance, Œil mystique, Divination, Communication à distance | 3 : Alarme, Détection de la magie ; 5 : Rayon de lune, Voir l'invisible ; 9 : Contresort, Antidétection ; 13 : Aura de vie, Bannissement ; 17 : Immobilisation de monstre, Scrutation | corrigé |
| 🟠 mineur | Aura de protection | Minimum +1 et condition « être conscient » absents ; « tous les alliés » | Mod. Charisme (min +1), créatures amicales à 3 m, paladin conscient ; 9 m au niveau 18 | corrigé |
| 🟠 mineur | Châtiment divin | Bonus +1d8 contre morts-vivants/fiélons omis ; « attaque armée » sans précision | Attaque d'arme au corps à corps ; +1d8 contre mort-vivant ou fiélon (max 6d8) | corrigé |
| 🟠 mineur | Focaliseur de châtiment (Optionnel - TCE) | Nom inventé ; ni action bonus, ni limite de niveau, ni utilisations — renommé « Exploitation du pouvoir divin (option Tasha) » | « Harness Divine Power » : action bonus, emplacement ≤ moitié du bonus de maîtrise (arr. sup.), 1/2/3 fois par repos long aux niv. 3/7/15 | corrigé |
| 🟠 mineur | Incantation | Nombre de sorts préparés, DD et sorts ajoutés par Tasha non indiqués | Préparés = mod. Charisme + moitié du niveau de paladin (min 1) ; DD = 8 + maîtrise + Charisme ; Tasha ajoute 5 sorts | corrigé |
| 🟠 mineur | Polyvalence martiale (TCE) | Option de Tasha absente — ajoutée au niveau 4 « Polyvalence martiale (option Tasha) » | Niveaux 4/8/12/16/19 : possibilité de remplacer le style de combat | corrigé |
| 🟠 mineur | Sens divin | Détecte « le mal et le bien » en général | Détecte célestes, fiélons et morts-vivants à 18 m (hors abri total) + lieux consacrés/profanés ; action, jusqu'à la fin du prochain tour | corrigé |
| 🟠 mineur | Serment de Conquête / Réprimande méprisante | Limité au corps à corps | Toute attaque qui touche ; mod. Charisme (min 1), si non neutralisé | corrigé |
| 🟠 mineur | Serment de Conquête / sorts | « Armure de agathys » | Armure d'Agathys | corrigé |
| 🟠 mineur | Serment de Dévotion / Arme sacrée | Minimum +1, lumière 6 m et durée de 1 min absents | Action, 1 min, + mod. Charisme (min +1) à l'attaque, lumière vive 6 m + faible 6 m | corrigé |
| 🟠 mineur | Serment de Dévotion / Nimbe sacrée | Genre (« Nimbe sacré ») ; durée 1 min et avantage aux JS absents | Action, 1 min, 10 radiants en lumière vive 9 m, avantage aux JS contre sorts de fiélons/morts-vivants | corrigé |
| 🟠 mineur | Serment de Dévotion / sorts | « Protection contre le bien et le mal » (ordre inversé), « Colonne de feu » | VF : Protection contre le mal et le bien ; Colonne de flamme | corrigé |
| 🟠 mineur | Serment de Rédemption / Aura de sacrifice | Nom non officiel ; utilisation de la réaction non indiquée — renommée « Aura du gardien » | Aura du gardien : réaction, subir les dégâts d'une créature à 3 m | corrigé |
| 🟠 mineur | Serment de Vengeance / Ange de la vengeance | Durée (1 h) et vol 18 m absents | Action, 1 heure, vol 18 m, aura de menace 9 m ; 1/repos long | corrigé |
| 🟠 mineur | Serment de Vengeance / Condamnation de l'ennemi | Portée 18 m, vitesse 0 et effet en cas de réussite absents | 18 m ; échec : effrayé + vitesse 0 (1 min) ; réussite : vitesse réduite de moitié | corrigé |
| 🟠 mineur | Serment de Vengeance / Vengeur implacable | Déclenché par toute attaque d'opportunité | Uniquement quand l'attaque d'opportunité touche ; déplacement sans provoquer d'attaque d'opportunité | corrigé |
| 🟠 mineur | Serment de la Gloire / Aura d'entrain | Rayon 3 m ; nom non officiel — renommée « Aura d'alacrité » | +3 m de vitesse pour vous ; alliés commençant leur tour à 1,50 m : +3 m (3 m au niveau 18) | corrigé |
| 🟠 mineur | Serment de la Gloire / Châtiment exaltant | Montant des PV temporaires absent | Action bonus après Châtiment divin : 2d8 + niveau de paladin PV temporaires répartis à 9 m | corrigé |
| 🟠 mineur | Serment des Anciens / Courroux de la nature | Portée 3 m et JS répété non indiqués | Créature visible à 3 m, entravée, JS Force ou Dex à la fin de chacun de ses tours | corrigé |
| 🟠 mineur | Serment des Cendres / sorts | « Châtiment incandescent », « Rayon ardent », « Colonne de feu » | Noms de la base : Châtiment calcinant, Rayon ardent, Colonne de flamme | corrigé |
| 🟠 mineur | Serment des Cendres / sorts | Essaim de météores (sort du 9e niveau) inutilisable par un paladin ; Mur de feu (4e) au niv. 9 | Liste ≤ 5e niveau : Mains brûlantes, Châtiment calcinant / Rayon ardent, Sphère de feu / Boule de feu, Châtiment aveuglant / Mur de feu, Bouclier de feu / Colonne de flamme, Immolation | corrigé |
| 🟠 mineur | Serment des Guetteurs / Aplomb du guetteur | Nombre de cibles et portée absents ; noms non officiels — renommé « Volonté du guetteur & Abjuration de l'extraplanaire » | Volonté du guetteur : mod. Charisme (min 1) créatures à 9 m, avantage aux JS Int/Sag/Cha 1 min | corrigé |
| 🟠 mineur | Serment des Guetteurs / Réprimande vigilante | Montant des dégâts absent | Réaction : 2d8 + mod. Charisme dégâts de force à la créature ayant imposé le JS | corrigé |
| 🟠 mineur | Serment du Sang / sorts | « Vampirisme » et « Drain de vie » ne sont pas des sorts officiels | Remplacés par Toucher du vampire (niv. 9) ; liste : Frayeur, Fléau / Rayon affaiblissant, Cécité/Surdité / Toucher du vampire, Peur / Flétrissement, Confusion / Contagion, Fléau d'insectes | corrigé |
| 🟠 mineur | Style de combat | Option « Combat à deux mains » ambiguë ; options de Tasha absentes | Paladin : Défense, Duel, Arme à deux mains, Protection ; Tasha : Combat en aveugle, Interception, Guerrier béni | corrigé |
| 🟠 mineur | Toucher purificateur | Nom non officiel ; minimum 1 absent — renommé « Contact purifiant » | VF : « Contact purifiant » ; action, mod. Charisme (min 1) utilisations / repos long | corrigé |
| 🔵 info | Champion sacré | Aptitude de base inexistante (placeholder) — supprimée | Au niveau 20, le paladin reçoit uniquement l'aptitude ultime de son serment | corrigé |
| 🔵 info | Options de Tasha (paladin) | Aucune option « Harmonious Smite » / « Châtiment harmonieux » n'existe — seules les options officielles sont présentes | Options TCE : styles de combat, Polyvalence martiale, sorts supplémentaires, Harness Divine Power | corrigé |
| 🔵 info | Serment de la Gloire / Légende vivante | Action bonus, limite « une fois par tour » et recharge par emplacement du 5e niveau omises | Action bonus, 1 min ; 1/repos long ou emplacement du 5e niveau | corrigé |
| 🔵 info | Serment des Anciens / Sentinelle immortelle | Immunité au vieillissement omise | Ne subit plus les effets de l'âge, ne peut pas être vieilli magiquement | corrigé |
| 🔵 info | Serment des Guetteurs / source | « Guide de Wildemount » : source erronée — corrigée en « Chaudron des Merveilles de Tasha » | Oath of the Watchers : Tasha's Cauldron of Everything (2020) | corrigé |
| 🔵 info | Serment du Sang / sorts | Sorts trop élevés pour leur niveau d'obtention (Rayon d'affaiblissement au niv. 3, Fléau d'insectes et Contagion niv. 5 au niv. 13) | Sorts de serment : niveau de sort ≤ emplacements disponibles (1/2/3/4/5 aux niv. 3/5/9/13/17) — liste réordonnée | corrigé |

### Roublard (corrigé) — 29 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Assassin / Coup meurtrier | DD fixe de 14 dans les données | DD = 8 + modificateur de Dextérité + bonus de maîtrise (PHB) | corrigé |
| 🔴 majeur | Enquêteur (Inquisitive) / Vision infaillible | Limitée à 1/repos long ; portée omise | Utilisations = modificateur de Sagesse (min. 1) par repos long, rayon de 9 m | corrigé |
| 🔴 majeur | Fantôme (Phantom) / Bribes des défunts | Obtenue au niveau 6 sous le nom « Bribes funèbres (Jetons d'âme) » — renommée et déplacée au niveau 9 | Bribes des défunts (Tokens of the Departed) au niveau 9 ; le Fantôme n'a rien au niveau 6 | corrigé |
| 🔴 majeur | Fantôme (Phantom) / Murmures des défunts & Lamentations sépulcrales | Dégâts fixes de 5d6 ; utilisations absentes | Moitié des dés d'Attaque sournoise (arrondie au supérieur), bonus de maîtrise fois par repos long | corrigé |
| 🔴 majeur | Lame psychique / Soulknife / Pouvoir psionique & Lames psychiques | Dés psioniques fixés à d12 ; nombre de dés absent | 2 × bonus de maîtrise dés ; d6 (niveau 3), d8 (niveau 5), d10 (niveau 11), d12 (niveau 17) | corrigé |
| 🔴 majeur | Lame psychique / Soulknife / Rupture spirituelle | DD fixe de 14 | DD = 8 + bonus de maîtrise + modificateur de Dextérité ; 1/repos long ou 3 dés psioniques | corrigé |
| 🟠 mineur | Action rusée | Anglicisme « Dasher » | Action Foncer (Dash) | corrigé |
| 🟠 mineur | Arnaqueur arcanique / Escroquerie polyvalente | Nom non officiel « Omniprésence » ; cible « adjacente » à vous | Escroquerie polyvalente (Versatile Trickster) : créature à 1,50 m de la main spectrale | corrigé |
| 🟠 mineur | Arnaqueur arcanique / Voleur de sort | Présenté comme un Contresort | Réaction après un sort qui vous cible : JS contre votre DD de sort, annulation et vol 8 h ; 1/repos long | corrigé |
| 🟠 mineur | Attaque sournoise | Dé fixe « 1d6 » dans le nom ; description sans condition d'arme ni progression — renommée et décrite avec la formule (moitié arrondie au supérieur du niveau de roublard, en d6) | Arme de finesse ou à distance ; 1d6 au niveau 1 puis +1d6 tous les 2 niveaux (10d6 au niveau 19) | corrigé |
| 🟠 mineur | Attaque sournoise | « Allié à 1,5 m » sans préciser qu'il ne doit pas être neutralisé ni l'absence de désavantage | Ennemi de la cible à 1,50 m, non neutralisé, et vous n'avez pas le désavantage | corrigé |
| 🟠 mineur | Bretteur (Swashbuckler) / Jeu de jambes sophistiqué & Audace désinvolte | Faute d'accord « sophistiqués » ; abréviation « mod. » | Jeu de jambes sophistiqué ; modificateur de Charisme | corrigé |
| 🟠 mineur | Bretteur (Swashbuckler) / Panache | « Test de Charisme opposé à la Sagesse » imprécis | Charisme (Persuasion) opposé à Sagesse (Perspicacité), action, 1 minute | corrigé |
| 🟠 mineur | Conspirateur (Mastermind) / Maître des intrigues & Maître tacticien | Jeu (gaming set) et imitation d'accent omis | Matériel de déguisement, de contrefaçon, un jeu, deux langues, imitation après 1 minute d'écoute | corrigé |
| 🟠 mineur | Conspirateur (Mastermind) / Redirection | Condition d'abri absente | La créature à 1,50 m doit vous fournir un abri contre l'attaque | corrigé |
| 🟠 mineur | Coup de chance | « Réussite automatique » sur un test et « 1/repos » ambigu | Le d20 du test est considéré comme un 20 ; une fois par repos court ou long | corrigé |
| 🟠 mineur | Enquêteur (Inquisitive) / Détecteur de mensonges, Œil perçant & Sagacité au combat | Œil perçant non décrit ; durée de Sagacité (1 minute) omise | Œil perçant : action bonus Perception/Investigation ; Sagacité dure 1 minute | corrigé |
| 🟠 mineur | Fantôme (Phantom) / Marche spectrale | Durée et utilisations absentes ; action bonus correcte | 10 minutes, 1/repos long ou en détruisant une babiole d'âme | corrigé |
| 🟠 mineur | Insaisissable | Nom non officiel « Elusif » et accent manquant | Insaisissable (Elusive) | corrigé |
| 🟠 mineur | Lame d'ombre / sorts_domaine | Entrées numériques « 1 » à « 5 » mêlées aux noms de sorts — supprimées | Liste ne devant contenir que des noms de sorts (archétype non lanceur : liste inutilisée) | corrigé |
| 🟠 mineur | Lame d'ombre / sorts_domaine | « Passage dans l'éther » n'existe pas — remplacé par Double illusoire (niveau 5) | Sort officiel « Forme éthérée » (niveau 7), hors de portée d'un roublard | corrigé |
| 🟠 mineur | Perception aveugle | Nom non officiel « Sens aveugle » | Perception aveugle (Blindsense), 3 m | corrigé |
| 🟠 mineur | Visée stable (option Tasha) | Nom non officiel ; vitesse réduite à 0 non mentionnée | Visée stable (TCE) : action bonus, sans s'être déplacé, puis vitesse 0 jusqu'à la fin du tour | corrigé |
| 🟠 mineur | Voleur / Mains lestes & Monte-en-l'air | Bonus de saut en longueur (+ mod. de Dextérité) omis | Saut en longueur avec élan augmenté d'un nombre de pieds égal au modificateur de Dextérité | corrigé |
| 🟠 mineur | Voleur / Réflexes de voleur | Faute de frappe « initiale » ; restriction surprise absente | Initiative normale puis initiative − 10 ; inutilisable si surpris | corrigé |
| 🟠 mineur | Éclaireur (Scout) / Escarmoucheur & Survivaliste | Déclencheur « un ennemi s'approche » inexact | Réaction quand un ennemi termine son tour à 1,50 m de vous | corrigé |
| 🟠 mineur | Éclaireur (Scout) / Frappe soudaine | Restriction de cible omise | Pas deux Attaques sournoises contre la même cible le même tour | corrigé |
| 🔵 info | Arnaqueur arcanique / Sorts & Passe-passe à distance | Emplacements, sorts connus et DD absents | Lanceur au tiers (Intelligence) : 3 sorts connus au niveau 3 jusqu'à 13 ; emplacements jusqu'au niveau 4 | corrigé |
| 🔵 info | Arnaqueur arcanique / sorts_domaine | Liste fixe de sorts fournie, alors que l'archétype n'en a pas — liste vidée | Choix libre parmi les sorts de magicien (enchantement/illusion, sauf 4 choix libres) | corrigé |

### Rôdeur (corrigé) — 45 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Arpenteur de l'horizon / Détection de portail & Guerrier planaire | +2d8 dès le niveau 3 | +1d8 de force au niveau 3, 2d8 au niveau 11 | corrigé |
| 🔴 majeur | Arpenteur de l'horizon / sorts_domaine | Lévitation, Clairvoyance et Porte dimensionnelle ne sont pas les sorts du conclave | Protection contre le mal et le bien, Foulée brumeuse, Hâte, Bannissement, Cercle de téléportation | corrigé |
| 🔴 majeur | Chasseur / Proie du chasseur | « Tueur de géants (+1d8 sur cible blessée) » confond deux options | Tueur de colosses = +1d8 une fois par tour sur cible blessée ; Tueur de géants = attaque en réaction contre une créature G+ à 1,50 m | corrigé |
| 🔴 majeur | Disparition | « Ne peut plus être traqué par des moyens magiques » | Ne peut plus être pisté par des moyens NON magiques (sauf s'il le souhaite) | corrigé |
| 🔴 majeur | Ennemi juré / Explorateur passionné (Optionnel) | L'option décrite (expertise, vitesse, nage/escalade) est celle d'Explorateur expert, pas un remplaçant d'Ennemi juré | Tasha remplace Ennemi juré par Ennemi favori : marque 1 min (concentration), +1d4 (1d6 niv. 6, 1d8 niv. 14), bonus de maîtrise fois/repos long | corrigé |
| 🔴 majeur | Gardien des nuées / Dispersion de la nuée | « 6 fois/repos long » fixe | Un nombre de fois égal au bonus de maîtrise par repos long | corrigé |
| 🔴 majeur | Gardien des nuées / Marée frémissante | « 6 fois/repos long » fixe | Un nombre de fois égal au bonus de maîtrise par repos long | corrigé |
| 🔴 majeur | Gardien des nuées / Nuée spirituelle | DD 14 fixe ; « +1d8 » ajouté | DD = DD des sorts ; les 1d6 deviennent 1d8, mise à terre sur échec, demi-abri quand vous êtes déplacé | corrigé |
| 🔴 majeur | Gardien des nuées / sorts_domaine | Nappe de brouillard, Lévitation, Vent hurlant, Liberté de mouvement, Appel de la foudre : liste fausse | Main de mage + Lueurs féeriques, Toile d'araignée, Forme gazeuse, Œil magique, Fléau d'insectes | corrigé |
| 🔴 majeur | Maître des bêtes / Compagnon du rôdeur / Compagnon primordial | Bonus fixe « +6 » à CA, attaque, dégâts et JS | Bonus = bonus de maîtrise du rôdeur ; PV = max(normaux, 4 × niveau de rôdeur) | corrigé |
| 🔴 majeur | Rôdeur / niveaux 6, 10 et 14 | Aucune entrée pour les améliorations d'Ennemi juré / Explorateur-né | Niveau 6 : ennemi + terrain supplémentaires ; niveau 10 : terrain supplémentaire ; niveau 14 : ennemi supplémentaire (ou Vagabond niv. 6 / Infatigable niv. 10 de Tasha) | corrigé |
| 🔴 majeur | Traqueur des ténèbres / sorts_domaine | Liste fausse : Nappe de brouillard, Flou, Rapidité, « Insondable » (inexistant) | Déguisement, Corde enchantée, Peur, Invisibilité supérieure, Apparence trompeuse | corrigé |
| 🔴 majeur | Tueur de monstres / Sens du chasseur & Proie du tueur | Sens du chasseur : 1/repos long | Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long | corrigé |
| 🔴 majeur | Tueur de monstres / sorts_domaine | Protection contre l'énergie et Sonde mentale au lieu des sorts officiels | Protection contre le mal et le bien, Zone de vérité, Cercle magique, Bannissement, Immobilisation de monstre | corrigé |
| 🔴 majeur | Vagabond féérique / Charme mystique & Don des fées | Bonus fixe +1 aux tests de Charisme | Bonus = modificateur de Sagesse (minimum +1) | corrigé |
| 🔴 majeur | Vagabond féérique / Charme mystique & Don des fées | Frappes redoutables (1d4 psychiques) absentes au niveau 3 | Niveau 3 : +1d4 psychiques une fois par tour ; 1d6 au niveau 11 | corrigé |
| 🔴 majeur | Vagabond féérique / Vagabond des brumes | Foulée brumeuse gratuite 1/repos long | Un nombre de fois égal au modificateur de Sagesse (min. 1) par repos long | corrigé |
| 🔴 majeur | Vagabond féérique / sorts_domaine | Calme des émotions, « Appel de la fée » (inexistant), Domination de personne | Charme-personne, Foulée brumeuse, Dissipation de la magie, Porte dimensionnelle, Double illusoire | corrigé |
| 🟠 mineur | Arpenteur de l'horizon / Détection de portail & Guerrier planaire | Limitation de Détection de portail absente | Une action, une fois par repos court ou long | corrigé |
| 🟠 mineur | Arpenteur de l'horizon / Frappe à distance | « Jusqu'à 3 attaques distinctes » imprécis | Attaque supplémentaire contre une 3e créature si au moins deux créatures différentes ont été attaquées | corrigé |
| 🟠 mineur | Arpenteur de l'horizon / Pas éthéré | Sort nommé « Périple éthéré » ; durée et recharge imprécises | Forme éthérée, se termine à la fin du tour, une fois par repos court ou long | corrigé |
| 🟠 mineur | Camouflage / Invisibilité temporelle (Optionnel) | Nom « Invisibilité temporelle » et nombre d'utilisations absents | Tasha : Voile de la nature, action bonus, invisible jusqu'au début du prochain tour, bonus de maîtrise fois/repos long | corrigé |
| 🟠 mineur | Camouflage / Invisibilité temporelle (Optionnel) | Le +10 en Discrétion et la minute de préparation ne sont pas indiqués | PHB : 1 minute de camouflage, +10 aux tests de Discrétion tant qu'immobile contre une surface | corrigé |
| 🟠 mineur | Chasseur / Attaque multiple | Zone de la Volée non précisée ; nom « Salve » | Volée : créatures à 3 m d'un point visible à portée ; Attaque tourbillonnante : créatures à 1,50 m | corrigé |
| 🟠 mineur | Chasseur / Défense de chasseur supérieure | « Déplacement fluide » n'existe pas ; « Esquive totale » mal nommée | Options : Dérobade, Résister à la marée, Esquive instinctive | corrigé |
| 🟠 mineur | Chasseur / Tactique défensive | « Tactique de défense contre les géants » et « Volonté de fer » n'existent pas | Défense contre les attaques multiples (+4 CA contre le même attaquant) et Volonté d'acier (avantage contre effrayé) | corrigé |
| 🟠 mineur | Ennemi juré / Explorateur passionné (Optionnel) | Description incomplète : langue apprise et ennemis supplémentaires absents | PHB : une langue de l'ennemi, ennemi juré supplémentaire aux niveaux 6 et 14 | corrigé |
| 🟠 mineur | Explorateur natif / Explorateur habile (Optionnel) | Noms non officiels « Explorateur natif » / « Explorateur habile » | PHB : Explorateur-né ; Tasha : Explorateur expert (Habile 1, Vagabond 6, Infatigable 10) | corrigé |
| 🟠 mineur | Gardien des nuées / Magie de la nuée & Nuée magique | Effets d'Essaim rassemblé non décrits | 1 fois/tour après un coup : 1d6 perforants, ou JS Force sinon déplacé de 4,50 m, ou vous déplacer de 1,50 m | corrigé |
| 🟠 mineur | Maître des bêtes / Compagnon du rôdeur / Compagnon primordial | Profils du Compagnon primal de Tasha absents | CA 13 + bonus de maîtrise, PV 5 + 5 × niveau (ciel 4 + 4 ×), attaque = attaque des sorts, 1d8 + 2 + bonus de maîtrise | corrigé |
| 🟠 mineur | Maître des bêtes / Entraînement exceptionnel & Attaque de la bête magique | Esquiver absent et attaques magiques non décrites | Foncer, Se désengager, Esquiver ou Aider en action bonus ; attaques magiques (Tasha : dégâts de force) | corrigé |
| 🟠 mineur | Maître des bêtes / Lien partagé | Nom non officiel | PHB : Partage des sorts | corrigé |
| 🟠 mineur | Rôdeur / options de Tasha | Options « Capacités de classe optionnelles » absentes : styles de combat supplémentaires, Focaliseur d'incantation, Polyvalence martiale, sorts additionnels | Tasha : focaliseur druidique (niv. 2), changement de style/sort aux niveaux d'ASI, liste de sorts étendue | corrigé |
| 🟠 mineur | Sens des bêtes | Nom non officiel et portée de 9 m absente | Sens sauvages : pas de désavantage contre les créatures non vues ; position des invisibles non cachées à 9 m | corrigé |
| 🟠 mineur | Style de combat | Styles de Tasha (Combat à l'aveugle, Guerrier druidique, Armes de lancer) non mentionnés | Tasha ajoute ces trois styles au rôdeur | corrigé |
| 🟠 mineur | Traqueur de sang / sorts_domaine | « Vampirisme » n'est pas un nom de sort | Caresse du vampire (Vampiric Touch, 3e niveau) — nom de la base : Toucher du vampire | corrigé |
| 🟠 mineur | Traqueur des ténèbres / Embuscade effrayante & Vision des ombres | « Invisibilité totale dans les ténèbres » ; bonus d'initiative non chiffré | Invisible seulement pour les créatures qui comptent sur la vision dans le noir ; initiative + modificateur de Sagesse | corrigé |
| 🟠 mineur | Traqueur des ténèbres / Esquive des ombres | Condition omise | Utilisable seulement si l'attaquant n'a pas l'avantage | corrigé |
| 🟠 mineur | Traqueur des ténèbres / Mental d'acier | Typo « Inteligence » ; « Sagesse/Charisme/Intelligence » ambigu ; nom | Esprit de fer : maîtrise JS Sagesse, sinon Intelligence OU Charisme | corrigé |
| 🟠 mineur | Tueur de monstres / Contre-attaque du tueur | Effet principal omis | Si l'attaque touche, la sauvegarde est automatiquement réussie | corrigé |
| 🟠 mineur | Tueur de monstres / Némésis des mages | « Contrer » imprécis : téléportation et DD absents | Réaction contre un sort ou une téléportation à 18 m, JS Sagesse contre le DD des sorts, 1/repos court ou long | corrigé |
| 🟠 mineur | Vagabond féérique / Coups effroyables & Renforts féériques | Option sans concentration de Convocation de fée omise | Sans composante matérielle ; peut se lancer sans concentration (durée 1 minute) | corrigé |
| 🟠 mineur | Vigilance arcanique / Conscience de la nature | Noms non officiels ; description (« créatures magiques ») imprécise | PHB : Conscience primitive (emplacement dépensé, 1 min/niveau, 1,5 km ou 9 km) ; Tasha : sorts gratuits Communication avec les animaux, Sens animal, etc. | corrigé |
| 🔵 info | Maître des bêtes / Fureur bestiale | Bonus Marque du chasseur de la version Tasha non mentionné | Tasha : +1d6 de force la 1re fois par tour contre une cible de Marque du chasseur | corrigé |
| 🔵 info | Traqueur de sang / sorts_domaine | Peur (3e niveau) et Flétrissement (4e niveau) placés aux rangs 4 et 5 | Liste refaite : Frayeur, Rayon affaiblissant, Toucher du vampire, Flétrissement, Contagion (niveau de sort = palier) | corrigé |

### Espèces (corrigé) — 220 point(s)

| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |
|---|---|---|---|---|
| 🔴 majeur | Aarakocra / Appel du vent | Trait absent | Ajouté : Bourrasque niv. 3, 1/repos long ou emplacements, Int/Sag/Cha | corrigé |
| 🔴 majeur | Aarakocra / vitesse | Vol = marche sans précision (mélange EE/MotM) | Vol 9 m = marche, interdit en armure intermédiaire/lourde ; marche 9 m (défaut) | corrigé |
| 🔴 majeur | Aasimar déchu / Mains guérisseuses | Trait absent | Ajouté (Volo) : action, PV = niveau, 1/repos long | corrigé |
| 🔴 majeur | Aasimar déchu / Voile nécrotique | Effroi et DD absents | Action, effroi à 3 m (JS Cha DD 8 + maîtrise + Cha), +niveau nécrotiques 1/tour | corrigé |
| 🔴 majeur | Aasimar protecteur / Mains guérisseuses | Trait absent | Ajouté (Volo) : action, PV = niveau, 1/repos long | corrigé |
| 🔴 majeur | Aasimar protecteur / Transformation céleste | Action non précisée | Renommé Âme radieuse : action, vol 9 m, +niveau radiants 1/tour, 1 min, 1/repos long | corrigé |
| 🔴 majeur | Autognome / Conçu pour réussir | 6 fois/repos long | Bonus de maîtrise fois/repos long | corrigé |
| 🔴 majeur | Autognome / Machine de guérison | Réparation rend 1d6 PV | Réparation : dépense d'un dé de vie + Con ; liste des sorts de soin officielle | corrigé |
| 🔴 majeur | Conil / Saut de lapin | 9 m fixe, 6 fois/repos long | 1,50 m × maîtrise, maîtrise fois/repos long | corrigé |
| 🔴 majeur | Demi-dragon / Arme de souffle | Ni dégâts, ni DD, ni utilisations | Cône 4,50 m, DD 8 + maîtrise + Con, 2d6 → 5d6, 1/repos court ou long | corrigé |
| 🔴 majeur | Demi-elfe | Espèce absente (Manuel des Joueurs) | Ajoutée : Cha +2 et +1 à deux AUTRES caractéristiques, vision 18 m, ascendance féerique, polyvalence (2 compétences), Commun + Elfique + 1 langue | corrigé |
| 🔴 majeur | Dhampir / Morsure vampirique | Soin systématique, sans limite | 1d4 + Con ; soin ou bonus au choix, maîtrise fois/repos long | corrigé |
| 🔴 majeur | Dhampir / vitesse | 9 m par défaut | 10,5 m (marche et escalade) | corrigé |
| 🔴 majeur | Drakéide / Souffle | Absent | Ajouté : action, 2d6 → 5d6, DD 8 + maîtrise + Con, 1/repos court ou long | corrigé |
| 🔴 majeur | Drow (Elfe noir) | Espèce absente (sous-espèce elfe du Manuel des Joueurs) | Ajoutée : Dex +2, Cha +1, vision 36 m, sensibilité au soleil, magie drow (Lumières dansantes, Lueurs féeriques au niv. 3, Ténèbres au niv. 5, Charisme), rapière / épée courte / arbalète de poing, plus les traits elfes communs (ascendance féerique, sens aiguisés, transe) | corrigé |
| 🔴 majeur | Duergar / vitesse | 7,5 m (MToF) | MotM : 9 m | corrigé |
| 🔴 majeur | Eladrin / Changement de saison | Sorts mineurs inventés | Effets de saison MotM sur le Pas féerique (niv. 3), DD 8 + maîtrise + Int/Sag/Cha | corrigé |
| 🔴 majeur | Eladrin / Pas féerique | 1/repos long | Action bonus, 9 m, maîtrise fois/repos long | corrigé |
| 🔴 majeur | Eladrin / traits elfiques | Absents | Vision 18 m, Ascendance féerique, Sens aiguisés, Transe ajoutés | corrigé |
| 🔴 majeur | Elfe | Espèce de base absente (seules des variantes existaient) | Ajoutée : Dex +2, vision 18 m, ascendance féerique, sens aiguisés, transe ; sous-espèces Haut-elfe (Int +1, armes elfiques, sort mineur de magicien, langue) et Elfe des bois (Sag +1, vitesse 10,5 m, armes elfiques, cachette naturelle) | corrigé |
| 🔴 majeur | Elfe astral / Pas de lumière étoilée | 6 fois/repos long | Action bonus, 9 m, maîtrise fois/repos long | corrigé |
| 🔴 majeur | Elfe des mers / vitesse de nage | Absente | Enfant de la mer : nage = marche (9 m), respiration air/eau | corrigé |
| 🔴 majeur | Fadette / vitesse de vol | Sans valeur | Vol 9 m = marche, interdit en armure intermédiaire/lourde | corrigé |
| 🔴 majeur | Firbolg / Pas invisible | Fin du tour suivant, 6 fois | Jusqu'au début du prochain tour ou attaque/dégâts/JS, maîtrise fois/repos long | corrigé |
| 🔴 majeur | Féral / Métamorphose | 12 PV temp. fixes, usages absents | 2 × maîtrise PV temp., maîtrise fois/repos long | corrigé |
| 🔴 majeur | Féral / source | « Guide de Xanathar / Homebrew » | Monstres du Multivers (version la plus récente du Shifter) | corrigé |
| 🔴 majeur | Genasi (4) / version | Les quatre genasi suivaient EE 2015 malgré la source MotM | Alignés sur MotM 2022 : +2/+1 ou +1/+1/+1, Commun + 1 au choix, taille Moyenne ou Petite, VD 18 m | corrigé |
| 🔴 majeur | Genasi d'air / Mêlé au vent | Lévitation dès le niveau 1 | Poigne électrique ; niv. 3 Feuille morte ; niv. 5 Lévitation ; 1/repos long ou emplacements | corrigé |
| 🔴 majeur | Genasi d'air / traits MotM | VD et résistance à la foudre absentes | Traits ajoutés | corrigé |
| 🔴 majeur | Genasi d'air / vitesse | 9 m par défaut | 10,5 m | corrigé |
| 🔴 majeur | Genasi d'eau / Appel de la vague | Façonnage de l'eau + Création d'eau | Aspersion d'acide ; niv. 3 Création ou destruction d'eau ; niv. 5 Marche sur l'eau | corrigé |
| 🔴 majeur | Genasi de feu / sort mineur | « *Flamme* » résolu en Flamme sacrée | *Flammes* ; niv. 5 Lame de feu ajoutée | corrigé |
| 🔴 majeur | Genasi de terre / Fusion avec la pierre | Passage sans trace au niv. 1, Protection contre les armes absente | Protection contre les armes (action bonus, bonus de maîtrise fois/repos long) ; niv. 3 Passage sans trace | corrigé |
| 🔴 majeur | Giff / vitesse de nage | Nage absente | Trait Nageur : nage = marche | corrigé |
| 🔴 majeur | Giff / Étincelle astrale | +6 force, 6 fois/repos long | Bonus de maîtrise en force, 1/tour, BM fois/repos long | corrigé |
| 🔴 majeur | Githyanki / Maîtrises | Armures + langue + compétence (MToF) | Savoir astral (compétence + arme/outil par repos long) | corrigé |
| 🔴 majeur | Githyanki / Résilience psychique | Absente | Résistance aux dégâts psychiques | corrigé |
| 🔴 majeur | Githzerai / Défense mentale | +1 CA inventé | Remplacé par Discipline mentale (avantage contre charmé/effrayé) | corrigé |
| 🔴 majeur | Githzerai / Résilience psychique | Absente | Résistance aux dégâts psychiques | corrigé |
| 🔴 majeur | Gnome des profondeurs / Don du svirfnebelin | Absent | Niv. 3 Déguisement, niv. 5 Antidétection, 1/repos long | corrigé |
| 🔴 majeur | Gnome des profondeurs / vitesse | 7,5 m (MToF/EE) | 9 m (MotM) | corrigé |
| 🔴 majeur | Gobelin / Fureur des petits | +6 dégâts, 6 fois/repos long | Bonus de maîtrise, 1/tour, BM fois/repos long | corrigé |
| 🔴 majeur | Gobelours / Attaque surprise | Ennemi surpris au 1er tour (Volo) | Créature n'ayant pas encore joué, 1/combat | corrigé |
| 🔴 majeur | Goliath / Endurance de pierre | 1/repos long, modificateur non précisé | 1d12 + Con, BM fois/repos long | corrigé |
| 🔴 majeur | Goliath / source | « Manuel des Joueurs / MtoM » | Monstres du Multivers (version appliquée) | corrigé |
| 🔴 majeur | Goliath / taille | Grande | Moyenne (+ Puissante carrure via Petit géant) | corrigé |
| 🔴 majeur | Grung / Vigilance arboricole | Absente | Maîtrise de Perception | corrigé |
| 🔴 majeur | Grung / source | « One-D&D / Homebrew » | One Grung Above (DMs Guild, WotC) | corrigé |
| 🔴 majeur | Grung / vitesse | 9 m par défaut | 7,5 m, escalade 7,5 m | corrigé |
| 🔴 majeur | Hadozi / Esquive | 6 fois/repos long | Réaction, 1d6 + BM, BM fois/repos long | corrigé |
| 🔴 majeur | Harengon / Saut de lapin | Distance non chiffrée, 6 fois/repos long | 1,50 m × BM, BM fois/repos long | corrigé |
| 🔴 majeur | Hobgobelin / Chance du nombre | 6 fois/repos long | BM fois/repos long | corrigé |
| 🔴 majeur | Hobgobelin / Don féerique | Niv. 3, 6 fois ; *Aider* en italique | Dès le niv. 1, BM fois ; options au niv. 3 ; sans italique | corrigé |
| 🔴 majeur | Homme lézard / Mâchoires affamées | 6 PV temp., 6 fois/jour | PV temp. = BM, BM fois/repos long | corrigé |
| 🔴 majeur | Homme lézard / nage | Absente | Trait Nageur : nage = marche | corrigé |
| 🔴 majeur | Hybride Simic / caractéristiques | « Con +2, autre +1 » : le +1 libre n'était pas lu | « Con +2, +1 » | corrigé |
| 🔴 majeur | Kalashtar / Lien mental | 1,5 km fixe | 3 m × niveau de personnage | corrigé |
| 🔴 majeur | Kender / Intrépide | Avantage 1/repos long | Avantage permanent + échec → réussite 1/repos long | corrigé |
| 🔴 majeur | Kender / Provocation | Ni JS, ni portée, ni utilisations | 18 m, JS Sag DD 8 + BM + Int/Sag/Cha, BM fois/repos long | corrigé |
| 🔴 majeur | Kender / vitesse | 7,5 m | 9 m | corrigé |
| 🔴 majeur | Kenku / Mémoire kenku | Liste de 4 compétences (Volo) | 2 compétences au choix + avantage BM fois/repos long | corrigé |
| 🔴 majeur | Kobold / Cri draconique | 6 fois/repos long, portée absente | Action bonus, ennemis à 3 m, avantage jusqu'au début du prochain tour, bonus de maîtrise fois/repos long | corrigé |
| 🔴 majeur | Locathah / Observateur et athlétique | Trait absent | Ajouté : Athlétisme et Perception | corrigé |
| 🔴 majeur | Loxodon / Trompe | Soulève 50 kg (fixe) | 2,5 kg × Force, allonge 1,50 m, tuba, aucune arme ni tâche de précision | corrigé |
| 🔴 majeur | Léonin / Rugissement intimidant | DD 14 fixe, 1 fois/repos long | Renommé ; DD 8 + maîtrise + Con, effrayé jusqu'à la fin du prochain tour, repos court ou long | corrigé |
| 🔴 majeur | Léonin / vitesse | 9 m par défaut | 10,5 m | corrigé |
| 🔴 majeur | Minotaure / Cornes martelantes | DD 14 fixe | Action bonus après attaque de l'action Attaquer, JS For DD 8 + maîtrise + For, taille max +1 | corrigé |
| 🔴 majeur | Nain des montagnes / caractéristiques | Con +2, For +1 | MdJ : Con +2 (nain) et For +2 (nain des montagnes) | corrigé |
| 🔴 majeur | Orc / Endurance implacable | Trait absent | Ajouté : 1 PV au lieu de 0, 1/repos long | corrigé |
| 🔴 majeur | Orc / Poussée d'adrénaline | « Agressif » : action bonus Foncer | Renommé ; + PV temporaires = bonus de maîtrise, bonus de maîtrise fois, repos court ou long | corrigé |
| 🔴 majeur | Satyre / Sauts joyeux | Sauts augmentés de 1d6/2 mètres | +1d8 × 30 cm ; renommé | corrigé |
| 🔴 majeur | Satyre / vitesse | 9 m par défaut | 10,5 m | corrigé |
| 🔴 majeur | Shadar-kai / Bénédiction de la Reine corbeau | Résistance nécrotique, 6 fois/repos long | Renommé ; bonus de maîtrise fois/repos long, résistance à tous les dégâts au niveau 3 | corrigé |
| 🔴 majeur | Shadar-kai / Résistance nécrotique | Pas de trait permanent séparé | Ajouté | corrigé |
| 🔴 majeur | Tabaxi / vitesse d'escalade | Escalade absente | Escalade = marche (dans Griffes) | corrigé |
| 🔴 majeur | Tieffelin féral / Langue du diable | « Envoûtement » introuvable ; niveaux absents | Moquerie cruelle, Charme-personne niv. 3, Discours captivant niv. 5 | corrigé |
| 🔴 majeur | Tieffelin féral / traits de base | Résistance au feu et vision dans le noir absentes | Ajoutées | corrigé |
| 🔴 majeur | Tieffelin féral / variantes cumulées | Ailé ET Langue du diable ensemble | Un seul trait « variante au choix » : Héritage infernal, Langue du diable, Feu infernal ou Ailé | corrigé |
| 🔴 majeur | Tortle / Défense de carapace | Action bonus pour se retirer | Action pour se retirer, action bonus pour sortir, avantage JS For/Con, à terre ; renommé | corrigé |
| 🔴 majeur | Triton / Contrôle de l'air et de l'eau | Sorts sans niveau d'obtention | Nappe de brouillard niv. 1, Bourrasque niv. 3, Marche sur l'eau niv. 5, 1/repos long ou emplacements | corrigé |
| 🟠 mineur | Aarakocra / Serres | 1d4 tranchants | 1d6 + For tranchants (mains nues) | corrigé |
| 🟠 mineur | Aarakocra / caractéristiques | Dex +2, Sag +1 (EE) | MotM : +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Aarakocra / langues | Commun, Aarakocra | Commun + Au choix (MotM) | corrigé |
| 🟠 mineur | Aasimar / langues | Commun + Au choix | Volo : Commun, Céleste | corrigé |
| 🟠 mineur | Aasimar déchu / caractéristiques | +2, +1 libres | Volo : Cha +2, For +1 | corrigé |
| 🟠 mineur | Aasimar protecteur / caractéristiques | +2, +1 libres | Volo : Cha +2, Sag +1 | corrigé |
| 🟠 mineur | Autognome / Nature mécanique | Respiration omise | Pas besoin de respirer ajouté | corrigé |
| 🟠 mineur | Autognome / caractéristiques | +2, +1 | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Autognome / taille et type | Absents | Trait Taille et type : Petite, Créature artificielle | corrigé |
| 🟠 mineur | Centaure / Charge | Formulation imprécise | 9 m en ligne droite + attaque d'arme au corps à corps → Sabots en action bonus | corrigé |
| 🟠 mineur | Centaure / Morphologie équine | Capacité vague, escalade absente | Renommé ; compte comme Grande, +4 m par mètre d'escalade | corrigé |
| 🟠 mineur | Centaure / Sabots | 1d6 sans modificateur | 1d6 + For contondants | corrigé |
| 🟠 mineur | Centaure / type | Absent | Moyenne, Fée | corrigé |
| 🟠 mineur | Changelin / Instincts | Représentation absente | Liste MotM à 5 compétences | corrigé |
| 🟠 mineur | Changelin / caractéristiques | Cha +2, +1 (Eberron) | MotM : +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Changelin / langues | Commun + 2 au choix | Commun + Au choix (MotM) | corrigé |
| 🟠 mineur | Changelin / taille et type | Absents | Moyenne ou Petite, Fée | corrigé |
| 🟠 mineur | Changeling ténébreux / Frappe ténébreuse | Dégâts et repos non chiffrés | Homebrew rééquilibré : 1d6 → 4d6 (niv. 6/11/16), 1/repos court ou long | corrigé |
| 🟠 mineur | Changeling ténébreux, Demi-dragon, Golem miniature, Naïade, Orc cendré | Espèces non retenues pour le référentiel | Retirées | corrigé |
| 🟠 mineur | Conil / Gambade heureuse | Réaction non précisée | Réaction, +1d4 au JS de Dex raté | corrigé |
| 🟠 mineur | Dhampir / Ascension de l'araignée | Murs et plafonds dès le niveau 1 | Escalade niv. 1, surfaces verticales/plafonds niv. 3 | corrigé |
| 🟠 mineur | Dhampir / caractéristiques | +2, +1 | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Drakéide / Ascendance draconique | Pas de table des dragons | Table des 10 dragons (dégâts, zone, JS) | corrigé |
| 🟠 mineur | Duergar / Magie duergar | Cible et carac. non précisées | Sur soi, sans composante matérielle, emplacements, Int/Sag/Cha | corrigé |
| 🟠 mineur | Duergar / Résistance mentale | Nom non officiel | Renommé Fortitude psionique | corrigé |
| 🟠 mineur | Duergar / caractéristiques | +2, +1 | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Duergar / langues | Commun, Nain | Commun + Au choix (MotM) | corrigé |
| 🟠 mineur | Eladrin / caractéristiques | Dex +2, +1 (Int ou Cha) | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Eladrin / langues | Commun, Elfique | Commun + Au choix (MotM) | corrigé |
| 🟠 mineur | Elfe astral / Feu astral | Carac. absente | Int, Sag ou Cha | corrigé |
| 🟠 mineur | Elfe astral / Transe astrale | « Immunité au sommeil magique » | Pas besoin de dormir, ne peut être endormi par magie ; compétence + arme/outil | corrigé |
| 🟠 mineur | Elfe des mers / Ami de la mer | « Animaux marins » | Bêtes, Élémentaires, Créatures monstrueuses avec vitesse de nage (MotM) | corrigé |
| 🟠 mineur | Elfe des mers / Maîtrise | Perception et charme confondus | Séparés en Sens aiguisés et Ascendance féerique | corrigé |
| 🟠 mineur | Elfe des mers / Transe | Sans maîtrises temporaires | 2 maîtrises d'arme/outil jusqu'au repos long | corrigé |
| 🟠 mineur | Elfe des mers / source | Libellé long | « Monstres du Multivers » | corrigé |
| 🟠 mineur | Elfe sylvestre | Doublon : nom VF de l'Elfe des bois (Wood Elf) du Manuel des Joueurs | Retiré ; l'Elfe des bois est la sous-espèce de l'Elfe | corrigé |
| 🟠 mineur | Elfe sylvestre / Cachette naturelle | Formulation vague | Légèrement masqué par feuillage, pluie, neige, brume | corrigé |
| 🟠 mineur | Enfant de la lune | Doublon du Féral | Retiré ; anciennes fiches converties en Féral | corrigé |
| 🟠 mineur | Enfant de la lune / Posture hybride | Valeurs non chiffrées | Homebrew rééquilibré : action bonus, 1 min, 2 × maîtrise PV temp., +1d4 griffes, 1/repos court ou long | corrigé |
| 🟠 mineur | Fadette / Magie des fadettes | Carac. absente, coquille | Lueurs féeriques, emplacements, Int/Sag/Cha | corrigé |
| 🟠 mineur | Fadette / caractéristiques | +2, +1 | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Fadette / type | Absent | Petite, Fée | corrigé |
| 🟠 mineur | Firbolg / Magie firbolg | Option 90 cm absente | Ajoutée, + emplacements, Int/Sag/Cha | corrigé |
| 🟠 mineur | Firbolg / Parler aux bêtes et plantes | « Avantage de charme » | Avantage aux tests de Charisme pour les influencer | corrigé |
| 🟠 mineur | Firbolg / Puissante carrure | Absent | Ajouté | corrigé |
| 🟠 mineur | Firbolg / caractéristiques | +2, +1 | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Forgelier / Protection intégrée | +1 CA seul | Armure intégrée en 1 h, inamovible contre son gré | corrigé |
| 🟠 mineur | Forgelier / Résilience | Respiration omise | Pas besoin de respirer ; sommeil magique | corrigé |
| 🟠 mineur | Forgelier / type | Absent | Humanoïde | corrigé |
| 🟠 mineur | Féral / Chasse sauvage | Avantage aux JS de Sagesse | Avantage aux tests de Sagesse, pas d'avantage contre vous à 9 m | corrigé |
| 🟠 mineur | Féral / Longs crocs | Ni action ni modificateur | Action bonus, 1d6 + For perforants | corrigé |
| 🟠 mineur | Féral / Pas rapides | +3 m seul | +3 m et réaction de déplacement de 3 m | corrigé |
| 🟠 mineur | Féral / Peau de bête | +1 CA seul | +1d6 PV temp. et +1 CA | corrigé |
| 🟠 mineur | Féral / caractéristiques | +2, +1 | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Genasi / langues et taille | Commun, Primordial ; taille absente | Commun + 1 au choix ; Moyenne ou Petite | corrigé |
| 🟠 mineur | Genasi d'eau / nage | Vitesse de nage non chiffrée | Nage = marche (9 m) | corrigé |
| 🟠 mineur | Giff / caractéristiques | +2, +1 sans alternative | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Githyanki / Psionique | Main invisible non précisée | Main invisible, emplacements, sans composante, Int/Sag/Cha | corrigé |
| 🟠 mineur | Githyanki, Githzerai / carac. et langues | Valeurs MToF | +2/+1 ou +1/+1/+1 ; Commun + 1 au choix | corrigé |
| 🟠 mineur | Gnome des forêts / taille et traits | Taille absente ; Illusionniste-né et Communication fusionnés | Taille Petite ; deux traits distincts précis | corrigé |
| 🟠 mineur | Gnome des profondeurs / Camouflage | Avantage sur terrain rocheux (EE) | Avantage en Discrétion, BM fois/repos long | corrigé |
| 🟠 mineur | Gnome des profondeurs / Ruse, carac., langues | Libellé flou ; valeurs EE | Contre les sorts ; MotM | corrigé |
| 🟠 mineur | Gnome des roches / Savoir de l'artificier, Bricoleur, taille | Libellés imprécis ; taille absente | Double maîtrise Histoire ; mécanismes détaillés ; Petite | corrigé |
| 🟠 mineur | Gobelin / Ascendance féerique, carac., langues | Absente ; valeurs Volo | Ajoutée ; MotM | corrigé |
| 🟠 mineur | Gobelours / allonge, traits, carac., langues | Allonge non chiffrée ; Puissante carrure et Ascendance absentes | +1,50 m ; traits ajoutés ; MotM | corrigé |
| 🟠 mineur | Golem miniature / Surcharge à vapeur (homebrew) | Effet non chiffré (action « fulgurante ») | Action bonus : +3 m et Foncer ou Se désengager, 1/repos court ; Nature de construct précisée (empoisonné) | corrigé |
| 🟠 mineur | Goliath / Né des montagnes, carac. | Altitude absente ; valeurs Volo | Acclimatation ajoutée ; MotM | corrigé |
| 🟠 mineur | Grung / Peau venimeuse, taille | Contact = 2d4 ; taille absente | Contact = empoisonné 1 min ; 2d4 via arme ; Petite | corrigé |
| 🟠 mineur | Hadozi / Planer, carac. | Distance absente ; sans alternative | Distance = vitesse de marche ; MotM | corrigé |
| 🟠 mineur | Halfelin robuste / Agilité halfeline | Trait commun aux halfelins absent | Ajouté | corrigé |
| 🟠 mineur | Halfelins / taille, Chanceux | Taille absente ; jet non précisé | Petite ; 1 naturel sur attaque, test ou JS | corrigé |
| 🟠 mineur | Harengon / Gambade, taille, carac. | Réaction absente ; taille absente | Réaction ; Moyenne ou Petite ; MotM | corrigé |
| 🟠 mineur | Harengon / Mort-vivant | Doublons du Conil et du Revenant | Retirés | corrigé |
| 🟠 mineur | Homme lézard / Morsure | Sans modificateur | 1d6 + For tranchants | corrigé |
| 🟠 mineur | Humain | Aucun trait listé (le panneau gardait les traits de la race précédente) | Traits « Augmentation de caractéristiques » et « Langues » | corrigé |
| 🟠 mineur | Humain variant | Affichait « aucun bonus » tant que les +1 n'étaient pas répartis ; don et compétence sans effet | +1 / +1 sur deux caractéristiques différentes, emplacement de don, rappel de la compétence à choisir | corrigé |
| 🟠 mineur | Hybride Simic / Améliorations | Options niv. 1 et 5 mélangées, Crachat d'acide non chiffré | Deux traits séparés ; Crachat 2d10/3d10/4d10, DD 8 + BM + Con, mod. Con fois/repos long | corrigé |
| 🟠 mineur | Kenku / taille, carac., Mimétisme | Taille absente ; valeurs Volo ; DD absent | Moyenne ou Petite ; MotM ; DD 8 + BM + Cha | corrigé |
| 🟠 mineur | Kitsune / Forme hybride (homebrew) | Bonus non chiffré | Avantage Tromperie/Persuasion 1 min, BM fois/repos long | corrigé |
| 🟠 mineur | Kobold / Héritage kobold | Option Défiance absente ; trait nommé « Héritage » | Renommé ; trois options MotM (Ingéniosité, Défiance, Sorcellerie draconique) | corrigé |
| 🟠 mineur | Kobold / caractéristiques | +2, +1 sans alternative | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Kobold / langues | Commun, Draconique (Volo) | Commun + Au choix (MotM) | corrigé |
| 🟠 mineur | Locathah / Armure naturelle | Bouclier non mentionné | 12 + Dex, bouclier autorisé | corrigé |
| 🟠 mineur | Loxodon / Odorat développé | Perception/Investigation seulement | Ajout de Survie | corrigé |
| 🟠 mineur | Léonin / Griffes | 1d4 tranchants sans modificateur | 1d4 + modificateur de Force | corrigé |
| 🟠 mineur | Minotaure / Cornes | 1d6 perforants sans modificateur | 1d6 + modificateur de Force | corrigé |
| 🟠 mineur | Minotaure / Mémoire labyrinthique | Connaissance du nord absente | Ajoutée | corrigé |
| 🟠 mineur | Mort-vivant / Nature de mort-vivant | Immunité au poison (trop forte), repos non défini | Homebrew rééquilibré : résistance au poison + avantage contre empoisonné, repos long de 4 h conscient | corrigé |
| 🟠 mineur | Mort-vivant / Ossature résistante | « Sous certaines conditions » : non chiffré | Homebrew rééquilibré : 1 PV au lieu de 0 sauf dégâts radiants, 1/repos long | corrigé |
| 🟠 mineur | Mort-vivant / langues | Chaîne unique « Commun et une autre langue… » | [Commun, Au choix] | corrigé |
| 🟠 mineur | Myconide éveillé / Réseau mycélien | « Courte portée » non chiffrée | 9 m | corrigé |
| 🟠 mineur | Myconide éveillé / Spores | Ni DD, ni dégâts, ni portée | Homebrew rééquilibré : 3 m, JS Con DD 8 + maîtrise + Con, 1d6 poison progressif, bonus de maîtrise/repos long | corrigé |
| 🟠 mineur | Nain des collines / armure lourde | Vitesse non réduite par l'armure lourde non mentionnée | Trait « Vitesse naine » ajouté | corrigé |
| 🟠 mineur | Nain des collines / traits | Descriptions incomplètes (armes, outils, pierre, résilience) | Listes et règles complètes du MdJ | corrigé |
| 🟠 mineur | Nain des montagnes / armure lourde | Vitesse non réduite par l'armure lourde non mentionnée | Trait « Vitesse naine » ajouté | corrigé |
| 🟠 mineur | Nain des montagnes / traits du nain | Entraînement aux armes naines et Connaissance de la pierre absents | Ajoutés | corrigé |
| 🟠 mineur | Naïade / Bénédiction des eaux | « Imbibition / Façonnage de l'eau » : Imbibition n'existe pas | Façonnage de l'eau ; Nappe de brouillard au niv. 3, 1/repos long ou emplacements | corrigé |
| 🟠 mineur | Naïade / vitesse de nage | Nage 12 m (supérieure à la marche) | Homebrew rééquilibré : nage = marche (9 m) | corrigé |
| 🟠 mineur | Orc / Intuition primitive | Deux compétences (Volo) | Supprimé (absent de MotM) | corrigé |
| 🟠 mineur | Orc / caractéristiques | For +2, Con +1 (Volo/Eberron) | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Orc / langues | Commun, Orc | Commun + Au choix (MotM) | corrigé |
| 🟠 mineur | Orc cendré / Courroux des cendres | Dégâts non chiffrés | Homebrew rééquilibré : réaction sur attaque au corps à corps à 1,50 m, 1d6 + Con feu, repos court ou long | corrigé |
| 🟠 mineur | Owlin / caractéristiques | +2, +1 sans alternative | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Owlin / vol | Vitesse de vol non chiffrée | Vol = marche (9 m), précisé dans le trait | corrigé |
| 🟠 mineur | Plasmoïde / Apnée | Trait absent | Ajouté : 1 heure | corrigé |
| 🟠 mineur | Plasmoïde / Modelage du corps | Pseudopode sans portée ; « Remodele » | Action pour remodeler, action bonus pour un pseudopode de 3 m (≤ 5 kg) | corrigé |
| 🟠 mineur | Plasmoïde / taille et type | Taille et type absents | Moyenne ou Petite, type Vase | corrigé |
| 🟠 mineur | Revenant / Connaissance d'une vie antérieure | « Jet de capacité » imprécis | Test utilisant une compétence, après le d20, bonus de maîtrise fois/repos long | corrigé |
| 🟠 mineur | Revenant / Nature immortelle | Avantage contre les maladies absent ; sommeil magique non mentionné ; trait éclaté en trois | Trait unique VRGR (mort, maladies, empoisonné, poison, repos de 4 h) | corrigé |
| 🟠 mineur | Revenant / caractéristiques | +2, +1 sans alternative | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Revenant / taille | Taille absente | Moyenne ou Petite | corrigé |
| 🟠 mineur | Sang-Maudit / Jeton étrange | Action d'utilisation et cécité non précisées | Précisés | corrigé |
| 🟠 mineur | Sang-Maudit / Magie maudite | Caractéristique et emplacements absents | Int, Sag ou Cha au choix ; aussi via emplacements | corrigé |
| 🟠 mineur | Sang-Maudit / caractéristiques | +2, +1 sans alternative | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Sang-Maudit / source | « Dhampir/Hulder variant » | Guide de Ravenloft | corrigé |
| 🟠 mineur | Satyre / Bélier | 1d6 sans modificateur ; « Bêlier » | Renommé ; 1d6 + modificateur de Force | corrigé |
| 🟠 mineur | Satyre / Fêtard | Instrument de musique absent | Ajouté | corrigé |
| 🟠 mineur | Satyre / type | Type absent | Fée | corrigé |
| 🟠 mineur | Shadar-kai / Ascendance féerique | Trait absent | Ajouté | corrigé |
| 🟠 mineur | Shadar-kai / Transe | « Trance », sommeil magique non mentionné | Renommé et complété | corrigé |
| 🟠 mineur | Shadar-kai / caractéristiques | +2, +1 sans alternative | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Shadar-kai / langues | Commun, Elfique (version Mordenkainen) | Commun + Au choix (MotM) | corrigé |
| 🟠 mineur | Tabaxi / caractéristiques | +2, +1 sans alternative | +2, +1 (ou +1, +1, +1) | corrigé |
| 🟠 mineur | Tabaxi / taille | Taille absente | Moyenne ou Petite | corrigé |
| 🟠 mineur | Thri-kreen / Carapace caméléon | Changement de couleur (action) non précisé | Précisé | corrigé |
| 🟠 mineur | Thri-kreen / taille et type | Taille et type absents | Moyenne ou Petite, type Monstruosité | corrigé |
| 🟠 mineur | Tieffelin / Héritage infernal | Utilisations et niveau de lancement absents | Représailles infernales niv. 3 (sort de niveau 2) 1/repos long, Ténèbres niv. 5 1/repos long, Cha | corrigé |
| 🟠 mineur | Tortle / Armure naturelle | Bouclier non mentionné | Bouclier autorisé, aucune armure | corrigé |
| 🟠 mineur | Tortle / Griffes | 1d6 sans modificateur | 1d6 + modificateur de Force | corrigé |
| 🟠 mineur | Tortle / Intuition naturelle | Trait absent | Ajouté | corrigé |
| 🟠 mineur | Triton / Amphibie | Vitesse de nage non chiffrée | Nage = marche (9 m) | corrigé |
| 🟠 mineur | Triton / sort | « *Brouillard* » | *Nappe de brouillard* | corrigé |
| 🟠 mineur | Triton / Émissaire de la mer | Trait absent | Ajouté | corrigé |
| 🟠 mineur | Vedalken / Précision inlassable | Liste de compétences absente | Liste GGR ajoutée | corrigé |
| 🟠 mineur | Verdan / taille | Taille absente | Petite, puis Moyenne au niveau 5 | corrigé |
| 🟠 mineur | Yuan-ti / Incantation serpentine | « Communication avec les serpents » | Amitié avec les animaux à volonté sur les serpents ; Suggestion niv. 3 ; renommé | corrigé |
| 🔵 info | Aarakocra / version | Données EE | Toutes les données alignées sur MotM | corrigé |
| 🔵 info | Aasimar / version | Mélange Volo/MotM | Sous-races = Volo : source fixée à « Guide de Volo », taille Moyenne | corrigé |
| 🔵 info | Changelin / version | Eberron malgré « MotM / Eberron » | Version MotM (la plus récente) ; source fixée à Monstres du Multivers | corrigé |
| 🔵 info | Myconide éveillé / langues | Langue « Spore » inexistante | [Commun, Au choix] | corrigé |
