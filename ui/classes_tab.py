"""Onglet « Classes » : multiclassage, niveau par classe, PV, aptitudes avec info-bulles, sorts associés."""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QHBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QSpinBox, QSplitter, QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

from core import rules as R
from . import theme
from .common import BaseTab, blocked, fill_combo, formula_html, formula_tip, make_label, rich_tip
from .dialogs import ask_yes_no


def text_width(widget, text: str, bold: bool = False) -> int:
    """Largeur en pixels d'un libellé dans la police du widget (240 px si Qt n'est pas disponible)."""
    try:
        from PyQt6.QtGui import QFont, QFontMetrics
        f = QFont(widget.font())
        f.setBold(bold)
        return max(240, int(QFontMetrics(f).horizontalAdvance(text)))
    except (TypeError, AttributeError, ValueError, ImportError):
        return 240



class RoadmapStrip(QWidget):
    """Frise de progression 1 → 20 (v29, inspirée de l'écran de classe de Solasta) : une case par niveau avec ses
    icônes (✦ aptitude · ◆ sous-classe · ▲ amélioration ou don · ✧ nouveau niveau de sort) ; niveau actuel encadré,
    niveaux à venir atténués ; infobulle = aptitudes du niveau."""

    LEGEND = "✦ aptitude · ◆ sous-classe · ▲ amélioration ou don · ✧ nouveau niveau de sort"

    def __init__(self):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        self.cells = []
        for lvl in range(1, R.MAX_LEVEL + 1):
            cell = make_label("", align=Qt.AlignmentFlag.AlignCenter)
            cell.setMinimumWidth(30)
            cell.setTextFormat(Qt.TextFormat.RichText)
            lay.addWidget(cell, 1)
            self.cells.append(cell)
        self.setToolTip(self.LEGEND)

    def set_roadmap(self, road: list[dict]) -> None:
        from core.levelup import roadmap_icons
        t = theme.current()
        for cell, col in zip(self.cells, road):
            icons = roadmap_icons(col) or "·"
            color = t.accent_text if col["actuel"] else t.text if col["atteint"] else t.locked
            cell.setText("<div style='color:{c}'><small>{n}</small><br/><b>{i}</b></div>".format(
                c=color, n=col["niveau"], i=icons))
            border = ("2px solid {}".format(t.accent_text) if col["actuel"] else "1px solid {}".format(t.border))
            cell.setStyleSheet("border: {}; border-radius: 6px; padding: 2px;".format(border))
            lines = list(col["aptitudes"])
            if col["choix_sous_classe"]:
                lines.append("Choix de la sous-classe")
            if col["amelioration"]:
                lines.append("Amélioration de caractéristiques ou don")
            if col["sort_niveau"]:
                lines.append("Sorts de niveau {} accessibles".format(col["sort_niveau"]))
            cell.setToolTip(rich_tip("Niveau {}{}".format(col["niveau"], " (actuel)" if col["actuel"] else
                                                           "" if col["atteint"] else " (à venir)"),
                                     "\n".join("• " + x for x in lines) or "Progression des valeurs seulement."))


