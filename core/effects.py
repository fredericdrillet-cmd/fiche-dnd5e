"""
Bibliothèque de buffs, débuffs, états, auras et aptitudes de D&D 5e — logique pure (aucune dépendance Qt).

Chaque effet est un dict :
    nom, icone, categorie (une valeur de CATEGORIES), source, duree, concentration, description,
    mods (facultatif) : ca, vitesse_mult, vitesse_bonus (m), attaque, js, tests, degats,
                        resistances (liste), notes (liste)
Les descriptions sont des paraphrases ; les distances sont en mètres.
"""
from __future__ import annotations

import html
import unicodedata

CATEGORIES = ["Bonus", "Malus", "État", "Aura", "Aptitude"]

EFFECTS: dict[str, dict] = {}

_PHB = "État (PHB)"
_IMM = "Immersion (inspiré de BG3)"


def _e(key, nom, icone, categorie, source, duree, description, concentration=False, **mods) -> None:
    assert categorie in CATEGORIES, categorie
    assert key not in EFFECTS, key
    EFFECTS[key] = {"nom": nom, "icone": icone, "categorie": categorie, "source": source,
                    "duree": duree, "concentration": concentration, "description": description,
                    "mods": mods}


def _sort(niv: int, nom: str) -> str:
    return f"Tour de magie ({nom})" if niv == 0 else f"Sort de niveau {niv} ({nom})"


# ======================================================================================
# États officiels (PHB)
# ======================================================================================
_e("a_terre", "À terre", "🛌", "État", _PHB, "Jusqu'à ce qu'on se relève",
   "La créature ne peut que ramper (chaque mètre parcouru en coûte un de plus) ou se relever, ce qui "
   "consomme la moitié de sa vitesse. Elle a le désavantage à ses jets d'attaque. Les attaques contre "
   "elle ont l'avantage si l'attaquant est à 1,5 m, le désavantage sinon.",
   attaque="désavantage",
   notes=["Se relever coûte la moitié de la vitesse", "Ramper : coût de déplacement doublé",
          "Attaques au contact contre elle : avantage ; à distance : désavantage"])
_e("agrippe", "Agrippé", "🤼", "État", _PHB, "Jusqu'à libération",
   "La vitesse de la créature tombe à 0 et ne peut bénéficier d'aucun bonus. L'état prend fin si "
   "l'agrippeur est neutralisé ou si un effet éloigne la créature hors de son allonge. Elle peut "
   "utiliser une action pour tenter de se libérer.",
   vitesse_mult=0.0, notes=["Action : test d'Athlétisme ou d'Acrobaties (ou JS) pour se libérer"])
_e("assourdi", "Assourdi", "🔇", "État", _PHB, "Variable",
   "La créature n'entend rien et rate automatiquement tout test de caractéristique qui repose sur l'ouïe.",
   notes=["Échec automatique aux tests basés sur l'ouïe", "Ne peut pas entendre les composantes verbales ni les ordres"])
_e("aveugle", "Aveuglé", "🙈", "État", _PHB, "Variable",
   "La créature ne voit rien et rate automatiquement tout test qui repose sur la vue. Ses jets "
   "d'attaque ont le désavantage et ceux effectués contre elle ont l'avantage.",
   attaque="désavantage", notes=["Échec automatique aux tests basés sur la vue", "Attaques contre elle : avantage"])
_e("charme", "Charmé", "💞", "État", _PHB, "Variable",
   "La créature ne peut ni attaquer son charmeur ni le cibler avec des capacités ou effets nuisibles. "
   "Le charmeur a l'avantage à ses tests de caractéristique pour interagir socialement avec elle.",
   notes=["Ne peut pas attaquer le charmeur", "Le charmeur a l'avantage aux tests sociaux contre elle"])
_e("effraye", "Effrayé", "😱", "État", _PHB, "Variable",
   "Tant que la source de sa peur est dans son champ de vision, la créature a le désavantage à ses "
   "tests de caractéristique et jets d'attaque. Elle ne peut pas se rapprocher volontairement de cette source.",
   attaque="désavantage", tests="désavantage",
   notes=["Ne peut pas se rapprocher de la source de la peur", "Désavantage seulement si la source est visible"])
_e("empoisonne", "Empoisonné", "🤢", "État", _PHB, "Variable",
   "La créature a le désavantage à ses jets d'attaque et à ses tests de caractéristique.",
   attaque="désavantage", tests="désavantage")
_e("entrave", "Entravé", "⛓️", "État", _PHB, "Jusqu'à libération",
   "La vitesse de la créature tombe à 0. Ses jets d'attaque ont le désavantage, ceux effectués contre "
   "elle ont l'avantage, et elle a le désavantage à ses jets de sauvegarde de Dextérité.",
   vitesse_mult=0.0, attaque="désavantage",
   notes=["Désavantage aux JS de Dextérité", "Attaques contre elle : avantage"])
_e("etourdi", "Étourdi", "💫", "État", _PHB, "Variable",
   "La créature est neutralisée, ne peut plus se déplacer et ne parle que de façon hésitante. Elle rate "
   "automatiquement ses JS de Force et de Dextérité, et les attaques contre elle ont l'avantage.",
   vitesse_mult=0.0,
   notes=["Neutralisée (ni action ni réaction)", "Échec automatique aux JS de Force et Dextérité",
          "Attaques contre elle : avantage"])
_e("neutralise", "Neutralisé (incapable d'agir)", "🚫", "État", _PHB, "Variable",
   "La créature ne peut effectuer ni action, ni action bonus, ni réaction. Sa concentration est rompue.",
   notes=["Aucune action, action bonus ni réaction"])
_e("inconscient", "Inconscient", "😵", "État", _PHB, "Variable",
   "La créature est neutralisée, ne peut ni bouger ni parler, n'a pas conscience de son environnement, "
   "lâche ce qu'elle tient et tombe À terre. Elle rate automatiquement ses JS de Force et de Dextérité ; "
   "les attaques contre elle ont l'avantage et toute attaque qui la touche à 1,5 m est un coup critique.",
   vitesse_mult=0.0,
   notes=["Neutralisée et À terre", "Échec automatique aux JS de Force et Dextérité",
          "Coup critique automatique si touchée à 1,5 m"])
_e("invisible", "Invisible", "👻", "État", _PHB, "Variable",
   "La créature ne peut être vue sans magie ou sens spécial ; pour se cacher, elle est considérée comme "
   "dans une zone à visibilité nulle. Ses jets d'attaque ont l'avantage et ceux effectués contre elle "
   "ont le désavantage.",
   attaque="avantage", notes=["Attaques contre elle : désavantage"])
