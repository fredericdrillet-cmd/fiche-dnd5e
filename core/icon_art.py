"""
Dessins des icônes (v53) — pictogrammes carrés dessinés ici, en SVG (viewBox 64 × 64, blanc sur transparent ; le noir
sert de découpe). Aucune image extérieure : primitives (lame, flamme, main…) composées en icônes.

- ICONS : actions, armes, capacités, écoles, effets, objets, génériques (écrits dans data/icons par
  tools/build_icons.py) ;
- SPELL_ART : sorts dessinés à la main ; core/spell_icons.py compose les autres.
"""
from __future__ import annotations

import math

W = "#FFFFFF"
S = 'fill="none" stroke="#FFFFFF" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'


def stroke(w: float = 3.5) -> str:
    return S.format(w=w)


def g(content: str, tf: str = "") -> str:
    return '<g transform="{}">{}</g>'.format(tf, content) if tf else content


def rot(content: str, angle: float, cx: float = 32, cy: float = 32) -> str:
    return g(content, "rotate({} {} {})".format(angle, cx, cy))


def place(content: str, x: float, y: float, s: float = 1.0) -> str:
    """Primitive dessinée autour de (32, 32), déplacée en (x, y) et mise à l'échelle s."""
    return g(content, "translate({} {}) scale({}) translate(-32 -32)".format(x, y, s))


def poly(points, fill=True, w=3.5) -> str:
    pts = " ".join("{:g},{:g}".format(x, y) for x, y in points)
    return '<polygon points="{}" {}/>'.format(pts, 'fill="#FFFFFF"' if fill else stroke(w))


def path(d: str, fill=False, w=3.5) -> str:
    return '<path d="{}" {}/>'.format(d, 'fill="#FFFFFF"' if fill else stroke(w))


def circle(cx, cy, r, fill=False, w=3.5) -> str:
    return '<circle cx="{:g}" cy="{:g}" r="{:g}" {}/>'.format(cx, cy, r, 'fill="#FFFFFF"' if fill else stroke(w))


def line(x1, y1, x2, y2, w=3.5) -> str:
    return '<line x1="{:g}" y1="{:g}" x2="{:g}" y2="{:g}" {}/>'.format(x1, y1, x2, y2, stroke(w))


def rect(x, y, w_, h, r=0, fill=True, w=3.5) -> str:
    return '<rect x="{:g}" y="{:g}" width="{:g}" height="{:g}" rx="{:g}" {}/>'.format(
        x, y, w_, h, r, 'fill="#FFFFFF"' if fill else stroke(w))


# ====================================================================================== primitives (verticales)
def sword(length=50, width=10) -> str:
    """Épée pointe en haut, centrée sur x = 32."""
    top = 32 - length / 2
    guard = top + length * 0.68
    return (poly([(32, top), (32 + width / 2, top + 6), (32 + width / 2, guard), (32 - width / 2, guard),
                  (32 - width / 2, top + 6)])
            + rect(32 - width * 1.5, guard, width * 3, 5, 2)
            + rect(32 - 3, guard + 5, 6, length * 0.18)
            + circle(32, guard + 5 + length * 0.18 + 3, 4, True))


def dagger() -> str:
    return sword(34, 9)


def axe() -> str:
    return (rect(30, 8, 4, 50, 2)
            + path("M34 12 C48 10 54 18 54 26 C54 32 48 36 34 34 Z", True))


def greataxe() -> str:
    return (rect(30, 6, 4, 52, 2)
            + path("M34 10 C48 8 54 16 54 24 C54 30 48 34 34 32 Z", True)
            + path("M30 10 C16 8 10 16 10 24 C10 30 16 34 30 32 Z", True))


def hammer() -> str:
    return rect(30, 14, 4, 44, 2) + rect(16, 8, 32, 12, 3)


def mace() -> str:
    spikes = "".join(rot(poly([(32, 2), (36.5, 11), (27.5, 11)]), a, 32, 20) for a in range(0, 360, 45))
    return rect(29, 26, 6, 34, 2) + circle(32, 20, 12, True) + spikes


def flail() -> str:
    return (rect(14, 34, 4, 26, 2) + path("M16 34 Q22 22 34 20", w=2.5)
            + circle(42, 18, 8, True)
            + "".join(rot(poly([(42, 6), (45, 12), (39, 12)]), a, 42, 18) for a in range(0, 360, 72)))


def spear() -> str:
    return rect(30, 18, 4, 42, 2) + poly([(32, 2), (39, 18), (32, 22), (25, 18)])


def halberd() -> str:
    return (rect(30, 10, 4, 50, 2) + poly([(32, 2), (36, 10), (28, 10)])
            + path("M34 12 C46 12 50 20 48 28 L34 26 Z", True))


def bow() -> str:
    return path("M20 6 C44 16 44 48 20 58", w=4) + line(20, 6, 20, 58, 2) + line(14, 32, 50, 32, 2.5) \
        + poly([(54, 32), (46, 28), (46, 36)])


def crossbow() -> str:
    return (rect(30, 18, 4, 38, 2) + path("M10 24 C20 14 44 14 54 24", w=4) + line(10, 24, 32, 30, 2)
            + line(54, 24, 32, 30, 2) + poly([(32, 6), (36, 14), (28, 14)]) + rect(26, 46, 12, 4, 1.5))


def sling() -> str:
    return path("M18 50 C10 34 20 18 32 14 C44 18 54 34 46 50", w=3) + circle(32, 14, 6, True) \
        + line(18, 50, 18, 60, 3) + line(46, 50, 46, 60, 3)


def staff() -> str:
    return rect(30, 12, 4, 48, 2) + circle(32, 10, 7, False, 3) + circle(32, 10, 2.5, True)


def whip() -> str:
    return rect(12, 40, 5, 18, 2) + path("M15 40 C20 20 44 8 52 18 C58 26 46 36 40 30", w=3)


def javelin() -> str:
    return rot(rect(30, 16, 4, 44, 2) + poly([(32, 2), (37, 16), (27, 16)]), 0)


def fist() -> str:
    return (rect(16, 22, 30, 26, 8)
            + path("M22 22 v-6 M30 22 v-8 M38 22 v-6", w=6)
            + rect(24, 46, 18, 12, 3)
            + path("M44 30 C52 30 52 40 44 40", True))


def open_hand() -> str:
    return (rect(20, 30, 24, 26, 8)
            + "".join(rect(x, y, 5.5, 22, 2.75) for x, y in ((21, 12), (27.5, 8), (34, 10)))
            + rect(40.5, 16, 5.5, 18, 2.75)
            + rot(rect(10, 30, 5.5, 18, 2.75), -35, 14, 40))


def shield() -> str:
    return path("M32 6 L52 13 C52 34 46 48 32 58 C18 48 12 34 12 13 Z", True)


def heater_shield() -> str:
    """v53 : grand écu de chevalier (Paladin) — bordure et croix évidées."""
    outer = "M7 7 H57 V28 C57 45 46 54 32 61 C18 54 7 45 7 28 Z"
    inner = "M13 13 H51 V28 C51 41 43 48 32 54 C21 48 13 41 13 28 Z"
    return (path(outer, True) + '<path d="{}" fill="none" stroke="#000000" stroke-width="3"/>'.format(inner)
            + '<path d="M32 17 V47 M20 27 H44" fill="none" stroke="#000000" stroke-width="4" '
              'stroke-linecap="round"/>')


def sickle() -> str:
    """v53 : serpe (Druide) — lame en croissant, manche en bas à gauche."""
    blade = path("M22 46 C42 46 58 34 58 18 C58 8 50 2 38 4 C48 9 51 15 50 21 C48 33 38 40 22 40 Z", True)
    return blade + rot(rect(8, 40, 22, 7, 3), -40, 22, 43)


def key() -> str:
    """v53 : clé (Roublard)."""
    return (circle(32, 14, 9, False, 5.5) + rect(29, 22, 6, 36, 2)
            + rect(35, 44, 10, 5, 1) + rect(35, 52, 7, 5, 1))


