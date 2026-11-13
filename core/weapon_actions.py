"""
Actions d'arme façon Baldur's Gate 3, traduites en règles de D&D 5e — logique pure (aucune dépendance Qt).

Chaque arme reçoit : sa botte d'arme (PHB 2024, déjà présente dans data/Armes.json)
en tête de liste, puis 1 à 3 actions spéciales inspirées de BG3, attribuées par arme (table explicite)
ou, pour une arme inconnue (homebrew), d'après ses propriétés et son type de dégâts.

Conventions 5e retenues pour les actions inspirées de BG3 :
* en général 1 utilisation par repos court (une seule action d'arme par tour) ;
* DD = 8 + bonus de maîtrise + modificateur d'attaque de l'arme ;
* les distances sont exprimées en mètres (1,5 m = 1 case).
"""
from __future__ import annotations

import html
import re
import unicodedata
from typing import Optional

SRC_BG3 = "Inspiré de Baldur's Gate 3, adapté 5e"
SRC_BOTTE = "PHB 2024 (botte)"
SRC_DMG = "DMG (action optionnelle)"
SRC_PHB = "PHB (action de base)"

BOTTE_TYPE = "Botte d'arme (passive)"
ACTION_TYPE = "Action d'arme"


def _norm(text: str) -> str:
    """Minuscules, sans accents, apostrophes typographiques unifiées, espaces compactés."""
    text = (text or "").replace("’", "'").replace("‘", "'").replace("`", "'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def _a(nom, icone, action, recharge, sauvegarde, condition_dd, succes, echec, description,
       source=SRC_BG3, type_=ACTION_TYPE) -> dict:
    return {"nom": nom, "icone": icone, "action": action, "recharge": recharge,
            "sauvegarde": sauvegarde, "condition_dd": condition_dd, "succes": succes,
            "echec": echec, "description": description, "source": source, "type": type_}


