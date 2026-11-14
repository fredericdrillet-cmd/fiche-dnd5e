"""
Fenêtre « Bottes d'arme » (v52) : choix des armes dont la botte (maîtrise d'arme 2024) s'applique.

Fiche 2024 : autant d'armes que l'aptitude le permet (table de la classe) ; le choix peut changer à chaque repos long.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QDialog, QFrame, QHBoxLayout, QPushButton, QScrollArea, QVBoxLayout, QWidget

from .common import make_label


class MasteryDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        eng = win.engine
        self.setWindowTitle("Bottes d'arme")
        self.setMinimumWidth(520)
        self.count = eng.mastery_count() or 0
        current = set(eng.mastery_weapons() or [])
        root = QVBoxLayout(self)
        root.addWidget(make_label("Choisissez {} arme(s) maîtrisée(s) : leur botte s'applique. Vous pouvez changer "
                                  "ce choix à chaque repos long.".format(self.count), "muted", wrap=True))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)
        self.checks: dict[str, QCheckBox] = {}
        for name in eng.mastery_candidates():
            w = eng.db.weapons[name]
            cb = QCheckBox("{} — {}".format(name, w.get("botte", "")))
            cb.setToolTip(w.get("botte_desc", ""))
            cb.setChecked(name in current)
            cb.toggled.connect(lambda _=False: self._update())
            self.checks[name] = cb
            lay.addWidget(cb)
        self.status = make_label("", "muted")
        root.addWidget(self.status)
        row = QHBoxLayout()
        row.addStretch(1)
        cancel = QPushButton("Annuler")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Appliquer")
        ok.clicked.connect(self.accept)
        row.addWidget(cancel)
        row.addWidget(ok)
        root.addLayout(row)
        self._update()

    def selected(self) -> list[str]:
        return [n for n, cb in self.checks.items() if cb.isChecked()]

    def _update(self) -> None:
        n = len(self.selected())
        self.status.setText("{} / {} botte(s) choisie(s){}".format(
            n, self.count, " — trop d'armes cochées" if n > self.count else ""))
        for cb in self.checks.values():                      # limite atteinte : les autres cases se grisent
            cb.setEnabled(cb.isChecked() or n < self.count)

    def accept(self) -> None:
        self.win.engine.ch.bottes_choisies = self.selected()[:self.count]
        if hasattr(self.win, "changed"):
            self.win.changed()
        self.done(1)
