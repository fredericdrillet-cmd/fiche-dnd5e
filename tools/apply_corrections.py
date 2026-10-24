#!/usr/bin/env python3
"""
Applique les corrections de règles issues de l'audit (AUDIT_REGLES.md) aux fichiers de données.

Ordre d'application (idempotent, relançable sans risque) :
  1. tools/class_fixes/<classe>.py  -> corrections structurelles des classes (noms, niveaux, aptitudes manquantes,
                                       listes de sorts de sous-classe, sources) ;
  2. tools/class_texts/<classe>.py  -> descriptions enrichies (voir apply_class_texts.py) ;
  3. tools/race_fixes/*.py          -> corrections des espèces (bonus, langues, traits, vitesses).

    python tools/apply_corrections.py           # applique tout
    python tools/apply_corrections.py --check   # simule et signale les opérations impossibles

Opérations de classe (FIXES) — « sous_classe » vaut None pour la classe de base :
    {"op": "rename", "sous_classe", "nom", "nouveau"}           renomme une aptitude (garde niveau et texte)
    {"op": "niveau", "sous_classe", "nom", "niveau"}            change le niveau d'obtention
    {"op": "add",    "sous_classe", "nom", "niveau"}            ajoute une aptitude (texte fourni par class_texts)
    {"op": "remove", "sous_classe", "nom"}                      supprime une aptitude inventée / en double
    {"op": "sorts",  "sous_classe", "sorts": [...]}             remplace la liste de sorts de sous-classe
    {"op": "source", "sous_classe", "source"}                   corrige la source
    {"op": "champ",  "sous_classe", "champ", "valeur"}          ajoute / remplace un champ de la sous-classe
                                                                (ex. « terrains » du Cercle de la Terre)
Opérations d'espèce (FIXES) :
    {"op": "set", "espece", "champ": "caracteristiques"|"langues"|"source", "valeur"}
    {"op": "trait", "espece", "nom", "description"}             ajoute ou remplace un trait
    {"op": "rename_trait", "espece", "nom", "nouveau"}
    {"op": "remove_trait", "espece", "nom"}
    {"op": "vitesse", "espece", "valeur": mètres}               data/Bonus_Raciaux.json (« vitesses »)
    {"op": "remove_espece", "espece"}                            retire une espèce (et sa vitesse)
    {"op": "add_espece", "espece", "entree": {...}}              ajoute / remplace une espèce complète
                                                                (« sous_races » : sous-espèces avec bonus et traits)
"""
from __future__ import annotations

import importlib
import json
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]

import apply_class_texts  # noqa: E402

DATA = ROOT / "data"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def iter_modules(package: str):
    pkg = importlib.import_module(package)
    for info in pkgutil.iter_modules(pkg.__path__):
        if not info.name.startswith("_"):
            yield importlib.import_module(f"{package}.{info.name}")


# ------------------------------------------------------------------------------------------------------- classes
def _fr(name):
    """Nom de sous-classe après francisation (les modules de correction citent parfois l'ancien nom VF/VO)."""
    from francisation import NAME_MIGRATIONS
    return NAME_MIGRATIONS.get(name, name) if isinstance(name, str) else name


def _features(cls: dict, sub_name):
    sub_name = _fr(sub_name)
    if sub_name is None:
        return cls["capacites_classe"]
    for s in cls["sous_classes"]:
        if s["nom"] == sub_name:
            return s["capacites"]
    return None


def _sub(cls: dict, sub_name):
    sub_name = _fr(sub_name)
    return next((s for s in cls["sous_classes"] if s["nom"] == sub_name), None)


def apply_class_fix(cls: dict, op: dict) -> str:
    """Applique une opération ; renvoie '' si OK / déjà appliquée, sinon un message d'erreur."""
    kind, sub = op["op"], op.get("sous_classe")
    if kind in ("sorts", "source", "champ"):
        s = _sub(cls, sub)
        if s is None:
            return f"sous-classe inconnue : {sub}"
        if kind == "sorts":
            s["sorts_domaine"] = list(op["sorts"])
        elif kind == "champ":
            s[op["champ"]] = op["valeur"]
        else:
            s["source"] = op["source"]
        return ""
    feats = _features(cls, sub)
    if feats is None:
        return f"sous-classe inconnue : {sub}"
    by_name = [f for f in feats if f["nom"] == op["nom"]]
    if kind == "rename":
        if not by_name:
            return "" if any(f["nom"] == op["nouveau"] for f in feats) else f"aptitude introuvable : {op['nom']}"
        for f in by_name:
            f["nom"] = op["nouveau"]
    elif kind == "niveau":
        if not by_name:
            return f"aptitude introuvable : {op['nom']}"
        for f in by_name:
            f["niveau"] = int(op["niveau"])
    elif kind == "add":
        if not by_name:
            feats.append({"niveau": int(op["niveau"]), "nom": op["nom"], "description": op.get("description", "")})
    elif kind == "remove":
        feats[:] = [f for f in feats if f["nom"] != op["nom"]]
    else:
        return f"opération inconnue : {kind}"
    feats.sort(key=lambda f: f["niveau"])            # tri stable : l'ordre d'origine est conservé par niveau
    return ""


