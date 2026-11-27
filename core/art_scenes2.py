"""
Scènes dessinées (v53) des sorts de niveau 2 : un dessin d'un seul tenant par sort (pas d'élément posé en coin),
même grammaire que les sorts dessinés à la main — silhouettes pleines, découpes noires franches, éclats discrets.
Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

import math

from .art_armes import Cc, G, K, L, P, R, S, blade_sword, burst, curved_arrow, over, star4
from .art_kit import black, figure, place
from .art_motifs import MOTIFS as M


def _hand(x=32, y=34, s=1.0, a=0):
    return G(R(-14, -4, 26, 26, 8) + R(-14, -22, 6, 22, 3) + R(-7, -26, 6, 26, 3) + R(0, -25, 6, 25, 3)
             + R(7, -20, 6, 20, 3) + P("M12 6 L22 -6 C25 -8 28 -5 26 -2 L14 14 Z"), x, y, a, s)


def _sword(x=32, y=32, a=45, s=1.0):
    return G(blade_sword(30, 8.5, 20, 9, 3.6), x, y, a, s)


def _dashed(svg, dash="4 3", w=2.4):
    return svg.replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="{}" stroke-dasharray="{}"'.format(w, dash))


def _rays(x, y, r1, r2, n=8, w=3, start=0):
    return "".join(L([(x + r1 * math.cos(a), y + r1 * math.sin(a)), (x + r2 * math.cos(a), y + r2 * math.sin(a))], w)
                   for a in [math.radians(start + k * 360 / n) for k in range(n)])


def _head(x=32, y=32, s=1.0, flip=False):
    d = "M30 58 V48 C22 48 18 44 18 38 L12 34 L18 30 C16 18 22 8 34 8 C44 8 50 16 50 26 C50 34 46 40 42 42 V58 Z"
    g = P(d)
    if flip:
        g = '<g transform="translate(64 0) scale(-1 1)">' + g + "</g>"
    return place(g, x, y, s)


def _bubble(x=32, y=30, s=1.0):
    return G(P("M-22 -20 H22 C27 -20 30 -17 30 -12 V8 C30 13 27 16 22 16 H-2 L-14 26 V16 H-22 C-27 16 -30 13 -30 8 "
               "V-12 C-30 -17 -27 -20 -22 -20 Z"), x, y, 0, s)


def _flame(x, y, s=1.0):
    d = ("M0 22 C-14 22 -18 8 -12 -2 C-10 4 -6 6 -5 3 C-8 -8 -2 -18 4 -26 C4 -16 10 -12 12 -4 "
         "C14 -8 14 -12 13 -15 C20 -6 20 6 16 13 C13 19 7 22 0 22 Z")
    return G(P(d), x, y, 0, s)


def _drop(x, y, s=1.0):
    return G(P("M0 -24 C8 -12 16 -2 16 8 C16 18 9 24 0 24 C-9 24 -16 18 -16 8 C-16 -2 -8 -12 0 -24 Z"), x, y, 0, s)


def _snow(x, y, s=1.0):
    return place(M["flocon"](), x, y, s)


# ------------------------------------------------------------------------------------------------ scènes
def agrandissement():
    """Silhouette petite puis grande, flèches d'agrandissement entre les deux."""
    return (figure(14, 44, 0.5) + figure(42, 32, 1.05) + curved_arrow("M14 22 C16 10 24 6 30 8", (30, 8), 0, 2.8, 7))


def apaisement():
    """Visage serein aux yeux clos, vaguelettes paisibles autour."""
    face = P("M32 8 C45 8 52 18 52 30 C52 44 43 54 32 54 C21 54 12 44 12 30 C12 18 19 8 32 8 Z")
    eyes = S("M20 30 Q25 34 30 30", 2.8, K) + S("M34 30 Q39 34 44 30", 2.8, K)
    smile = S("M24 42 Q32 47 40 42", 2.8, K)
    waves = S("M2 58 C8 54 14 62 20 58 C26 54 32 62 38 58 C44 54 50 62 56 58", 2.6)
    return face + eyes + smile + waves + S("M4 18 C8 14 12 22 16 18", 2.2) + S("M48 14 C52 10 56 18 60 14", 2.2)


def appel_destrier():
    """Cheval cabré avec selle, éclats."""
    from .art_kit import horse
    return horse() + R(24, 18, 12, 5, 2, K) + star4(8, 8, 4) + star4(56, 54, 3.4)


