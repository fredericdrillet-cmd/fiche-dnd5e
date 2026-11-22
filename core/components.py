"""
Composantes matérielles coûteuses (v52) — logique pure mélangée à Engine.

Un sort qui consomme une composante d'une valeur indiquée (Rappel à la vie : diamant de 500 po…) est repéré dans
le texte de ses composantes ; les fiches 2014 dont la base n'a pas ce texte reprennent celui du sort 2024 jumeau,
sauf écarts connus (`OVERRIDES_2014`). Avant le lancement, l'interface vérifie l'inventaire : l'objet présent est
retiré (après confirmation) ; sinon le joueur choisit : payer la valeur avec la bourse, « le MJ l'a fournie », ou
annuler le sort. Un focaliseur ne remplace jamais une composante qui a un coût.
"""
from __future__ import annotations

import re
from typing import Optional

from .rules import norm

# 2014 : écarts avec le texte 2024 (None = aucune composante coûteuse consommée en 2014)
OVERRIDES_2014 = {
    "projection astrale": ("une jacinthe d'une valeur de 1 000 po et une barre d'argent de 100 po par cible, que le "
                           "sort consomme", 1100),
    "contrat": None,
    "preservation des morts": None,
    "protection contre le mal et le bien": None,
    "appel de familier": ("du charbon, de l'encens et des herbes d'une valeur de 10 po, que le sort consomme", 10),
}
KEYWORDS = ("diamant", "rubis", "jade", "encens", "agate", "huile", "encre", "or", "gemme", "jacinthe",
            "champignon", "joyau", "bol", "eau benite", "charbon")
_COST = re.compile(r"(\d[\d\s  ]*)\s*\+?\s*po", re.I)


def _cost(text: str) -> int:
    m = _COST.search(text)
    return int(re.sub(r"\D", "", m.group(1))) if m else 0


class ComponentsMixin:
    """Mélangé à Engine."""

    def costly_component(self, spell_name: str) -> Optional[dict]:
        """{texte, cout (po), mot} d'une composante coûteuse consommée par le sort ; None sinon."""
        base = re.sub(r"\s*\(2024\)$", "", spell_name or "")
        key = norm(base)
        if self.sheet_edition != 2024 and key in OVERRIDES_2014:
            ov = OVERRIDES_2014[key]
            return None if ov is None else self._component_info(ov[0], ov[1])
        texts = []
        for name in ((spell_name, base + " (2024)") if self.sheet_edition != 2024 else (spell_name,)):
            s = self.db.find_spell(name) or {}
            texts.append(s.get("composantes", ""))
        for comp in texts:
            m = re.search(r"M\s*\((.*)\)\s*$", comp or "")
            if not m:
                continue
            inner = m.group(1)
            if not re.search(r"consom|consum", norm(inner)):
                continue
            cost = _cost(inner)
            if cost:
                return self._component_info(inner, cost)
        return None

    @staticmethod
    def _component_info(text: str, cost: int) -> dict:
        n = norm(text)
        word = next((k for k in KEYWORDS if re.search(r"\b{}s?\b".format(k), n)), "")
        return {"texte": text, "cout": int(cost), "mot": word}

    def component_item(self, info: dict) -> Optional[dict]:
        """Objet de l'inventaire qui correspond à la composante (mot-clé dans le nom, quantité > 0)."""
        word = info.get("mot", "")
        if not word:
            return None
        for item in list(self.ch.equipement) + list(self.ch.objets_magiques):
            if re.search(r"\b{}s?\b".format(word), norm(item.get("nom", ""))) and int(item.get("qte", 1) or 0) > 0:
                return item
        return None

    def consume_component(self, item: dict) -> str:
        if item in self.ch.equipement:
            item["qte"] = int(item.get("qte", 1)) - 1
            if item["qte"] <= 0:
                self.ch.equipement.remove(item)
        elif item in self.ch.objets_magiques:
            self.ch.objets_magiques.remove(item)
        return "Composante consommée : {}.".format(item.get("nom", ""))

    def purse_copper(self) -> int:
        p = self.ch.pieces
        return int(p.get("po", 0)) * 100 + int(p.get("pa", 0)) * 10 + int(p.get("pc", 0))

    def pay_component(self, info: dict) -> tuple[bool, str]:
        """Déduit la valeur de la composante de la bourse (monnaie rendue en pa / pc)."""
        need = int(info["cout"]) * 100
        have = self.purse_copper()
        if have < need:
            return False, "Bourse insuffisante : {} po demandés.".format(info["cout"])
        left = have - need
        self.ch.pieces.update({"po": left // 100, "pa": (left % 100) // 10, "pc": left % 10})
        return True, "Composante payée : {} po retirés de la bourse.".format(info["cout"])
