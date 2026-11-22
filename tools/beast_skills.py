"""
Compétences des bêtes (v52) — complète le champ « competences » de data/monsters_db.json d'après le Manuel des
monstres (DD 5e), pour les bêtes qui ne l'ont pas. La Forme sauvage et la Métamorphose utilisent ces bonus
(le meilleur entre celui de la bête et celui du personnage pour la Forme sauvage). Idempotent.

    python tools/beast_skills.py          # applique
    python tools/beast_skills.py --check  # liste ce qui manque, sans écrire
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "monsters_db.json"

SKILLS = {
    "Araignée": "Discrétion +4", "Araignée géante": "Discrétion +7",
    "Araignée-loup géante": "Discrétion +7, Perception +3", "Belette": "Discrétion +5, Perception +3",
    "Belette géante": "Discrétion +5, Perception +3", "Chat": "Discrétion +4, Perception +3",
    "Chouette": "Discrétion +3, Perception +3", "Chouette géante": "Discrétion +4, Perception +5",
    "Crabe": "Discrétion +2", "Crabe géant": "Discrétion +4", "Crocodile": "Discrétion +2",
    "Crocodile géant": "Discrétion +5", "Grand singe": "Athlétisme +5, Perception +3",
    "Grenouille": "Discrétion +3, Perception +1", "Grenouille géante": "Discrétion +3, Perception +2",
    "Lion": "Discrétion +6, Perception +3", "Loup": "Discrétion +4, Perception +3",
    "Loup sanguinaire": "Discrétion +4, Perception +3", "Panthère": "Discrétion +6, Perception +4",
    "Pieuvre": "Discrétion +4, Perception +2", "Pieuvre géante": "Discrétion +5, Perception +4",
    "Singe géant": "Athlétisme +9, Perception +4", "Tigre": "Discrétion +6, Perception +3",
    "Tigre à dents de sabre": "Discrétion +6, Perception +3",
}


def main() -> int:
    check = "--check" in sys.argv
    data = json.loads(FILE.read_text(encoding="utf-8"))
    changed = []
    for m in data:
        name = m.get("nom", "")
        if name in SKILLS and not (m.get("competences") or "").strip():
            changed.append(name)
            if not check:
                m["competences"] = SKILLS[name]
    if changed and not check:
        FILE.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print("{} bête(s) {} : {}".format(len(changed), "à compléter" if check else "complétée(s)", ", ".join(changed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
