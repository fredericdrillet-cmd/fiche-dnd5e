# Rapport d'architecture UI/UX v49 — aide pédagogique, recommandations, inspecteur de sorts

## 1. Panneau pédagogique des classes et sous-classes
### Données (`core/class_guide.py`)
- **`CLASS_GUIDE`** : rédigé pour les 13 classes. Pour chacune : concept, style de jeu, mécaniques clés (Attaque sournoise, Restauration arcanique, Manifestations occultes, Rage, Ki…) et caractéristiques recommandées, avec leur rôle et la raison.
- **Sous-classes** : la liste et les résumés sont **tirés des données** (`Guerrier.json`, `Roublard.json`…), avec leurs sources (Manuel des joueurs, Tasha, Xanathar…). Aucune liste n'est figée dans le code.
  - **Niveau de déblocage** : `SUBCLASS_LEVEL` (Clerc, Ensorceleur et Occultiste au niveau 1 ; Magicien et Druide au 2 ; les autres classes au 3).
  - **Pouvoirs principaux** : chaque aptitude avec son niveau et un résumé.
  - **Orientation de gameplay** : déduite du texte (🔮 Magie, ⚔ Offensive, 🛡 Défense, ✚ Soutien, 🌑 Furtivité, 🐾 Compagnon, 🎓 Polyvalence).
  - **Sorts accordés** : sorts de domaine ou de serment, quand il y en a.

### Interface (`ui/class_guide_panel.py`)
```
┌ Roublard ─────────────────────────────────┐ ┌ Sous-classes — choix au niveau 3 ┐
│ Concept · Style de jeu                    │ │ ▸ Voleur — Manuel des Joueurs     │
│ Mécaniques clés (puces)                   │ │ ▸ Assassin — …                    │
│ ⭐ Dextérité — pourquoi…                   │ │ ▸ Arnaqueur arcanique — …         │
│ Dé de vie · sauvegardes · maîtrises       │ └───────────────────────────────────┘
└───────────────────────────────────────────┘
┌ Fiche dépliée : Arnaqueur arcanique — débloquée au niveau 3 — 🔮 Magie · 🌑 Furtivité │
│ Niv. 3 Sorts & Passe-passe… · Niv. 9 Embuscade magique… · Niv. 13 … · Niv. 17 …      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```
- **Accordéon** : un clic sur une sous-classe déplie sa fiche, un second clic la replie.
- **Assistant de création (étape Classe)** :
  - pour les classes à sous-classe de niveau 1, le clic **choisit** la sous-classe ;
  - pour les autres, il fixe une **sous-classe visée** (sélecteur « ◇ Sous-classe visée »), qui adapte les recommandations de caractéristiques sans rien attribuer avant le niveau requis.
- **Niveau supérieur** :
  - étape Classe : même panneau pour la classe qui monte ;
  - étape Choix du niveau : chaque sous-classe du sélecteur a un résumé au survol, et la fiche de la sous-classe choisie s'affiche dessous.

## 2. Recommandations de caractéristiques
- **Calcul** : `ability_recommendations(classe, sous_classe)` renvoie `{caractéristique: (« principale » | « secondaire », raison)}`. Il part de la classe puis ajoute les apports de la sous-classe (`SUBCLASS_ABILITIES`). Exemples :

  | Personnage | Principale | Secondaire |
  |---|---|---|
  | Roublard | Dextérité | Constitution |
  | Roublard (Arnaqueur arcanique) | Dextérité | Constitution, **Intelligence** (« augmente le DD des jets de sauvegarde de vos sorts d'Arnaqueur arcanique ») |
  | Guerrier (Chevalier occulte) | Force / Dextérité | Constitution, **Intelligence** |
  | Occultiste (Lame maudite) | **Charisme** (attaques comprises) | Constitution |

- **Badges** : sur chaque carte de caractéristique (fiche et assistant), « ⭐ [Principale] » ou « ✦ [Secondaire] ». L'**infobulle** donne la raison. Ils se mettent à jour quand on change de classe ou de sous-classe (visée).

## 3. Identité : portrait et histoire
- **Étape Identité de l'assistant** :
  - bouton **« [ Importer un portrait ] »** : sélecteur de fichiers du système. L'image passe par le même traitement que la fiche (réduite à 640 px maximum, enregistrée dans la sauvegarde) et un aperçu au format 3:4 s'affiche ;
  - bouton « Retirer » ;
  - zone multiligne **« Passé du personnage (backstory) »**.
- **Reprise sur la fiche** : à la création, le portrait et l'histoire passent tels quels dans l'onglet **« Histoire, Portrait »**, où ils restent modifiables à tout moment, en Mode guidé comme en Mode libre.

## 4. Inspecteur de sorts (`ui/spell_inspector.py`)
- **Clic simple** sur un sort (disponible ou déjà choisi) : la fiche détaillée s'affiche dans l'encart « Fiche du sort ». Elle donne l'école, le temps d'incantation, la portée, les composantes, la durée, la concentration, le rituel, le texte complet et les listes de classes.
- **Apprentissage** :
  - **double-clic** ou bouton **« ✚ Apprendre le sort »** (« ✚ Préparer » pour Clerc, Druide, Paladin et Artificier) : même action, dans la limite des quotas ;
  - « ✖ Retirer » dans l'assistant de création.
- **Où** : assistant de création (étape Sorts) et Niveau supérieur (étape Nouveaux sorts, onglets Tours de magie et Sorts de niveau 1+).

## 5. Exécutable
Le `.exe` n'est toujours pas joint : cet environnement est un serveur Linux, sans PyInstaller ni PyQt6. Sous Windows, `compiler_windows.bat` le génère dans `dist\`.

## 6. Fichiers et validation
- **Nouveaux** : `core/class_guide.py`, `ui/class_guide_panel.py`, `ui/spell_inspector.py`, `tests/test_v49_guide_inspector.py` (9 tests).
- **Modifiés** : `core/engine.py`, `ui/abilities_tab.py` (badges), `ui/creation_wizard.py`, `ui/levelup_dialog.py`.
- **Résultat** : **593 tests OK**, 4 ignorés.
- **Limite** : les tests utilisent une interface simulée. La mise en page du panneau de classe, de l'accordéon et de l'aperçu du portrait reste à vérifier à l'écran.