_e("paralyse", "Paralysé", "🧊", "État", _PHB, "Variable",
   "La créature est neutralisée et ne peut ni bouger ni parler. Elle rate automatiquement ses JS de Force "
   "et de Dextérité ; les attaques contre elle ont l'avantage et toute attaque qui la touche à 1,5 m est "
   "un coup critique.",
   vitesse_mult=0.0,
   notes=["Neutralisée", "Échec automatique aux JS de Force et Dextérité", "Coup critique automatique si touchée à 1,5 m"])
_e("petrifie", "Pétrifié", "🗿", "État", _PHB, "Variable",
   "La créature et son équipement non magique sont changés en substance inanimée ; son poids est "
   "multiplié par dix et elle cesse de vieillir. Elle est neutralisée, rate ses JS de Force et de "
   "Dextérité, et les attaques contre elle ont l'avantage. Elle résiste à tous les dégâts et est immunisée "
   "contre le poison et la maladie (ceux déjà présents sont suspendus).",
   vitesse_mult=0.0, resistances=["tous les dégâts"],
   notes=["Neutralisée", "Immunité : poison et maladie", "Échec automatique aux JS de Force et Dextérité"])

_EXH = [
    ("Désavantage aux tests de caractéristique.", dict(tests="désavantage")),
    ("Vitesse divisée par deux.", dict(tests="désavantage", vitesse_mult=0.5)),
    ("Désavantage aux jets d'attaque et aux jets de sauvegarde.",
     dict(tests="désavantage", vitesse_mult=0.5, attaque="désavantage", js="désavantage")),
    ("Maximum de points de vie divisé par deux.",
     dict(tests="désavantage", vitesse_mult=0.5, attaque="désavantage", js="désavantage",
          notes=["PV maximum divisés par deux"])),
    ("Vitesse réduite à 0.",
     dict(tests="désavantage", vitesse_mult=0.0, attaque="désavantage", js="désavantage",
          notes=["PV maximum divisés par deux"])),
    ("Mort.", dict(vitesse_mult=0.0, notes=["La créature meurt"])),
]
for _lvl, (_txt, _mods) in enumerate(_EXH, start=1):
    _e(f"epuisement_{_lvl}", f"Épuisement {_lvl}", "🥱", "État", _PHB, "Jusqu'à un repos long (−1 niveau)",
       f"Niveau {_lvl} : {_txt} Les effets des niveaux inférieurs s'appliquent aussi. Un repos long "
       "réduit l'épuisement d'un niveau, à condition d'avoir mangé et bu.", **_mods)

# ======================================================================================
# États d'immersion (jeu vidéo / table)
# ======================================================================================
_e("alcoolise", "Alcoolisé (ivre)", "🍺", "État", _IMM, "1 heure par verre au-delà du mod. de Con",
   "La créature a le désavantage aux tests de Dextérité et de Sagesse (Perception, Perspicacité, Discrétion…) "
   "mais l'avantage aux JS contre l'état Effrayé. Elle gagne 1d4 PV temporaires à chaque verre. Un JS de "
   "Constitution DD 10 + nombre de verres réussi après un repos court dissipe l'ivresse.",
   notes=["Désavantage aux tests de Dextérité et de Sagesse", "Avantage aux JS contre Effrayé"])
_e("saignement", "Saignement", "🩸", "Malus", _IMM, "1 minute",
   "La créature subit 1d4 dégâts (tranchants ou perforants) au début de chacun de ses tours. L'effet "
   "prend fin si elle reçoit des soins magiques ou si une créature réussit un test de Sagesse (Médecine) "
   "DD 10 par une action. Les créatures artificielles et les morts-vivants y sont immunisés.",
   notes=["1d4 dégâts au début de chaque tour", "Fin : soins magiques ou Médecine DD 10"])
_e("en_feu", "En feu (brûlure)", "🔥", "Malus", _IMM, "Jusqu'à extinction",
   "La créature subit 1d4 dégâts de feu au début de chacun de ses tours. Elle (ou une alliée à 1,5 m) "
   "peut utiliser une action pour éteindre les flammes ; se jeter à l'eau ou être mouillée les éteint aussi.",
   notes=["1d4 feu au début de chaque tour", "Action pour éteindre"])
_e("mouille", "Mouillé", "💧", "État", _IMM, "1 minute ou jusqu'à séchage",
   "La créature trempée résiste aux dégâts de feu mais devient vulnérable aux dégâts de froid et de "
   "foudre. Elle ne peut pas être enflammée tant qu'elle est mouillée.",
   resistances=["feu"], notes=["Vulnérable au froid et à la foudre", "Ne peut pas prendre feu"])
_e("glace", "Glacé (transi)", "❄️", "Malus", _IMM, "Jusqu'à la fin de son prochain tour",
   "Engourdie par le froid, la créature voit sa vitesse réduite de 3 m et ne peut pas prendre de réaction.",
   vitesse_bonus=-3.0, notes=["Pas de réaction"])
_e("gele", "Gelé", "🧊", "Malus", _IMM, "Jusqu'à la fin de son prochain tour",
   "Prise dans la glace, la créature est Entravée et vulnérable aux dégâts contondants. Tout dégât de "
   "feu ou un JS de Force DD 12 par une action la libère.",
   vitesse_mult=0.0, attaque="désavantage", notes=["Entravée", "Vulnérable aux dégâts contondants"])
_e("ralenti", "Ralenti", "🐌", "Malus", _IMM, "Jusqu'à la fin de son prochain tour",
   "La vitesse de la créature est divisée par deux et elle ne peut pas effectuer l'action Foncer.",
   vitesse_mult=0.5, notes=["Pas d'action Foncer"])
_e("malade", "Malade", "🤒", "Malus", _IMM, "Jusqu'à guérison",
   "Fiévreuse, la créature a le désavantage aux tests de Force et de Constitution et ne récupère pas de "
   "PV en dépensant des dés de vie. Restauration partielle ou un traitement réussi (Médecine DD 13 après un "
   "repos long) la guérit.",
   notes=["Désavantage aux tests de Force et de Constitution", "Pas de récupération par dés de vie"])
_e("concentration", "Concentration", "🧠", "État", "Règle de lanceur (PHB)", "Selon le sort",
   "Le lanceur maintient un sort à concentration. Chaque fois qu'il subit des dégâts, il fait un JS de "
   "Constitution DD 10 ou moitié des dégâts (le plus élevé) ; un échec rompt le sort. Lancer un autre sort "
   "à concentration, être neutralisé ou mourir y met aussi fin.",
   notes=["JS Con DD max(10, dégâts/2) à chaque dégât subi"])
_e("hebete", "Hébété", "😵‍💫", "Malus", _IMM, "Jusqu'à la fin de son prochain tour",
   "Sonnée, la créature ne peut pas prendre de réaction et a le désavantage à ses JS de Dextérité.",
   notes=["Pas de réaction", "Désavantage aux JS de Dextérité"])
_e("plaie_beante", "Plaie béante", "🕳️", "Malus", _IMM, "Jusqu'à la fin du prochain tour de l'attaquant",
   "Chaque attaque qui touche la créature inflige 1d4 dégâts supplémentaires du type de l'arme.",
   notes=["Attaques contre elle : +1d4 dégâts"])
