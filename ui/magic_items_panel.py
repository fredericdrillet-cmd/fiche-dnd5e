"""
Sous-onglet « Équipement & objets magiques » de l'Inventaire.

    - catalogue : objets chargés depuis data/objets_magiques.json (filtres type / rareté / harmonisation, recherche) ;
    - équipement porté : objets ajoutés, avec case « équipé », badge interactif d'harmonisation (3 objets maximum,
      davantage avec les aptitudes de l'Artificier), bonus et prérequis vérifiés ;
    - les bonus automatiques (CA, jets de sauvegarde) ne s'appliquent que si l'objet est équipé ET harmonisé (si requis).
"""
from __future__ import annotations

import html

from PyQt6.QtCore import QStringListModel, Qt, QTimer
from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QCompleter, QDoubleSpinBox, QFrame, QGroupBox,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QTableWidget, QTextBrowser,
                             QVBoxLayout, QWidget)

from core.rules import norm
from . import theme
from .common import BaseTab, bulk_fill, cell, check_item, fill_combo, make_label, rich_tip, style_table
from .game_widgets import use_consumable
from .orbs import OrbBar

ALL_TYPES, ALL_RARITIES = "Tous les types", "Toutes les raretés"
RARITY_ORDER = ["commun", "peu commun", "rare", "très rare", "légendaire", "artefact", "variable", "autre"]
STATE_ICON = {"ok": "✔", "ko": "⚠", "?": "?"}
# sources affichées en français (les données gardent leur libellé d'origine)
SOURCE_FR = {"Dungeon Master's Guide": "Guide du maître", "Xanathar's Guide to Everything": "Guide complet de Xanathar",
             "Tasha's Cauldron of Everything": "Le Chaudron des merveilles de Tasha",
             "Player's Handbook": "Manuel des joueurs"}
CUSTOM_TYPES = ["Objet merveilleux", "Anneau", "Arme", "Armure", "Bâton", "Baguette", "Sceptre", "Potion", "Parchemin"]
CUSTOM_RARITIES = ["commun", "peu commun", "rare", "très rare", "légendaire"]


def quick_matches(names, text: str, limit: int = 40) -> list[str]:
    """Autocomplétion tolérante (accents, casse, mots dans le désordre) : « anneau de » -> « Anneau de… » ;
    les noms qui COMMENCENT par la saisie viennent en premier."""
    key = norm(text).strip()
    if not key:
        return []
    words = key.split()
    hits = [n for n in names if all(w in norm(n) for w in words)]
    hits.sort(key=lambda n: (not norm(n).startswith(key), norm(n)))
    return hits[:limit]


EXTRA_TYPES = ["acide", "contondants", "feu", "foudre", "force", "froid", "nécrotiques", "perforants", "poison",
               "psychiques", "radiants", "tonnerre", "tranchants"]
EXTRA_WHEN = [("toujours", "À chaque coup"), ("cible", "Contre une créature"), ("activation", "Si activée")]


def _weapon_fields(weapon_names: list[str]) -> tuple[QWidget, dict]:
    """v52 : champs d'une arme sur mesure — arme de base, bonus magique, deux dégâts supplémentaires."""
    box = QWidget()
    g = QGridLayout(box)
    g.setContentsMargins(0, 0, 0, 0)
    f = {"base": QComboBox(), "bonus": QComboBox(), "extras": []}
    f["base"].addItems(weapon_names)
    f["bonus"].addItems(["+0", "+1", "+2", "+3"])
    g.addWidget(QLabel("Arme de base"), 0, 0)
    g.addWidget(f["base"], 0, 1)
    g.addWidget(QLabel("Bonus magique"), 0, 2)
    g.addWidget(f["bonus"], 0, 3)
    g.addWidget(QLabel("Dégâts en plus"), 1, 0)
    g.addWidget(QLabel("Type"), 1, 1)
    g.addWidget(QLabel("Quand"), 1, 2)
    g.addWidget(QLabel("Précision"), 1, 3)
    for r in range(1, 3):
        dice = QLineEdit()
        dice.setPlaceholderText("ex. 1d4")
        dice.setMinimumWidth(90)
        kind = QComboBox()
        kind.addItems(EXTRA_TYPES)
        when = QComboBox()
        for _k, label in EXTRA_WHEN:
            when.addItem(label)
        note = QLineEdit()
        note.setPlaceholderText("ex. morts-vivants")
        note.setMinimumWidth(180)
        when.setToolTip("« À chaque coup » : ajouté d'office. Les deux autres : case à cocher avant le jet de dégâts.")
        g.addWidget(dice, r + 1, 0)
        g.addWidget(kind, r + 1, 1)
        g.addWidget(when, r + 1, 2)
        g.addWidget(note, r + 1, 3)
        f["extras"].append((dice, kind, when, note))
    g.setColumnStretch(3, 1)
    return box, f


