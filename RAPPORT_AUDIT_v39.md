# Audit v39 — tuiles d'action du Combat et résolution unifiée

**Référentiel** : Manuel des joueurs, Guide complet de Xanathar, Chaudron des merveilles de Tasha (VF).

**Méthode** : chaque classe et sous-classe a été instanciée au niveau 20, avec ses options (manœuvres, runes, tirs, métamagie) remplies. Les tableaux ci-dessous sont générés à partir du moteur : ce sont les tuiles réellement produites dans « Actions, capacités de classe » de l'onglet Combat.

## 1. Flux de résolution unifiés

### Armes, liées au mannequin (main principale / main secondaire / distance)

| Tuile | Type | Déroulé |
|---|---|---|
| Attaque — arme (main principale) | Action (une par attaque de l'action Attaquer) | d20 + bonus de toucher → « L'attaque touche-t-elle ? » → dégâts de l'arme + modificateur (Force ou Dextérité selon Finesse / distance) |
| Attaque à mains nues | Action | Proposée quand la main principale est vide |
| Attaque en main secondaire | Action bonus | Active si une arme est en main secondaire, après l'action Attaquer. Les deux armes doivent être légères, de corps à corps et à une main (sauf don Combattant à deux armes). d20 distinct ; dégâts **sans** le modificateur, sauf s'il est négatif ou avec le style **Combat à deux armes** ; Duel ne s'applique pas |
| Attaque — arme à distance | Action | Même flux ; munitions et Archerie compris |

**Effets actifs** :
- Inconditionnels (Faveur divine…) : ajoutés aux dés.
- Conditionnels (Marque du chasseur, Maléfice : « cible marquée / maudite ») : proposés par une question après un coup qui touche.
- Coup critique : dés doublés, conditionnels compris.

### Sorts : tous les sorts préparés ou connus et les sorts mineurs sont des tuiles

1. **Niveau d'emplacement** : la fenêtre liste le niveau de base et tous les niveaux supérieurs disponibles, avec les dégâts recalculés pour chacun (par exemple « Niveau 3 — surclassé — dégâts 5d6 feu »). S'il n'y a qu'un niveau possible, comme pour la Magie des pactes de l'Occultiste, il est choisi d'office.
2. **Lancement** : l'emplacement est décompté, ainsi que la concentration et les effets sur la fiche.
3. **Résolution** :
   - **Attaque de sort** : d20 → touche ? → dégâts au niveau dépensé. Décharge occulte fait un jet par rayon.
   - **Jet de sauvegarde** : une fenêtre indique « DD 15 de sauvegarde de Dextérité », les effets en cas d'échec et de réussite (moitié ou aucun dégât), puis lance les dégâts au niveau dépensé.
   - **Dégâts automatiques** (Projectile magique) : jet direct.
   - **Soins** : jet, puis application à vous-même ou à un allié.

Le bouton « Lancer » de l'onglet Magie suit le même flux après le sélecteur d'emplacement.

### Ressources : décompte central

Chaque tuile qui consomme une ressource la décompte à l'usage :
- emplacements de sort et emplacements de Pacte ;
- rage, points de ki, dés de supériorité, points de sorcellerie, dés d'inspiration ;
- Formes sauvages, runes, dés psioniques, Conduit divin ;
- utilisations propres (bonus de maîtrise, modificateur, nombre fixe) récupérées au repos court ou long.

À 0, la tuile est grisée avec le motif (« Rages épuisées — récupération au repos long », « Uniquement en rage », « Déjà utilisée ce tour »…). Le libellé de coût est explicite : « 2 points de sorcellerie », « 1 dé de supériorité ».

### Maître de guerre, Roublard, Barbare, Moine, Rôdeur

- **Manœuvres** : elles se choisissent dans l'encart « Options de sous-classe » (3 / 5 / 7 / 9 aux niveaux 3 / 7 / 10 / 15 ; tant qu'elles manquent, c'est un choix manquant).
  - Chaque manœuvre apprise a sa tuile et décompte 1 dé de supériorité.
  - Manœuvres offensives : attaque avec l'arme équipée, puis dégâts de l'arme + dé (Attaque précise : le dé s'ajoute au d20 ; Balayage : dé à une seconde créature).
  - Parade (dé + Dex) et Ralliement (dé + Cha) : seul le dé est lancé.
  - Le DD est affiché.
  - Les 7 manœuvres de Tasha ont été ajoutées et la description de Manœuvre tactique corrigée.
- **Attaque sournoise** :
  - tuile d'attaque d'arme qui vérifie l'arme (Finesse ou à distance, sinon grisée) ;
  - jet de toucher, puis dégâts de l'arme + Xd6 ;
  - une fois par tour, de nouveau disponible au round suivant.
- **Action astucieuse** : trois tuiles d'action bonus, Foncer, Se désengager, Se cacher.
- **Barbare** : Entrer en rage décompte une rage et active l'état. Les tuiles « en rage » (Frénésie, auras de tempête, Forme de la bête avec armes naturelles) sont grisées hors rage.
- **Moine** : Déluge de coups, Défense patiente, Pas du vent et Coup étourdissant décomptent le ki.
- **Rôdeur** : Marque du chasseur se lance comme un sort (emplacement décompté) et active l'effet. Le +1d6 est ensuite proposé sur chaque coup d'arme.

## 2. Correspondance classe / sous-classe → tuiles

Ces tuiles s'ajoutent aux actions communes (Attaquer, Esquiver, Foncer, Se cacher…), aux armes équipées et aux sorts.

### Artificier

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 7) | Éclair de génie | Réaction | 1 utilisation |
| Alchimiste (niv. 3) | Élixir expérimental | Action | 1 utilisation |
| Armurier (niv. 3) | Champ défensif | Action bonus | 1 utilisation |
| Artilleur (niv. 3) | Canon occulte | Action | 1 utilisation |
| Forgeur d'armes (niv. 3) | Commander le défenseur d'acier | Action bonus | — |
| Forgeur d'armes (niv. 9) | Décharge arcanique | Spécial | 1 utilisation |

*Hors PHB / Xanathar / Tasha, non traitées : Automaturge, Cartomancien, Horloger.*

### Barbare

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 1) | Entrer en rage | Action bonus | 1 rage |
| Classe (niv. 2) | Attaque téméraire | Spécial | — |
| Voie du Berserker (niv. 3) | Attaque de frénésie | Action bonus | — |
| Voie du Berserker (niv. 10) | Présence intimidante | Action | — |
| Voie du Berserker (niv. 14) | Représailles | Réaction | — |
| Voie totémique - Ours | — | — | Totem de l'ours : résistance à tous les dégâts sauf psychiques en rage (passif). |
| Voie totémique - Aigle (niv. 3) | Esprit de l'aigle : Foncer | Action bonus | — |
| Voie totémique - Loup | — | — | Totem du loup : avantage des alliés au corps à corps (passif). |
| Voie du Gardien ancestral (niv. 6) | Bouclier spirituel | Réaction | — |
| Voie des tempêtes - Désert (niv. 3) | Aura de tempête : désert | Action bonus | — |
| Voie des tempêtes - Mer (niv. 3) | Aura de tempête : mer | Action bonus | — |
| Voie des tempêtes - Toundra (niv. 3) | Aura de tempête : toundra | Action bonus | — |
| Voie du Zélote (niv. 10) | Présence zélée | Action bonus | 1 utilisation |
| Voie de la Bête (niv. 3) | Forme de la bête : morsure | Action | — |
| Voie de la Bête (niv. 3) | Forme de la bête : griffes | Action | — |
| Voie de la Bête (niv. 3) | Forme de la bête : queue | Action | — |
| Voie de la Magie sauvage (niv. 3) | Conscience magique | Action | 1 utilisation |
| Voie de la Magie sauvage (niv. 6) | Magie renforçante | Action | 1 utilisation |

