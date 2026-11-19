"""Fenêtre « Lexique des règles » (v52) : recherche, liste par catégorie, définition 2014 / 2024 (F1)."""
from __future__ import annotations

import html

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QListWidget, QTextBrowser, QVBoxLayout

from .common import make_label


def term_html(glossary, term: dict, edition: int = 0) -> str:
    out = ["<h3>{}</h3><p>{}</p>".format(html.escape(term["terme"]), html.escape(term.get("definition", "")))]
    for ed in (2014, 2024):
        if term.get(str(ed)):
            mark = " (votre fiche)" if ed == edition else ""
            out.append("<p><b>{}{}</b> : {}</p>".format(ed, mark, html.escape(term[str(ed)])))
    if term.get("variantes"):
        out.append("<p style='color:gray'>Aussi : {}</p>".format(html.escape(", ".join(term["variantes"]))))
    out.append("<p style='color:gray'>Catégorie : {}</p>".format(html.escape(term.get("categorie", ""))))
    return "".join(out)


class GlossaryDialog(QDialog):
    def __init__(self, win, glossary, edition: int = 0, initial: str = ""):
        super().__init__(win)
        self.setWindowTitle("Lexique des règles")
        self.resize(760, 520)
        self.glossary, self.edition = glossary, edition
        lay = QVBoxLayout(self)
        lay.addWidget(make_label("Les mots du jeu, en une ou deux phrases — avec ce qui change entre 2014 et 2024. "
                                 "Ils sont aussi expliqués au survol, partout dans l'application.", "muted", wrap=True))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher un terme (avantage, concentration, à terre…)")
        lay.addWidget(self.search)
        row = QHBoxLayout()
        self.list = QListWidget()
        self.list.setFixedWidth(240)
        self.detail = QTextBrowser()
        row.addWidget(self.list)
        row.addWidget(self.detail, 1)
        lay.addLayout(row, 1)
        self._shown: list[dict] = []
        self.search.textChanged.connect(lambda _="": self._fill())
        self.list.currentRowChanged.connect(self._show)
        self.search.setText(initial)
        self._fill()

    def _fill(self) -> None:
        self._shown = sorted(self.glossary.search(self.search.text()), key=lambda t: (t.get("categorie", ""),
                                                                                     t["terme"]))
        self.list.clear()
        for t in self._shown:
            self.list.addItem("{} — {}".format(t["terme"], t.get("categorie", "")))
        if self._shown:
            self.list.setCurrentRow(0)
            self._show(0)
        else:
            self.detail.setHtml("<p>Aucun terme trouvé.</p>")

    def _show(self, row: int) -> None:
        if 0 <= row < len(self._shown):
            self.detail.setHtml(term_html(self.glossary, self._shown[row], self.edition))
