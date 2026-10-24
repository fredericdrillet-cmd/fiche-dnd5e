# Rapport v44 — Nouveaux flux UI/UX : échange de sorts et préparation au repos long

## 1. Échange d'un sort connu à la montée de niveau

### Règle appliquée (Manuel des Joueurs)
Quand une classe à sorts connus gagne un niveau, le personnage peut oublier **au plus un** sort connu de cette classe et le remplacer par un autre sort de la liste de la classe. Ce sort doit être d'un niveau pour lequel il a des emplacements.

| Classe | Restriction du remplaçant |
|---|---|
| Barde, Ensorceleur, Occultiste, Rôdeur | Liste de la classe, niveau 1 à niveau maximal |
| Chevalier occulte (Guerrier) | Abjuration ou Évocation, **sauf** si le sort oublié occupait un emplacement libre (niveaux 3, 8, 14, 20) |
| Arnaqueur arcanique (Roublard) | Enchantement ou Illusion, même exception |

Points de règle :
- **Un emplacement libre** est repéré par l'école du sort oublié. Quand on oublie un sort hors des écoles imposées, l'emplacement libre se libère et le remplaçant peut être de n'importe quelle école.
- **Sorts oubliables** : seulement ceux connus **avant** ce niveau. Un sort appris au niveau en cours ne peut pas servir à l'échange, et un sort accordé (Main de mage de l'Arnaqueur) non plus.
- **Classe concernée** : seule la classe qui gagne le niveau peut échanger. En multiclassage, un niveau de Guerrier ne permet pas d'échanger un sort de Barde.
- **Tours de magie** : ils ne s'échangent pas ici, seulement les sorts de niveau 1 ou plus.

### Design de l'encart (étape 5 « Nouveaux sorts »)

```
┌ 🔁 Remplacer un sort connu — Guerrier (facultatif, 1 sort au maximum) ─────────────┐
│ Rappel de la règle (+ écoles imposées du Chevalier occulte / de l'Arnaqueur)      │
│ Étape 1 — Oublier : [ — garder tous mes sorts —            ▼ ]  (infobulles)       │
│ Oublié : Appel de familier — il occupait un emplacement libre : n'importe quelle école │
│ Étape 2 — Remplacer : double-cliquez sur le nouveau sort (n possible(s))           │
│ [ Rechercher…            ] [ Toutes les écoles ▼ ]                                 │
│ ┌ Liste des remplaçants (grisée tant que l'étape 1 n'est pas faite) ─────────────┐ │
│ └────────────────────────────────────────────────────────────────────────────────┘ │
│ ✔ Échange : Appel de familier → Brume       [ ✖ Annuler l'échange ]                │
└────────────────────────────────────────────────────────────────────────────────────┘
```

Comportement :
1. **Étape 1** : un sélecteur liste les sorts connus oubliables, avec le texte du sort en infobulle. Choisir un sort l'enlève de la copie de travail. Sa place reste réservée : la liste des nouveaux sorts n'offre pas de choix supplémentaire.
2. **Étape 2** : la liste des remplaçants se débloque, avec recherche et filtre d'école. Elle ne contient déjà que les sorts permis, écoles imposées comprises.
3. **Après le choix** : le résumé « ✔ Échange : A → B » s'affiche et le sélecteur de l'étape 1 se verrouille. On ne peut faire qu'un échange ; pour en changer, il faut cliquer sur « Annuler l'échange ».
4. **Échange incomplet** : un sort oublié sans remplaçant bloque « Confirmer ». Le motif apparaît dans l'infobulle du bouton et dans le compteur de l'étape 5.
5. **« Annuler » de l'assistant** : rien ne change sur la fiche, puisque tout se fait sur la copie.

## 2. Repos long — sorts pour la journée à venir

### Design de la fenêtre de repos (ajout)

```
🌙 Repos long
… (PV, ressources rechargées, effets qui prennent fin)
📖 Sorts pour la journée à venir :
   Les changements sont appliqués à la fin du repos (« Se reposer ») ; « Annuler » les abandonne.
   [ Changer les sorts préparés ]     Clerc — préparés : 4 / 6 ✎ (modifié)
   [ Changer un tour de magie ]       🔁 Lumière → Amis
                                           [ Annuler ]  [ Se reposer ]
```

