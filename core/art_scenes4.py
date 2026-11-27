"""
Scènes dessinées (v53) des sorts de niveau 4. Grille 64 × 64, blanc = dessin, noir = découpe.
"""
from __future__ import annotations

import math

from .art_armes import Cc, G, L, P, R, S, burst, curved_arrow, over, star4
from .art_kit import angel_wings, black, cloud, demon, doorway, figure, horse, insect, place, tree
from .art_motifs import MOTIFS as M
from .art_scenes2 import _dashed, _drop, _flame, _hand, _head, _rays, _snow, _sword


def _ring_dashed(r=28, w=3):
    return '<circle cx="32" cy="32" r="{}" fill="none" stroke="#FFFFFF" stroke-width="{}" stroke-dasharray="5 4"/>'.format(r, w)


def destrier_superieur():
    """Cheval ailé (pégase) au galop."""
    wing = P("M30 22 C26 8 34 0 46 0 C42 4 40 6 40 8 C46 6 50 6 54 8 C48 10 44 12 42 16 C46 16 48 18 50 20 C42 22 36 22 30 22 Z")
    return horse() + over("", wing, 5)


def assassin_imaginaire():
    """Silhouette spectrale qui surgit derrière une tête apeurée, lame levée."""
    return (_head(20, 38, 0.6) + _dashed(figure(44, 30, 1.0), "3 2", 2.2) + _sword(54, 12, 30, 0.4))


def aura_purete():
    """Silhouette dans un halo de gouttes pures."""
    return (figure(32, 34, 0.8) + "".join(_drop(32 + 24 * math.cos(a), 32 + 24 * math.sin(a), 0.16) for a in
                                          [k * math.pi / 4 for k in range(8)]))


def aura_vie():
    """Cœur au centre d'un soleil vivant, rayons alternés."""
    return place(M["coeur"](), 32, 32, 0.55) + _rays(32, 32, 20, 28, 12, 3) + _ring_dashed(30, 2)


def bannissement():
    """Silhouette aspirée vers une faille d'un autre plan."""
    rift = P("M44 4 C50 16 56 24 54 36 C52 48 46 54 44 62 C40 52 36 44 38 32 C40 22 42 14 44 4 Z") + black(
        P("M44 14 C48 22 50 28 48 36 C46 44 44 48 44 52 C42 46 40 40 42 32 C42 26 44 20 44 14 Z"))
    return rift + figure(18, 34, 0.75, 15) + S("M24 18 C30 14 34 16 38 20", 2.2) + S("M24 50 C30 54 34 52 38 48", 2.2)


def bouclier_feu():
    """Silhouette enveloppée de flammes protectrices."""
    return _flame(32, 36, 1.0) + black(figure(32, 36, 0.55))


def charme_monstre():
    """Tête de démon apaisée, cœur flottant au-dessus."""
    return place(demon(), 32, 38, 0.75) + place(M["coeur"](), 32, 8, 0.24) + star4(10, 14, 4) + star4(54, 14, 4)


def chien_garde():
    """Chien spectral assis, oreilles dressées, aboiement."""
    from .art_retouches import wolf_profile
    return _dashed(wolf_profile(28, 36, 0.8), "3 2", 2.2) + S("M52 22 C56 26 56 32 52 36", 2.6) + S("M58 18 C62 24 62 34 58 40", 2.2)


def chatiment_stupeur():
    """Épée qui frappe, étoiles d'étourdissement en cercle."""
    return _sword(30, 38, 45, 1.0) + S("M30 12 C38 4 54 4 60 12", 2.2) + star4(34, 8, 4) + star4(46, 4, 4.4) + star4(58, 10, 4)


def chatiment_debilitant():
    """Épée dégoulinante d'un poison qui affaiblit."""
    return _sword(28, 32, 45, 1.05) + _drop(46, 44, 0.22) + _drop(54, 54, 0.18) + _drop(38, 54, 0.16)


