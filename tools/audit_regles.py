#!/usr/bin/env python3
"""
Génère AUDIT_REGLES.md : divergences des données JSON (classes et espèces) par rapport aux règles officielles 5e
(Manuel des joueurs, Guide complet de Xanathar, Chaudron de Tasha, Monstres du Multivers...), en distinguant
les écarts CORRIGÉS (tools/class_fixes, tools/class_texts, tools/race_fixes appliqués par apply_corrections.py)
et les écarts RESTANTS (volontairement non corrigés, avec la raison).

Deux sources :
  1. contrôles automatiques sur data/ (sorts de sous-classe introuvables dans la base de sorts, sources vides,
     niveaux d'amélioration de caractéristique, doublons) ;
  2. relecture manuelle aptitude par aptitude, consignée dans tools/class_texts/<classe>.py et
     tools/race_fixes/<tranche>.py (listes AUDIT = restant, CORRIGE = résolu).

Usage : python tools/audit_regles.py
"""
from __future__ import annotations

import collections
import datetime
import importlib
import json
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]

from core.data_loader import Database  # noqa: E402
from core.rules import is_asi_feature, norm  # noqa: E402

ORDER = {"majeur": 0, "mineur": 1, "info": 2}
ICON = {"majeur": "🔴 majeur", "mineur": "🟠 mineur", "info": "🔵 info"}
ASI_LEVELS = {"Guerrier": [4, 6, 8, 12, 14, 16, 19], "Roublard": [4, 8, 10, 12, 16, 19]}
DISPLAY = {"Rodeur": "Rôdeur"}


