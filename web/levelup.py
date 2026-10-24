"""
Assistant de montée de niveau — version web de ui/levelup_dialog.py, sur la logique pure de core/levelup.py.

Le serveur étant sans état, l'assistant est « rejoué » à chaque requête :
  personnage d'origine + classe choisie + liste des choix faits dans l'assistant
  -> copie de travail `sim = eng.simulate_level_up(classe)` -> choix réappliqués dans l'ordre -> rapport.
Rien ne touche la fiche tant que `confirm` n'est pas demandé (exactement comme « Confirmer » dans le bureau) :
la copie devient alors le personnage.
"""
from __future__ import annotations

from core import rules as R
from core.data_loader import PACTS
from core.levelup import roadmap_icons
from core.rules import ABILITIES

from .service import ActionError, build_sheet, load_character

ASI_MODES = ("aucun", "plus2", "plus1x2", "don")
TAB_LABELS = {"classes": "Perso › Classes", "race": "Carac › Langues", "caracteristiques": "Carac",
              "progression": "Carac › Améliorations", "combat": "Combat", "magie": "Magie"}


# ------------------------------------------------------------------------------------------------ choix rejoués
def _apply(eng, sim, cls: str, op: dict, state: dict) -> None:
    kind = op.get("op")
    if kind == "sub":                                    # ui : _set_sub
        entry = sim.ch.find_class(cls)
        name = op.get("name", "")
        if name and not sim.db.subclass(cls, name):
            raise ActionError("Sous-classe inconnue.")
        entry["sous_classe"] = name
        entry["_wizard_sub"] = True                      # garde le sélecteur visible jusqu'à la confirmation
    elif kind == "asi":                                  # ui : _set_asi
        slot = op.get("slot", "")
        if slot not in {s["id"] for s in sim.asi_slots()}:
            raise ActionError("Emplacement d'amélioration inconnu.")
        mode = op.get("mode", "aucun")
        if mode not in ASI_MODES:
            raise ActionError("Choix inconnu.")
        choice = {"mode": mode}
        if op.get("a1") in ABILITIES:
            choice["a1"] = op["a1"]
        if mode == "plus1x2" and op.get("a2") in ABILITIES and op["a2"] != choice.get("a1"):
            choice["a2"] = op["a2"]                      # deux caractéristiques DIFFÉRENTES
        if mode == "don" and op.get("don") in sim.db.feats:
            choice["don"] = op["don"]
            if op.get("don_carac"):
                choice["don_carac"] = op["don_carac"]
        sim.ch.ameliorations[slot] = choice
    elif kind == "style":                                # ui : _set_style
        slot, name = op.get("slot", ""), op.get("name", "")
        if not name:
            sim.ch.styles_combat.pop(slot, None)
        elif name in sim.style_options(slot):
            sim.ch.styles_combat[slot] = name
        else:
            raise ActionError("Style non disponible.")
    elif kind == "pact":                                 # ui : _set_pact
        name = op.get("name", "")
        if name and name not in PACTS:
            raise ActionError("Pacte inconnu.")
        sim.ch.pacte = name
    elif kind == "invocation":                           # ui : _set_invocation
        base = list(eng.ch.manifestations)
        added = [x for x in sim.ch.manifestations if x not in base]
        index = max(0, min(20, int(op.get("index", 0))))
        while len(added) <= index:
            added.append("")
        name = op.get("name", "")
        if name and name not in sim.db.manifestations:
            raise ActionError("Manifestation inconnue.")
        added[index] = name
        seen: list[str] = []
        for x in added:
            if x and x not in seen:
                seen.append(x)
        sim.ch.manifestations = base + seen
    elif kind == "learn":                                # ui : _learn
        c, name = op.get("cls", ""), op.get("name", "")
        if not eng.level_learn_spell(sim, c, name):
            raise ActionError(f"« {name} » ne peut pas être appris maintenant (quota atteint ou sort hors liste).")
        state.setdefault(c, []).append(name)
    elif kind == "unlearn":                              # ui : _unlearn (seulement les sorts appris ici)
        c, name = op.get("cls", ""), op.get("name", "")
        if name in state.get(c, []):
            state[c].remove(name)
            sim.ch.sorts[c] = [s for s in sim.ch.sorts.get(c, []) if s["nom"] != name]
    elif kind == "prepare":                              # ui : _on_prepare_item
        c, name, on = op.get("cls", ""), op.get("name", ""), bool(op.get("on"))
        if not eng.level_set_prepared(sim, c, name, on) and on:
            raise ActionError(f"Limite de sorts préparés atteinte pour {c}.")
    elif kind == "swap_forget":
        c, name = op.get("cls", ""), op.get("name", "")
        ok = eng.level_swap_forget(sim, c, name) if name else eng.level_swap_cancel(sim, c)
        if name and not ok:
            raise ActionError("Ce sort ne peut pas être oublié.")
    elif kind == "swap_choose":
        if not eng.level_swap_choose(sim, op.get("cls", ""), op.get("name", "")):
            raise ActionError("Remplaçant non valide.")
    elif kind == "swap_cancel":
        eng.level_swap_cancel(sim, op.get("cls", ""))
    else:
        raise ActionError("Choix inconnu.")
    sim.normalize()


