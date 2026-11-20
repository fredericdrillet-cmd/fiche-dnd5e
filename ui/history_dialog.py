"""Fenêtre « Historique des lancers » et journal de session (v52) : Ctrl+H ou Options > Historique…"""
from __future__ import annotations

import html

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTabWidget, QTextBrowser, QVBoxLayout, QWidget

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


def journal_html(entries: list[dict]) -> str:
    t = theme.current()
    if not entries:
        return "<p><i>Journal vide : les dégâts, soins, sorts, ressources, repos et états s'y inscrivent tout seuls."\
               "</i></p>"
    rows, day = [], None
    for e in entries:
        stamp = e.get("jour", "")
        this_day, _, game_hour = stamp.partition(", ")
        if this_day != day:
            day = this_day
            rows.append("<tr><td colspan='3' style='color:{}'><b>{}</b></td></tr>".format(t.accent_text,
                                                                                       html.escape(day or "")))
        rows.append("<tr><td style='color:{}' width='50'>{}</td><td style='color:{}' width='90'>{}</td><td>{}</td>"
                    "</tr>".format(t.accent_text, html.escape(game_hour), t.muted, html.escape(e.get("heure", "")),
                                   html.escape(e.get("texte", ""))))
    return "<table width='100%' cellspacing='0' cellpadding='3'>{}</table>".format("".join(rows))


class HistoryDialog(QDialog):
    """v52 : deux onglets — lancers de dés et journal de session (export texte, vider)."""

    def __init__(self, win, tab: int = 0):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("Historique des lancers et journal de session")
        self.resize(660, 600)
        lay = QVBoxLayout(self)
        self.tabs = QTabWidget()
        lay.addWidget(self.tabs, 1)
        # lancers
        rolls = QWidget()
        rl = QVBoxLayout(rolls)
        rl.addWidget(make_label("Les {} derniers lancers de ce personnage (le plus récent en haut).".format(
            win.engine.MAX_ROLL_HISTORY), "muted", wrap=True))
        self.view = QTextBrowser()
        rl.addWidget(self.view, 1)
        clear = QPushButton("Effacer l'historique")
        clear.setProperty("role", "ghost")
        clear.clicked.connect(self.clear)
        rl.addWidget(clear)
        self.tabs.addTab(rolls, "🎲 Lancers")
        # journal
        jour = QWidget()
        jl = QVBoxLayout(jour)
        jl.addWidget(make_label("Journal de session : les 500 derniers événements (le plus récent en haut), groupés "
                                "par jour de jeu.", "muted", wrap=True))
        self.journal = QTextBrowser()
        jl.addWidget(self.journal, 1)
        jrow = QHBoxLayout()
        export = QPushButton("Exporter en texte…")
        export.clicked.connect(self.export_journal)
        jclear = QPushButton("Vider le journal (nouvelle séance)")
        jclear.setProperty("role", "ghost")
        jclear.clicked.connect(self.clear_journal)
        jrow.addWidget(export)
        jrow.addWidget(jclear)
        jrow.addStretch(1)
        jl.addLayout(jrow)
        self.tabs.addTab(jour, "📜 Journal de session")
        row = QHBoxLayout()
        row.addStretch(1)
        close = QPushButton("Fermer")
        close.clicked.connect(self.accept)
        row.addWidget(close)
        lay.addLayout(row)
        self.tabs.setCurrentIndex(tab)
        self.refresh()

    def refresh(self) -> None:
        self.view.setHtml(history_html(self.win.engine.ch.historique_jets or []))
        self.journal.setHtml(journal_html(self.win.engine.ch.journal or []))

    def clear(self) -> None:
        self.win.engine.ch.historique_jets = []
        if hasattr(self.win, "light_changed"):
            self.win.light_changed()
        self.refresh()

    def clear_journal(self) -> None:
        self.win.engine.ch.journal = []
        if hasattr(self.win, "light_changed"):
            self.win.light_changed()
        self.refresh()

    def export_journal(self, path: str = "") -> str:
        from pathlib import Path
        if not path:
            from PyQt6.QtWidgets import QFileDialog
            name = (self.win.engine.ch.nom or "personnage").strip().replace(" ", "_")
            path, _ = QFileDialog.getSaveFileName(self, "Exporter le journal", "journal_{}.txt".format(name),
                                                  "Texte (*.txt)")
        if not path:
            return ""
        Path(path).write_text(self.win.engine.journal_text() + "\n", encoding="utf-8")
        return path
