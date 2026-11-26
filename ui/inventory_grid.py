"""
Sac en tuiles (v53), façon jeu de rôle : une tuile carrée par objet (icône du type d'objet, bordure de la couleur
de rareté, quantité en coin, « É » si équipé), fiche de l'objet au survol, glisser-déposer vers une case du
mannequin (et d'une case vers le sac pour la vider). Double-clic : utiliser (consommable) ou équiper / déséquiper ;
clic droit : menu. La table de l'inventaire reste le modèle (sélection synchronisée), rien ne change côté règles.
"""
from __future__ import annotations

from PyQt6.QtCore import QMimeData, QSize, Qt
from PyQt6.QtGui import QColor, QDrag, QFont, QIcon, QPainter, QPen
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMenu

import re

from core.rules import norm
from core.tile_icons import ITEMS, WEAPONS, _find
from . import icons as IC
from . import theme
from .common import blocked

MIME_ITEM = "application/x-dnd5e-objet"
MIME_SLOT = "application/x-dnd5e-case"
RARITY = {"commun": "#A8A8A8", "peu commun": "#4CB050", "rare": "#3B82E0", "tres rare": "#A057D6",  # bordures
          "legendaire": "#F0A030", "artefact": "#E2533F"}
TILE = 60
KEY_ROLE = 0x0100 + 77                                   # Qt.UserRole + 77 : nom de l'objet (clé)


# v53 : filtres du sac (l'inventaire contient tout : objets courants et magiques)
FAMILIES = [("tout", "Tout"), ("armes", "⚔ Armes"), ("armures", "🛡 Armures"), ("consommables", "🧪 Potions"),
            ("magiques", "✨ Magiques"), ("outils", "🔧 Outils"), ("divers", "🎒 Divers")]
FAMILY_TIPS = {"tout": "Tout le contenu du sac.", "armes": "Armes courantes et magiques, munitions comprises.",
               "armures": "Armures et boucliers, courants et magiques.",
               "consommables": "Consommables : potions, élixirs, philtres, huiles, antitoxines, parchemins.",
               "magiques": "Autres objets magiques : anneaux, baguettes, bâtons, capes, bottes, amulettes…",
               "outils": "Outils et instruments.", "divers": "Équipement courant, paquetages et le reste."}


def item_family(name: str, category: str = "", magic: bool = False) -> str:
    """Famille d'un objet du sac : armes (munitions comprises), armures (boucliers compris), consommables
    (potions, élixirs, huiles, parchemins…), objets magiques (anneaux, baguettes, capes…), outils, divers.
    `category` : catégorie du catalogue (objet courant) ou type de l'objet magique."""
    from core import mechanics as M
    n, cat = norm(name), norm(category)
    if M.is_consumable(name) or cat in ("potion", "parchemin") or n.startswith(("parchemin", "philtre")):
        return "consommables"
    if cat == "arme" or re.search(r"\b(munitions?|fleches?|carreaux?|billes?|flechettes?)\b", n):
        return "armes"
    if cat in ("armure", "bouclier"):
        return "armures"
    if magic:
        return "magiques"
    if cat == "outil":
        return "outils"
    return "divers"


def item_icon_name(name: str, category: str = "") -> str:
    n = norm(name)
    cat = norm(category)
    if "armure" in cat or any(k in n for k in ("armure", "cotte", "harnois", "cuir", "brigandine", "demi-plate")):
        return "objet_armure"
    if "bouclier" in cat or "bouclier" in n:
        return "objet_bouclier"
    return _find(name, ITEMS) or _find(name, WEAPONS) or ("objet_outil" if "outil" in cat else "objet")


def item_body(name: str, category: str = "") -> str:
    """v53 : corps SVG de l'icône du sac — une arme reprend le dessin de sa tuile d'attaque (core/action_icons)."""
    icon = item_icon_name(name, category)
    if icon.startswith("arme_") or icon == "objet":
        from core.action_icons import weapon_body
        body = weapon_body(name)
        if body:
            return body
    return IC.named_body(icon)


def tile_pixmap(name: str, category: str, rarity: str, qty: int, equipped: bool, magic: bool, dim: bool = False):
    cat = theme.rarity_category(rarity) if magic else "commune"      # v53 : fond de la couleur de la rareté
    pix = IC._render(item_body(name, category), cat, TILE, theme.current().key, dim)
    if not IC.HAS_SVG:
        return pix
    pix = pix.copy()
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    color = RARITY.get(theme.rarity_key(rarity))
    if color:                                            # sertissure de la couleur de la rareté (pierre runique)
        path = IC._octagon(TILE, 2)
        p.setPen(QPen(QColor(color), 3.2))
        p.drawPath(path)
    f = QFont()
    f.setBold(True)
    f.setPointSizeF(7.5)
    p.setFont(f)
    if qty > 1:
        text = "×{}".format(qty)
        w = p.fontMetrics().horizontalAdvance(text) + 6
        p.setBrush(QColor(0, 0, 0, 170))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(TILE - w - 3, TILE - 16, w, 13, 4, 4)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(TILE - w, TILE - 6, text)
    if equipped:
        p.setBrush(QColor(theme.current().good))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(3, 3, 14, 14)
        p.setPen(QColor("#000000"))
        p.drawText(6, 14, "É")
    p.end()
    return pix


