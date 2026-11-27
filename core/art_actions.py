"""
Dessins soignés (v53) des actions communes de l'onglet « En partie » et des capacités de classe les plus
fréquentes — même grammaire que core/art_armes : silhouettes pleines, une idée par icône, découpes noires
franches, quelques éclats. Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

from .art_armes import (Cc, G, K, L, P, R, S, arrow, blade_sword, boot, bubble, burst, curved_arrow, dagger, eye, fist, hand, heart, hourglass, magnifier, over, shield, skull, speed, star4, sword, target)


# ------------------------------------------------------------------------------------------------ motifs
def runner(x=32, y=32, s=1.0, a=0):
    """Silhouette qui court, penchée vers l'avant."""
    body = (Cc(6, -22, 6)
            + P("M-2 -14 C2 -16 8 -15 10 -11 L14 -2 L22 2 C25 3 24 8 21 7 L11 3 L8 -2 L5 8 L12 14 L14 26 "
                "C14 30 9 30 9 27 L7 17 L-1 11 L-6 20 L-16 24 C-19 25 -21 21 -18 19 L-10 15 L-6 4 L-4 -6 "
                "L-12 -2 L-16 6 C-17 9 -22 8 -21 5 L-17 -5 C-15 -9 -8 -13 -2 -14 Z"))
    return G(body, x, y, a, s)


def hood(x=32, y=32, s=1.0):
    """Capuche pointue, visage dans l'ombre, regard clos."""
    cape = P("M0 -30 C6 -22 20 -16 22 0 C24 14 20 24 14 30 H-14 C-20 24 -24 14 -22 0 C-20 -16 -6 -22 0 -30 Z")
    face = P("M0 -14 C-9 -14 -13 -6 -13 2 C-13 9 -9 14 -5 16 H5 C9 14 13 9 13 2 C13 -6 9 -14 0 -14 Z", K)
    eyes = S("M-9 0 Q-5.5 3.5 -2 0", 2.4) + S("M2 0 Q5.5 3.5 9 0", 2.4)
    return G(cape + face + eyes, x, y, 0, s)


def broken_chain():
    def link(cx, cy, a):
        return ('<g transform="translate({} {}) rotate({})"><rect x="-11" y="-6.5" width="22" height="13" rx="6.5" '
                'fill="none" stroke="#FFFFFF" stroke-width="4.4"/></g>').format(cx, cy, a)
    left = link(14, 46, -35) + link(24, 36, 55)
    right = link(40, 28, 55) + link(50, 18, -35)
    return left + right + burst(32, 32, 9, 7) + L([(20, 22), (16, 16)], 2.6) + L([(44, 42), (48, 48)], 2.6)


def flask(x=32, y=32, s=1.0, a=0):
    return G(R(-4.5, -26, 9, 4, 1.5) + R(-3.5, -22, 7, 9, 1) + P("M-3.5 -14 C-3.5 -10 -16 -6 -16 6 C-16 17 -8 24 0 24 "
                                                              "C8 24 16 17 16 6 C16 -6 3.5 -10 3.5 -14 Z")
             + P("M-12 6 C-8 3 -4 8 0 6 C4 4 8 8 12 6 C12 15 7 20 0 20 C-7 20 -12 15 -12 6 Z", K)
             + Cc(-5, 13, 2.2) + Cc(3, 10, 1.6), x, y, a, s)


def book_open(x=32, y=32, s=1.0):
    return G(P("M0 -14 C-8 -20 -20 -20 -28 -16 V18 C-20 14 -8 14 0 20 C8 14 20 14 28 18 V-16 C20 -20 8 -20 0 -14 Z")
             + L([(0, -12), (0, 18)], 2.4, K) + "".join(L([(-22, y_), (-6, y_ + 2)], 1.8, K) + L([(6, y_ + 2), (22, y_)], 1.8, K)
                                                        for y_ in (-8, -2, 4, 10)), x, y, 0, s)


def sun_symbol(x=32, y=32, s=1.0, cross=True):
    rays = "".join(G(P("M-2.4 -28 L2.4 -28 L1.4 -16 L-1.4 -16 Z"), 0, 0, a) for a in range(0, 360, 30))
    core = Cc(0, 0, 12)
    sign = (R(-2.2, -8, 4.4, 16, 1, K) + R(-8, -2.2, 16, 4.4, 1, K)) if cross else ""
    return G(rays + core + sign, x, y, 0, s)