CONDITION_CHOICES = [("charme", "Charmé"), ("effraye", "Effrayé"), ("empoisonne", "Empoisonné"),
                     ("paralyse", "Paralysé"), ("etourdi", "Étourdi"), ("malade", "Malade"),
                     ("epuisement_1", "Épuisement")]
SPELL_USES = [("", "À volonté"), ("1", "1 fois par jour (aube)"), ("n", "Charges (regagnées à l'aube)")]


def _power_fields(spell_names: list[str]) -> tuple[QWidget, dict]:
    """v52 : pouvoirs d'un objet sur mesure — résistances, immunités (dégâts et états), bonus aux JS, un sort."""
    from PyQt6.QtWidgets import QListWidget, QListWidgetItem
    from core.engine_extras import ExtrasMixin
    box = QWidget()
    g = QGridLayout(box)
    g.setContentsMargins(0, 0, 0, 0)
    f = {}

    def checklist(rows):
        lst = QListWidget()
        lst.setMaximumHeight(110)
        for key, label in rows:
            it = QListWidgetItem(label)
            it.setData(Qt.ItemDataRole.UserRole, key)
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Unchecked)
            lst.addItem(it)
        from .common import indicator_qss                 # v52 : cases bien visibles quel que soit le thème
        t = theme.current()
        lst.setStyleSheet(indicator_qss(t, "QListWidget") + "QListWidget::item {{ padding: 3px 2px; }}"
                          "QListWidget::item:hover {{ background: {}; }}".format(t.select_bg))
        return lst
    damage = [(t, t.capitalize()) for t in ExtrasMixin.DAMAGE_TYPES]
    f["res"] = checklist(damage)
    f["imm"] = checklist(damage + [("etat:" + k, "État " + label) for k, label in CONDITION_CHOICES])
    g.addWidget(QLabel("Résistances"), 0, 0)
    g.addWidget(QLabel("Immunités (dégâts, états)"), 0, 1)
    g.addWidget(f["res"], 1, 0)
    g.addWidget(f["imm"], 1, 1)
    f["js"] = QSpinBox()
    f["js"].setRange(0, 3)
    f["js"].setPrefix("Bonus aux jets de sauvegarde +")
    g.addWidget(f["js"], 2, 0, 1, 2)
    f["spell"] = QComboBox()
    f["spell"].setEditable(True)
    f["spell"].addItems(["— aucun sort —"] + spell_names)
    f["spell"].setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    if f["spell"].completer() is not None:
        f["spell"].completer().setFilterMode(Qt.MatchFlag.MatchContains)
        f["spell"].completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    f["use"] = QComboBox()
    for _k, label in SPELL_USES:
        f["use"].addItem(label)
    f["charges"] = QSpinBox()
    f["charges"].setRange(1, 50)
    f["charges"].setValue(3)
    f["charges"].setPrefix("Charges : ")
    f["charges"].setVisible(False)
    f["use"].currentIndexChanged.connect(lambda i: f["charges"].setVisible(SPELL_USES[i][0] == "n"))
    g.addWidget(QLabel("Sort lançable"), 3, 0, 1, 2)
    row = QHBoxLayout()
    row.addWidget(f["spell"], 2)
    row.addWidget(f["use"], 1)
    row.addWidget(f["charges"])
    g.addLayout(row, 4, 0, 1, 2)
    return box, f


def _checked(lst) -> list[str]:
    return [lst.item(i).data(Qt.ItemDataRole.UserRole) for i in range(lst.count())
            if lst.item(i).checkState() == Qt.CheckState.Checked]


