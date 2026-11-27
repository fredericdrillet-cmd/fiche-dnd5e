"""
Scènes dessinées (v53) des sorts de niveau 1 et 3 qui n'avaient qu'une composition à deux éléments. Grille 64 × 64,
blanc = dessin, noir = découpe.
"""
from __future__ import annotations

import math

from .art_armes import Cc, G, K, L, P, R, S, boot, burst, curved_arrow, dagger, over, star4
from .art_kit import black, cloud, demon, figure, horse, place
from .art_motifs import MOTIFS as M
from .art_scenes2 import _bubble, _dashed, _drop, _flame, _rays, _snow, _sword


def _wave_line(y, w=3.4, amp=5):
    return S("M2 {y} C10 {a} 18 {b} 26 {y} C34 {a} 42 {b} 50 {y} C56 {a} 60 {y} 62 {y}".format(y=y, a=y - amp, b=y + amp), w)


# ------------------------------------------------------------------------------------------------ niveau 1
def barbes_argentees():
    """Crâne nimbé, lune d'argent au-dessus, rayons froids."""
    return place(M["crane"](), 32, 38, 0.75) + place(M["lune"](), 32, 10, 0.3) + _rays(32, 38, 24, 29, 8, 2.2)


def chatiment_divin_sort():
    """Épée brandie, faisceau sacré qui descend sur la lame."""
    beam = P("M40 2 H56 L46 30 H36 Z") + black(P("M44 4 H52 L45 24 H40 Z"))
    return beam + _sword(26, 40, 45, 1.05) + burst(36, 30, 7, 8)


def creation_destruction_eau():
    """Une goutte qui naît d'un côté, une goutte qui s'évapore de l'autre."""
    return (_drop(20, 34, 0.7) + _dashed(_drop(46, 34, 0.7), "3 3", 2) + S("M44 10 C40 6 48 4 44 0", 2.4)
            + S("M52 12 C48 8 56 6 52 2", 2.4) + curved_arrow("M24 8 C30 2 36 2 42 8", (42, 8), 40, 2.4, 6))


def ceremonie():
    """Calice entre deux bougies, lumière au-dessus."""
    chalice = P("M22 22 H42 C42 34 38 40 32 40 C26 40 22 34 22 22 Z") + R(30, 40, 4, 10, 1) + R(22, 50, 20, 5, 2)
    candles = R(6, 30, 7, 24, 1) + R(51, 30, 7, 24, 1) + _flame(9.5, 24, 0.2) + _flame(54.5, 24, 0.2)
    return chalice + candles + _rays(32, 12, 4, 9, 8, 2) + Cc(32, 12, 2.6)


def disque_tenser():
    """Disque de force flottant qui porte un coffre."""
    disk = '<ellipse cx="32" cy="44" rx="28" ry="8" fill="#FFFFFF"/><ellipse cx="32" cy="42" rx="20" ry="4" fill="#000000"/>'
    chest = P("M18 26 C18 18 24 14 32 14 C40 14 46 18 46 26 Z") + R(18, 28, 28, 14, 1) + black(R(29, 24, 6, 8, 1))
    under = L([(14, 54), (12, 60)], 2.4) + L([(32, 54), (32, 62)], 2.4) + L([(50, 54), (52, 60)], 2.4)
    return disk + chest + under


def don_alacrite():
    """Sablier ailé, trait de vitesse."""
    wing = lambda sx: '<g transform="translate(32 0) scale({} 1) translate(-32 0)">'.format(sx) + P(
        "M42 26 C48 18 56 14 62 14 C58 18 56 20 54 22 C58 22 60 24 62 26 C56 28 50 30 42 30 Z") + "</g>"
    return wing(1) + wing(-1) + place(M["sablier"](), 32, 34, 0.62)


def detection_poison():
    """Œil au-dessus d'une fiole fumante."""
    return (place(M["fiole"](), 32, 42, 0.6) + S("M28 20 C24 16 32 14 28 10", 2.2) + S("M36 20 C32 16 40 14 36 10", 2.2)
            + _rays(32, 42, 20, 24, 10, 2))


def frappe_zephyr():
    """Silhouette portée par une bourrasque, lame en avant."""
    return (figure(30, 34, 0.9, 20) + _sword(48, 20, 60, 0.55) + S("M2 30 H16", 3.4) + S("M4 40 H18", 3.4) + S("M2 50 H14", 3.4))