def apply_classes(write: bool) -> list[str]:
    report = []
    for mod in iter_modules("class_fixes"):
        path = DATA / f"{mod.CLASSE}.json"
        raw = load(path)
        for op in mod.FIXES:
            err = apply_class_fix(raw["classe"], op)
            if err:
                report.append(f"{mod.CLASSE} : {err}  ({op})")
        if write:
            save(path, raw)
    return report


# ------------------------------------------------------------------------------------------------------- espèces
def apply_races(write: bool) -> list[str]:
    report = []
    races_path, bonus_path = DATA / "Races.json", DATA / "Bonus_Raciaux.json"
    races, bonus = load(races_path), load(bonus_path)
    index = {e["nom"]: e for e in races["especes"]}
    modules = list(iter_modules("race_fixes"))
    removed = {op["espece"] for mod in modules for op in mod.FIXES if op["op"] == "remove_espece"}
    for mod in modules:
        for op in mod.FIXES:
            kind, name = op["op"], op["espece"]
            if name in removed and kind != "remove_espece":
                continue                                      # espèce retirée : ses anciennes corrections sont sans objet
            if kind == "remove_espece":                       # retrait définitif (doublons, espèces écartées)
                races["especes"] = [x for x in races["especes"] if x["nom"] != name]
                index.pop(name, None)
                bonus.get("vitesses", {}).pop(name, None)
                continue
            if kind == "add_espece":                          # ajout / remplacement complet d'une espèce
                entry = dict(op["entree"])
                races["especes"] = [x for x in races["especes"] if x["nom"] != name] + [entry]
                index[name] = entry
                continue
            if kind == "vitesse":
                bonus.setdefault("vitesses", {})[name] = float(op["valeur"])
                continue
            e = index.get(name)
            if e is None:
                report.append(f"espèce inconnue : {name}  ({kind})")
                continue
            caps = e.setdefault("capacites", [])
            match = [c for c in caps if c["nom"] == op.get("nom")]
            if kind == "set":
                e[op["champ"]] = op["valeur"]
            elif kind == "trait":
                if match:
                    match[0]["description"] = op["description"]
                else:
                    caps.append({"nom": op["nom"], "description": op["description"]})
            elif kind == "rename_trait":
                if match:
                    match[0]["nom"] = op["nouveau"]
                elif not any(c["nom"] == op["nouveau"] for c in caps):
                    report.append(f"{name} : trait introuvable {op['nom']}")
            elif kind == "remove_trait":
                e["capacites"] = [c for c in caps if c["nom"] != op["nom"]]
            else:
                report.append(f"opération inconnue : {kind}")
    if write:
        save(races_path, races)
        save(bonus_path, bonus)
    return report


def main(argv: list[str]) -> int:
    write = "--check" not in argv
    report = apply_classes(write)
    for mod in apply_class_texts.modules([]):
        if write:
            report += [f"{mod.CLASSE} (textes) :{x}" for x in apply_class_texts.apply(mod, write=True)]
    report += apply_races(write)
    import francisation                                # 4. francisation (doublons VO retirés), idempotente
    francisation.apply(write=write)
    if write:                                          # 5. montures (v36), idempotent
        import add_mounts
        add_mounts.apply()
        import invocation_fixes                        # 6. manifestations occultes auditées (v37)
        invocation_fixes.apply()
        import spell_rules                             # 7. règles chiffrées des sorts (v37)
        spell_rules.apply()
        import maneuver_fixes                          # 8. manœuvres (Tasha) du Maître de guerre (v39)
        maneuver_fixes.apply()
    for line in report:
        print(line)
    print("Corrections appliquées." if write and not report else f"{len(report)} remarque(s).")
    return 1 if report else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