def ask_custom_item(parent, name: str = "", weapon_names: list[str] | None = None,
                    spell_names: list[str] | None = None, armor_names: list[str] | None = None) -> dict | None:
    """Formulaire « Objet sur mesure » en une fenêtre : nom, type, rareté (peu commun par défaut), case
    « Harmonisation requise », description courte, poids, bonus de CA. Renvoie le dictionnaire ou None."""
    from .dialogs import BlurBackdrop, ConfirmDialog
    backdrop = BlurBackdrop(parent) if parent is not None else None
    dialog = ConfirmDialog(parent, "Objet sur mesure", "Seul le nom est obligatoire ; les autres champs ont des "
                           "valeurs par défaut.", yes="Créer et ajouter", no="Annuler", default_no=False)
    w = {"nom": QLineEdit(name), "type": QComboBox(), "rarete": QComboBox(), "lien": QCheckBox("Harmonisation requise"),
         "description": QLineEdit(), "poids": QDoubleSpinBox(), "ca": QSpinBox()}
    w["nom"].setPlaceholderText("Nom de l'objet")
    w["type"].addItems(CUSTOM_TYPES)
    w["rarete"].addItems(CUSTOM_RARITIES)
    w["rarete"].setCurrentIndex(1)
    w["description"].setPlaceholderText("Effet en une phrase (facultatif)")
    from .common import indicator_qss
    w["lien"].setStyleSheet(indicator_qss(theme.current()))   # case « Harmonisation requise » bien visible
    w["lien"].setToolTip("Cochée : l'objet doit être harmonisé (repos court) pour fonctionner ; il compte alors "
                         "dans la limite de 3 objets harmonisés.")
    w["lien"].setMinimumHeight(28)
    w["poids"].setSuffix(" kg")
    w["poids"].setDecimals(1)
    w["poids"].setRange(0, 500)
    w["ca"].setRange(0, 3)
    w["ca"].setPrefix("Bonus de CA +")
    card = dialog.findChild(QFrame, "dialogCard")
    lay = card.layout() if card is not None else None
    if lay is not None:
        pos = max(0, lay.count() - 1)
        row = QHBoxLayout()
        for k in ("type", "rarete"):
            row.addWidget(w[k])
        row2 = QHBoxLayout()
        for k in ("poids", "ca"):
            row2.addWidget(w[k])
        lay.insertWidget(pos, w["nom"])
        lay.insertLayout(pos + 1, row)
        lay.insertWidget(pos + 2, w["description"])
        lay.insertLayout(pos + 3, row2)
        lay.insertWidget(pos + 4, w["lien"])                     # sur sa propre ligne : impossible à manquer
    wbox, wf = _weapon_fields(weapon_names or [])                # v52 : arme sur mesure
    dialog.setMinimumWidth(720)
    if lay is not None:
        lay.insertWidget(pos + 5, wbox)
    wbox.setVisible(w["type"].currentText() == "Arme")
    w["type"].currentTextChanged.connect(lambda t: wbox.setVisible(t == "Arme"))
    abox = QWidget()                                     # v53 : armure / bouclier sur mesure
    al = QHBoxLayout(abox)
    al.setContentsMargins(0, 0, 0, 0)
    armor_base = QComboBox()
    armor_base.addItems(armor_names or [])
    armor_base.setToolTip("Armure (ou bouclier) de base : sa CA, sa catégorie, sa force requise et son désavantage "
                          "en Discrétion s'appliquent ; le bonus de CA ci-dessus s'y ajoute.")
    al.addWidget(QLabel("Armure de base :"))
    al.addWidget(armor_base, 1)
    if lay is not None:
        lay.insertWidget(pos + 5, abox)
    abox.setVisible(w["type"].currentText() == "Armure")
    w["type"].currentTextChanged.connect(lambda t: abox.setVisible(t == "Armure"))
    pbox, pf = _power_fields(spell_names or [])                  # v52 : pouvoirs (tous types d'objets)
    if lay is not None:
        lay.insertWidget(pos + 6, QLabel("<b>Pouvoirs de l'objet</b> (facultatif)"))
        lay.insertWidget(pos + 7, pbox)
    try:
        if dialog.exec() != 1 or not w["nom"].text().strip():
            return None
    finally:
        if backdrop is not None:
            backdrop.dispose()
    data = {"nom": w["nom"].text().strip(), "type_": w["type"].currentText(), "rarete": w["rarete"].currentText(),
            "lien": w["lien"].isChecked(), "description": w["description"].text(), "poids": w["poids"].value(),
            "ca": w["ca"].value()}
    imm = _checked(pf["imm"])
    use = SPELL_USES[pf["use"].currentIndex()][0]
    spell = pf["spell"].currentText().strip()
    data.update(resistances=_checked(pf["res"]), immunites=[k for k in imm if not k.startswith("etat:")],
                immunites_etats=[k[5:] for k in imm if k.startswith("etat:")], js_bonus=pf["js"].value(),
                sort=spell if spell in (spell_names or []) else "",
                charges=pf["charges"].value() if use == "n" else 1 if use == "1" else 0)
    if data["type_"] == "Arme" and weapon_names:
        extras = []
        for dice, kind, when, note in wf["extras"]:
            d = dice.text().strip().lower().replace(" ", "")
            if d:
                extras.append({"des": d, "type": kind.currentText(), "condition": EXTRA_WHEN[when.currentIndex()][0],
                               "note": note.text().strip()})
        data.update(base=wf["base"].currentText(), bonus=wf["bonus"].currentIndex(), degats_sup=extras)
    if data["type_"] == "Armure" and armor_names:        # v53 : armure de base + bonus de CA (+0 à +3)
        data.update(base=armor_base.currentText(), bonus=w["ca"].value())
    return data