def coffre_secret():
    """Coffre qui se dissout dans un portail éthéré."""
    from .art_objets import OBJECTS
    return place(OBJECTS["objet_coffre"](), 26, 36, 0.7) + _dashed(place(OBJECTS["objet_coffre"](), 50, 20, 0.4), "2 2", 1.6) \
        + curved_arrow("M28 14 C34 6 40 6 44 10", (44, 10), 40, 2.2, 6)


def compulsion():
    """Silhouettes forcées de marcher dans une même direction."""
    return figure(14, 34, 0.6) + figure(30, 34, 0.6) + figure(46, 34, 0.6) + L([(4, 58), (52, 58)], 3) + P("M60 58 L50 52 V64 Z")


def confusion():
    """Tête dont s'échappent des spirales en tous sens."""
    return _head(28, 38, 0.7) + place(M["spirale"](), 46, 14, 0.3) + place(M["spirale"](), 18, 10, 0.22) + S("M50 32 C56 30 58 36 54 38", 2.4)


def controle_eau():
    """Mains qui écartent les eaux en deux murailles."""
    walls = P("M2 60 V20 C6 14 12 22 18 16 V60 Z") + P("M62 60 V20 C58 14 52 22 46 16 V60 Z")
    return walls + black(S("M6 30 C10 26 14 34 16 30", 1.8) + S("M48 30 C52 26 56 34 58 30", 1.8)) + _hand(32, 30, 0.45, 0) \
        + L([(22, 60), (42, 60)], 3)


def convocation_aberration():
    """Masse de tentacules surmontée d'un œil unique."""
    return place(M["tentacules"](), 32, 44, 0.75) + Cc(32, 16, 12) + black(Cc(32, 16, 6)) + Cc(32, 16, 2.6)


def convocation_artificiel():
    """Automate de métal : tête carrée, yeux ronds, engrenage."""
    body = R(16, 26, 32, 30, 4) + R(20, 6, 24, 18, 3)
    eyes = black(Cc(27, 15, 3) + Cc(37, 15, 3) + R(26, 34, 12, 4, 1))
    gear = "".join(G(R(-2, -9, 4, 4, 1), 32, 46, a) for a in range(0, 360, 45)) + Cc(32, 46, 5)
    return body + eyes + black(Cc(32, 46, 8)) + gear + R(6, 30, 8, 18, 3) + R(50, 30, 8, 18, 3)


def convocation_elementaire():
    """Silhouette faite de flamme et de pierre qui se dresse."""
    return _flame(32, 32, 1.05) + black(Cc(26, 30, 2.6) + Cc(38, 30, 2.6)) + place(M["pierres"](), 32, 54, 0.4)


def convocation_demon_majeur():
    """Grand démon ailé qui surgit d'un cercle de feu."""
    wings = P("M20 22 C10 10 2 12 2 22 C8 20 10 24 14 30 Z") + P("M44 22 C54 10 62 12 62 22 C56 20 54 24 50 30 Z")
    return wings + place(demon(), 32, 28, 0.6) + _flame(14, 56, 0.2) + _flame(32, 58, 0.24) + _flame(50, 56, 0.2)


def divination():
    """Œil dans un triangle rayonnant, étoiles."""
    tri = P("M32 4 L60 54 H4 Z") + black(P("M32 14 L52 50 H12 Z"))
    return tri + place(M["oeil"](), 32, 36, 0.44) + _rays(32, 4, 4, 8, 6, 2, 200)


def domination_bete():
    """Loup soumis, couronne de volonté au-dessus de sa tête."""
    from .art_retouches import wolf_profile
    return wolf_profile(30, 40, 0.75) + place(M["couronne"](), 30, 10, 0.3) + S("M30 18 V24", 2)


def fabrication():
    """Matériaux qui se transforment en objet fini sur une enclume."""
    anvil = P("M10 40 H48 C48 46 42 48 38 48 L40 58 H18 L20 48 C14 48 10 46 10 40 Z") + R(48, 40, 10, 4, 2)
    return anvil + place(M["marteau"](), 32, 18, 0.5) + burst(30, 36, 5, 6) + star4(54, 14, 4)


