"""
OrbBar — compteur de ressources à sphères interactives, identique partout dans l'application
(rage, ki, emplacements de sorts, emplacements de Pacte, points de sorcellerie, harmonisation).

    - une sphère PLEINE = ressource disponible ; une sphère VIDE = ressource dépensée ;
    - un clic sur une sphère pleine en dépense une, un clic sur une sphère vide en récupère une
      (règle `rules.orb_click`) ; touches + / - et flèches fonctionnent aussi (la molette fait défiler la page) ;
    - les couleurs viennent du thème actif (`theme.current()`) : le composant suit les 10 thèmes ;
    - au-delà de `per_row` sphères, le compteur passe à la ligne.
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap, QRadialGradient
from PyQt6.QtWidgets import QSizePolicy, QWidget

from core import rules as R
from . import theme

# type de ressource -> champ de couleur du thème utilisé pour les sphères pleines
KIND_COLOR = {"souffle": "warn", "rage": "warn", "ki": "good", "sorcellerie": "accent_text", "emplacement": "accent_text",
              "pacte": "ornament", "harmonisation": "ornament", "forme": "good", "superiorite": "accent_text",
              "sursaut": "warn", "conduit": "accent_text", "inspiration": "good", "sens": "ornament", "psionique": "accent_text"}

# Performance : chaque aspect de sphère (pleine / vide / survolée) est dessiné UNE fois par thème et par taille,
# puis réutilisé sous forme d'image. Un clic ne redessine que deux petites images au lieu de recalculer des dégradés.
_SPRITES: dict[tuple, QPixmap] = {}


def orb_color(kind: str) -> str:
    """Couleur (hex) d'un type de ressource dans le thème courant."""
    return getattr(theme.current(), KIND_COLOR.get(kind, "accent_text"))


def orb_sprite(kind: str, size: int, filled: bool, hovered: bool) -> QPixmap:
    """Image (mise en cache) d'une sphère : dégradé radial brillant si pleine, creux sombre si vide."""
    t = theme.current()
    key = (t.key, kind, size, filled, hovered)
    pm = _SPRITES.get(key)
    if pm is not None:
        return pm
    pad = 3
    full = size + 2 * pad
    pm = QPixmap(full, full)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c, r = QPointF(full / 2, full / 2), size / 2
    base = QColor(orb_color(kind))
    if filled:
        grad = QRadialGradient(QPointF(c.x() - r * 0.35, c.y() - r * 0.4), r * 1.35)
        grad.setColorAt(0.0, base.lighter(165))
        grad.setColorAt(0.55, base)
        grad.setColorAt(1.0, base.darker(165))
        p.setBrush(grad)
        p.setPen(QPen(QColor(t.ornament), 1.6))
    else:
        grad = QRadialGradient(QPointF(c.x(), c.y() + r * 0.2), r * 1.2)
        grad.setColorAt(0.0, QColor(t.panel_alt))
        grad.setColorAt(1.0, QColor(t.input_bg))
        p.setBrush(grad)
        p.setPen(QPen(QColor(t.border), 1.6))
    p.drawEllipse(c, r - 1.5, r - 1.5)
    if filled:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 90))
        p.drawEllipse(QRectF(c.x() - r * 0.55, c.y() - r * 0.7, r * 0.6, r * 0.38))
    if hovered:
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(t.accent_text), 2.2))
        p.drawEllipse(c, r + 1.2, r + 1.2)
    p.end()
    if len(_SPRITES) > 400:
        _SPRITES.clear()
    _SPRITES[key] = pm
    return pm


