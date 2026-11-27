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
