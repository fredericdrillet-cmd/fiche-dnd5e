"""
Élixirs expérimentaux de l'Alchimiste (Artificier 2014, Chaudron de Tasha) (v53) — logique pure mélangée à Engine.

- À la fin d'un repos long (outils d'alchimiste en main) : 1 élixir gratuit (2 au niveau 6, 3 au niveau 15), effet
  tiré au d6 ; ils arrivent dans l'inventaire (« Élixir expérimental (Guérison) »). Les élixirs non bus du repos
  précédent disparaissent (ils ne durent que jusqu'à la fin du repos long suivant).
- « Créer un élixir » : action, un emplacement de sort de niveau 1 ou plus, effet AU CHOIX.
- Boire / faire boire : action. Guérison 2d4 + Int ; Rapidité +3 m (1 h) ; Résistance +1 CA (10 min) ; Audace +1d4
  aux attaques et JS (1 min) ; Vol 3 m (10 min) ; Transformation (Modification d'apparence, 10 min).
  Niveau 9 (Ingrédients revigorants) : + 2d6 + Int PV temporaires.
- Donner : l'élixir quitte l'inventaire (aucun lien entre les fiches) ; côté allié, « Élixir reçu » l'ajoute avec le
  niveau et le modificateur d'Intelligence de l'Alchimiste.
"""
from __future__ import annotations

import random
import re
from typing import Optional

from .rules import norm

ELIXIRS = ["Guérison", "Rapidité", "Résistance", "Audace", "Vol", "Transformation"]
EFFECT_KEYS = {"Rapidité": "elixir_rapidite", "Résistance": "elixir_resistance", "Audace": "elixir_audace",
               "Vol": "elixir_vol", "Transformation": "elixir_transformation"}
PREFIX = "Élixir expérimental"


def elixir_name(effect: str) -> str:
    return "{} ({})".format(PREFIX, effect)


def elixir_effect(name: str) -> str:
    m = re.match(r"elixir experimental \(([^)]+)\)", norm(name))
    return next((e for e in ELIXIRS if m and norm(e) == m.group(1)), "")


class ElixirsMixin:
    """Mélangé à Engine."""

    def alchemist_level(self) -> int:
        for e in self.ch.classes:
            if e["nom"] == "Artificier" and "alchimiste" in norm(self.active_subclass(e)) and e["niveau"] >= 3:
                return e["niveau"]
        return 0

    def free_elixir_count(self) -> int:
        lvl = self.alchemist_level()
        return 0 if not lvl else 3 if lvl >= 15 else 2 if lvl >= 6 else 1

    def _add_elixir_item(self, effect: str, record: dict) -> str:
        name = elixir_name(effect)
        item = next((i for i in self.ch.equipement if i.get("nom") == name), None)
        if item:
            item["qte"] = int(item.get("qte", 1)) + 1
        else:
            self.ch.equipement.append({"nom": name, "qte": 1})
        self.ch.elixirs.append(dict(record, effet=effect, nom=name))
        return name

    def _remove_elixir_item(self, name: str) -> bool:
        for i, item in enumerate(self.ch.equipement):
            if item.get("nom") == name:
                item["qte"] = int(item.get("qte", 1)) - 1
                if item["qte"] <= 0:
                    self.ch.equipement.pop(i)
                return True
        return False

    def own_elixirs(self) -> list[dict]:
        return [e for e in self.ch.elixirs if e.get("propre")]

    def long_rest_elixirs(self, rolls: Optional[list[int]] = None, rng=None) -> dict:
        """Fin du repos long : les élixirs non bus du repos précédent disparaissent, les nouveaux (1d6 chacun) sont
        ajoutés à l'inventaire. Renvoie {crees: [effets], disparus: [effets]}."""
        gone = []
        for rec in list(self.own_elixirs()):
            if self._remove_elixir_item(rec["nom"]):
                gone.append(rec["effet"])
            self.ch.elixirs.remove(rec)
        created = []
        n = self.free_elixir_count()
        rng = rng or random
        rolls = list(rolls or [])
        for k in range(n):
            r = rolls[k] if k < len(rolls) else rng.randint(1, 6)
            effect = ELIXIRS[max(1, min(6, int(r))) - 1]
            self._add_elixir_item(effect, self._elixir_record(propre=True))
            created.append(effect)
        return {"crees": created, "disparus": gone}

    def _elixir_record(self, propre: bool, level: int = 0, intm: Optional[int] = None) -> dict:
        return {"propre": propre, "niveau": int(level or self.alchemist_level()),
                "int": int(self.mod("Intelligence") if intm is None else intm)}

    def create_elixir(self, effect: str) -> str:
        """Élixir créé en dépensant un emplacement de sort (l'emplacement est dépensé par la tuile)."""
        if effect not in ELIXIRS:
            return ""
        self._add_elixir_item(effect, self._elixir_record(propre=True))
        return "{} créé ({}) — ajouté à l'inventaire.".format(PREFIX, effect)

    def receive_elixir(self, effect: str, level: int, intm: int) -> str:
        """Élixir donné par un Alchimiste allié (niveau et mod. d'Intelligence saisis)."""
        if effect not in ELIXIRS:
            return ""
        self._add_elixir_item(effect, self._elixir_record(propre=False, level=level, intm=intm))
        return "{} reçu ({}) — ajouté à l'inventaire.".format(PREFIX, effect)

    def give_elixir(self, name: str) -> str:
        """L'élixir est donné à un allié : il quitte l'inventaire (sans lien avec l'autre fiche)."""
        if not self._remove_elixir_item(name):
            return ""
        rec = next((e for e in self.ch.elixirs if e.get("nom") == name), None)
        if rec:
            self.ch.elixirs.remove(rec)
        return "{} donné.".format(name)

    def drink_elixir(self, name: str, rng=None) -> str:
        """Effet d'un élixir bu (l'objet est retiré par use_consumable)."""
        effect = elixir_effect(name)
        rec = next((e for e in self.ch.elixirs if e.get("nom") == name), None) or self._elixir_record(False)
        if rec in self.ch.elixirs:
            self.ch.elixirs.remove(rec)
        rng = rng or random
        lvl, intm = int(rec.get("niveau", 0)), int(rec.get("int", 0))
        msg = "{} : ".format(name)
        if effect == "Guérison":
            total = max(1, sum(rng.randint(1, 4) for _ in range(2)) + intm)
            before = self.ch.pv_actuels if self.ch.pv_actuels >= 0 else self.hp_max()
            self.ch.pv_actuels = min(self.hp_max(), before + total)
            if self.ch.pv_actuels > 0 and hasattr(self, "wake_up"):
                self.wake_up()
            msg += "2d4 + {} = {} → +{} PV".format(intm, total, self.ch.pv_actuels - before)
        elif effect in EFFECT_KEYS:
            from . import effects as FX
            self.add_effect(EFFECT_KEYS[effect])
            if EFFECT_KEYS[effect] not in self.ch.effets_potions:
                self.ch.effets_potions.append(EFFECT_KEYS[effect])
            msg += "état « {} » actif ({})".format(FX.EFFECTS[EFFECT_KEYS[effect]]["nom"],
                                                   FX.EFFECTS[EFFECT_KEYS[effect]]["duree"])
        if lvl >= 9:                                      # Ingrédients revigorants
            temp = max(1, sum(rng.randint(1, 6) for _ in range(2)) + intm)
            self.ch.pv_temporaires = max(int(self.ch.pv_temporaires), temp)
            msg += " ; {} PV temporaires (ingrédients revigorants)".format(temp)
        return msg