*Hors PHB / Xanathar / Tasha, non traitées : Voie du Météore, Voie du Colosse des Glaces.*

### Barde

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 1) | Inspiration bardique | Action bonus | 1 dé d'inspiration |
| Classe (niv. 6) | Contre-charme | Action | — |
| Collège du Savoir (niv. 3) | Mots cinglants | Réaction | 1 dé d'inspiration |
| Collège de la Vaillance (niv. 3) | Inspiration au combat | Spécial | 1 dé d'inspiration |
| Collège de la Séduction (niv. 3) | Manteau d'inspiration | Action bonus | 1 dé d'inspiration |
| Collège de la Séduction (niv. 6) | Manteau de majesté | Action bonus | 1 utilisation |
| Collège des Épées (niv. 3) | Fioriture défensive | Action | 1 dé d'inspiration |
| Collège des Épées (niv. 3) | Fioriture tranchante | Action | 1 dé d'inspiration |
| Collège des Épées (niv. 3) | Fioriture mobile | Action | 1 dé d'inspiration |
| Collège des Murmures (niv. 3) | Lames psychiques | Spécial | 1 dé d'inspiration |
| Collège de l'Éloquence (niv. 3) | Paroles troublantes | Action bonus | 1 dé d'inspiration |
| Collège de la Création (niv. 3) | Représentation de la création | Action | 1 utilisation |
| Collège de la Création (niv. 6) | Représentation animée | Action | 1 utilisation |