_e("desarme", "Désarmé", "🤚", "Malus", _IMM, "Jusqu'à récupération de l'objet",
   "La créature a lâché son arme ou un objet tenu, qui gît à 1,5 m. Le ramasser coûte son interaction "
   "gratuite et du déplacement ; d'ici là elle combat à mains nues ou avec une autre arme.",
   notes=["Arme au sol à 1,5 m"])
_e("affaibli", "Affaibli", "🥀", "Malus", _IMM, "1 minute (JS de Con en fin de tour)",
   "La créature a le désavantage aux jets d'attaque et tests utilisant la Force, et ses dégâts d'arme "
   "diminuent de 1d4.",
   degats="-1d4", notes=["Désavantage aux attaques et tests de Force"])
_e("desequilibre", "Déséquilibré", "🌪️", "Malus", _IMM, "Jusqu'au début du prochain tour de l'attaquant",
   "La créature a perdu sa garde : les jets d'attaque contre elle ont l'avantage.",
   notes=["Attaques contre elle : avantage"])
_e("cache", "Caché", "🫥", "État", "Action Se cacher (PHB)", "Jusqu'à être repéré",
   "Après un test de Dextérité (Discrétion) réussi, la créature n'est pas localisée. Sa première attaque "
   "a l'avantage, puis elle est révélée ; faire du bruit ou être vue met fin à l'effet.",
   attaque="avantage", notes=["Révélé après l'attaque"])
_e("surpris", "Surpris", "😲", "État", "Règle de combat (PHB)", "Premier round",
   "La créature n'a pas vu venir l'embuscade : elle ne peut ni bouger ni agir à son premier tour, et ne "
   "peut pas prendre de réaction avant la fin de celui-ci.",
   vitesse_mult=0.0, notes=["Ni action ni réaction pendant son premier tour"])

# ======================================================================================
# Sorts : bonus
# ======================================================================================
_e("benediction", "Bénédiction", "🙏", "Bonus", _sort(1, "Bénédiction"), "1 minute",
   "Jusqu'à trois créatures ajoutent 1d4 à leurs jets d'attaque et jets de sauvegarde.",
   True, attaque="+1d4", js="+1d4")
_e("bouclier_foi", "Bouclier de la foi", "🛡️", "Bonus", _sort(1, "Bouclier de la foi"), "10 minutes",
   "Un champ chatoyant entoure une créature et lui accorde +2 à la CA.", True, ca=2)
_e("bouclier", "Bouclier (sort)", "🔰", "Bonus", _sort(1, "Bouclier"), "Jusqu'au début de votre prochain tour",
   "Réaction lorsque vous êtes touché ou visé par Projectile magique : +5 à la CA, y compris contre "
   "l'attaque déclencheuse, et aucun dégât de Projectile magique.", ca=5,
   notes=["Immunité à Projectile magique"])
_e("hate", "Hâte", "⚡", "Bonus", _sort(3, "Hâte"), "1 minute",
   "La cible voit sa vitesse doublée, gagne +2 à la CA et l'avantage aux JS de Dextérité. Elle obtient une "
   "action supplémentaire par tour, limitée à une attaque d'arme, Foncer, Se désengager, Se cacher ou "
   "Utiliser un objet. À la fin du sort, elle subit Léthargie.",
   True, ca=2, vitesse_mult=2.0,
   notes=["Avantage aux JS de Dextérité", "Action supplémentaire limitée", "Léthargie à la fin du sort"])
_e("aide", "Aide", "❤️", "Bonus", _sort(2, "Aide"), "8 heures",
   "Jusqu'à trois créatures voient leurs PV maximum et actuels augmenter de 5 (+5 par niveau d'emplacement "
   "au-delà du 2e).", notes=["PV max et actuels +5"])
_e("heroisme", "Héroïsme", "🦸", "Bonus", _sort(1, "Héroïsme"), "1 minute",
   "La cible est immunisée contre l'état Effrayé et gagne, au début de chacun de ses tours, des PV "
   "temporaires égaux au modificateur de caractéristique d'incantation du lanceur.",
   True, notes=["Immunité : Effrayé", "PV temporaires à chaque tour"])
_e("faveur_divine", "Faveur divine", "✝️", "Bonus", _sort(1, "Faveur divine"), "1 minute",
   "Vos attaques avec une arme infligent 1d4 dégâts radiants supplémentaires quand elles touchent.",
   degats="+1d4 radiants")
_e("armure_mage", "Armure du mage", "🧥", "Bonus", _sort(1, "Armure du mage"), "8 heures",
   "Une créature consentante qui ne porte pas d'armure a une CA de base de 13 + son modificateur de "
   "Dextérité. Le sort prend fin si elle enfile une armure.",
   notes=["CA de base = 13 + mod. Dex (sans armure)"])
_e("peau_ecorce", "Peau d'écorce", "🌳", "Bonus", _sort(2, "Peau d'écorce"), "1 heure",
   "La peau de la cible prend la texture de l'écorce : sa CA ne peut pas être inférieure à 16, quelle "
   "que soit l'armure portée.", True, notes=["CA minimale 16"])
_e("peau_pierre", "Peau de pierre", "🪨", "Bonus", _sort(4, "Peau de pierre"), "1 heure",
   "La chair de la cible devient dure comme la pierre : elle résiste aux dégâts contondants, perforants "
   "et tranchants non magiques.", True,
   resistances=["contondant (non magique)", "perforant (non magique)", "tranchant (non magique)"])
_e("flou", "Flou", "🌫️", "Bonus", _sort(2, "Flou"), "1 minute",
   "Votre silhouette devient floue : les créatures qui vous attaquent ont le désavantage, sauf si elles "
   "ne dépendent pas de la vue (vision aveugle, vision véritable…).", True,
   notes=["Attaques contre vous : désavantage"])
_e("image_miroir", "Image miroir", "🪞", "Bonus", _sort(2, "Image miroir"), "1 minute",
   "Trois doubles illusoires vous entourent. Quand une attaque vous vise, lancez un d20 pour savoir si "
   "elle frappe un double (6+ avec 3 doubles, 8+ avec 2, 11+ avec 1) ; un double a une CA de 10 + mod. "
   "Dex et disparaît s'il est touché.", notes=["3 doubles (CA 10 + Dex)"])
_e("invisibilite_sort", "Invisibilité (sort)", "👻", "Bonus", _sort(2, "Invisibilité"), "1 heure",
   "La cible devient Invisible avec tout ce qu'elle porte. Le sort prend fin dès qu'elle attaque ou "
   "lance un sort.", True, attaque="avantage",
   notes=["Attaques contre elle : désavantage", "Prend fin si elle attaque ou lance un sort"])
