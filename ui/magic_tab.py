"""
Onglet « Magie » : bibliothèque filtrée par classe, sorts choisis, emplacements de sorts, sorts raciaux et accordés.

Lancer un sort (bouton « Lancer » ou double-clic) dépense le plus petit emplacement disponible ; un sort de
concentration occupe la concentration du personnage (bandeau + marqueur 🧠 sur le sort) et, si une autre
concentration est en cours, une fenêtre demande confirmation avant de la rompre.
"""
from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout,
                             QLineEdit, QPushButton, QScrollArea, QSpinBox, QSplitter, QTableWidget,
                             QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

from core import effects as FX
from core import rules as R
from core.rules import norm
from . import theme
from .dialogs import ask_choice, ask_gm_spell, ask_yes_no
from core import dice as D
from .dice_dialog import d20_icon, roll_damage_dialog, roll_dice
from .manifestations_panel import ManifestationsPanel
from .orbs import OrbBar
from .common import CENTER, BaseTab, blocked, cell, check_item, fill_combo, head, make_label, rich_tip, style_table

ALL_LEVELS = "Tous les niveaux"
ALL_SCHOOLS = "Toutes les écoles"



def spell_quota(cnt: dict, c: dict) -> tuple[str, bool]:
    """Rappel du quota (bibliothèque) : « Sorts mineurs : x / y · Sorts connus : x / y (reste n) » ; True si dépassé."""
    parts, over = [], False
    left = c["mineurs_max"] - cnt["mineurs"]
    over |= left < 0
    parts.append("Sorts mineurs : {} / {}{}".format(cnt["mineurs"], c["mineurs_max"],
                                                    " (reste {})".format(left) if left > 0 else ""))
    if c["connus_max"] is not None:
        left = c["connus_max"] - cnt["sorts"]
        parts.append("Sorts connus : {} / {}{}".format(cnt["sorts"], c["connus_max"],
                                                       " (reste {})".format(left) if left > 0 else ""))
    else:
        left = c["prepares_max"] - cnt["prepares"]
        parts.append("Sorts préparés : {} / {}{} — dans la liste : {}".format(
            cnt["prepares"], c["prepares_max"], " (reste {})".format(left) if left > 0 else "", cnt["sorts"]))
    over |= left < 0
    return ("⚠ " if over else "📌 ") + "  ·  ".join(parts), over


def spell_status(row: dict, concentration: str, blocked_form: bool) -> dict:
    """Statut instantané d'un sort de la liste : texte court + infobulle + drapeau « actif »."""
    sp = row.get("sort") or {}
    actif = bool(concentration) and row["nom"] == concentration
    parts, tips = [], []
    if blocked_form:
        parts.append("🔒 Indisponible")
        tips.append(blocked_form if isinstance(blocked_form, str) else "Aucun sort ne peut être lancé pour l'instant.")
    if actif:
        parts.append("🧠 Concentration active")
        tips.append("Vous maintenez actuellement votre concentration sur ce sort.")
    elif sp.get("concentration"):
        parts.append("Ⓒ Concentration")
        tips.append("Sort de concentration : en lancer un autre romprait le précédent.")
    if sp.get("test") in ("A", "AC"):
        parts.append("🎲 Attaque")
        tips.append("Jet d'attaque de sort (bouton d20 du volet de détail).")
    if row["niveau"] > 0 and not blocked_form:
        if row.get("domaine"):
            parts.append("✔ Toujours préparé")
        elif row.get("prepare", True):
            parts.append("✔ Préparé")
        else:
            parts.append("○ Non préparé")
    return {"texte": " · ".join(parts) or "—", "tip": rich_tip(row["nom"], "<br/>".join(tips)) if tips else "",
            "actif": actif}

DTYPE_NOUNS = ("feu", "froid", "foudre", "force", "tonnerre", "poison")


def dtype_label(dtype: str) -> str:
    """« feu » -> « de feu », « acide » -> « d'acide » (« Dégâts : 5d6 de feu ») ; adjectifs inchangés."""
    t = (dtype or "").strip()
    if t in DTYPE_NOUNS:
        return "de " + t
    if t == "acide":
        return "d'acide"
    return t


from core.data_loader import SAVE_TESTS, save_success_text  # noqa: E402