# --------------------------------------------------------------------------------------
# Catalogue des actions
# --------------------------------------------------------------------------------------
ACTIONS: dict[str, dict] = {
    # ---------------- Bottes d'arme (PHB 2024) ----------------
    "botte_coup_double": _a(
        "Coup double", "⚔️", "Passive", "Aucune", None, False,
        "—", "—",
        "Quand vous attaquez avec une arme légère dans le cadre de l'action Attaquer, l'attaque "
        "supplémentaire accordée par la propriété Légère peut être effectuée dans le cadre de cette "
        "même action au lieu de coûter une action bonus. Une seule fois par tour.",
        SRC_BOTTE, BOTTE_TYPE),
    "botte_ecorchure": _a(
        "Écorchure", "🩸", "Passive", "Aucune", None, False,
        "—", "Raté : la cible subit malgré tout des dégâts égaux à votre modificateur de caractéristique.",
        "Si votre jet d'attaque avec cette arme rate une créature, vous lui infligez quand même des "
        "dégâts égaux au modificateur de caractéristique utilisé pour l'attaque, du même type que "
        "l'arme. Ces dégâts ne peuvent être augmentés que par une hausse de ce modificateur.",
        SRC_BOTTE, BOTTE_TYPE),
    "botte_enchainement": _a(
        "Enchaînement", "🪓", "Passive", "1 fois par tour", None, False,
        "—", "Seconde cible touchée : dégâts de l'arme sans modificateur de caractéristique.",
        "Quand vous touchez une créature au corps à corps avec cette arme, vous pouvez effectuer un "
        "second jet d'attaque contre une autre créature située à 1,5 m de la première et à votre portée. "
        "En cas de réussite, elle subit les dégâts de l'arme sans votre modificateur (sauf s'il est "
        "négatif). Une seule fois par tour.",
        SRC_BOTTE, BOTTE_TYPE),
    "botte_ouverture": _a(
        "Ouverture", "🎯", "Passive", "Aucune", None, False,
        "—", "Avantage à votre prochain jet d'attaque contre la cible.",
        "Quand vous touchez une créature avec cette arme et lui infligez des dégâts, vous avez "
        "l'avantage à votre prochain jet d'attaque contre elle avant la fin de votre prochain tour.",
        SRC_BOTTE, BOTTE_TYPE),
    "botte_poussee": _a(
        "Poussée", "💨", "Passive", "Aucune", None, False,
        "—", "Cible de taille G ou inférieure repoussée jusqu'à 3 m.",
        "Quand vous touchez une créature avec cette arme, vous pouvez la repousser en ligne droite "
        "jusqu'à 3 m loin de vous, à condition qu'elle soit de taille G ou inférieure.",
        SRC_BOTTE, BOTTE_TYPE),
    "botte_ralentissement": _a(
        "Ralentissement", "🐌", "Passive", "Aucune", None, False,
        "—", "Ralenti : vitesse réduite de 3 m jusqu'au début de votre prochain tour.",
        "Quand vous touchez une créature avec cette arme et lui infligez des dégâts, sa vitesse "
        "diminue de 3 m jusqu'au début de votre prochain tour. Plusieurs touches ne cumulent pas "
        "cette réduction au-delà de 3 m.",
        SRC_BOTTE, BOTTE_TYPE),
    "botte_renversement": _a(
        "Renversement", "🤸", "Passive", "Aucune", "Constitution", True,
        "La cible reste debout.", "À terre.",
        "Quand vous touchez une créature avec cette arme, vous pouvez l'obliger à faire un jet de "
        "sauvegarde de Constitution (DD = 8 + bonus de maîtrise + modificateur d'attaque). "
        "En cas d'échec, elle tombe À terre.",
        SRC_BOTTE, BOTTE_TYPE),
    "botte_sape": _a(
        "Sape", "🔨", "Passive", "Aucune", None, False,
        "—", "Désavantage au prochain jet d'attaque de la cible.",
        "Quand vous touchez une créature avec cette arme, elle a le désavantage à son prochain jet "
        "d'attaque effectué avant le début de votre prochain tour.",
        SRC_BOTTE, BOTTE_TYPE),

    # ---------------- Actions d'arme inspirées de BG3 ----------------
    "frappe_pommeau": _a(
        "Frappe du pommeau", "🗡️", "Action bonus", "Repos court", "Constitution", True,
        "Dégâts seulement.", "Hébété : pas de réaction et désavantage aux JS de Dextérité jusqu'à la fin de son prochain tour.",
        "Après avoir effectué l'action Attaquer avec une épée, vous frappez du pommeau une créature à "
        "1,5 m : jet d'attaque normal, 1d4 + modificateur dégâts contondants. Si l'attaque touche, la "
        "cible fait un JS de Constitution ; en cas d'échec, elle est hébétée jusqu'à la fin de son "
        "prochain tour."),
    "laceration": _a(
        "Lacération (entaille)", "🩸", "Action", "Repos court", "Constitution", True,
        "Dégâts seulement.", "Saignement : 1d4 tranchants au début de chacun de ses tours.",
        "Vous portez un coup de taille profond (attaque normale avec l'arme). Si l'attaque touche, la "
        "cible fait un JS de Constitution ; en cas d'échec elle saigne pendant 1 minute : 1d4 dégâts "
        "tranchants au début de chacun de ses tours. Le saignement cesse si elle reçoit des soins "
        "magiques, ou si une créature réussit un test de Sagesse (Médecine) DD 10 par une action. "
        "Sans effet sur les créatures artificielles et les morts-vivants."),
    "fauchage": _a(
        "Fauchage", "🦵", "Action", "Repos court", "Dextérité", True,
        "Dégâts seulement.", "À terre.",
        "Vous balayez les appuis de la cible avec votre arme (attaque normale). Si l'attaque touche, la "
        "cible de taille G ou inférieure fait un JS de Dextérité ; en cas d'échec, elle tombe À terre."),
    "percage": _a(
        "Perçage (frappe perforante)", "📌", "Action", "Repos court", "Constitution", True,
        "Dégâts seulement.", "Plaie béante : les attaques contre elle infligent +1d4 dégâts jusqu'à la fin de votre prochain tour.",
        "Vous plongez la pointe de l'arme dans un point faible (attaque normale). Si l'attaque touche, "
        "la cible fait un JS de Constitution ; en cas d'échec, chaque attaque qui la touche inflige "
        "1d4 dégâts perforants supplémentaires jusqu'à la fin de votre prochain tour."),
    "preparation": _a(
        "Préparation", "🛡️", "Action bonus", "Repos court", None, False,
        "—", "—",
        "Vous adoptez une garde d'hast jusqu'au début de votre prochain tour. Quand une créature entre "
        "dans votre allonge, vous pouvez utiliser votre réaction pour lui porter une attaque "
        "d'opportunité ; si elle touche, elle inflige 1d6 dégâts supplémentaires du type de l'arme et "
        "la vitesse de la cible tombe à 0 jusqu'à la fin de son tour."),
    "brise_crane": _a(
        "Brise-crâne (frappe commotionnante)", "💫", "Action", "Repos court", "Constitution", True,
        "Dégâts seulement.", "Étourdi jusqu'au début de votre prochain tour.",
        "Vous assénez un coup violent à la tête (attaque normale avec une arme contondante). Si "
        "l'attaque touche, la cible fait un JS de Constitution ; en cas d'échec, elle est Étourdie "
        "jusqu'au début de votre prochain tour."),
    "frappe_affaiblissante": _a(
        "Frappe affaiblissante", "🥀", "Action", "Repos court", "Constitution", True,
        "Dégâts seulement.", "Affaibli : désavantage aux jets d'attaque et tests de Force, dégâts d'arme −1d4 (1 minute).",
        "Vous frappez un muscle ou une articulation (attaque normale). Si l'attaque touche, la cible "
        "fait un JS de Constitution ; en cas d'échec elle est affaiblie pendant 1 minute. Elle refait "
        "le JS à la fin de chacun de ses tours et met fin à l'effet en cas de réussite."),
    "fendoir": _a(
        "Moulinet de taille (Fendoir)", "🌀", "Action", "Repos court", None, False,
        "—", "Chaque cible touchée subit la moitié des dégâts de l'arme.",
        "Vous décrivez un large arc de cercle : choisissez jusqu'à trois créatures à votre portée, "
        "toutes à 1,5 m l'une de l'autre. Faites un seul jet d'attaque et comparez-le à la CA de "
        "chacune ; chaque cible touchée subit la moitié des dégâts de l'arme (arrondie à l'inférieur)."),
    "charge": _a(
        "Charge", "🐗", "Action", "Repos court", "Dextérité", True,
        "Moitié des dégâts.", "Dégâts complets de l'arme.",
        "Vous vous ruez jusqu'à 6 m en ligne droite sans provoquer d'attaque d'opportunité. Chaque "
        "créature de taille G ou inférieure sur votre trajet fait un JS de Dextérité : échec, elle "
        "subit les dégâts de l'arme (dés + modificateur) ; réussite, la moitié."),
    "tir_handicapant": _a(
        "Tir handicapant", "🦿", "Action", "Repos court", "Constitution", True,
        "Dégâts seulement.", "Ralenti : vitesse divisée par deux jusqu'à la fin de son prochain tour.",
        "Vous visez les jambes (attaque à distance normale). Si l'attaque touche, la cible fait un JS "
        "de Constitution ; en cas d'échec, sa vitesse est divisée par deux jusqu'à la fin de son "
        "prochain tour et elle ne peut pas effectuer l'action Foncer."),
    "tir_mobile": _a(
        "Tir mobile", "🏃", "Partie de l'attaque", "Repos court", None, False,
        "—", "—",
        "Lors d'une attaque à distance, vous pouvez vous déplacer jusqu'à 3 m avant ou après le tir "
        "sans provoquer d'attaque d'opportunité. Ce tir ne subit pas de désavantage du fait d'un "
        "ennemi situé à 1,5 m de vous."),
    "tir_perforant": _a(
        "Tir perforant", "🏹", "Action", "Repos court", "Constitution", True,
        "Dégâts seulement.", "Saignement : 1d4 perforants au début de chacun de ses tours.",
        "Le projectile traverse les protections : l'attaque ignore l'abri partiel et l'abri important. "
        "Si elle touche, la cible fait un JS de Constitution ; en cas d'échec, elle saigne (1d4 par "
        "tour, fin par soins magiques ou test de Médecine DD 10)."),
    "tenacite": _a(
        "Ténacité", "🪨", "Action", "Repos court", None, False,
        "—", "Raté : la cible subit des dégâts contondants égaux à votre modificateur d'attaque (min. 1).",
        "Vous frappez avec obstination (attaque normale). Si l'attaque rate, la cible subit quand même "
        "des dégâts contondants égaux à votre modificateur d'attaque (minimum 1). Si elle touche, elle "
        "inflige 1d4 dégâts contondants supplémentaires."),
    "desarmement": _a(
        "Désarmement", "🤚", "Action", "Repos court", "Force", True,
        "Dégâts seulement.", "Désarmé : lâche un objet tenu, qui tombe à 1,5 m dans la direction de votre choix.",
        "Vous visez la main de l'adversaire (attaque normale). Si l'attaque touche, la cible fait un JS "
        "de Force ; en cas d'échec, elle lâche une arme ou un objet de votre choix qu'elle tient. "
        "Ramasser l'objet lui coûte son interaction gratuite et 1,5 m de déplacement."),
    "briseur_dos": _a(
        "Briseur de dos", "🦴", "Action", "Repos court", "Force", True,
        "Dégâts seulement.", "À terre et vitesse 0 jusqu'à la fin de son prochain tour.",
        "Vous écrasez la colonne de l'adversaire d'un coup puissant (attaque normale). Si l'attaque "
        "touche, la cible fait un JS de Force ; en cas d'échec, elle tombe À terre et ne peut pas se "
        "relever avant la fin de son prochain tour."),
    "arret_coeur": _a(
        "Arrêt-cœur", "💔", "Action", "Repos long", "Constitution", True,
        "Dégâts seulement.", "Pas de réaction, désavantage aux jets d'attaque et ne peut pas regagner de PV jusqu'à la fin de son prochain tour.",
        "Un coup sourd en pleine poitrine (attaque normale, +1d6 dégâts contondants si elle touche). "
        "La cible fait un JS de Constitution ; en cas d'échec, son cœur manque un battement : effets "
        "ci-dessous jusqu'à la fin de son prochain tour."),
    "moulinet": _a(
        "Moulinet", "✨", "Action", "Repos court", "Dextérité", True,
        "Dégâts seulement.", "Déséquilibré : les attaques contre elle ont l'avantage jusqu'au début de votre prochain tour.",
        "Une série de feintes élégantes (attaque normale). Si l'attaque touche, la cible fait un JS de "
        "Dextérité ; en cas d'échec, elle est déséquilibrée. Que l'attaque touche ou non, vous gagnez "
        "+1 à la CA contre cette cible jusqu'au début de votre prochain tour."),
    "coup_cinglant": _a(
        "Coup cinglant", "〰️", "Action bonus", "Repos court", "Dextérité", True,
        "Dégâts seulement.", "Tirée de 3 m vers vous et désavantage à son prochain jet d'attaque.",
        "Après avoir effectué l'action Attaquer, vous faites claquer le fouet sur une créature à votre "
        "allonge (jet d'attaque, 1d4 dégâts tranchants). Si l'attaque touche, la cible fait un JS de "
        "Dextérité ; en cas d'échec, elle est tirée de 3 m vers vous et a le désavantage à son "
        "prochain jet d'attaque."),

    # ---------------- Actions de base / optionnelles ----------------
    "bousculer": _a(
        "Bousculer", "👐", "Partie de l'attaque", "Aucune", "Force", True,
        "Rien ne se passe.", "Repoussée de 1,5 m ou À terre (au choix de l'attaquant).",
        "Remplace une attaque de l'action Attaquer. Une créature de taille au plus supérieure d'un cran "
        "à la vôtre, à 1,5 m, fait un JS de Force ou de Dextérité (à son choix). En cas d'échec, vous "
        "la repoussez de 1,5 m ou la faites tomber À terre.",
        SRC_DMG),
    "lutte": _a(
        "Lutte", "🤼", "Partie de l'attaque", "Aucune", "Force", True,
        "Rien ne se passe.", "Agrippé (vitesse 0) jusqu'à ce qu'elle se libère.",
        "Remplace une attaque de l'action Attaquer ; il vous faut une main libre. La cible, de taille "
        "au plus supérieure d'un cran à la vôtre et à 1,5 m, fait un JS de Force ou de Dextérité. En "
        "cas d'échec elle est Agrippée ; elle peut retenter de se libérer par une action.",
        SRC_PHB),
}