class OrbBar(QWidget):
    """Rangée de sphères à remplir / vider. Signal `changed(used)` : nombre de ressources dépensées."""

    changed = pyqtSignal(int)

    def __init__(self, kind: str = "emplacement", orb: int = 26, gap: int = 8, per_row: int = 10,
                 interactive: bool = True):
        super().__init__()
        self.kind, self.orb, self.gap, self.per_row, self.interactive = kind, orb, gap, per_row, interactive
        self.total, self.used = 0, 0
        self._hover = -1
        self._sized = False
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus if interactive else Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        if interactive:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("Clic sur une sphère pleine : dépenser — clic sur une sphère vide : récupérer")

    # ------------------------------------------------------------------ état
    def set_state(self, total: int, used: int) -> None:
        """Met à jour le compteur (sans émettre de signal), recalcule la taille et redessine."""
        total, used = max(0, int(total)), max(0, int(used))
        used = min(used, total)
        if (total, used) == (self.total, self.used) and self._sized:
            return                                   # rien n'a changé : ni relayout ni redessin
        self._sized = True
        self.total, self.used = total, used
        step = self.orb + self.gap
        rows = max(1, math.ceil(total / self.per_row)) if total else 1
        cols = max(1, min(total, self.per_row))
        self.setFixedHeight(rows * step)
        self.setMinimumWidth(cols * step)
        self.update()

    @property
    def remaining(self) -> int:
        return self.total - self.used

    def sizeHint(self) -> QSize:  # noqa: N802 (nom imposé par Qt)
        step = self.orb + self.gap
        return QSize(max(1, min(self.total, self.per_row)) * step, max(1, math.ceil(self.total / self.per_row)) * step)

    # ------------------------------------------------------------------ géométrie
    def _center(self, i: int) -> QPointF:
        step = self.orb + self.gap
        return QPointF((i % self.per_row) * step + step / 2, (i // self.per_row) * step + step / 2)

    def _index_at(self, x: float, y: float) -> int:
        step = self.orb + self.gap
        if x < 0 or y < 0:
            return -1
        col, row = int(x // step), int(y // step)
        i = row * self.per_row + col
        if col >= self.per_row or i >= self.total:
            return -1
        c = self._center(i)
        return i if (x - c.x()) ** 2 + (y - c.y()) ** 2 <= (self.orb / 2 + 3) ** 2 else -1

    # ------------------------------------------------------------------ dessin
    def paintEvent(self, event):  # noqa: N802
        """Dessine les sphères à partir des images en cache (aucun calcul de dégradé à chaque clic)."""
        painter = QPainter(self)
        r = self.orb / 2
        for i in range(self.total):
            c = self._center(i)
            pm = orb_sprite(self.kind, self.orb, i < self.remaining, self.interactive and i == self._hover)
            painter.drawPixmap(int(c.x() - pm.width() / 2), int(c.y() - pm.height() / 2), pm)
        if self.interactive and self.hasFocus():
            t = theme.current()
            painter.setPen(QPen(QColor(t.accent_text), 1, Qt.PenStyle.DotLine))
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.end()

    # ------------------------------------------------------------------ interaction
    def _set_used(self, used: int) -> None:
        """Mise à jour immédiate de l'affichage, puis signal : le parent n'a rien à reconstruire."""
        used = max(0, min(self.total, used))
        if used != self.used:
            self.used = used
            self.repaint()                           # retour visuel instantané, avant tout traitement du signal
            self.changed.emit(used)

    def mousePressEvent(self, event):  # noqa: N802
        if not self.interactive or event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position()
        i = self._index_at(pos.x(), pos.y())
        if i >= 0:
            self._set_used(R.orb_click(self.total, self.used, i))

    def mouseMoveEvent(self, event):  # noqa: N802
        pos = event.position()
        i = self._index_at(pos.x(), pos.y()) if self.interactive else -1
        if i != self._hover:
            self._hover = i
            self.update()

    def leaveEvent(self, event):  # noqa: N802
        self._hover = -1
        self.update()

    def keyPressEvent(self, event):  # noqa: N802
        if not self.interactive:
            return
        if event.key() in (Qt.Key.Key_Minus, Qt.Key.Key_Down, Qt.Key.Key_Left):
            self._set_used(self.used + 1)            # dépenser
        elif event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Up, Qt.Key.Key_Right, Qt.Key.Key_Equal):
            self._set_used(self.used - 1)            # récupérer
        else:
            super().keyPressEvent(event)


class GaugeBar(QWidget):
    """
    Jauge horizontale pour une grande réserve de points (Imposition des mains : 5 × niveau, jusqu'à 100 PV),
    même interface que OrbBar : set_state(total, used), signal `changed(used)`.
    Clic sur la jauge : fixe le niveau restant à cet endroit ; flèches : ±1 point (la molette fait défiler la page).
    """

    changed = pyqtSignal(int)

    def __init__(self, kind: str = "jauge", height: int = 22, interactive: bool = True, text_color: str = ""):
        super().__init__()
        self.kind, self.interactive = kind, interactive
        self.text_color = text_color                     # "" = couleur du thème ; sinon texte forcé (ex. noir)
        self.total, self.used = 0, 0
        self.setFixedHeight(height)
        self.setMinimumWidth(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus if interactive else Qt.FocusPolicy.NoFocus)
        if interactive:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("Clic : fixer la réserve restante à cet endroit — flèches : ±1 point")

    def set_state(self, total: int, used: int) -> None:
        total, used = max(0, int(total)), max(0, int(used))
        self.total, self.used = total, min(used, total)
        self.update()

    @property
    def remaining(self) -> int:
        return self.total - self.used

    def _set_used(self, used: int) -> None:
        used = max(0, min(self.total, used))
        if used != self.used:
            self.used = used
            self.repaint()
            self.changed.emit(used)

    def paintEvent(self, event):  # noqa: N802
        t = theme.current()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        radius = rect.height() / 2
        # creux de la jauge
        p.setPen(QPen(QColor(t.border), 1.4))
        p.setBrush(QColor(t.input_bg))
        p.drawRoundedRect(rect, radius, radius)
        # remplissage : dégradé de la couleur « soins » du thème
        if self.total:
            frac = self.remaining / self.total
            if frac > 0:
                fill = QRectF(rect.x(), rect.y(), max(rect.height(), rect.width() * frac), rect.height())
                from PyQt6.QtGui import QLinearGradient
                base = QColor(t.good)
                grad = QLinearGradient(fill.topLeft(), fill.bottomLeft())
                grad.setColorAt(0.0, base.lighter(150))
                grad.setColorAt(0.5, base)
                grad.setColorAt(1.0, base.darker(150))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(grad)
                p.drawRoundedRect(fill, radius, radius)
                gloss = QColor(255, 255, 255, 60)
                p.setBrush(gloss)
                p.drawRoundedRect(QRectF(fill.x() + 3, fill.y() + 2, max(0.0, fill.width() - 6), fill.height() / 3),
                                  radius / 2, radius / 2)
            # graduations tous les 5 points (une « dose » de guérison de maladie / poison)
            p.setPen(QPen(QColor(t.border), 1))
            step = 5
            for k in range(step, self.total, step):
                x = rect.x() + rect.width() * k / self.total
                p.drawLine(QPointF(x, rect.bottom() - 4), QPointF(x, rect.bottom() - 1))
        label = "{} / {} PV".format(self.remaining, self.total)
        if self.text_color:
            # texte forcé (noir) en gras, cerné d'un halo clair : lisible sur la partie verte comme sur le creux
            from PyQt6.QtGui import QFont, QFontMetricsF, QPainterPath
            font = QFont(self.font())
            font.setBold(True)
            fm = QFontMetricsF(font)
            path = QPainterPath()
            x = rect.center().x() - fm.horizontalAdvance(label) / 2
            y = rect.center().y() + (fm.ascent() - fm.descent()) / 2
            path.addText(QPointF(x, y), font, label)
            p.setPen(QPen(QColor(255, 255, 255, 210), 3.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(self.text_color))
            p.drawPath(path)
        else:
            p.setPen(QColor(t.text))
            p.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), label)
        if self.interactive and self.hasFocus():
            p.setPen(QPen(QColor(t.accent_text), 1, Qt.PenStyle.DotLine))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect, radius, radius)
        p.end()

    def mousePressEvent(self, event):  # noqa: N802
        if not self.interactive or event.button() != Qt.MouseButton.LeftButton or not self.total:
            return
        frac = max(0.0, min(1.0, event.position().x() / max(1, self.width())))
        self._set_used(self.total - round(frac * self.total))

    def keyPressEvent(self, event):  # noqa: N802
        if not self.interactive:
            return
        if event.key() in (Qt.Key.Key_Minus, Qt.Key.Key_Down, Qt.Key.Key_Left):
            self._set_used(self.used + 1)
        elif event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Up, Qt.Key.Key_Right, Qt.Key.Key_Equal):
            self._set_used(self.used - 1)
        else:
            super().keyPressEvent(event)
