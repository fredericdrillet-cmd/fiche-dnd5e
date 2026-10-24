#!/usr/bin/env python3
"""Recherche de sorts dans la base : python3 tools/find_spell.py "Toucher du vampire" "Colonne de flamme" ...
Affiche le nom exact retenu par la base (ou « ABSENT ») et les noms proches."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.data_loader import Database
from core.rules import norm
db = Database(ROOT / "data")
for q in sys.argv[1:]:
    exact = db.find_spell(q)
    close = [n for n in db.spells if any(w in norm(n) for w in norm(q).split() if len(w) > 4)][:8]
    print(f"{q!r}: {exact['nom'] + ' (niv. ' + str(exact['niveau']) + ')' if exact else 'ABSENT'} | proches: {close}")
