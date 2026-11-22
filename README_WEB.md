# Fiche D&D 5e — version web mobile

La version web réutilise **tel quel** le moteur de l'application bureau (`core/` et `data/`).
Seule l'interface PyQt6 (`ui/`) est remplacée par une interface web pensée pour le smartphone.
L'application bureau fonctionne toujours (`python main.py`).

## Pourquoi Flask + HTML/JS (et pas Streamlit ou Gradio)

| Critère | Streamlit / Gradio | **Flask + interface HTML/JS (choisi)** |
|---|---|---|
| Logique métier conservée | oui | oui : `core/` est appelé sans aucune modification |
| Rendu mobile | gabarits figés, chaque clic recharge toute la page | interface sur mesure : barre d'onglets en bas, gros boutons, feuilles coulissantes |
| Interactions de la fiche (sphères, dés, cases) | lourdes à reproduire | natives (un toucher = une action) |
| Hébergement gratuit | Streamlit Cloud, HF Spaces | Render, HF Spaces, Railway, Fly.io… |
| Installable sur l'écran d'accueil | non | oui (PWA) |

Le serveur est **sans état** : le personnage est gardé dans le navigateur (au format JSON de l'application
bureau) et envoyé au serveur à chaque action. Le serveur reconstruit `Engine(db, Character)`, applique
l'action (le même code que les gestionnaires de `ui/*.py`), puis renvoie la fiche calculée. Aucune base de données,
aucun compte : l'offre gratuite d'un hébergeur suffit.

## Structure

```
app.py                 fichier principal web (gunicorn app:app)
web/service.py         façade du moteur : opérations + fiche calculée + export texte
web/levelup.py         assistant de montée de niveau (core/levelup.py rejoué à chaque requête)
web/app.py             routes Flask (/api/character, /api/levelup, /api/catalog…)
web/static/            interface mobile : index.html, style.css, app.js, manifest, service worker, icônes
core/  data/           moteur de règles et base JSON — inchangés
ui/                    interface bureau PyQt6 (ui/theme.py fournit aussi les 10 thèmes du web)
main.py                application bureau
requirements.txt       dépendances web (Flask, gunicorn)
requirements-desktop.txt  dépendances bureau (PyQt6)
render.yaml  Procfile  Dockerfile   déploiement
tests/test_web.py      tests de la version web (les 570 tests existants passent toujours, + 15 tests web)
```

## Lancer en local

```bash
python -m venv .venv
source .venv/bin/activate            # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python app.py                        # http://localhost:8000
```

Pour tester sur votre téléphone à la maison : même Wi-Fi, puis ouvrez `http://<IP-du-PC>:8000`.

Tests : `python -m unittest discover tests`

## Ce que fait l'application web

- **Perso** : identité, portrait (photo du téléphone), espèce et sous-espèce avec illustration, historique,
  classes / multiclassage / sous-classes, aptitudes, histoire et notes, liste « À faire » (choix encore manquants).