def wrench() -> str:
    """v53 : clé plate (Artificier) — mâchoire ouverte en haut, œillet en bas."""
    return (rect(28, 22, 8, 32, 4) + circle(32, 15, 12, True) + circle(32, 54, 7, True)
            + '<rect x="27.5" y="0" width="9" height="15" fill="#000000"/>'
            + '<circle cx="32" cy="54" r="3" fill="#000000"/>')


def greataxe_double() -> str:
    """v53 : hache à deux mains (Barbare) — long manche, deux lames."""
    return (rect(30, 3, 4, 59, 2)
            + path("M34 16 L46 5 C56 11 61 19 61 25 C61 31 56 39 46 45 L34 32 Z", True)
            + path("M30 16 L18 5 C8 11 3 19 3 25 C3 31 8 39 18 45 L30 32 Z", True)
            + circle(32, 60, 3.5, True))


def magic_sparkles() -> str:
    """v53 : éclats de magie (au-dessus d'un œil, d'un livre…)."""
    return sparkle(32, 30, 20) + sparkle(12, 14, 9) + sparkle(52, 12, 8) + sparkle(54, 50, 7) + sparkle(10, 50, 6)


def blood_drops() -> str:
    """v53 : gouttes de sang (Ensorceleur)."""
    return drop() + place(drop(), 50, 50, 0.45)


def shield_outline(w=3.5) -> str:
    return path("M32 6 L52 13 C52 34 46 48 32 58 C18 48 12 34 12 13 Z", w=w)


def boot() -> str:
    return path("M22 8 h14 v28 l14 8 c4 2 4 8 0 10 h-30 Z", True)


def speed_lines(x=4) -> str:
    return line(x, 26, x + 12, 26, 3) + line(x - 2, 34, x + 10, 34, 3) + line(x, 42, x + 12, 42, 3)


def flame(scale=1.0) -> str:
    return path("M32 4 C38 16 50 22 48 38 C46 52 38 58 32 58 C24 58 16 52 16 40 C16 30 22 26 26 18 "
                "C28 26 32 28 34 26 C34 18 32 12 32 4 Z", True)


def snowflake() -> str:
    arms = ""
    for a in range(0, 180, 60):
        arms += rot(line(32, 6, 32, 58, 4) + line(32, 14, 26, 8, 3) + line(32, 14, 38, 8, 3)
                    + line(32, 50, 26, 56, 3) + line(32, 50, 38, 56, 3), a)
    return arms


def bolt() -> str:
    return poly([(36, 2), (14, 36), (30, 36), (24, 62), (50, 26), (34, 26), (42, 2)])


def waves() -> str:
    return (path("M14 20 C24 26 24 38 14 44", w=4) + path("M26 12 C40 22 40 42 26 52", w=4)
            + path("M38 6 C56 20 56 44 38 58", w=4))


def drop() -> str:
    return path("M32 6 C40 20 48 30 48 40 C48 50 40 58 32 58 C24 58 16 50 16 40 C16 30 24 20 32 6 Z", True)


def bubbles() -> str:
    return circle(46, 14, 5, False, 3) + circle(54, 26, 3.5, False, 2.5)


def skull() -> str:
    return (path("M32 6 C46 6 54 16 54 28 C54 36 50 40 46 42 L46 52 L18 52 L18 42 C14 40 10 36 10 28 "
                 "C10 16 18 6 32 6 Z", True)
            + '<circle cx="23" cy="28" r="6" fill="#000000"/><circle cx="41" cy="28" r="6" fill="#000000"/>'
            + '<polygon points="32,34 28,42 36,42" fill="#000000"/>'
            + rect(22, 52, 4, 6, 1) + rect(30, 52, 4, 6, 1) + rect(38, 52, 4, 6, 1))


def heart() -> str:
    return path("M32 56 C14 42 6 32 6 22 C6 12 14 6 22 6 C27 6 30 9 32 12 C34 9 37 6 42 6 C50 6 58 12 58 22 "
                "C58 32 50 42 32 56 Z", True)


def plus(w=7) -> str:
    return rect(32 - w / 2, 14, w, 36, 2) + rect(14, 32 - w / 2, 36, w, 2)


def eye() -> str:
    return (path("M4 32 C14 16 50 16 60 32 C50 48 14 48 4 32 Z", w=3.5)
            + circle(32, 32, 9, True) + '<circle cx="32" cy="32" r="3.5" fill="#000000"/>')


def eye_closed() -> str:
    return path("M4 30 C14 44 50 44 60 30", w=3.5) + line(16, 40, 12, 48, 3) + line(32, 44, 32, 52, 3) \
        + line(48, 40, 52, 48, 3)


def magnifier() -> str:
    return circle(26, 26, 15, False, 5) + rot(rect(36, 38, 22, 7, 3), 45, 40, 40)


def door() -> str:
    return rect(16, 6, 32, 52, 3, False, 4) + circle(40, 34, 3, True) + line(10, 58, 54, 58, 4)


def bubble() -> str:
    return path("M10 12 h44 a4 4 0 0 1 4 4 v24 a4 4 0 0 1 -4 4 h-26 l-12 10 v-10 h-6 a4 4 0 0 1 -4 -4 v-24 "
                "a4 4 0 0 1 4 -4 Z", True)


def hourglass() -> str:
    return (rect(14, 4, 36, 5, 2) + rect(14, 55, 36, 5, 2)
            + path("M18 9 L46 9 L34 32 L46 55 L18 55 L30 32 Z", w=3.5)
            + poly([(24, 50), (40, 50), (32, 40)]))


def flask() -> str:
    return (rect(26, 4, 12, 5, 2) + path("M28 9 v14 L14 48 C12 54 16 58 22 58 h20 c6 0 10 -4 8 -10 L36 23 V9",
                                         w=3.5)
            + path("M19 44 h26 l4 6 c1 4 -2 6 -5 6 h-24 c-3 0 -6 -2 -5 -6 Z", True))


def scroll() -> str:
    return (rect(14, 10, 36, 44, 4, False, 3.5) + circle(14, 14, 5, False, 3) + circle(50, 50, 5, False, 3)
            + line(22, 22, 42, 22, 3) + line(22, 30, 42, 30, 3) + line(22, 38, 36, 38, 3))


def ring() -> str:
    return circle(32, 38, 16, False, 6) + poly([(32, 6), (42, 16), (32, 24), (22, 16)])


def wand() -> str:
    return rot(rect(29, 14, 6, 46, 3), 35) + sparkle(14, 14, 9)


def amulet() -> str:
    return path("M14 6 C14 24 24 32 32 34 C40 32 50 24 50 6", w=3) + poly([(32, 30), (44, 44), (32, 60), (20, 44)])


def book() -> str:
    return (path("M32 14 C24 8 14 8 6 12 V54 C14 50 24 50 32 56 C40 50 50 50 58 54 V12 C50 8 40 8 32 14 Z",
                 w=3.5) + line(32, 14, 32, 56, 3))


def star(cx=32, cy=32, r=26, ri=11) -> str:
    pts = []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else ri
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    return poly(pts)


def sparkle(cx=32, cy=32, r=24) -> str:
    q = r * 0.22
    return poly([(cx, cy - r), (cx + q, cy - q), (cx + r, cy), (cx + q, cy + q), (cx, cy + r), (cx - q, cy + q),
                 (cx - r, cy), (cx - q, cy - q)])


def sun() -> str:
    rays = "".join(rot(rect(30, 2, 4, 12, 2), a) for a in range(0, 360, 45))
    return circle(32, 32, 13, True) + rays


def moon() -> str:
    return path("M40 6 C24 8 14 20 14 34 C14 48 26 58 40 58 C30 52 24 44 24 32 C24 20 30 12 40 6 Z", True)


