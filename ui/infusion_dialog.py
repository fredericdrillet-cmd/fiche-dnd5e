"""
Menu « Infusions d'objet » (v53) — onglet Inventaire, toutes les fiches.

Onglet « Infusions » : objets infusés de la fiche (retirer, niveau de l'artificier modifiable) et ajout d'une
infusion sur un objet NON magique de l'inventaire (filtré selon l'infusion) ou un objet ordinaire non listé.
Onglet « Élixir reçu » : élixir expérimental donné par un Alchimiste allié (effet, niveau, mod. d'Intelligence).
"""
from __future__ import annotations

import html

from PyQt6.QtWidgets import (QComboBox, QDialog, QGridLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
                             QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from core.infusions import RESIST_TYPES, infusion_defs, replicable_items
from .common import make_label, rich_tip


class InfusionDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("✨ Infusions d'objet")
        self.resize(760, 560)
        lay = QVBoxLayout(self)
        tabs = QTabWidget()
        lay.addWidget(tabs)
        tabs.addTab(self._infusions_page(), "✨ Infusions")
        tabs.addTab(self._elixir_page(), "🧪 Élixir reçu")
        close = QPushButton("Fermer")
        close.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(close)
        lay.addLayout(row)
        self.refresh()

    @property
    def engine(self):
        return self.win.engine

    # ------------------------------------------------------------------ infusions
    def _infusions_page(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(make_label("Objets infusés de ce personnage", "head"))
        self.current = QListWidget()
        self.current.setMaximumHeight(140)
        lay.addWidget(self.current)
        row = QHBoxLayout()
        self.level_edit = QSpinBox()
        self.level_edit.setRange(2, 20)
        self.level_edit.setPrefix("Niveau de l'artificier : ")
        self.level_btn = QPushButton("Mettre à jour le bonus")
        self.remove_btn = QPushButton("✖ Retirer l'infusion")
        self.remove_btn.setProperty("role", "danger")
        row.addWidget(self.level_edit)
        row.addWidget(self.level_btn)
        row.addStretch(1)
        row.addWidget(self.remove_btn)
        lay.addLayout(row)
        self.level_btn.clicked.connect(self._on_level)
        self.remove_btn.clicked.connect(self._on_remove)
        self.current.currentRowChanged.connect(self._on_select_current)

        lay.addWidget(make_label("Ajouter une infusion", "head"))
        g = QGridLayout()
        self.infusion = QComboBox()
        self.target = QComboBox()
        self.base = QComboBox()                           # arme / armure d'un objet non listé
        self.choice = QComboBox()                         # type de dégâts / objet reproduit
        self.artificer = QLineEdit()
        self.artificer.setPlaceholderText("Nom de l'artificier")
        self.level = QSpinBox()
        self.level.setRange(2, 20)
        rows = [("Infusion", self.infusion), ("Objet", self.target), ("Objet de base", self.base),
                ("Choix", self.choice), ("Artificier", self.artificer), ("Niveau d'artificier", self.level)]
        self.row_labels = {}
        for r, (label, wid) in enumerate(rows):
            lab = make_label(label)
            self.row_labels[label] = lab
            g.addWidget(lab, r, 0)
            g.addWidget(wid, r, 1)
        g.setColumnStretch(1, 1)
        lay.addLayout(g)
        self.desc = make_label("", "muted", wrap=True)
        lay.addWidget(self.desc)
        self.apply_btn = QPushButton("✨ Infuser l'objet")
        self.apply_btn.setDefault(True)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.apply_btn)
        lay.addLayout(row)
        lay.addStretch(1)
        self.infusion.currentIndexChanged.connect(lambda _=0: self._on_infusion())
        self.target.currentIndexChanged.connect(lambda _=0: self._on_target())
        self.level.valueChanged.connect(lambda _=0: self._on_infusion(keep_target=True))
        self.apply_btn.clicked.connect(self._on_apply)
        return w

    def refresh(self) -> None:
        eng = self.engine
        self._entries = eng.infused_entries()
        self.current.clear()
        for i, e in self._entries:
            meta = e["infusion"]
            it = QListWidgetItem("{} — artificier : {}, niveau {}".format(
                eng.magic_display_name(e), meta.get("artificier") or "?", meta.get("niveau", "?")))
            it.setToolTip(rich_tip(meta.get("nom", ""), (infusion_defs().get(meta.get("nom", "")) or {}).get(
                "description", "")))
            self.current.addItem(it)
        if not self._entries:
            self.current.addItem("Aucun objet infusé.")
        self.remove_btn.setEnabled(bool(self._entries))
        self.level_btn.setEnabled(bool(self._entries))
        if self._entries:
            self.current.setCurrentRow(0)
            self._on_select_current(0)
        # infusions proposées : celles connues pour un artificier, toutes sinon
        defs = infusion_defs()
        own = eng.class_level("Artificier") >= 2
        names = eng.known_infusions() if own else list(defs)
        if own and not names:
            names = list(defs)
        cur = self.infusion.currentText()
        self.infusion.blockSignals(True)
        self.infusion.clear()
        self.infusion.addItems(names)
        if cur in names:
            self.infusion.setCurrentIndex(names.index(cur))
        self.infusion.blockSignals(False)
        if not self.artificer.text():
            self.artificer.setText(eng.ch.nom if own else "")
        if own:
            self.level.setValue(max(2, eng.class_level("Artificier")))
        self._on_infusion()

    def _on_select_current(self, row: int) -> None:
        if 0 <= row < len(self._entries):
            self.level_edit.setValue(int(self._entries[row][1]["infusion"].get("niveau", 2) or 2))

    def _on_infusion(self, keep_target: bool = False) -> None:
        eng, name = self.engine, self.infusion.currentText()
        d = infusion_defs().get(name) or {}
        cur = self.target.currentData()
        self.target.blockSignals(True)
        self.target.clear()
        for c in eng.infusion_candidates(name):
            self.target.addItem(c["label"], c["key"])
        if keep_target and cur is not None:
            idx = self.target.findData(cur)
            if idx >= 0:
                self.target.setCurrentIndex(idx)
        self.target.blockSignals(False)
        repro = d.get("cible") == "reproduction"
        self.target.setVisible(not repro)
        self.row_labels["Objet"].setVisible(not repro)
        self.choice.clear()
        if repro:
            items = [n for n in replicable_items(self.level.value()) if eng.magic_item(n)]
            self.choice.addItems(items)
            self.row_labels["Choix"].setText("Objet reproduit")
        elif name == "Armure résistante":
            self.choice.addItems(RESIST_TYPES)
            self.row_labels["Choix"].setText("Résistance")
        show_choice = repro or name == "Armure résistante"
        self.choice.setVisible(show_choice)
        self.row_labels["Choix"].setVisible(show_choice)
        req = "Prérequis : artificier de niveau {}. ".format(d["niveau"]) if d.get("niveau") else ""
        low = d.get("niveau", 0) > self.level.value()
        self.desc.setText(("⚠ Niveau d'artificier insuffisant. " if low else "") + req + (d.get("description", "")[:500]))
        self.apply_btn.setEnabled(not low and (repro or self.target.count() > 0))
        self._on_target()

    def _on_target(self) -> None:
        key = self.target.currentData() or ""
        cible = (infusion_defs().get(self.infusion.currentText()) or {}).get("cible", "")
        need_base = key == "nouveau:"
        self.base.clear()
        if need_base:
            db = self.engine.db
            if cible.startswith("arme"):
                def ok(w):
                    props = [p.lower() for p in w.get("proprietes", [])]
                    return cible == "arme" or (cible == "arme_munitions" and any("munition" in p for p in props)) \
                        or (cible == "arme_lancer" and any("lancer" in p for p in props))
                names = [n for n, w in db.weapons.items() if n != "Mains nues" and ok(w)]
            else:
                names = [n for n, a in db.armors.items() if a.get("categorie") != "aucune"] if cible != "bouclier" else []
                if cible in ("bouclier", "armure_bouclier"):
                    names += list(getattr(db, "shields", {}) or {})
            self.base.addItems(sorted(names))
        self.base.setVisible(need_base)
        self.row_labels["Objet de base"].setVisible(need_base)

    def _on_apply(self) -> None:
        eng = self.engine
        name = self.infusion.currentText()
        msg = eng.apply_infusion(name, self.target.currentData() or "", self.artificer.text(), self.level.value(),
                                 self.choice.currentText(), self.base.currentText())
        self.win.statusBar().showMessage("Infusion appliquée : {}.".format(msg) if msg else
                                         "Infusion impossible (objet ou choix manquant).", 6000)
        if msg:
            self.win.changed()
            self.refresh()

    def _selected_index(self):
        row = self.current.currentRow()
        if 0 <= row < len(self._entries):
            return self._entries[row][0]
        return None

    def _on_remove(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        self.win.statusBar().showMessage(self.engine.remove_infusion(idx), 6000)
        self.win.changed()
        self.refresh()

    def _on_level(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        self.engine.set_infusion_level(idx, self.level_edit.value())
        self.win.changed()
        self.refresh()

    # ------------------------------------------------------------------ élixir reçu
    def _elixir_page(self) -> QWidget:
        from core.elixirs import ELIXIRS
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(make_label("Un Alchimiste allié vous donne un élixir expérimental : il arrive dans votre "
                                 "inventaire et se boit comme une potion (action).", "muted", wrap=True))
        g = QGridLayout()
        self.elixir = QComboBox()
        self.elixir.addItems(ELIXIRS)
        self.elixir_level = QSpinBox()
        self.elixir_level.setRange(3, 20)
        self.elixir_int = QSpinBox()
        self.elixir_int.setRange(-5, 10)
        self.elixir_int.setValue(3)
        for r, (label, wid) in enumerate((("Effet", self.elixir), ("Niveau de l'Alchimiste", self.elixir_level),
                                          ("Mod. d'Intelligence de l'Alchimiste", self.elixir_int))):
            g.addWidget(make_label(label), r, 0)
            g.addWidget(wid, r, 1)
        lay.addLayout(g)
        lay.addWidget(make_label(html.escape("Guérison : 2d4 + Int PV. Rapidité : +3 m (1 h). Résistance : +1 CA "
                                             "(10 min). Audace : +1d4 aux attaques et JS (1 min). Vol : 3 m (10 min). "
                                             "Transformation : Modification d'apparence (10 min). Niveau 9 et plus : "
                                             "+ 2d6 + Int PV temporaires."), "muted", wrap=True))
        btn = QPushButton("🧪 Ajouter l'élixir à l'inventaire")
        btn.clicked.connect(self._on_receive)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn)
        lay.addLayout(row)
        lay.addStretch(1)
        return w

    def _on_receive(self) -> None:
        msg = self.engine.receive_elixir(self.elixir.currentText(), self.elixir_level.value(), self.elixir_int.value())
        self.win.statusBar().showMessage(msg, 6000)
        self.win.changed()


def open_infusions(win) -> None:
    InfusionDialog(win).exec()
