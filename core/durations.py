"""
Durées des effets en rounds (v52) — logique pure mélangée à Engine.

Un effet ajouté avec une durée chiffrée (« 1 minute », « Concentration, jusqu'à 10 minutes », « 1 heure ») reçoit un
compte à rebours en rounds (1 minute = 10 rounds) dans `Character.effets_rounds`. Il baisse d'un round à chaque
« ▶ Début de mon tour » et du temps écoulé (repos, avance du temps : 1 minute = 10 rounds) ; à 0, l'effet prend
fin avec un message. « Prolonger » remet la durée complète.
"""
from __future__ import annotations

import re
from typing import Optional

from . import effects as FX
from .rules import norm

ROUNDS_PER_MINUTE = 10
_UNITS = {"round": 1, "minute": ROUNDS_PER_MINUTE, "heure": 60 * ROUNDS_PER_MINUTE,
          "jour": 24 * 60 * ROUNDS_PER_MINUTE}
_DURATION = re.compile(r"(\d+)\s*(round|minute|heure|jour)s?\b")


def parse_rounds(text: str) -> Optional[int]:
    """« 1 minute » → 10, « Concentration, jusqu'à 10 minutes » → 100 ; None si la durée n'est pas chiffrée."""
    n = norm(text or "")
    if " par " in n or "niveau" in n:                   # « 1 heure par verre », « moitié du niveau en heures »
        return None
    m = _DURATION.search(n)
    return int(m.group(1)) * _UNITS[m.group(2)] if m else None


def rounds_text(rounds: int) -> str:
    if rounds < ROUNDS_PER_MINUTE * 2:
        return "{} round{}".format(rounds, "s" if rounds > 1 else "")
    minutes = -(-rounds // ROUNDS_PER_MINUTE)
    if minutes < 120:
        return "{} min".format(minutes)
    return "{} h".format(-(-minutes // 60))


class DurationsMixin:
    """Mélangé à Engine."""

    def effect_full_rounds(self, key: str) -> Optional[int]:
        return parse_rounds(FX.EFFECTS.get(key, {}).get("duree", ""))

    def start_effect_timer(self, key: str, rounds: Optional[int] = None) -> None:
        rounds = rounds if rounds is not None else self.effect_full_rounds(key)
        if rounds:
            self.ch.effets_rounds[key] = int(rounds)
            self.ch.effets_rounds_max[key] = int(rounds)

    def _timer_alive(self, key: str) -> bool:
        return bool(self.ch.concentration) if key == "concentration" else key in self.ch.effets_actifs

    def effect_rounds(self, key: str) -> Optional[int]:
        """Rounds restants d'un effet actif (None : durée non suivie)."""
        if not self._timer_alive(key):
            return None
        return self.ch.effets_rounds.get(key)

    def effect_rounds_text(self, key: str) -> str:
        r = self.effect_rounds(key)
        return "" if r is None else "{} restant{}".format(rounds_text(r), "s" if r > 1 else "")

    def extend_effect(self, key: str) -> str:
        """Remet la durée complète d'un effet (nouvelle incantation, potion reprise…)."""
        full = self.ch.effets_rounds_max.get(key) or self.effect_full_rounds(key)
        if not full or not self._timer_alive(key):
            return ""
        self.ch.effets_rounds[key] = full
        name = "Concentration ({})".format(self.ch.concentration) if key == "concentration" else FX.EFFECTS[key]["nom"]
        return "{} : durée remise à {}.".format(name, rounds_text(full))

    def tick_effects(self, rounds: int = 1) -> list[str]:
        """Fait passer `rounds` rounds ; renvoie les noms des effets qui prennent fin."""
        ended = []
        for key in list(self.ch.effets_rounds):
            if not self._timer_alive(key):
                self.ch.effets_rounds.pop(key, None)
                self.ch.effets_rounds_max.pop(key, None)
                continue
            left = self.ch.effets_rounds[key] - int(rounds)
            if left > 0:
                self.ch.effets_rounds[key] = left
                continue
            self.ch.effets_rounds.pop(key, None)
            self.ch.effets_rounds_max.pop(key, None)
            if key == "concentration":
                ended.append(self.ch.concentration)
                self.break_concentration()
                continue
            ended.append(FX.EFFECTS[key]["nom"])
            if self.ch.concentration and self.ch.concentration_effet == key:
                self.break_concentration()                 # la durée du sort est écoulée : concentration finie
            else:
                self.remove_effect(key)
            ended += self.on_effect_expired(key)           # v52 : souffle épuisé -> suffocation…
        return ended
