"""
Boîte d'éléments soignés (v53) pour les dessins de sorts et de capacités : silhouettes, créatures, murs, sphères,
portails, arbres, monture, nuage, tornade… et deux assemblages (`duo` : élément principal + second élément détouré
en bas à droite ; `ring` : élément dans un cercle). Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations


from .art_armes import Cc, G, K, L, P, R, S, burst, curved_arrow, over, star4
from .art_motifs import MOTIFS as M


def place(svg: str, x: float, y: float, s: float) -> str:
    """Élément dessiné sur la grille 64 × 64, recentré en (x, y) à l'échelle s."""
    return '<g transform="translate({:g} {:g}) scale({:g}) translate(-32 -32)">{}</g>'.format(x, y, s, svg)


def black(svg: str) -> str:
    return svg.replace('fill="#FFFFFF"', 'fill="#000000"').replace('stroke="#FFFFFF"', 'stroke="#000000"')


def duo(main: str, second: str, s2: float = 0.46) -> str:
    """Élément principal en grand, second élément détouré en bas à droite."""
    return over(place(main, 27, 27, 0.74), place(second, 47, 47, s2), 9)


def corner(main: str, second: str, s2: float = 0.4) -> str:
    """Second élément détouré en haut à droite."""
    return over(place(main, 28, 34, 0.76), place(second, 49, 15, s2), 9)


def inside(outer: str, inner: str, s: float = 0.5) -> str:
    """Élément évidé (noir) au centre d'un élément plein."""
    return outer + black(place(inner, 32, 32, s))


def ring(inner: str, dashed: bool = False, s: float = 0.66) -> str:
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return ('<circle cx="32" cy="32" r="28" fill="none" stroke="#FFFFFF" stroke-width="3.6"{}/>'.format(dash)
            + place(inner, 32, 32, s))


# ------------------------------------------------------------------------------------------------ personnages
def figure(x=32, y=32, s=1.0, a=0) -> str:
    return G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), x, y, a, s)


def ghost_figure(x=32, y=32, s=1.0) -> str:
    return figure(x, y, s).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-dasharray="4 3"')


def crowd() -> str:
    return figure(16, 36, 0.75) + figure(48, 36, 0.75) + over("", figure(32, 32, 0.95), 6)


def head_profile() -> str:
    return P("M30 58 V48 C22 48 18 44 18 38 L12 34 L18 30 C16 18 22 8 34 8 C44 8 50 16 50 26 C50 34 46 40 42 42 V58 Z")


def crown_small() -> str:
    return P("M10 44 L8 20 L22 32 L32 14 L42 32 L56 20 L54 44 Z") + R(10, 46, 44, 8, 2) + Cc(8, 18, 3) + Cc(32, 12, 3) + Cc(56, 18, 3)


# ------------------------------------------------------------------------------------------------ créatures
def demon() -> str:
    head = P("M32 58 C18 58 10 46 10 32 C10 24 14 18 18 16 L10 2 L26 12 C30 11 34 11 38 12 L54 2 L46 16 "
             "C50 18 54 24 54 32 C54 46 46 58 32 58 Z")
    eyes = P("M18 30 L28 34 L19 37 Z", K) + P("M46 30 L36 34 L45 37 Z", K)
    mouth = P("M22 44 H42 L38 52 H26 Z", K) + P("M25 44 L27 48 L29 44 Z") + P("M35 44 L37 48 L39 44 Z")
    return head + eyes + mouth


def dragon_head() -> str:
    """Tête de dragon de profil : cornes en arrière, crête, gueule ouverte et crocs, naseau."""
    horns = P("M22 20 C14 12 8 6 2 4 C8 10 12 16 14 22 Z") + P("M30 16 C26 8 22 2 16 0 C20 6 22 12 24 18 Z")
    head = P("M10 30 C12 20 22 14 34 16 C44 18 54 22 62 26 L60 32 L44 32 L60 38 C52 46 40 46 32 44 "
             "C26 52 18 58 8 60 L12 46 C8 42 8 36 10 30 Z")
    jaw = P("M44 32 L60 32 L60 38 Z", K)
    teeth = P("M46 32 L48 36 L50 32 Z") + P("M52 32 L54 35 L56 32 Z") + P("M48 38 L50 35 L52 38 Z")
    eye = P("M30 24 L40 25 L32 29 Z", K)
    crest = P("M12 30 L6 26 L10 34 Z") + P("M12 40 L4 40 L10 46 Z")
    return horns + head + jaw + teeth + eye + crest + Cc(56, 27, 1.4, K)