def faconnage_pierre():
    """Mains qui modèlent un bloc de pierre en arche."""
    arch = P("M6 58 V34 C6 18 18 10 32 10 C46 10 58 18 58 34 V58 H46 V34 C46 26 40 22 32 22 C24 22 18 26 18 34 V58 Z")
    return arch + black(L([(10, 44), (14, 44)], 1.8) + L([(50, 44), (54, 44)], 1.8)) + _hand(32, 46, 0.36, 0)


def fleau_elementaire():
    """Crâne entouré des quatre éléments qui le rongent."""
    return (place(M["crane"](), 32, 34, 0.55) + _flame(12, 14, 0.2) + _snow(52, 14, 0.18) + place(M["eclair"](), 12, 54, 0.2)
            + _drop(52, 54, 0.18))


def fletrissement():
    """Plante qui se dessèche et se courbe, feuilles tombées."""
    stem = S("M30 60 C30 40 34 30 48 22", 3.4)
    leaves = P("M48 22 C52 12 60 12 60 16 C56 22 52 24 48 22 Z") + P("M36 30 C34 22 38 16 42 18 C42 24 40 28 36 30 Z")
    fallen = P("M8 54 C14 48 20 52 18 58 C14 58 10 58 8 54 Z") + P("M40 56 C46 52 50 56 48 60 Z")
    return stem + leaves + fallen + L([(2, 61), (62, 61)], 2.4)


def fontaine_lune():
    """Fontaine dont l'eau reflète la lune."""
    basin = P("M8 40 H56 C56 50 46 56 32 56 C18 56 8 50 8 40 Z") + R(28, 24, 8, 16, 2)
    jets = S("M32 24 C26 14 18 18 14 26", 2.6) + S("M32 24 C38 14 46 18 50 26", 2.6)
    return basin + jets + place(M["lune"](), 32, 8, 0.24) + black(S("M14 46 H50", 1.8))


def gardien_foi():
    """Grand gardien ailé portant une épée et un bouclier."""
    return angel_wings() + _sword(50, 44, -20, 0.45) + R(14, 56, 36, 4, 2)


def gardien_nature():
    """Arbre aux branches en forme de bras qui protègent."""
    return tree() + S("M8 30 C2 22 4 14 10 12", 3.4) + S("M56 30 C62 22 60 14 54 12", 3.4)


def gouffre_gravitationnel():
    """Puits gravitationnel : cercles qui s'enfoncent, débris aspirés."""
    rings = "".join('<ellipse cx="32" cy="{}" rx="{}" ry="{}" fill="none" stroke="#FFFFFF" stroke-width="{}"/>'.format(
        30 + k * 4, 28 - k * 6, 10 - k * 2, 3.4 - k * 0.5) for k in range(4))
    return rings + Cc(32, 46, 3.4) + Cc(8, 12, 2.4) + Cc(56, 10, 2) + Cc(48, 20, 1.6)


def insecte_geant():
    """Insecte géant, mandibules ouvertes."""
    return insect() + P("M26 8 L22 2 L28 6 Z") + P("M38 8 L42 2 L36 6 Z")


def invisibilite_superieure():
    """Silhouette presque effacée, contours en éclats, en mouvement."""
    return _dashed(figure(30, 32, 1.15), "2 3", 2.4) + star4(50, 10, 6) + star4(12, 50, 5) + S("M48 40 H60", 2.4) + S("M50 48 H62", 2.4)


def invocation_ombres():
    """Créature d'ombre aux griffes qui sort d'une faille."""
    shade = P("M32 6 C44 6 50 16 50 28 C50 38 56 48 60 58 H4 C8 48 14 38 14 28 C14 16 20 6 32 6 Z")
    return shade + black(P("M22 22 L30 25 L23 27 Z") + P("M42 22 L34 25 L41 27 Z") + S("M22 38 L26 46 M32 38 V48 M42 38 L38 46", 2))


