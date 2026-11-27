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
                 permanent: bool = False, timer: str = "", on_extend=None):
        QWidget.__init__(self)
        self.timer = timer                               # v52 : « 7 r », « 9 min » (durée restante)
        self.on_extend = on_extend
        self.key, self.icon, self.name, self.category = key, icon, name, category
        self.permanent = permanent                       # trait inné (race / classe) : cadenas + liseré doré
        self.tip_html = tip_html + ("<p style='color:gray'><i>Trait permanent — clic : le retirer (confirmation "
                                    "demandée).</i></p>" if permanent else
                                    "<p style='color:gray'><i>Clic : retirer l'effet.{}</i></p>".format(
                                        " Clic droit : prolonger (durée complète)." if on_extend else ""))
        self.on_remove = on_remove
        self._hover = False
        self.lines = self.wrap(name)                     # v53 : nom entier, sur plusieurs lignes
        w, h = self.SIZE.width(), self.SIZE.height()
        try:
            from PyQt6.QtGui import QFontMetrics
            f = QFont(self.font())
            f.setPixelSize(10)
            f.setBold(True)
            fm = QFontMetrics(f)
            w = max(w, max(fm.horizontalAdvance(t) for t in self.lines) + 6)
            h = 53 + len(self.lines) * fm.lineSpacing() + 4
        except (AttributeError, TypeError, ValueError, ImportError):   # faux Qt des tests
            h = 53 + len(self.lines) * 13 + 4
        try:
            self.setFixedSize(QSize(int(w), int(max(h, self.SIZE.height()))))
        except (TypeError, ValueError):                  # faux Qt des tests
            self.setFixedSize(self.SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def _pixmap(self, color: QColor):
        """Icône soignée de l'effet (core/art_etats), en ×2 pour les écrans haute densité ; None sans dessin."""
        try:
            from core.art_etats import effect_body
            from . import icons as IC
            body = effect_body(self.key, self.name)
            if not body or not IC.HAS_SVG:
                return None
            key = "effet_" + self.category
            if key not in theme.ICON_HUES:                   # teinte de la catégorie (vert bonus, rouge malus…)
                import colorsys
                h, _l, s_ = colorsys.rgb_to_hls(color.redF(), color.greenF(), color.blueF())
                theme.ICON_HUES[key] = (h * 360, s_)
            return IC._render(body, key, 96, theme.current().key, False)
        except (ImportError, AttributeError, TypeError, KeyError):
            return None

    @staticmethod
    def wrap(name: str, width: int = 12) -> list[str]:
        lines: list[str] = []
        for word in (name or "").split(" "):
            if lines and len(lines[-1]) + 1 + len(word) <= width:
                lines[-1] += " " + word
            else:
                lines.append(word)
        return lines or [""]

    def enterEvent(self, event):  # noqa: N802
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):  # noqa: N802
        if self.on_extend and event.button() == Qt.MouseButton.RightButton:
            QToolTip.hideText()
            self.on_extend(self.key)
            return
        if self.on_remove:
            QToolTip.hideText()
            self.on_remove(self.key)

    def paintEvent(self, event):  # noqa: N802
        t = theme.current()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        color = QColor(CATEGORY_COLORS.get(self.category, t.ornament))
        x0 = (self.width() - 48) / 2                     # tuile centrée (la largeur suit le nom)
        tile = QRectF(x0, 3, 48, 48)
        path = QPainterPath()
        path.addRoundedRect(tile, 4.3, 4.3)
        pix = self._pixmap(color)
        if pix is not None:                              # v53 : dessin soigné « carré peint sombre »
            p.drawPixmap(tile.toRect(), pix)
        else:                                            # repli : emoji sur dégradé
            grad = QLinearGradient(tile.topLeft(), tile.bottomLeft())
            grad.setColorAt(0.0, color.lighter(135))
            grad.setColorAt(1.0, color.darker(170))
            p.fillPath(path, grad)
            f0 = QFont(self.font())
            f0.setPixelSize(24)
            p.setFont(f0)
            p.setPen(QColor("#ffffff"))
            p.drawText(tile, int(Qt.AlignmentFlag.AlignCenter), self.icon)
        if self._hover:
            p.setPen(QPen(QColor(t.accent_text), 2.4))
            p.drawPath(path)
        f = QFont(self.font())
        f.setPixelSize(10)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(t.text))
        p.drawText(QRectF(0, 52, self.width(), self.height() - 52),
                   int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop), "\n".join(self.lines))
        if self.permanent:                               # cadenas : trait racial / aptitude de classe permanente
            p.setBrush(QColor(t.panel))
            p.setPen(QPen(QColor(t.accent_text), 1.2))
            p.drawEllipse(QRectF(x0 - 5, 0, 16, 16))
            f.setPixelSize(10)
            p.setFont(f)
            p.drawText(QRectF(x0 - 5, 0, 16, 16), int(Qt.AlignmentFlag.AlignCenter), "🔒")
        if self.timer:                                   # v52 : pastille de durée restante
            f.setPixelSize(9)
            f.setBold(True)
            p.setFont(f)
            w = max(22, 7 * len(self.timer))
            pill = QRectF(x0 + 48 - w, 38, w, 13)
            p.setBrush(QColor(t.panel))
            p.setPen(QPen(QColor(t.accent_text), 1.0))
            p.drawRoundedRect(pill, 6, 6)
            p.setPen(QColor(t.text))
            p.drawText(pill, int(Qt.AlignmentFlag.AlignCenter), self.timer)
        if self._hover:                                  # pastille ✕ de retrait
            p.setBrush(QColor(t.warn))
            p.setPen(QPen(QColor("#ffffff"), 1.2))
            p.drawEllipse(QRectF(x0 + 37, 0, 16, 16))
            f.setPixelSize(11)
            p.setFont(f)
            p.drawText(QRectF(x0 + 37, 0, 16, 16), int(Qt.AlignmentFlag.AlignCenter), "✕")
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