def gravite_amplifiee():
    """Rochers écrasés contre le sol, flèches vers le bas."""
    down = lambda x: G(R(-3, -10, 6, 12, 2) + P("M-8 2 H8 L0 12 Z"), x, 14, 0, 1.0)
    return down(14) + down(32) + down(50) + place(M["pierres"](), 32, 46, 0.6) + R(2, 58, 60, 4, 2)


def injonction():
    """Bouche qui crie un ordre, mot unique en majuscule."""
    bub = _bubble(34, 28, 0.95)
    return bub + black(R(31, 14, 6, 18, 3) + Cc(34, 38, 3.4)) + S("M6 18 C2 26 2 34 6 42", 3)


def lien_bete():
    """Silhouette et loup reliés par un fil lumineux."""
    from .art_retouches import wolf_profile
    return figure(14, 34, 0.75) + wolf_profile(46, 36, 0.6) + S("M22 20 C28 12 36 12 40 22", 2.6) + star4(31, 12, 3.6)


def malefice():
    """Œil cerclé d'épines, larme sombre."""
    eye = place(M["oeil"](), 32, 30, 0.9)
    thorns = "".join(G(P("M0 -30 L3 -22 L-3 -22 Z"), 32, 30, a) for a in range(0, 360, 30))
    return thorns + eye + _drop(32, 56, 0.2)


def mixture_caustique():
    """Fiole renversée d'où coule un acide qui ronge le sol."""
    return (G(R(-6, -14, 12, 6, 2) + P("M-8 -8 H8 C14 -2 16 6 16 12 C16 20 8 24 0 24 C-8 24 -16 20 -16 12 C-16 6 -14 -2 -8 -8 Z"), 24, 24, -60, 0.9)
            + _drop(44, 40, 0.24) + _drop(52, 48, 0.2) + P("M30 56 C36 50 46 52 50 58 Z") + R(4, 58, 56, 4, 2))


def projectile_jim():
    """Trois petites comètes rieuses."""
    def comet(x, y, s):
        return G(P("M0 -6 C4 -6 7 -3 7 0 C7 3 4 6 0 6 L-22 1.2 L-22 -1.2 Z"), x, y, -45, s)
    return comet(46, 18, 1.1) + comet(30, 34, 1.1) + comet(50, 42, 0.9) + black(Cc(47, 17, 1.4) + Cc(31, 33, 1.4))


def projectile_elementaire():
    """Comète dont la traîne se divise en flamme, givre et éclair."""
    head = Cc(46, 18, 9)
    trails = (L([(40, 24), (10, 54)], 3.4) + L([(42, 26), (20, 58)], 3) + L([(38, 22), (6, 42)], 3))
    return trails + head + black(Cc(46, 18, 4)) + _flame(10, 52, 0.2) + _snow(22, 58, 0.14) + star4(6, 40, 3.4)


def purification():
    """Assiette et gobelet sous une pluie d'éclats purs."""
    plate = '<ellipse cx="24" cy="48" rx="18" ry="6" fill="#FFFFFF"/><ellipse cx="24" cy="46" rx="11" ry="3" fill="#000000"/>'
    cup = P("M42 30 H56 L54 52 H44 Z") + R(40, 28, 18, 4, 1)
    return plate + cup + star4(16, 18, 6) + star4(32, 10, 5) + star4(48, 16, 4) + Cc(26, 30, 2) + Cc(40, 22, 2)


def represailles_infernales():
    """Silhouette frappée qui riposte : flammes infernales qui retournent vers l'agresseur."""
    return (figure(20, 34, 0.9) + curved_arrow("M28 24 C38 14 48 14 54 22", (54, 22), 60, 3, 8)
            + _flame(48, 44, 0.48) + _flame(58, 36, 0.3))


def secousse_sismique():
    """Sol qui se fend, onde de choc en arcs."""
    ground = P("M2 44 H62 V62 H2 Z") + black(L([(20, 44), (26, 52), (22, 58), (30, 62)], 2.6) + L([(42, 44), (38, 54), (44, 62)], 2.6))
    arcs = S("M14 36 C22 24 42 24 50 36", 3) + S("M6 34 C16 14 48 14 58 34", 2.6)
    return ground + arcs + L([(32, 30), (32, 40)], 3)