def angel_wings() -> str:
    def wing(sx):
        d = ("M32 30 C26 18 14 10 2 10 C6 14 8 16 10 18 C4 18 2 20 0 22 C8 24 12 26 14 28 C8 30 6 32 4 34 "
             "C14 36 22 36 32 34 Z")
        return '<g transform="translate(32 0) scale({} 1) translate(-32 0)">{}</g>'.format(sx, P(d))
    return wing(1) + wing(-1) + figure(32, 38, 0.6) + '<ellipse cx="32" cy="16" rx="8" ry="2.6" fill="none" ' \
        'stroke="#FFFFFF" stroke-width="2.4"/>'


def horse() -> str:
    body = P("M10 34 C10 26 18 22 28 22 H42 L46 10 L52 8 L56 14 L60 22 L56 24 L52 20 L50 28 C52 34 50 38 46 40 "
             "L48 56 H43 L41 42 H24 L20 56 H15 L16 40 C12 40 10 38 10 34 Z")
    mane = P("M46 10 C42 14 40 18 42 22 L44 22 Z", K)
    tail = P("M10 30 C4 34 2 42 4 50 C8 44 10 40 12 36 Z")
    return body + mane + tail + Cc(52, 14, 1.4, K)


def insect() -> str:
    body = '<ellipse cx="32" cy="38" rx="10" ry="16" fill="#FFFFFF"/>' + Cc(32, 16, 7)
    wings = '<ellipse cx="18" cy="30" rx="12" ry="6" transform="rotate(-30 18 30)" fill="#FFFFFF"/>' \
            '<ellipse cx="46" cy="30" rx="12" ry="6" transform="rotate(30 46 30)" fill="#FFFFFF"/>'
    legs = "".join(L([(32 + sx * 8, y), (32 + sx * 18, y + d)], 2.4) for sx in (-1, 1) for y, d in ((34, -4), (40, 4), (46, 10)))
    bands = "".join(L([(23, y), (41, y)], 2, K) for y in (36, 42, 48))
    return legs + wings + body + bands + L([(28, 10), (24, 4)], 2) + L([(36, 10), (40, 4)], 2)


def bird() -> str:
    return (P("M4 30 C12 26 20 28 26 32 C30 22 40 14 54 12 C48 18 44 24 42 30 L56 30 L46 36 C40 42 30 44 22 40 "
              "C16 38 10 34 4 30 Z") + Cc(44, 22, 1.6, K))


def tree() -> str:
    """Chêne : large couronne à plusieurs lobes, tronc noueux et racines."""
    crown = (Cc(20, 24, 12) + Cc(32, 16, 13) + Cc(44, 24, 12) + Cc(14, 34, 9) + Cc(50, 34, 9) + Cc(32, 30, 13))
    trunk = P("M27 62 L29 42 L22 36 L24 34 L30 38 L31 32 L33 32 L34 38 L40 34 L42 36 L35 42 L37 62 Z")
    roots = P("M20 62 C24 58 26 56 28 56 L28 62 Z") + P("M44 62 C40 58 38 56 36 56 L36 62 Z")
    leaves = Cc(22, 22, 2.4, K) + Cc(40, 14, 2, K) + Cc(46, 30, 2.2, K) + Cc(16, 34, 1.8, K)
    return crown + black(trunk) + trunk + roots + leaves


def cloud(y=28, s=1.0) -> str:
    return G(P("M-22 14 C-30 14 -32 2 -24 -2 C-26 -12 -14 -18 -6 -12 C-2 -22 16 -22 18 -8 C28 -10 32 4 24 10 "
               "C26 14 22 16 18 16 H-20 C-21 16 -22 15 -22 14 Z"), 32, y, 0, s)


