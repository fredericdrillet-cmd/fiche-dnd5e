"""
Audit automatique des automatismes (v52) : crée des personnages fictifs pour toutes les combinaisons
classe × sous-classe × niveau (1 à 20) × édition (2014, 2024), puis, pour chacun :
  - rafraîchit tous les onglets de l'interface (PyQt6 factice : tests/qt_stub.py) ;
  - lance chaque tuile d'action du tour, fait un début et une fin de tour, une fin de combat, un repos court et un
    repos long ;
  - relève les erreurs (plantages) ;
  - relève les aptitudes débloquées qui ne semblent qu'un texte : à leur niveau, rien de visible ne change sur la
    fiche (valeurs, tuiles, compteurs, choix, rappels) et leur nom n'apparaît pas dans le code du moteur.

    python tools/audit_automatismes.py                  # tout (plusieurs minutes)
    python tools/audit_automatismes.py --classe Moine   # une classe
    python tools/audit_automatismes.py --rapport AUDIT_AUTOMATISMES_v52.md

Le rapport Markdown liste les erreurs (à corriger) puis les aptitudes « texte seul » (à examiner).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import traceback
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
os.environ.setdefault("DND_EAGER_REFRESH", "0")

import qt_stub  # noqa: E402

qt_stub.install()

from core.data_loader import Database  # noqa: E402
from core.engine import Engine  # noqa: E402
from core.rules import norm  # noqa: E402

GENERIC = ("amelioration de caracteristique", "caracteristiques (2024)", "aptitude de sous-classe",
           "capacite de sous-classe", "sous-classe", "incantation", "maitrise des armes", "style de combat",
           "attaque supplementaire", "faveur epique", "don")


def core_source() -> str:
    return norm(" ".join(p.read_text(encoding="utf-8") for p in (ROOT / "core").glob("*.py")))


def build(db, cls, lvl, sub, edition):
    ch = Engine.new_character(db)
    ch.classes = [{"nom": cls, "niveau": lvl, "sous_classe": sub, "pv_jets": []}]
    eng = Engine(db, ch)
    eng.normalize()
    if edition == "2024":
        eng.set_edition_mode("2024")
        eng.normalize()
        ch.classes[0]["sous_classe"] = sub
        eng.normalize()
    return eng


def exercise(win, eng, errors, label):
    """Onglets, tuiles, tour, combat, repos ; chaque erreur est notée avec son contexte."""
    def guard(what, fn, *a):
        try:
            return fn(*a)
        except Exception as exc:                           # noqa: BLE001
            tb = traceback.extract_tb(exc.__traceback__)
            where = next((f"{Path(f.filename).name}:{f.lineno}" for f in reversed(tb)
                          if "/core/" in f.filename or "/ui/" in f.filename), "?")
            errors[(type(exc).__name__, str(exc)[:120], where)].append(f"{label} — {what}")
            return None

    win.engine = eng
    guard("chargement", win.load_character, eng.ch, None)
    eng = win.engine
    for key, _w, _t in win.tab_defs:
        guard("onglet " + key, win._refresh_tab, key)
    tiles = guard("tuiles", eng.turn_actions) or []
    guard("début de tour", eng.start_turn)
    for t in tiles:
        guard("tuile " + t["nom"], eng.use_turn_action, t["id"])
        guard("nouveau round", eng.new_round)
    guard("fin de tour", eng.end_turn)
    guard("fin du combat", eng.end_combat)
    guard("repos court", eng.do_short_rest)
    guard("repos long", eng.do_long_rest)
    guard("onglet combat après repos", win._refresh_tab, "combat")
    return eng


def fingerprint(eng) -> str:
    """Ce qu'une aptitude peut changer de visible sur la fiche, SANS ce qui grandit seul avec le niveau (PV, bonus de
    maîtrise, nombre d'utilisations, chiffres des descriptions) : vitesse, CA, sources d'avantage, maîtrises et
    expertises, tuiles et compteurs (noms), choix, défenses, vision, effets, rappels, attaques par action."""
    def rows(rs):
        return [(r.get("nom", r.get("carac")), r.get("maitrise"), r.get("expertise"), tuple(r.get("avantage", [])),
                 tuple(r.get("desavantage", [])), tuple(r.get("echec", []))) for r in rs]
    parts = []
    for name, fn in (("vitesse", eng.speed), ("ca", lambda: eng.armor_class()[0]),
                     ("init", lambda: (tuple(lab for lab, _ in eng.initiative_detail()["termes"]),
                                       tuple(eng.initiative_detail()["avantage"]))),
                     ("js", lambda: rows(eng.save_rows())), ("comp", lambda: rows(eng.skill_rows())),
                     ("res", lambda: sorted(t["label"] for t in eng.resource_trackers())),
                     ("tuiles", lambda: sorted(t["nom"] for t in eng.turn_actions())),
                     ("choix", lambda: sorted(str(x.get("id", x.get("label", ""))) for x in eng.option_sets())),
                     ("def", eng.defenses), ("vision", lambda: eng.darkvision()["portee"]),
                     ("fx", lambda: sorted(eng.innate_effects())), ("rappels", eng.remember_list),
                     ("attaques", eng.attacks_per_action),
                     ("a_choisir", lambda: sorted(str(m.get("message", m)) for m in eng.missing_choices()
                                                  if "sort" not in norm(str(m.get("message", m))))),
                     ("maitrises", lambda: sorted(eng.armor_proficiencies() + eng.weapon_proficiencies()))):
        try:
            parts.append((name, repr(fn())))
        except Exception as exc:                           # noqa: BLE001
            parts.append((name, "erreur " + type(exc).__name__))
    return repr(parts)


def new_features(eng, lvl) -> list[tuple[str, int, str]]:
    out = []
    for e in eng.ch.classes:
        for f in eng.features(e):
            if f.get("debloque") and int(f.get("niveau", 0)) == lvl:
                n = norm(f["nom"])
                if n and not any(n.startswith(g) for g in GENERIC):
                    out.append((e["nom"], lvl, f["nom"]))
    return out


def text_only(eng, prev_fp, source) -> list[tuple[str, int, str]]:
    """Aptitudes débloquées à ce niveau alors que rien de visible ne change par rapport au niveau précédent, et
    dont le nom n'apparaît pas dans le moteur."""
    lvl = eng.ch.classes[0]["niveau"]
    if prev_fp is None or fingerprint(eng) != prev_fp:
        return []
    return [x for x in new_features(eng, lvl) if re.sub(r"\s*\(.*?\)", "", norm(x[2])).strip() not in source]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--classe", default="")
    ap.add_argument("--edition", default="")
    ap.add_argument("--niveaux", default="1-20")
    ap.add_argument("--rapport", default="")
    ap.add_argument("--json", default="", help="résultats bruts (pour fusionner des audits lancés en parallèle)")
    ap.add_argument("--fusion", nargs="*", default=[], help="fichiers --json à fusionner en un seul rapport")
    args = ap.parse_args()
    if args.fusion:
        return merge(args.fusion, args.rapport)
    lo, hi = (int(x) for x in args.niveaux.split("-"))
    db = Database(ROOT / "data")
    from ui.main_window import MainWindow
    win = MainWindow(db)
    source = core_source()
    errors = defaultdict(list)
    texts = defaultdict(set)                               # (édition, classe, sous-classe ou "") -> {(niv, nom)}
    count = 0
    for edition in ([args.edition] if args.edition else ["2014", "2024"]):
        probe = build(db, "Guerrier", 1, "", edition)
        classes = [c for c in probe.db.classes if not args.classe or c == args.classe]
        for cls in classes:
            subs = [s["nom"] for s in probe.db.classes[cls].get("sous_classes", [])]
            sub_lvl = probe.subclass_level(cls)
            for lvl in range(lo, hi + 1):
                for sub in (subs if lvl >= sub_lvl and subs else [""]):
                    label = f"{edition} {cls} {lvl}" + (f" ({sub})" if sub else "")
                    try:
                        eng = build(db, cls, lvl, sub, edition)
                    except Exception as exc:               # noqa: BLE001
                        errors[(type(exc).__name__, str(exc)[:120], "création")].append(label)
                        continue
                    eng = exercise(win, eng, errors, label)
                    count += 1
                    try:
                        prev = build(db, cls, lvl - 1, sub, edition) if lvl > 1 else None
                        fresh = build(db, cls, lvl, sub, edition)
                        for c, niv, nom in text_only(fresh, fingerprint(prev) if prev else None, source):
                            texts[(edition, c, sub if niv >= sub_lvl else "")].add((niv, nom))
                    except Exception as exc:               # noqa: BLE001
                        errors[(type(exc).__name__, str(exc)[:120], "analyse")].append(label)
    if args.json:
        import json
        Path(args.json).write_text(json.dumps({
            "count": count, "niveaux": [lo, hi],
            "errors": [[list(k), v] for k, v in errors.items()],
            "texts": [[list(k), sorted(v)] for k, v in texts.items()]}, ensure_ascii=False), encoding="utf-8")
    return write_report(count, lo, hi, errors, texts, args.rapport)


