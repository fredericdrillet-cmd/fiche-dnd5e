"""
Finitions (v53) : dessins repris pour les icônes qui se ressemblaient encore en petit (tempêtes, boucliers,
tourbillons, épées enflammées…). Appliqués en dernier, par-dessus les sorts (SPELL_FIX) et les capacités (CAP_FIX,
clés normalisées). Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

from .art_armes import Cc, G, L, P, R, S, arrow, burst, dagger, fist, over, star4
from .art_kit import black, cloud, dragon_head, figure, place, tree
from .art_motifs import MOTIFS as M
from .art_scenes2 import _drop, _flame, _hand, _rays, _snow, _sword


def _m(n, x=32, y=32, s=1.0):
    return place(M[n](), x, y, s)


def _gear(x, y, r):
    teeth = "".join(G(R(-r * 0.18, -r * 1.25, r * 0.36, r * 0.4, 1), x, y, a) for a in range(0, 360, 45))
    return teeth + Cc(x, y, r) + black(Cc(x, y, r * 0.45))


def _dunes():
    return (P("M2 62 C10 48 24 46 34 54 C42 46 54 46 62 54 V62 Z")
            + black(S("M8 58 C14 54 20 54 26 58", 1.8)) + S("M2 40 C14 34 26 42 38 36 C46 32 54 36 62 32", 2.6))


def _dashed_fig():
    from .art_scenes2 import _dashed
    return _dashed(figure(44, 32, 1.0), "3 2", 2.2)


def _rune_big(inner):
    """Pierre runique hexagonale, symbole gravé en grand."""
    stone = P("M32 4 L56 18 V46 L32 60 L8 46 V18 Z") + black(P("M32 10 L50 21 V43 L32 54 L14 43 V21 Z"))
    return stone + G(inner, 32, 32, 0, 1.25)


SPELL_FIX = {
    "Invocation d'élémentaire": lambda: (P("M22 10 L42 8 L46 22 L54 30 L50 40 L44 38 L44 60 H36 L34 44 H30 L28 60 H20 L20 38 L14 40 "
                                           "L10 30 L18 22 Z") + black(P("M26 18 L31 20 L27 22 Z") + P("M40 18 L35 20 L39 22 Z")
                                                                 + L([(24, 30), (40, 34)], 1.8))),
    "Coup de tonnerre": lambda: (place(M["marteau"](), 30, 24, 0.62) + R(4, 50, 56, 4, 2)
                                 + S("M10 46 C14 40 18 40 22 46", 2.6) + S("M42 46 C46 40 50 40 54 46", 2.6)
                                 + S("M2 44 C6 34 12 32 16 36", 2.2) + S("M48 36 C52 32 58 34 62 44", 2.2)),
    "Tempête de neige": lambda: (_snow(20, 20, 0.36) + _snow(44, 30, 0.42) + _snow(22, 48, 0.3) + _snow(50, 54, 0.22)
                                 + S("M2 34 C14 30 22 38 34 34", 2.4) + S("M30 12 C42 8 50 16 62 12", 2.4)),
    "Tempête de grêle": lambda: (cloud(18, 0.85) + "".join(Cc(x, y, r) for x, y, r in ((14, 40, 4.4), (30, 44, 5), (46, 40, 4.4), (22, 56, 3.4), (40, 58, 3.4)))
                                 + R(2, 61, 60, 3, 1)),
    "Tempête vengeresse": lambda: (cloud(18, 1.0) + black(P("M18 16 L26 20 L19 22 Z") + P("M46 16 L38 20 L45 22 Z"))
                                   + L([(20, 34), (12, 46), (20, 46), (10, 62)], 3.4) + L([(44, 34), (36, 46), (44, 46), (34, 62)], 3.4)),
    "Héroïsme": lambda: (figure(32, 36, 0.95) + P("M22 26 L10 58 L22 52 Z") + P("M42 26 L54 58 L42 52 Z")
                         + place(M["coeur"](), 32, 8, 0.2) + black(star4(32, 30, 4))),
    "Châtiment calcinant": lambda: (figure(46, 36, 0.8) + _flame(46, 18, 0.3) + _sword(20, 38, 45, 0.8) + burst(36, 32, 5, 6)),
    "Espièglerie de Nathair": lambda: (_m("masque", 32, 36, 0.8) + star4(12, 12, 5) + star4(32, 6, 4) + star4(52, 12, 6)
                                       + Cc(18, 56, 2.4) + Cc(46, 58, 2)),
}

CAP_FIX = {
    "souffle": lambda: place(dragon_head(), 20, 22, 0.55) + _flame(42, 42, 0.42) + _flame(56, 30, 0.3) + _flame(52, 54, 0.26),
    "charmantes defenses": lambda: (figure(22, 36, 0.85) + place(M["coeur"](), 22, 8, 0.2) + dagger(48, 28, 135, 0.6)
                                    + S("M38 44 C42 50 48 52 54 50", 2.2)),
    "bouclier runique": lambda: (P("M32 4 L56 18 V46 L32 60 L8 46 V18 Z") + black(P("M32 10 L50 21 V43 L32 54 L14 43 V21 Z"))
                                 + L([(32, 16), (32, 48)], 4) + L([(32, 24), (42, 18)], 4) + L([(32, 32), (22, 26)], 4)),
    "toucher purifiant": lambda: (figure(32, 40, 0.75) + _hand(32, 10, 0.32, 180) + _drop(20, 22, 0.14) + _drop(44, 22, 0.14)),
    "ascendance gigante": lambda: (figure(42, 30, 1.2) + P("M2 62 L10 44 L16 50 L22 40 L30 62 Z")),
    "lien protecteur": lambda: (figure(14, 36, 0.65) + figure(50, 36, 0.65) + place(M["bouclier"](), 32, 34, 0.55)),
    "puissance des geants": lambda: (fist(32, 24, 0.9) + P("M2 52 L14 48 L26 52 L40 46 L62 52 V62 H2 Z")
                                     + black(L([(22, 52), (28, 58)], 2) + L([(40, 50), (36, 58)], 2)) + Cc(10, 40, 2.6) + Cc(54, 38, 2.4)),
    "tempete dechainee (desert)": lambda: _dunes() + _m("soleil", 44, 16, 0.4),
    "tempete dechainee (mer)": lambda: _m("vague", 30, 38, 0.85) + L([(56, 2), (48, 14), (54, 16), (46, 28)], 3),
    "ame de l'artifice": lambda: _gear(32, 32, 18) + place(M["coeur"](), 32, 32, 0.22),
    "malediction de la lame maudite": lambda: (_sword(32, 32, 45, 1.15) + over("", S("M14 22 C24 14 30 30 40 22 C48 16 54 26 58 22", 3), 4)
                                               + _m("crane", 52, 52, 0.22)),
    "branches de l'arbre": lambda: (place(tree(), 16, 30, 0.5) + S("M24 28 C36 24 40 36 52 30", 4) + figure(50, 44, 0.55)
                                    + S("M44 40 C50 36 56 40 56 46", 3)),
    "connaissance de la pierre": lambda: _m("livre", 26, 40, 0.6) + _m("pierres", 48, 20, 0.4),
    "double illusoire": lambda: figure(20, 32, 1.0) + R(30, 6, 4, 52, 2) + _dashed_fig(),
    "sentinelle au seuil de la mort": lambda: (place(M["crane"](), 32, 30, 0.7) + R(4, 54, 56, 5, 2) + L([(10, 48), (10, 60)], 3)
                                               + L([(54, 48), (54, 60)], 3)),
    "voile necrotique": lambda: (P("M32 22 C42 22 48 30 48 38 L54 62 H10 L16 38 C16 30 22 22 32 22 Z")
                                 + place(M["crane"](), 32, 10, 0.3)),
    "rune de la pierre": lambda: _rune_big(P("M-12 8 L-8 -10 L8 -12 L12 6 L2 12 Z")),
    "rune du feu": lambda: _rune_big(P("M0 14 C-10 14 -12 4 -8 -2 C-6 2 -3 2 -3 0 C-5 -7 0 -12 2 -16 C2 -9 7 -7 8 -2 C10 5 8 14 0 14 Z")),
    "rune du nuage": lambda: _rune_big(P("M-14 8 C-19 8 -19 0 -14 -1 C-14 -7 -7 -10 -2 -6 C0 -12 10 -12 12 -5 C17 -5 19 3 14 8 Z")),
    "frappes terribles": lambda: fist(22, 30, 0.6) + fist(44, 40, 0.6) + burst(34, 14, 7, 7) + burst(54, 56, 5, 6),
    "pretre de guerre": lambda: figure(24, 36, 0.85) + _sword(46, 22, 20, 0.6) + _rays(24, 10, 4, 8, 6, 2),
    "deviation d'assaut": lambda: place(M["bouclier"](), 22, 34, 0.7) + _sword(50, 26, 135, 0.5) + burst(36, 32, 6, 6),
}



# v53 — variantes d'un même sort, tuiles séparées dans l'onglet En partie (« Sort#effet ») : flèches inversées
SPELL_VARIANTS = {
    "agrandissement": lambda: (figure(32, 34, 0.85) + arrow(15, 15, 3, 3, 4.2, 10) + arrow(49, 15, 61, 3, 4.2, 10)
                               + arrow(15, 51, 3, 63, 4.2, 10) + arrow(49, 51, 61, 63, 4.2, 10)),
    "rapetissement": lambda: (figure(32, 35, 0.48) + arrow(3, 3, 18, 18, 4.2, 10) + arrow(61, 3, 46, 18, 4.2, 10)
                              + arrow(3, 63, 18, 48, 4.2, 10) + arrow(61, 63, 46, 48, 4.2, 10)),
}