def arme_magique():
    """Épée dont la lame porte des runes lumineuses."""
    blade = _sword(32, 32, 45, 1.25)
    runes = "".join(G(R(-1.2, -3, 2.4, 6, 0.6, K), 32 + d * 0.7071, 32 - d * 0.7071, 45) for d in (4, 10, 16))
    return blade + runes + star4(52, 12, 6) + star4(12, 52, 4)


def attraction_terrestre():
    """Silhouette tirée vers le sol par des mains de pierre."""
    ground = P("M2 52 L10 46 L22 50 L34 44 L46 50 L62 46 V62 H2 Z")
    hands = (_hand(20, 46, 0.42, 160) + _hand(44, 46, 0.42, -160))
    return figure(32, 22, 0.75) + ground + black(L([(10, 54), (22, 58), (34, 52)], 1.8)) + hands


def aura_nystul():
    """Objet (anneau) entouré d'une aura en pointillés qui le masque."""
    aura = '<circle cx="32" cy="32" r="26" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="5 4"/>'
    return aura + place(M["anneau"](), 32, 32, 0.6) + star4(56, 8, 4)


def bouche_magique():
    """Lèvres flottantes qui parlent, éclats."""
    lips = (P("M8 32 C16 20 26 22 32 26 C38 22 48 20 56 32 C48 44 16 44 8 32 Z")
            + P("M14 32 C22 30 42 30 50 32 C42 36 22 36 14 32 Z", K))
    return lips + S("M58 22 C62 28 62 36 58 42", 2.6) + star4(10, 12, 4) + star4(52, 12, 3.4)


def bourrasque():
    """Rafale puissante qui pousse une silhouette penchée."""
    gust = (S("M4 18 H34 C42 18 44 8 36 7", 4.4) + S("M2 32 H40", 4.4) + S("M6 46 H30 C38 46 40 56 32 57", 4.4))
    return gust + figure(52, 32, 0.8, 18)


def chatiment_revelation():
    """Épée qui frappe, éclat d'où sort un œil révélateur."""
    return over(_sword(24, 40, 45, 1.0), place(M["oeil"](), 44, 20, 0.5), 6) + _rays(44, 20, 14, 18, 8, 2.2)


def chatiment_revelateur():
    """Épée nimbée, contour d'une silhouette invisible révélé."""
    return over(_dashed(figure(44, 32, 1.0)), _sword(24, 36, 45, 1.0), 6) + star4(54, 10, 5)


def connaissance_empruntee():
    """Livre ouvert dont la connaissance monte vers une tête."""
    book = place(M["livre"](), 32, 48, 0.6)
    return book + _head(32, 18, 0.45) + S("M24 38 C24 32 30 34 30 28", 2.4) + S("M40 38 C40 32 34 34 34 28", 2.4)


def convocation_bete():
    """Loup qui surgit d'un cercle de convocation."""
    circle = '<ellipse cx="32" cy="52" rx="26" ry="8" fill="none" stroke="#FFFFFF" stroke-width="3.4"/>'
    return circle + place(M["bete"](), 32, 30, 0.78) + star4(8, 40, 3.6) + star4(56, 40, 3.6)


def corde_enchantee():
    """Corde dressée en l'air vers une ouverture lumineuse."""
    rope = S("M30 60 C26 48 36 42 30 30 C26 22 34 16 32 10", 5)
    opening = '<ellipse cx="32" cy="8" rx="14" ry="4.5" fill="#FFFFFF"/><ellipse cx="32" cy="8" rx="9" ry="2.4" fill="#000000"/>'
    knots = Cc(30, 46, 3.4) + Cc(31, 30, 3.4)
    return rope + knots + opening + star4(52, 30, 4) + star4(12, 24, 3.4)


def cordon_fleches():
    """Quatre flèches plantées en ligne, prêtes à partir."""
    out = ""
    for x in (12, 24, 36, 48):
        out += L([(x, 58), (x, 20)], 3) + P("M{} 12 L{} 22 L{} 22 Z".format(x, x + 5, x - 5))
        out += P("M{} 58 L{} 52 L{} 54 Z".format(x, x - 5, x - 5)) + P("M{} 58 L{} 52 L{} 54 Z".format(x, x + 5, x + 5))
    return out + R(4, 58, 56, 4, 2)


