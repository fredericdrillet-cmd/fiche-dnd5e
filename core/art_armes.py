"""Dessins soignés (v53) des armes, des actions d'arme et des manœuvres du Maître de guerre : silhouettes pleines,
une idée par icône, sans médaillon. Grille 64 × 64, blanc = dessin, noir = découpe. Les armes sont dessinées
verticales (pointe en haut, autour de
l'origine) puis posées en diagonale."""
from __future__ import annotations

import math

W, K = "#FFFFFF", "#000000"


def P(d, col=W):
    return '<path d="{}" fill="{}"/>'.format(d, col)


def Cc(cx, cy, r, col=W):
    return '<circle cx="{:g}" cy="{:g}" r="{:g}" fill="{}"/>'.format(cx, cy, r, col)


def R(x, y, w, h, rx=0, col=W):
    return '<rect x="{:g}" y="{:g}" width="{:g}" height="{:g}" rx="{:g}" fill="{}"/>'.format(x, y, w, h, rx, col)


def L(pts, w=4.0, col=W):
    d = "M" + " L".join("{:g} {:g}".format(x, y) for x, y in pts)
    return ('<path d="{}" fill="none" stroke="{}" stroke-width="{}" stroke-linecap="round" '
            'stroke-linejoin="round"/>').format(d, col, w)


def S(d, w=4.0, col=W):
    return ('<path d="{}" fill="none" stroke="{}" stroke-width="{}" stroke-linecap="round" '
            'stroke-linejoin="round"/>').format(d, col, w)


def G(svg, x=32, y=32, a=0, s=1.0):
    return '<g transform="translate({:g} {:g}) rotate({:g}) scale({:g})">{}</g>'.format(x, y, a, s, svg)


def cut(svg, w=7):
    """Copie noire épaissie : détoure le dessin posé ensuite par-dessus un autre."""
    b = svg.replace('fill="#FFFFFF"', 'fill="#000000"').replace('stroke="#FFFFFF"', 'stroke="#000000"')
    return '<g stroke="#000000" stroke-width="{}" stroke-linejoin="round" stroke-linecap="round">{}</g>'.format(w, b)


def over(base, top, w=7):
    return base + cut(top, w) + top


def star4(cx, cy, r, col=W):
    q = r * 0.26
    pts = [(cx, cy - r), (cx + q, cy - q), (cx + r, cy), (cx + q, cy + q), (cx, cy + r), (cx - q, cy + q),
           (cx - r, cy), (cx - q, cy - q)]
    return P("M" + " L".join("{:g} {:g}".format(x, y) for x, y in pts) + " Z", col)


def speed(x, y, n=3, ln=12, gap=6, a=0, w=3.4):
    out = ""
    for i in range(n):
        dy = (i - (n - 1) / 2) * gap
        l = ln * (1 - 0.25 * abs(i - (n - 1) / 2))
        out += L([(0, dy), (l, dy)], w)
    return G(out, x, y, a)


# ============================================================ primitives verticales (origine = centre)
def blade_sword(blade=30, w=8.5, guard=20, grip=9, pommel=3.8, fuller=True, quillon_curve=0):
    t = -blade
    out = P("M0 {t} L{h} {t2} L{h} 0 L{mh} 0 L{mh} {t2} Z".format(t=t, t2=t + w * 1.1, h=w / 2, mh=-w / 2))
    if fuller:
        out += L([(0, t + w * 1.6), (0, -3)], 1.6, K)
    if quillon_curve:
        out += S("M{} {} Q0 4 {} {}".format(-guard / 2, -quillon_curve, guard / 2, -quillon_curve), 5)
    else:
        out += R(-guard / 2, 0, guard, 5.2, 2.4)
    out += R(-3, 4.6, 6, grip, 1.8) + Cc(0, 4.6 + grip + pommel - 0.6, pommel)
    return out


def shaft(top=-28, bottom=28, w=5.0):
    return R(-w / 2, top, w, bottom - top, w / 2)


def bow_v(h=50, depth=14):
    """Arc vertical, ventre vers la droite, corde à gauche (la flèche part vers la droite)."""
    half = h / 2
    limb = S("M0 {} C{} {} {} {} 0 {}".format(-half, depth * 1.4, -half * 0.55, depth * 1.4, half * 0.55, half), 4.8)
    tips = Cc(0, -half, 2.6) + Cc(0, half, 2.6)
    return limb + tips + L([(0, -half), (0, half)], 1.8) + R(depth * 1.05 - 3, -6, 6, 12, 2)


def arrow_h(x1, x2, y=0, head=7, w=3.2):
    return (L([(x1, y), (x2 - head + 1, y)], w) + P("M{} {} L{} {} L{} {} Z".format(x2, y, x2 - head, y - head * 0.6,
                                                                                     x2 - head, y + head * 0.6))
            + P("M{} {} l-6 -5 l3 0 l5 5 l-5 5 l-3 0 Z".format(x1 + 7, y)))


def crossbow_v(span=40, stock=46, heavy=False):
    arms = S("M{} {} Q0 {} {} {}".format(-span / 2, -stock / 2 + 14, -stock / 2 - 2, span / 2, -stock / 2 + 14),
             5.4 if heavy else 4.4)
    string = L([(-span / 2, -stock / 2 + 14), (0, -stock / 2 + 22), (span / 2, -stock / 2 + 14)], 1.8)
    body = R(-3.5, -stock / 2 + 4, 7, stock - 6, 3) + P("M-5 {} L5 {} L4 {} L-4 {} Z".format(
        stock / 2 - 14, stock / 2 - 14, stock / 2, stock / 2))
    bolt = L([(0, -stock / 2 - 2), (0, -stock / 2 + 22)], 2.6, K) + L([(0, -stock / 2 - 4), (0, -stock / 2 + 20)], 2.2)
    return arms + string + body + bolt