_e("invisibilite_sup", "Invisibilité supérieure", "🌌", "Bonus", _sort(4, "Invisibilité supérieure"), "1 minute",
   "La cible devient Invisible pour toute la durée, même si elle attaque ou lance des sorts.",
   True, attaque="avantage", notes=["Attaques contre elle : désavantage"])
_e("agrandissement", "Agrandissement", "⬆️", "Bonus", _sort(2, "Agrandir/Rapetisser"), "1 minute",
   "La cible double de taille (une catégorie de plus). Elle a l'avantage aux tests et JS de Force et ses "
   "armes infligent 1d4 dégâts supplémentaires.", True, degats="+1d4",
   notes=["Avantage aux tests et JS de Force", "Taille +1 catégorie"])
_e("rapetissement", "Rapetissement", "⬇️", "Malus", _sort(2, "Agrandir/Rapetisser"), "1 minute",
   "La cible est réduite de moitié (une catégorie de moins). Elle a le désavantage aux tests et JS de "
   "Force et ses armes infligent 1d4 dégâts de moins (minimum 1).", True, degats="-1d4",
   notes=["Désavantage aux tests et JS de Force", "Taille −1 catégorie"])
_e("protection_mal_bien", "Protection contre le mal et le bien", "✨", "Bonus",
   _sort(1, "Protection contre le mal et le bien"), "10 minutes",
   "Les aberrations, célestes, élémentaires, fées, fiélons et morts-vivants ont le désavantage pour "
   "attaquer la cible. Celle-ci ne peut pas être charmée, effrayée ou possédée par eux ; si elle l'est "
   "déjà, elle a l'avantage au JS pour s'en libérer.", True,
   notes=["Désavantage aux attaques de 6 types de créatures", "Immunité au charme/peur/possession de ces créatures"])
_e("sanctuaire", "Sanctuaire", "🕊️", "Bonus", _sort(1, "Sanctuaire"), "1 minute",
   "Toute créature qui veut attaquer la cible ou la viser avec un sort nuisible doit d'abord réussir un "
   "JS de Sagesse, sinon elle doit choisir une autre cible. Le sort prend fin si la cible attaque, lance "
   "un sort affectant un ennemi ou inflige des dégâts.",
   notes=["Les attaquants doivent réussir un JS de Sagesse"])
_e("vol", "Vol", "🪽", "Bonus", _sort(3, "Vol"), "10 minutes",
   "La cible gagne une vitesse de vol de 18 m. Si le sort prend fin en vol, elle tombe, à moins de "
   "pouvoir l'éviter.", True, notes=["Vitesse de vol 18 m"])
_e("saut", "Saut", "🦘", "Bonus", _sort(1, "Saut"), "1 minute",
   "La distance de saut de la cible est triplée.", notes=["Distance de saut ×3"])
_e("grande_foulee", "Grande foulée", "👟", "Bonus", _sort(1, "Grande foulée"), "1 heure",
   "La vitesse de la cible augmente de 3 m.", vitesse_bonus=3.0)
_e("pattes_araignee", "Pattes d'araignée", "🕷️", "Bonus", _sort(2, "Pattes d'araignée"), "1 heure",
   "La cible peut se déplacer sur les murs et les plafonds en gardant les mains libres, et gagne une "
   "vitesse d'escalade égale à sa vitesse au sol.", True, notes=["Vitesse d'escalade = vitesse"])
_e("vision_noir", "Vision dans le noir (sort)", "🌑", "Bonus", _sort(2, "Vision dans le noir"), "8 heures",
   "La cible voit dans les ténèbres jusqu'à 18 m.", notes=["Vision dans le noir 18 m"])
_e("resistance", "Résistance", "🧿", "Bonus", _sort(0, "Résistance"), "1 minute",
   "Une fois avant la fin du sort, la cible peut lancer 1d4 et l'ajouter à un jet de sauvegarde de son choix.",
   True, js="+1d4", notes=["Une seule utilisation"])
_e("assistance", "Assistance", "🤲", "Bonus", _sort(0, "Assistance"), "1 minute",
   "Une fois avant la fin du sort, la cible peut lancer 1d4 et l'ajouter à un test de caractéristique.",
   True, tests="+1d4", notes=["Une seule utilisation"])
_e("arme_magique", "Arme magique", "🗡️", "Bonus", _sort(2, "Arme magique"), "1 heure",
   "Une arme non magique devient magique et gagne +1 aux jets d'attaque et de dégâts (+2 avec un "
   "emplacement de niveau 4, +3 au niveau 6).", True, attaque=1, degats="+1")
_e("marque_chasseur_lanceur", "Marque du chasseur (vous marquez)", "🎯", "Bonus", _sort(1, "Marque du chasseur"),
   "1 heure", "Vous infligez 1d6 dégâts supplémentaires à la cible marquée à chaque attaque d'arme qui la "
   "touche, et vous avez l'avantage aux tests de Perception et de Survie pour la trouver. Si elle tombe à "
   "0 PV, vous pouvez transférer la marque par une action bonus.", True,
   degats="+1d6 (cible marquée)", notes=["Avantage aux tests pour pister la cible"])
_e("malefice_lanceur", "Maléfice (vous maudissez)", "🕯️", "Bonus", _sort(1, "Maléfice"), "1 heure",
   "Chaque attaque qui touche la cible maudite lui inflige 1d6 dégâts nécrotiques supplémentaires. Si elle "
   "tombe à 0 PV, vous pouvez transférer la malédiction par une action bonus.", True,
   degats="+1d6 nécrotiques (cible maudite)")
_e("liberte_mouvement", "Liberté de mouvement", "🕊️", "Bonus", _sort(4, "Liberté de mouvement"), "1 heure",
   "Le terrain difficile n'affecte pas la cible, ni la magie qui réduirait sa vitesse, la paralyserait ou "
   "l'entraverait. Elle peut dépenser 1,5 m de déplacement pour se libérer d'une entrave non magique, et "
   "nager ou combattre sous l'eau sans pénalité.", notes=["Ignore terrain difficile, paralysie et entrave magiques"])
_e("protection_mort", "Protection contre la mort", "⚰️", "Bonus", _sort(4, "Protection contre la mort"), "8 heures",
   "La première fois que la cible devrait tomber à 0 PV, elle tombe à 1 PV à la place et le sort prend fin. "
   "Un effet qui la tuerait instantanément sans dégâts est annulé de la même manière.",
   notes=["Tombe à 1 PV au lieu de 0 (une fois)"])
_e("protection_energie", "Protection contre l'énergie", "🌈", "Bonus", _sort(3, "Protection contre l'énergie"),
   "1 heure", "La cible résiste à un type de dégâts choisi au lancement : acide, froid, feu, foudre ou tonnerre.",
   True, resistances=["type au choix (acide, froid, feu, foudre ou tonnerre)"])