def invocation_elementaires_mineurs():
    """Quatre petites créatures élémentaires en ronde."""
    return (_flame(18, 18, 0.32) + _drop(46, 18, 0.3) + place(M["pierres"](), 18, 46, 0.36) + place(M["vent"](), 46, 46, 0.36)
            + '<circle cx="32" cy="32" r="8" fill="none" stroke="#FFFFFF" stroke-width="2"/>')


def invocation_sylvestres():
    """Dryade aux cheveux de feuilles devant un arbre."""
    hair = "".join(G(P("M0 0 C-4 -6 -2 -12 2 -12 C4 -8 4 -4 0 0 Z"), 32 + 10 * math.cos(math.radians(a)), 16 + 8 * math.sin(math.radians(a)), a + 90)
                   for a in range(180, 361, 30))
    return hair + Cc(32, 18, 8) + P("M22 28 H42 L46 60 H18 Z") + black(Cc(29, 18, 1.4) + Cc(35, 18, 1.4))


def lance_psychique():
    """Lance d'énergie mentale qui jaillit d'un cerveau."""
    return place(M["cerveau"](), 16, 46, 0.4) + P("M60 4 L26 34 L22 30 Z") + P("M60 4 L50 6 L58 14 Z") + burst(24, 32, 5, 6)


def liane_avide():
    """Liane épineuse qui s'enroule et cherche une proie."""
    vine = S("M6 60 C10 42 30 46 28 28 C26 14 40 8 50 12 C58 16 56 26 48 26", 5)
    thorns = "".join(G(P("M0 -6 L3 0 L-3 0 Z"), x, y, a) for x, y, a in ((12, 50, -40), (24, 42, 30), (28, 30, -60), (40, 12, 0), (54, 18, 70)))
    return vine + thorns + P("M48 26 C44 30 40 30 38 28 C42 24 46 24 48 26 Z")


def liberte_mouvement():
    """Silhouette qui court en brisant des entraves."""
    return figure(30, 32, 0.95, 15) + place(M["chaine_brisee"](), 52, 52, 0.3) + S("M2 40 H14", 3) + S("M4 50 H16", 3)


def localisation_creature():
    """Carte et loupe qui suivent une piste d'empreintes."""
    from .art_armes import footprint
    return (footprint(12, 54, -20, 0.5) + footprint(22, 44, 10, 0.5) + footprint(30, 34, -10, 0.5)
            + over("", place(M["loupe"](), 44, 20, 0.6), 5))


def mur_feu():
    """Muraille de flammes hautes."""
    return "".join(_flame(x, 32, 0.55 if i % 2 else 0.7) for i, x in enumerate((10, 22, 34, 46, 58))) + R(2, 56, 60, 5, 2)


def metamorphose():
    """Silhouette qui se change en bête, flèche de transformation."""
    from .art_retouches import wolf_profile
    return figure(14, 34, 0.7) + curved_arrow("M22 14 C30 6 38 8 42 14", (42, 14), 50, 2.6, 7) + wolf_profile(46, 40, 0.5)


def oeil_magique():
    """Œil volant aux ailes de lumière."""
    wing = lambda sx: '<g transform="translate(32 0) scale({} 1) translate(-32 0)">'.format(sx) + P(
        "M50 30 C54 22 60 20 64 22 C61 25 60 27 58 28 C61 28 63 30 64 32 C59 34 55 34 50 34 Z") + "</g>"
    eye = P("M12 32 C18 20 46 20 52 32 C46 44 18 44 12 32 Z") + black(Cc(32, 32, 9)) + Cc(32, 32, 6) + black(Cc(32, 32, 2.4))
    return wing(1) + wing(-1) + eye


def ombre_egarement():
    """Silhouette visible en pointillés, la vraie cachée dans l'ombre."""
    return _dashed(figure(20, 32, 1.0), "3 3", 2) + figure(46, 32, 1.0) + black(R(38, 4, 2, 56, 1))


