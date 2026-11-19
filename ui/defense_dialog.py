"""Fenêtre « 🛡 On m'attaque ! » (v52) : jet de l'ennemi contre votre CA, réactions défensives, puis dégâts."""
from __future__ import annotations

from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QGridLayout, QHBoxLayout, QPushButton, QSpinBox,
                             QVBoxLayout, QWidget)

from core.engine_extras import ExtrasMixin
from .common import make_label, rich_tip


class DefenseDialog(QDialog):
    """Étape « attaque » (jet ennemi, réactions qui changent le résultat) puis « dégâts » (réactions qui
    réduisent, type de dégâts, « Subir les dégâts »). `start` = "degats" depuis la saisie rapide des PV."""

    def __init__(self, win, start: str = "attaque", amount: int = 0, dtype: str = "", magical: bool = False):
        super().__init__(win)
        self.win = win
        self.eng = win.engine
        self.setWindowTitle("🛡 On m'attaque !")
        self.effects: list[dict] = []          # réactions appliquées
        self.ca_bonus = 0
        self.malus = 0
        self.result_text = ""
        lay = QVBoxLayout(self)
        # --- étape 1 : le jet d'attaque
        self.attack_box = QWidget()
        al = QGridLayout(self.attack_box)
        al.addWidget(make_label("Jet d'attaque de l'ennemi (total)"), 0, 0)
        self.atk = QSpinBox()
        self.atk.setRange(-10, 60)
        self.atk.setValue(10)
        self.atk.valueChanged.connect(lambda _=0: self._refresh())
        al.addWidget(self.atk, 0, 1)
        self.crit = QCheckBox("20 naturel (coup critique)")
        self.crit.toggled.connect(lambda _=False: self._refresh())
        al.addWidget(self.crit, 0, 2)
        self.hit_label = make_label("", "head", wrap=True)
        al.addWidget(self.hit_label, 1, 0, 1, 3)
        self.atk_reacts = QVBoxLayout()
        al.addLayout(self.atk_reacts, 2, 0, 1, 3)
        lay.addWidget(self.attack_box)
        # --- étape 2 : les dégâts
        self.dmg_box = QWidget()
        dl = QGridLayout(self.dmg_box)
        dl.addWidget(make_label("Dégâts reçus"), 0, 0)
        self.dmg = QSpinBox()
        self.dmg.setRange(0, 999)
        self.dmg.setValue(int(amount))
        self.dmg.valueChanged.connect(lambda _=0: self._refresh())
        dl.addWidget(self.dmg, 0, 1)
        self.dtype = QComboBox()
        self.dtype.addItems(["Type : —"] + [t.capitalize() for t in ExtrasMixin.DAMAGE_TYPES])
        if dtype in ExtrasMixin.DAMAGE_TYPES:
            self.dtype.setCurrentIndex(ExtrasMixin.DAMAGE_TYPES.index(dtype) + 1)
        self.dtype.activated.connect(lambda _=0: self._refresh())
        dl.addWidget(self.dtype, 0, 2)
        self.magic = QCheckBox("magique")
        self.magic.setChecked(bool(magical))
        self.magic.toggled.connect(lambda _=False: self._refresh())
        dl.addWidget(self.magic, 0, 3)
        self.range = QComboBox()
        self.range.addItems(["Attaque au corps à corps", "Attaque à distance", "Sort ou autre effet"])
        self.range.activated.connect(lambda _=0: self._rebuild_damage_reacts())
        dl.addWidget(self.range, 1, 0, 1, 2)
        self.dmg_label = make_label("", "head", wrap=True)
        dl.addWidget(self.dmg_label, 2, 0, 1, 4)
        self.dmg_reacts = QVBoxLayout()
        dl.addLayout(self.dmg_reacts, 3, 0, 1, 4)
        lay.addWidget(self.dmg_box)
        self.log = make_label("", "muted", wrap=True)
        lay.addWidget(self.log)
        btns = QHBoxLayout()
        btns.addStretch(1)
        self.miss_btn = QPushButton("✔ L'attaque rate")
        self.miss_btn.clicked.connect(self._on_miss)
        self.take_btn = QPushButton("💥 Subir les dégâts")
        self.take_btn.clicked.connect(self._on_take)
        close = QPushButton("Annuler")
        close.setProperty("role", "ghost")
        close.clicked.connect(lambda: self.done(0))
        for b in (close, self.miss_btn, self.take_btn):
            btns.addWidget(b)
        lay.addLayout(btns)
        self.stage = start
        if start == "degats":
            self.attack_box.setVisible(False)
        self._rebuild_attack_reacts()
        self._rebuild_damage_reacts()
        self._refresh()

    # ------------------------------------------------------------------ état
    def _melee(self):
        i = self.range.currentIndex()
        return True if i == 0 else False if i == 1 else None

    def touches(self) -> bool:
        if self.stage == "degats" and not self.attack_box.isVisible():
            return True
        chk = self.eng.attack_check(self.atk.value() - self.malus, self.crit.isChecked())
        return chk["touche"] if self.crit.isChecked() else chk["total"] >= chk["ca"] + self.ca_bonus

    def final_damage(self) -> tuple[int, str]:
        amount = self.eng.damage_after_reactions(self.dmg.value(), self.effects)
        idx = self.dtype.currentIndex()
        dtype = ExtrasMixin.DAMAGE_TYPES[idx - 1] if idx > 0 else ""
        after, notes = self.eng.damage_after_defenses(amount, dtype, self.magic.isChecked())
        return after, " ; ".join(notes)

    def _refresh(self) -> None:
        ca = self.eng.attack_check(0)["ca"] + self.ca_bonus
        total = self.atk.value() - self.malus
        hit = self.touches()
        self.hit_label.setText("Votre CA : {} — jet {}{} : {}".format(
            ca, total, " (−{} réaction)".format(self.malus) if self.malus else "",
            "<b>l'attaque touche</b>" if hit else "<b>l'attaque rate</b>"))
        after, notes = self.final_damage()
        self.dmg_label.setText("Vous perdrez {} PV{}".format(after, " ({})".format(notes) if notes else ""))
        self.miss_btn.setVisible(not hit)
        self.dmg_box.setEnabled(hit)
        self.take_btn.setEnabled(hit)

    def _clear(self, lay) -> None:
        while lay.count():
            item = lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _rebuild_attack_reacts(self) -> None:
        self._clear(self.atk_reacts)
        opts = self.eng.defense_options("attaque") if self.stage == "attaque" else []
        if opts:
            self.atk_reacts.addWidget(make_label("Réactions possibles avant les dégâts :", "muted"))
        for o in opts:
            b = QPushButton("◆ {} — {}".format(o["label"], o["cout"]) if o["cout"] else "◆ " + o["label"])
            b.setToolTip(rich_tip(o["label"], "Utilise votre réaction de ce round."))
            b.clicked.connect(lambda _=False, opt=o: self._use(opt))
            self.atk_reacts.addWidget(b)

    def _rebuild_damage_reacts(self) -> None:
        self._clear(self.dmg_reacts)
        opts = self.eng.defense_options("degats", melee=self._melee())
        if opts:
            self.dmg_reacts.addWidget(make_label("Réactions qui réduisent les dégâts :", "muted"))
        for o in opts:
            b = QPushButton("◆ " + o["label"])
            b.clicked.connect(lambda _=False, opt=o: self._use(opt))
            self.dmg_reacts.addWidget(b)
        self._refresh()

    # ------------------------------------------------------------------ actions
    def _use(self, option: dict) -> None:
        res = self.eng.use_defense(option)
        if not res["ok"]:
            self.log.setText(res["message"])
            return
        self.ca_bonus += res["ca"]
        self.malus += res["malus"]
        if res["moitie"] or res["reduction"]:
            self.effects.append(res)
        self.log.setText((self.log.text() + "\n" if self.log.text() else "") + res["message"])
        self._rebuild_attack_reacts()                    # réaction utilisée : plus de proposition
        self._rebuild_damage_reacts()
        self._refresh()

    def _on_miss(self) -> None:
        self.result_text = "L'attaque rate." + (" " + self.log.text().replace("\n", " ") if self.log.text() else "")
        self.done(1)

    def _on_take(self) -> None:
        after, notes = self.final_damage()
        self.result_text = ("{} — ".format(notes) if notes else "") + self.eng.take_damage(after)
        self.done(1)