def couronne_dement():
    """Couronne aux pointes épineuses au-dessus d'un regard en spirale."""
    crown = P("M8 30 L6 8 L18 20 L24 4 L32 18 L40 4 L46 20 L58 8 L56 30 Z") + R(8, 30, 48, 7, 2)
    spiral = place(M["spirale"](), 32, 50, 0.3)
    return crown + spiral + Cc(18, 34, 2, K) + Cc(32, 34, 2, K) + Cc(46, 34, 2, K)


def cecite_surdite():
    """Visage aux yeux bandés et à l'oreille barrée."""
    head = P("M32 6 C46 6 54 16 54 30 C54 46 44 58 32 58 C20 58 10 46 10 30 C10 16 18 6 32 6 Z")
    band = R(6, 24, 52, 10, 3, K) + R(8, 26, 48, 6, 2)
    return head + band + P("M24 44 Q32 48 40 44", K).replace('fill="#000000"', 'fill="none" stroke="#000000" stroke-width="2.6"')


def discours_captivant():
    """Orateur levant la main, notes qui s'envolent vers la foule."""
    return (figure(20, 30, 0.95) + _hand(34, 14, 0.32, 20) + place(M["note"](), 44, 24, 0.34)
            + place(M["note"](), 54, 40, 0.28) + Cc(40, 58, 3) + Cc(50, 58, 3) + Cc(60, 58, 3))


def distorsion_vortex():
    """Silhouette aspirée dans un vortex."""
    return place(M["spirale"](), 32, 32, 0.95) + black(figure(32, 32, 0.5)) + figure(32, 32, 0.38)


def don_parole():
    """Bête dont la gueule laisse échapper une bulle de parole."""
    from .art_retouches import wolf_profile
    return over(wolf_profile(24, 40, 0.65), _bubble(44, 18, 0.5), 6) + Cc(38, 18, 2, K) + Cc(44, 18, 2, K) + Cc(50, 18, 2, K)


def deblocage():
    """Cadenas qui s'ouvre, anse soulevée, éclat."""
    body = R(14, 28, 36, 28, 5) + Cc(32, 40, 4, K) + R(30, 40, 4, 9, 1, K)
    shackle = S("M22 28 V18 C22 6 42 6 42 16", 6)
    return body + shackle + burst(52, 10, 7, 6)


def entraves_givre():
    """Chevilles prises dans des anneaux de glace hérissés de cristaux."""
    from .art_armes import boot
    ring = '<ellipse cx="32" cy="46" rx="22" ry="7" fill="none" stroke="#FFFFFF" stroke-width="5"/>'
    crystals = P("M12 46 L8 34 L16 42 Z") + P("M22 42 L20 28 L26 40 Z") + P("M42 40 L44 26 L48 40 Z") + P("M52 44 L58 32 L56 46 Z")
    return boot(32, 26, 0.6) + over("", ring + crystals, 5) + _snow(54, 10, 0.22)


def escapade_cinetique():
    """Silhouette qui bondit, traînée d'énergie."""
    return figure(40, 26, 0.9, 25) + S("M4 56 C14 50 22 50 30 40", 3.4) + S("M10 60 C18 56 24 56 30 48", 2.6) + burst(30, 44, 5, 6)


def espieglerie_nathair():
    """Nuage de malice rieur qui lâche des étincelles."""
    from .art_kit import cloud
    face = black(Cc(24, 28, 2.4) + Cc(38, 28, 2.4) + P("M24 34 C28 40 36 40 40 34 Z"))
    return cloud(28, 1.05) + face + star4(14, 54, 5) + star4(32, 58, 4) + star4(50, 52, 6) + Cc(22, 46, 2) + Cc(42, 46, 2)


def esprit_guerisseur():
    """Esprit lumineux en forme de flamme douce portant une croix de soin."""
    spirit = P("M32 4 C44 16 52 26 52 38 C52 50 44 58 32 58 C20 58 12 50 12 38 C12 26 20 16 32 4 Z")
    cross = '<path d="M32 26 V48 M21 37 H43" stroke="#000000" stroke-width="7" stroke-linecap="round"/>'
    return spirit + cross + star4(56, 10, 4)


def faveur_fortune():
    """Pièce qui tourne, trèfle gravé, éclats."""
    coin = Cc(32, 32, 24) + Cc(32, 32, 19, K) + Cc(32, 32, 16)
    clover = black(Cc(32, 24, 5) + Cc(25, 31, 5) + Cc(39, 31, 5) + Cc(32, 38, 5) + R(31, 38, 2, 10, 1))
    return coin + clover + star4(58, 8, 4) + star4(8, 56, 3.4)


