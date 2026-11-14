"""
Montée de niveau guidée (v29) et frise de progression 1 → 20 — logique pure.

L'assistant travaille sur une COPIE du personnage (`simulate_level_up`) : le joueur choisit la classe, les PV,
les choix du niveau (sous-classe, amélioration ou don, style de combat, faveur de pacte) ; le récapitulatif
avant / après se calcule sur la copie ; rien ne touche la vraie fiche tant que « Confirmer » n'est pas cliqué
(la copie remplace alors le personnage).
"""
from __future__ import annotations

import copy
from typing import Optional
from . import rules as R
from .character import Character
from .data_loader import PACTS
from .rules import ABILITIES

SCHOOLS = ["Abjuration", "Divination", "Enchantement", "Évocation", "Illusion", "Invocation", "Nécromancie",
           "Transmutation"]


def filter_spells(spells: list[dict], niveau=None, ecole: str = "", rituel: bool = False, concentration: bool = False,
                  texte: str = "") -> list[dict]:
    """Filtres du grimoire (v41) : niveau exact (None = tous), école, Rituel (R), Concentration (C), recherche."""
    t = R.norm(texte or "")
    out = []
    for sp in spells:
        if niveau is not None and int(sp.get("niveau") or 0) != niveau:
            continue
        if ecole and R.norm(sp.get("ecole", "")) != R.norm(ecole):
            continue
        if rituel and not sp.get("rituel"):
            continue
        if concentration and not sp.get("concentration"):
            continue
        if t and t not in R.norm(sp["nom"]):
            continue
        out.append(sp)
    return out


# choix faits DANS l'assistant (bloquent « Confirmer ») : (onglet, encart) de missing_choices()
INLINE = {("classes", "Sous-classe"): "sous_classe", ("progression", "Emplacements débloqués"): "amelioration",
          ("combat", "Style de combat"): "style", ("magie", "Pacte"): "pacte"}


class LevelUpMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ copie de travail
    def clone(self):
        return type(self)(self.db, Character.from_dict(copy.deepcopy(self.ch.to_dict())))

    def multiclass_prereq(self, class_name: str) -> str:
        """Message si les prérequis de multiclassage (classe visée ET classes actuelles) ne sont pas remplis."""
        problems = []
        for name in [class_name] + [e["nom"] for e in self.ch.classes if e["nom"] != class_name]:
            reqs, how = R.MULTICLASS_PREREQ.get(name, ([], "et"))
            ok = [self.score(ab) >= mn for ab, mn in reqs]
            if reqs and not (any(ok) if how == "ou" else all(ok)):
                problems.append("{} demande {}".format(name, (" ou " if how == "ou" else " et ").join(
                    "{} {}".format(ab, mn) for ab, mn in reqs)))
        return " ; ".join(problems)

    def level_up_options(self) -> list[dict]:
        """Classes proposées : celles du personnage (+1 niveau) et les autres classes (v50 : multiclassage toujours
        proposé par « Niveau supérieur », prérequis de caractéristiques vérifiés)."""
        if self.ch.niveau_total >= R.MAX_LEVEL:
            return []
        out = [{"classe": e["nom"], "avant": e["niveau"], "apres": e["niveau"] + 1, "nouvelle": False,
                "prerequis": "", "label": "{} — niveau {} → {}".format(e["nom"], e["niveau"], e["niveau"] + 1)}
               for e in self.ch.classes]
        if True:                                         # v50 : plus d'interrupteur de multiclassage
            owned = {e["nom"] for e in self.ch.classes}
            for name in self.db.class_names():
                if name in owned:
                    continue
                pre = self.multiclass_prereq(name) if self.ch.classes else ""
                out.append({"classe": name, "avant": 0, "apres": 1, "nouvelle": True, "prerequis": pre,
                            "label": "{} — nouvelle classe (multiclassage){}".format(name, " ⚠" if pre else "")})
        return out

    def simulate_level_up(self, class_name: str):
        """Copie du personnage avec un niveau de plus dans `class_name` (ajout de la classe si nouvelle)."""
        sim = self.clone()
        entry = sim.ch.find_class(class_name)
        if entry is None:
            sim.add_class(class_name)
        else:
            sim.set_class_level(sim.ch.classes.index(entry), entry["niveau"] + 1)
        return sim

    # ------------------------------------------------------------------ points de vie du niveau
    def level_hp_info(self, class_name: str) -> dict:
        """{de, faces, moyenne, con, gain_moyen, jet (valeur tirée ou None), mode} pour le niveau qui vient d'être pris."""
        entry = self.ch.find_class(class_name)
        sides = R.die_sides(self.db.start_info(class_name)["de_vie"])
        ci = self.ch.classes.index(entry)
        extra = self._hp_bonus_per_level(entry)
        con = self.mod("Constitution")
        roll = None
        if self.ch.pv_mode == "jets":
            ri = self._roll_index(ci, entry["niveau"])
            if 0 <= ri < len(entry["pv_jets"]):
                roll = entry["pv_jets"][ri]
        first = ci == 0 and entry["niveau"] == 1
        avg = sides if first else R.average_die(sides)
        return {"de": "d{}".format(sides), "faces": sides, "moyenne": avg, "con": con, "bonus": extra,
                "gain": max(1, (roll if roll is not None else avg) + con + extra), "jet": roll,
                "mode": self.ch.pv_mode, "premier": first}

    # ------------------------------------------------------------------ rapport de l'assistant
    def level_up_report(self, sim, class_name: str) -> dict:
        """Aptitudes gagnées, choix du niveau (dans l'assistant / à faire ensuite), récapitulatif avant / après."""
        entry = sim.ch.find_class(class_name)
        lvl = entry["niveau"]
        gained = [f for f in sim.features(entry) if f["niveau"] == lvl and f["debloque"]]
        before = {m["message"] for m in self.missing_choices()}
        new = [m for m in sim.missing_choices() if m["message"] not in before]
        inline = [dict(m, kind=INLINE[(m["onglet"], m["encart"])]) for m in new       # choix DE CE NIVEAU
                  if (m["onglet"], m["encart"]) in INLINE]
        # v40 : nouveaux sorts (sorts mineurs, sorts connus, grimoire) choisis DANS l'assistant ; la préparation
        # quotidienne reste à faire dans l'onglet Magie
        spells = [dict(m, kind="sorts") for m in new if (m["onglet"], m["encart"]) == ("magie", "Sorts")
                  and "a preparer" not in R.norm(m["message"])]
        inline += spells
        # v43 : manifestations occultes de l'Occultiste choisies DANS l'assistant
        manifs = [dict(m, kind="manifestations") for m in new if (m["onglet"], m["encart"]) ==
                  ("magie", "Manifestations occultes") and "manifestation" in R.norm(m["message"])]
        inline += manifs
        spells = spells + manifs
        inline += self.level_swap_pending(sim)          # v44 : échange de sort commencé mais incomplet
        # v51 : seuls les choix de LA classe montée à ce niveau comptent (« Choix du niveau (N) ») ; un message
        # d'une autre classe dont seul le texte a changé ne bloque plus l'assistant
        inline = [m for m in inline if self._concerns_class(m, class_name)]
        later = [m for m in new if (m["onglet"], m["encart"]) not in INLINE and m not in
                 [{k: v for k, v in x.items() if k != "kind"} for x in spells]]
        return {"classe": class_name, "niveau": lvl, "aptitudes": gained, "dans_assistant": inline,
                "ensuite": later, "recap": self.level_up_recap(sim)}

    @staticmethod
    def _concerns_class(m: dict, class_name: str) -> bool:
        """Choix de l'assistant lié à la classe montée : préfixe « Classe : » / « Classe — », style « (Classe) »,
        pacte et manifestations pour l'Occultiste ; les échanges de sorts sont toujours ceux de la classe montée."""
        kind, msg = m.get("kind", ""), m.get("message", "")
        if m.get("echange"):
            return True
        if kind in ("pacte", "manifestations"):
            return class_name == "Occultiste" or "Occultiste" not in msg and kind == "manifestations"
        if kind == "style":
            return "({})".format(class_name) in msg or "(" not in msg
        if kind in ("sous_classe", "amelioration", "sorts"):
            return msg.startswith(class_name) or not any(msg.startswith(c) for c in R.SUBCLASS_LEVEL)
        return True

    def level_up_recap(self, sim) -> list[tuple[str, str, str]]:
        """(libellé, avant, après) — seules les lignes qui changent sont gardées, sauf PV et maîtrise."""
        def slots(eng) -> str:
            s = eng.spell_slots()
            txt = " · ".join("{}:{}".format(i + 1, n) for i, n in enumerate(s) if n)
            count, plvl = eng.pact()
            if count:
                txt += (" · " if txt else "") + "pacte {}×niv.{}".format(count, plvl)
            return txt or "—"

        def casters(eng) -> dict:
            return {c["classe"]: "DD {} / attaque {}".format(c["dc"], R.fmt_bonus(c["attaque"])) for c in eng.casters()}

        def trackers(eng) -> dict:
            return {t["label"]: str(t["total"]) if t["total"] is not None else "∞"
                    for t in eng.resource_trackers() if not t.get("race") and t.get("where") != "interne"}

        rows = [("Niveau global", str(self.total_level), str(sim.total_level)),
                ("Points de vie maximum", str(self.hp_max()), str(sim.hp_max())),
                ("Bonus de maîtrise", R.fmt_bonus(self.prof), R.fmt_bonus(sim.prof)),
                ("Dés de vie", " + ".join("{}{}".format(n, d) for d, n in self.hit_dice().items()),
                 " + ".join("{}{}".format(n, d) for d, n in sim.hit_dice().items())),
                ("Emplacements de sorts", slots(self), slots(sim))]
        a, b = casters(self), casters(sim)
        for k in sorted(set(a) | set(b)):
            rows.append(("Sorts ({})".format(k), a.get(k, "—"), b.get(k, "—")))
        a, b = trackers(self), trackers(sim)
        for k in sorted(set(a) | set(b)):
            rows.append((k, a.get(k, "—"), b.get(k, "—")))
        a, b = self.manifestation_slots()["total"], sim.manifestation_slots()["total"]
        if a or b:
            rows.append(("Manifestations occultes", str(a), str(b)))
        for ab in ABILITIES:
            if self.score(ab) != sim.score(ab):
                rows.append((ab, str(self.score(ab)), str(sim.score(ab))))
        keep = {"Niveau global", "Points de vie maximum", "Bonus de maîtrise"}
        return [r for r in rows if r[0] in keep or r[1] != r[2]]

    def pact_options(self) -> list[str]:
        return list(PACTS) if self.sheet_edition != 2024 else []      # 2024 : le pacte est une manifestation

    # ------------------------------------------------------------------ v40 : nouveaux sorts du niveau
    def level_invocation_options(self, sim) -> list[dict]:
        """Manifestations occultes que la copie peut choisir maintenant (prérequis de niveau, pacte, sort remplis)."""
        return [m for n, m in sorted(sim.db.manifestations.items()) if n not in sim.ch.manifestations
                and sim.manifestation_status(n)[0] == "ok"]

    def level_invocations_missing(self, sim) -> int:
        return max(0, sim.manifestation_slots()["total"] - len(sim.ch.manifestations))

    def level_spell_plan(self, sim, class_name: str) -> Optional[dict]:
        """
        Quotas de sorts de `class_name` sur la copie : {classe, mode, mineurs: (choisis, maximum),
        connus: (choisis, maximum) | None, grimoire: (inscrits, minimum) | None, prepares: (préparés, maximum) | None,
        niveau_max, gain_mineurs, gain_sorts}. Les gains comparent avec la fiche actuelle (avant le niveau).
        """
        c = sim.caster(class_name)
        if c is None:
            return None
        cnt = sim.spell_counts(class_name)
        before = self.caster(class_name)
        grim = (cnt["sorts"], 6 + 2 * (c["niveau"] - 1)) if class_name == "Magicien" else None
        connus = (cnt["sorts"], c["connus_max"]) if c["connus_max"] is not None else None
        prep = (cnt["prepares"], c["prepares_max"]) if c["prepares_max"] is not None else None
        gain_c = c["mineurs_max"] - (before["mineurs_max"] if before else 0)
        if connus:
            gain_s = c["connus_max"] - (before["connus_max"] if before and before["connus_max"] is not None else 0)
        elif grim:
            gain_s = 2 if before else 6
        else:
            gain_s = 0
        return {"classe": class_name, "mode": c["mode"], "mineurs": (cnt["mineurs"], c["mineurs_max"]),
                "connus": connus, "grimoire": grim, "prepares": prep, "niveau_max": c["niveau_max"],
                "gain_mineurs": max(0, gain_c), "gain_sorts": max(0, gain_s)}

    @staticmethod
    def prepares_from_list(plan: dict) -> bool:
        """Lanceur qui prépare dans toute sa liste (Clerc, Druide, Paladin, Artificier) : pas de sorts « connus »."""
        return plan["connus"] is None and plan["grimoire"] is None and plan["prepares"] is not None

    def level_spell_options(self, sim, class_name: str) -> list[dict]:
        """Sorts que la copie peut apprendre maintenant (liste de classe, niveau max, écoles imposées), non connus.
        Pour un lanceur qui prépare dans sa liste, les sorts de niveau 1+ sont proposés à la préparation."""
        plan = self.level_spell_plan(sim, class_name)
        if plan is None:
            return []
        owned = {s["nom"] for s in sim.ch.sorts.get(class_name, [])}
        out = []
        for sp in sim.available_spells(class_name):
            if sp["nom"] in owned or sp.get("hors_corpus"):
                continue
            ok, _why = sim.school_check(class_name, sp)
            if not ok:
                continue
            if sp["niveau"] == 0 and plan["mineurs"][0] >= plan["mineurs"][1]:
                continue
            if sp["niveau"] > 0:
                quota = plan["connus"] or plan["grimoire"] or (plan["prepares"] if self.prepares_from_list(plan)
                                                               else None)
                if quota is None or quota[0] >= quota[1]:
                    continue
            out.append(sp)
        return out

    def level_learn_spell(self, sim, class_name: str, name: str) -> bool:
        if not any(sp["nom"] == name for sp in self.level_spell_options(sim, class_name)):
            return False
        plan = self.level_spell_plan(sim, class_name)
        spell = sim.db.find_spell(name) or {}
        # magicien : un sort inscrit au grimoire n'est préparé que s'il reste de la place
        prepared = True
        if class_name == "Magicien" and spell.get("niveau") and plan["prepares"] is not None:
            prepared = plan["prepares"][0] < plan["prepares"][1]
        sim.ch.sorts.setdefault(class_name, []).append({"nom": name, "prepare": prepared})
        sim.normalize()
        return True

    def level_prepare_info(self, sim, class_name: str) -> Optional[dict]:
        """{prepares, maximum, toujours} : jauge des sorts préparés (niveau de classe + modificateur…).
        `toujours` = lanceur à sorts connus (Barde, Ensorceleur, Occultiste, Rôdeur) : tout sort connu est utilisable."""
        plan = self.level_spell_plan(sim, class_name)
        if plan is None:
            return None
        if plan["prepares"] is None:
            return {"prepares": plan["connus"][0] if plan["connus"] else 0,
                    "maximum": plan["connus"][1] if plan["connus"] else 0, "toujours": True}
        return {"prepares": plan["prepares"][0], "maximum": plan["prepares"][1], "toujours": False}

    def level_set_prepared(self, sim, class_name: str, name: str, on: bool) -> bool:
        """Coche / décoche « Préparé » sur la copie, dans la limite de la classe. Renvoie True si l'état a changé."""
        info = self.level_prepare_info(sim, class_name)
        if info is None or info["toujours"]:
            return False
        entry = next((s for s in sim.ch.sorts.get(class_name, []) if s["nom"] == name), None)
        if entry is None or bool(entry.get("prepare")) == bool(on):
            return False
        if on and info["prepares"] >= info["maximum"]:
            return False
        entry["prepare"] = bool(on)
        sim.normalize()
        return True

    # ------------------------------------------------------------------ frise de progression 1 → 20
    def class_roadmap(self, entry: dict) -> list[dict]:
        """Une colonne par niveau : {niveau, atteint, aptitudes, sous_classe, amelioration, sort_niveau}."""
        name = entry["nom"]
        feats = self.features(entry)
        cls = self.db.classes.get(name, {})
        sub_need = self.subclass_level(name)
        cfg = R.CASTERS.get(name) or R.SUBCLASS_CASTERS.get((name, self.active_subclass(entry)))
        out = []
        for lvl in range(1, R.MAX_LEVEL + 1):
            names = [f["nom"] for f in feats if f["niveau"] == lvl and not R.is_asi_feature(f["nom"])]
            asi = any(R.is_asi_feature(f["nom"]) and f["niveau"] == lvl for f in cls.get("capacites_classe", []))
            spell = None
            if cfg and lvl >= cfg["min_level"]:
                now = R.max_spell_level(cfg["kind"], lvl)
                prev = R.max_spell_level(cfg["kind"], lvl - 1) if lvl - 1 >= cfg["min_level"] else 0
                if now and now > prev:
                    spell = now
            sub_feats = [f["nom"] for f in feats if f["niveau"] == lvl and f.get("sous_classe")]
            out.append({"niveau": lvl, "atteint": entry["niveau"] >= lvl, "actuel": entry["niveau"] == lvl,
                        "aptitudes": names, "sous_classe": lvl == sub_need or bool(sub_feats),
                        "choix_sous_classe": lvl == sub_need, "amelioration": asi, "sort_niveau": spell})
        return out


def roadmap_icons(col: dict) -> str:
    """Icônes d'une colonne de la frise : ✦ aptitude · ◆ sous-classe · ▲ amélioration ou don · ✧ niveau de sort."""
    icons = ""
    if col["aptitudes"]:
        icons += "✦"
    if col["sous_classe"]:
        icons += "◆"
    if col["amelioration"]:
        icons += "▲"
    if col["sort_niveau"]:
        icons += "✧"
    return icons

