"""
Lancer de d20 animé (inspiré de Baldur's Gate 3).

    - d20_icon() / d20_button() : petite icône de d20 (couleur du thème) placée à côté des caractéristiques,
      compétences, jets de sauvegarde, attaques d'arme et sorts d'attaque ;
    - DiceRollDialog : fenêtre centrée sur fond flouté semi-transparent ; grand d20 dessiné aux couleurs du thème ;
      le chiffre défile pendant 2 secondes (cadence décroissante, rotation qui ralentit), puis se fige ;
      20 naturel = vert vif, 1 naturel = rouge vif (résultat brut uniquement) ;
      les bonus / malus sont listés dès l'ouverture avec leur provenance, puis appliqués un par un au total
      seulement une fois le d20 figé ; bouton « Continuer » pour refermer.

Animation non bloquante : un QTimer (≈ 60 images/s) pilote les phases ; aucun thread ni boucle bloquante.
"""
from __future__ import annotations

import html
import math
import random
import time

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (QDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton,
                             QToolButton, QVBoxLayout, QWidget)

from core import dice as D
from . import theme
from .common import make_label
from .dialogs import BlurBackdrop

ROLL_MS = 2000            # durée du défilement du d20
STEP_MS = 380             # délai entre l'application de deux bonus
CRIT_GREEN, CRIT_RED = "#2EE66B", "#FF3B3B"


# ------------------------------------------------------------------------------------------------ dessin du d20
def _hexagon(rect: QRectF, angle: float = 0.0) -> list[QPointF]:
    cx, cy, r = rect.center().x(), rect.center().y(), min(rect.width(), rect.height()) / 2
    return [QPointF(cx + r * math.cos(math.radians(a + angle)), cy + r * math.sin(math.radians(a + angle)))
            for a in (-90, -30, 30, 90, 150, 210)]


def paint_d20(p: QPainter, rect: QRectF, color: str, number: str = "", num_color: str = "#FFFFFF",
              angle: float = 0.0, glow: str = "") -> None:
    """d20 vu de face (hexagone + facettes) en dégradé de la couleur du thème, chiffre au centre."""
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    base = QColor(color)
    pts = _hexagon(rect, angle)
    path = QPainterPath()
    path.moveTo(pts[0])
    for pt in pts[1:]:
        path.lineTo(pt)
    path.closeSubpath()
    if glow:                                              # halo critique
        for i, alpha in ((14, 40), (8, 70), (4, 110)):
            g = QColor(glow)
            g.setAlpha(alpha)
            p.setPen(QPen(g, i))
            p.drawPath(path)
    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, base.lighter(150))
    grad.setColorAt(0.55, base)
    grad.setColorAt(1.0, base.darker(190))
    p.fillPath(path, grad)
    # facettes : triangle central + arêtes vers les sommets
    cx, cy = rect.center().x(), rect.center().y()
    r = min(rect.width(), rect.height()) / 2
    inner = [QPointF(cx + 0.55 * r * math.cos(math.radians(a + angle)), cy + 0.55 * r * math.sin(math.radians(a + angle)))
             for a in (-90, 30, 150)]
    edge = base.lighter(185)
    edge.setAlpha(170)
    p.setPen(QPen(edge, max(1.0, r / 55)))
    tri = QPainterPath()
    tri.moveTo(inner[0])
    tri.lineTo(inner[1])
    tri.lineTo(inner[2])
    tri.closeSubpath()
    p.drawPath(tri)
    links = {0: (0, 1, 5), 1: (1, 2, 3), 2: (3, 4, 5)}
    for i, verts in links.items():
        for v in verts:
            p.drawLine(inner[i], pts[v])
    p.setPen(QPen(base.darker(230), max(1.2, r / 40)))
    p.drawPath(path)
    if number:
        f = QFont()
        f.setBold(True)
        f.setPixelSize(int(r * 0.62))
        p.setFont(f)
        p.setPen(QColor(0, 0, 0, 150))
        p.drawText(rect.translated(2, 3), int(Qt.AlignmentFlag.AlignCenter), number)
        p.setPen(QColor(num_color))
        p.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), number)


