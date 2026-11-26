"""
Rendu des icônes (v53) : « pierre runique » — octogone de pierre grise sertie d'argent, rune gravée qui luit de
la couleur de la catégorie (attaque rouge, magie de l'école, soins verts, action commune brune, rareté…). Les dessins viennent de data/icons (actions, armes, objets…) ou de core/spell_icons
(un dessin par sort). Cache par (dessin, catégorie, taille, thème).
"""
from __future__ import annotations

from functools import lru_cache

from PyQt6.QtCore import QByteArray, QPointF, QRectF, Qt
from PyQt6.QtGui import (QBrush, QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap,
                         QRadialGradient)

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
    """Dessin -> masque alpha (blanc opaque = visible, noir = découpe transparente). v53 : rendu en blanc sur fond
    NOIR opaque, puis niveaux de gris = couverture × luminance — sans boucle Python sur les pixels."""
    img = QImage(size, size, QImage.Format.Format_RGB32)
    img.fill(QColor(0, 0, 0))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    QSvgRenderer(_svg_bytes(body)).render(p, QRectF(0, 0, size, size))
    p.end()
    return img.convertToFormat(QImage.Format.Format_Grayscale8)


def _tinted(body: str, size: int, color: str) -> QImage:
    out = QImage(size, size, QImage.Format.Format_ARGB32)
    out.fill(QColor(color))
    out.setAlphaChannel(_glyph_mask(body, size))
    return out


def named_body(name: str) -> str:
    """Corps SVG d'une icône nommée (data/icons, sinon dessin direct, sinon « inconnu »)."""
    fn = ICONS.get(name) or ICONS["inconnu"]
    return fn()


# v53 : style « pierre runique » — octogone de pierre grise sertie d'argent, rune gravée qui luit de la couleur
# de la catégorie (attaque rouge, magie de l'école, soins verts, rareté de l'objet…).
_GRAIN = 256                                             # texture de grain partagée (tirée une fois, sans numpy)


@lru_cache(maxsize=4)
def _grain(strength: int, light: bool) -> QImage:
    """Grain de pierre : points noirs (ou blancs) d'opacité aléatoire ; une seule texture, décalée par icône."""
    import random
    rng = random.Random(4217 + strength + light)
    level = 255 if light else 0
    data = bytearray(_GRAIN * _GRAIN * 4)
    alphas = rng.randbytes(_GRAIN * _GRAIN)
    for i, a in enumerate(alphas):
        a = a * strength // 256
        v = level * a // 255                              # prémultiplié
        data[4 * i:4 * i + 4] = bytes((v, v, v, a))
    return QImage(bytes(data), _GRAIN, _GRAIN, _GRAIN * 4, QImage.Format.Format_ARGB32_Premultiplied).copy()


def _seed(body: str) -> int:
    import zlib
    return zlib.crc32(body.encode("utf-8"))


