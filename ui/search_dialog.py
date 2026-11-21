"""Fenêtre « 🔎 Recherche » (v52, Ctrl+F) : votre fiche d'abord, puis les règles de l'édition et le lexique."""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout

from .common import make_label

GROUP_TITLES = {"fiche": "— Sur votre fiche —", "regles": "— Règles et lexique —"}


class SearchDialog(QDialog):
    def __init__(self, win, initial: str = ""):
        super().__init__(win)
        self.win = win
        self.eng = win.engine
        self.results: list[dict] = []
        self.setWindowTitle("🔎 Recherche")
        self.resize(720, 520)
        lay = QVBoxLayout(self)
        self.field = QLineEdit()
        self.field.setPlaceholderText("Sort, aptitude, objet, état, action, terme de règle… (2 lettres minimum)")
        self.field.setClearButtonEnabled(True)
        lay.addWidget(self.field)
        self.list = QListWidget()
        lay.addWidget(self.list, 1)
        self.detail = make_label("", "", wrap=True)
        self.detail.setTextFormat(Qt.TextFormat.RichText)
        self.detail.setMinimumHeight(120)
        self.detail.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(self.detail)
        lay.addWidget(make_label("Entrée : ouvrir l'onglet de l'élément (ou son détail) — Échap : fermer.", "muted"))
        self.field.textChanged.connect(lambda _="": self._search())
        self.field.returnPressed.connect(self.open_selected)
        self.list.currentRowChanged.connect(lambda _=0: self._show())
        self.list.itemActivated.connect(lambda _=None: self.open_selected())
        self.field.setText(initial)
        self._search()
        self.field.setFocus()

    def _search(self) -> None:
        self.results = self.eng.quick_search(self.field.text())
        self.list.clear()
        group = ""
        self._rows: list[int] = []                         # ligne -> indice du résultat (-1 : titre de groupe)
        for i, r in enumerate(self.results):
            if r["groupe"] != group:
                group = r["groupe"]
                head = QListWidgetItem(GROUP_TITLES[group])
                head.setFlags(Qt.ItemFlag.NoItemFlags)
                self.list.addItem(head)
                self._rows.append(-1)
            self.list.addItem(QListWidgetItem("{}   ·   {}".format(r["nom"], r["type"])))
            self._rows.append(i)
        first = next((n for n, i in enumerate(self._rows) if i >= 0), -1)
        if first >= 0:
            self.list.setCurrentRow(first)
        else:
            self.detail.setText("" if len(self.field.text().strip()) < 2 else "Aucun résultat.")

    def current(self):
        row = self.list.currentRow()
        if 0 <= row < len(getattr(self, "_rows", [])) and self._rows[row] >= 0:
            return self.results[self._rows[row]]
        return None

    def _show(self) -> None:
        r = self.current()
        if r is None:
            return
        self.detail.setText("<b>{}</b> — <i>{}</i><br/>{}".format(html.escape(r["nom"]), html.escape(r["type"]),
                                                                  html.escape(r["texte"][:900]).replace("\n", "<br/>")))

    def open_selected(self) -> None:
        r = self.current()
        if r is None:
            return
        if r["onglet"]:
            self.win.open_tab(r["onglet"])
            self.accept()