def paw() -> str:
    return (path("M32 30 C42 30 50 40 48 48 C46 56 38 54 32 52 C26 54 18 56 16 48 C14 40 22 30 32 30 Z", True)
            + circle(16, 24, 6, True) + circle(27, 14, 6, True) + circle(38, 14, 6, True) + circle(48, 24, 6, True))


def note() -> str:
    return (circle(20, 48, 8, True) + circle(44, 42, 8, True) + rect(25, 12, 4, 36, 1)
            + rect(49, 8, 4, 34, 1) + poly([(25, 12), (53, 6), (53, 14), (25, 20)]))


def chain() -> str:
    return (rot(rect(8, 22, 26, 14, 7, False, 4), -35, 21, 29) + rot(rect(30, 28, 26, 14, 7, False, 4), -35, 43, 35))


def broken_chain() -> str:
    return (rot(rect(4, 24, 24, 14, 7, False, 4), -35, 16, 31) + rot(rect(36, 26, 24, 14, 7, False, 4), -35, 48, 33)
            + line(32, 12, 30, 22, 3) + line(38, 14, 42, 20, 3) + line(26, 42, 22, 50, 3))


def mask() -> str:
    return (path("M6 20 C16 14 26 16 32 20 C38 16 48 14 58 20 C58 34 50 42 40 42 C36 42 34 38 32 36 C30 38 28 42 24 42 "
                 "C14 42 6 34 6 20 Z", True)
            + '<ellipse cx="20" cy="28" rx="6" ry="4" fill="#000000"/><ellipse cx="44" cy="28" rx="6" ry="4" fill="#000000"/>')


def burst() -> str:
    pts = []
    for k in range(16):
        a = k * math.pi / 8
        rr = 28 if k % 2 == 0 else 13
        pts.append((32 + rr * math.cos(a), 32 + rr * math.sin(a)))
    return poly(pts)


def spiral() -> str:
    return path("M32 32 m0 -3 a3 3 0 1 1 -3 3 a7 7 0 1 1 7 7 a11 11 0 1 1 -11 -11 a15 15 0 1 1 15 15 "
                "a19 19 0 1 1 -19 -19", w=3.5)


def wing() -> str:
    return path("M8 50 C12 24 30 10 56 8 C50 16 50 18 44 22 C50 24 50 26 40 30 C46 32 44 36 34 38 C40 40 36 44 26 44 "
                "C22 48 14 50 8 50 Z", True)


def crown() -> str:
    return poly([(8, 46), (8, 18), (20, 30), (32, 12), (44, 30), (56, 18), (56, 46)]) + rect(8, 48, 48, 6, 2)


def target() -> str:
    return circle(32, 32, 26, False, 4) + circle(32, 32, 16, False, 4) + circle(32, 32, 6, True)


def claws() -> str:
    """Trois griffures en biais, effilées aux deux bouts."""
    one = path("M0 0 C4 10 6 22 3 34 C8 22 8 10 0 0 Z", True)
    return "".join(g(one, "translate({} {}) rotate(-28) scale(1.45)".format(x, y)) for x, y in ((10, 14), (24, 9), (38, 4)))


def cycle_arrows() -> str:
    return (path("M50 26 A20 20 0 0 0 14 22", w=4) + poly([(10, 12), (20, 24), (8, 28)])
            + path("M14 38 A20 20 0 0 0 50 42", w=4) + poly([(54, 52), (44, 40), (56, 36)]))


def back_arrow() -> str:
    return path("M48 54 V30 C48 18 40 12 28 12 H18", w=5) + poly([(6, 12), (20, 2), (20, 22)])


def portal() -> str:
    return circle(32, 32, 24, False, 3) + circle(32, 32, 16, False, 3) + sparkle(32, 32, 10)


def brain() -> str:
    return (path("M32 10 C22 6 12 12 12 22 C6 26 6 38 12 42 C12 52 22 58 32 54 C42 58 52 52 52 42 C58 38 58 26 52 22 "
                 "C52 12 42 6 32 10 Z", w=3.5)
            + line(32, 10, 32, 54, 3) + path("M20 24 C26 24 26 32 20 34", w=3) + path("M44 24 C38 24 38 32 44 34", w=3))


def diamond_burst() -> str:
    return poly([(32, 4), (44, 32), (32, 60), (20, 32)]) + line(6, 32, 16, 32, 3) + line(48, 32, 58, 32, 3) \
        + line(12, 12, 18, 18, 3) + line(52, 12, 46, 18, 3)


def arrow_up() -> str:
    return poly([(32, 4), (54, 28), (40, 28), (40, 58), (24, 58), (24, 28), (10, 28)])


def bulb() -> str:
    return (path("M32 6 C44 6 52 14 52 26 C52 34 46 38 42 44 V48 H22 V44 C18 38 12 34 12 26 C12 14 20 6 32 6 Z", True)
            + rect(22, 50, 20, 4, 2) + rect(25, 56, 14, 4, 2))


def cloak() -> str:
    return path("M24 6 h16 l4 8 C52 30 56 46 58 58 H6 C8 46 12 30 20 14 Z", True)


def glove() -> str:
    return (rect(18, 28, 28, 30, 6) + "".join(rect(x, 10, 5.5, 22, 2.75) for x in (19, 26, 33, 40))
            + rect(10, 30, 8, 5, 2.5))


def helm() -> str:
    return path("M10 40 C10 18 20 8 32 8 C44 8 54 18 54 40 V54 H40 V40 H24 V54 H10 Z", True) \
        + '<rect x="18" y="26" width="28" height="5" fill="#000000"/>'


def armor() -> str:
    return path("M18 6 L26 10 C28 14 36 14 38 10 L46 6 L56 16 L50 26 V58 H14 V26 L8 16 Z", True)


def arrows() -> str:
    return (rot(line(32, 12, 32, 58, 3) + poly([(32, 4), (37, 14), (27, 14)]), -18)
            + line(32, 12, 32, 58, 3) + poly([(32, 4), (37, 14), (27, 14)])
            + rot(line(32, 12, 32, 58, 3) + poly([(32, 4), (37, 14), (27, 14)]), 18))


def gem() -> str:
    return poly([(18, 10), (46, 10), (58, 24), (32, 58), (6, 24)]) + \
        '<polyline points="6,24 58,24" stroke="#000000" stroke-width="2" fill="none"/>'


def bag() -> str:
    return path("M22 14 C18 8 46 8 42 14 C54 22 58 36 56 48 C54 56 46 58 32 58 C18 58 10 56 8 48 C6 36 10 22 22 14 Z",
                True) + rect(20, 14, 24, 4, 2)


def tool() -> str:
    return rot(rect(29, 18, 6, 42, 2) + path("M22 6 h20 v12 c0 4 -4 6 -10 6 s-10 -2 -10 -6 Z", True), 40)


def torch() -> str:
    return rot(rect(29, 28, 6, 32, 2) + place(flame(), 32, 16, 0.42), 20)


def bread() -> str:
    return (path("M6 42 C6 24 18 16 32 16 C46 16 58 24 58 42 C58 48 54 50 50 50 H14 C10 50 6 48 6 42 Z", True)
            + '<path d="M20 24 l-4 10 M32 22 l-4 12 M44 24 l-4 10" stroke="#000000" stroke-width="3" '
              'stroke-linecap="round"/>')


def tent_rest() -> str:
    return moon()


def dragon_breath() -> str:
    return (path("M6 30 L22 18 L30 24 L26 34 L14 40 Z", True)
            + path("M30 26 C40 20 48 14 58 10 M30 30 C42 30 50 30 60 32 M30 34 C40 40 48 46 58 52", w=3.5))


def exclaim() -> str:
    return rect(28, 8, 8, 32, 3) + circle(32, 52, 5, True)


def figure_dodge() -> str:
    return (circle(38, 10, 6, True) + path("M36 18 L26 36 L36 44 L30 58 M26 36 L16 42 M34 24 L48 28", w=5)
            + line(4, 22, 14, 22, 3) + line(2, 32, 12, 32, 3))