def axe_head(size=1.0, double=False):
    one = P("M2 -6 C10 -9 16 -16 18 -24 C22 -16 22 -2 18 8 C16 2 10 -2 2 0 Z")
    out = one
    if double:
        out += G(one, 0, 0, 0, 1).replace("<g transform=\"translate(0 0) rotate(0) scale(1)\">",
                                          "<g transform=\"scale(-1 1)\">")
    return G(out, 0, 0, 0, size)


def hammer_head(w=18, h=10, spike=False):
    out = R(-w / 2, -h / 2, w, h, 2) + R(-w / 2 - 1.5, -h / 2 + 1.5, 3, h - 3, 1)
    if spike:
        out += P("M{} -3 L{} 0 L{} 3 Z".format(-w / 2, -w / 2 - 9, -w / 2))
    return out


def spearhead(len_=14, w=8):
    return P("M0 {} C{} {} {} {} 0 0 C{} {} {} {} 0 {} Z".format(-len_, w / 2, -len_ * 0.6, w / 2, -len_ * 0.2,
                                                                  -w / 2, -len_ * 0.2, -w / 2, -len_ * 0.6, -len_))


def flame(cx, cy, s=1.0):
    d = ("M0 22 C-14 22 -18 8 -12 -2 C-10 4 -6 6 -5 3 C-8 -8 -2 -18 4 -26 C4 -16 10 -12 12 -4 "
         "C14 -8 14 -12 13 -15 C20 -6 20 6 16 13 C13 19 7 22 0 22 Z")
    return G(P(d), cx, cy, 0, s)


WEAPON_SCALE = 1.0                                     # armes : plus grandes dans la tuile


def diag(svg, s=1.0, x=32, y=32):
    return G(svg, x, y, 45, s * WEAPON_SCALE)



SWORD_SCALE = 1.0                                      # épées et dague : même échelle, longueurs réelles


def sized(svg, y=0):
    return G(svg, 32, 32, 45, SWORD_SCALE)


# ============================================================ armes
def w_epee_longue():
    return sized(G(blade_sword(38, 8.5, 22, 11, 3.8), 0, 6))


def w_epee_deux_mains():                               # ~ 1,80 m : la plus longue, grande garde, long manche
    return sized(G(blade_sword(50, 9.5, 28, 17, 4.4, quillon_curve=5), 0, 9))


def w_rapiere():
    hilt = S("M-9 2 C-12 10 -6 14 0 14 C6 14 12 10 9 2", 3) + R(-11, 0, 22, 3.6, 1.8)
    blade = P("M0 -40 L1.8 -36 L1.8 0 L-1.8 0 L-1.8 -36 Z")
    return diag(blade + hilt + R(-2.4, 3.6, 4.8, 10, 1.4) + Cc(0, 16, 3.2), 0.95, 32, 30)


def w_epee_courte():                                   # glaive : lame large et droite, garde courte
    blade = P("M0 -28 L5.5 -20 L5.5 0 L-5.5 0 L-5.5 -20 Z") + L([(0, -21), (0, -3)], 1.8, K)
    return sized(G(blade + R(-8, 0, 16, 5, 2.4) + R(-3, 5, 6, 8, 1.8) + Cc(0, 15.5, 4.4), 0, 2))


def w_cimeterre():
    blade = P("M-3 0 C-4 -12 -2 -26 8 -38 C6 -26 6 -12 4 0 Z")
    return diag(blade + R(-9, 0, 18, 4.4, 2.2) + R(-2.4, 4.4, 4.8, 9, 1.4) + P("M-2.4 13.4 L4 18 L2.4 13.4 Z"), 1.05,
                32, 32)


def w_dague():                                         # courte lame en feuille, garde recourbée, pommeau anneau
    blade = P("M0 -21 C5 -15 5.5 -6 3 0 L-3 0 C-5.5 -6 -5 -15 0 -21 Z")
    guard = S("M-8 -3.5 Q-7 1.5 0 1.5 Q7 1.5 8 -3.5", 3.4)
    ring = '<circle cx="0" cy="13" r="3.6" fill="none" stroke="#FFFFFF" stroke-width="2.8"/>'
    return sized(G(blade + guard + R(-2.2, 1.5, 4.4, 8, 1.3) + ring, 0, -1))


def w_hachette():
    return diag(shaft(-18, 18, 4) + G(axe_head(0.85), 0, -12), 1.15, 30, 32)


def w_hache_armes():
    return diag(shaft(-26, 26, 4.4) + G(axe_head(1.15), 0, -18), 0.95, 30, 32)


def w_grande_hache():
    return diag(shaft(-30, 30, 4.4) + G(axe_head(1.15, True), 0, -20) + P("M0 -36 L3 -28 L-3 -28 Z"), 0.86)


def w_marteau_leger():
    return diag(shaft(-14, 22, 4) + G(hammer_head(16, 10), 0, -16), 1.15, 32, 32)


def w_marteau_guerre():
    return diag(shaft(-20, 26, 4.4) + G(hammer_head(18, 12, True), 2, -22), 1.0, 32, 33)


def w_maillet():
    return diag(shaft(-20, 28, 4.8) + R(-15, -32, 30, 18, 3) + L([(-9, -32), (-9, -14)], 1.6, K)
                + L([(9, -32), (9, -14)], 1.6, K), 0.95, 32, 32)


def w_masse():
    head = P("M0 -36 L8 -28 L8 -16 L0 -10 L-8 -16 L-8 -28 Z") + L([(0, -33), (0, -13)], 1.8, K)
    return diag(shaft(-14, 26, 4.4) + head + Cc(0, 27, 3.4), 0.98, 32, 32)


def w_morgenstern():
    spikes = "".join(G(P("M0 -16 L3 -8 L-3 -8 Z"), 0, -24, a) for a in range(0, 360, 45))
    return diag(shaft(-14, 26, 4.4) + Cc(0, -24, 9.5) + spikes, 0.98, 32, 32)


def w_gourdin():
    return diag(P("M-2.5 24 L-6 -18 C-6 -28 6 -28 6 -18 L2.5 24 Z") + R(-3.5, 20, 7, 6, 2), 1.0, 32, 32)


