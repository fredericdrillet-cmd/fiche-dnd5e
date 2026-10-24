#!/usr/bin/env python3
"""
Sépare les objets magiques à paliers multiples en lignes indépendantes dans data/objets_magiques.json.

    « Potion de guérison » (variable)  -> Potion de guérison / majeure / supérieure / suprême
    « Arme +1, +2 ou +3 »              -> Arme +1 / Arme +2 / Arme +3 (idem armure, bouclier, munition, baguette...)
    « Potion / Ceinturon de force de géant », « Parchemin de sort », « Pierre de Ioun », « Figurine merveilleuse »,
    « Instrument de barde », « Cor du Valhalla », « Boule de cristal »  -> une ligne par variante.

Chaque nouvelle ligne garde les champs d'origine, reçoit sa rareté propre, un identifiant unique et le champ
« palier_de » (identifiant de l'objet générique). L'index (par_rarete / par_lien / par_type) est régénéré.
Le script est idempotent : relancé sur un fichier déjà séparé, il ne change rien.

Usage : python tools/split_magic_items.py [chemin/objets_magiques.json]
"""
from __future__ import annotations

import copy
import json
import re
import sys
import unicodedata
from pathlib import Path

RANK = {"commun": 0, "peu commun": 1, "rare": 2, "très rare": 3, "légendaire": 4, "artéfact": 5}


