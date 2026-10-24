#!/usr/bin/env python3
"""
Manœuvres du Maître de guerre (v39), idempotent : corrige « Manœuvre tactique » et ajoute les 7 manœuvres du
Chaudron des merveilles de Tasha dans data/Actions_Classes.json (clé « manoeuvres »).

    python tools/maneuver_fixes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "Actions_Classes.json"

FIXES = {
    "Manœuvre tactique": "Quand vous touchez une créature avec une attaque d'arme, ajoutez le dé aux dégâts ; un allié "
                         "qui vous voit peut utiliser sa réaction pour se déplacer de la moitié de sa vitesse sans "
                         "provoquer d'attaque d'opportunité de la cible.",
    "Embuscade": "Quand vous faites un test de Dextérité (Discrétion) ou un jet d'initiative, ajoutez le dé au jet "
                 "(sauf si vous êtes neutralisé). (Tasha)",
    "Échange de position": "À votre tour, avant ou après votre déplacement, échangez de place avec une créature "
                           "consentante à 1,50 m (sans attaque d'opportunité) ; vous ou elle ajoutez le dé à la CA "
                           "jusqu'au début de votre prochain tour. (Tasha)",
    "Garde préparée": "Réaction quand une créature que vous voyez entre dans votre allonge : attaque d'arme contre "
                      "elle, ajoutez le dé aux dégâts. (Tasha)",
    "Présence imposante": "Quand vous faites un test de Charisme (Intimidation, Représentation ou Persuasion), ajoutez "
                          "le dé au test. (Tasha)",
    "Frappe agrippante": "Juste après avoir touché une créature avec une attaque au corps à corps à votre tour : action "
                         "bonus pour tenter de l'agripper, en ajoutant le dé au test de Force (Athlétisme). (Tasha)",
    "Lancer rapide": "Action bonus : attaque à distance avec une arme de lancer (dégainée dans le cadre de l'attaque) ; "
                     "ajoutez le dé aux dégâts. (Tasha)",
    "Évaluation tactique": "Quand vous faites un test d'Intelligence (Investigation ou Histoire) ou de Sagesse "
                           "(Perspicacité), ajoutez le dé au test. (Tasha)",
}


def apply(path: Path = PATH) -> int:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    lst = data.setdefault("manoeuvres", [])
    by_name = {m["nom"]: m for m in lst}
    for name, desc in FIXES.items():
        if name in by_name:
            by_name[name]["description"] = desc
        else:
            lst.append({"nom": name, "description": desc})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(lst)


if __name__ == "__main__":
    print("{} manœuvres dans {}".format(apply(), PATH.name))
    sys.exit(0)