def w_massue():
    club = P("M-3 26 L-10 -14 C-12 -30 12 -30 10 -14 L3 26 Z")
    knobs = Cc(-9, -10, 3) + Cc(9, -16, 3) + Cc(-6, -24, 3) + Cc(8, -2, 2.6)
    return diag(club + knobs + Cc(-3, -14, 1.6, K) + Cc(3, -6, 1.6, K), 0.98, 32, 32)


def w_fleau():
    handle = G(R(-3, -16, 6, 32, 3) + R(-4.5, 14, 9, 4.5, 2), 16, 42, 20)
    top = (16 + 16 * math.sin(math.radians(20)), 42 - 16 * math.cos(math.radians(20)))
    ring = '<circle cx="{:g}" cy="{:g}" r="3.4" fill="none" stroke="#FFFFFF" stroke-width="2.6"/>'.format(*top)
    links, (x, y) = "", top
    for i in range(3):                                 # maillons bien séparés, alternés
        x, y = x + 6.5, y - 1.2
        if i % 2 == 0:
            links += '<ellipse cx="{:g}" cy="{:g}" rx="4.4" ry="2.8" fill="none" stroke="#FFFFFF" stroke-width="2.4"/>'.format(x, y)
        else:
            links += R(x - 4.4, y - 1.3, 8.8, 2.6, 1.3)
    bx, by = x + 12, y - 2
    ball = Cc(bx, by, 8.5) + "".join(G(P("M0 -14 L2.8 -6.5 L-2.8 -6.5 Z"), bx, by, a) for a in range(0, 360, 60))
    return handle + ring + links + ball


def w_pic():
    head = P("M-2 -26 C-10 -26 -20 -22 -26 -14 C-16 -18 -8 -19 -2 -19 Z") + R(-3.5, -29, 9, 11, 2)
    return diag(shaft(-26, 26, 4.4) + head, 0.98, 33, 32)


def w_lance():
    return diag(shaft(-18, 30, 3.6) + G(spearhead(18, 9), 0, -18), 0.95, 32, 32)


def w_pique():
    return diag(shaft(-24, 34, 3.4) + G(spearhead(12, 6.5), 0, -24), 0.88, 32, 32)


def w_hallebarde():
    blade = P("M2 -26 C10 -28 15 -24 17 -16 C16 -8 10 -6 2 -8 Z")
    hook = P("M-2 -20 L-10 -16 L-2 -14 Z")
    return diag(shaft(-26, 32, 3.6) + G(spearhead(12, 6), 0, -26) + blade + hook, 0.86, 31, 32)


def w_coutille():
    blade = P("M-2 -10 L-2 -28 C2 -38 8 -42 10 -42 C8 -30 6 -18 2 -10 Z")
    return diag(shaft(-12, 30, 3.6) + blade + R(-5, -12, 10, 3.6, 1.8), 0.9, 32, 32)


def w_trident():
    prongs = S("M-10 -34 L-10 -22 Q-10 -16 0 -16 Q10 -16 10 -22 L10 -34", 3.8) + L([(0, -38), (0, -16)], 3.8)
    tips = P("M0 -42 L3 -36 L-3 -36 Z") + P("M-10 -38 L-7 -32 L-13 -32 Z") + P("M10 -38 L13 -32 L7 -32 Z")
    return diag(shaft(-16, 30, 3.8) + prongs + tips, 0.9, 32, 32)


def w_lance_arcon():
    return diag(P("M0 -36 L5 -4 L-5 -4 Z") + P("M-10 -4 C-8 2 8 2 10 -4 Z") + R(-2.4, -2, 4.8, 24, 2), 1.0, 32, 30)


def w_javeline():
    return diag(shaft(-12, 22, 3.2) + G(spearhead(12, 7), 0, -12), 1.0, 30, 34) + speed(8, 50, 3, 10, 5, -45, 3)


def w_arc_court():
    return G(G(bow_v(36, 9), 24, 32, 0) + arrow_h(20, 50, 32, 7, 2.8), 32, 32, 0, 0.8).replace('translate(32 32)', 'translate(6.4 6.4)')


def w_arc_long():
    return G(G(bow_v(60, 13), 20, 32, 0) + arrow_h(16, 60, 32, 8, 3), 32, 32, 0, 0.8).replace('translate(32 32)', 'translate(6.4 6.4)')


def w_arbalete_legere():
    return G(crossbow_v(36, 42), 32, 33, 0, 0.8)


def w_arbalete_lourde():                               # plus grande : arc épais, grand étrier à l'avant, manivelle
    base = crossbow_v(52, 50, True)
    stirrup = '<path d="M-7 -24 L-7 -33 Q-7 -39 0 -39 Q7 -39 7 -33 L7 -24" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
    crank = R(-13, 16, 26, 4.4, 2) + Cc(-13, 18, 3.8) + Cc(13, 18, 3.8)
    return G(base + stirrup + crank, 32, 35, 0, 0.8)


def w_arbalete_poing():                                # vue de profil, petite, crosse de pistolet
    stock = P("M8 26 H48 C51 26 52 28 52 30 V32 H30 L28 36 C27 44 25 50 20 54 L12 52 C16 46 18 40 18 34 H8 Z")
    limb = S("M48 14 C54 20 54 40 48 46", 4.2) + L([(48, 14), (40, 30), (48, 46)], 1.6)
    bolt = R(14, 22, 38, 2.6, 1.2) + P("M56 23.3 L50 20 L50 26.6 Z")
    trigger = S("M26 34 C26 38 29 40 31 39", 2.2)
    return stock + limb + bolt + trigger


def w_fronde():
    cord = S("M10 8 C14 30 26 44 32 44 C38 44 50 30 54 8", 3)
    pouch = P("M24 42 C26 50 38 50 40 42 C36 46 28 46 24 42 Z") + Cc(32, 38, 6)
    return cord + pouch + Cc(10, 8, 3.4) + Cc(54, 8, 3.4)