# ------------------------------------------------------------------------------------------------ dés polyédriques
def _rot(cx: float, cy: float, x: float, y: float, angle: float) -> QPointF:
    a = math.radians(angle)
    dx, dy = x - cx, y - cy
    return QPointF(cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))


def die_outline(sides: int, rect: QRectF, angle: float = 0.0) -> tuple[list[QPointF], list[tuple[QPointF, QPointF]]]:
    """Contour (polygone) et arêtes intérieures d'un dé vu de face : d4, d6, d8, d10, d12 (autres : cercle)."""
    cx, cy = rect.center().x(), rect.center().y()
    r = min(rect.width(), rect.height()) / 2

    def ring(n, radius, start=-90.0):
        return [QPointF(cx + radius * math.cos(math.radians(start + i * 360 / n)),
                        cy + radius * math.sin(math.radians(start + i * 360 / n))) for i in range(n)]
    lines: list[tuple[QPointF, QPointF]] = []
    c = QPointF(cx, cy + r * 0.12)
    if sides == 4:
        pts = ring(3, r * 1.02, -90)
        pts = [QPointF(p.x(), p.y() + r * 0.12) for p in pts]
        lines = [(c, p) for p in pts]
    elif sides == 6:
        k = r * 0.82
        pts = [QPointF(cx - k, cy - k), QPointF(cx + k, cy - k), QPointF(cx + k, cy + k), QPointF(cx - k, cy + k)]
        inner = [QPointF(cx - k * 0.72, cy - k * 0.72), QPointF(cx + k * 0.72, cy - k * 0.72),
                 QPointF(cx + k * 0.72, cy + k * 0.72), QPointF(cx - k * 0.72, cy + k * 0.72)]
        lines = [(inner[i], inner[(i + 1) % 4]) for i in range(4)] + [(pts[i], inner[i]) for i in range(4)]
    elif sides == 8:
        pts = [QPointF(cx, cy - r), QPointF(cx + r * 0.86, cy), QPointF(cx, cy + r), QPointF(cx - r * 0.86, cy)]
        tri = [QPointF(cx, cy - r), QPointF(cx + r * 0.55, cy + r * 0.32), QPointF(cx - r * 0.55, cy + r * 0.32)]
        lines = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0]), (tri[1], pts[1]), (tri[2], pts[3]),
                 (tri[1], pts[2]), (tri[2], pts[2])]
    elif sides == 10:
        pts = [QPointF(cx, cy - r), QPointF(cx + r * 0.95, cy - r * 0.08), QPointF(cx + r * 0.62, cy + r * 0.55),
               QPointF(cx, cy + r), QPointF(cx - r * 0.62, cy + r * 0.55), QPointF(cx - r * 0.95, cy - r * 0.08)]
        mid = [QPointF(cx - r * 0.42, cy + r * 0.3), QPointF(cx + r * 0.42, cy + r * 0.3)]
        lines = [(pts[0], mid[0]), (pts[0], mid[1]), (mid[0], mid[1]), (mid[0], pts[4]), (mid[1], pts[2]),
                 (mid[0], pts[3]), (mid[1], pts[3])]
    elif sides == 12:
        pts = ring(10, r, -90)
        inner = ring(5, r * 0.55, -90)
        lines = [(inner[i], inner[(i + 1) % 5]) for i in range(5)] + [(inner[i], pts[2 * i]) for i in range(5)]
    else:
        pts = ring(24, r * 0.95, -90)
    rot = lambda p: _rot(cx, cy, p.x(), p.y(), angle)   # noqa: E731
    return [rot(p) for p in pts], [(rot(a), rot(b)) for a, b in lines]


