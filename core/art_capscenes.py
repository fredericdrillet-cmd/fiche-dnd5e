"""
Scènes dessinées (v53) des capacités de classe, de sous-classe et d'espèce : un dessin d'un seul tenant par
capacité (remplace la formule à deux éléments de core/art_capacites). Grille 64 × 64, blanc = dessin, noir = découpe.
Clés : nom normalisé de la capacité (comme dans art_capacites.FORMULES).
"""
from __future__ import annotations

import math

from .art_armes import Cc, G, K, L, P, R, S, boot, burst, curved_arrow, dagger, fist, footprint, star4
from .art_kit import angel_wings, bird, black, cloud, doorway, dragon_head, figure, insect, place, tornado, tree
from .art_motifs import MOTIFS as M
from .art_scenes2 import _bubble, _dashed, _drop, _flame, _hand, _head, _rays, _snow, _sword


def _m(n, x=32, y=32, s=1.0):
    return place(M[n](), x, y, s)


def _shield(x=32, y=32, s=1.0):
    return place(M["bouclier"](), x, y, s)


def _wolf(x=32, y=32, s=1.0):
    from .art_retouches import wolf_profile
    return wolf_profile(x, y, s)


def _kneel(x, y, s=1.0):
    return G(Cc(0, -14, 6) + P("M-9 -6 H9 L10 8 L16 22 H9 L4 12 L-4 12 L-6 24 H-12 L-10 8 Z"), x, y, 0, s)


def _ring(r=28, w=3, dash=""):
    d = ' stroke-dasharray="{}"'.format(dash) if dash else ""
    return '<circle cx="32" cy="32" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"{}/>'.format(r, w, d)


def _arrow(x1, y1, x2, y2, w=3.2):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - 8 * math.cos(a), y2 - 8 * math.sin(a)
    px, py = -math.sin(a) * 5, math.cos(a) * 5
    return L([(x1, y1), (bx, by)], w) + P("M{:g} {:g} L{:g} {:g} L{:g} {:g} Z".format(x2, y2, bx + px, by + py, bx - px, by - py))


def _cape(x=32, y=32, s=1.0):
    return place(M["cape"](), x, y, s)


def _wing(x, y, s=1.0, flip=False):
    w = M["aile"]()
    if flip:
        w = '<g transform="translate(64 0) scale(-1 1)">' + w + "</g>"
    return place(w, x, y, s)


