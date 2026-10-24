# Rapport de build v47 — exécutable Windows autonome

## 1. Résultat
| Élément | État |
|---|---|
| Chemins compatibles PyInstaller (`core/paths.py`) | ✔ fait et testé (mode source, mode `sys._MEIPASS` simulé) |
| `build_executable.py` (compilation, placement, vérification, journal) | ✔ écrit ; testé en mode `--simulation` |
| `compiler_windows.bat` (double-clic) | ✔ |
| Compilation automatique sur GitHub (`.github/workflows/build-exe.yml`) | ✔ prête |
| Icône `assets/app_icon.ico` | ✔ |
| **`dist/Fiche_Personnage_DnD5E.exe`** | **✖ non fourni dans cette livraison** — voir § 2 |

## 2. Pourquoi l'exécutable n'est pas joint
L'environnement où le code est développé et testé est un serveur Linux.
- **PyInstaller ne compile pas pour un autre système.** Il produit un exécutable pour le système sur lequel il tourne : un `.exe` Windows ne peut être fabriqué que sous Windows. Aucune couche de compatibilité Windows (Wine) n'est disponible ici.
- **PyInstaller et PyQt6 ne sont pas installables ici.** Le dépôt de paquets accessible depuis ce serveur ne les propose pas.

Je ne joins donc pas de faux `.exe`. Deux moyens fiables de l'obtenir à chaque itération sans lancer de commande :
1. **Sur votre PC Windows** : double-clic sur `compiler_windows.bat`. Il installe PyInstaller et PyQt6 si besoin, lance les tests, compile, vérifie l'exécutable et le place dans `dist/` (environ 2 à 4 minutes).
2. **Sur GitHub** (aucune action locale) : publiez le dossier dans un dépôt. À chaque envoi, le flux « Exécutable Windows » compile sur un serveur Windows de GitHub et publie `Fiche_Personnage_DnD5E.exe` et `journal_build.txt`. Ils sont téléchargeables dans l'onglet *Actions*, artefact « Fiche_Personnage_DnD5E ».

## 3. Gestion des chemins (`core/paths.py`)
```python
def get_resource_path(relative_path):
    """Obtient le chemin absolu vers une ressource (développement et exécutable PyInstaller)."""
    return os.path.join(str(base_dir()), relative_path)   # base_dir() = sys._MEIPASS ou dossier du projet
```
- **Différence avec la fonction proposée** : en mode source, la base est le **dossier du projet**, et non `os.path.abspath(".")`. Le dossier courant varie selon le lancement (Spyder, raccourci, double-clic), alors que le dossier du projet est toujours le bon.
- **Utilisations** :
  - `main.py` : données par défaut `get_resource_path("data")` ;
  - `core/race_images.py` : images d'espèces ;
  - `ui/main_window.run()` : icône de la fenêtre.
- **Données inscriptibles** :
  - `sys._MEIPASS` est un dossier temporaire, effacé à la fermeture, où rien n'est écrit.
  - `user_data_dir()` donne `%APPDATA%\Fiche_DnD5E`.
  - `working_copy("data/…")` crée au premier appel une copie de travail modifiable d'une ressource embarquée.
  - Aujourd'hui, l'application ne modifie pas ses JSON. Les réglages restent dans `~/.dnd5e_fiche/settings.json`, dossier inscriptible conservé pour ne pas perdre vos préférences actuelles. Les fiches sont enregistrées là où vous le choisissez.
- **Vérification sans console** : `--check --check-file fichier.txt` écrit le résumé de la base dans un fichier, car un exécutable `--windowed` n'a pas de console.

## 4. Structure
J'ai gardé la structure du projet plutôt que de la renommer, ce qui aurait cassé les imports, les tests et vos habitudes dans Spyder :

| Proposé | Projet | Rôle |
|---|---|---|
| `database/` | `data/` | JSON (sorts, classes, objets…) et images |
| `assets/` | `assets/` (nouveau) | icône de l'application |
| `modules/` | `core/` (règles) + `ui/` (interface) | code source |
| `build_executable.py`, `dist/` | identiques | compilation, exécutable |

## 5. Commande PyInstaller générée
Extrait de `python build_executable.py --simulation` (chemins absolus raccourcis ; sous Windows, le séparateur de `--add-data` est « ; ») :
```
pyinstaller --noconfirm --clean --onefile --windowed --name Fiche_Personnage_DnD5E
  --distpath build/sortie --workpath build/travail --specpath build
  --add-data data;data --add-data assets;assets --icon assets/app_icon.ico
  --exclude-module tests --exclude-module qt_stub --exclude-module tkinter --exclude-module unittest --exclude-module pydoc
  main.py
```
À la fin de la compilation :
- l'exécutable est déplacé dans `dist/`, où il remplace l'ancien ;
- il est lancé avec `--check` pour prouver que les données embarquées sont lisibles ;
- le journal est écrit dans `dist/journal_build.txt`.

Un échec des tests annule la compilation, sauf avec `--sans-tests`.

## 6. Journal de cette itération (environnement Linux)
```
=== Build Fiche_Personnage_DnD5E — version v47 ===
Python 3.13 — Linux
Icône : app_icon.ico
✖ Ce script doit être lancé sous Windows : PyInstaller produit un exécutable pour le système sur lequel il tourne.
✖ pyinstaller manquant ; ✖ PyQt6 manquant
BUILD ANNULÉ
```
Tests : **569 OK**, 4 ignorés. Ils comprennent 6 nouveaux tests sur les chemins (mode source, `sys._MEIPASS` simulé avec lecture complète de la base, copie de travail hors du paquet), sur `--check-file` et sur la commande PyInstaller.

## 7. À vérifier lors du premier build Windows
- **Taille et démarrage** : environ 60 à 90 Mo avec Qt et 15 Mo de données. Le démarrage en `--onefile` prend quelques secondes, le temps de l'extraction.
- **Antivirus** : Windows Defender signale parfois les exécutables PyInstaller non signés. Si c'est le cas, autorisez le fichier.
