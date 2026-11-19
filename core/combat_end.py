"""
Début et fin d'un combat (v52) — logique pure mélangée à Engine.

- Le combat commence au jet d'initiative ou au premier « ▶ Début de mon tour » : instantané des PV, ressources
  et emplacements (`Character.combat_etat`), compteur de rounds.
- Chaque attaque avec une arme à munitions consomme une munition (`fire_ammo`), comptée dans
  `Character.munitions_tirees`.
- « 🏁 Fin du combat » (`end_combat`) : la moitié des munitions tirées revient au stock, la rage et les effets « jusqu'à
  votre prochain tour » prennent fin, ainsi que les états de combat (Surpris, Caché, À terre) ; le tour est remis
  à zéro ; les sorts en cours gardent leur durée (l'horloge n'avance pas). Renvoie le bilan.
"""
from __future__ import annotations

from . import effects as FX
from .rules import norm

COMBAT_STATES = ("surpris", "cache", "a_terre")
TURN_DURATIONS = ("jusqu'au debut", "jusqu'a la fin", "premier round", "votre tour", "duree de la rage")


class CombatEndMixin:
    """Mélangé à Engine."""

    def in_combat(self) -> bool:
        return bool(self.ch.combat_etat)

    def ensure_combat_started(self) -> None:
        if self.ch.combat_etat:
            return
        self.ch.combat_etat = {"pv": int(self.ch.pv_actuels), "pv_temp": int(self.ch.pv_temporaires),
                               "ressources": dict(self.ch.ressources_utilisees),
                               "emplacements": list(self.ch.emplacements_utilises),
                               "pacte": int(self.ch.pacte_utilises), "rounds": 0}

    def count_round(self) -> None:
        self.ensure_combat_started()
        self.ch.combat_etat["rounds"] = int(self.ch.combat_etat.get("rounds", 0)) + 1

    # ------------------------------------------------------------------ munitions
    def fire_ammo(self, slot: dict) -> str:
        """Attaque avec une arme à munitions : une munition consommée et comptée pour la récupération."""
        if not slot or not self.ammo_kind(self.db.weapons.get(slot.get("nom", ""), {})):
            return ""
        return self.shoot(slot)

    def note_shot(self, ammo_name: str) -> None:
        self.ch.munitions_tirees[ammo_name] = int(self.ch.munitions_tirees.get(ammo_name, 0)) + 1

    def recover_ammo(self) -> list[str]:
        out = []
        for name, n in self.ch.munitions_tirees.items():
            back = int(n) // 2
            item = next((i for i in self.ch.equipement if i.get("nom") == name), None)
            if back and item is not None:
                item["qte"] = int(item.get("qte", 0)) + back
                out.append("{} : {} récupérée(s) sur {} tirée(s)".format(name, back, n))
            elif n:
                out.append("{} : aucune récupérée sur {} tirée(s)".format(name, n))
        self.ch.munitions_tirees = {}
        return out

    # ------------------------------------------------------------------ fin du combat
    def _combat_only(self, key: str) -> bool:
        if key in COMBAT_STATES or key in ("rage", "frenesie"):
            return True
        d = norm(FX.EFFECTS.get(key, {}).get("duree", ""))
        return any(d.startswith(x) for x in TURN_DURATIONS)

    def end_combat(self) -> list[str]:
        """Bilan du combat terminé (lignes lisibles)."""
        lines = []
        start = dict(self.ch.combat_etat or {})
        if "frenesie" in self.ch.effets_actifs and "rage" in self.ch.effets_actifs and self.sheet_edition == 2014:
            lines.append(self.gain_exhaustion("Frénésie"))
        ended = [k for k in list(self.ch.effets_actifs) if self._combat_only(k)]
        for k in ended:
            self.remove_effect(k)
        if ended:
            lines.append("Fin de : " + ", ".join(FX.EFFECTS[k]["nom"] for k in ended if k in FX.EFFECTS))
        lines += self.recover_ammo()
        if start:
            if start.get("rounds"):
                lines.append("Durée : {} round(s)".format(start["rounds"]))
            lost = int(start.get("pv", 0)) - int(self.ch.pv_actuels)
            if lost > 0:
                lines.append("PV perdus : {} ({} / {})".format(lost, self.ch.pv_actuels, self.hp_max()))
            elif lost < 0:
                lines.append("PV regagnés : {}".format(-lost))
            spent = []
            labels = {t["key"]: t["label"] for t in self.resource_trackers()}
            for key, used in self.ch.ressources_utilisees.items():
                diff = int(used) - int(start.get("ressources", {}).get(key, 0))
                if diff > 0 and key in labels:
                    spent.append("{} ×{}".format(labels[key], diff))
            slots = [int(a) - int(b) for a, b in zip(self.ch.emplacements_utilises, start.get("emplacements", []))]
            for lvl, diff in enumerate(slots, 1):
                if diff > 0:
                    spent.append("emplacement niv. {} ×{}".format(lvl, diff))
            pact = int(self.ch.pacte_utilises) - int(start.get("pacte", 0))
            if pact > 0:
                spent.append("emplacement de pacte ×{}".format(pact))
            if spent:
                lines.append("Dépensé : " + ", ".join(spent))
        dice_left = sum(p["restants"] for p in self.hit_dice_pool())
        if 0 < self.ch.pv_actuels < self.hp_max() and dice_left > 0:
            lines.append("Pensez au repos court : {} dé(s) de vie disponible(s).".format(dice_left))
        self.ch.combat_etat = {}
        self.ch.reaction_utilisee = ""
        self.ch.tour_action = self.ch.tour_bonus = False
        self.ch.tour_attaques = 0
        self.ch.tour_deplacement = 0.0
        self.ch.tour_utilises = []
        self.ch.initiative_jet = 0
        return lines or ["Combat terminé."]