def flambee_aganazzar():
    """Ligne de flammes qui file en avant."""
    return (_flame(14, 40, 0.42) + _flame(30, 34, 0.55) + _flame(48, 28, 0.7) + L([(2, 58), (62, 58)], 3))


def flamme_eternelle():
    """Flamme posée sur une coupe, cerclée."""
    cup = P("M18 40 H46 C46 50 40 54 32 54 C24 54 18 50 18 40 Z") + R(28, 54, 8, 4, 1) + R(22, 58, 20, 4, 2)
    return _flame(32, 22, 0.72) + cup + '<circle cx="32" cy="32" r="30" fill="none" stroke="#FFFFFF" stroke-width="2"/>'


def fletrissement_floraison():
    """Branche : feuille morte d'un côté, fleur épanouie de l'autre."""
    stem = S("M6 58 C20 46 40 44 58 30", 3.6)
    dead = P("M18 48 C12 40 14 32 20 30 C22 36 22 42 18 48 Z")
    flower = "".join(G(P("M0 0 C-5 -6 -5 -12 0 -14 C5 -12 5 -6 0 0 Z"), 52, 22, a) for a in range(0, 360, 72)) + Cc(52, 22, 3, K)
    return stem + dead + flower


def force_fantasmagorique():
    """Monstre aux contours flous qui surgit d'un esprit."""
    from .art_kit import demon
    return _head(18, 40, 0.55) + _dashed(place(demon(), 44, 26, 0.6), "3 3", 2.2) + S("M26 28 C30 22 34 22 36 24", 2.2)


def fouet_mental():
    """Lanière d'énergie qui claque depuis un cerveau."""
    return place(M["cerveau"](), 18, 22, 0.5) + S("M26 30 C36 34 30 46 42 48 C50 50 54 44 58 40", 3.6) + burst(58, 40, 6, 6)


def glace_rime():
    """Bloc de glace épineux qui enserre une jambe."""
    shards = P("M6 58 L14 30 L20 44 L26 22 L34 42 L40 18 L46 40 L52 28 L58 58 Z")
    return shards + black(L([(20, 50), (26, 34)], 1.8) + L([(40, 50), (46, 36)], 1.8)) + _snow(54, 10, 0.2)


def lame_ombres():
    """Dague faite d'ombre : contour plein, intérieur évidé, volutes sombres."""
    from .art_armes import dagger
    blade = dagger(32, 32, 45, 1.4)
    wisps = S("M8 20 C14 16 18 22 24 18", 2.6) + S("M40 52 C46 48 50 54 56 50", 2.6)
    return blade + black(place(dagger(32, 32, 45, 1.4), 32, 32, 0.6)) + wisps


def libelle_aerien():
    """Lettres de fumée tracées dans le ciel au-dessus des nuages."""
    clouds = place(M["brume"](), 32, 50, 0.6)
    letters = S("M8 24 L14 10 L20 24 M11 18 H17", 2.8) + S("M26 10 V24 M26 10 H34 M26 17 H32", 2.8) + S("M40 10 V24 H48", 2.8)
    return letters + clouds + star4(56, 10, 4)


def lien_protection():
    """Deux silhouettes reliées par un lien lumineux sous un même bouclier."""
    arc = S("M6 30 C6 10 58 10 58 30", 4)
    return arc + figure(18, 40, 0.65) + figure(46, 40, 0.65) + L([(24, 36), (40, 36)], 2.4) + Cc(32, 36, 3)


def localisation_animaux_plantes():
    """Loupe posée sur une empreinte et une feuille."""
    from .art_retouches import wolf_paw
    return wolf_paw(22, 40, 0.5) + place(M["feuille"](), 46, 44, 0.34) + over("", place(M["loupe"](), 34, 26, 0.7), 6)


def localisation_objet():
    """Boussole dont l'aiguille pointe vers un objet lointain."""
    compass = Cc(26, 38, 20) + Cc(26, 38, 15, K) + P("M26 26 L30 38 L26 50 L22 38 Z") + Cc(26, 38, 2.4, K)
    return compass + place(M["anneau"](), 52, 14, 0.36) + S("M40 26 C44 22 46 20 48 18", 2) + star4(56, 34, 3)


