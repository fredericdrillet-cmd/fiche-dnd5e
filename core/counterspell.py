"""
Contresort et Dissipation de la magie (v52) — logique pure mélangée à Engine.

- Contresort 2014 et Dissipation de la magie (2014 et 2024) : un sort de niveau inférieur ou égal à l'emplacement
  utilisé est annulé d'office ; au-delà, test de votre caractéristique d'incantation contre DD 10 + niveau du sort
  (Abjuration améliorée : + bonus de maîtrise ; Touche-à-tout : + moitié du bonus de maîtrise).
- Contresort 2024 : le lanceur adverse fait un JS de Constitution contre votre DD de sauvegarde des sorts.
"""
from __future__ import annotations

from typing import Optional

from . import dice as D
from .rules import norm

COUNTER_SPELLS = {"contresort": "contresort", "dissipation de la magie": "dissipation"}


class CounterspellMixin:
    """Mélangé à Engine."""

    def counter_kind(self, spell_name: str) -> str:
        base = norm((spell_name or "").replace(" (2024)", ""))
        return COUNTER_SPELLS.get(base, "")

    def _counter_caster(self, spell_name: str) -> Optional[dict]:
        casters = self.casters()
        sp = self.db.find_spell(spell_name) or {}
        for c in casters:
            if c["classe"] in (sp.get("classes") or []) or c.get("liste") in (sp.get("classes") or []):
                return c
        return casters[0] if casters else None

    def counter_info(self, spell_name: str, slot_level: int, target_level: int) -> dict:
        """{auto: annulé d'office, dd (test), js_dd (2024 Contresort), texte}."""
        kind = self.counter_kind(spell_name)
        caster = self._counter_caster(spell_name) or {"carac": "Intelligence", "dc": 10}
        if kind == "contresort" and self.sheet_edition == 2024:
            return {"auto": False, "dd": 0, "js_dd": caster["dc"], "carac": caster["carac"],
                    "texte": "Contresort : le lanceur fait un JS de Constitution DD {} ; sur un échec, son sort est "
                             "dissipé sans effet (son emplacement n'est pas dépensé).".format(caster["dc"])}
        what = "le sort" if kind == "contresort" else "l'effet"
        if int(target_level) <= int(slot_level):
            return {"auto": True, "dd": 0, "js_dd": 0, "carac": caster["carac"],
                    "texte": "{} : {} de niveau {} est {} d'office (emplacement de niveau {}).".format(
                        "Contresort" if kind == "contresort" else "Dissipation de la magie", what, target_level,
                        "annulé" if kind == "contresort" else "dissipé", slot_level)}
        dc = 10 + int(target_level)
        return {"auto": False, "dd": dc, "js_dd": 0, "carac": caster["carac"],
                "texte": "Niveau {} au-dessus de votre emplacement ({}) : test de {} DD {}.".format(
                    target_level, slot_level, caster["carac"], dc)}

    def counter_check_spec(self, spell_name: str, dc: int, ability: str) -> "D.RollSpec":
        spec = self.ability_check_spec(ability)
        extra = []
        if self.has_feature("abjuration amelioree"):
            extra.append(D.Term("Abjuration améliorée", self.prof))
        elif self.has_feature("touche-a-tout"):
            extra.append(D.Term("Touche-à-tout", self.prof // 2))
        spec.terms = list(spec.terms) + extra
        spec.title = "{} — test de {} DD {}".format(spell_name.replace(" (2024)", ""), ability, dc)
        return spec

    def counter_result(self, spell_name: str, total: int, dc: int) -> str:
        ok = int(total) >= int(dc)
        verb = "annulé" if self.counter_kind(spell_name) == "contresort" else "dissipé"
        return "{} : {} contre DD {} — {}.".format(spell_name.replace(" (2024)", ""), total, dc,
                                                   "réussite, le sort est " + verb if ok else "échec, le sort persiste")
