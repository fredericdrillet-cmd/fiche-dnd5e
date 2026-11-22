"""Fenêtres « 💥 Dégâts » et « 💚 Soins » (v52) : le montant est demandé après le clic."""
from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QComboBox, QDialog, QGridLayout, QHBoxLayout, QPushButton, QSpinBox, QVBoxLayout

from core.engine_extras import ExtrasMixin
from .common import make_label


class DamageDialog(QDialog):
    """Montant, type de dégâts, « magique » ; l'aperçu applique résistances, immunités et réductions."""

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.eng = win.engine
        self.setWindowTitle("💥 Dégâts subis")
        lay = QVBoxLayout(self)
        grid = QGridLayout()
        grid.addWidget(make_label("Dégâts subis"), 0, 0)
        self.amount = QSpinBox()
        self.amount.setRange(0, 999)
        grid.addWidget(self.amount, 0, 1)
        grid.addWidget(make_label("Type"), 1, 0)
        self.dtype = QComboBox()
        self.dtype.addItems(["— (non précisé)"] + [t.capitalize() for t in ExtrasMixin.DAMAGE_TYPES])
        grid.addWidget(self.dtype, 1, 1)
        self.magic = QCheckBox("Arme ou attaque magique")
        grid.addWidget(self.magic, 2, 1)
        lay.addLayout(grid)
        self.preview = make_label("", "head", wrap=True)
        lay.addWidget(self.preview)
        row = QHBoxLayout()
        row.addStretch(1)
        cancel = QPushButton("Annuler")
        cancel.setProperty("role", "ghost")
        cancel.clicked.connect(self.reject)
        self.ok_btn = QPushButton("💥 Subir les dégâts")
        self.ok_btn.clicked.connect(self.accept)
        row.addWidget(cancel)
        row.addWidget(self.ok_btn)
        lay.addLayout(row)
        self.amount.valueChanged.connect(lambda _=0: self._refresh())
        self.dtype.currentIndexChanged.connect(lambda _=0: self._refresh())
        self.magic.toggled.connect(lambda _=False: self._refresh())
        self._refresh()
        self.amount.setFocus()
        self.amount.selectAll()

    def values(self) -> tuple[int, str, bool]:
        i = self.dtype.currentIndex()
        return self.amount.value(), ExtrasMixin.DAMAGE_TYPES[i - 1] if i > 0 else "", self.magic.isChecked()

    def _refresh(self) -> None:
        amount, dtype, magical = self.values()
        after, notes = self.eng.damage_after_defenses(amount, dtype, magical)
        if notes:
            self.preview.setText("{} {} → {} PV perdus ({}).".format(amount, dtype, after, " ; ".join(notes)))
        else:
            self.preview.setText("{} PV perdus.".format(after) if amount else "Saisissez les dégâts reçus.")
        self.ok_btn.setEnabled(amount > 0)


class HealDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("💚 Soins reçus")
        lay = QVBoxLayout(self)
        grid = QGridLayout()
        grid.addWidget(make_label("PV regagnés"), 0, 0)
        self.amount = QSpinBox()
        self.amount.setRange(0, 999)
        grid.addWidget(self.amount, 0, 1)
        self.temp = QCheckBox("PV temporaires (ne se cumulent pas : on garde le plus élevé)")
        grid.addWidget(self.temp, 1, 0, 1, 2)
        lay.addLayout(grid)
        row = QHBoxLayout()
        row.addStretch(1)
        cancel = QPushButton("Annuler")
        cancel.setProperty("role", "ghost")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("💚 Appliquer")
        ok.clicked.connect(self.accept)
        row.addWidget(cancel)
        row.addWidget(ok)
        lay.addLayout(row)
        self.amount.setFocus()
        self.amount.selectAll()

    def values(self) -> tuple[int, bool]:
        return self.amount.value(), self.temp.isChecked()