A = {
    "adaptation du terrain": lambda: figure(32, 26, 0.75) + P("M2 52 L14 44 L26 50 L40 42 L62 50 V62 H2 Z") + S("M10 36 C16 30 20 30 24 34", 2.2) + S("M40 34 C44 30 48 30 54 36", 2.2),
    "ailes de dragon": lambda: _wing(18, 30, 0.6) + _wing(46, 30, 0.6, True) + figure(32, 36, 0.6) + black(S("M22 26 L28 32 M42 26 L36 32", 1.6)),
    "allegeance divine": lambda: _kneel(32, 44, 0.85) + _rays(32, 12, 4, 10, 8, 2.4) + Cc(32, 12, 3) + L([(32, 18), (32, 26)], 2),
    "ame de l'artifice": lambda: _m("coeur", 32, 34, 0.75) + black("".join(G(R(-2, -7, 4, 4, 1), 32, 32, a) for a in range(0, 360, 45)) + Cc(32, 32, 4)),
    "ame oceane & tentacule gardien": lambda: _m("vague", 26, 40, 0.75) + S("M46 60 C42 44 54 38 50 24 C48 16 54 12 58 14", 5),
    "ame radieuse": lambda: figure(32, 36, 0.8) + _wing(14, 22, 0.4) + _wing(50, 22, 0.4, True) + _rays(32, 14, 6, 10, 8, 2),
    "ame vengeresse": lambda: _dashed(figure(26, 32, 1.0), "3 2", 2.2) + _sword(46, 28, 20, 0.6),
    "ange de la vengeance": lambda: angel_wings() + _flame(52, 48, 0.28) + _flame(12, 48, 0.24),
    "animation fongique": lambda: P("M8 30 C8 18 20 10 32 10 C44 10 56 18 56 30 Z") + R(26, 30, 12, 24, 4) + black(Cc(20, 22, 3) + Cc(40, 18, 2.6) + Cc(46, 26, 2)) + _m("crane", 52, 52, 0.24),
    "arme occulte": lambda: _sword(30, 34, 45, 1.1) + black(place(M["oeil"](), 26, 38, 0.2)) + star4(54, 10, 5),
    "armes du kensei, parade agile & tir du kensei": lambda: G(R(-2.6, -28, 5.2, 56, 2.6), 32, 32, 45) + G(R(-2.6, -28, 5.2, 56, 2.6), 32, 32, -45) + Cc(32, 32, 6),
    "armure de malefices": lambda: _m("armure", 32, 34, 0.9) + black(place(M["crane"](), 32, 34, 0.28)) + _rays(32, 34, 26, 30, 8, 2),
    "armure parachevee": lambda: _m("armure", 32, 36, 0.85) + _rays(32, 36, 26, 30, 10, 2) + star4(54, 8, 5),
    "ascendance draconique": lambda: figure(18, 36, 0.8) + place(dragon_head(), 46, 22, 0.45) + L([(26, 30), (36, 26)], 1.8),
    "ascendance gigante": lambda: figure(32, 30, 1.2) + P("M2 56 L12 50 L22 54 L32 48 L44 54 L62 50 V62 H2 Z"),
    "attaque de frenesie": lambda: G(R(-2.6, -26, 5.2, 50, 2.6) + P("M2 -24 C14 -28 22 -20 24 -8 C22 2 14 6 2 2 Z"), 28, 34, 35, 1.0) + _flame(50, 16, 0.34),
    "attenuation des elements": lambda: _shield(32, 34, 0.85) + _flame(8, 10, 0.18) + _snow(56, 10, 0.16) + place(M["eclair"](), 8, 56, 0.2),
    "attraction violente": lambda: _hand(20, 40, 0.65, 90) + figure(50, 34, 0.7) + S("M28 30 C36 26 40 26 44 28", 2.4) + S("M28 40 C36 44 40 44 44 42", 2.4),
    "aura de tempete : desert": lambda: figure(32, 36, 0.7) + _rays(32, 32, 22, 30, 12, 2.6) + _m("soleil", 52, 10, 0.2),
    "aura de tempete : mer": lambda: figure(32, 30, 0.7) + S("M2 52 C10 46 18 58 26 52 C34 46 42 58 50 52 C56 48 60 54 62 52", 3.4) + S("M4 60 C12 56 20 62 30 58", 2.6),
    "aura de tempete : toundra": lambda: figure(32, 36, 0.7) + _snow(10, 12, 0.2) + _snow(54, 12, 0.2) + _snow(10, 52, 0.16) + _snow(54, 52, 0.16),
    "aura du gardien": lambda: figure(20, 36, 0.7) + figure(44, 36, 0.7) + S("M6 24 C6 8 58 8 58 24", 4),
    "aura du phenix": lambda: place(bird(), 32, 30, 1.0) + _flame(14, 50, 0.24) + _flame(32, 54, 0.28) + _flame(50, 50, 0.24),
    "aval de la terre": lambda: _shield(32, 30, 0.8) + P("M2 54 L14 48 L26 52 L40 46 L62 52 V62 H2 Z"),
    "avenir convergent": lambda: _m("oeil", 32, 24, 0.6) + _arrow(8, 56, 28, 40) + _arrow(56, 56, 36, 40) + Cc(32, 40, 3),
    "balancement emeche": lambda: G(figure(0, 0, 1.0), 30, 34, -18) + S("M48 14 C54 18 54 26 48 30", 2.4) + Cc(50, 46, 4) + black(Cc(50, 46, 2)),
    "bastion de la loi": lambda: R(10, 20, 44, 40, 2) + "".join(R(x, 12, 8, 10, 1) for x in (10, 22, 34, 46)) + black(R(30, 30, 4, 20, 1) + R(20, 30, 24, 3, 1)),
    "baume de la cour d'ete": lambda: _m("feuille", 26, 34, 0.75) + place(M["soin"](), 48, 18, 0.32) + Cc(44, 46, 2.4) + Cc(52, 52, 2),
    "benediction de l'escroc": lambda: _m("masque", 32, 36, 0.85) + _rays(32, 12, 4, 9, 6, 2, 200) + Cc(32, 12, 3),
    "benediction de la forge": lambda: P("M10 40 H48 C48 46 42 48 38 48 L40 58 H18 L20 48 C14 48 10 46 10 40 Z") + R(48, 40, 10, 4, 2) + _rays(30, 18, 6, 12, 8, 2.4) + Cc(30, 18, 3),
    "benediction de la reine corbeau": lambda: place(bird(), 32, 34, 1.0) + _m("lune", 50, 8, 0.22),
    "bond psi": lambda: figure(40, 22, 0.75, 20) + curved_arrow("M6 58 C10 40 20 30 32 28", (32, 28), -20, 3, 8) + black(Cc(40, 8, 2)),
    "bouclier runique": lambda: _shield(32, 32, 1.05) + black(L([(32, 18), (32, 44)], 3) + L([(32, 24), (40, 18)], 3) + L([(32, 32), (24, 26)], 3)),
    "bouclier solaire": lambda: _shield(32, 36, 0.85) + _rays(32, 36, 24, 30, 10, 2.6),
    "bouclier spirituel": lambda: _dashed(_shield(32, 32, 1.1), "3 2", 2.6) + star4(32, 32, 8),
    "branches de l'arbre": lambda: tree() + S("M8 30 C2 22 4 14 10 12", 3.4) + figure(56, 52, 0.3),
    "bras du moi astral": lambda: _dashed(G(R(-14, -4, 26, 26, 8) + R(-14, -22, 6, 22, 3) + R(-7, -26, 6, 26, 3) + R(0, -25, 6, 25, 3) + R(7, -20, 6, 20, 3), 32, 34, 0, 1.1), "3 2", 2.4) + star4(52, 10, 5),
    "bribes des defunts": lambda: _m("crane", 24, 38, 0.6) + _bubble(46, 16, 0.4) + black(Cc(40, 14, 1.6) + Cc(46, 14, 1.6) + Cc(52, 14, 1.6)),
    "cadran d'arcanes & retrogradation": lambda: _ring(26, 3.4) + "".join(L([(32 + 20 * math.cos(a), 32 + 20 * math.sin(a)), (32 + 24 * math.cos(a), 32 + 24 * math.sin(a))], 2.4) for a in [k * math.pi / 6 for k in range(12)]) + L([(32, 32), (32, 16)], 3) + curved_arrow("M44 22 C40 16 36 14 32 14", (24, 16), 190, 2.2, 6),
    "camouflage svirfnebelin": lambda: P("M4 58 L10 30 L24 24 L34 34 L46 22 L60 30 L60 58 Z") + black(_dashed(figure(32, 44, 0.45), "2 2", 1.6)),
    "canon occulte": lambda: P("M8 44 L44 22 L50 32 L14 54 Z") + Cc(14, 52, 7) + Cc(30, 46, 6) + black(Cc(14, 52, 3) + Cc(30, 46, 2.4)) + burst(54, 22, 7, 8),
    "carapace cameleon": lambda: P("M6 44 C6 30 18 22 32 22 C46 22 56 30 58 40 L62 42 L56 46 H8 Z") + black("".join(Cc(x, y, 2.4) for x, y in ((20, 32), (32, 30), (44, 32), (26, 40), (40, 40)))) + S("M58 40 C62 36 60 30 56 30", 2),
    "carapace necrotique": lambda: _m("armure", 32, 36, 0.85) + black(S("M22 30 L42 50 M42 30 L22 50", 2)) + _m("crane", 52, 10, 0.2),
    "champ defensif": lambda: figure(32, 38, 0.7) + _ring(24, 3, "5 3") + _shield(52, 12, 0.26),
    "champ protecteur": lambda: figure(18, 38, 0.65) + figure(44, 38, 0.65) + _dashed(_shield(32, 26, 0.9), "3 2", 2.4),
    "champion antique": lambda: figure(32, 34, 0.9) + _m("couronne", 32, 8, 0.28) + _sword(50, 40, 20, 0.45),
    "chance alteree": lambda: Cc(32, 32, 20) + black(Cc(32, 32, 15)) + _m("etoile", 32, 32, 0.4) + curved_arrow("M54 40 C58 28 54 16 44 10", (44, 10), 210, 2.6, 7),
    "chance du nombre": lambda: figure(14, 40, 0.55) + figure(32, 36, 0.65) + figure(50, 40, 0.55) + star4(32, 8, 6),
    "chance du tenebreux": lambda: _m("lune", 32, 34, 0.75) + star4(52, 18, 6) + star4(18, 52, 4),
    "chance forcee": lambda: _hand(26, 42, 0.7, 0) + star4(46, 14, 10) + S("M34 26 C38 22 40 20 42 20", 2),
    "chancellements emeches": lambda: G(figure(0, 0, 1.0), 26, 34, 15) + footprint(48, 50, -30, 0.5) + footprint(56, 40, 20, 0.45),
    "changeforme": lambda: _dashed(figure(18, 34, 0.75), "3 2", 2) + figure(46, 34, 0.75) + curved_arrow("M24 14 C30 6 36 6 40 12", (40, 12), 40, 2.2, 6),
    "chant de defense": lambda: _m("note", 24, 34, 0.6) + _shield(46, 36, 0.55),
    "chant de la lame": lambda: _sword(30, 36, 45, 1.0) + _m("note", 50, 16, 0.3) + S("M44 32 C48 28 52 30 56 26", 2),
    "charmantes defenses": lambda: _shield(32, 34, 0.95) + black(place(M["coeur"](), 32, 32, 0.3)),
    "charme instinctif": lambda: _m("coeur", 32, 32, 0.8) + curved_arrow("M10 48 C4 36 8 22 18 16", (18, 16), -40, 2.4, 6),
    "chatiment de sang": lambda: _sword(28, 32, 45, 1.05) + _drop(46, 46, 0.22) + _drop(54, 56, 0.16),
    "chatiment divin (gratuit)": lambda: _sword(26, 38, 45, 1.0) + star4(48, 16, 12) + _rays(48, 16, 14, 18, 8, 1.8),
    "chatiment divin (sort)": lambda: _sword(32, 36, 0, 1.15) + _rays(32, 10, 6, 12, 8, 2.4) + Cc(32, 10, 3),
    "chien de mauvais augure": lambda: _dashed(_wolf(32, 36, 0.85), "3 2", 2.2) + _m("lune", 52, 8, 0.2),
    "clone d'ombre": lambda: figure(32, 26, 0.85) + P("M24 50 L56 56 L60 62 L20 58 Z") + black(L([(30, 52), (52, 57)], 1.4)),
    "combat perspicace": lambda: _m("oeil", 32, 18, 0.55) + _sword(32, 46, 90, 0.7),
    "combattant clairvoyant": lambda: _sword(24, 40, 45, 0.95) + _m("oeil", 46, 16, 0.42) + _rays(46, 16, 14, 17, 6, 2),
    "commander le compagnon": lambda: _wolf(42, 40, 0.6) + figure(14, 34, 0.7) + _bubble(22, 10, 0.26),
    "commander le defenseur d'acier": lambda: R(34, 22, 24, 28, 4) + R(38, 8, 16, 12, 3) + black(Cc(43, 14, 2) + Cc(49, 14, 2)) + figure(14, 34, 0.7) + _bubble(18, 8, 0.24),
    "comme par hasard": lambda: Cc(30, 34, 14) + black(Cc(30, 34, 10)) + star4(30, 34, 6) + curved_arrow("M44 20 C50 12 56 12 60 16", (60, 16), 30, 2.2, 6) + star4(52, 50, 4),
    "compagnon primitif": lambda: _wolf(32, 36, 0.85) + _m("feuille", 54, 10, 0.2) + _m("feuille", 10, 10, 0.16),
    "concu pour reussir": lambda: R(12, 18, 40, 34, 4) + black(Cc(24, 32, 4) + Cc(40, 32, 4) + R(24, 42, 16, 3, 1)) + star4(52, 8, 6) + L([(32, 6), (32, 18)], 2.4),
    "conduit divin : benediction du dieu de la guerre": lambda: _sword(32, 36, 0, 1.0) + _rays(32, 14, 6, 12, 8, 2.4) + R(14, 30, 36, 5, 2),
    "conduit divin : emissaire de paix & reprimander la violence": lambda: place(bird(), 32, 30, 0.9) + P("M44 30 C50 34 52 38 48 40 Z") + _rays(32, 10, 4, 8, 6, 2),
    "conjuration mineure": lambda: _hand(22, 44, 0.65, 0) + P("M38 14 L52 12 L56 24 L44 30 L36 24 Z") + star4(30, 14, 4) + S("M30 30 C34 26 36 24 38 24", 2),
    "connaissance d'une vie anterieure": lambda: _head(26, 38, 0.65) + _dashed(_head(42, 30, 0.55), "2 2", 1.8),
    "connaissance de la pierre": lambda: P("M6 56 L10 28 L26 20 L40 30 L58 22 L60 56 Z") + black(place(M["oeil"](), 32, 40, 0.36)),
    "conquerant invincible": lambda: figure(32, 36, 0.85) + _m("couronne", 32, 10, 0.3) + _shield(52, 44, 0.3) + _sword(12, 44, -20, 0.4),
    "conscience magique": lambda: _m("oeil", 32, 32, 0.9) + star4(10, 10, 5) + star4(54, 10, 4) + star4(32, 58, 4),
    "conscience temporelle & dephasage chronal": lambda: Cc(32, 34, 22) + black(Cc(32, 34, 17)) + L([(32, 34), (32, 22)], 3) + L([(32, 34), (40, 38)], 3) + _dashed(Cc(40, 26, 22), "3 3", 2),
    "contre-attaque du tueur": lambda: dagger(26, 38, 45, 1.1) + curved_arrow("M46 54 C58 44 58 24 48 16", (48, 16), 220, 3, 8),
    "convocation de l'esprit du feu sauvage": lambda: _flame(32, 32, 1.0) + black(Cc(26, 34, 2.4) + Cc(38, 34, 2.4)) + '<ellipse cx="32" cy="58" rx="22" ry="4" fill="none" stroke="#FFFFFF" stroke-width="2.4"/>',
    "cornes martelantes": lambda: _head(28, 38, 0.75) + P("M30 14 C26 6 20 2 14 2 C20 6 22 12 24 18 Z") + burst(54, 30, 7, 7),
    "coup de chance": lambda: Cc(26, 36, 16) + black(Cc(26, 36, 12)) + star4(26, 36, 7) + L([(44, 2), (36, 16), (42, 18), (34, 30)], 3),
    "courroux de la tempete": lambda: cloud(20, 0.9) + L([(32, 34), (24, 48), (32, 48), (22, 62)], 3.4) + S("M2 58 C10 54 14 62 20 58", 2.4),
    "courroux des mers": lambda: _m("vague", 32, 32, 1.0) + L([(54, 4), (48, 14), (52, 16), (46, 26)], 2.6),
    "cri draconique": lambda: place(dragon_head(), 26, 34, 0.75) + S("M52 22 C58 28 58 38 52 44", 3) + S("M58 16 C66 26 66 40 58 50", 2.6),
    "decharge arcanique": lambda: _hand(18, 46, 0.55, 40) + L([(28, 34), (40, 26), (36, 22), (52, 12)], 4) + burst(54, 10, 7, 8),
    "decharge elementaire": lambda: _hand(16, 46, 0.5, 40) + _flame(46, 22, 0.4) + _snow(54, 44, 0.16) + L([(26, 36), (38, 28)], 3),
    "defense de carapace": lambda: P("M6 46 C6 28 18 16 32 16 C46 16 58 28 58 46 Z") + black("".join(P("M{} {} l6 -5 l6 5 l-6 5 Z".format(x, y)) for x, y in ((16, 34), (26, 26), (38, 26), (40, 38), (26, 38)))) + R(4, 46, 56, 4, 2),
    "defense de chasseur superieure": lambda: _m("arc", 24, 32, 0.6) + _shield(48, 38, 0.5),
    "defense glorieuse": lambda: _shield(32, 36, 0.9) + _rays(32, 36, 26, 30, 8, 2.4),
    "defense patiente (gratuite)": lambda: _kneel(30, 42, 0.85) + _shield(50, 20, 0.36),
    "defense spectrale": lambda: _dashed(figure(32, 32, 1.0), "3 2", 2.2) + _shield(50, 46, 0.32),
    "defenseur vigilant": lambda: _shield(30, 38, 0.8) + _m("oeil", 32, 10, 0.36),
    "deplacement exaltant": lambda: figure(34, 26, 0.85, 20) + _arrow(10, 56, 30, 36, 3) + S("M2 46 H12", 2.6),
    "deviation arcanique": lambda: _shield(26, 34, 0.85) + _arrow(54, 8, 40, 22, 2.6) + S("M44 30 C50 36 54 40 60 42", 2.4) + star4(56, 50, 4),
    "deviation arcanique & esprit tactique": lambda: _shield(22, 38, 0.65) + _head(46, 24, 0.45) + star4(52, 52, 5),
    "deviation d'assaut": lambda: _shield(26, 34, 0.85) + _sword(52, 16, 135, 0.45) + curved_arrow("M44 40 C52 46 56 52 58 58", (58, 58), 70, 2.4, 6),
    "disciple draconique": lambda: _m("livre", 32, 44, 0.65) + place(dragon_head(), 32, 18, 0.42),
    "dispersion de l'essaim": lambda: place(insect(), 14, 18, 0.28) + place(insect(), 50, 16, 0.26) + place(insect(), 12, 48, 0.26) + place(insect(), 52, 50, 0.28) + figure(32, 34, 0.5),
    "don elementaire": lambda: _hand(32, 46, 0.6, 0) + _flame(18, 16, 0.22) + _drop(32, 12, 0.2) + _snow(46, 16, 0.16),
    "don feerique": lambda: _wing(18, 30, 0.55) + _wing(46, 30, 0.55, True) + star4(32, 34, 9),
    "double illusoire": lambda: figure(20, 32, 1.0) + _dashed(figure(44, 32, 1.0), "4 2", 2.2) + star4(56, 8, 4) + star4(32, 58, 3),
    "echappatoire brumeuse": lambda: _dashed(figure(20, 30, 0.75), "2 2", 1.6) + S("M4 48 C10 44 16 52 24 48 C32 44 38 52 46 48", 3) + S("M10 58 C18 54 26 62 34 58", 2.6) + figure(50, 24, 0.55),
    "elixir experimental": lambda: _m("fiole", 32, 34, 0.9) + Cc(14, 14, 3) + Cc(22, 6, 2.4) + star4(52, 12, 5),
    "embuscade effrayante": lambda: P("M4 58 C4 38 14 24 28 24 C34 24 38 28 40 34 L60 58 Z") + black(P("M16 40 L24 42 L17 45 Z") + P("M34 40 L26 42 L33 45 Z")) + S("M44 14 L48 8 M52 16 L58 12", 2.4),
    "embusque redoutable": lambda: P("M4 58 C10 40 18 34 26 34 C34 34 40 42 44 58 Z") + _m("arc", 46, 24, 0.45),
    "endurance de pierre": lambda: figure(32, 30, 1.05) + black(L([(26, 16), (30, 26)], 1.8) + L([(36, 34), (34, 46)], 1.8)) + P("M2 56 L14 52 L28 56 L42 52 L62 56 V62 H2 Z"),
}


