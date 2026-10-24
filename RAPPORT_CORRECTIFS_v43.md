# Correctifs v43 — bibliothèque de sorts, maîtrises, manifestations dans l'assistant

## 1. Bibliothèque de sorts

**Superposition** : l'encart de la bibliothèque n'avait pas de fond plein, contrairement aux encarts de « Mes sorts » (v34), et le texte d'arrière-plan transparaissait. Corrections :
- l'encart Bibliothèque reçoit `objectName = opaqueBox` et `setAutoFillBackground(True)`, comme les autres encarts ;
- le viewport de la liste remplit son fond ;
- les pages du `QTabWidget` central ont un fond plein (`QTabWidget::pane`) ;
- les cellules de la liste sont transparentes sur un fond opaque, aux couleurs du thème.

**Ajout / retrait réversible** :
- double-clic ou bouton sur un sort **✔ déjà appris** : il est retiré de vos sorts ;
- sur un sort non appris : il est ajouté, avec les mêmes contrôles qu'avant (liste de la classe, niveau, écoles imposées, mode MJ) ;
- le bouton change de libellé selon la sélection : « Ajouter à mes sorts ✚ » ou « Retirer de mes sorts ✖ » ;
- les sorts accordés par la sous-classe (Main de mage de l'Arnaqueur arcanique) ne peuvent pas être retirés.

## 2. Maîtrises d'armes et d'armures

**Moteur** (`core/proficiencies.py`) :
- `proficiency_sources()` liste les sources : classe de départ (toutes ses maîtrises), classes ajoutées en multiclassage (table officielle du PHB : par exemple Guerrier → armures légères et intermédiaires, boucliers, armes courantes et de guerre, mais **pas** les armures lourdes), sous-classes et espèce ;
- maîtrises de sous-classe : Domaines de la Guerre, de la Tempête, de la Vie, de la Nature, de la Forge, de l'Ordre et du Crépuscule ; Collèges de la Vaillance et des Épées ; Lame maudite ; Chantelame ; Armurier ; Forgeur d'armes.

**Onglet Classes** : encart « Maîtrises — armes et armures » sur chaque classe. Il indique ce que la classe apporte (départ ou multiclassage, avec un rappel de la règle), le total du personnage et ce qui est porté sans maîtrise. L'infobulle détaille toutes les sources.

**Armure ou bouclier non maîtrisé** :

| Où | Affichage |
|---|---|
| Inventaire (liste), mannequin (case Armure ou Main secondaire) | ⚠ et infobulle : « Attention : Vous ne maîtrisez pas cette armure ! Vous avez un désavantage aux jets de caractéristique et jets d'attaque basés sur la Force ou la Dextérité. » |
| CA (onglet Combat et en-tête) | « 15 ⚠ » ; l'infobulle ajoute l'avertissement et le blocage des sorts |
| Fiche | Désavantage aux tests et jets de sauvegarde de Force et de Dextérité, et aux jets d'attaque |
| Sorts | `spell_block_reason()` renvoie « Impossible de lancer un sort tout en portant une armure non maîtrisée. ». Toutes les tuiles de sorts du Combat sont grisées avec ce motif ; « Lancer » dans l'onglet Magie affiche une alerte ; un lancement depuis le moteur est refusé |

Contrairement à la forme sauvage, l'onglet Magie reste utilisable (préparer, ajouter ou retirer des sorts) : seule l'incantation est bloquée.

**Arme non maîtrisée** :
- ⚠ dans l'inventaire, sur le mannequin, sur la valeur d'attaque de la ligne d'arme et sur la tuile d'attaque (« ⚠ Attaque — Épée longue ») ;
- infobulle : « Arme non maîtrisée : Le bonus de maîtrise ne s'applique pas au jet de toucher. » ;
- calcul : 1d20 + modificateur de caractéristique (+ bonus magique), sans bonus de maîtrise ; la case de maîtrise manuelle de la ligne d'arme reste prioritaire.

## 3. Manifestations occultes dans l'assistant de niveau

À chaque niveau où l'Occultiste gagne des manifestations (niveau 2 : deux), une carte apparaît à l'étape « Choix du niveau » :
- **Un sélecteur par manifestation à choisir.** Il ne propose que celles dont les prérequis sont remplis : niveau d'occultiste, pacte choisi (y compris s'il est choisi au même niveau), sort mineur requis, Maléfice.
- **Au survol** : infobulle avec le texte complet, le sort accordé et son usage, les prérequis et la source (Manuel des joueurs, Xanathar, Tasha). Un aperçu « 👁 Aperçu » s'affiche aussi pendant la navigation.
- **Après sélection** : résumé « ✔ Choisie : … » sous le sélecteur. Les doublons sont refusés.
- **Confirmer** reste grisé tant que le quota n'est pas atteint.

## 4. Vérifications

- **Tests** : 7 tests v43 ajoutés ; la suite complète passe (524 tests, 4 désactivés).
- **Tests anciens mis à jour** : un Magicien en armure légère ne peut plus lancer Armure de mage (règle des armures non maîtrisées), et l'épée longue d'un Magicien est marquée ⚠.
- **Limite** : les tests tournent sur une interface simulée. Le rendu réel (fonds opaques, ⚠, infobulles des listes déroulantes) reste à vérifier à l'écran.
