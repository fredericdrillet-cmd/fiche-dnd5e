# Rapport des ajustements UI/UX v46

## 1. Décomposition des modificateurs de dégâts

### Avant / après
Avant, la fiche n'affichait qu'un bonus consolidé (« Bonus fixe : +2 ») ; elle montre désormais l'origine de chaque point.

### Moteur
- **`weapon_stats()`** (`core/engine.py`) construit, en même temps que la formule, la liste ordonnée des modificateurs de dégâts `bonus_degats = [(source, valeur)]` :

  | Source | Libellé |
  |---|---|
  | Caractéristique | `Mod. FOR` / `Mod. DEX` (affichée même à +0 ; retirée en main secondaire, sauf si elle est négative ou avec le style Combat à deux armes) |
  | Arme magique liée à l'inventaire | `Objet magique : Épée longue +3` |
  | Bonus magique saisi à la main | `Arme magique` |
  | Style Duel | `Style de combat : Duel` (à une main seulement) |
  | Rage | `Rage` |
  | Munition magique | `Munition : Flèche +1` |

- **Formateur `damage_calc(dé, termes, résultat)`** : produit la chaîne lisible `1d8 - 1 (Mod. FOR) + 3 (Objet magique : Épée longue +3) = 1d8 + 2`, exposée en `calcul`, avec `calcul_1m` et `calcul_2m` pour les deux prises d'une arme polyvalente.
- **`weapon_damage_spec()`** (`core/combat_flow.py`) :
  - ajoute au calcul les dés supplémentaires (Faveur divine, dé de supériorité, Attaque sournoise…) ;
  - transmet `flat_labels` et `calcul` au jet de dégâts (`DamageSpec`, nouveau champ `calcul`).

### Interface
- **Ligne d'arme (onglet Combat)** : l'infobulle des dégâts affiche « Calcul : … (à deux mains) » et le calcul de l'autre prise.
- **Tuile d'attaque (« Ce tour-ci »)** : la description contient « Calcul des dégâts : … ». La tuile de main secondaire indique aussi son calcul.
- **Fenêtre de dés** : la ligne « Bonus fixe » devient `Bonus fixe : -1 (Mod. FOR) + 3 (Objet magique : Épée longue +3) = +2`, suivie de `Calcul : …`. Elle est mise en évidence une fois les dés posés.
- **Bouton « dégâts » de la ligne d'arme** : il utilise désormais le même jet que les tuiles, donc la même formule, le même détail et les mêmes dés ajoutés.

## 2. Inventaire : colonne Quantité
Les quantités des objets mondains sont des compteurs (`QSpinBox`), qui étaient alignés à gauche. Ils sont maintenant centrés avec `setAlignment(Qt.AlignmentFlag.AlignCenter)`, comme les cellules des objets magiques : toute la colonne est homogène.

## 3. Armes polyvalentes : prise automatique

### Détection de la main secondaire
- **`off_hand_free(arme)`** (`core/combat_flow.py`) renvoie `False` si :
  - un bouclier est porté (`armure["bouclier"]`) ;
  - ou une arme valide occupe la main secondaire (`armes_cac[1]`).

  L'arme de la main secondaire elle-même est toujours tenue à une main.
- **`weapon_stats()`** applique :
  - `prise à deux mains = arme polyvalente ET pas d'attaque en main secondaire ET off_hand_free(arme)` ;
  - main libre → dé polyvalent (1d10 pour l'Épée longue) ;
  - main occupée → dé standard (1d8) ;
  - le champ `prise` vaut « à deux mains » ou « à une main ».
- **Fin de l'ancien réglage manuel** : le marqueur `deux_mains` de l'emplacement n'est plus lu, et `two_handed_main()` ne considère comme « à deux mains » que les armes ayant réellement la propriété *Deux mains*. Équiper un bouclier ou une dague en main secondaire bascule donc simplement l'arme polyvalente à une main, au lieu de libérer la main secondaire.

### Mise à jour en temps réel
- **Recalcul** : rien n'est stocké. La prise est recalculée à chaque appel à partir de l'état réel de la main secondaire, et chaque changement d'équipement (onglet Combat, mannequin, inventaire, objet magique) rafraîchit la fiche. Dégâts, libellés et tuiles suivent donc immédiatement.
- **Libellés** :
  - tuile : « Attaque — Épée longue (à deux mains) (main principale) » ou « … (à une main) … » ;
  - fenêtre de dégâts : « Dégâts — Épée longue (à deux mains) ».
- **Indicateur** : l'ancien commutateur « 1 main / 2 mains » devient un indicateur grisé (« 🙌 À deux mains » / « ✋ À une main »). Son infobulle donne les deux calculs et explique la raison de la prise.

## 4. Fichiers
- **Moteur** : `core/engine.py` (`damage_calc`, `pretty_formula`, détail et prise dans `weapon_stats`), `core/combat_flow.py` (`off_hand_free`, jet de dégâts détaillé), `core/dice.py` (`DamageSpec.calcul`, `flat_breakdown`), `core/turn.py` (libellés et calcul des tuiles), `core/equipment.py` (`two_handed_main`).
- **Interface** : `ui/dice_dialog.py` (`flat_text`), `ui/combat_tab.py` (indicateur de prise, infobulle, jet de dégâts), `ui/inventory_tab.py` (centrage).
- **Tests** : `tests/test_v46_damage_versatile.py` (9 tests). J'ai aussi mis à jour les anciens tests qui supposaient l'Épée longue à une main ou le commutateur manuel : `test_rules`, `test_data_theme`, `test_v24`, `test_v30`, `test_v34`.

## 5. Validation
- **Tests** : la suite complète passe, **563 tests OK** et 4 ignorés.
- **Limite** : ces tests utilisent une interface simulée (sans PyQt6 réel). Le rendu visuel reste à vérifier dans l'application : centrage des compteurs, retour à la ligne du calcul dans la fenêtre de dés.
