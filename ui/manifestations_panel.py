"""
Sous-onglet « Manifestations occultes » de l'onglet Magie.

Sources de manifestations (synchronisées avec le moteur) :
    - la classe Occultiste (nombre connu selon le niveau) ;
    - les dons de type « Initié aux arcanes occultes » choisis dans l'onglet Progression, Dons.
Les manifestations qui accordent un sort (à volonté ou gratuit) l'injectent automatiquement dans la liste
des sorts de l'onglet Magie (voir `MagicTab._refresh_granted`).
"""
from __future__ import annotations

import html

from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QPushButton,
                             QTableWidget, QTextBrowser, QVBoxLayout, QWidget)

from core.data_loader import PACTS
from core.rules import norm
from . import theme
from .common import BaseTab, cell, fill_combo, formula_html, make_label, rich_tip, style_table

NO_PACT = "— aucun pacte —"
ALL = "Toutes les catégories"


def group_of(m: dict) -> str:
    """Catégorie de filtre : pacte, « Niveau N » ou « Communes »."""
    if m["pacte"]:
        return m["pacte"]
    return f"Niveau {m['niveau']}" if m["niveau"] else "Communes"


class ManifestationsPanel(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QVBoxLayout(self)

        # ---------------- en-tête : sources, pacte
        top = QHBoxLayout()
        self.info = make_label("", "head", wrap=True)
        self.pact = QComboBox()
        self.pact_label = make_label("Pacte divin")
        top.addWidget(self.info, 1)
        top.addWidget(self.pact_label)
        top.addWidget(self.pact)
        root.addLayout(top)
        self.hint = make_label("", "muted", wrap=True)
        root.addWidget(self.hint)

        body = QHBoxLayout()
        root.addLayout(body, 1)

        # ---------------- gauche : catalogue
        lib = QGroupBox("Manifestations disponibles")
        ll = QVBoxLayout(lib)
        flt = QHBoxLayout()
        self.category = QComboBox()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher…")
        self.add_btn = QPushButton("Ajouter ▶")
        flt.addWidget(self.category)
        flt.addWidget(self.search, 1)
        flt.addWidget(self.add_btn)
        ll.addLayout(flt)
        self.library = self._table(["Nom", "Catégorie", "Sort accordé", "État"])
        ll.addWidget(self.library)
        body.addWidget(lib, 3)

        # ---------------- droite : choisies + détail
        right = QVBoxLayout()
        chosen = QGroupBox("Manifestations choisies")
        cl = QVBoxLayout(chosen)
        self.chosen = self._table(["Nom", "Source", "Sort accordé"])
        self.remove_btn = QPushButton("◀ Retirer")
        cl.addWidget(self.chosen)
        cl.addWidget(self.remove_btn)
        right.addWidget(chosen, 3)
        # ---------------- Livre des secrets anciens (Pacte du grimoire) : rituels inscrits
        self.book = QGroupBox("📖 Livre des secrets anciens — rituels inscrits")
        bl = QVBoxLayout(self.book)
        self.book_info = make_label("", "muted", wrap=True)
        bl.addWidget(self.book_info)
        brow = QHBoxLayout()
        self.book_combo = QComboBox()
        self.book_add = QPushButton("Inscrire ▶")
        self.book_del = QPushButton("◀ Effacer")
        brow.addWidget(self.book_combo, 1)
        brow.addWidget(self.book_add)
        brow.addWidget(self.book_del)
        bl.addLayout(brow)
        self.book_list = self._table(["Rituel", "Niveau", "Classes"])
        bl.addWidget(self.book_list)
        right.addWidget(self.book, 2)
        self.book_add.clicked.connect(self._on_book_add)
        self.book_del.clicked.connect(self._on_book_del)
        self._book_rows: list[str] = []
        self._book_options: list[str] = []
        det = QGroupBox("Détail")
        dl = QVBoxLayout(det)
        self.detail = QTextBrowser()
        dl.addWidget(self.detail)
        right.addWidget(det, 2)
        body.addLayout(right, 3)

        self.pact.activated.connect(self._on_pact)
        self.category.activated.connect(lambda _=0: self._fill_library())
        self.search.textChanged.connect(lambda _="": self._fill_library())
        self.add_btn.clicked.connect(self._on_add)
        self.remove_btn.clicked.connect(self._on_remove)
        self.library.cellDoubleClicked.connect(lambda r, c: self._on_add())
        self.library.currentCellChanged.connect(lambda r, c, pr, pc: self._show(self._lib_rows, r))
        self.chosen.currentCellChanged.connect(lambda r, c, pr, pc: self._show(self._chosen_rows, r))
        self._lib_rows: list[str] = []
        self._chosen_rows: list[str] = []

    @staticmethod
    def _table(headers: list[str]) -> QTableWidget:
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        return style_table(t, stretch_col=0)

    # ------------------------------------------------------------------ handlers
    def _on_pact(self, _=0):
        text = self.pact.currentText()
        self.ch.pacte = "" if text == NO_PACT else text
        self.changed()

    def _selected(self, table: QTableWidget, rows: list[str]) -> str:
        r = table.currentRow()
        return rows[r] if 0 <= r < len(rows) else ""

    def _on_add(self):
        name = self._selected(self.library, self._lib_rows)
        eng = self.engine
        if not name or name in self.ch.manifestations:
            return
        if len(self.ch.manifestations) >= eng.manifestation_slots()["total"] or eng.manifestation_status(name)[0] != "ok":
            return
        self.ch.manifestations.append(name)
        self.changed()

    def _on_remove(self):
        name = self._selected(self.chosen, self._chosen_rows)
        if name:
            self.ch.manifestations = [m for m in self.ch.manifestations if m != name]
            self.changed()

    def _on_book_add(self):
        i = self.book_combo.currentIndex()
        if not 0 <= i < len(self._book_options):
            return
        ok, why = self.engine.ritual_book_can_add(self._book_options[i])
        if not ok:
            self.win.statusBar().showMessage(why, 6000)
            return
        self.engine.add_ritual(self._book_options[i])
        self.changed()

    def _on_book_del(self):
        name = self._selected(self.book_list, self._book_rows)
        if name:
            self.engine.remove_ritual(name)
            self.changed()

    def _refresh_book(self):
        eng = self.engine
        active = eng.ritual_book_active()
        self.book.setVisible(active)
        if not active:
            return
        missing = eng.ritual_book_missing()
        self.book_info.setText(
            "Choisissez {} rituel{} de niveau 1 (toutes listes de classe). Ensuite, vous pouvez recopier les rituels "
            "trouvés en aventure, jusqu'au niveau {} (moitié du niveau d'occultiste, arrondie au supérieur) : 2 heures "
            "et 50 po par niveau. Ils se lancent uniquement comme rituels (+10 minutes, sans emplacement).".format(
                missing or "les deux", "s" * (missing != 1), eng.ritual_book_max_level())
            if missing else "Rituels de niveau {} maximum. Ils se lancent uniquement comme rituels (+10 minutes, "
            "sans emplacement) depuis l'onglet Sorts.".format(eng.ritual_book_max_level()))
        self.book.setTitle("📖 Livre des secrets anciens — rituels inscrits" +
                           ("  — ○ {} à choisir".format(missing) if missing else ""))
        opts = [s for s in eng.ritual_book_options() if s["nom"] not in self.ch.rituels_livre
                and (not missing or s["niveau"] == 1)]
        self._book_options = [s["nom"] for s in opts]
        fill_combo(self.book_combo, ["{} (niv. {} — {})".format(s["nom"], s["niveau"], ", ".join(s["classes"]))
                                     for s in opts], "")
        self.book_add.setEnabled(bool(opts))
        self._book_rows = list(self.ch.rituels_livre)
        self.book_list.setRowCount(len(self._book_rows))
        for r, n in enumerate(self._book_rows):
            sp = self.db.find_spell(n) or {}
            tip = rich_tip(n, sp.get("description", ""))
            self.book_list.setItem(r, 0, cell("📜 " + n, "left", tip))
            self.book_list.setItem(r, 1, cell(str(sp.get("niveau", "—")), "center", tip))
            self.book_list.setItem(r, 2, cell(", ".join(sp.get("classes", [])), "left", tip))
        self.book_del.setEnabled(bool(self._book_rows))

    def _show(self, rows: list[str], row: int):
        if not 0 <= row < len(rows):
            return
        m = self.db.manifestations[rows[row]]
        state, why = self.engine.manifestation_status(m["nom"])
        spells = "".join("<p><b>✦ Sort accordé :</b> {} — {}</p>".format(html.escape(g["sort"]), html.escape(g["usage"]))
                         for g in m["sorts"])
        prereq = []
        if m["pacte"]:
            prereq.append(m["pacte"])
        if m["niveau"]:
            prereq.append("Occultiste niveau {}".format(m["niveau"]))
        if m.get("sort_requis"):
            prereq.append("sort mineur {}".format(m["sort_requis"]))
        if m.get("special"):
            prereq.append(m["special"])
        if m.get("source"):
            spells += "<p><small>Source : {}</small></p>".format(html.escape(
                {"PHB": "Manuel des joueurs", "XGtE": "Guide complet de Xanathar",
                 "TCoE": "Chaudron des merveilles de Tasha"}.get(m["source"], m["source"])))
        self.detail.setHtml(
            "<h3 style='color:{}'>{}</h3><p><i>{}</i></p><p>{}</p>{}<p><b>Prérequis :</b> {} {}</p>".format(
                theme.current().accent_text, html.escape(m["nom"]), html.escape(m["categorie"]),
                formula_html(self.engine, m["description"], "Occultiste"), spells, html.escape(", ".join(prereq) or "aucun"),
                "" if state == "ok" else "— ⚠ " + html.escape(why)))

    # ------------------------------------------------------------------ rafraîchissement
    def _fill_library(self):
        eng, t = self.engine, theme.current()
        cat, text = self.category.currentText(), norm(self.search.text())
        names = [n for n, m in self.db.manifestations.items()
                 if (cat == ALL or group_of(m) == cat) and text in norm(n + " " + m["description"])]
        self._lib_rows = names
        self.library.setRowCount(len(names))
        for r, n in enumerate(names):
            m = self.db.manifestations[n]
            state, why = eng.manifestation_status(n)
            owned = n in self.ch.manifestations
            tip = rich_tip(n, m["description"])
            color = t.good if owned else (None if state == "ok" else t.locked)
            grant = ", ".join(g["sort"] for g in m["sorts"]) or "—"
            self.library.setItem(r, 0, cell(n, "left", tip, color, bold=owned))
            self.library.setItem(r, 1, cell(group_of(m), "center", tip, color))
            self.library.setItem(r, 2, cell(grant, "center", tip, color))
            self.library.setItem(r, 3, cell("●" if owned else "✔" if state == "ok" else "🔒", "center",
                                            "Déjà choisie" if owned else (why or "Disponible"), color, bold=True))

    def refresh(self):
        eng, ch, db = self.engine, self.ch, self.db
        slots = eng.manifestation_slots()
        used = len(ch.manifestations)
        parts = ["Occultiste : {}".format(slots["classe"])]
        if slots["dons"]:
            parts.append("dons : {} ({})".format(slots["dons"], ", ".join(slots["sources_dons"])))
        self.info.setText("Manifestations connues : {} / {}   ({})".format(used, slots["total"], " ; ".join(parts)))
        if slots["total"] == 0:
            self.hint.setText("Aucune source pour l'instant : Occultiste niveau 2 ou plus, ou don « Initié aux arcanes "
                              "occultes » (onglet Progression, Dons). Le catalogue reste consultable.")
        else:
            self.hint.setText("Double-cliquez sur une manifestation pour l'ajouter. Celles qui accordent un sort "
                              "l'ajoutent automatiquement à l'onglet Sorts, avec leur source.")
        # pacte
        avail = eng.pact_available()
        self.pact.setEnabled(avail)
        self.pact_label.setEnabled(avail)
        fill_combo(self.pact, [NO_PACT] + PACTS, ch.pacte if ch.pacte in PACTS and avail else NO_PACT)
        self.pact.setToolTip(rich_tip("Pacte divin", "Se choisit au niveau 3 de l'Occultiste : débloque les "
                                      "manifestations propres à chaque pacte." if not avail else
                                      "Détermine les manifestations de pacte disponibles."))
        groups = [ALL, "Communes"] + PACTS + sorted({group_of(m) for m in db.manifestations.values()
                                                     if group_of(m).startswith("Niveau")},
                                                    key=lambda g: int(g.split()[1]))
        fill_combo(self.category, groups, self.category.currentText() if self.category.currentText() in groups else ALL)
        self._fill_library()

        # choisies : source attribuée dans l'ordre (classe d'abord, puis dons)
        self._chosen_rows = list(ch.manifestations)
        self.chosen.setRowCount(len(ch.manifestations))
        sources = ["Occultiste"] * slots["classe"] + ["Don : " + d for d in slots["sources_dons"]]
        for r, n in enumerate(ch.manifestations):
            m = db.manifestations[n]
            state, why = eng.manifestation_status(n)
            color = None if state == "ok" else theme.current().warn
            src = sources[r] if r < len(sources) else "⚠ hors quota"
            tip = rich_tip(n, m["description"] + ("" if state == "ok" else "\n⚠ " + why))
            self.chosen.setItem(r, 0, cell(n, "left", tip, color))
            self.chosen.setItem(r, 1, cell(src, "center", tip, color))
            self.chosen.setItem(r, 2, cell(", ".join(g["sort"] for g in m["sorts"]) or "—", "center", tip, color))
        full = used >= slots["total"]
        self.add_btn.setEnabled(not full)
        self.add_btn.setToolTip("Toutes les manifestations disponibles sont choisies." if full else "")
        self._refresh_book()