def paint_die(p: QPainter, rect: QRectF, sides: int, color: str, number: str = "", num_color: str = "#FFFFFF",
              angle: float = 0.0, glow: str = "") -> None:
    """Dessine un dé polyédrique (d4 → d12 ; d20 délégué à paint_d20) aux couleurs du thème."""
    if sides == 20:
        paint_d20(p, rect, color, number, num_color, angle, glow)
        return
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    base = QColor(color)
    pts, lines = die_outline(sides, rect, angle)
    path = QPainterPath()
    path.moveTo(pts[0])
    for pt in pts[1:]:
        path.lineTo(pt)
    path.closeSubpath()
    r = min(rect.width(), rect.height()) / 2
    if glow:
        for w, alpha in ((12, 40), (7, 80), (3, 120)):
            g = QColor(glow)
            g.setAlpha(alpha)
            p.setPen(QPen(g, w))
            p.drawPath(path)
    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, base.lighter(150))
    grad.setColorAt(0.55, base)
    grad.setColorAt(1.0, base.darker(190))
    p.fillPath(path, grad)
    edge = base.lighter(185)
    edge.setAlpha(160)
    p.setPen(QPen(edge, max(1.0, r / 50)))
    for a, b in lines:
        p.drawLine(a, b)
    p.setPen(QPen(base.darker(230), max(1.2, r / 38)))
    p.drawPath(path)
    if number:
        f = QFont()
        f.setBold(True)
        f.setPixelSize(int(r * (0.5 if sides == 4 else 0.62)))
        p.setFont(f)
        box = rect.translated(0, r * 0.14) if sides == 4 else rect
        p.setPen(QColor(0, 0, 0, 150))
        p.drawText(box.translated(2, 3), int(Qt.AlignmentFlag.AlignCenter), number)
        p.setPen(QColor(num_color))
        p.drawText(box, int(Qt.AlignmentFlag.AlignCenter), number)


def die_icon(sides: int, size: int = 22) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    try:
        paint_die(p, QRectF(1, 1, size - 2, size - 2), sides, theme.current().ornament)
    except TypeError:                                   # environnement de test sans Qt réel
        pass
    p.end()
    return QIcon(pix)


def d20_icon(size: int = 22) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    try:
        paint_d20(p, QRectF(1, 1, size - 2, size - 2), theme.current().ornament, "20" if size >= 30 else "")
    except TypeError:                                   # environnement de test sans Qt réel
        pass
    p.end()
    return QIcon(pix)


def d20_button(tip: str = "Lancer le d20") -> QToolButton:
    b = QToolButton()
    b.setIcon(d20_icon(22))
    b.setIconSize(QSize(20, 20))
    b.setAutoRaise(True)
    b.setFixedSize(QSize(30, 30))                    # taille fixe : même gabarit dans toutes les lignes
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setToolTip("<qt><b>🎲 {}</b><br/>Ouvre le lancer de d20 animé : bonus et malus détaillés, critiques "
                 "(20 naturel / 1 naturel) mis en évidence.</qt>".format(html.escape(tip)))
    return b


def retain_when_hidden(widget, on: bool) -> None:
    """Masqué -> garde (on=True) ou libère (False) sa place dans la grille : évite les décalages de ligne."""
    try:
        pol = widget.sizePolicy()
        pol.setRetainSizeWhenHidden(bool(on))
        widget.setSizePolicy(pol)
    except (AttributeError, TypeError):
        pass


