"""
Dessins soignés (v53) des sorts de niveau 4 et 5 — compositions choisies à la main à partir des éléments de
core/art_kit et des motifs de core/art_motifs (un dessin distinct par sort).
"""
from __future__ import annotations

from .art_armes import Cc, K, L, P, R, S, burst, curved_arrow, over, star4
from .art_kit import (angel_wings, arrows_volley, black, book_closed, cloud, coffin, column_fire,
                      bird, contract, corner, crowd, demon, doorway, dragon_head, duo, figure, ghost_figure, giant_hand,
                      hand_up, head_profile, horse, hut, inside, insect, mind_link, mirror, place, quiver, ring,
                      scales, snow_cone, sphere, sunburst, tornado, tree, wall)
from .art_motifs import MOTIFS as M


def _m(name):
    return M[name]()


def _shield_aura(inner):
    return ring(inside(_m("bouclier"), inner, 0.5), False, 0.7)


LEVEL4 = {
    "Appel de destrier supérieur": lambda: corner(horse(), _m("aile"), 0.42),
    "Assassin imaginaire": lambda: duo(ghost_figure(32, 32, 1.1), _m("crane"), 0.5),
    "Aura de pureté": lambda: ring(inside(_m("goutte"), _m("eclat"), 0.45)),
    "Aura de vie": lambda: ring(_m("coeur"), True),
    "Bannissement": lambda: duo(doorway(), figure(32, 32, 1.0), 0.42),
    "Bouclier de feu": lambda: duo(_m("bouclier"), _m("flamme"), 0.5),
    "Charme-monstre": lambda: duo(demon(), _m("coeur"), 0.42),
    "Chien de garde de Mordenkainen": lambda: corner(M["bete"](), _m("alerte"), 0.36),
    "Châtiment de stupeur": lambda: duo(_m("epee"), _m("spirale"), 0.46),
    "Châtiment débilitant": lambda: duo(_m("epee"), _m("goutte"), 0.44),
    "Coffre secret de Léomund": lambda: corner(__import__("core.art_objets", fromlist=["x"]).OBJECTS["objet_coffre"](), _m("portail"), 0.36),
    "Compulsion": lambda: duo(crowd(), _m("spirale"), 0.42),
    "Confusion": lambda: ring(_m("spirale")) + star4(56, 8, 4),
    "Contrôle de l'eau": lambda: duo(_m("vague"), hand_up(32, 34, 1.0), 0.44),
    "Convocation d'aberration": lambda: corner(_m("tentacules"), _m("oeil"), 0.4),
    "Convocation d'artificiel": lambda: corner(_m("casque"), _m("outil"), 0.4),
    "Convocation d'élémentaire": lambda: duo(tornado(), _m("flamme"), 0.42),
    "Convocation de démon majeur": lambda: corner(demon(), _m("portail"), 0.36),
    "Divination": lambda: duo(_m("oeil"), _m("etoile"), 0.42),
    "Domination de bête": lambda: duo(M["bete"](), _m("chaine"), 0.42),
    "Fabrication": lambda: duo(_m("outil"), _m("eclat"), 0.44),
    "Façonnage de la pierre": lambda: duo(_m("pierres"), hand_up(32, 34, 1.0), 0.44),
    "Fléau élémentaire": lambda: duo(_m("crane"), _m("flamme"), 0.42),
    "Flétrissement": lambda: duo(_m("feuille"), _m("crane"), 0.44),
    "Fontaine de lune": lambda: duo(_m("lune"), _m("goutte"), 0.4),
    "Gardien de la foi": lambda: angel_wings() + R(14, 56, 36, 4, 2),
    "Gardien de la nature": lambda: duo(tree(), _m("bouclier"), 0.42),
    "Gouffre gravitationnel": lambda: ring(place(_m("spirale"), 32, 32, 0.9), True) + star4(54, 54, 4),
    "Insecte géant": lambda: insect(),
    "Invisibilité supérieure": lambda: ghost_figure(32, 32, 1.15) + star4(52, 10, 6) + star4(12, 52, 5),
    "Invocation d'ombres": lambda: duo(ghost_figure(32, 32, 1.0), _m("lune"), 0.42),
    "Invocation d'élémentaires mineurs": lambda: place(_m("flamme"), 18, 20, 0.45) + place(_m("goutte"), 46, 20, 0.45)
                                                 + place(_m("pierres"), 18, 48, 0.45) + place(_m("vent"), 46, 48, 0.45),
    "Invocation d'êtres sylvestres": lambda: duo(tree(), _m("eclat"), 0.4),
    "Lance d'arçon psychique de Raulothim": lambda: duo(_m("lance"), _m("cerveau"), 0.44),
    "Liane avide": lambda: S("M8 60 C10 40 30 44 28 26 C26 14 38 8 48 12", 5.4) + P("M44 6 L58 10 L48 18 Z")
                           + P("M22 40 C28 34 32 36 34 40 C28 42 24 42 22 40 Z") + P("M30 22 C24 18 18 20 16 24 C22 26 26 26 30 22 Z"),
    "Liberté de mouvement": lambda: _m("chaine_brisee"),
    "Localisation de créature": lambda: duo(_m("loupe"), M["bete"](), 0.42),
    "Mur de feu": lambda: wall("feu"),
    "Métamorphose": lambda: duo(_m("cycle"), M["bete"](), 0.42),
    "Oeil magique": lambda: _m("oeil") + star4(52, 10, 6) + star4(12, 54, 4),
    "Œil magique": lambda: corner(_m("oeil"), _m("aile"), 0.4),
    "Ombre d'égarement": lambda: duo(figure(32, 32, 1.0), _m("brume"), 0.46),
    "Peau de pierre": lambda: duo(figure(32, 32, 1.1), _m("pierres"), 0.46),
    "Porte dimensionnelle": lambda: doorway() + curved_arrow("M6 50 C2 30 8 12 20 8", (20, 8), -20, 3),
    "Protection contre la mort": lambda: duo(_m("crane"), _m("bouclier"), 0.44),
    "Rayonnement écoeurant": lambda: ring(_m("soleil")).replace('stroke-width="3.6"', 'stroke-width="3.6" stroke-dasharray="2 4"'),
    "Sanctuaire privé de Mordenkainen": lambda: duo(hut(), _m("bouclier"), 0.42),
    "Scellé de portail": lambda: duo(doorway(), _m("chaine"), 0.44),
    "Sphère aqueuse": lambda: sphere(_m("vague"), 0.5),
    "Sphère de tempête": lambda: over(sphere(), place(_m("eclair"), 32, 32, 0.95), 6),
    "Sphère de vitriol": lambda: sphere(_m("goutte"), 0.46),
    "Sphère résiliente d'Otiluke": lambda: sphere(figure(32, 32, 1.0), 0.5),
    "Tempête de grêle": lambda: cloud(20, 0.9) + "".join(Cc(x, y, 3.4) for x, y in ((16, 44), (28, 52), (40, 44), (50, 54), (22, 60))),
    "Tentacules noirs d'Evard": lambda: _m("tentacules") + R(2, 58, 60, 4, 1),
    "Terrain hallucinatoire": lambda: duo(_m("terre"), _m("masque"), 0.42),
}

