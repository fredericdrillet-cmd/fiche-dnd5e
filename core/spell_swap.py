"""
Gestion des sorts entre deux niveaux (v44) — logique pure.

1. Échange d'un sort connu à la montée de niveau (Manuel des Joueurs) :
   Barde, Ensorceleur, Occultiste, Rôdeur, Chevalier occulte (Guerrier) et Arnaqueur arcanique (Roublard)
   peuvent, quand LA classe concernée gagne un niveau, oublier AU PLUS UN sort connu (de niveau 1 ou plus) et le
   remplacer par un autre sort de la liste de la classe, d'un niveau pour lequel ils ont des emplacements.
   Chevalier occulte / Arnaqueur arcanique : le remplaçant doit être d'Abjuration / d'Évocation (Guerrier) ou
   d'Enchantement / d'Illusion (Roublard), sauf si le sort oublié occupait un emplacement « libre » (sort hors
   école des niveaux 3, 8, 14, 20) : l'emplacement libéré accepte alors n'importe quelle école.
   L'échange se fait sur la COPIE de l'assistant ; un sort oublié sans remplaçant bloque « Confirmer ».

2. Repos long :
   - Clerc, Druide, Paladin (et Artificier, Magicien) : changer la liste des sorts préparés pour la journée,
     dans la limite niveau de classe (ou moitié) + modificateur d'incantation ; les sorts de domaine / serment /
     cercle restent préparés d'office et ne comptent pas ;
   - Magicien (Tasha, « Formules de sorts mineurs ») : échanger un tour de magie connu contre un autre tour de
     magie de la liste du Magicien.
"""
from __future__ import annotations

from typing import Optional

from .rules import norm

SWAP_CLASSES = ("Barde", "Ensorceleur", "Occultiste", "Rôdeur", "Guerrier", "Roublard")
REST_PREP_CLASSES = ("Clerc", "Druide", "Paladin", "Artificier", "Magicien")
CANTRIP_SWAP_CLASS = "Magicien"
SWAP_TITLE = "Remplacer un sort connu"
SWAP_PENDING = "{} : choisissez le sort qui remplace {} (ou annulez l'échange)."


def _swaps(sim) -> dict:
    """État des échanges de la copie de l'assistant : {classe: {"oublie": entrée, "nouveau": nom}}."""
    return sim.__dict__.setdefault("_level_swaps", {})