def messager_animal():
    """Oiseau en vol portant un parchemin roulé."""
    from .art_kit import bird
    return place(bird(), 30, 26, 1.0) + R(26, 42, 18, 7, 3) + Cc(26, 45.5, 3.5) + Cc(44, 45.5, 3.5) + black(L([(32, 42), (32, 49)], 1.4))


def modification_apparence():
    """Visage à moitié transformé : une moitié humaine, une moitié bestiale."""
    left = P("M32 6 C20 6 12 16 12 30 C12 46 22 58 32 58 Z")
    right = P("M32 6 C40 6 48 10 52 16 L60 6 L56 22 C56 26 54 30 54 34 C54 46 44 58 32 58 Z")
    return (left + right + L([(32, 6), (32, 58)], 1.8, K) + P("M18 28 L28 30 L19 33 Z", K) + P("M46 26 L36 30 L45 33 Z", K)
            + S("M20 44 Q26 46 30 44", 2, K) + P("M36 42 L40 48 L44 42 Z", K))


def metal_brulant():
    """Plastron chauffé au rouge, vapeur qui s'en échappe."""
    armor = M["armure"]()
    heat = S("M20 16 C16 12 24 10 20 4", 2.6) + S("M32 14 C28 10 36 8 32 2", 2.6) + S("M44 16 C40 12 48 10 44 4", 2.6)
    return place(armor, 32, 40, 0.75) + heat


def nuee_dagues():
    """Couronne de dagues qui tournoient."""
    from .art_armes import dagger
    out = ""
    for k in range(6):
        a = k * 60
        x, y = 32 + 20 * math.cos(math.radians(a)), 32 + 20 * math.sin(math.radians(a))
        out += dagger(x, y, a + 90, 0.55)
    return out + Cc(32, 32, 4)


def objet_immobile():
    """Objet suspendu, figé par des chaînes tendues vers le sol."""
    stone = P("M20 14 L44 12 L52 28 L42 40 L22 40 L12 26 Z")
    chains = "".join(L([(x1, 40), (x2, 60)], 2.4) for x1, x2 in ((24, 14), (32, 32), (40, 50)))
    return stone + black(L([(22, 22), (40, 32)], 1.8)) + chains + R(6, 58, 52, 4, 2) + star4(56, 8, 4)


def passage_sans_trace():
    """Empreintes qui s'effacent dans la brume."""
    from .art_armes import footprint
    return (footprint(14, 50, -10, 0.8) + footprint(26, 38, 10, 0.7) + _dashed(footprint(38, 26, -10, 0.6), "2 2", 1.6)
            + S("M30 14 H58", 3) + S("M40 22 H60", 3) + S("M44 6 H58", 3))


def pattes_araignee():
    """Silhouette qui marche au plafond, la tête en bas, fil de soie."""
    return (R(2, 2, 60, 5, 1) + G(figure(0, 0, 0.85), 32, 30, 180) + L([(10, 7), (10, 40)], 1.6)
            + place(M["toile"](), 52, 20, 0.3))


def piece_lumineuse():
    """Pièce brillante, grands rayons de lumière."""
    coin = Cc(32, 32, 15) + Cc(32, 32, 11, K) + Cc(32, 32, 8) + black(star4(32, 32, 5))
    return coin + _rays(32, 32, 19, 29, 12, 3.4) + _rays(32, 32, 19, 24, 12, 2, 15)


def poche_poignet():
    """Poignet d'où s'ouvre une petite poche dimensionnelle."""
    return _hand(24, 40, 0.75, 0) + '<ellipse cx="46" cy="20" rx="12" ry="8" fill="#FFFFFF"/>' \
        + '<ellipse cx="46" cy="20" rx="8" ry="4.6" fill="#000000"/>' + star4(46, 20, 3) + S("M32 30 C36 26 38 26 40 26", 2)


def poigne_terreuse():
    """Main de terre qui jaillit du sol et serre le poing."""
    ground = P("M2 50 L12 44 L22 48 L40 42 L52 48 L62 44 V62 H2 Z")
    from .art_armes import fist
    return fist(32, 26, 0.9) + R(22, 36, 20, 12, 2) + ground + black(L([(8, 54), (20, 52)], 1.8) + L([(40, 56), (52, 52)], 1.8))


def priere_guerison():
    """Deux mains jointes en prière, lumière qui en descend."""
    hands = P("M32 10 C28 16 22 30 22 42 L18 56 H30 L32 46 L34 56 H46 L42 42 C42 30 36 16 32 10 Z") + L([(32, 14), (32, 46)], 2, K)
    return hands + _rays(32, 10, 10, 16, 6, 2.6, 200) + star4(10, 44, 4) + star4(54, 44, 4)