class MagicTab(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        outer = QVBoxLayout(self)
        # verrou de transformation (Forme sauvage / Métamorphose) : tout l'onglet est grisé
        self.lock_label = make_label("", "banner", wrap=True)
        self.lock_label.setVisible(False)
        outer.addWidget(self.lock_label)
        # Deux sous-onglets : « Sorts » (bibliothèque, emplacements, sorts accordés) et « Manifestations occultes »
        self.sub = QTabWidget()
        outer.addWidget(self.sub)
        spells_page = QWidget()
        root = QVBoxLayout(spells_page)
        self.manif = ManifestationsPanel(win)
        self.sub.addTab(spells_page, "✧ Sorts")
        self.sub.addTab(self.manif, "☠ Manifestations occultes")

        # ---------------- en-tête : classe incantatrice + statistiques
        top = QHBoxLayout()
        self.cls = QComboBox()
        top.addWidget(make_label("Classe incantatrice", "title"))
        top.addWidget(self.cls)
        self.info = make_label("", wrap=True)
        top.addWidget(self.info, 1)
        root.addLayout(top)
        self.empty = make_label("Aucune de vos classes ne lance de sorts à son niveau actuel.", "muted")
        root.addWidget(self.empty)

        # ---------------- forme sauvage : sorts indisponibles (bandeau)
        self.form_block = make_label("", "banner", wrap=True)
        self.form_block.setVisible(False)
        root.addWidget(self.form_block)

        # ---------------- concentration en cours (bandeau)
        conc = QHBoxLayout()
        self.conc_label = make_label("", "banner", wrap=True)
        self.conc_label.setToolTip(rich_tip("Concentration", "Un seul sort de concentration à la fois. Subir des "
                                            "dégâts impose un JS de Constitution (DD 10 ou moitié des dégâts) ; "
                                            "être neutralisé ou mourir rompt la concentration."))
        self.conc_btn = QPushButton("Rompre la concentration")
        self.conc_btn.setToolTip(rich_tip("Rompre la concentration", "Met fin au sort en cours et retire ses effets "
                                          "de la barre d'états."))
        self.conc_btn.setProperty("role", "ghost")
        conc.addWidget(self.conc_label, 1)
        conc.addWidget(self.conc_btn)
        root.addLayout(conc)

        # ======== tableau de bord du mage : [ressources] | [mes sorts par niveau / bibliothèque] | [détail + actions]
        self.body = QSplitter(Qt.Orientation.Horizontal)
        self.body.setChildrenCollapsible(False)
        root.addWidget(self.body, 1)

        # ---------------- colonne gauche (ressources) : sorts mineurs, emplacements 1 à 9, pacte, sorcellerie, repos
        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.left_scroll.setMinimumWidth(255)            # emplacements affichés en entier (niveau, sphères, restants)
        self.left_scroll.setMaximumWidth(320)
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 4, 0)
        self.left_scroll.setWidget(left)
        slots = QGroupBox("Emplacements de sorts")
        slots.setToolTip(rich_tip("Emplacements de sorts", "Cliquez une sphère pour dépenser ou récupérer un "
                                  "emplacement."))
        sl = QGridLayout(slots)
        sl.setHorizontalSpacing(4)
        self.cantrip_count = make_label("", "head", wrap=True)
        self.cantrip_count.setToolTip(rich_tip("Sorts mineurs", "Les sorts mineurs (tours de magie) ne consomment "
                                               "aucun emplacement : utilisables à volonté."))
        sl.addWidget(self.cantrip_count, 0, 0, 1, 3)
        for c, h in enumerate(["Niv.", "Emplacements", "Rest."]):
            sl.addWidget(head(h), 1, c)
        self.slot_rows = []
        for lvl in range(9):
            w = {"name": make_label("{}".format(lvl + 1), "head", align=CENTER),
                 "orbs": OrbBar("emplacement", orb=22, gap=6, per_row=5),
                 "left": make_label("", "head", align=CENTER)}
            for c, k in enumerate(["name", "orbs", "left"]):
                sl.addWidget(w[k], lvl + 2, c)
            w["orbs"].changed.connect(lambda used, n=lvl: self._on_used(n, used))
            self.slot_rows.append(w)
        self.pact_row = {"name": make_label("Pacte", "warn", align=CENTER), "orbs": OrbBar("pacte", orb=22, gap=6, per_row=5),
                         "left": make_label("", "head", align=CENTER)}
        for c, k in enumerate(["name", "orbs", "left"]):
            sl.addWidget(self.pact_row[k], 11, c)
        self.pact_row["orbs"].changed.connect(self._on_pact_used)
        sl.setColumnStretch(1, 1)
        left_lay.addWidget(slots)

        # points de sorcellerie : Ensorceleur ou don de métamagie uniquement
        self.sorc_box = QGroupBox("Points de sorcellerie")
        self.sorc_box.setToolTip(rich_tip("Points de sorcellerie", "Cliquez une sphère pour dépenser ou récupérer "
                                          "un point (métamagie, création d'emplacements)."))
        sg = QGridLayout(self.sorc_box)
        self.sorc_orbs = OrbBar("sorcellerie", orb=20, gap=6, per_row=6)
        self.sorc_left = make_label("", "head", align=CENTER)
        self.sorc_info = make_label("", "muted", wrap=True)
        sg.addWidget(self.sorc_orbs, 0, 0)
        sg.addWidget(self.sorc_left, 0, 1)
        sg.addWidget(self.sorc_info, 1, 0, 1, 2)
        sg.setColumnStretch(0, 1)
        self.sorc_orbs.changed.connect(self._on_sorcery)
        self.sorc_box.setVisible(False)
        left_lay.addWidget(self.sorc_box)
        left_lay.addStretch(1)
        self.body.addWidget(self.left_scroll)

        # ---------------- centre : « Mes sorts » (par niveau, avec statut) | « Bibliothèque » (ajouter des sorts)
        self.center_tabs = QTabWidget()
        mine = QSplitter(Qt.Orientation.Vertical)
        mine.setChildrenCollapsible(False)
        self.chosen_box = chosen = QGroupBox("Sorts du personnage pour cette classe — par niveau")
        cl = QVBoxLayout(chosen)
        top_row = QHBoxLayout()
        self.count_label = make_label("", "muted", wrap=True)
        self.prepared_only = QCheckBox("Sorts préparés seulement")
        self.prepared_only.setToolTip(rich_tip("Filtre d'affichage", "Coché : n'affiche que les sorts préparés "
                                               "(plus les sorts mineurs et les sorts de sous-classe toujours "
                                               "préparés). Décoché : tous les sorts connus / du grimoire. "
                                               "Indispensable pour le Clerc, le Druide, le Paladin ou le Magicien."))
        top_row.addWidget(self.count_label, 1)
        top_row.addWidget(self.prepared_only)
        cl.addLayout(top_row)
        self.chosen = self._table(["Sort", "Niv.", "Préparé", "Statut"])
        self.chosen.setMinimumHeight(160)
        cl.addWidget(self.chosen, 1)
        mine.addWidget(chosen)

        # sorts raciaux : toujours visibles, même pour une classe qui ne lance pas de sorts
        self.racial_box = QGroupBox("Sorts raciaux")
        rl = QVBoxLayout(self.racial_box)
        self.racial_info = make_label("", "muted", wrap=True)
        self.racial = self._table(["Sort", "Niv.", "Disponible", "Utilisation", "Jet", "Trait racial"])
        self.racial.setMinimumHeight(90)
        rl.addWidget(self.racial_info)
        rl.addWidget(self.racial, 1)
        self.racial_box.setVisible(False)
        mine.addWidget(self.racial_box)
        self._racial_rows: list[dict] = []

        # sorts accordés (manifestations occultes, dons, MJ) : injectés automatiquement
        self.granted_box = QGroupBox("Sorts accordés (manifestations occultes, dons, MJ)")
        gl = QVBoxLayout(self.granted_box)
        gtop = QHBoxLayout()
        self.granted_filter = QComboBox()
        self.granted_filter.setToolTip(rich_tip("Filtrer par source", "Manifestations occultes, sorts accordés "
                                                "par le MJ…"))
        self.gm_add_btn = QPushButton("＋ Ajouter un sort (Accordé par le MJ)")
        self.gm_add_btn.setToolTip(rich_tip("Sort accordé par le MJ", "Ajoute un sort obtenu pour des raisons "
                                            "narratives (bénédiction divine, pacte, relique…), avec son utilisation "
                                            "et une note. Il est lançable comme les autres sorts accordés "
                                            "(double-clic) et compte dans les réactions s'il en est une."))
        self.gm_del_btn = QPushButton("Retirer")
        self.gm_del_btn.setProperty("role", "ghost")
        self.gm_del_btn.setToolTip(rich_tip("Retirer", "Retire le sort accordé par le MJ sélectionné."))
        gtop.addWidget(self.granted_filter, 1)
        gtop.addWidget(self.gm_add_btn)
        gtop.addWidget(self.gm_del_btn)
        gl.addLayout(gtop)
        self.granted = self._table(["Sort", "Niv.", "Utilisation", "Source"])
        self.granted.setMinimumHeight(90)
        gl.addWidget(self.granted, 1)
        mine.addWidget(self.granted_box)
        self._granted_rows: list[dict] = []
        mine.setSizes([460, 150, 150])
        # v34 : encarts du séparateur opaques et découpés — au redimensionnement, rien ne doit apparaître par
        # transparence derrière « Sorts accordés » (fond plein + hauteur minimale = contenu entier)
        self._opaque_boxes = [chosen, self.racial_box, self.granted_box]
        for box in self._opaque_boxes:
            box.setObjectName("opaqueBox")
            box.setAutoFillBackground(True)
        self.racial_box.setMinimumHeight(170)
        self.granted_box.setMinimumHeight(190)
        mine.setOpaqueResize(True)
        self.center_tabs.addTab(mine, "📖 Mes sorts")

        self.lib_box = lib = QGroupBox("Bibliothèque de sorts (filtrée sur la liste de la classe)")
        ll = QVBoxLayout(lib)
        # rappel du quota (même logique que « Mes sorts ») : combien de choix il reste, en temps réel
        self.lib_quota = make_label("", "head", wrap=True)
        ll.addWidget(self.lib_quota)
        # recherche instantanée (nom, sans tenir compte des accents) + école + ajout
        flt = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔎 Rechercher un sort (nom)…")
        self.search.setClearButtonEnabled(True)
        self.school_filter = QComboBox()
        self.school_filter.addItem(ALL_SCHOOLS)
        self.school_filter.setToolTip(rich_tip("École de magie", "Ne montre que les sorts de l'école choisie."))
        self.add_btn = QPushButton("Ajouter à mes sorts ✚")
        flt.addWidget(self.search, 1)
        flt.addWidget(self.school_filter)
        flt.addWidget(self.add_btn)
        ll.addLayout(flt)
        # niveaux : boutons-pastilles en un clic (le menu déroulant reste la source de vérité, masqué)
        self.level_filter = QComboBox()
        self.level_filter.addItems([ALL_LEVELS, "Sorts mineurs"] + ["Niveau {}".format(i) for i in range(1, 10)])
        self.level_filter.setVisible(False)
        chips = QHBoxLayout()
        chips.setSpacing(4)
        self.level_chips: list[QPushButton] = []
        for i, label in enumerate(["Tous", "Mineurs"] + [str(n) for n in range(1, 10)]):
            b = QPushButton(label)
            b.setCheckable(True)
            b.setProperty("role", "attune")
            b.setToolTip("Tous les niveaux" if i == 0 else "Sorts mineurs" if i == 1 else "Sorts de niveau {}".format(i - 1))
            b.clicked.connect(lambda _=False, n=i: self._on_level_chip(n))
            chips.addWidget(b)
            self.level_chips.append(b)
        chips.addStretch(1)
        self.unknown_only = QCheckBox("Masquer mes sorts")
        self.unknown_only.setToolTip(rich_tip("Masquer mes sorts", "Cache les sorts déjà ajoutés à votre liste."))
        chips.addWidget(self.unknown_only)
        ll.addLayout(chips)
        self.all_chk = QCheckBox("📜 Ajout manuel par le MJ — sans restriction de liste ni de niveau")
        self.all_chk.setToolTip(rich_tip("Ajout manuel par le MJ", "Par défaut, la bibliothèque ne montre que les "
                                         "sorts que votre personnage peut légalement apprendre : liste de sa classe "
                                         "et niveau de sort maximal atteint. Cochez pour que le MJ ajoute "
                                         "exceptionnellement n'importe quel sort (don, objet, récompense…)."))
        self.lib_rule = make_label("", "muted", wrap=True)
        ll.addWidget(self.lib_rule)
        ll.addWidget(self.all_chk)
        self.lib_result = make_label("", "muted")
        ll.addWidget(self.lib_result)
        self.library = self._table(["Nom", "Niv.", "École", "Incantation", "Portée", "Compos.", "C / R"])
        ll.addWidget(self.library)
        lib.setObjectName("opaqueBox")                   # v43 : fond plein, rien ne transparaît derrière la liste
        lib.setAutoFillBackground(True)
        self.library.viewport().setAutoFillBackground(True)
        self._opaque_boxes.append(lib)
        self.center_tabs.addTab(lib, "📚 Bibliothèque — ajouter / retirer des sorts")
        self.body.addWidget(self.center_tabs)

        # ---------------- droite : détail du sort sélectionné + actions (lancer, jet d'attaque, retirer)
        det = QGroupBox("Détail du sort")
        dl = QVBoxLayout(det)
        self.detail = QTextBrowser()
        self.detail.setMinimumHeight(160)
        self.detail.setOpenLinks(False)
        self.detail.setOpenExternalLinks(False)
        self.detail.anchorClicked.connect(self._on_detail_link)
        self._detail_damage = None
        self._active_table = None                        # table « Mes sorts » sélectionnée en dernier
        dl.addWidget(self.detail, 1)
        self.cast_btn = QPushButton("✨ Lancer le sort")
        self.cast_btn.setToolTip(rich_tip("Lancer", "Même effet qu'un double-clic : choix de la cible pour un buff, "
                                          "emplacement (repli sur un niveau supérieur proposé), concentration."))
        self.attack_btn = QPushButton("Jet d'attaque")
        self.attack_btn.setIcon(d20_icon(22))
        self.attack_btn.setToolTip(rich_tip("Jet d'attaque de sort", "Pour un sort qui demande un jet d'attaque "
                                            "(Trait de feu, Rayon ardent, Décharge occulte…) : lancer de d20 animé "
                                            "avec la caractéristique d'incantation, la maîtrise et les effets actifs."))
        self.attack_btn.setEnabled(False)
        self.remove_btn = QPushButton("Retirer de mes sorts")
        self.remove_btn.setProperty("role", "ghost")
        # v30 : surclassement direct — niveau d'emplacement choisi ici, sans fenêtre
        self.slot_row = QWidget()
        sr = QHBoxLayout(self.slot_row)
        sr.setContentsMargins(0, 0, 0, 0)
        sr.addWidget(make_label("Emplacement"))
        self.slot_spin = QSpinBox()
        self.slot_spin.setPrefix("niveau ")
        self.slot_spin.setToolTip(rich_tip("Surclassement", "Niveau d'emplacement dépensé au lancement. Au-dessus du "
                                           "niveau du sort, il est lancé à un niveau supérieur (effets « aux niveaux "
                                           "supérieurs » de sa description)."))
        sr.addWidget(self.slot_spin, 1)
        self.slot_row.setVisible(False)
        self.slot_spin.valueChanged.connect(self._on_slot_changed)   # v38 : dégâts / description recalculés
        self._spin_spell = None
        self.last_cast_level = 0
        dl.addWidget(self.slot_row)
        for b in (self.cast_btn, self.attack_btn, self.remove_btn):
            dl.addWidget(b)
        dl.addWidget(make_label("Double-clic sur un sort : le lancer. 🧠 concentration en cours · Ⓒ concentration · "
                                "🎲 jet d'attaque · ✔ préparé.", "muted", wrap=True))
        det.setMinimumWidth(250)
        det.setMaximumWidth(400)                         # volet de détail plus étroit : la liste centrale respire
        self.body.addWidget(det)
        self.body.setStretchFactor(0, 0)
        self.body.setStretchFactor(1, 4)
        self.body.setStretchFactor(2, 3)
        self.body.setSizes([280, 820, 360])

        # ---------------- connexions
        self.cls.activated.connect(lambda _=0: self.refresh())
        self.level_filter.activated.connect(lambda _=0: self._fill_library())
        self.all_chk.toggled.connect(lambda _=False: self._fill_library())
        self.school_filter.activated.connect(lambda _=0: self._fill_library())
        self.unknown_only.toggled.connect(lambda _=False: self._fill_library())
        self.search.textChanged.connect(lambda _="": self._fill_library())
        self.add_btn.clicked.connect(self._on_add)
        self.library.cellDoubleClicked.connect(lambda r, c: self._on_add())
        self.library.currentCellChanged.connect(lambda r, c, pr, pc: (self._show_from(self.library, r),
                                                                      self._update_lib_btn()))
        self.chosen.currentCellChanged.connect(lambda r, c, pr, pc: self._on_mine_select(self.chosen, r))
        self.center_tabs.currentChanged.connect(self._on_center_tab)
        self.granted.currentCellChanged.connect(lambda r, c, pr, pc: self._on_mine_select(self.granted, r))
        self.racial.currentCellChanged.connect(lambda r, c, pr, pc: self._on_mine_select(self.racial, r))
        self.remove_btn.clicked.connect(self._on_remove)
        self.chosen.cellClicked.connect(self._on_chosen_click)
        self.sub.currentChanged.connect(lambda _=0: self._refresh_visible_sub())
        self.cast_btn.clicked.connect(self._on_cast_btn)
        self.chosen.cellDoubleClicked.connect(lambda r, c: self._cast_selected(self.chosen, self._chosen_rows, True))
        self.racial.cellDoubleClicked.connect(lambda r, c: self._cast_selected(self.racial, self._racial_rows, False))
        self.granted.cellDoubleClicked.connect(lambda r, c: self._cast_selected(self.granted, self._granted_rows, False))
        self.conc_btn.clicked.connect(self._on_break)
        self.gm_add_btn.clicked.connect(self._on_gm_add)
        self.gm_del_btn.clicked.connect(self._on_gm_remove)
        self.granted_filter.activated.connect(lambda _=0: self._refresh_granted())
        self.attack_btn.clicked.connect(self._on_spell_attack)
        self.prepared_only.toggled.connect(lambda _=False: self.refresh())
        self._lib_rows: list[dict] = []
        self._chosen_rows: list[dict] = []

    @staticmethod
    def _table(headers: list[str]) -> QTableWidget:
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        return style_table(t, stretch_col=0)

    # ------------------------------------------------------------------ état courant
    def current_class(self) -> str:
        return self.cls.currentText()

    def select_class(self, name: str) -> None:
        self.refresh()
        idx = self.cls.findText(name)
        if idx >= 0:
            self.cls.setCurrentIndex(idx)
            self.refresh()

    # ------------------------------------------------------------------ handlers
    def _on_used(self, level_idx: int, value: int):
        """Emplacement dépensé / récupéré : mise à jour locale instantanée, sans recalcul de tout l'onglet."""
        self.ch.emplacements_utilises[level_idx] = value
        total = self.slot_rows[level_idx]["orbs"].total
        self.slot_rows[level_idx]["left"].setText("{} / {}".format(total - value, total))
        self.win.light_changed()

    def _on_pact_used(self, value: int):
        self.ch.pacte_utilises = value
        total = self.pact_row["orbs"].total
        self.pact_row["left"].setText("{} / {}".format(total - value, total))
        self.win.light_changed()

    def _selected_spell(self, table: QTableWidget, rows: list[dict]):
        r = table.currentRow()
        row = rows[r] if 0 <= r < len(rows) else None
        return None if row is None or row.get("separator") else row

    def _on_mine_select(self, table, row: int) -> None:
        """Sélection dans « Mes sorts » (classe, raciaux, accordés par le MJ / manifestations) : table active."""
        self._active_table = table
        self._update_action_btns()                       # d'abord le niveau d'emplacement, puis le détail
        self._show_from(table, row)

    def _on_cast_btn(self) -> None:
        """Lancer : sort de classe (emplacement), sort racial (sans emplacement) ou sort accordé (selon son usage)."""
        if self.center_tabs.currentIndex() != 0:
            return
        table, rows = self._active_rows()
        self._cast_selected(table, rows, table is self.chosen)

    def _on_detail_link(self, url) -> None:
        """Clic sur « 🎲 Dégâts » du détail : animation multi-dés (uniquement depuis « Mes sorts »)."""
        if self._detail_damage is not None and self.center_tabs.currentIndex() == 0:
            roll_damage_dialog(self.win, self._detail_damage)

    def _on_center_tab(self, idx: int):
        self._update_action_btns()
        if idx == 1:
            self._show_from(self.library, self.library.currentRow())
        else:
            self._show_from(self.chosen, self.chosen.currentRow())

    def _on_slot_changed(self, _value: int = 0) -> None:
        """Niveau d'emplacement modifié : description, dégâts, soins et jet de dés suivent le niveau choisi."""
        if self.center_tabs.currentIndex() != 0:
            return
        table, _rows = self._active_rows()
        self._show_from(table, table.currentRow())

    def _slot_level_for(self, table, spell: dict) -> int:
        """Niveau effectif affiché / lancé : sélecteur d'emplacement (grimoire actif), sinon niveau par défaut
        (niveau du pacte pour l'Occultiste, niveau du sort sinon)."""
        lvl = int(spell.get("niveau") or 0)
        if not lvl:
            return 0
        if table is self.chosen and self.slot_row.isVisible() and self._spin_spell == spell.get("nom"):
            return max(lvl, self.slot_spin.value())
        cls = self.current_class() if table in (self.chosen, self.library) else ""
        return self.engine.default_slot_level(spell["nom"], cls)

    def _spell_list_changed(self):
        """
        Ajout / retrait d'un sort : mise à jour ciblée et instantanée — liste « Mes sorts », marquage de la ligne dans
        la bibliothèque et compteurs. Aucun recalcul global ; les autres onglets sont simplement marqués « à
        rafraîchir » (recalculés à leur ouverture).
        """
        name = self.current_class()
        eng = self.engine
        self.win.light_changed()
        with eng.batch():
            c = eng.caster(name) if name else None
            if c:
                self._refresh_chosen(name, c)
                if self.unknown_only.isChecked():
                    self._fill_library()                 # « Masquer mes sorts » : la liste change vraiment
                else:
                    self._mark_owned()
        if hasattr(self.win, "refresh_warnings"):
            self.win.refresh_warnings()

    def _mark_owned(self):
        """Repeint seulement les lignes de la bibliothèque dont l'état « déjà dans mes sorts » a changé."""
        owned = {sp["nom"] for sp in self.ch.sorts.get(self.current_class(), [])}
        painted = getattr(self, "_lib_painted", set())
        t = theme.current()
        for r, row in enumerate(self._lib_rows):
            n = row["nom"]
            if (n in owned) != (n in painted):
                self._paint_lib_row(r, row["sort"], n in owned, t)
        self._lib_painted = owned & {row["nom"] for row in self._lib_rows}

    def _paint_lib_row(self, r: int, sp: dict, owned: bool, t):
        tip = rich_tip(sp["nom"], sp.get("description", ""))
        color = t.good if owned else None
        name = self.current_class()
        allowed, why = self.engine.school_check(name, sp) if name else (True, "")
        if not owned and not allowed:                    # école interdite (sorts libres épuisés) : grisé + motif
            color = t.locked
            tip = rich_tip(sp["nom"], "🔒 " + why + "\n\n" + sp.get("description", ""))
        flags = ("C" if sp.get("concentration") else "") + (" R" if sp.get("rituel") else "")
        vals = [(("✔ " if owned else "") + sp["nom"], "left"), ("0" if sp["niveau"] == 0 else str(sp["niveau"]), "center"),
                (sp.get("ecole", ""), "center"), (sp.get("temps", ""), "center"),
                (sp.get("portee", ""), "center"), (sp.get("composantes", ""), "center"),
                (flags.strip() or "—", "center")]
        for col, (v, al) in enumerate(vals):
            self.library.setItem(r, col, cell(v, al, tip, color, bold=owned and col == 0))

    def _update_lib_btn(self) -> None:
        """Bouton de la bibliothèque : « Ajouter » ou « Retirer » selon le sort sélectionné."""
        sp = self._selected_spell(self.library, self._lib_rows)
        owned = bool(sp) and any(s["nom"] == sp["nom"] for s in self.ch.sorts.get(self.current_class(), []))
        self.add_btn.setText("Retirer de mes sorts ✖" if owned else "Ajouter à mes sorts ✚")
        self.add_btn.setToolTip(rich_tip("Bibliothèque", "Double-clic ou bouton : un sort marqué ✔ (déjà appris) est "
                                         "retiré de vos sorts, un sort non appris y est ajouté."))

    def _on_level_chip(self, idx: int):
        self.level_filter.setCurrentIndex(idx)
        self._fill_library()

    def _on_add(self):
        """Bibliothèque (v43) : sort non appris -> ajouté ; sort déjà appris (✔) -> retiré de vos sorts."""
        name = self.current_class()
        sp = self._selected_spell(self.library, self._lib_rows)
        if not name or not sp:
            return
        lst = self.ch.sorts.setdefault(name, [])
        entry = next((s for s in lst if s["nom"] == sp["nom"]), None)
        if entry is not None:
            if entry.get("accorde"):
                self.win.statusBar().showMessage("« {} » est accordé par votre sous-classe : il ne peut pas être "
                                                 "retiré.".format(sp["nom"]), 6000)
                return
            self.ch.sorts[name] = [s for s in lst if s["nom"] != sp["nom"]]
            self.win.statusBar().showMessage("« {} » retiré de vos sorts.".format(sp["nom"]), 6000)
            self._spell_list_changed()
            self._update_lib_btn()
            return
        if not self.all_chk.isChecked() and not self.engine.can_learn(name, sp["nom"]):
            self.win.statusBar().showMessage("« {} » n'est pas apprenable à votre niveau (mode MJ requis).".format(
                sp["nom"]), 6000)
            return
        ok, why = self.engine.school_check(name, sp)      # v36 : écoles du Chevalier occulte / de l'Arnaqueur
        if not ok and not self.all_chk.isChecked():
            self.win.statusBar().showMessage("« {} » ({}) : {}".format(sp["nom"], sp.get("ecole", ""), why), 8000)
            return
        lst = self.ch.sorts.setdefault(name, [])
        if any(s["nom"] == sp["nom"] for s in lst):
            return
        if why:
            self.win.statusBar().showMessage("« {} » appris comme {}".format(sp["nom"], why[0].lower() + why[1:]), 6000)
        lst.append({"nom": sp["nom"], "prepare": True})
        self._spell_list_changed()
        self._update_lib_btn()

    def _on_remove(self):
        name = self.current_class()
        row = self._selected_spell(self.chosen, self._chosen_rows)
        if not row or row.get("domaine"):
            return
        self.ch.sorts[name] = [s for s in self.ch.sorts.get(name, []) if s["nom"] != row["nom"]]
        self._spell_list_changed()

    def _cast_selected(self, table: QTableWidget, rows: list[dict], use_slot: bool):
        row = self._selected_spell(table, rows)
        if row:
            if "emplacement" in row:                     # sort accordé : la manifestation / le MJ fixe la règle
                use_slot = use_slot or bool(row["emplacement"])
            slot_level = self._slot_level_for(table, row.get("sort") or {"nom": row["nom"], "niveau": row.get("niveau")}) \
                if use_slot else 0
            key = row.get("cle", "") if table is self.granted else ""
            if key and not self.engine.granted_limit_left(key):
                self.win.statusBar().showMessage("{} : déjà utilisé — récupéré au repos long.".format(row["nom"]), 6000)
                return
            if row.get("rituel_seul"):
                self.win.statusBar().showMessage("{} : lancé comme rituel (+10 minutes, sans emplacement).".format(
                    row["nom"]), 6000)
            cls = self.current_class() if table is self.chosen else ""
            if self.cast(row["nom"], use_slot and (row.get("niveau") or 0) > 0, slot_level, limit_key=key,
                         self_only=row.get("cible") == "soi" and table is self.granted):
                from .spell_flow import resolve_spell             # v39 : jets au niveau réellement dépensé
                combat = getattr(self.win, "combat_tab", None)
                resolve_spell(self.win, self.engine, row["nom"], self.last_cast_level or slot_level, cls,
                              getattr(combat, "_attack_flow", None))

    def cast(self, name: str, use_slot: bool = True, slot_level: int = 0, limit_key: str = "",
             self_only: bool = False) -> bool:
        """Lance un sort ; demande confirmation s'il rompt une concentration en cours.
        `limit_key` : compteur d'un sort accordé 1 fois par repos long (manifestation), dépensé si le sort part."""
        if limit_key and not self.engine.granted_limit_left(limit_key):
            self.win.statusBar().showMessage("{} : déjà utilisé — récupéré au repos long.".format(name), 6000)
            return False
        self.last_cast_level = 0
        ok = self._cast(name, use_slot, slot_level, self_only)
        if ok and limit_key:
            self.engine.spend_granted_limit(limit_key)
            self.changed()
        return ok

    def _cast(self, name: str, use_slot: bool = True, slot_level: int = 0, self_only: bool = False) -> bool:
        old = self.engine.concentration_conflict(name)
        if old and not ask_yes_no(
                self.win, "Briser la concentration ?",
                "Vous maintenez déjà votre concentration sur « {} ».\n\nLancer « {} » (sort de concentration) "
                "rompra immédiatement le sort précédent et mettra fin à ses effets.\n\nConfirmer le lancement ?"
                .format(old, name), yes="Lancer quand même", no="Annuler"):
            return False
        if norm(name) == "metamorphose":                 # Métamorphose : choix de la bête puis transformation
            from .druid_tab import start_polymorph
            return start_polymorph(self.win, use_slot)
        eng = self.engine
        spell = self.db.find_spell(name) or {}
        block = eng.spell_block_reason()
        if block:                                        # forme animale ou armure / bouclier non maîtrisé (v43)
            self.win.statusBar().showMessage(block[1], 8000)
            if block[0] == "armure":
                ask_yes_no(self.win, "Incantation impossible", block[1] + "\n\nRetirez l'armure ou le bouclier non "
                           "maîtrisé (onglet Combat ou Inventaire) pour lancer des sorts.", yes="Compris", no="Fermer",
                           default_no=False)
            return False
        # Armure de mage : inefficace si une armure est portée -> avertissement avant de dépenser quoi que ce soit
        armor = eng.wears_armor()
        if norm(spell.get("nom", name)) == "armure de mage" and armor and not ask_yes_no(
                self.win, "Armure de mage inefficace",
                "Vous portez « {} ».\n\nArmure de mage n'a aucun effet tant qu'une armure est équipée : votre CA "
                "ne changera pas. Retirez l'armure (onglet Combat) pour profiter du sort.\n\nLancer quand même ?"
                .format(armor), yes="Lancer quand même", no="Annuler"):
            return False
        # sorts à PV temporaires (Simulacre de vie…) : choix du niveau d'emplacement, jet, injection dans les PV temp.
        if eng.temp_hp_spell(name):
            return self._cast_temp_hp(name, spell, use_slot)
        # 1) sort de buff : cible (sur soi / sur un allié) et variante éventuelle
        target, effect = "", ""
        buffs = eng.buff_options(name)
        if buffs:
            effect = buffs[0]
            if len(buffs) > 1:
                labels = {FX.EFFECTS[k]["nom"]: k for k in buffs}
                picked = ask_choice(self.win, name, "Choisissez l'effet du sort :", list(labels))
                if not picked:
                    return False
                effect = labels[picked]
            if eng.spell_is_personal(name) or self_only:
                target = "soi"                             # portée personnelle, ou manifestation « sur vous-même »
            else:
                picked = ask_choice(self.win, "Cible du sort — " + name,
                                    "Sur soi : les bonus du sort s'appliquent à votre fiche.\nSur un allié / autre : "
                                    "l'emplacement est dépensé et la concentration suivie, sans bonus sur votre fiche.",
                                    ["Sur soi", "Sur un allié / autre"])
                if not picked:
                    return False
                target = "soi" if picked == "Sur soi" else "allie"
        # 2) emplacement : niveau exact, sinon repli sur un niveau supérieur (proposé au joueur)
        level = int(spell.get("niveau") or 0)
        if use_slot and level > 0:
            plan = eng.slot_plan(level)
            if not plan["disponible"]:
                self.win.statusBar().showMessage("Aucun emplacement de niveau {} ou plus disponible.".format(level), 6000)
                return False
            if not plan["exact"] and slot_level <= level and not ask_yes_no(
                    self.win, "Emplacement de niveau supérieur",
                    "Plus d'emplacement de niveau {} disponible.\n\nLancer « {} » avec un emplacement de {} "
                    "(sort lancé à un niveau supérieur) ?".format(
                        level, name, "Pacte (niveau {})".format(plan["niveau"]) if plan["pacte"]
                        else "niveau {}".format(plan["niveau"])), yes="Utiliser cet emplacement", no="Annuler"):
                return False
        res = eng.cast_spell(name, use_slot, target, effect, slot_level)
        self.last_cast_level = res.get("niveau", 0) if res["ok"] else 0
        self.win.statusBar().showMessage(res["message"], 6000)
        if res["ok"]:
            self.changed()
        return res["ok"]

    def _cast_temp_hp(self, name: str, spell: dict, use_slot: bool) -> bool:
        eng, win = self.engine, self.win
        level = int(spell.get("niveau") or 0)
        slot_level = level
        if use_slot and level > 0:
            levels = eng.slot_levels_from(level)
            if not levels:
                win.statusBar().showMessage("Aucun emplacement de niveau {} ou plus disponible.".format(level), 6000)
                return False
            labels = {"Niveau {} — {} PV temporaires".format(lvl, eng.temp_hp_formula(name, lvl)): lvl for lvl in levels}
            picked = ask_choice(win, name, "Niveau d'emplacement à dépenser (surclassement) :", list(labels))
            if not picked:
                return False
            slot_level = labels[picked]
        res = eng.cast_spell(name, use_slot and level > 0, "soi", "", slot_level)
        win.statusBar().showMessage(res["message"], 6000)
        if not res["ok"]:
            return False
        slot = res.get("emplacement") or ""
        used_level = eng.pact()[1] if slot == "pacte" else int(slot[5:]) if slot.startswith("slot:") else level
        formula = eng.temp_hp_formula(name, used_level)
        if D.has_dice(formula):
            r = roll_damage_dialog(win, D.DamageSpec(name, formula, "", "Les PV temporaires ne se cumulent pas : la "
                                                     "valeur la plus haute est conservée.", "pv_temp"))
            amount = r.total if r is not None else D.roll_damage(D.DamageSpec(name, formula)).total
        else:
            amount = D.parse_damage(formula)[1]
        before = self.ch.pv_temporaires
        now = eng.apply_temp_hp(amount)
        win.statusBar().showMessage("{} : {} PV temporaires{}.".format(
            name, amount, "" if now == amount else " (vous gardez vos {} PV temporaires, plus élevés)".format(before)),
            8000)
        self.changed()
        return True

    def _active_rows(self):
        """Table « Mes sorts » active (sorts de classe, raciaux ou accordés) et ses lignes."""
        table = self._active_table if self._active_table is not None else self.chosen
        rows = (self._racial_rows if table is self.racial else self._granted_rows if table is self.granted
                else self._chosen_rows)
        return table, rows

    def _attack_spec(self):
        table, rows = self._active_rows()
        row = self._selected_spell(table, rows)
        if not row:
            return None
        cls = self.current_class() if table is self.chosen else ""
        sp = row.get("sort") or self.db.find_spell(row["nom"]) or {}
        return self.engine.spell_attack_spec(row["nom"], cls, self._slot_level_for(table, sp) if sp else 0)

    def _update_attack_btn(self):
        self._update_action_btns()

    def _update_action_btns(self):
        """
        « Lancer le sort », « Jet d'attaque » et « Retirer » n'agissent que sur le grimoire actif (onglet « Mes sorts ») :
        dans la Bibliothèque (sorts explorés, pas forcément connus ni préparés), ils sont désactivés.
        """
        on_mine = self.center_tabs.currentIndex() == 0
        table, rows = self._active_rows()
        row = self._selected_spell(table, rows) if on_mine else None
        block = self.engine.spell_block_reason()
        armor_block = block is not None and block[0] == "armure"
        usable = row is not None and (block is None or armor_block)   # armure : le clic affiche l'alerte (v43)
        self.cast_btn.setEnabled(usable)
        self.cast_btn.setToolTip(rich_tip("Incantation impossible", block[1]) if armor_block else "")
        self.attack_btn.setEnabled(usable and not armor_block and self._attack_spec() is not None)
        self.remove_btn.setEnabled(row is not None and table is self.chosen and not row.get("domaine"))
        level = int((row or {}).get("niveau") or 0)
        levels = self.engine.slot_levels_from(level) if usable and table is self.chosen and level > 0 else []
        self.slot_row.setVisible(bool(levels))
        if levels:
            name = row["nom"]
            default = self.engine.default_slot_level(name, self.current_class())
            pact_count, plvl = self.engine.pact()
            pact_locked = default == plvl and plvl > level and self.current_class() == "Occultiste" and \
                self.engine.pact_only_caster()
            with blocked(self.slot_spin):
                cur = self.slot_spin.value()
                self.slot_spin.setRange(min(levels), max(levels))
                if self._spin_spell != name:                 # nouveau sort : niveau effectif par défaut
                    cur = default
                self.slot_spin.setValue(cur if min(levels) <= cur <= max(levels) else
                                        (default if min(levels) <= default <= max(levels) else min(levels)))
            self._spin_spell = name
            self.slot_spin.setEnabled(not pact_locked and len(levels) > 1)
            self.slot_spin.setToolTip(rich_tip("Magie des pactes" if pact_locked else "Surclassement",
                                               "Tous vos emplacements de Pacte sont de niveau {} : ce sort est lancé "
                                               "d'office à ce niveau, dégâts et effets compris.".format(plvl)
                                               if pact_locked else
                                               "Niveau d'emplacement dépensé au lancement. Au-dessus du niveau du sort, "
                                               "la description, les dégâts / soins et le jet de dés sont recalculés."))
        else:
            self._spin_spell = None
        tip = "" if on_mine else "Disponible uniquement dans l'onglet « Mes sorts »."
        for b in (self.cast_btn, self.attack_btn):
            b.setStatusTip(tip)

    def _on_spell_attack(self):
        """Jet d'attaque de sort ; s'il touche, dégâts au niveau effectif (surclassement / pacte) — flux du Combat."""
        spec = self._attack_spec()
        flow = getattr(getattr(self.win, "combat_tab", None), "_attack_flow", None)
        if spec is not None and flow is not None and self._detail_damage is not None:
            flow(spec, self._detail_damage)
        else:
            roll_dice(self.win, spec)

    def _on_break(self):
        self.engine.break_concentration()
        self.changed()

    def _on_chosen_click(self, row: int, col: int):
        """Clic dans la colonne « Préparé » (toute la cellule) : bascule la préparation du sort."""
        if col != 2 or not 0 <= row < len(self._chosen_rows):
            return
        r = self._chosen_rows[row]
        block = self.engine.spell_block_reason()
        if r.get("separator") or r.get("domaine") or r["niveau"] == 0 or (block and block[0] == "forme"):
            return
        for sp in self.ch.sorts.get(self.current_class(), []):
            if sp["nom"] == r["nom"]:
                sp["prepare"] = not sp.get("prepare", True)
        self.changed()

    def _show_from(self, table: QTableWidget, row: int):
        rows = (self._lib_rows if table is self.library else
                self._granted_rows if table is self.granted else
                self._racial_rows if table is self.racial else self._chosen_rows)
        if not 0 <= row < len(rows) or rows[row].get("separator"):
            return
        sp = rows[row].get("sort") or {}
        col = theme.current().accent_text
        if not sp:
            self.detail.setHtml("<h3>{}</h3><p><i>Sort absent de la bibliothèque de sorts.</i></p>".format(
                html.escape(rows[row]["nom"])))
            return
        dmg = ""
        self._detail_damage = None
        slot_level = self._slot_level_for(table, sp)
        vals = self.engine.spell_values(sp["nom"], slot_level) if sp.get("niveau") else None
        formula = self.engine.spell_damage_formula(sp["nom"], slot_level) or ("" if vals else sp.get("degats", ""))
        extra = ""
        if vals:
            lvl_txt = "niveau {}".format(vals["niveau"])
            if vals["surclasse"]:
                extra += "<p style='color:{}'><b>⬆ Lancé au niveau {}</b> (sort de niveau {}){}</p>".format(
                    theme.current().good, vals["niveau"], vals["base"],
                    " — Magie des pactes : tous vos emplacements sont de ce niveau" if vals["pacte"] else "")
            if vals["soins"]:
                extra += "<p><b>Soins ({}) :</b> {} points de vie</p>".format(lvl_txt, html.escape(vals["soins"]))
            if vals["pv_temp"]:
                extra += "<p><b>PV temporaires ({}) :</b> {}</p>".format(lvl_txt, html.escape(vals["pv_temp"]))
            if vals["regle_sup"]:
                extra += "<p><b>Au niveau supérieur :</b> {}</p>".format(html.escape(vals["regle_sup"]))
            if vals["bonus"]:
                extra += "<p><small>Ajouté aux dégâts : {}</small></p>".format(html.escape(", ".join(
                    "{} {:+d}".format(lab, v) for lab, v in vals["bonus"])))
        elif sp.get("niveau") == 0:
            st = self.engine.cantrip_stats(sp["nom"]) or {}
            if st.get("effets"):
                extra += "".join("<p>• {}</p>".format(html.escape(e)) for e in st["effets"])
            if st.get("portee") and st["portee"] != sp.get("portee"):
                extra += "<p><b>Portée modifiée :</b> {}</p>".format(html.escape(st["portee"]))
        if sp.get("hors_corpus"):
            extra += "<p><small><i>Sort hors Manuel des joueurs / Xanathar / Tasha : valeurs non auditées.</i></small></p>"
        if formula:
            dtype = sp.get("type_degats", "")
            if table is not self.library and D.has_dice(formula):   # grimoire actif : libellé cliquable -> dés animés
                self._detail_damage = D.DamageSpec("Dégâts — " + sp["nom"], formula, dtype,
                                                   "Emplacement de niveau {}.".format(vals["niveau"]) if vals else
                                                   "Sort mineur : dégâts à l'échelle de votre niveau.")
                dmg = ("<p><b>Dégâts{} :</b> <a href='roll:degats' style='color:{}'>🎲 {} {}</a> "
                       "<small>(cliquez pour lancer les dés)</small></p>").format(
                    " (niveau {})".format(vals["niveau"]) if vals else "", col, html.escape(formula),
                    html.escape(dtype_label(dtype)))
            else:
                dmg = "<p><b>Dégâts{} :</b> {} {}</p>".format(" (niveau {})".format(vals["niveau"]) if vals else "",
                                                             html.escape(formula), html.escape(dtype_label(dtype)))
        test = sp.get("test", "")
        jet = ""
        if test in SAVE_TESTS:                           # v40 : JS de la cible, DD et effet d'une réussite
            res = self.engine.spell_resolution(sp["nom"], slot_level,
                                               self.current_class() if table is self.chosen else "") or {}
            jet = "<p><b>{}</b><br/><span style='color:{}'>{}</span></p>".format(
                html.escape(res.get("ligne_js") or "Jet de sauvegarde ({})".format(test)), theme.current().good,
                html.escape(save_success_text(sp)))
        elif test:
            jet = "<p><b>Jet :</b> {}</p>".format("attaque de sort" if test in ("A", "AC") else
                                                 "attaque d'arme" if test == "Arme" else "JS " + html.escape(test))
        tags = ", ".join(x for x, on in (("concentration", sp.get("concentration")), ("rituel", sp.get("rituel"))) if on)
        blocked_form = self.engine.spells_blocked()
        hint = ("<p style='color:{}'><b>🔒 {}</b></p>".format(theme.current().warn, html.escape(
            (self.engine.spell_block_reason() or ("", "Magie indisponible."))[1]))
                if blocked_form else "<p><small><i>Double-cliquez sur le sort (ou « Lancer ») pour l'incanter"
                                     "{}.</i></small></p>".format(" et appliquer ses effets" if self.engine.buff_options(
                                         sp["nom"]) else ""))
        desc_text, changed = (self.engine.spell_description_at(sp["nom"], slot_level) if sp.get("niveau")
                              else (sp.get("description", ""), []))
        desc_html = html.escape(desc_text).replace("\n", "<br/>")
        for value in dict.fromkeys(changed):             # valeurs surclassées mises en évidence
            esc = html.escape(value)
            desc_html = desc_html.replace(esc, "<b style='color:{}'>{}</b>".format(theme.current().good, esc), 1)
        info = "".join("<tr><td><b>{}</b></td><td>{}</td></tr>".format(k, html.escape(str(v)))
                       for k, v in (("Temps d'incantation", sp.get("temps", "")), ("Portée", sp.get("portee", "")),
                                    ("Composantes", sp.get("composantes", "")), ("Durée", sp.get("duree", "")),
                                    ("Propriétés", tags)) if v)
        self.detail.setHtml(
            "<h3 style='color:{}'>{}</h3><p><i>{} — {}</i></p>"
            "<table cellspacing='0' cellpadding='3'>{}</table>{}{}<hr/><p>{}</p><p><small>Classes : {}</small></p>{}".format(
                col, html.escape(sp["nom"]), "Sort mineur" if sp["niveau"] == 0 else "Niveau {}".format(sp["niveau"]),
                html.escape(sp.get("ecole", "")), info, dmg + extra, jet,
                desc_html,
                html.escape(", ".join(sp.get("classes", [])) or "—"), hint))

    def _refresh_chosen(self, name: str, c: dict):
        """Liste « Mes sorts » (par niveau) + compteurs / quota — seule partie recalculée après un ajout / retrait."""
        eng, ch = self.engine, self.ch
        entry = ch.find_class(name)
        rows: list[dict] = []
        for dom in eng.domain_spells(entry):
            sp = self.db.find_spell(dom)
            rows.append({"nom": dom, "sort": sp, "domaine": True, "prepare": True,
                         "niveau": sp["niveau"] if sp else 1})
        for s in ch.sorts.get(name, []):
            sp = self.db.find_spell(s["nom"])
            rows.append({"nom": s["nom"], "sort": sp, "domaine": False, "prepare": s.get("prepare", True),
                         "niveau": sp["niveau"] if sp else 1})
        rows.sort(key=lambda r: (r["niveau"], r["nom"]))
        total_rows = len(rows)
        if self.prepared_only.isChecked():
            rows = [r for r in rows if r["domaine"] or r["niveau"] == 0 or r["prepare"]]
        self.prepared_only.setText("Sorts préparés seulement ({} / {})".format(len(rows), total_rows)
                                   if self.prepared_only.isChecked() else "Sorts préparés seulement")
        # liste hiérarchisée : une ligne-titre par niveau (Sorts mineurs, Niveau 1, ...)
        grouped: list[dict] = []
        for row in rows:
            if not grouped or (grouped[-1]["niveau"] != row["niveau"]):
                grouped.append({"separator": True, "nom": "", "sort": None, "domaine": False, "prepare": True,
                                "niveau": row["niveau"]})
            grouped.append(row)
        rows = grouped
        self._chosen_rows = rows
        show_prepare = c["mode"] == "prepared"
        blocked_form = (eng.spell_block_reason() or (None, ""))[1]   # texte du motif (forme, armure) ou ""
        t = theme.current()
        with blocked(self.chosen):
            self.chosen.setRowCount(len(rows))
            self.chosen.setColumnHidden(2, not show_prepare)
            for r, row in enumerate(rows):
                if row.get("separator"):
                    lvl = row["niveau"]
                    title = "✦ Sorts mineurs — à volonté" if lvl == 0 else "✦ Niveau {}".format(lvl)
                    self.chosen.setItem(r, 0, cell(title, "left", "", t.accent_text, bold=True, selectable=False))
                    for col in (1, 2, 3):
                        self.chosen.setItem(r, col, cell("", "center", selectable=False))
                    continue
                st = spell_status(row, ch.concentration, blocked_form)
                label = row["nom"] + ("  (sous-classe)" if row["domaine"] else "")
                tip = rich_tip(row["nom"], eng.spell_description_at(row["nom"], 0, name)[0]) if row["sort"] else ""
                color = t.muted if blocked_form else t.good if st["actif"] else t.accent_text if row["domaine"] else None
                self.chosen.setItem(r, 0, cell("    " + label, "left", tip, color, bold=row["domaine"] or st["actif"]))
                eff = eng.default_slot_level(row["nom"], name) if row["niveau"] else 0
                if eff > row["niveau"] > 0:                  # Magie des pactes : surclassé d'office
                    self.chosen.setItem(r, 1, cell("{} ⇒ {}".format(row["niveau"], eff), "center", rich_tip(
                        "Magie des pactes", "Sort de niveau {} lancé d'office au niveau {} (niveau de vos emplacements "
                        "de Pacte) : dégâts et effets surclassés.".format(row["niveau"], eff)), t.good, bold=True))
                else:
                    self.chosen.setItem(r, 1, cell("0" if row["niveau"] == 0 else str(row["niveau"]), "center", tip,
                                                   color))
                if row["niveau"] == 0 or row["domaine"]:
                    self.chosen.setItem(r, 2, cell("—" if row["niveau"] == 0 else "✔", "center", selectable=False))
                else:
                    self.chosen.setItem(r, 2, check_item(row["prepare"], not blocked_form,
                                                         "Sort préparé — cliquez pour basculer"))
                self.chosen.setItem(r, 3, cell(st["texte"], "left", st["tip"],
                                               t.muted if blocked_form else t.good if st["actif"] else None,
                                               bold=st["actif"]))
        self._update_action_btns()
        cnt = eng.spell_counts(name)
        known = ("sorts connus {}/{}".format(cnt["sorts"], c["connus_max"]) if c["connus_max"] is not None
                 else "préparés {}/{} (grimoire/liste : {})".format(cnt["prepares"], c["prepares_max"], cnt["sorts"]))
        self.count_label.setText("Sorts mineurs {}/{} — {}".format(cnt["mineurs"], c["mineurs_max"], known))
        quota, over = spell_quota(cnt, c)
        self.lib_quota.setText(quota)
        self.lib_quota.setStyleSheet("color: {};".format(t.warn if over else t.good))
        self.cantrip_count.setText("Sorts mineurs : {} / {} — à volonté".format(cnt["mineurs"], c["mineurs_max"]))

    # ------------------------------------------------------------------ bibliothèque
    def _fill_library(self, force: bool = False):
        name, t = self.current_class(), theme.current()
        flt = max(0, self.level_filter.currentIndex())
        c0 = self.engine.caster(name) if name else None
        if c0 and not self.all_chk.isChecked() and flt >= 2 and flt - 1 > c0["niveau_max"]:
            flt = 0                                      # niveau devenu inaccessible (sortie du mode MJ)
            self.level_filter.setCurrentIndex(0)
        text = norm(self.search.text().strip())
        school = self.school_filter.currentText()
        hide_owned = self.unknown_only.isChecked()
        owned = {sp["nom"] for sp in self.ch.sorts.get(name, [])}
        c = self.engine.caster(name) if name else None
        for i, b in enumerate(self.level_chips):
            with blocked(b):
                b.setChecked(i == flt)
            b.setVisible(i < 2 or (c is not None and i - 1 <= c["niveau_max"]) or self.all_chk.isChecked())
        key = (name, c["niveau_max"] if c else -1, flt, text, school, hide_owned, self.all_chk.isChecked(),
               frozenset(owned) if hide_owned else None, t.key,
               self.engine.off_school_count(name) if name else 0)       # sorts libres utilisés (écoles imposées)
        if key == getattr(self, "_lib_key", None) and not force:
            self._mark_owned()                           # seules les lignes dont l'état a changé sont repeintes
            return                                       # rien d'autre n'a changé : on évite de reconstruire ~250 lignes
        self._lib_key = key
        spells = self.engine.available_spells(name, self.all_chk.isChecked()) if name else []
        schools = sorted({sp.get("ecole", "") for sp in spells if sp.get("ecole")}, key=norm)
        fill_combo(self.school_filter, [ALL_SCHOOLS] + schools, school if school in schools else ALL_SCHOOLS)
        school = self.school_filter.currentText()
        rows = [sp for sp in spells if (flt == 0 or sp["niveau"] == flt - 1) and text in norm(sp["nom"])
                and (school in ("", ALL_SCHOOLS) or sp.get("ecole") == school)
                and not (hide_owned and sp["nom"] in owned)]
        gm = self.all_chk.isChecked()
        restr = self.engine.school_restriction(name) if name else None
        self.lib_rule.setText("⚠ Mode MJ : tous les sorts, tous niveaux." if gm else
                              "Sorts apprenables : liste {} — niveau 1 à {} (niveau de sort maximal à votre niveau)."
                              .format(c["liste"], c["niveau_max"]) + (
                                  " — {} : sorts d'{} ; sorts libres (toute école) : {} / {} utilisé(s)."
                                  .format(restr["sous_classe"], " ou d'".join(x.lower() for x in restr["ecoles"]),
                                          restr["libres_utilises"], restr["libres_max"]) if restr else "")
                              if c else "")
        self.lib_result.setText("{} sort{} affiché{} sur {}".format(len(rows), "s" * (len(rows) > 1),
                                                                    "s" * (len(rows) > 1), len(spells)))
        self._lib_rows = [{"nom": sp["nom"], "sort": sp} for sp in rows]
        self.library.setUpdatesEnabled(False)
        with blocked(self.library):
            self.library.setRowCount(len(rows))
            for r, sp in enumerate(rows):
                self._paint_lib_row(r, sp, sp["nom"] in owned, t)
        self.library.setUpdatesEnabled(True)
        self._lib_painted = owned & {sp["nom"] for sp in rows}

    # ------------------------------------------------------------------ rafraîchissement
    ALL_SOURCES = "Toutes les sources"

    def _refresh_granted(self):
        """Sorts accordés (manifestations occultes, sorts du MJ), filtrables par source ; section toujours visible
        pour permettre l'ajout d'un sort accordé par le MJ."""
        t = theme.current()
        all_spells = self.engine.granted_spells()
        cats = [self.ALL_SOURCES] + list(dict.fromkeys(g.get("categorie", "Autres") for g in all_spells))
        current = self.granted_filter.currentText()
        fill_combo(self.granted_filter, cats, current if current in cats else self.ALL_SOURCES)
        flt = self.granted_filter.currentText()
        spells = [g for g in all_spells if flt in ("", self.ALL_SOURCES) or g.get("categorie") == flt]
        self._granted_rows = [{"nom": g["nom"], "sort": g["sort"], "niveau": g["niveau"] or 0, "mj": g.get("mj", False),
                               "usage": g["usage"], "emplacement": g.get("emplacement", False),
                               "cle": g.get("cle", ""), "rituel_seul": g.get("rituel_seul", False),
                               "cible": g.get("cible", "")} for g in spells]
        self.granted.setRowCount(len(spells))
        for r, g in enumerate(spells):
            tip = rich_tip(g["nom"], ((g["sort"] or {}).get("description", "") or "Sort absent de la bibliothèque "
                                      "locale.") + "\nSource : " + g["source"])
            active = g["nom"] == self.ch.concentration
            icon = "🧠 " if active else ("📜 " if g.get("mj") else "✦ ")
            self.granted.setItem(r, 0, cell(icon + g["nom"], "left", tip, t.good if active else t.accent_text, bold=True))
            self.granted.setItem(r, 1, cell("—" if g["niveau"] is None else ("0" if g["niveau"] == 0 else str(g["niveau"])),
                                            "center", tip))
            self.granted.setItem(r, 2, cell(g["usage"], "center", tip))
            self.granted.setItem(r, 3, cell(g["source"], "left", tip))
        self.granted.setVisible(bool(all_spells))
        self.gm_del_btn.setEnabled(any(row["mj"] for row in self._granted_rows))

    def _on_gm_add(self):
        from core.engine_extras import GM_USAGES
        res = ask_gm_spell(self.win, sorted(self.db.spells, key=norm), GM_USAGES)
        if res and self.engine.add_gm_spell(*res):
            self.granted_filter.setCurrentIndex(0)
            self.changed()

    def _on_gm_remove(self):
        row = self._selected_spell(self.granted, self._granted_rows)
        if row and row.get("mj"):
            self.engine.remove_gm_spell(row["nom"])
            self.changed()

    def _refresh_racial(self):
        """Encart des sorts raciaux (Races.json) : niveau requis, utilisation, DD / attaque avec la carac. raciale."""
        eng, t = self.engine, theme.current()
        spells = eng.racial_spells()
        self._racial_rows = [{"nom": r["nom"], "sort": r["sort"]} for r in spells]
        self.racial_box.setVisible(bool(spells))
        if not spells:
            return
        ab, choice = eng.racial_spell_ability()
        mod = eng.mod(ab)
        self.racial_info.setText("{} — caractéristique d'incantation : {}{} — DD {} — attaque {}{}".format(
            self.ch.race, ab, " (au choix entre Int, Sag et Cha : la meilleure est retenue)" if choice else "",
            R.spell_save_dc(eng.prof, mod), R.fmt_bonus(R.spell_attack_bonus(eng.prof, mod)),
            " — certains sorts sont à choisir parmi la liste (un seul)" if any(r["au_choix"] for r in spells) else ""))
        self.racial.setRowCount(len(spells))
        for i, r in enumerate(spells):
            sp = r["sort"]
            tip = rich_tip(r["nom"], sp.get("description", ""))
            color = None if r["debloque"] else t.locked
            test = sp.get("test", "")
            jet = ("Attaque {}".format(R.fmt_bonus(r["attaque"])) if test in ("A", "AC") else
                   "JS {} DD {}".format(test, r["dc"]) if test and test != "Arme" else "—")
            self.racial.setItem(i, 0, cell(("🧠 " if r["nom"] == self.ch.concentration else "✦ " if r["debloque"] else "🔒 ") + r["nom"] + (" (au choix)" if r["au_choix"] else ""),
                                           "left", tip, color or t.accent_text, bold=r["debloque"]))
            self.racial.setItem(i, 1, cell("0" if r["niveau"] == 0 else str(r["niveau"]), "center", tip, color))
            self.racial.setItem(i, 2, cell("oui" if r["debloque"] else "niveau {}".format(r["niveau_requis"]), "center",
                                           tip, color))
            self.racial.setItem(i, 3, cell(r["usage"], "center", tip, color))
            self.racial.setItem(i, 4, cell(jet, "center", tip, color))
            self.racial.setItem(i, 5, cell(r["source"], "left", tip, color))

    def _on_sorcery(self, used: int):
        self.engine.set_resource_used("sorcellerie", used)
        total = self.sorc_orbs.total
        self.sorc_left.setText("{} / {}".format(total - self.engine.resource_used("sorcellerie"), total))
        self.win.light_changed()

    def _refresh_sorcery(self):
        """Points de sorcellerie : visibles uniquement pour l'Ensorceleur ou un personnage ayant un don de métamagie."""
        trackers = self.engine.resource_trackers("magie")
        self.sorc_box.setVisible(bool(trackers))
        if trackers:
            tr = trackers[0]
            used = self.engine.resource_used(tr["key"])
            self.sorc_orbs.set_state(tr["total"], used)
            self.sorc_left.setText("{} / {}".format(tr["total"] - used, tr["total"]))
            self.sorc_info.setText(tr["info"] + " — Créer un emplacement : niv. 1 = 2 pts, niv. 2 = 3, niv. 3 = 5, "
                                   "niv. 4 = 6, niv. 5 = 7.")

    def _refresh_visible_sub(self):
        if self.sub.currentIndex() == 1 or not self.win.lazy_refresh:
            if getattr(self, "_manif_stale", True):
                with self.engine.batch():
                    self.manif.refresh()
                self._manif_stale = False

    def _paint_opaque(self) -> None:
        t = theme.current()
        qss = ("QGroupBox#opaqueBox {{ background-color: {bg}; }}"
               "QGroupBox#opaqueBox QTableWidget {{ background-color: {inp}; }}"
               "QGroupBox#opaqueBox QTableWidget::item {{ background-color: transparent; }}").format(
            bg=t.panel, inp=t.input_bg)
        for box in self._opaque_boxes:
            if box.styleSheet() != qss:
                box.setStyleSheet(qss)
        pane = "QTabWidget::pane {{ background-color: {bg}; }}".format(bg=t.panel)   # v43 : pages pleines
        if self.center_tabs.styleSheet() != pane:
            self.center_tabs.setStyleSheet(pane)

    def refresh(self):
        self._paint_opaque()
        self.mark_box(self.chosen_box, "Sorts du personnage pour cette classe — par niveau", "magie", "Sorts")
        eng, ch = self.engine, self.ch
        self._manif_stale = True
        self._refresh_visible_sub()
        self._refresh_racial()
        self._refresh_granted()
        block = eng.spell_block_reason()
        blocked_form = block is not None and block[0] == "forme"
        form = eng.form_status()
        self.form_block.setVisible(False)
        self.lock_label.setVisible(block is not None)
        self.sub.setEnabled(not blocked_form)            # onglet Magie entièrement grisé sous forme animale
        if block is not None and block[0] == "armure":   # v43 : gestion des sorts possible, incantation bloquée
            gear = ", ".join(g["nom"] for g in eng.unproficient_gear())
            self.lock_label.setText("⚠ {} ({})".format(block[1], gear))
            self.lock_label.setToolTip("<qt><b>Armure non maîtrisée</b><br/>Un personnage qui porte une armure ou un "
                                       "bouclier qu'il ne maîtrise pas ne peut pas lancer de sorts. Vous pouvez "
                                       "toujours gérer vos sorts.</qt>")
        if blocked_form and form:
            self.lock_label.setText("{} Magie indisponible sous cette forme ({}).{}".format(
                form["icone"], form["libelle"],
                " Concentration maintenue sur « {} » : vous pouvez utiliser votre action pour en maintenir ou "
                "rediriger les effets.".format(ch.concentration) if ch.concentration else ""))
            self.lock_label.setToolTip("<qt><b>{}</b><br/>Reprenez votre forme normale (bannière en haut de la "
                                       "fiche) pour déverrouiller la magie.</qt>".format(form["libelle"]))
        self.conc_label.setVisible(bool(ch.concentration))
        self.conc_btn.setVisible(bool(ch.concentration))
        if ch.concentration:
            self.conc_label.setText("🧠 Concentration occupée par : {}{} — un nouveau sort de concentration la "
                                    "romprait.".format(ch.concentration, " (sur un allié)" if ch.concentration_cible ==
                                                       "allie" else " (sur vous)" if ch.concentration_effet else ""))
        casters = eng.casters()
        names = [c["classe"] for c in casters]
        self.empty.setVisible(not casters and not eng.pact()[0])
        self.empty.setText("Aucune de vos classes ne lance de sorts à son niveau actuel."
                           + (" Vos sorts raciaux restent utilisables ci-dessous." if eng.racial_spells() else ""))
        for w in (self.left_scroll, self.lib_box, self.chosen_box):    # sorts raciaux / accordés restent visibles
            w.setVisible(bool(casters) or (w is self.left_scroll and bool(eng.pact()[0])))
        self.center_tabs.setTabEnabled(1, bool(casters))
        fill_combo(self.cls, names, self.cls.currentText() if self.cls.currentText() in names else (names[0] if names else ""))
        self.cls.setEnabled(len(names) > 1)

        # emplacements
        slots = eng.spell_slots()
        for i, w in enumerate(self.slot_rows):
            total = slots[i]
            for k in w:
                w[k].setVisible(total > 0)
            if total:
                w["orbs"].set_state(total, ch.emplacements_utilises[i])
                w["left"].setText("{} / {}".format(total - ch.emplacements_utilises[i], total))
        n, lvl = eng.pact()
        for k in self.pact_row:
            self.pact_row[k].setVisible(n > 0)
        if n:
            self.pact_row["name"].setText("Pacte (niv. {})".format(lvl))
            self.pact_row["orbs"].set_state(n, ch.pacte_utilises)
            self.pact_row["left"].setText("{} / {}".format(n - ch.pacte_utilises, n))
        self._refresh_sorcery()

        name = self.current_class()
        c = eng.caster(name) if name else None
        if not c:
            self.info.setText("")
            self._lib_rows, self._chosen_rows = [], []
            self.library.setRowCount(0)
            self.chosen.setRowCount(0)
            return
        self.info.setText("{} — carac. {} — DD {} — attaque {} — sorts mineurs max {} — {} — niveau de sort max {}".format(
            name, c["carac"], c["dc"], R.fmt_bonus(c["attaque"]), c["mineurs_max"],
            "connus max {}".format(c["connus_max"]) if c["connus_max"] is not None
            else "préparés max {}".format(c["prepares_max"]), c["niveau_max"]))
        self._fill_library()

        self._refresh_chosen(name, c)
