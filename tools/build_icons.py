"""
Icônes de l'interface (v53) : écrit data/icons/*.svg à partir des dessins de core/icon_art.py.

    python tools/build_icons.py            # écrit data/icons/*.svg
    python tools/build_icons.py --check    # vérifie que tous les fichiers sont à jour
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "data" / "icons"

from core.icon_art import ICONS, svg_document  # noqa: E402


def main() -> int:
    check = "--check" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for name in ICONS:
        p = OUT / "{}.svg".format(name)
        text = svg_document(name, ICONS[name]())
        if not p.exists() or p.read_text(encoding="utf-8") != text:
            stale.append(name)
            if not check:
                p.write_text(text, encoding="utf-8")
    print("{} icône(s) {} sur {}".format(len(stale), "à régénérer" if check else "écrite(s)", len(ICONS)))
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main())