def note(x=32, y=32, s=1.0):
    return G('<ellipse cx="-8" cy="14" rx="9" ry="7" transform="rotate(-20 -8 14)" fill="#FFFFFF"/>'
             + R(-1, -24, 4.4, 38, 1.5) + P("M3.4 -24 C10 -20 18 -16 16 -4 C14 -10 9 -12 3.4 -12 Z"), x, y, 0, s)


def feather(x=32, y=32, s=1.0, a=0):
    return G(P("M0 -26 C10 -18 12 -2 4 14 L0 24 L-4 14 C-12 -2 -10 -18 0 -26 Z") + L([(0, -18), (0, 26)], 2, K)
             + "".join(L([(0, y_), (sx * 6, y_ - 6)], 1.4, K) for y_ in (-8, 0, 8) for sx in (-1, 1)), x, y, a, s)


def wolf(x=32, y=32, s=1.0):
    head = P("M-18 -22 L-10 -8 C-6 -10 6 -10 10 -8 L18 -22 L20 -2 C22 6 16 14 8 20 L0 26 L-8 20 C-16 14 -22 6 -20 -2 Z")
    eyes = P("M-12 -2 L-4 0 L-11 3 Z", K) + P("M12 -2 L4 0 L11 3 Z", K)
    nose = P("M-4 14 H4 L0 19 Z", K)
    return G(head + eyes + nose, x, y, 0, s)


def bulb(x=32, y=32, s=1.0):
    return G(P("M0 -24 C12 -24 18 -15 18 -6 C18 2 12 7 10 12 H-10 C-12 7 -18 2 -18 -6 C-18 -15 -12 -24 0 -24 Z")
             + R(-9, 14, 18, 4, 1.5) + R(-8, 19, 16, 4, 1.5) + R(-5, 24, 10, 3, 1.5)
             + S("M-6 6 L-6 -2 L0 -8 L6 -2 L6 6", 2.4, K), x, y, 0, s)


def door(x=32, y=32, s=1.0):
    return G(R(-16, -26, 32, 52, 2) + P("M-11 -21 H11 V26 H-11 Z", K) + P("M-11 -21 L8 -16 V30 L-11 26 Z")
             + Cc(3, 4, 2, K) + R(-20, 24, 40, 4, 1), x, y, 0, s)


def two_bubbles():
    return (G(P("M-20 -14 H16 C20 -14 22 -12 22 -8 V6 C22 10 20 12 16 12 H-6 L-16 20 V12 H-20 C-24 12 -26 10 -26 6 V-8 "
                "C-26 -12 -24 -14 -20 -14 Z"), 26, 24, 0, 0.9)
            + over("", G(P("M-16 -10 H16 C20 -10 22 -8 22 -4 V8 C22 12 20 14 16 14 H12 V22 L2 14 H-16 C-20 14 -22 12 "
                           "-22 8 V-4 C-22 -8 -20 -10 -16 -10 Z"), 40, 42, 0, 0.8), 6))


def figure(x=32, y=32, s=1.0, a=0):
    return G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), x, y, a, s)


def lightning(x=32, y=32, s=1.0):
    return G(P("M6 -28 L-12 4 L0 4 L-6 28 L14 -4 L2 -4 L10 -28 Z"), x, y, 0, s)


def wind(x=32, y=32, s=1.0):
    return G(S("M-24 -10 H10 C18 -10 20 -20 12 -22 C6 -23 4 -16 8 -14", 4) + S("M-26 2 H18 C26 2 28 14 20 16 C14 17 12 10 16 8", 4)
             + S("M-20 14 H0 C6 14 8 22 2 24", 4), x, y, 0, s)


def heart_plus(x=32, y=32, s=1.0):
    return G(P("M0 22 C-16 10 -24 2 -24 -8 C-24 -16 -18 -21 -11 -21 C-6 -21 -2 -18 0 -14 C2 -18 6 -21 11 -21 "
               "C18 -21 24 -16 24 -8 C24 2 16 10 0 22 Z")
             + '<path d="M0 -10 V8 M-9 -1 H9" stroke="#000000" stroke-width="5.5" stroke-linecap="round"/>', x, y, 0, s)