*Hors PHB / Xanathar / Tasha, non traitées : Collège des Commandants, Collège de la Discorde.*

### Clerc

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 2) | Conduit divin : Renvoi des morts-vivants | Action | 1 utilisation |
| Classe (niv. 2) | Conduit divin (domaine) | Action | 1 utilisation |
| Classe (niv. 10) | Intervention divine | Action | 1 utilisation |
| Domaine de la Guerre (niv. 1) | Prêtre de guerre | Action bonus | 1 utilisation |
| Domaine de la Lumière (niv. 1) | Éclat protecteur | Réaction | 1 utilisation |
| Domaine de la Nature | — | — | Conduit divin (domaine) : Charme des animaux et des plantes. |
| Domaine de la Ruse (niv. 1) | Bénédiction de l'escroc | Action | — |
| Domaine du Savoir | — | — | Conduit divin (domaine) : Savoir ancestral / Lecture des pensées. |
| Domaine de la Tempête (niv. 1) | Courroux de la tempête | Réaction | 1 utilisation |
| Domaine de la Vie | — | — | Conduit divin (domaine) : Préservation de la vie ; Disciple de la vie (passif). |
| Domaine de la Forge (niv. 1) | Bénédiction de la forge | Spécial | 1 utilisation |
| Domaine de la Tombe (niv. 1) | Yeux de la tombe | Action | 1 utilisation |
| Domaine de la Tombe (niv. 6) | Sentinelle aux portes de la mort | Réaction | 1 utilisation |
| Domaine du Crépuscule | — | — | Conduit divin (domaine) : Sanctuaire crépusculaire. |
| Domaine de l'Ordre | — | — | Conduit divin (domaine) : Exigence de l'ordre ; Voix de l'autorité (passif). |
| Domaine de la Paix (niv. 1) | Lien enhardissant | Action | 1 utilisation |
| Domaine de la Paix (niv. 6) | Lien protecteur | Réaction | — |

*Hors PHB / Xanathar / Tasha, non traitées : Domaine de la Mort, Domaine du Sang (Communauté), Domaine de l'Arcane (Communauté).*

