#!/usr/bin/env python3
"""
Francisation des données : retire les doublons VO (« Lame psychique / Soulknife », « Bretteur (Swashbuckler) »…)
et les termes anglais visibles dans l'interface. Seule la terminologie française officielle est conservée.

    python tools/francisation.py            # applique (idempotent)
    python tools/francisation.py --check    # liste ce qui serait modifié

Les remplacements portent sur toutes les chaînes des fichiers data/*.json (sauf le bestiaire et le champ
« nom_en » des objets magiques, référence VO interne jamais affichée). Les anciennes sauvegardes sont migrées au
chargement grâce à NAME_MIGRATIONS (core/engine.py).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))

# remplacements exacts de sous-chaînes (ordre = ordre d'application)
REPLACEMENTS: list[tuple[str, str]] = [
    # sous-classes
    ("Lame psychique / Soulknife", "Lame psychique"),
    ("Bretteur (Swashbuckler)", "Bretteur"),
    ("Conspirateur (Mastermind)", "Conspirateur"),
    ("Éclaireur (Scout)", "Éclaireur"),
    ("Enquêteur (Inquisitive)", "Enquêteur"),
    ("Fantôme (Phantom)", "Fantôme"),
    ("Cercle des Fournaises (Wildfire)", "Cercle des Fournaises"),
    ("Guerrier Psi (Soldat psi)", "Soldat psi"),              # nom officiel VF (Tasha)
    ("La Lame maudite (Magelame)", "La Lame maudite"),         # « Magelame » désigne le Chanteur de lame
    # langues
    ("Profonde Parler (Deep Speech)", "Profond"),
    ("Commun des Profondeurs (Undercommon)", "Commun des profondeurs"),
    ("Halphen", "Halfelin"),                                   # coquille (langue des halfelins)
    # sources et mentions diverses
    ("Création de la communauté (Homebrew populaire)", "Création de la communauté"),
    ("Création de la communauté (Homebrew)", "Création de la communauté"),
    ("Favori de la communauté / Homebrew mycologique", "Favori de la communauté"),
    ("Homebrew / Populaire", "Création de la communauté"),
    (" (SCAG)", ""),
    (" (construct)", ""),
]
# valeurs entières remplacées seulement si la chaîne est exactement égale (champ « origine » des armures…)
EXACT: dict[str, str] = {"Homebrew": "Création de la communauté"}

# anciens noms -> nouveaux (sauvegardes, corrections de données relancées)
NAME_MIGRATIONS: dict[str, str] = {old: new for old, new in REPLACEMENTS if "(" in old or "/" in old}

SKIP_FILES = {"monsters_db.json"}
SKIP_KEYS = {"nom_en", "name_en"}


def fix_text(text: str) -> str:
    if text in EXACT:
        return EXACT[text]
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
    return text


def _walk(node, changes: list):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            nk = fix_text(k) if isinstance(k, str) else k
            out[nk] = v if k in SKIP_KEYS else _walk(v, changes)
            if nk != k:
                changes.append(k)
        return out
    if isinstance(node, list):
        return [_walk(v, changes) for v in node]
    if isinstance(node, str):
        new = fix_text(node)
        if new != node:
            changes.append(node[:60])
        return new
    return node


def apply(write: bool = True, data_dir: Path = DATA) -> dict[str, int]:
    from core.data_loader import read_json
    report = {}
    for path in sorted(Path(data_dir).glob("*.json")):
        if path.name in SKIP_FILES:
            continue
        data, _warn = read_json(path)
        changes: list = []
        fixed = _walk(data, changes)
        if changes:
            report[path.name] = len(changes)
            if write:
                path.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str]) -> int:
    report = apply(write="--check" not in argv)
    for name, n in report.items():
        print("{} : {} chaîne(s) francisée(s)".format(name, n))
    if not report:
        print("Rien à franciser.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