def ask_gear_base(win, engine, item: dict) -> str:
    """v45 — arme / armure / bouclier magique : choix de l'objet de base (Épée à deux mains, Harnois, Dague…).
    Un seul objet possible -> choisi d'office. Renvoie « » si annulé."""
    from .dialogs import ask_choice
    options = engine.magic_base_options(item["nom"])
    if not options:
        return ""
    if len(options) == 1:
        return options[0]
    what = {"arme": "arme", "armure": "armure", "bouclier": "bouclier"}.get(engine.magic_gear_kind(item), "objet")
    prec = " ({})".format(item["precision"]) if item.get("precision") else ""
    return ask_choice(win, "{} — {} de base".format(item["nom"], what),
                      "Sur quelle {} de base cet objet magique est-il forgé{} ? Le nom affiché et les statistiques "
                      "(dés de dégâts, CA) en dépendent ; le bonus magique s'applique dès que l'objet est équipé."
                      .format(what if what != "bouclier" else "pièce d'équipement", prec), options)


def add_catalog_item(win, engine, item: dict, bonus: int = 0) -> str:
    """Ajoute un objet du catalogue ; une arme / armure / un bouclier magique demande d'abord son objet de base.
    Renvoie le nom affiché (« » si annulé)."""
    if engine.magic_gear_kind(item):
        base = ask_gear_base(win, engine, item)
        return engine.add_magic_gear(item["nom"], base, bonus) if base else ""
    if not engine.add_magic_item(item["nom"], bonus):
        return ""
    from core.item_passives import needs_resistance_choice, DAMAGE_TYPES
    if needs_resistance_choice(item) and engine.ch.objets_magiques:   # v52 : type choisi par le MD
        from .dialogs import ask_choice
        picked = ask_choice(win, item["nom"], "Résistance à quel type de dégâts (choisi par le MD ou tiré au "
                            "hasard) ?", [t.capitalize() for t in DAMAGE_TYPES])
        if picked:
            engine.ch.objets_magiques[-1]["resistance_choisie"] = picked.lower()
    elements = engine.item_rules(item)["elements"]
    entry = engine.ch.objets_magiques[-1] if engine.ch.objets_magiques else {}
    if elements and entry.get("nom") == item["nom"]:     # v52 : nombre de perles… indiqué par le joueur
        from .dialogs import ask_int
        n = ask_int(win, item["nom"], "Nombre de {} ({} — tirage proposé : {}). Indiquez le nombre réel si le MJ "
                    "l'a fixé.".format(elements[1], elements[0], entry.get("elements", 0)),
                    int(entry.get("elements", 0) or 1), 0, 99)
        if n is not None:
            engine.set_item_elements(len(engine.ch.objets_magiques) - 1, n)
    return item["nom"]


def rarity_group(text: str) -> str:
    """Rareté simplifiée pour le filtre (« rare (+2) ou très rare (+3) » -> « variable »)."""
    n = norm(text)
    if "variable" in n or n.count("(") >= 2 or " ou " in n:
        return "variable"
    for key, label in (("tres rare", "très rare"), ("peu commun", "peu commun"), ("legendaire", "légendaire"),
                       ("artefact", "artefact"), ("rare", "rare"), ("commun", "commun")):
        if key in n:
            return label
    return "autre"


def display_name(entry: dict) -> str:
    """« Bouclier +1, +2 ou +3 » avec le bonus choisi 2 -> « Bouclier +2 »."""
    name = entry["nom"]
    return name.replace("+1, +2 ou +3", "+{}".format(entry["bonus"])) if entry.get("bonus") else name


