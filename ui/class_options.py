"""
v52 — Choix de classe et de sous-classe (manœuvres du Maître de guerre, runes du Chevalier runique, options de Tir
arcanique, Métamagie, Ordre divin / primitif, formes connues…) : `option_sets()` hors dons.

Ces choix se font au moment où on les gagne : dans l'assistant de création (niveau 1) et dans « Niveau supérieur ».
L'onglet Classes n'affiche plus que des rappels ; une fenêtre de rattrapage reste possible pour une fiche dont des
choix manquent (ancienne sauvegarde, Mode libre).
"""
from __future__ import annotations

import html
from typing import Callable, Optional

from PyQt6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QGridLayout, QVBoxLayout, QWidget

from .common import fill_combo, make_label, rich_tip
from .game_widgets import clear_layout

NO_OPTION = "— à choisir —"


def class_option_sets(engine) -> list[dict]:
    """Ensembles de choix de classe (les choix des dons restent dans l'onglet Progression)."""
    return [s for s in engine.option_sets() if not s["key"].startswith("don:")]


def options_missing(engine) -> int:
    return sum(max(0, s["total"] - len(s["chosen"])) for s in class_option_sets(engine))


class OptionSetsPanel(QWidget):
    """Une liste déroulante par choix ; une option déjà prise est retirée des autres listes du même ensemble.
    `keys` : ne montrer que ces ensembles (None = tous) ; `on_change` est appelé après chaque choix."""

    def __init__(self, engine_getter: Callable, on_change: Callable[[], None], keys=None,
                 locked: Optional[Callable[[str], set]] = None):
        super().__init__()
        self._engine = engine_getter
        self._on_change = on_change
        self.keys = keys
        self.locked = locked                             # v52 : choix d'avant ce niveau (non modifiables ici)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self._key = None
        self.combos: dict[tuple[str, int], QComboBox] = {}

    def sets(self) -> list[dict]:
        keys = self.keys() if callable(self.keys) else self.keys    # clés fixes ou calculées à chaque rafraîchissement
        if keys is None:                                 # par défaut : choix de classe (sans les dons)
            return class_option_sets(self._engine())
        return [s for s in self._engine().option_sets() if s["key"] in keys]   # clés données : dons compris

    def refresh(self) -> None:
        sets = self.sets()
        self.setVisible(bool(sets))
        key = tuple((s["key"], s["total"], tuple(s["options"]), tuple(s["chosen"])) for s in sets)
        if key == self._key:
            return
        self._key = key
        clear_layout(self.grid)
        self.combos = {}
        row = 0
        for s in sets:
            self.grid.addWidget(make_label("{} — {} / {}".format(s["label"], len(s["chosen"]), s["total"]), "head"),
                                row, 0, 1, 2)
            row += 1
            for i in range(s["total"]):
                current = s["chosen"][i] if i < len(s["chosen"]) else ""
                taken = {c for j, c in enumerate(s["chosen"]) if j != i}
                names = [n for n in s["options"] if n not in taken]
                combo = QComboBox()
                combo.setMinimumWidth(280)
                fill_combo(combo, [NO_OPTION] + names, current or NO_OPTION,
                           {n: rich_tip(n, s["options"][n]) for n in names})
                combo.activated.connect(lambda _=0, k=s["key"], idx=i, c=combo: self.choose(k, idx, c.currentText()))
                if self.locked is not None and current and current in self.locked(s["key"]):
                    combo.setEnabled(False)
                    combo.setToolTip("Choix d'un niveau précédent (voir « Remplacer un choix » si la règle le permet).")
                self.combos[(s["key"], i)] = combo
                desc = make_label((s["options"].get(current, "") or "").split("\n")[0], "muted", wrap=True)
                self.grid.addWidget(combo, row, 0)
                self.grid.addWidget(desc, row, 1)
                row += 1
        self.grid.setColumnStretch(1, 1)

    def choose(self, key: str, index: int, name: str) -> None:
        self._engine().set_class_option(key, index, "" if name == NO_OPTION else name)
        self._key = None
        self._on_change()
        self.refresh()


def reminders_html(engine, accent: str, warn: str) -> str:
    """Rappels de l'onglet Classes : choix faits (description au survol impossible en HTML : texte court) et
    choix restants."""
    out = []
    for s in class_option_sets(engine):
        missing = s["total"] - len(s["chosen"])
        chosen = ", ".join(html.escape(c) for c in s["chosen"]) or "—"
        line = "<b style='color:{}'>{}</b> ({}/{}) : {}".format(accent, html.escape(s["label"]), len(s["chosen"]),
                                                                 s["total"], chosen)
        if missing > 0:
            line += " <b style='color:{}'>— ○ {} à choisir</b>".format(warn, missing)
        out.append(line)
    return "<br/>".join(out)


def ask_class_options(parent, engine, on_change: Callable[[], None]) -> None:
    """Fenêtre de rattrapage : choix de classe manquants d'une fiche existante."""
    dlg = QDialog(parent)
    dlg.setWindowTitle("Choix de classe à faire")
    lay = QVBoxLayout(dlg)
    lay.addWidget(make_label("Ces choix se font normalement pendant la montée de niveau. Complétez ici ceux qui "
                             "manquent sur cette fiche.", "muted", wrap=True))
    panel = OptionSetsPanel(lambda: engine, on_change)
    panel.refresh()
    lay.addWidget(panel)
    box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    box.rejected.connect(dlg.reject)
    box.accepted.connect(dlg.accept)
    lay.addWidget(box)
    dlg.resize(760, 420)
    dlg.exec()
