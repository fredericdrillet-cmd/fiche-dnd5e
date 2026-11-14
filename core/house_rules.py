"""
Règles de la table (v52) : mécaniques optionnelles activables indépendamment de l'édition du personnage.

Les choix sont enregistrés dans le personnage (`Character.regles_optionnelles`, {clé: bool}) ; une clé absente
prend la valeur par défaut du mode d'édition (`defaults_for`). Les préférences peuvent définir des valeurs par défaut
propres à la table pour les nouveaux personnages.

Les anciennes sauvegardes (sans ce champ) gardent le comportement des versions précédentes : potion en action bonus,
bottes d'arme et actions d'arme toujours actives (`LEGACY`).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from . import editions as E


@dataclass(frozen=True)
class HouseRule:
    cle: str
    nom: str
    description: str
    origine: str
    categorie: str
    defaut_2014: bool
    defaut_2024: bool


RULES: tuple[HouseRule, ...] = (
    HouseRule(
        "potion_action_bonus", "Potion en action bonus",
        "Boire soi-même une potion ne coûte qu'une action bonus (au lieu d'une action). Administrer une potion à "
        "un allié reste une action (« Utiliser un objet »).",
        "Règle maison courante, inspirée de 2024", "Combat", False, True),
    HouseRule(
        "maitrises_armes_2014", "Maîtrises d'armes (bottes) sur l'arsenal 2014",
        "Les propriétés de maîtrise de 2024 (Coup double, Entaille, Poussée, Ralentissement, Renversement, Sape, "
        "Vexation, Effleurement) s'appliquent aux armes 2014 que le personnage maîtrise.",
        "Manuel des joueurs 2024", "Combat", False, True),
    HouseRule(
        "inspiration_heroique", "Inspiration héroïque (2024)",
        "L'inspiration permet de relancer n'importe quel dé juste après l'avoir lancé (le nouveau résultat "
        "s'impose). Un personnage n'en a qu'une à la fois : s'il en reçoit une autre, il peut la donner à un allié "
        "qui n'en a pas. Désactivée : règle 2014 (avantage à un jet d'attaque, de sauvegarde ou de caractéristique).",
        "Manuel des joueurs 2024", "Héroïsme", False, True),
    HouseRule(
        "actions_arme_bg3", "Actions d'arme façon Baldur's Gate 3",
        "Chaque arme propose 1 à 3 actions spéciales (Lacération, Brise-crâne, Désarmement…) avec un DD et une "
        "recharge. Règle maison : n'existe dans aucune édition officielle.",
        "Règle maison de l'application", "Combat", True, True),
)
BY_KEY: dict[str, HouseRule] = {r.cle: r for r in RULES}

# comportement des versions ≤ 51, conservé pour les sauvegardes qui n'ont pas encore de règles de la table
LEGACY: dict[str, bool] = {"potion_action_bonus": True, "maitrises_armes_2014": True, "inspiration_heroique": False,
                           "actions_arme_bg3": True}


def defaults_for(mode: str) -> dict[str, bool]:
    """Valeurs par défaut des règles selon le mode d'édition (le mode libre suit les valeurs de 2024)."""
    use_2024 = E.normalize_mode(mode) != E.MODE_2014
    return {r.cle: (r.defaut_2024 if use_2024 else r.defaut_2014) for r in RULES}


def resolve(stored: Optional[dict], mode: str) -> dict[str, bool]:
    """Règles effectives : choix enregistrés, complétés par les valeurs par défaut du mode."""
    out = defaults_for(mode)
    for key, value in (stored or {}).items():
        if key in BY_KEY:
            out[key] = bool(value)
    return out


def is_active(stored: Optional[dict], mode: str, key: str) -> bool:
    return resolve(stored, mode).get(key, False)


def clean(stored: Optional[dict]) -> dict[str, bool]:
    """Ne garde que les clés connues, en booléens (lecture d'une sauvegarde ou des préférences)."""
    return {k: bool(v) for k, v in (stored or {}).items() if k in BY_KEY} if isinstance(stored, dict) else {}


def inspiration_text(heroic: bool) -> str:
    """Effet de l'inspiration selon la règle active."""
    if heroic:
        return ("Inspiration héroïque (2024) : relancez un dé juste après l'avoir lancé et gardez le nouveau "
                "résultat. Si vous en recevez une alors que vous en avez déjà une, donnez-la à un allié qui n'en a pas.")
    return ("Inspiration (2014) : avantage à un jet d'attaque, de sauvegarde ou de caractéristique. Vous pouvez la "
            "donner à un autre joueur.")
