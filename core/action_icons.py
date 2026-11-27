"""
Icône unique de chaque action (v53) — capacités de classe et d'espèce, manœuvres, actions de ruse, frappes
psioniques, formes du druide, runes, tirs arcaniques, métamagie, actions d'arme, attaques par arme…

Composition par le SENS du nom : un dessin principal (ce que fait l'action) et un dessin secondaire en médaillon
(sa famille ou sa nuance : « Métamagie : Sort prudent » = bouclier + médaillon de magie). Les familles importantes
ont des choix explicites (PAIRS) ; les autres passent par le lexique (LEX). Les armes ont chacune leur dessin
(WEAPON_ART). L'unicité est garantie par data/action_icons.json (tools/build_action_icons.py), qui recense toutes
les actions du jeu et la petite marque distinctive ajoutée quand deux dessins coïncideraient.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Callable, Optional

from . import icon_art as A
from .rules import norm

G: dict[str, Callable[[], str]] = {
    "epee": lambda: A.rot(A.place(A.sword(), 32, 32, 1.05), 35), "dague": lambda: A.rot(A.place(A.dagger(), 32, 32, 1.3), 35),
    "hache": A.axe, "marteau": A.hammer, "masse": A.mace, "lance": A.spear, "arc": A.bow, "arbalete": A.crossbow,
    "poing": A.fist, "main": A.open_hand, "bouclier": A.shield, "botte": A.boot, "flamme": A.flame,
    "flocon": A.snowflake, "eclair": A.bolt, "ondes": A.waves, "goutte": A.drop, "crane": A.skull, "coeur": A.heart,
    "oeil": A.eye, "oeil_clos": A.eye_closed, "loupe": A.magnifier, "porte": A.door, "bulle": A.bubble,
    "sablier": A.hourglass, "fiole": A.flask, "parchemin": A.scroll, "anneau": A.ring, "baguette": A.wand,
    "amulette": A.amulet, "livre": A.book, "etoile": A.star, "eclat": A.sparkle, "soleil": A.sun, "lune": A.moon,
    "patte": A.paw, "note": A.note, "chaine": A.chain, "chaine_brisee": A.broken_chain, "masque": A.mask,
    "explosion": A.burst, "spirale": A.spiral, "aile": A.wing, "couronne": A.crown, "cible": A.target,
    "griffes": A.claws, "cycle": A.cycle_arrows, "retour": A.back_arrow, "portail": A.portal, "cerveau": A.brain,
    "diamant": A.diamond_burst, "fleche_haut": A.arrow_up, "ampoule": A.bulb, "cape": A.cloak, "casque": A.helm,
    "armure": A.armor, "fleches": A.arrows, "gemme": A.gem, "outil": A.tool, "torche": A.torch, "feuille": A.leaf,
    "brume": A.fog, "terre": A.tremor_earth, "vague": A.water_wave, "vent": A.gust, "pierres": A.stones,
    "toile": A.web, "souffle": A.dragon_breath, "alerte": A.exclaim, "esquive": A.figure_dodge, "plus": lambda: A.plus(),
    "soin": A.ICONS["effet_soins"], "fleche": A.ICONS["effet_perforant"], "rune": A.ICONS["rune"],
    "tentacules": A.tentacles, "meteores": A.meteors, "glyphe": lambda: A.rect(10, 10, 44, 44, 6, False, 3) +
    A.path("M20 20 L44 44 M44 20 L20 44 M32 14 V50", w=3), "bete": A.ICONS["forme_sauvage"],
    # v53 : dessins des icônes de classe
    "epee_longue": lambda: A.rot(A.sword(60, 10), 35), "serpe": A.sickle, "cle": A.key, "cle_plate": A.wrench,
    "grande_hache": A.greataxe_double, "ecu": A.heater_shield, "magie": A.magic_sparkles, "sang": A.blood_drops,
}

# --- choix explicites (dessin principal, médaillon) pour les familles importantes
PAIRS = {
    # manœuvres du Maître de guerre
    "attaque menacante": ("crane", "epee"), "attaque precise": ("cible", "epee"), "attaque repoussante": ("retour", "epee"),
    "attaque avec feinte": ("masque", "epee"), "attaque balayage": ("cycle", "epee"), "croc-en-jambe": ("botte", "epee"),
    "desarmement": ("main", "epee"), "distraction": ("oeil", "epee"), "fente": ("lance", "botte"),
    "manoeuvre d'interposition": ("bouclier", "botte"), "manoeuvre protectrice": ("bouclier", "coeur"),
    "manoeuvre tactique": ("botte", "cible"), "parade": ("bouclier", "epee"), "riposte": ("cycle", "epee"),
    "provocation": ("bulle", "alerte"), "ralliement": ("couronne", "coeur"), "commandement": ("couronne", "alerte"),
    "embuscade": ("oeil_clos", "epee"), "evaluation tactique": ("loupe", "cible"), "jeu de jambes": ("botte", "esquive"),
    "lancer rapide": ("dague", "vent"), "frappe agrippante": ("poing", "chaine"), "fioriture defensive": ("bouclier", "note"),
    "fioriture mobile": ("botte", "note"), "fioriture tranchante": ("epee", "note"), "presence imposante": ("couronne", "oeil"),
    "redirection": ("retour", "bouclier"), "echange de position": ("cycle", "botte"), "rechargement eclair": ("arbalete", "eclair"),
    "inspiration martiale": ("note", "epee"), "moulinet": ("cycle", "dague"), "frappe en arc ardent": ("flamme", "epee"),
    # Ruse et Frappe malicieuse (Roublard)
    "action astucieuse : foncer": ("botte", "masque"), "action astucieuse : se cacher": ("oeil_clos", "masque"),
    "action astucieuse : se desengager": ("retour", "masque"), "attaque sournoise": ("dague", "oeil_clos"),
    "frappe malicieuse : assommer": ("marteau", "dague"), "frappe malicieuse : aveugler": ("oeil_clos", "dague"),
    "frappe malicieuse : croc-en-jambe": ("botte", "dague"), "frappe malicieuse : hebetement": ("spirale", "dague"),
    "frappe malicieuse : poison": ("goutte", "dague"), "frappe malicieuse : repli": ("retour", "dague"),
    "esquive instinctive": ("esquive", "bouclier"), "mains lestes": ("main", "masque"), "visee stable": ("cible", "oeil"),
    "coup de chance": ("diamant", "dague"), "voleur de sort": ("eclat", "main"), "pas de l'ombre": ("botte", "lune"),
    # Moine
    "deluge de coups": ("poing", "explosion"), "defense patiente": ("bouclier", "poing"),
    "defense patiente (gratuite)": ("bouclier", "eclat"), "pas du vent": ("botte", "vent"), "pas du vent (gratuit)": ("vent", "eclat"),
    "coup etourdissant": ("spirale", "poing"), "frappe a mains nues (arts martiaux)": ("poing", "botte"),
    "plenitude du corps": ("coeur", "poing"), "plenitude physique": ("coeur", "botte"), "parade de projectiles": ("main", "fleche"),
    "deviation d'assaut": ("main", "bouclier"), "chute ralentie": ("aile", "botte"), "visee concentree": ("cible", "poing"),
    "foulee d'ombre": ("lune", "botte"), "balancement emeche": ("cycle", "fiole"), "chancellements emeches": ("esquive", "fiole"),
    "redirection": ("retour", "poing"),
    # psionique (Soldat psi, Arnaqueur de l'âme, Mystique…)
    "bond psi": ("botte", "cerveau"), "champ protecteur": ("bouclier", "cerveau"), "frappe psionique": ("poing", "cerveau"),
    "mouvement telekinetique": ("main", "cerveau"), "recuperation psionique": ("cycle", "cerveau"),
    "teleportation psychique": ("portail", "cerveau"), "murmures psychiques": ("bulle", "cerveau"),
    "lames psychiques": ("dague", "cerveau"), "seconde lame psychique": ("epee", "cerveau"), "pouvoirs psioniques": ("cerveau", "eclat"),
    "maitre telekinetique": ("main", "couronne"), "rempart de force": ("bouclier", "diamant"), "voile psychique": ("oeil_clos", "cerveau"),
    "rupture spirituelle": ("explosion", "cerveau"), "lien mental": ("chaine", "cerveau"),
    # Druide
    "forme sauvage": ("patte", "cycle"), "forme sauvage de combat : soins": ("soin", "patte"), "formes de metamorphose": ("cycle", "patte"),
    "forme etoilee": ("etoile", "patte"), "forme stellaire": ("etoile", "cycle"), "compagnon sauvage": ("patte", "aile"),
    "convocation de l'esprit du feu sauvage": ("flamme", "patte"), "esprit du feu sauvage : graine de flamme": ("flamme", "feuille"),
    "halo de spores": ("brume", "feuille"), "symbiote & halo de spores": ("feuille", "brume"),
    "animation fongique": ("crane", "feuille"), "entite symbiotique": ("feuille", "coeur"),
    "spores pacifiantes ou toxiques": ("brume", "goutte"), "baume de la cour d'ete": ("soin", "feuille"),
    # métamagie
    "metamagie : sort accelere": ("eclair", "eclat"), "metamagie : sort ample": ("explosion", "eclat"),
    "metamagie : sort amplifie": ("fleche_haut", "eclat"), "metamagie : sort distant": ("cible", "eclat"),
    "metamagie : sort intensifie": ("diamant", "eclat"), "metamagie : sort prudent": ("bouclier", "eclat"),
    "metamagie : sort prevenant": ("oeil", "eclat"), "metamagie : sort renforce": ("poing", "eclat"),
    "metamagie : sort etendu": ("sablier", "eclat"), "sorcellerie innee": ("eclat", "flamme"),
    "sorcellerie innee (2 points de sorcellerie)": ("eclat", "diamant"),
    # runes, tirs arcaniques
    "rune de la colline": ("pierres", "rune"), "rune de la pierre": ("terre", "rune"), "rune du feu": ("flamme", "rune"),
    "rune du givre": ("flocon", "rune"), "rune du nuage": ("brume", "rune"), "bouclier runique": ("bouclier", "rune"),
    "fleche affaiblissante": ("crane", "fleche"), "fleche bannissante": ("portail", "fleche"), "fleche charmeuse": ("coeur", "fleche"),
    "fleche de saisie": ("feuille", "fleche"), "fleche explosive": ("explosion", "fleche"), "fleche perforante": ("fleche", "eclat"),
    # Barbare, Guerrier, Paladin, Clerc, Barde, Occultiste…
    "entrer en rage": ("griffes", "flamme"), "attaque temeraire": ("griffes", "epee"), "attaque de frenesie": ("griffes", "explosion"),
    "presence intimidante": ("alerte", "griffes"), "second souffle": ("soin", "vent"), "sursaut d'activite": ("eclair", "botte"),
    "inflexible": ("bouclier", "etoile"), "imposition des mains": ("soin", "main"), "chatiment divin": ("soleil", "epee"),
    "chatiment divin (gratuit)": ("soleil", "eclat"), "chatiment divin (sort)": ("soleil", "parchemin"), "sens divin": ("oeil", "soleil"),
    "conduit divin (serment)": ("soleil", "bouclier"), "conduit divin (domaine)": ("soleil", "livre"),
    "conduit divin : renvoi des morts-vivants": ("crane", "soleil"), "intervention divine": ("soleil", "couronne"),
    "canalisation de puissance divine": ("soleil", "fleche_haut"), "inspiration bardique": ("note", "coeur"),
    "inspiration au combat": ("note", "epee"), "mots cinglants": ("bulle", "note"), "contre-charme": ("note", "bouclier"),
    "recevoir l'inspiration (mj)": ("etoile", "note"), "manteau d'inspiration": ("cape", "note"), "manteau de majeste": ("cape", "couronne"),
    "mante d'inspiration": ("cape", "note"), "mante de majeste": ("cape", "couronne"), "arme occulte": ("epee", "parchemin"),
    "lien avec l'arme : rappel": ("epee", "chaine"), "main de mage arcanique": ("main", "eclat"), "souffle": ("souffle", "flamme"),
    "attaque d'opportunite": ("alerte", "epee"), "proie du chasseur": ("cible", "arc"), "tueur de colosses": ("cible", "couronne"),
    "commander le compagnon": ("patte", "couronne"), "compagnon primitif": ("patte", "feuille"),
    "elixir experimental": ("fiole", "eclat"), "eclair de genie": ("ampoule", "eclair"),
}


# --- même aptitude sous deux noms (2014 / 2024, traductions) : même icône, voulu
ALIASES = {
    "ailes draconiques": "ailes de dragon", "vol draconique": "ailes de dragon", "ange vengeur": "ange de la vengeance",
    "defense superieure du chasseur": "defense de chasseur superieure", "sentinelle aux portes de la mort":
    "sentinelle au seuil de la mort", "nemesis des mages": "nemesis des lanceurs", "eclat protecteur":
    "illumination protectrice", "mante d'inspiration": "manteau d'inspiration", "mante de majeste": "manteau de majeste",
    "marees du chaos": "maree du chaos", "retablir l\u2019equilibre": "retablir l'equilibre",
    "torsion envoutante": "torsion seduisante", "revirement envoutant": "torsion seduisante",
    "pas feerique": "foulee des fees", "protection entropique": "garde entropique", "main de guerison": "mains guerisseuses",
    "mains guerisseuses": "mains guerisseuses", "egide projetee": "protection projetee",
    "manifestation d'un echo": "manifestation d'un echo", "chance du nombre": "chance du nombre",
}

PAIRS.update({
    "adaptation du terrain": ("terre", "botte"), "arret-coeur": ("coeur", "poing"), "bousculer": ("main", "retour"),
    "briseur de dos": ("marteau", "esquive"), "conjuration mineure": ("portail", "gemme"),
    "deplacement exaltant": ("botte", "fleche_haut"), "deviation arcanique": ("bouclier", "eclat"),
    "escarmoucheur": ("esquive", "arc"), "escarmoucheur & survivaliste": ("esquive", "feuille"),
    "esprit combatif": ("epee", "fleche_haut"), "esprit manifeste": ("aile", "oeil"), "fauchage": ("cycle", "botte"),
    "guerrier planaire": ("portail", "epee"), "guidage magique": ("cible", "eclat"), "laceration (entaille)": ("griffes", "epee"),
    "lutte": ("poing", "main"), "magie de guerre": ("epee", "eclat"), "magie renforcante": ("fleche_haut", "eclat"),
    "magie tempetueuse": ("eclair", "eclat"), "marque inebranlable": ("cible", "bouclier"),
    "moulinet de taille (fendoir)": ("cycle", "hache"), "memoire kenku": ("bulle", "aile"),
    "onde de choc acoustique": ("ondes", "explosion"), "pirouettes coordonnees": ("esquive", "note"),
    "poussee d'adrenaline": ("coeur", "eclair"), "proie du tueur": ("cible", "crane"), "preparation": ("sablier", "epee"),
    "represailles": ("retour", "griffes"), "riposte capricieuse": ("cycle", "spirale"), "ruse magique": ("masque", "eclat"),
    "retablir l'equilibre": ("cycle", "spirale"), "revelation dans la chair": ("griffes", "oeil"), "tenacite": ("bouclier", "poing"),
    "voile de murmure": ("oeil_clos", "bulle"),
    "ailes de dragon": ("aile", "souffle"), "ange de la vengeance": ("aile", "epee"),
    "benediction de l'escroc": ("masque", "soleil"), "conduit divin : benediction du dieu de la guerre": ("epee", "soleil"),
    "conduit divin : emissaire de paix & reprimander la violence": ("coeur", "soleil"),
    "exploitation du pouvoir divin": ("fleche_haut", "soleil"), "nimbe sacre": ("soleil", "couronne"),
    "nemesis des lanceurs": ("eclat", "epee"), "presence zelee": ("alerte", "soleil"), "pretre de guerre": ("epee", "livre"),
    "revelation celeste": ("aile", "soleil"), "trait de soleil radieux": ("soleil", "fleche"), "vengeur implacable": ("epee", "botte"),
    "ame radieuse": ("soleil", "aile"), "armure de malefices": ("armure", "crane"), "bastion de la loi": ("bouclier", "couronne"),
    "bouclier spirituel": ("bouclier", "aile"), "champ defensif": ("bouclier", "explosion"), "defense de carapace": ("bouclier", "pierres"),
    "defense de chasseur superieure": ("bouclier", "arc"), "defense glorieuse": ("bouclier", "soleil"),
    "endurance implacable": ("coeur", "crane"), "esprit garde": ("bouclier", "cerveau"),
    "illumination protectrice": ("ampoule", "bouclier"), "illumination protectrice amelioree": ("ampoule", "fleche_haut"),
    "protection projetee": ("bouclier", "fleche"), "ascendance draconique": ("souffle", "goutte"),
    "disciple draconique": ("souffle", "livre"), "ascendance gigante": ("couronne", "poing"), "attraction violente": ("chaine", "poing"),
    "brise-crane (frappe commotionnante)": ("marteau", "spirale"), "charge": ("botte", "lance"),
    "contre-attaque du tueur": ("retour", "crane"), "coup cinglant": ("poing", "eclair"), "forme de geant": ("fleche_haut", "poing"),
    "frappe affaiblissante": ("poing", "crane"), "frappe du pommeau": ("epee", "spirale"), "frappes autoguidees": ("cible", "poing"),
    "frappes terribles": ("poing", "alerte"), "percage (frappe perforante)": ("fleche", "poing"),
    "puissance des geants": ("poing", "fleche_haut"), "ruee cornue": ("griffes", "botte"),
    "attenuation des elements": ("bouclier", "flamme"), "aura du gardien": ("coeur", "bouclier"), "don elementaire": ("explosion", "gemme"),
    "aval de la terre": ("terre", "coeur"), "gnome des roches": ("outil", "pierres"), "avenir convergent": ("oeil", "sablier"),
    "combat perspicace": ("oeil", "epee"), "combattant clairvoyant": ("oeil", "esquive"), "presage": ("oeil", "diamant"),
    "bouclier solaire": ("bouclier", "soleil"), "branches de l'arbre": ("feuille", "chaine"), "don feerique": ("feuille", "eclat"),
    "gnome des forets": ("feuille", "oeil_clos"), "presence feerique": ("feuille", "coeur"),
    "sanctuaire de dame nature": ("feuille", "bouclier"), "bribes des defunts": ("crane", "bulle"),
    "force avant la mort": ("crane", "poing"), "inexorable martyr": ("crane", "coeur"), "plaintes d'outre-tombe": ("crane", "ondes"),
    "sentinelle au seuil de la mort": ("crane", "oeil"), "voile necrotique": ("crane", "cape"), "ame vengeresse": ("crane", "epee"),
    "cadran d'arcanes & retrogradation": ("sablier", "retour"), "camouflage svirfnebelin": ("oeil_clos", "pierres"),
    "embusque redoutable": ("oeil_clos", "arc"), "canon occulte": ("outil", "explosion"), "concu pour reussir": ("outil", "etoile"),
    "reseau maille": ("toile", "outil"), "ame de l'artifice": ("outil", "coeur"), "carapace necrotique": ("crane", "bouclier"),
    "defense spectrale": ("aile", "bouclier"), "champion antique": ("couronne", "epee"),
    "commander le defenseur d'acier": ("outil", "couronne"), "chance alteree": ("diamant", "cycle"), "chance forcee": ("diamant", "poing"),
    "comme par hasard": ("diamant", "spirale"), "faveur des dieux": ("diamant", "soleil"), "jeton etrange": ("gemme", "spirale"),
    "quinte flush royale": ("diamant", "couronne"), "chance du nombre": ("diamant", "patte"), "chance du tenebreux": ("diamant", "lune"),
    "changeforme": ("masque", "cycle"), "cornes martelantes": ("griffes", "marteau"), "courroux des mers": ("vague", "griffes"),
    "forme hybride": ("griffes", "masque"), "fureur des petits": ("griffes", "fleche_haut"), "modelage du corps": ("cycle", "main"),
    "machoires affamees": ("griffes", "crane"), "metamorphose": ("cycle", "griffes"), "chant de defense": ("note", "bouclier"),
    "chant de la lame": ("note", "dague"), "inspiration martiale": ("note", "poing"),
    "chien de mauvais augure": ("patte", "lune"), "dispersion de l'essaim": ("patte", "vent"),
    "esprit de l'aigle : foncer": ("aile", "botte"), "esprit totem": ("patte", "aile"), "essaim rassemble": ("patte", "chaine"),
    "chatiment de sang": ("goutte", "epee"), "sanguisuga supreme": ("goutte", "coeur"), "conquerant invincible": ("couronne", "bouclier"),
    "maitre tacticien": ("couronne", "cible"), "courroux de la tempete": ("eclair", "retour"), "fureur de la tempete": ("eclair", "griffes"),
    "double illusoire": ("masque", "esquive"), "manifestation d'un echo": ("masque", "ondes"), "moi illusoire": ("masque", "bouclier"),
    "decharge arcanique": ("eclat", "explosion"), "surcharge magique": ("eclat", "fleche_haut"), "decharge elementaire": ("explosion", "flamme"),
    "sort mineur supp. & illumination protectrice": ("ampoule", "eclat"),
    "embuscade effrayante": ("alerte", "oeil_clos"), "frayeur predatrice": ("alerte", "griffes"), "intrepide": ("coeur", "alerte"),
    "opportuniste": ("alerte", "epee"), "rugissement intimidant": ("alerte", "ondes"), "reprimande vigilante": ("alerte", "bulle"),
    "force vivifiante": ("soin", "fleche_haut"), "guerison acceleree": ("soin", "eclair"), "toucher purifiant": ("soin", "goutte"),
    "forme de la bete": ("griffes", "patte"), "langage de la foret & totem spirituel": ("bulle", "feuille"),
    "forme de la bete : griffes": ("griffes", "patte"), "forme de la bete : morsure": ("crane", "patte"),
    "forme de la bete : queue": ("cycle", "patte"), "foulee des fees": ("feuille", "botte"),
    "voyage au gre de l'arbre": ("feuille", "portail"), "fuite agile": ("botte", "retour"), "pied agile": ("botte", "eclair"),
    "fuite brumeuse": ("brume", "botte"), "gambade heureuse": ("botte", "coeur"), "pas ethere": ("botte", "aile"),
    "saut de lapin": ("botte", "fleche_haut"), "transposition bienveillante": ("cycle", "coeur"),
    "echappatoire brumeuse": ("brume", "retour"), "garde entropique": ("spirale", "bouclier"),
    "mains guerisseuses": ("soin", "main"), "inspiration contagieuse": ("note", "explosion"), "legende vivante": ("note", "couronne"),
    "panache": ("note", "esquive"), "paroles troublantes": ("bulle", "spirale"), "representation animee": ("note", "patte"),
    "representation de la creation": ("note", "outil"), "lien enhardissant": ("chaine", "fleche_haut"), "lien parfait": ("chaine", "etoile"),
    "main de souffrance": ("main", "crane"), "main du mal": ("main", "spirale"), "manteau d'inspiration": ("cape", "note"),
    "manteau de majeste": ("cape", "couronne"), "maree du chaos": ("spirale", "vague"), "torsion seduisante": ("coeur", "cycle"),
    "union avec le verbe": ("bulle", "coeur"), "tentacule des profondeurs": ("tentacules", "vague"),
    "ame oceane & tentacule gardien": ("vague", "tentacules"), "tir handicapant": ("arc", "botte"), "tir mobile": ("arc", "esquive"),
    "tir perforant": ("arc", "fleche"),
    # derniers départages (deux aptitudes différentes ne partagent jamais un dessin)
    "arret-coeur": ("crane", "coeur"), "opportuniste": ("alerte", "dague"), "ame vengeresse": ("crane", "aile"),
    "laceration (entaille)": ("griffes", "dague"), "aura du gardien": ("explosion", "coeur"),
    "charmantes defenses": ("coeur", "bouclier"), "defense glorieuse": ("couronne", "soleil"),
    "esprit garde": ("cerveau", "bouclier"), "chant de defense": ("note", "armure"), "esprit de l'aigle : foncer": ("aile", "vent"),
    "combat perspicace": ("oeil", "cible"), "esprit totem": ("patte", "etoile"), "tenacite": ("poing", "bouclier"),
    "deviation arcanique": ("retour", "eclat"), "metamagie : sort prudent": ("bouclier", "plus"),
    "saut de lapin": ("botte", "patte"), "presence feerique": ("feuille", "couronne"), "forme de la bete": ("patte", "griffes"),
    "forme de la bete : queue": ("retour", "patte"), "frappes autoguidees": ("cible", "fleche"),
    "frayeur predatrice": ("griffes", "alerte"), "maitrises sup. & fureur de l'ouragan": ("vent", "eclair"),
    "metamagie : sort distant": ("fleche", "eclat"), "mains guerisseuses": ("main", "soin"), "nimbe sacre": ("ampoule", "soleil"),
    "magie renforcante": ("fleche_haut", "gemme"), "magie tempetueuse": ("eclair", "vent"),
    "riposte capricieuse": ("retour", "spirale"), "yeux de la tombe": ("oeil", "crane"),
    "allegeance divine": ("chaine", "soleil"), "armes du kensei, parade agile & tir du kensei": ("epee", "arc"),
    "inexorable martyr": ("coeur", "fleche_haut"), "aura de tempete : desert": ("vent", "flamme"),
    "aura de tempete : mer": ("vague", "eclair"), "aura de tempete : toundra": ("flocon", "eclair"),
    "metamagie : sort distant": ("fleches", "eclat"), "tempete dechainee (desert)": ("flamme", "vent"),
    "tempete dechainee (mer)": ("vague", "vent"),
})

# --- lexique : (motif du nom, dessin), du plus précis au plus général
LEX = [
    (r"dragon|draconi", "souffle"), (r"\bailes?\b|\bvol\b|planer|voler", "aile"), (r"phenix", "flamme"),
    (r"\bange|celeste|radieu|soleil|solaire|nimbe|lumiere|halo de lumiere|aube", "soleil"),
    (r"ombre|tenebr|nocturne", "lune"), (r"etoil|stellaire|astral|cosmique", "etoile"),
    (r"tombe|defunt|mort|necrot|spectral|vengeresse|martyr", "crane"), (r"sang|vampir|sanguisuga", "goutte"),
    (r"\bfeu\b|flamme|ardent|cauteris|brul", "flamme"), (r"givre|toundra|glace|froid", "flocon"),
    (r"tempete|ouragan|foudre|eclair", "eclair"), (r"\bmer\b|ocean|tentacule|profondeurs|maree", "vague"),
    (r"desert|\bvent\b|nuage|nuees", "vent"), (r"pierre|colline|\bterre\b|roche|svirfneblin|endurance de pierre", "pierres"),
    (r"arbre|foret|nature|branche|spore|fongi|symbio|ete\b|feerique|fees?\b", "feuille"),
    (r"geant|gigant|colosse|puissance", "poing"), (r"chance|hasard|jeton|flush|des dieux|faveur", "diamant"),
    (r"presage|avenir|clairvoy|perspicace|vie anterieure", "oeil"), (r"chaos|entropi", "spirale"),
    (r"tempor|chronal|temps|cadran", "sablier"), (r"psion|psychi|mental|telepath|telekin|\bpsi\b", "cerveau"),
    (r"teleport|\bpas\b|foulee|saut|bond|transposition|ethere|fuite|echappatoire|gambade|pied agile|voyage", "botte"),
    (r"invisible|camoufl|chameleon|cameleon|embusqu|cache", "oeil_clos"),
    (r"illusoir|double|clone|\bmoi\b|echo|reflet", "masque"),
    (r"charm|envout|seduis|hypnot|torsion|revirement|union avec", "coeur"),
    (r"terreur|terrif|effray|intimid|rugissement|frayeur|menac|cri\b", "alerte"),
    (r"guerison|guerisseu|vivifiant|baume|plenitude|purifiant|soin", "soin"),
    (r"protect|bouclier|egide|garde|rempart|defense|defenseur|parade|bastion|carapace|champ|armure|inflexible|endurance", "bouclier"),
    (r"rage|frenesie|fureur|furie|courroux|dechaine", "griffes"),
    (r"inspiration|chant|mots|paroles|represent|manteau|mante|panache|legende", "note"),
    (r"command|rallie|tacticien|tactique|maitre|conquerant|champion|allegeance", "couronne"),
    (r"compagnon|\bbete|chien|totem|essaim|defenseur d.acier|corbeau|aigle", "patte"),
    (r"morsure|machoire|corne|griffe|queue|hybride|changeforme|modelage|metamorph", "griffes"),
    (r"fleche", "fleche"), (r"\btir\b", "arc"), (r"lame|epee|kensei|arme", "epee"), (r"lien|chaine", "chaine"),
    (r"rune", "rune"), (r"potion|elixir|alchim", "fiole"), (r"forge|artifice|mecani|canon|maille|parachev|concu", "outil"),
    (r"divin|conduit|benedict|pretre|sacre|zele|intervention|vengeur|vengeance|nemesis", "soleil"),
    (r"magi|sort|arcan|sorcellerie|surcharge", "eclat"), (r"main\b|mains", "main"), (r"oeil|yeux|regard|vision", "oeil"),
    (r"frappe|coup|attaque|charge|ruee|attraction", "poing"), (r"esquive|evite|agile", "esquive"),
    (r"opportun|vigilant|alerte|prepare|intrepide", "alerte"), (r"conscience|savoir|connaissance|eclair de genie", "livre"),
    (r"elementaire|element", "explosion"), (r"halo|aura", "explosion"),
]

ACCENTS = [lambda: A.sparkle(9, 55, 5), lambda: A.circle(9, 55, 4, True), lambda: A.star(9, 55, 6, 2.6),
           lambda: A.poly([(9, 49), (14, 59), (4, 59)]), lambda: A.rect(5, 51, 8, 8, 1.5),
           lambda: A.poly([(9, 49), (15, 55), (9, 61), (3, 55)]), lambda: A.circle(9, 55, 4.5, False, 2),
           lambda: A.line(3, 59, 15, 47, 3), lambda: A.path("M3 55 C7 49 11 61 15 55", w=2.5)]


def _matches(text: str) -> list[str]:
    n = norm(text)
    out = []
    for rx, glyph in LEX:
        if re.search(rx, n) and glyph not in out:
            out.append(glyph)
    return out


def pair_for(name: str) -> tuple[str, str]:
    """(dessin principal, médaillon) d'une action."""
    key = norm(name)
    key = ALIASES.get(key, key)
    if key in PAIRS:
        return PAIRS[key]
    if ":" in name:                                      # « Famille : nuance » -> nuance en grand, famille en médaillon
        family, detail = name.split(":", 1)
        main = (_matches(detail) or _matches(name) or ["eclat"])[0]
        badge = next((g for g in _matches(family) if g != main), "")
        return main, badge
    found = _matches(name)
    if not found:
        return "eclat", ""
    return found[0], found[1] if len(found) > 1 else ""


