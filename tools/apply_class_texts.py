#!/usr/bin/env python3
"""
Applique les descriptions enrichies (tools/class_texts/<classe>.py) aux fichiers de progression data/<Classe>.json.

    python tools/apply_class_texts.py            # applique à toutes les classes
    python tools/apply_class_texts.py --check    # vérifie seulement (clés inconnues, aptitudes non couvertes)
    python tools/apply_class_texts.py barbare    # une seule classe

Chaque module de tools/class_texts/ expose :
    CLASSE = "Barbare"                       # nom du fichier data/<CLASSE>.json (sans accent pour Rôdeur : « Rodeur »)
    BASE   = {"Rage": "…", "Attaque supplémentaire@11": "…"}   # « Nom » ou « Nom@niveau » (prioritaire)
    SUB    = {"Voie du Berserker": {"Frénésie": "…"}}
    AUDIT  = [("majeur"|"mineur"|"info", "élément", "constat", "règle officielle"), ...]

Seules les descriptions sont modifiées (niveaux, noms et listes de sorts restent tels quels : les écarts
structurels sont listés dans AUDIT_REGLES.md). Le libellé des améliorations de caractéristiques devient
« Amélioration de caractéristique ou choix d'un don » dans toutes les classes. Le script est idempotent.
"""
from __future__ import annotations

import importlib
import json
import pkgutil
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

ASI_LABEL = "Amélioration de caractéristique ou choix d'un don"
ASI_DESC = ("Augmentez une valeur de caractéristique de 2, ou deux valeurs de caractéristique de 1 (aucune ne peut "
            "dépasser 20 par ce biais). À la place, si la règle optionnelle des dons est utilisée, vous pouvez choisir "
            "un don dont vous remplissez les prérequis (onglet Progression & Dons).")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("’", "'"))
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def is_asi(name: str) -> bool:
    return bool(re.match(r"amelioration de caracteristique", norm(name)))


def modules(only: list[str]):
    import class_texts
    for info in pkgutil.iter_modules(class_texts.__path__):
        if info.name.startswith("_") or (only and info.name not in only):
            continue
        yield importlib.import_module(f"class_texts.{info.name}")


def pick(table: dict, feat: dict):
    return table.get(f"{feat['nom']}@{feat['niveau']}", table.get(feat["nom"]))


def apply(mod, write: bool) -> list[str]:
    path = ROOT / "data" / f"{mod.CLASSE}.json"
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    report = apply_raw(mod, raw)
    if write:
        path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def apply_raw(mod, raw: dict) -> list[str]:
    """Applique les textes au contenu JSON déjà chargé ; renvoie la liste des remarques."""
    cls = raw["classe"]
    report, used = [], set()
    for feat in cls["capacites_classe"]:
        if is_asi(feat["nom"]):
            feat["nom"], feat["description"] = ASI_LABEL, ASI_DESC
            continue
        text = pick(mod.BASE, feat)
        if text:
            feat["description"] = text.strip()
            used.update({feat["nom"], f"{feat['nom']}@{feat['niveau']}"})
        else:
            report.append(f"  base non couverte : L{feat['niveau']} {feat['nom']}")
    for key in mod.BASE:
        if key not in used:
            report.append(f"  clé BASE inconnue : {key}")
    subs = {s["nom"]: s for s in cls["sous_classes"]}
    from francisation import NAME_MIGRATIONS               # anciens noms VF/VO cités par les modules de textes
    subs.update({old: subs[new] for old, new in NAME_MIGRATIONS.items() if new in subs})
    for sname, table in mod.SUB.items():
        if sname not in subs:
            report.append(f"  sous-classe inconnue : {sname}")
            continue
        sused = set()
        for feat in subs[sname]["capacites"]:
            text = pick(table, feat)
            if text:
                feat["description"] = text.strip()
                sused.update({feat["nom"], f"{feat['nom']}@{feat['niveau']}"})
            else:
                report.append(f"  non couverte : {sname} / L{feat['niveau']} {feat['nom']}")
        for key in table:
            if key not in sused:
                report.append(f"  clé inconnue : {sname} / {key}")
    covered = set(mod.SUB) | {NAME_MIGRATIONS.get(n, n) for n in mod.SUB}
    for sname in {s["nom"] for s in cls["sous_classes"]}:
        if sname not in covered:
            report.append(f"  sous-classe sans texte : {sname}")
    return report


def main(argv: list[str]) -> int:
    check = "--check" in argv
    only = [a for a in argv if not a.startswith("--")]
    problems = 0
    for mod in modules(only):
        rep = apply(mod, write=not check)
        problems += len(rep)
        print(f"{mod.CLASSE}: {'OK' if not rep else str(len(rep)) + ' remarque(s)'}")
        for line in rep:
            print(line)
    return 1 if (check and problems) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
