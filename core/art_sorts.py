"""Dessins soignés (v53) des sorts les plus courants — grille 64 × 64, géométrie symétrique, trait unique de 4 px,
courbes régulières, découpes noires franches. Blanc = dessin, noir = découpe."""
from __future__ import annotations

import math

W, K = "#FFFFFF", "#000000"


def path(d, col=W):
    return '<path d="{}" fill="{}"/>'.format(d, col)


def circ(cx, cy, r, col=W):
    return '<circle cx="{:g}" cy="{:g}" r="{:g}" fill="{}"/>'.format(cx, cy, r, col)


def line(pts, w=4.0, col=W):
    d = "M" + " L".join("{:g} {:g}".format(x, y) for x, y in pts)
    return '<path d="{}" fill="none" stroke="{}" stroke-width="{}" stroke-linecap="round" stroke-linejoin="round"/>'.format(
        d, col, w)


def curve(d, w=4.0, col=W):
    return '<path d="{}" fill="none" stroke="{}" stroke-width="{}" stroke-linecap="round" stroke-linejoin="round"/>'.format(
        d, col, w)


def star4(cx, cy, r, col=W):
    q = r * 0.26
    pts = [(cx, cy - r), (cx + q, cy - q), (cx + r, cy), (cx + q, cy + q), (cx, cy + r), (cx - q, cy + q),
           (cx - r, cy), (cx - q, cy - q)]
    return path("M" + " L".join("{:g} {:g}".format(x, y) for x, y in pts) + " Z", col)


def rot(svg, a, cx=32, cy=32):
    return '<g transform="rotate({} {} {})">{}</g>'.format(a, cx, cy, svg)


# ------------------------------------------------------------------------------------------------ sorts
def boule_de_feu():
    outer = ("M25 59 C14 59 6 51 6 41 C6 32 11 25 19 22 C18 26 19 29 21 31 C23 22 30 14 41 9 C38 15 38 19 40 22 "
             "C44 15 51 11 59 10 C54 16 52 21 52 26 C55 25 58 26 60 27 C55 31 53 36 52 42 C50 52 39 59 25 59 Z")
    inner = ("M26 53 C19 53 13 48 13 41 C13 36 15 32 19 30 C19 34 21 36 24 37 C25 32 29 27 35 24 C34 28 35 31 38 33 "
             "C40 30 43 29 46 29 C44 32 44 36 45 39 C45 47 37 53 26 53 Z")
    return path(outer) + path(inner, K) + circ(27, 44, 6.5)


def eclair():
    bolt = "M38 3 L14 36 L29 36 L23 61 L50 25 L35 25 L45 3 Z"
    return path(bolt) + star4(10, 12, 5) + star4(55, 52, 4)


def bouclier():
    outer = "M32 5 L54 12 V30 C54 45 45 54 32 60 C19 54 10 45 10 30 V12 Z"
    ring = "M32 11 L49 16.5 V30 C49 41.5 42 49 32 54 C22 49 15 41.5 15 30 V16.5 Z"
    inner = "M32 15 L45 19.5 V30 C45 39 39.5 45.5 32 49.5 C24.5 45.5 19 39 19 30 V19.5 Z"
    return path(outer) + path(ring, K) + path(inner) + star4(32, 31, 12, K)


def soins():
    heart = ("M32 57 C14 44 6 34 6 23 C6 14 13 8 21 8 C26 8 30 11 32 15 C34 11 38 8 43 8 C51 8 58 14 58 23 "
             "C58 34 50 44 32 57 Z")
    cross = '<path d="M32 20 V42 M21 31 H43" stroke="#000000" stroke-width="7" stroke-linecap="round"/>'
    return path(heart) + cross


def rayon_de_givre():
    out = ""
    for k in range(6):
        a = math.radians(90 + 60 * k)
        ex, ey = 32 + 26 * math.cos(a), 32 - 26 * math.sin(a)
        bx, by = 32 + 15 * math.cos(a), 32 - 15 * math.sin(a)
        out += line([(32, 32), (ex, ey)], 4.2)
        for s in (-1, 1):
            b = a + s * math.radians(42)
            out += line([(bx, by), (bx + 9 * math.cos(b), by - 9 * math.sin(b))], 3.6)
    return out + circ(32, 32, 7.5) + circ(32, 32, 3.2, K)


def projectile_magique():
    def dart(x, y, s):
        d = "M0 -15 L5.5 -4 L1.8 -5 L1.8 12 L0 15 L-1.8 12 L-1.8 -5 L-5.5 -4 Z"
        return '<path transform="translate({} {}) rotate(45) scale({})" d="{}" fill="#FFFFFF"/>'.format(x, y, s, d)
    return dart(38, 24, 1.6) + dart(20, 30, 1.3) + dart(42, 44, 1.3) + star4(54, 9, 4.5) + star4(10, 54, 4)


def sommeil():
    moon = circ(27, 36, 21) + circ(36, 28, 18, K)
    zz = (line([(38, 8), (50, 8), (38, 20), (50, 20)], 3.8) + line([(46, 30), (55, 30), (46, 39), (55, 39)], 3.2))
    return moon + zz + star4(52, 52, 4)


def detection_magie():
    eye = path("M3 34 C14 19 50 19 61 34 C50 49 14 49 3 34 Z")
    iris = circ(32, 34, 12, K) + circ(32, 34, 8.5) + path("M32 28 L34.5 34 L32 40 L29.5 34 Z", K)
    rays = "".join(rot(line([(32, 4), (32, 11)], 3.6), a, 32, 34) for a in (-56, -28, 0, 28, 56))
    return rays + eye + iris