def merge(files, rapport) -> int:
    import json
    count, errors, texts, lo, hi = 0, defaultdict(list), defaultdict(set), 1, 20
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        count += d["count"]
        lo, hi = d["niveaux"]
        for k, v in d["errors"]:
            errors[tuple(k)] += v
        for k, v in d["texts"]:
            texts[tuple(k)] |= {tuple(x) for x in v}
    return write_report(count, lo, hi, errors, texts, rapport)


def write_report(count, lo, hi, errors, texts, rapport) -> int:
    lines = ["# Audit des automatismes — v52", "",
             f"{count} personnages fictifs testés (classes × sous-classes × niveaux {lo}–{hi} × éditions).", "",
             f"## Erreurs ({len(errors)})", ""]
    if not errors:
        lines.append("Aucune erreur.")
    for (kind, msg, where), cases in sorted(errors.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"- **{kind}** `{where}` — {msg} — {len(cases)} cas, ex. : {'; '.join(cases[:3])}")
    total = sum(len(v) for v in texts.values())
    lines += ["", f"## Aptitudes en « texte seul » ({total})", "",
              "Aptitudes débloquées à un niveau où rien de visible ne change sur la fiche (valeurs, tuiles, "
              "compteurs, choix, rappels) et dont le nom n'apparaît pas dans le moteur : à examiner (beaucoup sont "
              "purement narratives ou de roleplay). Une aptitude débloquée au même niveau qu'une autre qui, elle, "
              "change la fiche n'est pas listée.", ""]
    for (edition, cls, sub), items in sorted(texts.items()):
        lines.append(f"- **{edition} — {cls}{' — ' + sub if sub else ''}** : " +
                     ", ".join(f"{nom} (niv. {niv})" for niv, nom in sorted(items)))
    report = "\n".join(lines) + "\n"
    if rapport:
        Path(rapport).write_text(report, encoding="utf-8")
    print(report[:4000])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
