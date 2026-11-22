"""
Icônes de l'interface (v53) — pictogrammes carrés monochromes dessinés ici, en SVG (viewBox 64 × 64, blanc sur
transparent : l'application les teinte selon le thème). Aucune image extérieure.

    python tools/build_icons.py            # écrit data/icons/*.svg
    python tools/build_icons.py --check    # vérifie que tous les fichiers sont à jour

Les formes sont composées à partir de primitives (lame, flamme, main…) : modifier une primitive redessine toutes
les icônes qui l'utilisent. Le catalogue ICONS (nom -> fonction) sert aussi de référence au code (core/icons.py).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "icons"
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


def svg(name: str) -> str:
    body = ICONS[name]()
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            "<!-- {} : icône de la fiche D&D 5e (dessinée par tools/build_icons.py) -->{}</svg>\n").format(name, body)


def main() -> int:
    check = "--check" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for name in ICONS:
        p = OUT / "{}.svg".format(name)
        text = svg(name)
        if not p.exists() or p.read_text(encoding="utf-8") != text:
            stale.append(name)
            if not check:
                p.write_text(text, encoding="utf-8")
    print("{} icône(s) {} sur {}".format(len(stale), "à régénérer" if check else "écrite(s)", len(ICONS)))
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main())