LEVEL5 = {
    "Amélioration de compétences": lambda: duo(figure(32, 32, 1.1), _m("fleche_haut"), 0.44),
    "Animation d'objets": lambda: duo(book_closed(), _m("eclat"), 0.44),
    "Apparence trompeuse": lambda: crowd() + black(place(_m("masque"), 32, 28, 0.36)),
    "Arme sacrée": lambda: duo(_m("epee"), _m("soleil"), 0.44),
    "Assignation infernale": lambda: duo(contract(), demon(), 0.42),
    "Aube": lambda: sunburst() + L([(2, 58), (62, 58)], 3),
    "Brume mortelle": lambda: duo(cloud(30, 1.0), _m("crane"), 0.42),
    "Carquois magique": lambda: quiver() + star4(54, 52, 5),
    "Cercle de pouvoir": lambda: ring(_m("couronne")),
    "Cercle de téléportation": lambda: ring(_m("portail"), True),
    "Châtiment du ban": lambda: duo(_m("epee"), doorway(), 0.42),
    "Colonne de flamme": lambda: column_fire(),
    "Communion": lambda: duo(_m("soleil"), hand_up(32, 34, 1.0), 0.42),
    "Communion avec la nature": lambda: duo(tree(), _m("oeil"), 0.4),
    "Contact avec un autre plan": lambda: duo(_m("portail"), head_profile(), 0.42),
    "Contagion": lambda: duo(figure(32, 32, 1.0), _m("fiole"), 0.42),
    "Contrat": lambda: contract(),
    "Contrôle des vents": lambda: duo(_m("vent"), hand_up(32, 34, 1.0), 0.42),
    "Convocation d'esprit draconique": lambda: corner(dragon_head(), _m("eclat"), 0.36),
    "Convocation de céleste": lambda: angel_wings(),
    "Convocation de dragon": lambda: dragon_head(),
    "Coquille antivie": lambda: sphere(M["bete"](), 0.46),
    "Création": lambda: duo(_m("pierres"), _m("eclat"), 0.44),
    "Cône de froid": lambda: snow_cone(),
    "Danse macabre": lambda: duo(_m("crane"), _m("note"), 0.42),
    "Dissipation du mal et du bien": lambda: duo(_m("soleil"), demon(), 0.44),
    "Domination de personne": lambda: duo(figure(32, 32, 1.1), _m("chaine"), 0.44),
    "Double illusoire": lambda: figure(22, 32, 1.0) + ghost_figure(44, 32, 1.0),
    "Décalage temporel": lambda: duo(_m("sablier"), _m("cycle"), 0.44),
    "Déluge d'énergie négative": lambda: ring(_m("crane")).replace('stroke-width="3.6"', 'stroke-width="5"'),
    "Fléau d'insectes": lambda: place(insect(), 20, 22, 0.45) + place(insect(), 44, 18, 0.38) + place(insect(), 34, 44, 0.5)
                                 + place(insect(), 12, 48, 0.32) + place(insect(), 54, 46, 0.3),
    "Foulée dimensionnelle": lambda: figure(16, 34, 0.75) + place(_m("portail"), 46, 32, 0.6),
    "Frappe du vent d'acier": lambda: duo(_m("epee"), _m("vent"), 0.46),
    "Fureur de la nature": lambda: duo(tree(), _m("eclair"), 0.42),
    "Immobilisation de monstre": lambda: over(place(demon(), 32, 28, 0.85), place(_m("chaine"), 32, 50, 0.42), 7),
    "Immolation": lambda: duo(figure(32, 32, 1.0), _m("flamme"), 0.5),
    "Invocation d'élémentaire": lambda: tornado() + place(_m("eclat"), 52, 10, 0.25),
    "Invocation de volée": lambda: arrows_volley(),
    "Lien télépathique de Rary": lambda: mind_link(),
    "Maelström": lambda: ring(place(_m("vague"), 32, 32, 0.8)) + place(_m("spirale"), 32, 32, 0.4),
    "Main de Bigby": lambda: giant_hand(),
    "Modification de mémoire": lambda: duo(head_profile(), _m("cycle"), 0.42),
    "Mur de force": lambda: wall("force"),
    "Mur de lumière": lambda: wall("lumiere"),
    "Mur de pierre": lambda: wall("pierre"),
    "Mythes et légendes": lambda: duo(book_closed(), _m("etoile"), 0.42),
    "Passage par les arbres": lambda: tree() + curved_arrow("M4 58 C2 42 6 30 14 24", (14, 24), -40, 3),
    "Passe-muraille": lambda: wall("pierre") + over("", place(doorway(), 32, 38, 0.6), 6),
    "Perturbations synaptiques": lambda: duo(_m("cerveau"), _m("explosion"), 0.42),
    "Présence royale de Yolane": lambda: duo(_m("couronne"), _m("soleil"), 0.42),
    "Quête": lambda: duo(scales(), _m("parchemin"), 0.4),
    "Rappel à la vie": lambda: duo(coffin(), _m("coeur"), 0.44),
    "Restauration supérieure": lambda: duo(_m("coeur"), _m("etoile"), 0.42),
    "Réincarnation": lambda: duo(figure(32, 32, 1.0), _m("cycle"), 0.44),
    "Sanctification": lambda: duo(_m("soleil"), _m("terre"), 0.42),
    "Scrutation": lambda: mirror() + black(place(_m("oeil"), 32, 26, 0.36)),
    "Soins de groupe": lambda: crowd() + over("", place(_m("soin"), 50, 14, 0.34), 6),
    "Songe": lambda: duo(head_profile(), _m("lune"), 0.44),
    "Tempête radieuse de Jallarzi": lambda: _radiant_storm(),
    "Transmutation de la pierre": lambda: duo(_m("pierres"), _m("cycle"), 0.44),
    "Télékinésie": lambda: hand_up(24, 40, 0.8) + place(_m("pierres"), 46, 18, 0.45) + S("M30 20 C34 14 36 14 38 16", 2.4),
    "Vague destructrice": lambda: duo(_m("ondes"), _m("soleil"), 0.42),
    "Énervation": lambda: duo(figure(32, 32, 1.0), _m("crane"), 0.42),
    "Éveil": lambda: duo(tree(), figure(32, 32, 1.0), 0.4) + star4(10, 10, 4),
}