- **▲ Niveau supérieur** (carte Classes) : l'assistant de montée de niveau en 6 étapes, comme dans le bureau —
  classe (prérequis de multiclassage), points de vie, nouvelles aptitudes, choix du niveau (sous-classe, amélioration
  ou don, style de combat, faveur de pacte, manifestations occultes), nouveaux sorts (tours de magie, sorts connus,
  grimoire, préparation, échange d'un sort connu), récapitulatif avant / après. Rien ne change avant « Confirmer ».
- **Carac** : achat de points, 4d6 avec répartition auto, saisie manuelle, bonus d'espèce (+ règle libre de Tasha),
  améliorations / dons, dons du MJ, sauvegardes, compétences (maîtrise / expertise), langues, maîtrises.
- **Combat** : **suivi du tour** (action, action bonus, réaction, déplacement, nouveau tour) avec les tuiles
  d'actions de classe et d'espèce (attaques lancées avec leurs dégâts, critique doublé, Second souffle, Rage,
  potions, réactions…), CA, initiative, PV / dégâts / soins / jets contre la mort, états et effets, ressources à
  sphères, armes, style de combat, options de classe (runes, tirs arcaniques, manœuvres, métamagie, Technique
  supérieure), ascendance draconique, **Forme sauvage** (bêtes autorisées selon le niveau et le Cercle de la Lune),
  armure, dés de vie, repos.
- **Magie** : emplacements et Pacte, DD et attaque, sorts connus / préparés, bibliothèque filtrée (mode MJ),
  lancement avec choix du niveau, **Métamorphose** (choix de la bête), concentration, **pacte et manifestations
  occultes**, Livre des secrets anciens, sorts accordés, sorts d'espèce, **sorts accordés par le MJ**.
- **Sac** : bourse, charge, objets du catalogue ou libres, paquetages, objets magiques (équipé / harmonisé),
  **objets magiques sur mesure**.
- **Alliés** : ménagerie (familiers, compagnons de classe, invocations, montures) avec fiche calculée, PV, statut,
  niveau du sort de convocation, jets et attaques ; conseils selon la classe.
- **Menu ☰** : plusieurs personnages, import / export, partage, impression PDF, 10 thèmes, lanceur de dés.
- **Édition 2014 ou 2024** (v52) : choisie à la création du personnage ; toute la fiche suit cette édition (classes, sous-classes, espèces, historiques, dons, sorts). Menu ☰ → **⚖ Règles de la table** : changer d'édition, règles optionnelles (potion en action bonus, bottes d'arme, inspiration héroïque, actions d'arme), choix des bottes d'arme.

Seul le **mannequin d'équipement** (affichage graphique des emplacements portés) reste propre à l'application
bureau : sur le web, les objets se portent avec la case « Équipé », et leurs effets s'appliquent de la même façon.

### Import / export

| Format | Export | Import | Usage |
|---|---|---|---|
| `.json` (un personnage) | oui | oui | **identique à la sauvegarde de l'application bureau** : un fichier s'ouvre des deux côtés |
| `.json` (sauvegarde complète) | oui | oui | tous les personnages du navigateur d'un coup |
| `.txt` (fiche lisible, Markdown) | oui | non | lecture, envoi au MJ (un texte ne contient pas toutes les données) |
| PDF | via « Imprimer » | — | fiche papier |
| Partager | fichier `.json` | — | feuille de partage du téléphone (messagerie, Drive…) |

Les personnages sont enregistrés **dans le navigateur** de l'appareil. Pour passer du téléphone au PC,
exportez le `.json` puis importez-le de l'autre côté.

---

## Mettre le projet sur GitHub

Prérequis : [Git](https://git-scm.com/downloads) installé et un compte GitHub.

1. Sur github.com : **New repository** → nom `fiche-dnd5e` → *Public* ou *Private* → **ne cochez pas**
   « Add a README » → **Create repository**.
2. Dans un terminal, depuis le dossier du projet (celui qui contient `app.py`) :

```bash
git init
git branch -M main
git add .
git commit -m "Fiche D&D 5e : version web mobile"
git remote add origin https://github.com/VOTRE_PSEUDO/fiche-dnd5e.git
git push -u origin main
```

GitHub demande alors de vous identifier : utilisez un *Personal access token* (Settings → Developer settings →
Personal access tokens) comme mot de passe, ou installez [GitHub Desktop](https://desktop.github.com/) /
`gh auth login`, qui s'en chargent.

Mises à jour suivantes :

```bash
git add .
git commit -m "Description du changement"
git push
```

Le dépôt contient aussi le workflow `.github/workflows/build-exe.yml` : chaque `push` compile toujours
l'exécutable Windows (onglet **Actions** du dépôt).

## Mettre l'application en ligne (gratuit) — Render

1. Créez un compte sur [render.com](https://render.com) avec « Sign in with GitHub ».
2. **New +** → **Blueprint** → choisissez le dépôt `fiche-dnd5e`. Render lit `render.yaml`
   (build : `pip install -r requirements.txt`, démarrage : `gunicorn app:app`, offre *Free*).
   *Variante* : **New +** → **Web Service** → dépôt → Runtime *Python 3*, Build Command
   `pip install -r requirements.txt`, Start Command `gunicorn app:app --bind 0.0.0.0:$PORT`, Instance *Free*.
3. **Apply / Create**. Après 2 à 3 minutes, l'adresse `https://fiche-dnd5e.onrender.com` (ou proche) est active.
4. Sur le téléphone, ouvrez l'adresse puis « Ajouter à l'écran d'accueil » (Safari : bouton Partager ;
   Chrome : menu ⋮) : l'application s'ouvre alors en plein écran comme une appli.

Chaque `git push` sur `main` redéploie automatiquement. Sur l'offre gratuite, le service s'endort après
15 minutes sans visite : la première ouverture suivante prend environ 30 à 60 secondes (vos personnages,
stockés sur le téléphone, ne sont pas touchés).

### Autre option : Hugging Face Spaces (ne s'endort qu'après 48 h)

1. [huggingface.co](https://huggingface.co) → **New Space** → SDK **Docker** → *Blank* → *Public*.
2. Ajoutez ces lignes **tout en haut** de `README.md` (Hugging Face lit la configuration du Space à cet endroit) :

```yaml
---
title: Fiche D&D 5e
emoji: 🎲
sdk: docker
app_port: 7860
---
```

3. Poussez le même code vers le Space (le `Dockerfile` fourni écoute sur le port 7860) :

```bash
git remote add space https://huggingface.co/spaces/VOTRE_PSEUDO/fiche-dnd5e
git push space main
```

(Hugging Face demande un *Access token* avec le droit *write* comme mot de passe.)

> Streamlit Community Cloud n'héberge que des applications Streamlit : il ne convient pas à cette architecture.