### Druide

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 2) | Forme sauvage | Action | 1 Forme sauvage |
| Cercle de la Lune (niv. 2) | Forme sauvage | Action bonus | 1 Forme sauvage |
| Cercle de la Lune (niv. 2) | Forme sauvage de combat : soins | Action bonus | 1 emplacement de sort |
| Cercle de la Terre | — | — | Sorts de cercle (onglet Magie) ; Récupération naturelle (hors combat). |
| Cercle des Rêves (niv. 2) | Baume de la Cour d'été | Action bonus | 1 utilisation |
| Cercle du Berger (niv. 2) | Esprit totem | Action bonus | 1 utilisation |
| Cercle des Astres (niv. 2) | Forme étoilée | Action bonus | 1 Forme sauvage |
| Cercle des Spores (niv. 2) | Halo de spores | Réaction | — |
| Cercle des Spores (niv. 2) | Entité symbiotique | Action | 1 Forme sauvage |
| Cercle des Fournaises (niv. 2) | Convocation de l'esprit du feu sauvage | Action | 1 Forme sauvage |

*Hors PHB / Xanathar / Tasha, non traitées : Cercle de la Mutation, Cercle de la Sangsue.*

### Ensorceleur

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 3) | Métamagie : Sort prudent | Spécial | 1 point de sorcellerie |
| Classe (niv. 3) | Métamagie : Sort distant | Spécial | 1 point de sorcellerie |
| Classe (niv. 3) | Métamagie : Sort amplifié | Spécial | 1 point de sorcellerie |
| Classe (niv. 3) | Métamagie : Sort étendu | Spécial | 1 point de sorcellerie |
| Lignée draconique (niv. 14) | Ailes de dragon | Action bonus | — |
| Magie sauvage (niv. 1) | Marées du chaos | Spécial | 1 utilisation |
| Magie sauvage (niv. 6) | Chance altérée | Réaction | 2 points de sorcellerie |
| Âme divine (niv. 1) | Faveur des dieux | Spécial | 1 utilisation |
| Magie des ombres (niv. 6) | Chien de mauvais augure | Action bonus | 3 points de sorcellerie |
| Magie des ombres (niv. 14) | Marche dans l'ombre | Action bonus | — |
| Sorcellerie des tempêtes (niv. 1) | Magie tempétueuse | Action bonus | — |
| Sorcellerie des tempêtes (niv. 14) | Fureur de la tempête | Réaction | — |
| Esprit aberrant (niv. 14) | Révélation dans la chair | Action bonus | 1 point de sorcellerie |
| Âme mécanique (niv. 1) | Rétablir l'équilibre | Réaction | 1 utilisation |
| Âme mécanique (niv. 6) | Bastion de la loi | Action | 1 point de sorcellerie |

*Hors PHB / Xanathar / Tasha, non traitées : Lignée du Sang, Magie Cosmique.*