def w_flechette():
    dart = P("M0 -24 L3 -14 L3 8 L-3 8 L-3 -14 Z") + P("M-3 8 L-9 18 L-3 15 Z") + P("M3 8 L9 18 L3 15 Z") + R(-1.2, 8, 2.4, 10)
    return diag(dart, 1.15, 34, 30) + speed(8, 48, 3, 10, 5, -45, 3)


def w_sarbacane():
    tube = diag(R(-4, -10, 8, 46, 4) + R(-5.5, 28, 11, 6, 2), 1.0, 26, 38)
    return tube + P("M50 14 l6 -6 l1 4 l-5 5 Z") + Cc(46, 18, 2.4) + Cc(41, 22, 1.6)


def w_fouet():
    handle = G(R(-3.5, -12, 7, 22, 3) + R(-5, 8, 10, 4, 2), 16, 46, 35)
    lash = S("M22 38 C34 26 52 30 52 18 C52 8 40 6 36 14 C33 20 40 24 44 20", 3.2)
    return handle + lash


def w_filet():
    ring = '<circle cx="32" cy="32" r="25" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
    mesh = '<g stroke="#FFFFFF" stroke-width="2.2">' + "".join(
        '<line x1="{0}" y1="8" x2="{0}" y2="56"/><line x1="8" y1="{0}" x2="56" y2="{0}"/>'.format(v)
        for v in (18, 25, 32, 39, 46)) + "</g>"
    clip = '<clipPath id="netc"><circle cx="32" cy="32" r="24"/></clipPath>'
    weights = "".join(Cc(32 + 25 * math.cos(a), 32 + 25 * math.sin(a), 3.4) for a in [k * math.pi / 3 for k in range(6)])
    return clip + '<g clip-path="url(#netc)">' + mesh + "</g>" + ring + weights


def w_faucille():
    blade = P("M22 46 C42 46 58 34 58 18 C58 8 50 2 38 4 C48 9 51 15 50 21 C48 33 38 40 22 40 Z")
    return blade + G(R(-3.5, -12, 7, 24, 3), 16, 50, -40)


def w_baton():
    staff = diag(R(-3, -32, 6, 64, 3), 0.95)
    bands = diag(R(-3.6, -20, 7.2, 3, 1, K) + R(-3.6, 17, 7.2, 3, 1, K), 0.95)
    return staff + bands


def w_mains_nues():                                    # poing fermé, vu de face, petit éclat d'impact
    fingers = "".join(R(x, 12, 9.5, 18, 4.6) for x in (14, 23.5, 33, 42.5))
    palm = P("M14 24 H52 V40 C52 48 46 54 38 54 H26 C19 54 14 48 14 40 Z")
    gaps = "".join(L([(x, 14), (x, 27)], 1.8, K) for x in (23.5, 33, 42.5))
    thumb = P("M10 30 C10 26 13 24 17 25 L38 30 C41 31 42 35 39 37 L18 38 C13 38 10 35 10 30 Z")
    thumb_cut = S("M17 25 L38 30 C41 31 42 35 39 37 L18 38", 2.2, K)
    wrist = R(22, 52, 22, 9, 3)
    impact = L([(54, 8), (58, 4)], 2.8) + L([(57, 14), (62, 13)], 2.8) + L([(50, 5), (51, 0)], 2.8)
    return fingers + palm + gaps + thumb_cut + thumb + wrist + impact


def w_bouclier():
    outer = P("M32 5 L54 12 V30 C54 45 45 54 32 60 C19 54 10 45 10 30 V12 Z")
    ring = P("M32 11 L49 16.5 V30 C49 41.5 42 49 32 54 C22 49 15 41.5 15 30 V16.5 Z", K)
    inner = P("M32 15 L45 19.5 V30 C45 39 39.5 45.5 32 49.5 C24.5 45.5 19 39 19 30 V19.5 Z")
    return outer + ring + inner + Cc(32, 31, 6, K) + Cc(32, 31, 3.6)


def w_pistolet():                                      # pistolet à silex
    barrel = R(26, 19, 32, 6.4, 3) + R(56, 17.6, 6, 9.2, 2.2)                 # canon rond, bague de bouche
    fore = P("M26 25 H52 C54 25 55 26.5 54 28 H26 Z")                           # fût sous le canon
    lock = P("M18 16 H30 V30 H18 Z")                                             # platine
    grip = P("M30 26 L30 30.5 C26.5 34 23 40 20.5 47 C19 51.5 15 54.5 10.5 53.5 C6 52.5 5 48 7 44 C11 37 14 29 16.5 20 L18 16 Z")
    pommel = Cc(9, 50.5, 5) + Cc(9, 50.5, 2.2, K) + Cc(9, 50.5, 1.2)
    cock = P("M21 17 C19 11 15 9 11 7 C13 5 17 5 20 7 C23 9 25 13 24 17 Z")    # chien en col de cygne
    frizzen = R(27, 11, 4, 7, 1.2)
    guard = S("M22 30 C21 38 33 39 32 30", 2.6)
    trigger = S("M26 30 C26 33 28 34 29 33", 2)
    cuts = (L([(26, 25), (52, 25)], 1.4, K) + L([(44, 19), (44, 25.4)], 1.4, K) + Cc(24, 23, 1.8, K)
            + L([(18, 16), (30, 16)], 1.2, K))
    return G(G(barrel + fore + lock + grip + pommel + cock + frizzen + guard + trigger + cuts, -32, -32), 32, 32, -12)