# ------------------------------------------------------------------------------------------------ niveaux 1 à 3
def _obj(name):
    from .art_objets import OBJECTS
    return OBJECTS[name]()


LOW = {
    # niveau 1
    "Barbes argentées": lambda: duo(_m("crane"), _m("lune"), 0.42),
    "Châtiment divin": lambda: duo(_m("epee"), _m("soleil"), 0.5) + star4(10, 54, 4),
    "Création ou destruction d'eau": lambda: duo(_m("goutte"), _m("cycle"), 0.44),
    "Cérémonie": lambda: duo(_m("soleil"), _m("anneau"), 0.42),
    "Disque flottant de Tenser": lambda: '<ellipse cx="32" cy="44" rx="26" ry="8" fill="#FFFFFF"/>'
                                         '<ellipse cx="32" cy="42" rx="18" ry="4" fill="#000000"/>' + place(_obj("objet_coffre"), 32, 22, 0.5)
                                         + L([(16, 54), (16, 60)], 2.4) + L([(32, 54), (32, 62)], 2.4) + L([(48, 54), (48, 60)], 2.4),
    "Don d'alacrité": lambda: duo(_m("sablier"), _m("eclair"), 0.44),
    "Détection du poison et des maladies": lambda: duo(_m("loupe"), _m("fiole"), 0.42),
    "Frappe du zéphyr": lambda: duo(_m("vent"), _m("epee"), 0.46),
    "Gravité amplifiée": lambda: duo(_m("pierres"), _m("fleche_haut"), 0.4).replace('translate(47 47)', 'translate(47 47) rotate(180)'),
    "Injonction": lambda: duo(_m("bulle"), _m("alerte"), 0.4),
    "Lien avec une bête": lambda: corner(M["bete"](), _m("chaine"), 0.4),
    "Maléfice": lambda: duo(_m("crane"), _m("oeil"), 0.44),
    "Mixture caustique de Tasha": lambda: duo(_m("fiole"), _m("goutte"), 0.4),
    "Projectile magique de Jim": lambda: duo(_m("meteores"), _m("etoile"), 0.4),
    "Projectile élémentaire": lambda: duo(_m("meteores"), _m("flamme"), 0.42),
    "Purification de nourriture et d'eau": lambda: duo(_obj("objet_ration"), _m("eclat"), 0.42),
    "Représailles infernales": lambda: duo(demon(), _m("flamme"), 0.44),
    "Secousse sismique": lambda: _m("terre"),
    "Serviteur invisible": lambda: ghost_figure(32, 32, 1.1) + place(_m("outil"), 50, 50, 0.3),
    "Simulacre de vie": lambda: duo(_m("coeur"), _m("crane"), 0.44),
    "Tentacules de Hadar": lambda: duo(_m("tentacules"), _m("lune"), 0.38),
    "Texte illusoire": lambda: duo(_m("parchemin"), _m("masque"), 0.42),
    "Trait ensorcelé": lambda: duo(_m("eclair"), _m("chaine"), 0.42),
    "Valeur déformée": lambda: duo(_m("gemme"), _m("masque"), 0.42),
    "Vents contraires": lambda: place(_m("vent"), 32, 20, 0.6) + '<g transform="translate(64 0) scale(-1 1)">' + place(_m("vent"), 32, 46, 0.6) + "</g>",
    "Éclair de chaos": lambda: duo(_m("eclair"), _m("spirale"), 0.42),
    "Éclair traçant": lambda: duo(_m("eclair"), _m("cible"), 0.42),
    # niveau 2
    "Agrandissement/Rapetissement": lambda: figure(18, 38, 0.65) + figure(44, 32, 1.05) + L([(30, 8), (30, 56)], 1.6),
    "Apaisement des émotions": lambda: duo(head_profile(), _m("goutte"), 0.4),
    "Appel de destrier": lambda: horse(),
    "Arme magique": lambda: duo(_m("epee"), _m("eclat"), 0.44),
    "Attraction terrestre": lambda: duo(_m("terre"), _m("chaine"), 0.42),
    "Aura magique de Nystul": lambda: ring(_m("masque"), True),
    "Bouche magique": lambda: duo(_m("bulle"), _m("eclat"), 0.42),
    "Bourrasque": lambda: _m("vent") + S("M52 44 C58 40 58 32 52 30", 3),
    "Châtiment de révélation": lambda: duo(_m("epee"), _m("oeil"), 0.44),
    "Châtiment révélateur": lambda: duo(_m("epee"), _m("ampoule"), 0.44),
    "Connaissance empruntée": lambda: duo(book_closed(), head_profile(), 0.42),
    "Convocation de bête": lambda: corner(M["bete"](), _m("portail"), 0.36),
    "Corde enchantée": lambda: duo(_obj("objet_corde"), _m("eclat"), 0.4),
    "Cordon de flèches": lambda: arrows_volley() + L([(2, 62), (62, 62)], 2),
    "Couronne du dément": lambda: duo(_m("couronne"), _m("spirale"), 0.42),
    "Cécité/Surdité": lambda: duo(_m("oeil_clos"), _m("ondes"), 0.4),
    "Discours captivant": lambda: duo(crowd(), _m("note"), 0.42),
    "Distorsion de vortex": lambda: duo(_m("spirale"), figure(32, 32, 1.0), 0.42),
    "Don de la parole": lambda: duo(_m("bulle"), M["bete"](), 0.4),
    "Déblocage": lambda: duo(_obj("objet_cle"), _m("eclat"), 0.42),
    "Entraves de givre": lambda: duo(_m("chaine"), _m("flocon"), 0.44),
    "Escapade cinétique": lambda: duo(_m("botte"), _m("eclair"), 0.42),
    "Espièglerie de Nathair": lambda: duo(_m("masque"), _m("eclat"), 0.42),
    "Esprit guérisseur": lambda: duo(ghost_figure(32, 32, 1.0), _m("soin"), 0.42),
    "Faveur de la fortune": lambda: duo(_m("etoile"), _m("cycle"), 0.42),
    "Flambée d'Aganazzar": lambda: duo(_m("flamme"), _m("fleche"), 0.4),
    "Flamme éternelle": lambda: ring(_m("flamme")),
    "Flétrissement et floraison": lambda: duo(_m("feuille"), _m("cycle"), 0.42),
    "Force fantasmagorique": lambda: duo(demon(), _m("masque"), 0.42),
    "Fouet mental de Tasha": lambda: duo(_m("cerveau"), _m("eclair"), 0.42),
    "Glace entravante de Rime": lambda: duo(_m("flocon"), _m("botte"), 0.42),
    "Lame d'ombres": lambda: duo(_m("dague"), _m("lune"), 0.42),
    "Libellé aérien": lambda: duo(_m("parchemin"), _m("aile"), 0.4),
    "Lien de protection": lambda: duo(_m("bouclier"), _m("chaine"), 0.42),
    "Localisation d'animaux ou de plantes": lambda: duo(_m("loupe"), _m("feuille"), 0.42),
    "Localisation d'objet": lambda: duo(_m("loupe"), _m("anneau"), 0.42),
    "Messager animal": lambda: duo(bird(), _m("parchemin"), 0.4),
    "Modification d'apparence": lambda: duo(figure(32, 32, 1.0), _m("masque"), 0.42),
    "Métal brûlant": lambda: duo(_m("armure"), _m("flamme"), 0.44),
    "Nuée de boules de neige de Snilloc": lambda: place(_m("flocon"), 18, 18, 0.4) + Cc(42, 22, 8) + Cc(24, 44, 9) + Cc(48, 48, 7),
    "Nuée de dagues": lambda: "".join(place(_m("dague"), x, y, 0.42) for x, y in ((18, 18), (46, 16), (20, 46), (48, 46), (32, 32))),
    "Objet immobile": lambda: duo(_obj("objet_coffre"), _m("chaine"), 0.42),
    "Passage sans trace": lambda: duo(_m("brume"), _m("botte"), 0.4),
    "Pattes d'araignée": lambda: duo(_m("toile"), figure(32, 32, 1.0), 0.42),
    "Pièce lumineuse de Jim": lambda: Cc(32, 32, 18) + Cc(32, 32, 13, K) + star4(32, 32, 7) + "".join(
        L([(32 + 23 * c, 32 + 23 * s_), (32 + 29 * c, 32 + 29 * s_)], 3) for c, s_ in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7))),
    "Poche de poignet": lambda: duo(_m("main"), _m("portail"), 0.38),
    "Poigne terreuse de Maximilien": lambda: duo(_m("terre"), _m("main"), 0.44),
    "Prière de guérison": lambda: crowd() + over("", place(_m("soin"), 50, 12, 0.3), 6),
    "Protection contre le poison": lambda: duo(_m("fiole"), _m("bouclier"), 0.44),
    "Préservation des morts": lambda: duo(coffin(), _m("sablier"), 0.42),
    "Pyrotechnie": lambda: place(burst(32, 32, 20, 8), 20, 22, 0.6) + place(burst(32, 32, 20, 8), 46, 30, 0.5)
                           + place(_m("flamme"), 30, 48, 0.36),
    "Rayon affaiblissant": lambda: duo(_m("eclair"), _m("poing"), 0.4),
    "Rayon de lune": lambda: place(_m("lune"), 20, 16, 0.42) + P("M22 22 L42 22 L58 62 H6 Z") + P("M26 28 H38 L50 58 H14 Z", K),
    "Sens animal": lambda: duo(M["bete"](), _m("oeil"), 0.42),
    "Sens de la distorsion": lambda: duo(_m("oeil"), _m("spirale"), 0.42),
    "Sens des pièges": lambda: duo(_m("oeil"), _m("alerte"), 0.4),
    "Souffle du dragon": lambda: _m("souffle"),
    "Tourbillon de poussière": lambda: duo(tornado(), _m("pierres"), 0.38),
    "Vent protecteur": lambda: duo(_m("vent"), _m("bouclier"), 0.42),
    "Verrou magique": lambda: duo(doorway(), _obj("objet_cle"), 0.42),
    "Vigueur arcanique": lambda: corner(_m("coeur"), _m("eclat"), 0.42),
    "Voir l'invisible": lambda: duo(_m("oeil"), ghost_figure(32, 32, 1.0), 0.42),
    "Zone de vérité": lambda: ring(scales(), False, 0.6),
    "Épine mentale": lambda: duo(_m("cerveau"), _m("dague"), 0.44),
    # niveau 3
    "Amitié instantanée": lambda: duo(crowd(), _m("coeur"), 0.4),
    "Antidétection": lambda: duo(_m("oeil_clos"), _m("bouclier"), 0.42),
    "Aura de vitalité": lambda: ring(_m("soin"), True),
    "Châtiment aveuglant": lambda: duo(_m("epee"), _m("oeil_clos"), 0.44),
    "Clairvoyance": lambda: corner(_m("oeil"), doorway(), 0.36),
    "Communication avec les plantes": lambda: duo(_m("feuille"), _m("bulle"), 0.42),
    "Convocation de démons mineurs": lambda: place(demon(), 20, 22, 0.42) + place(demon(), 44, 22, 0.42) + place(demon(), 32, 46, 0.42),
    "Convocation de fée": lambda: corner(figure(32, 32, 1.0), _m("aile"), 0.42),
    "Convocation de mort-vivant": lambda: corner(_m("crane"), _m("portail"), 0.36),
    "Convocation de rejeton d'ombre": lambda: corner(ghost_figure(32, 32, 1.0), _m("lune"), 0.4),
    "Création de nourriture et d'eau": lambda: place(_obj("objet_ration"), 24, 36, 0.6) + place(_obj("objet_gourde"), 48, 30, 0.5),
    "Discours motivant": lambda: duo(_m("bulle"), _m("coeur"), 0.42),
    "Délivrance des malédictions": lambda: duo(_m("chaine_brisee"), _m("crane"), 0.4),
    "Ennemis à foison": lambda: duo(crowd(), _m("masque"), 0.4),
    "Flèches enflammées": lambda: duo(quiver(), _m("flamme"), 0.42),
    "Forme gazeuse": lambda: duo(_m("brume"), figure(32, 32, 1.0), 0.42),
    "Forteresse d'intellect": lambda: duo(_m("cerveau"), _m("bouclier"), 0.44),
    "Foulée d'Ashardalon": lambda: duo(_m("botte"), _m("flamme"), 0.44),
    "Foulée tonitruante": lambda: duo(_m("botte"), _m("ondes"), 0.42),
    "Image majeure": lambda: duo(dragon_head(), _m("masque"), 0.38),
    "Inciter à la cupidité": lambda: duo(_m("gemme"), _m("chaine"), 0.42),
    "Invocation d'animaux": lambda: place(M["bete"](), 20, 24, 0.5) + place(M["bete"](), 46, 40, 0.5),
    "Invocation de projectiles": lambda: duo(arrows_volley(), _m("eclat"), 0.38),
    "Marche sur l'eau": lambda: duo(_m("vague"), _m("botte"), 0.42),
    "Minuscules météores de Melf": lambda: _m("meteores") + star4(10, 10, 4) + star4(54, 54, 3),
    "Monture fantôme": lambda: horse().replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2.4"') + star4(54, 8, 4),
    "Mort simulée": lambda: duo(coffin(), _m("masque"), 0.42),
    "Mur d'eau": lambda: wall("eau"),
    "Mur de sable": lambda: wall("sable"),
    "Mur de vent": lambda: wall("vent"),
    "Onde pulsée": lambda: _m("ondes") + star4(54, 10, 4),
    "Petite hutte de Léomund": lambda: hut(),
    "Protection contre une énergie": lambda: duo(_m("eclair"), _m("bouclier"), 0.44),
    "Raz-de-marée": lambda: _m("vague") + R(2, 58, 60, 4, 1),
    "Serviteur miniature": lambda: duo(_m("outil"), figure(32, 32, 1.0), 0.4),
    "Sieste": lambda: duo(_m("lune"), figure(32, 32, 1.0), 0.4),
    "Transfert de vie": lambda: duo(_m("coeur"), _m("fleche"), 0.42),
    "Voile spirituel": lambda: duo(ghost_figure(32, 32, 1.0), _m("eclat"), 0.42),
    "Voracité de Hadar": lambda: ring(_m("lune")).replace('stroke-width="3.6"', 'stroke-width="5"'),
    "Éruption de terre": lambda: spikes_ground_k(),
}


