"""
Motifs de base soignés (v53) — remplacent les dessins au trait du registre core/action_icons.G et des effets de
sorts (core/spell_icons) : toutes les icônes COMPOSÉES (capacités, sorts sans dessin propre, historiques) en
profitent. Chaque motif occupe la grille 64 × 64 entière, centré ; blanc = dessin, noir = découpe. Deux motifs
différents ne se ressemblent jamais (les compositions restent uniques).
"""
from __future__ import annotations

import math

from .art_actions import book_open, bulb, door, figure, flask, lightning, note, sun_symbol, wind, wolf
from .art_armes import (Cc, G, K, L, P, R, S, blade_sword, boot, bubble, burst, crown, curved_arrow, dagger, eye,
                        fist, hand, hourglass, magnifier, shield, skull, slashes, spearhead, star4, target)
from .art_retouches import wolf_paw


def _flame():
    return (P("M32 60 C16 60 10 46 16 36 C18 42 22 44 23 41 C20 30 26 18 34 8 C34 18 40 24 42 32 C44 28 44 24 43 21 "
              "C52 30 52 46 46 53 C42 58 37 60 32 60 Z")
            + P("M32 54 C25 54 22 47 25 42 C27 46 30 46 31 43 C30 37 33 31 37 27 C37 33 41 37 41 43 C41 49 37 54 32 54 Z", K)
            + P("M32 50 C29 50 28 47 29 45 C30 47 31 47 32 45 C32 42 33 40 35 38 C35 41 37 43 37 45 C37 48 35 50 32 50 Z"))


def _snowflake():
    out = ""
    for k in range(6):
        a = math.radians(90 + 60 * k)
        ex, ey = 32 + 27 * math.cos(a), 32 - 27 * math.sin(a)
        bx, by = 32 + 15 * math.cos(a), 32 - 15 * math.sin(a)
        out += L([(32, 32), (ex, ey)], 4.4)
        for sg in (-1, 1):
            b = a + sg * math.radians(42)
            out += L([(bx, by), (bx + 9 * math.cos(b), by - 9 * math.sin(b))], 3.8)
    return out + Cc(32, 32, 7.5) + Cc(32, 32, 3.2, K)


def _drop():
    return (P("M32 4 C41 18 50 28 50 40 C50 52 42 60 32 60 C22 60 14 52 14 40 C14 28 23 18 32 4 Z")
            + P("M24 40 C24 46 28 51 33 52 C28 49 26 45 27 40 Z", K))


def _moon():
    return Cc(28, 34, 25) + Cc(40, 26, 21, K) + star4(50, 46, 5) + star4(56, 14, 3.4)


def _sun():
    return sun_symbol(32, 32, 1.05, False) + Cc(32, 32, 6, K) + Cc(32, 32, 3)


def _star():
    pts = []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        r = 28 if k % 2 == 0 else 12
        pts.append((32 + r * math.cos(a), 34 - r * math.sin(a)))
    return P("M" + " L".join("{:.1f} {:.1f}".format(*p) for p in pts) + " Z") + Cc(32, 33, 4.5, K)


def _sparkle():
    return star4(30, 34, 24) + star4(52, 12, 7) + star4(12, 12, 4)


def _wing():
    return (P("M6 58 C6 36 18 14 42 5 C51 2 57 2 60 4 C56 8 52 10 47 12 C53 12 57 13 60 15 C55 19 50 21 44 23 "
              "C49 24 53 26 55 28 C49 32 43 34 37 35 C41 37 43 39 44 41 C37 44 30 45 24 45 C19 49 13 54 6 58 Z")
            + S("M13 51 C22 42 32 34 45 22", 2.4, K) + S("M11 46 C20 38 30 28 44 14", 2.4, K)
            + S("M17 54 C26 48 32 44 40 38", 2.4, K))


def _spiral():
    pts = []
    for i in range(141):
        t = i / 140 * 3.6 * math.pi
        r = 1.5 + 1.95 * t
        pts.append((32 + r * math.cos(t), 32 + r * math.sin(t)))
    return L(pts, 5)


def _cycle():
    return (curved_arrow("M10 34 A22 22 0 0 1 50 18", (50, 18), 40, 6, 13)
            + curved_arrow("M54 30 A22 22 0 0 1 14 46", (14, 46), 220, 6, 13))


def _back():
    return curved_arrow("M52 52 V34 C52 20 42 14 30 14 H14", (8, 14), 180, 6.5, 14)


