"""
Chance (v52) — logique pure mélangée à Engine.

- Chanceux (trait du Halfelin, 2014 et 2024) : un 1 naturel au d20 d'une attaque, d'un test ou d'un JS est relancé
  et le nouveau résultat doit être utilisé (`RollSpec.reroll_ones`, appliqué par `dice.roll_d20`).
- Don Chanceux : points de chance (3 en 2014, bonus de maîtrise en 2024, repos long).
  2014 : un d20 de plus, on garde le meilleur de tous ; 2024 : avantage au jet, ou désavantage imposé à une attaque
  contre vous (« On m'attaque ! », sans réaction).
"""
from __future__ import annotations

from .rules import norm

LUCK_KEY = "don_chance"
D20_KINDS = ("test", "competence", "sauvegarde", "attaque", "sort")


class LuckMixin:
    """Mélangé à Engine."""

    def halfling_lucky(self) -> bool:
        return any(norm(c.get("nom", "")) == "chanceux" for c in self.race_capacities())

    def prepare_d20_spec(self, spec):
        """Réglages communs à tous les jets de d20 lancés par la fenêtre de dés (Chanceux du Halfelin)."""
        if spec is not None and getattr(spec, "kind", "") in D20_KINDS and self.halfling_lucky():
            spec.reroll_ones = "Chanceux (halfelin)"
        return spec

    def luck_tracker(self):
        return next((t for t in self.feat_trackers() if t["key"] == LUCK_KEY), None)

    def luck_left(self) -> int:
        tr = self.luck_tracker()
        return max(0, tr["total"] - self.resource_used(LUCK_KEY)) if tr else 0

    def spend_luck(self) -> bool:
        if self.luck_left() <= 0:
            return False
        self.ch.ressources_utilisees[LUCK_KEY] = self.resource_used(LUCK_KEY) + 1
        return True

    def luck_defense_option(self) -> list[dict]:
        """2024 : dépenser un point pour imposer le désavantage à une attaque contre vous (pas une réaction)."""
        if self.sheet_edition != 2024 or self.luck_left() <= 0:
            return []
        return [{"key": "chance", "label": "Chanceux ({} point(s)) : désavantage à l'attaquant".format(
            self.luck_left()), "effet": "desavantage", "valeur": 0, "cout": "1 point de chance", "chance": True}]