def w_mousquet():                                      # mousquet à silex : longue crosse, plaque de couche
    barrel = R(30, 23, 33, 3.8, 1.8) + R(61, 22.2, 3, 5.4, 1)
    fore = P("M28 26.8 H58 C59.5 26.8 59.5 29.4 58 29.4 H28 Z")
    bands = "".join(R(x, 22, 2.2, 8, 0.8) for x in (40, 51))
    band_cuts = "".join(L([(x - 0.5, 22), (x - 0.5, 30)], 0.9, K) + L([(x + 2.7, 22), (x + 2.7, 30)], 0.9, K)
                        for x in (40, 51))
    lock = P("M21 21.5 H30 V30.5 H21 Z")
    butt = P("M21 21.5 L2 25 C0.5 25.3 0 26 0 27.2 L0 40 C0 41.5 1.2 42.2 2.5 41.4 C9 37.5 15 34 21 31.5 Z")
    plate = R(0, 25, 2.6, 17, 1, K) + R(0, 25.6, 1.6, 15.8, 0.8)
    comb = L([(4, 27.5), (19, 24)], 1.2, K)
    cock = P("M23 22 C21.5 17.5 18.5 15.5 15.5 14.5 C17.5 12.6 20.5 12.6 22.5 14.2 C25 16 26 19 26 22 Z")
    frizzen = R(27.5, 17.2, 3, 5.4, 1)
    guard = S("M21 30.5 C20 36 28 37 28 30.5", 2.2)
    cuts = L([(28, 26.8), (58, 26.8)], 1.1, K) + L([(21, 21.5), (30, 21.5)], 0.9, K)
    body = barrel + fore + bands + band_cuts + lock + butt + plate + comb + cock + frizzen + guard + cuts
    return G(G(body, -32, -32), 32, 32, -32)


FIXED = "<!-- TAILLE_FIXE -->"                         # ui/icons : pas de recadrage, tailles comparables

SIZED = {"Épée à deux mains", "Épée longue", "Épée courte", "Dague", "Arc court", "Arc long", "Arbalète légère",
         "Arbalète lourde"}

WEAPONS = {"Épée longue": w_epee_longue, "Épée à deux mains": w_epee_deux_mains, "Rapière": w_rapiere,
           "Épée courte": w_epee_courte, "Cimeterre": w_cimeterre, "Dague": w_dague, "Hachette": w_hachette,
           "Hache d'armes": w_hache_armes, "Grande hache": w_grande_hache, "Marteau léger": w_marteau_leger,
           "Marteau de guerre": w_marteau_guerre, "Maillet d'armes": w_maillet, "Masse d'armes": w_masse,
           "Morgenstern": w_morgenstern, "Gourdin": w_gourdin, "Massue": w_massue, "Fléau d'armes": w_fleau,
           "Pic de guerre": w_pic, "Lance": w_lance, "Pique": w_pique, "Hallebarde": w_hallebarde,
           "Coutille": w_coutille, "Trident": w_trident, "Lance d'arçon": w_lance_arcon, "Javeline": w_javeline,
           "Arc court": w_arc_court, "Arc long": w_arc_long, "Arbalète légère": w_arbalete_legere,
           "Arbalète lourde": w_arbalete_lourde, "Arbalète de poing": w_arbalete_poing, "Fronde": w_fronde,
           "Fléchette": w_flechette, "Sarbacane": w_sarbacane, "Fouet": w_fouet, "Filet": w_filet,
           "Faucille": w_faucille, "Bâton": w_baton, "Mains nues": w_mains_nues, "Bouclier": w_bouclier,
           "Pistolet": w_pistolet, "Mousquet": w_mousquet}


# ============================================================ motifs d'action
def sword(x=32, y=32, a=45, s=1.0):
    return G(blade_sword(30, 7.5, 20, 9, 3.6), x, y, a, s)


def dagger(x=32, y=32, a=45, s=1.0):
    return G(P("M0 -22 C5 -16 5 -6 3.5 0 L-3.5 0 C-5 -6 -5 -16 0 -22 Z") + R(-8, 0, 16, 4, 2) + R(-2.2, 4, 4.4, 8, 1.3)
             + Cc(0, 14.5, 3), x, y, a, s)


def hammer(x=32, y=32, a=45, s=1.0):
    return G(shaft(-14, 22, 4.2) + G(hammer_head(18, 11), 0, -16), x, y, a, s)


def arrow(x1, y1, x2, y2, w=3.6, head=8):
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    px, py = -math.sin(ang) * head * 0.62, math.cos(ang) * head * 0.62
    return L([(x1, y1), (bx, by)], w) + P("M{:g} {:g} L{:g} {:g} L{:g} {:g} Z".format(x2, y2, bx + px, by + py, bx - px, by - py))


def curved_arrow(d, end, ang, w=4, head=8):
    ex, ey = end
    a = math.radians(ang)
    bx, by = ex - head * math.cos(a), ey - head * math.sin(a)
    px, py = -math.sin(a) * head * 0.62, math.cos(a) * head * 0.62
    return S(d, w) + P("M{:g} {:g} L{:g} {:g} L{:g} {:g} Z".format(ex, ey, bx + px, by + py, bx - px, by - py))


def skull(x=32, y=30, s=1.0):
    return G(P("M0 -18 C11 -18 18 -10 18 -1 C18 6 14 9 12 11 L12 17 L-12 17 L-12 11 C-14 9 -18 6 -18 -1 "
               "C-18 -10 -11 -18 0 -18 Z") + Cc(-7, -1, 4.6, K) + Cc(7, -1, 4.6, K) + P("M0 5 L3 10 L-3 10 Z", K)
             + R(-6, 13, 2, 4, 0, K) + R(-1, 13, 2, 4, 0, K) + R(4, 13, 2, 4, 0, K), x, y, 0, s)


def eye(x=32, y=32, s=1.0, closed=False):
    if closed:
        return G(S("M-26 -2 C-14 12 14 12 26 -2", 4.2) + "".join(L([(px, py), (px + dx, py + 8)], 3)
                                                                  for px, py, dx in ((-14, 6, -3), (0, 9, 0), (14, 6, 3))), x, y, 0, s)
    return G(P("M-28 0 C-16 -16 16 -16 28 0 C16 16 -16 16 -28 0 Z") + Cc(0, 0, 10, K) + Cc(0, 0, 7) + Cc(0, 0, 3, K),
             x, y, 0, s)


