"""
Styles de combat (v42) — texte mécanique complet (Manuel des joueurs et Chaudron des merveilles de Tasha, VF) et
répercussion sur la fiche. Utilisé par les infobulles et les résumés (assistant de niveau, onglet Combat).
"""
from __future__ import annotations

STYLES = {
    "Archerie": "Vous gagnez un bonus de +2 aux jets d'attaque effectués avec une arme à distance.",
    "Armes à deux mains": "Quand vous obtenez 1 ou 2 sur un dé de dégâts d'une attaque faite avec une arme de corps à "
                          "corps tenue à deux mains, vous pouvez relancer ce dé et devez utiliser le nouveau résultat, "
                          "même s'il s'agit d'un 1 ou d'un 2. L'arme doit avoir la propriété deux mains ou polyvalente.",
    "Combat à deux armes": "Quand vous combattez à deux armes, vous pouvez ajouter votre modificateur de "
                           "caractéristique aux dégâts de la seconde attaque (attaque en main secondaire, action bonus).",
    "Défense": "Tant que vous portez une armure, vous gagnez un bonus de +1 à la CA.",
    "Duel": "Quand vous maniez une arme de corps à corps dans une main et aucune autre arme, vous gagnez un bonus de +2 "
            "aux jets de dégâts avec cette arme (un bouclier est autorisé).",
    "Protection": "Quand une créature que vous voyez attaque une cible autre que vous située à 1,50 m ou moins de vous, "
                  "vous pouvez utiliser votre réaction pour imposer un désavantage à son jet d'attaque. Vous devez "
                  "manier un bouclier.",
    "Arme de lancer": "Vous pouvez dégainer une arme qui possède la propriété lancer dans le cadre de l'attaque que vous "
                      "faites avec elle. De plus, quand vous touchez avec une attaque à distance faite avec une arme de "
                      "lancer, vous gagnez un bonus de +2 au jet de dégâts.",
    "Combat à mains nues": "Vos frappes à mains nues infligent 1d6 + votre modificateur de Force dégâts contondants, ou "
                           "1d8 + modificateur de Force si vous ne tenez ni arme ni bouclier. Au début de chacun de vos "
                           "tours, vous pouvez infliger 1d4 dégâts contondants à une créature que vous agrippez.",
    "Combat en aveugle": "Vous avez la vision aveugle sur 3 m : vous voyez tout ce qui n'est pas derrière un abri total, "
                         "même si vous êtes aveuglé ou dans les ténèbres, et les créatures invisibles dans ce rayon, à "
                         "moins qu'elles ne réussissent à se cacher de vous.",
    "Interception": "Quand une créature que vous voyez touche une cible autre que vous située à 1,50 m ou moins de "
                    "vous, vous pouvez utiliser votre réaction pour réduire les dégâts subis de 1d10 + votre bonus de "
                    "maîtrise (minimum 0). Vous devez manier un bouclier, ou une arme courante ou de guerre.",
    "Technique supérieure": "Vous apprenez une manœuvre de votre choix parmi celles du Maître de guerre (si elle impose "
                            "un jet de sauvegarde, DD = 8 + bonus de maîtrise + modificateur de Force ou de "
                            "Dextérité). Vous gagnez un dé de supériorité, un d6, qui s'ajoute à ceux d'une autre source "
                            "et se récupère au repos court ou long.",
    "Combattant béni": "Vous apprenez deux sorts mineurs de votre choix dans la liste du clerc. Ils comptent comme des "
                       "sorts de paladin et utilisent le Charisme comme caractéristique d'incantation. Quand vous gagnez "
                       "un niveau de paladin, vous pouvez remplacer l'un d'eux par un autre sort mineur de clerc.",
    "Combattant druidique": "Vous apprenez deux sorts mineurs de votre choix dans la liste du druide. Ils comptent "
                            "comme des sorts de rôdeur et utilisent la Sagesse comme caractéristique d'incantation. Quand "
                            "vous gagnez un niveau de rôdeur, vous pouvez remplacer l'un d'eux par un autre sort mineur "
                            "de druide.",
}

# ce que la fiche fait automatiquement pour chaque style
APPLIED = {
    "Archerie": "+2 ajouté aux attaques à distance (onglet Combat).",
    "Armes à deux mains": "Rappel affiché sur les armes à deux mains ou polyvalentes (relance des 1 et 2).",
    "Combat à deux armes": "Modificateur ajouté aux dégâts de l'attaque en main secondaire.",
    "Défense": "+1 à la CA calculée quand une armure est portée.",
    "Duel": "+2 aux dégâts d'une arme de corps à corps à une main (pas avec deux armes).",
    "Protection": "Tuile de réaction « Protection » dans le groupe ⚡ Réactions.",
    "Arme de lancer": "Rappel « +2 dégâts » sur les armes de lancer.",
    "Combat à mains nues": "Dé des mains nues porté à 1d6 / 1d8.",
    "Combat en aveugle": "Vision aveugle de 3 m dans les sens.",
    "Interception": "Tuile de réaction « Interception » dans le groupe ⚡ Réactions.",
    "Technique supérieure": "Manœuvre à choisir dans l'onglet Combat ; dé de supériorité d6 suivi.",
    "Combattant béni": "Deux sorts mineurs de clerc à choisir (onglet Magie).",
    "Combattant druidique": "Deux sorts mineurs de druide à choisir (onglet Magie).",
}


def style_text(name: str, fallback: str = "") -> str:
    return STYLES.get(name) or fallback


def style_applied(name: str) -> str:
    return APPLIED.get(name, "")
