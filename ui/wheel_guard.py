"""
Molette neutralisée sur les contrôles (v35) : elle ne doit QUE faire défiler la page.

Un filtre d'événements installé sur l'application intercepte la molette au-dessus :
    - des listes déroulantes (QComboBox) ;
    - des champs numériques (QSpinBox, QDoubleSpinBox), même quand ils ont le focus ;
    - des barres d'onglets (QTabBar) ;
    - des curseurs (QSlider ; les barres de défilement restent actives).
L'événement n'atteint jamais le contrôle (aucune valeur, aucun onglet ne change) ; il est redirigé vers le premier
conteneur défilant parent (QScrollArea, liste, tableau, texte…), qui défile normalement. Les sphères et jauges de
ressources n'ont plus de gestion de la molette : elle remonte d'elle-même au conteneur.
"""
from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtWidgets import (QAbstractScrollArea, QAbstractSlider, QAbstractSpinBox, QComboBox, QScrollBar, QTabBar,
                             QWidget)

GUARDED = (QComboBox, QAbstractSpinBox, QTabBar, QAbstractSlider)


def guarded_control(obj) -> "QWidget | None":
    """Contrôle protégé visé par la molette (l'objet lui-même ou un parent proche : champ texte d'un compteur…)."""
    w = obj
    for _ in range(3):
        if not isinstance(w, QWidget):
            return None
        if isinstance(w, GUARDED) and not isinstance(w, QScrollBar):
            return w
        w = w.parentWidget()
    return None


def scroll_container(widget) -> "QAbstractScrollArea | None":
    """Premier ancêtre défilant qui peut réellement défiler."""
    w = widget.parentWidget() if isinstance(widget, QWidget) else None
    while isinstance(w, QWidget):
        if isinstance(w, QAbstractScrollArea):
            bar = w.verticalScrollBar()
            if bar is not None and bar.maximum() > bar.minimum():
                return w
        w = w.parentWidget()
    return None


def forward_scroll(widget, delta_y: int) -> bool:
    """Fait défiler le conteneur parent comme la molette l'aurait fait (3 pas par cran)."""
    area = scroll_container(widget)
    if area is None:
        return False
    bar = area.verticalScrollBar()
    notches = delta_y / 120.0
    bar.setValue(int(bar.value() - notches * max(1, bar.singleStep()) * 3))
    return True


class WheelGuard(QObject):
    def eventFilter(self, obj, event):  # noqa: N802
        if event.type() != QEvent.Type.Wheel:
            return False
        control = guarded_control(obj)
        if control is None:
            return False
        forward_scroll(control, event.angleDelta().y())
        return True                                      # le contrôle ne reçoit jamais la molette


_GUARD: "WheelGuard | None" = None


def install(app) -> "WheelGuard | None":
    """Installe le filtre une seule fois sur l'application."""
    global _GUARD
    if app is None or not hasattr(app, "installEventFilter"):
        return None
    if _GUARD is None:
        _GUARD = WheelGuard()
        app.installEventFilter(_GUARD)
    return _GUARD