def serviteur_invisible():
    """Plateau porté par une silhouette invisible en pointillés."""
    tray = R(6, 24, 44, 4, 2) + P("M14 24 C14 16 22 12 28 12 C34 12 42 16 42 24 Z")
    return _dashed(figure(30, 40, 0.8), "3 3", 2) + tray + Cc(28, 10, 2.4) + star4(56, 10, 4)


def simulacre_vie():
    """Crâne dont la mâchoire laisse voir un cœur battant, trait de pouls."""
    return (place(M["crane"](), 32, 26, 0.75) + over("", place(M["coeur"](), 46, 46, 0.36), 6)
            + S("M2 52 H12 L16 44 L20 58 L24 52 H30", 2.8))


def tentacules_hadar():
    """Tentacules noirs qui jaillissent d'un vide."""
    void = '<ellipse cx="32" cy="54" rx="28" ry="8" fill="#FFFFFF"/><ellipse cx="32" cy="54" rx="22" ry="5" fill="#000000"/>'
    tents = S("M14 54 C10 40 22 34 18 20 C16 12 22 8 26 10", 5) + S("M34 54 C34 40 44 34 40 18 C38 10 46 4 50 8", 5) \
        + S("M50 54 C54 46 58 42 58 32", 4)
    return void + tents


def texte_illusoire():
    """Parchemin dont les lignes se changent en volutes illusoires."""
    scroll = R(8, 12, 40, 40, 2) + Cc(8, 18, 6) + Cc(48, 46, 6)
    lines = black(L([(14, 22), (40, 22)], 2) + L([(14, 30), (34, 30)], 2) + S("M14 38 C20 34 24 42 30 38 C34 34 38 42 42 38", 2))
    return scroll + lines + star4(56, 10, 6) + star4(56, 30, 3.4)


def trait_ensorcele():
    """Éclair qui enchaîne une silhouette par un lien crépitant."""
    return (place(M["eclair"](), 14, 20, 0.5) + L([(20, 28), (30, 32), (26, 36), (38, 40)], 3) + figure(48, 38, 0.8))


def valeur_deformee():
    """Gemme à moitié réelle, à moitié en trompe-l'œil."""
    gem = M["gemme"]()
    return place(gem, 24, 30, 0.75) + _dashed(place(gem, 48, 46, 0.4), "2 2", 1.6) + star4(52, 12, 4)


def vents_contraires():
    """Deux rafales qui s'opposent et se heurtent."""
    left = S("M2 22 H26 C32 22 34 14 28 12", 4) + S("M4 34 H28", 4)
    right = S("M62 30 H38 C32 30 30 38 36 40", 4) + S("M60 42 H36", 4)
    return left + right + burst(32, 28, 6, 6) + S("M10 52 C18 48 22 56 30 52 C38 48 42 56 50 52", 2.4)


def eclair_chaos():
    """Éclair qui rebondit en zigzag désordonné."""
    pts = [(4, 10), (20, 24), (12, 30), (34, 40), (26, 46), (58, 58)]
    return L(pts, 6) + L(pts, 2, K) + burst(58, 58, 7, 6) + star4(48, 12, 5) + star4(10, 48, 3.4)


def eclair_tracant():
    """Rayon lumineux qui frappe une cible et la laisse étincelante."""
    return L([(4, 60), (36, 28)], 6) + L([(4, 60), (36, 28)], 2, K) + place(M["cible"](), 44, 20, 0.5) + _rays(44, 20, 17, 21, 8, 2)


# ------------------------------------------------------------------------------------------------ niveau 3
def amitie_instantanee():
    """Deux silhouettes qui se serrent la main, cœur au-dessus."""
    return figure(18, 38, 0.8) + figure(46, 38, 0.8) + R(24, 34, 16, 4, 2) + place(M["coeur"](), 32, 12, 0.3)


def antidetection():
    """Œil barré par un voile ondulé : la divination ne voit rien."""
    eye = place(M["oeil"](), 32, 30, 0.95)
    veil = S("M2 22 C12 14 20 30 32 22 C44 14 52 30 62 22", 5) + S("M2 40 C12 32 20 48 32 40 C44 32 52 48 62 40", 5)
    return over(eye, veil, 6)


def aura_vitalite():
    """Silhouette rayonnante d'où partent des cœurs."""
    return figure(32, 34, 0.9) + place(M["coeur"](), 10, 16, 0.2) + place(M["coeur"](), 54, 16, 0.2) \
        + place(M["coeur"](), 54, 46, 0.18) + place(M["coeur"](), 10, 46, 0.18) + _rays(32, 30, 24, 28, 8, 2)