def toile():
    legs = ""
    for s in (-1, 1):
        for y0, dx, dy, ex, ey in ((25, 12, -10, 18, -18), (29, 15, -3, 24, -2), (33, 15, 4, 23, 12), (37, 12, 10, 16, 22)):
            legs += curve("M{} {} Q{} {} {} {}".format(32 + s * 5, y0, 32 + s * dx, y0 + dy, 32 + s * ex, y0 + ey), 3.4)
    body = '<ellipse cx="32" cy="41" rx="9.5" ry="12" fill="#FFFFFF"/>' + circ(32, 24, 6.5)
    mark = path("M32 35 L35 40 L32 45 L29 40 Z", K)
    return legs + body + mark


def invisibilite():
    head = circ(32, 15, 8)
    body = path("M14 44 C14 31 22 26 32 26 C42 26 50 31 50 44 Z")
    cuts = "".join(line([(10, y), (54, y)], 2.6, K) for y in (35, 41))
    fade = (line([(18, 49), (46, 49)], 3.6) + line([(22, 55), (30, 55)], 3.2) + line([(36, 55), (42, 55)], 3.2)
            + line([(28, 60.5), (34, 60.5)], 2.8))
    return head + body + cuts + fade + star4(53, 11, 4.5) + star4(11, 22, 3)


def vol():
    wing = ("M8 56 C8 36 20 15 42 6 C51 3 57 3 60 5 C56 9 52 11 47 13 C53 13 57 14 60 16 C55 20 50 22 44 24 "
            "C49 25 53 27 55 29 C49 33 43 35 37 36 C41 38 43 40 44 42 C37 45 30 46 24 46 C19 50 14 54 8 56 Z")
    cuts = (curve("M15 47 C24 38 34 30 46 23", 2.4, K) + curve("M19 42 C27 35 36 30 45 24", 0.1, K)
            + curve("M13 52 C22 46 30 41 39 36", 2.4, K) + curve("M18 38 C28 28 38 20 50 13", 2.4, K))
    return path(wing) + cuts + star4(54, 52, 4.5)


def flamme_sacree():
    outer = ("M32 3 C35 13 47 20 47 35 C47 46 40 53 32 53 C24 53 17 46 17 35 C17 27 21 22 24 16 C26 22 28 24 30 25 "
             "C29 17 29 10 32 3 Z")
    inner = "M32 22 C34 29 41 33 41 40 C41 45 37 48 32 48 C27 48 23 45 23 40 C23 34 29 30 32 22 Z"
    return path(outer) + path(inner, K) + path("M32 33 C33 37 36 39 36 42 C36 44 34 45 32 45 C30 45 28 44 28 42 "
                                                   "C28 39 31 37 32 33 Z") + line([(16, 59), (48, 59)], 4)


def charme():
    heart = ("M32 57 C14 44 6 34 6 23 C6 14 13 8 21 8 C26 8 30 11 32 15 C34 11 38 8 43 8 C51 8 58 14 58 23 "
             "C58 34 50 44 32 57 Z")
    pts = []
    for i in range(0, 121):
        t = i / 120 * 3.2 * math.pi
        r = 1.0 + 1.55 * t
        pts.append((32 + r * math.cos(t), 30 + r * math.sin(t)))
    return path(heart) + line(pts, 3.2, K)


def mot_de_guerison():
    bubble = path("M14 6 H50 C55 6 58 9 58 14 V36 C58 41 55 44 50 44 H28 L14 57 V44 C9 44 6 41 6 36 V14 C6 9 9 6 14 6 Z")
    cross = '<path d="M32 15 V35 M22 25 H42" stroke="#000000" stroke-width="6.5" stroke-linecap="round"/>'
    return bubble + cross


SPELLS = {"Boule de feu": boule_de_feu, "Projectile magique": projectile_magique, "Soins": soins,
          "Bouclier": bouclier, "Éclair": eclair, "Rayon de givre": rayon_de_givre, "Toile d'araignée": toile,
          "Sommeil": sommeil, "Invisibilité": invisibilite, "Mot de guérison": mot_de_guerison,
          "Flamme sacrée": flamme_sacree, "Charme-personne": charme, "Détection de la magie": detection_magie,
          "Vol": vol}


# ================================================================================================ v53 : lot 2
# Tours de magie — mêmes règles : silhouettes pleines, découpes noires franches, éclats discrets.
from .art_armes import (Cc as _C, G as _G, K as _K, L as _L, P as _P, R as _R, S as _S, arrow as _arrow,  # noqa: E402
                        blade_sword as _blade, burst as _burst, curved_arrow as _carrow, over as _over,
                        shield as _shield, skull as _skull, speed as _speed, star4 as _star)
from .art_actions import (eye as _eye, flask as _flask, hand as _hand, heart as _heart, lightning as _bolt,  # noqa: E402
                          sun_symbol as _sun, wind as _wind)


def _flame(x=32, y=32, s=1.0):
    d = ("M0 22 C-14 22 -18 8 -12 -2 C-10 4 -6 6 -5 3 C-8 -8 -2 -18 4 -26 C4 -16 10 -12 12 -4 "
         "C14 -8 14 -12 13 -15 C20 -6 20 6 16 13 C13 19 7 22 0 22 Z")
    return _G(_P(d), x, y, 0, s)


def _flame_cut(x=32, y=32, s=1.0):
    return _flame(x, y, s) + _G(_P("M0 18 C-7 18 -9 11 -6 6 C-4 10 -1 10 0 7 C-1 2 2 -4 5 -8 C5 -2 9 2 9 8 "
                                   "C9 14 5 18 0 18 Z", _K), x, y, 0, s)


