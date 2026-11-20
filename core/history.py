"""
Annuler / Refaire (v52) — historique des états de la fiche, logique pure.

`UndoHistory.capture(state)` est appelé après chaque modification (état = `Character.to_dict()`) : si l'état a changé,
l'état précédent est empilé avec un libellé déduit des champs modifiés (« PV », « ressources », « états »…). Des
modifications rapprochées du même champ (saisie dans une case, plusieurs clics de sphère) forment une seule étape.
L'historique des lancers n'est jamais annulé.
"""
from __future__ import annotations

import copy
import time
from typing import Callable, Optional

LIMIT = 30
MERGE_SECONDS = 2.0
IGNORED = ("historique_jets", "journal")                         # jamais annulé (journal des lancers)
LABELS = [
    (("pv_actuels", "pv_temporaires", "pv_divers"), "PV"),
    (("mort_reussites", "mort_echecs"), "jets contre la mort"),
    (("ressources_utilisees",), "ressources"),
    (("emplacements_utilises", "pacte_utilises"), "emplacements de sort"),
    (("effets_actifs", "effets_retires", "effets_potions", "effets_rounds", "effets_rounds_max"), "états et effets"),
    (("concentration", "concentration_cible", "concentration_effet"), "concentration"),
    (("classes",), "classes et niveaux"),
    (("ameliorations",), "améliorations et dons"),
    (("options_classe",), "choix de classe et de dons"),
    (("sorts", "sorts_mineurs", "sorts_mj", "sorts_raciaux"), "sorts"),
    (("equipement", "objets_magiques", "armure", "armes_cac", "armes_distance"), "équipement"),
    (("tour_action", "tour_bonus", "tour_attaques", "tour_deplacement", "reaction_utilisee", "tour_utilises"),
     "tour en cours"),
    (("competences", "sauvegardes", "scores_achat", "bonus_divers"), "caractéristiques et compétences"),
    (("temps_minutes", "dernier_repos_long", "des_vie_utilises"), "repos et dés de vie"),
]


def describe(before: dict, after: dict) -> str:
    changed = {k for k in set(before) | set(after) if k not in IGNORED and before.get(k) != after.get(k)}
    names = [label for keys, label in LABELS if changed & set(keys)]
    if not names:
        names = ["fiche"] if changed else []
    if len(names) > 2:
        return "{}, {}…".format(names[0], names[1])
    return " et ".join(names)


class UndoHistory:
    def __init__(self, limit: int = LIMIT, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.clock = clock
        self.undo_stack: list[tuple[dict, str]] = []
        self.redo_stack: list[tuple[dict, str]] = []
        self.current: Optional[dict] = None
        self._last_time = 0.0
        self._last_label = ""

    def reset(self, state: dict) -> None:
        self.undo_stack, self.redo_stack = [], []
        self.current = copy.deepcopy(state)
        self._last_label = ""

    def capture(self, state: dict) -> bool:
        """Enregistre l'état après une modification ; True si une étape a été ajoutée ou fusionnée."""
        if self.current is None:
            self.reset(state)
            return False
        label = describe(self.current, state)
        if not label:
            return False
        now = self.clock()
        merge = (self.undo_stack and label == self._last_label and now - self._last_time < MERGE_SECONDS)
        if not merge:
            self.undo_stack.append((self.current, label))
            del self.undo_stack[:-self.limit]
        self.current = copy.deepcopy(state)
        self.redo_stack = []
        self._last_time, self._last_label = now, label
        return True

    def can_undo(self) -> bool:
        return bool(self.undo_stack)

    def can_redo(self) -> bool:
        return bool(self.redo_stack)

    def undo_label(self) -> str:
        return self.undo_stack[-1][1] if self.undo_stack else ""

    def redo_label(self) -> str:
        return self.redo_stack[-1][1] if self.redo_stack else ""

    def _restore(self, state: dict) -> dict:
        out = copy.deepcopy(state)
        for k in IGNORED:                                 # le journal des lancers reste celui d'aujourd'hui
            if self.current is not None and k in self.current:
                out[k] = copy.deepcopy(self.current[k])
        return out

    def undo(self) -> Optional[tuple[dict, str]]:
        if not self.undo_stack:
            return None
        state, label = self.undo_stack.pop()
        restored = self._restore(state)
        self.redo_stack.append((self.current, label))
        self.current = copy.deepcopy(restored)
        self._last_label = ""
        return restored, label

    def redo(self) -> Optional[tuple[dict, str]]:
        if not self.redo_stack:
            return None
        state, label = self.redo_stack.pop()
        restored = self._restore(state)
        self.undo_stack.append((self.current, label))
        self.current = copy.deepcopy(restored)
        self._last_label = ""
        return restored, label
