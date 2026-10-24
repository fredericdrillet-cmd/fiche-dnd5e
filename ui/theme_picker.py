"""Sélecteurs de thème : liste déroulante à icônes (barre de menu) et galerie de cartes (fenêtre Options)."""
from __future__ import annotations

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QComboBox, QGridLayout, QPushButton, QWidget

from . import theme


def theme_icon(t: "theme.Theme", size: int = 22) -> QIcon:
    """Pastille du thème : fond dégradé, liseré d'ornement et petit bouton coloré."""
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    grad = QLinearGradient(0, 0, 0, size)
    grad.setColorAt(0.0, QColor(t.panel))
    grad.setColorAt(1.0, QColor(t.bg2))
    p.setBrush(grad)
    p.setPen(QPen(QColor(t.ornament), 2))
    p.drawRoundedRect(1, 1, size - 2, size - 2, 5, 5)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(t.button_bg))
    p.drawRoundedRect(int(size * 0.25), int(size * 0.55), int(size * 0.5), int(size * 0.22), 3, 3)
    p.setBrush(QColor(t.accent_text))
    p.drawEllipse(int(size * 0.4), int(size * 0.2), int(size * 0.2), int(size * 0.2))
    p.end()
    return QIcon(pm)


def make_theme_combo() -> QComboBox:
    """Liste déroulante compacte des thèmes (donnée = clé du thème)."""
    combo = QComboBox()
    combo.setIconSize(QSize(22, 22))
    combo.setToolTip("Changer de thème graphique")
    for key, t in theme.THEMES.items():
        combo.addItem(theme_icon(t), t.name, key)
    combo.setMinimumWidth(230)
    return combo


class ThemeGallery(QWidget):
    """Galerie de cartes cliquables : chaque carte est rendue avec le dégradé et les couleurs de son thème."""

    chosen = pyqtSignal(str)

    def __init__(self, current_key: str, columns: int = 2):
        super().__init__()
        grid = QGridLayout(self)
        grid.setSpacing(10)
        self.buttons: dict[str, QPushButton] = {}
        for i, (key, t) in enumerate(theme.THEMES.items()):
            b = QPushButton("{}{}\n{}".format(t.name, "   ★ par défaut" if key == theme.DEFAULT_THEME else "", t.game))
            b.setCheckable(True)
            b.setAutoExclusive(True)
            b.setMinimumHeight(66)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setToolTip(t.description)
            b.setStyleSheet(
                "QPushButton {{ background: {g}; color: {fg}; border: 2px solid {orn}; border-radius: 9px; "
                "text-align: left; padding: 8px 12px; font-weight: bold; }}"
                "QPushButton:hover {{ border: 2px solid {acc}; }}"
                "QPushButton:checked {{ border: 4px solid {acc}; }}".format(
                    g=theme.vgrad(t.bg, t.bg2), fg=t.text, orn=t.ornament, acc=t.accent_text))
            b.clicked.connect(lambda _=False, k=key: self.chosen.emit(k))
            grid.addWidget(b, i // columns, i % columns)
            self.buttons[key] = b
        self.select(current_key)

    def select(self, key: str) -> None:
        for k, b in self.buttons.items():
            b.setChecked(k == key)