def peau_pierre():
    """Bras couvert de plaques de pierre."""
    from .art_armes import fist
    arm = fist(32, 24, 0.9) + R(22, 34, 22, 24, 4)
    plates = black(L([(22, 42), (44, 40)], 2) + L([(22, 50), (44, 48)], 2) + L([(32, 34), (30, 58)], 2) + L([(20, 18), (40, 20)], 1.6))
    return arm + plates


def porte_dimensionnelle():
    """Deux arches reliées : on entre dans l'une, on sort de l'autre."""
    return (place(doorway(), 18, 38, 0.55) + place(doorway(), 46, 22, 0.55)
            + curved_arrow("M24 22 C28 10 34 6 40 8", (40, 8), 20, 2.6, 7))


def protection_mort():
    """Silhouette protégée par un sceau qui repousse un crâne."""
    seal = '<circle cx="24" cy="34" r="20" fill="none" stroke="#FFFFFF" stroke-width="3.4"/>'
    return seal + figure(24, 34, 0.6) + _dashed(place(M["crane"](), 52, 18, 0.34), "2 2", 1.6) + L([(42, 26), (48, 22)], 2.4)


def rayonnement_ecoeurant():
    """Lumière verdâtre qui irradie en ondes nauséeuses."""
    return Cc(32, 32, 9) + "".join(S("M32 {a} C{b} {c} {d} {e} 32 {f}".format(a=32 - r, b=32 + r * 1.2, c=32 - r * 0.6, d=32 + r * 1.2,
                                                                         e=32 + r * 0.6, f=32 + r), 2.6) for r in (16, 24)) \
        + "".join(S("M32 {a} C{b} {c} {d} {e} 32 {f}".format(a=32 - r, b=32 - r * 1.2, c=32 - r * 0.6, d=32 - r * 1.2,
                                                             e=32 + r * 0.6, f=32 + r), 2.6) for r in (16, 24))


def sanctuaire_prive():
    """Maison protégée par un dôme et des yeux barrés."""
    house = P("M14 34 L32 20 L50 34 V56 H14 Z") + black(R(28, 42, 8, 14, 1))
    dome = '<path d="M4 58 C4 30 16 8 32 8 C48 8 60 30 60 58" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="4 3"/>'
    return dome + house + L([(2, 58), (62, 58)], 3)


def scelle_portail():
    """Arche barrée par des chaînes en croix et un sceau."""
    return doorway() + over("", L([(14, 22), (50, 58)], 4) + L([(50, 22), (14, 58)], 4), 4) + Cc(32, 40, 7) + black(star4(32, 40, 4))


def sphere_aqueuse():
    """Sphère d'eau qui emprisonne une silhouette, bulles."""
    return (Cc(32, 34, 26) + black(Cc(32, 34, 21)) + figure(32, 36, 0.6) + Cc(18, 22, 2.6) + Cc(46, 26, 2) + Cc(40, 18, 1.6)
            + S("M14 44 C20 40 26 48 32 44", 2))


def sphere_tempete():
    """Boule de tempête crépitante qui lance des éclairs."""
    return (Cc(30, 34, 18) + black(Cc(30, 34, 14)) + place(M["eclair"](), 30, 34, 0.4) + L([(46, 22), (54, 12), (50, 10), (60, 2)], 3)
            + L([(14, 46), (6, 54), (10, 56), (2, 62)], 3))


def sphere_vitriol():
    """Globe d'acide qui éclate en éclaboussures corrosives."""
    return Cc(30, 30, 16) + black(Cc(34, 26, 4)) + _drop(52, 48, 0.2) + _drop(14, 52, 0.2) + _drop(48, 12, 0.16) + _drop(8, 22, 0.14)


def sphere_otiluke():
    """Bulle parfaite qui enferme une silhouette, reflet."""
    return (Cc(32, 32, 28) + black(Cc(32, 32, 24)) + figure(32, 34, 0.75)
            + S("M14 22 C18 14 26 10 34 10", 3) + Cc(42, 12, 2))