def chatiment_aveuglant():
    """Épée qui frappe dans un éclair de lumière aveuglante."""
    return _sword(26, 38, 45, 1.0) + Cc(44, 18, 9) + _rays(44, 18, 12, 20, 12, 2.6)


def clairvoyance():
    """Œil flottant devant une porte lointaine."""
    door = P("M30 60 V34 C30 26 36 22 44 22 C52 22 58 26 58 34 V60 Z") + black(L([(44, 24), (44, 60)], 1.6))
    return door + over("", place(M["oeil"](), 22, 24, 0.6), 6) + S("M10 46 C16 40 22 40 28 44", 2.2)


def communication_plantes():
    """Fleur au visage souriant, bulle de parole."""
    flower = "".join(G(P("M0 0 C-6 -8 -6 -16 0 -18 C6 -16 6 -8 0 0 Z"), 24, 26, a) for a in range(0, 360, 60)) + Cc(24, 26, 6)
    face = black(Cc(22, 25, 1.4) + Cc(26, 25, 1.4))
    return S("M24 34 V60", 3.4) + P("M24 50 C16 46 12 50 10 54 C16 56 20 54 24 50 Z") + flower + face + _bubble(48, 14, 0.36)


def convocation_demons_mineurs():
    """Trois petits démons qui surgissent d'un cercle de flammes."""
    circle = '<ellipse cx="32" cy="54" rx="28" ry="7" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
    return circle + place(demon(), 16, 34, 0.38) + place(demon(), 48, 34, 0.38) + place(demon(), 32, 22, 0.42)


def convocation_fee():
    """Fée aux ailes de papillon, baguette étoilée."""
    wings = (P("M32 30 C24 16 10 12 6 20 C4 28 16 34 32 32 Z") + P("M32 30 C40 16 54 12 58 20 C60 28 48 34 32 32 Z")
             + P("M32 34 C24 40 14 48 16 54 C20 58 28 48 32 36 Z") + P("M32 34 C40 40 50 48 48 54 C44 58 36 48 32 36 Z"))
    return wings + black(R(30, 22, 4, 24, 2)) + Cc(32, 18, 4) + star4(54, 8, 5)


def convocation_mort_vivant():
    """Crâne et main osseuse qui émergent d'une tombe."""
    ground = P("M2 50 L14 46 L28 50 L42 44 L62 48 V62 H2 Z")
    tomb = P("M40 50 V22 C40 14 46 10 52 10 C58 10 62 14 62 22 V50 Z") + black(R(49, 18, 6, 18, 1) + R(46, 24, 12, 5, 1))
    return tomb + place(M["crane"](), 20, 34, 0.5) + ground


def convocation_rejeton_ombre():
    """Silhouette d'ombre aux yeux brillants qui sort d'une flaque sombre."""
    pool = '<ellipse cx="32" cy="56" rx="26" ry="6" fill="#FFFFFF"/>'
    shade = P("M32 6 C42 6 46 14 46 22 C46 30 52 40 54 56 H10 C12 40 18 30 18 22 C18 14 22 6 32 6 Z")
    return pool + shade + black(P("M24 18 L30 20 L25 22 Z") + P("M40 18 L34 20 L39 22 Z") + S("M20 40 C24 46 26 50 26 56", 1.8))


def creation_nourriture():
    """Pain, gourde et fruits apparaissant dans un éclat."""
    from .art_objets import OBJECTS
    return place(OBJECTS["objet_ration"](), 22, 40, 0.6) + place(OBJECTS["objet_gourde"](), 48, 38, 0.5) + star4(32, 10, 7)


def discours_motivant():
    """Orateur au poing levé, rayons d'enthousiasme."""
    from .art_armes import fist
    return figure(24, 38, 0.85) + fist(44, 16, 0.4) + L([(30, 26), (40, 20)], 4) + _rays(44, 16, 12, 16, 7, 2, 200)


def delivrance_malediction():
    """Chaîne qui se brise au-dessus d'un crâne qui s'efface."""
    return M["chaine_brisee"]() + _dashed(place(M["crane"](), 50, 50, 0.3), "2 2", 1.6)


