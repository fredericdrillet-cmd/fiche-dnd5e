"""Fenêtre « 📖 Manuel d'utilisation » (v52, F2) : sommaire, recherche, liens vers les onglets, export PDF."""
from __future__ import annotations

from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QPushButton,
                             QTextBrowser, QVBoxLayout)

from .common import make_label


class ManualDialog(QDialog):
    def __init__(self, win, chapter_id: str = ""):
        super().__init__(win)
        self.win = win
        self.manual = getattr(win.db, "manual", None)
        self.setWindowTitle("📖 Manuel d'utilisation")
        self.resize(900, 620)
        self.current_id = ""
        lay = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher dans le manuel (munitions, repos, concentration…)")
        self.search.setClearButtonEnabled(True)
        lay.addWidget(self.search)
        body = QHBoxLayout()
        self.toc = QListWidget()
        self.toc.setMaximumWidth(280)
        body.addWidget(self.toc)
        self.view = QTextBrowser()
        body.addWidget(self.view, 1)
        lay.addLayout(body, 1)
        row = QHBoxLayout()
        self.open_btn = QPushButton("Ouvrir l'onglet")
        self.open_btn.clicked.connect(self.open_tab)
        export = QPushButton("Exporter le manuel en PDF…")
        export.setProperty("role", "ghost")
        export.clicked.connect(self.export_pdf)
        close = QPushButton("Fermer")
        close.clicked.connect(self.accept)
        row.addWidget(self.open_btn)
        row.addWidget(export)
        row.addStretch(1)
        row.addWidget(close)
        lay.addLayout(row)
        self.search.textChanged.connect(lambda _="": self._fill())
        self.toc.currentRowChanged.connect(lambda _=0: self._show_current())
        if not self.manual:
            lay.insertWidget(0, make_label("Manuel introuvable (data/Manuel.json).", "warn"))
        self._rows: list[str] = []
        self._fill()
        self.show_chapter(chapter_id or (self.manual.chapters[0]["id"] if self.manual else ""))

    def _fill(self) -> None:
        """Sommaire complet, ou sections trouvées par la recherche."""
        self.toc.clear()
        self._rows = []
        if not self.manual:
            return
        hits = self.manual.search(self.search.text())
        if self.search.text().strip() and len(self.search.text().strip()) >= 2:
            for cid, title, _snippet in hits:
                self.toc.addItem(QListWidgetItem("{} — {}".format(self.manual.chapter(cid)["titre"], title)))
                self._rows.append(cid)
            if not hits:
                self.view.setHtml("<p><i>Rien trouvé dans le manuel.</i></p>")
        else:
            for c in self.manual.chapters:
                self.toc.addItem(QListWidgetItem(c["titre"]))
                self._rows.append(c["id"])
        if self._rows:
            self.toc.setCurrentRow(0)
            self._show_current()

    def _show_current(self) -> None:
        row = self.toc.currentRow()
        if 0 <= row < len(self._rows):
            self.show_chapter(self._rows[row], select=False)

    def show_chapter(self, chapter_id: str, select: bool = True) -> None:
        if not self.manual or not self.manual.chapter(chapter_id):
            return
        self.current_id = chapter_id
        self.view.setHtml(self.manual.chapter_html(chapter_id, self.search.text()))
        tab = self.manual.chapter(chapter_id).get("onglet", "")
        self.open_btn.setEnabled(bool(tab))
        if select and chapter_id in self._rows:
            self.toc.setCurrentRow(self._rows.index(chapter_id))

    def open_tab(self) -> bool:
        c = self.manual.chapter(self.current_id) if self.manual else None
        if c and c.get("onglet") and self.win.open_tab(c["onglet"]):
            self.accept()
            return True
        return False

    def export_pdf(self, path: str = "") -> str:
        if not self.manual:
            return ""
        if not path:
            from PyQt6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getSaveFileName(self, "Exporter le manuel", "Manuel_fiche_DnD5e.pdf", "PDF (*.pdf)")
        if not path:
            return ""
        from .pdf_export import export_html_pdf
        export_html_pdf(self.manual.print_html(), path, "Manuel d'utilisation")
        return path