# Botte (libellé du JSON, normalisé) -> clé
_BOTTE_KEYS = {_norm(v["nom"]): k for k, v in ACTIONS.items() if k.startswith("botte_")}

# Attribution explicite façon BG3 (nom normalisé -> clés, botte exclue)
_WEAPON_MAP: dict[str, list[str]] = {
    "baton de combat": ["tenacite", "fauchage"],
    "dague": ["percage", "desarmement"],
    "gourdin": ["brise_crane", "tenacite"],
    "hachette": ["laceration"],
    "javeline": ["charge", "percage"],
    "lance": ["charge", "percage"],
    "marteau leger": ["brise_crane"],
    "masse d'armes": ["frappe_affaiblissante", "brise_crane"],
    "massue": ["brise_crane", "tenacite"],
    "serpe": ["laceration"],
    "arbalete legere": ["tir_perforant", "tir_handicapant"],
    "arc court": ["tir_mobile", "tir_handicapant"],
    "flechette": ["tir_mobile"],
    "fronde": ["tir_handicapant"],
    "cimeterre": ["frappe_pommeau", "laceration", "moulinet"],
    "coutille": ["preparation", "laceration", "fendoir"],
    "epee a deux mains": ["fendoir", "frappe_pommeau", "laceration"],
    "epee courte": ["frappe_pommeau", "percage", "moulinet"],
    "epee longue": ["frappe_pommeau", "laceration"],
    "fleau d'armes": ["frappe_affaiblissante", "brise_crane"],
    "fouet": ["coup_cinglant", "desarmement"],
    "hache a deux mains": ["fendoir", "laceration"],
    "hache d'armes": ["laceration", "fendoir"],
    "hallebarde": ["preparation", "fendoir", "laceration"],
    "lance d'arcon": ["charge", "preparation", "percage"],
    "maillet d'armes": ["briseur_dos", "arret_coeur", "brise_crane"],
    "marteau de guerre": ["brise_crane", "frappe_affaiblissante"],
    "morgenstern": ["percage", "brise_crane"],
    "pic de guerre": ["percage", "frappe_affaiblissante"],
    "pique": ["preparation", "percage", "charge"],
    "rapiere": ["percage", "moulinet", "frappe_pommeau"],
    "trident": ["percage", "desarmement"],
    "arbalete de poing": ["tir_mobile", "tir_perforant"],
    "arbalete lourde": ["tir_perforant", "tir_handicapant"],
    "arc long": ["tir_handicapant", "tir_perforant"],
    "mousquet": ["tir_perforant", "tir_handicapant"],
    "pistolet": ["tir_perforant", "tir_mobile"],
    "sarbacane": ["tir_handicapant"],
    "mains nues": ["bousculer", "lutte"],
}