def tornado() -> str:
    return "".join(L([(32 - w / 2 + o, y), (32 + w / 2 + o, y)], 4.4) for y, w, o in
                   ((8, 48, 0), (17, 40, 2), (26, 32, 0), (35, 24, -2), (44, 16, 0), (52, 10, 2), (59, 4, 0)))


def wall(kind: str = "pierre") -> str:
    if kind == "feu":
        return "".join(G(P("M0 22 C-8 22 -10 14 -7 8 C-6 12 -3 13 -3 11 C-4 4 -1 -2 3 -8 C3 -2 6 2 7 8 C9 14 7 22 0 22 Z"),
                         x, 38, 0, 1.0) for x in (12, 24, 36, 48)) + R(2, 58, 60, 4, 1)
    if kind == "eau":
        return R(4, 18, 56, 40, 4) + "".join(S("M8 {y} C16 {a} 24 {b} 32 {y} C40 {a} 48 {b} 56 {y}".format(
            y=y, a=y - 5, b=y + 5), 2.6, K) for y in (28, 38, 48))
    if kind == "lumiere":
        return R(10, 10, 44, 46, 2) + "".join(L([(x, 14), (x, 52)], 2, K) for x in (20, 32, 44)) + star4(32, 32, 8, K)
    if kind == "force":
        return R(8, 8, 48, 50, 3) + R(14, 14, 36, 38, 2, K) + star4(32, 32, 10)
    if kind == "vent":
        return R(4, 6, 6, 52, 2) + R(54, 6, 6, 52, 2) + "".join(S("M14 {} H40 C46 {} 48 {} 42 {}".format(y, y, y - 6, y - 7), 3.4)
                                                              for y in (18, 32, 46))
    if kind == "sable":
        return R(4, 22, 56, 36, 3) + "".join(Cc(x, y, 1.6, K) for x, y in ((12, 30), (24, 36), (40, 28), (50, 40), (18, 48), (34, 50), (46, 52)))
    rows = ""
    for r in range(4):
        off = 0 if r % 2 == 0 else 7
        for c in range(4):
            x = 4 + c * 14 + off - (7 if r % 2 else 0)
            rows += R(max(4, x), 16 + r * 11, min(13, 60 - max(4, x)), 9, 1.5)
    return rows


def sphere(inner: str = "", s: float = 0.5) -> str:
    out = Cc(32, 32, 27) + Cc(32, 32, 22, K) + '<path d="M16 22 C20 14 28 10 36 11" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
    return out + (place(inner, 32, 34, max(s, 0.6)) if inner else "")


def portal() -> str:
    return M["portail"]()


def doorway() -> str:
    return (P("M14 60 V22 C14 10 22 4 32 4 C42 4 50 10 50 22 V60 Z") + P("M20 60 V24 C20 15 26 10 32 10 C38 10 44 15 44 24 V60 Z", K)
            + star4(32, 34, 9))


def hut() -> str:
    return '<path d="M4 54 C4 30 18 12 32 12 C46 12 60 30 60 54 Z" fill="#FFFFFF"/>' + P("M26 54 V40 C26 36 38 36 38 40 V54 Z", K) \
        + L([(2, 56), (62, 56)], 3) + star4(52, 10, 4)


def hand_up(x=32, y=34, s=1.0) -> str:
    return G(R(-14, -4, 26, 26, 8) + R(-14, -22, 6, 22, 3) + R(-7, -26, 6, 26, 3) + R(0, -25, 6, 25, 3)
             + R(7, -20, 6, 20, 3) + P("M12 6 L22 -6 C25 -8 28 -5 26 -2 L14 14 Z"), x, y, 0, s)


def giant_hand() -> str:
    return hand_up(32, 34, 1.15) + star4(54, 10, 5) + star4(10, 12, 4)


def skull_x(x=32, y=30, s=1.0) -> str:
    return place(M["crane"](), x, y, s)


def coffin() -> str:
    return P("M24 4 H40 L50 18 L44 60 H20 L14 18 Z") + R(30, 14, 4, 28, 1, K) + R(24, 22, 16, 4, 1, K)


def bolt_rain() -> str:
    return cloud(18, 0.9) + "".join(G(P("M2 -10 L-4 2 L0 2 L-2 10 L5 -2 L1 -2 L4 -10 Z"), x, 46, 0, 1.0) for x in (18, 32, 46))


