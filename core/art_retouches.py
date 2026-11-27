"""
Retouches (v53) de dessins jugés peu lisibles : formes sauvages, bulles de texte, Décharge occulte, familier,
rage, lumières dansantes, main de mage, piqûre mentale. Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

from .art_armes import Cc, G, K, L, P, R, S, burst, over, star4


def wolf_profile(x=32, y=32, s=1.0):
    """Tête de loup de profil, museau à droite, oreilles dressées, gueule entrouverte."""
    head = P("M-24 22 C-26 10 -22 -2 -14 -10 L-16 -28 L-6 -16 L-2 -18 L2 -30 L8 -14 C16 -12 22 -8 28 -4 "
             "L30 0 C30 3 28 4 26 4 L18 4 L24 10 C20 12 14 12 10 10 C6 16 0 22 -6 26 Z")
    eye = P("M2 -6 L10 -5 L4 -1 Z", K)
    ear = P("M-12 -16 L-13 -24 L-8 -18 Z", K)
    fur = L([(-18, 8), (-10, 4)], 2, K) + L([(-16, 16), (-8, 12)], 2, K)
    nose = Cc(28, -1, 2.2, K)
    return G(head + eye + ear + fur + nose, x, y, 0, s)


def wolf_paw(x=32, y=32, s=1.0):
    """Empreinte de loup : coussinet triangulaire, quatre doigts ovales, griffes."""
    pad = P("M0 2 C7 2 16 10 16 18 C16 24 10 26 6 24 C3 23 1 22 0 22 C-1 22 -3 23 -6 24 C-10 26 -16 24 -16 18 "
            "C-16 10 -7 2 0 2 Z")
    toes = "".join('<ellipse cx="{}" cy="{}" rx="5" ry="7" transform="rotate({} {} {})" fill="#FFFFFF"/>'.format(
        tx, ty, a, tx, ty) for tx, ty, a in ((-15, -6, -25), (-6, -16, -8), (6, -16, 8), (15, -6, 25)))
    claws = "".join(P("M{} {} L{} {} L{} {} Z".format(cx - 2, cy, cx, cy - 6, cx + 2, cy)) .replace(
        'd="', 'transform="rotate({} {} {})" d="'.format(a, cx, cy)) for cx, cy, a in
        ((-18, -13, -25), (-7, -23, -8), (7, -23, 8), (18, -13, 25)))
    return G(pad + toes + claws, x, y, 0, s)


def tall_bubble(x=32, y=30, s=1.0):
    """Bulle de dialogue haute, pour lire « … » ou « ! »."""
    return G(P("M-22 -24 H22 C27 -24 30 -21 30 -16 V10 C30 15 27 18 22 18 H-2 L-16 30 V18 H-22 C-27 18 -30 15 -30 10 "
               "V-16 C-30 -21 -27 -24 -22 -24 Z"), x, y, 0, s)


def provocation():
    return tall_bubble(32, 30, 1.0) + R(28, 10, 8, 20, 4, K) + Cc(32, 37, 4.4, K)


def message():
    waves = S("M56 26 C61 31 61 41 56 46", 3) + S("M61 20 C68 30 68 42 61 52", 2.6)
    return (G(tall_bubble(0, 0, 1.0), 28, 30, 0, 0.92) + Cc(16, 27, 4.4, K) + Cc(28, 27, 4.4, K) + Cc(40, 27, 4.4, K)
            + waves)


def eldritch_blast():
    """Rayon occulte : orbe cerclé, trait d'énergie en zigzag large qui s'évase, éclat à l'impact."""
    orb = Cc(13, 51, 11) + '<circle cx="13" cy="51" r="6.5" fill="none" stroke="#000000" stroke-width="2.8"/>' + Cc(13, 51, 2.8)
    pts = [(21, 44), (33, 37), (29, 31), (43, 25), (39, 20), (53, 11)]
    beam = L(pts, 8.5)
    core = L(pts, 2.4, K)
    return orb + beam + core + burst(56, 10, 9, 8) + star4(12, 20, 4) + star4(46, 52, 3.4)


