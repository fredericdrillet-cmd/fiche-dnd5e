"""
Icône de chaque tuile du tour (v53) : (genre, nom, catégorie de couleur).

- genre « sort » : nom du sort (icône unique de core/spell_icons, couleur de l'école ou verte pour un soin) ;
- genre « icone » : nom d'une icône de data/icons (core/icon_art.ICONS).
Catégories : attaque (rouge), soins (vert), commune (brun), capacite (violet), objet (doré), reaction (turquoise).
"""
from __future__ import annotations

import re

from .rules import norm

COMMON = [("foncer", "foncer"), ("desengager", "desengager"), ("esquiver", "esquiver"), ("aider", "aider"),
          ("cacher", "se_cacher"), ("bousculer", "bousculer"), ("saisir", "saisir"), ("pret", "se_tenir_pret"),
          ("utiliser un objet", "utiliser_objet"), ("chercher", "chercher"), ("interagir", "interagir"),
          ("parler", "parler"), ("etudier", "etudier"), ("influencer", "influencer"), ("potion", "boire_potion"),
          ("liberer", "se_liberer"), ("magie", "magie"), ("lancer", "lancer_objet")]

WEAPONS = [("grande hache", "arme_grande_hache"), ("hache", "arme_hache"), ("epee courte", "arme_epee_courte"),
           ("cimeterre", "arme_cimeterre"), ("sabre", "arme_cimeterre"), ("rapiere", "arme_epee"),
           ("epee", "arme_epee"), ("dague", "arme_dague"), ("marteau", "arme_marteau"), ("pic de guerre", "arme_marteau"),
           ("masse", "arme_masse"), ("morgenstern", "arme_masse"), ("gourdin", "arme_masse"), ("fleau", "arme_fleau"),
           ("hallebarde", "arme_hallebarde"), ("coutille", "arme_hallebarde"), ("pique", "arme_hallebarde"),
           ("lance", "arme_lance"), ("trident", "arme_lance"), ("arbalete", "arme_arbalete"), ("arc", "arme_arc"),
           ("fronde", "arme_fronde"), ("baton", "arme_baton"), ("fouet", "arme_fouet"), ("javeline", "arme_javeline"),
           ("fleche", "arme_arc"), ("mains nues", "arme_mains_nues"), ("bouclier", "arme_bouclier"),
           ("faucille", "arme_cimeterre"), ("serpe", "arme_cimeterre"), ("hachette", "arme_hache"),
           ("sarbacane", "arme_javeline"), ("filet", "saisir")]

ITEMS = [("potion", "objet_potion"), ("elixir", "objet_potion"), ("parchemin", "objet_parchemin"),
         ("anneau", "objet_anneau"), ("baguette", "objet_baguette"), ("baton", "objet_baton"),
         ("sceptre", "objet_baton"), ("amulette", "objet_amulette"), ("collier", "objet_amulette"),
         ("medaillon", "objet_amulette"), ("perle", "objet_gemme"), ("gemme", "objet_gemme"),
         ("cape", "objet_cape"), ("manteau", "objet_cape"), ("bottes", "objet_bottes"), ("gants", "objet_gants"),
         ("gantelets", "objet_gants"), ("bracelet", "objet_gants"), ("casque", "objet_casque"),
         ("heaume", "objet_casque"), ("armure", "objet_armure"), ("bouclier", "objet_bouclier"),
         ("fleche", "objet_munitions"), ("carreau", "objet_munitions"), ("livre", "objet_livre"),
         ("tome", "objet_livre"), ("sac", "objet_sac"), ("torche", "objet_torche")]

