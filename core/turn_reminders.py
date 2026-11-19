"""
Rappels de tour (v52) — logique pure mélangée à Engine.

- `start_turn()` : « ▶ Début de mon tour » — remet l'économie d'actions à zéro, applique les effets de début de
  tour (Héros du champ d'honneur, Ralliement héroïque…) et renvoie les rappels : concentration, jet contre la mort,
  rage à entretenir, aptitudes dont le texte se déclenche « au début de votre tour ».
- `end_turn()` : « ⏹ Fin de mon tour » — ce qui n'a pas servi (action, action bonus disponible), concentration,
  aptitudes « à la fin de votre tour ».
- `initiative_reminders()` : ressources rendues à l'initiative et aptitudes qui se déclenchent à ce moment.

Les déclencheurs sont lus dans les textes (aptitudes de classe et de sous-classe débloquées, traits d'espèce, dons,
effets actifs) : toute capacité nouvelle des données est donc rappelée sans liste à tenir à jour.
"""
from __future__ import annotations

import re

from .rules import norm

TRIGGERS = {
    "debut": re.compile(r"au debut de (?:chacun de )?(?:vos|votre) tours?(?! suivant)"),
    "fin": re.compile(r"(?:^|[.;:!]\s*|\bet\s)a la fin de (?:chacun de )?(?:vos|votre) tours?(?! suivant)"),
    "initiative": re.compile(r"(?:lancez|jetez|lancer|jeter|jet d') ?l'initiative|jet d'initiative|jets d'initiative"),
}
_SENTENCE = re.compile(r"(?<=[.!?])\s+")
# capacités déjà appliquées automatiquement à ce moment (pas de rappel en double)
AUTO_APPLIED = {"survivant", "heros du champ d'honneur", "rage persistante", "inspiration superieure",
                "concentration parfaite", "yo perfectionne", "instinct sauvage", "athlete accompli", "assassinat",
                "esprit parfait", "metabolisme surnaturel"}


def _sentence_with(text: str, rx) -> str:
    for s in _SENTENCE.split(text or ""):
        if rx.search(norm(s).replace("’", "'")):
            return s.strip()
    return ""


class TurnRemindersMixin:
    """Mélangé à Engine."""

    def _trigger_sources(self) -> list[tuple[str, str]]:
        """[(nom, description)] : aptitudes débloquées, traits d'espèce, dons, effets actifs."""
        out = []
        for e in self.ch.classes:
            for f in self.features(e):
                if f.get("debloque") and self.feature_allowed(f["nom"]):
                    out.append((f["nom"], f.get("description", "")))
        for c in self.race_capacities():
            out.append((c.get("nom", ""), c.get("description", "")))
        for name in dict.fromkeys(self.chosen_feats()):
            out.append(("Don : " + name, (self.db.feats.get(name) or {}).get("description", "")))
        from . import effects as FX
        for k in self.active_effect_keys():
            fx = FX.EFFECTS.get(k) or {}
            if fx:
                out.append((fx["nom"], fx.get("description", "")))
        return out

    def trigger_reminders(self, moment: str) -> list[str]:
        """Rappels « Nom : phrase » des capacités qui se déclenchent à ce moment (debut | fin | initiative)."""
        rx = TRIGGERS[moment]
        out, seen = [], set()
        for name, desc in self._trigger_sources():
            if not name or name in seen or norm(name) in AUTO_APPLIED:
                continue
            sentence = _sentence_with(desc, rx)
            if sentence:
                seen.add(name)
                out.append("{} : {}".format(name, sentence[:220] + ("…" if len(sentence) > 220 else "")))
        return out

    # ------------------------------------------------------------------ début de tour
    def start_turn(self) -> dict:
        """▶ Début de mon tour : {"appliques": [effets appliqués], "rappels": [à ne pas oublier]}."""
        applied = self.new_round()
        reminders = []
        ch = self.ch
        if ch.pv_actuels == 0 and not ch.forme_active:
            reminders.append("Vous êtes à 0 PV : faites votre jet contre la mort (bouton 🎲 dans Points de vie).")
        if ch.concentration:
            reminders.append("Concentration : {} — un JS de Constitution à chaque dégât subi.".format(ch.concentration))
        if "rage" in self.active_effect_keys():
            reminders.append("Rage : " + ("attaquez, forcez un JS ou dépensez une action bonus pour la prolonger, "
                                          "sinon elle prend fin à la fin de votre tour." if self.sheet_edition == 2024
                                          else "elle prend fin si vous n'avez ni attaqué ni subi de dégâts depuis "
                                               "votre dernier tour."))
        reminders += self.trigger_reminders("debut")
        return {"appliques": applied, "rappels": reminders}

    # ------------------------------------------------------------------ fin de tour
    def end_turn(self) -> list[str]:
        """⏹ Fin de mon tour : ce qui n'a pas servi et ce qui se déclenche maintenant."""
        out = []
        ch = self.ch
        active = {a["id"] for a in self.class_actions() if a.get("actif")}        # rage déjà active…
        tiles = [t for t in self.turn_actions() if t.get("disponible")
                 and (t.get("ref") or {}).get("action") not in active]
        if not ch.tour_action:
            out.append("Action non utilisée (Esquiver, Se tenir prêt, Aider… restent possibles).")
        bonus = [t["nom"] for t in tiles if t["type"] == "Action bonus" and t.get("groupe") != "generiques"]
        if not ch.tour_bonus and bonus:
            out.append("Action bonus non utilisée — disponible : {}.".format(", ".join(dict.fromkeys(bonus))[:220]))
        if ch.concentration:
            out.append("Concentration en cours : {}.".format(ch.concentration))
        out += self.trigger_reminders("fin")
        return out

    # ------------------------------------------------------------------ initiative
    def initiative_reminders(self) -> list[str]:
        return list(getattr(self, "_last_initiative_msgs", []) or []) + self.trigger_reminders("initiative")

    # ------------------------------------------------------------------ v52 : avant un repos
    def unused_before_rest(self, kind: str) -> list[str]:
        """Ressources jamais dépensées depuis qu'elles sont revenues (« long » : tout ce qui revient ;
        « court » : ce qui revient au repos court)."""
        out = []
        for tr in self.resource_trackers():
            if tr.get("where") == "interne" or not tr.get("total"):
                continue
            if kind == "court" and tr.get("recover") != "repos court":
                continue
            if self.resource_used(tr["key"]) == 0:
                out.append("{} ({} / {})".format(tr["label"], tr["total"], tr["total"]))
        slots = self.spell_slots()
        free = [(i + 1, s - self.ch.emplacements_utilises[i]) for i, s in enumerate(slots)
                if s and s - self.ch.emplacements_utilises[i] > 0]
        if kind == "long" and free and all(self.ch.emplacements_utilises[i] == 0 for i, s in enumerate(slots) if s):
            out.append("Emplacements de sort : aucun dépensé ({})".format(
                ", ".join("niv. {} ×{}".format(lv, n) for lv, n in free)))
        count, plvl = self.pact()
        if count and self.ch.pacte_utilises == 0:
            out.append("Emplacements de pacte (niveau {}) : {} non dépensé(s)".format(plvl, count))
        return out