class MagicItemsPanel(BaseTab):
    def __init__(self, win):
        super().__init__(win)
        root = QHBoxLayout(self)

        # ---------------- gauche : catalogue JSON
        lib = QGroupBox("Catalogue d'objets magiques officiels (Guide du maître, Guide complet de Xanathar)")
        ll = QVBoxLayout(lib)
        # v33 : ajout rapide — on tape quelques lettres, l'objet officiel est proposé et pré-rempli
        quick = QHBoxLayout()
        quick.addWidget(make_label("⚡ Ajout rapide", "head"))
        self.quick = QLineEdit()
        self.quick.setPlaceholderText("Tapez un nom : « Anneau de… », « Bottes… », « Cape… » — Entrée pour ajouter")
        self.quick_model = QStringListModel()
        self.completer = QCompleter(self.quick_model, self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setMaxVisibleItems(12)
        self.quick.setCompleter(self.completer)
        quick.addWidget(self.quick, 1)
        self.quick_bonus = QComboBox()
        self.quick_bonus.addItems(["+1", "+2", "+3"])
        self.quick_bonus.setVisible(False)
        quick.addWidget(self.quick_bonus)
        self.quick_add = QPushButton("Ajouter ▶")
        quick.addWidget(self.quick_add)
        self.custom_btn = QPushButton("✚ Objet sur mesure…")
        self.custom_btn.setProperty("role", "ghost")
        self.custom_btn.setToolTip(rich_tip("Objet sur mesure", "Objet absent du catalogue : nom, type, rareté, "
                                            "harmonisation et poids en une seule fenêtre."))
        quick.addWidget(self.custom_btn)
        ll.addLayout(quick)
        self.quick_info = make_label("", "muted", wrap=True)
        ll.addWidget(self.quick_info)
        flt = QHBoxLayout()
        self.type_combo, self.rarity_combo = QComboBox(), QComboBox()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher un objet…")
        flt.addWidget(self.type_combo)
        flt.addWidget(self.rarity_combo)
        flt.addWidget(self.search, 1)
        ll.addLayout(flt)
        self.attune_only = QCheckBox("Harmonisation requise uniquement")
        ll.addWidget(self.attune_only)
        self.library = self._table(["Objet", "Type", "Rareté", "Lien"])
        ll.addWidget(self.library)
        add = QHBoxLayout()
        self.bonus_label = make_label("Bonus :")
        self.bonus_combo = QComboBox()
        self.bonus_combo.addItems(["+1", "+2", "+3"])
        self.add_btn = QPushButton("Ajouter à l'équipement ▶")
        add.addWidget(self.bonus_label)
        add.addWidget(self.bonus_combo)
        add.addStretch(1)
        add.addWidget(self.add_btn)
        ll.addLayout(add)
        root.addWidget(lib, 3)

        # ---------------- droite : équipement magique porté + harmonisation
        right = QVBoxLayout()
        worn = QGroupBox("Équipement, objets magiques")
        wl = QVBoxLayout(worn)
        att = QHBoxLayout()
        att.addWidget(make_label("Harmonisation", "head"))
        # affichage seul : sphères pleines = emplacements libres ; on (dés)harmonise avec les badges du tableau
        self.attune_orbs = OrbBar("harmonisation", per_row=6, interactive=False)
        self.attune_left = make_label("", "stat")
        att.addWidget(self.attune_orbs)
        att.addWidget(self.attune_left)
        att.addStretch(1)
        wl.addLayout(att)
        self.table = self._table(["Équipé", "Objet", "Bonus", "Harmonisation", "Condition"], stretch=1)
        wl.addWidget(self.table)
        self.effects = make_label("", "head", wrap=True)
        wl.addWidget(self.effects)
        self.remove_btn = QPushButton("Retirer l'objet sélectionné")
        self.remove_btn.setProperty("role", "danger")
        self.use_btn = QPushButton("🧪 Boire / utiliser")
        self.use_btn.setToolTip(rich_tip("Utiliser un consommable", "Potions, huiles, élixirs : l'effet officiel "
                                         "s'applique immédiatement (soins, Force de géant, Hâte, purge du poison…) "
                                         "et l'objet est consommé."))
        row_btns = QHBoxLayout()
        row_btns.addWidget(self.use_btn)
        row_btns.addWidget(self.remove_btn)
        wl.addLayout(row_btns)
        right.addWidget(worn, 3)
        det = QGroupBox("Détail de l'objet")
        dl = QVBoxLayout(det)
        self.detail = QTextBrowser()
        dl.addWidget(self.detail)
        right.addWidget(det, 2)
        root.addLayout(right, 4)

        self.type_combo.activated.connect(lambda _=0: self._fill_library())
        self.rarity_combo.activated.connect(lambda _=0: self._fill_library())
        self.search.textChanged.connect(lambda _="": self._fill_library())
        self.attune_only.toggled.connect(lambda _=False: self._fill_library())
        self.library.currentCellChanged.connect(lambda r, c, pr, pc: self._on_library_select(r))
        self.library.cellDoubleClicked.connect(lambda r, c: self._on_add())
        self.add_btn.clicked.connect(self._on_add)
        self.remove_btn.clicked.connect(self._on_remove)
        self.quick.textEdited.connect(self._on_quick_text)
        self.quick.returnPressed.connect(self._on_quick_add)
        self.completer.activated.connect(self._on_quick_pick)
        self.quick_add.clicked.connect(self._on_quick_add)
        self.custom_btn.clicked.connect(lambda: self._on_custom(self.quick.text()))
        self.use_btn.clicked.connect(lambda: use_consumable(self.win, "objet", self.table.currentRow()))
        self.table.currentCellChanged.connect(lambda r, c, pr, pc: self._show_worn(r))
        self.table.cellClicked.connect(self._on_table_click)
        self._lib_rows: list[str] = []
        self.bonus_label.setVisible(False)
        self.bonus_combo.setVisible(False)

    @staticmethod
    def _table(headers: list[str], stretch: int = 0) -> QTableWidget:
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        return style_table(t, stretch_col=stretch, row_h=38)

    # ------------------------------------------------------------------ catalogue
    def _fill_library(self, force: bool = False):
        t = theme.current()
        kind, rar, text = self.type_combo.currentText(), self.rarity_combo.currentText(), norm(self.search.text())
        key = (kind, rar, text, self.attune_only.isChecked(), t.key, len(self.db.magic_items))
        if not force and key == getattr(self, "_lib_key", None):
            return                                        # v52 : catalogue inchangé — pas de reconstruction
        self._lib_key = key
        items = [i for i in self.db.magic_items.values()
                 if (kind == ALL_TYPES or i["type"] == kind) and (rar == ALL_RARITIES or rarity_group(i["rarete"]) == rar)
                 and (not self.attune_only.isChecked() or i["lien"]) and text in norm(i["nom"])]
        self._lib_rows = [i["nom"] for i in items]
        with bulk_fill(self.library):
            self.library.setRowCount(len(items))
            for r, i in enumerate(items):
                tip = "{} — {}".format(i["nom"], i["description"][:300])   # le détail complet est dans le panneau
                kind_txt = i["type"] + (" ({})".format(i["precision"]) if i["precision"] else "")
                self.library.setItem(r, 0, cell(i["nom"], "left", tip))
                self.library.setItem(r, 1, cell(kind_txt, "center", tip))
                self.library.setItem(r, 2, cell(i["rarete"], "center", tip))
                self.library.setItem(r, 3, cell("✦" if i["lien"] else "—", "center",
                                                i["condition"] or ("Harmonisation requise" if i["lien"] else
                                                                   "Aucune harmonisation"),
                                                t.accent_text if i["lien"] else None, bold=i["lien"]))

    def _selected_library_item(self) -> dict | None:
        r = self.library.currentRow()
        return self.db.magic_items.get(self._lib_rows[r]) if 0 <= r < len(self._lib_rows) else None

    def _on_library_select(self, row: int):
        item = self._selected_library_item()
        variable = bool(item and item["variable"])
        self.bonus_label.setVisible(variable)
        self.bonus_combo.setVisible(variable)
        if item:
            self._show_item(item, None)

    def _on_add(self):
        item = self._selected_library_item()
        if not item:
            return
        added = add_catalog_item(self.win, self.engine, item,
                                 self.bonus_combo.currentIndex() + 1 if item["variable"] else 0)
        if added:
            self.win.statusBar().showMessage("✨ {} ajouté à l'inventaire{}.".format(
                added, " — équipez-le pour appliquer son bonus" if self.engine.magic_gear_kind(item) else ""), 6000)
            self.changed()

    # ------------------------------------------------------------------ ajout rapide (v33)
    def _quick_item(self) -> dict | None:
        return self.db.magic_items.get(self.quick.text().strip())

    def _on_quick_text(self, text: str) -> None:
        hits = quick_matches(self.db.magic_items, text)
        self.quick_model.setStringList(hits)
        if hits and hasattr(self.completer, "complete"):
            self.completer.complete()
        self._update_quick()

    def _on_quick_pick(self, name: str) -> None:
        self.quick.setText(name)
        self._update_quick()

    def _update_quick(self) -> None:
        item = self._quick_item()
        self.quick_bonus.setVisible(bool(item and item["variable"]))
        if item:
            self._show_item(item, None)
            self.quick_info.setText("✔ {} — {} — {} — harmonisation {}. Entrée ou « Ajouter » : ajout immédiat.".format(
                item["nom"], item["type"] + (" ({})".format(item["precision"]) if item["precision"] else ""),
                item["rarete"], "requise" + (" ({})".format(item["condition"]) if item["condition"] else "")
                if item["lien"] else "non requise"))
        elif self.quick.text().strip():
            n = len(quick_matches(self.db.magic_items, self.quick.text()))
            self.quick_info.setText("{} objet{} correspondant{}. Absent du catalogue ? « Ajouter » crée un objet sur "
                                    "mesure.".format(n, "s" * (n > 1), "s" * (n > 1)) if n else
                                    "Aucun objet officiel ne correspond : « Ajouter » ouvre le formulaire sur mesure.")
        else:
            self.quick_info.setText("")

    def _on_quick_add(self) -> None:
        item = self._quick_item()
        if item is None:
            hits = quick_matches(self.db.magic_items, self.quick.text())
            if len(hits) == 1:                           # un seul candidat : on le prend
                item = self.db.magic_items[hits[0]]
            else:
                self._on_custom(self.quick.text())
                return
        bonus = self.quick_bonus.currentIndex() + 1 if item["variable"] else 0
        added = add_catalog_item(self.win, self.engine, item, bonus)
        if not added:
            return
        self.win.statusBar().showMessage("✨ {} ajouté à l'inventaire ({}{}).".format(
            added, item["rarete"], ", harmonisation requise" if item["lien"] else ""), 6000)
        self.quick.clear()
        self.quick_info.setText("")
        self.changed()

    def _on_custom(self, name: str = "") -> None:
        weapons = sorted((n for n in self.db.weapons if n != "Mains nues"), key=norm)
        spells = sorted((n for n, sp in self.db.spells.items()
                         if (self.engine.sheet_edition == 2024) == ("(2024)" in n or sp.get("edition") == 2024)),
                        key=norm)
        armors = [n for n in self.db.armors if n != "Aucune armure"] + sorted(getattr(self.db, "shields", {}) or {})
        data = ask_custom_item(self.win, name.strip(), weapon_names=weapons, spell_names=spells, armor_names=armors)
        if not data:
            return
        real = self.engine.add_custom_magic_item(**data)
        if real:
            self.win.statusBar().showMessage("Objet sur mesure « {} » ajouté.".format(real), 6000)
            self.quick.clear()
            self.changed()

    # ------------------------------------------------------------------ équipement porté
    def _on_remove(self):
        self.engine.remove_magic_item(self.table.currentRow())
        self.changed()

    def _toggle_equipped(self, idx: int, checked: bool):
        msg = ""
        if 0 <= idx < len(self.ch.objets_magiques) and self.ch.objets_magiques[idx].get("base") and checked:
            msg = self.engine.equip_magic_gear(idx)      # v45 : arme / armure -> case du mannequin
        else:
            self.engine.set_equipped(idx, checked)
        if msg:
            self.win.statusBar().showMessage(msg, 6000)
        self.changed()

    def _on_table_click(self, row: int, col: int):
        """Toute la cellule « Équipé » est cliquable."""
        if col == 0 and 0 <= row < len(self.ch.objets_magiques):
            self._toggle_equipped(row, not self.ch.objets_magiques[row].get("equipe", True))

    def _toggle_attune(self, idx: int, checked: bool):
        self.engine.set_attuned(idx, checked)     # refusé si limite atteinte : le rafraîchissement rétablit l'état
        QTimer.singleShot(0, self.changed)

    def _show_worn(self, row: int):
        from core import mechanics as M
        self.use_btn.setEnabled(0 <= row < len(self.ch.objets_magiques)
                                and M.is_consumable(self.ch.objets_magiques[row]["nom"]))
        if 0 <= row < len(self.ch.objets_magiques):
            entry = self.ch.objets_magiques[row]
            item = self.engine.magic_item(entry["nom"])
            if item:
                self._show_item(item, entry)

    def _show_item(self, item: dict, entry: dict | None):
        state, _ = self.engine.attune_status(item["nom"])
        if item["lien"]:
            attune = "requise" + (" — {} {}".format(html.escape(item["condition"]), STATE_ICON[state])
                                  if item["condition"] else "")
        else:
            attune = "non requise"
        bonus = []
        if entry and entry.get("bonus"):
            bonus.append("bonus choisi : +{}".format(entry["bonus"]))
        if item["ca"]:
            bonus.append("+{} à la CA".format(item["ca"]) + (" et aux jets de sauvegarde" if item["js"] else ""))
        self.detail.setHtml(
            "<h3 style='color:{}'>{}</h3><p><i>{}{} — {} — {}</i></p><p><b>Harmonisation :</b> {}</p>{}<p>{}</p>".format(
                theme.current().accent_text, html.escape(self.engine.magic_display_name(entry) if entry else item["nom"]),
                html.escape(item["type"]), " ({})".format(html.escape(item["precision"])) if item["precision"] else "",
                html.escape(item["rarete"]), html.escape(SOURCE_FR.get(item["source"], item["source"]) or "source inconnue")
                + (" — {:g} kg".format(item["poids"]).replace(".", ",") if item.get("poids") else ""), attune,
                "<p><b>Bonus :</b> {}</p>".format(html.escape(" ; ".join(bonus))) if bonus else "",
                html.escape(item["description"]).replace("\n", "<br/>")))

    # ------------------------------------------------------------------ rafraîchissement
    def refresh(self):
        eng, db, ch, t = self.engine, self.db, self.ch, theme.current()
        types = [ALL_TYPES] + sorted({i["type"] for i in db.magic_items.values() if i["type"]})
        rarities = [ALL_RARITIES] + [r for r in RARITY_ORDER
                                     if any(rarity_group(i["rarete"]) == r for i in db.magic_items.values())]
        fill_combo(self.type_combo, types,
                   self.type_combo.currentText() if self.type_combo.currentText() in types else ALL_TYPES)
        fill_combo(self.rarity_combo, rarities,
                   self.rarity_combo.currentText() if self.rarity_combo.currentText() in rarities else ALL_RARITIES)
        self._fill_library()

        # jauge d'harmonisation : sphères pleines = emplacements libres, vides = occupés par un objet harmonisé
        limit, used = eng.attunement_limit(), eng.attuned_count()
        self.attune_orbs.set_state(limit, used)
        self.attune_left.setText("{} / {}".format(used, limit))
        self.attune_orbs.setToolTip(rich_tip("Harmonisation", "{} objet(s) harmonisé(s) sur {} possibles. Les aptitudes "
                                             "de l'Artificier (niv. 10, 14, 18) augmentent ce maximum.".format(used, limit)))

        full = used >= limit
        self.table.setRowCount(len(ch.objets_magiques))
        for r, entry in enumerate(ch.objets_magiques):
            item = eng.magic_item(entry["nom"])
            label = eng.magic_display_name(entry)
            tip = rich_tip("✨ " + label, (item or {}).get("description", "Objet absent du catalogue actuel.")[:600])
            self.table.setItem(r, 0, check_item(entry.get("equipe", True), True, "Objet porté / équipé — cliquez"))
            self.table.setItem(r, 1, cell("✨ " + label, "left", tip, t.accent_text, bold=bool(entry.get("equipe"))))
            tier = eng.magic_gear_tier(item, entry) if item and entry.get("base") else 0
            kind = eng.magic_gear_kind(item) if item and entry.get("base") else ""
            bonus = ("+{} {}".format(tier, "toucher / dégâts" if kind == "arme" else "CA") if tier else
                     "+{}".format(entry["bonus"]) if entry.get("bonus") else
                     "+{} CA".format(item["ca"]) if item and item["ca"] else "—")
            self.table.setItem(r, 2, cell(bonus, "center", tip, t.accent_text if bonus != "—" else None,
                                          bold=bonus != "—"))
            if item and item["lien"]:
                # badge interactif : « ◇ Harmoniser » / « ✦ Harmonisé » (bouton à bascule stylé par le thème)
                badge = QPushButton("✦ Harmonisé" if entry.get("harmonise") else "◇ Non harmonisé")
                badge.setProperty("role", "attune")
                badge.setCheckable(True)
                badge.setChecked(bool(entry.get("harmonise")))
                badge.setEnabled(bool(entry.get("harmonise")) or not full)
                badge.setToolTip("Clic : {} cet objet ({} / {} objets harmonisés).".format(
                    "déharmoniser" if entry.get("harmonise") else "harmoniser", used, limit) if badge.isEnabled() else
                    "Maximum d'objets harmonisés atteint ({} / {}) : déharmonisez d'abord un autre objet.".format(
                        used, limit))
                badge.clicked.connect(lambda checked, i=r: self._toggle_attune(i, checked))
                self.table.setCellWidget(r, 3, badge)
            else:
                self.table.removeCellWidget(r, 3)
                self.table.setItem(r, 3, cell("—", "center", "Aucune harmonisation requise"))
            state, _ = eng.attune_status(entry["nom"])
            color = t.warn if state == "ko" else (t.muted if state == "?" else t.good)
            cond = item["condition"] if item else ""
            self.table.setItem(r, 4, cell("{} {}".format(STATE_ICON[state], cond) if cond else "—", "left", tip,
                                          color if cond else None))
        b = eng.magic_item_bonuses()
        if b["ca"] or b["js"]:
            self.effects.setText("Bonus actifs des objets (équipés et harmonisés) : CA {:+d} — jets de sauvegarde {:+d}"
                                 .format(b["ca"], b["js"]))
        else:
            self.effects.setText("Aucun bonus de CA ni de jet de sauvegarde actif : un objet doit être équipé "
                                 "(et harmonisé s'il l'exige).")
        self.remove_btn.setEnabled(bool(ch.objets_magiques))