def _drop(x=32, y=32, s=1.0):
    return _G(_P("M0 -24 C8 -12 16 -2 16 8 C16 18 9 24 0 24 C-9 24 -16 18 -16 8 C-16 -2 -8 -12 0 -24 Z"), x, y, 0, s)


def _cloud(x=32, y=32, s=1.0):
    return _G(_P("M-22 14 C-30 14 -32 2 -24 -2 C-26 -12 -14 -18 -6 -12 C-2 -22 16 -22 18 -8 C28 -10 32 4 24 10 "
                 "C26 14 22 16 18 16 H-20 C-21 16 -22 15 -22 14 Z"), x, y, 0, s)


def _orb(x, y, r):
    return _C(x, y, r) + _C(x - r * 0.3, y - r * 0.3, r * 0.28, _K)


def _snowflake(x=32, y=32, s=1.0):
    out = ""
    for k in range(6):
        a = math.radians(90 + 60 * k)
        ex, ey = 26 * math.cos(a), -26 * math.sin(a)
        bx, by = 15 * math.cos(a), -15 * math.sin(a)
        out += _L([(0, 0), (ex, ey)], 4.2)
        for sg in (-1, 1):
            b = a + sg * math.radians(42)
            out += _L([(bx, by), (bx + 9 * math.cos(b), by - 9 * math.sin(b))], 3.6)
    return _G(out + _C(0, 0, 7) + _C(0, 0, 3, _K), x, y, 0, s)


def _mask_face(x=32, y=32, s=1.0, smile=True):
    face = _P("M0 -24 C14 -24 22 -16 22 -2 C22 14 12 24 0 24 C-12 24 -22 14 -22 -2 C-22 -16 -14 -24 0 -24 Z")
    eyes = _P("M-14 -6 Q-9 -12 -4 -6 Q-9 -3 -14 -6 Z", _K) + _P("M14 -6 Q9 -12 4 -6 Q9 -3 14 -6 Z", _K)
    mouth = (_P("M-11 6 Q0 18 11 6 Q0 11 -11 6 Z", _K) if smile else _P("M-10 13 Q0 3 10 13 Q0 9 -10 13 Z", _K))
    return _G(face + eyes + mouth, x, y, 0, s)


def _rings(x, y, radii, w=3.2):
    return "".join('<circle cx="{}" cy="{}" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(x, y, r, w)
                   for r in radii)


def _bug(x, y, s=1.0, a=0):
    body = '<ellipse cx="0" cy="3" rx="5" ry="7" fill="#FFFFFF"/>' + _C(0, -6, 3.6)
    legs = "".join(_L([(sx * 3, yy), (sx * 9, yy + d)], 1.8) for sx in (-1, 1) for yy, d in ((-1, -4), (3, 0), (7, 4)))
    return _G(body + legs + _L([(0, 0), (0, 9)], 1.2, _K), x, y, a, s)


def _bell(x=32, y=32, s=1.0):
    return _G(_P("M0 -24 C4 -24 6 -21 6 -18 C14 -15 18 -6 18 6 L22 14 H-22 L-18 6 C-18 -6 -14 -15 -6 -18 C-6 -21 -4 -24 0 -24 Z")
              + _C(0, 20, 5) + _L([(-14, 8), (14, 8)], 2, _K), x, y, 0, s)


def _vine(d, w=5):
    return _S(d, w)


def _thorns(points):
    return "".join(_G(_P("M0 -7 L3 0 L-3 0 Z"), x, y, a) for x, y, a in points)


