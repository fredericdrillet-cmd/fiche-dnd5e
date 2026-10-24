# Audit v37 — manifestations occultes et sorts

**Référentiel** : Manuel des joueurs (PHB), Guide complet de Xanathar (XGtE), Chaudron des merveilles de Tasha (TCoE), en terminologie VF.

**Données corrigées** :
- `data/Manifestations_occultes.json`, généré par `tools/invocation_fixes.py`.
- `data/Regles_sorts.json`, généré par `tools/spell_rules.py`. C'est une surcouche lue au chargement ; les fichiers `Magie-N.json` ne sont pas modifiés.

Les deux outils sont idempotents et relancés par `tools/apply_corrections.py` (étapes 6 et 7).

## 1. Anomalies détectées et corrigées

### 1.1 Manifestations occultes (54 auditées)

**Bugs de calcul et d'effet**

| Manifestation | Anomalie | Correction |
|---|---|---|
| Décharge déchirante | +1 fixe aux dégâts | + modificateur de Charisme à **chaque rayon** (1d10 + Mod. CHA) |
| Voleur des cinq destinées | Accordait « Imprécation » | Fléau (*Bane*), 1 fois par repos long avec un emplacement d'occultiste |
| Attaque occulte | Niveau 0, « +5d8 » | Niveau 5 (Pacte de la lame) ; 1d8 + 1d8 par niveau de l'emplacement de Pacte, force, cible à terre (Très grande ou moins), 1 fois par tour |
| Buveuse de vie | « Bonus de dégâts nécrotiques » sans valeur | + Mod. CHA nécrotiques (minimum 1) à chaque coup d'arme de pacte |
| Tombe de Levistus | 200 PV temporaires | 10 PV temporaires par niveau d'occultiste, 1 fois par repos court ou long |
| Maléfice accablant | 1 dégât | Mod. CHA psychiques (min. 1) à la cible maudite et aux créatures choisies à 1,50 m ; requiert Maléfice ou une malédiction |
| Voile de mouches | Effet incomplet, repos long | Aura de 1,50 m : Mod. CHA poison (min. 0), avantage en Intimidation ; repos court ou long |

**Limites d'usage erronées**

| Manifestation | Anomalie | Correction |
|---|---|---|
| Chaîne des carcères | 1 fois par repos long | À volonté (céleste, fiélon, élémentaire) ; pas deux fois la même créature avant un repos long |
| Fuite de l'escamoteur | À volonté | 1 fois par repos long, sur soi, sans emplacement |
| Regard fantomatique | Repos long | Repos court ou long, concentration 1 minute, vision dans le noir incluse |
| Servitude de la tombe | Formulation | Animation des morts sans emplacement, 1 fois par repos long |

**Valeurs fixes à remplacer par le bonus de maîtrise**

| Manifestation | Anomalie | Correction |
|---|---|---|
| Scribe des horizons, Présent des sauveurs | « 6 noms » | Noms = bonus de maîtrise |
| Réprimande du talisman | 6 dégâts | Dégâts psychiques = bonus de maîtrise, poussée 3 m |
| Protection et Lien du talisman | 6 utilisations | Bonus de maîtrise utilisations par repos long |

**Effets ou textes incomplets**

| Manifestation | Anomalie | Correction |
|---|---|---|
| Don des profondeurs | Sort manquant | + Respiration aquatique 1 fois par repos long |
| Lame assoiffée | Sans effet sur la fiche | 2 attaques par action Attaquer |
| Armure d'ombres | Catégorie « Communes / Pactes » | Commune ; sur soi, sans emplacement ni composante matérielle |
| Engagement du maître, Perception transférée, Aspect de la lune, Arme de pacte améliorée | Textes résumés | Textes officiels complets |

**Prérequis et nom**

| Manifestation | Anomalie | Correction |
|---|---|---|
| Décharge déchirante, Décharge répulsive, Étreinte de Hadar, Lance de léthargie, Lance occulte | Aucun prérequis | Exigent de connaître Décharge occulte |
| Maléfice accablant, Maléfice implacable | Aucun prérequis | Exigent Maléfice ou une aptitude de malédiction (Lame maudite) |
| Etreinte de Hadar | Accent manquant | Étreinte de Hadar ; les anciennes sauvegardes sont migrées automatiquement |

