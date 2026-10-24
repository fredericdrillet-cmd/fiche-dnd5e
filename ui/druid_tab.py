"""
Onglet « Forme sauvage » (Druide uniquement) : compteur de formes sauvages et bestiaire interactif.

    - le compteur utilise les mêmes sphères que la rage ou le ki (clic = dépenser / récupérer) ;
    - le bestiaire (data/monsters_db.json) est filtré selon les règles du druide actif : facteur de puissance
      maximal, vitesse de nage (niveau 4) et de vol (niveau 8), Cercle de la Lune (formes de combat) ;
    - un clic sur une bête affiche son statblock complet à droite ; « Adopter cette forme » dépense une utilisation.
"""
from __future__ import annotations

import html

from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QDialog, QGroupBox, QHBoxLayout, QLineEdit, QPushButton,
                             QSplitter, QTableWidget, QTextBrowser, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt

from core import rules as R
from core.rules import norm
from . import theme
from .common import BaseTab, cell, make_label, rich_tip, style_table
from .orbs import OrbBar


def statblock_html(beast: dict, t) -> str:
    """Statblock complet au format « Manuel des monstres » (couleurs du thème actif)."""
    esc = html.escape
    rows = "".join("<td align='center'><b>{}</b><br/>{} ({})</td>".format(k, v[0], esc(v[1]))
                   for k, v in beast["carac"].items())
    lines = []
    for label, key in (("Compétences", "competences"), ("Sens", "sens"), ("Langues", "langues")):
        if beast.get(key) and beast[key] not in ("—", ""):
            lines.append("<b>{}</b> {}".format(label, esc(beast[key])))
    lines.append("<b>Puissance</b> {} ({} PX)".format(esc(beast["fp_txt"]), beast["px"]))
    traits = "".join("<p>• {}</p>".format(esc(x)) for x in beast["traits"]) or "<p><i>Aucun trait particulier.</i></p>"
    actions = "".join("<p>⚔ {}</p>".format(esc(x)) for x in beast["actions"]) or "<p><i>Aucune action détaillée.</i></p>"
    return (
        "<h2 style='color:{acc}; margin-bottom:0'>{nom}</h2><p><i>{type}</i></p>"
        "<hr/><p><b>Classe d'armure</b> {ca}<br/><b>Points de vie</b> {pv}<br/><b>Vitesse</b> {vit}</p><hr/>"
        "<table width='100%' cellspacing='4'><tr>{rows}</tr></table><hr/><p>{lines}</p><hr/>"
        "<h3 style='color:{acc}'>Traits</h3>{traits}<h3 style='color:{acc}'>Actions</h3>{actions}"
    ).format(acc=t.accent_text, nom=esc(beast["nom"]), type=esc(beast["type"]), ca=esc(beast["ca"]),
             pv=esc(beast["pv"]), vit=esc(beast["vitesse"]), rows=rows, lines="<br/>".join(lines),
             traits=traits, actions=actions)


class DruidTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QVBoxLayout(self)

        # ---------------- en-tête : compteur + règles en vigueur + forme active
        top = QGroupBox("Forme sauvage — cliquez une sphère pour dépenser / récupérer")
        tl = QHBoxLayout(top)
        self.orbs = OrbBar("forme", orb=30, per_row=10)
        self.left = make_label("", "stat")
        self.rules = make_label("", "muted", wrap=True)
        tl.addWidget(self.orbs)
        tl.addWidget(self.left)
        tl.addWidget(self.rules, 1)
        root.addWidget(top)
        active = QHBoxLayout()
        self.active = make_label("", "head", wrap=True)
        self.end_btn = QPushButton("Reprendre sa forme normale")
        self.end_btn.setProperty("role", "ghost")
        active.addWidget(self.active, 1)
        active.addWidget(self.end_btn)
        root.addLayout(active)

        # ---------------- deux colonnes : liste filtrée | statblock
        split = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        flt = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher une bête…")
        self.show_all = QCheckBox("Afficher aussi les formes interdites (grisées)")
        flt.addWidget(self.search, 1)
        flt.addWidget(self.show_all)
        ll.addLayout(flt)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Bête", "FP", "CA", "PV", "Déplacements"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        style_table(self.table, stretch_col=0)
        ll.addWidget(self.table)
        self.count = make_label("", "muted")
        ll.addWidget(self.count)
        split.addWidget(left)
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        self.statblock = QTextBrowser()
        self.assume_btn = QPushButton("🐾 Adopter cette forme")
        rl.addWidget(self.statblock, 1)
        rl.addWidget(self.assume_btn)
        split.addWidget(right)
        split.setSizes([620, 560])
        root.addWidget(split, 1)
        self.empty = make_label("", "muted", wrap=True)
        root.addWidget(self.empty)

        self.orbs.changed.connect(self._on_orbs)
        self.search.textChanged.connect(lambda _="": self._fill())
        self.show_all.toggled.connect(lambda _=False: self._fill())
        self.table.currentCellChanged.connect(lambda r, c, pr, pc: self._show(r))
        self.assume_btn.clicked.connect(self._on_assume)
        self.end_btn.clicked.connect(self._on_end)
        self._rows: list[str] = []
        self._fill_key = None

    # ------------------------------------------------------------------ handlers
    def _on_orbs(self, used: int):
        self.engine.set_resource_used("forme", used)
        self._refresh_counter()
        self.win.light_changed()

    def _selected(self) -> str:
        r = self.table.currentRow()
        return self._rows[r] if 0 <= r < len(self._rows) else ""

    def _on_assume(self):
        name = self._selected()
        if name and self.engine.assume_form(name):
            self.changed()

    def _on_end(self):
        self.engine.end_form()
        self.changed()

    def _show(self, row: int):
        if not 0 <= row < len(self._rows):
            return
        beast = self.db.beasts[self._rows[row]]
        ok, why = self.engine.beast_status(beast["nom"])
        warn = "" if ok else "<p style='color:{}'><b>⚠ Forme interdite :</b> {}</p>".format(
            theme.current().warn, html.escape(why))
        self.statblock.setHtml(warn + statblock_html(beast, theme.current()))
        self._update_assume()

    def _update_assume(self):
        name = self._selected()
        ok = bool(name) and self.engine.beast_status(name)[0]
        tracker = next(iter(self.engine.resource_trackers("druide")), None)
        has_use = tracker is not None and (tracker["total"] is None
                                           or self.engine.resource_used("forme") < tracker["total"])
        self.assume_btn.setEnabled(ok and has_use)
        self.assume_btn.setToolTip("" if (ok and has_use) else
                                   "Plus aucune utilisation : faites un repos court." if ok else "Forme non autorisée.")

    # ------------------------------------------------------------------ rafraîchissement
    def _refresh_counter(self):
        tracker = next(iter(self.engine.resource_trackers("druide")), None)
        if tracker is None:
            self.orbs.set_state(0, 0)
            self.left.setText("")
            return
        if tracker["total"] is None:
            self.orbs.set_state(0, 0)
            self.left.setText("∞  illimitées (Archidruide)")
        else:
            used = self.engine.resource_used("forme")
            self.orbs.set_state(tracker["total"], used)
            self.left.setText("{} / {}".format(tracker["total"] - used, tracker["total"]))
        self._update_assume()

    def _fill(self):
        """Liste filtrée (recalculée seulement si les règles, la recherche ou l'option d'affichage ont changé)."""
        ws = self.engine.wild_shape()
        text = norm(self.search.text())
        key = (ws["fp_max"], ws["nage"], ws["vol"], ws["actif"], text, self.show_all.isChecked(), theme.current().key)
        if key == self._fill_key:
            return
        self._fill_key = key
        t = theme.current()
        beasts = sorted(self.db.beasts.values(), key=lambda b: (b["fp"], b["nom"]))
        rows = []
        for b in beasts:
            ok, why = self.engine.beast_status(b["nom"])
            if (ok or self.show_all.isChecked()) and text in norm(b["nom"]):
                rows.append((b, ok, why))
        self._rows = [b["nom"] for b, _, _ in rows]
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(rows))
        for r, (b, ok, why) in enumerate(rows):
            color = None if ok else t.locked
            tip = rich_tip(b["nom"], "Autorisée" if ok else "Interdite : " + why)
            moves = ", ".join(x for x, on in (("vol", b["vol"]), ("nage", b["nage"])) if on) or "marche"
            self.table.setItem(r, 0, cell(("✔ " if ok else "🔒 ") + b["nom"], "left", tip, color, bold=ok))
            self.table.setItem(r, 1, cell(b["fp_txt"], "center", tip, color))
            self.table.setItem(r, 2, cell(b["ca"].split(" ")[0], "center", tip, color))
            self.table.setItem(r, 3, cell(b["pv"].split(" ")[0], "center", tip, color))
            self.table.setItem(r, 4, cell(moves, "center", b["vitesse"], color))
        self.table.setUpdatesEnabled(True)
        allowed = sum(1 for _, ok, _ in rows if ok)
        self.count.setText("{} forme(s) autorisée(s) sur {} bêtes du bestiaire.".format(
            len(self.engine.allowed_beasts()), len(self.db.beasts)) if rows else "Aucune bête ne correspond.")
        if rows and self.table.currentRow() < 0:
            self.table.selectRow(0)
        _ = allowed

    def refresh(self):
        ws = self.engine.wild_shape()
        druid = ws["niveau"]
        if not ws["actif"]:
            self.rules.setText("")
            self.empty.setText("La Forme sauvage s'obtient au niveau 2 de Druide (niveau actuel : {}).".format(druid))
        else:
            self.empty.setText("" if self.db.beasts else "Bestiaire introuvable : le fichier du bestiaire manque dans le dossier des données.")
            circle = "Cercle de la Lune (formes de combat)" if ws["lune"] else "Druide"
            self.rules.setText("{} niveau {} — FP maximal {} — {} — durée {} heure(s) — vous devez avoir déjà vu la bête."
                               .format(circle, druid, R.fmt_cr(ws["fp_max"]), ws["mouvements"], ws["duree"]))
        form = self.ch.forme_active
        if form and form in self.db.beasts:
            b = self.db.beasts[form]
            self.active.setText("Forme actuelle : {} — CA {} — PV de la bête {} / {} (vos PV de druide sont mis de "
                                "côté ; les dégâts excédentaires leur sont reportés à 0 PV)".format(
                                    form, self.engine.beast_ac(b), self.ch.forme_pv, self.engine.beast_hp_max(form)))
        else:
            self.active.setText("Forme actuelle : aucune (forme normale)")
        self.end_btn.setEnabled(bool(form))
        self._refresh_counter()
        self._fill_key = None if self._fill_key and self._fill_key[-1] != theme.current().key else self._fill_key
        self._fill()
        self._show(self.table.currentRow())