def push() -> str:
    return open_hand() + poly([(60, 32), (50, 24), (50, 40)])


def grab() -> str:
    return (place(fist(), 32, 34, 0.75) + poly([(4, 34), (14, 26), (14, 42)]) + poly([(60, 34), (50, 26), (50, 42)]))


def use_item() -> str:
    return place(open_hand(), 26, 40, 0.6) + place(flask(), 42, 22, 0.6)


def hide() -> str:
    return eye() + line(8, 56, 56, 8, 5)


def ready() -> str:
    return hourglass()


def heal_hand() -> str:
    return place(open_hand(), 32, 38, 0.75) + place(plus(), 46, 14, 0.4)


def second_wind() -> str:
    return place(heart(), 30, 34, 0.7) + path("M44 10 C56 14 58 26 50 30", w=3.5) + poly([(48, 36), (46, 24), (56, 28)])


def surge() -> str:
    return place(bolt(), 22, 32, 0.75) + place(bolt(), 42, 32, 0.75)


def sneak() -> str:
    return place(dagger(), 22, 34, 0.9) + place(eye_closed(), 44, 22, 0.55)


def smite() -> str:
    return place(sword(), 32, 36, 0.9) + place(sun(), 32, 12, 0.35)


def holy() -> str:
    return sun()


def flurry() -> str:
    return (place(fist(), 40, 34, 0.72) + speed_lines(2) + place(burst(), 54, 14, 0.3) + place(burst(), 12, 54, 0.22))


def ki() -> str:
    return (circle(32, 32, 26, False, 3.5)
            + path("M32 6 A13 13 0 0 1 32 32 A13 13 0 0 0 32 58 A26 26 0 0 1 32 6 Z", True))


def maneuver() -> str:
    return target() + rot(place(sword(), 32, 32, 0.6), 45)


def riposte() -> str:
    return rot(place(sword(), 32, 34, 0.8), 40) + path("M14 14 C24 4 40 4 50 14", w=4) + poly([(56, 20), (44, 18), (52, 8)])


def indomitable() -> str:
    return shield() + '<g fill="#000000">' + star(32, 30, 12, 5).replace('fill="#FFFFFF"', '') + '</g>'


def rage() -> str:
    return claws()


def wildshape() -> str:
    return paw()


def bardic() -> str:
    return note()


def unarmored() -> str:
    return shield_outline() + place(fist(), 32, 32, 0.5)


def opportunity() -> str:
    return place(sword(), 24, 32, 1.05) + place(exclaim(), 48, 30, 0.75)


def generic_action() -> str:
    return circle(32, 32, 24, True)


def generic_bonus() -> str:
    return poly([(32, 8), (56, 52), (8, 52)])


def generic_reaction() -> str:
    return cycle_arrows()


def generic_passive() -> str:
    return circle(32, 32, 24, False, 4) + circle(32, 32, 8, True)


def generic_class() -> str:
    return star()


def generic_race() -> str:
    return path("M32 6 C46 18 46 46 32 58 C18 46 18 18 32 6 Z", True) + line(32, 14, 32, 58, 2.5)


def generic_item() -> str:
    """Coffre."""
    return (path("M8 28 C8 16 18 10 32 10 C46 10 56 16 56 28 Z", True) + rect(8, 30, 48, 26, 3)
            + '<rect x="28" y="26" width="8" height="12" rx="2" fill="#000000"/>')


def generic_spell() -> str:
    return sparkle()


def unknown() -> str:
    return circle(32, 32, 24, False, 4) + path("M24 24 C24 16 40 16 40 24 C40 30 32 30 32 38", w=4) + circle(32, 46, 3, True)


# ====================================================================================== catalogue
ICONS = {
    # --- actions communes
    "attaque": lambda: rot(place(sword(), 32, 32, 1.05), 40) + rot(place(sword(), 32, 32, 1.05), -40),
    "foncer": lambda: place(boot(), 38, 32, 0.9) + speed_lines(),
    "desengager": back_arrow,
    "esquiver": figure_dodge,
    "aider": lambda: place(open_hand(), 20, 34, 0.62) + place(open_hand(), 44, 34, 0.62) + place(heart(), 32, 12, 0.3),
    "se_cacher": hide,
    "bousculer": push,
    "saisir": grab,
    "se_tenir_pret": ready,
    "utiliser_objet": use_item,
    "chercher": magnifier,
    "interagir": door,
    "parler": bubble,
    "etudier": book,
    "influencer": lambda: bubble() + '<g fill="#000000">' + star(34, 28, 10, 4).replace('fill="#FFFFFF"', '') + '</g>',
    "magie": sparkle,
    "boire_potion": flask,
    "se_liberer": broken_chain,
    "attaque_opportunite": opportunity,
    "lancer_objet": lambda: rot(place(dagger(), 40, 28, 1.0), 60) + speed_lines(2),
    # --- attaques par type d'arme
    "arme_epee": lambda: rot(place(sword(), 32, 32, 1.12), 35),
    "arme_epee_courte": lambda: rot(place(sword(40, 10), 32, 32, 1.12), 35),
    "arme_dague": lambda: rot(place(dagger(), 32, 32, 1.35), 35),
    "arme_hache": axe,
    "arme_grande_hache": greataxe,
    "arme_marteau": hammer,
    "arme_masse": mace,
    "arme_fleau": flail,
    "arme_lance": spear,
    "arme_hallebarde": halberd,
    "arme_arc": bow,
    "arme_arbalete": crossbow,
    "arme_fronde": sling,
    "arme_baton": staff,
    "arme_fouet": whip,
    "arme_javeline": javelin,
    "arme_cimeterre": lambda: path("M24 58 L28 46 C40 36 46 20 44 6 C52 20 50 38 34 50 Z", True) + rect(18, 44, 18, 4, 2),
    "arme_mains_nues": fist,
    "arme_bouclier": shield,
    # --- capacités de classe et d'espèce
    "rage": rage,
    "second_souffle": second_wind,
    "fougue": surge,
    "attaque_sournoise": sneak,
    "chatiment": smite,
    "imposition_mains": heal_hand,
    "inspiration_bardique": bardic,
    "forme_sauvage": wildshape,
    "conduit_divin": holy,
    "deluge_coups": flurry,
    "ki": ki,
    "action_fourbe": lambda: place(boot(), 36, 34, 0.8) + place(mask(), 20, 14, 0.45),
    "souffle_draconique": dragon_breath,
    "manoeuvre": maneuver,
    "riposte": riposte,
    "parade": lambda: shield_outline() + rot(place(sword(), 32, 32, 0.6), 90),
    "indomptable": indomitable,
    "esquive_totale": figure_dodge,
    "defense_sans_armure": unarmored,
    "frappe_temporelle": hourglass,
    "sens_divin": lambda: eye() + place(sun(), 50, 12, 0.3),
    "aura": lambda: circle(32, 32, 26, False, 3) + circle(32, 32, 18, False, 2.5) + place(shield(), 32, 32, 0.35),
    "metamagie": lambda: sparkle() + circle(32, 32, 27, False, 2.5),
    "points_sorcellerie": lambda: place(sparkle(), 24, 24, 0.5) + place(sparkle(), 42, 40, 0.5),
    "manifestation": lambda: place(eye(), 32, 30, 0.8) + place(sparkle(), 50, 50, 0.3),
    "pacte": lambda: place(scroll(), 32, 32, 0.9) + place(flame(), 46, 46, 0.3),
    "familier": lambda: place(wing(), 32, 32, 0.9),
    "compagnon": paw,
    "ennemi_jure": target,
    "marque_chasseur": lambda: target() + place(bow(), 32, 32, 0.5),
    "furie": claws,
    "grandeur": crown,
    "rune": lambda: rect(14, 8, 36, 48, 6, False, 3.5) + path("M24 18 L40 30 L24 42 M40 18 V46", w=3.5),
    "tir_arcanique": lambda: place(bow(), 30, 32, 0.9) + place(sparkle(), 50, 14, 0.3),
    "repos": moon,
    "regeneration": lambda: place(heart(), 32, 32, 0.45) + place(cycle_arrows(), 32, 32, 1.0),
    "resistance": shield,
    "vision_noir": lambda: place(eye(), 32, 36, 0.85) + place(moon(), 50, 12, 0.3),
    "transformation": cycle_arrows,
    "invocation_creature": portal,
    "chance": lambda: star() + circle(32, 32, 28, False, 2),
    # --- écoles de magie
    "ecole_abjuration": shield,
    "ecole_divination": eye,
    "ecole_enchantement": lambda: place(heart(), 30, 36, 0.75) + sparkle(50, 12, 10) + sparkle(12, 14, 6),
    "ecole_evocation": burst,
    "ecole_illusion": mask,
    "ecole_invocation": portal,
    "ecole_necromancie": skull,
    "ecole_transmutation": cycle_arrows,
    # --- types d'effet
    "effet_feu": flame,
    "effet_froid": snowflake,
    "effet_foudre": bolt,
    "effet_tonnerre": waves,
    "effet_acide": lambda: drop() + bubbles(),
    "effet_poison": lambda: drop() + '<path d="M26 40 h12 M32 34 v12" stroke="#000000" stroke-width="3"/>',
    "effet_necrotique": skull,
    "effet_radiant": sun,
    "effet_force": diamond_burst,
    "effet_psychique": brain,
    "effet_contondant": hammer,
    "effet_tranchant": lambda: rot(place(sword(), 32, 32, 1.1), 35),
    "effet_perforant": lambda: line(32, 14, 32, 60, 4) + poly([(32, 2), (40, 16), (24, 16)]),
    "effet_soins": lambda: heart() + '<path d="M32 18 v20 M22 28 h20" stroke="#000000" stroke-width="5"/>',
    "effet_controle": chain,
    "effet_protection": shield,
    "effet_deplacement": wing,
    "effet_information": eye,
    "effet_amelioration": arrow_up,
    "effet_lumiere": bulb,
    "effet_invocation": portal,
    # --- objets
    "objet_potion": flask,
    "objet_parchemin": scroll,
    "objet_anneau": ring,
    "objet_baguette": wand,
    "objet_baton": staff,
    "objet_amulette": amulet,
    "objet_cape": cloak,
    "objet_bottes": boot,
    "objet_gants": glove,
    "objet_casque": helm,
    "objet_armure": armor,
    "objet_bouclier": shield,
    "objet_munitions": arrows,
    "objet_livre": book,
    "objet_gemme": gem,
    "objet_sac": bag,
    "objet_outil": tool,
    "objet_torche": torch,
    "objet_ration": bread,
    # --- génériques (repli)
    "type_action": generic_action,
    "type_action_bonus": generic_bonus,
    "type_reaction": generic_reaction,
    "type_passif": generic_passive,
    "capacite_classe": generic_class,
    "capacite_espece": generic_race,
    "objet": generic_item,
    "sort": generic_spell,
    "attaque_generique": lambda: rot(place(sword(), 32, 32, 1.1), 35),
    "inconnu": unknown,
}