def face_rage(x=32, y=32, s=1.0):
    head = P("M0 -24 C14 -24 22 -14 22 -2 C22 12 14 24 0 24 C-14 24 -22 12 -22 -2 C-22 -14 -14 -24 0 -24 Z")
    brows = P("M-16 -10 L-4 -4 L-4 -1 L-16 -6 Z", K) + P("M16 -10 L4 -4 L4 -1 L16 -6 Z", K)
    eyes = Cc(-9, 2, 2.6, K) + Cc(9, 2, 2.6, K)
    mouth = P("M-10 10 C-6 6 6 6 10 10 L8 17 C4 14 -4 14 -8 17 Z", K) + P("M-6 11 L-4 14 L-2 11 Z") + P("M6 11 L4 14 L2 11 Z")
    horns = P("M-18 -14 C-26 -20 -28 -28 -24 -34 C-22 -26 -16 -22 -12 -20 Z") + P("M18 -14 C26 -20 28 -28 24 -34 C22 -26 16 -22 12 -20 Z")
    return G(horns + head + brows + eyes + mouth, x, y, 0, s)


# ------------------------------------------------------------------------------------------------ actions communes
COMMON = {
    "foncer": lambda: runner(36, 32, 1.05) + speed(4, 30, 3, 12, 8, 0, 3.4),
    "desengager": lambda: G(runner(0, 0, 1.0), 40, 32, 0).replace("translate(40 32) rotate(0) scale(1)",
                                                                   "translate(30 32) scale(-1 1)")
                  + arrow(54, 12, 36, 12, 3.4, 8) + speed(46, 46, 3, 10, 7, 0, 3),
    "esquiver": lambda: figure(26, 36, 1.0, -30) + arrow(30, 6, 62, 22, 3.2, 9)
                        + S("M46 34 C52 40 52 50 46 56", 3) + S("M54 32 C61 40 61 52 54 60", 2.6),
    "aider": lambda: over(hand(32, 42, 0.85, 0), heart(32, 14, 0.42)) + star4(10, 14, 4) + star4(54, 20, 4),
    "se_cacher": lambda: hood(32, 32, 1.0),
    "bousculer": lambda: over(hand(38, 34, 0.9, 0), arrow(40, 8, 60, 8, 3.2, 8)) + speed(4, 34, 3, 12, 8, 0, 3.2),
    "saisir": lambda: over(R(4, 34, 56, 9, 4.5), fist(32, 32, 0.85)),
    "se_tenir_pret": lambda: over(hourglass(26, 32, 0.95), G(R(-3.5, -18, 7, 22, 3.5) + Cc(0, 12, 4), 50, 34)),
    "utiliser_objet": lambda: over(hand(28, 42, 0.8, 0), flask(36, 20, 0.6)),
    "chercher": lambda: magnifier(32, 32, 1.25),
    "interagir": lambda: over(door(28, 32, 1.0), hand(48, 44, 0.5, -30)),
    "parler": two_bubbles,
    "etudier": lambda: over(book_open(30, 38, 0.85), magnifier(44, 20, 0.6)),
    "influencer": lambda: over(bubble(30, 30, 0.95), heart(30, 26, 0.42).replace('fill="#FFFFFF"', 'fill="#000000"')),
    "boire_potion": lambda: flask(32, 30, 1.05, 25) + Cc(14, 52, 2.6) + Cc(20, 58, 2),
    "se_liberer": broken_chain,
    "lancer_objet": lambda: hand(18, 44, 0.65, 30) + curved_arrow("M24 22 C34 6 50 8 56 22", (56, 22), 70, 3.2)
                            + Cc(56, 34, 6),
    "magie": lambda: star4(30, 34, 20) + star4(50, 14, 8) + star4(12, 12, 5) + S("M8 52 C20 60 44 60 56 46", 3),
}