def _fallback_actions(weapon: dict) -> list[str]:
    """Attribution par propriétés pour une arme absente de la table (homebrew)."""
    nom = _norm(weapon.get("nom", ""))
    props = {_norm(p).split(" ")[0] for p in weapon.get("proprietes", []) or []}
    dmg = _norm(weapon.get("type_degats", ""))
    out: list[str] = []
    if weapon.get("type") == "distance":
        if "arc" in nom:
            out += ["tir_mobile", "tir_handicapant"]
        elif "arbalete" in nom or "chargement" in props:
            out += ["tir_perforant", "tir_handicapant"]
        else:
            out += ["tir_handicapant"]
        return out[:3]
    if "epee" in nom:
        out.append("frappe_pommeau")
    if "allonge" in props:
        out.append("preparation")
    if dmg.startswith("tranchant"):
        out.append("laceration")
        if "lourde" in props:
            out.append("fendoir")
    elif dmg.startswith("perforant"):
        out.append("percage")
        if "lancer" in props:
            out.append("charge")
    elif dmg.startswith("contondant"):
        out += ["brise_crane", "briseur_dos"] if "lourde" in props else ["brise_crane", "tenacite"]
    if not out:
        out.append("bousculer")
    return list(dict.fromkeys(out))[:3]


def botte_key(weapon: dict) -> Optional[str]:
    return _BOTTE_KEYS.get(_norm(weapon.get("botte", "")))