def svg_document(name: str, body: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            "<!-- {} : icône de la fiche D&D 5e (core/icon_art.py) -->{}</svg>\n").format(name, body)


# ====================================================================================== sorts dessinés à la main
def ray(x1=8, y1=56, x2=56, y2=8, w=6) -> str:
    return line(x1, y1, x2, y2, w) + line(x1, y1, x2, y2, w * 2.2).replace('stroke="#FFFFFF"', 'stroke="#FFFFFF" '
                                                                         'stroke-opacity="0.25"')


def orb(cx=32, cy=32, r=14) -> str:
    return circle(cx, cy, r, True) + circle(cx, cy, r + 6, False, 2)


def cone(apex=(8, 32)) -> str:
    x, y = apex
    return poly([(x, y), (58, 8), (58, 56)]) + '<path d="M{} {} L58 20 M{} {} L58 44" stroke="#000000" ' \
        'stroke-width="2.5"/>'.format(x + 14, y, x + 14, y)


def small(art: str, x: float, y: float, s: float) -> str:
    return place(art, x, y, s)


def leaf() -> str:
    return path("M10 54 C10 26 30 10 56 8 C54 34 38 54 10 54 Z", True) + \
        '<path d="M12 52 L44 20" stroke="#000000" stroke-width="2.5"/>'


def thorn_whip() -> str:
    return path("M8 54 C20 40 20 24 34 18 C44 14 52 18 56 10", w=4) + "".join(
        poly([(x, y), (x + 5, y - 7), (x + 7, y + 1)]) for x, y in ((14, 46), (22, 32), (34, 20), (46, 15)))


def hand_glow() -> str:
    return place(open_hand(), 32, 36, 0.8) + circle(32, 36, 28, False, 1.5)


def lightning_hand() -> str:
    return place(open_hand(), 26, 38, 0.7) + place(bolt(), 46, 20, 0.45)


def grave() -> str:
    return path("M18 58 V24 C18 12 46 12 46 24 V58 Z", True) + \
        '<path d="M32 24 v18 M24 32 h16" stroke="#000000" stroke-width="4"/>'


def bell() -> str:
    return path("M32 6 C22 6 18 16 18 28 C18 40 12 44 10 48 H54 C52 44 46 40 46 28 C46 16 42 6 32 6 Z", True) + \
        circle(32, 54, 5, True)


def club() -> str:
    return rot(path("M28 60 L28 30 C22 24 22 8 32 6 C42 8 42 24 36 30 L36 60 Z", True), 25) + sparkle(50, 12, 8)


def stones() -> str:
    return circle(20, 40, 10, True) + circle(42, 44, 8, True) + circle(34, 22, 9, True) + sparkle(52, 12, 7)


def dancing_lights() -> str:
    return "".join(circle(x, y, r, True) + circle(x, y, r + 4, False, 1.5)
                   for x, y, r in ((16, 20, 5), (44, 14, 6), (26, 44, 6), (50, 42, 5)))


def mending() -> str:
    return place(tool(), 30, 32, 0.8) + sparkle(50, 14, 9)


def mouth_note() -> str:
    return path("M8 34 C16 22 32 22 40 34 C32 46 16 46 8 34 Z", True) + place(note(), 48, 18, 0.45)


def mind_spike() -> str:
    return place(brain(), 30, 36, 0.75) + poly([(56, 4), (40, 26), (36, 22)])


def star_dust() -> str:
    return sparkle(24, 24, 14) + sparkle(46, 42, 10) + sparkle(46, 14, 6) + sparkle(16, 48, 5)


def gust() -> str:
    return (path("M6 22 H40 C48 22 50 12 42 10", w=4) + path("M6 34 H50 C58 34 58 46 50 46", w=4)
            + path("M14 46 H30", w=4))


def savage() -> str:
    return claws() + place(paw(), 50, 50, 0.3)


def tremor_earth() -> str:
    return poly([(4, 50), (20, 34), (28, 42), (40, 24), (60, 50)]) + path("M10 58 L24 54 L34 60 L48 54 L58 58", w=3)


def water_wave() -> str:
    return path("M4 40 C14 28 22 28 32 40 C42 52 50 52 60 40 V60 H4 Z", True) + path("M8 24 C16 16 24 16 30 24", w=3.5)


def blades_ring() -> str:
    return "".join(rot(place(dagger(), 32, 14, 0.45), a) for a in range(0, 360, 60)) + circle(32, 32, 6, True)


def infestation() -> str:
    return "".join(circle(x, y, 3.5, True) + line(x - 5, y, x + 5, y, 1.5) for x, y in
                   ((16, 18), (30, 12), (44, 20), (22, 32), (40, 34), (14, 46), (30, 50), (48, 48)))