CANTRIPS = {
    "Amis": lambda: _over(_mask_face(30, 34, 1.05), _star(52, 12, 8)) + _star(12, 12, 4),
    "Aspersion d'acide": lambda: _flask(24, 30, 0.85, -40) + _drop(46, 34, 0.32) + _drop(54, 48, 0.26)
                                 + _drop(40, 52, 0.22) + _drop(56, 24, 0.18),
    "Assistance": lambda: _over(_hand(30, 44, 0.8, 0), _star(32, 14, 11)) + _star(52, 24, 4) + _star(12, 22, 3.5),
    "Bouffée de poison": lambda: _cloud(32, 26, 1.05) + _G(_P("M0 -9 C6 -9 9 -5 9 0 C9 4 7 6 6 7 V10 H-6 V7 C-7 6 -9 4 -9 0 "
                                                             "C-9 -5 -6 -9 0 -9 Z", _K) + _C(-3.5, 0, 2.2) + _C(3.5, 0, 2.2), 32, 28, 0, 1.0)
                                 + _C(18, 50, 3.4) + _C(28, 56, 2.6) + _C(42, 52, 3) + _C(50, 58, 2),
    "Contact glacial": lambda: _over(_hand(28, 38, 0.9, 0), _snowflake(50, 14, 0.42))
                               + "".join(_R(x, y, 2.6, 7, 1.3, _K) for x, y in ((17.5, 26), (23.3, 22), (29.1, 22), (34.9, 25),
                                                                                 (17.5, 36), (23.3, 33), (29.1, 33), (34.9, 35))),
    "Contrôle des flammes": lambda: _over(_flame_cut(32, 34, 0.95), _carrow("M10 22 C8 44 22 58 40 58", (40, 58), 0, 3.2)
                                          + _carrow("M54 42 C56 20 42 6 24 6", (24, 6), 180, 3.2)),
    "Coup au but": lambda: _over(_rings(32, 32, (24, 15), 4.4), _eye(32, 32, 0.42)),
    "Coup de tonnerre": lambda: _burst(32, 32, 14, 8) + _rings(32, 32, (20, 27), 3),
    "Druidisme": lambda: _R(30, 30, 4.4, 28, 2) + _P("M32 34 C22 34 10 28 8 14 C22 14 30 22 32 34 Z")
                         + _P("M32 26 C40 24 52 18 56 4 C42 4 34 12 32 26 Z") + _star(52, 50, 4.5) + _star(14, 46, 3.5),
    "Décharge occulte": lambda: _P("M6 58 L22 40 L18 36 L36 22 L32 18 L58 6 L40 26 L44 30 L26 44 L30 48 Z")
                                + _C(12, 52, 7) + _C(12, 52, 3.2, _K) + _burst(56, 8, 9, 8) + _star(48, 50, 4),
    "Embrasement": lambda: _flame_cut(32, 26, 0.9) + _G(_R(-24, -3, 48, 6, 3), 32, 52, 15) + _G(_R(-24, -3, 48, 6, 3), 32, 52, -15),
    "Façonnage de l'eau": lambda: _S("M6 26 C14 18 22 18 30 26 C38 34 46 34 58 24", 5) + _S("M6 40 C14 32 22 32 30 40 C38 48 46 48 58 38", 5)
                                  + _drop(48, 12, 0.3) + _star(14, 54, 4),
    "Façonnage de la terre": lambda: _P("M4 56 L18 30 L26 40 L38 14 L60 56 Z") + _P("M38 14 L44 26 L40 30 L36 24 Z", _K)
                                     + _P("M18 30 L22 38 L18 40 Z", _K) + _star(52, 12, 5),
    "Ferrage foudroyant": lambda: _bolt(22, 30, 0.9) + _S("M34 46 C44 52 54 48 56 38 C57 30 50 28 48 34", 4) + _P("M46 31 L52 30 L48 37 Z"),
    "Flammes": lambda: _over(_hand(32, 46, 0.75, 0), _flame_cut(32, 20, 0.62)),
    "Fouet épineux": lambda: _vine("M8 56 C16 40 34 46 40 30 C44 20 54 18 56 8", 4.4)
                             + _thorns(((14, 47, -40), (24, 44, 30), (34, 42, -30), (40, 30, 60), (46, 22, -10), (53, 15, 40))),
    "Gelure": lambda: _snowflake(30, 34, 0.95) + _drop(52, 14, 0.28),
    "Glas": lambda: _over(_bell(32, 30, 1.0), _skull(32, 26, 0.38).replace('fill="#FFFFFF"', 'fill="#000000"', 1))
                    + _S("M6 14 C2 22 2 30 6 38", 2.8) + _S("M58 14 C62 22 62 30 58 38", 2.8),
    "Gourdin magique": lambda: _G(_P("M-3 24 L-7 -16 C-7 -26 7 -26 7 -16 L3 24 Z") + _R(-4, 20, 8, 6, 2), 30, 34, 30, 1.05)
                               + _P("M44 10 C52 6 58 10 58 16 C52 18 46 16 44 10 Z") + _star(14, 14, 5) + _star(54, 44, 4),
    "Illusion mineure": lambda: _over(_mask_face(32, 32, 1.0), _star(50, 50, 6))
                                + '<circle cx="32" cy="32" r="29" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-dasharray="4 5"/>',
    "Infestation": lambda: _bug(22, 22, 1.1, -20) + _bug(42, 18, 0.9, 30) + _bug(36, 42, 1.2, 10) + _bug(16, 46, 0.8, -50) + _bug(52, 44, 0.75, 70),
    "Lame aux flammes vertes": lambda: _over(_G(_blade(30, 8.5, 20, 9, 3.6), 24, 40, 45, 1.0), _flame(46, 20, 0.55)),
    "Lame retentissante": lambda: _over(_rings(42, 22, (14, 21), 2.8), _G(_blade(30, 8.5, 20, 9, 3.6), 26, 38, 45, 1.0)),
    "Lumière": lambda: _sun(32, 32, 1.05, False) + _C(32, 32, 6, _K) + _C(32, 32, 3),
    "Lumières dansantes": lambda: _orb(16, 18, 6) + _orb(44, 14, 7) + _orb(26, 44, 7) + _orb(50, 44, 5.5)
                                  + _S("M16 26 C18 34 22 36 26 36", 2) + _S("M44 22 C44 30 48 34 50 38", 2),
    "Main de mage": lambda: _over(_hand(32, 34, 1.0, 0), _star(54, 12, 6))
                            + '<path d="M8 58 C14 54 20 58 26 54 C32 58 38 54 44 58 C50 54 56 58 60 54" fill="none" '
                              'stroke="#FFFFFF" stroke-width="2.6" stroke-dasharray="3 3"/>',
    "Message": lambda: _over(_P("M8 14 H44 C48 14 50 16 50 20 V34 C50 38 48 40 44 40 H24 L14 50 V40 H8 C4 40 2 38 2 34 V20 "
                                "C2 16 4 14 8 14 Z"), _C(16, 27, 3, _K) + _C(26, 27, 3, _K) + _C(36, 27, 3, _K))
                       + _S("M54 30 C58 34 58 42 54 46", 2.8) + _S("M58 24 C64 32 64 44 58 52", 2.4),
    "Moquerie cruelle": lambda: _over(_mask_face(28, 34, 0.95, False), _bolt(52, 16, 0.42)) + _bolt(10, 12, 0.3),
    "Mot de radiance": lambda: _over("".join(_G(_P("M-2.4 -30 L2.4 -30 L1.4 -20 L-1.4 -20 Z"), 32, 32, a) for a in range(0, 360, 30)),
                                     _P("M18 18 H46 C49 18 50 20 50 23 V37 C50 40 49 42 46 42 H30 L22 50 V42 H18 C15 42 14 40 14 37 "
                                        "V23 C14 20 15 18 18 18 Z")) + _star(32, 30, 6, _K),
    "Pierre magique": lambda: _G(_P("M-10 -14 L8 -16 L18 -4 L14 12 L-4 16 L-16 6 Z") + _P("M-10 -14 L0 -4 L18 -4", _K)
                                 .replace('fill="#000000"', 'fill="none" stroke="#000000" stroke-width="2"'), 30, 36, 0, 1.15)
                              + _star(52, 12, 7) + _star(12, 14, 4),
    "Piqûre mentale": lambda: _G(_P("M-20 4 C-24 -8 -16 -20 -4 -20 C0 -24 10 -24 14 -18 C22 -16 26 -6 22 2 C24 10 18 16 10 16 "
                                    "C6 20 -6 20 -10 16 C-18 16 -22 10 -20 4 Z")
                                 + _S("M-8 -10 C-4 -6 -10 0 -4 4 M4 -14 C8 -8 2 -2 8 4 M-14 8 C-6 6 0 12 8 8", 2, _K), 32, 30, 0, 1.0)
                          + _G(_R(-1.5, -12, 3, 18, 1.5) + _P("M0 10 L3 4 L-3 4 Z"), 50, 46, 140),
    "Piqûre sapeuse": lambda: _over(_skull(30, 34, 0.9), _G(_P("M0 -14 C4 -6 4 4 0 14 C-4 4 -4 -6 0 -14 Z"), 50, 16, 40, 1.0)),
    "Poigne électrique": lambda: _over(_hand(26, 40, 0.85, 0), _bolt(46, 22, 0.75)),
    "Poussière d'étoile": lambda: _star(30, 30, 16) + _star(50, 14, 7) + _star(48, 46, 5) + _star(14, 50, 5) + _star(12, 14, 4)
                                  + _C(40, 56, 2) + _C(56, 30, 2) + _C(22, 8, 2),
    "Prestidigitation": lambda: _G(_R(-3.2, -26, 6.4, 46, 3) + _R(-3.2, -26, 6.4, 8, 1, _K) + _R(-2.2, -25, 4.4, 6, 1), 24, 38, 40)
                                + _star(46, 16, 12) + _star(56, 36, 5) + _star(32, 8, 4),
    "Protection contre les armes": lambda: _over(_G(_blade(30, 8.5, 20, 9, 3.6), 32, 34, 45, 1.15) + _G(_blade(30, 8.5, 20, 9, 3.6), 32, 34, -45, 1.15),
                                                 _shield(32, 34, 0.6)),
    "Rafale de vent": lambda: _wind(30, 32, 1.1) + _C(56, 12, 2.4),
    "Réparation": lambda: _G(_P("M-14 -20 H14 L10 -12 C18 -6 20 4 16 14 C12 22 -12 22 -16 14 C-20 4 -18 -6 -10 -12 Z")
                             + _L([(-2, -12), (4, -2), (-4, 6), (2, 16)], 2.6, _K), 30, 34, 0, 1.0)
                          + _star(52, 14, 7) + _star(54, 44, 4),
    "Résistance": lambda: _over(_shield(30, 32, 1.1), _P("M30 20 V44 M18 32 H42", _K).replace('fill="#000000"',
                                'fill="none" stroke="#000000" stroke-width="6" stroke-linecap="round"')),
    "Saute de vent": lambda: _over(_wind(30, 40, 0.9), _G(_P("M-12 -24 H4 V2 L18 8 C24 11 24 18 18 18 H-14 C-16 18 -16 16 -15 14 Z"), 44, 20, 0, 0.5)),
    "Sauvagerie primitive": lambda: _G("".join(_P("M{a} -24 C{b} -8 {c} 8 {d} 24 C{e} 10 {f} -8 {a} -24 Z".format(
        a=dx + 10, b=dx + 6, c=dx - 2, d=dx - 10, e=dx + 3, f=dx + 9)) for dx in (-13, 0, 13)), 32, 32, 0, 1.0),
    "Stabilisation": lambda: _over(_heart(32, 30, 0.95), _P("M8 30 H22 L26 22 L32 40 L37 26 L40 30 H56", _K).replace(
        'fill="#000000"', 'fill="none" stroke="#000000" stroke-width="3.6" stroke-linejoin="round"')),
    "Thaumaturgie": lambda: _over(_eye(32, 34, 0.95), _sun(32, 34, 0.35, False).replace('fill="#FFFFFF"', 'fill="#000000"', 0))
                            + "".join(_G(_R(-1.8, -30, 3.6, 8, 1.8), 32, 34, a) for a in (-60, -30, 0, 30, 60)),
    "Trait de feu": lambda: _G(_flame(0, 0, 0.75), 42, 22, 45) + _L([(6, 58), (26, 38)], 4) + _L([(4, 46), (18, 34)], 3)
                            + _L([(18, 60), (30, 48)], 3),
    "Élémentalisme": lambda: _flame(18, 20, 0.5) + _drop(46, 18, 0.42) + _P("M16 54 C10 48 10 40 16 34 C22 40 22 48 16 54 Z")
                             + _S("M36 44 H54 C58 44 58 38 54 38", 3.2) + _S("M38 52 H50", 3.2) + _L([(32, 6), (32, 58)], 1.6) + _L([(6, 32), (58, 32)], 1.6),
    "Éruption de lames": lambda: "".join(_G(_blade(18, 6, 12, 5, 2.6), 32, 32, a, 0.85).replace(
        'translate(32 32) rotate({}) scale(0.85)'.format(a), 'translate(32 32) rotate({}) translate(0 -8) scale(0.85)'.format(a))
                                         for a in range(0, 360, 60)) + _C(32, 32, 5),
    "Éruption ensorcelée": lambda: _burst(32, 32, 26, 10) + _C(32, 32, 9, _K) + _C(32, 32, 5),
}

