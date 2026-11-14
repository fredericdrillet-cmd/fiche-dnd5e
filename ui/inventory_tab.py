"""Onglet « Inventaire & Notes » : équipement (catalogue Equipement/Armes/Armures/Outils), paquetages, charge, outils."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLineEdit,
                             QListWidget, QListWidgetItem, QPlainTextEdit, QPushButton, QSpinBox, QTableWidget,
                             QTabWidget, QVBoxLayout, QWidget, QProgressBar)

from core import rules as R
from core.rules import ABILITIES, norm
from . import theme
from core import weapon_actions as WA
from .game_widgets import ActionChip, clear_layout, use_consumable
from .magic_items_panel import MagicItemsPanel
from .common import CENTER, BaseTab, blocked, cell, fill_combo, indicator_qss, make_label, rich_tip, style_table

ALL_CATEGORIES = "Toutes catégories"
CATEGORIES = [ALL_CATEGORIES, "Équipement", "Paquetage", "Arme", "Armure", "Bouclier", "Outil"]


class InventoryTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        outer = QVBoxLayout(self)
        # Deux sous-onglets : « Équipement » (objets courants, outils, notes) et « Équipement & objets magiques »
        self.sub = QTabWidget()
        outer.addWidget(self.sub)
        page = QWidget()
        root = QHBoxLayout(page)
        # v31 : mannequin d'équipement à gauche (silhouette + 12 cases), le sac et la charge à droite
        from .paperdoll import PaperdollPanel
        self.paperdoll = PaperdollPanel(win)
        root.addWidget(self.paperdoll, 2)
        self.magic_items = MagicItemsPanel(win)
        # v50 : page défilante — rien n'est masqué en fenêtre réduite (case « Sac sans fond » comprise)
        from PyQt6.QtWidgets import QFrame, QScrollArea
        page_scroll = QScrollArea()
        page_scroll.setWidgetResizable(True)
        page_scroll.setFrameShape(QFrame.Shape.NoFrame)
        page.setMinimumSize(1000, 620)
        page_scroll.setWidget(page)
        self.sub.addTab(page_scroll, "🎒 Équipement")
        self.sub.addTab(self.magic_items, "✦ Équipement, objets magiques")

        # =============================== colonne gauche : inventaire
        left = QVBoxLayout()
        add = QGroupBox("Ajouter un objet")
        ag = QGridLayout(add)
        self.category = QComboBox()
        self.category.addItems(CATEGORIES)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher…")
        self.item_combo = QComboBox()
        self.qty = QSpinBox()
        self.qty.setRange(1, 999)
        self.add_btn = QPushButton("Ajouter")
        self.pack_btn = QPushButton("Développer le paquetage")
        self.item_info = make_label("", "muted", wrap=True)
        ag.addWidget(make_label("Catégorie"), 0, 0)
        ag.addWidget(self.category, 0, 1)
        ag.addWidget(self.search, 0, 2, 1, 2)
        ag.addWidget(make_label("Objet"), 1, 0)
        ag.addWidget(self.item_combo, 1, 1, 1, 3)
        ag.addWidget(make_label("Quantité"), 2, 0)
        ag.addWidget(self.qty, 2, 1)
        ag.addWidget(self.add_btn, 2, 2)
        ag.addWidget(self.pack_btn, 2, 3)
        ag.addWidget(self.item_info, 3, 0, 1, 4)
        ag.setColumnStretch(1, 1)
        left.addWidget(add)

        inv = QGroupBox("Équipement porté")
        il = QVBoxLayout(inv)
        # ---- encombrement : jauge, seuils, alerte et « Sac sans fond »
        enc_row = QVBoxLayout()                          # v50 : charge et « Sac sans fond » sur deux lignes
        self.weight = make_label("", "head", wrap=True)
        self.bag = QCheckBox("🎒 Possède un Sac sans fond")
        self.bag.setMinimumHeight(30)
        self.bag.setToolTip(rich_tip("Sac sans fond", "Cochée, la limite de charge est ignorée : aucune alerte de "
                                     "surcharge n'est affichée."))
        enc_row.addWidget(self.weight)
        enc_row.addWidget(self.bag)
        il.addLayout(enc_row)
        self.weight_bar = QProgressBar()
        self.weight_bar.setTextVisible(False)
        self.weight_bar.setFixedHeight(14)
        il.addWidget(self.weight_bar)
        self.weight_warn = make_label("", "muted", wrap=True)
        il.addWidget(self.weight_warn)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Objet", "Qté", "Poids", "Catégorie"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        style_table(self.table, stretch_col=0)
        il.addWidget(self.table)
        btns = QHBoxLayout()
        self.del_btn = QPushButton("Retirer la ligne")
        self.bg_btn = QPushButton("Équipement de l'historique")
        self.use_btn = QPushButton("🧪 Utiliser / boire")
        self.use_btn.setToolTip(rich_tip("Utiliser un consommable", "Boit la potion (ou applique l'huile, "
                                         "l'antitoxine…) sélectionnée : son effet officiel s'applique aussitôt "
                                         "(soins, état actif dans l'onglet Combat, purge du poison…) et la quantité "
                                         "diminue de 1."))
        self.equip_btn = QPushButton("✨ Équiper / déséquiper")
        self.equip_btn.setToolTip(rich_tip("Objet magique", "Équipe l'objet magique sélectionné dans sa case du "
                                           "mannequin (arme : main principale ou distance, armure, bouclier : main "
                                           "secondaire, anneau, cape…) ou le retire. Le bonus +X s'applique dès que "
                                           "l'objet est équipé (et harmonisé s'il l'exige)."))
        self.equip_btn.clicked.connect(self._on_equip_magic)
        btns.addWidget(self.use_btn)
        btns.addWidget(self.equip_btn)
        btns.addWidget(self.del_btn)
        btns.addWidget(self.bg_btn)
        il.addLayout(btns)
        left.addWidget(inv, 1)
        root.addLayout(left, 3)

        # =============================== colonne droite : outils, richesse, notes
        right = QVBoxLayout()
        wbox = QGroupBox("Armes et compétences d'arme — survolez une compétence pour ses règles")
        self.weapons_grid = QGridLayout(wbox)
        self._weapons_key = None
        right.addWidget(wbox)
        tools = QGroupBox("Maîtrises d'outils")
        tl = QVBoxLayout(tools)
        row = QHBoxLayout()
        self.tool_combo = QComboBox()
        self.tool_add = QPushButton("Ajouter")
        self.tool_del = QPushButton("Retirer")
        row.addWidget(self.tool_combo, 1)
        row.addWidget(self.tool_add)
        row.addWidget(self.tool_del)
        tl.addLayout(row)
        self.tool_bg = make_label("", "muted", wrap=True)
        tl.addWidget(self.tool_bg)
        self.tool_list = QListWidget()
        self.tool_list.setMouseTracking(True)
        tl.addWidget(self.tool_list)
        right.addWidget(tools, 3)

        money = QGroupBox("Richesse")
        ml = QHBoxLayout(money)
        self.coins: dict[str, QSpinBox] = {}
        for key, name in (("po", "Or"), ("pa", "Argent"), ("pc", "Cuivre")):
            sp = QSpinBox()
            sp.setRange(0, 99_999_999)
            ml.addWidget(make_label(name))
            ml.addWidget(sp)
            sp.valueChanged.connect(lambda v, k=key: self._on_coin(k, v))
            self.coins[key] = sp
        right.addWidget(money)

        # v33 : « Traits, idéaux, liens, défauts » déplacé dans l'onglet Histoire, Portrait (informations RP) ;
        # l'espace libéré revient aux maîtrises d'outils et aux notes d'équipement
        self.texts: dict[str, QPlainTextEdit] = {}
        box = QGroupBox("Notes d'équipement")
        bl = QVBoxLayout(box)
        ed = QPlainTextEdit()
        ed.setPlaceholderText("Objets prêtés, coffres, montures, biens laissés à l'auberge…")
        bl.addWidget(ed)
        ed.textChanged.connect(lambda k="inventaire": self._on_text(k))
        self.texts["inventaire"] = ed
        right.addWidget(box, 2)
        root.addLayout(right, 2)

        # ---------------- connexions
        self.category.activated.connect(lambda _=0: self._fill_items())
        self.search.textChanged.connect(lambda _="": self._fill_items())
        self.item_combo.activated.connect(lambda _=0: self._update_info())
        self.add_btn.clicked.connect(self._on_add_item)
        self.pack_btn.clicked.connect(self._on_pack)
        self.del_btn.clicked.connect(self._on_del_item)
        self.use_btn.clicked.connect(self._on_use_item)
        self.table.currentCellChanged.connect(lambda r, c, pr, pc: self._update_use_btn())
        self.bag.toggled.connect(self._on_bag)
        self.sub.currentChanged.connect(lambda _=0: self._refresh_visible_sub())
        self.bg_btn.clicked.connect(self._on_bg_gear)
        self.tool_add.clicked.connect(self._on_add_tool)
        self.tool_del.clicked.connect(self._on_del_tool)

    # ------------------------------------------------------------------ catalogue
    def _fill_items(self):
        cat = self.category.currentText()
        text = norm(self.search.text())
        items = [n for n, it in self.db.catalog.items()
                 if (cat == ALL_CATEGORIES or it["categorie"] == cat) and text in norm(n)]
        tips = {n: rich_tip(n, "{} — {} — {}".format(self.db.catalog[n]["description"], self.db.catalog[n]["poids_txt"],
                                                       self.db.catalog[n]["prix"])) for n in items}
        keep = self.item_combo.currentText()
        fill_combo(self.item_combo, items, keep if keep in items else (items[0] if items else ""), tips)
        self._update_info()

    def _update_info(self):
        it = self.db.catalog.get(self.item_combo.currentText())
        self.pack_btn.setEnabled(bool(it) and it["categorie"] == "Paquetage")
        text = "{} — poids {} — prix {}".format(it["description"], it["poids_txt"], it["prix"]) if it else ""
        cmp = self.compare_text(self.item_combo.currentText(), it)
        self.item_info.setText(text + ("\n" + cmp if cmp else ""))

    def compare_text(self, name: str, it) -> str:
        """Comparaison « équipé / survolé » (v31) : Δ de CA pour une armure, de dégâts moyens pour une arme."""
        if not it:
            return ""
        eng = self.engine
        if it["categorie"] == "Armure" and name in self.db.armors:
            c = eng.compare_armor(name)
            bits = ["⚖ Équipée : CA {} → avec celle-ci : CA {} ({:+d})".format(c["ca_avant"], c["ca_apres"],
                                                                           c["delta"])]
            if c["discretion"]:
                bits.append("désavantage en Discrétion")
            if c["force"] and not c["force_ok"]:
                bits.append("Force {} requise : vitesse −3 m".format(c["force"]))
            return " — ".join(bits)
        if it["categorie"] == "Arme" and name in self.db.weapons:
            ranged = norm(str(self.db.weapons[name].get("type", ""))) not in ("cac", "")
            c = eng.compare_weapon(name, ranged)
            if not c:
                return ""
            if not c["actuelle"]:
                return "⚖ Aucune arme équipée : {} ({:.1f} dégâts en moyenne)".format(c["degats_apres"], c["moy_apres"])
            return "⚖ {} : {} ({:.1f}) → {} : {} ({:.1f}, {:+.1f} en moyenne)".format(
                c["actuelle"], c["degats_avant"], c["moy_avant"], name, c["degats_apres"], c["moy_apres"],
                c["delta_moy"]).replace(".", ",")
        return ""

    # ------------------------------------------------------------------ handlers
    def _on_add_item(self):
        name = self.item_combo.currentText()
        if name:
            self.engine.add_item(name, self.qty.value())
            self.changed()

    def _on_pack(self):
        name = self.item_combo.currentText()
        if name:
            self.engine.add_pack(name, expand=True)
            self.changed()

    def _on_bag(self, checked: bool):
        self.ch.sac_sans_fond = bool(checked)
        self.changed()

    def _refresh_visible_sub(self):
        """Sous-onglet « objets magiques » : recalculé seulement quand il est visible (ou s'il était périmé)."""
        if self.sub.currentIndex() == 1 or not self.win.lazy_refresh:
            if getattr(self, "_magic_stale", True):
                with self.engine.batch():
                    self.magic_items.refresh()
                self._magic_stale = False

    def _refresh_encumbrance(self):
        """Jauge de charge : capacité Force × 7,5 kg, seuils de la règle optionnelle, alerte de surcharge."""
        eng, t = self.engine, theme.current()
        enc = eng.encumbrance()
        with blocked(self.bag):
            self.bag.setChecked(enc["sac"])
        self.bag.setStyleSheet(indicator_qss(t))         # v50 : case bien visible quel que soit le thème
        load, cap = enc["poids"], enc["capacite"]
        colors = {"ok": t.good, "encombre": t.accent_text, "lourd": t.warn, "surcharge": t.warn, "sac": t.good}
        color = colors[enc["etat"]]
        if enc["sac"]:
            self.weight.setText("Charge : {} kg — limite ignorée (Sac sans fond)".format(R.fmt_meters(round(load, 2))))
            self.weight_bar.setRange(0, 100)
            self.weight_bar.setValue(0)
        else:
            icon = "⚠ " if enc["etat"] in ("lourd", "surcharge") else ""
            self.weight.setText("{}Charge : {} kg / {} kg (Force {} × 7,5 kg{})".format(
                icon, R.fmt_meters(round(load, 2)), R.fmt_meters(cap), eng.score("Force"),
                " × 2, Puissante carrure" if eng.carry_multiplier() == 2 else ""))
            self.weight_bar.setRange(0, max(1, int(cap * 10)))
            self.weight_bar.setValue(min(int(load * 10), int(cap * 10)))
        self.weight.setStyleSheet("color: {};".format(color))
        self.weight_bar.setStyleSheet(
            "QProgressBar {{ background: {bg}; border: 1px solid {b}; border-radius: 6px; }}"
            "QProgressBar::chunk {{ background: {c}; border-radius: 5px; }}".format(bg=t.input_bg, b=t.border, c=color))
        self.weight_warn.setText("{}  Seuils (règle optionnelle) : encombré > {} kg, lourdement encombré > {} kg."
                                 .format(enc["message"], R.fmt_meters(enc["seuil_encombre"]), R.fmt_meters(enc["seuil_lourd"]))
                                 if not enc["sac"] else enc["message"])
        self.weight_warn.setProperty("role", "warn" if enc["etat"] in ("lourd", "surcharge") else "muted")
        self.weight_warn.style().unpolish(self.weight_warn)
        self.weight_warn.style().polish(self.weight_warn)

    # v45 : les objets magiques sont listés dans l'inventaire principal, après les objets courants
    def magic_row(self, row: int) -> int:
        """Indice de l'objet magique de la ligne (-1 = objet courant)."""
        n = len(self.ch.equipement)
        return row - n if n <= row < n + len(self.ch.objets_magiques) else -1

    def _on_use_item(self):
        r = self.table.currentRow()
        m = self.magic_row(r)
        if m >= 0:
            use_consumable(self.win, "objet", m)
        else:
            use_consumable(self.win, "equipement", r)

    def _update_use_btn(self):
        from core import mechanics as M
        r = self.table.currentRow()
        m = self.magic_row(r)
        if m >= 0:
            ok = M.is_consumable(self.ch.objets_magiques[m]["nom"])
        else:
            ok = 0 <= r < len(self.ch.equipement) and M.is_consumable(self.ch.equipement[r]["nom"])
        self.use_btn.setEnabled(ok)
        if hasattr(self, "equip_btn"):
            self.equip_btn.setEnabled(m >= 0)
            if m >= 0:
                self.equip_btn.setText("✨ Déséquiper" if self.ch.objets_magiques[m].get("equipe") else "✨ Équiper")

    def _on_equip_magic(self) -> bool:
        m = self.magic_row(self.table.currentRow())
        if m < 0:
            return False
        entry = self.ch.objets_magiques[m]
        on = not entry.get("equipe")
        if entry.get("base") and on:
            msg = self.engine.equip_magic_gear(m)
        else:
            self.engine.set_equipped(m, on)
            msg = "{} : {}.".format(self.engine.magic_display_name(entry), "équipé" if on else "rangé")
        self.win.statusBar().showMessage(msg, 6000)
        self.changed()
        return True

    def _on_del_item(self):
        r = self.table.currentRow()
        m = self.magic_row(r)
        if m >= 0:
            self.engine.remove_magic_item(m)
        else:
            self.engine.remove_item(r)
        self.changed()

    def _on_bg_gear(self):
        self.engine.add_background_gear()
        self.changed()

    def _set_qty(self, row: int, value: int):
        if 0 <= row < len(self.ch.equipement):
            self.ch.equipement[row]["qte"] = value
            QTimer.singleShot(0, self.changed)

    def _on_add_tool(self):
        name = self.tool_combo.currentText()
        if name and name not in self.ch.outils:
            self.ch.outils.append(name)
            self.changed()

    def _on_del_tool(self):
        row = self.tool_list.currentRow()
        if 0 <= row < len(self.ch.outils):
            self.ch.outils.pop(row)
            self.changed()

    def _on_coin(self, key: str, value: int):
        self.ch.pieces[key] = value
        self.win.mark_dirty()

    def _on_text(self, key: str):
        setattr(self.ch, key, self.texts[key].toPlainText())
        self.win.mark_dirty()

    # ------------------------------------------------------------------ rafraîchissement
    def _refresh_weapons(self):
        """Armes de l'inventaire et des emplacements de combat, avec dégâts et compétences d'arme (style BG3)."""
        eng = self.engine
        names = [sl["nom"] for sl in self.ch.armes_cac + self.ch.armes_distance if sl.get("nom")]
        names += [i["nom"] for i in self.ch.equipement if i["nom"] in self.db.weapons]
        names = list(dict.fromkeys(names))
        slots = {sl["nom"]: sl for sl in self.ch.armes_cac + self.ch.armes_distance if sl.get("nom")}
        rows = []
        for n in names:
            slot = slots.get(n, {"nom": n, "bonus": 0, "maitrise": None})
            st = eng.weapon_stats(slot)
            if st:
                rows.append((n, st, eng.weapon_actions(slot)))
        key = tuple((n, st["attaque"], st["degats"], tuple((a["cle"], a["dd"]) for a in acts)) for n, st, acts in rows)
        key += (theme.current().key,)
        if key == self._weapons_key:
            return
        self._weapons_key = key
        clear_layout(self.weapons_grid)
        if not rows:
            self.weapons_grid.addWidget(make_label("Aucune arme : équipez-en une dans l'onglet Combat ou ajoutez-la "
                                                   "à l'inventaire.", "muted", wrap=True), 0, 0)
            return
        for r, (n, st, acts) in enumerate(rows):
            self.weapons_grid.addWidget(make_label(n, "head"), r, 0)
            self.weapons_grid.addWidget(make_label("{} · {} {}".format(R.fmt_bonus(st["attaque"]), st["degats"],
                                                                         st["type_degats"]), "muted"), r, 1)
            chips = QWidget()
            cl = QHBoxLayout(chips)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(4)
            for a in acts:
                label = a["nom"] + (" (DD {})".format(a["dd"]) if a["dd"] else "")
                cl.addWidget(ActionChip(a["icone"], label, WA.tooltip_html(a, theme.current().accent_text)))
            cl.addStretch(1)
            self.weapons_grid.addWidget(chips, r, 2)
        self.weapons_grid.setColumnStretch(2, 1)

    def refresh(self):
        eng, db, ch, t = self.engine, self.db, self.ch, theme.current()
        self._magic_stale = True
        self._refresh_visible_sub()
        self.paperdoll.refresh()
        if self.item_combo.count() == 0:
            self._fill_items()
        self._refresh_weapons()
        self._update_use_btn()
        # inventaire
        cur = self.table.currentRow()
        self.table.setRowCount(len(ch.equipement) + len(ch.objets_magiques))
        for r, it in enumerate(ch.equipement):
            info = db.catalog.get(it["nom"])
            tip = rich_tip(it["nom"], "{} — {} — {}".format(info["description"], info["poids_txt"], info["prix"])
                           if info else "Objet personnalisé (hors catalogue).")
            warn = self.engine.item_proficiency_warning(it["nom"])   # v43 : objet équipé non maîtrisé
            if warn:
                tip = rich_tip("⚠ " + it["nom"], warn)
            self.table.setItem(r, 0, cell(("⚠ " if warn else "") + it["nom"], "left", tip,
                                          theme.current().warn if warn else None))
            spin = QSpinBox()
            spin.setRange(1, 999)
            spin.setValue(it["qte"])
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)       # v46 : quantités centrées (comme les objets magiques)
            spin.setObjectName("qtySpin")
            spin.valueChanged.connect(lambda v, row=r: self._set_qty(row, v))
            self.table.setCellWidget(r, 1, spin)
            w = (info["poids"] * it["qte"]) if info else 0.0
            self.table.setItem(r, 2, cell(("{} kg".format(R.fmt_meters(w)) if w else "—"), "center", tip))
            self.table.setItem(r, 3, cell(info["categorie"] if info else "Divers", "center", tip))
        base_row = len(ch.equipement)
        for i, entry in enumerate(ch.objets_magiques):     # v45 : objets magiques (badge ✨, couleur dorée)
            r = base_row + i
            item = eng.magic_item(entry["nom"]) or {}
            label = eng.magic_display_name(entry)
            state = ("équipé" + (" — {}".format(entry.get("emplacement", "").replace("_", " "))
                                 if entry.get("emplacement") else "")) if entry.get("equipe") else "non équipé"
            if item.get("lien"):
                state += ", harmonisé" if entry.get("harmonise") else ", à harmoniser"
            warn = eng.item_proficiency_warning(label) if entry.get("equipe") else ""
            tip = rich_tip(("⚠ " if warn else "✨ ") + label, "{}{}\n{} — {} ({})".format(
                warn + "\n" if warn else "", item.get("description", "")[:500], item.get("type", "Objet magique"),
                item.get("rarete", ""), state))
            self.table.setItem(r, 0, cell(("⚠ " if warn else "") + "✨ " + label, "left", tip,
                                          t.warn if warn else t.accent_text, bold=True))
            self.table.removeCellWidget(r, 1)
            self.table.setItem(r, 1, cell("1", "center", tip))
            w = float(item.get("poids") or (db.catalog.get(entry.get("base", ""), {}) or {}).get("poids", 0) or 0)
            self.table.setItem(r, 2, cell("{} kg".format(R.fmt_meters(w)) if w else "—", "center", tip))
            self.table.setItem(r, 3, cell("Objet magique ({})".format(state), "center", tip, t.accent_text))
        if 0 <= cur < self.table.rowCount():
            self.table.selectRow(cur)
        self._refresh_encumbrance()

        # outils
        names = [x["nom"] for x in db.tools]
        fill_combo(self.tool_combo, names, self.tool_combo.currentText() or (names[0] if names else ""))
        bg = db.backgrounds.get(ch.historique, {})
        self.tool_bg.setText("Outils accordés par l'historique : {}".format(bg.get("outil_maitrise") or "—"))
        with blocked(self.tool_list):
            self.tool_list.clear()
            for n in ch.outils:
                tool = next((x for x in db.tools if x["nom"] == n), None)
                if tool:
                    ab = tool.get("caracteristique", "")
                    bonus = eng.mod(ab) + eng.prof if ab in ABILITIES else eng.prof
                    li = QListWidgetItem("{} — {} {}".format(n, R.ABBR.get(ab, ab), R.fmt_bonus(bonus)))
                    li.setToolTip(rich_tip(n, "Utilisation : {}. Prix {} — poids {}.".format(
                        tool.get("utilisation", "—"), tool.get("prix", "—"), tool.get("poids", "—"))))
                else:
                    li = QListWidgetItem(n)
                self.tool_list.addItem(li)
        for key, sp in self.coins.items():
            with blocked(sp):
                sp.setValue(ch.pieces.get(key, 0))
        for key, ed in self.texts.items():
            if ed.toPlainText() != getattr(ch, key):
                with blocked(ed):
                    ed.setPlainText(getattr(ch, key))