class InventoryGrid(QListWidget):
    """Grille de tuiles ; `rows` : [{nom, categorie, rarete, qte, equipe, magique, tip, ligne}]."""

    def __init__(self, tab):
        super().__init__()
        self.tab = tab
        self._key = None
        IC.card_grid(self, TILE, (124, 128))           # nom sur trois lignes
        try:
            self.setMinimumHeight(260)
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
            self.setDropIndicatorShown(False)
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self._menu)
        except (AttributeError, TypeError):
            pass
        self.currentRowChanged.connect(self._select)
        self.itemDoubleClicked.connect(self._activate)

    # ------------------------------------------------------------------ contenu
    def set_rows(self, rows: list[dict]) -> None:
        key = tuple((r["nom"], r["qte"], r["equipe"], r["rarete"], r.get("epuise", False)) for r in rows) + \
            (theme.current().key,)
        if key == self._key:
            return
        self._key = key
        cur = self.currentRow()
        with blocked(self):
            self.clear()
            for r in rows:
                it = QListWidgetItem(r["nom"])
                it.setData(Qt.ItemDataRole.UserRole, r["ligne"])
                it.setData(KEY_ROLE, r.get("cle", r["nom"]))
                if IC.HAS_SVG:
                    it.setIcon(QIcon(tile_pixmap(r["nom"], r["categorie"], r["rarete"], r["qte"], r["equipe"],
                                                 r["magique"], r.get("epuise", False))))
                it.setToolTip(r["tip"])
                if r.get("magique") and r.get("rarete"):        # v53 : nom de la couleur de la rareté
                    try:
                        it.setForeground(QColor(theme.rarity_color(r["rarete"], bg=theme.table_bgs())))
                    except (AttributeError, TypeError):      # faux Qt des tests
                        pass
                self.addItem(it)
            if 0 <= cur < self.count():
                self.setCurrentRow(cur)

    def _select(self, row: int) -> None:
        it = self.item(row) if row >= 0 else None
        if it is not None:
            self.tab.table.selectRow(it.data(Qt.ItemDataRole.UserRole))
            self.tab._update_use_btn()

    def _activate(self, it) -> None:
        """Double-clic : consommable -> utiliser ; objet magique -> équiper / déséquiper ; arme, armure, bouclier
        -> case du mannequin correspondante."""
        self._select(self.row(it))
        tab = self.tab
        if tab.use_btn.isEnabled() and "boire" in norm(tab.use_btn.text() or "") or \
                tab.use_btn.isEnabled() and "utiliser" in norm(tab.use_btn.text() or ""):
            tab._on_use_item()
            return
        if tab.magic_row(tab.table.currentRow()) >= 0:
            tab._on_equip_magic()
            return
        self.equip_to_best_slot(it.data(KEY_ROLE))

    def equip_to_best_slot(self, key: str) -> bool:
        """Clé du sac (`Engine.bag_key`) -> case naturelle de l'objet."""
        ok, msg = self.tab.engine.equip_from_bag(key)
        self.tab.win.statusBar().showMessage(msg, 7000)
        if ok:
            self.tab.changed()
        return ok

    def _menu(self, pos) -> None:
        it = self.itemAt(pos)
        if it is None:
            return
        self.setCurrentItem(it)
        tab = self.tab
        menu = QMenu(self)
        if tab.use_btn.isEnabled():
            menu.addAction(tab.use_btn.text(), tab._on_use_item)
        if tab.magic_row(tab.table.currentRow()) >= 0:
            menu.addAction("✨ Équiper / déséquiper", tab._on_equip_magic)
        else:
            menu.addAction("🧍 Équiper", lambda n=it.data(KEY_ROLE): self.equip_to_best_slot(n))
        menu.addSeparator()
        menu.addAction("🗑 Retirer de l'inventaire", tab._on_del_item)
        menu.exec(self.mapToGlobal(pos))

    # ------------------------------------------------------------------ glisser-déposer
    def startDrag(self, actions) -> None:  # noqa: N802
        it = self.currentItem()
        if it is None:
            return
        mime = QMimeData()
        mime.setData(MIME_ITEM, str(it.data(KEY_ROLE)).encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(it.icon().pixmap(QSize(TILE, TILE)))
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, e) -> None:  # noqa: N802
        if e.mimeData().hasFormat(MIME_SLOT):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e) -> None:  # noqa: N802
        if e.mimeData().hasFormat(MIME_SLOT):
            e.acceptProposedAction()

    def dropEvent(self, e) -> None:  # noqa: N802
        """Case du mannequin déposée dans le sac : elle est vidée (l'objet reste dans l'inventaire)."""
        if not e.mimeData().hasFormat(MIME_SLOT):
            return
        slot = bytes(e.mimeData().data(MIME_SLOT)).decode("utf-8")
        if slot.startswith("rapide:"):                   # v53 : emplacement rapide vidé
            self.tab.engine.clear_quick_slot(int(slot.split(":")[1]))
        else:
            self.tab.engine.unequip_slot(slot)
        self.tab.win.statusBar().showMessage("Case vidée : l'objet retourne dans le sac.", 5000)
        e.acceptProposedAction()
        self.tab.changed()
