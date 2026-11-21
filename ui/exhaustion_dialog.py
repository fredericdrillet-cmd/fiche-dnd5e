"""Fenêtre « 🎲 JS d'épuisement » (v52) : cause, DD officiel, JS de Constitution, un niveau sur un échec."""
from __future__ import annotations

from PyQt6.QtWidgets import QComboBox, QDialog, QGridLayout, QHBoxLayout, QPushButton, QSpinBox, QVBoxLayout

from .common import make_label
from .dice_dialog import roll_dice


class ExhaustionDialog(QDialog):
    def __init__(self, win, cause: str = "marche"):
        super().__init__(win)
        self.win = win
        self.eng = win.engine
        self.result_text = ""
        self.setWindowTitle("🎲 JS d'épuisement")
        self.causes = self.eng.exhaustion_causes()
        lay = QVBoxLayout(self)
        lay.addWidget(make_label(self.eng.exhaustion_text(), "head", wrap=True))
        grid = QGridLayout()
        grid.addWidget(make_label("Cause"), 0, 0)
        self.cause = QComboBox()
        self.cause.addItems([c[1] for c in self.causes])
        ids = [c[0] for c in self.causes]
        self.cause.setCurrentIndex(ids.index(cause) if cause in ids else 0)
        grid.addWidget(self.cause, 0, 1)
        self.hours_label = make_label("Heures")
        grid.addWidget(self.hours_label, 1, 0)
        self.hours = QSpinBox()
        self.hours.setRange(1, 24)
        grid.addWidget(self.hours, 1, 1)
        grid.addWidget(make_label("DD"), 2, 0)
        self.dc = QSpinBox()
        self.dc.setRange(1, 40)
        self.dc.setValue(10)
        grid.addWidget(self.dc, 2, 1)
        lay.addLayout(grid)
        self.rule = make_label("", "muted", wrap=True)
        lay.addWidget(self.rule)
        row = QHBoxLayout()
        self.roll_btn = QPushButton("🎲 Lancer le JS de Constitution")
        self.fail_btn = QPushButton("＋ Un niveau sans jet")
        self.fail_btn.setProperty("role", "ghost")
        close = QPushButton("Fermer")
        close.setProperty("role", "ghost")
        for b in (self.roll_btn, self.fail_btn, close):
            row.addWidget(b)
        lay.addLayout(row)
        self.cause.currentIndexChanged.connect(lambda _=0: self._refresh())
        self.hours.valueChanged.connect(lambda _=0: self._refresh(keep_dc=False))
        self.roll_btn.clicked.connect(self._on_roll)
        self.fail_btn.clicked.connect(self._on_fail)
        close.clicked.connect(self.reject)
        self._refresh()

    def cause_id(self) -> str:
        return self.causes[self.cause.currentIndex()][0]

    def _refresh(self, keep_dc: bool = False) -> None:
        cid = self.cause_id()
        self.rule.setText(self.causes[self.cause.currentIndex()][2])
        timed = cid in ("marche", "chaleur")
        self.hours.setVisible(timed)
        self.hours_label.setVisible(timed)
        self.hours_label.setText("Heures au-delà de 8" if cid == "marche" else "Heure n°")
        if cid != "autre" and not keep_dc:
            self.dc.setValue(self.eng.exhaustion_dc(cid, self.hours.value(), self.dc.value()))
        self.dc.setEnabled(cid == "autre")
        self.roll_btn.setEnabled(cid != "nourriture")

    def _on_roll(self) -> None:
        dc = self.dc.value()
        r = roll_dice(self.win, self.eng.exhaustion_save_spec(self.cause_id(), dc))
        if r is None:
            return
        self.result_text = self.eng.apply_exhaustion_save(r.total, dc)
        self.accept()

    def _on_fail(self) -> None:
        self.result_text = self.eng.gain_exhaustion(self.cause.currentText())
        self.accept()
