#!/usr/bin/env python3
"""
Manifestations occultes (Eldritch Invocations) — référentiel corrigé v37 (idempotent).

Réécrit data/Manifestations_occultes.json à partir de la table ci-dessous, auditée sur les règles officielles
(Manuel des joueurs, Guide complet de Xanathar, Chaudron des merveilles de Tasha), en VF :

  * « prerequis » structuré : niveau d'Occultiste, pacte, sort mineur requis (Décharge occulte), condition
    spéciale (sort Maléfice ou aptitude de malédiction) ;
  * « sorts » explicites : sort accordé, usage affiché, « emplacement » (true = dépense un emplacement de sort
    d'occultiste), « limite » (repos qui recharge l'utilisation unique, "" = à volonté) ;
  * « effets » : étiquettes lues par le moteur (core/invocations.py) pour répercuter la manifestation sur la fiche ;
  * « source » : PHB / XGtE / TCoE.

    python tools/invocation_fixes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "Manifestations_occultes.json"

EB = "Décharge occulte"
HEX = "le sort Maléfice ou une aptitude d'occultiste qui maudit (Malédiction de la Lame maudite)"


def inv(nom, source, description, niveau=0, pacte="", sort="", special="", sorts=None, effets=None):
    cat = pacte or ("Niveau {}".format(niveau) if niveau else "Communes")
    if pacte and niveau:
        cat = "{} (Niv. {})".format(pacte, niveau)
    return {"nom": nom, "categorie": cat, "source": source,
            "prerequis": {"niveau": niveau, "pacte": pacte, "sort": sort, "special": special},
            "description": description, "sorts": sorts or [], "effets": effets or []}


def grant(sort, usage, emplacement=False, limite="", cible=""):
    return {"sort": sort, "usage": usage, "emplacement": emplacement, "limite": limite, "cible": cible}


AT_WILL = "À volonté (sans emplacement)"
ONCE_SLOT = "1 fois / repos long (emplacement d'occultiste)"
ONCE_FREE = "1 fois / repos long (gratuit)"

INVOCATIONS = [
    # ---------------------------------------------------------------- Manuel des joueurs
    inv("Armure d'ombres", "PHB", "Vous pouvez lancer Armure de mage sur vous-même à volonté, sans dépenser "
        "d'emplacement de sort ni de composantes matérielles. Tant que le sort est actif et que vous ne portez pas "
        "d'armure, votre CA de base devient 13 + modificateur de Dextérité.",
        sorts=[grant("Armure de mage", AT_WILL + ", sur soi", cible="soi")], effets=["armure_mage"]),
    inv("Décharge déchirante", "PHB", "Quand vous lancez Décharge occulte, ajoutez votre modificateur de Charisme "
        "aux dégâts de chaque rayon qui touche (1d10 + modificateur de Charisme par rayon).", sort=EB,
        effets=["decharge:plat_cha"]),
    inv("Décharge répulsive", "PHB", "Quand vous touchez une créature avec un rayon de Décharge occulte, vous "
        "pouvez la repousser jusqu'à 3 m (2 cases) en ligne droite, à l'opposé de vous — à chaque rayon qui touche.",
        sort=EB, effets=["decharge:repousse"]),
    inv("Esprit occulte", "TCoE", "Vous avez l'avantage aux jets de sauvegarde de Constitution effectués pour "
        "maintenir votre concentration sur un sort.", effets=["concentration_avantage"]),
    inv("Étreinte de Hadar", "XGtE", "Une fois par tour, quand vous touchez une créature avec Décharge occulte, vous "
        "pouvez la déplacer en ligne droite de 3 m (2 cases) vers vous.", sort=EB, effets=["decharge:attire"]),
    inv("Lance de léthargie", "XGtE", "Une fois par tour, quand vous touchez une créature avec Décharge occulte, vous "
        "pouvez réduire sa vitesse de 3 m (2 cases) jusqu'à la fin de votre prochain tour.", sort=EB,
        effets=["decharge:ralentit"]),
    inv("Lance occulte", "PHB", "Quand vous lancez Décharge occulte, sa portée passe à 90 m (60 cases).", sort=EB,
        effets=["decharge:portee"]),
    inv("Langage animal", "PHB", "Vous pouvez lancer Communication avec les animaux à volonté, sans dépenser "
        "d'emplacement de sort.", sorts=[grant("Communication avec les animaux", AT_WILL)]),
    inv("Mille visages", "PHB", "Vous pouvez lancer Déguisement à volonté, sans dépenser d'emplacement de sort.",
        sorts=[grant("Déguisement", AT_WILL)]),
    inv("Œil du gardien des runes", "PHB", "Vous pouvez lire toutes les écritures.", effets=["lecture"]),
    inv("Perception transférée", "PHB", "Par une action, vous touchez un humanoïde consentant et percevez par ses sens "
        "jusqu'à la fin de votre prochain tour. Tant que la créature est sur le même plan que vous, vous pouvez "
        "utiliser votre action lors des tours suivants pour maintenir ce lien jusqu'à la fin de votre tour suivant. "
        "Pendant ce temps, vous êtes aveuglé et assourdi vis-à-vis de votre propre environnement.",
        effets=["action:perception_transferee"]),
    inv("Présence captivante", "PHB", "Vous gagnez la maîtrise des compétences Tromperie et Persuasion.",
        effets=["competence:Tromperie", "competence:Persuasion"]),
    inv("Vigueur fiélonne", "PHB", "Vous pouvez lancer Simulacre de vie sur vous-même à volonté, comme un sort de "
        "niveau 1, sans dépenser d'emplacement de sort ni de composantes matérielles.",
        sorts=[grant("Simulacre de vie", AT_WILL + ", sur soi (niveau 1)", cible="soi")]),
    inv("Vision du diable", "PHB", "Vous voyez normalement dans les ténèbres, magiques ou non, jusqu'à une distance "
        "de 36 m.", effets=["vision_diable"]),
    inv("Vision occulte", "PHB", "Vous pouvez lancer Détection de la magie à volonté, sans dépenser d'emplacement de "
        "sort.", sorts=[grant("Détection de la magie", AT_WILL)]),
    inv("Visions embrumées", "PHB", "Vous pouvez lancer Image silencieuse à volonté, sans dépenser d'emplacement de "
        "sort ni de composantes matérielles.", sorts=[grant("Image silencieuse", AT_WILL)]),
    inv("Voleur des cinq destinées", "PHB", "Vous pouvez lancer Fléau une fois en utilisant un emplacement de sort "
        "d'occultiste. Vous ne pouvez plus le faire avant d'avoir terminé un repos long.",
        sorts=[grant("Fléau", ONCE_SLOT, emplacement=True, limite="repos long")]),
    inv("Arme de pacte améliorée", "XGtE", "Vous pouvez utiliser toute arme invoquée par votre Pacte de la lame comme "
        "focaliseur d'incantation. Elle devient une arme magique avec un bonus de +1 aux jets d'attaque et de dégâts, "
        "sauf si c'est déjà une arme magique conférant un bonus à ces jets. Votre arme de pacte peut aussi être un arc "
        "court, un arc long, une arbalète légère ou une arbalète lourde.", pacte="Pacte de la lame",
        effets=["arme_pacte:+1"]),
    inv("Attaque occulte", "XGtE", "Une fois par tour, quand vous touchez une créature avec votre arme de pacte, "
        "vous pouvez dépenser un emplacement de sort d'occultiste : la cible subit 1d8 dégâts de force "
        "supplémentaires, plus 1d8 par niveau de l'emplacement, et tombe à terre si elle est de taille Très grande "
        "ou inférieure.", niveau=5, pacte="Pacte de la lame", effets=["action:attaque_occulte"]),
    inv("Buveuse de vie", "PHB", "Quand vous touchez une créature avec votre arme de pacte, elle subit des dégâts "
        "nécrotiques supplémentaires égaux à votre modificateur de Charisme (minimum 1).", niveau=12,
        pacte="Pacte de la lame", effets=["arme_pacte:necrotique_cha"]),
    inv("Lame assoiffée", "PHB", "Vous pouvez attaquer deux fois, au lieu d'une, avec votre arme de pacte lorsque "
        "vous effectuez l'action Attaquer lors de votre tour.", niveau=5, pacte="Pacte de la lame",
        effets=["attaques:2"]),
    inv("Aspect de la lune", "XGtE", "Vous n'avez plus besoin de dormir et ne pouvez pas être forcé à dormir par "
        "quelque moyen que ce soit. Pour bénéficier d'un repos long, vous pouvez passer les 8 heures à pratiquer des "
        "activités légères, comme lire votre Livre des ombres et monter la garde.", pacte="Pacte du grimoire",
        effets=["sommeil_immunite"]),
    inv("Livre des secrets anciens", "PHB", "Vous pouvez inscrire des rituels magiques dans votre Livre des ombres. "
        "Choisissez deux sorts de niveau 1 possédant l'étiquette rituel, issus de la liste de sorts de n'importe quelle "
        "classe (pas forcément la même). Ils figurent dans le livre, ne comptent pas dans vos sorts connus et ne se "
        "lancent que comme rituels, sauf si vous les avez appris autrement. Vous pouvez y recopier d'autres rituels "
        "trouvés au fil de l'aventure, d'un niveau au plus égal à la moitié de votre niveau d'occultiste (arrondie au "
        "supérieur) : 2 heures et 50 po par niveau du sort.", pacte="Pacte du grimoire", effets=["livre_rituels"]),
    inv("Scribe des horizons", "TCoE", "Une nouvelle page apparaît dans votre Livre des ombres. Par une action, une "
        "créature peut y écrire son nom : la page peut contenir un nombre de noms égal à votre bonus de maîtrise. Vous "
        "pouvez lancer Communication à distance en ciblant une créature dont le nom figure sur la page, sans dépenser "
        "d'emplacement de sort ni de composantes matérielles ; le message est écrit sur la page au lieu d'être "
        "prononcé.", niveau=5, pacte="Pacte du grimoire",
        sorts=[grant("Communication à distance", AT_WILL + ", noms inscrits uniquement")], effets=["noms_bm"]),
    inv("Présent des sauveurs", "TCoE", "Une nouvelle page apparaît dans votre Livre des ombres. Par une action, une "
        "créature peut y écrire son nom : la page peut contenir un nombre de noms égal à votre bonus de maîtrise. "
        "Quand une créature dont le nom figure sur la page tombe à 0 point de vie sans être tuée sur le coup, elle "
        "tombe à 1 point de vie à la place. Une fois cette protection déclenchée, elle ne peut plus l'être avant que "
        "vous ayez terminé un repos long.", niveau=9, pacte="Pacte du grimoire",
        effets=["action:present_sauveurs", "noms_bm"]),
    inv("Don des immortels", "XGtE", "Quand vous regagnez des points de vie alors que votre familier se trouve à 30 m "
        "ou moins de vous, traitez chaque dé lancé pour déterminer les points de vie regagnés comme s'il avait obtenu "
        "son résultat maximal.", pacte="Pacte de la chaîne", effets=["soins_maximaux"]),
    inv("Engagement du maître", "TCoE", "Quand vous lancez Appel de familier, la créature invoquée gagne : une vitesse "
        "de vol ou de nage (au choix) de 12 m ; par une action bonus, vous pouvez lui ordonner d'effectuer l'action "
        "Attaquer ; ses attaques d'arme sont magiques ; si elle force une créature à faire un jet de sauvegarde, elle "
        "utilise votre DD de sauvegarde des sorts ; quand elle subit des dégâts, vous pouvez utiliser votre réaction "
        "pour lui accorder la résistance contre ces dégâts.", pacte="Pacte de la chaîne",
        effets=["familier_ameliore", "action:engagement_ordre", "action:engagement_resistance"]),
    inv("Voix du maître des chaînes", "PHB", "Vous pouvez communiquer télépathiquement avec votre familier et percevoir "
        "par ses sens tant que vous êtes sur le même plan d'existence. En outre, en percevant par ses sens, vous pouvez "
        "parler par sa bouche avec votre propre voix, même si votre familier est normalement incapable de parler.",
        pacte="Pacte de la chaîne", effets=["familier_telepathie"]),
    inv("Chaîne des carcères", "PHB", "Vous pouvez lancer Immobilisation de monstre à volonté, en ciblant uniquement un "
        "céleste, un fiélon ou un élémentaire, sans dépenser d'emplacement de sort ni de composantes matérielles. Vous "
        "devez terminer un repos long avant de pouvoir utiliser cette manifestation de nouveau sur la même créature.",
        niveau=15, pacte="Pacte de la chaîne",
        sorts=[grant("Immobilisation de monstre", AT_WILL + ", céleste, fiélon ou élémentaire (pas deux fois la même "
                     "créature avant un repos long)")]),
    inv("Réprimande du talisman", "TCoE", "Quand le porteur de votre talisman est touché par un attaquant que vous "
        "voyez à 9 m ou moins de vous, vous pouvez utiliser votre réaction pour infliger à l'attaquant des dégâts "
        "psychiques égaux à votre bonus de maîtrise et le repousser jusqu'à 3 m de vous.", pacte="Pacte du talisman",
        effets=["action:reprimande_talisman"]),
    inv("Protection du talisman", "TCoE", "Quand le porteur de votre talisman rate un jet de sauvegarde, il peut "
        "ajouter 1d4 au jet, ce qui peut transformer l'échec en réussite. Utilisable un nombre de fois égal à votre "
        "bonus de maîtrise ; toutes les utilisations sont récupérées au repos long.", niveau=7,
        pacte="Pacte du talisman", effets=["action:protection_talisman"]),
    inv("Lien du talisman", "TCoE", "Tant que quelqu'un porte votre talisman, vous pouvez utiliser votre action pour "
        "vous téléporter dans un espace inoccupé à 1,50 m ou moins de lui, à condition d'être sur le même plan. Le "
        "porteur peut faire de même pour vous rejoindre. Utilisable un nombre de fois égal à votre bonus de maîtrise ; "
        "toutes les utilisations sont récupérées au repos long.", niveau=12, pacte="Pacte du talisman",
        effets=["action:lien_talisman"]),
    inv("Avachissement", "PHB", "Vous pouvez lancer Lenteur une fois en utilisant un emplacement de sort "
        "d'occultiste. Vous ne pouvez plus le faire avant d'avoir terminé un repos long.", niveau=5,
        sorts=[grant("Lenteur", ONCE_SLOT, emplacement=True, limite="repos long")]),
    inv("Don des profondeurs", "XGtE", "Vous pouvez respirer sous l'eau et vous gagnez une vitesse de nage égale à votre "
        "vitesse de marche. Vous pouvez aussi lancer Respiration aquatique une fois sans dépenser d'emplacement de "
        "sort ; vous récupérez cette possibilité à la fin d'un repos long.", niveau=5,
        sorts=[grant("Respiration aquatique", ONCE_FREE, limite="repos long")], effets=["nage", "respiration_eau"]),
    inv("Maître des ombres", "PHB", "Quand vous vous trouvez dans une zone de lumière faible ou de ténèbres, vous "
        "pouvez utiliser votre action pour devenir invisible jusqu'à ce que vous vous déplaciez ou que vous effectuiez "
        "une action ou une réaction.", niveau=5, effets=["action:maitre_ombres"]),
    inv("Maléfice accablant", "XGtE", "Par une action bonus, vous provoquez une vague de douleur psychique autour d'une "
        "créature maudite par votre sort Maléfice ou par une aptitude d'occultiste (Malédiction de la Lame maudite…). "
        "La cible et chaque créature de votre choix à 1,50 m ou moins d'elle subissent des dégâts psychiques égaux à "
        "votre modificateur de Charisme (minimum 1). La cible maudite doit se trouver à 9 m ou moins de vous.",
        niveau=5, special=HEX, effets=["action:malefice_accablant"]),
    inv("Servitude de la tombe", "TCoE", "Vous pouvez lancer Animation des morts sans dépenser d'emplacement de sort. "
        "Vous ne pouvez plus le faire avant d'avoir terminé un repos long.", niveau=5,
        sorts=[grant("Animation des morts", ONCE_FREE, limite="repos long")]),
    inv("Sombre présage", "PHB", "Vous pouvez lancer Malédiction une fois en utilisant un emplacement de sort "
        "d'occultiste. Vous ne pouvez plus le faire avant d'avoir terminé un repos long.", niveau=5,
        sorts=[grant("Malédiction", ONCE_SLOT, emplacement=True, limite="repos long")]),
    inv("Tombe de Levistus", "XGtE", "Par une réaction, quand vous subissez des dégâts, vous vous enfermez dans la glace "
        "jusqu'à la fin de votre prochain tour. Vous gagnez 10 points de vie temporaires par niveau d'occultiste, qui "
        "absorbent autant que possible les dégâts déclencheurs. Juste après, vous gagnez la vulnérabilité aux dégâts de "
        "feu, votre vitesse tombe à 0 et vous êtes neutralisé. À la fin de votre prochain tour, la glace fond et ces "
        "effets prennent fin. Une fois utilisée, cette manifestation se recharge au repos court ou long.", niveau=5,
        effets=["action:tombe_levistus"]),
    inv("Voile de mouches", "XGtE", "Par une action bonus, vous vous entourez d'une aura de mouches bourdonnantes dans un "
        "rayon de 1,50 m, jusqu'à ce que vous soyez neutralisé ou que vous la congédiiez par une action bonus. Vous "
        "avez l'avantage aux tests de Charisme (Intimidation), mais le désavantage à tous les autres tests de Charisme. "
        "Toute autre créature qui commence son tour dans l'aura subit des dégâts de poison égaux à votre modificateur "
        "de Charisme (minimum 0). Une fois utilisée, cette manifestation se recharge au repos court ou long.", niveau=5,
        effets=["action:voile_mouches"]),
    inv("Fuite de l'escamoteur", "XGtE", "Vous pouvez lancer Liberté de mouvement une fois sur vous-même sans dépenser "
        "d'emplacement de sort. Vous récupérez cette possibilité à la fin d'un repos long.", niveau=7,
        sorts=[grant("Liberté de mouvement", ONCE_FREE + ", sur soi", limite="repos long", cible="soi")]),
    inv("Maléfice implacable", "XGtE", "Par une action bonus, vous vous téléportez jusqu'à 9 m vers un espace inoccupé "
        "que vous voyez, à 1,50 m ou moins de la créature maudite par votre sort Maléfice ou par une aptitude "
        "d'occultiste (Malédiction de la Lame maudite…). La cible doit se trouver à 9 m ou moins de vous.", niveau=7,
        special=HEX, effets=["action:malefice_implacable"]),
    inv("Mot d'effroi", "PHB", "Vous pouvez lancer Confusion une fois en utilisant un emplacement de sort d'occultiste. "
        "Vous ne pouvez plus le faire avant d'avoir terminé un repos long.", niveau=7,
        sorts=[grant("Confusion", ONCE_SLOT, emplacement=True, limite="repos long")]),
    inv("Murmures impérieux", "PHB", "Vous pouvez lancer Compulsion une fois en utilisant un emplacement de sort "
        "d'occultiste. Vous ne pouvez plus le faire avant d'avoir terminé un repos long.", niveau=7,
        sorts=[grant("Compulsion", ONCE_SLOT, emplacement=True, limite="repos long")]),
    inv("Regard fantomatique", "XGtE", "Par une action, vous gagnez la capacité de voir à travers les objets solides "
        "jusqu'à 9 m, pendant 1 minute au maximum, tant que vous vous concentrez (comme pour un sort). Durant ce temps, "
        "vous percevez les objets comme des images fantomatiques et transparentes, et vous voyez dans le noir comme "
        "dans la pénombre (vision dans le noir). Une fois utilisée, cette manifestation se recharge au repos court ou "
        "long.", niveau=7, effets=["action:regard_fantomatique"]),
    inv("Sculpteur de chair", "PHB", "Vous pouvez lancer Métamorphose une fois en utilisant un emplacement de sort "
        "d'occultiste. Vous ne pouvez plus le faire avant d'avoir terminé un repos long.", niveau=7,
        sorts=[grant("Métamorphose", ONCE_SLOT, emplacement=True, limite="repos long")]),
    inv("Murmures de la tombe", "PHB", "Vous pouvez lancer Communication avec les morts à volonté, sans dépenser "
        "d'emplacement de sort.", niveau=9, sorts=[grant("Communication avec les morts", AT_WILL)]),
    inv("Pas aérien", "PHB", "Vous pouvez lancer Lévitation sur vous-même à volonté, sans dépenser d'emplacement de "
        "sort ni de composantes matérielles.", niveau=9,
        sorts=[grant("Lévitation", AT_WILL + ", sur soi", cible="soi")]),
    inv("Saut d'outre-tombe", "PHB", "Vous pouvez lancer Saut sur vous-même à volonté, sans dépenser d'emplacement de "
        "sort ni de composantes matérielles.", niveau=9, sorts=[grant("Saut", AT_WILL + ", sur soi", cible="soi")]),
    inv("Sbire du chaos", "PHB", "Vous pouvez lancer Invocation d'élémentaire une fois en utilisant un emplacement de "
        "sort d'occultiste. Vous ne pouvez plus le faire avant d'avoir terminé un repos long.", niveau=9,
        sorts=[grant("Invocation d'élémentaire", ONCE_SLOT, emplacement=True, limite="repos long")]),
    inv("Maître des formes", "PHB", "Vous pouvez lancer Modification d'apparence à volonté, sans dépenser "
        "d'emplacement de sort.", niveau=15, sorts=[grant("Modification d'apparence", AT_WILL, cible="soi")]),
    inv("Royaumes lointains", "PHB", "Vous pouvez lancer Œil magique à volonté, sans dépenser d'emplacement de sort.",
        niveau=15, sorts=[grant("Oeil magique", AT_WILL)]),
    inv("Vision sorcière", "PHB", "Vous voyez la véritable forme de tout métamorphe ou de toute créature dissimulée par "
        "une magie d'illusion ou de transmutation tant qu'elle se trouve à 9 m ou moins de vous et dans votre champ de "
        "vision.", niveau=15, effets=["vision_veritable_9m"]),
    inv("Voile d'ombres", "XGtE", "Vous pouvez lancer Invisibilité à volonté, sans dépenser d'emplacement de sort.",
        niveau=15, sorts=[grant("Invisibilité", AT_WILL)]),
]

RENAMES = {"Etreinte de Hadar": "Étreinte de Hadar"}


def apply(path: Path = PATH) -> int:
    path.write_text(json.dumps({"manifestations_occultes": INVOCATIONS}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    return len(INVOCATIONS)


if __name__ == "__main__":
    print("{} manifestations occultes écrites dans {}".format(apply(), PATH.name))
    sys.exit(0)