def _up():
    return R(26, 24, 12, 34, 4) + P("M32 4 L52 28 H12 Z")


def _chain():
    def link(cx, cy, a, open_=False):
        return ('<g transform="translate({} {}) rotate({})"><rect x="-12" y="-7" width="24" height="14" rx="7" '
                'fill="none" stroke="#FFFFFF" stroke-width="4.6"/></g>').format(cx, cy, a)
    return link(14, 50, -45) + link(25, 39, 45) + link(39, 25, -45) + link(50, 14, 45)


def _broken_chain():
    def link(cx, cy, a):
        return ('<g transform="translate({} {}) rotate({})"><rect x="-11" y="-6.5" width="22" height="13" rx="6.5" '
                'fill="none" stroke="#FFFFFF" stroke-width="4.4"/></g>').format(cx, cy, a)
    return link(14, 46, -35) + link(24, 36, 55) + link(40, 28, 55) + link(50, 18, -35) + burst(32, 32, 9, 7)


def _leaf():
    return (P("M10 56 C6 32 20 10 56 6 C58 30 44 54 18 56 Z")
            + L([(14, 52), (46, 18)], 2.6, K) + L([(24, 42), (24, 30)], 2, K) + L([(32, 34), (42, 34)], 2, K)
            + L([(30, 36), (30, 24)], 2, K))


def _mountain():
    return (P("M2 56 L20 24 L28 34 L40 10 L62 56 Z") + P("M40 10 L46 22 L42 26 L38 20 L34 24 Z", K)
            + P("M20 24 L24 32 L20 34 L17 30 Z", K))


def _wave():
    return (P("M4 46 C14 46 18 28 32 22 C44 18 56 26 58 36 C52 30 44 30 40 36 C36 42 44 48 52 46 C48 54 40 58 30 58 "
              "C18 58 8 54 4 46 Z") + S("M10 50 C18 50 24 38 34 32", 2, K))


def _portal():
    return ('<ellipse cx="32" cy="32" rx="20" ry="28" fill="#FFFFFF"/><ellipse cx="32" cy="32" rx="14" ry="22" '
            'fill="#000000"/>' + S("M32 18 C40 22 40 30 32 32 C24 34 24 42 32 46", 3) + star4(56, 10, 4) + star4(8, 54, 4))


def _mask():
    return (P("M4 22 C12 14 24 14 32 22 C40 14 52 14 60 22 C60 36 50 44 40 42 C36 41 34 38 32 36 C30 38 28 41 24 42 "
              "C14 44 4 36 4 22 Z")
            + '<ellipse cx="18" cy="27" rx="7" ry="4.4" fill="#000000"/><ellipse cx="46" cy="27" rx="7" ry="4.4" fill="#000000"/>'
            + L([(32, 42), (32, 58)], 3) + Cc(32, 58, 3))


def _brain():
    return G(
        P("M0 -20 C-6 -24 -16 -22 -19 -14 C-26 -12 -28 -2 -23 4 C-26 10 -20 18 -12 17 C-8 22 -2 21 0 18 "
          "C2 21 8 22 12 17 C20 18 26 10 23 4 C28 -2 26 -12 19 -14 C16 -22 6 -24 0 -20 Z")
        + L([(0, -18), (0, 16)], 2.2, K) + S("M-6 -14 C-12 -12 -10 -6 -16 -4", 2, K) + S("M-4 2 C-10 0 -14 6 -18 6", 2, K)
        + S("M6 -14 C12 -12 10 -6 16 -4", 2, K) + S("M4 2 C10 0 14 6 18 6", 2, K), 32, 32, 0, 1.25)


def _alert():
    return R(26, 4, 12, 38, 6) + Cc(32, 54, 7)


def _arrow_diag():
    return (L([(10, 54), (46, 18)], 5) + P("M56 8 L50 30 L34 14 Z")
            + P("M10 54 L6 44 L12 42 L16 50 Z") + P("M10 54 L20 58 L22 52 L14 48 Z"))


def _arrows():
    return "".join(L([(x, 56), (x + 26, 30)], 3.6) + P("M{} {} l-3 9 l-6 -6 Z".format(x + 30, 26)) for x in (6, 18, 30))


def _bow():
    return (S("M14 4 C44 14 44 50 14 60", 5) + L([(14, 4), (14, 60)], 2) + L([(6, 32), (52, 32)], 3.6)
            + P("M60 32 L50 26 L50 38 Z") + P("M6 32 l-4 -5 h4 l5 5 l-5 5 h-4 Z"))