def _replay(data: dict, cls: str, ops: list[dict]):
    eng, ch = load_character(data)
    options = eng.level_up_options()
    if not options:
        raise ActionError("Niveau 20 atteint : plus de montée de niveau possible.")
    names = [o["classe"] for o in options]
    if cls not in names:
        cls = names[0]
    sim = eng.simulate_level_up(cls)
    state: dict[str, list[str]] = {}
    errors: list[str] = []
    for i, op in enumerate(ops or []):
        if not isinstance(op, dict):
            continue
        try:
            _apply(eng, sim, cls, op, state)
        except ActionError as exc:
            if i == len(ops) - 1:                        # seule l'erreur du DERNIER choix intéresse l'utilisateur
                errors.append(str(exc))
        except (TypeError, ValueError, KeyError):
            if i == len(ops) - 1:
                errors.append("Choix invalide.")
    sim.normalize()
    return eng, sim, cls, options, state, errors


# ------------------------------------------------------------------------------------------------ vue
def _spell_brief(sp: dict) -> dict:
    return {"nom": sp["nom"], "niveau": int(sp.get("niveau") or 0), "ecole": sp.get("ecole", ""),
            "concentration": bool(sp.get("concentration")), "rituel": bool(sp.get("rituel")),
            "description": sp.get("description", "")}


def _spell_classes(eng, sim, cls: str, pending: list[dict]) -> list[str]:
    out = []
    for e in sim.ch.classes:
        plan = eng.level_spell_plan(sim, e["nom"])
        if plan and (e["nom"] == cls or any(m.get("kind") == "sorts" and m["message"].startswith(e["nom"])
                                            for m in pending)):
            out.append(e["nom"])
    return out


