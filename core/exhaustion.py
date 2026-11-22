"""
Épuisement (v52) — selon l'édition de la fiche, logique pure mélangée à Engine.

- 2014 : six paliers cumulatifs (désavantage aux tests ; vitesse ÷ 2 ; désavantage aux attaques et JS ; PV max ÷ 2 ;
  vitesse 0 ; mort) — effets « epuisement_N » de core/mechanics.py.
- 2024 : chaque niveau donne −2 à tous les tests de d20 (attaques, tests, JS) et −1,50 m de vitesse ; mort au 6e.
- Compteur −/+ (`set_exhaustion`), JS d'épuisement selon la cause (`exhaustion_causes`, `exhaustion_save_spec`,
  `apply_exhaustion_save`), Frénésie du Berserker 2014 (un niveau à la fin de la rage).
"""
from __future__ import annotations

from . import dice as D

CAUSES = [
    ("marche", "Marche forcée", "Constitution DD 10 + 1 par heure au-delà de 8 heures de marche."),
    ("chaleur", "Chaleur extrême", "Sans eau ni protection : Constitution DD 5 à la fin de chaque heure, +1 par "
                                   "heure. Armure intermédiaire ou lourde, vêtements épais : désavantage."),
    ("froid", "Froid extrême", "Sans protection contre le froid : Constitution DD 10 à la fin de chaque heure."),
    ("eau", "Manque d'eau", "Moitié de la ration d'eau : Constitution DD 15 à la fin de la journée ; moins : un "
                            "niveau automatique."),
    ("nourriture", "Manque de nourriture", "Au-delà de 3 + modificateur de Constitution jours sans manger : un "
                                           "niveau automatique par jour (pas de jet)."),
    ("autre", "Autre (DD du MJ)", "Le MJ fixe le DD (sort, poison, piège…)."),
]


class ExhaustionMixin:
    """Mélangé à Engine."""

    def exhaustion_level(self) -> int:
        levels = [int(k.split("_")[1]) for k in self.ch.effets_actifs if k.startswith("epuisement_")]
        return max(levels) if levels else 0

    def set_exhaustion(self, level: int) -> str:
        level = max(0, min(6, int(level)))
        was_dead = self.exhaustion_level() >= 6
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if not k.startswith("epuisement_")]
        if level:
            self.ch.effets_actifs.append("epuisement_{}".format(level))
        if level >= 6:                                   # v52 : le personnage meurt — 0 PV, PV maximum inchangés
            if getattr(self.ch, "forme_active", ""):
                self.end_form()
            self.ch.pv_actuels = 0
            self.ch.pv_temporaires = 0
            self.ch.mort_echecs = 3
        elif was_dead:                                   # correction (niveau 6 retiré) : la mort est annulée,
            self.ch.mort_echecs = self.ch.mort_reussites = 0   # les PV restent à 0 (soins nécessaires)
        return self.exhaustion_text()

    def exhaustion_text(self) -> str:
        n = self.exhaustion_level()
        if not n:
            return "Aucun épuisement."
        if n >= 6:
            return "Épuisement 6 : le personnage meurt."
        if self.sheet_edition == 2024:
            return "Épuisement {} : −{} à tous les tests de d20, vitesse −{:g} m.".format(n, 2 * n, 1.5 * n)
        effects = ["désavantage aux tests de caractéristique", "vitesse divisée par deux",
                   "désavantage aux attaques et aux JS", "PV maximum divisés par deux", "vitesse réduite à 0"]
        return "Épuisement {} : {}.".format(n, ", ".join(effects[:n]))

    def exhaustion_mech_2024(self, level: int) -> dict:
        """Modificateurs 2024 d'un niveau d'épuisement (remplace la table 2014 sur une fiche 2024)."""
        malus = -2 * level
        return {"tests": {"*": [malus]}, "js": {"*": [malus]}, "attaque": [malus], "vitesse_bonus": -1.5 * level}

    # ------------------------------------------------------------------ JS d'épuisement
    def exhaustion_causes(self) -> list[tuple[str, str, str]]:
        return list(CAUSES)

    def exhaustion_dc(self, cause: str, hours: int = 1, dc: int = 10) -> int:
        if cause == "marche":
            return 10 + max(1, int(hours))
        if cause == "chaleur":
            return 5 + max(0, int(hours) - 1)
        if cause == "froid":
            return 10
        if cause == "eau":
            return 15
        return int(dc)

    def exhaustion_save_spec(self, cause: str, dc: int) -> "D.RollSpec":
        spec = self.save_spec("Constitution")
        label = next((c[1] for c in CAUSES if c[0] == cause), "Épuisement")
        spec.title = "{} — JS de Constitution DD {}".format(label, dc)
        if cause == "chaleur" and self.db.armors.get(self.ch.armure.get("nom", ""), {}).get("categorie") in (
                "intermédiaire", "lourde"):
            spec.desavantage = list(spec.desavantage) + ["Armure intermédiaire ou lourde (chaleur)"]
            spec.mode = D.mode_of(spec.avantage, spec.desavantage, spec.echec)
        return spec

    def apply_exhaustion_save(self, total: int, dc: int) -> str:
        if int(total) >= dc:
            return "JS réussi ({} contre DD {}) : pas d'épuisement.".format(total, dc)
        self.set_exhaustion(self.exhaustion_level() + 1)
        return "JS raté ({} contre DD {}) : un niveau d'épuisement. {}".format(total, dc, self.exhaustion_text())

    def gain_exhaustion(self, reason: str = "") -> str:
        self.set_exhaustion(self.exhaustion_level() + 1)
        return ("{} : un niveau d'épuisement. ".format(reason) if reason else "") + self.exhaustion_text()
