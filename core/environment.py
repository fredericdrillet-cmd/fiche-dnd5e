"""
Dangers de l'environnement (v52) — chute et suffocation, logique pure mélangée à Engine.

- Chute : 1d6 contondants par tranche de 3 m (20d6 au plus), puis À terre si des dégâts restent. Chute ralentie du
  Moine (réaction, 5 × niveau de moine) ; Feuille morte : aucun dégât.
- Suffocation : retenir son souffle 1 + modificateur de Constitution minutes (30 secondes au moins), effet
  « Retient son souffle » décompté en rounds ; ensuite « Suffoque » :
  2014 : on survit un nombre de rounds égal au modificateur de Constitution (1 au moins), puis 0 PV ;
  2024 : un niveau d'épuisement à la fin de chacun de vos tours, tous retirés quand vous respirez à nouveau.
"""
from __future__ import annotations

from .durations import ROUNDS_PER_MINUTE

FALL_STEP_M = 3.0
FALL_MAX_DICE = 20


class EnvironmentMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ chute
    def fall_dice(self, height_m: float) -> int:
        return min(FALL_MAX_DICE, int(float(height_m) // FALL_STEP_M))

    def fall_formula(self, height_m: float) -> str:
        n = self.fall_dice(height_m)
        return "{}d6".format(n) if n else ""

    def slow_fall_reduction(self) -> int:
        """Chute ralentie (Moine 4) : 5 × niveau de moine, si la réaction est disponible."""
        lvl = self.class_level("Moine")
        return 5 * lvl if lvl >= 4 and not self.ch.reaction_utilisee else 0

    def apply_fall(self, total: int, height_m: float, slow_fall: bool = False, feather: bool = False) -> str:
        if feather:
            return "Feuille morte : vous descendez lentement, aucun dégât de chute."
        reduction = 0
        if slow_fall and self.slow_fall_reduction():
            reduction = self.slow_fall_reduction()
            self.ch.reaction_utilisee = "chute_ralentie"
        dmg = max(0, int(total) - reduction)
        head = "Chute de {:g} m : {} contondants".format(float(height_m), total)
        if reduction:
            head += " − {} (Chute ralentie) = {}".format(reduction, dmg)
        if dmg <= 0:
            return head + " — aucun dégât, vous retombez sur vos pieds."
        msg = self.take_damage(dmg, "contondant")
        if self.ch.pv_actuels > 0 or self.ch.forme_active:
            self.add_effect("a_terre")
        return "{} — {} À terre.".format(head, msg.rstrip(".") + "." if msg else "")

    # ------------------------------------------------------------------ suffocation
    def breath_rounds(self) -> int:
        """Souffle retenu : 1 + Con minutes, 30 secondes (5 rounds) au moins."""
        return max(5, (1 + self.mod("Constitution")) * ROUNDS_PER_MINUTE)

    def suffocation_rounds_2014(self) -> int:
        return max(1, self.mod("Constitution"))

    def hold_breath(self) -> str:
        self.add_effect("apnee")
        self.start_effect_timer("apnee", self.breath_rounds())
        return "Vous retenez votre souffle : {} rounds.".format(self.breath_rounds())

    def start_suffocating(self) -> str:
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if k != "apnee"]
        self.add_effect("suffoque")
        if self.sheet_edition == 2024:
            return "Vous suffoquez : un niveau d'épuisement à la fin de chacun de vos tours."
        self.start_effect_timer("suffoque", self.suffocation_rounds_2014())
        return "Vous suffoquez : {} round(s) avant de tomber à 0 PV.".format(self.suffocation_rounds_2014())

    def breathe_again(self) -> str:
        gained = int(self.ch.suffocation_niveaux or 0)
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if k not in ("apnee", "suffoque")]
        self.ch.suffocation_niveaux = 0
        if gained:
            self.set_exhaustion(self.exhaustion_level() - gained)
            return "Vous respirez : les {} niveau(x) d'épuisement dus à la suffocation disparaissent.".format(gained)
        return "Vous respirez à nouveau."

    def on_effect_expired(self, key: str) -> list[str]:
        """Suites d'un effet arrivé au bout de sa durée (appelé par `tick_effects`)."""
        if key == "apnee":
            return [self.start_suffocating()]
        if key == "suffoque" and self.sheet_edition != 2024:
            self.ch.pv_actuels = 0
            self.ch.pv_temporaires = 0
            return ["Suffocation : vous tombez à 0 PV et êtes mourant."]
        return []

    def suffocation_end_turn(self) -> list[str]:
        if self.sheet_edition != 2024 or "suffoque" not in self.ch.effets_actifs:
            return []
        self.ch.suffocation_niveaux = int(self.ch.suffocation_niveaux or 0) + 1
        return ["Suffocation : " + self.gain_exhaustion()]