def slug(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("’", "'"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def variant(base: dict, name: str, rarity: str, description: str, **extra) -> dict:
    o = copy.deepcopy(base)
    rarity = re.sub(r"^ou\s+", "", rarity.lower().strip())
    o.update({"id": slug(name), "nom": name, "rarete": rarity, "raretes": [rarity], "rarete_texte": rarity,
              "rarete_rang": RANK.get(rarity, 98), "description": description.strip(), "palier_de": base["id"]})
    o.update(extra)
    return o


def intro(desc: str, marker: str) -> str:
    """Texte commun placé avant la première variante / le premier tableau."""
    i = desc.find(marker)
    return desc[:i].strip() if i > 0 else desc.strip()


# ------------------------------------------------------------------------------------------------- règles par objet
def split_plus(o: dict) -> list[dict]:
    """« X +1, +2 ou +3 » -> trois lignes (raretés lues dans rarete_texte : « peu commun (+1) rare (+2) ... »)."""
    rar = dict((int(b), a.strip()) for a, b in re.findall(r"([a-zéè ]+?)\s*\(\+(\d)\)", o["rarete_texte"]))
    base_name = o["nom"].replace(" +1, +2 ou +3", "").strip()
    out = []
    for n in (1, 2, 3):
        name = f"{base_name} +{n}"
        extra = o["description"] + f" Palier : bonus de +{n}."
        out.append(variant(o, name, rar.get(n, o["rarete"]), extra, bonus=n))
    return out


def split_scepter(o: dict) -> list[dict]:
    rar = dict((int(b), a.strip()) for a, b in re.findall(r"([a-zéè ]+?)\s*\(\+(\d)\)", o["rarete_texte"]))
    return [variant(o, f"{o['nom']} +{n}", rar.get(n, "rare"), o["description"] + f" Palier : bonus de +{n}.", bonus=n)
            for n in (1, 2, 3)]


def split_healing(o: dict) -> list[dict]:
    base = intro(o["description"], "Potion de ...")
    tiers = [("Potion de guérison", "commun", "2d4 + 2"), ("Potion de guérison majeure", "peu commun", "4d4 + 4"),
             ("Potion de guérison supérieure", "rare", "8d4 + 8"), ("Potion de guérison suprême", "très rare", "10d4 + 20")]
    return [variant(o, n, r, f"{base} Cette potion rend {pv} points de vie.", soins=pv) for n, r, pv in tiers]


GIANTS = [("des collines", 21), ("des pierres", 23), ("du givre", 23), ("du feu", 25), ("des nuages", 27),
          ("des tempêtes", 29)]


def split_giant_potion(o: dict) -> list[dict]:
    base = intro(o["description"], "Type de géant")
    rar = {"des collines": "peu commun", "des pierres": "rare", "du givre": "rare", "du feu": "rare",
           "des nuages": "très rare", "des tempêtes": "légendaire"}
    return [variant(o, f"Potion de force de géant {g}", rar[g], f"{base} Force fixée à {f} pendant 1 heure.", force=f)
            for g, f in GIANTS]


def split_giant_belt(o: dict) -> list[dict]:
    base = intro(o["description"], "Type")
    rar = {"des collines": "rare", "des pierres": "très rare", "du givre": "très rare", "du feu": "très rare",
           "des nuages": "légendaire", "des tempêtes": "légendaire"}
    return [variant(o, f"Ceinturon de force de géant {g}", rar[g], f"{base} Force fixée à {f}.", force=f)
            for g, f in GIANTS]


def split_scroll(o: dict) -> list[dict]:
    base = intro(o["description"], "Niveau\ndu sort").replace(
        "le bonus d'attaque, ainsi que sa rareté, comme indiqué dans le tableau suivant :", "le bonus d'attaque.")
    rows = [("sort mineur", "commun", 13, 5), ("1", "commun", 13, 5), ("2", "peu commun", 13, 5),
            ("3", "peu commun", 15, 7), ("4", "rare", 15, 7), ("5", "rare", 17, 9), ("6", "très rare", 17, 9),
            ("7", "très rare", 18, 10), ("8", "très rare", 18, 10), ("9", "légendaire", 19, 11)]
    out = []
    for lvl, rar, dd, atk in rows:
        name = "Parchemin de sort (sort mineur)" if lvl == "sort mineur" else f"Parchemin de sort (niveau {lvl})"
        out.append(variant(o, name, rar, f"{base} Ce parchemin : DD de sauvegarde {dd}, bonus d'attaque +{atk}.",
                           dd=dd, attaque=atk))
    return out


def split_paragraph_variants(o: dict, prefix: str) -> list[dict]:
    """Variantes décrites en paragraphes « Nom (rareté). Texte » (Pierre de Ioun, Figurine merveilleuse)."""
    desc = o["description"]
    rx = re.compile(r"^([A-ZÉÈÂÎÔ][^\n(]{2,60}?)\s*\((commun|peu commun|rare|très rare|légendaire)\)\.\s*(.*)$",
                    re.M | re.I)
    matches = list(rx.finditer(desc))
    if not matches:
        return [o]
    base = desc[:matches[0].start()].strip()
    out = []
    for m in matches:
        name = f"{prefix} ({m.group(1).strip()})"
        out.append(variant(o, name, m.group(2), f"{base}\n{m.group(1).strip()}. {m.group(3).strip()}"))
    return out


def split_bard_instrument(o: dict) -> list[dict]:
    desc = o["description"]
    lines = [x.strip() for x in desc.split("\n")]
    base = intro(desc, "Instrument\nRareté")
    common = ""
    out = []
    i = lines.index("Sorts") + 1 if "Sorts" in lines else len(lines)
    while i + 2 < len(lines) + 1 and i < len(lines):
        name = lines[i]
        rar = lines[i + 1] if i + 1 < len(lines) else ""
        spells = lines[i + 2] if i + 2 < len(lines) else ""
        if name.lower() == "tous":
            common = spells
        elif rar.lower() in RANK:
            common_txt = re.sub(r",?\s*plus les sorts listés ci-dessous.*$", "", common).strip()
            out.append(variant(o, name, rar, f"{base} Sorts de cet instrument : {spells}"
                               + (f" ; ainsi que : {common_txt}." if common_txt else "."),
                               type_precision="instrument de barde"))
        else:
            break
        i += 3
    return out or [o]


def split_horn(o: dict) -> list[dict]:
    base = intro(o["description"], "d100")
    rows = [("argent", "rare", "2d4 + 2", "aucune"), ("airain", "rare", "3d4 + 3", "maîtrise de toutes les armes courantes"),
            ("bronze", "très rare", "4d4 + 4", "maîtrise de toutes les armures intermédiaires"),
            ("fer", "légendaire", "5d4 + 5", "maîtrise de toutes les armes de guerre")]
    return [variant(o, f"Cor du Valhalla ({metal})", rar, f"{base} Ce cor : {n} berserkers ; condition : {cond}.")
            for metal, rar, n, cond in rows]


def split_crystal_ball(o: dict) -> list[dict]:
    desc = o["description"]
    base = intro(desc, "Les variantes")
    out = [variant(o, "Boule de cristal", "très rare", base)]
    for m in re.finditer(r"(Boule de cristal de [^.]+)\.\s*([^\n]+)", desc):
        out.append(variant(o, m.group(1).strip(), "légendaire", f"{base}\n{m.group(2).strip()}"))
    return out


RULES = {
    "Potion de guérison": split_healing, "Potion de force de géant": split_giant_potion,
    "Ceinturon de force de géant": split_giant_belt, "Parchemin de sort": split_scroll,
    "Pierre de Ioun": lambda o: split_paragraph_variants(o, "Pierre de Ioun"),
    "Figurine merveilleuse": lambda o: split_paragraph_variants(o, "Figurine merveilleuse"),
    "Instrument de barde": split_bard_instrument, "Cor du Valhalla": split_horn,
    "Boule de cristal": split_crystal_ball, "Sceptre du gardien des pactes": split_scepter,
}


def split_item(o: dict) -> list[dict]:
    if o.get("palier_de"):
        return [o]
    if "+1, +2 ou +3" in o["nom"]:
        return split_plus(o)
    rule = RULES.get(o["nom"])
    return rule(o) if rule else [o]


def build_index(objs: list[dict]) -> dict:
    idx = {"par_rarete": {}, "par_lien": {"oui": [], "non": []}, "par_type": {}}
    for o in objs:
        idx["par_rarete"].setdefault(o["rarete"], []).append(o["id"])
        idx["par_lien"]["oui" if o["lien"] else "non"].append(o["id"])
        idx["par_type"].setdefault(o["type"], []).append(o["id"])
    return idx


def main(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    before = len(data["objets"])
    objs = []
    for o in data["objets"]:
        objs.extend(split_item(o))
    seen, unique = set(), []
    for o in objs:                                 # identifiants uniques
        oid = o["id"]
        n = 2
        while oid in seen:
            oid = f"{o['id']}-{n}"
            n += 1
        o["id"] = oid
        seen.add(oid)
        unique.append(o)
    data["objets"] = unique
    data["total"] = len(unique)
    data["index"] = build_index(unique)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{before} objets -> {len(unique)} lignes (paliers séparés)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "data" / "objets_magiques.json")