def shield_spark() -> str:
    return shield() + '<g fill="#000000">' + sparkle(32, 30, 12).replace('fill="#FFFFFF"', '') + '</g>'


def missiles() -> str:
    return "".join(rot(place(poly([(32, 6), (40, 30), (32, 26), (24, 30)]) + line(32, 26, 32, 58, 3), 32, 32, 0.7), a)
                   for a in (-28, 0, 28))


def fireball() -> str:
    return burst() + '<g fill="#000000">' + place(flame(), 32, 33, 0.42).replace('fill="#FFFFFF"', '') + '</g>'


def heal_touch() -> str:
    return place(open_hand(), 26, 38, 0.72) + place(heart(), 46, 18, 0.4)


def healing_word() -> str:
    return bubble() + '<path d="M32 18 v20 M22 28 h20" stroke="#000000" stroke-width="5"/>'


def mass_heal() -> str:
    return place(heart(), 20, 40, 0.45) + place(heart(), 44, 40, 0.45) + place(heart(), 32, 18, 0.45)


def zzz() -> str:
    return path("M10 14 H26 L10 30 H26", w=3.5) + path("M30 30 H44 L30 44 H44", w=3.5) + path("M44 46 H56 L44 58 H56", w=3)


def charm() -> str:
    return place(heart(), 32, 36, 0.8) + path("M8 10 C20 4 30 16 22 22", w=3) + poly([(26, 26), (16, 24), (24, 16)])


def mage_armor() -> str:
    return armor() + '<g fill="#000000">' + sparkle(32, 34, 10).replace('fill="#FFFFFF"', '') + '</g>'


def bless() -> str:
    return place(sun(), 32, 24, 0.6) + place(open_hand(), 32, 50, 0.45)


def bane() -> str:
    return place(skull(), 32, 28, 0.6) + line(10, 56, 54, 56, 4)


def detect_magic() -> str:
    return eye() + sparkle(52, 12, 8) + sparkle(12, 12, 5)


def grease() -> str:
    return path("M4 50 C14 42 24 52 32 46 C40 40 50 50 60 44 V60 H4 Z", True) + drop().replace('d="M32 6', 'd="M32 6') \
        .replace('<path', '<path transform="translate(16 4) scale(0.5)"')


def thunderwave() -> str:
    return waves() + place(burst(), 10, 32, 0.25)


def lightning_bolt() -> str:
    return ray(4, 60, 60, 4, 3) + place(bolt(), 32, 32, 0.8)


def counterspell() -> str:
    return sparkle() + line(8, 56, 56, 8, 6)


def dispel() -> str:
    return sparkle(32, 32, 16) + "".join(rot(line(32, 4, 32, 14, 3), a) for a in range(0, 360, 45))


def haste() -> str:
    return place(bolt(), 40, 32, 0.7) + speed_lines(2)


def slow() -> str:
    return place(hourglass(), 32, 32, 0.8) + path("M4 58 H60", w=3)


def fly() -> str:
    return wing() + place(wing(), 40, 30, 0.6).replace('<path', '<path transform="scale(-1 1) translate(-64 0)"')


def misty_step() -> str:
    return (place(boot(), 22, 40, 0.5) + place(boot(), 44, 22, 0.5)
            + path("M6 56 C16 50 26 58 36 52 C46 46 54 54 60 50", w=3) + path("M10 14 C18 8 26 14 32 10", w=3))


def invisibility() -> str:
    return (circle(32, 14, 8, False, 3) + path("M18 58 V34 C18 24 46 24 46 34 V58", w=3)
            + '<path d="M18 40 h28 M18 48 h28" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="3 4"/>')


def mirror_image() -> str:
    one = circle(32, 16, 7, True) + path("M20 58 V34 C20 26 44 26 44 34 V58 Z", True)
    return place(one, 16, 34, 0.6) + place(one, 48, 34, 0.6) + place(one, 32, 32, 0.8)


def hold_person() -> str:
    return place(chain(), 32, 32, 1.0) + circle(32, 32, 28, False, 2.5)


def web() -> str:
    lines_ = "".join(rot(line(32, 32, 32, 2, 2.5), a) for a in range(0, 360, 45))
    rings = "".join(circle(32, 32, r, False, 2) for r in (8, 16, 24))
    return lines_ + rings


def spiritual_weapon() -> str:
    return place(hammer(), 32, 34, 0.8) + sparkle(50, 12, 8) + circle(32, 34, 26, False, 1.5)


def restoration() -> str:
    return place(heart(), 32, 34, 0.75) + place(cycle_arrows(), 32, 32, 1.0)


def guardians() -> str:
    return "".join(rot(place(wing(), 32, 10, 0.32), a) for a in range(0, 360, 72)) + place(sun(), 32, 32, 0.35)


def revivify() -> str:
    return place(heart(), 32, 34, 0.75) + place(bolt(), 50, 14, 0.35) + sparkle(12, 12, 6)


def animate_dead() -> str:
    return place(skull(), 32, 24, 0.6) + place(open_hand(), 32, 50, 0.45)


def dimension_door() -> str:
    return door() + sparkle(32, 30, 10)


def polymorph() -> str:
    return place(paw(), 20, 22, 0.45) + place(cycle_arrows(), 32, 32, 1.0) + circle(44, 42, 8, True)


def wall_fire() -> str:
    return "".join(place(flame(), x, 30, 0.42) for x in (12, 26, 40, 54)) + rect(4, 52, 56, 6, 2)


def banishment() -> str:
    return portal() + poly([(56, 8), (44, 12), (52, 20)]) + line(36, 28, 52, 12, 3)


def stoneskin() -> str:
    return path("M18 6 L46 6 L58 30 L46 58 L18 58 L6 30 Z", True) + \
        '<path d="M18 22 L30 30 L22 44 M40 16 L36 32 L48 40" stroke="#000000" stroke-width="2.5" fill="none"/>'


def cone_cold() -> str:
    return cone() + place(snowflake(), 46, 32, 0.4).replace('#FFFFFF', '#000000')


def resurrection() -> str:
    return place(sun(), 32, 18, 0.5) + place(open_hand(), 20, 46, 0.4) + place(open_hand(), 44, 46, 0.4)


def disintegrate() -> str:
    return ray(6, 58, 40, 24, 4) + "".join(rect(x, y, 4, 4, 0.5) for x, y in ((44, 16), (52, 10), (48, 24),
                                                                             (56, 20), (40, 8), (54, 30)))


def finger_death() -> str:
    return place(open_hand(), 24, 40, 0.65) + place(skull(), 48, 18, 0.45)


def power_word() -> str:
    return bubble() + '<g fill="#000000">' + place(skull(), 32, 28, 0.35).replace('fill="#FFFFFF"', '') + '</g>'


def wish() -> str:
    return star() + sparkle(52, 10, 7) + sparkle(10, 52, 6) + sparkle(54, 52, 5)


def time_stop() -> str:
    return circle(32, 32, 26, False, 4) + line(32, 32, 32, 14, 4) + line(32, 32, 44, 38, 4) + \
        line(10, 10, 54, 54, 4)


def meteors() -> str:
    one = circle(44, 20, 9, True) + path("M38 26 L10 54", w=4)
    return place(one, 32, 32, 0.9) + place(one, 18, 18, 0.5) + place(one, 48, 46, 0.45)


def teleport() -> str:
    return place(portal(), 18, 32, 0.5) + place(portal(), 46, 32, 0.5) + path("M26 24 C32 16 34 16 40 24", w=3)


def acid_arrow() -> str:
    return rot(line(32, 18, 32, 60, 4) + poly([(32, 4), (40, 20), (24, 20)]), 45) + drop().replace(
        '<path', '<path transform="translate(2 34) scale(0.4)"')


def scorching_ray() -> str:
    return "".join(ray(6, 58 - d, 58 - d, 6, 3) for d in (0, 12, 24)) + place(flame(), 50, 14, 0.3)