def _crossbow():
    return (S("M8 22 Q32 6 56 22", 5) + L([(8, 22), (32, 30), (56, 22)], 1.8)
            + R(28, 12, 8, 46, 3) + P("M26 46 H38 L36 60 H28 Z") + L([(32, 6), (32, 28)], 2.6, K))


def _hammer():
    return G(R(-2.6, -14, 5.2, 40, 2.6) + R(-14, -26, 28, 16, 3) + L([(-8, -26), (-8, -10)], 1.8, K)
             + L([(8, -26), (8, -10)], 1.8, K), 32, 34, 40, 1.0)


def _axe():
    return G(R(-2.6, -26, 5.2, 54, 2.6) + P("M2 -24 C14 -28 22 -20 24 -8 C22 2 14 6 2 2 Z"), 30, 32, 35, 1.0)


def _spear():
    return G(R(-2.4, -14, 4.8, 44, 2.4) + spearhead(18, 11).replace('d="', 'transform="translate(0 -14)" d="'), 32, 32, 45, 1.0)


def _sword():
    return G(blade_sword(34, 9, 22, 10, 4), 32, 32, 45, 1.0)


def _dagger():
    return dagger(32, 32, 45, 1.25)


def _ring():
    return ('<circle cx="32" cy="38" r="18" fill="none" stroke="#FFFFFF" stroke-width="7"/>'
            + P("M32 4 L42 16 L32 26 L22 16 Z") + P("M22 16 H42 L32 4 Z", K).replace('fill="#000000"',
                                                                                    'fill="none" stroke="#000000" stroke-width="1.6"'))


def _amulet():
    return (S("M14 6 C14 24 24 30 32 30 C40 30 50 24 50 6", 3) + Cc(32, 42, 15) + Cc(32, 42, 9, K) + star4(32, 42, 7))


def _wand():
    return G(R(-3, -24, 6, 46, 3) + R(-3, -24, 6, 8, 1, K) + R(-2, -23, 4, 6, 1), 24, 38, 40) + star4(46, 16, 12) + star4(56, 36, 4)


def _cape():
    return (P("M22 6 H42 L46 14 C54 30 58 46 60 58 C50 54 42 58 32 54 C22 58 14 54 4 58 C6 46 10 30 18 14 Z")
            + Cc(32, 10, 4, K) + S("M24 18 C22 32 20 44 18 54", 2, K) + S("M40 18 C42 32 44 44 46 54", 2, K))


def _helm():
    return (P("M32 4 C48 4 56 16 56 32 V50 L42 58 V40 H22 V58 L8 50 V32 C8 16 16 4 32 4 Z")
            + R(14, 28, 36, 5, 1, K) + R(29, 4, 6, 24, 0, K))


def _armor():
    return (P("M14 8 L24 6 C26 12 38 12 40 6 L50 8 L58 20 L50 26 L48 54 C40 60 24 60 16 54 L14 26 L6 20 Z")
            + L([(32, 14), (32, 54)], 2.2, K) + S("M20 30 C26 34 38 34 44 30", 2.2, K) + S("M20 40 C26 44 38 44 44 40", 2.2, K))


def _gem():
    return (P("M16 10 H48 L60 26 L32 58 L4 26 Z") + L([(4, 26), (60, 26)], 2, K) + L([(16, 10), (24, 26), (32, 58)], 2, K)
            + L([(48, 10), (40, 26), (32, 58)], 2, K) + L([(32, 10), (24, 26)], 1.6, K) + L([(32, 10), (40, 26)], 1.6, K))


def _diamond_burst():
    return burst(32, 32, 28, 8) + P("M32 18 L42 32 L32 46 L22 32 Z", K) + P("M32 24 L37 32 L32 40 L27 32 Z")


def _torch():
    return (G(P("M-6 0 H6 L3 28 H-3 Z"), 30, 30, 15) + R(18, 26, 22, 6, 2)
            + P("M30 26 C20 26 16 16 22 8 C23 12 26 13 27 11 C25 6 28 2 32 0 C32 6 36 8 38 13 C39 11 39 9 39 7 "
                "C44 12 44 22 38 25 Z"))


def _scroll():
    return (R(10, 12, 44, 40, 2) + Cc(10, 18, 7) + Cc(54, 46, 7) + R(10, 11, 6, 14, 0)
            + "".join(L([(18, y), (46, y)], 2.2, K) for y in (22, 30, 38, 44)) + Cc(10, 18, 3, K) + Cc(54, 46, 3, K))


