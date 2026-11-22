"""
Versions de sauvegarde (v52) — logique pure (aucune dépendance Qt).

Chaque enregistrement volontaire (Ctrl+S, Enregistrer sous) copie le fichier dans
`<dossier utilisateur>/versions/<nom du fichier>/AAAAMMJJ-HHMMSS-micro.json` ; seules les `KEEP` dernières copies sont
gardées. La sauvegarde automatique n'en crée pas. Restaurer une version garde d'abord la version en cours.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import shutil
from pathlib import Path
from typing import Optional

KEEP = 10


def versions_root() -> Path:
    from .paths import user_data_dir
    return user_data_dir() / "versions"


def _folder(save_path, root: Optional[Path] = None) -> Path:
    stem = re.sub(r"[^\w\-. ]", "_", Path(save_path).stem) or "personnage"
    return (root or versions_root()) / stem


def save_version(save_path, root: Optional[Path] = None, keep: int = KEEP, now: Optional[_dt.datetime] = None,
                 write=None) -> Path:
    """Copie datée du fichier enregistré (ou, avec `write(dest)`, de l'état fourni) ; supprime les plus anciennes
    au-delà de `keep`."""
    src = Path(save_path)
    folder = _folder(src, root)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = (now or _dt.datetime.now()).strftime("%Y%m%d-%H%M%S-%f")   # microsecondes : noms triables
    dest = folder / "{}.json".format(stamp)
    n = 1
    while dest.exists():                                  # même instant (date imposée) : suffixe croissant
        dest = folder / "{}-{:03d}.json".format(stamp, n)
        n += 1
    if write is not None:
        write(dest)
    else:
        shutil.copy2(src, dest)
    for old in sorted(folder.glob("*.json"))[:-keep]:
        old.unlink(missing_ok=True)
    return dest


def list_versions(save_path, root: Optional[Path] = None) -> list[dict]:
    """[{chemin, date, nom, niveau, pv}] du plus récent au plus ancien."""
    out = []
    for f in sorted(_folder(save_path, root).glob("*.json"), reverse=True):
        info = {"chemin": str(f), "date": "", "nom": "", "niveau": 0, "pv": ""}
        m = re.match(r"(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})", f.stem)
        if m:
            y, mo, d, h, mi, s = m.groups()
            info["date"] = "{}/{}/{} {}:{}".format(d, mo, y, h, mi)
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            info["nom"] = data.get("nom", "")
            info["niveau"] = sum(int(c.get("niveau", 0)) for c in data.get("classes", []) if isinstance(c, dict))
            info["pv"] = data.get("pv_actuels", "")
        except (OSError, ValueError):
            info["nom"] = "(fichier illisible)"
        out.append(info)
    return out


def version_label(info: dict) -> str:
    return "{} — {} niveau {} — {} PV".format(info["date"], info["nom"] or "Sans nom", info["niveau"], info["pv"])
