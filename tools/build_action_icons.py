"""
Registre des icônes d'actions (v53) : recense TOUTES les actions du jeu (chaque classe et sous-classe aux
niveaux 3, 7, 11, 15 et 20, en 2014 et 2024, toutes les options choisies — manœuvres, runes, tirs arcaniques,
métamagie — chaque espèce, les actions d'arme) puis attribue la petite marque distinctive nécessaire pour que deux
actions n'aient jamais le même dessin. Écrit data/action_icons.json.

    python tools/build_action_icons.py           # écrit le registre
    python tools/build_action_icons.py --check   # vérifie qu'il est à jour (sans écrire)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "data" / "action_icons.json"

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402
from core import action_icons as AI  # noqa: E402
from core import icon_art as A  # noqa: E402
from core.tile_icons import tile_icon  # noqa: E402


def all_actions(db) -> list[str]:
    names = set()

    def take(eng) -> None:
        for x in eng.turn_actions():
            kind, name, _cat = tile_icon(x)
            if kind == "action":
                names.add(name)
    for ed in ("2014", "2024"):
        base = Engine(db, Engine.new_character(db))
        if ed == "2024":
            base.set_edition_mode("2024")
        for cls in base.db.class_names():
            for sub in [s["nom"] for s in base.db.subclasses(cls)] or [""]:
                for lvl in (3, 7, 11, 15, 20):
                    ch = Engine.new_character(db)
                    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
                    eng = Engine(db, ch)
                    eng.normalize()
                    if ed == "2024":
                        eng.set_edition_mode("2024")
                        eng.normalize()
                    for s in eng.option_sets():
                        if s["key"] in ("manoeuvres", "tirs", "runes", "metamagie"):
                            ch.options_classe[s["key"]] = list(s["options"])
                    ch.options_classe["manoeuvres"] = list(db.maneuvers)
                    eng.normalize()
                    take(eng)
        for race in base.race_options():
            ch = Engine.new_character(db)
            ch.classes = [{"nom": "Guerrier", "niveau": 10, "sous_classe": "", "pv_jets": []}]
            eng = Engine(db, ch)
            eng.normalize()
            if ed == "2024":
                eng.set_edition_mode("2024")
                eng.normalize()
            ch.race = race
            eng.normalize()
            take(eng)
    eng = Engine(db, Engine.new_character(db))
    eng.normalize()
    for w in db.weapons:                                 # actions d'arme (bottes 2024, actions façon BG3)
        try:
            names.update(row["nom"] for row in eng.weapon_actions({"nom": w}))
        except Exception:                                # pragma: no cover - arme sans action
            pass
    return sorted(names)


def build(db) -> dict:
    names = all_actions(db)
    taken = {fn() for fn in A.ICONS.values()} | {fn() for fn in AI.WEAPON_ART.values()}
    return {"actions": names, "variantes": AI.assign_variants(names, taken)}


def main() -> int:
    data = build(Database(ROOT / "data"))
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("registre à jour" if ok else "registre à régénérer")
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print("{} actions, {} avec une marque distinctive".format(len(data["actions"]), len(data["variantes"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