_e("bouclier_feu", "Bouclier de feu", "🔥", "Bonus", _sort(4, "Bouclier de feu"), "10 minutes",
   "Des flammes vous entourent. Bouclier chaud : résistance au froid ; bouclier froid : résistance au feu. "
   "Une créature à 1,5 m qui vous touche au corps à corps subit 2d8 dégâts de feu (ou de froid).",
   resistances=["froid (bouclier chaud) ou feu (bouclier froid)"],
   notes=["2d8 dégâts à l'attaquant au corps à corps"])
_e("armure_agathys", "Armure d'Agathys", "🥶", "Bonus", _sort(1, "Armure d'Agathys"), "1 heure",
   "Vous gagnez 5 PV temporaires (+5 par niveau d'emplacement supérieur). Tant qu'ils durent, une créature "
   "qui vous touche au corps à corps subit 5 dégâts de froid (même progression).",
   notes=["5 PV temporaires", "5 dégâts de froid à l'attaquant"])
_e("fausse_vie", "Simulacre de vie", "💀", "Bonus", _sort(1, "Simulacre de vie"), "1 heure",
   "Vous gagnez 1d4 + 4 PV temporaires (+5 par niveau d'emplacement supérieur).",
   notes=["1d4 + 4 PV temporaires"])
_e("protection_poison", "Protection contre le poison", "🧪", "Bonus", _sort(2, "Protection contre le poison"),
   "1 heure", "Le sort neutralise un poison affectant la cible. Pour la durée, elle a l'avantage aux JS "
   "contre l'état Empoisonné et résiste aux dégâts de poison.",
   resistances=["poison"], notes=["Avantage aux JS contre Empoisonné"])
_e("vision_veritable", "Vision lucide", "👁️", "Bonus", _sort(6, "Vision lucide"), "1 heure",
   "La cible voit jusqu'à 36 m les choses telles qu'elles sont : ténèbres magiques, créatures invisibles, "
   "illusions, métamorphoses et le plan Éthéré.", notes=["Vision véritable 36 m"])
_e("respiration_aquatique", "Respiration aquatique", "🫧", "Bonus", _sort(3, "Respiration aquatique"),
   "24 heures", "Jusqu'à dix créatures peuvent respirer sous l'eau tout en conservant leur respiration normale.",
   notes=["Respire sous l'eau"])
_e("arme_elementaire", "Arme élémentaire", "🌋", "Bonus", _sort(3, "Arme élémentaire"), "1 heure",
   "Une arme non magique gagne +1 aux jets d'attaque et inflige 1d4 dégâts supplémentaires d'un type "
   "élémentaire choisi (acide, froid, feu, foudre ou tonnerre).", True, attaque=1,
   degats="+1d4 (acide, froid, feu, foudre ou tonnerre)")
_e("abri_partiel", "Abri partiel", "🧱", "Bonus", "Règle de combat (PHB)", "Tant que l'abri est présent",
   "Un obstacle couvre au moins la moitié de la créature : +2 à la CA et aux JS de Dextérité.",
   ca=2, notes=["+2 aux JS de Dextérité"])
_e("abri_important", "Abri important", "🏰", "Bonus", "Règle de combat (PHB)", "Tant que l'abri est présent",
   "Un obstacle couvre les trois quarts de la créature : +5 à la CA et aux JS de Dextérité.",
   ca=5, notes=["+5 aux JS de Dextérité"])

# ======================================================================================
# Sorts : malus
# ======================================================================================
_e("lethargie", "Léthargie (fin de Hâte)", "😴", "Malus", _sort(3, "Hâte"), "Jusqu'à la fin de son prochain tour",
   "Quand Hâte prend fin, une vague de lassitude empêche la créature de se déplacer ou d'agir jusqu'à la "
   "fin de son prochain tour.", vitesse_mult=0.0, notes=["Ni déplacement ni action"])
_e("fleau", "Fléau", "☠️", "Malus", _sort(1, "Fléau"), "1 minute",
   "Jusqu'à trois créatures ratant un JS de Charisme soustraient 1d4 à leurs jets d'attaque et jets de sauvegarde.",
   True, attaque="-1d4", js="-1d4")
_e("lenteur", "Lenteur", "🐢", "Malus", _sort(3, "Lenteur"), "1 minute",
   "Jusqu'à six créatures ratant un JS de Sagesse voient leur vitesse divisée par deux, subissent −2 à la "
   "CA et aux JS de Dextérité et ne peuvent pas prendre de réaction. À leur tour : une action ou une action "
   "bonus, pas les deux, et une seule attaque ; leurs sorts à incantation d'une action peuvent échouer. "
   "JS de Sagesse en fin de tour pour y mettre fin.", True, ca=-2, vitesse_mult=0.5,
   notes=["−2 aux JS de Dextérité", "Pas de réaction", "Action ou action bonus, pas les deux"])
_e("rayon_affaiblissant", "Rayon affaiblissant", "📉", "Malus", _sort(2, "Rayon affaiblissant"), "1 minute",
   "La cible qui rate un JS de Constitution n'inflige que la moitié des dégâts avec les armes utilisant "
   "la Force. JS en fin de tour pour y mettre fin.", True,
   notes=["Dégâts des armes de Force divisés par deux"])
_e("lueurs_feeriques", "Lueurs féeriques", "🟣", "Malus", _sort(1, "Lueurs féeriques"), "1 minute",
   "Les créatures ratant un JS de Dextérité sont nimbées de lumière : elles ne peuvent pas être invisibles "
   "et les attaques contre elles ont l'avantage si l'attaquant les voit.", True,
   notes=["Attaques contre elle : avantage", "Ne peut pas bénéficier de l'invisibilité"])
_e("toile", "Toile", "🕸️", "Malus", _sort(2, "Toile"), "1 heure",
   "Une créature prise dans les toiles (JS de Dextérité raté) est Entravée. Elle peut utiliser une action "
   "pour un test de Force contre le DD du sort afin de se libérer. Les toiles sont inflammables.", True,
   vitesse_mult=0.0, attaque="désavantage", notes=["Entravée", "Action : test de Force pour se libérer"])
_e("immobilisation_personne", "Immobilisation de personne", "🧍", "Malus", _sort(2, "Immobilisation de personne"),
   "1 minute", "Un humanoïde ratant un JS de Sagesse est Paralysé. Il refait le JS à la fin de chacun de "
   "ses tours.", True, vitesse_mult=0.0, notes=["Paralysé", "Coups critiques à 1,5 m"])
_e("malediction", "Malédiction", "🧿", "Malus", _sort(3, "Jeter une malédiction"), "1 minute",
   "La cible (JS de Sagesse raté) subit un effet au choix : désavantage aux tests et JS d'une "
   "caractéristique ; désavantage aux attaques contre le lanceur ; JS de Sagesse à chaque tour sous peine "
   "de perdre son action ; ou 1d8 dégâts nécrotiques supplémentaires des attaques du lanceur.", True,
   notes=["Un effet au choix parmi quatre"])