def _hls(h: float, l: float, s: float) -> QColor:
    import colorsys
    r, g, b = colorsys.hls_to_rgb(h / 360, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return QColor(round(r * 255), round(g * 255), round(b * 255))


def _glyph_gradient(body: str, size: int, top: QColor, bottom: QColor) -> QImage:
    out = QImage(size, size, QImage.Format.Format_ARGB32)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    grad = QLinearGradient(0, 0, 0, size)
    grad.setColorAt(0, top)
    grad.setColorAt(1, bottom)
    p.fillRect(0, 0, size, size, grad)
    p.end()
    out.setAlphaChannel(_glyph_mask(body, size))
    return out


def _octagon(size: int, m: float) -> QPainterPath:
    from PyQt6.QtGui import QPolygonF
    k = size * 0.29
    pts = [(k, m), (size - k, m), (size - m, k), (size - m, size - k), (size - k, size - m), (k, size - m),
           (m, size - k), (m, k)]
    path = QPainterPath()
    path.addPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
    path.closeSubpath()
    return path


@lru_cache(maxsize=4096)
def _render(body: str, category: str, size: int, theme_key: str, dim: bool) -> QPixmap:
    if not HAS_SVG:
        return QPixmap()
    import random
    hue, sat = theme.ICON_HUES.get(category) or theme.ICON_HUES["commune"]
    seed = _seed(body)
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    stone = _octagon(size, 1)
    grad = QLinearGradient(0, 0, size, size)             # pierre grise, plus claire en haut à gauche
    grad.setColorAt(0, QColor("#7C7A76"))
    grad.setColorAt(1, QColor("#2E2C2A"))
    p.fillPath(stone, grad)
    p.setClipPath(stone)
    ox, oy = seed % (_GRAIN - size) if size < _GRAIN else 0, (seed >> 8) % (_GRAIN - size) if size < _GRAIN else 0
    p.drawImage(QPointF(0, 0), _grain(70, False), QRectF(ox, oy, size, size))
    p.drawImage(QPointF(0, 0), _grain(30, True), QRectF(oy, ox, size, size))
    rng = random.Random(seed)                            # deux fissures, propres à chaque dessin
    p.setPen(QPen(QColor(0, 0, 0, 90), max(0.8, size / 90)))
    for _ in range(2):
        x, y = rng.random() * size, rng.random() * size
        crack = QPainterPath(QPointF(x, y))
        for _ in range(4):
            x += (rng.random() - 0.5) * size * 0.3
            y += (rng.random() - 0.5) * size * 0.3
            crack.lineTo(x, y)
        p.drawPath(crack)
    p.setClipping(False)
    inner = _octagon(size, size * 0.09)                  # biseau intérieur
    p.setPen(QPen(QColor(255, 255, 255, 60), max(1.0, size / 45)))
    p.drawPath(inner.translated(-0.7, -0.7))
    p.setPen(QPen(QColor(0, 0, 0, 140), max(1.0, size / 45)))
    p.drawPath(inner.translated(0.7, 0.7))
    silver = QLinearGradient(0, 0, size, size)           # sertissure d'argent
    for pos, col in ((0, "#FFFFFF"), (0.4, "#D6D9DE"), (0.7, "#8C939C"), (1, "#4A5058")):
        silver.setColorAt(pos, QColor(col))
    p.setPen(QPen(QBrush(silver), max(2.0, size / 18)))
    p.drawPath(stone)
    g = int(size * 0.60)
    off = (size - g) / 2
    rect = QRectF(off, off, g, g)
    # rune gravée : lueur de la catégorie, lèvre claire dessous, creux sombre, puis la rune lumineuse
    p.setOpacity(0.55)
    p.drawImage(rect.adjusted(-size * 0.06, -size * 0.06, size * 0.06, size * 0.06),
                _tinted(body, g, _hls(hue, 0.62, sat + 0.2).name()))
    p.setOpacity(0.8)
    p.drawImage(rect.translated(0, size / 40), _tinted(body, g, "#EDEDED"))
    p.setOpacity(1.0)
    p.drawImage(rect.translated(0, -size / 70), _tinted(body, g, "#141210"))
    p.drawImage(rect, _glyph_gradient(body, g, _hls(hue, 0.85, sat), _hls(hue, 0.55, sat + 0.2)))
    p.setPen(QPen(QColor("#0E0E0E"), max(1.0, size / 60)))
    p.drawPath(stone)
    if dim:                                              # indisponible : voile sombre
        p.fillPath(stone, QColor(0, 0, 0, 150))
    p.end()
    return QPixmap.fromImage(img)


@lru_cache(maxsize=512)
def tinted_stone_pixmap(mask_path: str, color: str, size: int, theme_key: str = "") -> QPixmap:
    """v53 : pierre runique teintée de `color`, dessin blanc gravé d'après un masque en niveaux de gris (blanc =
    dessin) — icônes de classe de l'assistant. Pixmap vide si le masque est illisible."""
    if not HAS_SVG:
        return QPixmap()
    import colorsys
    m = QImage(mask_path)
    if m.isNull():
        return QPixmap()
    g = int(size * 0.66)
    m = m.convertToFormat(QImage.Format.Format_Grayscale8).scaled(
        g, g, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    def paint(top: str, bottom: str = "") -> QImage:
        out = QImage(m.width(), m.height(), QImage.Format.Format_ARGB32)
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        if bottom:
            grad = QLinearGradient(0, 0, 0, m.height())
            grad.setColorAt(0, QColor(top))
            grad.setColorAt(1, QColor(bottom))
            p.fillRect(0, 0, m.width(), m.height(), grad)
        else:
            p.fillRect(0, 0, m.width(), m.height(), QColor(top))
        p.end()
        out.setAlphaChannel(m)
        return out

    c = QColor(color)
    h, _l, s = colorsys.rgb_to_hls(c.redF(), c.greenF(), c.blueF())
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    stone = _octagon(size, 1)
    grad = QLinearGradient(0, 0, size, size)             # pierre de la couleur de la classe
    grad.setColorAt(0, _hls(h * 360, 0.50, s))
    grad.setColorAt(1, _hls(h * 360, 0.22, s))
    p.fillPath(stone, grad)
    p.setClipPath(stone)
    o = _seed(mask_path) % (_GRAIN - size) if size < _GRAIN else 0
    p.drawImage(QPointF(0, 0), _grain(70, False), QRectF(o, o, size, size))
    p.drawImage(QPointF(0, 0), _grain(30, True), QRectF(0, o, size, size))
    p.setClipping(False)
    inner = _octagon(size, size * 0.09)
    p.setPen(QPen(QColor(255, 255, 255, 60), max(1.0, size / 45)))
    p.drawPath(inner.translated(-0.7, -0.7))
    p.setPen(QPen(QColor(0, 0, 0, 140), max(1.0, size / 45)))
    p.drawPath(inner.translated(0.7, 0.7))
    silver = QLinearGradient(0, 0, size, size)
    for pos, col in ((0, "#FFFFFF"), (0.4, "#D6D9DE"), (0.7, "#8C939C"), (1, "#4A5058")):
        silver.setColorAt(pos, QColor(col))
    p.setPen(QPen(QBrush(silver), max(2.0, size / 18)))
    p.drawPath(stone)
    x, y = (size - m.width()) / 2, (size - m.height()) / 2
    p.setOpacity(0.6)                                    # ombre gravée
    p.drawImage(QPointF(x + size / 60, y + size / 35), paint("#000000"))
    p.setOpacity(1.0)
    p.drawImage(QPointF(x, y), paint("#FFFFFF", "#E9E4DA"))
    p.setPen(QPen(QColor("#0E0E0E"), max(1.0, size / 60)))
    p.drawPath(stone)
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


def action_pixmap(name: str, category: str, size: int = 56, dim: bool = False) -> QPixmap:
    """v53 : icône unique d'une action (capacité, manœuvre, action d'arme…), couleur de sa catégorie."""
    from core.action_icons import action_body
    return _render(action_body(name), category, size, theme.current().key, dim)


def weapon_pixmap(weapon_text: str, size: int = 56, dim: bool = False) -> QPixmap:
    """v53 : dessin propre à l'arme (épée longue, rapière, hache d'armes…), en rouge « attaque »."""
    from core.action_icons import weapon_body
    body = weapon_body(weapon_text) or ICONS["attaque_generique"]()
    return _render(body, "attaque", size, theme.current().key, dim)


def icon_file(name: str) -> str:
    return get_resource_path("data/icons/{}.svg".format(name))


# ---------------------------------------------------------------------------------------------- cartes de sorts
def card_grid(lst, icon: int = 52, cell=(124, 116)) -> None:
    """v53 : liste en grille de cartes (icône carrée, nom dessous) — mêmes éléments, mêmes signaux qu'avant."""
    try:
        from PyQt6.QtCore import QSize
        from PyQt6.QtWidgets import QListView
        lst.setViewMode(QListView.ViewMode.IconMode)
        lst.setIconSize(QSize(icon, icon))
        lst.setGridSize(QSize(*cell))
        lst.setResizeMode(QListView.ResizeMode.Adjust)
        lst.setMovement(QListView.Movement.Static)
        lst.setWordWrap(True)
        lst.setUniformItemSizes(False)                   # v53 : chaque nom a la hauteur qu'il lui faut
        lst.setTextElideMode(Qt.TextElideMode.ElideNone)  # v53 : nom entier, sur trois lignes au besoin
    except (AttributeError, TypeError, ImportError):     # faux Qt des tests
        pass


def spell_card(it, db, sp: dict, prefix: str = "", size: int = 52, extra: str = "") -> None:
    """Élément de liste -> carte de sort : icône unique (couleur de l'école), nom court, niveau ; fiche au survol."""
    from PyQt6.QtGui import QIcon
    from .spell_inspector import spell_card_html
    lvl = int(sp.get("niveau") or 0)
    tags = "".join(x for x, on in ((" Ⓒ", sp.get("concentration")), (" ᴿ", sp.get("rituel"))) if on)
    it.setText("{}{}{}".format(prefix, sp["nom"].replace(" (2024)", ""), tags))   # niveau : dans la fiche
    it.setData(Qt.ItemDataRole.AccessibleDescriptionRole, "tour de magie" if lvl == 0 else "niveau {}".format(lvl))
    if HAS_SVG:
        it.setIcon(QIcon(spell_pixmap(db, sp["nom"], size=size)))
    it.setToolTip(spell_card_html(sp) + extra)
