"""Fenêtre « 🌪 Environnement » (v52) : chute (dégâts, À terre, Chute ralentie, Feuille morte) et suffocation."""
from __future__ import annotations

from PyQt6.QtWidgets import (QCheckBox, QDialog, QDoubleSpinBox, QHBoxLayout, QPushButton, QTabWidget, QVBoxLayout,
                             QWidget)

from core import dice as D
from .common import make_label
from .dice_dialog import roll_damage_dialog


class EnvironmentDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.eng = win.engine
        self.result_text = ""
        self.setWindowTitle("🌪 Environnement")
        lay = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._fall_tab(), "🪂 Chute")
        tabs.addTab(self._breath_tab(), "🫧 Suffocation")
        lay.addWidget(tabs)
        close = QPushButton("Fermer")
        close.setProperty("role", "ghost")
        close.clicked.connect(self.reject)
        lay.addWidget(close)

    # ------------------------------------------------------------------ chute
    def _fall_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(make_label("1d6 contondants par tranche de 3 m (20d6 au plus), puis À terre.", "muted",
                                 wrap=True))
        row = QHBoxLayout()
        row.addWidget(make_label("Hauteur"))
        self.height = QDoubleSpinBox()
        self.height.setRange(0, 600)
        self.height.setSingleStep(3)
        self.height.setDecimals(1)
        self.height.setSuffix(" m")
        self.height.setValue(6)
        row.addWidget(self.height)
        self.fall_formula = make_label("", "head")
        row.addWidget(self.fall_formula, 1)
        lay.addLayout(row)
        red = self.eng.slow_fall_reduction()
        self.slow = QCheckBox("Chute ralentie (réaction) : −{} dégâts".format(red))
        self.slow.setVisible(bool(red))
        self.slow.setChecked(bool(red))
        lay.addWidget(self.slow)
        self.feather = QCheckBox("Feuille morte (sort) : aucun dégât")
        lay.addWidget(self.feather)
        self.fall_btn = QPushButton("🎲 Lancer les dégâts de chute")
        self.fall_btn.clicked.connect(self._on_fall)
        lay.addWidget(self.fall_btn)
        self.height.valueChanged.connect(lambda _=0: self._refresh_fall())
        self._refresh_fall()
        return w

    def _refresh_fall(self) -> None:
        f = self.eng.fall_formula(self.height.value())
        self.fall_formula.setText(f or "moins de 3 m : aucun dégât")
        self.fall_btn.setEnabled(bool(f))

    def _on_fall(self) -> None:
        h = self.height.value()
        if self.feather.isChecked():
            self.result_text = self.eng.apply_fall(0, h, feather=True)
            self.accept()
            return
        r = roll_damage_dialog(self.win, D.DamageSpec("Chute de {:g} m".format(h), self.eng.fall_formula(h),
                                                      "contondants"))
        if r is None:
            return
        self.result_text = self.eng.apply_fall(r.total, h, slow_fall=self.slow.isChecked())
        self.accept()

    # ------------------------------------------------------------------ suffocation
    def _breath_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        e = self.eng
        rule = ("2024 : un niveau d'épuisement à la fin de chacun de vos tours, tous retirés quand vous respirez."
                if e.sheet_edition == 2024 else
                "2014 : vous survivez {} round(s), puis tombez à 0 PV.".format(e.suffocation_rounds_2014()))
        lay.addWidget(make_label("Souffle retenu : {} rounds (1 + Constitution minutes, 30 secondes au moins). "
                                 "Ensuite, vous suffoquez — {}".format(e.breath_rounds(), rule), "muted", wrap=True))
        for text, slot in (("🫧 Retenir son souffle", e.hold_breath), ("😶‍🌫️ Suffoquer maintenant (étranglé…)",
                                                                       e.start_suffocating),
                           ("🌬 Respirer à nouveau", e.breathe_again)):
            b = QPushButton(text)
            b.clicked.connect(lambda _=False, s=slot: self._done(s()))
            lay.addWidget(b)
        return w

    def _done(self, text: str) -> None:
        self.result_text = text
        self.accept()
