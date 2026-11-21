"""
Sources de lumière (v52, règle de survie) — logique pure mélangée à Engine.

Allumer une bougie, une torche ou une lanterne retire l'objet (ou une flasque d'huile pour une lanterne) de
l'inventaire et pose un effet décompté en rounds (1 heure = 600 rounds, 6 heures par flasque). Sans lumière,
`light_status()` rappelle la vision dans le noir.
"""
from __future__ import annotations

from .durations import ROUNDS_PER_MINUTE
from .rules import norm

HOUR = 60 * ROUNDS_PER_MINUTE
# clé d'effet, nom, objet consommé, objet requis (lanterne), lumière vive, lumière faible en plus, heures
LIGHT_SOURCES = [
    ("lumiere_bougie", "Bougie", "bougie", "", "1,50 m", "1,50 m", 1),
    ("lumiere_torche", "Torche", "torche", "", "6 m", "6 m", 1),
    ("lumiere_lanterne", "Lanterne à capote", "huile", "lanterne a capote", "9 m", "9 m", 6),
    ("lumiere_sourde", "Lanterne sourde", "huile", "lanterne sourde", "cône de 18 m", "18 m", 6),
]


class LightMixin:
    """Mélangé à Engine."""

    def _inventory_item(self, word: str):
        return next((i for i in self.ch.equipement if norm(i.get("nom", "")).startswith(word)
                     and int(i.get("qte", 1) or 0) > 0), None)

    def light_options(self) -> list[dict]:
        out = []
        for key, name, fuel, needs, bright, dim, hours in LIGHT_SOURCES:
            item = self._inventory_item(fuel)
            holder = self._inventory_item(needs) if needs else True
            why = "" if (item and holder) else ("Pas de {} dans l'inventaire.".format(name.lower()) if not needs
                                                 and not item else "Il faut la lanterne." if not holder
                                                 else "Plus d'huile pour la lanterne.")
            out.append({"key": key, "nom": name, "vive": bright, "faible": dim, "heures": hours,
                        "stock": int(item.get("qte", 1)) if item else 0, "possible": not why, "raison": why})
        return out

    def light_source(self, key: str) -> str:
        opt = next((o for o in self.light_options() if o["key"] == key), None)
        if opt is None or not opt["possible"]:
            return opt["raison"] if opt else "Source de lumière inconnue."
        fuel = next(s[2] for s in LIGHT_SOURCES if s[0] == key)
        item = self._inventory_item(fuel)
        item["qte"] = int(item.get("qte", 1)) - 1
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if k != key]
        self.add_effect(key)
        self.start_effect_timer(key, opt["heures"] * HOUR)
        return "{} allumée : lumière vive {}, faible {} de plus, {} h ({} restante(s)).".format(
            opt["nom"], opt["vive"], opt["faible"], opt["heures"], item["qte"])

    def active_light(self) -> list[str]:
        return [k for k in self.active_effect_keys() if k.startswith("lumiere_")]

    def light_status(self) -> str:
        lights = self.active_light()
        if lights:
            return "Éclairé : " + ", ".join("{} ({})".format(next(s[1] for s in LIGHT_SOURCES if s[0] == k),
                                                            self.effect_rounds_text(k) or "allumée") for k in lights)
        dv = self.darkvision()
        if dv["portee"]:
            return "Aucune lumière : vision dans le noir {:g} m (lumière faible jusqu'à cette distance, pas de " \
                   "couleurs).".format(dv["portee"])
        return "Aucune lumière et pas de vision dans le noir : vous êtes aveuglé dans les ténèbres."