FEATURES = [("rage", "rage"), ("second souffle", "second_souffle"), ("sursaut", "fougue"), ("fougue", "fougue"),
            ("attaque sournoise", "attaque_sournoise"), ("chatiment", "chatiment"),
            ("imposition des mains", "imposition_mains"), ("inspiration bardique", "inspiration_bardique"),
            ("inspiration", "inspiration_bardique"), ("manteau", "inspiration_bardique"),
            ("mante", "inspiration_bardique"), ("forme sauvage", "forme_sauvage"), ("compagnon", "compagnon"),
            ("conduit divin", "conduit_divin"), ("renvoi", "conduit_divin"), ("intervention divine", "conduit_divin"),
            ("canalisation", "conduit_divin"), ("pouvoir divin", "conduit_divin"), ("sens divin", "sens_divin"),
            ("deluge", "deluge_coups"), ("defense patiente", "defense_sans_armure"), ("pas du vent", "foncer"),
            ("coup etourdissant", "ki"), ("plenitude", "ki"), ("ombre", "action_fourbe"), ("foulee", "action_fourbe"),
            ("action fourbe", "action_fourbe"), ("mains lestes", "action_fourbe"), ("visee", "manoeuvre"),
            ("souffle", "souffle_draconique"), ("manoeuvre", "manoeuvre"), ("riposte", "riposte"),
            ("parade", "parade"), ("deviation", "parade"), ("inflexible", "indomptable"),
            ("indomptable", "indomptable"), ("esquive", "esquive_totale"), ("aura", "aura"),
            ("sorcellerie", "points_sorcellerie"), ("metamagie", "metamagie"), ("arme occulte", "pacte"),
            ("lien avec l.arme", "pacte"), ("pacte", "pacte"), ("familier", "familier"), ("marque", "marque_chasseur"),
            ("proie", "marque_chasseur"), ("tueur de colosses", "ennemi_jure"), ("rune", "rune"),
            ("tir arcanique", "tir_arcanique"), ("presage", "chance"), ("chance", "chance"), ("hasard", "chance"),
            ("marees du chaos", "chance"), ("faveur", "chance"), ("presence", "grandeur"), ("majeste", "grandeur"),
            ("regard", "vision_noir"), ("charme", "ecole_enchantement"), ("contre-charme", "inspiration_bardique"),
            ("mots cinglants", "inspiration_bardique"), ("brumeuse", "action_fourbe"), ("teleport", "invocation_creature"),
            ("elixir", "objet_potion"), ("eclair de genie", "chance"), ("champ defensif", "aura"),
            ("illumination", "aura"), ("eclat protecteur", "aura"), ("attenuation", "resistance"),
            ("protection", "parade"), ("egide", "parade"), ("garde", "parade"), ("represailles", "riposte"),
            ("attaque temeraire", "rage"), ("frappe malicieuse", "attaque_sournoise"), ("frappes", "manoeuvre"),
            ("murmures", "manifestation"), ("psioni", "manifestation"), ("psychique", "manifestation"),
            ("decharge elementaire", "ecole_evocation"), ("elementaire", "ecole_evocation"),
            ("main de mage", "ecole_invocation"), ("guidage", "metamagie"), ("ruse", "metamagie"),
            ("savoir-faire", "rune"), ("bastion", "aura"), ("equilibre", "chance"), ("chute ralentie", "familier"),
            ("deplacement", "foncer"), ("pirouettes", "esquiver"), ("branches", "compagnon"),
            ("force vivifiante", "regeneration"), ("aigle", "familier"), ("vengeur", "ennemi_jure"),
            ("benediction", "conduit_divin"), ("revirement", "ecole_enchantement"), ("torsion", "ecole_enchantement"),
            ("bete", "forme_sauvage"), ("morsure", "forme_sauvage"), ("griffes", "rage"), ("fioriture", "manoeuvre"),
            ("moulinet", "riposte"), ("bouclier", "parade"), ("champ protecteur", "aura"), ("psi", "manifestation"),
            ("illusoire", "ecole_illusion"), ("echo", "ecole_illusion"), ("tempete", "effet_foudre"),
            ("ouragan", "effet_foudre"), ("feu", "effet_feu"), ("flamme", "effet_feu"), ("spores", "effet_poison"),
            ("fongi", "effet_poison"), ("chant", "inspiration_bardique"), ("esprit", "familier"),
            ("totem", "compagnon"), ("lames psychiques", "manifestation"), ("tombe", "ecole_necromancie"),
            ("mort", "ecole_necromancie"), ("geants", "grandeur"), ("frenesie", "rage"), ("canon", "objet_baguette"),
            ("defenseur d.acier", "compagnon"), ("conscience magique", "ecole_divination"), ("magie", "metamagie"),
            ("conjuration", "ecole_invocation"), ("transposition", "invocation_creature"), ("lien", "compagnon"),
            ("etoil", "chance"), ("chien", "compagnon")]

HEALING = ("imposition", "second souffle", "guerison", "baume", "plenitude", "main de guerison", "lumiere guerisseuse",
           "soins", "force vivifiante")


def _find(name: str, table) -> str:
    n = norm(name)
    return next((icon for key, icon in table if re.search(key, n)), "")


def tile_icon(x: dict) -> tuple[str, str, str]:
    """(genre, nom, catégorie) de l'icône d'une tuile de `Engine.turn_actions()` (ou d'une action d'arme)."""
    tid, name, group = x.get("id", ""), x.get("nom", ""), x.get("groupe", "")
    if tid.startswith("sort:") or group == "magie" and x.get("sort"):
        return "sort", (x.get("sort") or tid[5:]), ""
    if tid.startswith("classe:manoeuvre"):              # manœuvres du Maître de guerre
        return "icone", "manoeuvre", "attaque"
    if tid.startswith("arme_action:"):
        return "icone", _find(x.get("arme", name), WEAPONS) or "attaque_generique", "attaque"
    if group == "attaques":
        weapon = name.split("—", 1)[-1]
        return "icone", _find(weapon, WEAPONS) or _find(name, FEATURES) or "attaque_generique", "attaque"
    if group == "generiques":
        return "icone", _find(name, COMMON) or "type_action", "commune"
    if group == "objets":
        return "icone", _find(name, ITEMS) or "objet", "objet"
    if tid.startswith("bete:"):                        # attaques de la forme de bête
        return "icone", "forme_sauvage", "attaque"
    healing = any(k in norm(name) for k in HEALING)
    icon = _find(name, FEATURES)
    if x.get("type") == "Réaction" or group == "reactions":
        if norm(name).startswith("attaque d'opportunite"):
            return "icone", "attaque_opportunite", "reaction"
        return "icone", icon or "type_reaction", "soins" if healing else "reaction"
    if healing:
        return "icone", icon or "effet_soins", "soins"
    if x.get("origine") == "race":
        return "icone", icon or "capacite_espece", "capacite"
    return "icone", icon or "capacite_classe", "capacite"