class SpellSwapMixin:
    """Mélangé à Engine. Les méthodes `level_swap_*` s'appellent sur la fiche d'origine avec la copie `sim`."""

    # ================================================================ 1. échange à la montée de niveau
    def level_swap_allowed(self, sim, class_name: str) -> bool:
        """Classe à sorts connus qui vient de gagner le niveau, et qui connaissait déjà au moins un sort de niveau 1+."""
        if class_name not in SWAP_CLASSES:
            return False
        c, before = sim.caster(class_name), self.caster(class_name)
        list_2024 = self.sheet_edition == 2024 and class_name in ("Barde", "Ensorceleur", "Occultiste")
        if c is None or before is None or (c.get("mode") != "known" and not list_2024):   # v52 : listes 2024
            return False
        return bool(self.level_swap_candidates(sim, class_name)) or class_name in _swaps(sim)

    def level_swap_candidates(self, sim, class_name: str) -> list[dict]:
        """Sorts connus AVANT ce niveau (niveau 1+, hors sorts accordés) encore présents sur la copie."""
        before = {s["nom"] for s in self.ch.sorts.get(class_name, []) if not s.get("accorde")}
        out = []
        for s in sim.ch.sorts.get(class_name, []):
            sp = sim.db.find_spell(s["nom"]) or {}
            if s["nom"] in before and int(sp.get("niveau") or 0) > 0:
                out.append(sp or {"nom": s["nom"], "niveau": 1})
        return out

    def level_swap_state(self, sim, class_name: str) -> dict:
        st = _swaps(sim).get(class_name) or {}
        old = st.get("oublie") or {}
        return {"oublie": old.get("nom", ""), "nouveau": st.get("nouveau", ""), "libre": bool(st.get("libre"))}

    def level_swap_forget(self, sim, class_name: str, name: str) -> bool:
        """Étape 1 : oublie `name` (un seul sort par niveau — un autre choix annule d'abord le précédent)."""
        if not self.level_swap_allowed(sim, class_name):
            return False
        if self.level_swap_state(sim, class_name)["oublie"]:
            self.level_swap_cancel(sim, class_name)
        if not any(sp["nom"] == name for sp in self.level_swap_candidates(sim, class_name)):
            return False
        lst = sim.ch.sorts.get(class_name, [])
        entry = next(s for s in lst if s["nom"] == name)
        r = sim.school_restriction(class_name)
        spell = sim.db.find_spell(name) or {}
        free = bool(r and spell.get("ecole") not in r["ecoles"])       # il occupait un emplacement « libre »
        sim.ch.sorts[class_name] = [s for s in lst if s is not entry]
        _swaps(sim)[class_name] = {"oublie": dict(entry), "nouveau": "", "libre": free}
        sim.normalize()
        return True

    def level_swap_options(self, sim, class_name: str) -> list[dict]:
        """Étape 2 : remplaçants possibles — liste de la classe, niveau 1 à niveau maximal, non connus, écoles."""
        st = self.level_swap_state(sim, class_name)
        if not st["oublie"] or st["nouveau"]:
            return []
        owned = {s["nom"] for s in sim.ch.sorts.get(class_name, [])}
        out = []
        for sp in sim.available_spells(class_name):
            if sp["niveau"] == 0 or sp["nom"] in owned or sp["nom"] == st["oublie"] or sp.get("hors_corpus"):
                continue
            if not sim.school_check(class_name, sp)[0]:
                continue
            out.append(sp)
        return out

    def level_swap_choose(self, sim, class_name: str, name: str) -> bool:
        if not any(sp["nom"] == name for sp in self.level_swap_options(sim, class_name)):
            return False
        sim.ch.sorts.setdefault(class_name, []).append({"nom": name, "prepare": True})
        _swaps(sim)[class_name]["nouveau"] = name
        sim.normalize()
        return True

    def level_swap_cancel(self, sim, class_name: str) -> bool:
        """Annule l'échange : le remplaçant disparaît, le sort oublié revient."""
        st = _swaps(sim).pop(class_name, None)
        if not st:
            return False
        lst = [s for s in sim.ch.sorts.get(class_name, []) if s["nom"] != st.get("nouveau")]
        if st.get("oublie") and not any(s["nom"] == st["oublie"]["nom"] for s in lst):
            lst.append(dict(st["oublie"]))
        sim.ch.sorts[class_name] = lst
        sim.normalize()
        return True

    def level_swap_pending(self, sim) -> list[dict]:
        """Échanges commencés mais incomplets (bloquent « Confirmer »)."""
        out = []
        for cls, st in _swaps(sim).items():
            if st.get("oublie") and not st.get("nouveau"):
                out.append({"onglet": "magie", "encart": "Sorts", "kind": "sorts", "echange": True,
                            "message": SWAP_PENDING.format(cls, st["oublie"]["nom"])})
        return out

    def level_swap_rule(self, sim, class_name: str) -> str:
        """Rappel de la règle affiché dans l'encart (écoles imposées comprises)."""
        base = ("À chaque niveau gagné dans cette classe, vous pouvez oublier au plus un sort connu et le remplacer "
                "par un autre sort de la liste de la classe, d'un niveau pour lequel vous avez des emplacements.")
        r = sim.school_restriction(class_name)
        if r:
            base += (" {} : le remplaçant doit être d'{}, sauf si le sort oublié occupait un emplacement libre "
                     "(sort de n'importe quelle école des niveaux 3, 8, 14 et 20).").format(
                r["sous_classe"], " ou d'".join(x.lower() for x in r["ecoles"]))
        return base

    # ================================================================ 2. repos long
    # ================================================================ v52 : Mode guidé (onglet Magie)
    FREE_PREP_2024 = ("Clerc", "Druide", "Magicien")

    def free_prep_class(self, class_name: str) -> bool:
        """Préparation quotidienne libre (onglet Magie) : Clerc, Druide, Paladin, Artificier, Magicien en 2014 ;
        Clerc, Druide, Magicien en 2024 (Paladin et Rôdeur : un sort au repos long ; Barde, Ensorceleur,
        Occultiste : un sort à la montée de niveau)."""
        if self.sheet_edition == 2024:
            return class_name in self.FREE_PREP_2024
        return class_name in REST_PREP_CLASSES

    def spell_learning_open(self, class_name: str, cantrip: bool) -> bool:
        """Un choix de sort manquant (sort mineur, sort connu ou à préparer) : complétable en Mode guidé."""
        c = self.caster(class_name)
        if c is None:
            return False
        cnt = self.spell_counts(class_name)
        if cantrip:
            return cnt["mineurs"] < (c.get("mineurs_max") or 0)
        if c.get("connus_max") is not None:
            return cnt["sorts"] < c["connus_max"]
        return c.get("prepares_max") is not None and cnt["prepares"] < c["prepares_max"]

    @staticmethod
    def scribe_cost(spell: dict) -> tuple[int, int]:
        """Recopier un sort dans le grimoire : 50 po et 2 heures par niveau du sort (po, minutes)."""
        lvl = max(1, int(spell.get("niveau") or 1))
        return 50 * lvl, 120 * lvl

    def scribe_spell(self, name: str, pay: bool = True, take_time: bool = True) -> tuple[bool, str]:
        """v52 : le Magicien recopie un sort trouvé (parchemin, grimoire) dans son grimoire, à tout moment."""
        spell = self.db.find_spell(name)
        if spell is None or self.caster("Magicien") is None or not int(spell.get("niveau") or 0):
            return False, "Seul un sort de niveau 1 ou plus se recopie dans le grimoire du Magicien."
        lst = self.ch.sorts.setdefault("Magicien", [])
        if any(s["nom"] == spell["nom"] for s in lst):
            return False, "« {} » est déjà dans votre grimoire.".format(spell["nom"])
        po, minutes = self.scribe_cost(spell)
        if pay and self.ch.pieces.get("po", 0) < po:
            return False, "Il faut {} po pour recopier « {} » (vous en avez {}).".format(
                po, spell["nom"], self.ch.pieces.get("po", 0))
        if pay:
            self.ch.pieces["po"] = self.ch.pieces.get("po", 0) - po
        if take_time:
            self.advance_time(minutes)
        lst.append({"nom": spell["nom"], "prepare": False})
        self.normalize()
        return True, "« {} » recopié dans le grimoire{}{}.".format(
            spell["nom"], " (−{} po)".format(po) if pay else "", ", {} h de travail".format(minutes // 60)
            if take_time else "")

    # v52 : règles 2024 — Paladin et Rôdeur ne remplacent qu'UN sort préparé par repos long
    ONE_SWAP_2024 = ("Paladin", "Rôdeur")

    def _rest_prep_class(self, class_name: str) -> bool:
        return class_name in REST_PREP_CLASSES or (self.sheet_edition == 2024 and class_name in self.ONE_SWAP_2024)

    def rest_prepare_classes(self) -> list[str]:
        return [c["classe"] for c in self.casters()
                if self._rest_prep_class(c["classe"]) and c.get("prepares_max") is not None]

    def _granted_names(self, class_name: str) -> list[str]:
        e = self.ch.find_class(class_name)
        return list(self.domain_spells(e)) if e else []

    def rest_prepare_info(self, class_name: str) -> Optional[dict]:
        """{classe, maximum, formule, toujours, candidats, prepares} pour la fenêtre « Changer les sorts préparés ».
        Candidats : toute la liste (Clerc, Druide, Paladin, Artificier) ou le grimoire (Magicien), niveau 1+."""
        c = self.caster(class_name)
        if c is None or c.get("prepares_max") is None or not self._rest_prep_class(class_name):
            return None
        granted = set(self._granted_names(class_name))
        entries = {s["nom"]: s for s in self.ch.sorts.get(class_name, [])}
        if class_name == "Magicien":
            pool = [self.db.find_spell(n) or {"nom": n, "niveau": 1} for n in entries]
        else:
            pool = list(self.available_spells(class_name))
        cands = [sp for sp in pool if int(sp.get("niveau") or 0) > 0 and sp["nom"] not in granted
                 and not sp.get("hors_corpus")]
        cands.sort(key=lambda sp: (int(sp.get("niveau") or 0), norm(sp["nom"])))
        prepared = [n for n, s in entries.items() if s.get("prepare") and n in {sp["nom"] for sp in cands}]
        half = class_name in ("Paladin", "Artificier")
        formula = "{} {} ({}) {:+d} ({})".format("moitié du niveau de" if half else "niveau de", class_name,
                                                 c["niveau"] // 2 if half else c["niveau"], c["mod"], c["carac"])
        if self.sheet_edition == 2024:                   # 2024 : quota de la table de classe
            formula = "table du {} (niveau {})".format(class_name, c["niveau"])
        swaps = 1 if self.sheet_edition == 2024 and class_name in self.ONE_SWAP_2024 else None
        return {"classe": class_name, "maximum": c["prepares_max"], "formule": formula, "toujours": sorted(granted),
                "candidats": cands, "prepares": prepared, "remplacements": swaps}

    @staticmethod
    def rest_new_allowed(info: dict) -> Optional[int]:
        """Nouveaux sorts permis au repos (None = libre) : 1 remplacement (Paladin, Rôdeur 2024), plus les places
        encore libres dans le quota."""
        if not info.get("remplacements"):
            return None
        return info["remplacements"] + max(0, info["maximum"] - len(info["prepares"]))

    def rest_set_prepared(self, class_name: str, names) -> tuple[bool, str]:
        """Applique la liste des sorts préparés (après le repos). Refuse au-delà du quota."""
        info = self.rest_prepare_info(class_name)
        if info is None:
            return False, "{} ne prépare pas ses sorts.".format(class_name)
        allowed = {sp["nom"] for sp in info["candidats"]}
        names = [n for n in dict.fromkeys(names) if n in allowed]
        if len(names) > info["maximum"]:
            return False, "Trop de sorts préparés : {} / {}.".format(len(names), info["maximum"])
        limit = self.rest_new_allowed(info)
        if limit is not None and len([n for n in names if n not in info["prepares"]]) > limit:
            return False, "Règle 2024 : {} ne remplace qu'un sort préparé par repos long.".format(class_name)
        lst = self.ch.sorts.setdefault(class_name, [])
        have = {s["nom"]: s for s in lst}
        for n in names:
            if n not in have:
                lst.append({"nom": n, "prepare": True})
        chosen = set(names)
        for s in lst:
            if s["nom"] in allowed:
                s["prepare"] = s["nom"] in chosen
        if class_name != "Magicien":       # sorts de liste non préparés : retirés (ils restent dans la liste de classe)
            self.ch.sorts[class_name] = [s for s in lst if s.get("prepare") or s["nom"] not in allowed
                                         or s.get("accorde")]
        self.normalize()
        return True, "{} : {} sort(s) préparé(s) pour la journée.".format(class_name, len(names))

    def cantrip_swap_available(self) -> bool:
        """Magicien : un tour de magie au repos long — règle 2024 (Incantation), option de Tasha en 2014."""
        if self.sheet_edition != 2024 and not self.rule_active("options_tasha"):
            return False
        return self.caster(CANTRIP_SWAP_CLASS) is not None and bool(self.cantrip_swap_known())

    def cantrip_swap_known(self) -> list[dict]:
        out = []
        for s in self.ch.sorts.get(CANTRIP_SWAP_CLASS, []):
            sp = self.db.find_spell(s["nom"]) or {}
            if sp.get("niveau") == 0 and not s.get("accorde"):
                out.append(sp)
        return out

    def cantrip_swap_options(self) -> list[dict]:
        owned = {s["nom"] for lst in self.ch.sorts.values() for s in lst}
        return sorted((sp for sp in self.available_spells(CANTRIP_SWAP_CLASS)
                       if sp["niveau"] == 0 and sp["nom"] not in owned and not sp.get("hors_corpus")),
                      key=lambda sp: norm(sp["nom"]))

    def swap_cantrip(self, old: str, new: str) -> tuple[bool, str]:
        """Formules de sorts mineurs (Tasha) : un tour de magie du Magicien remplacé par un autre de sa liste."""
        if not any(sp["nom"] == old for sp in self.cantrip_swap_known()):
            return False, "{} n'est pas un tour de magie connu du Magicien.".format(old)
        if not any(sp["nom"] == new for sp in self.cantrip_swap_options()):
            return False, "{} n'est pas un tour de magie disponible pour le Magicien.".format(new)
        lst = self.ch.sorts[CANTRIP_SWAP_CLASS]
        for s in lst:
            if s["nom"] == old:
                s["nom"] = new
                s["prepare"] = True
                break
        self.normalize()
        return True, "Tour de magie échangé : {} → {}.".format(old, new)