def daylight() -> str:
    return sun() + circle(32, 32, 30, False, 1.5)


def silence() -> str:
    return bubble() + line(8, 56, 56, 8, 5)


def darkness() -> str:
    return circle(32, 32, 26, True) + '<circle cx="40" cy="26" r="20" fill="#000000"/>'


def fog() -> str:
    return (path("M8 40 C8 32 16 28 22 30 C24 22 34 18 40 24 C48 20 56 26 54 34 C60 36 60 46 52 46 H14 C8 46 6 42 8 40 Z",
                 True) + path("M10 54 H54", w=3))


def divine_favor() -> str:
    return place(sword(), 32, 36, 0.85) + place(sun(), 32, 10, 0.3)


def jump() -> str:
    return path("M8 54 C20 10 44 10 56 54", w=3) + place(boot(), 32, 18, 0.45)


def feather_fall() -> str:
    return place(wing(), 32, 30, 0.8) + path("M20 56 C26 52 38 60 44 56", w=3)


def expeditious() -> str:
    return place(boot(), 38, 30, 0.8) + speed_lines(0) + place(wing(), 52, 12, 0.3)


def burning_hands() -> str:
    return place(open_hand(), 14, 34, 0.5) + cone((22, 32)).replace('<path d="M36', '<path d="M40') \
        + '<g fill="#000000">' + place(flame(), 46, 32, 0.32).replace('fill="#FFFFFF"', '') + '</g>'


def ray_sickness() -> str:
    return ray(6, 58, 52, 12, 4) + place(drop(), 52, 12, 0.35)


def chromatic_orb() -> str:
    return orb() + '<path d="M18 32 H46 M32 18 V46" stroke="#000000" stroke-width="2.5"/>'


def guiding_bolt() -> str:
    return ray(6, 58, 48, 16, 4) + place(star(), 50, 14, 0.35)


def shield_faith() -> str:
    return shield() + '<path d="M32 18 v26 M22 28 h20" stroke="#000000" stroke-width="5"/>'


def sanctuary() -> str:
    return path("M8 58 V30 L32 8 L56 30 V58 Z", w=3.5) + place(heart(), 32, 40, 0.4)


def protection_evil() -> str:
    return circle(32, 32, 26, False, 3.5) + place(shield(), 32, 32, 0.6)


def speak_animals() -> str:
    return bubble() + '<g fill="#000000">' + place(paw(), 32, 28, 0.35).replace('fill="#FFFFFF"', '') + '</g>'


def prayer_healing() -> str:
    return place(open_hand(), 22, 38, 0.55) + place(open_hand(), 42, 38, 0.55) + place(heart(), 32, 12, 0.32)


def heal_spell() -> str:
    return heart() + sparkle(52, 10, 8) + '<path d="M32 18 v20 M22 28 h20" stroke="#000000" stroke-width="5"/>'


def smite_spell() -> str:
    return smite()


def moonbeam() -> str:
    return place(moon(), 40, 12, 0.35) + rect(26, 20, 12, 40, 3) + circle(32, 58, 4, False, 2)


def shatter() -> str:
    return burst() + '<path d="M32 10 L28 30 L38 36 L30 56" stroke="#000000" stroke-width="3" fill="none"/>'


def ray_enfeeble() -> str:
    return ray(6, 58, 50, 14, 4) + place(arrow_up(), 52, 12, 0.3).replace('<polygon', '<polygon transform="rotate(180 32 32)"')


def bigby() -> str:
    return place(open_hand(), 32, 34, 1.0) + sparkle(54, 10, 7)


def tentacles() -> str:
    return "".join(path("M{} 60 C{} 44 {} 34 {} 18".format(x, x - 8, x + 8, x + d), w=4.5)
                   for x, d in ((14, -4), (26, 6), (38, -6), (50, 4)))


def circle_death() -> str:
    return circle(32, 32, 26, False, 4) + place(skull(), 32, 32, 0.5)


def chain_lightning() -> str:
    return (place(bolt(), 14, 20, 0.35) + place(bolt(), 32, 40, 0.35) + place(bolt(), 50, 20, 0.35)
            + path("M16 28 L30 34 M34 34 L48 28", w=2.5))


def firestorm() -> str:
    return "".join(place(flame(), x, y, 0.36) for x, y in ((16, 20), (36, 14), (52, 30), (24, 44), (44, 50)))


def earthquake() -> str:
    return tremor_earth() + path("M30 30 L26 40 L34 46 L28 58", w=2.5)