def heart(x=32, y=32, s=1.0):
    return G(P("M0 22 C-16 10 -24 2 -24 -8 C-24 -16 -18 -21 -11 -21 C-6 -21 -2 -18 0 -14 C2 -18 6 -21 11 -21 "
               "C18 -21 24 -16 24 -8 C24 2 16 10 0 22 Z"), x, y, 0, s)


def shield(x=32, y=32, s=1.0):
    return G(P("M0 -26 L20 -19 V-2 C20 12 12 21 0 27 C-12 21 -20 12 -20 -2 V-19 Z")
             + P("M0 -20 L15 -15 V-2 C15 9 9 16 0 21 C-9 16 -15 9 -15 -2 V-15 Z", K)
             + P("M0 -16 L12 -12 V-2 C12 7 7 13 0 17 C-7 13 -12 7 -12 -2 V-12 Z"), x, y, 0, s)


def boot(x=32, y=32, s=1.0):
    return G(P("M-12 -24 H4 V2 L18 8 C24 11 24 18 18 18 H-14 C-16 18 -16 16 -15 14 Z") + R(-16, 14, 38, 4, 0, K), x, y, 0, s)


def fist(x=32, y=32, s=1.0):
    return G(R(-16, -6, 32, 24, 7) + R(-14, -14, 8, 14, 4) + R(-6, -16, 8, 14, 4) + R(2, -15, 8, 14, 4)
             + R(10, -12, 7, 13, 3.5) + P("M-16 6 C-22 6 -24 0 -20 -4 L-12 -6 Z")
             + L([(-6, -2), (-6, 2)], 1.6, K) + L([(2, -2), (2, 2)], 1.6, K) + L([(10, -1), (10, 3)], 1.6, K), x, y, 0, s)


def hand(x=32, y=32, s=1.0, a=0):
    return G(R(-14, -4, 26, 26, 8) + R(-14, -22, 6, 22, 3) + R(-7, -26, 6, 26, 3) + R(0, -25, 6, 25, 3)
             + R(7, -20, 6, 20, 3) + P("M12 6 L22 -6 C25 -8 28 -5 26 -2 L14 14 Z"), x, y, a, s)


def crown(x=32, y=32, s=1.0):
    return G(P("M-22 10 L-24 -14 L-11 -2 L0 -18 L11 -2 L24 -14 L22 10 Z") + R(-22, 12, 44, 7, 2)
             + Cc(-24, -16, 3) + Cc(0, -20, 3) + Cc(24, -16, 3), x, y, 0, s)


def chain(x1, y1, x2, y2, n=4):
    out = ""
    for i in range(n):
        t = (i + 0.5) / n
        cx, cy = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) + (0 if i % 2 else 0)
        rx, ry = (6, 3.4) if i % 2 == 0 else (6, 1.6)
        out += ('<ellipse cx="{:g}" cy="{:g}" rx="{}" ry="{}" fill="none" stroke="#FFFFFF" stroke-width="2.8" '
                'transform="rotate({:g} {:g} {:g})"/>').format(cx, cy, rx, ry, ang, cx, cy)
    return out


def target(x=32, y=32, s=1.0):
    return G('<circle r="24" fill="#FFFFFF"/><circle r="18" fill="#000000"/><circle r="13" fill="#FFFFFF"/>'
             '<circle r="7.5" fill="#000000"/><circle r="3.5" fill="#FFFFFF"/>', x, y, 0, s)


def burst(x, y, r, n=8):
    pts = []
    for k in range(2 * n):
        a = math.pi * k / n - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return P("M" + " L".join("{:g} {:g}".format(*p) for p in pts) + " Z")


def slashes(x=32, y=32, s=1.0, n=3):
    out = ""
    for i in range(n):
        dx = (i - (n - 1) / 2) * 13
        out += P("M{a} -26 C{b} -10 {c} 8 {d} 26 C{e} 10 {f} -8 {a} -26 Z".format(
            a=dx + 10, b=dx + 6, c=dx - 2, d=dx - 10, e=dx + 3, f=dx + 9))
    return G(out, x, y, 0, s)


def hourglass(x=32, y=32, s=1.0):
    return G(R(-16, -26, 32, 5, 2) + R(-16, 21, 32, 5, 2) + P("M-12 -21 H12 C12 -10 3 -4 3 0 C3 4 12 10 12 21 H-12 "
                                                              "C-12 10 -3 4 -3 0 C-3 -4 -12 -10 -12 -21 Z")
             + P("M-7 -16 H7 C7 -11 2 -7 0 -5 C-2 -7 -7 -11 -7 -16 Z", K) + P("M-8 18 H8 C6 13 2 11 0 11 C-2 11 -6 13 -8 18 Z", K),
             x, y, 0, s)


def banner(x=32, y=32, s=1.0):
    return G(R(-18, -28, 4, 58, 2) + P("M-14 -26 H20 L14 -16 L20 -6 H-14 Z") + Cc(-16, -29, 3.4), x, y, 0, s)


def bubble(x=32, y=32, s=1.0):
    return G(P("M-24 -20 H24 C28 -20 30 -18 30 -14 V6 C30 10 28 12 24 12 H-4 L-16 24 V12 H-24 C-28 12 -30 10 -30 6 "
               "V-14 C-30 -18 -28 -20 -24 -20 Z"), x, y, 0, s)


def footprint(x, y, a=0, s=1.0):
    return G(P("M0 -12 C5 -12 6 -4 5 2 C4 8 -4 8 -5 2 C-6 -4 -5 -12 0 -12 Z") + Cc(-1, 10, 4), x, y, a, s)


def helm(x=32, y=32, s=1.0):
    return G(P("M0 -24 C14 -24 22 -14 22 0 V16 L10 22 V8 H-10 V22 L-22 16 V0 C-22 -14 -14 -24 0 -24 Z")
             + R(-16, -2, 32, 4.6, 1, K) + R(-2, -24, 4, 22, 0, K), x, y, 0, s)


