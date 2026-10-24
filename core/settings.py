"""Préférences utilisateur persistantes (thème, taille de police, dernier dossier) — fichier JSON local."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_THEME = "bg3"   # Porte de Baldur (BG3) : thème principal au premier lancement
DEFAULTS = {"theme": DEFAULT_THEME, "font_px": 14, "last_dir": "", "ordre_onglets": [],
            "regle_survie": False}   # regle_survie : repos long = 1 ration consommée   # ordre_onglets : clés des onglets


def settings_path() -> Path:
    return Path.home() / ".dnd5e_fiche" / "settings.json"


def load_settings() -> dict:
    data = dict(DEFAULTS)
    try:
        with open(settings_path(), encoding="utf-8") as fh:
            loaded = json.load(fh)
        if isinstance(loaded, dict):
            data.update({k: v for k, v in loaded.items() if k in DEFAULTS})
    except (OSError, json.JSONDecodeError):
        pass
    data["font_px"] = max(11, min(22, int(data.get("font_px", 14))))
    if not isinstance(data.get("ordre_onglets"), list):
        data["ordre_onglets"] = []
    return data


def save_settings(data: dict) -> None:
    try:
        path = settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({k: data.get(k, v) for k, v in DEFAULTS.items()}, fh, ensure_ascii=False, indent=2)
    except OSError:
        pass  # les préférences ne sont jamais critiques
