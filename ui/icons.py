"""
Rendu des icônes (v53) : carré plein façon jeu de rôle — fond en dégradé de la couleur de la catégorie (attaque
rouge, magie bleue, soins verts, action commune brune… accordée au thème), cadre fin, dessin clair avec ombre
portée et légère lueur. Les dessins viennent de data/icons (actions, armes, objets…) ou de core/spell_icons
(un dessin par sort). Cache par (dessin, catégorie, taille, thème).
"""
from __future__ import annotations

from functools import lru_cache

from PyQt6.QtCore import QByteArray, QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient

try:                                                     # absent du faux Qt des tests : icônes vides
    from PyQt6.QtSvg import QSvgRenderer
    HAS_SVG = True
except ImportError:                                      # pragma: no cover - dépend de l'installation
    QSvgRenderer = None
    HAS_SVG = False

from core.icon_art import ICONS, svg_document
from core.paths import get_resource_path
from . import theme


def _svg_bytes(body: str) -> QByteArray:
    return QByteArray(svg_document("icone", body).encode("utf-8"))


@lru_cache(maxsize=4096)
def _glyph_mask(body: str, size: int) -> QImage:
    """Dessin -> masque alpha (blanc opaque = visible, noir = découpe transparente)."""
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    QSvgRenderer(_svg_bytes(body)).render(p, QRectF(0, 0, size, size))
    p.end()
    gray = img.convertToFormat(QImage.Format.Format_Grayscale8)
    alpha = img.convertToFormat(QImage.Format.Format_Alpha8)
    mask = QImage(size, size, QImage.Format.Format_Grayscale8)
    for y in range(size):                                # alpha × luminance : le noir devient transparent
        g_line, a_line, m_line = gray.scanLine(y), alpha.scanLine(y), mask.scanLine(y)
        g_line.setsize(size)
        a_line.setsize(size)
        m_line.setsize(size)
        m_line[:] = bytes(a * l // 255 for a, l in zip(bytes(a_line), bytes(g_line)))
    return mask


def _tinted(body: str, size: int, color: str) -> QImage:
    out = QImage(size, size, QImage.Format.Format_ARGB32)
    out.fill(QColor(color))
    out.setAlphaChannel(_glyph_mask(body, size))
    return out


def named_body(name: str) -> str:
    """Corps SVG d'une icône nommée (data/icons, sinon dessin direct, sinon « inconnu »)."""
    fn = ICONS.get(name) or ICONS["inconnu"]
    return fn()


@lru_cache(maxsize=4096)
def _render(body: str, category: str, size: int, theme_key: str, dim: bool) -> QPixmap:
    if not HAS_SVG:
        return QPixmap()
    t = theme.THEMES.get(theme_key) or theme.current()
    pal = theme.icon_palette(t).get(category) or theme.icon_palette(t)["commune"]
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    r = QRectF(1, 1, size - 2, size - 2)
    radius = size * 0.14
    shape = QPainterPath()
    shape.addRoundedRect(r, radius, radius)
    grad = QLinearGradient(r.topLeft(), r.bottomRight())
    grad.setColorAt(0, QColor(pal["haut"]))
    grad.setColorAt(1, QColor(pal["bas"]))
    p.fillPath(shape, grad)
    hi = QRadialGradient(QPointF(size * 0.35, size * 0.25), size * 0.7)    # reflet doux en haut à gauche
    hi.setColorAt(0, QColor(255, 255, 255, 46))
    hi.setColorAt(1, QColor(255, 255, 255, 0))
    p.fillPath(shape, hi)
    g = int(size * 0.74)
    off = (size - g) // 2
    glow = _tinted(body, g, pal["glyphe"])               # lueur : dessin agrandi, très transparent
    p.setOpacity(0.28)
    p.drawImage(QRectF(off - size * 0.04, off - size * 0.04, g + size * 0.08, g + size * 0.08), glow)
    p.setOpacity(0.55)                                   # ombre portée
    p.drawImage(QRectF(off + size * 0.03, off + size * 0.04, g, g), _tinted(body, g, "#000000"))
    p.setOpacity(1.0)
    p.drawImage(QRectF(off, off, g, g), _tinted(body, g, pal["glyphe"]))
    p.setPen(QPen(QColor(pal["cadre"]), max(1.5, size / 28)))
    p.drawPath(shape)
    if dim:                                              # indisponible : voile sombre
        p.fillPath(shape, QColor(0, 0, 0, 140))
    p.end()
    return QPixmap.fromImage(img)


def icon_pixmap(name: str, category: str, size: int = 56, dim: bool = False) -> QPixmap:
    """Icône nommée (data/icons) rendue dans le style de la catégorie et du thème courant."""
    return _render(named_body(name), category, size, theme.current().key, dim)


def spell_pixmap(db, spell_name: str, category: str = "", size: int = 56, dim: bool = False) -> QPixmap:
    """Icône unique d'un sort : couleur de son école (verte pour un sort de soins)."""
    from core import spell_icons as SI
    from core.rules import norm
    body = SI.spell_icon(db.spells, spell_name) or ICONS["sort"]()
    if not category:
        sp = db.find_spell(spell_name) or {}
        category = "soins" if SI.is_healing(sp) else theme.SCHOOL_KEYS.get(norm(sp.get("ecole", "")), "magie")
    return _render(body, category, size, theme.current().key, dim)


def icon_file(name: str) -> str:
    return get_resource_path("data/icons/{}.svg".format(name))