class ClassPanel(QWidget):
    """Contenu d'un onglet de classe : spécificités, PV, aptitudes et sorts associés."""

    def __init__(self, tab: "ClassesTab", index: int):
        super().__init__()
        self.tab, self.index = tab, index
        lay = QVBoxLayout(self)

        # --- ligne de contrôle : classe / niveau / sous-classe / retrait
        ctl = QHBoxLayout()
        self.class_combo = QComboBox()
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, R.MAX_LEVEL)
        self.sub_combo = QComboBox()
        self.sub_note = make_label("", "muted")
        # largeur réservée en permanence : l'apparition / disparition de « (choix au niveau N) » ne décale rien
        self.sub_note.setFixedWidth(150)
        self.sub_note.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.remove_btn = QPushButton("Retirer cette classe")
        self.remove_btn.setProperty("role", "danger")
        ctl.addWidget(make_label("Classe"))
        ctl.addWidget(self.class_combo, 2)
        ctl.addWidget(make_label("Niveau"))
        ctl.addWidget(self.level_spin)
        ctl.addWidget(make_label("Sous-classe"))
        ctl.addWidget(self.sub_combo, 3)
        ctl.addWidget(self.sub_note)
        ctl.addStretch(1)
        ctl.addWidget(self.remove_btn)
        lay.addLayout(ctl)

        # --- frise de progression 1 → 20 (v29)
        self.roadmap = RoadmapStrip()
        lay.addWidget(self.roadmap)

        # --- Cercle de la Terre (Druide) : choix du terrain — visible uniquement pour cette sous-classe
        self.terrain_row = QWidget()
        tr = QHBoxLayout(self.terrain_row)
        tr.setContentsMargins(0, 0, 0, 0)
        self.terrain_combo = QComboBox()
        self.terrain_combo.setMinimumWidth(160)
        self.terrain_spells = make_label("", "muted", wrap=True)
        tr.addWidget(make_label("🌍 Terrain du cercle", "head"))
        tr.addWidget(self.terrain_combo)
        tr.addWidget(self.terrain_spells, 1)
        self.terrain_row.setVisible(False)
        lay.addWidget(self.terrain_row)

        # --- résumé : PV / ressources / incantation
        row = QHBoxLayout()
        self.hp_box = QGroupBox("Points de vie")
        self.hp_label = make_label("", wrap=True)
        QVBoxLayout(self.hp_box).addWidget(self.hp_label)
        self.res_box = QGroupBox("Ressources de classe")
        self.res_label = make_label("", wrap=True)
        QVBoxLayout(self.res_box).addWidget(self.res_label)
        self.cast_box = QGroupBox("Incantation")
        cl = QVBoxLayout(self.cast_box)
        self.cast_label = make_label("", wrap=True)
        self.cast_btn = QPushButton("Gérer les sorts →")
        cl.addWidget(self.cast_label)
        cl.addWidget(self.cast_btn)
        self.prof_box = QGroupBox("Maîtrises — armes et armures")   # v43 : multiclassage compris
        self.prof_label = make_label("", "muted", wrap=True)
        self.prof_label.setTextFormat(Qt.TextFormat.RichText)
        QVBoxLayout(self.prof_box).addWidget(self.prof_label)
        row.addWidget(self.hp_box, 1)
        row.addWidget(self.res_box, 1)
        row.addWidget(self.cast_box, 1)
        row.addWidget(self.prof_box, 1)
        lay.addLayout(row)

        # --- aptitudes + détail + sorts associés
        split = QSplitter(Qt.Orientation.Horizontal)
        feat_box = QGroupBox("Aptitudes et capacités (survolez pour le détail)")
        fl = QVBoxLayout(feat_box)
        self.future_chk = QCheckBox("Afficher aussi les capacités des niveaux à venir")
        self.feat_list = QListWidget()
        self.feat_list.setMouseTracking(True)
        fl.addWidget(self.future_chk)
        fl.addWidget(self.feat_list)
        split.addWidget(feat_box)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        det_box = QGroupBox("Détail")
        dl = QVBoxLayout(det_box)
        self.detail = QTextBrowser()
        dl.addWidget(self.detail)
        spell_box = QGroupBox("Sorts associés")
        sl = QVBoxLayout(spell_box)
        self.spell_list = QListWidget()
        sl.addWidget(self.spell_list)
        rl.addWidget(det_box, 3)
        rl.addWidget(spell_box, 2)
        split.addWidget(right)
        split.setSizes([700, 500])
        lay.addWidget(split, 1)

        # --- connexions (signaux « utilisateur » uniquement)
        self.class_combo.activated.connect(self._on_class)
        self.level_spin.valueChanged.connect(self._on_level)
        self.sub_combo.activated.connect(self._on_sub)
        self.terrain_combo.activated.connect(self._on_terrain)
        self.remove_btn.clicked.connect(self._on_remove)
        self.cast_btn.clicked.connect(self._on_cast)
        self.future_chk.toggled.connect(lambda _=False: self.refresh())
        self.feat_list.currentRowChanged.connect(self._on_select)
        self._features: list[dict] = []

    # ------------------------------------------------------------------ accès
    @property
    def entry(self) -> dict:
        return self.tab.ch.classes[self.index]

    # ------------------------------------------------------------------ handlers
    def _on_class(self, _=None):
        """Changement de classe : les spécificités et ressources de l'ancienne classe sont retirées (confirmation)."""
        new, old = self.class_combo.currentText(), self.entry["nom"]
        if new == old:
            return
        if not ask_yes_no(self.tab.win, "Changer de classe",
                          "Remplacer « {} » par « {} » ?\n\nLes spécificités de l'ancienne classe seront "
                          "réinitialisées : sous-classe, sorts, ressources dépensées, états de classe (Rage…), "
                          "forme sauvage, manifestations, emplacements dépensés.".format(old, new),
                          yes="Changer de classe", no="Annuler"):
            self.refresh()
            return
        if self.tab.engine.change_class(self.index, new):
            self.tab.changed()
        else:
            self.refresh()

    def _on_level(self, value: int):
        self.tab.engine.set_class_level(self.index, value)
        self.tab.changed()

    def _on_sub(self, _=None):
        text = self.sub_combo.currentText()
        self.entry["sous_classe"] = "" if text.startswith("—") else text
        self.tab.changed()

    def _on_terrain(self, _=None):
        if self.tab.engine.set_land_terrain(self.index, self.terrain_combo.currentText()):
            self.tab.changed()

    def _refresh_profs(self) -> None:
        """Encart « Maîtrises » : ce que CETTE classe apporte (départ ou multiclassage) et le total du personnage."""
        eng, e = self.tab.engine, self.entry
        summ = eng.proficiency_summary()
        mine = [x for x in summ["sources"] if x.get("classe") == e["nom"]]

        def fmt(items):
            return html.escape(", ".join(items)) if items else "—"
        lines = []
        for x in mine:
            lines.append("<b>{}</b><br/>Armures : {}<br/>Armes : {}".format(html.escape(x["source"]), fmt(x["armures"]),
                                                                            fmt(x["armes"])))
        if self.index > 0:
            lines.append("<i>Multiclassage : seules les maîtrises de la table du multiclassage sont gagnées.</i>")
        feats = [x for x in summ["sources"] if x["mode"] == "don"]
        for x in feats:                                   # v45 : maîtrises accordées par un don
            lines.append("<b>{}</b><br/>Armures : {}".format(html.escape(x["source"]), fmt(x["armures"])))
        lines.append("<b>Total du personnage</b><br/>Armures : {}<br/>Armes : {}".format(
            fmt(eng.proficiency_origin_labels("armures")), fmt(eng.proficiency_origin_labels("armes"))))
        gear = eng.unproficient_gear()
        if gear:
            lines.append("<span style='color:{}'>⚠ Porté sans maîtrise : {}</span>".format(
                theme.current().warn, html.escape(", ".join(g["nom"] for g in gear))))
        self.prof_label.setText("<br/>".join(lines))
        self.prof_box.setToolTip(rich_tip("Maîtrises", "\n".join("{} — armures : {} ; armes : {}".format(
            x["source"], ", ".join(x["armures"]) or "—", ", ".join(x["armes"]) or "—") for x in summ["sources"])))

    def _refresh_terrain(self):
        """Sélecteur de terrain : affiché seulement si la sous-classe en propose (Cercle de la Terre)."""
        eng, e = self.tab.engine, self.entry
        terrains = eng.land_terrains(e)
        self.terrain_row.setVisible(bool(terrains))
        if not terrains:
            return
        current = eng.land_terrain(e)
        tips = {t: rich_tip("Terrain : " + t, "Sorts de cercle (niveaux de druide 3 / 5 / 7 / 9) : " + " ; ".join(
            ", ".join(spells[i:i + 2]) for i in range(0, len(spells), 2))) for t, spells in terrains.items()}
        fill_combo(self.terrain_combo, list(terrains), current, tips)
        spells = terrains[current]
        tiers = [3, 5, 7, 9]
        parts = []
        for i, lvl in enumerate(tiers):
            pair = ", ".join(spells[i * 2:i * 2 + 2])
            parts.append(("✔ " if e["niveau"] >= lvl else "🔒 ") + "niv. {} : {}".format(lvl, pair))
        self.terrain_spells.setText("Sorts de cercle toujours préparés — " + " · ".join(parts))

    def _on_remove(self):
        if self.tab.engine.remove_class(self.index):
            self.tab.changed()

    def _on_cast(self):
        self.tab.win.open_magic(self.entry["nom"])

    def _on_select(self, row: int):
        if 0 <= row < len(self._features):
            f = self._features[row]
            state = "" if f["debloque"] else " <i>(non débloquée)</i>"
            self.detail.setHtml("<h3 style='color:{}'>{}</h3><p><i>Niveau {} — {}</i>{}</p><p>{}</p>".format(
                theme.current().accent_text, html.escape(f["nom"]), f["niveau"], html.escape(f["source"]), state, formula_html(self.tab.engine, f["description"], self.entry["nom"])))

    # ------------------------------------------------------------------ rafraîchissement
    def refresh(self):
        eng, db, e = self.tab.engine, self.tab.db, self.entry
        owned = {c["nom"] for i, c in enumerate(self.tab.ch.classes) if i != self.index}
        fill_combo(self.class_combo, [n for n in db.class_names() if n not in owned], e["nom"])
        others = self.tab.ch.niveau_total - e["niveau"]
        with blocked(self.level_spin):
            self.level_spin.setRange(1, max(1, R.MAX_LEVEL - others))
            self.level_spin.setValue(e["niveau"])
        # sous-classe
        need = R.SUBCLASS_LEVEL.get(e["nom"], 3)
        subs = ["— aucune —"] + [s["nom"] for s in db.subclasses(e["nom"])]
        fill_combo(self.sub_combo, subs, e.get("sous_classe") or subs[0])
        unlocked = e["niveau"] >= need
        self.sub_combo.setEnabled(unlocked)
        todo = unlocked and not e.get("sous_classe") and len(subs) > 1
        self.sub_note.setText("○ à choisir" if todo else "" if unlocked else "(choix au niveau {})".format(need))
        self.sub_note.setStyleSheet("color: {}; font-weight: bold;".format(theme.current().ornament) if todo else "")
        self._refresh_terrain()
        self.roadmap.set_roadmap(eng.class_roadmap(e))
        self.remove_btn.setEnabled(len(self.tab.ch.classes) > 1)

        self._refresh_profs()
        # PV
        bd = next((b for b in eng.hp_breakdown() if b["classe"] == e["nom"]), None)
        mode = "moyenne fixe"
        con = R.fmt_bonus(eng.mod("Constitution"))
        first = " — 1er niveau du personnage : dé maximum" if self.index == 0 else ""
        self.hp_label.setText("Dé de vie : {} × {}\nPV apportés : {} (mod. CON {}, {}){}\nPV totaux du personnage : {}".format(
            bd["de"] if bd else "?", e["niveau"], bd["pv"] if bd else 0, con, mode, first, eng.hp_max()))
        res = eng.resources(e)
        self.res_label.setText("\n".join("{} : {}".format(k, v) for k, v in res) or "—")

        # incantation
        c = eng.caster(e["nom"])
        if c:
            kind = {"full": "complet", "half": "demi-incantateur", "artificer": "demi-incantateur (artificier)",
                    "third": "tiers d'incantateur", "pact": "Magie des pactes"}[c["kind"]]
            known = ("Connus : {}".format(c["connus_max"]) if c["connus_max"] is not None
                     else "Préparés : {}".format(c["prepares_max"]))
            self.cast_label.setText("{} ({})\nCaractéristique : {}\nDD des sorts {} / attaque {}\nSorts mineurs : {} — {}"
                                    "\nNiveau de sort max : {}".format(
                                        e["nom"], kind, c["carac"], c["dc"], R.fmt_bonus(c["attaque"]),
                                        c["mineurs_max"], known, c["niveau_max"]))
        else:
            self.cast_label.setText("Cette classe ne lance pas de sorts à ce niveau.")
        self.cast_btn.setEnabled(bool(c))

        # aptitudes
        feats = eng.features(e)
        show_future = self.future_chk.isChecked()
        self._features = [f for f in feats if f["debloque"] or show_future]
        row = self.feat_list.currentRow()
        with blocked(self.feat_list):
            self.feat_list.clear()
            for f in self._features:
                tag = "★ " if f["sous_classe"] else ""
                item = QListWidgetItem("Niv. {:>2} — {}{}".format(f["niveau"], tag, f["nom"]))
                item.setToolTip(formula_tip(eng, "{} (niveau {})".format(f["nom"], f["niveau"]), f["description"], e["nom"]))
                if not f["debloque"]:
                    item.setForeground(QBrush(QColor(theme.current().locked)))
                self.feat_list.addItem(item)
            if self._features:
                self.feat_list.setCurrentRow(min(max(row, 0), len(self._features) - 1))
        self._on_select(self.feat_list.currentRow())

        # sorts associés
        self.spell_list.clear()
        if c:
            for n in eng.domain_spells(e):
                it = QListWidgetItem("● {} (toujours préparé)".format(n))
                sp = db.find_spell(n)
                if sp:
                    it.setToolTip(rich_tip(sp["nom"], sp["description"]))
                self.spell_list.addItem(it)
            if e["nom"] == "Occultiste":                       # sorts injectés par les manifestations occultes
                for g in eng.granted_spells():
                    it = QListWidgetItem("✦ {} — {} ({})".format(g["nom"], g["usage"], g["source"]))
                    if g["sort"]:
                        it.setToolTip(rich_tip(g["nom"], g["sort"]["description"]))
                    self.spell_list.addItem(it)
            for s in sorted(self.tab.ch.sorts.get(e["nom"], []),
                            key=lambda s: ((db.find_spell(s["nom"]) or {}).get("niveau", 9), s["nom"])):
                sp = db.find_spell(s["nom"])
                lvl = "Mineur" if sp and sp["niveau"] == 0 else "Niv. {}".format(sp["niveau"] if sp else "?")
                it = QListWidgetItem("{} — {}".format(lvl, s["nom"]))
                if sp:
                    it.setToolTip(rich_tip(sp["nom"], sp["description"]))
                self.spell_list.addItem(it)
        else:
            self.spell_list.addItem("(aucun)")


class ClassesTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.add_combo = QComboBox()
        self.add_btn = QPushButton("＋ Ajouter une classe (multiclassage)")
        self.multi_chk = QPushButton("⚔ Multiclassage : désactivé")       # interrupteur stylé (cliquable)
        self.multi_chk.setCheckable(True)
        self.multi_chk.setProperty("role", "toggle")
        # largeur fixée sur le libellé le plus long, en GRAS (état activé) : jamais tronqué
        self.multi_chk.setMinimumWidth(text_width(self.multi_chk, "⚔ Multiclassage : désactivé", bold=True) + 44)
        self.multi_chk.setCursor(Qt.CursorShape.PointingHandCursor)
        self.multi_chk.setToolTip(rich_tip("Multiclassage", "Désactivé : une seule classe ; changer de classe "
                                           "remplace entièrement l'ancienne. Activé : vous pouvez cumuler plusieurs "
                                           "classes (capacités superposées, table d'emplacements de sorts combinée, "
                                           "prérequis de caractéristiques vérifiés)."))
        top.addWidget(make_label("Classes du personnage", "title"))
        top.addStretch(1)
        top.addWidget(self.multi_chk)
        top.addWidget(self.add_combo)
        top.addWidget(self.add_btn)
        lay.addLayout(top)
        self.info = make_label("", "muted", wrap=True)
        lay.addWidget(self.info)
        self.tabs = QTabWidget()
        lay.addWidget(self.tabs, 1)
        self.panels: list[ClassPanel] = []
        self._key: tuple = ()
        self.add_btn.clicked.connect(self._on_add)
        self.multi_chk.toggled.connect(self._on_multiclass)

    def _on_multiclass(self, checked: bool):
        others = [c["nom"] for c in self.ch.classes[1:]]
        if not checked and others and not ask_yes_no(
                self.win, "Désactiver le multiclassage",
                "Seule la classe principale ({}) sera conservée.\n\nClasses retirées avec leurs capacités, sorts et "
                "ressources : {}.".format(self.ch.classes[0]["nom"], ", ".join(others)),
                yes="Désactiver", no="Annuler"):
            with blocked(self.multi_chk):
                self.multi_chk.setChecked(True)
            return
        self.engine.set_multiclass(checked)
        self.changed()

    def current_index(self) -> int:
        return max(0, self.tabs.currentIndex())

    def select_class(self, name: str) -> None:
        for i, c in enumerate(self.ch.classes):
            if c["nom"] == name:
                self.tabs.setCurrentIndex(i)

    def _on_add(self):
        name = self.add_combo.currentText()
        if name and self.engine.add_class(name):
            self.changed()
            self.select_class(name)

    def refresh(self):
        key = tuple(i for i, _ in enumerate(self.ch.classes))
        if key != self._key:
            cur = self.tabs.currentIndex()
            with blocked(self.tabs):
                while self.tabs.count():
                    w = self.tabs.widget(0)
                    self.tabs.removeTab(0)
                    w.deleteLater()
                self.panels = []
                for i in range(len(self.ch.classes)):
                    p = ClassPanel(self, i)
                    self.panels.append(p)
                    self.tabs.addTab(p, "")
                self.tabs.setCurrentIndex(min(max(cur, 0), len(self.panels) - 1))
            self._key = key
        for i, p in enumerate(self.panels):
            p.refresh()
            c = self.ch.classes[i]
            self.tabs.setTabText(i, "{} {}".format(c["nom"], c["niveau"]))
        owned = {c["nom"] for c in self.ch.classes}
        free = [n for n in self.db.class_names() if n not in owned]
        fill_combo(self.add_combo, free, free[0] if free else "")
        with blocked(self.multi_chk):
            self.multi_chk.setChecked(self.ch.multiclassage)
        self.multi_chk.setText("⚔ Multiclassage : activé" if self.ch.multiclassage else
                               "⚔ Multiclassage : désactivé")
        can_add = bool(free) and self.ch.niveau_total < R.MAX_LEVEL and self.ch.multiclassage
        self.add_btn.setEnabled(can_add)
        self.add_combo.setEnabled(can_add)
        self.add_btn.setToolTip("" if self.ch.multiclassage else "Activez l'option « Multiclassage » pour ajouter "
                                "une classe.")
        self.info.setText("Niveau global : {} — bonus de maîtrise {}. Chaque onglet détaille une classe ; "
                          "le niveau global de l'en-tête agit sur l'onglet de classe affiché.".format(
                              self.engine.total_level, R.fmt_bonus(self.engine.prof)))
