"""
Rapports d'erreur (v52) — logique pure (aucune dépendance Qt).

Une erreur inattendue ne ferme plus l'application : `write_report` enregistre le détail technique et la fiche en
cours dans `<dossier utilisateur>/erreurs/erreur_AAAAMMJJ-HHMMSS.txt` (20 rapports au plus).
"""
from __future__ import annotations

import datetime as _dt
import json
import platform
import sys
import traceback
from pathlib import Path
from typing import Optional

KEEP = 20
VERSION = "v52"


def reports_dir() -> Path:
    from .paths import user_data_dir
    return user_data_dir() / "erreurs"


def format_report(exc_type, exc, tb, character: Optional[dict] = None, context: str = "") -> str:
    lines = ["Fiche de personnage D&D 5e — rapport d'erreur",
             "Date : {}".format(_dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
             "Version : {} — Python {} — {} {}".format(VERSION, platform.python_version(), platform.system(),
                                                       platform.release()),
             "Exécutable : {}".format("oui" if getattr(sys, "frozen", False) else "non (code source)")]
    if context:
        lines.append("Contexte : " + context)
    lines += ["", "".join(traceback.format_exception(exc_type, exc, tb)).rstrip()]
    if character is not None:
        light = {k: v for k, v in character.items() if k not in ("portrait", "historique_jets", "journal")}
        lines += ["", "--- Fiche (sans portrait ni journaux) ---", json.dumps(light, ensure_ascii=False, indent=1)]
    return "\n".join(lines) + "\n"


def write_report(text: str, root: Optional[Path] = None, keep: int = KEEP) -> Optional[Path]:
    folder = root or reports_dir()
    try:
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "erreur_{}.txt".format(_dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        path.write_text(text, encoding="utf-8")
        for old in sorted(folder.glob("erreur_*.txt"))[:-keep]:
            old.unlink(missing_ok=True)
        return path
    except OSError:
        return None


def short_message(exc_type, exc) -> str:
    return "{} : {}".format(getattr(exc_type, "__name__", "Erreur"), str(exc)[:300])