_e("moquerie_cruelle", "Moquerie cruelle", "🤬", "Malus", _sort(0, "Moquerie cruelle"),
   "Jusqu'à la fin de son prochain tour", "La cible blessée par les insultes (JS de Sagesse raté) a le "
   "désavantage à son prochain jet d'attaque.", attaque="désavantage", notes=["Prochaine attaque seulement"])
_e("marque_chasseur_cible", "Marque du chasseur (cible)", "🎯", "Malus", _sort(1, "Marque du chasseur"),
   "1 heure", "La créature est marquée par un rôdeur : elle subit 1d6 dégâts supplémentaires de ses "
   "attaques d'arme et peut difficilement lui échapper.", True,
   notes=["Subit +1d6 des attaques du lanceur"])
_e("malefice_cible", "Maléfice (cible)", "🕯️", "Malus", _sort(1, "Maléfice"), "1 heure",
   "La créature maudite subit 1d6 dégâts nécrotiques supplémentaires des attaques du lanceur et a le "
   "désavantage aux tests d'une caractéristique choisie par celui-ci.", True,
   notes=["Désavantage aux tests d'une caractéristique choisie", "Subit +1d6 nécrotiques du lanceur"])
_e("confusion", "Confusion", "🌀", "Malus", _sort(4, "Confusion"), "1 minute",
   "La créature (JS de Sagesse raté) ne peut pas prendre de réaction et lance 1d10 au début de son tour : "
   "1 déplacement aléatoire ; 2-6 aucune action ; 7-8 attaque une créature au hasard à son contact ; 9-10 "
   "agit normalement. JS en fin de tour pour y mettre fin.", True,
   notes=["Pas de réaction", "Comportement tiré au d10"])
_e("peur", "Peur (sort)", "👹", "Malus", _sort(3, "Terreur"), "1 minute",
   "Les créatures prises dans le cône (JS de Sagesse raté) lâchent ce qu'elles tiennent et sont "
   "Effrayées ; elles doivent fuir le lanceur par le chemin le plus sûr. JS de Sagesse en fin de tour hors "
   "de vue du lanceur pour y mettre fin.", True, attaque="désavantage", tests="désavantage",
   notes=["Effrayée", "Doit utiliser Foncer pour s'éloigner"])
_e("rayon_givre", "Rayon de givre", "🧊", "Malus", _sort(0, "Rayon de givre"),
   "Jusqu'au début du prochain tour du lanceur", "Touchée par le rayon, la cible voit sa vitesse réduite de 3 m.",
   vitesse_bonus=-3.0)
_e("enchevetrement", "Enchevêtrement", "🌿", "Malus", _sort(1, "Enchevêtrement"), "1 minute",
   "Des plantes jaillissent dans un carré de 6 m : la zone devient terrain difficile et une créature "
   "ratant son JS de Force est Entravée. Une action et un test de Force permettent de se libérer.", True,
   vitesse_mult=0.0, attaque="désavantage", notes=["Entravée"])
_e("fou_rire", "Fou rire de Tasha", "🤣", "Malus", _sort(1, "Fou rire"), "1 minute",
   "La cible (JS de Sagesse raté) tombe À terre, hilare, et est neutralisée. Elle refait le JS à la fin "
   "de chacun de ses tours et à chaque fois qu'elle subit des dégâts (avec l'avantage dans ce cas).", True,
   vitesse_mult=0.0, notes=["À terre et neutralisée"])
_e("cecite_surdite", "Cécité/Surdité", "🙉", "Malus", _sort(2, "Cécité/Surdité"), "1 minute",
   "La cible (JS de Constitution raté) est Aveuglée ou Assourdie, au choix du lanceur. JS en fin de tour "
   "pour y mettre fin.", attaque="désavantage", notes=["Aveuglée ou Assourdie"])
_e("sommeil", "Sommeil (sort)", "💤", "Malus", _sort(1, "Sommeil"), "1 minute",
   "La créature sombre dans un sommeil magique : elle est Inconsciente jusqu'à la fin du sort, ou "
   "jusqu'à subir des dégâts ou être secouée par une action.", vitesse_mult=0.0, notes=["Inconsciente"])
_e("eclair_tracant", "Éclair traçant", "🌠", "Malus", _sort(1, "Éclair traçant"),
   "Jusqu'à la fin du prochain tour du lanceur", "Une lueur mystique reste sur la cible : le prochain "
   "jet d'attaque effectué contre elle a l'avantage.", notes=["Prochaine attaque contre elle : avantage"])

# ======================================================================================
# Auras
# ======================================================================================
_e("esprit_gardien", "Esprits gardiens", "👼", "Aura", _sort(3, "Esprits gardiens"), "10 minutes",
   "Des esprits vous entourent dans un rayon de 4,5 m. Pour les ennemis, la zone est un terrain où leur "
   "vitesse est divisée par deux ; ceux qui y entrent ou y commencent leur tour font un JS de Sagesse : "
   "3d8 dégâts radiants (ou nécrotiques), moitié en cas de réussite.", True,
   notes=["Rayon 4,5 m", "Ennemis : vitesse ÷ 2 et 3d8 dégâts"])
_e("cercle_pouvoir", "Cercle de pouvoir", "⭕", "Aura", _sort(5, "Cercle de pouvoir"), "10 minutes",
   "Les alliés à 9 m ou moins ont l'avantage aux JS contre les sorts et autres effets magiques ; s'ils "
   "réussissent un JS qui inflige la moitié des dégâts, ils n'en subissent aucun.", True,
   notes=["Avantage aux JS contre la magie", "Dégâts annulés sur réussite d'un JS à moitié"])
_e("aura_vie", "Aura de vie", "💚", "Aura", _sort(4, "Aura de vie"), "10 minutes",
   "Dans un rayon de 9 m, les créatures non hostiles résistent aux dégâts nécrotiques, ne peuvent pas "
   "voir leurs PV maximum réduits, et une créature à 0 PV regagne 1 PV au début de son tour.", True,
   resistances=["nécrotique"], notes=["PV max ne peuvent pas être réduits", "Les créatures à 0 PV remontent à 1 PV"])
_e("aura_vitalite", "Aura de vitalité", "💗", "Aura", _sort(3, "Aura de vitalité"), "1 minute",
   "Une énergie curative rayonne à 9 m autour de vous : par une action bonus, vous rendez 2d6 PV à une "
   "créature dans l'aura.", True, notes=["Action bonus : soigne 2d6 PV"])
_e("aura_protection", "Aura de protection", "🛡️", "Aura", "Paladin niv. 6", "Permanente (conscient)",
   "Vous et vos alliés à 3 m ajoutez votre modificateur de Charisme (minimum +1) à vos jets de sauvegarde, "
   "tant que vous êtes conscient. Le rayon passe à 9 m au niveau 18.",
   notes=["+ mod. de Charisme du paladin aux JS"])
