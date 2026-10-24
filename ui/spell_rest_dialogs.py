"""
Fenêtres de gestion des sorts ouvertes depuis la fenêtre de Repos long (v44).

- « Changer les sorts préparés » (Clerc, Druide, Paladin — aussi Artificier et Magicien) : liste cochable de toute
  la liste de classe (ou du grimoire du Magicien), filtres (recherche, niveau, école, Rituel, Concentration),
  jauge « Préparés : n / maximum » avec la formule (niveau de classe + modificateur), sorts de domaine / serment /
  cercle rappelés « toujours préparés ». Au-delà du quota, la case refuse de se cocher (message en rouge).
- « Changer un tour de magie » (Magicien, Tasha — Formules de sorts mineurs) : tour de magie à oublier, nouveau
  tour de magie de la liste du Magicien, aperçu des deux textes.

Les deux fenêtres ne modifient rien elles-mêmes : la fenêtre de repos garde le choix et l'applique à la fin du
repos (« Se reposer ») ; « Annuler » le repos annule tout.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout,
                             QLineEdit, QListWidget, QListWidgetItem, QProgressBar, QPushButton, QVBoxLayout)

from core.levelup import SCHOOLS, filter_spells
from .common import blocked, make_label, rich_tip

ALL_LEVELS = "Tous les niveaux"
ALL_SCHOOLS = "Toutes les écoles"
NO_CANTRIP = "— à choisir —"


def _card_dialog(dialog: QDialog, title: str):
    """Carte « jeu vidéo » (sans bordure, ombre portée) commune aux fenêtres de repos. Renvoie le layout."""
    dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
    dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    dialog.setModal(True)
    outer = QVBoxLayout(dialog)
    outer.setContentsMargins(26, 26, 26, 30)
    card = QFrame()
    card.setObjectName("dialogCard")
    shadow = QGraphicsDropShadowEffect(card)
    shadow.setBlurRadius(38)
    shadow.setOffset(0, 8)
    shadow.setColor(QColor(0, 0, 0, 175))
    card.setGraphicsEffect(shadow)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(28, 24, 28, 22)
    lay.setSpacing(10)
    outer.addWidget(card)
    lay.addWidget(make_label(title, "title"))
    return lay


def _buttons(dialog: QDialog, lay, ok_text: str):
    row = QHBoxLayout()
    row.addStretch(1)
    cancel = QPushButton("Annuler")
    cancel.setProperty("role", "ghost")
    ok = QPushButton(ok_text)
    for b in (cancel, ok):
        b.setMinimumWidth(140)
        row.addWidget(b)
    ok.setDefault(True)
    cancel.clicked.connect(dialog.reject)
    ok.clicked.connect(dialog.accept)
    lay.addLayout(row)
    return ok


def spell_label(sp: dict) -> str:
    tags = "".join(x for x, on in ((" Ⓒ", sp.get("concentration")), (" ᴿ", sp.get("rituel"))) if on)
    return "{} — {} ({}){}".format(sp["nom"], "tour de magie" if not sp.get("niveau") else
                                   "niveau {}".format(sp["niveau"]), sp.get("ecole", ""), tags)


class PrepareSpellsDialog(QDialog):
    """Modale « Changer les sorts préparés » : `selected` = liste des sorts cochés."""

    def __init__(self, parent, info: dict, current=None):
        super().__init__(parent)
        self.info = info
        self.selected: list[str] = list(current if current is not None else info["prepares"])
        self.resize(860, 720)
        lay = _card_dialog(self, "📖  Changer les sorts préparés — {}".format(info["classe"]))
        lay.addWidget(make_label("Choisissez les sorts préparés pour la journée à venir. Limite : {} = <b>{}</b> "
                                 "sort(s) de niveau 1 ou plus.".format(html.escape(info["formule"]), info["maximum"]),
                                 "muted", wrap=True))
        if info["toujours"]:
            lay.addWidget(make_label("✦ Toujours préparés (sous-classe, hors quota) : " +
                                     html.escape(", ".join(info["toujours"])), "", wrap=True))
        gauge = QHBoxLayout()
        self.count = make_label("", "head")
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(10)
        self.bar.setRange(0, max(1, info["maximum"]))
        gauge.addWidget(self.count)
        gauge.addWidget(self.bar, 1)
        lay.addLayout(gauge)
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher un sort…")
        self.level = QComboBox()
        levels = sorted({int(sp.get("niveau") or 0) for sp in info["candidats"]})
        self.level.addItems([ALL_LEVELS] + ["Niveau {}".format(n) for n in levels])
        self.school = QComboBox()
        self.school.addItems([ALL_SCHOOLS] + SCHOOLS)
        self.ritual = QCheckBox("Rituel (R)")
        self.conc = QCheckBox("Concentration (C)")
        for w, stretch in ((self.search, 2), (self.level, 1), (self.school, 1), (self.ritual, 0), (self.conc, 0)):
            filters.addWidget(w, stretch)
        lay.addLayout(filters)
        self.only = QCheckBox("Afficher seulement les sorts préparés")
        lay.addWidget(self.only)
        self.list = QListWidget()
        self.list.setMinimumHeight(320)
        lay.addWidget(self.list, 1)
        self.warn = make_label("", "warn", wrap=True)
        lay.addWidget(self.warn)
        self.ok_btn = _buttons(self, lay, "✔ Valider la préparation")
        self.search.textChanged.connect(lambda _t="": self.refresh())
        for combo in (self.level, self.school):
            combo.currentIndexChanged.connect(lambda _i=0: self.refresh())
        for box in (self.ritual, self.conc, self.only):
            box.toggled.connect(lambda _b=False: self.refresh())
        self.list.itemChanged.connect(self._on_item)
        self.refresh()

    # ------------------------------------------------------------------ logique
    def visible_spells(self) -> list[dict]:
        txt = self.level.currentText()
        lvl = None if txt == ALL_LEVELS or not txt.startswith("Niveau ") else int(txt.split()[-1])
        school = "" if self.school.currentText() == ALL_SCHOOLS else self.school.currentText()
        rows = filter_spells(self.info["candidats"], lvl, school, bool(self.ritual.isChecked()),
                             bool(self.conc.isChecked()), self.search.text())
        if self.only.isChecked():
            rows = [sp for sp in rows if sp["nom"] in self.selected]
        return rows

    def toggle(self, name: str, on: bool) -> bool:
        """Coche / décoche ; refuse au-delà du quota. Renvoie True si l'état a changé."""
        if on and name not in self.selected:
            if len(self.selected) >= self.info["maximum"]:
                self.warn.setText("Limite atteinte : {} / {} sorts préparés. Décochez d'abord un sort.".format(
                    len(self.selected), self.info["maximum"]))
                return False
            self.selected.append(name)
        elif not on and name in self.selected:
            self.selected.remove(name)
        else:
            return False
        self.warn.setText("")
        self._update_gauge()
        return True

    def _on_item(self, item) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        on = item.checkState() == Qt.CheckState.Checked
        if not self.toggle(name, on):
            with blocked(self.list):
                item.setCheckState(Qt.CheckState.Checked if name in self.selected else Qt.CheckState.Unchecked)

    def _update_gauge(self) -> None:
        n, mx = len(self.selected), self.info["maximum"]
        self.count.setText("Préparés : {} / {}".format(n, mx))
        self.bar.setValue(min(n, max(1, mx)))
        self.ok_btn.setEnabled(n <= mx)

    def refresh(self) -> None:
        with blocked(self.list):
            self.list.clear()
            for sp in self.visible_spells():
                it = QListWidgetItem(spell_label(sp))
                it.setData(Qt.ItemDataRole.UserRole, sp["nom"])
                it.setToolTip(rich_tip(sp["nom"], sp.get("description", "")))
                it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                it.setCheckState(Qt.CheckState.Checked if sp["nom"] in self.selected else Qt.CheckState.Unchecked)
                self.list.addItem(it)
        self._update_gauge()


