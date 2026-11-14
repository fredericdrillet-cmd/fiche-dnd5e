"""
Onglet « Progression, Dons » : améliorations de caractéristiques, choix de dons, catalogue des dons.

Performances : la liste des dons est triée une seule fois (ordre alphabétique strict, sans tenir compte des
accents), les infobulles à formules sont calculées une fois par état du personnage (cache), et le catalogue
n'est reconstruit que si la recherche, les prérequis ou les dons choisis ont changé.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTextBrowser, QVBoxLayout)

from core.formulas import annotate
from core.rules import ABILITIES, norm
from . import theme
from .dialogs import ask_gm_feat
from .common import BaseTab, blocked, cell, fill_combo, formula_html, formula_tip, head, make_label, rich_tip, style_table

MODES = {"Non utilisée": "aucun", "+2 à une caractéristique": "plus2", "+1 à deux caractéristiques": "plus1x2",
         "Don": "don"}
STATE_ICON = {"ok": "✔", "ko": "⚠", "?": "?"}


class ProgressionTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QVBoxLayout(self)
        root.addWidget(make_label("Améliorations de caractéristiques et dons", "title"))
        root.addWidget(make_label(
            "Chaque classe accorde des améliorations à certains niveaux (lues dans les fichiers de classe). "
            "Les bonus s'appliquent automatiquement aux caractéristiques (plafond 20). Survolez un don pour lire "
            "son effet ; les prérequis sont vérifiés automatiquement (✔ rempli, ⚠ manquant, ? à vérifier).",
            "muted", wrap=True))
        self.box = QGroupBox("Emplacements débloqués")
        self.grid = QGridLayout(self.box)
        root.addWidget(self.box)
        self.empty = make_label("Aucune amélioration débloquée pour l'instant (niveau 4 pour la plupart des classes).",
                                "muted")
        root.addWidget(self.empty)

        cat = QGroupBox("Catalogue des dons")
        cl = QVBoxLayout(cat)
        flt = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher un don, un prérequis…")
        flt.addWidget(self.search, 1)
        self.gm_btn = QPushButton("📜 Don accordé par le MJ")
        self.gm_btn.setToolTip(rich_tip("Don accordé par le MJ", "Ajoute un don supplémentaire à la fiche, en plus "
                                        "des dons de niveau et de l'Humain variant. Ses bonus (caractéristique, "
                                        "initiative, PV…) s'appliquent automatiquement."))
        flt.addWidget(self.gm_btn)
        cl.addLayout(flt)
        split = QHBoxLayout()
        self.table = QTableWidget(0, 4)                  # colonne « Source » retirée (visible dans le détail du don)
        self.table.setHorizontalHeaderLabels(["Don", "Prérequis", "Augmentation", "État"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        style_table(self.table, stretch_col=0)
        self.detail = QTextBrowser()
        split.addWidget(self.table, 3)
        split.addWidget(self.detail, 2)
        cl.addLayout(split)
        root.addWidget(cat, 1)

        self.search.textChanged.connect(lambda _="": self._fill_catalog())
        self.gm_btn.clicked.connect(self._on_gm_feat)
        self.table.currentCellChanged.connect(lambda r, c, pr, pc: self._show_feat(r))
        self._rows: list[dict] = []
        self._key: tuple = ()
        self._cat_names: list[str] = []
        self._cat_key = None
        self._tips_key = None
        self._tips: dict[str, str] = {}
        self._sorted: list[str] = []

    # ------------------------------------------------------------------ construction dynamique
    def _rebuild(self, slots: list[dict]):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._rows = []
        for c, h in enumerate(["Emplacement", "Choix", "Caractéristique 1", "Caractéristique 2", "Don", "Bonus du don",
                               "Prérequis", ""]):
            self.grid.addWidget(head(h), 0, c)
        for r, s in enumerate(slots, start=1):
            w = {"id": s["id"], "label": make_label(s["label"]), "mode": QComboBox(), "a1": QComboBox(),
                 "a2": QComboBox(), "feat": QComboBox(), "fa": QComboBox(), "state": make_label("", "muted"),
                 "don_seul": bool(s.get("don_seul")), "mj": bool(s.get("mj")), "remove": QPushButton("✖ Retirer")}
            w["remove"].setProperty("role", "ghost")
            w["remove"].setVisible(w["mj"])
            w["remove"].clicked.connect(lambda _=False, sid=s["id"]: self._on_remove_gm(sid))
            w["mode"].addItems(list(MODES))
            for k in ("a1", "a2"):
                w[k].addItems(ABILITIES)
            w["feat"].addItems(self.feat_names())
            for c, k in enumerate(["label", "mode", "a1", "a2", "feat", "fa", "state", "remove"]):
                self.grid.addWidget(w[k], r, c)
            for k in ("mode", "a1", "a2", "feat", "fa"):
                w[k].activated.connect(lambda _=0, sid=s["id"]: self._on_change(sid))
            self._rows.append(w)

    def _on_gm_feat(self):
        row = self.table.currentRow()
        pre = self._cat_names[row] if 0 <= row < len(self._cat_names) else ""
        name = ask_gm_feat(self.win, self.feat_names(), pre)
        if name and self.engine.add_gm_feat(name):
            self.win.statusBar().showMessage("Don accordé par le MJ : {}.".format(name), 6000)
            self.changed()
        elif name:
            self.win.statusBar().showMessage("« {} » est déjà accordé par le MJ.".format(name), 6000)

    def _on_remove_gm(self, sid: str):
        self.engine.remove_gm_feat(sid[3:])
        self.changed()

    def _on_change(self, sid: str):
        w = next(r for r in self._rows if r["id"] == sid)
        self.ch.ameliorations[sid] = {
            "mode": MODES[w["mode"].currentText()], "a1": w["a1"].currentText(), "a2": w["a2"].currentText(),
            "don": w["feat"].currentText(), "don_carac": w["fa"].currentText()}
        self.changed()

    # ------------------------------------------------------------------ catalogue
    def feat_names(self) -> list[str]:
        """Dons triés par ordre alphabétique strict (accents ignorés), calculé une seule fois."""
        key = (len(self.db.feats), self.engine.edition_mode)          # v52 : dons de l'édition du personnage
        if getattr(self, "_sorted_key", None) != key:
            self._sorted = sorted(self.engine.feat_options(), key=lambda n: (norm(n), n))
            self._sorted_key = key
        return self._sorted

    def _ctx_key(self) -> tuple:
        eng = self.engine
        return tuple(sorted(eng.mods().items())), eng.prof, eng.total_level

    def _all_tips(self) -> dict[str, str]:
        """Infobulles de tous les dons (formules évaluées) — recalculées seulement si le personnage a changé."""
        key = self._ctx_key()
        if key != self._tips_key:
            ctx = self.engine.formula_context("")
            self._tips = {n: rich_tip(n, annotate("Prérequis : {} — Augmentation : {} — {}".format(
                f["prerequis"], f["asi_texte"] or "aucune", f["description"]), ctx)) for n, f in self.db.feats.items()}
            self._tips_key = key
        return self._tips

    def _feat_tip(self, f: dict) -> str:
        return self._all_tips().get(f["nom"], "")

    def _fill_catalog(self):
        eng, t = self.engine, theme.current()
        text = norm(self.search.text())
        names = [n for n in self.feat_names()
                 if not text or text in norm(" ".join((n, self.db.feats[n]["source"], self.db.feats[n]["prerequis"],
                                                       self.db.feats[n]["description"])))]
        chosen = set(eng.chosen_feats())
        status = {n: eng.feat_status(n) for n in names}
        key = (text, self._ctx_key(), tuple(sorted(chosen)), tuple(status[n][0] for n in names), t.key)
        if key == self._cat_key:
            return                                  # rien n'a changé : pas de reconstruction du tableau
        self._cat_key = key
        tips = self._all_tips()
        self._cat_names = names
        self.table.setUpdatesEnabled(False)
        with blocked(self.table):
            self.table.setRowCount(len(names))
            for r, n in enumerate(names):
                f = self.db.feats[n]
                state, msg = status[n]
                tip = tips.get(n, "")
                color = {"ok": t.good, "ko": t.warn, "?": t.muted}[state]
                self.table.setItem(r, 0, cell(n, "left", tip, bold=n in chosen))
                self.table.setItem(r, 1, cell(f["prerequis"], "center", tip))
                self.table.setItem(r, 2, cell(f["asi_texte"] or "—", "center", tip))
                self.table.setItem(r, 3, cell(STATE_ICON[state], "center", msg or "Prérequis rempli", color, bold=True))
        self.table.setUpdatesEnabled(True)

    def _show_feat(self, row: int):
        if 0 <= row < len(self._cat_names):
            f = self.db.feats[self._cat_names[row]]
            state, msg = self.engine.feat_status(f["nom"])
            self.detail.setHtml(
                "<h3 style='color:{}'>{}</h3><p><i>{}</i></p><p><b>Prérequis :</b> {} {}</p>"
                "<p><b>Augmentation :</b> {}</p><p>{}</p>".format(
                    theme.current().accent_text, html.escape(f["nom"]), html.escape(f["source"]),
                    html.escape(f["prerequis"]), STATE_ICON[state], html.escape(f["asi_texte"] or "aucune"),
                    formula_html(self.engine, f["description"])))

    # ------------------------------------------------------------------ rafraîchissement
    def refresh(self):
        self.mark_box(self.box, "Emplacements débloqués", "progression", "Emplacements débloqués")
        eng, db = self.engine, self.db
        slots = eng.asi_slots()
        key = tuple(s["id"] for s in slots)
        if key != self._key:
            self._rebuild(slots)
            self._key = key
        self.empty.setVisible(not slots)
        self.box.setVisible(bool(slots))
        tips = self._all_tips() if self._rows else {}
        names = self.feat_names()
        for w in self._rows:
            c = self.ch.ameliorations.get(w["id"], {"mode": "aucun"})
            mode = c.get("mode", "aucun")
            with blocked(w["mode"], w["a1"], w["a2"]):
                w["mode"].setCurrentIndex(list(MODES.values()).index(mode))
                w["a1"].setCurrentIndex(max(0, w["a1"].findText(c.get("a1", "Force"))))
                w["a2"].setCurrentIndex(max(0, w["a2"].findText(c.get("a2", "Dextérité"))))
            fill_combo(w["feat"], names, c.get("don", "") or (names[0] if names else ""), tips)
            feat = db.feats.get(w["feat"].currentText(), {})
            choices = feat.get("carac_choix", [])
            fill_combo(w["fa"], choices or ["—"], c.get("don_carac", "") if c.get("don_carac") in choices
                       else (choices[0] if choices else "—"))
            w["mode"].setEnabled(not w["don_seul"])         # Humain variant / MJ : un don, rien d'autre
            w["feat"].setEnabled(not w["mj"])               # don du MJ : fixé (le retirer puis en ajouter un autre)
            w["a1"].setVisible(mode in ("plus2", "plus1x2"))
            w["a2"].setVisible(mode == "plus1x2")
            w["feat"].setVisible(mode == "don")
            w["fa"].setVisible(mode == "don" and len(choices) > 1)
            w["fa"].setToolTip(rich_tip("Bonus du don", "Choisissez la caractéristique augmentée de +1."))
            if mode == "don" and feat:
                state, msg = eng.feat_status(feat["nom"])
                extra = " (+1 {})".format(choices[0]) if len(choices) == 1 else ""
                w["state"].setText("{} {}{}".format(STATE_ICON[state], msg or "prérequis rempli", extra))
            else:
                w["state"].setText("")
        self._fill_catalog()
