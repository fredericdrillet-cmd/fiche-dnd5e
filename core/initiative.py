"""
Jet d'initiative (v45) : 1d20 + modificateur d'initiative, détail complet du calcul.

Le modificateur comprend :
  - le modificateur de Dextérité (l'initiative est un test de Dextérité) ;
  - les dons (Alerte : +5 ; Vigilant, s'il est présent : + bonus de maîtrise) ;
  - Touche-à-tout (Barde 2 : moitié du bonus de maîtrise, arrondie à l'inférieur) ou Athlète remarquable
    (Champion 7 : moitié, arrondie au supérieur) — le plus élevé des deux ;
  - aptitudes de sous-classe : Embusqué redoutable (+ Sagesse), Audace désinvolte (+ Charisme), Prescience de
    bataille (+ Charisme, minimum 1), Esprit tactique et Conscience temporelle (+ Intelligence) ;
  - les effets actifs qui modifient les tests de Dextérité (bonus, dés, avantage / désavantage) ;
  - avantage : Instinct sauvage (Barbare 7), Maître de l'embuscade.
"""
from __future__ import annotations

import random
from typing import Optional

from . import dice as D
from . import rules as R

ABILITY_FEATURES = [("embusque redoutable", "Sagesse", "Embusqué redoutable", 0),
                    ("audace desinvolte", "Charisme", "Audace désinvolte", 0),
                    ("prescience de bataille", "Charisme", "Prescience de bataille", 1),
                    ("esprit tactique", "Intelligence", "Esprit tactique", 0),
                    ("conscience temporelle", "Intelligence", "Conscience temporelle", 0)]
ADVANTAGE_FEATURES = [("instinct sauvage", "Instinct sauvage"), ("maitre de l'embuscade", "Maître de l'embuscade")]


class InitiativeMixin:
    def initiative_detail(self) -> dict:
        """{termes: [(source, valeur)], total, avantage: [...], desavantage: [...], des: [...]}"""
        terms = [("Modificateur de Dextérité", self.mod("Dextérité"))]
        for feat in self.chosen_feats():
            eff = int(self.db.feats.get(feat, {}).get("effets", {}).get("initiative", 0))
            if R.norm(feat) == "vigilant":
                eff = eff or self.prof
            if eff:
                terms.append(("Don : " + feat, eff))
        half = []
        if self.has_feature("touche-a-tout"):
            half.append(("Touche-à-tout (½ maîtrise)", self.prof // 2))
        if self.has_feature("athlete remarquable"):
            half.append(("Athlète remarquable (½ maîtrise)", (self.prof + 1) // 2))
        if half:
            terms.append(max(half, key=lambda x: x[1]))
        for frag, ab, label, minimum in ABILITY_FEATURES:
            if self.has_feature(frag):
                terms.append(("{} ({})".format(label, ab), max(minimum, self.mod(ab))))
        fx = self.check_mods("Dextérité")
        dice = []
        for label, val in fx["detail"]:
            v = str(val).replace(" ", "")
            if "d" in v:
                dice.append((label, v))
            else:
                try:
                    terms.append((label, int(v)))
                except ValueError:
                    pass
        adv = list(fx["avantage"]) + [lab for frag, lab in ADVANTAGE_FEATURES if self.has_feature(frag)]
        return {"termes": terms, "total": sum(v for _, v in terms), "des": dice, "avantage": adv,
                "desavantage": list(fx["desavantage"])}

    def initiative_spec(self) -> "D.RollSpec":
        d = self.initiative_detail()
        detail = [(label, "{:+d}".format(v)) for label, v in d["termes"]] + list(d["des"])
        return D.spec_from_detail("Jet d'initiative", "test", detail, d["avantage"], d["desavantage"], (),
                                  "1d20 {} (modificateur d'initiative)".format(R.fmt_bonus(d["total"])))

    def roll_initiative(self, natural: Optional[int] = None) -> dict:
        """Jet sans interface (tests / repli) : {d20, total, texte}. Le résultat est gardé sur la fiche."""
        d = self.initiative_detail()
        n = natural if natural is not None else random.randint(1, 20)
        total = n + d["total"]
        self.ch.initiative_jet = total
        text = "1d20 ({}) {} = {}".format(n, " ".join("{} {}".format(R.fmt_bonus(v), lab) for lab, v in d["termes"]),
                                          total)
        return {"d20": n, "total": total, "texte": text}

    def record_initiative(self, total: int) -> None:
        self.ch.initiative_jet = int(total)
