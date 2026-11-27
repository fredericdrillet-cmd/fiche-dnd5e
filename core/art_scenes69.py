"""
Scènes dessinées (v53) des sorts de niveau 6 à 9. Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

import math

from .art_armes import Cc, G, K, L, P, R, S, burst, curved_arrow, over, star4
from .art_kit import (angel_wings, bird, black, cloud, coffin, demon, doorway, dragon_head, figure, insect, place,
                      tornado, tree)
from .art_motifs import MOTIFS as M
from .art_scenes2 import _bubble, _dashed, _drop, _flame, _hand, _head, _rays, _snow, _sword


def _circle(r, w=3, dash=""):
    d = ' stroke-dasharray="{}"'.format(dash) if dash else ""
    return '<circle cx="32" cy="32" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"{}/>'.format(r, w, d)


def _lying(x, y, s=1.0):
    return G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), x, y, 90, s)


def _word(inner, s=0.86):
    waves = S("M5 22 C1 28 1 36 5 42", 3.4) + S("M59 22 C63 28 63 36 59 42", 3.4)
    return over(waves, place(inner, 32, 32, s), 6)


def _clock():
    return (Cc(32, 36, 24) + black(Cc(32, 36, 19)) + R(28, 4, 8, 8, 2) + L([(32, 36), (32, 22)], 3.4)
            + L([(32, 36), (42, 40)], 3.4) + Cc(32, 36, 3))


def _rainbow(n, w):
    return "".join('<path d="M{} 54 A{} {} 0 0 1 {} 54" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(32 - r, r, r, 32 + r, w)
                   for r in range(28, 28 - n * (w + 2), -(w + 2)))


SCENES = {
    # ------------------------------------------------------------------ niveau 6
    "Allié planaire": lambda: figure(14, 40, 0.65) + place(angel_wings(), 42, 30, 0.7) + R(20, 30, 10, 3, 1.5),
    "Barrière de lames": lambda: ("".join(G(P("M0 -18 L4 -8 L2 12 H-2 L-4 -8 Z") + R(-6, 12, 12, 3, 1.5), x, 30, a, 1.0)
                                          for x, a in ((10, -20), (22, 10), (34, -15), (46, 20), (56, -10)))
                                  + S("M4 52 C16 46 26 58 36 52 C46 46 54 56 62 50", 3) + S("M4 8 C16 2 26 12 36 6 C46 0 54 10 62 4", 2.4)),
    "Bosquet des druides": lambda: place(tree(), 14, 34, 0.48) + place(tree(), 50, 34, 0.48) + place(tree(), 32, 26, 0.6) + R(2, 58, 60, 4, 2),
    "Bouclier de platine de Fizban": lambda: place(M["bouclier"](), 32, 36, 0.9) + black(place(dragon_head(), 32, 34, 0.42)),
    "Cage des âmes": lambda: (R(14, 4, 36, 4, 2) + R(14, 58, 36, 4, 2) + "".join(S("M{} 8 C{} 24 {} 40 {} 58".format(x, x - 4, x - 4, x), 2.6) for x in (18, 26, 38, 46))
                              + _dashed(figure(32, 34, 0.6), "2 2", 1.6)),
    "Cercle de mort": lambda: place(M["crane"](), 32, 32, 0.5) + _circle(22, 4) + _circle(29, 2.2, "4 3"),
    "Chaudron bouillonnant de Tasha": lambda: (P("M8 28 H56 C56 48 46 58 32 58 C18 58 8 48 8 28 Z") + R(4, 24, 56, 6, 3)
                                               + Cc(22, 18, 4) + Cc(34, 10, 5) + Cc(44, 18, 3.4) + R(14, 56, 6, 6, 1) + R(44, 56, 6, 6, 1)),
    "Chaîne d'éclairs": lambda: (L([(4, 8), (18, 26), (12, 28), (28, 42)], 4) + L([(28, 42), (40, 30), (36, 28), (52, 18)], 4)
                                 + L([(28, 42), (38, 52), (34, 54), (46, 62)], 4) + burst(28, 42, 6, 6) + burst(52, 18, 5, 6)),
    "Contamination": lambda: (figure(26, 34, 1.0) + "".join(Cc(x, y, r) for x, y, r in ((46, 12, 5), (54, 24, 3.4), (48, 36, 4), (56, 48, 3)))
                              + black(Cc(26, 30, 2.4) + Cc(24, 40, 2) + Cc(30, 44, 1.6))),
    "Convocation de fiélon": lambda: place(demon(), 32, 28, 0.72) + _flame(12, 56, 0.24) + _flame(32, 58, 0.28) + _flame(52, 56, 0.24),
    "Convocations instantanées de Drawmij": lambda: (_hand(20, 44, 0.6, 30) + place(M["gemme"](), 46, 18, 0.42)
                                                     + S("M28 26 C32 20 36 20 38 22", 2.2) + star4(56, 40, 4)),
    "Costume d'Outremonde de Tasha": lambda: figure(32, 30, 1.0) + S("M22 46 C16 54 20 60 14 62", 4) + S("M42 46 C48 54 44 60 50 62", 4) + black(Cc(32, 24, 3)),
    "Création d'homoncule": lambda: (place(M["fiole"](), 20, 40, 0.6) + G(P("M-8 6 C-10 -6 -4 -12 0 -12 C4 -12 10 -6 8 6 Z")
                                     + P("M-8 -4 C-16 -10 -18 -2 -12 2 Z") + P("M8 -4 C16 -10 18 -2 12 2 Z"), 46, 22, 0, 1.2)
                                     + black(Cc(44, 14, 1.4) + Cc(48, 14, 1.4))),
    "Création de mort-vivant": lambda: (place(M["crane"](), 32, 22, 0.6) + G(R(-3, 0, 6, 22, 2) + R(-14, 4, 28, 4, 2) + R(-10, 12, 20, 3, 1.5), 32, 34)
                                        + _rays(32, 22, 22, 26, 6, 2, 200)),
    "Danse irrésistible d'Otto": lambda: (G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L14 26 H8 L2 10 L-4 26 H-10 L-4 8 H-12 Z"), 30, 34, -15, 1.0)
                                          + L([(18, 18), (10, 10)], 3) + L([(40, 18), (48, 8)], 3) + place(M["note"](), 52, 40, 0.3)),
    "Dispersion": lambda: (figure(32, 34, 0.7) + "".join(curved_arrow(d, e, a, 2.6, 7) for d, e, a in (
        ("M26 22 C20 16 14 12 8 10", (6, 8), 200), ("M38 22 C44 16 50 12 56 10", (58, 8), -20), ("M26 48 C20 54 14 58 8 60", (6, 62), 160)))),
    "Désintégration": lambda: (L([(2, 8), (30, 30)], 5) + _dashed(figure(44, 36, 1.0), "2 2", 2.4) + Cc(56, 24, 2) + Cc(58, 34, 1.6) + Cc(54, 46, 1.6)),
    "Festin des héros": lambda: ('<ellipse cx="32" cy="46" rx="28" ry="8" fill="#FFFFFF"/>' + black('<ellipse cx="32" cy="44" rx="20" ry="4" fill="#FFFFFF"/>')
                                 + P("M18 40 C18 30 26 26 32 26 C38 26 46 30 46 40 Z") + R(10, 26, 6, 14, 2) + R(48, 26, 6, 14, 2) + star4(32, 12, 6)),
    "Fissure gravitationnelle": lambda: (L([(2, 32), (62, 32)], 6) + black(L([(4, 32), (60, 32)], 2)) + "".join(
        P("M{} {} l4 -6 l4 6 Z".format(x, 26 - (x % 3) * 4)) for x in (8, 22, 36, 50)) + S("M10 44 C18 50 26 50 32 44", 2.4) + S("M32 44 C38 50 46 50 54 44", 2.4)),
    "Globe d'invulnérabilité": lambda: (Cc(32, 34, 27) + black(Cc(32, 34, 23)) + figure(32, 36, 0.6) + S("M12 22 C16 14 24 10 32 9", 3)
                                        + L([(4, 4), (12, 12)], 3) + L([(60, 4), (52, 12)], 3)),
    "Guérison": lambda: (_hand(32, 44, 0.75, 0) + place(M["soin"](), 32, 14, 0.44) + _rays(32, 14, 16, 20, 8, 2)),
    "Illusion programmée": lambda: (_dashed(figure(24, 34, 1.0), "3 2", 2.2) + place(M["sablier"](), 50, 16, 0.36) + star4(54, 48, 4)),
    "Interdiction": lambda: (doorway() + over("", '<circle cx="32" cy="38" r="12" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
                                               + L([(24, 30), (40, 46)], 4), 4)),
    "Invocation de fée": lambda: (place(M["aile"](), 20, 28, 0.6) + '<g transform="translate(64 0) scale(-1 1)">' + place(M["aile"](), 20, 28, 0.6) + "</g>"
                                  + Cc(32, 30, 6) + star4(32, 54, 6)),
    "Marche sur le vent": lambda: (figure(32, 22, 0.75) + S("M4 44 H40 C48 44 50 34 42 32", 4) + S("M10 56 H54", 4) + S("M22 50 H60", 3)),
    "Mauvais oeil": lambda: (place(M["oeil"](), 32, 32, 1.0) + black(Cc(32, 32, 9)) + P("M32 25 L35 32 L32 39 L29 32 Z") + _rays(32, 32, 26, 30, 10, 2)),
    "Mauvais œil": lambda: (place(M["oeil"](), 32, 26, 0.85) + _drop(32, 52, 0.24) + _rays(32, 26, 22, 26, 6, 2, 200)),
    "Mot de retour": lambda: _word(doorway() + black(place(curved_arrow("M44 44 V30 C44 20 36 16 28 16 H18", (12, 16), 180, 6, 12), 32, 36, 0.6))),
    "Mur d'épines": lambda: (R(2, 46, 60, 12, 2) + "".join(P("M{} 46 L{} {} L{} 46 Z".format(x - 5, x, 46 - h, x + 5)) for x, h in ((8, 26), (20, 34), (32, 28), (44, 36), (56, 24)))
                             + black(S("M6 52 C16 48 26 56 36 52 C46 48 54 54 60 52", 1.8))),
    "Mur de glace": lambda: (P("M4 58 L8 18 L18 10 L30 14 L42 8 L56 14 L60 58 Z") + black(L([(14, 22), (20, 50)], 2) + L([(34, 18), (30, 46)], 2) + L([(48, 20), (52, 48)], 2))
                             + _snow(52, 6, 0.18)),
    "Ossements de la Terre": lambda: (P("M2 54 H62 V62 H2 Z") + "".join(P("M{} 54 L{} {} L{} 54 Z".format(x - 4, x, 54 - h, x + 4)) + Cc(x, 54 - h, 3.4)
                                                                         for x, h in ((12, 30), (26, 40), (40, 26), (52, 36)))),
    "Portail magique": lambda: ('<ellipse cx="14" cy="34" rx="9" ry="18" fill="#FFFFFF"/>' + black('<ellipse cx="14" cy="34" rx="5" ry="13" fill="#FFFFFF"/>')
                                + '<ellipse cx="50" cy="34" rx="9" ry="18" fill="#FFFFFF"/>' + black('<ellipse cx="50" cy="34" rx="5" ry="13" fill="#FFFFFF"/>')
                                + curved_arrow("M20 12 C28 4 36 4 44 12", (44, 12), 50, 2.6, 7)),
    "Prison mentale": lambda: (_head(30, 36, 0.8) + "".join(L([(x, 6), (x, 60)], 2.6) for x in (10, 22, 42, 54)) + R(6, 4, 52, 4, 1) + R(6, 58, 52, 4, 1)),
    "Protection primordiale": lambda: (figure(32, 34, 0.6) + _flame(10, 12, 0.2) + _snow(54, 12, 0.18) + place(M["eclair"](), 10, 54, 0.22)
                                       + _drop(54, 54, 0.18) + _circle(24, 2.4, "4 3")),
    "Protections et sceaux": lambda: (place(doorway(), 22, 34, 0.75) + place(M["rune"](), 50, 20, 0.36) + place(M["rune"](), 52, 48, 0.28)),
    "Préméditation": lambda: (_head(26, 36, 0.75) + _bubble(48, 16, 0.38) + black(place(M["sablier"](), 48, 14, 0.2))),
    "Prévoyance": lambda: (place(M["oeil"](), 30, 30, 0.75) + curved_arrow("M14 54 C26 60 42 60 54 50", (54, 50), -40, 3, 8) + star4(56, 8, 4)),
    "Pétrification": lambda: (figure(32, 32, 1.1) + black(L([(26, 14), (30, 24), (26, 32)], 2) + L([(36, 34), (40, 44), (34, 52)], 2))
                              + L([(4, 60), (60, 60)], 3) + place(M["oeil"](), 52, 10, 0.26)),
    "Rayon de soleil": lambda: (place(M["soleil"](), 14, 14, 0.4) + P("M20 22 L62 50 L56 60 L14 28 Z") + black(L([(22, 26), (56, 52)], 2))),
    "Sacre de la glace": lambda: figure(32, 36, 0.85) + _snow(32, 10, 0.3) + _snow(10, 30, 0.2) + _snow(54, 30, 0.2),
    "Sacre de la pierre": lambda: figure(32, 30, 0.85) + place(M["pierres"](), 32, 54, 0.44) + R(4, 60, 56, 3, 1),
    "Sacre des flammes": lambda: figure(32, 36, 0.85) + _flame(32, 10, 0.3) + _flame(10, 28, 0.22) + _flame(54, 28, 0.22),
    "Sacre du vent": lambda: figure(32, 30, 0.85) + S("M6 50 C14 44 22 56 32 50 C42 44 50 56 58 50", 3.4) + S("M10 60 C18 54 26 64 34 58", 2.6),
    "Sens de l'orientation": lambda: (Cc(32, 32, 26) + black(Cc(32, 32, 21)) + P("M32 12 L38 32 L32 52 L26 32 Z") + black(P("M32 34 L36 34 L32 48 L28 34 Z"))
                                      + R(30, 2, 4, 6, 1)),
    "Sphère glaciale d'Otiluke": lambda: Cc(32, 32, 22) + black(Cc(32, 32, 18)) + _snow(32, 32, 0.5) + _snow(54, 54, 0.16) + _snow(10, 10, 0.14),
    "Suggestion de groupe": lambda: (figure(12, 42, 0.55) + figure(32, 42, 0.55) + figure(52, 42, 0.55) + _bubble(32, 12, 0.36)
                                     + L([(12, 26), (28, 20)], 1.4) + L([(52, 26), (36, 20)], 1.4)),
    "Terraformage": lambda: (P("M2 58 L14 36 L22 44 L34 24 L46 40 L54 32 L62 58 Z") + _hand(50, 12, 0.36, 180)
                             + curved_arrow("M10 20 C14 12 20 10 26 12", (26, 12), 10, 2.2, 6)),
    "Transformation de Tenser": lambda: (figure(28, 34, 1.0) + _sword(48, 26, 30, 0.6) + _rays(28, 30, 26, 30, 8, 2)),
    "Urne magique": lambda: (P("M22 4 H42 V10 C52 16 54 30 50 42 C48 52 42 58 32 58 C22 58 16 52 14 42 C10 30 12 16 22 10 Z")
                             + black(_dashed(figure(32, 38, 0.5), "2 2", 1.6)) + black(R(20, 14, 24, 3, 1))),
    "Vision suprême": lambda: (place(M["oeil"](), 32, 34, 0.9) + _rays(32, 34, 26, 30, 12, 2.6) + star4(32, 4, 4)),
    "Voie végétale": lambda: (place(tree(), 16, 32, 0.52) + place(tree(), 48, 32, 0.52) + curved_arrow("M14 52 C22 60 42 60 50 52", (50, 52), -40, 2.6, 7)),
    # ------------------------------------------------------------------ niveau 7
    "Boule de feu à retardement": lambda: (Cc(30, 38, 18) + black(Cc(30, 38, 13)) + _flame(30, 38, 0.36) + S("M42 24 C48 14 54 12 58 8", 2.6)
                                           + burst(58, 8, 5, 6)),
    "Cage de force": lambda: (R(8, 6, 48, 5, 2) + R(8, 54, 48, 5, 2) + "".join(L([(x, 8), (x, 56)], 3.4) for x in (12, 22, 32, 42, 52))),
    "Changement de plan": lambda: (figure(20, 36, 0.8) + '<ellipse cx="46" cy="32" rx="12" ry="24" fill="#FFFFFF"/>'
                                   + black('<ellipse cx="46" cy="32" rx="7" ry="18" fill="#FFFFFF"/>') + star4(46, 32, 6) + star4(10, 10, 3.4)),
    "Couronne d'étoiles": lambda: (figure(32, 40, 0.7) + "".join(star4(32 + 22 * math.cos(a), 16 + 8 * math.sin(a), 4.6) for a in [k * math.pi / 3.5 + math.pi for k in range(7)])),
    "Dissimulation": lambda: (P("M10 54 C10 30 20 12 32 12 C44 12 54 30 54 54 Z") + black(_dashed(figure(32, 38, 0.6), "2 2", 1.8))
                              + L([(4, 58), (60, 58)], 3)),
    "Doigt de mort": lambda: (G(R(-12, -6, 22, 22, 7) + R(-1, -30, 6, 26, 3) + R(-12, -10, 5, 10, 2.5) + R(-6, -12, 5, 10, 2.5)
                              + R(5, -8, 5, 9, 2.5) + P("M10 6 L18 -2 C21 -4 24 -1 22 2 L12 14 Z"), 22, 44, 40, 0.9)
                              + L([(32, 30), (42, 22)], 2.4) + place(M["crane"](), 50, 16, 0.4)),
    "Forme éthérée": lambda: (_dashed(figure(32, 30, 1.1), "3 3", 2.4) + S("M6 54 C14 50 22 58 32 54 C42 50 50 58 58 54", 2.6) + star4(54, 10, 4)),
    "Inversion de la gravité": lambda: (G(figure(0, 0, 0.9), 32, 34, 180) + R(2, 2, 60, 4, 2) + R(2, 58, 60, 4, 2)
                                        + G(R(-3, -8, 6, 10, 2) + P("M-8 -8 H8 L0 -16 Z"), 54, 40, 0, 1.0) + G(R(-3, -8, 6, 10, 2) + P("M-8 -8 H8 L0 -16 Z"), 10, 40, 0, 1.0)),
    "Invocation de céleste": lambda: place(angel_wings(), 32, 26, 0.8) + _rays(32, 26, 26, 30, 12, 2) + R(10, 56, 44, 4, 2),
    "Lien d'essence": lambda: (place(M["coeur"](), 16, 30, 0.4) + place(M["coeur"](), 48, 30, 0.4) + L([(26, 30), (38, 30)], 3)
                               + Cc(32, 30, 3) + star4(32, 52, 5)),
    "Manoir somptueux de Mordenkainen": lambda: (doorway() + black(P("M24 60 V40 H40 V60 Z")) + P("M26 60 V42 H38 V60 Z") + R(2, 58, 60, 4, 1)
                                                 + star4(56, 8, 5) + star4(8, 8, 4)),
    "Mirage": lambda: (_dashed(P("M2 34 L16 14 L28 26 L38 8 L62 34 Z"), "3 2", 2.2) + place(M["soleil"](), 54, 8, 0.2)
                       + "".join(S("M4 {y} C12 {a} 20 {b} 28 {y} C36 {a} 44 {b} 52 {y} C56 {a} 60 {y} 62 {y}".format(y=y, a=y - 3, b=y + 3), 2.4) for y in (46, 54))),
    "Mot de pouvoir douloureux": lambda: _word(burst(32, 32, 28, 9) + Cc(32, 32, 9, K) + L([(26, 26), (38, 38)], 3) + L([(38, 26), (26, 38)], 3)),
    "Mot de pouvoir fortifiant": lambda: _word(place(M["poing"](), 32, 32, 0.95) + star4(52, 10, 6)),
    "Parole divine": lambda: _word(M["soleil"]()),
    "Projection d'image": lambda: (figure(18, 34, 0.85) + _dashed(figure(46, 30, 0.85), "3 2", 2) + L([(26, 24), (38, 22)], 2) + star4(56, 52, 4)),
    "Rayons prismatiques": lambda: (P("M32 6 L56 50 H8 Z") + black(P("M32 18 L46 44 H18 Z")) + L([(40, 28), (62, 18)], 3) + L([(44, 36), (62, 32)], 3)
                                    + L([(46, 44), (62, 48)], 3) + L([(2, 34), (24, 34)], 3)),
    "Régénération": lambda: (figure(28, 34, 1.0) + curved_arrow("M44 54 C58 46 58 22 46 14", (46, 14), 220, 3.4, 8) + place(M["coeur"](), 52, 34, 0.2)),
    "Résurrection": lambda: (place(coffin(), 22, 38, 0.75) + _dashed(figure(46, 26, 0.7), "2 2", 1.8) + _rays(46, 20, 16, 20, 8, 2)),
    "Simulacre": lambda: (figure(20, 32, 1.0) + figure(44, 32, 1.0).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2.6"')
                          + place(M["flocon"](), 56, 8, 0.16)),
    "Songe du voile bleu": lambda: (_lying(30, 52, 0.6) + '<ellipse cx="40" cy="22" rx="16" ry="14" fill="#FFFFFF"/>'
                                    + black('<ellipse cx="40" cy="22" rx="10" ry="8" fill="#FFFFFF"/>') + star4(40, 22, 5) + S("M22 44 C26 36 30 34 32 34", 2.2)),
    "Symbole": lambda: ('<circle cx="32" cy="32" r="27" fill="none" stroke="#FFFFFF" stroke-width="4"/>' + P("M32 10 L52 44 H12 Z")
                        + black(P("M32 20 L44 40 H20 Z")) + Cc(32, 34, 4.6) + L([(32, 2), (32, 8)], 3)),
    "Temple des dieux": lambda: (P("M6 22 L32 6 L58 22 Z") + R(6, 24, 52, 4, 1) + "".join(R(x, 30, 6, 22, 1) for x in (10, 22, 36, 48))
                                 + R(4, 54, 56, 6, 1) + black(Cc(32, 16, 3))),
    "Tempête de feu": lambda: _flame(14, 34, 0.5) + _flame(32, 26, 0.65) + _flame(50, 34, 0.5) + R(2, 58, 60, 4, 2),
    "Tourbillon": lambda: tornado() + G(figure(0, 0, 0.36), 52, 14, 40) + G(figure(0, 0, 0.3), 12, 22, -30),
    "Transformation draconique": lambda: (figure(18, 36, 0.8) + place(dragon_head(), 46, 28, 0.55) + P("M24 26 C30 16 36 14 40 16 L38 22 Z")),
    "Téléportation": lambda: (_dashed(figure(16, 32, 0.8), "3 3", 2.2) + figure(48, 32, 0.8) + star4(32, 14, 6) + star4(32, 52, 4)
                              + curved_arrow("M20 8 C28 2 36 2 44 8", (44, 8), 40, 2.2, 6)),
    "Épée de Mordenkainen": lambda: (_sword(32, 32, 45, 1.3) + _rays(32, 32, 26, 30, 8, 2) + star4(10, 10, 4)),
    # ------------------------------------------------------------------ niveau 8
    "Aliénation": lambda: _head(26, 38, 0.7) + S("M36 24 C44 18 46 8 56 8", 4) + S("M38 32 C48 30 52 22 60 24", 3.4) + black(Cc(26, 30, 2.4)),
    "Aura sacrée": lambda: (figure(32, 36, 0.75) + _circle(26, 3.4) + _rays(32, 32, 28, 31, 16, 2)),
    "Aversion/Attirance": lambda: (place(M["coeur"](), 32, 34, 0.5) + curved_arrow("M6 20 C10 30 14 32 20 32", (20, 32), 0, 2.6, 7)
                                   + curved_arrow("M44 32 C52 32 56 28 60 20", (60, 20), -60, 2.6, 7)),
    "Aversion/attirance": lambda: (S("M16 10 V32 C16 46 48 46 48 32 V10", 9) + black(R(10, 10, 12, 8, 0) + R(42, 10, 12, 8, 0)) + R(11, 4, 10, 5, 1) + R(43, 4, 10, 5, 1) + place(M["coeur"](), 32, 58, 0.16)),
    "Bagou": lambda: (figure(22, 38, 0.8) + place(M["couronne"](), 22, 10, 0.24) + _bubble(48, 22, 0.4)),
    "Champ antimagie": lambda: (_circle(26, 4) + star4(32, 32, 14) + L([(12, 12), (52, 52)], 5)),
    "Clone": lambda: (figure(20, 32, 1.0) + figure(44, 32, 1.0) + '<ellipse cx="44" cy="56" rx="12" ry="3" fill="#FFFFFF"/>' + L([(32, 6), (32, 58)], 1.6)),
    "Contrôle du climat": lambda: (cloud(30, 0.9) + place(M["soleil"](), 48, 14, 0.3) + L([(16, 44), (12, 54)], 2.6) + L([(28, 44), (24, 54)], 2.6)
                                   + _snow(44, 52, 0.16)),
    "Demi-plan": lambda: (doorway() + black(Cc(32, 36, 9)) + star4(32, 36, 5) + star4(10, 10, 4) + star4(54, 10, 4)),
    "Domination de monstre": lambda: (place(dragon_head(), 30, 38, 0.75) + place(M["couronne"](), 26, 10, 0.3)),
    "Dragon illusoire": lambda: _dashed(dragon_head(), "3 2", 2.4) + place(M["masque"](), 52, 52, 0.26),
    "Dédale": lambda: "".join(L(p, 4) for p in (((6, 6), (58, 6), (58, 58), (6, 58), (6, 14)), ((14, 14), (50, 14), (50, 50), (14, 50), (14, 22)),
                                                 ((22, 22), (42, 22), (42, 42), (22, 42)))) + Cc(32, 32, 3.4),
    "Esprit faible": lambda: (_head(30, 36, 0.8) + black(S("M26 24 C30 20 34 28 38 24", 2.2)) + G(R(-3, -8, 6, 10, 2) + P("M-8 2 H8 L0 10 Z"), 54, 14, 0, 0.8)),
    "Esprit impénétrable": lambda: (_head(30, 36, 0.8) + '<path d="M8 30 C8 12 52 12 52 30" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
                                    + R(46, 30, 12, 10, 2) + S("M48 30 V26 C48 22 56 22 56 26 V30", 2.4)),
    "Flétrissure épouvantable d'Abi-Dalzim": lambda: (figure(32, 32, 0.9) + black(S("M26 26 L38 38 M38 26 L26 38", 1.8))
                                                      + _drop(10, 12, 0.18) + _drop(54, 14, 0.16) + S("M8 56 C16 52 24 60 32 56", 2.4)),
    "Formes animales": lambda: (place(M["bete"](), 18, 22, 0.42) + place(bird(), 46, 22, 0.4) + place(insect(), 32, 48, 0.4)),
    "Forteresse majestueuse": lambda: (R(4, 26, 56, 32, 2) + "".join(R(x, 18, 8, 10, 1) for x in (4, 18, 32, 46))
                                       + black(P("M26 58 V44 C26 38 38 38 38 44 V58 Z")) + P("M28 18 L32 4 L36 18 Z") + R(31, 2, 2, 4, 0)),
    "Mot de pouvoir étourdissant": lambda: _word(Cc(32, 36, 16) + Cc(32, 36, 10, K) + Cc(32, 36, 4) + star4(14, 12, 6) + star4(32, 6, 5) + star4(50, 12, 6)),
    "Nuage incendiaire": lambda: (cloud(22, 1.0) + _flame(16, 50, 0.3) + _flame(32, 54, 0.34) + _flame(48, 50, 0.3)),
    "Rupture de la réalité": lambda: (P("M30 2 L36 20 L28 28 L38 40 L30 62 L24 40 L32 30 L22 18 Z") + black(L([(30, 8), (32, 20), (28, 28), (34, 40), (30, 54)], 1.6))
                                      + star4(8, 14, 4) + star4(54, 50, 5) + Cc(50, 14, 3) + Cc(12, 50, 2.4)),
    "Tremblement de terre": lambda: (P("M2 40 H62 V62 H2 Z") + black(L([(10, 40), (16, 48), (12, 54), (20, 62)], 2.6) + L([(32, 40), (28, 50), (34, 62)], 2.6)
                                     + L([(50, 40), (54, 50), (48, 56), (54, 62)], 2.6)) + S("M10 30 C18 22 24 30 32 22 C40 30 46 22 54 30", 3)),
    "Tsunami": lambda: (P("M2 60 C2 40 12 16 32 8 C46 4 60 10 62 22 C56 16 48 16 44 22 C40 28 46 36 56 34 C50 46 40 52 30 54 L62 54 V62 H2 Z")
                        + black(S("M10 52 C14 38 22 26 34 18", 2.2))),
    "Télépathie": lambda: (_head(16, 38, 0.5) + '<g transform="translate(64 0) scale(-1 1)">' + _head(16, 38, 0.5) + "</g>"
                           + S("M22 18 C28 10 36 10 42 18", 2.6) + S("M18 10 C26 0 38 0 46 10", 2) + Cc(32, 14, 2.6)),
    "Ténèbres oppressantes": lambda: (Cc(32, 32, 28) + black(Cc(32, 32, 23)) + place(M["lune"](), 32, 30, 0.44) + black(Cc(26, 46, 2) + Cc(38, 46, 2))),
    "Éclat du soleil": lambda: (Cc(32, 32, 12) + black(Cc(32, 32, 7)) + Cc(32, 32, 4) + _rays(32, 32, 16, 30, 16, 3)),
    "Étoile noire": lambda: (Cc(32, 32, 22) + black(Cc(32, 32, 17)) + burst(32, 32, 30, 12).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2"')),
    # ------------------------------------------------------------------ niveau 9
    "Arrêt du temps": lambda: _clock(),
    "Changement de forme": lambda: (figure(14, 36, 0.6) + curved_arrow("M20 18 C26 10 32 10 36 14", (36, 14), 40, 2.2, 6)
                                    + place(dragon_head(), 46, 38, 0.5)),
    "Emprisonnement": lambda: (figure(32, 34, 0.9) + '<ellipse cx="32" cy="20" rx="26" ry="5" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
                               + '<ellipse cx="32" cy="38" rx="26" ry="5" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
                               + '<ellipse cx="32" cy="54" rx="26" ry="5" fill="none" stroke="#FFFFFF" stroke-width="3"/>'),
    "Ennemi subconscient": lambda: (_head(22, 38, 0.65) + _dashed(place(demon(), 48, 22, 0.5), "2 2", 1.8) + S("M30 26 C34 20 38 20 40 22", 2.2)),
    "Guérison de groupe": lambda: (figure(12, 42, 0.55) + figure(32, 42, 0.55) + figure(52, 42, 0.55) + place(M["soin"](), 32, 12, 0.32)
                                   + _rays(32, 12, 12, 16, 8, 2)),
    "Hurlement psychique": lambda: (_head(22, 36, 0.7) + S("M40 22 C46 28 46 36 40 42", 3.4) + S("M48 16 C56 26 56 38 48 48", 3)
                                    + S("M56 10 C66 24 66 40 56 54", 2.6)),
    "Invulnérabilité": lambda: (figure(32, 34, 0.8) + "".join(G(P("M0 -30 L4 -22 L-4 -22 Z"), 32, 32, a) for a in range(0, 360, 30))
                                + _circle(22, 2.4)),
    "Lame du désastre": lambda: (P("M32 2 L40 12 L36 44 L32 48 L28 44 L24 12 Z") + black(P("M32 10 L35 14 L33 40 L32 42 L31 40 L29 14 Z"))
                                 + R(20, 46, 24, 4, 2) + R(30, 50, 4, 10, 1) + star4(10, 20, 5) + star4(54, 20, 5)),
    "Mot de pouvoir guérisseur": lambda: _word(M["soin"]()),
    "Mot de pouvoir mortel": lambda: _word(M["crane"]()),
    "Mur prismatique": lambda: "".join(R(4 + i * 8, 8 + (i % 2) * 4, 7, 48 - (i % 2) * 8, 1) for i in range(7)),
    "Métamorphose de groupe": lambda: (figure(12, 30, 0.5) + figure(30, 30, 0.5) + curved_arrow("M14 50 C24 60 40 60 48 52", (48, 52), -40, 2.4, 6)
                                       + place(M["bete"](), 50, 26, 0.36)),
    "Métamorphose suprême": lambda: (place(M["bete"](), 18, 40, 0.5) + curved_arrow("M14 16 C22 6 32 6 38 12", (38, 12), 40, 2.4, 6)
                                     + place(dragon_head(), 46, 36, 0.5) + star4(56, 8, 4)),
    "Nuée de météores": lambda: ("".join(G(P("M0 -7 C5 -7 8 -4 8 0 C8 4 5 7 0 7 L-24 2 L-24 -2 Z"), x, y, 135, s)
                                         for x, y, s in ((46, 16, 1.0), (24, 22, 0.8), (52, 40, 0.8), (30, 44, 0.9)))
                                 + R(2, 58, 60, 4, 1) + burst(30, 56, 5, 6)),
    "Portail": lambda: ('<ellipse cx="32" cy="32" rx="22" ry="28" fill="#FFFFFF"/>' + black('<ellipse cx="32" cy="32" rx="16" ry="22" fill="#FFFFFF"/>')
                        + place(M["spirale"](), 32, 32, 0.4) + R(4, 58, 56, 4, 1)),
    "Projection astrale": lambda: (_lying(30, 52, 0.6) + _dashed(figure(40, 22, 0.75), "2 2", 1.8) + S("M28 46 C30 38 34 34 36 32", 1.8)
                                   + star4(56, 8, 4) + star4(10, 10, 3)),
    "Prémonition": lambda: (place(M["oeil"](), 32, 30, 0.85) + L([(54, 2), (46, 14), (52, 16), (44, 26)], 3) + star4(8, 54, 4)),
    "Ravage temporel": lambda: (_clock() + burst(52, 14, 8, 8)),
    "Résurrection suprême": lambda: (place(coffin(), 22, 38, 0.75) + figure(46, 26, 0.7) + _rays(46, 20, 16, 20, 10, 2.2) + star4(56, 52, 5)),
    "Souhait": lambda: (place(M["etoile"](), 32, 30, 0.9) + star4(54, 8, 6) + star4(10, 54, 5) + star4(10, 10, 3.4) + star4(54, 54, 3.4)),
    "Tempête vengeresse": lambda: (cloud(20, 1.0) + L([(16, 36), (10, 48), (16, 48), (8, 62)], 3) + L([(32, 36), (26, 48), (32, 48), (24, 62)], 3)
                                   + L([(48, 36), (42, 48), (48, 48), (40, 62)], 3)),
    "Vide vorace": lambda: (Cc(32, 32, 26) + black(Cc(32, 32, 21)) + place(M["spirale"](), 32, 32, 0.5) + Cc(6, 6, 2) + Cc(58, 8, 1.6)),
}
