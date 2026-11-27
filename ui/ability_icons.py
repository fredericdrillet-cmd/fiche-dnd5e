"""
Symboles des caractéristiques (v53) : bras (Force), sauteur (Dextérité), cœur (Constitution), tête (Intelligence),
ampoule (Sagesse), personnage bras levé (Charisme) — data/images/caracteristiques/<caractéristique>.png (blanc = dessin), rendus
en « carré peint sombre » de la couleur de la caractéristique.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from core.paths import get_resource_path
from . import icons as IC

# v53 : noms de fichiers complets — « con » est un nom réservé sous Windows (le dépôt ne s'y extrait plus)
KEYS = {"Force": "force", "Dextérité": "dexterite", "Constitution": "constitution", "Intelligence": "intelligence",
        "Sagesse": "sagesse", "Charisme": "charisme"}
COLORS = {"force": "#991539", "dexterite": "#326A83", "constitution": "#035F3B", "intelligence": "#B4832D",
          "sagesse": "#680F62", "charisme": "#A71758"}


def icon_path(ability: str) -> Optional[str]:
    key = KEYS.get(ability, "")
    path = Path(get_resource_path(str(Path("data") / "images" / "caracteristiques" / (key + ".png"))))
    return str(path) if key and path.is_file() else None


def ability_pixmap(ability: str, size: int):
    path = icon_path(ability)
    if not path:
        return None
    return IC.tinted_stone_pixmap(path, COLORS[KEYS[ability]], size)


def icon_label(ability: str, size: int = 24) -> QLabel:
    """Petite icône de la caractéristique (vide si le symbole manque) ; nette sur écran haute densité."""
    lab = QLabel()
    try:
        ratio = 2
        pix = ability_pixmap(ability, size * ratio)
        if pix is not None and not pix.isNull():
            pix.setDevicePixelRatio(ratio)
            lab.setPixmap(pix)
        lab.setFixedSize(size, size)
        lab.setToolTip(ability)
    except (AttributeError, TypeError):                  # faux Qt des tests
        pass
    return lab


def with_icon(ability: str, widget: QWidget, size: int = 24, spacing: int = 6) -> QWidget:
    """Le widget (nom de la caractéristique) précédé de son icône."""
    box = QWidget()
    lay = QHBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(spacing)
    lay.addWidget(icon_label(ability, size))
    lay.addWidget(widget)
    lay.addStretch(1)
    try:
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
    except (AttributeError, TypeError):
        pass
    return box
