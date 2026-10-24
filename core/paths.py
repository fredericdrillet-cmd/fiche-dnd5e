"""
Résolution des chemins (v47) — compatible avec l'exécution depuis le code source ET depuis l'exécutable
PyInstaller (`--onefile`).

- Ressources en LECTURE (données JSON, images, icône) : `get_resource_path("data")`.
  Exécutable PyInstaller : les fichiers embarqués avec `--add-data` sont extraits dans le dossier temporaire
  `sys._MEIPASS` ; on les y cherche.
  Code source : on part du dossier du projet (celui de main.py). On n'utilise pas le dossier courant, qui change
  selon la façon de lancer l'appli (Spyder, raccourci, double-clic…).
- Données en ÉCRITURE (réglages, copies de travail) : `user_data_dir()`.
  Le dossier temporaire de PyInstaller est en lecture seule et effacé à la fermeture : rien n'y est écrit.
  Sous Windows : %APPDATA%\\Fiche_DnD5E ; ailleurs : ~/.dnd5e_fiche.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_FOLDER = "Fiche_DnD5E"
PROJECT_DIR = Path(__file__).resolve().parent.parent


def is_frozen() -> bool:
    """Vrai quand l'appli tourne depuis l'exécutable PyInstaller."""
    return bool(getattr(sys, "frozen", False)) or hasattr(sys, "_MEIPASS")


def base_dir() -> Path:
    """Racine des ressources : dossier d'extraction de PyInstaller, sinon dossier du projet."""
    meipass = getattr(sys, "_MEIPASS", None)
    return Path(meipass) if meipass else PROJECT_DIR


def get_resource_path(relative_path: str) -> str:
    """Obtient le chemin absolu vers une ressource (développement et exécutable PyInstaller)."""
    return os.path.join(str(base_dir()), relative_path)


def user_data_dir() -> Path:
    """Dossier inscriptible de l'utilisateur (créé au besoin)."""
    if os.name == "nt" and os.environ.get("APPDATA"):
        path = Path(os.environ["APPDATA"]) / APP_FOLDER
    else:
        path = Path.home() / ".dnd5e_fiche"
    path.mkdir(parents=True, exist_ok=True)
    return path


def working_copy(relative_path: str) -> Path:
    """Copie de travail inscriptible d'une ressource embarquée (fichier ou dossier), créée au premier appel.
    À utiliser pour toute donnée que l'utilisateur doit pouvoir modifier ; la ressource d'origine reste intacte."""
    src = Path(get_resource_path(relative_path))
    dst = user_data_dir() / relative_path
    if not dst.exists() and src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    return dst
