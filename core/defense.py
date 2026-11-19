"""
« 🛡 On m'attaque ! » (v52) — réactions défensives proposées au bon moment, logique pure mélangée à Engine.

1. `attack_check(total)` : l'attaque touche-t-elle votre CA ?
2. `defense_options("attaque")` : réactions qui changent le résultat avant les dégâts — Bouclier (+5 CA),
   Duelliste défensif (+ bonus de maîtrise à la CA), Mots cinglants (dé d'inspiration retiré du jet),
   Illumination protectrice / Éclat protecteur (désavantage).
3. `defense_options("degats")` : réactions qui réduisent les dégâts — Esquive instinctive (moitié), Parade de
   projectiles 2014 / Déviation d'assaut 2024, manœuvre Parade.
4. `use_defense(key)` dépense la réaction et le coût (emplacement, dé, utilisation) et renvoie l'effet chiffré.
Les dégâts restants passent par `take_damage` (type, résistances, réductions). On peut toujours subir les dégâts
sans réaction.
"""
from __future__ import annotations

import random
from typing import Optional

from . import dice as D
from .rules import norm


class DefenseMixin:
    """Mélangé à Engine."""

    def attack_check(self, total: int, crit: bool = False) -> dict:
        ca = self.armor_class()[0]
        return {"ca": ca, "touche": crit or int(total) >= ca, "total": int(total)}

    def _shield_spell(self) -> str:
        for name in ("Bouclier (2024)", "Bouclier") if self.sheet_edition == 2024 else ("Bouclier",):
            if name in self.known_spell_names():
                return name
        return ""

    def defense_options(self, stage: str, total: int = 0, melee: Optional[bool] = None) -> list[dict]:
        """Réactions possibles à ce stade (« attaque » avant les dégâts, « degats » après) ; [] si réaction prise."""
        luck = self.luck_defense_option() if stage == "attaque" else []   # v52 : Chanceux 2024 (sans réaction)
        if self.ch.reaction_utilisee:
            return luck
        acts = {a["id"]: a for a in self.class_actions()}
        out = list(luck)
        if stage == "attaque":
            spell = self._shield_spell()
            if spell and any(self.smite_levels()):
                out.append({"key": "bouclier", "label": "Bouclier (sort, emplacement de niveau 1+)", "effet": "ca",
                            "valeur": 5, "cout": "1 emplacement", "spell": spell})
            if any("duelliste defensif" in norm(f) for f in self.chosen_feats()):
                slot = self.main_hand_slot()
                if slot and "finesse" in self._props(slot):
                    out.append({"key": "duelliste", "label": "Duelliste défensif (arme de finesse)", "effet": "ca",
                                "valeur": self.prof, "cout": "réaction"})
            for aid, label in (("cap:mots_cinglants", "Mots cinglants"),):
                a = acts.get(aid)
                if a and a.get("disponible") and a.get("formule"):
                    out.append({"key": aid, "label": label + " (dé d'inspiration retiré du jet)", "effet": "malus",
                                "valeur": a["formule"], "cout": a.get("cout_txt", ""), "action": aid})
            a = acts.get("cap:eclat_protecteur")
            if a and a.get("disponible"):
                out.append({"key": "cap:eclat_protecteur", "label": a["nom"] + " (désavantage au jet)",
                            "effet": "desavantage", "valeur": 0, "cout": a.get("cout_txt", ""),
                            "action": "cap:eclat_protecteur"})
        else:
            a = acts.get("esquive_instinctive")
            if a and a.get("disponible"):
                out.append({"key": "esquive_instinctive", "label": "Esquive instinctive (moitié des dégâts)",
                            "effet": "moitie", "valeur": 0, "cout": "réaction", "action": "esquive_instinctive"})
            a = acts.get("cap:parade_projectiles")
            if a and a.get("disponible") and (self.sheet_edition == 2024 or melee is not True):
                what = "toute attaque (contondant, perforant, tranchant)" if self.sheet_edition == 2024 \
                    else "attaque d'arme à distance"
                out.append({"key": "cap:parade_projectiles", "label": "{} ({})".format(a["nom"], what),
                            "effet": "reduction", "valeur": a["formule"], "cout": "réaction",
                            "action": "cap:parade_projectiles"})
            for a in acts.values():
                if a.get("manoeuvre") == "Parade" and a.get("disponible") and melee is not False:
                    out.append({"key": a["id"], "label": "Manœuvre Parade (attaque au corps à corps)",
                                "effet": "reduction", "valeur": a["formule"], "cout": a.get("cout_txt", ""),
                                "action": a["id"]})
        return out

    def use_defense(self, option: dict, rng=None) -> dict:
        """Applique une réaction : {ok, message, ca, malus, moitie, reduction}."""
        rng = rng or random
        res = {"ok": True, "message": "", "ca": 0, "malus": 0, "moitie": False, "reduction": 0,
               "desavantage": False}
        if option.get("chance"):                         # v52 : point de chance, pas de réaction
            if not self.spend_luck():
                return dict(res, ok=False, message="Plus de point de chance.")
            return dict(res, desavantage=True, message="Chanceux : désavantage imposé à l'attaquant (point de chance "
                                                         "dépensé).")
        if option.get("spell"):
            cast = self.cast_spell(option["spell"], slot_level=1, effect="bouclier")   # +5 CA jusqu'à votre tour
            if not cast["ok"]:
                return dict(res, ok=False, message=cast["message"])
        elif option.get("action"):
            r = self.use_class_action(option["action"])
            if not r.get("ok"):
                return dict(res, ok=False, message=r.get("message", ""))
        self.ch.reaction_utilisee = self.ch.reaction_utilisee or option["key"]
        kind, val = option["effet"], option["valeur"]
        if kind == "ca":
            res["ca"] = 0 if option.get("spell") else int(val)          # Bouclier : effet actif, déjà dans la CA
            res["message"] = "{} : +{} à la CA contre cette attaque.".format(option["label"].split(" (")[0], val)
        elif kind == "malus":
            n = self._roll_formula(val, rng)
            res["malus"] = n
            res["message"] = "{} : −{} au jet d'attaque.".format(option["label"].split(" (")[0], n)
        elif kind == "desavantage":
            res["desavantage"] = True
            res["message"] = "Désavantage imposé : l'attaquant relance un d20 et garde le moins bon."
        elif kind == "moitie":
            res["moitie"] = True
            res["message"] = "Esquive instinctive : dégâts divisés par deux."
        elif kind == "reduction":
            n = max(0, self._roll_formula(val, rng))
            res["reduction"] = n
            res["message"] = "{} : dégâts réduits de {} ({}).".format(option["label"].split(" (")[0], n, val)
        return res

    @staticmethod
    def _roll_formula(formula: str, rng) -> int:
        dice, flat = D.parse_damage(formula)
        total = flat
        for sign, n, sides in dice:
            total += sign * sum(rng.randint(1, sides) for _ in range(n))
        return total

    def damage_after_reactions(self, amount: int, effects: list[dict]) -> int:
        for e in effects:
            if e.get("reduction"):
                amount = max(0, amount - e["reduction"])
            if e.get("moitie"):
                amount //= 2
        return amount

    # ------------------------------------------------------------------ v52 : jet de concentration
    def concentration_dc(self, damage: int) -> int:
        dc = max(10, int(damage) // 2)
        return min(dc, 30) if self.sheet_edition == 2024 else dc

    def concentration_save_spec(self, damage: int) -> "D.RollSpec":
        """JS de Constitution pour maintenir la concentration : maîtrise, effets, Mage de guerre, Esprit occulte…"""
        spec = self.save_spec("Constitution")
        extra = [s for s in self.concentration_advantage() if s not in spec.avantage]
        spec.avantage = list(spec.avantage) + extra
        spec.mode = D.mode_of(spec.avantage, spec.desavantage, spec.echec)
        spec.title = "Concentration — {} (DD {})".format(self.ch.concentration or "sort", self.concentration_dc(damage))
        spec.note = (spec.note + " — " if spec.note else "") + "DD {} : moitié des dégâts subis, minimum 10".format(
            self.concentration_dc(damage))
        return spec

    def resolve_concentration(self, total: int, damage: int) -> str:
        """Applique le résultat : sur un échec, le sort et ses effets prennent fin."""
        dc = self.concentration_dc(damage)
        self.pending_concentration = 0
        if int(total) >= dc:
            return "Concentration maintenue sur {} ({} contre DD {}).".format(self.ch.concentration, total, dc)
        old = self.break_concentration()
        return "Concentration rompue ({} contre DD {}) : {} prend fin.".format(total, dc, old)
