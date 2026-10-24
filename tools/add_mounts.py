#!/usr/bin/env python3
"""
Ajoute (ou met à jour) les montures courantes dans data/Familiers_Invocations.json — v36, idempotent.

Profils du Manuel des monstres (DMG/MM 5e, règles de référence) : Cheval de selle, Cheval de trait, Cheval de guerre,
Poney, Mule, Chameau, Mâtin (mastiff). entity_type « mount » ; prix d'achat du Manuel des joueurs (montures).

    python tools/add_mounts.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "Familiers_Invocations.json"

CONTROL = ("Monture contrôlée : elle agit à votre initiative et ne peut que Foncer, Se désengager ou Esquiver ; "
           "monture indépendante (intelligente) : elle garde sa propre initiative. Monter ou descendre coûte la "
           "moitié de votre vitesse.")
CAVALIER = {"name": "Né en selle (Guerrier Cavalier)", "kind": "feature", "level_min": 3, "book": "XGtE",
            "notes": "Avantage pour ne pas tomber de selle, monter ou descendre ne coûte que 1,50 m de déplacement."}


def hooves(bonus: int, dice: str, dtype: str = "Contondant", name: str = "Sabots", reach: str = "1.5m",
           extra: str = "") -> dict:
    return {"name": name, "description": "Attaque d'arme au corps à corps : {:+d} au toucher, allonge 1,5 m, une cible. "
                                         "Touché : {} dégâts {}.{}".format(bonus, dice, dtype.lower(), extra),
            "activation": "action", "uses": None, "attack_type": "melee", "attack_bonus": bonus, "range": reach,
            "damage_dice": dice, "damage_type": dtype, "extra_damage_dice": "", "extra_damage_type": "", "save": None}


def mount(eid, name, name_en, size, cr, ac, hp_formula, hp, speed, stats, actions, price, traits=None, skills=None,
          pp=10, cavalier=True):
    sources = [{"name": "Achat", "kind": "purchase", "level_min": None, "book": "PHB",
                "notes": "Prix : {} (Manuel des joueurs, montures et véhicules).".format(price)}]
    if cavalier:
        sources.append(CAVALIER)
    return {
        "id": eid, "name": name, "name_en": name_en, "entity_type": "mount", "source": "MM", "category": "monture",
        "type": "Bête", "size": size, "alignment": "Non aligné", "cr": cr, "ac": ac, "ac_note": "", "hp_formula":
        hp_formula, "hp_base": hp, "speed": {"walk": speed},
        "stats": dict(zip(("str", "dex", "con", "int", "wis", "cha"), stats)), "saves": {}, "skills": skills or {},
        "senses": "Aucun sens particulier", "passive_perception": pp, "damage_vulnerabilities": [],
        "damage_resistances": [], "damage_immunities": [], "condition_immunities": [], "languages": "Aucune",
        "traits": traits or [], "actions": actions, "reactions": [],
        "summon_info": {"origin": "purchase", "sources": sources, "concentration": False,
                        "duration": "Permanente (animal acheté ou dressé)", "control": CONTROL},
        "scaling": None}


MOUNTS = [
    mount("cheval_selle", "Cheval de selle", "Riding Horse", "G", "1/4", 10, "2d10 + 2", 13, "18m",
          (16, 10, 12, 2, 11, 7), [hooves(5, "2d4 + 3")], "75 po"),
    mount("cheval_trait", "Cheval de trait", "Draft Horse", "G", "1/4", 10, "3d10 + 3", 19, "12m",
          (18, 10, 12, 2, 11, 7), [hooves(6, "2d4 + 4")], "50 po"),
    mount("cheval_guerre", "Cheval de guerre", "Warhorse", "G", "1/2", 11, "3d10 + 3", 19, "18m",
          (18, 12, 13, 2, 12, 7), [hooves(6, "2d6 + 4")], "400 po", pp=11,
          traits=[{"name": "Charge piétinante", "description": "Si le cheval se déplace d'au moins 6 m en ligne droite "
                   "vers une créature puis la touche avec ses sabots lors du même tour, la cible doit réussir un JS de "
                   "Force DD 14 ou tomber à terre. Si elle est à terre, le cheval peut l'attaquer avec ses sabots par "
                   "une action bonus."}]),
    mount("poney", "Poney", "Pony", "M", "1/8", 10, "2d8 + 2", 11, "12m", (15, 10, 13, 2, 11, 7),
          [hooves(4, "2d4 + 2")], "30 po"),
    mount("mule", "Mule", "Mule", "M", "1/8", 10, "2d8 + 2", 11, "12m", (14, 10, 13, 2, 10, 5),
          [hooves(4, "1d4 + 2")], "8 po",
          traits=[{"name": "Bête de somme", "description": "La mule compte comme une créature de taille Grande pour "
                   "déterminer sa capacité de charge."},
                  {"name": "Pied sûr", "description": "La mule a l'avantage aux jets de sauvegarde de Force et de "
                   "Dextérité contre les effets qui la feraient tomber à terre."}]),
    mount("chameau", "Chameau", "Camel", "G", "1/8", 9, "2d10 + 4", 15, "15m", (16, 8, 14, 2, 8, 5),
          [hooves(5, "1d4", name="Morsure")], "50 po", pp=9),
    mount("matin", "Mâtin", "Mastiff", "M", "1/8", 12, "1d8 + 1", 5, "12m", (13, 14, 12, 3, 12, 7),
          [hooves(3, "1d6 + 1", "Perforant", name="Morsure",
                  extra=" Si la cible est une créature, elle doit réussir un JS de Force DD 11 ou tomber à terre.")],
          "25 po", skills={"Perception": 3}, pp=13, cavalier=False,
          traits=[{"name": "Ouïe et odorat aiguisés", "description": "Le mâtin a l'avantage aux tests de Sagesse "
                   "(Perception) basés sur l'ouïe ou l'odorat."},
                  {"name": "Monture de petite taille", "description": "Un mâtin peut servir de monture à une "
                   "créature de taille Petite (halfelin, gnome…)."}]),
]


def apply(path: Path = PATH) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {e["id"]: i for i, e in enumerate(data)}
    for m in MOUNTS:
        if m["id"] in by_id:
            data[by_id[m["id"]]] = m
        else:
            data.append(m)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(MOUNTS)


if __name__ == "__main__":
    print("{} montures écrites dans {}".format(apply(), PATH.name))
    sys.exit(0)