def actions_for_weapon(weapon: dict, botte: bool = True, extras: bool = True) -> list[str]:
    """
    Clés d'actions de l'arme, botte d'arme en premier (1 à 4 entrées).
    v52 : `botte` = maîtrise d'arme 2024 permise (règle de la table + arme maîtrisée), `extras` = actions BG3.
    Sans botte ni actions BG3, il reste l'action de base (Bousculer).
    """
    keys: list[str] = []
    b = botte_key(weapon) if botte else None
    if b:
        keys.append(b)
    if extras:
        extra = _WEAPON_MAP.get(_norm(weapon.get("nom", "")))
        if extra is None:
            extra = _fallback_actions(weapon)
        for k in extra:
            if k in ACTIONS and k not in keys:
                keys.append(k)
    if not keys:
        keys.append("bousculer")
    return keys[:4]


def compute_dd(attack_mod: int, prof: int) -> int:
    return 8 + int(prof) + int(attack_mod)


def weapon_action_rows(weapon: dict, attack_mod: int, prof: int, botte: bool = True, extras: bool = True) -> list[dict]:
    """Actions de l'arme enrichies de « cle » et « dd » (int si la règle utilise le DD, sinon None)."""
    rows = []
    for k in actions_for_weapon(weapon, botte, extras):
        row = dict(ACTIONS[k])
        row["cle"] = k
        row["dd"] = compute_dd(attack_mod, prof) if row.get("condition_dd") else None
        if k.startswith("botte_") and weapon.get("botte_desc"):
            row["botte_desc"] = weapon["botte_desc"]
        rows.append(row)
    return rows


