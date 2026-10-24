# Correctifs v40 — assistant de niveau, sorts à sauvegarde, réactions, potions

## 1. Assistant « Niveau supérieur »

| Point | Avant | Après |
|---|---|---|
| Nouveaux sorts | Listés « à faire ensuite » dans l'onglet Magie | Étape 5 **« Nouveaux sorts »** : quota exact du niveau (par exemple « Sorts mineurs : 4 / 5 (+1 à ce niveau) — Sorts connus : 4 / 5 (+1) — niveau de sort maximal : 2 ») |
| Liste de sorts | — | Sorts apprenables seulement : liste de classe, niveau maximal, écoles imposées du Chevalier occulte et de l'Arnaqueur arcanique, quota restant ; recherche et description au survol |
| Préparation (Clerc, Druide, Paladin, Artificier) | — | Non demandée dans l'assistant : la préparation est quotidienne et reste dans l'onglet Magie |
| Confirmer | Grisé si l'étape 4 est incomplète | Grisé si l'étape 4 ou 5 est incomplète (motif en infobulle) |
| Liste des dons | Noms seuls | Infobulle au survol de chaque don : effet, prérequis (⚠ si non rempli), bonus de caractéristique, source |
| Don choisi | — | Résumé sous le sélecteur |
| « +1 à deux caractéristiques » | Sélecteurs superposés dans une grille ; la même caractéristique pouvait être prise deux fois | Une carte par emplacement (« +1 à [ ] et +1 à [ ] ») ; la seconde liste exclut la première ; le moteur refuse les doublons ; aperçu « Force 15 → 16 » et alerte au-delà de 20 |
| Coupures | Contenu tronqué | Pages 4 et 5 dans une zone défilante ; fenêtre élargie à 960 × 640 |

**Moteur** (`core/levelup.py`) :
- `level_spell_plan()` : quotas et gains du niveau.
- `level_spell_options()` : sorts apprenables.
- `level_learn_spell()` : apprentissage sur la copie de travail.
- `level_up_report()` : classe les choix de sorts dans l'assistant.

## 2. Sorts à jet de sauvegarde

- **Règle par sort** dans `data/Regles_sorts.json` (champ `js_succes`, généré par `tools/spell_rules.py`) :
  - sort de niveau 1+ : **moitié des dégâts** en cas de réussite ;
  - sort mineur : **aucun dégât** ;
  - exceptions vérifiées sur le texte officiel :
    - **Succès = 0 dégât** : Catapulte, Mixture caustique de Tasha, Secousse sismique, Frappe piégeuse, Cordon de flèches, Poigne terreuse de Maximilien, Foulée d'Ashardalon, Sphère de tempête, Tentacules noirs d'Evard, Assassin imaginaire, Rayonnement écoeurant, Maelström, Contact avec un autre plan, Désintégration, Ennemi subconscient, Quête ;
    - **Dégâts même en cas de succès** (le jet n'évite que l'effet) : les cinq Châtiments, Métal brûlant, Fléau élémentaire, Prison mentale, Esprit faible, Voracité de Hadar (froid) ;
    - **Cas particulier** : Énervation, 2d8 nécrotiques en cas de réussite puis fin du sort.
- **Affichage** sous les dégâts :
  - détail du sort dans l'onglet Magie : « Jet de sauvegarde de Dextérité : DD 15 », puis « Succès = 1/2 dégâts » ;
  - tuile du Combat : même ligne ;
  - fenêtre de résolution.
- **Après le jet de dégâts** : « Boule de feu : échec = 31 dégâts, réussite = 15 (moitié) ». La moitié est arrondie à l'inférieur.

## 3. Réactions

- **Réglages retirés** : les menus « Demander / Automatique / Désactivée » de l'encart Réactions et le bouton de réaction automatique du pied de tour.
- **Fonctionnement** : chaque réaction (Bouclier, Absorption des éléments, Protection projetée, attaque d'opportunité, aptitudes…) est une simple tuile cliquable, utilisable une fois par round ; elle consomme la réaction du personnage.
- **Anciennes sauvegardes** : les réglages enregistrés sont ignorés.

## 4. Règle optionnelle : potion en action bonus

- **Nouvelle tuile** « Boire une potion (Action bonus) ». Elle est active si l'inventaire contient une potion, un élixir, un philtre ou une antitoxine ; les huiles s'appliquent, elles ne se boivent pas.
- **Au clic** : choix de la potion, puis effet officiel appliqué (soins lancés, état actif…) et potion retirée de l'inventaire. Si l'on annule, l'action bonus est rendue.
- **Administrer une potion à un allié**, même inconscient, reste l'action « Utiliser un objet » ; sa description le précise.

## 5. Vérifications

- **Tests** : 9 tests v40 ont été ajoutés ; la suite complète passe (506 tests, dont 4 anciens tests de réglages de réaction désactivés car la fonction est retirée).
- **Limite** : les tests tournent avec une interface simulée. La mise en page réelle de l'assistant (cartes, défilement, infobulles des listes) reste à vérifier à l'écran.