# ------------------------------------------------------------------------------------------------ sélecteur partagé
class BeastPickerDialog(QDialog):
    """
    Même tableau de bêtes que l'onglet Forme sauvage (liste filtrable + statblock complet), réutilisé par le sort
    Métamorphose. `status_fn(nom) -> (autorisée, raison)` détermine les bêtes accessibles.
    """

    def __init__(self, win, title: str, status_fn, intro: str = ""):
        super().__init__(win)
        self.win, self.status_fn, self.choice = win, status_fn, ""
        self.setWindowTitle(title)
        self.resize(1100, 680)
        root = QVBoxLayout(self)
        root.addWidget(make_label(title, "title"))
        if intro:
            root.addWidget(make_label(intro, "muted", wrap=True))
        split = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        flt = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher une bête…")
        self.show_all = QCheckBox("Afficher aussi les formes interdites (grisées)")
        flt.addWidget(self.search, 1)
        flt.addWidget(self.show_all)
        ll.addLayout(flt)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Bête", "FP", "CA", "PV", "Déplacements"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        style_table(self.table, stretch_col=0)
        ll.addWidget(self.table)
        split.addWidget(left)
        self.statblock = QTextBrowser()
        split.addWidget(self.statblock)
        split.setSizes([560, 520])
        root.addWidget(split, 1)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setProperty("role", "ghost")
        self.ok_btn = QPushButton("🦋 Adopter cette forme")
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.ok_btn)
        root.addLayout(buttons)
        self._rows: list[str] = []
        self.search.textChanged.connect(lambda _="": self.fill())
        self.show_all.toggled.connect(lambda _=False: self.fill())
        self.table.currentCellChanged.connect(lambda r, c, pr, pc: self._show(r))
        self.table.cellDoubleClicked.connect(lambda r, c: self._accept())
        self.ok_btn.clicked.connect(self._accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.fill()

    def fill(self):
        t, db = theme.current(), self.win.db
        text = norm(self.search.text())
        rows = []
        for b in sorted(db.beasts.values(), key=lambda b: (b["fp"], b["nom"])):
            ok, why = self.status_fn(b["nom"])
            if (ok or self.show_all.isChecked()) and text in norm(b["nom"]):
                rows.append((b, ok, why))
        self._rows = [b["nom"] for b, _, _ in rows]
        self.table.setRowCount(len(rows))
        for r, (b, ok, why) in enumerate(rows):
            color = None if ok else t.locked
            tip = rich_tip(b["nom"], "Autorisée" if ok else "Interdite : " + why)
            moves = ", ".join(x for x, on in (("vol", b["vol"]), ("nage", b["nage"])) if on) or "marche"
            self.table.setItem(r, 0, cell(("✔ " if ok else "🔒 ") + b["nom"], "left", tip, color, bold=ok))
            self.table.setItem(r, 1, cell(b["fp_txt"], "center", tip, color))
            self.table.setItem(r, 2, cell(b["ca"].split(" ")[0], "center", tip, color))
            self.table.setItem(r, 3, cell(b["pv"].split(" ")[0], "center", tip, color))
            self.table.setItem(r, 4, cell(moves, "center", b["vitesse"], color))
        if rows and self.table.currentRow() < 0:
            self.table.selectRow(0)

    def selected(self) -> str:
        r = self.table.currentRow()
        return self._rows[r] if 0 <= r < len(self._rows) else ""

    def _show(self, row: int):
        if 0 <= row < len(self._rows):
            beast = self.win.db.beasts[self._rows[row]]
            ok, why = self.status_fn(beast["nom"])
            warn = "" if ok else "<p style='color:{}'><b>⚠ Forme interdite :</b> {}</p>".format(
                theme.current().warn, html.escape(why))
            self.statblock.setHtml(warn + statblock_html(beast, theme.current()))
            self.ok_btn.setEnabled(ok)

    def _accept(self):
        name = self.selected()
        if name and self.status_fn(name)[0]:
            self.choice = name
            self.accept()


def start_polymorph(win, use_slot: bool = True) -> bool:
    """Sort Métamorphose sur soi : choix de la bête dans le tableau de bêtes, puis lancement (concentration)."""
    eng = win.engine
    dlg = BeastPickerDialog(win, "Métamorphose — choisissez la bête",
                            eng.polymorph_status,
                            "Bêtes de FP inférieur ou égal à votre niveau ({}). Toutes vos caractéristiques, y compris "
                            "mentales, et vos PV deviennent ceux de la bête ; vous ne pouvez plus lancer de sorts. "
                            "Métamorphose demande votre concentration.".format(eng.total_level))
    if dlg.exec() != 1 or not dlg.choice:
        return False
    res = eng.cast_polymorph(dlg.choice, use_slot)
    win.statusBar().showMessage(res["message"], 8000)
    if res["ok"]:
        win.changed()
    return res["ok"]

