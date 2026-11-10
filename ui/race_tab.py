"""Onglet « Race, Historique & Langues » : traits raciaux, sous-race, historique, langues maîtrisées."""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
                             QPushButton, QTextBrowser, QVBoxLayout)

from core import rules as R
from . import theme
from .common import BaseTab, blocked, fill_combo, formula_html, formula_tip, make_label, rich_tip
from .race_portrait import RaceIllustration


class RaceTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QHBoxLayout(self)

        # ---------------- race
        rbox = self.race_box = QGroupBox("Race")
        rl = QVBoxLayout(rbox)
        form = QGridLayout()
        self.race = QComboBox()
        self.sub = QComboBox()
        self.sub_label = make_label("Sous-race")
        form.addWidget(make_label("Race"), 0, 0)
        form.addWidget(self.race, 0, 1)
        form.addWidget(self.sub_label, 1, 0)
        form.addWidget(self.sub, 1, 1)
        form.setColumnStretch(1, 1)
        rl.addLayout(form)
        # illustration 8 cm × 8 cm : sous le choix de la race, au-dessus des traits, centrée
        self.portrait = RaceIllustration()
        rl.addWidget(self.portrait, 0, Qt.AlignmentFlag.AlignHCenter)
        self.race_meta = make_label("", "muted", wrap=True)
        rl.addWidget(self.race_meta)
        rl.addWidget(make_label("Traits et pouvoirs (survolez pour le détail)", "muted"))
        self.traits = QListWidget()
        self.traits.setMouseTracking(True)
        rl.addWidget(self.traits, 2)
        self.detail = QTextBrowser()
        rl.addWidget(self.detail, 2)
        root.addWidget(rbox, 1)

        # ---------------- historique
        bbox = self.bg_box = QGroupBox("Historique")
        bl = QVBoxLayout(bbox)
        self.bg = QComboBox()
        bl.addWidget(self.bg)
        self.bg_view = QTextBrowser()
        bl.addWidget(self.bg_view, 1)
        self.add_inv = QPushButton("Ajouter l'équipement et l'or à l'inventaire")
        bl.addWidget(self.add_inv)
        root.addWidget(bbox, 1)

        # ---------------- langues
        lbox = self.lang_box = QGroupBox("Langues")
        ll = QVBoxLayout(lbox)
        ll.addWidget(make_label("Cochez les langues connues du personnage (clic sur la ligne entière).", "muted",
                                wrap=True))
        self.lang_count = make_label("", "head")         # v36 : « Langues choisies : X / Y »
        ll.addWidget(self.lang_count)
        self.lang_list = QListWidget()
        self.lang_list.setMouseTracking(True)
        ll.addWidget(self.lang_list, 1)
        ll.addWidget(make_label("Autres langues (texte libre)", "muted"))
        self.langs = QLineEdit()
        ll.addWidget(self.langs)
        self.add_lang = QPushButton("Noter les langues de l'historique")
        ll.addWidget(self.add_lang)
        root.addWidget(lbox, 1)

        self.race.activated.connect(self._on_race)
        self.sub.activated.connect(self._on_sub)
        self.bg.activated.connect(self._on_bg)
        self.traits.currentRowChanged.connect(self._on_trait)
        self.add_inv.clicked.connect(self._on_add_inv)
        self.add_lang.clicked.connect(self._on_add_lang)
        self.langs.textEdited.connect(self._on_langs)
        self.lang_list.itemChanged.connect(self._on_lang_item)
        self.lang_list.itemPressed.connect(self._on_lang_pressed)
        self.lang_list.itemClicked.connect(self._on_lang_clicked)
        self._lang_pressed_state = None
        self._traits: list[dict] = []

    # ------------------------------------------------------------------ handlers
    def _on_race(self, _=0):
        """Changement de race : langues et compétences de l'ancienne race retirées, puis celles de la nouvelle."""
        new = self.race.currentText()
        if new == self.ch.race:
            return
        removed = self.engine.change_race(new)
        if removed["langues"] or removed["competences"]:
            self.win.statusBar().showMessage("Acquis de l'ancienne race retirés — langues : {} ; compétences : {}."
                                             .format(", ".join(removed["langues"]) or "aucune",
                                                     ", ".join(removed["competences"]) or "aucune"), 8000)
        self.changed()

    def _on_sub(self, _=0):
        text = self.sub.currentText()
        new = "" if text.startswith("—") else text
        if new != self.ch.sous_race:
            self.ch.sous_race = new
            self.engine.apply_race_languages()
            self.engine.apply_race_skills()
        self.changed()

    def _on_bg(self, _=0):
        self.ch.historique = self.bg.currentText()
        self.engine.apply_background()
        self.changed()

    def _on_trait(self, row: int):
        if not self._traits:                              # race sans trait : on efface le détail précédent
            self.detail.setHtml("<p><i>Aucun trait particulier pour cette race.</i></p>")
            return
        if 0 <= row < len(self._traits):
            t = self._traits[row]
            self.detail.setHtml("<h3 style='color:{}'>{}</h3><p>{}</p>".format(
                theme.current().accent_text, html.escape(t["nom"]), formula_html(self.engine, t["description"])))

    def _on_add_inv(self):
        self.engine.add_background_gear()
        self.changed()

    def _on_add_lang(self):
        bg = self.db.backgrounds.get(self.ch.historique)
        if bg and bg.get("langues") and bg["langues"] not in self.ch.langues:
            self.ch.langues = (self.ch.langues + ("; " if self.ch.langues else "") + bg["langues"]).strip()
        self.changed()

    def _on_langs(self, text: str):
        self.ch.langues = text
        self._refresh_lang_count()
        self.win.mark_dirty()

    def _refresh_lang_count(self) -> None:
        """Compteur « Langues choisies : X / Y » : vert si le compte est juste, couleur d'ornement s'il en manque,
        couleur d'alerte au-delà du quota (signalé aussi comme incohérence)."""
        eng, t = self.engine, theme.current()
        have, allowed = eng.languages_known(), eng.languages_allowed()
        color = t.good if have == allowed else t.warn if have > allowed else t.ornament
        state = "" if have == allowed else "  — {} de trop".format(have - allowed) if have > allowed else \
            "  — {} à choisir".format(allowed - have)
        self.lang_count.setText("Langues choisies : {} / {}{}".format(have, allowed, state))
        self.lang_count.setStyleSheet("color: {}; font-weight: bold;".format(color))
        lines = ["Langues fixes (espèce, historique) : {}".format(len(eng.languages_fixed()))]
        lines += ["{} : {} au choix".format(src, n) for src, n in eng.language_grants()]
        self.lang_count.setToolTip(rich_tip("Quota de langues", "\n".join(lines)))

    def _on_lang_pressed(self, item: QListWidgetItem):
        self._lang_pressed_state = item.checkState()

    def _on_lang_clicked(self, item: QListWidgetItem):
        """Clic n'importe où sur la ligne : coche / décoche (sauf si le clic sur la case l'a déjà fait)."""
        if item.checkState() == self._lang_pressed_state:
            item.setCheckState(Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked
                               else Qt.CheckState.Checked)
        self._lang_pressed_state = None

    def _on_lang_item(self, item: QListWidgetItem):
        name = item.data(Qt.ItemDataRole.UserRole)
        langs = [x for x in self.ch.langues_liste if x != name]
        if item.checkState() == Qt.CheckState.Checked:
            langs.append(name)
        self.ch.langues_liste = [n for n in self.db.language_names() if n in langs]
        f = item.font()
        f.setBold(item.checkState() == Qt.CheckState.Checked)
        with blocked(self.lang_list):
            item.setFont(f)
        self._refresh_lang_count()
        self.win.refresh_warnings()                      # pastilles et voyants suivent le quota
        self.win.mark_dirty()

    # ------------------------------------------------------------------ rafraîchissement
    def refresh(self):
        self.mark_box(self.lang_box, "Langues", "race", "Langues")
        self._refresh_lang_count()
        from .common import indicator_qss
        t = theme.current()
        self.lang_list.setStyleSheet(indicator_qss(t, "QListWidget") +
                                     "QListWidget::item {{ padding: 4px 2px; }}"
                                     "QListWidget::item:hover {{ background: {}; }}".format(t.select_bg))
        eng, db, ch, t = self.engine, self.db, self.ch, theme.current()
        fill_combo(self.race, db.race_names(), ch.race)
        subs = db.subraces_of(ch.race)
        self.sub.setVisible(bool(subs))
        self.sub_label.setVisible(bool(subs))
        if subs:
            fill_combo(self.sub, ["— aucune —"] + [s["nom"] for s in subs], ch.sous_race or "— aucune —")
        self.portrait.set_race(ch.race, ch.sous_race)
        race = db.races.get(ch.race, {})
        bonus = ", ".join("{} {}".format(a, R.fmt_bonus(v)) for a, v in eng.race_bonus().items() if v)
        rule = eng.race_rule()
        free = [v for i, v in enumerate(rule["libres"]) if i >= len(ch.bonus_libres) or not ch.bonus_libres[i]]
        if free:                                         # bonus libres pas encore répartis (Humain variant…)
            bonus = (bonus + " ; " if bonus else "") + "{} au choix (sur des caractéristiques différentes, onglet " \
                "Caractéristiques)".format(", ".join(R.fmt_bonus(v) for v in free))
        bonus = bonus or "aucun"
        self.race_meta.setText("Source : {} — Vitesse : {} — Bonus de caractéristiques : {}".format(
            race.get("source", "?"), eng.speed_text(), bonus))
        self._traits = eng.race_traits()
        row = self.traits.currentRow()
        with blocked(self.traits):
            self.traits.clear()
            for tr in self._traits:
                it = QListWidgetItem(tr["nom"])
                it.setToolTip(formula_tip(eng, tr["nom"], tr["description"]))
                self.traits.addItem(it)
            if self._traits:
                self.traits.setCurrentRow(min(max(row, 0), len(self._traits) - 1))
        self._on_trait(self.traits.currentRow())

        fill_combo(self.bg, db.background_names(), ch.historique)
        bg = db.backgrounds.get(ch.historique)
        if bg:
            skills = ", ".join(ch.competences_historique) or "—"
            self.bg_view.setHtml(
                "<h3 style='color:{}'>{}</h3><p><b>Compétences :</b> {}</p><p><b>Langues :</b> {}</p>"
                "<p><b>Outils :</b> {}</p><p><b>Équipement :</b> {}</p><p><b>Or de départ :</b> {} po</p>".format(
                    t.accent_text, html.escape(bg["historique"]), html.escape(skills),
                    html.escape(bg.get("langues") or "—"), html.escape(bg.get("outil_maitrise") or "—"),
                    html.escape(bg.get("inventaire_historique", "")), bg.get("or", 0)))
        else:
            self.bg_view.setHtml("")

        # langues : liste cochable construite une fois, états mis à jour ensuite
        langs = db.languages
        with blocked(self.lang_list):
            if self.lang_list.count() != len(langs):
                self.lang_list.clear()
                for x in langs:
                    it = QListWidgetItem("{} — {}".format(x["nom"], x["categorie"]))
                    it.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                    it.setData(Qt.ItemDataRole.UserRole, x["nom"])
                    it.setToolTip(rich_tip(x["nom"], "Locuteurs typiques : " + x["locuteurs"]))
                    self.lang_list.addItem(it)
            for i, x in enumerate(langs):
                known = x["nom"] in ch.langues_liste
                item = self.lang_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if known else Qt.CheckState.Unchecked)
                f = item.font()
                f.setBold(known)                         # langue connue : en gras, repérable d'un coup d'œil
                item.setFont(f)
        if self.langs.text() != ch.langues:
            with blocked(self.langs):
                self.langs.setText(ch.langues)