def _web():
    return ('<g fill="none" stroke="#FFFFFF" stroke-width="2.4">' + "".join(
        '<line x1="32" y1="32" x2="{:.1f}" y2="{:.1f}"/>'.format(32 + 30 * math.cos(a), 32 + 30 * math.sin(a))
        for a in [k * math.pi / 4 + math.pi / 8 for k in range(8)])
        + "".join('<circle cx="32" cy="32" r="{}"/>'.format(r) for r in (9, 18, 27)) + "</g>"
        + '<ellipse cx="32" cy="34" rx="6" ry="8" fill="#FFFFFF"/>' + Cc(32, 24, 4))


def _tentacles():
    return (S("M12 60 C10 44 22 40 18 26 C16 18 22 12 28 14", 6) + S("M32 60 C32 46 40 40 38 26 C37 18 44 10 50 14", 6)
            + S("M50 60 C52 50 58 46 58 38", 5) + Cc(28, 14, 3) + Cc(50, 14, 3))


def _meteors():
    def m(x, y, s):
        return G(P("M0 -7 C5 -7 8 -4 8 0 C8 4 5 7 0 7 L-24 2 L-24 -2 Z"), x, y, 135, s)
    return m(46, 18, 1.1) + m(26, 30, 0.9) + m(48, 44, 0.8)


def _fog():
    return (S("M6 20 H40 C46 20 48 12 42 10", 4.4) + S("M10 32 H54", 4.4) + S("M4 44 H34", 4.4) + S("M40 44 H58", 4.4)
            + S("M14 56 H50", 4.4))


def _stones():
    return (P("M8 56 L14 40 L30 36 L36 50 L28 58 Z") + P("M34 56 L38 42 L52 38 L60 52 L52 58 Z")
            + P("M18 34 L24 18 L40 14 L46 28 L34 34 Z") + L([(18, 46), (28, 44)], 1.8, K) + L([(26, 24), (38, 22)], 1.8, K))


def _tremor():
    return (P("M2 52 H62 V60 H2 Z") + L([(10, 52), (18, 42), (24, 48), (32, 34), (40, 46), (46, 40), (54, 52)], 3.4, K)
                                    + L([(14, 30), (14, 18)], 3) + L([(32, 22), (32, 6)], 3) + L([(50, 30), (50, 18)], 3)
                                    + P("M10 24 L14 16 L18 24 Z") + P("M28 12 L32 4 L36 12 Z") + P("M46 24 L50 16 L54 24 Z"))


def _waves():
    return (S("M16 10 C26 22 26 42 16 54", 5.4) + S("M30 6 C42 20 42 44 30 58", 4.6) + S("M44 4 C58 20 58 44 44 60", 3.8)
            + burst(8, 32, 7, 7))


def _ondes():
    return ('<circle cx="32" cy="32" r="8" fill="#FFFFFF"/>'
            + "".join('<circle cx="32" cy="32" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(r, w)
                      for r, w in ((16, 4), (24, 3.4))))


def _breath():
    """Souffle de dragon : gueule de profil à gauche, cône de flammes qui s'évase vers la droite."""
    head = P("M2 30 C4 22 12 18 20 20 L26 14 L26 22 C30 24 32 28 32 32 L24 34 L30 38 C26 42 18 42 12 40 C6 38 2 34 2 30 Z")
    eye = P("M14 24 L20 25 L15 28 Z", K)
    cone = P("M30 32 L62 12 C60 18 58 22 62 26 C56 28 54 32 62 38 C56 40 58 46 62 52 Z")
    tongues = P("M36 32 L54 22 C52 26 52 30 56 32 C52 34 52 38 54 42 Z", K)
    return head + eye + cone + tongues


def _claws():
    return slashes(32, 32, 1.0)


def _cible():
    return target(32, 32, 1.15)


def _soin():
    return (
        P("M32 58 C14 45 6 35 6 24 C6 15 13 9 21 9 C26 9 30 12 32 16 C34 12 38 9 43 9 C51 9 58 15 58 24 C58 35 50 45 32 58 Z")
        + '<path d="M32 21 V43 M21 32 H43" stroke="#000000" stroke-width="7" stroke-linecap="round"/>')


def _heart():
    return (P("M32 58 C14 45 6 35 6 24 C6 15 13 9 21 9 C26 9 30 12 32 16 C34 12 38 9 43 9 C51 9 58 15 58 24 C58 35 50 45 32 58 Z")
            + P("M18 20 C14 22 13 27 15 31 C15 26 17 23 21 21 Z", K))