SPELLS.update(CANTRIPS)


# ================================================================================================ v53 : lot 3
# Sorts de niveau 1 les plus courants.
from .art_actions import book_open as _book, feather as _feather, runner as _runner, wolf as _wolf  # noqa: E402
from .art_armes import boot as _boot, fist as _fist, footprint as _footprint, magnifier as _magnifier  # noqa: E402


def _armor(x=32, y=32, s=1.0):
    return _G(_P("M-16 -22 L-6 -24 C-4 -18 4 -18 6 -24 L16 -22 L24 -12 L18 -6 L16 22 C8 26 -8 26 -16 22 L-18 -6 "
                 "L-24 -12 Z") + _L([(0, -16), (0, 20)], 2, _K) + _S("M-12 2 C-6 6 6 6 12 2", 2, _K), x, y, 0, s)


def _paw(x=32, y=32, s=1.0):
    return _G(_P("M0 4 C-9 4 -14 11 -14 16 C-14 21 -9 23 0 21 C9 23 14 21 14 16 C14 11 9 4 0 4 Z")
              + _C(-12, -8, 5) + _C(-4, -15, 5) + _C(4, -15, 5) + _C(12, -8, 5), x, y, 0, s)


def _owl(x=32, y=32, s=1.0):
    body = _P("M-18 -22 L-10 -14 C-4 -17 4 -17 10 -14 L18 -22 L18 0 C18 14 10 24 0 24 C-10 24 -18 14 -18 0 Z")
    eyes = _C(-8, -4, 7, _K) + _C(8, -4, 7, _K) + _C(-8, -4, 3.4) + _C(8, -4, 3.4)
    beak = _P("M0 2 L4 8 L0 12 L-4 8 Z", _K)
    feathers = _S("M-10 14 Q-5 18 0 14 Q5 18 10 14", 2, _K)
    return _G(body + eyes + beak + feathers, x, y, 0, s)


