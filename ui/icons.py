"""
Rendu des icônes (v53) : « carré peint sombre » — fond de la couleur de la catégorie (attaque rouge, magie de
l'école, soins verts, action commune brune, rareté de l'objet…) en dégradé radial, dessin ivoire net avec une ombre
portée courte, cadre sombre et fin reflet. Les dessins viennent de core/game_art (dessins soignés), data/icons ou
core/spell_icons. Netteté : le dessin est calculé en ×4 puis réduit, recadré sur son étendue réelle (toutes les
icônes ont le même poids visuel ; `TAILLE_FIXE` dans le dessin garde sa taille propre, pour comparer les armes),
et colorié par composition (pixels prémultipliés valides : aucun liseré). Cache par (dessin, catégorie, taille, thème).
"""
from __future__ import annotations

import colorsys
from functools import lru_cache

from PyQt6.QtCore import QByteArray, QPointF, QRectF, Qt
from PyQt6.QtGui import (QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap,
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

SUPERSAMPLE = 4
FIXED_SIZE_MARK = "TAILLE_FIXE"                          # commentaire placé dans un dessin : pas de recadrage


def _svg_bytes(body: str) -> QByteArray:
    return QByteArray(svg_document("icone", body).encode("utf-8"))


@lru_cache(maxsize=4096)
def _glyph_mask(body: str, size: int) -> QImage:
    """Dessin -> masque en niveaux de gris (blanc = dessin, noir = découpe), calculé en ×4 puis réduit."""
    big = size * SUPERSAMPLE
    img = QImage(big, big, QImage.Format.Format_RGB32)
    img.fill(QColor(0, 0, 0))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    QSvgRenderer(_svg_bytes(body)).render(p, QRectF(0, 0, big, big))
    p.end()
    small = img.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return small.convertToFormat(QImage.Format.Format_Grayscale8)


def _colorize(mask: QImage, color: str, top: str = "") -> QImage:
    """Masque -> dessin colorié (dégradé vertical si `top`). Alpha posé d'abord, couleur composée ensuite : les
    pixels restent prémultipliés valides, sans liseré coloré sur les bords."""
    alpha = mask.convertToFormat(QImage.Format.Format_Grayscale8).copy()
    alpha.reinterpretAsFormat(QImage.Format.Format_Alpha8)
    out = QImage(mask.width(), mask.height(), QImage.Format.Format_ARGB32_Premultiplied)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.drawImage(0, 0, alpha)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    if top:
        grad = QLinearGradient(0, 0, 0, mask.height())
        grad.setColorAt(0, QColor(top))
        grad.setColorAt(1, QColor(color))
        p.fillRect(out.rect(), grad)
    else:
        p.fillRect(out.rect(), QColor(color))
    p.end()
    return out


def _tinted(body: str, size: int, color: str) -> QImage:
    return _colorize(_glyph_mask(body, size), color)


def named_body(name: str) -> str:
    """Corps SVG d'une icône nommée : dessin soigné (core/art_actions, core/art_objets) s'il existe, sinon
    data/icons, sinon dessin direct, sinon « inconnu »."""
    from core.art_actions import COMMON
    from core.art_objets import OBJECTS
    fn = COMMON.get(name) or OBJECTS.get(name) or ICONS.get(name) or ICONS["inconnu"]
    return fn()


def _hls(h: float, l: float, s: float) -> QColor:
    r, g, b = colorsys.hls_to_rgb(h / 360, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return QColor(round(r * 255), round(g * 255), round(b * 255))


def category_color(category: str) -> str:
    hue, sat = theme.ICON_HUES.get(category) or theme.ICON_HUES["commune"]
    return _hls(hue, 0.45, sat).name()


def tile_path(size: int, margin: float = 1.0) -> QPainterPath:
    """Contour des icônes : carré aux coins arrondis (aussi pour la bordure de rareté du sac)."""
    path = QPainterPath()
    path.addRoundedRect(QRectF(margin, margin, size - 2 * margin, size - 2 * margin), size * 0.09, size * 0.09)
    return path


def _bbox(mask: QImage):
    from PyQt6.QtGui import QBitmap, QRegion
    rgb = mask.convertToFormat(QImage.Format.Format_RGB32)
    bits = rgb.createMaskFromColor(QColor(0, 0, 0).rgb(), Qt.MaskMode.MaskInColor)
    return QRegion(QBitmap.fromImage(bits)).boundingRect()


def _fitted(mask: QImage, box: int, keep_size: bool) -> QImage:
    """Recadre le masque sur le dessin, puis le centre dans un carré `box` (agrandi pour le remplir, sauf
    `keep_size` : taille propre conservée, seulement centrée)."""
    try:
        r = _bbox(mask)
    except (ImportError, TypeError, AttributeError):    # pragma: no cover - Qt incomplet
        return mask.scaled(box, box)
    if r.isEmpty():
        return mask.scaled(box, box)
    crop = mask.copy(r)
    if keep_size:
        k = box / mask.width()
        crop = crop.scaled(max(1, round(crop.width() * k)), max(1, round(crop.height() * k)),
                           Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    else:
        side = round(box * 0.92)
        crop = crop.scaled(side, side, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    out = QImage(box, box, QImage.Format.Format_Grayscale8)
    out.fill(0)
    p = QPainter(out)
    p.drawImage(QPointF((box - crop.width()) / 2, (box - crop.height()) / 2), crop)
    p.end()
    return out


def _soft(img: QImage, radius: float) -> QImage:
    """Flou léger (réduction puis agrandissement lissés) pour l'ombre portée."""
    w, h = img.width(), img.height()
    k = max(2, int(radius))
    small = img.scaled(max(1, w // k), max(1, h // k), Qt.AspectRatioMode.IgnoreAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
    return small.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)


def _paint_tile(mask: QImage, color: str, size: int, dim: bool, keep_size: bool) -> QPixmap:
    c = QColor(color)
    hue, _l, sat = colorsys.rgb_to_hls(c.redF(), c.greenF(), c.blueF())
    hue *= 360
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    shape = tile_path(size)
    grad = QRadialGradient(QPointF(size * 0.5, size * 0.38), size * 0.8)    # fond peint : clair au centre-haut
    grad.setColorAt(0, _hls(hue, 0.44, sat))
    grad.setColorAt(0.65, _hls(hue, 0.26, sat))
    grad.setColorAt(1, _hls(hue, 0.13, sat))
    p.fillPath(shape, grad)
    box = int(size * (0.90 if keep_size else 0.66))
    glyph = _fitted(mask, box, keep_size)
    full = QImage(size, size, QImage.Format.Format_Grayscale8)
    full.fill(0)
    q = QPainter(full)
    q.drawImage(QPointF((size - box) / 2, (size - box) / 2), glyph)
    q.end()
    p.setOpacity(0.8)                                    # ombre portée courte et nette
    p.drawImage(QPointF(0, size / 34), _soft(_colorize(full, "#000000"), size / 22))
    p.setOpacity(1.0)
    p.drawImage(0, 0, _colorize(full, "#E9DCC0", "#FFFBF0"))            # dessin ivoire, léger dégradé
    p.setPen(QPen(QColor(0, 0, 0, 210), max(1.5, size / 34)))
    p.drawPath(shape)
    inner = QPainterPath()
    inset = size / 28
    inner.addRoundedRect(QRectF(1 + inset, 1 + inset, size - 2 - 2 * inset, size - 2 - 2 * inset), size * 0.07,
                         size * 0.07)
    shine = QLinearGradient(0, 0, 0, size)
    shine.setColorAt(0, QColor(255, 255, 255, 70))
    shine.setColorAt(1, QColor(255, 255, 255, 10))
    p.setPen(QPen(shine, max(1.0, size / 64)))
    p.drawPath(inner)
    if dim:                                              # indisponible : voile sombre
        p.fillPath(shape, QColor(0, 0, 0, 150))
    p.end()
    return QPixmap.fromImage(img)


@lru_cache(maxsize=4096)
def _render(body: str, category: str, size: int, theme_key: str, dim: bool) -> QPixmap:
    if not HAS_SVG:
        return QPixmap()
    keep = FIXED_SIZE_MARK in body
    mask = _glyph_mask(body, int(size * (0.90 if keep else 0.66)) * 2)
    return _paint_tile(mask, category_color(category), size, dim, keep)


@lru_cache(maxsize=512)
def tinted_stone_pixmap(mask_path: str, color: str, size: int, theme_key: str = "") -> QPixmap:
    """Icône d'après un masque en niveaux de gris (blanc = dessin) : classes, caractéristiques. Nom conservé pour
    compatibilité ; même rendu « carré peint sombre » que les autres icônes. Pixmap vide si le masque manque."""
    if not HAS_SVG:
        return QPixmap()
    m = QImage(mask_path)
    if m.isNull():
        return QPixmap()
    return _paint_tile(m.convertToFormat(QImage.Format.Format_Grayscale8), color, size, False, False)


masked_pixmap = tinted_stone_pixmap


def icon_pixmap(name: str, category: str, size: int = 56, dim: bool = False) -> QPixmap:
    """Icône nommée (data/icons) rendue dans le style de la catégorie et du thème courant."""
    return _render(named_body(name), category, size, theme.current().key, dim)


def spell_pixmap(db, spell_name: str, category: str = "", size: int = 56, dim: bool = False) -> QPixmap:
    """Icône unique d'un sort : couleur de son école (verte pour un sort de soins)."""
    from core import spell_icons as SI
    from core.rules import norm
    variant = ""
    if "#" in spell_name:                                # v53 : « Sort#effet » — tuile d'une variante du sort
        spell_name, variant = spell_name.split("#", 1)
    from core.art_finitions import SPELL_VARIANTS
    body = SPELL_VARIANTS[variant]() if variant in SPELL_VARIANTS else \
        (SI.spell_icon(db.spells, spell_name) or named_body("sort"))
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
    body = weapon_body(weapon_text) or named_body("attaque_generique")
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