_e("aura_devotion", "Aura de dévotion", "😇", "Aura", "Paladin (Serment de dévotion) niv. 7",
   "Permanente (conscient)", "Vous et vos alliés à 3 m ne pouvez pas être charmés tant que vous êtes "
   "conscient (9 m au niveau 18).", notes=["Immunité : Charmé"])
_e("aura_courage", "Aura de courage", "🦁", "Aura", "Paladin niv. 10", "Permanente (conscient)",
   "Vous et vos alliés à 3 m ne pouvez pas être effrayés tant que vous êtes conscient (9 m au niveau 18).",
   notes=["Immunité : Effrayé"])
_e("aura_garde", "Aura de garde", "🌲", "Aura", "Paladin (Serment des Anciens) niv. 7", "Permanente (conscient)",
   "Vous et vos alliés à 3 m résistez aux dégâts infligés par les sorts (9 m au niveau 18).",
   resistances=["dégâts des sorts"])
_e("aura_conquete", "Aura de conquête", "👑", "Aura", "Paladin (Serment de conquête) niv. 7",
   "Permanente (conscient)", "Une créature effrayée par vous qui commence son tour à 3 m de vous voit sa "
   "vitesse tomber à 0 et subit des dégâts psychiques égaux à la moitié de votre niveau de paladin.",
   notes=["Ennemis effrayés à 3 m : vitesse 0 et dégâts psychiques"])

# ======================================================================================
# Aptitudes de classe et actions
# ======================================================================================
_e("rage", "Rage", "😡", "Aptitude", "Barbare niv. 1", "1 minute",
   "Sans armure lourde : avantage aux tests et JS de Force, bonus aux dégâts des attaques de Force (+2 "
   "à +4 selon le niveau) et résistance aux dégâts contondants, perforants et tranchants. Impossible de "
   "lancer des sorts ou de se concentrer. Prend fin si vous n'attaquez pas ni ne subissez de dégâts "
   "pendant un tour.", degats="+2 (attaques de Force)",
   resistances=["contondant", "perforant", "tranchant"],
   notes=["Avantage aux tests et JS de Force", "Pas de sorts ni de concentration"])
_e("attaque_temeraire", "Attaque téméraire", "🪓", "Aptitude", "Barbare niv. 2", "Jusqu'à votre prochain tour",
   "Vous avez l'avantage à vos jets d'attaque au corps à corps utilisant la Force pendant ce tour, mais les "
   "attaques contre vous ont l'avantage jusqu'à votre prochain tour.", attaque="avantage",
   notes=["Attaques contre vous : avantage"])
_e("frenesie", "Frénésie", "🌋", "Aptitude", "Barbare (Berserker) niv. 3", "Durée de la rage",
   "Pendant votre rage, vous pouvez effectuer une attaque d'arme au corps à corps par une action bonus à "
   "chacun de vos tours. À la fin de la rage, vous subissez un niveau d'épuisement (règle 2014).",
   notes=["Action bonus : une attaque au corps à corps", "+1 épuisement à la fin"])
_e("fureur_divine", "Fureur divine", "⚡", "Aptitude", "Barbare (Zélateur) niv. 3", "Durée de la rage",
   "Pendant votre rage, la première créature que vous touchez à chacun de vos tours subit 1d6 + la moitié "
   "de votre niveau de barbare en dégâts nécrotiques ou radiants (au choix).",
   degats="+1d6 + ½ niveau (nécrotiques ou radiants, 1/tour)")
_e("inspiration_bardique", "Inspiration bardique", "🎵", "Aptitude", "Barde niv. 1", "10 minutes",
   "La créature inspirée peut ajouter le dé d'inspiration (d6, puis d8, d10, d12) à un test, un jet "
   "d'attaque ou un jet de sauvegarde, après avoir vu le d20 mais avant de connaître le résultat.",
   notes=["+1d6 (d8/d10/d12) à un jet, une fois"])
_e("inspiration_heroique", "Inspiration héroïque", "🌟", "Aptitude", "Règle (PHB 2024)", "Jusqu'à utilisation",
   "Vous pouvez dépenser votre inspiration pour relancer n'importe quel dé et garder le nouveau résultat.",
   notes=["Relance d'un dé"])
_e("esquive", "Esquive (action)", "🤺", "Aptitude", "Action (PHB)", "Jusqu'au début de votre prochain tour",
   "Les jets d'attaque contre vous ont le désavantage si vous voyez l'attaquant, et vous avez l'avantage aux "
   "JS de Dextérité. Perdu si vous êtes neutralisé ou si votre vitesse tombe à 0.",
   notes=["Attaques contre vous : désavantage", "Avantage aux JS de Dextérité"])
_e("desengagement", "Désengagement", "↩️", "Aptitude", "Action (PHB)", "Jusqu'à la fin du tour",
   "Votre déplacement ne provoque pas d'attaque d'opportunité pour le reste du tour.",
   notes=["Pas d'attaque d'opportunité"])
_e("foncer", "Foncer", "🏃", "Aptitude", "Action (PHB)", "Jusqu'à la fin du tour",
   "Vous gagnez un déplacement supplémentaire égal à votre vitesse pour ce tour.", vitesse_mult=2.0)
_e("arme_sacree", "Arme sacrée", "🌞", "Aptitude", "Paladin (Serment de dévotion) niv. 3", "1 minute",
   "Par Conduit divin, votre arme émet une lumière vive sur 6 m et vous ajoutez votre modificateur de "
   "Charisme (minimum +1) à vos jets d'attaque avec elle. L'arme est considérée comme magique.",
   notes=["+ mod. de Charisme aux jets d'attaque", "Arme magique, lumière 6 m"])
_e("voeu_inimitie", "Vœu d'inimitié", "⚔️", "Aptitude", "Paladin (Serment de vengeance) niv. 3", "1 minute",
   "Par Conduit divin, vous désignez une créature à 3 m : vous avez l'avantage à vos jets d'attaque contre "
   "elle pour la durée.", attaque="avantage", notes=["Contre la créature désignée uniquement"])
_e("sursaut_activite", "Sursaut d'activité", "💥", "Aptitude", "Guerrier niv. 2", "Votre tour",
   "Une fois par repos court, vous pouvez effectuer une action supplémentaire à votre tour.",
   notes=["Une action supplémentaire"])
_e("second_souffle", "Second souffle", "🌬️", "Aptitude", "Guerrier niv. 1", "Instantané",
   "Par une action bonus, vous regagnez 1d10 + votre niveau de guerrier PV.", notes=["Soins 1d10 + niveau"])
_e("forme_sauvage", "Forme sauvage", "🐺", "Aptitude", "Druide niv. 2", "Moitié du niveau de druide en heures",
   "Vous prenez la forme d'une bête déjà vue, en adoptant ses statistiques physiques, ses PV et ses sens "
   "tout en conservant vos caractéristiques mentales. Vous ne pouvez pas lancer de sorts sous cette forme "
   "et reprenez votre forme quand ses PV tombent à 0.", notes=["Statistiques de la bête", "Pas de sorts"])