def owl():
    """Chouette assise sur une branche : aigrettes, grands yeux cerclés, ailes repliées."""
    body = P("M-17 -18 L-12 -26 L-6 -19 C-2 -20 2 -20 6 -19 L12 -26 L17 -18 C20 -12 20 -4 19 2 C18 14 10 22 0 22 "
             "C-10 22 -18 14 -19 2 C-20 -4 -20 -12 -17 -18 Z")
    face = P("M0 -14 C4 -18 14 -18 15 -8 C16 2 6 4 0 -2 C-6 4 -16 2 -15 -8 C-14 -18 -4 -18 0 -14 Z", K)
    eyes = Cc(-7, -8, 5.6) + Cc(7, -8, 5.6) + Cc(-7, -8, 2.6, K) + Cc(7, -8, 2.6, K)
    beak = P("M-2.5 -2 H2.5 L0 4 Z")
    wings = S("M-15 2 C-12 10 -8 16 -2 18", 2, K) + S("M15 2 C12 10 8 16 2 18", 2, K)
    belly = S("M-5 8 Q0 11 5 8", 1.6, K) + S("M-4 13 Q0 16 4 13", 1.6, K)
    talons = R(-8, 21, 4, 3, 1) + R(4, 21, 4, 3, 1)
    branch = R(-26, 24, 52, 4.4, 2.2)
    return G(body + face + eyes + beak + wings + belly + talons + branch, 30, 30, 0, 1.0) + star4(54, 10, 5)


def rage():
    """Visage furieux : sourcils en V, yeux plissés, bouche hurlante, éclats de colère."""
    head = P("M0 -22 C13 -22 20 -13 20 -1 C20 13 11 22 0 22 C-11 22 -20 13 -20 -1 C-20 -13 -13 -22 0 -22 Z")
    brows = P("M-17 -12 L-3 -5 L-4 -1 L-17 -7 Z", K) + P("M17 -12 L3 -5 L4 -1 L17 -7 Z", K)
    eyes = P("M-14 -1 L-5 1 L-13 4 Z", K) + P("M14 -1 L5 1 L13 4 Z", K)
    mouth = P("M-10 8 H10 L8 18 C4 20 -4 20 -8 18 Z", K) + P("M-8 8 H8 L7 11 H-7 Z") + P("M-6 18 L-4 15 L-2 18 Z")
    fury = "".join(G(P("M-1.6 -31 L1.6 -31 L0.9 -25 L-0.9 -25 Z"), 0, 0, a) for a in (-60, -35, 35, 60))
    return G(fury + head + brows + eyes + mouth, 32, 34, 0, 1.0)


def glow(x, y, r):
    """Petite lumière flottante : disque et rayons courts."""
    rays = "".join(G(P("M-1.2 {a} L1.2 {a} L0.7 {b} L-0.7 {b} Z".format(a=-r - 7, b=-r - 2.5)), x, y, k)
                   for k in range(0, 360, 45))
    return Cc(x, y, r) + rays


def dancing_lights():
    trail = S("M10 52 C18 44 22 50 28 42", 2.2) + S("M34 36 C40 30 44 34 48 26", 2.2)
    return trail + glow(12, 48, 4.5) + glow(32, 34, 6) + glow(50, 16, 7.5) + glow(52, 46, 3.6)


def mage_hand():
    """Main spectrale : la main flotte, son poignet se défait en volute, éclats autour."""
    hand = (R(-14, -4, 26, 22, 8) + R(-14, -22, 6, 22, 3) + R(-7, -26, 6, 26, 3) + R(0, -25, 6, 25, 3)
            + R(7, -20, 6, 20, 3) + P("M12 4 L22 -8 C25 -10 28 -7 26 -4 L14 12 Z"))
    tail = P("M-12 14 H10 C10 22 4 26 -2 28 C4 30 6 34 2 38 C0 34 -6 34 -8 30 C-12 26 -14 20 -12 14 Z")
    return G(hand + tail, 30, 30, 0, 1.0) + star4(54, 12, 6) + star4(10, 16, 4) + star4(52, 44, 3.4)


def mind_sliver():
    """Cerveau net (deux lobes, circonvolutions évidées) frappé par un éclair."""
    brain = P("M0 -20 C-6 -24 -16 -22 -19 -14 C-26 -12 -28 -2 -23 4 C-26 10 -20 18 -12 17 C-8 22 -2 21 0 18 "
              "C2 21 8 22 12 17 C20 18 26 10 23 4 C28 -2 26 -12 19 -14 C16 -22 6 -24 0 -20 Z")
    folds = (L([(0, -18), (0, 16)], 2.2, K) + S("M-6 -14 C-12 -12 -10 -6 -16 -4", 2, K) + S("M-4 2 C-10 0 -14 6 -18 6", 2, K)
             + S("M6 -14 C12 -12 10 -6 16 -4", 2, K) + S("M4 2 C10 0 14 6 18 6", 2, K) + S("M-8 10 C-6 14 -10 16 -12 14", 2, K)
             + S("M8 10 C6 14 10 16 12 14", 2, K))
    bolt = P("M6 -30 L-4 -14 L2 -14 L-4 -2 L10 -18 L4 -18 L10 -30 Z")
    return over(G(brain + folds, 30, 38, 0, 1.0), G(bolt, 48, 26, 0, 0.9))


