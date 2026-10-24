"""
Widgets « jeu vidéo » de la fiche (style Baldur's Gate 3 / Solasta) :

    - InstantTip      : mixin d'infobulle immédiate (affichée dès l'entrée de la souris, sans délai Qt) ;
    - ActionChip      : pastille « icône + nom » (actions d'arme, réactions), cliquable, infobulle riche ;
    - EffectBadge     : icône d'effet dessinée (tuile arrondie colorée selon la catégorie + emoji + nom),
                        survol = ✕ de retrait + infobulle détaillée, clic = retirer l'effet ;
    - clear_layout    : vide un layout (widgets détruits).
"""
from __future__ import annotations

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QCursor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QLabel, QSizePolicy, QToolTip, QWidget

from . import theme

CATEGORY_COLORS = {"Bonus": "#3a9d5d", "Malus": "#c0392b", "État": "#b0832f", "Aura": "#2e86c1",
                   "Aptitude": "#8e44ad", "Concentration": "#d4ac0d"}


def clear_layout(layout) -> None:
    """Vide un layout, y compris ses sous-layouts (grilles, lignes insérées) : chaque widget est masqué
    IMMÉDIATEMENT puis détruit (v45 — sans cela, les widgets d'une grille imbriquée restaient affichés et se
    superposaient aux nouveaux : Faveur de pacte par-dessus le Style de combat dans l'assistant de niveau)."""
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            break
        w = item.widget()
        if w is not None:
            w.hide()
            w.setParent(None)
            w.deleteLater()
            continue
        sub = item.layout()
        if sub is not None:
            clear_layout(sub)
            sub.deleteLater()


class InstantTip:
    """À mixer avec un QWidget : `self.tip_html` s'affiche immédiatement au survol."""
    tip_html = ""

    def enterEvent(self, event):  # noqa: N802 (nom imposé par Qt)
        if self.tip_html:
            QToolTip.showText(QCursor.pos(), self.tip_html, self)
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802
        QToolTip.hideText()
        super().leaveEvent(event)


class ActionChip(InstantTip, QLabel):
    """Pastille compacte « ⚔ Nom ». `state` : '' | 'used' | 'ok' (teinte), `on_click` : rappel facultatif."""

    def __init__(self, icon: str, name: str, tip_html: str = "", on_click=None, state: str = ""):
        QLabel.__init__(self, f"{icon} {name}")
        self.tip_html = tip_html
        self.on_click = on_click
        self.setProperty("role", "chip")
        self.setProperty("state", state)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        if on_click:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):  # noqa: N802
        if self.on_click:
            self.on_click()
        else:
            super().mousePressEvent(event)


class EffectBadge(InstantTip, QWidget):
    """Icône d'effet actif (64 × 70 px) : tuile en dégradé + liseré de catégorie + emoji + nom abrégé."""

    SIZE = QSize(66, 72)

    def __init__(self, key: str, icon: str, name: str, category: str, tip_html: str, on_remove=None,
                 permanent: bool = False):
        QWidget.__init__(self)
        self.key, self.icon, self.name, self.category = key, icon, name, category
        self.permanent = permanent                       # trait inné (race / classe) : cadenas + liseré doré
        self.tip_html = tip_html + ("<p style='color:gray'><i>Trait permanent — clic : le retirer (confirmation "
                                    "demandée).</i></p>" if permanent else
                                    "<p style='color:gray'><i>Clic : retirer l'effet.</i></p>")
        self.on_remove = on_remove
        self._hover = False
        self.setFixedSize(self.SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def enterEvent(self, event):  # noqa: N802
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):  # noqa: N802
        if self.on_remove:
            QToolTip.hideText()
            self.on_remove(self.key)

    def paintEvent(self, event):  # noqa: N802
        t = theme.current()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        color = QColor(CATEGORY_COLORS.get(self.category, t.ornament))
        tile = QRectF(9, 3, 48, 48)
        path = QPainterPath()
        path.addRoundedRect(tile, 10, 10)
        grad = QLinearGradient(tile.topLeft(), tile.bottomLeft())
        grad.setColorAt(0.0, color.lighter(135))
        grad.setColorAt(1.0, color.darker(170))
        p.fillPath(path, grad)
        p.setPen(QPen(QColor(t.accent_text) if self._hover else color.lighter(160), 2.4 if self._hover else 1.6))
        p.drawPath(path)
        f = QFont(self.font())
        f.setPixelSize(24)
        p.setFont(f)
        p.setPen(QColor("#ffffff"))
        p.drawText(tile, int(Qt.AlignmentFlag.AlignCenter), self.icon)
        f.setPixelSize(10)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(t.text))
        label = self.name if len(self.name) <= 11 else self.name[:10] + "…"
        p.drawText(QRectF(0, 53, self.width(), 17), int(Qt.AlignmentFlag.AlignCenter), label)
        if self.permanent:                               # cadenas : trait racial / aptitude de classe permanente
            p.setBrush(QColor(t.panel))
            p.setPen(QPen(QColor(t.accent_text), 1.2))
            p.drawEllipse(QRectF(4, 0, 16, 16))
            f.setPixelSize(10)
            p.setFont(f)
            p.drawText(QRectF(4, 0, 16, 16), int(Qt.AlignmentFlag.AlignCenter), "🔒")
        if self._hover:                                  # pastille ✕ de retrait
            p.setBrush(QColor(t.warn))
            p.setPen(QPen(QColor("#ffffff"), 1.2))
            p.drawEllipse(QRectF(46, 0, 16, 16))
            f.setPixelSize(11)
            p.setFont(f)
            p.drawText(QRectF(46, 0, 16, 16), int(Qt.AlignmentFlag.AlignCenter), "✕")
        p.end()


def use_consumable(win, source: str, index: int) -> str:
    """Boire / utiliser un consommable de l'inventaire (demande le type de dégâts d'une potion de résistance)."""
    from core import mechanics as M
    from .dialogs import ask_choice
    items = win.ch.equipement if source == "equipement" else win.ch.objets_magiques
    if not 0 <= index < len(items) or not M.is_consumable(items[index]["nom"]):
        return ""
    name = items[index]["nom"]
    choice = ""
    kind, _ = M.potion_action(name)
    if kind == "resistance" and not M.damage_types_in(name):
        labels = {M.DAMAGE_TYPES[k][0]: k for k in M.DAMAGE_TYPES}
        picked = ask_choice(win, "Potion de résistance", "Choisissez le type de dégâts auquel la potion vous rend "
                            "résistant pendant 1 heure :", list(labels))
        if not picked:
            return ""
        choice = labels[picked]
    msg = win.engine.use_consumable(source, index, choice=choice)
    win.statusBar().showMessage("🧪 " + msg, 8000)
    win.changed()
    return msg