def scenes() -> dict:
    """Toutes les scènes de capacités (lots A, B, C)."""
    out = dict(A)
    for extra in ("B", "C"):
        out.update(globals().get(extra, {}))
    return out


B = {
    "endurance implacable": lambda: _kneel(30, 40, 0.9) + place(M["coeur"](), 52, 16, 0.3) + L([(4, 60), (60, 60)], 2.4),
    "entite symbiotique": lambda: figure(32, 34, 0.85) + S("M14 58 C10 44 18 36 22 28", 3) + S("M50 58 C54 44 46 36 42 28", 3) + _m("feuille", 12, 14, 0.18) + _m("feuille", 52, 14, 0.18),
    "escarmoucheur": lambda: figure(30, 32, 0.9, 15) + _sword(50, 20, 40, 0.45) + S("M2 44 H14", 3) + S("M4 52 H16", 3),
    "escarmoucheur & survivaliste": lambda: figure(24, 34, 0.85) + _shield(48, 36, 0.4) + S("M2 50 H12", 2.6),
    "esprit combatif": lambda: fist(32, 38, 0.95) + L([(48, 2), (40, 14), (46, 16), (38, 28)], 3) + L([(14, 6), (18, 14)], 2.4),
    "esprit de l'aigle : foncer": lambda: place(bird(), 36, 24, 0.85) + S("M2 40 H24", 3) + S("M6 50 H28", 3) + S("M2 60 H20", 3),
    "esprit du feu sauvage : graine de flamme": lambda: _flame(32, 26, 0.6) + P("M24 46 C24 40 40 40 40 46 C40 54 24 54 24 46 Z") + black(Cc(32, 47, 2)) + L([(32, 54), (32, 62)], 2.4),
    "esprit garde": lambda: _dashed(figure(32, 34, 1.0), "3 2", 2.2) + black(Cc(29, 14, 1.6) + Cc(35, 14, 1.6)) + _ring(28, 2, "3 4"),
    "esprit manifeste": lambda: _dashed(figure(32, 34, 1.0), "2 2", 2) + _rays(32, 34, 24, 28, 10, 2),
    "esprit totem": lambda: R(20, 18, 24, 42, 2) + black(P("M24 24 L30 26 L25 28 Z") + P("M40 24 L34 26 L39 28 Z") + R(26, 34, 12, 4, 1) + L([(20, 44), (44, 44)], 2)) + P("M14 18 H50 L32 4 Z"),
    "esquive des ombres": lambda: _dashed(figure(20, 32, 0.9), "2 2", 1.8) + figure(42, 32, 0.9, -15) + _m("lune", 54, 8, 0.18),
    "esquive hadozi": lambda: figure(30, 32, 0.85, -20) + _wing(46, 34, 0.42, True) + _wing(14, 34, 0.42),
    "essaim rassemble": lambda: "".join(place(insect(), 32 + 20 * math.cos(a), 32 + 20 * math.sin(a), 0.22) for a in [k * math.pi / 4 for k in range(8)]) + Cc(32, 32, 5),
    "etincelle astrale": lambda: star4(32, 32, 22) + Cc(32, 32, 4, K) + _rays(32, 32, 24, 28, 8, 2),
    "faveur des dieux": lambda: _hand(32, 46, 0.6, 0) + star4(32, 14, 10) + _rays(32, 14, 12, 16, 8, 2),
    "fioriture defensive": lambda: _sword(26, 30, 0, 0.9) + S("M10 40 C16 52 36 54 44 44", 3) + _shield(50, 46, 0.3),
    "fioriture mobile": lambda: _sword(22, 30, 30, 0.8) + S("M8 52 C20 60 36 58 48 50", 3) + figure(50, 30, 0.5),
    "fioriture tranchante": lambda: _sword(30, 32, 45, 0.95) + S("M6 20 C10 40 24 54 44 58", 3) + S("M14 16 C18 34 30 46 48 50", 2.2),
    "flammes cauterisantes": lambda: _flame(26, 32, 0.7) + place(M["soin"](), 50, 46, 0.3),
    "fleche affaiblissante": lambda: _arrow(6, 56, 50, 12, 3.2) + G(R(-3, -8, 6, 10, 2) + P("M-8 2 H8 L0 10 Z"), 52, 46, 0, 0.8),
    "fleche bannissante": lambda: _arrow(6, 56, 40, 22, 3.2) + '<ellipse cx="50" cy="16" rx="8" ry="13" fill="#FFFFFF"/>' + black('<ellipse cx="50" cy="16" rx="4.6" ry="9" fill="#FFFFFF"/>'),
    "fleche charmeuse": lambda: _arrow(6, 56, 42, 20, 3.2) + place(M["coeur"](), 50, 14, 0.3),
    "fleche de saisie": lambda: _arrow(6, 56, 50, 12, 3.2) + S("M24 38 C18 34 22 26 28 30 C34 34 30 42 24 38", 2.2) + S("M34 28 C30 22 36 16 40 22", 2.2),
    "fleche explosive": lambda: _arrow(6, 56, 40, 22, 3.2) + burst(48, 14, 12, 10),
    "fleche perforante": lambda: _arrow(2, 50, 62, 14, 3.2) + figure(24, 30, 0.6) + figure(42, 26, 0.55),
    "force avant la mort": lambda: _m("crane", 22, 36, 0.55) + fist(46, 30, 0.6) + burst(56, 12, 6, 6),
    "force vivifiante": lambda: figure(32, 34, 0.9) + L([(50, 2), (42, 14), (48, 16), (40, 28)], 3) + place(M["coeur"](), 14, 14, 0.22),
    "forme de geant": lambda: figure(40, 30, 1.2) + figure(10, 50, 0.4) + _arrow(10, 30, 10, 12, 2.4),
    "forme de la bete": lambda: _wolf(26, 38, 0.7) + "".join(S("M{a} 6 C{b} 14 {c} 24 {d} 32".format(a=x + 6, b=x + 3, c=x - 1, d=x - 4), 3) for x in (40, 48, 56)),
    "forme de la bete : griffes": lambda: _hand(26, 34, 0.8, 0) + "".join(P("M{} 8 L{} 2 L{} 10 Z".format(x, x + 2, x + 4)) for x in (14, 21, 28, 35)) + S("M44 20 L52 44 M50 18 L58 40", 2.4),
    "forme de la bete : morsure": lambda: P("M4 24 C14 10 50 10 60 24 L48 26 L44 32 L40 26 L36 32 L32 26 L28 32 L24 26 L20 32 L16 26 Z") + P("M4 40 C14 54 50 54 60 40 L48 38 L44 32 L40 38 L36 32 L32 38 L28 32 L24 38 L20 32 L16 38 Z"),
    "forme de la bete : queue": lambda: S("M6 50 C18 54 30 50 36 40 C42 30 50 26 58 30", 6) + P("M58 22 L64 30 L56 36 Z"),
    "forme etoilee": lambda: figure(32, 34, 0.85) + "".join(star4(32 + 24 * math.cos(a), 32 + 24 * math.sin(a), 3.4) for a in [k * math.pi / 3 for k in range(6)]),
    "forme hybride": lambda: P("M32 10 C40 10 44 16 44 22 L52 12 L50 24 C52 28 52 32 50 36 H42 L44 60 H36 L34 44 H30 L28 60 H20 L22 36 H14 L16 24 C16 16 22 10 32 10 Z") + black(P("M26 20 L32 22 L27 24 Z") + P("M40 20 L34 22 L39 24 Z")),
    "forme sauvage de combat : soins": lambda: _wolf(28, 36, 0.8) + place(M["soin"](), 52, 14, 0.3),
    "forme stellaire": lambda: star4(32, 30, 24) + black(figure(32, 32, 0.45)) + star4(54, 54, 4),
    "formes de metamorphose": lambda: _wolf(20, 22, 0.42) + place(bird(), 44, 22, 0.34) + place(insect(), 32, 48, 0.34) + _ring(28, 2, "4 4"),
    "foulee d'ombre": lambda: _dashed(figure(16, 34, 0.7), "2 2", 1.6) + figure(48, 34, 0.7) + P("M24 50 C30 46 38 46 44 50 C38 54 30 54 24 50 Z") + _m("lune", 32, 10, 0.2),
    "foulee des fees": lambda: _dashed(figure(16, 34, 0.7), "2 2", 1.6) + figure(48, 34, 0.7) + _wing(32, 16, 0.3) + star4(32, 48, 5),
    "frappe en arc ardent": lambda: _sword(26, 38, 45, 0.95) + S("M8 18 C20 4 44 4 56 18", 4) + _flame(56, 26, 0.24),
    "frappe malicieuse : assommer": lambda: dagger(22, 40, 45, 0.9) + _head(46, 28, 0.45) + star4(46, 6, 4) + star4(56, 12, 3),
    "frappe malicieuse : aveugler": lambda: dagger(22, 40, 45, 0.9) + _m("oeil_clos", 46, 22, 0.42),
    "frappe malicieuse : croc-en-jambe": lambda: dagger(22, 34, 45, 0.85) + boot(46, 40, 0.5) + curved_arrow("M30 58 C40 62 50 60 58 52", (58, 52), -40, 2.2, 6),
    "frappe malicieuse : hebetement": lambda: dagger(22, 40, 45, 0.9) + _m("spirale", 46, 22, 0.36),
    "frappe malicieuse : poison": lambda: dagger(24, 36, 45, 1.0) + _drop(46, 46, 0.2) + _drop(54, 56, 0.16) + _drop(38, 54, 0.14),
    "frappe malicieuse : repli": lambda: dagger(18, 40, 45, 0.85) + figure(48, 32, 0.6, -10) + curved_arrow("M44 54 C52 58 58 54 60 48", (60, 48), -60, 2.2, 6),
    "frappe psionique": lambda: fist(26, 38, 0.8) + _m("cerveau", 48, 16, 0.36) + S("M38 26 C42 22 44 22 46 26", 2),
    "frappes autoguidees": lambda: _arrow(6, 50, 36, 30, 3) + curved_arrow("M36 30 C46 24 48 14 46 10", (46, 10), -80, 3, 8) + place(M["cible"](), 50, 46, 0.3),
    "frappes terribles": lambda: fist(28, 34, 0.9) + burst(50, 20, 12, 10),
    "frappes terrifiantes": lambda: fist(26, 38, 0.8) + _m("crane", 48, 18, 0.38),
    "frayeur predatrice": lambda: "".join(S("M{a} 8 C{b} 22 {c} 38 {d} 56".format(a=x + 8, b=x + 4, c=x - 2, d=x - 6), 4) for x in (14, 28, 42)) + _m("crane", 50, 50, 0.2),
    "fuite agile": lambda: figure(40, 30, 0.85, 20) + S("M2 40 H20", 3) + S("M6 50 H24", 3) + S("M2 60 H16", 3),
    "fuite brumeuse": lambda: _dashed(figure(28, 28, 0.85), "2 3", 2) + S("M4 50 C12 44 20 56 30 50 C40 44 48 56 58 50", 3.4) + S("M8 60 C16 54 24 64 34 58", 2.6),
    "fureur de la tempete": lambda: tornado() + L([(52, 4), (46, 16), (52, 18), (44, 30)], 3),
    "fureur des petits": lambda: figure(32, 40, 0.6) + _rays(32, 38, 18, 26, 8, 3) + fist(32, 14, 0.3),
    "gambade heureuse": lambda: G(figure(0, 0, 1.0), 30, 30, -10) + _m("note", 52, 16, 0.24) + S("M4 58 C14 52 24 52 34 58", 2.4),
    "garde entropique": lambda: _shield(30, 34, 0.85) + S("M50 14 C58 18 58 28 50 30 C44 32 44 40 50 42", 2.6),
    "generation alchimique": lambda: _m("fiole", 22, 36, 0.6) + _m("fiole", 46, 36, 0.5) + curved_arrow("M24 12 C30 6 38 6 44 12", (44, 12), 40, 2.4, 6),
    "gnome des forets": lambda: P("M32 2 L46 30 H18 Z") + Cc(32, 38, 12) + black(Cc(27, 36, 2) + Cc(37, 36, 2)) + P("M28 46 C30 54 34 54 36 46 Z") + _m("feuille", 54, 50, 0.2),
    "gnome des roches": lambda: P("M32 2 L46 30 H18 Z") + Cc(32, 38, 12) + black(Cc(27, 36, 2) + Cc(37, 36, 2)) + place(M["outil"](), 52, 52, 0.28),
    "guerrier planaire": lambda: figure(26, 34, 0.9) + _sword(42, 30, 30, 0.55) + '<ellipse cx="52" cy="14" rx="6" ry="10" fill="none" stroke="#FFFFFF" stroke-width="2.4"/>',
    "halo de lumiere": lambda: figure(32, 38, 0.8) + '<ellipse cx="32" cy="10" rx="12" ry="4" fill="none" stroke="#FFFFFF" stroke-width="3"/>' + _rays(32, 30, 26, 30, 10, 2),
    "halo de spores": lambda: figure(32, 34, 0.7) + "".join(Cc(32 + 22 * math.cos(a), 32 + 22 * math.sin(a), 2.6 + (k % 2)) for k, a in enumerate([j * math.pi / 6 for j in range(12)])),
    "illumination protectrice": lambda: place(M["ampoule"](), 32, 24, 0.6) + figure(18, 50, 0.36) + figure(46, 50, 0.36) + _rays(32, 22, 18, 22, 6, 2, 200),
    "illumination protectrice amelioree": lambda: place(M["ampoule"](), 32, 26, 0.6) + _rays(32, 26, 18, 26, 12, 2.4),
    "inexorable martyr": lambda: _kneel(28, 40, 0.85) + _shield(50, 28, 0.36) + place(M["coeur"](), 14, 12, 0.2),
    "inflexible": lambda: figure(32, 30, 1.0) + R(6, 56, 52, 5, 2) + S("M4 20 H14", 3) + S("M2 30 H12", 3) + S("M50 20 H60", 3),
    "inspiration au combat": lambda: _m("note", 22, 30, 0.55) + _sword(46, 32, 30, 0.6),
    "inspiration contagieuse": lambda: _m("note", 32, 22, 0.5) + figure(12, 50, 0.4) + figure(32, 52, 0.4) + figure(52, 50, 0.4),
    "inspiration martiale": lambda: _m("note", 22, 24, 0.45) + fist(46, 40, 0.55),
    "intervention divine": lambda: _hand(32, 16, 0.55, 180) + _rays(32, 30, 6, 14, 8, 2.4) + figure(32, 52, 0.36),
    "intrepide": lambda: figure(32, 34, 0.9) + black(place(M["coeur"](), 32, 26, 0.16)) + S("M6 20 L14 24 M58 20 L50 24", 2.4),
    "jeton etrange": lambda: Cc(32, 32, 20) + black(Cc(32, 32, 15)) + place(M["oeil"](), 32, 32, 0.36) + star4(54, 8, 4),
    "lames psychiques": lambda: dagger(22, 34, 45, 0.9) + dagger(42, 34, -45, 0.9).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2"') + star4(32, 8, 4),
    "langage de la foret & totem spirituel": lambda: _m("feuille", 22, 40, 0.6) + _bubble(44, 18, 0.5) + black(Cc(38, 16, 1.8) + Cc(44, 16, 1.8) + Cc(50, 16, 1.8)),
    "legende vivante": lambda: figure(32, 36, 0.9) + "".join(star4(32 + 22 * math.cos(a), 12 + 6 * math.sin(a), 3.4) for a in [math.pi + k * math.pi / 4 for k in range(5)]),
    "lien avec l'arme : rappel": lambda: _sword(42, 24, 45, 0.8) + _hand(18, 46, 0.5, 30) + curved_arrow("M44 40 C40 48 34 50 28 48", (28, 48), 170, 2.4, 6),
    "lien elementaire": lambda: _flame(14, 32, 0.32) + _drop(50, 32, 0.3) + L([(22, 32), (40, 32)], 2.6) + Cc(31, 32, 3),
    "lien enhardissant": lambda: figure(16, 36, 0.7) + figure(48, 36, 0.7) + L([(24, 30), (40, 30)], 2.4) + place(M["coeur"](), 32, 14, 0.2),
    "lien mental": lambda: _head(16, 36, 0.5) + '<g transform="translate(64 0) scale(-1 1)">' + _head(16, 36, 0.5) + "</g>" + L([(24, 22), (40, 22)], 2.4) + Cc(32, 22, 3),
    "lien parfait": lambda: figure(16, 36, 0.7) + _wolf(46, 38, 0.5) + L([(22, 22), (40, 26)], 2.4) + star4(32, 10, 5),
    "lien protecteur": lambda: figure(16, 36, 0.7) + figure(48, 36, 0.7) + _shield(32, 14, 0.26) + L([(22, 28), (42, 28)], 2),
    "lumiere guerisseuse": lambda: _rays(32, 16, 6, 14, 8, 2.6) + Cc(32, 16, 4) + place(M["soin"](), 32, 46, 0.4),
    "machoires affamees": lambda: P("M4 22 C14 8 50 8 60 22 L48 24 L44 30 L40 24 L36 30 L32 24 L28 30 L24 24 L20 30 L16 24 Z") + P("M4 42 C14 56 50 56 60 42 L48 40 L44 34 L40 40 L36 34 L32 40 L28 34 L24 40 L20 34 L16 40 Z"),
    "magie de guerre": lambda: _sword(24, 38, 45, 0.9) + star4(48, 16, 10) + star4(56, 36, 4),
    "magie mecanique & retablir l'equilibre": lambda: "".join(G(R(-2.4, -14, 4.8, 6, 1), 24, 32, a) for a in range(0, 360, 45)) + Cc(24, 32, 8) + black(Cc(24, 32, 3.4)) + place(__import__("core.art_kit", fromlist=["x"]).scales(), 48, 30, 0.42),
    "magie renforcante": lambda: star4(30, 34, 16) + G(R(-3, -8, 6, 12, 2) + P("M-8 -6 H8 L0 -16 Z"), 52, 24, 0, 1.0),
    "magie tempetueuse": lambda: star4(24, 32, 14) + S("M38 18 H54 C60 18 62 10 56 8", 3) + S("M40 30 H60", 3) + S("M38 42 H52 C58 42 60 50 54 52", 3),
    "main de mage arcanique": lambda: _dashed(G(R(-14, -4, 26, 26, 8) + R(-14, -22, 6, 22, 3) + R(-7, -26, 6, 26, 3) + R(0, -25, 6, 25, 3) + R(7, -20, 6, 20, 3), 32, 34, 0, 1.0), "3 2", 2.4) + star4(54, 10, 5) + star4(10, 12, 4),
    "main de souffrance": lambda: _hand(26, 38, 0.8, 0) + S("M44 16 L50 22 L46 26 L54 32", 2.6) + burst(54, 34, 5, 6),
    "main du mal": lambda: _hand(28, 38, 0.85, 0) + _m("lune", 52, 12, 0.24) + black(Cc(28, 40, 3)),
    "mains guerisseuses": lambda: _hand(20, 40, 0.6, 20) + _hand(44, 40, 0.6, -20) + place(M["soin"](), 32, 14, 0.3),
    "mains lestes": lambda: _hand(30, 36, 0.85, 20) + S("M2 24 H12", 2.6) + S("M4 34 H14", 2.6) + S("M2 44 H12", 2.6) + Cc(52, 14, 4),
    "maitre tacticien": lambda: R(6, 34, 52, 26, 2) + black("".join(R(x, 38, 5, 5, 0) for x in (10, 22, 34, 46)) + "".join(R(x, 50, 5, 5, 0) for x in (16, 28, 40))) + _m("couronne", 32, 14, 0.36),
    "maitre telekinetique": lambda: _hand(18, 46, 0.55, 0) + P("M30 10 L44 6 L50 18 L40 26 L28 20 Z") + P("M48 30 L58 28 L62 38 L54 44 L46 40 Z") + S("M24 32 C28 26 30 24 32 24", 2),
    "maitrises sup. & fureur de l'ouragan": lambda: figure(22, 34, 0.8) + place(tornado(), 48, 30, 0.55) + _sword(30, 12, 45, 0.3),
    "malediction de la lame maudite": lambda: _sword(28, 36, 45, 1.0) + _m("crane", 48, 16, 0.36) + black(Cc(22, 42, 2)),
    "manifestation d'un echo": lambda: figure(22, 32, 1.0) + _dashed(figure(44, 32, 0.9), "2 2", 1.8) + S("M54 20 C58 24 58 30 54 34", 2.2),
    "manoeuvre d'interposition": lambda: figure(20, 34, 0.75) + _shield(42, 34, 0.6) + _arrow(62, 10, 52, 20, 2.4),
    "manoeuvre protectrice": lambda: _shield(26, 34, 0.75) + figure(48, 36, 0.6) + place(M["coeur"](), 48, 8, 0.18),
    "manteau d'inspiration": lambda: _cape(30, 36, 0.85) + _m("note", 52, 12, 0.24),
    "manteau de majeste": lambda: _cape(32, 38, 0.85) + _m("couronne", 32, 8, 0.28),
    "marche dans l'ombre": lambda: figure(32, 30, 0.85) + P("M6 52 C16 46 48 46 58 52 C48 58 16 58 6 52 Z") + _m("lune", 54, 8, 0.2),
    "maree du chaos": lambda: _m("vague", 28, 36, 0.8) + _m("spirale", 50, 14, 0.28),
    "marque inebranlable": lambda: place(M["cible"](), 30, 34, 0.75) + _shield(52, 12, 0.26),
}