def spiral_arrow() -> str:
    return (curved_arrow("M10 34 A22 22 0 0 1 50 18", (50, 18), 40, 5, 12)
            + curved_arrow("M54 30 A22 22 0 0 1 14 46", (14, 46), 220, 5, 12))


def scales() -> str:
    return (R(30, 10, 4, 44, 2) + R(18, 54, 28, 5, 2) + L([(8, 18), (56, 18)], 3.4)
            + P("M2 36 L8 18 L14 36 Z") + P("M50 36 L56 18 L62 36 Z") + P("M0 36 H16 C16 42 0 42 0 36 Z")
            + P("M48 36 H64 C64 42 48 42 48 36 Z") + Cc(32, 10, 4))


def contract() -> str:
    return M["parchemin"]() + Cc(46, 48, 8) + Cc(46, 48, 4.4, K) + star4(46, 48, 3.4)


def book_closed() -> str:
    return (P("M14 8 H48 C51 8 52 10 52 12 V56 H18 C14 56 12 54 12 50 V12 C12 10 13 8 14 8 Z")
            + R(16, 48, 36, 6, 1, K) + R(18, 49.5, 34, 3, 1) + R(46, 8, 4, 40, 0, K))


def arrows_volley() -> str:
    return "".join(L([(x, 58), (x + 24, 30)], 3.2) + P("M{} {} l-2 9 l-7 -5 Z".format(x + 28, 26)) for x in (4, 16, 28, 40) if x + 28 < 64)


def mirror() -> str:
    return ('<ellipse cx="32" cy="26" rx="18" ry="22" fill="#FFFFFF"/><ellipse cx="32" cy="26" rx="13" ry="17" fill="#000000"/>'
            + R(29, 48, 6, 12, 2) + R(22, 58, 20, 4, 2) + L([(24, 20), (32, 12)], 2.6) + L([(26, 30), (38, 18)], 2.6))


def eye_big() -> str:
    return M["oeil"]()


def wave_big() -> str:
    return M["vague"]()


def quiver() -> str:
    return (G(R(-9, -18, 18, 40, 6) + R(-9, -18, 18, 6, 2, K), 30, 38, 15)
            + "".join(L([(x, 22), (x + 4, 4)], 2.6) + P("M{} 2 l3 6 h-6 Z".format(x + 4)) for x in (24, 32, 40)))


def chess_king() -> str:
    return M["couronne"]()


def mind_link() -> str:
    return (place(head_profile(), 18, 34, 0.55) + '<g transform="translate(64 0) scale(-1 1)">' + place(head_profile(), 18, 34, 0.55) + "</g>"
            + S("M24 20 C30 12 34 12 40 20", 3) + Cc(32, 14, 3))


def tentacle_arms() -> str:
    return M["tentacules"]()


def spikes_ground() -> str:
    return P("M2 54 H62 V60 H2 Z") + "".join(P("M{} 54 L{} {} L{} 54 Z".format(x - 4, x, 54 - h, x + 4))
                                             for x, h in ((8, 18), (18, 28), (28, 20), (38, 30), (48, 22), (58, 16)))


def column_fire() -> str:
    return (R(20, 16, 24, 44, 4) + G(P("M0 22 C-14 22 -18 8 -12 -2 C-10 4 -6 6 -5 3 C-8 -8 -2 -18 4 -26 C4 -16 10 -12 12 -4 "
                                       "C14 -8 14 -12 13 -15 C20 -6 20 6 16 13 C13 19 7 22 0 22 Z"), 32, 18, 0, 0.6)
            + "".join(L([(x, 22), (x, 56)], 2, K) for x in (26, 32, 38)))


def sunburst() -> str:
    return burst(32, 32, 28, 12) + Cc(32, 32, 10, K) + Cc(32, 32, 6)


def snow_cone() -> str:
    return (P("M4 32 L60 6 C64 24 64 40 60 58 Z") + black(place(M["flocon"](), 40, 32, 0.45)))


def hourglass_s() -> str:
    return M["sablier"]()


__all__ = [n for n in dir() if not n.startswith("_")]