def pair_body(main: str, badge: str = "") -> str:
    """v53 : icône « dessin + second dessin » à partir de deux dessins du registre G (historiques, classes…).
    Le second dessin (bouclier, étoile, flamme…) est posé tel quel en bas à droite, détouré d'un fin liseré vide
    qui le sépare du premier — sans médaillon rond."""
    if not badge:
        return A.place(G.get(main, A.sparkle)(), 32, 32, 0.8)
    out = A.place(G.get(main, A.sparkle)(), 27, 27, 0.7)
    second = A.place(G.get(badge, A.sparkle)(), 46, 46, 0.5)
    cut = second.replace('fill="#FFFFFF"', 'fill="#000000"').replace('stroke="#FFFFFF"', 'stroke="#000000"')
    return (out + '<g fill="#000000" stroke="#000000" stroke-width="9" stroke-linejoin="round">' + cut + "</g>"
            + second)


def layered_body(layers) -> str:
    """v53 : icône composée librement — [(dessin du registre G, x, y, échelle, angle)], dans l'ordre de dessin ;
    chaque dessin après le premier est détouré d'un fin liseré vide qui le sépare de ceux de dessous."""
    out = ""
    for i, (name, x, y, s, angle) in enumerate(layers):
        part = A.place(G.get(name, A.sparkle)(), x, y, s)
        if angle:
            part = A.rot(part, angle, x, y)
        if i:
            cut = part.replace('fill="#FFFFFF"', 'fill="#000000"').replace('stroke="#FFFFFF"', 'stroke="#000000"')
            out += '<g fill="#000000" stroke="#000000" stroke-width="9" stroke-linejoin="round">' + cut + "</g>"
        out += part
    return out