def wizard(data: dict, cls: str = "", ops: list[dict] | None = None, confirm: bool = False) -> dict:
    eng, sim, cls, options, state, errors = _replay(data, cls, ops or [])
    report = eng.level_up_report(sim, cls)
    pending = report["dans_assistant"]
    entry = sim.ch.find_class(cls)

    if confirm:
        if pending:
            raise ActionError("Choix manquants : " + " ; ".join(m["message"] for m in pending))
        for e in sim.ch.classes:
            e.pop("_wizard_sub", None)
        sim.__dict__.pop("_level_swaps", None)
        sim.normalize()
        note = [m["message"] for m in sim.missing_choices()]
        msg = "{} : niveau {} atteint (niveau global {}).".format(cls, entry["niveau"], sim.total_level)
        return {"character": sim.ch.to_dict(), "sheet": build_sheet(sim), "errors": [], "rolls": [],
                "messages": [msg] + (["À faire ensuite : " + " ; ".join(note)] if note else [])}

    kinds = {m["kind"] for m in pending}
    opt = next(o for o in options if o["classe"] == cls)

    # ---- choix de l'étape 4
    choices: dict = {}
    if "sous_classe" in kinds or (entry.get("sous_classe") and entry.get("_wizard_sub")):
        choices["sous_classe"] = {"options": [s["nom"] for s in sim.db.subclasses(cls)],
                                  "choix": entry.get("sous_classe", "")}
    old_asi = {s["id"] for s in eng.asi_slots()}
    asi = []
    for s in sim.asi_slots():
        if s["id"] in old_asi:
            continue
        c = sim.ch.ameliorations.get(s["id"], {"mode": "aucun"})
        st = list(sim.feat_status(c["don"])) if c.get("mode") == "don" and c.get("don") else None
        asi.append({**s, "choix": c, "etat": st})
    choices["asi"] = asi
    old_styles = {s["id"] for s in eng.fighting_style_slots() if s["debloque"]}
    styles = []
    for s in sim.fighting_style_slots():
        if s["debloque"] and s["id"] not in old_styles and s.get("classe", cls) in (cls, ""):
            styles.append({**s, "choix": sim.ch.styles_combat.get(s["id"], ""),
                           "options": [{"nom": n, "description": sim.db.styles_by_class.get(s["classe"], {}).get(n)
                                        or sim.db.armor_models.get(n, "")} for n in sim.style_options(s["id"])]})
    choices["styles"] = styles
    warlock = cls == "Occultiste"
    if warlock and ("pacte" in kinds or (sim.ch.pacte and eng.class_level("Occultiste") < 3
                                         <= sim.class_level("Occultiste"))):
        choices["pacte"] = {"options": list(PACTS), "choix": sim.ch.pacte,
                            "descriptions": {k: (v.get("description", "") if isinstance(v, dict) else str(v))
                                             for k, v in PACTS.items()} if isinstance(PACTS, dict) else {}}
    if warlock:
        base = list(eng.ch.manifestations)
        n = max(0, sim.manifestation_slots()["total"] - len(base))
        if n:
            added = [x for x in sim.ch.manifestations if x not in base]
            opts = [m["nom"] for m in eng.level_invocation_options(sim)]
            pool = sorted(set(opts + added))
            choices["manifestations"] = {
                "nombre": n, "choisies": added, "connues": len(sim.ch.manifestations),
                "total": sim.manifestation_slots()["total"],
                "options": [{"nom": nm, "description": sim.db.manifestations.get(nm, {}).get("description", ""),
                             "sorts": "; ".join("{} ({})".format(g["sort"], g["usage"])
                                                for g in sim.db.manifestations.get(nm, {}).get("sorts", []))}
                            for nm in pool]}

    # ---- étape 5 : sorts
    spells = []
    for c in _spell_classes(eng, sim, cls, pending):
        plan = eng.level_spell_plan(sim, c)
        prep = eng.level_prepare_info(sim, c)
        flags = {x["nom"]: bool(x.get("prepare")) for x in sim.ch.sorts.get(c, [])}
        mine = []
        for x in sim.ch.sorts.get(c, []):
            sp = sim.db.find_spell(x["nom"]) or {"nom": x["nom"], "niveau": 1}
            mine.append({**_spell_brief(sp), "prepare": flags.get(x["nom"], True),
                         "nouveau": x["nom"] in state.get(c, []), "accorde": bool(x.get("accorde"))})
        mine.sort(key=lambda s: (s["niveau"], R.norm(s["nom"])))
        quota = plan["connus"] or plan["grimoire"] or plan["prepares"]
        block = {"classe": c, "niveau_max": plan["niveau_max"], "mode": plan["mode"],
                 "mineurs": list(plan["mineurs"]), "gain_mineurs": plan["gain_mineurs"],
                 "quota": list(quota) if quota else None, "gain_sorts": plan["gain_sorts"],
                 "quota_label": "Sorts connus" if plan["connus"] else "Grimoire" if plan["grimoire"] else
                 "Sorts préparés", "liste_complete": eng.prepares_from_list(plan),
                 "prepares": prep, "options": [_spell_brief(sp) for sp in eng.level_spell_options(sim, c)],
                 "mes_sorts": mine, "echange": None}
        if c == cls and eng.level_swap_allowed(sim, c):
            st = eng.level_swap_state(sim, c)
            cands = [_spell_brief(sp) for sp in eng.level_swap_candidates(sim, c)]
            block["echange"] = {"regle": eng.level_swap_rule(sim, c), "etat": st, "candidats": cands,
                                "options": [_spell_brief(sp) for sp in eng.level_swap_options(sim, c)]}
        spells.append(block)

    road = sim.class_roadmap(entry)
    nxt = next((col for col in road if col["niveau"] > entry["niveau"] and roadmap_icons(col)), None)
    hp = sim.level_hp_info(cls)
    return {
        "classe": cls, "options": options, "titre": "{} {} → {}".format(cls, opt["avant"] or "—", opt["apres"]),
        "prerequis": opt["prerequis"],
        "niveau_global": [eng.total_level, sim.total_level],
        "pv": {**hp, "avant": eng.hp_max(), "apres": sim.hp_max()},
        "aptitudes": [{k: f.get(k) for k in ("nom", "niveau", "description", "source", "sous_classe")}
                      for f in report["aptitudes"]],
        "prochain": {"niveau": nxt["niveau"], "icones": roadmap_icons(nxt),
                     "texte": ", ".join(nxt["aptitudes"]) or "amélioration ou don"} if nxt else None,
        "choix": choices, "sorts": spells,
        "manquants": [{"message": m["message"], "kind": m["kind"]} for m in pending],
        "ensuite": [{"message": m["message"], "onglet": TAB_LABELS.get(m["onglet"], m["onglet"])}
                    for m in report["ensuite"]],
        "recap": [list(r) for r in report["recap"]],
        "pret": not pending, "errors": errors,
    }
