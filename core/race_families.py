"""
Familles d'espèces (v53) pour l'assistant de création : une carte par famille (Elfe, Nain, Halfelin, Génasi…), puis
ses variantes — sous-races du fichier (Haut-elfe, Elfe des bois) et espèces apparentées (Elfe des mers, Elfe pâle,
Elfe astral, Drow, Eladrin…). Logique pure, sans interface.
"""
from __future__ import annotations

import re

from .rules import norm

FAMILY_OF = {"drow": "elfe", "eladrin": "elfe", "shadar-kai": "elfe", "duergar": "nain", "fadette": "fadette"}
TITLES = {"elfe": "Elfe", "nain": "Nain", "halfelin": "Halfelin", "gnome": "Gnome", "drakeide": "Drakéide",
          "humain": "Humain", "genasi": "Génasi", "aasimar": "Aasimar", "tieffelin": "Tieffelin",
          "demi-elfe": "Demi-elfe", "goliath": "Goliath", "orc": "Orc"}


def family_key(name: str) -> str:
    n = norm(re.sub(r"\s*\(.*?\)", "", name or "")).strip()
    first = n.split(" ")[0] if n else ""
    return FAMILY_OF.get(first, first)


def families(names: list[str]) -> list[tuple[str, list[str]]]:
    """[(titre de la famille, [espèces])], dans l'ordre alphabétique des titres."""
    groups: dict[str, list[str]] = {}
    for name in names:
        groups.setdefault(family_key(name), []).append(name)
    out = []
    for key, members in groups.items():
        title = TITLES.get(key) or (members[0] if len(members) == 1 else members[0].split(" ")[0])
        members.sort(key=lambda m: (norm(m) != norm(title), norm(m)))   # l'espèce « de base » d'abord
        out.append((title, members))
    return sorted(out, key=lambda kv: norm(kv[0]))


def family_of(name: str, names: list[str]) -> tuple[str, list[str]]:
    key = family_key(name)
    return next(((t, m) for t, m in families(names) if family_key(m[0]) == key), (name, [name]))