### Guerrier

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 1) | Second souffle | Action bonus | 1 utilisation |
| Classe (niv. 2) | Sursaut d'activité | Spécial | 1 utilisation |
| Classe (niv. 9) | Inflexible | Spécial | 1 utilisation |
| Champion | — | — | Critique amélioré, Athlète remarquable, Survivant : passifs. |
| Maître de guerre (niv. 3) | Attaque menaçante | Action | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Attaque précise | Action | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Attaque repoussante | Action | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Attaque avec feinte | Action bonus | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Croc-en-jambe | Action | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Désarmement | Action | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Distraction | Action | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Fente | Action | 1 dé de supériorité |
| Maître de guerre (niv. 3) | Jeu de jambes | Spécial | 1 dé de supériorité |
| Chevalier occulte (niv. 3) | Lien avec l'arme : rappel | Action bonus | — |
| Chevalier occulte (niv. 7) | Magie de guerre | Action bonus | — |
| Archer arcanique (niv. 3) | Flèche bannissante | Spécial | 1 utilisation |
| Archer arcanique (niv. 3) | Flèche charmeuse | Spécial | 1 utilisation |
| Archer arcanique (niv. 3) | Flèche explosive | Spécial | 1 utilisation |
| Archer arcanique (niv. 3) | Flèche affaiblissante | Spécial | 1 utilisation |
| Archer arcanique (niv. 3) | Flèche de saisie | Spécial | 1 utilisation |
| Archer arcanique (niv. 3) | Flèche perforante | Spécial | 1 utilisation |
| Cavalier (niv. 3) | Marque inébranlable | Action bonus | 1 utilisation |
| Cavalier (niv. 7) | Manœuvre protectrice | Réaction | 1 utilisation |
| Samouraï (niv. 3) | Esprit combatif | Action bonus | 1 utilisation |
| Chevalier runique (niv. 3) | Rune du feu | Spécial | 1 utilisation |
| Chevalier runique (niv. 3) | Rune du nuage | Réaction | 1 utilisation |
| Chevalier runique (niv. 3) | Rune du givre | Action bonus | 1 utilisation |
| Chevalier runique (niv. 3) | Rune de la pierre | Réaction | 1 utilisation |
| Chevalier runique (niv. 3) | Rune de la colline | Action bonus | 1 utilisation |
| Chevalier runique (niv. 3) | Puissance des géants | Action bonus | 1 utilisation |
| Chevalier runique (niv. 7) | Bouclier runique | Réaction | 1 utilisation |
| Soldat psi (niv. 3) | Champ protecteur | Réaction | 1 dé psionique |
| Soldat psi (niv. 3) | Frappe psionique | Spécial | 1 dé psionique |
| Soldat psi (niv. 3) | Mouvement télékinétique | Action | gratuit (1re utilisation) |
| Soldat psi (niv. 3) | Récupération psionique | Action bonus | 1 utilisation |
| Soldat psi (niv. 7) | Bond psi | Action bonus | gratuit (1re utilisation) |
| Soldat psi (niv. 10) | Esprit gardé | Spécial | 1 dé psionique |
| Soldat psi (niv. 15) | Rempart de force | Action bonus | gratuit (1re utilisation) |
| Soldat psi (niv. 18) | Maître télékinétique | Action | gratuit (1re utilisation) |

*Hors PHB / Xanathar / Tasha, non traitées : Chevalier de Sang, Pancratiaste.*

### Magicien

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| École d'Abjuration (niv. 6) | Protection projetée | Réaction | — |
| École de Divination (niv. 2) | Présage | Spécial | 1 utilisation |
| École d'Enchantement (niv. 2) | Regard hypnotique | Action | — |
| École d'Enchantement (niv. 6) | Charme instinctif | Réaction | 1 utilisation |
| École d'Évocation | — | — | Sculpter les sorts, Évocation renforcée (appliquée aux dégâts des sorts) : passifs. |
| École d'Illusion (niv. 10) | Moi illusoire | Réaction | 1 utilisation |
| École de l'Invocation (niv. 2) | Conjuration mineure | Action | — |
| École de l'Invocation (niv. 6) | Transposition bienveillante | Action | 1 utilisation |
| École de la Nécromancie | — | — | Moisson macabre, Serviteurs morts-vivants : passifs. |
| École de la Transmutation | — | — | Pierre du transmutateur (hors combat). |
| Magie de guerre (niv. 2) | Déviation arcanique | Réaction | — |
| Chantelame (niv. 2) | Chant de la lame | Action bonus | 1 utilisation |
| Ordre des scribes (niv. 6) | Esprit manifesté | Action bonus | 1 utilisation |

*Hors PHB / Xanathar / Tasha, non traitées : Magie de la Chronurgie, Magicien du Sang, Liaison élémentaire, Gravure runique.*

