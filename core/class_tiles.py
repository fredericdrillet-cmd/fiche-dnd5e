"""
Tuiles d'actions de classe et de sous-classe (v39) — Manuel des joueurs, Xanathar, Tasha.

Complète data/Actions_Classes.json (actions de base : Rage, Ki, Second souffle, Châtiment…) avec les capacités
ACTIVES de chaque classe et sous-classe du corpus : action, action bonus, réaction ou capacité « Spécial » (ajoutée à
une attaque, un jet). Chaque entrée devient une tuile cliquable de l'onglet Combat et suit le flux unifié :

    - ressource propre (« uses ») : compteur créé automatiquement, décompté à l'usage, tuile grisée à 0 ;
      total = entier, « BM » (bonus de maîtrise), « MOD:Carac » (modificateur, minimum 1), « NIV » (niveau de classe) ;
    - ressource de classe existante (« cout ») : rage, ki, points de sorcellerie, dés de supériorité, inspiration…
    - dégâts / soins (« degats », éventuellement par paliers de niveau de classe), jet de sauvegarde (« js » : DD
      calculé), attaque avec l'arme équipée (« attaque_arme ») ou arme naturelle (« naturelle »).
Les sous-classes hors corpus (homebrew / autres suppléments) ne sont pas traitées ici.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from .rules import norm

LONG, SHORT = "repos long", "repos court"


def T(tid, nom, icone, classe, sc, niveau, kind, desc, uses=None, recover=LONG, degats="", type_degats="",
      cout=None, effet="", js="", js_carac="", attaque_arme=False, naturelle=None, par_tour=False, requiert="",
      soin=False, ui="", jusqua=0):
    return {"id": "cap:" + tid, "nom": nom, "icone": icone, "classe": classe, "sc": sc, "niveau": niveau,
            "type": kind, "description": desc, "uses": uses, "recover": recover, "degats": degats,
            "type_degats": type_degats, "cout": cout or {}, "effet": effet, "js": js, "js_carac": js_carac,
            "attaque_arme": attaque_arme, "naturelle": naturelle, "par_tour": par_tour, "requiert_effet": requiert,
            "soin": soin, "ui": ui, "jusqua": jusqua}


INSP = {"ressource": "inspiration", "n": 1}
KI = {"ressource": "ki", "n": 1}
SORC = {"ressource": "sorcellerie", "n": 1}
CONDUIT = {"ressource": "conduit", "n": 1}

TILES = [
    # ================================================================== BARBARE
    T("frenesie", "Attaque de frénésie", "😡", "Barbare", "berserker", 3, "Action bonus",
      "En rage frénétique : une attaque d'arme au corps à corps par une action bonus à chacun de vos tours (un niveau "
      "d'épuisement à la fin de la rage).", attaque_arme=True, requiert="rage"),
    T("presence_intimidante", "Présence intimidante", "😱", "Barbare", "berserker", 10, "Action",
      "Une créature à 9 m doit réussir un JS de Sagesse ou être effrayée jusqu'à la fin de votre prochain tour.",
      js="CHA", js_carac="Sagesse"),
    T("represailles", "Représailles", "↩️", "Barbare", "berserker", 14, "Réaction",
      "Quand une créature à 1,50 m vous inflige des dégâts : une attaque d'arme au corps à corps contre elle.",
      attaque_arme=True),
    T("aigle_foncer", "Esprit de l'aigle : Foncer", "🦅", "Barbare", "aigle", 3, "Action bonus",
      "En rage : Foncer par une action bonus ; les attaques d'opportunité contre vous ont le désavantage.",
      effet="foncer", requiert="rage"),
    T("bouclier_esprit", "Bouclier spirituel", "👻", "Barbare", "gardien ancestral", 6, "Réaction",
      "En rage, quand une créature à 9 m subit des dégâts : réduisez-les du résultat des dés.",
      degats={6: "2d6", 10: "3d6", 14: "4d6"}, requiert="rage"),
    T("aura_desert", "Aura de tempête : désert", "🔥", "Barbare", "desert", 3, "Action bonus",
      "En rage : chaque autre créature de votre choix dans l'aura de 3 m subit des dégâts de feu.",
      degats={3: "2", 5: "3", 10: "4", 15: "5", 20: "6"}, type_degats="feu", requiert="rage"),
    T("aura_mer", "Aura de tempête : mer", "🌊", "Barbare", "mer", 3, "Action bonus",
      "En rage : une créature de votre choix dans l'aura (3 m) fait un JS de Dextérité, foudre, moitié si réussite.",
      degats={3: "1d6", 10: "2d6", 15: "3d6", 20: "4d6"}, type_degats="foudre", js="CON", js_carac="Dextérité",
      requiert="rage"),
    T("aura_toundra", "Aura de tempête : toundra", "❄️", "Barbare", "toundra", 3, "Action bonus",
      "En rage : chaque créature de votre choix dans l'aura (3 m) gagne des PV temporaires.",
      degats={3: "2", 5: "3", 10: "4", 15: "5", 20: "6"}, requiert="rage"),
    T("presence_zelee", "Présence zélée", "📯", "Barbare", "zelote", 10, "Action bonus",
      "Jusqu'à 10 créatures à 18 m ont l'avantage aux jets d'attaque et de sauvegarde jusqu'au début de votre "
      "prochain tour.", uses=1),
    T("morsure_bete", "Forme de la bête : morsure", "🦷", "Barbare", "bete", 3, "Action",
      "En rage : attaque de morsure (Force) ; une fois par tour, si vous avez moins de la moitié de vos PV, vous "
      "regagnez des PV égaux à votre bonus de maîtrise.", naturelle=("1d8", "perforant"), requiert="rage"),
    T("griffes_bete", "Forme de la bête : griffes", "🐾", "Barbare", "bete", 3, "Action",
      "En rage : attaque de griffes (Force) ; une fois par tour, une attaque de griffes supplémentaire.",
      naturelle=("1d6", "tranchant"), requiert="rage"),
    T("queue_bete", "Forme de la bête : queue", "🦎", "Barbare", "bete", 3, "Action",
      "En rage : attaque de queue (allonge 3 m, Force) ; réaction : +1d8 à la CA contre une attaque.",
      naturelle=("1d8", "perforant"), requiert="rage"),
    T("conscience_magique", "Conscience magique", "✨", "Barbare", "magie sauvage", 3, "Action",
      "Vous percevez les sorts et objets magiques à 18 m jusqu'à la fin de votre prochain tour.", uses="BM"),
    T("magie_renforcante", "Magie renforçante", "🌟", "Barbare", "magie sauvage", 6, "Action",
      "Une créature : +1d3 aux jets d'attaque et tests pendant 10 minutes, ou elle regagne un emplacement de niveau "
      "1d3 au plus.", uses="BM", degats="1d3"),
    # ================================================================== BARDE
    T("contre_charme", "Contre-charme", "🎶", "Barde", "", 6, "Action",
      "Jusqu'à la fin de votre prochain tour, vous et vos alliés à 9 m avez l'avantage aux JS contre l'état charmé ou "
      "effrayé."),
    T("mots_cinglants", "Mots cinglants", "🗯", "Barde", "savoir", 3, "Réaction",
      "Une créature à 18 m réussit une attaque, un test ou un jet de dégâts : soustrayez le dé d'inspiration.",
      cout=INSP, degats="{INSPIRATION}"),
    T("inspiration_combat", "Inspiration au combat", "⚔️", "Barde", "vaillance", 3, "Spécial",
      "Une créature inspirée ajoute le dé à ses dégâts, ou à sa CA contre une attaque (réaction).", cout=INSP,
      degats="{INSPIRATION}"),
    T("fioriture_defensive", "Fioriture défensive", "🗡", "Barde", "epees", 3, "Action",
      "Quand vous touchez : ajoutez le dé d'inspiration aux dégâts et à votre CA jusqu'au début de votre prochain "
      "tour.", cout=INSP, attaque_arme=True, degats="{INSPIRATION}"),
    T("fioriture_tranchante", "Fioriture tranchante", "🗡", "Barde", "epees", 3, "Action",
      "Quand vous touchez : le dé d'inspiration s'ajoute aux dégâts de la cible et d'une autre créature à 1,50 m.",
      cout=INSP, attaque_arme=True, degats="{INSPIRATION}"),
    T("fioriture_mobile", "Fioriture mobile", "🗡", "Barde", "epees", 3, "Action",
      "Quand vous touchez : ajoutez le dé aux dégâts et repoussez la cible de 1,50 m + le dé (en mètres × 0,3).",
      cout=INSP, attaque_arme=True, degats="{INSPIRATION}"),
    T("manteau_inspiration", "Manteau d'inspiration", "🎭", "Barde", "seduction", 3, "Action bonus",
      "Jusqu'à mod. de Charisme créatures à 18 m gagnent des PV temporaires et peuvent se déplacer (réaction) sans "
      "attaque d'opportunité.", cout=INSP, degats={3: "5", 5: "8", 10: "11", 15: "14"}),
    T("manteau_majeste", "Manteau de majesté", "👑", "Barde", "seduction", 6, "Action bonus",
      "Pendant 1 minute (concentration) : Injonction sans emplacement par une action bonus à chaque tour.", uses=1),
    T("lames_psychiques_barde", "Lames psychiques", "🧠", "Barde", "murmures", 3, "Spécial",
      "Une fois par tour, quand vous touchez : dépensez un dé d'inspiration pour des dégâts psychiques "
      "supplémentaires.", cout=INSP, degats={3: "2d6", 5: "3d6", 10: "5d6", 15: "8d6"}, type_degats="psychique",
      par_tour=True),
    T("paroles_troublantes", "Paroles troublantes", "🗯", "Barde", "eloquence", 3, "Action bonus",
      "Une créature à 18 m soustrait le dé d'inspiration de son prochain jet de sauvegarde.", cout=INSP,
      degats="{INSPIRATION}"),
    T("representation_creation", "Représentation de la création", "🎨", "Barde", "creation", 3, "Action",
      "Créez un objet non magique (valeur ≤ 20 × niveau de barde po).", uses=1),
    T("representation_animee", "Représentation animée", "🪄", "Barde", "creation", 6, "Action",
      "Animez un objet de taille Grande ou moins : il agit à votre initiative (action bonus pour le commander).",
      uses=1),
    # ================================================================== CLERC
    T("intervention_divine", "Intervention divine", "🙏", "Clerc", "", 10, "Action",
      "Implorez l'aide de votre divinité : réussite si d100 ≤ niveau de clerc (automatique au niveau 20) ; 7 jours "
      "d'attente en cas de succès, un repos long sinon.", uses=1, degats="1d100"),
    T("pretre_guerre", "Prêtre de guerre", "⚔️", "Clerc", "guerre", 1, "Action bonus",
      "Après l'action Attaquer : une attaque d'arme supplémentaire.", uses="MOD:Sagesse", attaque_arme=True),
    T("eclat_protecteur", "Éclat protecteur", "💡", "Clerc", "lumiere", 1, "Réaction",
      "Un attaquant à 9 m que vous voyez a le désavantage à son jet d'attaque.", uses="MOD:Sagesse"),
    T("courroux_tempete", "Courroux de la tempête", "⛈", "Clerc", "tempete", 1, "Réaction",
      "Une créature à 1,50 m vous touche : JS de Dextérité, foudre ou tonnerre (moitié si réussite).",
      uses="MOD:Sagesse", degats="2d8", type_degats="foudre ou tonnerre", js="SAG", js_carac="Dextérité"),
    T("benediction_escroc", "Bénédiction de l'escroc", "🎭", "Clerc", "ruse", 1, "Action",
      "Une créature consentante a l'avantage aux tests de Dextérité (Discrétion) pendant 1 heure."),
    T("benediction_forge", "Bénédiction de la forge", "🔨", "Clerc", "forge", 1, "Spécial",
      "Fin d'un repos long : une arme ou une armure devient magique (+1).", uses=1),
    T("yeux_tombe", "Yeux de la tombe", "💀", "Clerc", "tombe", 1, "Action",
      "Vous savez où se trouvent les morts-vivants à 18 m jusqu'à la fin de votre prochain tour.",
      uses="MOD:Sagesse"),
    T("sentinelle_mort", "Sentinelle aux portes de la mort", "⚰️", "Clerc", "tombe", 6, "Réaction",
      "Un coup critique contre vous ou un allié à 9 m devient un coup normal.", uses="MOD:Sagesse"),
    T("lien_enhardissant", "Lien enhardissant", "🕊", "Clerc", "paix", 1, "Action",
      "Jusqu'à BM créatures liées ajoutent 1d4 à un jet par tour pendant 10 minutes.", uses="BM", degats="1d4"),
    T("lien_protecteur", "Lien protecteur", "🕊", "Clerc", "paix", 6, "Réaction",
      "Une créature liée subit des dégâts : téléportez-vous à 1,50 m d'elle et subissez les dégâts à sa place."),
    # ================================================================== DRUIDE
    T("forme_sauvage", "Forme sauvage", "🐺", "Druide", "", 2, "Action",
      "Prenez la forme d'une bête (FP selon votre niveau ; action bonus pour le Cercle de la Lune).",
      cout={"ressource": "forme", "n": 1, "verif_seul": True}, ui="forme_sauvage"),
    T("guerison_lune", "Forme sauvage de combat : soins", "🌙", "Druide", "lune", 2, "Action bonus",
      "Sous forme sauvage : dépensez un emplacement pour regagner 1d8 PV par niveau d'emplacement.",
      cout={"emplacement": True}, degats="{SOINS_LUNE}", soin=True),
    T("baume_cour", "Baume de la Cour d'été", "🌸", "Druide", "reves", 2, "Action bonus",
      "Dépensez des d6 de la réserve (niveau de druide) : une créature à 36 m regagne ces PV (+1 PV temporaire par "
      "dé).", uses="NIV", degats="1d6", soin=True),
    T("totem_esprit", "Esprit totem", "🐻", "Druide", "berger", 2, "Action bonus",
      "Esprit de l'ours (PV temporaires 5 + niveau), du faucon (avantage par réaction) ou de la licorne (soins) "
      "pendant 1 minute.", uses=1, recover=SHORT),
    T("forme_etoilee", "Forme étoilée", "✨", "Druide", "astres", 2, "Action bonus",
      "Dépensez une Forme sauvage : Archer (attaque de sort à distance, 1d8 + mod. de Sagesse radiants), Calice "
      "(soins +1d8 + Sag) ou Dragon (10 minimum aux tests d'Int/Sag et JS de concentration).",
      cout={"ressource": "forme", "n": 1}, degats="1d8+{MOD_SAG}", type_degats="radiant"),
    T("halo_spores", "Halo de spores", "🍄", "Druide", "spores", 2, "Réaction",
      "Une créature entre ou commence son tour à 3 m : JS de Constitution ou dégâts nécrotiques.",
      degats={2: "1d4", 6: "1d6", 10: "1d8", 14: "1d10"}, type_degats="nécrotique", js="SAG",
      js_carac="Constitution"),
    T("entite_symbiotique", "Entité symbiotique", "🍄", "Druide", "spores", 2, "Action",
      "Dépensez une Forme sauvage : 4 PV temporaires par niveau de druide ; Halo de spores doublé et +1d6 "
      "nécrotiques aux attaques au corps à corps pendant 10 minutes.", cout={"ressource": "forme", "n": 1}),
    T("esprit_feu", "Convocation de l'esprit du feu sauvage", "🔥", "Druide", "fournaises", 2, "Action",
      "Dépensez une Forme sauvage : l'esprit apparaît ; les créatures à 3 m font un JS de Dextérité ou subissent 2d6 "
      "dégâts de feu.", cout={"ressource": "forme", "n": 1}, degats="2d6", type_degats="feu", js="SAG",
      js_carac="Dextérité"),
    # ================================================================== ENSORCELEUR (métamagie : option de classe)
    T("ailes_dragon", "Ailes de dragon", "🐉", "Ensorceleur", "draconique", 14, "Action bonus",
      "Des ailes vous poussent : vitesse de vol égale à votre vitesse actuelle."),
    T("marees_chaos", "Marées du chaos", "🎲", "Ensorceleur", "sauvage", 1, "Spécial",
      "Avantage à un jet d'attaque, test ou jet de sauvegarde.", uses=1),
    T("chance_alteree", "Chance altérée", "🎲", "Ensorceleur", "sauvage", 6, "Réaction",
      "Dépensez 2 points de sorcellerie : ±1d4 au jet d'une créature que vous voyez.",
      cout={"ressource": "sorcellerie", "n": 2}, degats="1d4"),
    T("faveur_dieux", "Faveur des dieux", "✝️", "Ensorceleur", "ame divine", 1, "Spécial",
      "Vous ratez un jet de sauvegarde ou une attaque : ajoutez 2d4.", uses=1, recover=SHORT, degats="2d4"),
    T("chien_presage", "Chien de mauvais augure", "🐕", "Ensorceleur", "ombres", 6, "Action bonus",
      "Dépensez 3 points de sorcellerie : un chien d'ombre poursuit une créature à 36 m (vos sorts lui imposent le "
      "désavantage au JS).", cout={"ressource": "sorcellerie", "n": 3}),
    T("pas_ombre", "Marche dans l'ombre", "🌑", "Ensorceleur", "ombres", 14, "Action bonus",
      "Dans la pénombre ou les ténèbres : téléportation jusqu'à 36 m vers un espace dans la pénombre ou les ténèbres."),
    T("magie_tempetueuse", "Magie tempétueuse", "🌪", "Ensorceleur", "tempetes", 1, "Action bonus",
      "Juste avant ou après un sort de niveau 1+ : volez jusqu'à 3 m sans attaque d'opportunité."),
    T("fureur_tempete", "Fureur de la tempête", "⚡", "Ensorceleur", "tempetes", 14, "Réaction",
      "Une créature vous touche au corps à corps : dégâts de foudre égaux à votre niveau d'ensorceleur, JS de Force "
      "ou repoussée de 6 m.", degats="{NIV}", type_degats="foudre", js="CHA", js_carac="Force"),
    T("revelation_chair", "Révélation dans la chair", "🦑", "Ensorceleur", "aberrant", 14, "Action bonus",
      "Dépensez 1+ points de sorcellerie : vol, nage et respiration aquatique, vision des invisibles, ou passage "
      "par les interstices, pendant 10 minutes.", cout=SORC),
    T("retablir_equilibre", "Rétablir l'équilibre", "⚖️", "Ensorceleur", "mecanique", 1, "Réaction",
      "Une créature à 18 m s'apprête à jouer avec avantage ou désavantage : annulez-le.", uses="MOD:Charisme"),
    T("bastion_loi", "Bastion de la loi", "🛡", "Ensorceleur", "mecanique", 6, "Action",
      "Dépensez 1 à 5 points de sorcellerie : une protection de autant de d8 absorbe les dégâts d'une créature.",
      cout=SORC, degats="1d8"),
    # ================================================================== GUERRIER
    T("inflexible", "Inflexible", "🗿", "Guerrier", "", 9, "Spécial",
      "Relancez un jet de sauvegarde raté (vous devez garder le nouveau résultat).",
      uses={9: 1, 13: 2, 17: 3}),
    T("marque_inebranlable", "Marque inébranlable", "🐎", "Guerrier", "cavalier", 3, "Action bonus",
      "Une créature marquée qui a attaqué un autre que vous : attaque d'arme au corps à corps avec avantage, + la "
      "moitié de votre niveau de guerrier en dégâts.", uses="MOD:Force", attaque_arme=True, degats="{DEMI_NIV}"),
    T("manoeuvre_protectrice", "Manœuvre protectrice", "🛡", "Guerrier", "cavalier", 7, "Réaction",
      "Une créature à 1,50 m est attaquée : +1d8 à sa CA contre l'attaque (et résistance si elle touche).",
      uses="MOD:Constitution", degats="1d8"),
    T("esprit_combatif", "Esprit combatif", "🏯", "Guerrier", "samourai", 3, "Action bonus",
      "Avantage à vos jets d'attaque d'arme jusqu'à la fin du tour et PV temporaires.", uses=3,
      degats={3: "5", 10: "10", 15: "15"}),
    T("lien_arme", "Lien avec l'arme : rappel", "🗡", "Guerrier", "chevalier occulte", 3, "Action bonus",
      "Rappelez instantanément une arme liée (même plan), qui apparaît dans votre main."),
    T("magie_guerre", "Magie de guerre", "✨", "Guerrier", "chevalier occulte", 7, "Action bonus",
      "Après un sort mineur lancé par une action : une attaque d'arme (dès le niveau 18, après n'importe quel sort).",
      attaque_arme=True),
    # ================================================================== MOINE (base complétée)
    T("parade_projectiles", "Parade de projectiles", "🏹", "Moine", "", 3, "Réaction",
      "Une attaque d'arme à distance vous touche : réduisez les dégâts de 1d10 + Dex + niveau de moine ; à 0, "
      "relancez le projectile (1 point de ki).", degats="1d10+{MOD_DEX}+{NIV}"),
    T("chute_ralentie", "Chute ralentie", "🪶", "Moine", "", 4, "Réaction",
      "Réduisez les dégâts de chute de 5 × votre niveau de moine.", degats="{CINQ_NIV}"),
    T("plenitude_corps", "Plénitude du corps", "💚", "Moine", "paume", 6, "Action",
      "Vous regagnez 3 × votre niveau de moine en PV.", uses=1, degats="{TROIS_NIV}", soin=True),
    T("pas_ombre_moine", "Pas de l'ombre", "🌑", "Moine", "ombre", 6, "Action bonus",
      "Dans la pénombre ou les ténèbres : téléportation de 18 m ; avantage à la première attaque au corps à corps "
      "avant la fin du tour."),
    T("trait_solaire", "Trait de soleil radieux", "☀️", "Moine", "solaire", 3, "Action",
      "Attaque de sort à distance (Dex) : dé d'arts martiaux + Dex radiants ; 1 point de ki pour en faire deux par "
      "une action bonus.", degats="{ARTS_MARTIAUX}+{MOD_DEX}", type_degats="radiant"),
    T("frappe_arc_ardent", "Frappe en arc ardent", "🔥", "Moine", "solaire", 6, "Action bonus",
      "Après l'action Attaquer : 2 points de ki pour lancer Mains brûlantes (+1 niveau par ki supplémentaire).",
      cout={"ressource": "ki", "n": 2}, degats="3d6", type_degats="feu", js="SAG", js_carac="Dextérité"),
    T("tir_kensei", "Tir du kensei", "🏹", "Moine", "kensei", 3, "Action bonus",
      "Jusqu'à la fin du tour, vos attaques à distance avec une arme de kensei infligent 1d4 dégâts "
      "supplémentaires.", degats="1d4"),
    T("balancement_ivre", "Balancement éméché", "🍶", "Moine", "ivre", 6, "Réaction",
      "Une attaque au corps à corps vous rate : 1 point de ki pour la rediriger vers une autre créature à 1,50 m.",
      cout=KI),
    T("bras_astral", "Bras du moi astral", "👐", "Moine", "astre", 3, "Action bonus",
      "1 point de ki : bras spectraux 10 minutes ; les créatures à 3 m font un JS de Dextérité ou subissent 2 dés "
      "d'arts martiaux de force.", cout=KI, degats="{DEUX_ARTS_MARTIAUX}", type_degats="force", js="SAG",
      js_carac="Dextérité"),
    T("main_guerison", "Main de guérison", "🤲", "Moine", "misericorde", 3, "Action",
      "1 point de ki (ou à la place d'une frappe du Déluge de coups) : une créature regagne dé d'arts martiaux + "
      "Sagesse PV.", cout=KI, degats="{ARTS_MARTIAUX}+{MOD_SAG}", soin=True),
    T("main_souffrance", "Main de souffrance", "🖐", "Moine", "misericorde", 3, "Spécial",
      "Une fois par tour, frappe à mains nues qui touche : 1 point de ki pour dé d'arts martiaux + Sagesse "
      "nécrotiques.", cout=KI, degats="{ARTS_MARTIAUX}+{MOD_SAG}", type_degats="nécrotique", par_tour=True),
    # ================================================================== OCCULTISTE (patrons)
    T("presence_feerique", "Présence féerique", "🧚", "Occultiste", "archifee", 1, "Action",
      "Cube de 3 m : JS de Sagesse ou charmé / effrayé jusqu'à la fin de votre prochain tour.", uses=1,
      recover=SHORT, js="CHA", js_carac="Sagesse"),
    T("fuite_brumeuse", "Fuite brumeuse", "🌫", "Occultiste", "archifee", 6, "Réaction",
      "Vous subissez des dégâts : invisible et téléporté jusqu'à 18 m.", uses=1, recover=SHORT),
    T("chance_tenebres", "Chance du ténébreux", "😈", "Occultiste", "fielon", 6, "Spécial",
      "Ajoutez 1d10 à un test ou un jet de sauvegarde.", uses=1, recover=SHORT, degats="1d10"),
    T("garde_entropique", "Garde entropique", "🌀", "Occultiste", "grand ancien", 6, "Réaction",
      "Une créature vous attaque : désavantage ; si elle rate, avantage à votre prochaine attaque contre elle.",
      uses=1, recover=SHORT),
    T("lumiere_guerisseuse", "Lumière guérisseuse", "☀️", "Occultiste", "celeste", 1, "Action bonus",
      "Dépensez des d6 de la réserve (1 + niveau d'occultiste) : une créature à 18 m regagne ces PV (au plus mod. "
      "de Charisme dés).", uses="NIV+1", degats="1d6", soin=True),
    T("malediction_lame", "Malédiction de la Lame maudite", "🗡", "Occultiste", "lame maudite", 1, "Action bonus",
      "Maudissez une créature à 9 m pendant 1 minute : + bonus de maîtrise aux dégâts contre elle, critique sur 19-20, "
      "et vous regagnez niveau + Charisme PV si elle meurt.", uses=1, recover=SHORT, degats="{BM}"),
    T("don_elementaire", "Don élémentaire", "🧞", "Occultiste", "genie", 6, "Action bonus",
      "Vitesse de vol de 9 m pendant 10 minutes.", uses="BM"),
    T("tentacule_profondeurs", "Tentacule des profondeurs", "🐙", "Occultiste", "insondable", 1, "Action bonus",
      "Tentacule spectral à 18 m pendant 1 minute : attaque de sort au corps à corps, froid, vitesse −3 m.",
      uses="BM", degats={1: "1d8", 10: "2d8"}, type_degats="froid"),
    # ================================================================== PALADIN
    T("toucher_purifiant", "Toucher purifiant", "✋", "Paladin", "", 14, "Action",
      "Mettez fin à un sort affectant vous-même ou une créature consentante touchée.", uses="MOD:Charisme"),
    T("vengeur_implacable", "Vengeur implacable", "⚔️", "Paladin", "vengeance", 7, "Spécial",
      "Après une attaque d'opportunité qui touche : déplacez-vous de la moitié de votre vitesse sans attaque "
      "d'opportunité."),
    T("aura_gardien", "Aura du gardien", "🛡", "Paladin", "redemption", 7, "Réaction",
      "Une créature à 3 m subit des dégâts : vous les subissez à sa place (sans résistance)."),
    T("nimbe_sacre", "Nimbe sacré", "😇", "Paladin", "devotion", 20, "Action",
      "Pendant 1 minute : lumière vive de 9 m, 10 dégâts radiants aux ennemis qui y commencent leur tour, avantage aux "
      "JS contre les sorts des fiélons et morts-vivants.", uses=1, degats="10", type_degats="radiant"),
    T("champion_antique", "Champion antique", "🌳", "Paladin", "anciens", 20, "Action",
      "Pendant 1 minute : 10 PV regagnés au début de chaque tour, sorts de paladin en action bonus, désavantage aux JS "
      "des ennemis à 3 m contre vos sorts et Conduit divin.", uses=1),
    T("ange_vengeur", "Ange vengeur", "👼", "Paladin", "vengeance", 20, "Action",
      "Pendant 1 heure : ailes (vol 18 m) et aura de menace de 9 m (JS de Sagesse ou effrayé).", uses=1),
    T("conquerant_invincible", "Conquérant invincible", "👑", "Paladin", "conquete", 20, "Action",
      "Pendant 1 minute : résistance à tous les dégâts, une attaque supplémentaire, critiques sur 19-20.", uses=1),
    T("legende_vivante", "Légende vivante", "🏆", "Paladin", "gloire", 20, "Action bonus",
      "Pendant 1 minute : avantage aux tests de Charisme, une attaque ratée par tour peut être relancée, JS ratés "
      "relancés (réaction).", uses=1),
    T("reprimande_vigilante", "Réprimande vigilante", "👁", "Paladin", "guetteurs", 15, "Réaction",
      "Vous ou une créature à 9 m réussissez un JS d'Intelligence, Sagesse ou Charisme : la source subit des dégâts de "
      "force.", degats="2d8+{MOD_CHA}", type_degats="force"),
    # ================================================================== RÔDEUR
    T("ennemi_jure", "Ennemi juré", "🎯", "Rôdeur", "", 1, "Spécial",
      "Quand vous touchez : la créature devient votre ennemi juré (concentration, 1 minute) ; +dé aux dégâts une "
      "fois par tour.", uses="BM", degats={1: "1d4", 6: "1d6", 14: "1d8"}, par_tour=True),
    T("tueur_colosses", "Tueur de colosses", "🏹", "Rôdeur", "chasseur", 3, "Spécial",
      "Une fois par tour, contre une créature blessée : +1d8 dégâts.", degats="1d8", par_tour=True),
    T("ordre_compagnon", "Commander le compagnon", "🐾", "Rôdeur", "betes", 3, "Action bonus",
      "Votre compagnon animal effectue l'action Attaquer, Foncer, Se désengager ou Aider."),
    T("embuscade_terrible", "Embusqué redoutable", "🌑", "Rôdeur", "traqueur des tenebres", 3, "Spécial",
      "Premier tour du combat : une attaque d'arme supplémentaire, +1d8 dégâts si elle touche.", degats="1d8",
      attaque_arme=True),
    T("guerrier_planaire", "Guerrier planaire", "🌌", "Rôdeur", "horizon", 3, "Action bonus",
      "Votre prochaine attaque d'arme qui touche ce tour inflige des dégâts de force supplémentaires.",
      degats={3: "1d8", 11: "2d8"}, type_degats="force"),
    T("pas_ethere", "Pas éthéré", "👻", "Rôdeur", "horizon", 7, "Action bonus",
      "Plan éthéré jusqu'à la fin du tour (Forme éthérée).", uses=1, recover=SHORT),
    T("proie_tueur", "Proie du tueur", "🎯", "Rôdeur", "tueur de monstres", 3, "Action bonus",
      "Désignez une créature à 18 m : +1d6 dégâts la première fois que vous la touchez à chaque tour.", degats="1d6"),
    T("nemesis_mages", "Némésis des lanceurs", "🚫", "Rôdeur", "tueur de monstres", 11, "Réaction",
      "Une créature lance un sort ou se téléporte : JS de Sagesse ou l'action échoue.", uses=1, recover=SHORT,
      js="SAG", js_carac="Sagesse"),
    T("essaim", "Essaim rassemblé", "🐝", "Rôdeur", "nuees", 3, "Spécial",
      "Une fois par tour, quand vous touchez : +1d6 perforants, repousser de 4,50 m (JS de Force) ou vous déplacer "
      "de 1,50 m.", degats={3: "1d6", 11: "1d8"}, type_degats="perforant", par_tour=True),
    T("frappes_terribles", "Frappes terribles", "🧚", "Rôdeur", "feerique", 3, "Spécial",
      "Une fois par tour par créature, quand vous touchez : dégâts psychiques supplémentaires.",
      degats={3: "1d4", 11: "1d6"}, type_degats="psychique", par_tour=True),
    T("torsion_seduisante", "Torsion séduisante", "🌀", "Rôdeur", "feerique", 7, "Réaction",
      "Une créature réussit un JS contre charme / peur : une autre créature à 36 m fait un JS de Sagesse ou est "
      "charmée / effrayée.", js="SAG", js_carac="Sagesse"),
    # ================================================================== ROUBLARD
    T("coup_chance", "Coup de chance", "🍀", "Roublard", "", 20, "Spécial",
      "Une attaque ratée touche, ou un test raté devient un 20.", uses=1, recover=SHORT),
    T("mains_lestes", "Mains lestes", "🫳", "Roublard", "voleur", 3, "Action bonus",
      "Action astucieuse : Escamotage, outils de voleur ou Utiliser un objet."),
    T("maitre_tactique", "Maître tacticien", "🧠", "Roublard", "conspirateur", 3, "Action bonus",
      "Action Aider par une action bonus, sur une créature jusqu'à 9 m."),
    T("escarmoucheur", "Escarmoucheur", "🏃", "Roublard", "eclaireur", 3, "Réaction",
      "Un ennemi termine son tour à 1,50 m : déplacez-vous de la moitié de votre vitesse sans attaque "
      "d'opportunité."),
    T("combat_perspicace", "Combat perspicace", "👁", "Roublard", "enqueteur", 3, "Action bonus",
      "Sagesse (Perspicacité) contre Charisme (Tromperie) : Attaque sournoise contre elle sans avantage pendant "
      "1 minute."),
    T("panache", "Panache", "🎩", "Roublard", "bretteur", 9, "Action",
      "Charisme (Persuasion) contre Sagesse (Perspicacité) : un ennemi a le désavantage contre les autres que vous."),
    T("plaintes_tombe", "Plaintes d'outre-tombe", "👻", "Roublard", "fantome", 3, "Spécial",
      "Juste après une Attaque sournoise : une seconde créature à 9 m subit la moitié des dés d'Attaque sournoise en "
      "dégâts nécrotiques.", uses="BM", degats="{DEMI_SOURNOISE}", type_degats="nécrotique"),
    # ================================================================== MAGICIEN
    T("protection_projetee", "Protection projetée", "🛡", "Magicien", "abjuration", 6, "Réaction",
      "Une créature à 9 m subit des dégâts : votre Protection arcanique les absorbe."),
    T("presage", "Présage", "🔮", "Magicien", "divination", 2, "Spécial",
      "Remplacez un jet d'attaque, de sauvegarde ou un test par un des d20 tirés à l'aube.",
      uses={2: 2, 14: 3}, degats="1d20"),
    T("regard_hypnotique", "Regard hypnotique", "😵", "Magicien", "enchantement", 2, "Action",
      "Une créature à 1,50 m : JS de Sagesse ou charmée (neutralisée, vitesse 0) jusqu'à la fin de votre prochain "
      "tour.", js="INT", js_carac="Sagesse"),
    T("charme_instinctif", "Charme instinctif", "💫", "Magicien", "enchantement", 6, "Réaction",
      "Une créature à 9 m vous attaque : JS de Sagesse ou elle vise la créature la plus proche.", uses=1,
      js="INT", js_carac="Sagesse"),
    T("moi_illusoire", "Moi illusoire", "🪞", "Magicien", "illusion", 10, "Réaction",
      "Une créature vous attaque : un double illusoire s'interpose, l'attaque rate automatiquement.", uses=1,
      recover=SHORT),
    T("conjuration_mineure", "Conjuration mineure", "📦", "Magicien", "invocation", 2, "Action",
      "Faites apparaître un objet inanimé (≤ 1 m, ≤ 5 kg) pendant 1 heure."),
    T("transposition", "Transposition bienveillante", "🔄", "Magicien", "invocation", 6, "Action",
      "Téléportation jusqu'à 9 m, ou échange de place avec une créature consentante.", uses=1),
    T("deviation_arcanique", "Déviation arcanique", "🛡", "Magicien", "guerre", 2, "Réaction",
      "Touché par une attaque ou JS raté : +2 à la CA ou +4 au JS (puis seulement des sorts mineurs jusqu'à la fin "
      "de votre prochain tour)."),
    T("esprit_manifeste", "Esprit manifesté", "📜", "Magicien", "scribe", 6, "Action bonus",
      "L'esprit de votre grimoire apparaît (9 m) ; vos sorts peuvent partir de lui.", uses="BM"),
    # ================================================================== ARTIFICIER
    T("eclair_genie", "Éclair de génie", "💡", "Artificier", "", 7, "Réaction",
      "Une créature à 9 m fait un test ou un JS : ajoutez votre mod. d'Intelligence.", uses="MOD:Intelligence",
      degats="{MOD_INT}"),
    T("elixir", "Élixir expérimental", "🧪", "Artificier", "alchimiste", 3, "Action",
      "Créez un élixir aléatoire (soins, rapidité, résilience, audace, vol, transformation).", uses=1,
      degats="1d6"),
    T("champ_defensif", "Champ défensif", "🛡", "Artificier", "armurier", 3, "Action bonus",
      "Modèle Gardien : PV temporaires égaux à votre niveau d'artificier.", uses="BM", degats="{NIV}"),
    T("canon_occulte", "Canon occulte", "💥", "Artificier", "artilleur", 3, "Action",
      "Créez un canon (Lance-flammes 2d8 feu JS Dex, Baliste de force 2d8 force, Protecteur 1d8 + Int PV "
      "temporaires) — une fois par repos long, ou un emplacement de sort.", uses=1, degats={3: "2d8", 15: "3d8"},
      type_degats="feu ou force", js="INT", js_carac="Dextérité"),
    T("defenseur_acier", "Commander le défenseur d'acier", "🤖", "Artificier", "forgeur", 3, "Action bonus",
      "Le défenseur d'acier effectue une action (Attaquer, Foncer, Se désengager, Esquiver, Aider)."),
    T("decharge_arcanique", "Décharge arcanique", "⚡", "Artificier", "forgeur", 9, "Spécial",
      "Quand vous ou le défenseur touchez : +2d6 force, ou une créature à 9 m regagne 2d6 PV.",
      uses="MOD:Intelligence", degats={9: "2d6", 15: "4d6"}, type_degats="force", par_tour=True),
]

# Métamagie (Ensorceleur) : option de classe choisie, une tuile par option, coût en points de sorcellerie
METAMAGIC = {
    "Sort prudent": (1, "Jusqu'à mod. de Charisme créatures réussissent automatiquement le JS du sort."),
    "Sort distant": (1, "Portée doublée (contact : 9 m)."),
    "Sort amplifié": (1, "Relancez jusqu'à mod. de Charisme dés de dégâts."),
    "Sort étendu": (1, "Durée doublée (24 heures maximum)."),
    "Sort intensifié": (3, "Une cible a le désavantage à son premier JS contre le sort."),
    "Sort accéléré": (2, "Temps d'incantation d'une action -> une action bonus."),
    "Sort discret": (1, "Ni composante verbale ni somatique."),
    "Sort jumeau": (1, "Une seconde cible (coût = niveau du sort, 1 pour un sort mineur)."),
    "Sort guidé": (2, "Relancez le d20 d'une attaque de sort ratée (Tasha)."),
    "Sort transmuté": (1, "Change le type de dégâts (acide, froid, feu, foudre, poison, tonnerre) (Tasha)."),
}


def metamagic_known(level: int) -> int:
    return 0 if level < 3 else 2 if level < 10 else 3 if level < 17 else 4


def _tier(value, level: int):
    """Valeur par paliers {niveau: valeur} : la plus haute atteinte."""
    if isinstance(value, dict):
        best = max((k for k in value if k <= level), default=None)
        return value[best] if best is not None else ""
    return value


class ClassTilesMixin:
    """Mélangé à Engine : tuiles d'aptitudes actives des classes et sous-classes (voir TILES)."""

    def _tile_level(self, t: dict) -> int:
        e = self.ch.find_class(t["classe"])
        if not e or e["niveau"] < t["niveau"]:
            return 0
        if t["sc"] and t["sc"] not in norm(e.get("sous_classe", "")):
            return 0
        return e["niveau"]

    def _uses_total(self, t: dict, lvl: int) -> Optional[int]:
        u = _tier(t["uses"], lvl)
        if u is None or u == "":
            return None
        if isinstance(u, int):
            return u
        if u == "BM":
            return self.prof
        if u.startswith("MOD:"):
            return max(1, self.mod(u[4:]))
        if u.startswith("NIV"):
            return lvl + int(u[4:] or 0) if "+" in u else lvl
        return None

    def class_tile_trackers(self) -> list[dict]:
        out = []
        for t in TILES:
            lvl = self._tile_level(t)
            total = self._uses_total(t, lvl) if lvl else None
            if lvl and total is not None:
                out.append({"key": t["id"], "label": t["nom"], "total": total, "kind": "conduit",
                            "recover": t["recover"], "info": "{} utilisation{} — récupération au {}".format(
                                total, "s" * (total > 1), t["recover"]), "where": "combat", "de": ""})
        return out

    def class_tile_short_rest_keys(self) -> list[str]:
        return [t["key"] for t in self.class_tile_trackers() if t["recover"] == SHORT]

    def _tile_context(self, t: dict, lvl: int) -> dict:
        rogue = self.class_level("Roublard")
        ma = R_martial(self.class_level("Moine"))
        return {"BM": str(self.prof), "NIV": str(lvl), "DEMI_NIV": str(lvl // 2), "TROIS_NIV": str(3 * lvl),
                "CINQ_NIV": str(5 * lvl), "MOD_DEX": str(self.mod("Dextérité")),
                "MOD_SAG": str(self.mod("Sagesse")), "MOD_INT": str(self.mod("Intelligence")),
                "MOD_CHA": str(self.mod("Charisme")),
                "DEMI_SOURNOISE": "{}d6".format(max(1, math.ceil(math.ceil(rogue / 2) / 2))) if rogue else "1d6",
                "DEUX_ARTS_MARTIAUX": "2d{}".format(ma), "SOINS_LUNE": "{}d8".format(
                    max(1, (self.smite_levels() or [1])[0]))}

    def class_tile_actions(self) -> list[dict]:
        out = []
        for t in TILES:
            lvl = self._tile_level(t)
            if not lvl:
                continue
            ctx = self._tile_context(t, lvl)
            dmg = str(_tier(t["degats"], lvl) or "")
            dmg = re.sub(r"\{([A-Z_]+)\}", lambda m: ctx.get(m.group(1), "{" + m.group(1) + "}"), dmg)
            desc = t["description"]
            if t["js"]:
                ab = {"CHA": "Charisme", "SAG": "Sagesse", "INT": "Intelligence", "CON": "Constitution"}[t["js"]]
                desc += " (DD {} : 8 + maîtrise + mod. de {})".format(8 + self.prof + self.mod(ab), ab)
            cost = dict(t["cout"]) if t["cout"] else ({"ressource": t["id"], "n": 1} if self._uses_total(t, lvl)
                                                       is not None else {})
            kind = t["type"]
            if t["id"] == "cap:forme_sauvage" and "lune" in norm((self.ch.find_class("Druide") or {}).get(
                    "sous_classe", "")):
                kind = "Action bonus"                    # Cercle de la Lune : Forme sauvage de combat
            a = {"id": t["id"], "nom": t["nom"], "icone": t["icone"], "classe": t["classe"], "sous_classe": "",
                 "niveau": t["niveau"], "type": kind, "cout": cost, "jet": "degats" if dmg else "aucun",
                 "degats": dmg, "type_degats": t["type_degats"], "description": desc, "effet": t["effet"],
                 "soin": t["soin"], "par_tour": t["par_tour"], "attaque_arme": t["attaque_arme"],
                 "requiert_effet": t["requiert_effet"], "ui": t["ui"], "origine_cap": True}
            if t["naturelle"]:
                a["naturelle"] = t["naturelle"]
                a["attaque_arme"] = True
            out.append(a)
        out += self.metamagic_actions()
        return out

    # ------------------------------------------------------------------ Métamagie
    def metamagic_table(self) -> dict:
        """Options de Métamagie de l'édition de la fiche {nom: (coût, description)}."""
        view = getattr(self.db, "metamagic_2024", None)
        table = view() if (view and self.sheet_edition == 2024) else None
        return table or METAMAGIC

    def metamagic_known_count(self, lvl: int) -> int:
        if self.sheet_edition == 2024:                   # 2024 : 2 au niveau 2, 4 au niveau 10, 6 au niveau 17
            return 0 if lvl < 2 else 2 if lvl < 10 else 4 if lvl < 17 else 6
        return metamagic_known(lvl)

    def metamagic_option_set(self) -> Optional[dict]:
        lvl = self.class_level("Ensorceleur")
        if self.metamagic_known_count(lvl) == 0:
            return None
        return {"key": "metamagie", "label": "Options de métamagie (Ensorceleur)", "total": self.metamagic_known_count(lvl),
                "options": {n: "{} point{} de sorcellerie — {}".format(c, "s" * (c > 1), d)
                            for n, (c, d) in self.metamagic_table().items()},
                "chosen": list((self.ch.options_classe or {}).get("metamagie", []))}

    def chosen_metamagic(self) -> list[str]:
        table = self.metamagic_table()
        return [n for n in (self.ch.options_classe or {}).get("metamagie", []) if n in table] \
            if self.metamagic_known_count(self.class_level("Ensorceleur")) else []

    def metamagic_actions(self) -> list[dict]:
        out = []
        for name in self.chosen_metamagic():
            cost, desc = self.metamagic_table()[name]
            out.append({"id": "meta:" + norm(name).replace(" ", "_"), "nom": "Métamagie : " + name, "icone": "🔮",
                        "classe": "Ensorceleur", "sous_classe": "", "niveau": 3, "type": "Spécial",
                        "cout": {"ressource": "sorcellerie", "n": cost}, "jet": "aucun", "degats": "",
                        "type_degats": "", "description": desc + " À utiliser en lançant le sort.", "effet": ""})
        return out


def R_martial(level: int) -> int:
    from . import rules as R
    return R.martial_arts_die(level) if level else 4