def horn(x=32, y=32, s=1.0):
    body = P("M-26 14 C-14 12 2 2 12 -12 L20 -22 C24 -14 28 -6 30 4 L18 2 C8 12 -8 22 -24 24 Z")
    bell = '<ellipse cx="25" cy="-9" rx="5" ry="14" transform="rotate(25 25 -9)" fill="#000000"/>'
    rim = '<ellipse cx="25" cy="-9" rx="3" ry="11" transform="rotate(25 25 -9)" fill="#FFFFFF"/>'
    bands = L([(-10, 9), (-6, 19)], 2.2, K) + L([(2, 2), (8, 12)], 2.2, K)
    return G(body + bell + rim + bands + R(-30, 12, 8, 14, 3), x, y, 0, s)


def magnifier(x=32, y=32, s=1.0):
    return G('<circle cx="-4" cy="-4" r="14" fill="none" stroke="#FFFFFF" stroke-width="5.5"/>'
             + G(R(-3.5, 0, 7, 20, 3.5), 8, 8, -45), x, y, 0, s)


def crack(x, y, s=1.0):
    return G(L([(0, -16), (-4, -6), (3, 0), (-3, 9), (2, 16)], 3.2) + L([(3, 0), (12, -4)], 2.6) + L([(-4, -6), (-12, -9)], 2.6),
             x, y, 0, s)


def down_arrow(x, y, s=1.0):
    return G(R(-4, -16, 8, 18, 2) + P("M-11 2 H11 L0 16 Z"), x, y, 0, s)


def spin(x=32, y=32, r=24, w=4):
    a1 = curved_arrow("M{} {} A{} {} 0 0 1 {} {}".format(x - r, y, r, r, x + r * 0.7, y - r * 0.7),
                      (x + r * 0.7, y - r * 0.7), 45, w)
    a2 = curved_arrow("M{} {} A{} {} 0 0 1 {} {}".format(x + r, y, r, r, x - r * 0.7, y + r * 0.7),
                      (x - r * 0.7, y + r * 0.7), 225, w)
    return a1 + a2


def figure(x=32, y=32, s=1.0, a=0):
    return G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), x, y, a, s)


# ============================================================ actions d'arme (bottes, actions façon BG3)
ACTIONS = {
    "Coup double": lambda: sword(24, 32, 30, 0.95) + over("", sword(40, 32, 30, 0.95), 0) + star4(54, 52, 4),
    "Écorchure": lambda: over(sword(28, 36, 45, 0.95), slashes(46, 20, 0.45)),
    "Enchaînement": lambda: sword(20, 40, 45, 0.8) + chain(30, 30, 46, 14, 3) + sword(48, 22, 45, 0.55),
    "Ouverture": lambda: G(P("M0 -26 L20 -19 V-2 C20 12 12 21 0 27 C-12 21 -20 12 -20 -2 V-19 Z"), 26, 34, 0, 0.95)
                         + L([(26, 8), (22, 22), (30, 32), (24, 46), (28, 60)], 4.2, K) + arrow(36, 30, 60, 30),
    "Poussée": lambda: over(shield(24, 32, 0.95), arrow(30, 32, 60, 32, 5, 11)) + speed(4, 32, 3, 8, 7, 0, 2.6),
    "Ralentissement": lambda: over(boot(30, 30, 0.95), chain(14, 52, 50, 52, 5)),
    "Renversement": lambda: G(figure(0, 0, 1.0), 26, 30, -60) + curved_arrow("M44 10 C58 18 58 36 48 46", (48, 46), 120, 4),
    "Sape": lambda: over(hammer(26, 26, -30, 0.95), crack(46, 46, 0.9)),
    "Frappe du pommeau": lambda: over(G(blade_sword(30, 7.5, 20, 9, 3.6), 30, 26, 200, 0.95), burst(46, 50, 10)),
    "Lacération (entaille)": lambda: slashes(32, 32, 1.0),
    "Fauchage": lambda: over(G(blade_sword(30, 7.5, 20, 9, 3.6), 30, 28, 100, 0.9),
                             curved_arrow("M10 54 Q32 64 54 54", (54, 54), -20, 3.4)) + footprint(32, 50, 0, 0.6),
    "Perçage (frappe perforante)": lambda: over(shield(38, 32, 0.9), G(R(-2.2, -30, 4.4, 60, 2) + G(spearhead(14, 9), 0, -30),
                                                                         28, 34, 60, 0.95)),
    "Préparation": lambda: over(hourglass(24, 32, 0.9), sword(44, 32, 30, 0.8)),
    "Brise-crâne (frappe commotionnante)": lambda: over(skull(28, 38, 0.9), hammer(44, 18, 40, 0.75)) + star4(10, 12, 4),
    "Frappe affaiblissante": lambda: over(fist(28, 34, 0.9), down_arrow(50, 22, 0.85)),
    "Moulinet de taille (Fendoir)": lambda: over(spin(32, 32, 25, 3.6), G(axe_head(1.0), 32, 30, 0)
                                                 + G(shaft(-6, 14, 4), 32, 30, 0)),
    "Charge": lambda: boot(36, 30, 0.95) + speed(2, 30, 3, 14, 8, 0, 3.6),
    "Tir handicapant": lambda: over(boot(28, 32, 0.9), arrow(62, 4, 32, 34, 3.2, 9)),
    "Tir mobile": lambda: figure(22, 34, 0.9, 15) + arrow(32, 24, 62, 14, 3.2, 9) + speed(2, 44, 2, 10, 7, 0, 3),
    "Tir perforant": lambda: over(shield(32, 32, 0.85), arrow(4, 32, 62, 32, 3.4, 10)),
    "Ténacité": lambda: over(shield(28, 32, 1.0), fist(44, 44, 0.55)),
    "Désarmement": lambda: hand(22, 40, 0.85) + G(blade_sword(30, 7.5, 20, 9, 3.6), 46, 20, 150, 0.7)
                           + curved_arrow("M28 14 C34 6 42 4 50 6", (50, 6), 10, 3),
    "Briseur de dos": lambda: over(hammer(26, 24, -45, 0.9), crack(46, 44, 0.9)) + R(30, 56, 30, 4, 2),
    "Arrêt-cœur": lambda: over(heart(28, 36, 0.95), G(blade_sword(30, 7.5, 20, 9, 3.6), 40, 26, 225, 0.75)),
    "Moulinet": lambda: over(spin(32, 32, 25, 3.6), sword(32, 32, 45, 0.7)),
    "Coup cinglant": lambda: S("M8 54 C16 40 30 44 38 30 C44 20 56 22 58 10", 3.6) + burst(58, 10, 7, 6)
                             + G(R(-3.5, -10, 7, 18, 3), 8, 54, 40),
    "Bousculer": lambda: hand(36, 32, 0.95, 90) + speed(4, 32, 3, 10, 8, 0, 3),
    "Lutte": lambda: over(hand(24, 34, 0.75, 70), hand(42, 30, 0.75, -110)),
}