def compose(name: str, variant: int = 0) -> str:
    main, badge = pair_for(name)
    out = A.place(G.get(main, A.sparkle)(), 28, 28, 0.7 if badge else 0.8) if badge else \
        A.place(G.get(main, A.sparkle)(), 32, 32, 0.8)
    if badge:                                            # médaillon en bas à droite : disque plein, dessin découpé
        inner = A.place(G.get(badge, A.sparkle)(), 49, 49, 0.3)
        out += A.circle(49, 49, 14.5, True) + '<g fill="#000000" stroke="#000000">' + \
            inner.replace('fill="#FFFFFF"', 'fill="#000000"').replace('stroke="#FFFFFF"', 'stroke="#000000"') + "</g>"
    if variant:
        out += ACCENTS[(variant - 1) % len(ACCENTS)]()
        if variant > len(ACCENTS):
            out += A.place(ACCENTS[(variant // len(ACCENTS)) % len(ACCENTS)](), 9, 9, 1.0)
    return out


# --- armes : un dessin par arme (attaque — Épée longue, Rapière…)
def _long_sword(length, width, angle=35, scale=1.05):
    return lambda: A.rot(A.place(A.sword(length, width), 32, 32, scale), angle)


WEAPON_ART = {
    "epee longue": _long_sword(50, 10), "epee a deux mains": _long_sword(58, 13, 35, 1.0), "rapiere": _long_sword(58, 6),
    "epee courte": _long_sword(38, 10, 35, 1.1), "cimeterre": A.ICONS["arme_cimeterre"], "dague": G["dague"],
    "hachette": lambda: A.place(A.axe(), 32, 34, 0.75), "hache d'armes": A.axe, "grande hache": A.greataxe,
    "marteau leger": lambda: A.place(A.hammer(), 32, 34, 0.75), "marteau de guerre": A.hammer,
    "maillet d'armes": lambda: A.rect(30, 16, 4, 44, 2) + A.rect(12, 6, 40, 16, 3), "masse d'armes": A.mace,
    "morgenstern": lambda: A.mace() + A.circle(32, 20, 16, False, 2), "gourdin": lambda: A.rot(A.path(
        "M28 60 L28 30 C22 24 22 8 32 6 C42 8 42 24 36 30 L36 60 Z", True), 25),
    "massue": lambda: A.rot(A.path("M26 60 L26 28 C16 22 16 4 32 2 C48 4 48 22 38 28 L38 60 Z", True), 25),
    "fleau d'armes": A.flail, "pic de guerre": lambda: A.rect(30, 14, 4, 46, 2) + A.path("M10 16 C20 8 44 8 54 16 L32 20 Z", True),
    "lance": A.spear, "pique": lambda: A.place(A.spear(), 32, 32, 1.12), "hallebarde": A.halberd,
    "coutille": lambda: A.rect(30, 16, 4, 44, 2) + A.path("M32 2 C40 8 40 18 34 22 L30 22 C26 14 26 8 32 2 Z", True),
    "trident": lambda: A.rect(30, 20, 4, 40, 2) + A.path("M18 20 V6 M32 20 V2 M46 20 V6 M18 20 H46", w=4),
    "lance d'arcon": lambda: A.poly([(32, 2), (40, 44), (24, 44)]) + A.rect(28, 44, 8, 16, 2),
    "javeline": A.javelin, "arc court": lambda: A.place(A.bow(), 32, 32, 0.8), "arc long": A.bow,
    "arbalete legere": A.crossbow, "arbalete lourde": lambda: A.crossbow() + A.rect(24, 50, 16, 6, 2),
    "arbalete de poing": lambda: A.place(A.crossbow(), 32, 34, 0.75), "fronde": A.sling,
    "flechette": lambda: A.rot(A.line(32, 20, 32, 56, 3) + A.poly([(32, 8), (36, 20), (28, 20)]) +
                               A.path("M28 50 L32 56 L36 50", w=2.5), 30),
    "sarbacane": lambda: A.rot(A.rect(29, 6, 6, 52, 3), 45) + A.circle(50, 14, 3, True),
    "fouet": A.whip, "filet": A.web, "faucille": lambda: A.path(
        "M22 58 L26 40 C46 40 54 22 44 8 C58 18 56 44 30 46 L28 58 Z", True),
    "baton": A.staff, "mains nues": A.fist, "bouclier": A.shield,
    "pistolet": lambda: A.rot(A.rect(12, 20, 40, 9, 2) + A.path("M14 28 L26 28 L22 52 L10 52 Z", True)
                              + A.path("M28 29 C28 38 36 38 36 29", w=2.5), -15),
    "mousquet": lambda: A.rot(A.rect(4, 26, 46, 6, 2) + A.path("M40 26 L60 30 L60 40 L36 34 Z", True)
                              + A.path("M30 32 C30 40 38 40 38 32", w=2.5), -35),
}
# v53 : armes de base aux noms sans dessin propre -> dessin le plus proche
WEAPON_ALIASES = {"hache a deux mains": "grande hache", "serpe": "faucille", "arquebuse": "mousquet",
                  "revolver": "pistolet", "fusil": "mousquet"}
# famille de l'arme quand aucun nom ne correspond (arme sur mesure, homebrew…)
WEAPON_FAMILIES = [("arbalete", "arbalete legere"), ("arc", "arc long"), ("hache", "hache d'armes"),
                   ("epee", "epee longue"), ("sabre", "cimeterre"), ("marteau", "marteau de guerre"),
                   ("masse", "masse d'armes"), ("lance", "lance"), ("fleau", "fleau d'armes"), ("couteau", "dague"),
                   ("poignard", "dague")]


def weapon_key(text: str) -> str:
    n = norm(text)
    return (next((k for k in sorted(WEAPON_ART, key=len, reverse=True) if k in n), "")
            or next((v for k, v in WEAPON_ALIASES.items() if k in n), "")
            or next((v for k, v in WEAPON_FAMILIES if re.search(r"\b" + k + r"s?\b", n)), ""))


@lru_cache(maxsize=1)
def _registry() -> dict:
    try:
        from .paths import get_resource_path
        with open(get_resource_path("data/action_icons.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"variantes": {}, "actions": []}


@lru_cache(maxsize=1)
def _drawn_actions() -> dict:
    """v53 : dessins soignés (core/art_armes) des actions d'arme et des manœuvres, par nom normalisé."""
    from . import art_armes as AA
    return {norm(k): v for d in (AA.ACTIONS, AA.MANEUVERS) for k, v in d.items()}


@lru_cache(maxsize=1)
def _drawn_weapons() -> dict:
    from . import art_armes as AA
    return {norm(k): k for k in AA.WEAPONS}


def action_body(name: str) -> str:
    """Corps SVG de l'icône unique d'une action : dessin soigné s'il existe, sinon composition (variante issue du
    registre si deux dessins coïncident)."""
    base = re.sub(r"\s*\(2024\)\s*$", "", name or "").strip()
    drawn = _drawn_actions().get(norm(base)) or _drawn_actions().get(norm(base.split(" — ")[0]))
    if drawn:
        return drawn()
    return compose(base, int(_registry().get("variantes", {}).get(base, 0)))


def weapon_body(weapon_text: str) -> Optional[str]:
    k = weapon_key(weapon_text)
    if not k:
        return None
    name = _drawn_weapons().get(k)
    if name:                                             # v53 : dessin soigné
        from . import art_armes as AA
        return AA.weapon_art(name)
    return WEAPON_ART[k]()


def canonical(name: str) -> str:
    key = norm(name)
    return ALIASES.get(key, key)


def assign_variants(names: list[str], taken: set) -> dict[str, int]:
    """Variantes minimales pour que chaque action ait un dessin distinct (et distinct des icônes `taken`) ; deux
    noms d'une même aptitude (ALIASES) partagent volontairement le leur."""
    seen, out, done = set(taken), {}, {}
    for n in sorted(dict.fromkeys(names), key=lambda x: (canonical(x) not in PAIRS, x)):
        if canonical(n) in done:                         # alias : même dessin que le nom de référence
            if done[canonical(n)]:
                out[n] = done[canonical(n)]
            continue
        v = 0
        body = compose(n)
        while body in seen and v < 200:
            v += 1
            body = compose(n, v)
        seen.add(body)
        done[canonical(n)] = v
        if v:
            out[n] = v
    return out
