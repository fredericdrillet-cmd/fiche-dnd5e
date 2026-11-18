"""Fenêtre « Historique des lancers » (v52) : Ctrl+H ou Options > Historique des lancers…"""
from __future__ import annotations

import html

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout

from . import theme
from .common import make_label

KIND_LABELS = {"attaque": "Attaque", "sauvegarde": "Sauvegarde", "competence": "Test", "test": "Test",
               "sort": "Sort", "degats": "Dégâts", "soins": "Soins", "de": "Dé", "initiative": "Initiative"}


def history_html(entries: list[dict]) -> str:
    t = theme.current()
    if not entries:
        return "<p><i>Aucun lancer pour l'instant.</i></p>"
    rows = []
    for e in entries:
        mode = " — <b>{}</b>".format(html.escape(e.get("mode", ""))) if e.get("mode") else ""
        rows.append("<tr><td style='color:{}'>{}</td><td>{}</td><td><b>{}</b>{}<br/><span style='color:{}'>{}</span></td>"
                    "<td align='right' style='font-size:14pt'><b>{}</b></td></tr>".format(
                        t.muted, html.escape(e.get("heure", "")), html.escape(KIND_LABELS.get(e.get("type", ""), "")),
                        html.escape(e.get("titre", "")), mode, t.muted, html.escape(e.get("detail", "")),
                        e.get("total", "")))
    return "<table width='100%' cellspacing='0' cellpadding='4'>{}</table>".format("".join(rows))


class HistoryDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("Historique des lancers")
        self.resize(620, 560)
        lay = QVBoxLayout(self)
        lay.addWidget(make_label("Les {} derniers lancers de ce personnage (le plus récent en haut).".format(
            win.engine.MAX_ROLL_HISTORY), "muted", wrap=True))
        self.view = QTextBrowser()
        lay.addWidget(self.view, 1)
        row = QHBoxLayout()
        clear = QPushButton("Effacer l'historique")
        clear.setProperty("role", "ghost")
        clear.clicked.connect(self.clear)
        close = QPushButton("Fermer")
        close.clicked.connect(self.accept)
        row.addWidget(clear)
        row.addStretch(1)
        row.addWidget(close)
        lay.addLayout(row)
        self.refresh()

    def refresh(self) -> None:
        self.view.setHtml(history_html(self.win.engine.ch.historique_jets or []))

    def clear(self) -> None:
        self.win.engine.ch.historique_jets = []
        if hasattr(self.win, "light_changed"):
            self.win.light_changed()
        self.refresh()