def tooltip_html(row: dict, accent: str = "") -> str:
    """Infobulle HTML (Qt rich text) décrivant une action d'arme."""
    e = html.escape
    color = accent or "#c9a227"
    parts = [f"<div style='max-width:360px'>"
             f"<p style='margin:0'><span style='font-size:15pt'>{e(row.get('icone', ''))}</span> "
             f"<b style='color:{e(color)};font-size:12pt'>{e(row.get('nom', ''))}</b></p>",
             f"<p style='margin:2px 0'><i>{e(row.get('type', ACTION_TYPE))}</i> — "
             f"<b>{e(row.get('action', ''))}</b> · Recharge : {e(row.get('recharge', 'Aucune'))}</p>"]
    if row.get("sauvegarde"):
        dd = row.get("dd")
        dd_txt = f"DD {dd}" if dd is not None else "DD 8 + maîtrise + mod. d'attaque"
        parts.append(f"<p style='margin:2px 0'>🎲 JS de <b>{e(row['sauvegarde'])}</b> — <b>{e(dd_txt)}</b></p>")
    succ, ech = row.get("succes", "—"), row.get("echec", "—")
    if succ and succ != "—":
        parts.append(f"<p style='margin:2px 0'>✅ <b>Réussite :</b> {e(succ)}</p>")
    if ech and ech != "—":
        label = "Échec" if row.get("sauvegarde") else "Effet"
        parts.append(f"<p style='margin:2px 0'>❌ <b>{label} :</b> {e(ech)}</p>")
    parts.append(f"<p style='margin:4px 0'>{e(row.get('description', ''))}</p>")
    if row.get("botte_desc"):
        parts.append(f"<p style='margin:2px 0;color:gray'><i>Fiche de l'arme : {e(row['botte_desc'])}</i></p>")
    parts.append(f"<p style='margin:2px 0;color:gray;font-size:8pt'>{e(row.get('source', ''))}</p></div>")
    return "".join(parts)
