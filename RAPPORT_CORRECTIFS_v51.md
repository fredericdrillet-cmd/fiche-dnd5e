# Rapport d'audit UI et correctif multiclassage v51

## 1. Bug critique : « Choix du niveau (1) » lors d'un multiclassage
### Reproduction
Occultiste 1 (Charisme 16, Force 10) → « Niveau supérieur » → Paladin. L'assistant affichait :
```
✔ 1. Classe · ✔ 2. Points de vie · ✔ 3. Aptitudes gagnées · ○ 4. Choix du niveau (1) · … · ○ 6. Récapitulatif
```
« Confirmer » restait grisé alors que la page « Choix du niveau » ne proposait **aucun** choix.

### Cause
En v50, j'avais ajouté le contrôle des prérequis officiels de multiclassage en Mode guidé (Paladin : Force 13 et Charisme 13). L'élément « prérequis non remplis » était ajouté à la liste des choix en attente. Comme il n'était ni un sort, ni un choix affichable, il tombait dans le compteur de l'étape 4 sans aucun widget pour le résoudre : un blocage invisible.

### Correctif
1. **Prérequis traités à la source** (`ui/levelup_dialog.py`) :
   - en Mode guidé, une classe dont les prérequis ne sont pas remplis n'est **plus proposée** dans la liste des classes ;
   - l'étape Classe affiche « 🔒 Multiclassage indisponible (prérequis officiels de caractéristiques) : • Paladin — Paladin demande Force 13 et Charisme 13 » ;
   - en Mode libre, la classe reste proposée avec l'avertissement « ⚠ Prérequis… (Possible avec l'accord du MJ) ». Le prérequis n'est plus jamais un choix bloquant.
2. **Compteur calculé pour la classe montée** (`core/levelup.py`, `_concerns_class`) : seuls les choix de la classe augmentée à ce niveau sont comptés.
   - **Sous-classe, amélioration ou don, sorts** : message préfixé par le nom de la classe.
   - **Style de combat** : style « (Classe) ».
   - **Faveur de pacte** : Occultiste.
   - **Manifestations occultes** : Occultiste, ou don *Initié aux arcanes occultes*.
   - **Échange de sorts** : celui de la classe montée.
   
   Un message d'une autre classe dont seul le texte aurait changé ne peut plus bloquer.

### Résultat
| Cas | Choix du niveau | Validation |
|---|---|---|
| Occultiste 1 → Paladin 1 (prérequis remplis) | **0** (✔) | immédiate |
| Occultiste 1 → Paladin 1 (Force 10, Mode guidé) | — (Paladin listé 🔒 avec la raison) | — |
| Occultiste 1 → Occultiste 2 | Manifestations occultes (2) | après les choix |
| Magicien 1 → Guerrier 1 | Style de combat (1) | après le choix |

## 2. En-tête de la fiche
Les badges « Vitesse » et « Maîtrise » sont **retirés** : ils sont déjà dans les encarts de l'onglet Combat. Restent PV, CA et Initiative (avec son d20). Les champs Personnage, Joueur, XP et le badge de classe ne sont plus tronqués.

## 3. Onglet Combat : encarts de statistiques
- **Grille commune** : les cinq encarts (Initiative, Vitesse, Maîtrise, Perception passive, Vision dans le noir) sont placés dans une seule `QGridLayout` à colonnes d'égale largeur.
- **Hauteur identique** : chacun a une hauteur **fixe** commune (`STAT_BOX_HEIGHT = 104 px`, politique `Fixed`), avec un contenu centré verticalement. L'encart Initiative et sa ligne « Dernier jet » ne dépassent plus les autres.

## 4. Onglet Caractéristiques & Compétences : sans défilement
| Élément | Avant | Après |
|---|---|---|
| Cartes de caractéristiques | marges 10/8/10/10, espacement 4, libellé « Valeur de base » | marges 8/4/8/6, espacement 2, libellé retiré |
| Tables Compétences / Sauvegardes | lignes de 32 px | lignes de 26 px (18 compétences : −108 px) |
| Résumé en Mode guidé | phrase explicative sous les valeurs | phrase déplacée en infobulle |
| Légende « Valeurs passives » | 4 lignes | 1 ligne |
| Espacements de la page | 8 px | 4 px |

**Estimation** : environ 600 px en Mode guidé et 830 px en Mode libre. Cela tient dans la hauteur utile d'un écran 1080p, environ 880 px une fois la barre de titre, les menus, l'en-tête, les onglets et la barre d'état retirés. La zone de défilement est conservée comme filet de sécurité pour les très petites fenêtres : la barre n'apparaît que si le contenu dépasse vraiment.

## 5. Exécutable
Le `.exe` n'est toujours pas joint : l'environnement de développement est un serveur Linux, sans PyInstaller ni PyQt6. Sous Windows, `compiler_windows.bat` le génère dans `dist\`.

## 6. Fichiers et validation
- **Code modifié** :
  - moteur : `core/levelup.py` ;
  - interface : `ui/levelup_dialog.py`, `ui/main_window.py`, `ui/combat_tab.py`, `ui/stats_tab.py`, `ui/skills_tab.py`, `ui/abilities_tab.py`.
- **Tests** :
  - nouveaux : `tests/test_v51_layout_multiclass.py` (7 tests), dont la reproduction exacte du bug ;
  - adaptés au nouveau comportement des prérequis : `test_v29` et `test_v50`.
- **Résultat** : **608 tests OK**, 4 ignorés.
- **Limite** : ces tests utilisent une interface simulée. La hauteur réelle de l'onglet Caractéristiques & Compétences est une estimation, à confirmer sur ton écran.