def ennemis_foison():
    """Silhouette effrayée cernée par des yeux menaçants dans l'ombre."""
    eyes = "".join(P("M{x} {y} L{a} {b} L{x} {c} Z".format(x=x, y=y, a=x + 6, b=y + 2, c=y + 4)) + P(
        "M{x} {y} L{a} {b} L{x} {c} Z".format(x=x + 14, y=y, a=x + 8, b=y + 2, c=y + 4)) for x, y in ((2, 8), (44, 10), (2, 46), (46, 48)))
    return figure(32, 34, 0.85) + eyes + S("M24 12 L26 6 M32 10 V4 M40 12 L38 6", 2)


def fleches_enflammees():
    """Flèche à la pointe enflammée, traînée de feu."""
    return L([(6, 58), (40, 24)], 3.6) + _flame(46, 18, 0.5) + P("M10 54 L4 46 L10 44 Z") + P("M10 54 L18 60 L20 54 Z")


def forme_gazeuse():
    """Silhouette qui se dissout en volutes de brume."""
    return (G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H-12 Z"), 32, 28, 0, 1.0) + S("M20 38 C24 46 18 52 22 58", 3.4)
            + S("M32 38 C36 46 30 52 34 60", 3.4) + S("M44 38 C48 46 42 52 46 58", 3.4))


def forteresse_intellect():
    """Tour crénelée protégeant un cerveau."""
    tower = R(10, 22, 44, 38, 2) + "".join(R(x, 14, 8, 10, 1) for x in (10, 22, 34, 46))
    return tower + black(place(M["cerveau"](), 32, 40, 0.5))


def foulee_ashardalon():
    """Pas enflammés : botte qui laisse des flammes derrière elle."""
    return boot(44, 26, 0.6) + _flame(14, 46, 0.34) + _flame(28, 50, 0.28) + L([(2, 60), (62, 60)], 2.4)


def foulee_tonitruante():
    """Silhouette qui disparaît dans un grondement de tonnerre."""
    return _dashed(figure(32, 32, 1.0), "3 3", 2) + S("M6 18 C2 26 2 38 6 46", 3.4) + S("M58 18 C62 26 62 38 58 46", 3.4) \
        + S("M12 22 C8 28 8 36 12 42", 2.6) + S("M52 22 C56 28 56 36 52 42", 2.6)


def image_majeure():
    """Château illusoire aux contours en pointillés, éclats."""
    castle = R(8, 30, 48, 28, 1) + "".join(R(x, 22, 8, 10, 1) for x in (8, 22, 36, 48)) + P("M28 22 L32 8 L36 22 Z")
    return _dashed(castle, "3 2", 2.2) + star4(56, 8, 5)


def inciter_cupidite():
    """Pièces qui attirent un regard avide."""
    coins = "".join(Cc(x, y, 8) + black(Cc(x, y, 5.5)) + Cc(x, y, 4) for x, y in ((18, 46), (34, 52), (48, 42)))
    return coins + place(M["oeil"](), 32, 16, 0.5) + _rays(32, 16, 14, 18, 6, 2, 200)


def invocation_animaux():
    """Deux loups qui bondissent hors d'un cercle de convocation."""
    from .art_retouches import wolf_profile
    circle = '<ellipse cx="32" cy="54" rx="28" ry="7" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
    return circle + wolf_profile(20, 30, 0.55) + over("", wolf_profile(44, 36, 0.55), 5)


def invocation_projectiles():
    """Arme qui se démultiplie en volée de copies spectrales."""
    return (dagger(40, 24, 45, 1.0) + _dashed(dagger(26, 38, 45, 0.9), "3 2", 1.6) + _dashed(dagger(14, 50, 45, 0.8), "3 2", 1.6))


def marche_eau():
    """Silhouette debout sur les vagues."""
    return figure(32, 26, 0.85) + _wave_line(52) + _wave_line(60, 2.6, 3)


def minuscules_meteores():
    """Petites sphères enflammées qui tournent autour d'une silhouette."""
    return figure(32, 36, 0.75) + "".join(_flame(32 + 22 * math.cos(a), 30 + 18 * math.sin(a), 0.18)
                                          for a in [k * math.pi / 3 for k in range(6)])


def monture_fantome():
    """Cheval spectral aux contours en pointillés, crinière de brume."""
    return _dashed(horse(), "3 2", 2.4) + S("M46 4 C50 0 56 2 58 6", 2.4) + star4(8, 10, 4)


