"""
Dessins soignés (v53) des objets du sac et du mannequin : potion, parchemin, anneau, baguette, bâton, amulette,
cape, bottes, gants, casque, armure, bouclier, munitions, livre, gemme, sac, outils, torche, rations, et quelques
objets courants (corde, lanterne, instrument, gourde, coffre, clé). Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

from .art_actions import flask
from .art_armes import Cc, G, K, L, P, R, S, boot, shield, star4
from . import art_motifs as M


def _potion():
    return flask(32, 32, 1.2) + star4(52, 12, 4.5)


def _scroll():
    return M._scroll()


def _ring():
    return M._ring()


def _wand():
    return M._wand()


def _staff():
    return (G(R(-3.2, -20, 6.4, 50, 3.2) + R(-3.6, 14, 7.2, 3, 1, K), 30, 34, 25)
            + S("M36 18 C30 12 30 4 38 4 C46 4 46 12 40 14", 3.6) + Cc(38, 10, 3.6) + star4(52, 20, 4))


def _amulet():
    return M._amulet()


def _cape():
    return M._cape()


def _boots():
    return boot(22, 34, 0.75) + G(boot(0, 0, 0.75), 42, 30)


def _gloves():
    return G(R(-12, -4, 22, 24, 6) + R(-12, -20, 5, 18, 2.5) + R(-6, -24, 5, 22, 2.5) + R(0, -23, 5, 21, 2.5)
             + R(6, -18, 5, 16, 2.5) + P("M10 2 L18 -8 C21 -10 24 -7 22 -4 L12 10 Z") + R(-13, 18, 24, 8, 2)
             + L([(-13, 18), (11, 18)], 1.6, K), 32, 30, 0, 1.0)


def _helm():
    return M._helm()


def _armor():
    return M._armor()


def _shield():
    return shield(32, 32, 1.15)


def _ammo():
    return "".join(G(R(-1.6, -22, 3.2, 40, 1.6) + P("M0 -28 L5 -18 L-5 -18 Z") + P("M-1.6 18 L-6 26 L-1.6 23 Z")
                     + P("M1.6 18 L6 26 L1.6 23 Z"), x, 34, a) for x, a in ((22, -14), (32, 0), (42, 14)))


def _book():
    return (P("M14 8 H48 C51 8 52 10 52 12 V56 H18 C14 56 12 54 12 50 V12 C12 10 13 8 14 8 Z")
            + R(16, 48, 36, 6, 1, K) + R(18, 49.5, 34, 3, 1) + star4(32, 26, 9, K) + R(46, 8, 4, 40, 0, K))


def _gem():
    return M._gem()


def _bag():
    return (P("M22 14 C22 8 42 8 42 14 L40 18 C52 22 58 34 56 46 C54 56 46 60 32 60 C18 60 10 56 8 46 C6 34 12 22 24 18 Z")
            + S("M22 18 C28 21 36 21 42 18", 2.4, K) + P("M26 14 C26 12 38 12 38 14", K) + Cc(32, 40, 5, K))


def _tools():
    return M._tool()


def _torch():
    return M._torch()


def _ration():
    """Miche de pain entaillée et morceau de fromage."""
    loaf = P("M6 42 C4 28 16 18 32 18 C48 18 60 28 58 42 C58 48 54 50 48 50 H16 C10 50 6 48 6 42 Z")
    cuts = "".join(S("M{} 24 C{} 30 {} 36 {} 40".format(x, x - 2, x - 3, x - 4), 2.6, K) for x in (20, 32, 44))
    cheese = P("M34 46 L60 40 V56 H34 Z") + Cc(44, 50, 2.2, K) + Cc(53, 48, 1.8, K)
    return loaf + cuts + R(34, 44, 26, 4, 0, K) + cheese


def _rope():
    return S("M32 32 m-4 0 a4 4 0 1 1 8 0 a10 10 0 1 1 -20 0 a16 16 0 1 1 32 0 a22 22 0 1 1 -44 0", 5)


def _lantern():
    return (S("M24 12 C24 4 40 4 40 12", 3.4) + R(20, 12, 24, 6, 2) + P("M22 18 H42 L46 48 H18 Z")
            + P("M26 22 H38 L41 44 H23 Z", K) + P("M32 26 C35 30 37 33 37 36 C37 40 35 42 32 42 C29 42 27 40 27 36 "
                                                  "C27 33 29 30 32 26 Z") + R(16, 48, 32, 7, 2))


def _instrument():
    return (G('<ellipse cx="0" cy="12" rx="15" ry="17" fill="#FFFFFF"/>' + R(-3, -30, 6, 30, 2) + R(-6, -36, 12, 8, 2)
              + Cc(0, 10, 5, K) + L([(0, -28), (0, 24)], 1.2, K) + R(-8, 22, 16, 3, 1, K), 32, 34, 30, 1.0))


def _waterskin():
    return (P("M28 6 H36 V14 C48 18 56 28 56 40 C56 52 46 60 32 60 C18 60 8 52 8 40 C8 28 16 18 28 14 Z")
            + R(26, 4, 12, 6, 2) + S("M16 40 C20 50 28 54 36 54", 2.4, K) + Cc(42, 30, 3, K))


def _chest():
    return (P("M8 26 C8 14 18 8 32 8 C46 8 56 14 56 26 Z") + R(8, 28, 48, 28, 2) + R(8, 26, 48, 4, 0, K)
            + R(28, 22, 8, 12, 2, K) + R(30, 24, 4, 8, 1) + L([(18, 10), (18, 56)], 2.4, K) + L([(46, 10), (46, 56)], 2.4, K))


def _key():
    return G('<circle cx="0" cy="-16" r="10" fill="none" stroke="#FFFFFF" stroke-width="6"/>' + R(-3.2, -6, 6.4, 34, 2)
             + R(3, 16, 10, 5, 1) + R(3, 23, 7, 5, 1), 32, 32, 40, 1.0)


def _generic():
    return _bag()


OBJECTS = {"objet_potion": _potion, "objet_parchemin": _scroll, "objet_anneau": _ring, "objet_baguette": _wand,
           "objet_baton": _staff, "objet_amulette": _amulet, "objet_cape": _cape, "objet_bottes": _boots,
           "objet_gants": _gloves, "objet_casque": _helm, "objet_armure": _armor, "objet_bouclier": _shield,
           "objet_munitions": _ammo, "objet_livre": _book, "objet_gemme": _gem, "objet_sac": _bag,
           "objet_outil": _tools, "objet_torche": _torch, "objet_ration": _ration, "objet_corde": _rope,
           "objet_lanterne": _lantern, "objet_instrument": _instrument, "objet_gourde": _waterskin,
           "objet_coffre": _chest, "objet_cle": _key, "objet": _generic}
