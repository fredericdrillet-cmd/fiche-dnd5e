"""
Ménagerie : familiers, compagnons de classe et invocations (data/Familiers_Invocations.json) — logique pure.

    - formules de mise à l'échelle (« 14 + BM », « 5 + (5 * class_level) », « 1d8 + 4 + spell_level »…)
      évaluées de façon sûre (aucun eval Python : petit interpréteur d'expressions) ;
    - fiche calculée d'une entité : CA, PV max, vitesses, caractéristiques, sauvegardes, compétences, attaques
      (bonus au toucher, dégâts, DD) ajustées au bonus de maîtrise, au niveau de classe, à la caractéristique
      d'incantation du personnage ou au niveau du sort de convocation ;
    - inclusion automatique (Esprit du feu sauvage du Cercle des Fournaises) et conseils contextuels
      (Maître des bêtes, Forgeur d'armes, Artilleur, Lame maudite, Pacte de la chaîne).
"""
from __future__ import annotations

import ast
import math
import operator
import re
import uuid
from typing import Optional

from . import dice as D
from . import rules as R
from .rules import norm

TYPE_LABELS = {"familiar": "Familiers", "class_companion": "Compagnons de classe", "summons": "Invocations",
               "mount": "Montures"}
AB_KEYS = {"str": "Force", "dex": "Dextérité", "con": "Constitution", "int": "Intelligence", "wis": "Sagesse",
           "cha": "Charisme"}
SPEED_LABELS = {"walk": "Marche", "fly": "Vol", "swim": "Nage", "climb": "Escalade", "burrow": "Creusement",
                "hover": "Vol stationnaire"}
SIZE_LABELS = {"TP": "Très petite", "P": "Petite", "M": "Moyenne", "G": "Grande", "TG": "Très grande",
               "Gig": "Gigantesque"}
STATUSES = ["Actif", "Congédié", "À 0 PV", "Inconscient"]

# ------------------------------------------------------------------------------------------------ formules
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {"floor": math.floor, "ceil": math.ceil, "max": max, "min": min}


def _eval_node(node, ctx: dict):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, ctx)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in ctx:
            return ctx[node.id]
        raise ValueError(node.id)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left, ctx), _eval_node(node.right, ctx))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand, ctx))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return _FUNCS[node.func.id](*[_eval_node(a, ctx) for a in node.args])
    raise ValueError("expression non autorisée")


def eval_formula(expr, ctx: dict) -> Optional[int]:
    """« 14 + BM » -> 16 ; None si la formule n'est pas calculable (texte libre, dés…)."""
    if expr is None:
        return None
    if isinstance(expr, (int, float)):
        return int(expr)
    text = str(expr).strip()
    for candidate in (text, re.sub(r"\s+\([^()]*\)\s*$", "", text)):   # 2e essai sans note finale « (Lien primal) »
        try:
            return int(math.floor(_eval_node(ast.parse(candidate, mode="eval"), ctx)))
        except (ValueError, SyntaxError, TypeError, ZeroDivisionError, KeyError):
            continue
    return None


_DICE = re.compile(r"(\d*)d(\d+)")


def eval_dice(expr: str, ctx: dict) -> tuple[str, int, str]:
    """« 1d8 + 4 + spell_level (+1d6 force) » -> ('1d8', 4 + niveau, '+1d6 force') : dés, bonus fixe, note."""
    text = str(expr or "")
    note = ""
    m = re.search(r"\s+\(([^()]*)\)\s*$", text)       # « (+1d6 force) » : dégâts annexes, gardés en note
    if m:
        words = re.findall(r"[A-Za-zÀ-ÿ_]+", m.group(1))
        if _DICE.search(m.group(1)) or any(w not in ctx and w not in _FUNCS for w in words):
            note, text = m.group(1).strip(), text[:m.start()]
    dice = [x.group(0) for x in _DICE.finditer(text)]
    flat_expr = _DICE.sub("0", text).strip() or "0"
    flat = eval_formula(flat_expr, ctx)
    return "+".join(dice), (flat or 0), note


def split_damage(text: str) -> tuple[str, int]:
    """« 1d6+2 » -> ('1d6', 2) ; « 1 » -> ('', 1)."""
    groups, flat = D.parse_damage(text or "")
    dice = "+".join("{}d{}".format(n, s) if sign > 0 else "-{}d{}".format(n, s) for sign, n, s in groups)
    return dice, flat


def join_damage(dice: str, flat: int) -> str:
    if not dice:
        return str(max(0, flat))
    return dice + ("{:+d}".format(flat) if flat else "")


