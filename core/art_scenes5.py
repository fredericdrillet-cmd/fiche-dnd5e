"""
Scènes dessinées (v53) des sorts de niveau 5. Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

import math

from .art_armes import Cc, G, K, L, P, R, S, curved_arrow, over, star4
from .art_kit import angel_wings, black, cloud, coffin, demon, dragon_head, figure, insect, mirror, place, tornado, tree
from .art_motifs import MOTIFS as M
from .art_scenes2 import _bubble, _dashed, _drop, _flame, _hand, _head, _rays, _snow, _sword


def _ring(r=28, w=3.4, dash=""):
    d = ' stroke-dasharray="{}"'.format(dash) if dash else ""
    return '<circle cx="32" cy="32" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"{}/>'.format(r, w, d)


def _figure_kneel(x, y, s=1.0):
    return G(Cc(0, -14, 6) + P("M-9 -6 H9 L10 8 L16 22 H9 L4 12 L-4 12 L-6 24 H-12 L-10 8 Z"), x, y, 0, s)


SCENES = {
    "Amélioration de compétences": lambda: figure(24, 34, 0.9) + "".join(
        G(R(-2.4, -4, 4.8, 10, 1) + P("M-7 -4 H7 L0 -13 Z"), x, y, 0, 1.0) for x, y in ((46, 20), (54, 36), (46, 52))),
    "Animation d'objets": lambda: (place(M["livre"](), 18, 22, 0.42) + place(M["epee"](), 46, 20, 0.42)
                                  + place(M["fiole"](), 30, 48, 0.36) + S("M20 34 C22 38 24 40 22 44", 2) + star4(54, 46, 5)),
    "Apparence trompeuse": lambda: (figure(16, 36, 0.7) + figure(48, 36, 0.7)
                                    + black(place(M["masque"](), 16, 20, 0.22) + place(M["masque"](), 48, 20, 0.22))
                                    + place(M["masque"](), 32, 12, 0.36)),
    "Arme sacrée": lambda: _sword(32, 34, 0, 1.25) + _rays(32, 18, 10, 16, 8, 2.6),
    "Assignation infernale": lambda: (place(demon(), 20, 24, 0.5) + R(28, 32, 30, 26, 2)
                                      + black(L([(32, 40), (54, 40)], 2) + L([(32, 46), (50, 46)], 2)) + Cc(50, 54, 5)),
    "Aube": lambda: (P("M6 46 A26 26 0 0 1 58 46 Z") + _rays(32, 46, 30, 40, 9, 3, 180) + R(2, 48, 60, 4, 2)
                     + R(10, 56, 44, 3, 1.5)),
    "Brume mortelle": lambda: (cloud(26, 1.05) + black(place(M["crane"](), 32, 26, 0.32))
                               + S("M14 46 C10 52 16 56 12 62", 2.6) + S("M32 46 C28 52 34 56 30 62", 2.6) + S("M50 46 C46 52 52 56 48 62", 2.6)),
    "Carquois magique": lambda: (G(R(-9, -18, 18, 40, 6) + R(-9, -18, 18, 6, 2, K), 26, 38, 15)
                                 + "".join(L([(x, 22), (x + 6, 2)], 2.6) + P("M{} 0 l3 7 h-6 Z".format(x + 6)) for x in (18, 26, 34))
                                 + star4(50, 14, 6) + star4(54, 40, 4)),
    "Cercle de pouvoir": lambda: (_ring(28, 4) + _ring(20, 2) + figure(32, 34, 0.55)
                                  + "".join(G(P("M0 -26 L3 -21 L0 -16 L-3 -21 Z"), 32, 32, a) for a in range(0, 360, 60))),
    "Cercle de téléportation": lambda: ('<ellipse cx="32" cy="50" rx="28" ry="9" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
                                        '<ellipse cx="32" cy="50" rx="18" ry="5" fill="none" stroke="#FFFFFF" stroke-width="2"/>'
                                        + _dashed(figure(32, 26, 0.85), "3 2", 2.2) + "".join(L([(x, 46), (x, 14)], 1.6) for x in (10, 54))),
    "Châtiment du ban": lambda: (_sword(22, 40, 45, 0.95) + P("M44 4 C50 14 56 24 54 36 C52 46 48 50 46 58 C42 50 38 42 40 30 C42 22 44 14 44 4 Z")
                                 + black(P("M45 14 C48 22 50 28 48 36 C46 42 46 46 46 50 C44 44 42 38 43 30 C44 24 44 18 45 14 Z"))),
    "Colonne de flamme": lambda: (P("M20 60 V20 H44 V60 Z") + black(P("M24 58 V24 H40 V58 Z")) + _flame(32, 40, 0.7)
                                  + _flame(32, 12, 0.42) + R(10, 58, 44, 4, 2)),
    "Communion": lambda: (_figure_kneel(32, 44, 0.9) + P("M24 2 H40 L44 30 H20 Z") + black(P("M28 4 H36 L38 26 H26 Z"))
                          + star4(32, 14, 4)),
    "Communion avec la nature": lambda: (tree() + black(place(M["oeil"](), 32, 24, 0.3))),
    "Contact avec un autre plan": lambda: (_head(18, 40, 0.6) + '<ellipse cx="46" cy="22" rx="14" ry="18" fill="#FFFFFF"/>'
                                           + black('<ellipse cx="46" cy="22" rx="9" ry="13" fill="#FFFFFF"/>') + star4(46, 22, 5)
                                           + S("M26 30 C32 24 34 24 36 26", 2.2)),
    "Contagion": lambda: (figure(28, 34, 1.0) + "".join(Cc(x, y, r) for x, y, r in ((48, 14, 4), (54, 26, 3), (50, 40, 3.4), (12, 18, 2.6)))
                          + black(Cc(28, 30, 2) + Cc(26, 40, 1.6))),
    "Contrat": lambda: (R(10, 6, 40, 52, 2) + black(L([(16, 16), (44, 16)], 2) + L([(16, 24), (40, 24)], 2) + L([(16, 32), (44, 32)], 2))
                        + S("M16 46 C22 40 26 52 32 44", 2.4) + Cc(46, 50, 9) + black(Cc(46, 50, 5)) + star4(46, 50, 3.4)),
    "Contrôle des vents": lambda: (_hand(16, 44, 0.55, 30) + S("M24 14 H50 C58 14 60 4 52 2", 4) + S("M28 26 H58", 4)
                                   + S("M24 38 H46 C54 38 56 48 48 50", 4)),
    "Convocation d'esprit draconique": lambda: (_dashed(dragon_head(), "3 2", 2.2) + star4(8, 54, 5) + star4(54, 54, 4)),
    "Convocation de céleste": lambda: (angel_wings() + _rays(32, 16, 10, 14, 8, 2)),
    "Convocation de dragon": lambda: (dragon_head() + _flame(56, 52, 0.22) + star4(6, 8, 4)),
    "Coquille antivie": lambda: ('<circle cx="32" cy="34" r="24" fill="none" stroke="#FFFFFF" stroke-width="4"/>' + figure(32, 36, 0.7)
                                 + place(M["bete"](), 8, 12, 0.24) + place(M["bete"](), 56, 12, 0.24)),
    "Création": lambda: (_hand(20, 44, 0.6, 30) + P("M36 22 L52 18 L58 32 L46 42 L32 36 Z") + black(L([(36, 26), (52, 30)], 1.6))
                         + star4(46, 6, 5) + star4(60, 46, 4)),
    "Cône de froid": lambda: (P("M4 32 L60 4 C64 22 64 42 60 60 Z") + black(P("M14 32 L54 14 C56 26 56 38 54 50 Z"))
                              + _snow(42, 32, 0.32)),
    "Danse macabre": lambda: (place(M["crane"](), 18, 22, 0.42) + place(M["crane"](), 46, 28, 0.42)
                              + place(M["note"](), 32, 50, 0.3) + S("M10 46 C16 40 22 52 28 46", 2.2)),
    "Dissipation du mal et du bien": lambda: (figure(22, 36, 0.85) + L([(30, 24), (48, 12)], 3)
                                              + _rays(52, 10, 6, 10, 8, 2) + _dashed(place(demon(), 50, 46, 0.34), "2 2", 1.6)),
    "Domination de personne": lambda: (figure(32, 40, 0.85) + S("M14 4 L22 16", 2) + S("M50 4 L42 16", 2)
                                       + L([(22, 16), (28, 24)], 1.6) + L([(42, 16), (36, 24)], 1.6) + R(10, 2, 44, 4, 2)),
    "Double illusoire": lambda: (figure(22, 32, 1.0) + _dashed(figure(44, 32, 1.0), "3 2", 2.2) + star4(56, 8, 4)),
    "Décalage temporel": lambda: (place(M["sablier"](), 26, 34, 0.75) + curved_arrow("M46 54 C58 46 58 22 46 14", (46, 14), 220, 3.4, 8)),
    "Déluge d'énergie négative": lambda: (place(M["crane"](), 32, 32, 0.6) + "".join(
        L([(32 + 20 * math.cos(a), 32 + 20 * math.sin(a)), (32 + 30 * math.cos(a), 32 + 30 * math.sin(a))], 4)
        for a in [k * math.pi / 4 for k in range(8)])),
    "Fléau d'insectes": lambda: (place(insect(), 20, 22, 0.4) + place(insect(), 44, 16, 0.32) + place(insect(), 36, 44, 0.44)
                                 + place(insect(), 12, 48, 0.28) + place(insect(), 54, 46, 0.26)),
    "Foulée dimensionnelle": lambda: (figure(14, 36, 0.7) + '<ellipse cx="46" cy="34" rx="12" ry="22" fill="#FFFFFF"/>'
                                      + black('<ellipse cx="46" cy="34" rx="7" ry="16" fill="#FFFFFF"/>') + S("M22 20 C30 10 38 10 42 16", 2.2)),
    "Frappe du vent d'acier": lambda: (_sword(20, 44, 45, 0.7) + _sword(36, 30, 45, 0.7) + _sword(50, 16, 45, 0.7) + S("M2 60 C20 50 40 30 62 4", 2)),
    "Fureur de la nature": lambda: (tree() + L([(54, 2), (46, 16), (52, 18), (44, 32)], 3)),
    "Immobilisation de monstre": lambda: (place(demon(), 32, 30, 0.75) + '<ellipse cx="32" cy="24" rx="28" ry="6" fill="none" stroke="#FFFFFF" stroke-width="3.4"/>'
                                          + '<ellipse cx="32" cy="44" rx="28" ry="6" fill="none" stroke="#FFFFFF" stroke-width="3.4"/>'),
    "Immolation": lambda: (_flame(32, 32, 1.1) + black(figure(32, 38, 0.5)) + _flame(10, 52, 0.18) + _flame(54, 52, 0.18)),
    "Invocation d'élémentaire": lambda: (tornado() + black(Cc(28, 18, 2.4) + Cc(38, 18, 2.4)) + star4(56, 52, 4)),
    "Invocation de volée": lambda: "".join(L([(x, 60), (x + 26, 26)], 3) + P("M{} {} l-1 10 l-8 -6 Z".format(x + 30, 22)) for x in (2, 14, 26)),
    "Lien télépathique de Rary": lambda: (_head(16, 38, 0.48) + '<g transform="translate(64 0) scale(-1 1)">' + _head(16, 38, 0.48) + "</g>"
                                          + _head(32, 16, 0.38) + S("M22 26 C26 22 28 22 30 22", 2) + S("M42 26 C38 22 36 22 34 22", 2)
                                          + L([(24, 40), (40, 40)], 2)),
    "Maelström": lambda: ("".join('<ellipse cx="32" cy="{}" rx="{}" ry="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(
        24 + k * 6, 28 - k * 6, 9 - k * 1.5, 4 - k * 0.6) for k in range(4)) + Cc(32, 44, 3) + S("M2 14 C10 10 18 18 26 14", 2.4)),
    "Main de Bigby": lambda: (_hand(32, 34, 1.15, 0) + _rays(32, 34, 26, 30, 8, 2) + star4(54, 8, 4)),
    "Modification de mémoire": lambda: (_head(30, 36, 0.8) + black(place(M["spirale"](), 34, 26, 0.3)) + S("M52 8 L58 14 M58 8 L52 14", 2.6)),
    "Mur de force": lambda: (R(8, 6, 48, 52, 3) + black(R(13, 11, 38, 42, 2)) + _hand(32, 34, 0.5, 0)),
    "Mur de lumière": lambda: (R(10, 8, 44, 50, 2) + black(R(15, 12, 34, 42, 1)) + "".join(L([(x, 14), (x, 52)], 2) for x in (22, 32, 42))
                               + _rays(32, 32, 26, 30, 12, 2)),
    "Mur de pierre": lambda: "".join(R(4 + (c * 15) + (7 if r % 2 else 0), 12 + r * 12, 13, 10, 1.5)
                                     for r in range(4) for c in range(4) if 4 + (c * 15) + (7 if r % 2 else 0) < 54),
    "Mythes et légendes": lambda: (place(M["livre"](), 32, 40, 0.8) + place(M["couronne"](), 32, 12, 0.32) + star4(10, 12, 4) + star4(54, 12, 4)),
    "Passage par les arbres": lambda: (place(tree(), 18, 30, 0.6) + place(tree(), 46, 30, 0.6) + _dashed(figure(32, 44, 0.5), "2 2", 1.6)
                                       + curved_arrow("M16 54 C24 60 40 60 48 54", (48, 54), -30, 2.4, 6)),
    "Passe-muraille": lambda: ("".join(R(x, y, 13, 9, 1.5) for x, y in ((4, 14), (19, 14), (4, 26), (12, 38), (4, 50), (19, 50)))
                               + _dashed(figure(44, 32, 1.0), "3 2", 2.2) + R(34, 8, 3, 50, 1)),
    "Perturbations synaptiques": lambda: (place(M["cerveau"](), 32, 34, 0.7)
                                          + "".join(L([(32 + 26 * math.cos(a), 32 + 26 * math.sin(a)), (32 + 30 * math.cos(a + 0.3), 32 + 30 * math.sin(a + 0.3))], 2.6)
                                                    for a in [k * math.pi / 4 for k in range(8)])),
    "Présence royale de Yolane": lambda: (figure(32, 40, 0.8) + place(M["couronne"](), 32, 10, 0.36) + _rays(32, 30, 26, 30, 10, 2)),
    "Quête": lambda: (figure(20, 34, 0.85) + R(36, 14, 22, 30, 2) + black(L([(40, 22), (54, 22)], 1.8) + L([(40, 28), (52, 28)], 1.8))
                      + Cc(47, 40, 4) + S("M28 22 C32 18 34 18 36 20", 2)),
    "Rappel à la vie": lambda: (place(coffin(), 24, 36, 0.8) + over("", place(M["coeur"](), 48, 20, 0.36), 6) + _rays(48, 20, 13, 17, 6, 2)),
    "Restauration supérieure": lambda: (place(M["coeur"](), 32, 34, 0.8) + star4(32, 6, 6) + star4(8, 14, 4) + star4(56, 14, 4)),
    "Réincarnation": lambda: (_dashed(figure(16, 36, 0.7), "2 2", 1.8) + curved_arrow("M22 16 C30 6 38 6 44 14", (44, 14), 40, 2.6, 7)
                              + figure(48, 36, 0.7) + place(M["feuille"](), 48, 60, 0.16)),
    "Sanctification": lambda: (P("M2 50 L16 44 L32 48 L48 42 L62 46 V62 H2 Z") + _rays(32, 32, 8, 14, 8, 2.6) + Cc(32, 32, 5)
                               + L([(32, 6), (32, 18)], 3) + L([(26, 12), (38, 12)], 3)),
    "Scrutation": lambda: (mirror() + black(place(M["oeil"](), 32, 26, 0.36))),
    "Soins de groupe": lambda: (figure(14, 40, 0.6) + figure(32, 40, 0.6) + figure(50, 40, 0.6)
                                + place(M["soin"](), 32, 10, 0.3) + L([(14, 22), (32, 18), (50, 22)], 1.6)),
    "Songe": lambda: (G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), 30, 50, 90, 0.7)
                      + _bubble(42, 18, 0.5) + black(place(M["lune"](), 42, 16, 0.24))),
    "Tempête radieuse de Jallarzi": lambda: (place(M["soleil"](), 32, 18, 0.56) + "".join(L([(x, 40), (x - 6, 60)], 3.4) for x in (16, 28, 40, 52))),
    "Transmutation de la pierre": lambda: (P("M4 56 L10 30 L24 24 L30 40 L22 56 Z") + curved_arrow("M28 16 C34 8 40 8 44 14", (44, 14), 40, 2.6, 7)
                                           + _drop(48, 42, 0.5)),
    "Télékinésie": lambda: (_hand(20, 46, 0.65, 0) + P("M36 14 L54 10 L60 26 L46 34 L34 28 Z") + S("M26 26 C30 20 32 18 34 18", 2)
                            + S("M30 34 C34 30 36 30 38 30", 2)),
    "Vague destructrice": lambda: (Cc(32, 50, 6) + "".join(
        '<path d="M{} 50 A{} {} 0 0 1 {} 50" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(32 - r, r, r, 32 + r, w)
        for r, w in ((14, 4), (22, 3.4), (30, 2.8))) + R(2, 52, 60, 4, 2)),
    "Énervation": lambda: (figure(20, 34, 0.85) + S("M28 26 C36 22 40 30 48 24", 3) + Cc(52, 22, 6) + black(Cc(52, 22, 3))),
    "Éveil": lambda: (tree() + black(Cc(26, 24, 2.4) + Cc(38, 24, 2.4) + S("M26 32 Q32 36 38 32", 2)) + star4(56, 8, 4)),
}
