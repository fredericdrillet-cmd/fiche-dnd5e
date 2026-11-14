"""
Illustrations de races (onglet Race) — recherche du fichier d'après le nom, sans dépendance à Qt.

Convention : data/images/races/<nom-de-la-race>.<png|jpg|jpeg|webp>, nom en minuscules sans accents
(« demi-elfe.jpg », « genasi-d-air.jpg »). La comparaison ignore accents, majuscules, espaces, tirets et
apostrophes : « Génasi d'air.jpg » ou « genasi_dair.png » conviennent aussi.

Ordre de recherche : sous-espèce (« Elfe des bois ») -> race complète (« Drow (Elfe noir) ») -> race sans la
parenthèse (« Drow ») -> image dont le nom est le début de celui de la race (« myconide » pour « Myconide éveillé »).
Aucune image : None (l'interface affiche un médaillon de remplacement).
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Optional

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
from .paths import get_resource_path

DEFAULT_DIR = Path(get_resource_path(str(Path("data") / "images" / "races")))   # v47 : compatible PyInstaller
_CACHE: dict[str, dict[str, Path]] = {}


def _plain(text: str) -> str:
    text = unicodedata.normalize("NFD", text or "").lower()
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def key(text: str) -> str:
    """Clé de comparaison : « Génasi d'air » -> « genasidair »."""
    return re.sub(r"[^a-z0-9]+", "", _plain(text))


def file_slug(text: str) -> str:
    """Nom de fichier conventionnel : « Génasi d'air » -> « genasi-d-air »."""
    return re.sub(r"[^a-z0-9]+", "-", _plain(text)).strip("-")


def index(folder: Path = DEFAULT_DIR, refresh: bool = False) -> dict[str, Path]:
    """{clé: fichier} des images du dossier (PNG prioritaire sur JPEG à nom égal), mis en cache."""
    folder = Path(folder)
    cache_key = str(folder)
    if refresh or cache_key not in _CACHE:
        found: dict[str, Path] = {}
        if folder.is_dir():
            for p in sorted(folder.iterdir(), key=lambda p: IMAGE_EXTS.index(p.suffix.lower())
                            if p.suffix.lower() in IMAGE_EXTS else 99):
                if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                    found.setdefault(key(p.stem), p)
        _CACHE[cache_key] = found
    return _CACHE[cache_key]


def find_race_image(race: str, subrace: str = "", folder: Path = DEFAULT_DIR) -> Optional[Path]:
    files = index(folder)
    if not files or not race:
        return None
    candidates = []
    if subrace:
        candidates.append(key(subrace))
    candidates += [key(race), key(re.sub(r"\(.*?\)", "", race))]
    for c in candidates:
        if c and c in files:
            return files[c]
    base = key(re.sub(r"\(.*?\)", "", race))
    prefix = [k for k in files if len(k) >= 5 and base.startswith(k)]
    if prefix:
        return files[max(prefix, key=len)]
    # v52 : espèce 2024 générique (« Nain », « Gnome ») -> illustration d'une de ses variantes 2014 (« nain-des-collines »)
    variants = sorted((k for k in files if len(base) >= 3 and k.startswith(base) and k != base), key=len)
    return files[variants[0]] if variants else None