# ------------------------------------------------------------------------------------------------ moteur
class CompanionsMixin:
    """Mélangé à Engine : ménagerie du personnage (ch.menagerie) et fiches calculées des entités."""

    # ---------------------------------------------------------------- catalogue
    def entity(self, entity_id: str) -> Optional[dict]:
        return getattr(self.db, "entities", {}).get(entity_id)

    def entities_of_type(self, entity_type: str) -> list[dict]:
        return sorted((e for e in getattr(self.db, "entities", {}).values() if e["entity_type"] == entity_type),
                      key=lambda e: norm(e["name"]))

    # ---------------------------------------------------------------- ménagerie
    def menagerie_add(self, entity_id: str, name: str = "", auto: bool = False) -> Optional[dict]:
        ent = self.entity(entity_id)
        if ent is None:
            return None
        inst = {"uid": uuid.uuid4().hex[:10], "id": entity_id, "nom": name or ent["name"], "pv": None,
                "pv_temp": 0, "statut": "Actif", "niveau_sort": None, "auto": bool(auto)}
        scaling = ent.get("scaling") or {}
        if scaling.get("spell_level_min"):
            inst["niveau_sort"] = int(scaling["spell_level_min"])
        self.ch.menagerie.append(inst)
        inst["pv"] = self.entity_sheet(inst)["pv_max"]
        return inst

    def menagerie_remove(self, uid: str) -> None:
        self.ch.menagerie = [m for m in self.ch.menagerie if m.get("uid") != uid]

    def menagerie_get(self, uid: str) -> Optional[dict]:
        return next((m for m in self.ch.menagerie if m.get("uid") == uid), None)

    def menagerie_sync(self) -> None:
        """Inclusion automatique (Esprit du feu sauvage) ; retrait des entrées automatiques devenues caduques
        (changement de classe / sous-classe). Entrées inconnues du fichier JSON : retirées."""
        ents = getattr(self.db, "entities", {})
        if not ents:
            return
        self.ch.menagerie = [m for m in self.ch.menagerie if m.get("id") in ents]
        wanted = {eid for eid, ok in self.auto_entities().items() if ok}
        self.ch.menagerie = [m for m in self.ch.menagerie if not m.get("auto") or m["id"] in wanted]
        have = {m["id"] for m in self.ch.menagerie}
        for eid in wanted - have:
            self.menagerie_add(eid, auto=True)

    def auto_entities(self) -> dict[str, bool]:
        """Entités ajoutées d'office : {id: condition remplie}."""
        druid = self.ch.find_class("Druide")
        wildfire = bool(druid and druid["niveau"] >= 2 and "fournaise" in norm(druid.get("sous_classe", "")))
        return {"esprit_feu_sauvage": wildfire}

    def companion_hints(self) -> list[dict]:
        """Conseils contextuels : [{niveau: 'warning'|'info', texte, recommandes: [ids]}]."""
        out = []
        have = {m["id"] for m in self.ch.menagerie}

        def sub_of(cls: str) -> tuple[int, str]:
            e = self.ch.find_class(cls)
            return (e["niveau"], norm(e.get("sous_classe", ""))) if e else (0, "")

        rules = []
        lvl, sub = sub_of("Rôdeur")
        if lvl >= 3 and "maitre des betes" in sub:
            rules.append(("Rôdeur (Maître des bêtes)", ["esprit_terre", "esprit_mer", "esprit_ciel"]))
        if lvl >= 3 and "drake" in sub:
            rules.append(("Rôdeur (Gardien des drakes)", ["compagnon_drake"]))
        lvl, sub = sub_of("Artificier")
        if lvl >= 3 and "forgeur d'armes" in sub:
            rules.append(("Artificier (Forgeur d'armes)", ["defenseur_acier"]))
        if lvl >= 3 and "artilleur" in sub:
            rules.append(("Artificier (Artilleur)", ["canon_occulte"]))
        lvl, sub = sub_of("Occultiste")
        if lvl >= 6 and "lame maudite" in sub:
            rules.append(("Occultiste (La Lame maudite, niveau 6)", ["spectre_maudit"]))
        for label, ids in rules:
            ids = [i for i in ids if self.entity(i)]
            if ids and not have & set(ids):
                out.append({"niveau": "warning", "recommandes": ids,
                            "texte": "{} : votre classe / sous-classe vous permet de lier un compagnon spécifique. "
                                     "Veuillez le sélectionner parmi les compagnons recommandés : {}.".format(
                                         label, ", ".join(self.entity(i)["name"] for i in ids))})
        lvl, sub = sub_of("Guerrier")
        mounts = [e["id"] for e in getattr(self.db, "entities", {}).values() if e.get("entity_type") == "mount"]
        if lvl >= 3 and "cavalier" in sub and mounts and not have & set(mounts):
            ids = [i for i in ("cheval_guerre", "cheval_selle", "poney") if i in mounts] or mounts
            out.append({"niveau": "info", "recommandes": ids,
                        "texte": "Guerrier (Cavalier) : Né en selle — ajoutez votre monture à la ménagerie (cheval de "
                                 "guerre, cheval de selle, poney pour une créature de taille Petite…)."})
        if norm(self.ch.pacte) == norm("Pacte de la chaîne"):
            ids = [e["id"] for e in getattr(self.db, "entities", {}).values() if e.get("category") == "pact_chain"]
            if ids and not have & set(ids):
                out.append({"niveau": "info", "recommandes": ids,
                            "texte": "Pacte de la chaîne : votre Appel de familier peut prendre l'une des formes "
                                     "supérieures — {}. Ce familier peut attaquer à la place d'une de vos attaques."
                                     .format(", ".join(self.entity(i)["name"] for i in ids))})
        return out

    def recommended_entities(self) -> set[str]:
        ids = {i for h in self.companion_hints() for i in h["recommandes"]}
        return ids | {eid for eid, ok in self.auto_entities().items() if ok}

    # ---------------------------------------------------------------- contexte de mise à l'échelle
    def _caster_ability(self) -> str:
        casters = self.casters()
        if casters:
            return casters[0]["carac"]
        return max(("Intelligence", "Sagesse", "Charisme"), key=self.mod)

    def scaling_context(self, ent: dict, inst: Optional[dict] = None) -> tuple[dict, dict]:
        """(contexte actuel, contexte de référence du fichier) pour les formules de l'entité."""
        sc = ent.get("scaling") or {}
        ref = dict(sc.get("reference") or {})
        if "spell_attack_bonus" in ref:
            ref.setdefault("spell_attack_modifier", ref["spell_attack_bonus"])
        attr = sc.get("scaling_attribute", "")
        ab = AB_KEYS.get(attr) or self._caster_ability()
        mod = self.mod(ab)
        bm = self.prof
        level = self.class_level(sc["class"]) if sc.get("class") else self.total_level
        cur = {"BM": bm, "class_level": max(1, level), "ability_mod": mod,
               "spell_attack_modifier": bm + mod, "spell_save_dc": 8 + bm + mod}
        for key, name in AB_KEYS.items():
            cur["mod_" + key] = self.mod(name)
        if sc.get("spell_level_min"):
            lvl = int((inst or {}).get("niveau_sort") or sc["spell_level_min"])
            cur["spell_level"] = max(int(sc["spell_level_min"]), min(9, lvl))
        ref.setdefault("BM", 2)
        ref.setdefault("ability_mod", 0)
        for key in AB_KEYS:
            ref.setdefault("mod_" + key, ref.get("ability_mod", 0))
        if "spell_level" not in ref and "spell_level" in cur:
            ref["spell_level"] = int(sc["spell_level_min"])
        ref.setdefault("class_level", cur["class_level"])
        return cur, ref

    # ---------------------------------------------------------------- fiche calculée
    def entity_sheet(self, inst: dict) -> dict:
        ent = self.entity(inst.get("id", "")) or {}
        sc = ent.get("scaling") or {}
        scaled = bool(sc)
        cur, ref = self.scaling_context(ent, inst) if scaled else ({}, {})
        ac = eval_formula(sc.get("ac_formula"), cur) if scaled else None
        hp = eval_formula(sc.get("hp_formula"), cur) if scaled else None
        hp_max = hp if hp else int(ent.get("hp_base") or 1)
        stats = {AB_KEYS[k]: int(v) for k, v in (ent.get("stats") or {}).items() if k in AB_KEYS}
        mods = {ab: R.ability_modifier(v) for ab, v in stats.items()}
        bm_delta = (cur.get("BM", 0) - ref.get("BM", 0)) if scaled and sc.get("class") else 0
        primal = bool(sc.get("checks_and_saves_formula"))
        # sauvegardes
        saves = {}
        for k, name in AB_KEYS.items():
            if name not in mods:
                continue
            if sc.get("saves_formula", {}).get(k) is not None:
                saves[name] = eval_formula(sc["saves_formula"][k], cur)
            elif primal:
                saves[name] = mods[name] + cur.get("BM", 0)
            elif k in (ent.get("saves") or {}):
                saves[name] = int(ent["saves"][k]) + bm_delta
            else:
                saves[name] = mods[name]
        # compétences
        skills = {}
        for name, val in (ent.get("skills") or {}).items():
            skills[name] = int(val) + bm_delta
        for name, f in (sc.get("skills_formula") or {}).items():
            v = eval_formula(f, cur)
            if v is not None:
                skills[name] = v
        checks = {ab: m + (cur.get("BM", 0) if primal else 0) for ab, m in mods.items()}
        # actions (attaques, DD)
        dmg_delta, dice_of_formula = 0, ""
        if scaled and isinstance(sc.get("damage_formula"), str):
            dice_of_formula, cur_flat, _n = eval_dice(sc["damage_formula"], cur)
            _d, ref_flat, _n = eval_dice(sc["damage_formula"], ref)
            dmg_delta = cur_flat - ref_flat
        dc = eval_formula(sc.get("save_dc_formula"), cur) if scaled and sc.get("save_dc_formula") else None
        attack = eval_formula(sc.get("attack_bonus_formula"), cur) if scaled and sc.get("attack_bonus_formula") else None
        actions = []
        for a in ent.get("actions") or []:
            row = dict(a)
            if a.get("attack_type") not in (None, "none") and a.get("attack_bonus") is not None:
                row["attack_bonus"] = attack if attack is not None else a["attack_bonus"]
            if a.get("damage_dice") and (a.get("attack_type") not in (None, "none") or dice_of_formula
                                         and split_damage(str(a["damage_dice"]))[0] == dice_of_formula):
                dice, flat = split_damage(str(a["damage_dice"]))
                row["damage_dice"] = join_damage(dice, flat + dmg_delta)
            if a.get("save"):
                row["save"] = dict(a["save"], dc=dc if dc is not None else a["save"].get("dc"))
            actions.append(row)
        size = ent.get("size", "")
        for lvl, s in sorted((sc.get("size_by_level") or {}).items(), key=lambda kv: int(kv[0])):
            if cur.get("class_level", 0) >= int(lvl):
                size = s
        level_feats = [{"name": "Niveau {}".format(lvl), "description": txt}
                       for lvl, txt in sorted((sc.get("level_features") or {}).items(), key=lambda kv: int(kv[0]))
                       if cur.get("class_level", 0) >= int(lvl)]
        temp = eval_formula(sc.get("temp_hp_formula"), cur) if scaled and sc.get("temp_hp_formula") else 0
        pp = eval_formula(sc.get("passive_perception_formula"), cur) if scaled and sc.get("passive_perception_formula") \
            else ent.get("passive_perception")
        multi = eval_formula(sc.get("attacks_per_multiattack"), cur) if scaled and sc.get("attacks_per_multiattack") \
            else None
        return {"entite": ent, "nom": inst.get("nom") or ent.get("name", "?"),
                "ca": ac if ac is not None else ent.get("ac"), "ca_note": ent.get("ac_note", ""),
                "pv_max": hp_max, "pv_temp_sort": temp or 0, "taille": SIZE_LABELS.get(size, size),
                "vitesses": {SPEED_LABELS.get(k, k): v for k, v in (ent.get("speed") or {}).items()},
                "stats": stats, "mods": mods, "tests": checks, "sauvegardes": saves, "competences": skills,
                "actions": actions, "reactions": ent.get("reactions") or [],
                "traits": list(ent.get("traits") or []) + level_feats, "dd": dc,
                "perception_passive": pp, "attaques_multiples": multi, "contexte": cur,
                "niveau_sort_min": int(sc["spell_level_min"]) if sc.get("spell_level_min") else None}

    # ---------------------------------------------------------------- jets
    def entity_check_spec(self, inst: dict, ability: str, save: bool = False) -> "D.RollSpec":
        sh = self.entity_sheet(inst)
        bonus = sh["sauvegardes" if save else "tests"].get(ability, 0)
        kind = "Jet de sauvegarde" if save else "Test"
        return D.spec_from_detail("{} — {} de {}".format(sh["nom"], kind, ability), "sauvegarde" if save else "test",
                                  [("Modificateur ({})".format(ability), "{:+d}".format(bonus))])

    def entity_skill_spec(self, inst: dict, skill: str) -> "D.RollSpec":
        sh = self.entity_sheet(inst)
        return D.spec_from_detail("{} — {}".format(sh["nom"], skill), "competence",
                                  [("Modificateur ({})".format(skill), "{:+d}".format(sh["competences"].get(skill, 0)))])

    def entity_attack_spec(self, inst: dict, action: dict) -> "D.RollSpec":
        sh = self.entity_sheet(inst)
        note = "Dégâts : {} {}".format(action.get("damage_dice", ""), action.get("damage_type", "")).strip()
        return D.spec_from_detail("{} — {}".format(sh["nom"], action["name"]), "attaque",
                                  [("Bonus d'attaque", "{:+d}".format(int(action.get("attack_bonus") or 0)))],
                                  note=note)