def preservation_morts():
    """Sablier posé sur un cercueil, temps arrêté."""
    from .art_kit import coffin
    return place(coffin(), 26, 36, 0.8) + over("", place(M["sablier"](), 48, 24, 0.5), 6)


def pyrotechnie():
    """Feu d'artifice : gerbes qui éclatent dans le ciel."""
    def gerbe(x, y, r):
        return "".join(L([(x + r * 0.35 * math.cos(a), y + r * 0.35 * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))], 2.6)
                       for a in [k * math.pi / 5 for k in range(10)]) + Cc(x, y, 2.4)
    return gerbe(20, 20, 16) + gerbe(46, 30, 13) + S("M24 62 C24 50 22 44 20 36", 2.2)


def rayon_affaiblissant():
    """Rayon qui frappe une silhouette, qui fléchit sous le poids, flèche vers le bas."""
    kneel = G(Cc(0, -14, 6) + P("M-9 -6 H9 L10 8 L16 22 H9 L4 12 L-4 12 L-6 24 H-12 L-10 8 Z"), 40, 36, 0, 1.0)
    beam = L([(2, 6), (30, 26)], 5) + L([(2, 6), (30, 26)], 1.6, K)
    down = G(R(-3.5, -10, 7, 12, 2) + P("M-9 2 H9 L0 12 Z"), 56, 16, 0, 0.8)
    return beam + kneel + down


def rayon_lune():
    """Colonne de lumière lunaire qui tombe sur le sol."""
    return (place(M["lune"](), 32, 12, 0.36) + P("M22 20 H42 L50 58 H14 Z") + black(P("M26 24 H38 L44 54 H20 Z"))
            + R(4, 58, 56, 4, 2) + star4(54, 30, 3.4) + star4(10, 34, 3))


def sens_animal():
    """Œil de bête (pupille fendue) relié à une empreinte."""
    eye = P("M4 30 C14 16 50 16 60 30 C50 44 14 44 4 30 Z") + Cc(32, 30, 11, K) + P("M32 20 C35 26 35 34 32 40 C29 34 29 26 32 20 Z")
    from .art_retouches import wolf_paw
    return eye + wolf_paw(32, 54, 0.28)


def sens_distorsion():
    """Œil au centre de cercles déformés."""
    return (S("M4 32 C10 12 54 12 60 32 C54 52 10 52 4 32 Z", 2.4) + S("M10 32 C16 18 48 18 54 32 C48 46 16 46 10 32", 2.4)
            + place(M["oeil"](), 32, 32, 0.6))


def sens_pieges():
    """Plaque de pression au sol repérée, point d'exclamation."""
    return (R(10, 46, 44, 8, 2) + black(R(14, 48, 36, 4, 1)) + L([(4, 58), (60, 58)], 2.4)
            + R(28, 6, 8, 26, 4) + Cc(32, 38, 4.4))


def souffle_dragon_sort():
    """Bouche de dragon de face crachant un cône d'énergie."""
    from .art_kit import dragon_head
    return place(dragon_head(), 22, 28, 0.6) + P("M38 30 L62 16 V48 Z") + black(P("M42 31 L58 24 V40 Z"))


def tourbillon_poussiere():
    """Petit tourbillon de sable qui soulève graviers et poussière au ras du sol."""
    from .art_kit import tornado
    return (place(tornado(), 26, 30, 0.75) + "".join(Cc(x, y, r) for x, y, r in ((48, 40, 3.4), (54, 30, 2.4), (44, 22, 2), (56, 50, 2.6)))
            + S("M2 60 C14 54 30 54 40 58 C48 60 56 56 62 58", 3))

def vent_protecteur():
    """Tourbillon de vent qui entoure une silhouette."""
    return (figure(32, 32, 0.8) + S("M6 24 C10 10 54 10 58 24", 3.4) + S("M58 40 C54 54 10 54 6 40", 3.4)
            + P("M58 18 L60 28 L52 24 Z") + P("M6 46 L4 36 L12 40 Z"))