# ============================================================ manœuvres du Maître de guerre
MANEUVERS = {
    "Attaque menaçante": lambda: over(sword(30, 34, 45, 1.0), skull(42, 22, 0.6)),
    "Attaque précise": lambda: over(target(26, 38, 0.95), G(blade_sword(30, 7.5, 20, 9, 3.6), 42, 22, 225, 0.75)),
    "Attaque repoussante": lambda: over(sword(24, 38, 45, 0.85), curved_arrow("M30 22 C40 10 54 10 60 20", (60, 20), 60, 4)),
    "Attaque avec feinte": lambda: over(sword(30, 34, 45, 1.0),
                                        G(P("M-22 -4 C-16 -12 -6 -10 0 -4 C6 -10 16 -12 22 -4 C20 6 8 8 0 2 C-8 8 -20 6 -22 -4 Z")
                                          + '<ellipse cx="-10" cy="-3" rx="4.5" ry="2.6" fill="#000000"/>'
                                            '<ellipse cx="10" cy="-3" rx="4.5" ry="2.6" fill="#000000"/>', 40, 22, 0, 0.85)),
    "Croc-en-jambe": lambda: G(boot(0, 0, 1.0), 26, 30, -25) + curved_arrow("M10 56 Q34 62 56 48", (56, 48), -35, 3.6),
    "Désarmement": lambda: hand(22, 40, 0.85) + G(blade_sword(30, 7.5, 20, 9, 3.6), 46, 20, 150, 0.7)
                           + curved_arrow("M28 14 C34 6 42 4 50 6", (50, 6), 10, 3),
    "Distraction": lambda: over(eye(30, 30, 0.95), G(star4(0, 0, 9) + star4(10, -10, 5), 46, 48)),
    "Fente": lambda: G(blade_sword(30, 7.5, 20, 9, 3.6), 40, 32, 90, 0.95) + speed(2, 32, 3, 12, 9, 0, 3.4),
    "Jeu de jambes": lambda: footprint(22, 40, -15, 1.0) + footprint(42, 24, 15, 1.0)
                             + curved_arrow("M10 18 Q18 6 30 8", (30, 8), 0, 3),
    "Manœuvre tactique": lambda: over(G(banner(0, 0, 0.9), 22, 32), arrow(30, 46, 60, 46, 4, 9)),
    "Parade": lambda: sword(32, 34, 45, 0.95) + over("", sword(32, 34, -45, 0.95), 0) + burst(32, 18, 8, 6),
    "Provocation": lambda: over(bubble(32, 28, 0.95), R(29, 12, 6, 14, 3, K)) + Cc(32, 33, 3.4, K),
    "Ralliement": lambda: over(banner(28, 32, 1.0), heart(48, 46, 0.42)),
    "Riposte": lambda: over(sword(28, 36, 45, 0.9), curved_arrow("M46 46 C60 36 58 16 44 10", (44, 10), 200, 3.6)),
    "Attaque balayage": lambda: sword(22, 42, 60, 0.8) + curved_arrow("M10 26 C18 8 46 4 58 20", (58, 20), 50, 4.2)
                                + S("M14 34 C22 18 42 14 52 24", 2.4),
    "Commandement": lambda: horn(32, 34, 1.0) + G(L([(0, 0), (8, -6)], 3) + L([(2, 8), (12, 6)], 3) + L([(0, -10), (6, -18)], 3), 50, 18),
    "Embuscade": lambda: over(eye(30, 22, 0.85, True), dagger(34, 42, 45, 0.9)),
    "Échange de position": lambda: figure(16, 34, 0.75) + figure(48, 34, 0.75)
                                   + curved_arrow("M20 12 Q32 2 44 12", (44, 12), 40, 3.2)
                                   + curved_arrow("M44 56 Q32 64 20 56", (20, 56), 220, 3.2),
    "Garde préparée": lambda: over(sword(36, 30, -45, 0.85), shield(26, 34, 0.9)),
    "Présence imposante": lambda: helm(32, 36, 0.95) + "".join(
        G(R(-1.8, -30, 3.6, 7, 1.8), 32, 36, a) for a in (-60, -30, 0, 30, 60)),
    "Frappe agrippante": lambda: over(fist(26, 30, 0.9), chain(36, 44, 58, 58, 3)),
    "Lancer rapide": lambda: dagger(40, 26, 45, 0.95) + speed(4, 48, 3, 14, 7, -45, 3.2),
    "Évaluation tactique": lambda: over(target(26, 28, 0.75), magnifier(40, 40, 0.95)),
}


def weapon_art(name: str):
    """Dessin d'une arme par son nom (WEAPONS), marqué TAILLE_FIXE pour les armes comparées entre elles."""
    fn = WEAPONS.get(name)
    if fn is None:
        return None
    return fn() + (FIXED if name in SIZED else "")
