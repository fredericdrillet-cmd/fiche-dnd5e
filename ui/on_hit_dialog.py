"""Fenêtre « Quand vous touchez » (v52) : bonus de dégâts à cocher avant de lancer les dégâts."""
from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QComboBox, QDialog, QHBoxLayout, QPushButton, QVBoxLayout

from .common import make_label, rich_tip

NO_SMITE = "Pas de Châtiment"


class OnHitDialog(QDialog):
    """Cases à cocher (toutes décochées) ; le Châtiment est une liste (un seul niveau par coup)."""

    def __init__(self, win, title: str, options: list[dict], crit: bool = False, hit_question: str = ""):
        super().__init__(win)
        self.setWindowTitle("L'attaque touche-t-elle ?" if hit_question else "L'attaque touche : bonus de dégâts")
        self.options = options
        lay = QVBoxLayout(self)
        lay.addWidget(make_label(title + (" — coup critique : tous les dés seront doublés." if crit else ""), "head",
                                 wrap=True))
        if hit_question:                                 # v53 : question « touche ? » et bonus dans une seule fenêtre
            lay.addWidget(make_label(hit_question, "", wrap=True))
        lay.addWidget(make_label("Si l'attaque touche, cochez les bonus à ajouter aux dégâts (le coût n'est dépensé "
                                 "qu'en validant « Touché ») :" if hit_question else
                                 "Cochez ce qui s'applique à ce coup (coût dépensé à la validation) :", "muted",
                                 wrap=True))
        self.checks: dict[str, QCheckBox] = {}
        smites = [o for o in options if o.get("groupe") == "chatiment"]
        for o in options:
            if o.get("groupe") == "chatiment":
                continue
            cb = QCheckBox("{} : +{}{}".format(o["label"], o["dice"], " — " + o["cout"] if o["cout"] else ""))
            cb.setToolTip(rich_tip(o["label"], "+{} aux dégâts{}.".format(o["dice"], (" (" + o["cout"] + ")")
                                                                         if o["cout"] else "")))
            lay.addWidget(cb)
            self.checks[o["key"]] = cb
        self.smite = None
        if smites:
            row = QHBoxLayout()
            row.addWidget(make_label("⚡ Châtiment divin :"))
            self.smite = QComboBox()
            self.smite.addItem(NO_SMITE, "")
            for o in smites:
                self.smite.addItem("{} : +{} ({})".format(o["label"], o["dice"], o["cout"]), o["key"])
            row.addWidget(self.smite, 1)
            lay.addLayout(row)
        btns = QHBoxLayout()
        btns.addStretch(1)
        ok = QPushButton("✔ Touché : lancer les dégâts" if hit_question else "🎲 Lancer les dégâts")
        ok.setDefault(True)
        ok.clicked.connect(lambda: self.done(1))
        cancel = QPushButton("✘ Raté" if hit_question else "Annuler")
        cancel.setProperty("role", "ghost")
        cancel.clicked.connect(lambda: self.done(0))
        btns.addWidget(cancel)
        btns.addWidget(ok)
        lay.addLayout(btns)

    def chosen(self) -> list[str]:
        keys = [k for k, cb in self.checks.items() if cb.isChecked()]
        if self.smite is not None and self.smite.currentData():
            keys.append(self.smite.currentData())
        return keys


def ask_hit(win, title: str, question: str, options: list[dict], crit: bool = False):
    """v53 : « L'attaque touche-t-elle ? » ET les bonus au toucher (Attaque sournoise, Châtiment, manœuvre, dé psi…)
    dans une seule fenêtre. None = raté ; sinon la liste des bonus cochés."""
    dlg = OnHitDialog(win, title, options, crit, hit_question=question)
    return dlg.chosen() if dlg.exec() else None


def ask_on_hit(win, title: str, options: list[dict], crit: bool = False):
    """Liste des clés choisies, ou None si annulé ; [] sans fenêtre quand il n'y a rien à proposer."""
    if not options:
        return []
    dlg = OnHitDialog(win, title, options, crit)
    return dlg.chosen() if dlg.exec() else None