class D20Widget(QWidget):
    """Grand d20 animé. `kept` : dé retenu (anneau doré + légère mise en avant) ; `dimmed` : dé écarté (grisé)."""

    def __init__(self, size: int = 200):
        super().__init__()
        self.setFixedSize(size, size)
        self.number, self.num_color, self.angle, self.glow = "?", "#FFFFFF", 0.0, ""
        self.kept, self.dimmed = False, False

    def set_state(self, number, num_color: str = "#FFFFFF", angle: float = 0.0, glow: str = "") -> None:
        self.number, self.num_color, self.angle, self.glow = str(number), num_color, angle, glow
        self.update()

    def set_choice(self, kept: bool, dimmed: bool) -> None:
        self.kept, self.dimmed = kept, dimmed
        self.update()

    def paintEvent(self, event):  # noqa: N802
        t = theme.current()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        m = 18
        if self.kept:                                       # anneau « dé retenu »
            ring = QColor(t.accent_text)
            for width, alpha in ((10, 60), (5, 140), (2, 255)):
                ring.setAlpha(alpha)
                p.setPen(QPen(ring, width))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QRectF(4, 4, self.width() - 8, self.height() - 8))
        if self.dimmed:                                     # dé écarté : grisé et transparent
            p.setOpacity(0.35)
        color = "#7A7A7A" if self.dimmed else t.ornament
        paint_d20(p, QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m), color,
                  self.number, "#D0D0D0" if self.dimmed else self.num_color, self.angle,
                  "" if self.dimmed else self.glow)
        if self.dimmed:                                     # barre diagonale « écarté »
            p.setOpacity(0.8)
            p.setPen(QPen(QColor(t.warn), 4))
            p.drawLine(QPointF(m + 10, self.height() - m - 10), QPointF(self.width() - m - 10, m + 10))
        p.end()