def tempete_grele():
    """Nuage d'orage d'où tombent de gros grêlons."""
    return cloud(20, 1.0) + "".join(Cc(x, y, r) for x, y, r in ((14, 44, 4), (28, 52, 4.6), (42, 44, 4), (52, 56, 3.4), (20, 60, 3)))


def tentacules_evard():
    """Forêt de tentacules noirs qui jaillissent du sol et saisissent."""
    return (S("M10 60 C6 44 16 38 12 24 C10 16 16 10 20 12", 5) + S("M30 60 C30 44 40 38 36 22 C34 14 40 8 44 10", 5)
            + S("M50 60 C54 48 60 44 58 30", 5) + R(2, 58, 60, 4, 1))


def terrain_hallucinatoire():
    """Paysage illusoire de montagnes en pointillés au-dessus du vrai sol."""
    return (_dashed(P("M2 40 L16 16 L26 28 L38 8 L62 40 Z"), "3 2", 2.4) + P("M2 52 C14 48 24 56 34 52 C44 48 54 54 62 52 V62 H2 Z")
            + star4(56, 10, 4))


SCENES = {
    "Appel de destrier supérieur": destrier_superieur, "Assassin imaginaire": assassin_imaginaire,
    "Aura de pureté": aura_purete, "Aura de vie": aura_vie, "Bannissement": bannissement, "Bouclier de feu": bouclier_feu,
    "Charme-monstre": charme_monstre, "Chien de garde de Mordenkainen": chien_garde,
    "Châtiment de stupeur": chatiment_stupeur, "Châtiment débilitant": chatiment_debilitant,
    "Coffre secret de Léomund": coffre_secret, "Compulsion": compulsion, "Confusion": confusion,
    "Contrôle de l'eau": controle_eau, "Convocation d'aberration": convocation_aberration,
    "Convocation d'artificiel": convocation_artificiel, "Convocation d'élémentaire": convocation_elementaire,
    "Convocation de démon majeur": convocation_demon_majeur, "Divination": divination,
    "Domination de bête": domination_bete, "Fabrication": fabrication, "Façonnage de la pierre": faconnage_pierre,
    "Fléau élémentaire": fleau_elementaire, "Flétrissement": fletrissement, "Fontaine de lune": fontaine_lune,
    "Gardien de la foi": gardien_foi, "Gardien de la nature": gardien_nature,
    "Gouffre gravitationnel": gouffre_gravitationnel, "Insecte géant": insecte_geant,
    "Invisibilité supérieure": invisibilite_superieure, "Invocation d'ombres": invocation_ombres,
    "Invocation d'élémentaires mineurs": invocation_elementaires_mineurs,
    "Invocation d'êtres sylvestres": invocation_sylvestres, "Lance d'arçon psychique de Raulothim": lance_psychique,
    "Liane avide": liane_avide, "Liberté de mouvement": liberte_mouvement,
    "Localisation de créature": localisation_creature, "Mur de feu": mur_feu, "Métamorphose": metamorphose,
    "Oeil magique": oeil_magique, "Œil magique": lambda: place(oeil_magique(), 32, 32, 0.9) + star4(56, 56, 4),
    "Ombre d'égarement": ombre_egarement, "Peau de pierre": peau_pierre, "Porte dimensionnelle": porte_dimensionnelle,
    "Protection contre la mort": protection_mort, "Rayonnement écoeurant": rayonnement_ecoeurant,
    "Sanctuaire privé de Mordenkainen": sanctuaire_prive, "Scellé de portail": scelle_portail,
    "Sphère aqueuse": sphere_aqueuse, "Sphère de tempête": sphere_tempete, "Sphère de vitriol": sphere_vitriol,
    "Sphère résiliente d'Otiluke": sphere_otiluke, "Tempête de grêle": tempete_grele,
    "Tentacules noirs d'Evard": tentacules_evard, "Terrain hallucinatoire": terrain_hallucinatoire,
}