def mort_simulee():
    """Silhouette allongée, masque de mort, petit cœur encore battant."""
    body = G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H6 L5 26 H-5 L-6 8 H-12 Z"), 32, 44, 90, 0.85)
    return body + R(4, 56, 56, 3, 1) + place(M["coeur"](), 32, 20, 0.22) + S("M24 12 L28 8 L32 14 L36 8 L40 12", 2.2)


def mur_eau():
    """Muraille d'eau dressée, vagues qui ondulent."""
    return R(6, 10, 52, 48, 4) + black(_wave_line(22, 2.4) + _wave_line(34, 2.4) + _wave_line(46, 2.4))


def mur_sable():
    """Mur de sable qui s'écoule, grains qui volent."""
    wall = P("M6 58 V24 C14 18 22 26 32 20 C42 14 50 22 58 18 V58 Z")
    return wall + black("".join(Cc(x, y, 1.6) for x, y in ((14, 34), (26, 40), (40, 32), (50, 44), (20, 50), (36, 52))))


def mur_vent():
    """Colonne de vent tourbillonnant entre deux piliers."""
    return R(4, 8, 7, 50, 2) + R(53, 8, 7, 50, 2) + "".join(
        S("M14 {y} C24 {a} 40 {b} 50 {y}".format(y=y, a=y - 6, b=y + 6), 3.4) for y in (16, 28, 40, 52))


def onde_pulsee():
    """Onde de force concentrique qui repousse."""
    return Cc(32, 32, 7) + "".join('<circle cx="32" cy="32" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(r, w)
                                   for r, w in ((14, 3.6), (21, 3), (28, 2.4))) + curved_arrow("M54 8 L60 2", (60, 2), -45, 2.2, 5)


def petite_hutte():
    """Dôme de force translucide abritant un feu de camp."""
    dome = '<path d="M4 54 C4 28 18 10 32 10 C46 10 60 28 60 54 Z" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
    return dome + _flame(32, 42, 0.42) + R(20, 50, 24, 4, 2) + L([(2, 56), (62, 56)], 3)


def protection_energie():
    """Silhouette entourée d'une bulle qui fait ricocher flamme et éclair."""
    bubble = '<circle cx="32" cy="34" r="22" fill="none" stroke="#FFFFFF" stroke-width="3.4"/>'
    return bubble + figure(32, 36, 0.7) + _flame(8, 12, 0.22) + place(M["eclair"](), 56, 12, 0.3)


def raz_de_maree():
    """Grande vague qui déferle."""
    return (P("M2 58 C6 40 18 18 38 12 C52 8 62 18 60 30 C54 22 46 22 42 30 C38 38 46 46 56 44 C50 54 40 58 28 58 Z")
            + black(S("M10 52 C16 40 24 30 36 24", 2.2)) + Cc(56, 12, 2.4) + Cc(50, 6, 2))


def serviteur_miniature():
    """Petit objet animé qui marche, clé dans le dos."""
    body = R(18, 18, 28, 26, 6) + black(Cc(26, 30, 3) + Cc(38, 30, 3))
    legs = L([(24, 44), (20, 58)], 3.4) + L([(40, 44), (44, 58)], 3.4)
    key = Cc(52, 14, 4) + L([(46, 20), (52, 14)], 2.6)
    return body + legs + key + star4(10, 12, 4)


def sieste():
    """Silhouette endormie sur un nuage, lune et « Z »."""
    z = lambda x, y, s: '<path transform="translate({} {}) scale({})" d="M0 0 h12 v3 l-8 9 h8 v3 h-13 v-3 l8 -9 h-7 Z" fill="#FFFFFF"/>'.format(x, y, s)
    return cloud(44, 0.9) + black(G(Cc(0, -20, 6) + P("M-10 -10 H10 L12 8 H-12 Z"), 32, 42, 90, 0.6)) + z(40, 6, 0.9) + z(52, 18, 0.6)


def transfert_vie():
    """Deux cœurs reliés : l'un se vide au profit de l'autre."""
    return (_dashed(place(M["coeur"](), 16, 32, 0.4), "3 2", 2) + place(M["coeur"](), 48, 32, 0.4)
            + L([(28, 32), (34, 32)], 3) + P("M38 32 L32 26 V38 Z"))


def voile_spirituel():
    """Silhouette drapée d'un voile spectral flottant."""
    veil = P("M32 6 C44 6 52 16 52 28 L58 58 C50 54 42 60 32 56 C22 60 14 54 6 58 L12 28 C12 16 20 6 32 6 Z")
    return veil + black(Cc(26, 24, 2.6) + Cc(38, 24, 2.6) + S("M20 40 C24 48 22 54 24 58", 1.8) + S("M44 40 C40 48 42 54 40 58", 1.8))