# ------------------------------------------------------------------------------------------------ capacités de classe
FEATURES = {
    "Attaque d'opportunité": lambda: over(sword(28, 36, 45, 1.0), G(R(-3.5, -16, 7, 20, 3.5) + Cc(0, 12, 4), 50, 22)),
    "Attaque sournoise": lambda: over(eye(30, 16, 0.6, True), dagger(34, 40, 45, 1.05)),
    "Attaque téméraire": lambda: over(G(blade_sword(30, 8.5, 20, 9, 3.6), 28, 36, 45, 1.0), burst(48, 16, 12, 9)),
    "Canalisation de puissance divine": lambda: over(hand(32, 44, 0.8, 0), sun_symbol(32, 16, 0.5)),
    "Conduit divin (domaine)": lambda: sun_symbol(32, 32, 1.05),
    "Conduit divin (serment)": lambda: over(sun_symbol(32, 26, 0.8, False), shield(32, 40, 0.65)),
    "Conduit divin : Renvoi des morts-vivants": lambda: over(sun_symbol(22, 22, 0.7, False), skull(42, 42, 0.75)),
    "Exploitation du pouvoir divin": lambda: over(sun_symbol(30, 34, 0.85), arrow(50, 54, 50, 6, 4, 10)),
    "Chute ralentie": lambda: feather(28, 30, 1.0, 30) + arrow(52, 8, 52, 58, 3.4, 9),
    "Châtiment divin": lambda: over(sun_symbol(44, 20, 0.6, False), G(blade_sword(30, 8.5, 20, 9, 3.6), 28, 40, 45, 0.95)),
    "Compagnon sauvage": lambda: over(__import__("core.art_retouches", fromlist=["x"]).wolf_paw(30, 34, 1.05), star4(54, 10, 6)),
    "Contre-charme": lambda: over(shield(32, 34, 1.15), note(32, 34, 0.55).replace('fill="#FFFFFF"', 'fill="#000000"')),
    "Coup étourdissant": lambda: fist(32, 38, 1.0) + star4(14, 10, 6) + star4(32, 6, 5) + star4(50, 10, 6),
    "Défense patiente": lambda: over(shield(30, 32, 1.0), hand(46, 44, 0.5, 0)),
    "Déluge de coups": lambda: over(fist(24, 26, 0.75), fist(40, 42, 0.75)) + speed(4, 44, 2, 8, 7, 0, 3),
    "Entrer en rage": lambda: __import__("core.art_retouches", fromlist=["x"]).rage(),
    "Esquive instinctive": lambda: figure(24, 34, 1.0, -22) + arrow(30, 8, 60, 38, 3.2, 9),
    "Forme sauvage": lambda: __import__("core.art_retouches", fromlist=["x"]).wolf_profile(32, 32, 1.0),
    "Guidage magique": lambda: over(eye(32, 34, 0.9), star4(50, 12, 8)) + star4(12, 54, 5),
    "Guérison accélérée": lambda: heart_plus(30, 34, 1.0) + speed(52, 20, 3, 8, 6, 0, 2.8),
    "Imposition des mains": lambda: over(hand(32, 40, 0.9, 0), heart(32, 12, 0.4)) + star4(10, 12, 4) + star4(54, 18, 4),
    "Inspiration bardique": lambda: over(note(28, 36, 1.0), star4(50, 14, 10)),
    "Parade de projectiles": lambda: hand(26, 40, 0.85, 0) + arrow(60, 6, 34, 18, 3.4, 9),
    "Pas du vent": lambda: over(wind(32, 36, 1.0), boot(46, 18, 0.45)),
    "Recevoir l'inspiration (MJ)": lambda: star4(32, 32, 26) + star4(52, 12, 6) + star4(12, 52, 5),
    "Second souffle": lambda: over(heart_plus(28, 30, 0.95), curved_arrow("M44 58 C60 48 60 24 50 14", (50, 14), 245, 3.6)),
    "Sens divin": lambda: over(eye(32, 38, 0.95), sun_symbol(32, 14, 0.4, False)),
    "Sursaut d'activité": lambda: over(G(blade_sword(30, 8.5, 20, 9, 3.6), 26, 38, 45, 0.95), lightning(46, 22, 0.8)),
    "Visée concentrée": lambda: over(target(28, 36, 1.0), eye(46, 14, 0.45)),
    "Visée stable": lambda: '<circle cx="32" cy="32" r="22" fill="none" stroke="#FFFFFF" stroke-width="4.5"/>'
                            + "".join(L(p, 4.5) for p in (((32, 4), (32, 18)), ((32, 46), (32, 60)), ((4, 32), (18, 32)),
                                                           ((46, 32), (60, 32)))) + Cc(32, 32, 4.5),
    "Éclair de génie": lambda: over(bulb(28, 34, 1.0), lightning(48, 16, 0.5)),
}