def wolf_howl():
    """Loup assis qui hurle à la lune : gueule ouverte, tête rejetée en arrière, collerette de fourrure, pattes
    avant avec coussinets, queue touffue enroulée au sol."""
    moon = Cc(50, 14, 11) + Cc(56, 10, 10, K) + star4(36, 6, 2.4) + star4(60, 30, 2)
    # silhouette : museau ouvert vers le haut-gauche, oreille, crinière, dos, cuisse, queue au sol, pattes avant
    body = P(
        "M3 1 "                    # bout du museau (mâchoire supérieure)
        "C8 4 13 7 17 10 "         # dessus du museau
        "L19 3 L22 4 L23 11 "      # oreille pointue
        "C27 12 30 15 31 19 "      # arrière du crâne
        "C36 24 42 30 46 38 "      # nuque et dos
        "C48 42 49 46 49 49 "      # jusqu'à la cuisse
        "C50 54 50 57 48 59 "      # cuisse arrondie
        "C52 59 56 58 58 55 C60 52 62 53 62 56 C62 61 56 63 50 63 "   # queue touffue enroulée au sol
        "H31 C30 61 30 58 32 57 "  # patte arrière (pied)
        "L30 47 "                  # intérieur
        "L28 60 C28 62 26 63 24 63 H20 C19 62 20 60 22 60 "           # patte avant 1 + coussinet
        "L21 42 "
        "L19 58 C19 61 17 62 15 62 H12 C11 61 12 59 14 59 "           # patte avant 2
        "L15 38 "
        "L12 35 L16 32 L11 29 L15 26 L11 23 L15 21 "   # collerette de fourrure sur le poitrail
        "C12 19 11 17 12 15 "      # gorge
        "L2 10 "                   # mâchoire inférieure
        "L9 8 Z")                  # commissure : la gueule s'ouvre entre les deux mâchoires
    eye = P("M17 12 L22 13 L18 15 Z", K)
    lines = S("M31 47 C29 40 31 34 35 31", 1.8, K) + S("M30 22 C32 26 33 30 32 34", 1.4, K)
    return moon + body + eye + lines


def _sym(pts, col="#FFFFFF"):
    """Polygone symétrique : points de la moitié gauche (de haut en bas), miroir en x = 32."""
    allp = pts + [(64 - x, y) for x, y in reversed(pts)]
    return '<path d="M' + " L".join("{:g} {:g}".format(x, y) for x, y in allp) + ' Z" fill="{}"/>'.format(col)


def wolf_emblem():
    """Tête de loup de face, façon emblème : oreilles dressées, joues hérissées, regard en amande, chanfrein qui
    descend jusqu'à la truffe, marque en losange sur le front."""
    head = _sym([(32, 14), (25, 15), (14, 1), (11, 20), (5, 22), (8, 29), (1, 34), (9, 38), (4, 45), (13, 47), (16, 54),
                 (25, 57), (32, 62)])
    ears = P("M16.5 9 L20.5 16.5 L15 17.8 Z", K) + P("M47.5 9 L43.5 16.5 L49 17.8 Z", K)
    eyes = P("M14 28 L27 32 L24 35 L17 34 Z", K) + P("M50 28 L37 32 L40 35 L47 34 Z", K)
    glint = Cc(22, 32.5, 1.3) + Cc(42, 32.5, 1.3)
    brow = P("M32 19 L35 25 L32 29 L29 25 Z", K)
    muzzle = S("M27 36 C28 42 29 47 29.5 51", 2.4, K) + S("M37 36 C36 42 35 47 34.5 51", 2.4, K)
    nose = P("M26.5 50 H37.5 C37.5 53 35 56 32 57 C29 56 26.5 53 26.5 50 Z", K)
    mouth = S("M32 57 V60", 1.8, K)
    cheeks = S("M10 38 L18 41", 1.8, K) + S("M54 38 L46 41", 1.8, K)
    return head + ears + eyes + glint + brow + muzzle + nose + mouth + cheeks
