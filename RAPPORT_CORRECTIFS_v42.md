# Correctifs UI v42 — fenêtre « Niveau supérieur » et styles de combat

## 1. Dimensionnement de la fenêtre

| Avant | Après |
|---|---|
| Taille minimale fixe de 960 × 640, souvent trop petite | `_fit_to_screen()` : environ 75 % de la largeur et 85 % de la hauteur de l'écran disponible, au moins 1200 × 820 si l'écran le permet, jamais plus grande que l'écran (marge de 40 px) ; minimum 900 × 600 pour les petits écrans |
| Fenêtre non redimensionnable (sans bordure) | `QSizeGrip` en bas à droite de la carte : on agrandit à volonté |
| Pages Classe et Points de vie sans défilement | Les pages 1, 2, 4 et 5 sont dans des `QScrollArea` (redimensionnement automatique du contenu, sans cadre) ; les pages 3 et 6 sont des `QTextBrowser` qui défilent déjà |
| Colonne des étapes à 230 px | 250 px : « ✔ 5. Nouveaux sorts (2) » tient sur une ligne |

## 2. Styles de combat dans l'assistant

Chaque emplacement de style (ou modèle d'armure de l'Armurier) est maintenant une carte dédiée (`_style_card`) :

1. **Au survol, dans la liste** : chaque entrée a une infobulle (`Qt.ItemDataRole.ToolTipRole`) avec le texte mécanique complet du style et une ligne « Sur la fiche : … ». Par exemple, pour Défense : « +1 à la CA calculée quand une armure est portée ».
2. **Aperçu en direct** : pendant la navigation au clavier ou à la souris, le signal `highlighted` affiche « 👁 Aperçu : *style* — texte » sous le sélecteur.
3. **Après la sélection** : « ✔ Style choisi : *style* — texte complet » et sa répercussion sur la fiche. Le choix met à jour la copie de travail et le récapitulatif.

**Textes officiels complets** (`core/fighting_styles.py`) pour les 13 styles du Manuel des joueurs et de Tasha :
- Archerie, Armes à deux mains, Combat à deux armes, Défense, Duel, Protection ;
- Arme de lancer, Combat à mains nues, Combat en aveugle, Interception, Technique supérieure, Combattant béni, Combattant druidique.

`Database.style_description()` les utilise d'abord, puis le texte du fichier de données à défaut. L'onglet Combat (infobulles et description du style) et les passifs de classe profitent donc aussi des textes complets.

## 3. Vérifications

- **Tests** : 3 tests v42 ajoutés ; la suite complète passe (517 tests, dont 4 désactivés depuis la v40).
- **Limite** : les tests tournent sur une interface simulée. Le rendu réel (taille selon votre écran, infobulles de la liste déroulante, aperçu au survol) reste à vérifier à l'écran.