def _berries(x=32, y=32, s=1.0):
    pts = ((-8, 4), (6, 2), (-2, 14), (12, 14), (-14, 16), (0, -6))
    return _G("".join(_C(px, py, 7) + _C(px - 2, py - 2, 1.8, _K) for px, py in pts)
              + _P("M0 -14 C-6 -22 -16 -24 -22 -20 C-16 -14 -8 -12 0 -14 Z") + _L([(0, -14), (0, -6)], 2.4), x, y, 0, s)


def _vines_wrap():
    return (_S("M6 58 C10 40 26 44 24 28 C22 16 34 10 44 14", 4.2) + _S("M58 58 C52 44 38 48 40 32 C42 22 30 18 22 22", 4.2)
            + _P("M44 14 C50 6 58 6 60 10 C54 14 48 16 44 14 Z") + _P("M22 22 C14 18 8 20 6 24 C12 26 18 26 22 22 Z")
            + _P("M24 36 C30 32 34 34 36 38 C30 40 26 40 24 36 Z"))


def _laugh(x=32, y=32, s=1.0):
    face = _P("M0 -24 C14 -24 22 -16 22 -2 C22 14 12 24 0 24 C-12 24 -22 14 -22 -2 C-22 -16 -14 -24 0 -24 Z")
    eyes = _S("M-14 -6 Q-9 -12 -4 -6", 3, _K) + _S("M4 -6 Q9 -12 14 -6", 3, _K)
    mouth = _P("M-13 3 H13 C13 14 6 18 0 18 C-6 18 -13 14 -13 3 Z", _K) + _P("M-8 12 C-4 15 4 15 8 12 C6 16 -6 16 -8 12 Z")
    tears = _drop(-20, -6, 0.18) + _drop(20, -6, 0.18)
    return _G(face + eyes + mouth, x, y, 0, s) + _G(tears, x, y, 0, s)


def _ear(x=32, y=32, s=1.0):
    return _G(_P("M2 -24 C14 -24 20 -14 20 -4 C20 6 12 8 10 14 C8 20 4 24 -2 24 C-8 24 -12 20 -12 14 L-6 14 "
                 "C-6 17 -4 18 -2 18 C2 18 4 14 6 10 C8 4 14 2 14 -4 C14 -12 9 -18 2 -18 C-5 -18 -10 -12 -10 -6 L-16 -6 "
                 "C-16 -16 -8 -24 2 -24 Z") + _S("M-2 -6 C-2 -12 8 -12 8 -4 C8 2 2 2 2 6", 3), x, y, 0, s)