def _plus():
    return R(24, 6, 16, 52, 5) + R(6, 24, 52, 16, 5)


def _dodge():
    return figure(26, 34, 1.15, -30) + S("M46 16 C54 26 54 42 46 52", 3.6) + S("M54 12 C62 24 62 44 54 56", 3)


def _beast():
    return wolf(32, 32, 1.15)


def _mace():
    spikes = "".join(G(P("M0 -16 L3.4 -8 L-3.4 -8 Z"), 0, -16, a) for a in range(0, 360, 45))
    return G(R(-2.8, -6, 5.6, 34, 2.8) + Cc(0, -16, 10.5) + spikes + Cc(0, 29, 3.6), 32, 30, 35, 1.0)


def _tool():
    wrench = G(R(-4, -6, 8, 32, 4) + Cc(0, -12, 11) + R(-4.5, -26, 9, 14, 0, K) + Cc(0, 26, 6) + Cc(0, 26, 2.6, K), 22, 32, -40, 0.95)
    return wrench + G(R(-2.6, -8, 5.2, 34, 2.6) + R(-12, -18, 24, 11, 3), 42, 34, 40, 0.95)


def _rune():
    return (P("M32 4 L56 18 V46 L32 60 L8 46 V18 Z") + P("M32 10 L50 21 V43 L32 54 L14 43 V21 Z", K)
            + L([(32, 16), (32, 48)], 4.4) + L([(32, 24), (42, 18)], 4.4) + L([(32, 32), (22, 26)], 4.4)
            + L([(32, 40), (42, 34)], 4.4))


def _glyph():
    return ('<circle cx="32" cy="32" r="26" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
            + P("M32 10 L51 43 H13 Z") + P("M32 20 L44 40 H20 Z", K) + Cc(32, 33, 4.5))


MOTIFS = {
    "masse": _mace, "outil": _tool, "rune": _rune, "glyphe": _glyph,
    "flamme": _flame, "flocon": _snowflake, "eclair": lambda: lightning(32, 32, 1.05), "goutte": _drop,
    "crane": lambda: skull(32, 30, 1.25), "coeur": _heart, "oeil": lambda: eye(32, 32, 1.05),
    "oeil_clos": lambda: eye(32, 30, 1.1, True), "main": lambda: hand(32, 34, 1.1, 0), "poing": lambda: fist(32, 34, 1.2),
    "bouclier": lambda: shield(32, 32, 1.15), "soleil": _sun, "etoile": _star, "eclat": _sparkle, "lune": _moon,
    "cerveau": _brain, "patte": lambda: wolf_paw(32, 34, 1.1), "note": lambda: note(32, 32, 1.15),
    "masque": _mask, "feuille": _leaf, "livre": lambda: book_open(32, 34, 1.0), "epee": _sword, "dague": _dagger,
    "hache": _axe, "marteau": _hammer, "arc": _bow, "arbalete": _crossbow, "lance": _spear, "fiole": lambda: flask(32, 32, 1.15),
    "parchemin": _scroll, "anneau": _ring, "couronne": lambda: crown(32, 32, 1.15), "cible": _cible, "chaine": _chain,
    "chaine_brisee": _broken_chain, "sablier": lambda: hourglass(32, 32, 1.1), "botte": lambda: boot(32, 30, 1.15),
    "aile": _wing, "spirale": _spiral, "vent": lambda: wind(32, 32, 1.15), "vague": _wave, "terre": _tremor,
    "pierres": _stones, "toile": _web, "griffes": _claws, "bulle": lambda: bubble(32, 32, 1.0), "porte": lambda: door(32, 32, 1.1),
    "loupe": lambda: magnifier(32, 32, 1.25), "portail": _portal, "cycle": _cycle, "retour": _back,
    "fleche_haut": _up, "fleche": _arrow_diag, "fleches": _arrows, "alerte": _alert, "explosion": lambda: burst(32, 32, 28, 10),
    "souffle": _breath, "tentacules": _tentacles, "meteores": _meteors, "brume": _fog, "ondes": _ondes,
    "diamant": _diamond_burst, "gemme": _gem, "amulette": _amulet, "baguette": _wand, "cape": _cape, "casque": _helm,
    "armure": _armor, "torche": _torch, "ampoule": lambda: bulb(32, 32, 1.15), "soin": _soin, "plus": _plus,
    "esquive": _dodge, "bete": _beast,
}
