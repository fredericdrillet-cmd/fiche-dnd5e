"""
Grille de cartes à choisir (v53) — espèce, classe, historique dans l'assistant de création, façon jeu de rôle :
image ou icône carrée, nom dessous, description au survol ; un clic choisit.
"""
from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from core.rules import norm
from . import icons as IC
from . import theme
from .common import blocked

CLASS_ICONS = {"artificier": "objet_outil", "barbare": "rage", "barde": "inspiration_bardique",
               "clerc": "conduit_divin", "druide": "forme_sauvage", "ensorceleur": "points_sorcellerie",
               "guerrier": "attaque", "magicien": "objet_livre", "moine": "ki", "occultiste": "pacte",
               "paladin": "chatiment", "rodeur": "arme_arc", "roublard": "attaque_sournoise"}

BACKGROUND_ICONS = [("acolyte", "conduit_divin"), ("artisan", "objet_outil"), ("guilde", "objet_outil"),
                    ("criminel", "attaque_sournoise"), ("espion", "se_cacher"), ("soldat", "arme_epee"),
                    ("garde", "arme_bouclier"), ("sage", "objet_livre"), ("scribe", "objet_parchemin"),
                    ("erudit", "objet_livre"), ("noble", "grandeur"), ("courtisan", "grandeur"),
                    ("marin", "effet_eau"), ("pirate", "effet_eau"), ("ermite", "repos"), ("charlatan", "ecole_illusion"),
                    ("artiste", "inspiration_bardique"), ("saltimbanque", "inspiration_bardique"),
                    ("heros", "aider"), ("enfant des rues", "objet_sac"), ("orphelin", "objet_sac"),
                    ("sauvageon", "forme_sauvage"), ("etranger", "forme_sauvage"), ("marchand", "objet_gemme"),
                    ("voyageur", "foncer"), ("fermier", "objet_ration"), ("agriculteur", "objet_ration"),
                    ("chasseur", "arme_arc"), ("guide", "chercher"), ("archeolog", "chercher"),
                    ("chevalier", "arme_epee"), ("pelerin", "foncer"), ("entertainer", "inspiration_bardique")]


def _rounded(src: QPixmap, size: int) -> QPixmap:
    """Image « couverture » carrée aux coins arrondis, cadre de la couleur du thème."""
    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)
    scaled = src.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation)
    x, y = (scaled.width() - size) // 2, (scaled.height() - size) // 2
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(1, 1, size - 2, size - 2, size * 0.14, size * 0.14)
    p.setClipPath(path)
    p.drawPixmap(0, 0, scaled.copy(x, y, size, size))
    p.setClipping(False)
    p.setPen(QPen(QColor(theme.current().ornament), 2))
    p.drawPath(path)
    p.end()
    return out


def race_pixmap(race: str, size: int = 72) -> QPixmap:
    from .race_portrait import find_race_image
    path = find_race_image(race, "")
    if path and IC.HAS_SVG:
        src = QPixmap(str(path))
        try:
            if not src.isNull():
                return _rounded(src, size)
        except TypeError:
            pass
    return IC.icon_pixmap("capacite_espece", "capacite", size)


def class_pixmap(name: str, size: int = 72) -> QPixmap:
    key = norm(name.split(" (")[0])
    return IC.icon_pixmap(CLASS_ICONS.get(key, "capacite_classe"), "capacite", size)


def background_pixmap(name: str, size: int = 72) -> QPixmap:
    n = norm(name)
    icon = next((ic for k, ic in BACKGROUND_ICONS if k in n), "objet_parchemin")
    return IC.icon_pixmap(icon, "commune", size)


class CardPicker(QListWidget):
    """Grille de cartes à sélection unique : set_items([(nom, pixmap, infobulle)]), select(nom) ; on_pick(nom)."""

    def __init__(self, on_pick: Callable[[str], None], icon: int = 72, cell=(122, 116), height: int = 270):
        super().__init__()
        self._on_pick = on_pick
        self._key = None
        IC.card_grid(self, icon, cell)
        try:
            self.setMinimumHeight(height)
            self.setMaximumHeight(height + 60)
            self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        except (AttributeError, TypeError):
            pass
        self.itemClicked.connect(self._clicked)

    def set_items(self, rows: list[tuple[str, Optional[QPixmap], str]]) -> None:
        key = tuple(r[0] for r in rows) + (theme.current().key,)
        if key == self._key:
            return
        self._key = key
        with blocked(self):
            self.clear()
            for name, pix, tip in rows:
                it = QListWidgetItem(name.replace(" (2024)", ""))
                it.setData(Qt.ItemDataRole.UserRole, name)
                if pix is not None and IC.HAS_SVG:
                    it.setIcon(QIcon(pix))
                if tip:
                    it.setToolTip(tip)
                self.addItem(it)

    def select(self, name: str) -> None:
        with blocked(self):
            for i in range(self.count()):
                it = self.item(i)
                if it.data(Qt.ItemDataRole.UserRole) == name:
                    self.setCurrentItem(it)
                    try:
                        self.scrollToItem(it)
                    except (AttributeError, TypeError):
                        pass
                    return

    def _clicked(self, it) -> None:
        name = it.data(Qt.ItemDataRole.UserRole)
        if name:
            self._on_pick(name)