SPELL_ART = {
    # tours de magie
    "Amis": lambda: place(mask(), 32, 24, 0.7) + place(heart(), 32, 50, 0.3),
    "Aspersion d'acide": lambda: place(drop(), 20, 30, 0.55) + place(drop(), 44, 22, 0.45) + place(drop(), 40, 48, 0.4),
    "Assistance": lambda: place(open_hand(), 32, 38, 0.75) + sparkle(50, 12, 7),
    "Bouffée de poison": lambda: fog() + place(skull(), 50, 14, 0.3),
    "Contact glacial": lambda: place(skull(), 26, 34, 0.6) + place(snowflake(), 50, 14, 0.35),
    "Contrôle des flammes": lambda: place(flame(), 32, 26, 0.6) + place(open_hand(), 32, 54, 0.35),
    "Coup au but": lambda: target() + rot(line(32, 32, 32, 2, 3), 45),
    "Coup de tonnerre": lambda: place(burst(), 32, 32, 0.6) + waves().replace('stroke-width="4"', 'stroke-width="2"'),
    "Druidisme": leaf,
    "Décharge occulte": lambda: orb(26, 38, 10) + ray(30, 34, 58, 6, 4),
    "Embrasement": lambda: place(flame(), 32, 30, 0.8) + path("M8 58 H56", w=3),
    "Façonnage de l'eau": water_wave,
    "Façonnage de la terre": tremor_earth,
    "Ferrage foudroyant": lambda: place(bolt(), 32, 24, 0.6) + path("M16 50 C24 40 40 40 48 50", w=4),
    "Flamme sacrée": lambda: place(flame(), 32, 36, 0.7) + place(sun(), 32, 10, 0.25),
    "Flammes": lambda: place(open_hand(), 32, 48, 0.5) + place(flame(), 32, 20, 0.55),
    "Fouet épineux": thorn_whip,
    "Gelure": lambda: place(snowflake(), 32, 32, 0.8) + circle(32, 32, 28, False, 2),
    "Glas": bell,
    "Gourdin magique": club,
    "Illusion mineure": lambda: place(mask(), 32, 30, 0.8) + sparkle(52, 52, 6),
    "Infestation": infestation,
    "Lame aux flammes vertes": lambda: rot(place(sword(), 32, 34, 0.9), 35) + place(flame(), 48, 14, 0.3),
    "Lame retentissante": lambda: rot(place(sword(), 30, 34, 0.9), 35) + waves().replace('stroke-width="4"', 'stroke-width="2"'),
    "Lumière": bulb,
    "Lumières dansantes": dancing_lights,
    "Main de mage": lambda: hand_glow(),
    "Message": lambda: bubble() + path("M44 6 L58 6 L58 20", w=3),
    "Moquerie cruelle": mouth_note,
    "Mot de radiance": lambda: bubble() + '<g fill="#000000">' + place(sun(), 32, 28, 0.4).replace('fill="#FFFFFF"', '') + '</g>',
    "Pierre magique": stones,
    "Piqûre mentale": mind_spike,
    "Piqûre sapeuse": lambda: place(drop(), 32, 36, 0.6) + poly([(56, 4), (38, 26), (34, 22)]),
    "Poigne électrique": lightning_hand,
    "Poussière d'étoile": star_dust,
    "Prestidigitation": lambda: sparkle(22, 22, 12) + place(open_hand(), 40, 44, 0.45),
    "Protection contre les armes": lambda: shield_outline() + rot(place(sword(), 32, 32, 0.5), 45) + rot(place(sword(), 32, 32, 0.5), -45),
    "Rayon de givre": lambda: ray(6, 58, 46, 18, 4) + place(snowflake(), 48, 16, 0.32),
    "Réparation": mending,
    "Résistance": lambda: shield() + '<g fill="#000000">' + star(32, 30, 11, 5).replace('fill="#FFFFFF"', '') + '</g>',
    "Saute de vent": gust,
    "Sauvagerie primitive": savage,
    "Stabilisation": lambda: place(heart(), 32, 32, 0.7) + line(6, 32, 18, 32, 3) + line(46, 32, 58, 32, 3),
    "Thaumaturgie": lambda: place(eye(), 32, 30, 0.7) + sparkle(14, 50, 6) + sparkle(50, 50, 6),
    "Trait de feu": lambda: ray(6, 58, 44, 20, 4) + place(flame(), 46, 18, 0.36),
    "Élémentalisme": lambda: place(flame(), 20, 20, 0.3) + place(drop(), 44, 20, 0.3) + place(snowflake(), 20, 46, 0.3) + place(gust(), 44, 46, 0.35),
    "Éruption de lames": blades_ring,
    "Éruption ensorcelée": lambda: burst() + circle(32, 32, 8, False, 3).replace('#FFFFFF', '#000000'),
    "Trait ensorcelé": lambda: ray(6, 58, 52, 12, 4) + sparkle(50, 14, 8),
    "Glyphe de protection": lambda: rect(10, 10, 44, 44, 6, False, 3) + path("M20 20 L44 44 M44 20 L20 44 M32 14 V50", w=3),
    # sorts courants
    "Projectile magique": missiles,
    "Bouclier": shield_spark,
    "Boule de feu": fireball,
    "Soins": heal_touch,
    "Mot de guérison": healing_word,
    "Sommeil": lambda: place(moon(), 22, 30, 0.6) + place(zzz(), 44, 30, 0.6),
    "Charme-personne": charm,
    "Armure de mage": mage_armor,
    "Bénédiction": bless,
    "Fléau": bane,
    "Détection de la magie": detect_magic,
    "Graisse": grease,
    "Vague tonnante": thunderwave,
    "Éclair": lightning_bolt,
    "Contresort": counterspell,
    "Dissipation de la magie": dispel,
    "Hâte": haste,
    "Lenteur": slow,
    "Vol": fly,
    "Foulée brumeuse": misty_step,
    "Invisibilité": invisibility,
    "Image miroir": mirror_image,
    "Immobilisation de personne": hold_person,
    "Toile d'araignée": web,
    "Arme spirituelle": spiritual_weapon,
    "Restauration partielle": restoration,
    "Esprits gardiens": guardians,
    "Retour à la vie": revivify,
    "Animation des morts": animate_dead,
    "Porte dimensionnelle": dimension_door,
    "Métamorphose": polymorph,
    "Mur de feu": wall_fire,
    "Bannissement": banishment,
    "Peau de pierre": stoneskin,
    "Cône de froid": cone_cold,
    "Rappel à la vie": resurrection,
    "Désintégration": disintegrate,
    "Doigt de mort": finger_death,
    "Mot de pouvoir mortel": power_word,
    "Souhait": wish,
    "Arrêt du temps": time_stop,
    "Nuée de météores": meteors,
    "Téléportation": teleport,
    "Flèche acide de Melf": acid_arrow,
    "Rayon ardent": scorching_ray,
    "Lumière du jour": daylight,
    "Silence": silence,
    "Ténèbres": darkness,
    "Nappe de brouillard": fog,
    "Faveur divine": divine_favor,
    "Saut": jump,
    "Feuille morte": feather_fall,
    "Repli expéditif": expeditious,
    "Mains brûlantes": burning_hands,
    "Rayon empoisonné": ray_sickness,
    "Orbe chromatique": chromatic_orb,
    "Éclair traçant": guiding_bolt,
    "Bouclier de la foi": shield_faith,
    "Sanctuaire": sanctuary,
    "Protection contre le mal et le bien": protection_evil,
    "Communication avec les animaux": speak_animals,
    "Prière de guérison": prayer_healing,
    "Soins de groupe": mass_heal,
    "Guérison": heal_spell,
    "Châtiment divin": smite_spell,
    "Rayon de lune": moonbeam,
    "Fracassement": shatter,
    "Rayon affaiblissant": ray_enfeeble,
    "Main de Bigby": bigby,
    "Tentacules noirs d'Evard": tentacles,
    "Cercle de mort": circle_death,
    "Chaîne d'éclairs": chain_lightning,
    "Tempête de feu": firestorm,
    "Tremblement de terre": earthquake,
    "Résurrection": lambda: resurrection() + circle(32, 32, 30, False, 1.5) + sparkle(54, 54, 6),
    # v53 : sorts courants dont l'icône composée restait peu parlante
    "Petite hutte de Léomund": lambda: path("M6 52 C6 26 18 12 32 12 C46 12 58 26 58 52 Z", w=4) +
        path("M26 52 V40 C26 34 38 34 38 40 V52", True) + sparkle(50, 10, 6),
    "Portail": lambda: '<ellipse cx="32" cy="32" rx="18" ry="26" fill="none" stroke="#FFFFFF" stroke-width="5"/>' +
        '<ellipse cx="32" cy="32" rx="10" ry="18" fill="none" stroke="#FFFFFF" stroke-width="2"/>' + sparkle(32, 32, 7),
    "Création de nourriture et d'eau": lambda: place(bread(), 24, 40, 0.6) + place(drop(), 46, 22, 0.42),
    "Métal brûlant": lambda: rect(12, 34, 40, 16, 3) + place(flame(), 32, 20, 0.42) +
        '<path d="M18 42 h28" stroke="#000000" stroke-width="2"/>',
    "Nuage nauséabond": lambda: fog() + '<g fill="#000000">' + place(skull(), 32, 38, 0.22).replace('fill="#FFFFFF"', '') + '</g>',
    "Lévitation": lambda: circle(32, 14, 7, True) + path("M22 44 V28 C22 22 42 22 42 28 V44 Z", True) +
        path("M14 52 C24 48 40 48 50 52 M18 58 C26 55 38 55 46 58", w=3),
    "Communication à distance": lambda: place(bubble(), 22, 24, 0.55) + place(bubble(), 44, 44, 0.55) +
        path("M30 38 C34 44 38 44 40 40", w=2.5),
    "Voir l'invisible": lambda: eye() + '<path d="M8 54 h48" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="3 4"/>' +
        sparkle(54, 10, 6),
    "Héroïsme": lambda: place(shield(), 32, 34, 0.8) + place(arrow_up(), 32, 32, 0.35).replace('fill="#FFFFFF"', 'fill="#000000"'),
    "Lueur d'espoir": lambda: place(bulb(), 32, 34, 0.75) + place(heart(), 32, 30, 0.25).replace('fill="#FFFFFF"', 'fill="#000000"'),
    "Compulsion": lambda: place(spiral(), 32, 32, 1.0) + poly([(54, 8), (60, 20), (48, 16)]),
    "Zone de vérité": lambda: circle(32, 32, 27, False, 2.5) + place(bubble(), 32, 30, 0.6) +
        '<path d="M24 28 l5 5 l10 -10" stroke="#000000" stroke-width="3.5" fill="none" stroke-linecap="round"/>',
    "Appel de destrier": lambda: path("M14 56 L18 34 C14 26 18 14 28 10 L32 4 L36 12 C46 14 52 22 50 30 L44 30 "
        "L40 24 L36 30 L38 56 Z", True),
    "Tempête de neige": lambda: fog() + place(snowflake(), 20, 54, 0.22) + place(snowflake(), 44, 54, 0.22),
    "Mur d'eau": lambda: water_wave() + rect(6, 8, 52, 4, 2) + rect(6, 18, 52, 3, 1.5),
}
