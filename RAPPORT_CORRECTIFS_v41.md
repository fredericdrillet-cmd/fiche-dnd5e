# Correctifs UI/UX v41

## 1. Assistant de niveau : grimoire, filtres et préparation

**Composant** : `ui/levelup_dialog.py`, étape 5 « Nouveaux sorts ». Une carte par classe qui lance des sorts, contenant un `QTabWidget` à deux onglets.

| Onglet | Compteur | Contenu |
|---|---|---|
| **Tours de magie** | « Tours de magie : X / Y (+n à ce niveau) » (aussi dans le titre de l'onglet) | Disponibles (double-clic : apprendre) ; vos tours de magie (double-clic : retirer ceux appris à ce niveau, marqués ✦) |
| **Sorts de niveau 1+** | « Sorts connus », « Grimoire » ou « Sorts préparés : A / B » selon la classe | Disponibles ; vos sorts avec case **Préparé** |

**Filtres en temps réel** (onglet Sorts de niveau 1+) :
- boutons **Tous / Niveau 1 / Niveau 2…**, jusqu'au niveau de sort maximal de la classe ;
- école : Abjuration, Divination, Enchantement, Évocation, Illusion, Invocation, Nécromancie, Transmutation ;
- cases **Rituel (R)** et **Concentration (C)** ;
- recherche par nom.

L'onglet Tours de magie garde la recherche et l'école. Les filtres s'appliquent aux deux listes : disponibles et vos sorts.

**Préparation** :
- jauge « Préparés : n / max » (barre de progression), limite de la classe (niveau de classe + modificateur de la caractéristique d'incantation, selon les règles du moteur) ;
- au-delà de la limite, la case est refusée avec un message ;
- **Magicien** : un sort inscrit au grimoire n'est préparé que s'il reste de la place ;
- **Clerc, Druide, Paladin, Artificier** : ils préparent dans toute leur liste, et la liste « Disponibles » propose la préparation ;
- **Barde, Ensorceleur, Occultiste, Rôdeur** (sorts connus) : la jauge indique « tous vos sorts connus », sans case à cocher.

**Moteur** (`core/levelup.py`) :
- `filter_spells()` : niveau, école, Rituel, Concentration, texte ;
- `level_prepare_info()` : jauge des sorts préparés ;
- `level_set_prepared()` : coche ou décoche « Préparé » dans la limite ;
- `prepares_from_list()` : classes qui préparent dans leur liste ;
- `level_spell_options()` : élargi aux lanceurs qui préparent ;
- `level_learn_spell()` : préparation du Magicien selon la place.

## 2. Combat : tuiles groupées, déplacement en cases, réactions

### Groupes de « Ce tour-ci »

Le moteur classe chaque tuile (`TurnMixin.tile_group`, champ `groupe`) :

| Groupe | Contenu |
|---|---|
| 🗡️ Attaques au corps à corps et à distance | Armes (main principale, distance, mains nues), main secondaire, Attaque sournoise, manœuvres offensives, Châtiment divin, armes naturelles, capacités qui infligent des dégâts |
| ✨ Sorts et magie | Tous les sorts hors réaction (tours de magie, sorts à attaque ou à sauvegarde), métamagie, manifestations occultes |
| ⚡ Réactions | Toute tuile de type Réaction : attaque d'opportunité, Bouclier, Absorption des éléments, Riposte, Parade, Esquive instinctive… |
| 🏃 Actions génériques | Foncer, Esquiver, Se désengager, Aider, Se cacher, Bousculer, Saisir, Utiliser un objet, Chercher, Interagir, **Boire une potion (Action bonus)**, Action astucieuse |
| 🎖️ Capacités de classe et de race | Aptitudes sans jet d'attaque (Rage, Second souffle, Défense patiente…). Elles ne correspondent à aucun des quatre groupes demandés, d'où ce bloc complémentaire, affiché en dernier |

- **Affichage** : chaque groupe a son titre et son compteur, et il est masqué s'il est vide.
- **Filtre par coût** : Tout / Action / Action bonus / Réaction / Gratuit, appliqué à l'intérieur des groupes.

### Déplacement

- **Saisie** : en cases (`QSpinBox`, 1 case = 1,50 m).
- **Affichage** : cases d'abord, mètres à côté. Exemple : « Déplacement : reste 6 cases (9 m) (vitesse 6 cases (9 m)) ».

### Encart « Réactions » supprimé

- **Retiré** : l'encart lui-même, son bouton « Nouveau round » (doublon de celui du pied de tour) et son rafraîchissement.
- **Redirections** :
  - les tuiles du groupe ⚡ consomment la réaction du round (`ch.reaction_utilisee`) ;
  - les capacités de type Réaction (Riposte, Parade, Bouclier runique…) la synchronisent comme avant ;
  - le voyant « Réaction » du pied de tour affiche son état, avec en infobulle le nom de la réaction utilisée ; un clic l'annule (correction manuelle) ;
  - « Nouveau round » la libère.

## 3. Inventaire : Mains nues

- **Arme du Combat** : choisir « Mains nues » comme arme ne l'ajoute plus au sac (`ensure_in_inventory` l'ignore, via `is_natural_attack`).
- **Anciennes sauvegardes** : les entrées « Mains nues » présentes dans l'inventaire sont retirées à l'ouverture.
- **Main principale vide** : la tuile « Attaque à mains nues » reste toujours disponible.

## 4. Vérifications

- **Tests** : 8 tests v41 ont été ajoutés ; la suite complète passe (514 tests, dont 4 anciens tests de réglages de réaction désactivés).
- **Limite** : les tests tournent avec une interface simulée. Le rendu réel (onglets, jauge, groupes de tuiles) reste à vérifier à l'écran.
