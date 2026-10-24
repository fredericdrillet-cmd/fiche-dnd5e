#!/usr/bin/env python3
"""
Vérification à blanc (aucune écriture) d'un module de corrections :
    python3 tools/check_fixes.py <module_classe>     ex. barbare   (class_fixes + class_texts)
    python3 tools/check_fixes.py race <module>       ex. race especes_a_k
Contrôle : opérations applicables, textes couvrant toutes les aptitudes après correction, sorts de sous-classe
présents dans la base de sorts, bonus raciaux lisibles, sorts raciaux (*italique*) reconnus.
"""
import copy, importlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]
from core.data_loader import Database, parse_race_bonus
import apply_corrections as AC, apply_class_texts as AT

db = Database(ROOT / "data")
problems = []
if sys.argv[1] == "race":
    mod = importlib.import_module("race_fixes." + sys.argv[2])
    races = AC.load(ROOT / "data" / "Races.json")
    index = {e["nom"]: e for e in races["especes"]}
    for op in mod.FIXES:
        if op["espece"] not in index and op["op"] != "vitesse":
            problems.append(f"espèce inconnue : {op['espece']}")
        if op["op"] == "set" and op["champ"] == "caracteristiques":
            b = parse_race_bonus(op["valeur"])
            if not (b["fixe"] or b["libres"]):
                problems.append(f"bonus illisible : {op['valeur']}")
        if op["op"] == "trait":
            import re
            for m in re.finditer(r"\*([^*]+)\*", op["description"]):
                if not db.find_spell_fuzzy(m.group(1)):
                    problems.append(f"{op['espece']} / {op['nom']} : sort introuvable *{m.group(1)}*")
    for attr in ("AUDIT", "CORRIGE"):
        for e in getattr(mod, attr):
            if len(e) != 4 or e[0] not in ("majeur", "mineur", "info"):
                problems.append(f"{attr} mal formé : {e}")
else:
    name = sys.argv[1]
    texts = importlib.import_module("class_texts." + name)
    raw = AC.load(ROOT / "data" / f"{texts.CLASSE}.json")
    try:
        fixes = importlib.import_module("class_fixes." + name)
        for op in fixes.FIXES:
            err = AC.apply_class_fix(raw["classe"], op)
            if err:
                problems.append(err)
            if op["op"] == "sorts":
                for s in op["sorts"]:
                    if not db.find_spell(s):
                        problems.append(f"{op['sous_classe']} : sort absent de la base « {s} »")
    except ModuleNotFoundError:
        problems.append("pas de module class_fixes." + name)
    problems += AT.apply_raw(texts, raw)
    for attr in ("AUDIT", "CORRIGE"):
        for e in getattr(texts, attr, []):
            if len(e) != 4 or e[0] not in ("majeur", "mineur", "info"):
                problems.append(f"{attr} mal formé : {e}")
print("\n".join(problems) or "OK")