def spikes_ground_k():
    from .art_kit import spikes_ground
    return spikes_ground() + place(_m("pierres"), 32, 18, 0.32)


# ------------------------------------------------------------------------------------------------ niveaux 6 à 9
def _prism():
    return (P("M32 6 L56 50 H8 Z") + P("M32 18 L46 44 H18 Z", K) + L([(40, 28), (62, 18)], 3) + L([(44, 36), (62, 32)], 3)
            + L([(46, 44), (62, 48)], 3) + L([(2, 34), (24, 34)], 3))


def _star_dark():
    return Cc(32, 32, 24) + Cc(32, 32, 18, K) + burst(32, 32, 30, 12).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2"')


def _stopwatch():
    return (Cc(32, 36, 24) + Cc(32, 36, 19, K) + R(28, 4, 8, 8, 2) + L([(32, 36), (32, 22)], 3.4) + L([(32, 36), (42, 40)], 3.4)
            + Cc(32, 36, 3))


HIGH = {
    # niveau 6
    "Allié planaire": lambda: corner(angel_wings(), _m("portail"), 0.34),
    "Barrière de lames": lambda: "".join(place(_m("epee"), x, 32, 0.42) for x in (12, 26, 40, 54)) + R(2, 56, 60, 4, 1),
    "Bosquet des druides": lambda: place(tree(), 20, 30, 0.6) + place(tree(), 44, 30, 0.6) + R(2, 56, 60, 4, 1),
    "Bouclier de platine de Fizban": lambda: duo(_m("bouclier"), dragon_head(), 0.42),
    "Cage des âmes": lambda: R(10, 6, 44, 5, 2) + R(10, 56, 44, 5, 2) + "".join(L([(x, 10), (x, 56)], 3) for x in (14, 24, 40, 50))
                             + ghost_figure(32, 34, 0.8),
    "Cercle de mort": lambda: ring(_m("crane"), True).replace('stroke-width="3.6"', 'stroke-width="4.4"'),
    "Chaudron bouillonnant de Tasha": lambda: P("M8 26 H56 C56 48 46 58 32 58 C18 58 8 48 8 26 Z") + R(4, 22, 56, 6, 3)
                                              + Cc(22, 16, 4) + Cc(34, 10, 5) + Cc(44, 16, 3.4) + R(14, 56, 6, 6, 1) + R(44, 56, 6, 6, 1),
    "Chaîne d'éclairs": lambda: place(_m("eclair"), 14, 24, 0.4) + place(_m("eclair"), 32, 40, 0.4) + place(_m("eclair"), 50, 24, 0.4)
                                + L([(18, 32), (28, 36)], 2.4) + L([(36, 36), (46, 32)], 2.4),
    "Contamination": lambda: duo(figure(32, 32, 1.0), _m("goutte"), 0.4) + star4(10, 10, 3),
    "Convocation de fiélon": lambda: duo(demon(), _m("flamme"), 0.42) + star4(54, 8, 4),
    "Convocations instantanées de Drawmij": lambda: duo(_m("gemme"), _m("portail"), 0.4),
    "Costume d'Outremonde de Tasha": lambda: duo(_m("tentacules"), figure(32, 32, 1.0), 0.42),
    "Création d'homoncule": lambda: duo(_m("fiole"), M["bete"](), 0.4),
    "Création de mort-vivant": lambda: duo(_m("crane"), _m("eclat"), 0.42),
    "Danse irrésistible d'Otto": lambda: duo(G_dance(), _m("note"), 0.42),
    "Dispersion": lambda: crowd() + L([(4, 8), (16, 20)], 3) + L([(60, 8), (48, 20)], 3) + star4(32, 6, 5),
    "Désintégration": lambda: duo(figure(32, 32, 1.0), _m("explosion"), 0.42) + star4(54, 10, 4),
    "Festin des héros": lambda: duo(_obj("objet_ration"), _m("coeur"), 0.42),
    "Fissure gravitationnelle": lambda: duo(_m("terre"), _m("spirale"), 0.42),
    "Globe d'invulnérabilité": lambda: sphere(_m("bouclier"), 0.5),
    "Guérison": lambda: _m("soin") + star4(54, 8, 5) + star4(8, 10, 4),
    "Illusion programmée": lambda: duo(_m("masque"), _m("sablier"), 0.42),
    "Interdiction": lambda: duo(doorway(), _m("alerte"), 0.4),
    "Invocation de fée": lambda: corner(_m("aile"), _m("etoile"), 0.4),
    "Marche sur le vent": lambda: duo(_m("vent"), figure(32, 32, 1.0), 0.42),
    "Mauvais oeil": lambda: duo(_m("oeil"), _m("crane"), 0.42),
    "Mauvais œil": lambda: duo(_m("oeil"), demon(), 0.44),
    "Mot de retour": lambda: duo(_m("bulle"), _m("retour"), 0.4),
    "Mur d'épines": lambda: R(2, 46, 60, 12, 2) + "".join(P("M{} 46 L{} 18 L{} 46 Z".format(x - 4, x, x + 4)) for x in (8, 20, 32, 44, 56)),
    "Mur de glace": lambda: R(4, 18, 56, 40, 3) + "".join(L([(x, 22), (x + 8, 54)], 2, K) for x in (10, 26, 42)) + place(_m("flocon"), 52, 10, 0.24),
    "Ossements de la Terre": lambda: duo(_m("terre"), _m("crane"), 0.42),
    "Portail magique": lambda: place(_m("portail"), 18, 32, 0.6) + place(_m("portail"), 46, 32, 0.6),
    "Prison mentale": lambda: inside(R(8, 8, 48, 48, 4), _m("cerveau"), 0.5) + R(16, 8, 4, 48, 0, K) + R(44, 8, 4, 48, 0, K),
    "Protection primordiale": lambda: place(_m("flamme"), 18, 18, 0.42) + place(_m("flocon"), 46, 18, 0.42) + place(_m("eclair"), 18, 46, 0.42) + place(_m("goutte"), 46, 46, 0.42),
    "Protections et sceaux": lambda: duo(doorway(), _m("rune"), 0.42),
    "Préméditation": lambda: duo(head_profile(), _m("sablier"), 0.42),
    "Prévoyance": lambda: duo(_m("oeil"), _m("sablier"), 0.42),
    "Pétrification": lambda: __import__("core.art_etats", fromlist=["x"]).CONDITIONS["petrifie"](),
    "Rayon de soleil": lambda: L([(6, 58), (44, 20)], 8) + place(_m("soleil"), 46, 18, 0.5),
    "Sacre de la glace": lambda: ring(_m("flocon")),
    "Sacre de la pierre": lambda: ring(_m("pierres")),
    "Sacre des flammes": lambda: ring(_m("flamme"), True),
    "Sacre du vent": lambda: ring(_m("vent")),
    "Sens de l'orientation": lambda: Cc(32, 32, 26) + Cc(32, 32, 20, K) + P("M32 12 L38 32 L32 52 L26 32 Z") + P("M32 34 L37 34 L32 50 L27 34 Z", K),
    "Sphère glaciale d'Otiluke": lambda: sphere(_m("flocon"), 0.5),
    "Suggestion de groupe": lambda: duo(crowd(), _m("bulle"), 0.4),
    "Terraformage": lambda: duo(_m("terre"), _m("cycle"), 0.42),
    "Transformation de Tenser": lambda: duo(figure(32, 32, 1.0), _m("epee"), 0.46),
    "Urne magique": lambda: P("M22 4 H42 V10 C52 16 54 30 50 42 C48 52 42 58 32 58 C22 58 16 52 14 42 C10 30 12 16 22 10 Z")
                            + black(place(ghost_figure(32, 32, 1.0), 32, 36, 0.5)),
    "Vision suprême": lambda: _m("oeil") + "".join(L([(32 + 28 * c, 32 + 28 * s_), (32 + 31 * c, 32 + 31 * s_)], 3)
                                                   for c, s_ in ((0, -1), (0.7, -0.7), (-0.7, -0.7))),
    "Voie végétale": lambda: duo(tree(), _m("portail"), 0.38),
    # niveau 7
    "Boule de feu à retardement": lambda: duo(burst(32, 32, 28, 10), _m("sablier"), 0.42),
    "Cage de force": lambda: R(8, 6, 48, 5, 2) + R(8, 54, 48, 5, 2) + "".join(L([(x, 8), (x, 56)], 3.4) for x in (12, 22, 32, 42, 52)),
    "Changement de plan": lambda: duo(_m("portail"), _m("etoile"), 0.42),
    "Couronne d'étoiles": lambda: "".join(place(_m("etoile"), 32 + 22 * c, 32 + 22 * s_, 0.28)
                                          for c, s_ in ((0, -1), (0.95, -0.31), (0.59, 0.81), (-0.59, 0.81), (-0.95, -0.31))) + figure(32, 34, 0.55),
    "Dissimulation": lambda: duo(_m("oeil_clos"), figure(32, 32, 1.0), 0.4),
    "Doigt de mort": lambda: duo(_m("main"), _m("crane"), 0.46),
    "Forme éthérée": lambda: ghost_figure(32, 32, 1.15) + S("M4 56 H60", 3),
    "Inversion de la gravité": lambda: G_up(),
    "Invocation de céleste": lambda: angel_wings() + star4(54, 52, 5) + star4(10, 52, 4),
    "Lien d'essence": lambda: duo(_m("coeur"), _m("chaine"), 0.42),
    "Manoir somptueux de Mordenkainen": lambda: doorway() + R(2, 58, 60, 4, 1) + star4(54, 10, 5) + star4(10, 10, 4),
    "Mirage": lambda: duo(_m("terre"), _m("masque"), 0.4) + star4(10, 54, 4),
    "Mot de pouvoir douloureux": lambda: duo(_m("bulle"), _m("explosion"), 0.42),
    "Mot de pouvoir fortifiant": lambda: duo(_m("bulle"), _m("fleche_haut"), 0.4),
    "Parole divine": lambda: duo(_m("bulle"), _m("soleil"), 0.42),
    "Projection d'image": lambda: figure(20, 34, 0.85) + ghost_figure(46, 30, 0.85) + L([(28, 28), (38, 26)], 2),
    "Rayons prismatiques": lambda: _prism(),
    "Régénération": lambda: duo(_m("coeur"), _m("cycle"), 0.42),
    "Résurrection": lambda: duo(coffin(), _m("soleil"), 0.42),
    "Simulacre": lambda: figure(20, 32, 1.0) + figure(44, 32, 1.0).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2.6"'),
    "Songe du voile bleu": lambda: duo(_m("lune"), _m("portail"), 0.4),
    "Symbole": lambda: ring(_m("rune")),
    "Temple des dieux": lambda: P("M6 22 L32 6 L58 22 Z") + R(6, 24, 52, 4, 1) + "".join(R(x, 30, 6, 22, 1) for x in (10, 22, 36, 48)) + R(4, 54, 56, 6, 1),
    "Tempête de feu": lambda: place(_m("flamme"), 16, 34, 0.5) + place(_m("flamme"), 32, 26, 0.6) + place(_m("flamme"), 48, 34, 0.5),
    "Tourbillon": lambda: tornado() + Cc(12, 24, 2.6) + Cc(52, 40, 2.4),
    "Transformation draconique": lambda: duo(figure(32, 32, 1.0), dragon_head(), 0.44),
    "Téléportation": lambda: figure(18, 32, 0.8).replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-dasharray="3 3"')
                             + figure(46, 32, 0.8) + star4(32, 14, 6) + star4(32, 52, 4),
    "Épée de Mordenkainen": lambda: place(_m("epee"), 32, 32, 1.0) + star4(52, 52, 6) + star4(10, 12, 4),
    # niveau 8
    "Aliénation": lambda: duo(_m("cerveau"), _m("tentacules"), 0.42),
    "Aura sacrée": lambda: ring(_m("soleil")),
    "Aversion/Attirance": lambda: duo(_m("coeur"), _m("cycle"), 0.42) + star4(10, 10, 4),
    "Aversion/attirance": lambda: duo(_m("coeur"), _m("retour"), 0.42),
    "Bagou": lambda: duo(_m("bulle"), _m("couronne"), 0.4),
    "Champ antimagie": lambda: ring(_m("eclat")) + L([(12, 12), (52, 52)], 5),
    "Clone": lambda: figure(20, 32, 1.0) + figure(44, 32, 1.0) + L([(32, 8), (32, 56)], 1.6),
    "Contrôle du climat": lambda: duo(cloud(28, 1.0), _m("soleil"), 0.42) + star4(10, 54, 3),
    "Demi-plan": lambda: doorway() + star4(12, 12, 5) + star4(52, 12, 5),
    "Domination de monstre": lambda: duo(dragon_head(), _m("chaine"), 0.42),
    "Dragon illusoire": lambda: dragon_head().replace('fill="#FFFFFF"', 'fill="none" stroke="#FFFFFF" stroke-width="2.4"'),
    "Dédale": lambda: "".join(L(p, 4) for p in (((6, 6), (58, 6), (58, 58), (6, 58), (6, 14)), ((14, 14), (50, 14), (50, 50), (14, 50), (14, 22)),
                                                 ((22, 22), (42, 22), (42, 42), (22, 42)))),
    "Esprit faible": lambda: duo(_m("cerveau"), _m("cycle"), 0.4) + star4(10, 54, 3),
    "Esprit impénétrable": lambda: ring(_m("cerveau"), True),
    "Flétrissure épouvantable d'Abi-Dalzim": lambda: duo(_m("goutte"), _m("crane"), 0.44),
    "Formes animales": lambda: place(M["bete"](), 20, 22, 0.42) + place(bird(), 46, 22, 0.42) + place(insect(), 32, 48, 0.42),
    "Forteresse majestueuse": lambda: R(4, 26, 56, 32, 2) + "".join(R(x, 18, 8, 10, 1) for x in (4, 18, 32, 46))
                                      + P("M26 58 V44 C26 38 38 38 38 44 V58 Z", K) + P("M28 18 L32 4 L36 18 Z"),
    "Mot de pouvoir étourdissant": lambda: duo(_m("bulle"), _m("spirale"), 0.4),
    "Nuage incendiaire": lambda: duo(cloud(28, 1.0), _m("flamme"), 0.44),
    "Rupture de la réalité": lambda: duo(_m("portail"), _m("explosion"), 0.42),
    "Tremblement de terre": lambda: _m("terre") + L([(2, 62), (62, 62)], 2),
    "Tsunami": lambda: place(_m("vague"), 32, 30, 1.0) + R(2, 56, 60, 6, 1),
    "Télépathie": lambda: mind_link() + star4(32, 54, 5),
    "Ténèbres oppressantes": lambda: duo(_m("lune"), _m("crane"), 0.4),
    "Éclat du soleil": lambda: sunburst(),
    "Étoile noire": lambda: _star_dark(),
    # niveau 9
    "Arrêt du temps": lambda: _stopwatch(),
    "Changement de forme": lambda: duo(figure(32, 32, 1.0), dragon_head(), 0.4) + star4(10, 10, 4),
    "Emprisonnement": lambda: duo(figure(32, 32, 1.0), _m("chaine"), 0.42) + star4(54, 8, 3),
    "Ennemi subconscient": lambda: duo(head_profile(), demon(), 0.42),
    "Guérison de groupe": lambda: crowd() + over("", place(_m("soin"), 52, 12, 0.32), 6) + star4(10, 10, 4),
    "Hurlement psychique": lambda: duo(head_profile(), _m("ondes"), 0.44),
    "Invulnérabilité": lambda: duo(figure(32, 32, 1.1), _m("diamant"), 0.46),
    "Lame du désastre": lambda: duo(_m("epee"), _m("portail"), 0.4),
    "Mot de pouvoir guérisseur": lambda: duo(_m("bulle"), _m("soin"), 0.42),
    "Mot de pouvoir mortel": lambda: duo(_m("bulle"), _m("crane"), 0.42),
    "Mur prismatique": lambda: "".join(R(4 + i * 8, 8, 7, 50, 1) for i in range(7)),
    "Métamorphose de groupe": lambda: duo(crowd(), _m("cycle"), 0.42),
    "Métamorphose suprême": lambda: duo(M["bete"](), dragon_head(), 0.44),
    "Nuée de météores": lambda: place(_m("meteores"), 32, 30, 1.0) + R(2, 58, 60, 4, 1) + place(burst(32, 32, 20, 8), 50, 54, 0.3),
    "Portail": lambda: doorway() + star4(10, 10, 5) + star4(54, 10, 5) + R(4, 58, 56, 4, 1),
    "Projection astrale": lambda: figure(20, 40, 0.8) + ghost_figure(42, 24, 0.85) + S("M24 30 C28 24 32 24 36 26", 2),
    "Prémonition": lambda: duo(_m("oeil"), _m("eclair"), 0.42),
    "Ravage temporel": lambda: duo(_stopwatch(), _m("explosion"), 0.42),
    "Résurrection suprême": lambda: duo(coffin(), _m("etoile"), 0.42),
    "Souhait": lambda: _m("etoile") + star4(54, 10, 6) + star4(10, 54, 5) + star4(10, 10, 3.4),
    "Tempête vengeresse": lambda: _bolts_skull(),
    "Vide vorace": lambda: Cc(32, 32, 26) + Cc(32, 32, 20, K) + place(_m("spirale"), 32, 32, 0.5),
}


def G_dance():
    return figure(32, 32, 1.0).replace("rotate(0)", "rotate(-15)") + L([(14, 18), (22, 26)], 3) + L([(50, 18), (42, 26)], 3)


def G_up():
    return figure(32, 34, 0.9).replace("rotate(0)", "rotate(180)") + over("", place(_m("fleche_haut"), 52, 16, 0.36), 6) + R(2, 58, 60, 4, 1)


def bolt_rain_k():
    from .art_kit import bolt_rain
    return bolt_rain()


def _bolts_skull():
    from .art_kit import bolt_rain
    return bolt_rain() + place(_m("crane"), 52, 12, 0.28)


def _radiant_storm():
    """Nuage d'où tombent des rais de lumière."""
    rays = "".join(L([(x, 40), (x - 6, 60)], 3.4) for x in (16, 28, 40, 52))
    return place(_m("soleil"), 32, 20, 0.6) + rays