LEVEL1 = {
    "Armure de mage": lambda: _over(_armor(30, 34, 1.05), _star(52, 12, 8)) + _star(10, 14, 4),
    "Bénédiction": lambda: '<ellipse cx="32" cy="10" rx="13" ry="4.6" fill="none" stroke="#FFFFFF" stroke-width="3.6"/>'
                           + _hand(32, 40, 0.85, 0) + "".join(_G(_R(-1.6, -26, 3.2, 7, 1.6), 32, 40, a) for a in (-70, -50, 50, 70)),
    "Fléau": lambda: _over(_skull(28, 28, 0.9), _G(_R(-4, -16, 8, 18, 2) + _P("M-11 2 H11 L0 16 Z"), 50, 44, 0, 0.9)),
    "Graisse": lambda: _G(_P("M-28 8 C-24 0 -10 2 0 0 C12 -2 24 2 28 8 C24 14 10 12 0 14 C-12 16 -24 14 -28 8 Z"), 32, 48)
                       + _drop(32, 20, 0.5) + _G(_boot(0, 0, 0.5), 46, 26, -30),
    "Feuille morte": lambda: _feather(26, 28, 1.0, 35) + '<path d="M48 6 C56 16 42 24 50 34 C58 44 44 50 50 60" fill="none" '
                                                          'stroke="#FFFFFF" stroke-width="2.6" stroke-dasharray="4 4"/>',
    "Mains brûlantes": lambda: _over(_flame(18, 22, 0.55) + _flame(32, 16, 0.65) + _flame(46, 22, 0.55),
                                       _G(_R(-14, -4, 28, 18, 6) + _R(-14, -14, 6, 14, 3) + _R(-7, -17, 6, 16, 3)
                                          + _R(0, -17, 6, 16, 3) + _R(7, -14, 6, 14, 3), 32, 50, 0, 0.75)),
    "Vague tonnante": lambda: _S("M16 10 C26 22 26 42 16 54", 5) + _S("M30 6 C42 20 42 44 30 58", 4.2) + _S("M44 4 C58 20 58 44 44 60", 3.4)
                              + _burst(10, 32, 8, 7),
    "Orbe chromatique": lambda: _C(32, 32, 22) + _P("M32 10 C40 20 40 44 32 54", _K).replace('fill="#000000"', 'fill="none" stroke="#000000" stroke-width="2.6"')
                                + _P("M10 32 C20 24 44 24 54 32", _K).replace('fill="#000000"', 'fill="none" stroke="#000000" stroke-width="2.6"')
                                + _C(24, 22, 4, _K) + _star(56, 8, 5),
    "Bouclier de la foi": lambda: _over(_shield(32, 34, 1.15), _sun(32, 32, 0.45).replace('fill="#FFFFFF"', 'fill="#000000"')),
    "Faveur divine": lambda: _over(_sun(44, 18, 0.55, False), _G(_blade(30, 8.5, 20, 9, 3.6), 28, 38, 45, 1.0)),
    "Héroïsme": lambda: _over(_shield(32, 34, 1.15), _heart(32, 30, 0.45).replace('fill="#FFFFFF"', 'fill="#000000"')),
    "Châtiment courroucé": lambda: _over(_G(_blade(30, 8.5, 20, 9, 3.6), 26, 38, 45, 1.0), _skull(46, 18, 0.55)),
    "Châtiment calcinant": lambda: _over(_G(_blade(30, 8.5, 20, 9, 3.6), 26, 38, 45, 1.0), _flame(46, 18, 0.55)),
    "Châtiment tonitruant": lambda: _over(_G(_blade(30, 8.5, 20, 9, 3.6), 26, 38, 45, 1.0), _rings(46, 18, (8, 14), 2.8)),
    "Absorption des éléments": lambda: _over(_shield(30, 36, 1.0), _flame(14, 14, 0.35) + _snowflake(50, 12, 0.3))
                                       + _carrow("M18 24 C22 28 24 30 26 30", (26, 30), 40, 2.4),
    "Alarme": lambda: _over(_bell(30, 34, 1.0), _G(_R(-3.5, -16, 7, 20, 3.5) + _C(0, 12, 4), 54, 22, 0, 0.8))
                      + _S("M4 22 C0 30 0 38 4 46", 2.8),
    "Appel de familier": lambda: _over(_owl(30, 34, 1.1), _star(54, 12, 6)),
    "Amitié avec les animaux": lambda: _over(_paw(28, 36, 1.1), _heart(48, 16, 0.42)),
    "Armure d'Agathys": lambda: _over(_armor(28, 36, 1.0), _snowflake(48, 16, 0.45)),
    "Enchevêtrement": _vines_wrap,
    "Lueurs féeriques": lambda: '<g opacity="1">' + _G(_C(0, -20, 6) + _P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), 32, 32) + "</g>"
                                + "".join(_star(x, y, r) for x, y, r in ((12, 12, 5), (52, 14, 6), (10, 40, 4), (54, 44, 5), (32, 58, 3.5))),
    "Image silencieuse": lambda: _R(10, 10, 44, 44, 3) + _R(15, 15, 34, 34, 2, _K) + _mask_face(32, 32, 0.6) + _star(52, 52, 5),
    "Nappe de brouillard": lambda: _cloud(32, 22, 0.9) + _L([(8, 44), (48, 44)], 4) + _L([(16, 52), (56, 52)], 4) + _L([(10, 60), (40, 60)], 4),
    "Rayon empoisonné": lambda: _L([(8, 56), (40, 24)], 6) + _G(_P("M0 -9 C6 -9 9 -5 9 0 C9 4 7 6 6 7 V10 H-6 V7 C-7 6 -9 4 -9 0 "
                                                                   "C-9 -5 -6 -9 0 -9 Z") + _C(-3.5, 0, 2.2, _K) + _C(3.5, 0, 2.2, _K), 48, 16, 0, 1.3)
                                + _drop(20, 22, 0.2) + _drop(44, 48, 0.2),
    "Sanctuaire": lambda: _S("M6 52 C6 22 18 8 32 8 C46 8 58 22 58 52", 4.6) + _L([(4, 54), (60, 54)], 4)
                          + _G(_C(0, -12, 5) + _P("M-8 -4 H8 L9 10 H5 L4 22 H-4 L-5 10 H-9 Z"), 32, 32, 0, 0.95),
    "Protection contre le mal et le bien": lambda: '<circle cx="32" cy="32" r="26" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
                                                   + _shield(32, 33, 0.75) + _L([(26, 26), (38, 38)], 1, _K),
    "Détection du mal et du bien": lambda: _over(_eye(32, 38, 0.95), _P("M14 14 C10 8 10 2 14 -2 C14 4 18 8 22 10 Z")
                                                 + _P("M50 14 C54 8 54 2 50 -2 C50 4 46 8 42 10 Z")
                                                 + '<ellipse cx="32" cy="12" rx="9" ry="3.4" fill="none" stroke="#FFFFFF" stroke-width="2.8"/>'),
    "Couleurs dansantes": lambda: _P("M32 6 L54 50 H10 Z") + _P("M32 18 L46 46 H18 Z", _K)
                                  + _L([(40, 26), (60, 16)], 3) + _L([(44, 34), (62, 30)], 3) + _L([(46, 42), (60, 46)], 3),
    "Fou rire de Tasha": lambda: _laugh(32, 34, 1.05),
    "Murmures dissonants": lambda: _over(_ear(26, 32, 1.0), _G(_L([(0, -12), (6, -4), (0, 2), (6, 10)], 3.2), 50, 30)
                                         + _G(_L([(0, -8), (4, -2), (0, 4)], 2.6), 58, 30)),
    "Duel forcé": lambda: _over(_G(_blade(30, 8.5, 20, 9, 3.6), 32, 34, 45, 1.0) + _G(_blade(30, 8.5, 20, 9, 3.6), 32, 34, -45, 1.0),
                                _C(32, 20, 6)) + _rings(32, 34, (28,), 2.4),
    "Saut": lambda: _boot(26, 40, 0.75) + _arrow(48, 52, 48, 6, 4.4, 11) + _S("M10 60 H40", 3),
    "Repli expéditif": lambda: _runner(36, 32, 1.0) + _speed(4, 30, 3, 12, 8, 0, 3.4) + _star(54, 10, 5),
    "Déguisement": lambda: _over(_mask_face(26, 36, 0.8), _mask_face(42, 26, 0.7, False)),
    "Identification": lambda: _over(_G(_P("M0 -14 L12 -4 L0 16 L-12 -4 Z") + _P("M-12 -4 H12 L0 -14 Z", _K).replace(
        'fill="#000000"', 'fill="none" stroke="#000000" stroke-width="2"'), 26, 34, 0, 1.2), _magnifier(44, 22, 0.75)),
    "Compréhension des langues": lambda: _over(_book(32, 40, 0.8), _P("M30 2 H54 C57 2 58 4 58 7 V17 C58 20 57 22 54 22 H44 L38 28 "
                                                                       "V22 H30 C27 22 26 20 26 17 V7 C26 4 27 2 30 2 Z")),
    "Communication avec les animaux": lambda: _over(_paw(24, 40, 0.95), _P("M34 4 H56 C59 4 60 6 60 9 V19 C60 22 59 24 56 24 H46 "
                                                                            "L40 30 V24 H34 C31 24 30 22 30 19 V9 C30 6 31 4 34 4 Z")),
    "Grande foulée": lambda: _boot(36, 32, 1.0) + _speed(4, 30, 3, 14, 8, 0, 3.4),
    "Frayeur": lambda: _over(_skull(30, 34, 1.0), _G(_R(-3.5, -16, 7, 20, 3.5) + _C(0, 12, 4), 54, 18, 0, 0.75)),
    "Blessure": lambda: _over(_hand(26, 40, 0.85, 0), _skull(46, 18, 0.5)),
    "Baies nourricières": lambda: _berries(32, 34, 1.15),
    "Catapulte": lambda: _G(_P("M-11 -9 L7 -13 L15 0 L9 13 L-9 11 L-15 0 Z") + _L([(-6, -4), (4, 4)], 2, _K), 44, 20, 0, 1.0)
                         + _carrow("M6 56 C10 40 18 32 28 28", (28, 28), -25, 3.4) + _L([(20, 46), (30, 40)], 3) + _L([(14, 38), (24, 34)], 3),
    "Couteau de glace": lambda: _G(_P("M0 -24 L6 -6 L3 0 L-3 0 L-6 -6 Z") + _R(-7, 0, 14, 4, 2) + _R(-2, 4, 4, 9, 1.2), 26, 36, 45, 1.2)
                                + _P("M48 10 L52 18 L46 16 Z") + _P("M54 28 L60 32 L54 34 Z") + _P("M40 4 L44 8 L38 8 Z"),
    "Frappe piégeuse": lambda: _over(_G(_blade(30, 8.5, 20, 9, 3.6), 30, 34, 45, 1.0), _S("M12 22 C22 18 28 28 22 34 C16 40 26 48 34 44", 3.2)),
    "Grêle d'épines": lambda: _burst(32, 32, 10, 8) + "".join(_G(_P("M0 -8 L3 0 L-3 0 Z"), 32 + 20 * math.cos(math.radians(a)),
                                                                 32 + 20 * math.sin(math.radians(a)), a + 90) for a in range(0, 360, 30)),
    "Collet": lambda: '<ellipse cx="28" cy="44" rx="20" ry="10" fill="none" stroke="#FFFFFF" stroke-width="4.4"/>'
                      + _S("M46 40 C52 30 50 18 44 8", 4.2) + _P("M40 6 L48 4 L46 12 Z") + _star(10, 14, 4),
}

SPELLS.update(LEVEL1)