### 1.2 Sorts (488 dans la base, 482 du corpus PHB / XGtE / TCoE)

**Étiquettes et durées**
- **Rituels** : Rappel à la vie et Réincarnation étaient étiquetés rituels à tort. Les 224 étiquettes de concentration ont été vérifiées une à une : aucune erreur.
- **Durées** : la base n'en contenait aucune, hormis le mot « Concentration ». Les 482 sorts du corpus ont désormais leur durée officielle (« Concentration, jusqu'à 1 minute », « 8 heures », « Jusqu'à dissipation »…).

**Dés et jets**
- **Dés manquants ou faux** :
  - Éclair : aucun dé détecté, maintenant 8d6.
  - Projectile magique : 1d4 au lieu de 3 × (1d4 + 1).
  - Désintégration : le + 40 était perdu.
  - Doigt de mort : le + 30 était perdu.
- **Jets** :
  - Blessure : attaque au corps à corps.
  - Rayon empoisonné, Trait ensorcelé, Éclair traçant, Orbe chromatique, Flèche acide de Melf, Couteau de glace : attaque de sort.
  - Fouet épineux : attaque au corps à corps.
  - Tentacules de Hadar : JS de Force.

**Surclassement et échelle**
- **Surclassement** : rien n'existait. Il y a maintenant 106 règles : dés par niveau, paliers (Arme spirituelle et Lame de feu tous les 2 niveaux ; Lame d'ombres 3d8 / 4d8 / 5d8 ; Arme élémentaire), projectiles (Projectile magique, Rayon ardent, Minuscules météores, Couronne d'étoiles), cibles supplémentaires et durées (Maléfice, Marque du chasseur, Quête). Les sorts sans surclassement officiel n'en reçoivent pas (Châtiment tonitruant, Châtiment aveuglant, Aura de vitalité…).
- **Sorts mineurs** : Pierre magique et Gourdin magique ne gagnent plus de dés aux niveaux 5 / 11 / 17 ; ils ajoutent le modificateur d'incantation. Lame retentissante, Lame aux flammes vertes (version Tasha) et Glas (1d8 ou 1d12) suivent leur propre échelle.

**Modificateur aux dégâts** : il n'est ajouté que si une règle le prévoit.
- Le sort lui-même : sorts de soins, Arme spirituelle, Pierre magique, Gourdin magique.
- Une manifestation : Décharge déchirante.
- Une aptitude de classe : Incantation puissante (Clerc, sorts mineurs de clerc), Évocation renforcée (Magicien d'évocation), Affinité élémentaire (Ensorceleur draconique, type de son ancêtre).

**Hors corpus, non audités** : Vents contraires, Projectile élémentaire, Entraves de givre, Sens de la distorsion, Scellé de portail, Invocation d'ombres. Ils ne figurent pas dans le PHB, Xanathar ni Tasha et sont signalés dans leur fiche.

**Moteur** : le lanceur de dés lisait « 3 × 1d10+3 » comme 1d10+6. Il comprend maintenant les multiplicateurs de rayons et de projectiles.

## 2. Effet de chaque manifestation sur la fiche

### 2.1 Décharge occulte, onglet Combat

Ces effets apparaissent sur la tuile du tour, dans l'encart des sorts mineurs et dans le jet de dégâts.

| Manifestation | Effet |
|---|---|
| Décharge déchirante | 1d10 + Mod. CHA par rayon (par ex. « 3 × 1d10+4 » au niveau 11 avec CHA 18) |
| Décharge répulsive | Poussée de 3 m à chaque rayon qui touche |
| Étreinte de Hadar | Attire de 3 m vers vous, 1 fois par tour |
| Lance de léthargie | Vitesse −3 m jusqu'à la fin de votre prochain tour, 1 fois par tour |
| Lance occulte | Portée 90 m |

### 2.2 Sorts accordés, onglet Magie, « Sorts accordés »

Ces sorts figurent aussi sur les tuiles du tour.

**À volonté, sans emplacement**

| Manifestation | Sort |
|---|---|
| Armure d'ombres | Armure de mage, sur soi ; active l'effet « Armure du mage », CA 13 + Dex |
| Langage animal | Communication avec les animaux |
| Mille visages | Déguisement |
| Vigueur fiélonne | Simulacre de vie, sur soi, au niveau 1 ; PV temporaires injectés |
| Vision occulte | Détection de la magie |
| Visions embrumées | Image silencieuse |
| Scribe des horizons | Communication à distance, vers les noms inscrits |
| Chaîne des carcères | Immobilisation de monstre |
| Murmures de la tombe | Communication avec les morts |
| Pas aérien | Lévitation, sur soi |
| Saut d'outre-tombe | Saut, sur soi |
| Maître des formes | Modification d'apparence |
| Royaumes lointains | Œil magique |
| Voile d'ombres | Invisibilité |

**1 fois par repos long, avec un emplacement d'occultiste** (compteur interne)

| Manifestation | Sort |
|---|---|
| Voleur des cinq destinées | Fléau |
| Avachissement | Lenteur |
| Sombre présage | Malédiction |
| Mot d'effroi | Confusion |
| Murmures impérieux | Compulsion |
| Sculpteur de chair | Métamorphose ; ouvre le choix de la bête |
| Sbire du chaos | Invocation d'élémentaire |

**1 fois par repos long, sans emplacement**

| Manifestation | Sort |
|---|---|
| Don des profondeurs | Respiration aquatique |
| Servitude de la tombe | Animation des morts |
| Fuite de l'escamoteur | Liberté de mouvement, sur soi |

### 2.3 Actions et réactions, onglet Combat

| Manifestation | Type | Coût / valeur |
|---|---|---|
| Attaque occulte | Spécial | Emplacement de Pacte ; (1 + niveau)d8 force |
| Tombe de Levistus | Réaction | 10 × niveau d'occultiste en PV temporaires, appliqués ; repos court |
| Voile de mouches | Action bonus | Mod. CHA poison ; repos court |
| Maléfice accablant | Action bonus | Mod. CHA psychiques (min. 1) |
| Maléfice implacable | Action bonus | Téléportation 9 m |
| Regard fantomatique | Action | Repos court, concentration |
| Maître des ombres | Action | Active l'état Invisible |
| Perception transférée | Action | — |
| Réprimande du talisman | Réaction | Bonus de maîtrise en dégâts psychiques |
| Protection du talisman | Spécial | 1d4 ; bonus de maîtrise par repos long |
| Lien du talisman | Action | Bonus de maîtrise par repos long |
| Présent des sauveurs | Spécial | 1 par repos long |
| Engagement du maître | Action bonus et réaction | Ordre d'attaque ; résistance du familier |

### 2.4 Passifs, sens et compétences

| Manifestation | Effet sur la fiche |
|---|---|
| Vision du diable | Encart Vision : 36 m, ✦ ténèbres magiques |
| Présence captivante | Maîtrise de Tromperie et de Persuasion (onglet Compétences) |
| Esprit occulte | Avantage indiqué sur le JS de Constitution (concentration) |
| Lame assoiffée | 2 attaques par action Attaquer (compteur du tour) |
| Buveuse de vie | Passif chiffré : + Mod. CHA nécrotiques |
| Arme de pacte améliorée | Passif : +1 attaque et dégâts, arcs et arbalètes |
| Don des profondeurs | Vitesse de nage dans l'infobulle de la vitesse, respiration aquatique |
| Œil du gardien des runes, Aspect de la lune, Vision sorcière, Voix du maître des chaînes, Don des immortels | Passifs listés dans les capacités |

### 2.5 Livre des secrets anciens, onglet Magie, Manifestations

Un encart permet d'inscrire 2 rituels de niveau 1 de n'importe quelle liste de classe. Tant qu'ils manquent, c'est un choix manquant : badge d'onglet et liste de contrôle.

Ensuite, vous pouvez inscrire d'autres rituels jusqu'au niveau égal à la moitié du niveau d'occultiste (arrondie au supérieur). Ils apparaissent dans « Sorts accordés » avec l'usage « Rituel uniquement (+10 minutes) ». Ils restent hors des tuiles de combat.

## 3. Vérifications

- 25 nouveaux tests (`tests/test_v37_invocations_spells.py`) ; la suite complète passe (468 tests).
- Les tests tournent avec une interface simulée : le rendu réel des encarts PyQt6 reste à contrôler à l'écran.
