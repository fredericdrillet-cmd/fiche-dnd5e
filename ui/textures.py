"""
Textures procédurales (tuiles PNG semi-transparentes) superposées aux dégradés des thèmes.

Les tuiles sont générées une seule fois dans ~/.dnd5e_fiche/textures/ puis réutilisées. Elles sont volontairement
très discrètes (alpha faible) : l'audit WCAG des thèmes tient compte de leur intensité maximale.
Types : grain (cuir/parchemin) · leaf (grain verdoyant) · scan (lignes de balayage) · stone (pierre) ·
runes (runes nordiques) · embers (braises) · crystal (facettes) · ink (hachures d'encre) · hologram (grille).
"""
from __future__ import annotations

import random
import zlib
from pathlib import Path

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen

TILE = 128


def textures_dir() -> Path:
    return Path.home() / ".dnd5e_fiche" / "textures"


def _paint(kind: str, ornament: str) -> QImage:
    img = QImage(TILE, TILE, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    rng = random.Random(zlib.crc32(kind.encode()))        # résultat identique à chaque génération

    def color(hex_color: str, alpha: int) -> QColor:
        c = QColor(hex_color)
        c.setAlpha(alpha)
        return c

    def dot(x: float, y: float, hex_color: str, alpha: int, r: float = 1.0) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color(hex_color, alpha))
        p.drawEllipse(QPointF(x, y), r, r)

    def line(x1: float, y1: float, x2: float, y2: float, hex_color: str, alpha: int, w: float = 1.0) -> None:
        p.setPen(QPen(color(hex_color, alpha), w))
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def grain(count: int, hi: int = 16) -> None:
        for _ in range(count):
            dot(rng.uniform(0, TILE), rng.uniform(0, TILE), rng.choice(("#FFFFFF", "#000000")),
                rng.randint(6, hi), rng.uniform(0.5, 1.1))

    if kind == "grain":                                   # cuir / parchemin
        grain(520)
    elif kind == "leaf":                                  # grain verdoyant
        grain(260, 12)
        for _ in range(60):
            dot(rng.uniform(0, TILE), rng.uniform(0, TILE), ornament, rng.randint(8, 18), rng.uniform(0.6, 1.3))
    elif kind == "scan":                                  # lignes de balayage de HUD
        for y in range(0, TILE, 4):
            line(0, y + 0.5, TILE, y + 0.5, "#000000", 28)
        for y in (0, 64):
            line(0, y + 0.5, TILE, y + 0.5, ornament, 16)
    elif kind == "stone":                                 # pierre et fissures
        for _ in range(380):
            dot(rng.uniform(0, TILE), rng.uniform(0, TILE), rng.choice(("#FFFFFF", "#000000")),
                rng.randint(6, 16), rng.uniform(0.6, 1.7))
        for _ in range(7):
            x, y = rng.uniform(10, TILE - 10), rng.uniform(10, TILE - 10)
            for _ in range(3):
                nx, ny = x + rng.uniform(-9, 9), y + rng.uniform(-9, 9)
                line(x, y, nx, ny, "#000000", 30, 0.8)
                x, y = nx, ny
    elif kind == "runes":                                 # runes nordiques gravées
        grain(160, 10)
        for _ in range(7):
            x, y = rng.uniform(14, TILE - 14), rng.uniform(14, TILE - 24)
            h = rng.uniform(12, 20)
            line(x, y, x, y + h, ornament, 24, 1.3)
            for _ in range(rng.randint(1, 3)):
                by = y + rng.uniform(0, h * 0.7)
                d = rng.choice((-1, 1))
                line(x, by, x + d * rng.uniform(4, 8), by + rng.uniform(3, 8), ornament, 24, 1.3)
    elif kind == "embers":                                # braises
        grain(220, 12)
        for _ in range(110):
            dot(rng.uniform(0, TILE), rng.uniform(0, TILE), ornament, rng.randint(14, 44), rng.uniform(0.6, 1.5))
    elif kind == "crystal":                               # facettes de cristal
        for k in range(-TILE, TILE * 2, 32):
            line(k, 0, k + TILE, TILE, ornament, 20)
            line(k, TILE, k + TILE, 0, ornament, 14)
        for _ in range(26):
            dot(rng.uniform(0, TILE), rng.uniform(0, TILE), "#FFFFFF", rng.randint(24, 52), rng.uniform(0.6, 1.4))
    elif kind == "ink":                                   # hachures d'encre
        for k in range(-TILE, TILE, 8):
            line(k, 0, k + TILE, TILE, "#FFFFFF", 11, 0.8)
        grain(120, 10)
    elif kind == "hologram":                              # grille holographique
        for v in range(0, TILE, 32):
            line(v + 0.5, 0, v + 0.5, TILE, ornament, 17)
            line(0, v + 0.5, TILE, v + 0.5, ornament, 17)
        for x in range(0, TILE, 32):
            for y in range(0, TILE, 32):
                dot(x + 0.5, y + 0.5, ornament, 60, 1.2)
    p.end()
    return img


def texture_url(theme) -> str:
    """Chemin (format URL Qt) de la tuile du thème, générée au besoin ; chaîne vide si indisponible."""
    if not theme.texture:
        return ""
    try:
        path = textures_dir() / f"{theme.texture}_{theme.ornament.lstrip('#')}.png"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            if not _paint(theme.texture, theme.ornament).save(str(path), "PNG"):
                return ""
        return path.as_posix()
    except OSError:
        return ""        # sans texture, le thème reste entièrement fonctionnel (dégradés seuls)