# ------------------------------------------------------------------------------------------------ fenêtre
class DiceRollDialog(QDialog):
    def __init__(self, parent, spec: D.RollSpec, rng=None):
        super().__init__(parent)
        self.spec = spec
        self.result = D.roll_d20(spec, rng)          # tirage fait d'emblée : l'animation ne fait que le révéler
        self._rng = random.Random()
        self.phase = "roll"                           # roll -> apply -> done
        self.applied = 0
        self.running_total = 0
        self._start = time.monotonic()
        self._next_change = 0.0
        self._last_step = 0.0
        t = theme.current()

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet("DiceRollDialog { background: transparent; background-image: none; }")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 26, 26, 30)
        card = QFrame()
        card.setObjectName("dialogCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(30, 22, 30, 22)
        lay.setSpacing(8)
        outer.addWidget(card)

        lay.addWidget(make_label("🎲  " + spec.title, "title", align=Qt.AlignmentFlag.AlignCenter))
        for line in spec.mode_lines():
            lay.addWidget(make_label(line, "warn" if "Désavantage" in line or "Échec" in line else "head",
                                     wrap=True, align=Qt.AlignmentFlag.AlignCenter))
        # un d20 (jet normal) ou deux d20 côte à côte (avantage / désavantage), chacun avec sa propre animation
        row = QHBoxLayout()
        row.addStretch(1)
        count = len(self.result.d20s)
        self.dice: list[D20Widget] = []
        self.captions: list[QLabel] = []
        self._numbers = [0] * count
        self._next = [0.0] * count
        self._spin = [1.0 if i == 0 else -0.8 for i in range(count)]        # sens / vitesse de rotation propres
        for i in range(count):
            col = QVBoxLayout()
            die = D20Widget(210 if count == 1 else 180)
            cap = make_label("Dé {}".format(i + 1) if count > 1 else "", "muted", align=Qt.AlignmentFlag.AlignCenter)
            col.addWidget(die)
            col.addWidget(cap)
            row.addLayout(col)
            if i == 0 and count > 1:
                row.addSpacing(24)
            self.dice.append(die)
            self.captions.append(cap)
        row.addStretch(1)
        lay.addLayout(row)
        self.die = self.dice[0]
        self.other = make_label("", "head", wrap=True, align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.other)
        self.crit = make_label("", "head", align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.crit)

        # bonus / malus listés dès l'ouverture (atténués), appliqués un par un après l'arrêt du d20
        box = QFrame()
        bl = QVBoxLayout(box)
        bl.setContentsMargins(0, 4, 0, 4)
        bl.addWidget(make_label("Bonus et malus de ce jet", "head"))
        self.term_labels: list[QLabel] = []
        if not spec.terms:
            bl.addWidget(make_label("Aucun bonus ni malus.", "muted"))
        for term in spec.terms:
            lab = make_label("⏳  " + term.text(), "muted")
            self.term_labels.append(lab)
            bl.addWidget(lab)
        lay.addWidget(box)
        self.total = make_label("Total : …", "stat", align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.total)
        if spec.note:
            lay.addWidget(make_label(spec.note, "muted", wrap=True, align=Qt.AlignmentFlag.AlignCenter))
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.skip_btn = QPushButton("Passer l'animation")
        self.skip_btn.setProperty("role", "ghost")
        self.close_btn = QPushButton("Continuer")
        self.close_btn.setEnabled(False)
        self.close_btn.setMinimumWidth(130)
        buttons.addWidget(self.skip_btn)
        buttons.addWidget(self.close_btn)
        lay.addLayout(buttons)
        self.skip_btn.clicked.connect(self.finish_now)
        self.close_btn.clicked.connect(self.accept)
        self._accent = t.accent_text
        for die in self.dice:
            die.set_state("?")

        self.timer = QTimer(self)
        self.timer.setInterval(16)                   # ≈ 60 images par seconde
        self.timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------ animation
    def start(self) -> None:
        self._start = time.monotonic()
        self.timer.start()

    def _tick(self) -> None:
        elapsed = (time.monotonic() - self._start) * 1000
        if self.phase == "roll":
            if elapsed >= ROLL_MS:
                self._freeze()
                self._last_step = elapsed
                return
            progress = elapsed / ROLL_MS
            ease = 1 - (1 - progress) ** 3
            for i, die in enumerate(self.dice):               # chaque dé défile indépendamment
                if elapsed >= self._next[i]:                  # cadence : très rapide puis de plus en plus lente
                    self._next[i] = elapsed + 40 + 220 * progress ** 2 + self._rng.randint(0, 25)
                    self._numbers[i] = self._rng.randint(1, 20)
                die.set_state(self._numbers[i] or "?", "#FFFFFF", angle=720 * self._spin[i] * ease)
        elif self.phase == "apply" and elapsed - self._last_step >= STEP_MS:
            self._last_step = elapsed
            self._apply_next()

    def _freeze(self) -> None:
        """Le d20 se fige : résultat brut affiché (vert / rouge en cas de critique), puis application des bonus."""
        r = self.result
        kept = self.kept_index()
        for i, (die, value) in enumerate(zip(self.dice, r.d20s)):
            color = CRIT_GREEN if value == 20 else CRIT_RED if value == 1 else "#FFFFFF"
            die.set_state(value, color, 0.0, glow=color if value in (1, 20) and i == kept else "")
            if len(self.dice) > 1:
                die.set_choice(kept=i == kept, dimmed=i != kept)
                self.captions[i].setText("<b style='color:{}'>✔ Retenu</b>".format(self._accent) if i == kept
                                         else "<span style='color:gray'>✖ Écarté</span>")
        if len(r.d20s) == 2:
            rule = "on garde le meilleur" if self.spec.mode == "avantage" else "on garde le moins bon"
            self.other.setText("{} : {} et {} — {} → <b>{}</b>".format(
                self.spec.mode.capitalize(), r.d20s[0], r.d20s[1], rule, r.natural))
        if r.critical == "succes":
            self.crit.setText("<span style='color:{}'>✨ 20 naturel — réussite critique !</span>".format(CRIT_GREEN))
        elif r.critical == "echec":
            self.crit.setText("<span style='color:{}'>💀 1 naturel — échec critique !</span>".format(CRIT_RED))
        self.running_total = r.natural
        self.total.setText("Total : {}".format(self.running_total))
        self.phase = "apply" if self.spec.terms else "done"
        if self.phase == "done":
            self._done()

    def kept_index(self) -> int:
        """Indice du dé retenu : le meilleur avec avantage, le moins bon avec désavantage (le premier si égalité)."""
        return self.result.d20s.index(self.result.natural)

    def _apply_next(self) -> None:
        if self.applied >= len(self.spec.terms):
            self._done()
            return
        i = self.applied
        term, value = self.spec.terms[i], self.result.term_values[i]
        self.running_total += value
        shown = "{} → {:+d}".format(term.text(), value) if term.dice else term.text()
        self.term_labels[i].setText("<b style='color:{}'>✔  {}</b>".format(self._accent, html.escape(shown)))
        self.term_labels[i].setProperty("role", "")
        self.total.setText("Total : {}".format(self.running_total))
        self.applied += 1
        if self.applied >= len(self.spec.terms):
            self._done()

    def _done(self) -> None:
        self.phase = "done"
        if self.timer.isActive():
            self.timer.stop()
        r = self.result
        text = "Total : {}".format(r.total)
        if r.auto_fail:
            text += "  — échec automatique"
        self.total.setText(text)
        self.close_btn.setEnabled(True)
        self.close_btn.setFocus()
        self.skip_btn.setEnabled(False)

    def finish_now(self) -> None:
        """Saute l'animation (bouton « Passer l'animation » ; utilisé aussi par les tests)."""
        if self.phase == "roll":
            self._freeze()
        while self.phase == "apply":
            self._apply_next()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None:
            self.move(parent.frameGeometry().center() - self.rect().center())
        self.start()


def roll_dice(win, spec) -> "D.RollResult | None":
    """Ouvre la fenêtre de lancer (fond flouté semi-transparent) et renvoie le résultat."""
    if spec is None:
        return None
    backdrop = BlurBackdrop(win, tint="rgba(0, 0, 0, 90)")
    dialog = DiceRollDialog(win, spec)
    try:
        dialog.exec()
    finally:
        backdrop.dispose()
    r = dialog.result
    win.statusBar().showMessage("🎲 {} : d20 = {}{} → total {}".format(
        spec.title, r.natural, " (critique !)" if r.critical == "succes" else " (échec critique)" if r.critical else "",
        r.total), 8000)
    return r


# ================================================================================================ dés de dégâts
DMG_ROLL_MS = 1400


class DieWidget(QWidget):
    """Dé polyédrique animé (d4, d6, d8, d10, d12, d20) ; `best` : face maximale (halo vert)."""

    def __init__(self, sides: int, size: int = 110):
        super().__init__()
        self.sides = sides
        self.setFixedSize(size, size + 30)              # place réservée au libellé « d6 » (jamais tronqué)
        self.number, self.num_color, self.angle, self.glow = "?", "#FFFFFF", 0.0, ""

    def set_state(self, number, num_color: str = "#FFFFFF", angle: float = 0.0, glow: str = "") -> None:
        self.number, self.num_color, self.angle, self.glow = str(number), num_color, angle, glow
        self.update()

    def paintEvent(self, event):  # noqa: N802
        t = theme.current()
        p = QPainter(self)
        m = max(8, self.width() // 9)
        side = self.width() - 2 * m
        paint_die(p, QRectF(m, m, side, side), self.sides, t.ornament, self.number, self.num_color, self.angle,
                  self.glow)
        p.setPen(QColor(t.muted))
        f = QFont()
        f.setPixelSize(14)
        f.setBold(True)
        p.setFont(f)
        p.drawText(QRectF(0, self.height() - 28, self.width(), 26), int(Qt.AlignmentFlag.AlignCenter),
                   "d{}".format(self.sides))
        p.end()


def flat_text(spec, flat: int) -> str:
    """v46 : bonus fixe EXPLIQUÉ (caractéristique, objet magique, style…) au lieu d'un chiffre brut."""
    calc = getattr(spec, "calcul", "") or ""
    labels = getattr(spec, "flat_labels", []) or []
    if labels and sum(v for _, v in labels) == flat:
        text = "Bonus fixe : " + D.flat_breakdown(labels, flat)
    else:
        text = "Bonus fixe : {:+d}".format(flat) if flat else "Aucun bonus fixe."
    return text + ("\nCalcul : " + calc if calc else "")


class DamageRollDialog(QDialog):
    """
    Lancer de dégâts / soins / dé de ressource : un dé animé par dé de la formule (2d6 -> deux d6 côte à côte),
    défilement ≈ 1,4 s puis arrêt, somme des dés + bonus fixe = total. Non bloquant (QTimer).
    """

    def __init__(self, parent, spec: D.DamageSpec, rng=None):
        super().__init__(parent)
        self.spec = spec
        self.result = D.roll_damage(spec, rng)
        self._rng = random.Random()
        self.phase = "roll"
        self._start = time.monotonic()
        t = theme.current()
        self._accent = t.accent_text
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setStyleSheet("DamageRollDialog { background: transparent; background-image: none; }")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 26, 26, 30)
        card = QFrame()
        card.setObjectName("dialogCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(30, 22, 30, 26)
        lay.setSpacing(10)
        card.setMinimumWidth(420)
        outer.addWidget(card)
        icon = {"soins": "💚", "de": "🎲", "pv_temp": "🛡"}.get(spec.kind, "💥")
        lay.addWidget(make_label("{}  {}".format(icon, spec.title), "title", align=Qt.AlignmentFlag.AlignCenter))
        kind_txt = {"soins": "Soins", "de": "Dé", "pv_temp": "PV temporaires"}.get(spec.kind, "Dégâts")
        lay.addWidget(make_label("{} : {}{}".format(kind_txt, spec.formula, " " + spec.damage_type if spec.damage_type
                                                    else ""), "head", align=Qt.AlignmentFlag.AlignCenter))
        # un dé animé par dé de la formule — taille adaptée au nombre de dés, 6 par ligne au plus
        n = len(self.result.dice)
        size = 120 if n <= 3 else 92 if n <= 6 else 70
        grid = QVBoxLayout()
        self.dice: list[DieWidget] = []
        per_row = 6
        for start in range(0, n, per_row):
            row = QHBoxLayout()
            row.addStretch(1)
            for sides, _, _ in self.result.dice[start:start + per_row]:
                w = DieWidget(sides, size)
                w.set_state("?")
                self.dice.append(w)
                row.addWidget(w)
            row.addStretch(1)
            grid.addLayout(row)
        lay.addLayout(grid)
        self._numbers = [0] * n
        self._next = [0.0] * n
        self._spin = [(1 if i % 2 == 0 else -1) * (0.8 + 0.1 * (i % 3)) for i in range(n)]
        self.sum_label = make_label("", "head", wrap=True, align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.sum_label)
        flat = self.result.flat
        self.flat_label = make_label(flat_text(spec, flat), "muted", wrap=True, align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.flat_label)
        self.total = make_label("Total : …", "stat", align=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.total)
        if spec.note:
            lay.addWidget(make_label(spec.note, "muted", wrap=True, align=Qt.AlignmentFlag.AlignCenter))
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.skip_btn = QPushButton("Passer l'animation")
        self.skip_btn.setProperty("role", "ghost")
        self.close_btn = QPushButton("Continuer")
        self.close_btn.setEnabled(False)
        self.close_btn.setMinimumWidth(130)
        buttons.addWidget(self.skip_btn)
        buttons.addWidget(self.close_btn)
        lay.addLayout(buttons)
        self.skip_btn.clicked.connect(self.finish_now)
        self.close_btn.clicked.connect(self.accept)
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)

    def start(self) -> None:
        self._start = time.monotonic()
        self.timer.start()

    def _tick(self) -> None:
        elapsed = (time.monotonic() - self._start) * 1000
        if self.phase != "roll":
            return
        if elapsed >= DMG_ROLL_MS:
            self._freeze()
            return
        progress = elapsed / DMG_ROLL_MS
        ease = 1 - (1 - progress) ** 3
        for i, (die, (sides, _, _)) in enumerate(zip(self.dice, self.result.dice)):
            if elapsed >= self._next[i]:
                self._next[i] = elapsed + 35 + 200 * progress ** 2 + self._rng.randint(0, 25)
                self._numbers[i] = self._rng.randint(1, sides)
            die.set_state(self._numbers[i] or "?", "#FFFFFF", angle=540 * self._spin[i] * ease)

    def _freeze(self) -> None:
        r = self.result
        for die, (sides, value, sign) in zip(self.dice, r.dice):
            best = value == sides
            color = CRIT_GREEN if best else CRIT_RED if value == 1 and sides > 2 else "#FFFFFF"
            die.set_state(("-" if sign < 0 else "") + str(value), color, 0.0, glow=CRIT_GREEN if best else "")
        parts = " + ".join(("−" if sign < 0 else "") + str(v) for _, v, sign in r.dice) or "0"
        self.sum_label.setText("Dés : {} = <b>{}</b>".format(parts, r.dice_sum))
        if r.flat or getattr(self.spec, "calcul", ""):
            self.flat_label.setText("<b style='color:{}'>✔ {}</b>".format(self._accent, html.escape(
                flat_text(self.spec, r.flat))))
        word = {"soins": "PV regagnés", "de": "Résultat", "pv_temp": "PV temporaires"}.get(self.spec.kind, "dégâts")
        self.total.setText("Total : {} {}".format(r.total, word if self.spec.kind != "degats" else
                                                  "dégâts" + (" " + self.spec.damage_type if self.spec.damage_type
                                                              else "")))
        self.phase = "done"
        if self.timer.isActive():
            self.timer.stop()
        self.close_btn.setEnabled(True)
        self.close_btn.setFocus()
        self.skip_btn.setEnabled(False)

    def finish_now(self) -> None:
        if self.phase == "roll":
            self._freeze()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None:
            self.move(parent.frameGeometry().center() - self.rect().center())
        self.start()


def roll_damage_dialog(win, spec) -> "D.DamageResult | None":
    """Ouvre l'animation multi-dés (fond flouté) et renvoie le résultat ; None si la formule n'a pas de dé."""
    if spec is None or not D.has_dice(spec.formula):
        return None
    backdrop = BlurBackdrop(win, tint="rgba(0, 0, 0, 90)")
    dialog = DamageRollDialog(win, spec)
    try:
        dialog.exec()
    finally:
        backdrop.dispose()
    dialog.finish_now()
    r = dialog.result
    word = {"soins": "PV regagnés", "de": "", "pv_temp": "PV temporaires"}.get(spec.kind, "dégâts")
    win.statusBar().showMessage("🎲 {} : {} → {} {}".format(spec.title, spec.formula, r.total, word).strip(), 8000)
    return r


def roll_initiative(win) -> "D.RollResult | None":
    """v45 — jet d'initiative : 1d20 + modificateur d'initiative (Dextérité, Alerte, aptitudes, effets) dans la
    fenêtre de dés animée (détail du calcul affiché) ; le résultat est gardé sur la fiche et rappelé dans la barre
    d'état."""
    eng = win.engine
    spec = eng.initiative_spec()
    r = roll_dice(win, spec)
    if r is None:
        return None
    eng.record_initiative(r.total)
    detail = " ".join(t.text() for t in spec.terms)
    win.statusBar().showMessage("🎲 Initiative : d20 = {} {} = {}".format(r.natural, detail, r.total), 12000)
    if hasattr(win, "changed"):
        win.changed()
    return r