### Moine

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 1) | Frappe à mains nues (Arts martiaux) | Action bonus | — |
| Classe (niv. 2) | Déluge de coups | Action bonus | 1 point de ki |
| Classe (niv. 2) | Défense patiente | Action bonus | 1 point de ki |
| Classe (niv. 2) | Pas du vent | Action bonus | 1 point de ki |
| Classe (niv. 5) | Coup étourdissant | Spécial | 1 point de ki |
| Classe (niv. 3) | Parade de projectiles | Réaction | — |
| Classe (niv. 4) | Chute ralentie | Réaction | — |
| Voie de la Paume (niv. 6) | Plénitude du corps | Action | 1 utilisation |
| Voie de l'Ombre (niv. 6) | Pas de l'ombre | Action bonus | — |
| Voie des Quatre Éléments | — | — | Disciplines élémentaires = sorts payés en ki (onglet Magie). |
| Voie de l'Âme solaire (niv. 3) | Trait de soleil radieux | Action | — |
| Voie de l'Âme solaire (niv. 6) | Frappe en arc ardent | Action bonus | 2 points de ki |
| Voie du Kensei (niv. 3) | Tir du kensei | Action bonus | — |
| Voie du Maître ivre (niv. 6) | Balancement éméché | Réaction | 1 point de ki |
| Voie de l'Astre intérieur (niv. 3) | Bras du moi astral | Action bonus | 1 point de ki |
| Voie de la Miséricorde (niv. 3) | Main de guérison | Action | 1 point de ki |
| Voie de la Miséricorde (niv. 3) | Main de souffrance | Spécial | 1 point de ki |

*Hors PHB / Xanathar / Tasha, non traitées : Voie du Sang, Voie de la Tempête.*

### Occultiste

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| L'Archifée (niv. 1) | Présence féerique | Action | 1 utilisation |
| L'Archifée (niv. 6) | Fuite brumeuse | Réaction | 1 utilisation |
| Le Fiélon (niv. 6) | Chance du ténébreux | Spécial | 1 utilisation |
| Le Grand Ancien (niv. 6) | Garde entropique | Réaction | 1 utilisation |
| Le Céleste (niv. 1) | Lumière guérisseuse | Action bonus | 1 utilisation |
| La Lame maudite (niv. 1) | Malédiction de la Lame maudite | Action bonus | 1 utilisation |
| Le Génie (Dao - Terre) (niv. 6) | Don élémentaire | Action bonus | 1 utilisation |
| Le Génie (Djinn - Air) (niv. 6) | Don élémentaire | Action bonus | 1 utilisation |
| Le Génie (Éfrit - Feu) (niv. 6) | Don élémentaire | Action bonus | 1 utilisation |
| Le Génie (Maride - Eau) (niv. 6) | Don élémentaire | Action bonus | 1 utilisation |
| L'Insondable (niv. 1) | Tentacule des profondeurs | Action bonus | 1 utilisation |

*Hors PHB / Xanathar / Tasha, non traitées : Le Moissonneur, Le Protecteur astral.*

### Paladin

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 1) | Sens divin | Action | 1 utilisation |
| Classe (niv. 1) | Imposition des mains | Action | 1+ PV de la réserve |
| Classe (niv. 2) | Châtiment divin | Spécial | 1 emplacement de sort |
| Classe (niv. 3) | Conduit divin (serment) | Action | 1 utilisation |
| Classe (niv. 14) | Toucher purifiant | Action | 1 utilisation |
| Serment de Dévotion (niv. 20) | Nimbe sacré | Action | 1 utilisation |
| Serment des Anciens (niv. 20) | Champion antique | Action | 1 utilisation |
| Serment de Vengeance (niv. 7) | Vengeur implacable | Spécial | — |
| Serment de Vengeance (niv. 20) | Ange vengeur | Action | 1 utilisation |
| Serment de Conquête (niv. 20) | Conquérant invincible | Action | 1 utilisation |
| Serment de Rédemption (niv. 7) | Aura du gardien | Réaction | — |
| Serment de la Gloire (niv. 20) | Légende vivante | Action bonus | 1 utilisation |
| Serment des Guetteurs (niv. 15) | Réprimande vigilante | Réaction | — |

*Hors PHB / Xanathar / Tasha, non traitées : Serment du Sang, Serment des Cendres.*