_e("defense_patiente", "Défense patiente", "🧘", "Aptitude", "Moine niv. 2", "Jusqu'au début de votre prochain tour",
   "En dépensant 1 point de ki, vous effectuez l'action Esquive par une action bonus.",
   notes=["Attaques contre vous : désavantage", "Avantage aux JS de Dextérité"])
_e("deplacement_sans_armure", "Déplacement sans armure", "🦶", "Aptitude", "Moine niv. 2", "Permanente",
   "Sans armure ni bouclier, votre vitesse augmente de 3 m (davantage aux niveaux supérieurs, jusqu'à "
   "+9 m au niveau 18).", vitesse_bonus=3.0)
_e("benediction_tenebreux", "Bénédiction du ténébreux", "😈", "Aptitude", "Occultiste (Fiélon) niv. 1", "Instantané",
   "Quand vous réduisez une créature hostile à 0 PV, vous gagnez des PV temporaires égaux à votre "
   "modificateur de Charisme + votre niveau d'occultiste (minimum 1).",
   notes=["PV temporaires = mod. Cha + niveau"])
_e("chant_lame", "Chant de la lame", "🎶", "Aptitude", "Magicien (Chanteur de lame) niv. 2", "1 minute",
   "Sans armure intermédiaire ou lourde ni bouclier : bonus à la CA égal à votre modificateur "
   "d'Intelligence (minimum +1), vitesse +3 m, avantage aux tests d'Acrobaties et bonus égal à votre "
   "modificateur d'Intelligence aux JS de Constitution pour la concentration.", vitesse_bonus=3.0,
   notes=["+ mod. d'Intelligence à la CA", "Avantage aux tests d'Acrobaties",
          "+ mod. d'Intelligence aux JS de concentration"])
_e("egide_arcanique", "Égide arcanique", "🔷", "Aptitude", "Magicien (Abjuration) niv. 2", "Jusqu'à un repos long",
   "Quand vous lancez un sort d'abjuration de niveau 1+, vous créez une égide de PV égaux au double de "
   "votre niveau de magicien + votre mod. d'Intelligence. Elle absorbe les dégâts que vous subissez avant "
   "vos PV et se recharge de deux fois le niveau du sort à chaque abjuration lancée.",
   notes=["Absorbe les dégâts avant vos PV"])


# --------------------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------------------
def _norm(text: str) -> str:
    text = (text or "").replace("’", "'")
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower().strip()


def _sort_key(key: str):
    e = EFFECTS[key]
    cat = e["categorie"]
    return (CATEGORIES.index(cat) if cat in CATEGORIES else len(CATEGORIES), _norm(e["nom"]))


def search(text: str = "", categorie: str = "") -> list[str]:
    """Clés des effets correspondant au texte (nom, source, description ; sans accents) et à la catégorie."""
    needle = _norm(text)
    cat = _norm(categorie)
    out = []
    for k, e in EFFECTS.items():
        if cat and _norm(e["categorie"]) != cat:
            continue
        if needle and needle not in _norm(" ".join((k, e["nom"], e["source"], e["description"]))):
            continue
        out.append(k)
    return sorted(out, key=_sort_key)


def _fmt(value) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value:+d}" if isinstance(value, int) else f"{value:+g}"
    return str(value)


def summary_mods(keys: list[str]) -> dict:
    """Agrège les modificateurs des effets actifs (clés inconnues ignorées)."""
    res = {"ca": 0, "vitesse_mult": 1.0, "vitesse_bonus": 0.0,
           "attaque": [], "js": [], "tests": [], "degats": [], "resistances": [], "notes": []}
    for k in keys:
        e = EFFECTS.get(k)
        if not e:
            continue
        m, nom = e.get("mods") or {}, e["nom"]
        res["ca"] += int(m.get("ca", 0))
        if "vitesse_mult" in m:
            res["vitesse_mult"] *= float(m["vitesse_mult"])
        res["vitesse_bonus"] += float(m.get("vitesse_bonus", 0.0))
        for field in ("attaque", "js", "tests", "degats"):
            if field in m and m[field] not in (None, "", 0):
                res[field].append(f"{_fmt(m[field])} ({nom})")
        for r in m.get("resistances", []) or []:
            res["resistances"].append(f"{r} ({nom})")
        for n in m.get("notes", []) or []:
            res["notes"].append(f"{n} ({nom})")
    if res["vitesse_mult"] == 0:
        res["vitesse_mult"] = 0.0
    return res


_CAT_COLORS = {"Bonus": "#3a9d5d", "Malus": "#c0392b", "État": "#8e6c2f", "Aura": "#2e86c1", "Aptitude": "#8e44ad"}


def tooltip_html(key: str, accent: str = "") -> str:
    """Infobulle HTML (Qt rich text) d'un effet."""
    e = EFFECTS.get(key)
    if not e:
        return ""
    esc = html.escape
    color = accent or _CAT_COLORS.get(e["categorie"], "#c9a227")
    conc = " · <b>Concentration</b>" if e.get("concentration") else ""
    parts = [f"<div style='max-width:360px'>"
             f"<p style='margin:0'><span style='font-size:15pt'>{esc(e['icone'])}</span> "
             f"<b style='color:{esc(color)};font-size:12pt'>{esc(e['nom'])}</b></p>",
             f"<p style='margin:2px 0'><i>{esc(e['categorie'])}</i> — {esc(e['source'])}</p>",
             f"<p style='margin:2px 0'>⏳ Durée : {esc(e['duree'])}{conc}</p>",
             f"<p style='margin:4px 0'>{esc(e['description'])}</p>"]
    m = e.get("mods") or {}
    items = []
    if m.get("ca"):
        items.append(f"CA {_fmt(int(m['ca']))}")
    if "vitesse_mult" in m:
        vm = m["vitesse_mult"]
        items.append("Vitesse 0" if vm == 0 else f"Vitesse ×{vm:g}")
    if m.get("vitesse_bonus"):
        items.append(f"Vitesse {m['vitesse_bonus']:+g} m")
    for field, label in (("attaque", "Attaques"), ("js", "JS"), ("tests", "Tests"), ("degats", "Dégâts")):
        if m.get(field) not in (None, "", 0):
            items.append(f"{label} : {_fmt(m[field])}")
    if m.get("resistances"):
        items.append("Résistance : " + ", ".join(m["resistances"]))
    items += list(m.get("notes", []) or [])
    if items:
        parts.append("<ul style='margin:2px 0 0 -20px'>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>")
    parts.append("</div>")
    return "".join(parts)

from . import mechanics as _mechanics  # noqa: E402,F401  (enregistre résistances, potions, sorts complémentaires)