def voracite_hadar():
    """Sphère de ténèbres glacées où flottent des yeux et des dents."""
    sphere = Cc(32, 32, 27)
    inside = black(Cc(32, 32, 22)) + Cc(22, 24, 3) + Cc(42, 28, 2.4) + "".join(P("M{} 44 L{} 50 L{} 44 Z".format(x, x + 3, x + 6)) for x in (20, 30, 40))
    return sphere + inside + _snow(56, 8, 0.18)


def eruption_terre():
    """Le sol qui explose vers le haut en blocs de roche."""
    ground = P("M2 50 L18 46 L26 52 L38 46 L62 50 V62 H2 Z")
    rocks = P("M24 40 L30 22 L40 24 L42 40 Z") + P("M12 30 L18 20 L24 26 L20 34 Z") + P("M44 22 L52 14 L58 22 L52 30 Z")
    return ground + rocks + L([(32, 44), (32, 48)], 2) + burst(32, 44, 6, 6)


SCENES = {
    "Barbes argentées": barbes_argentees, "Châtiment divin": chatiment_divin_sort,
    "Création ou destruction d'eau": creation_destruction_eau, "Cérémonie": ceremonie,
    "Disque flottant de Tenser": disque_tenser, "Don d'alacrité": don_alacrite,
    "Détection du poison et des maladies": detection_poison, "Frappe du zéphyr": frappe_zephyr,
    "Gravité amplifiée": gravite_amplifiee, "Injonction": injonction, "Lien avec une bête": lien_bete,
    "Maléfice": malefice, "Mixture caustique de Tasha": mixture_caustique, "Projectile magique de Jim": projectile_jim,
    "Projectile élémentaire": projectile_elementaire, "Purification de nourriture et d'eau": purification,
    "Représailles infernales": represailles_infernales, "Secousse sismique": secousse_sismique,
    "Serviteur invisible": serviteur_invisible, "Simulacre de vie": simulacre_vie, "Tentacules de Hadar": tentacules_hadar,
    "Texte illusoire": texte_illusoire, "Trait ensorcelé": trait_ensorcele, "Valeur déformée": valeur_deformee,
    "Vents contraires": vents_contraires, "Éclair de chaos": eclair_chaos, "Éclair traçant": eclair_tracant,
    "Amitié instantanée": amitie_instantanee, "Antidétection": antidetection, "Aura de vitalité": aura_vitalite,
    "Châtiment aveuglant": chatiment_aveuglant, "Clairvoyance": clairvoyance,
    "Communication avec les plantes": communication_plantes, "Convocation de démons mineurs": convocation_demons_mineurs,
    "Convocation de fée": convocation_fee, "Convocation de mort-vivant": convocation_mort_vivant,
    "Convocation de rejeton d'ombre": convocation_rejeton_ombre, "Création de nourriture et d'eau": creation_nourriture,
    "Discours motivant": discours_motivant, "Délivrance des malédictions": delivrance_malediction,
    "Ennemis à foison": ennemis_foison, "Flèches enflammées": fleches_enflammees, "Forme gazeuse": forme_gazeuse,
    "Forteresse d'intellect": forteresse_intellect, "Foulée d'Ashardalon": foulee_ashardalon,
    "Foulée tonitruante": foulee_tonitruante, "Image majeure": image_majeure, "Inciter à la cupidité": inciter_cupidite,
    "Invocation d'animaux": invocation_animaux, "Invocation de projectiles": invocation_projectiles,
    "Marche sur l'eau": marche_eau, "Minuscules météores de Melf": minuscules_meteores, "Monture fantôme": monture_fantome,
    "Mort simulée": mort_simulee, "Mur d'eau": mur_eau, "Mur de sable": mur_sable, "Mur de vent": mur_vent,
    "Onde pulsée": onde_pulsee, "Petite hutte de Léomund": petite_hutte, "Protection contre une énergie": protection_energie,
    "Raz-de-marée": raz_de_maree, "Serviteur miniature": serviteur_miniature, "Sieste": sieste,
    "Transfert de vie": transfert_vie, "Voile spirituel": voile_spirituel, "Voracité de Hadar": voracite_hadar,
    "Éruption de terre": eruption_terre,
}