- **Bouton « Changer les sorts préparés »** : il apparaît pour le Clerc, le Druide et le Paladin dès qu'ils ont des sorts, ainsi que pour l'Artificier et le Magicien, qui préparent aussi leurs sorts. Un personnage multiclassé a un bouton par classe, suffixé « — Clerc », « — Druide », etc.
- **Bouton « Changer un tour de magie »** : réservé au Magicien qui connaît au moins un tour de magie (règle optionnelle de Tasha).
- **Application différée** : les choix ne sont appliqués qu'à la fin du repos, après la récupération. Annuler le repos annule tout.
- **Ancienne question supprimée** : « Revoir mes sorts ? », posée après le repos, disparaît. La fonction qui la posait reste disponible pour l'onglet Magie.

### Fenêtre « Changer les sorts préparés »
Contenu :
- Titre « 📖 Changer les sorts préparés — Clerc ».
- La limite avec sa formule, par exemple « niveau de Clerc (5) +3 (Sagesse) = 8 sort(s) de niveau 1 ou plus ». Pour le Paladin et l'Artificier, c'est la moitié du niveau.
- « ✦ Toujours préparés » : les sorts de domaine, de serment ou de cercle, affichés pour mémoire et hors quota.
- La jauge « Préparés : n / max ».
- Des filtres : recherche, niveau, école, Rituel (R), Concentration (C), et « Afficher seulement les sorts préparés ».
- La liste cochable : toute la liste de la classe jusqu'au niveau maximal, ou le grimoire pour le Magicien. Chaque sort a son texte en infobulle.

Validation :
- Au-delà du quota, la case refuse de se cocher et un message rouge s'affiche : « Limite atteinte : 8 / 8 sorts préparés. Décochez d'abord un sort. »
- Bouton « ✔ Valider la préparation ». À la fin du repos, le moteur vérifie encore le quota et refuse si la limite est dépassée.

### Fenêtre « Changer un tour de magie » (Magicien)
1. « Tour de magie à oublier » : liste des tours de magie connus du Magicien, hors tours de magie accordés.
2. « Nouveau tour de magie » : recherche, puis tours de magie de la liste du Magicien que le personnage ne connaît pas encore, toutes classes confondues.
3. Un aperçu des deux textes et le résumé « 🔁 A → B » s'affichent. Le bouton « ✔ Échanger » reste grisé tant qu'il manque un des deux choix.

## 3. Code source

| Fichier | Rôle |
|---|---|
| `core/spell_swap.py` (nouveau) | `SpellSwapMixin` : `level_swap_allowed / candidates / forget / options / choose / cancel / pending / rule` ; `rest_prepare_classes / rest_prepare_info / rest_set_prepared` ; `cantrip_swap_known / options / available`, `swap_cantrip` |
| `core/engine.py` | `SpellSwapMixin` ajouté à `Engine` ; `spell_counts` garde la place d'un sort oublié en attente de remplaçant |
| `core/levelup.py` | `level_up_report` ajoute l'échange incomplet aux choix bloquant « Confirmer » |
| `ui/levelup_dialog.py` | encart `_swap_card`, `_fill_swap`, `swap_forget / swap_choose / swap_cancel` ; nettoyage à la confirmation |
| `ui/spell_rest_dialogs.py` (nouveau) | modales `PrepareSpellsDialog` et `CantripSwapDialog` |
| `ui/rest_dialog.py` | section « Sorts pour la journée à venir », boutons, choix appliqués à la fin du repos |
| `tests/test_v44_spell_swap_rest.py` | 13 tests (classes concernées, 1 échange au maximum, écoles et emplacement libre, encart de l'assistant, quota de préparation, grimoire, Formules de sorts mineurs, application différée au repos) |

## 4. Validation
- Suite complète : **537 tests OK**, 4 ignorés (règles retirées en v40).
- Limite : les tests passent par une interface **simulée** (faux module Qt), sans affichage. La logique, les quotas, les écoles et l'application des choix sont vérifiés. Il reste à contrôler visuellement dans l'application réelle la mise en page des deux nouvelles fenêtres, les cases à cocher et les infobulles des listes déroulantes.