def esc(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def auto_checks(db: Database, cls_file: str) -> list[tuple]:
    raw = json.loads((ROOT / "data" / f"{cls_file}.json").read_text(encoding="utf-8-sig"))["classe"]
    name = DISPLAY.get(cls_file, cls_file)
    out = []
    asi = sorted(f["niveau"] for f in raw["capacites_classe"] if is_asi_feature(f["nom"]))
    expected = ASI_LEVELS.get(name, [4, 8, 12, 16, 19])
    if asi != expected:
        out.append(("majeur", "Améliorations de caractéristique", f"niveaux {asi}", f"niveaux {expected}"))
    seen = collections.Counter((f["niveau"], f["nom"]) for f in raw["capacites_classe"])
    for (lvl, fname), n in seen.items():
        if n > 1:
            out.append(("mineur", fname, f"aptitude en double au niveau {lvl}", "une seule entrée"))
    for sub in raw["sous_classes"]:
        if not (sub.get("source") or "").strip():
            out.append(("mineur", sub["nom"], "champ « source » vide", "indiquer l'ouvrage d'origine"))
        missing = [s for s in sub.get("sorts_domaine") or [] if not s.strip().isdigit() and not db.find_spell(s)]
        if missing:
            out.append(("mineur", f"{sub['nom']} / sorts", "sorts introuvables dans la base de sorts : "
                        + ", ".join(missing), "noms français officiels (Magie-0..9.json)"))
    return [(g, e, c, r, "auto") for g, e, c, r in out]


def section(title: str, entries: list[tuple]) -> list[str]:
    entries = sorted(entries, key=lambda x: (ORDER.get(x[0], 9), x[1]))
    lines = [f"### {title} — {len(entries)} point(s)", "",
             "| Gravité | Élément | Constat (données d'origine) | Règle officielle / correction | Origine |",
             "|---|---|---|---|---|"]
    for g, e, c, r, origin in entries:
        lines.append(f"| {ICON.get(g, g)} | {esc(e)} | {esc(c)} | {esc(r)} | {origin} |")
    return lines + [""]


def main() -> None:
    db = Database(ROOT / "data")
    import class_texts
    import race_fixes
    per_class, fixed_class = {}, {}
    for info in pkgutil.iter_modules(class_texts.__path__):
        mod = importlib.import_module(f"class_texts.{info.name}")
        name = DISPLAY.get(mod.CLASSE, mod.CLASSE)
        per_class[name] = auto_checks(db, mod.CLASSE) + [(g, e, c, r, "relecture") for g, e, c, r in mod.AUDIT]
        fixed_class[name] = [(g, e, c, r, "corrigé") for g, e, c, r in getattr(mod, "CORRIGE", [])]
    races, races_fixed = [], []
    for info in pkgutil.iter_modules(race_fixes.__path__):
        mod = importlib.import_module(f"race_fixes.{info.name}")
        races += [(g, e, c, r, "relecture") for g, e, c, r in mod.AUDIT]
        races_fixed += [(g, e, c, r, "corrigé") for g, e, c, r in mod.CORRIGE]

    def counts(entries):
        c = collections.Counter(x[0] for x in entries)
        return c["majeur"], c["mineur"], c["info"]

    remaining = [x for v in per_class.values() for x in v] + races
    fixed = [x for v in fixed_class.values() for x in v] + races_fixed
    md = [
        "# Audit de conformité des données — règles officielles D&D 5e",
        "",
        f"_Généré le {datetime.date.today():%d/%m/%Y} par `tools/audit_regles.py`._",
        "",
        "Périmètre : fichiers de progression des classes (`data/<Classe>.json`) et des espèces (`data/Races.json`, "
        "`data/Bonus_Raciaux.json`), comparés au Manuel des joueurs (PHB), au Guide complet de Xanathar (XGE), "
        "au Chaudron de Tasha (TCE) et, pour les espèces, aux ouvrages indiqués dans leur champ source.",
        "",
        "Les corrections ont été **appliquées aux fichiers JSON** par `python tools/apply_corrections.py` "
        "(idempotent) : noms et niveaux d'aptitudes, aptitudes manquantes, options du Chaudron de Tasha, listes de "
        "sorts de sous-classe, sources, bonus raciaux, langues, traits, vitesses, descriptions chiffrées.",
        "Restent listés ci-dessous les écarts **volontairement non corrigés** (renommer une sous-classe ou une espèce "
        "casserait les fiches sauvegardées, sous-classes officielles scindées, sorts absents de la base…).",
        "",
        "Légende : 🔴 **majeur** = règle fausse qui change le jeu · 🟠 **mineur** = imprécision, nom, faute · "
        "🔵 **info** = remarque.",
        "",
        "## Synthèse",
        "",
        "| Fichier | Corrigés | Restants 🔴 | Restants 🟠 | Restants 🔵 |",
        "|---|---|---|---|---|",
    ]
    for name in sorted(per_class):
        a, b, c = counts(per_class[name])
        md.append(f"| {name} | {len(fixed_class[name])} | {a} | {b} | {c} |")
    a, b, c = counts(races)
    md.append(f"| Espèces | {len(races_fixed)} | {a} | {b} | {c} |")
    tot = counts(remaining)
    md.append(f"| **Total** | **{len(fixed)}** | **{tot[0]}** | **{tot[1]}** | **{tot[2]}** |")
    md += ["", "## Écarts restants", ""]
    for name in sorted(per_class):
        if per_class[name]:
            md += section(name, per_class[name])
    if races:
        md += section("Espèces et sous-races", races)
    md += ["## Journal des corrections appliquées", ""]
    for name in sorted(fixed_class):
        if fixed_class[name]:
            md += section(name + " (corrigé)", fixed_class[name])
    md += section("Espèces (corrigé)", races_fixed)
    (ROOT / "AUDIT_REGLES.md").write_text("\n".join(md), encoding="utf-8")
    print(f"AUDIT_REGLES.md : {len(fixed)} écarts corrigés, {sum(tot)} restants "
          f"({tot[0]} majeurs, {tot[1]} mineurs, {tot[2]} infos)")


if __name__ == "__main__":
    main()