class CantripSwapDialog(QDialog):
    """Modale « Changer un tour de magie » (Magicien, Tasha) : `choice()` = (ancien, nouveau) ou None."""

    def __init__(self, parent, known: list[dict], options: list[dict]):
        super().__init__(parent)
        self.known = {sp["nom"]: sp for sp in known}
        self.options = {sp["nom"]: sp for sp in options}
        self.old, self.new = "", ""
        self.resize(720, 560)
        lay = _card_dialog(self, "✨  Changer un tour de magie — Magicien")
        lay.addWidget(make_label("Formules de sorts mineurs (Tasha) : à la fin d'un repos long, vous pouvez remplacer "
                                 "un tour de magie du Magicien que vous connaissez par un autre tour de magie de la "
                                 "liste du Magicien.", "muted", wrap=True))
        lay.addWidget(make_label("1. Tour de magie à oublier", "head"))
        self.old_combo = QComboBox()
        lay.addWidget(self.old_combo)
        self.old_text = make_label("", "muted", wrap=True)
        lay.addWidget(self.old_text)
        lay.addWidget(make_label("2. Nouveau tour de magie", "head"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher un tour de magie…")
        lay.addWidget(self.search)
        self.new_combo = QComboBox()
        lay.addWidget(self.new_combo)
        self.new_text = make_label("", "muted", wrap=True)
        lay.addWidget(self.new_text)
        self.summary = make_label("", "head", wrap=True)
        lay.addWidget(self.summary)
        lay.addStretch(1)
        self.ok_btn = _buttons(self, lay, "✔ Échanger")
        self._fill(self.old_combo, list(self.known))
        self._fill(self.new_combo, list(self.options))
        self.old_combo.currentIndexChanged.connect(lambda _i=0: self.set_old(self.old_combo.currentText()))
        self.new_combo.currentIndexChanged.connect(lambda _i=0: self.set_new(self.new_combo.currentText()))
        self.search.textChanged.connect(self._filter)
        self._update()

    def _fill(self, combo, names: list[str]) -> None:
        pool = {**self.known, **self.options}
        with blocked(combo):
            combo.clear()
            combo.addItem(NO_CANTRIP)
            for i, n in enumerate(names):
                combo.addItem(spell_label(pool[n]) if n in pool else n)
                combo.setItemData(i + 1, n, Qt.ItemDataRole.UserRole)
                combo.setItemData(i + 1, rich_tip(n, pool.get(n, {}).get("description", "")),
                                  Qt.ItemDataRole.ToolTipRole)

    def _filter(self, text: str) -> None:
        from core.rules import norm
        t = norm(text or "")
        names = [n for n in self.options if t in norm(n)]
        self._fill(self.new_combo, names)
        if self.new and self.new not in names:
            self.new = ""
        self._update()

    @staticmethod
    def _name(label: str) -> str:
        return label.split(" — ")[0] if label and label != NO_CANTRIP else ""

    def set_old(self, label: str) -> bool:
        name = self._name(label)
        if name and name not in self.known:
            return False
        self.old = name
        self._update()
        return True

    def set_new(self, label: str) -> bool:
        name = self._name(label)
        if name and name not in self.options:
            return False
        self.new = name
        self._update()
        return True

    def choice(self):
        return (self.old, self.new) if self.old and self.new else None

    def _update(self) -> None:
        self.old_text.setText(html.escape((self.known.get(self.old) or {}).get("description", ""))[:600])
        self.new_text.setText(html.escape((self.options.get(self.new) or {}).get("description", ""))[:600])
        self.summary.setText("🔁 {} → {}".format(self.old, self.new) if self.choice() else
                             "Choisissez le tour de magie à oublier et son remplaçant.")
        self.ok_btn.setEnabled(self.choice() is not None)
