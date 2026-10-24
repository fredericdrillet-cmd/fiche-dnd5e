"""
Illustration de race (onglet Race) : carré FIXE de 8 cm × 8 cm, cadre ornementé aux couleurs du thème.

    - la taille de l'image est calculée en centimètres réels à partir de la résolution logique de l'écran
      (8 cm ≈ 302 px à 96 dpi), puis figée : toutes les races s'affichent exactement au même format ;
    - l'image est mise à l'échelle en mode « cover » (remplit le carré, recadrée au centre, jamais déformée) ;
    - les illustrations détourées (PNG transparent) sont posées sur un fond en dégradé du thème ;
    - image absente : médaillon de remplacement (initiale de la race + « Illustration à venir »).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient
from PyQt6.QtWidgets import QSizePolicy, QWidget

from core.race_images import find_race_image
from . import theme

SIZE_CM = 8.0          # côté de l'illustration
FRAME = 16             # épaisseur du cadre ornementé (px), en plus des 8 cm d'image


def cm_to_px(cm: float, dpi: float) -> int:
    return int(round(cm / 2.54 * dpi))


class RaceIllustration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            dpi = float(self.logicalDpiX())
            if not 50 <= dpi <= 400:
                raise ValueError
        except (TypeError, ValueError):
            dpi = 96.0                                       # résolution logique standard
        self.side = cm_to_px(SIZE_CM, dpi)                   # 8 cm -> ≈ 302 px à 96 dpi
        self.setFixedSize(self.side + 2 * FRAME, self.side + 2 * FRAME)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.race, self.subrace = "", ""
        self.path: Optional[Path] = None
        self._pixmap: Optional[QPixmap] = None
        self._cache: dict[tuple, QPixmap] = {}

    # ------------------------------------------------------------------ données
    def set_race(self, race: str, subrace: str = "") -> None:
        """Met à jour l'illustration (appelé à chaque changement de race / sous-race)."""
        path = find_race_image(race, subrace)
        if (race, subrace, path) == (self.race, self.subrace, self.path):
            return
        self.race, self.subrace, self.path = race, subrace, path
        self._pixmap = self._load(path) if path else None
        label = race + (" — " + subrace if subrace else "")
        self.setToolTip("<qt><b>{}</b>{}</qt>".format(
            label, "" if self._pixmap is not None else "<br/>Illustration à venir : déposez « {} ».png ou .jpg dans "
            "data/images/races.".format(race.split(" (")[0].lower())))
        self.update()

    def has_image(self) -> bool:
        return self._pixmap is not None

    def _load(self, path: Path) -> Optional[QPixmap]:
        """Image mise à l'échelle « cover » au côté exact (× ratio d'écran HiDPI), recadrée au centre."""
        try:
            ratio = float(self.devicePixelRatioF())
        except (TypeError, ValueError, AttributeError):
            ratio = 1.0
        target = int(round(self.side * max(1.0, ratio)))
        key = (str(path), target)
        if key in self._cache:
            return self._cache[key]
        src = QPixmap(str(path))
        try:
            if src.isNull():
                return None
        except TypeError:
            return None
        scaled = src.scaled(target, target, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                            Qt.TransformationMode.SmoothTransformation)
        x, y = (scaled.width() - target) // 2, (scaled.height() - target) // 2
        pm = scaled.copy(x, y, target, target)
        pm.setDevicePixelRatio(max(1.0, ratio))
        self._cache[key] = pm
        return pm

    # ------------------------------------------------------------------ dessin
    def paintEvent(self, event):  # noqa: N802
        t = theme.current()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        outer = QRectF(1, 1, self.width() - 2, self.height() - 2)
        inner = QRectF(FRAME, FRAME, self.side, self.side)
        orn, accent = QColor(t.ornament), QColor(t.accent_text)

        # 1. cadre : métal brossé du thème, double filet
        grad = QLinearGradient(outer.topLeft(), outer.bottomRight())
        grad.setColorAt(0.0, QColor(t.panel_alt).lighter(135))
        grad.setColorAt(0.5, QColor(t.panel_alt))
        grad.setColorAt(1.0, QColor(t.panel_alt).darker(160))
        p.setPen(QPen(orn.darker(150), 2))
        p.setBrush(grad)
        p.drawRoundedRect(outer, 10, 10)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(orn, 1.6))
        p.drawRoundedRect(outer.adjusted(5, 5, -5, -5), 7, 7)

        # 2. fond de l'image (visible derrière les illustrations détourées) : halo du thème
        bg = QRadialGradient(inner.center(), self.side * 0.75)
        bg.setColorAt(0.0, QColor(t.panel2).lighter(130))
        bg.setColorAt(0.65, QColor(t.panel))
        bg.setColorAt(1.0, QColor(t.bg).darker(140))
        p.fillRect(inner, bg)

        if self._pixmap is not None:
            p.drawPixmap(inner.toRect(), self._pixmap)
        else:
            self._paint_fallback(p, inner, t)

        # 3. vignettage léger + biseau intérieur
        vig = QRadialGradient(inner.center(), self.side * 0.72)
        vig.setColorAt(0.70, QColor(0, 0, 0, 0))
        vig.setColorAt(1.0, QColor(0, 0, 0, 110))
        p.fillRect(inner, vig)
        p.setPen(QPen(QColor(0, 0, 0, 170), 2))
        p.drawRect(inner.adjusted(-1, -1, 1, 1))
        p.setPen(QPen(accent, 1))
        p.drawRect(inner.adjusted(-3, -3, 3, 3))

        # 4. ornements : losanges aux coins, rivets au milieu des côtés
        for cx, cy in ((FRAME / 2 + 1, FRAME / 2 + 1), (self.width() - FRAME / 2 - 1, FRAME / 2 + 1),
                       (FRAME / 2 + 1, self.height() - FRAME / 2 - 1),
                       (self.width() - FRAME / 2 - 1, self.height() - FRAME / 2 - 1)):
            self._diamond(p, QPointF(cx, cy), 9, orn, accent)
        mid_x, mid_y = self.width() / 2, self.height() / 2
        for cx, cy in ((mid_x, FRAME / 2 + 1), (mid_x, self.height() - FRAME / 2 - 1),
                       (FRAME / 2 + 1, mid_y), (self.width() - FRAME / 2 - 1, mid_y)):
            self._diamond(p, QPointF(cx, cy), 5, orn, accent)
        p.end()

    @staticmethod
    def _diamond(p: QPainter, c: QPointF, r: float, fill: QColor, edge: QColor) -> None:
        path = QPainterPath()
        path.moveTo(c.x(), c.y() - r)
        path.lineTo(c.x() + r, c.y())
        path.lineTo(c.x(), c.y() + r)
        path.lineTo(c.x() - r, c.y())
        path.closeSubpath()
        g = QLinearGradient(QPointF(c.x() - r, c.y() - r), QPointF(c.x() + r, c.y() + r))
        g.setColorAt(0.0, fill.lighter(160))
        g.setColorAt(1.0, fill.darker(150))
        p.setPen(QPen(edge, 1))
        p.setBrush(g)
        p.drawPath(path)
        p.setBrush(Qt.BrushStyle.NoBrush)

    def _paint_fallback(self, p: QPainter, inner: QRectF, t) -> None:
        """Médaillon de remplacement : initiale de la race dans un cercle ornementé + mention."""
        c, r = inner.center(), self.side * 0.28
        p.setPen(QPen(QColor(t.ornament), 3))
        p.setBrush(QColor(0, 0, 0, 60))
        p.drawEllipse(c, r, r)
        p.setPen(QPen(QColor(t.accent_text), 1))
        p.drawEllipse(c, r - 8, r - 8)
        f = QFont()
        f.setBold(True)
        f.setPixelSize(int(r * 1.05))
        p.setFont(f)
        p.setPen(QColor(t.accent_text))
        p.drawText(QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r), int(Qt.AlignmentFlag.AlignCenter),
                   (self.race[:1] or "?").upper())
        f.setPixelSize(15)
        f.setBold(False)
        f.setItalic(True)
        p.setFont(f)
        p.setPen(QColor(t.muted))
        p.drawText(QRectF(inner.x(), inner.bottom() - 52, inner.width(), 30), int(Qt.AlignmentFlag.AlignCenter),
                   "Illustration à venir")