### Rôdeur

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 1) | Ennemi juré | Spécial | 1 utilisation |
| Chasseur (niv. 3) | Tueur de colosses | Spécial | — |
| Maître des bêtes (niv. 3) | Commander le compagnon | Action bonus | — |
| Traqueur des ténèbres (niv. 3) | Embusqué redoutable | Spécial | — |
| Arpenteur de l'horizon (niv. 3) | Guerrier planaire | Action bonus | — |
| Arpenteur de l'horizon (niv. 7) | Pas éthéré | Action bonus | 1 utilisation |
| Tueur de monstres (niv. 3) | Proie du tueur | Action bonus | — |
| Tueur de monstres (niv. 11) | Némésis des lanceurs | Réaction | 1 utilisation |
| Gardien des nuées (niv. 3) | Essaim rassemblé | Spécial | — |
| Vagabond féérique (niv. 3) | Frappes terribles | Spécial | — |
| Vagabond féérique (niv. 7) | Torsion séduisante | Réaction | — |

*Hors PHB / Xanathar / Tasha, non traitées : Traqueur de sang, Artisan des pièges.*

### Roublard

| Origine | Tuile | Type d'action | Ressource décomptée |
|---|---|---|---|
| Classe (niv. 1) | Attaque sournoise | Action | — |
| Classe (niv. 2) | Action astucieuse : Foncer | Action bonus | — |
| Classe (niv. 2) | Action astucieuse : Se désengager | Action bonus | — |
| Classe (niv. 2) | Action astucieuse : Se cacher | Action bonus | — |
| Classe (niv. 5) | Esquive instinctive | Réaction | — |
| Classe (niv. 20) | Coup de chance | Spécial | 1 utilisation |
| Voleur (niv. 3) | Mains lestes | Action bonus | — |
| Assassin | — | — | Assassinat : avantage et critiques contre les créatures surprises (passif). |
| Arnaqueur arcanique (niv. 3) | Main de mage arcanique | Action bonus | — |
| Bretteur (niv. 9) | Panache | Action | — |
| Conspirateur (niv. 3) | Maître tacticien | Action bonus | — |
| Éclaireur (niv. 3) | Escarmoucheur | Réaction | — |
| Enquêteur (niv. 3) | Combat perspicace | Action bonus | — |
| Lame psychique (niv. 3) | Lames psychiques | Action | — |
| Lame psychique (niv. 3) | Seconde lame psychique | Action bonus | — |
| Lame psychique (niv. 3) | Savoir-faire renforcé | Spécial | 1 dé psionique |
| Lame psychique (niv. 3) | Murmures psychiques | Action | gratuit (1re utilisation) |
| Lame psychique (niv. 3) | Récupération psionique | Action bonus | 1 utilisation |
| Lame psychique (niv. 9) | Frappes autoguidées | Spécial | 1 dé psionique |
| Lame psychique (niv. 9) | Téléportation psychique | Action bonus | 1 dé psionique |
| Lame psychique (niv. 13) | Voile psychique | Action | gratuit (1re utilisation) |
| Lame psychique (niv. 17) | Rupture spirituelle | Spécial | gratuit (1re utilisation) |
| Fantôme (niv. 3) | Plaintes d'outre-tombe | Spécial | 1 utilisation |

*Hors PHB / Xanathar / Tasha, non traitées : Lame d'ombre, Pistoléro.*


## 3. Limites connues

- **Tests** : ils tournent avec une interface simulée (497 tests). Le rendu réel des fenêtres PyQt6 (choix du niveau, fenêtre du DD, question du coup qui touche) reste à vérifier à l'écran.
- **Bonus temporaires** : certaines capacités donnent un bonus pour un tour ou une durée (Fioritures, Guerrier planaire, Esprit combatif). Elles lancent leurs dés ; leur effet sur la CA ou les attaques suivantes est décrit, pas appliqué à la fiche.
- **Noms VF des manœuvres de Tasha** : ce sont des traductions de travail, à aligner sur votre édition si elle diffère.