def _rune(x, y, s, inner):
    stone = G(P("M0 -26 L22 -14 V14 L0 26 L-22 14 V-14 Z") + P("M0 -20 L16 -11 V11 L0 20 L-16 11 V-11 Z", K), x, y, 0, s)
    return stone + G(inner, x, y, 0, s * 1.35)


C = {
    "martyr de l'ombre": lambda: _kneel(30, 40, 0.85) + _m("lune", 50, 12, 0.26) + P("M8 58 C20 54 44 54 56 58 Z"),
    "memoire kenku": lambda: place(bird(), 30, 34, 0.9) + _bubble(50, 12, 0.24) + black(Cc(46, 11, 1.4) + Cc(52, 11, 1.4)),
    "metamorphose": lambda: _wolf(16, 24, 0.42) + curved_arrow("M30 18 C40 10 48 14 50 22", (50, 22), 70, 2.4, 6) + figure(48, 44, 0.55),
    "modelage du corps": lambda: figure(32, 32, 1.0) + _hand(10, 20, 0.32, 60) + _hand(54, 20, 0.32, -60),
    "moi illusoire": lambda: _dashed(figure(32, 32, 1.1), "4 2", 2.4) + star4(52, 52, 5) + _sword(50, 12, 135, 0.3),
    "morsure vampirique": lambda: P("M8 20 C18 8 46 8 56 20 L48 22 L44 34 L40 22 L24 22 L20 34 L16 22 Z") + _drop(44, 48, 0.22) + _drop(20, 48, 0.22),
    "mots cinglants": lambda: _bubble(30, 26, 0.85) + black(L([(16, 26), (44, 26)], 3)) + dagger(52, 48, 45, 0.5),
    "mouvement telekinetique": lambda: _hand(18, 44, 0.55, 0) + figure(46, 28, 0.6) + S("M26 28 C32 20 36 18 40 18", 2.2) + S("M28 36 C34 32 38 32 40 32", 2.2),
    "murmures psychiques": lambda: _head(22, 38, 0.6) + S("M36 20 C40 24 40 30 36 34", 2.2) + S("M42 16 C48 22 48 32 42 38", 2) + _bubble(52, 10, 0.18),
    "nemesis des lanceurs": lambda: _sword(30, 36, 45, 1.0) + star4(48, 14, 8) + L([(40, 6), (56, 22)], 3),
    "nimbe sacre": lambda: figure(32, 40, 0.7) + _m("soleil", 32, 12, 0.32),
    "onde de choc acoustique": lambda: Cc(14, 32, 6) + "".join('<path d="M{} {} A{} {} 0 0 1 {} {}" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(14, 32 - r, r, r, 14, 32 + r, w) for r, w in ((12, 4), (20, 3.4), (28, 2.8), (36, 2.2))),
    "opportuniste": lambda: _m("oeil", 32, 18, 0.5) + dagger(32, 44, 45, 0.85),
    "panache": lambda: figure(32, 36, 0.85) + P("M40 10 C48 2 58 2 60 6 C54 8 48 10 42 14 Z") + R(26, 14, 14, 4, 2) + _sword(50, 44, 20, 0.36),
    "paroles troublantes": lambda: _bubble(32, 28, 0.9) + black(place(M["spirale"](), 32, 26, 0.3)),
    "pas de l'ombre": lambda: P("M4 52 C14 46 30 46 40 52 C30 58 14 58 4 52 Z") + _dashed(figure(20, 32, 0.6), "2 2", 1.6) + figure(48, 32, 0.7) + _m("lune", 52, 8, 0.18),
    "pas de lumiere etoilee": lambda: figure(40, 30, 0.8, 15) + star4(12, 52, 5) + star4(22, 40, 4) + star4(14, 30, 3),
    "pas du vent (gratuit)": lambda: figure(36, 26, 0.75, 15) + S("M2 48 H34 C42 48 44 38 36 36", 3.4) + S("M8 58 H48", 3),
    "pas ethere": lambda: _dashed(figure(32, 30, 1.0), "3 3", 2.2) + S("M4 56 C14 52 22 60 32 56 C42 52 50 60 60 56", 2.4),
    "pas invisible": lambda: _dashed(footprint(20, 48, -10, 0.7), "2 2", 1.6) + _dashed(footprint(34, 34, 10, 0.6), "2 2", 1.6) + star4(50, 14, 6),
    "pied agile": lambda: boot(32, 32, 0.9) + L([(54, 4), (46, 16), (52, 18), (44, 30)], 3) + S("M2 40 H10", 2.6),
    "pirouettes coordonnees": lambda: G(figure(0, 0, 0.7), 20, 34, -15) + G(figure(0, 0, 0.7), 44, 34, 15) + S("M10 10 C20 2 44 2 54 10", 2.6),
    "plaintes d'outre-tombe": lambda: _m("crane", 26, 36, 0.6) + S("M44 22 C50 28 50 38 44 44", 2.6) + S("M52 16 C60 26 60 40 52 50", 2.2),
    "planer": lambda: figure(32, 30, 0.75) + _wing(14, 24, 0.42) + _wing(50, 24, 0.42, True) + S("M6 54 H58", 2.4),
    "plenitude du corps": lambda: figure(32, 34, 0.9) + _rays(32, 30, 22, 28, 8, 2) + place(M["soin"](), 52, 12, 0.22),
    "plenitude physique": lambda: place(M["coeur"](), 30, 32, 0.7) + boot(50, 48, 0.3),
    "poussee d'adrenaline": lambda: place(M["coeur"](), 26, 36, 0.6) + L([(50, 2), (42, 16), (48, 18), (40, 32)], 3) + G(R(-3, -6, 6, 10, 2) + P("M-8 -6 H8 L0 -16 Z"), 52, 46, 0, 0.8),
    "pouvoirs psioniques": lambda: _m("cerveau", 32, 34, 0.75) + _rays(32, 34, 24, 30, 10, 2.4),
    "presage": lambda: Cc(32, 30, 22) + black(Cc(32, 30, 17)) + _m("oeil", 32, 30, 0.42) + R(20, 52, 24, 6, 2),
    "presage cosmique": lambda: _m("oeil", 32, 34, 0.7) + star4(10, 10, 5) + star4(32, 6, 4) + star4(54, 10, 5),
    "presence feerique": lambda: figure(32, 38, 0.8) + _wing(16, 30, 0.4) + _wing(48, 30, 0.4, True) + star4(32, 8, 5),
    "presence intimidante": lambda: figure(32, 34, 1.0) + black(P("M26 14 L32 16 L27 18 Z") + P("M38 14 L32 16 L37 18 Z")) + S("M4 20 L12 26 M60 20 L52 26", 2.4),
    "presence zelee": lambda: figure(32, 36, 0.9) + _flame(32, 10, 0.24) + S("M6 30 C10 24 14 24 18 28", 2.2) + S("M46 28 C50 24 54 24 58 30", 2.2),
    "pretre de guerre": lambda: _sword(32, 34, 0, 1.0) + _rays(32, 12, 6, 12, 6, 2.2, 200),
    "proie du chasseur": lambda: place(M["cible"](), 26, 26, 0.65) + __import__("core.art_retouches", fromlist=["x"]).wolf_paw(48, 48, 0.4),
    "proie du tueur": lambda: place(M["cible"](), 26, 26, 0.65) + _m("crane", 48, 48, 0.34),
    "protection projetee": lambda: figure(16, 38, 0.65) + _shield(44, 32, 0.6) + _arrow(22, 20, 32, 24, 2.4),
    "puissance des geants": lambda: fist(30, 36, 1.0) + burst(52, 14, 8, 8),
    "quinte flush royale": lambda: "".join(G(R(-8, -12, 16, 24, 2) + black(star4(0, 0, 4)), x, 32, a) for x, a in ((14, -20), (24, -10), (34, 0), (44, 10), (54, 20))),
    "rechargement eclair": lambda: place(M["arbalete"](), 30, 36, 0.85) + L([(54, 2), (46, 16), (52, 18), (44, 30)], 3),
    "recuperation psionique": lambda: _m("cerveau", 28, 36, 0.7) + curved_arrow("M44 54 C58 46 58 22 46 14", (46, 14), 220, 3, 8),
    "redirection": lambda: _arrow(4, 20, 30, 32, 3) + _shield(36, 34, 0.5) + curved_arrow("M40 44 C46 54 52 56 60 54", (60, 54), -10, 3, 7),
    "regard hypnotique": lambda: _m("oeil", 32, 32, 0.8) + "".join(S("M{a} 32 C{a} {b} {c} {b} {c} 32".format(a=32 - r, b=32 - r, c=32 + r), 2) for r in (24, 29)),
    "rempart de force": lambda: R(8, 16, 48, 40, 3) + black(R(13, 21, 38, 30, 2)) + figure(32, 38, 0.55) + burst(32, 10, 6, 6),
    "represailles": lambda: figure(18, 34, 0.8) + curved_arrow("M26 22 C36 12 46 14 52 22", (52, 22), 60, 3, 8) + _sword(50, 44, 45, 0.45),
    "representation animee": lambda: _m("note", 22, 30, 0.5) + figure(46, 34, 0.6, 15) + star4(54, 8, 4),
    "representation de la creation": lambda: _m("note", 20, 22, 0.45) + P("M34 40 L50 36 L56 48 L44 56 L32 50 Z") + star4(44, 20, 6),
    "reprimande vigilante": lambda: _m("oeil", 24, 24, 0.55) + curved_arrow("M36 30 C46 30 52 38 54 48", (54, 48), 80, 3, 8) + burst(54, 54, 6, 6),
    "reseau maille": lambda: _m("toile", 32, 32, 1.0) + black(Cc(32, 32, 7)) + Cc(32, 32, 4),
    "retablir l'equilibre": lambda: place(__import__("core.art_kit", fromlist=["x"]).scales(), 32, 34, 1.0),
    "revelation celeste": lambda: figure(32, 38, 0.75) + _wing(14, 30, 0.42) + _wing(50, 30, 0.42, True) + _rays(32, 12, 4, 10, 10, 2.4),
    "revelation dans la chair": lambda: figure(32, 30, 0.95) + S("M22 44 C14 50 14 58 8 60", 4) + S("M42 44 C50 50 50 58 56 60", 4) + black(Cc(32, 26, 3)),
    "riposte capricieuse": lambda: _sword(24, 38, 45, 0.9) + curved_arrow("M44 54 C58 46 58 22 46 14", (46, 14), 220, 3, 8) + star4(10, 10, 4) + star4(52, 34, 3),
    "ruee cornue": lambda: _head(36, 38, 0.75) + P("M38 16 C34 8 28 4 22 4 C28 8 30 14 32 20 Z") + S("M2 34 H14", 3) + S("M4 44 H16", 3),
    "rugissement intimidant": lambda: _wolf(26, 36, 0.75) + S("M48 22 C54 28 54 38 48 44", 3) + S("M56 16 C64 26 64 40 56 50", 2.6),
    "rune de la colline": lambda: _rune(32, 32, 1.05, P("M-12 8 L-4 -6 L2 2 L8 -8 L14 8 Z")),
    "rune de la pierre": lambda: _rune(32, 32, 1.05, P("M-10 6 L-6 -8 L6 -10 L10 4 L2 10 Z")),
    "rune du feu": lambda: _rune(32, 32, 1.05, P("M0 12 C-8 12 -10 4 -6 -2 C-4 2 -2 2 -2 0 C-4 -6 0 -10 2 -14 C2 -8 6 -6 7 -2 C9 4 7 12 0 12 Z")),
    "rune du givre": lambda: _rune(32, 32, 1.05, L([(0, -12), (0, 12)], 2.6) + L([(-10, -6), (10, 6)], 2.6) + L([(-10, 6), (10, -6)], 2.6)),
    "rune du nuage": lambda: _rune(32, 32, 1.05, P("M-12 6 C-16 6 -16 0 -12 -1 C-12 -6 -6 -8 -2 -5 C0 -10 8 -10 10 -4 C14 -4 16 2 12 6 Z")),
    "rupture spirituelle": lambda: _dashed(figure(32, 32, 1.0), "3 2", 2.2) + L([(14, 6), (24, 24), (18, 28), (30, 44)], 3) + burst(30, 44, 6, 6),
    "ruse magique": lambda: _m("masque", 30, 34, 0.75) + star4(50, 12, 7) + star4(12, 12, 4),
    "sanctuaire de dame nature": lambda: place(tree(), 32, 36, 0.7) + _dashed(P("M4 60 C4 30 16 10 32 10 C48 10 60 30 60 60"), "4 3", 2.4),
    "sanguisuga supreme": lambda: _drop(24, 34, 0.75) + place(M["coeur"](), 48, 18, 0.3) + curved_arrow("M36 48 C44 52 50 46 52 38", (52, 30), 270, 2.4, 6),
    "saut de lapin": lambda: G(figure(0, 0, 0.8), 34, 22, 15) + curved_arrow("M4 58 C10 40 18 36 26 36", (26, 36), 0, 2.6, 7) + S("M36 58 H60", 2.4),
    "saut des nuees (geants des nuages)": lambda: cloud(46, 0.8) + figure(36, 18, 0.6) + _dashed(figure(12, 26, 0.5), "2 2", 1.6),
    "savoir-faire renforce": lambda: place(M["outil"](), 28, 36, 0.75) + G(R(-3, -6, 6, 10, 2) + P("M-8 -6 H8 L0 -16 Z"), 52, 20, 0, 1.0),
    "seconde lame psychique": lambda: dagger(24, 38, 45, 0.9) + _dashed(dagger(42, 26, 45, 0.9), "2 2", 1.8),
    "sentinelle au seuil de la mort": lambda: doorway() + place(M["crane"](), 32, 38, 0.3),
    "sorcellerie innee": lambda: _m("spirale", 32, 32, 0.8) + star4(52, 12, 6),
    "sorcellerie innee (2 points de sorcellerie)": lambda: _m("spirale", 24, 34, 0.6) + star4(48, 18, 6) + star4(52, 44, 6),
    "sort mineur supp. & illumination protectrice": lambda: place(M["ampoule"](), 24, 32, 0.6) + star4(48, 18, 6) + star4(52, 46, 4),
    "souffle": lambda: place(dragon_head(), 22, 30, 0.55) + P("M36 32 L62 18 V48 Z") + black(P("M40 33 L58 24 V42 Z")),
    "spores pacifiantes ou toxiques": lambda: P("M8 30 C8 18 20 10 32 10 C44 10 56 18 56 30 Z") + R(26, 30, 12, 20, 4) + "".join(Cc(x, y, 2.2) for x, y in ((10, 44), (18, 54), (48, 46), (54, 56), (40, 58))),
    "surcharge magique": lambda: star4(32, 32, 18) + burst(32, 32, 30, 12).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2"'),
    "symbiote & halo de spores": lambda: figure(32, 34, 0.8) + S("M14 58 C10 46 16 38 20 32", 3) + S("M50 58 C54 46 48 38 44 32", 3) + "".join(Cc(x, y, 2) for x, y in ((10, 14), (54, 14), (32, 4))),
    "teleportation psychique": lambda: _head(18, 38, 0.55) + '<ellipse cx="48" cy="30" rx="10" ry="18" fill="#FFFFFF"/>' + black('<ellipse cx="48" cy="30" rx="6" ry="12" fill="#FFFFFF"/>') + S("M26 24 C32 18 36 18 40 22", 2),
    "tempete dechainee (desert)": lambda: tornado() + _m("soleil", 52, 10, 0.2),
    "tempete dechainee (mer)": lambda: tornado() + S("M2 60 C10 54 18 62 26 58", 2.4),
    "tentacule des profondeurs": lambda: S("M24 62 C18 46 30 38 26 22 C24 14 32 6 40 8 C46 10 46 18 40 20", 6) + black("".join(Cc(x, y, 1.6) for x, y in ((24, 52), (26, 40), (28, 28)))) + S("M2 56 C10 52 16 60 24 56", 2),
    "tir du kensei": lambda: place(M["arc"](), 24, 32, 0.7) + fist(50, 46, 0.35) + star4(54, 12, 4),
    "torsion seduisante": lambda: place(M["coeur"](), 26, 34, 0.6) + _m("spirale", 48, 20, 0.3),
    "toucher purifiant": lambda: _hand(28, 40, 0.8, 0) + _drop(48, 16, 0.24) + star4(52, 36, 4),
    "trait de soleil radieux": lambda: _arrow(4, 58, 40, 22, 4) + _m("soleil", 48, 14, 0.36),
    "transposition bienveillante": lambda: figure(14, 34, 0.6) + figure(50, 34, 0.6) + curved_arrow("M20 14 C28 4 38 4 46 14", (46, 14), 50, 2.4, 6) + curved_arrow("M46 54 C38 62 28 62 20 54", (20, 54), 230, 2.4, 6) + place(M["coeur"](), 32, 34, 0.16),
    "tueur de colosses": lambda: figure(48, 26, 1.0) + figure(16, 46, 0.45) + _sword(26, 34, 45, 0.5),
    "union avec le verbe": lambda: _m("livre", 26, 40, 0.6) + _bubble(46, 16, 0.4),
    "vengeur implacable": lambda: _sword(24, 40, 45, 0.9) + place(M["cible"](), 48, 18, 0.38) + _arrow(32, 30, 40, 24, 2),
    "voile de murmure": lambda: _cape(30, 36, 0.85) + _bubble(52, 14, 0.22),
    "voile necrotique": lambda: _cape(32, 38, 0.85) + _m("crane", 32, 10, 0.24),
    "voile psychique": lambda: _head(30, 36, 0.8) + _dashed(P("M10 20 C10 6 50 6 50 20 V56 H10 Z"), "3 3", 2),
    "voleur de sort": lambda: _hand(22, 42, 0.7, 30) + star4(46, 16, 9) + curved_arrow("M40 30 C34 32 30 32 28 30", (26, 30), 180, 2.2, 5),
    "voyage au gre de l'arbre": lambda: place(tree(), 24, 32, 0.7) + _dashed(figure(50, 40, 0.5), "2 2", 1.6) + curved_arrow("M36 54 C42 58 48 58 52 52", (52, 52), -60, 2.2, 6),
    "yeux de la tombe": lambda: _m("oeil", 32, 24, 0.75) + black(Cc(32, 24, 4)) + place(M["crane"](), 32, 50, 0.3),
}