def verrou_magique():
    """Porte scellée par une serrure rayonnante."""
    door = P("M14 60 V22 C14 10 22 4 32 4 C42 4 50 10 50 22 V60 Z") + black(L([(32, 8), (32, 60)], 2))
    lock = Cc(32, 34, 8) + black(Cc(32, 32, 2.4) + R(31, 32, 2, 6, 1))
    return door + black(Cc(32, 34, 11)) + lock + _rays(32, 34, 13, 17, 8, 2)


def vigueur_arcanique():
    """Cœur traversé de filets d'énergie arcanique."""
    return (M["coeur"]() + black(S("M18 24 C24 30 28 20 34 28 C40 36 44 26 48 30", 2.6)) + star4(54, 8, 5))


def voir_invisible():
    """Œil grand ouvert qui révèle une silhouette en pointillés."""
    return place(M["oeil"](), 32, 18, 0.62) + _dashed(figure(32, 46, 0.55), "3 2", 2) + _rays(32, 18, 18, 22, 6, 2, 200)


def zone_verite():
    """Cercle au sol, flamme de vérité en son centre."""
    return ('<ellipse cx="32" cy="50" rx="28" ry="9" fill="none" stroke="#FFFFFF" stroke-width="3.4"/>'
            + _flame(32, 30, 0.7) + black(place(M["oeil"](), 32, 34, 0.28)))


def epine_mentale():
    """Épine de cristal plantée dans un cerveau."""
    return (place(M["cerveau"](), 28, 38, 0.72)
            + over("", P("M60 4 L36 32 L32 30 L56 2 Z"), 5) + burst(34, 32, 6, 6))


SCENES = {
    "Agrandissement/Rapetissement": agrandissement, "Apaisement des émotions": apaisement,
    "Appel de destrier": appel_destrier, "Arme magique": arme_magique, "Attraction terrestre": attraction_terrestre,
    "Aura magique de Nystul": aura_nystul, "Bouche magique": bouche_magique, "Bourrasque": bourrasque,
    "Châtiment de révélation": chatiment_revelation, "Châtiment révélateur": chatiment_revelateur,
    "Connaissance empruntée": connaissance_empruntee, "Convocation de bête": convocation_bete,
    "Corde enchantée": corde_enchantee, "Cordon de flèches": cordon_fleches, "Couronne du dément": couronne_dement,
    "Cécité/Surdité": cecite_surdite, "Discours captivant": discours_captivant, "Distorsion de vortex": distorsion_vortex,
    "Don de la parole": don_parole, "Déblocage": deblocage, "Entraves de givre": entraves_givre,
    "Escapade cinétique": escapade_cinetique, "Espièglerie de Nathair": espieglerie_nathair,
    "Esprit guérisseur": esprit_guerisseur, "Faveur de la fortune": faveur_fortune,
    "Flambée d'Aganazzar": flambee_aganazzar, "Flamme éternelle": flamme_eternelle,
    "Flétrissement et floraison": fletrissement_floraison, "Force fantasmagorique": force_fantasmagorique,
    "Fouet mental de Tasha": fouet_mental, "Glace entravante de Rime": glace_rime, "Lame d'ombres": lame_ombres,
    "Libellé aérien": libelle_aerien, "Lien de protection": lien_protection,
    "Localisation d'animaux ou de plantes": localisation_animaux_plantes, "Localisation d'objet": localisation_objet,
    "Messager animal": messager_animal, "Modification d'apparence": modification_apparence,
    "Métal brûlant": metal_brulant, "Nuée de dagues": nuee_dagues, "Objet immobile": objet_immobile,
    "Passage sans trace": passage_sans_trace, "Pattes d'araignée": pattes_araignee,
    "Pièce lumineuse de Jim": piece_lumineuse, "Poche de poignet": poche_poignet,
    "Poigne terreuse de Maximilien": poigne_terreuse, "Prière de guérison": priere_guerison,
    "Préservation des morts": preservation_morts, "Pyrotechnie": pyrotechnie,
    "Rayon affaiblissant": rayon_affaiblissant, "Rayon de lune": rayon_lune, "Sens animal": sens_animal,
    "Sens de la distorsion": sens_distorsion, "Sens des pièges": sens_pieges, "Souffle du dragon": souffle_dragon_sort,
    "Tourbillon de poussière": tourbillon_poussiere, "Vent protecteur": vent_protecteur, "Verrou magique": verrou_magique,
    "Vigueur arcanique": vigueur_arcanique, "Voir l'invisible": voir_invisible, "Zone de vérité": zone_verite,
    "Épine mentale": epine_mentale,
}
