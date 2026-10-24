"""
Règles de Donjons & Dragons 5e — logique pure (aucune dépendance à l'interface graphique).

Toutes les fonctions de ce module sont déterministes (sauf les tirages de dés, qui acceptent
un générateur aléatoire injectable pour pouvoir être testés).
"""
from __future__ import annotations

import math
import random
import re
import unicodedata
from typing import Iterable, Optional

# --------------------------------------------------------------------------------------
# Constantes générales
# --------------------------------------------------------------------------------------
ABILITIES = ["Force", "Dextérité", "Constitution", "Intelligence", "Sagesse", "Charisme"]
ABBR = {"Force": "FOR", "Dextérité": "DEX", "Constitution": "CON",
        "Intelligence": "INT", "Sagesse": "SAG", "Charisme": "CHA"}
# Abréviations utilisées dans les JSON de sorts ("Dex", "Sag"...) -> nom complet
ABBR_TO_FULL = {"for": "Force", "dex": "Dextérité", "con": "Constitution",
                "int": "Intelligence", "sag": "Sagesse", "cha": "Charisme"}

MAX_LEVEL = 20

ALIGNMENTS = [
    "Loyal Bon", "Neutre Bon", "Chaotique Bon",
    "Loyal Neutre", "Neutre", "Chaotique Neutre",
    "Loyal Mauvais", "Neutre Mauvais", "Chaotique Mauvais",
]

# Seuils d'expérience officiels (niveau -> XP minimale)
XP_THRESHOLDS = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
                 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]

# Nombre de compétences de classe à choisir (le fichier Classes_Depart.json ne le précise pas)
CLASS_SKILL_COUNT = {
    "Barbare": 2, "Barde": 3, "Clerc": 2, "Druide": 2, "Guerrier": 2, "Moine": 2, "Paladin": 2,
    "Rôdeur": 3, "Roublard": 4, "Ensorceleur": 2, "Magicien": 2, "Occultiste": 2, "Artificier": 2,
}

# Niveau auquel la sous-classe est choisie
SUBCLASS_LEVEL = {
    "Barbare": 3, "Barde": 3, "Clerc": 1, "Druide": 2, "Ensorceleur": 1, "Guerrier": 3,
    "Magicien": 2, "Moine": 3, "Occultiste": 1, "Paladin": 3, "Rôdeur": 3, "Roublard": 3,
    "Artificier": 3,
}

# Prérequis de multiclassage : liste de (caractéristique, minimum) ; "ou" = une seule suffit
MULTICLASS_PREREQ = {
    "Barbare": ([("Force", 13)], "et"), "Barde": ([("Charisme", 13)], "et"),
    "Clerc": ([("Sagesse", 13)], "et"), "Druide": ([("Sagesse", 13)], "et"),
    "Guerrier": ([("Force", 13), ("Dextérité", 13)], "ou"),
    "Moine": ([("Dextérité", 13), ("Sagesse", 13)], "et"),
    "Paladin": ([("Force", 13), ("Charisme", 13)], "et"),
    "Rôdeur": ([("Dextérité", 13), ("Sagesse", 13)], "et"),
    "Roublard": ([("Dextérité", 13)], "et"), "Ensorceleur": ([("Charisme", 13)], "et"),
    "Occultiste": ([("Charisme", 13)], "et"), "Magicien": ([("Intelligence", 13)], "et"),
    "Artificier": ([("Intelligence", 13)], "et"),
}

# Maîtrises gagnées en ajoutant une classe (multiclassage), hors classe de départ
MULTICLASS_PROFS = {
    "Barbare": (["Boucliers"], ["Armes courantes", "Armes de guerre"]),
    "Barde": (["Armures légères"], []),
    "Clerc": (["Armures légères", "Armures intermédiaires", "Boucliers"], []),
    "Druide": (["Armures légères", "Armures intermédiaires", "Boucliers"], []),
    "Guerrier": (["Armures légères", "Armures intermédiaires", "Boucliers"], ["Armes courantes", "Armes de guerre"]),
    "Moine": ([], ["Armes courantes", "Épées courtes"]),
    "Paladin": (["Armures légères", "Armures intermédiaires", "Boucliers"], ["Armes courantes", "Armes de guerre"]),
    "Rôdeur": (["Armures légères", "Armures intermédiaires", "Boucliers"], ["Armes courantes", "Armes de guerre"]),
    "Roublard": (["Armures légères"], []),
    "Ensorceleur": ([], []),
    "Magicien": ([], []),
    "Occultiste": (["Armures légères"], ["Armes courantes"]),
    "Artificier": (["Armures légères", "Armures intermédiaires", "Boucliers"], []),
}

# --------------------------------------------------------------------------------------
# Utilitaires de texte
# --------------------------------------------------------------------------------------


def norm(text: str) -> str:
    """Normalise un texte (minuscules, sans accents, apostrophes droites) pour les comparaisons."""
    if text is None:
        return ""
    text = text.replace("’", "'").replace("œ", "oe").replace("Œ", "oe")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.lower()).strip()


def _stem(word: str) -> str:
    return word[:-1] if len(word) > 3 and word[-1] in "sx" else word


_WEAPON_ALIASES = {"dard": "flechette", "baton": "baton de combat", "javelot": "javeline",
                   "frondes": "fronde", "sling": "fronde"}


def _words(text: str) -> set[str]:
    cleaned = re.sub(r"[()/,]", " ", norm(text))
    out = set()
    for w in cleaned.split():
        w = _WEAPON_ALIASES.get(_stem(w), _WEAPON_ALIASES.get(w, w))   # « bâtons » -> « bâton » -> « bâton de combat »
        out.update(_stem(x) for x in w.split())
    return out


# --------------------------------------------------------------------------------------
# Caractéristiques
# --------------------------------------------------------------------------------------
def ability_modifier(score: int) -> int:
    """Modificateur de caractéristique : (valeur - 10) // 2."""
    return (int(score) - 10) // 2


def proficiency_bonus(total_level: int) -> int:
    """Bonus de maîtrise selon le niveau global (2 au niveau 1, +1 tous les 4 niveaux)."""
    total_level = max(1, min(MAX_LEVEL, int(total_level)))
    return 2 + (total_level - 1) // 4


def fmt_bonus(value: int) -> str:
    """Formate un bonus avec son signe (+3 / -1 / +0)."""
    return f"{value:+d}"


# ---- Achat de points -----------------------------------------------------------------
POINT_BUY_TOTAL = 27
POINT_BUY_MIN, POINT_BUY_MAX = 8, 15
POINT_BUY_COST = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}


def point_buy_cost(score: int) -> int:
    """Coût officiel d'une valeur (8 à 15)."""
    if score not in POINT_BUY_COST:
        raise ValueError(f"Valeur hors règle d'achat de points : {score}")
    return POINT_BUY_COST[score]


def point_buy_total(scores: dict[str, int]) -> int:
    return sum(POINT_BUY_COST.get(max(POINT_BUY_MIN, min(POINT_BUY_MAX, v)), 0) for v in scores.values())


def point_buy_valid(scores: dict[str, int]) -> tuple[bool, str]:
    """Vérifie les règles officielles : valeurs 8-15 et 27 points maximum."""
    for ab, v in scores.items():
        if not POINT_BUY_MIN <= v <= POINT_BUY_MAX:
            return False, f"{ab} doit être entre {POINT_BUY_MIN} et {POINT_BUY_MAX} (achat de points)."
    total = point_buy_total(scores)
    if total > POINT_BUY_TOTAL:
        return False, f"Budget dépassé : {total}/{POINT_BUY_TOTAL} points."
    return True, f"{POINT_BUY_TOTAL - total} point(s) restant(s)."


def point_buy_remaining(scores: dict[str, int]) -> int:
    """Points restants sur les 27 du budget officiel."""
    return POINT_BUY_TOTAL - point_buy_total(scores)


def point_buy_step(scores: dict[str, int], ability: str, delta: int) -> dict[str, int]:
    """
    Monte (+1) ou baisse (-1) une valeur d'un cran. Retourne un NOUVEAU dictionnaire ; il est identique à
    l'original si le mouvement est interdit (valeur hors 8-15 ou budget de 27 points dépassé).
    """
    out = dict(scores)
    v = out[ability]
    if delta > 0 and can_raise(out, ability):
        out[ability] = v + 1
    elif delta < 0 and v > POINT_BUY_MIN:
        out[ability] = v - 1
    return out


def point_buy_normalize(scores: dict[str, int]) -> dict[str, int]:
    """
    Rend un jeu de valeurs conforme à l'achat de points (utile pour une sauvegarde ancienne ou modifiée à la main) :
    chaque valeur est ramenée dans 8-15, puis les plus hautes sont baissées d'un cran tant que le budget est dépassé.
    """
    out = {ab: max(POINT_BUY_MIN, min(POINT_BUY_MAX, int(v))) for ab, v in scores.items()}
    while point_buy_total(out) > POINT_BUY_TOTAL:
        top = max(out, key=lambda k: out[k])
        out[top] -= 1
    return out


def can_raise(scores: dict[str, int], ability: str) -> bool:
    """Peut-on augmenter cette valeur d'un cran sans dépasser 15 ni le budget ?"""
    v = scores[ability]
    if v >= POINT_BUY_MAX:
        return False
    return point_buy_total(scores) - POINT_BUY_COST[v] + POINT_BUY_COST[v + 1] <= POINT_BUY_TOTAL


# ---- Tirage 4d6 ----------------------------------------------------------------------
def roll_4d6_drop_lowest(rng: Optional[random.Random] = None) -> tuple[int, list[int]]:
    """Tire 4d6 et garde les 3 plus hauts. Retourne (total, [4 dés triés décroissants])."""
    rng = rng or random
    dice = sorted((rng.randint(1, 6) for _ in range(4)), reverse=True)
    return sum(dice[:3]), dice


def roll_ability_set(rng: Optional[random.Random] = None) -> list[tuple[int, list[int]]]:
    """Six tirages 4d6 (garde les 3 meilleurs)."""
    return [roll_4d6_drop_lowest(rng) for _ in range(6)]


# --------------------------------------------------------------------------------------
# Dés
# --------------------------------------------------------------------------------------
_DICE_TERM = re.compile(r"([+-]?)\s*(\d+)(?:d(\d+))?")


def parse_dice(expr: str) -> tuple[list[tuple[int, int]], int]:
    """Décompose '2d8+4d6+3' en ([(2,8),(4,6)], 3)."""
    dice, flat = [], 0
    for sign, a, b in _DICE_TERM.findall(expr or ""):
        s = -1 if sign == "-" else 1
        if b:
            dice.append((s * int(a), int(b)))
        else:
            flat += s * int(a)
    return dice, flat


def format_dice(dice: Iterable[tuple[int, int]], flat: int = 0) -> str:
    parts = [f"{n}d{s}" for n, s in dice]
    text = "+".join(parts).replace("+-", "-")
    if flat:
        text = f"{text}{flat:+d}" if text else str(flat)
    return text or "0"


def add_flat(expr: str, bonus: int) -> str:
    """'1d8' + 3 -> '1d8+3'."""
    dice, flat = parse_dice(expr)
    return format_dice(dice, flat + bonus)


def scale_dice(expr: str, multiplier: int) -> str:
    """Multiplie le nombre de dés (les constantes sont conservées)."""
    dice, flat = parse_dice(expr)
    return format_dice([(n * multiplier, s) for n, s in dice], flat)


def average_die(sides: int) -> int:
    """Valeur moyenne arrondie au supérieur (PV fixes) : d8 -> 5, d10 -> 6..."""
    return sides // 2 + 1


def die_sides(die: str) -> int:
    """'d10' -> 10."""
    return int(str(die).lower().replace("d", "").strip())


def add_dice(expr: str, extra: str, times: int = 1) -> str:
    """Ajoute `times` fois `extra` à `expr` en regroupant les dés de même taille : '8d6' + 2 × '1d6' -> '10d6'."""
    if times <= 0 or not extra:
        return format_dice(*parse_dice(expr)) if expr else ""
    dice, flat = parse_dice(expr)
    more, more_flat = parse_dice(extra)
    dice = list(dice)
    for n, sides in more:
        i = next((k for k, (_, s) in enumerate(dice) if s == sides), None)
        if i is None:
            dice.append((n * times, sides))
        else:
            dice[i] = (dice[i][0] + n * times, sides)
    return format_dice(dice, flat + more_flat * times)


def ordinal_level(level: int) -> str:
    return "1er" if level == 1 else "{}e".format(level)


def spell_scaling(spell: dict, slot_level: int = 0) -> dict:
    """
    Valeurs d'un sort de niveau 1+ lancé avec un emplacement de niveau `slot_level` (surclassement), d'après les
    champs audités de data/Regles_sorts.json : {niveau, degats, soins, pv_temp, projectiles, texte}.
    Le modificateur de caractéristique (« mod », « soins_mod ») est ajouté par le moteur, qui le connaît.
    """
    base = int(spell.get("niveau") or 0)
    slot = max(base, int(slot_level or 0))
    extra = slot - base
    step = max(1, int(spell.get("sup_pas") or 1))
    steps = extra // step
    dmg = spell.get("degats", "")
    table = spell.get("sup_table") or {}
    if table:
        best = max((int(k) for k in table if int(k) <= slot), default=None)
        if best is not None:
            dmg = table[str(best)] if str(best) in table else table[best]
    elif dmg and spell.get("sup"):
        dmg = add_dice(dmg, spell["sup"], steps)
    heal = spell.get("soins", "")
    if heal and spell.get("sup_soins"):
        heal = add_dice(heal, spell["sup_soins"], steps)
    temp = spell.get("pv_temp", "")
    if temp and spell.get("sup_pv_temp"):
        temp = add_dice(temp, spell["sup_pv_temp"], steps)
    proj = int(spell.get("projectiles") or 0)
    if proj:
        proj += extra * int(spell.get("sup_projectiles") or 0)
    return {"niveau": slot, "degats": dmg, "soins": heal, "pv_temp": temp, "projectiles": proj,
            "texte": spell.get("sup_texte", "")}


_FIRST_DICE = re.compile(r"\d+d\d+")
_COUNT_WORDS = r"(projectiles?|rayons?|m[ée]t[ée]ores?|sph[èe]res?|munitions?)"


def describe_at(spell: dict, slot_level: int = 0) -> tuple[str, list[str]]:
    """
    Description du sort réécrite au niveau d'emplacement choisi : les dés de base (dégâts, soins, PV temporaires) et
    le nombre de projectiles / rayons sont remplacés par leur valeur surclassée.
    Renvoie (texte, [valeurs remplacées]) — la liste sert à les mettre en évidence dans l'interface.
    « Mains brûlantes » au niveau 3 : « … infligeant 3d6 dégâts de feu … » -> « … infligeant 5d6 dégâts de feu … ».
    """
    text = spell.get("description", "") or ""
    base = int(spell.get("niveau") or 0)
    sc = spell_scaling(spell, slot_level)
    if base == 0 or sc["niveau"] <= base:
        return text, []
    changed = []
    for key in ("degats", "soins", "pv_temp"):
        old, new = spell.get(key, ""), sc[key]
        o, n = _FIRST_DICE.search(old or ""), _FIRST_DICE.search(new or "")
        if old and new and old != new and not o and str(old).strip().isdigit():   # valeur fixe (Armure d'Agathys)
            word = r"d[ée]g[âa]ts" if key == "degats" else r"(?:PV|points de vie)"
            p0 = re.compile(r"\b{}(\s+{})".format(re.escape(str(old).strip()), word))
            if p0.search(text):
                text = p0.sub(lambda m: str(new) + m.group(1), text, count=1)
                changed.append(str(new))
            continue
        if not (o and n):
            continue
        pattern = re.compile(r"(?<![\dd])" + re.escape(o.group(0)) + r"(?!\d)")
        if o.group(0) != n.group(0) and pattern.search(text):
            text = pattern.sub(n.group(0), text, count=1)
            changed.append(n.group(0))
        # dégâts fixes ajoutés (« 1d4 + 4 » de Simulacre de vie -> « 1d4 + 9 ») : constante en fin de formule
        of, nf = parse_dice(old)[1], parse_dice(new)[1]
        if of != nf and of:
            p2 = re.compile(re.escape(n.group(0)) + r"\s*\+\s*" + str(of) + r"\b")
            if p2.search(text):
                text = p2.sub("{} + {}".format(n.group(0), nf), text, count=1)
                changed.append("{} + {}".format(n.group(0), nf))
    proj = int(spell.get("projectiles") or 0)
    if proj and sc["projectiles"] != proj:
        p3 = re.compile(r"\b{}(\s+){}".format(proj, _COUNT_WORDS), re.I)
        if p3.search(text):
            text = p3.sub(lambda m: "{}{}{}".format(sc["projectiles"], m.group(1), m.group(2)), text, count=1)
            changed.append(str(sc["projectiles"]))
    return text, changed


def upcast_summary(spell: dict) -> str:
    """Règle de surclassement lisible : « +1d6 par niveau d'emplacement au-delà du 3e »."""
    base = int(spell.get("niveau") or 0)
    if base == 0:
        return ""
    step = int(spell.get("sup_pas") or 1)
    per = "par niveau d'emplacement" if step == 1 else "tous les {} niveaux d'emplacement".format(step)
    parts = []
    if spell.get("sup_table"):
        parts.append("dégâts : " + ", ".join("{} (niveau {}+)".format(v, k) for k, v in
                                               sorted(spell["sup_table"].items(), key=lambda kv: int(kv[0]))))
    elif spell.get("sup") and spell.get("degats"):
        parts.append("+{} dégâts {} au-delà du {}".format(spell["sup"], per, ordinal_level(base)))
    if spell.get("sup_soins"):
        parts.append("+{} points de vie rendus {} au-delà du {}".format(spell["sup_soins"], per, ordinal_level(base)))
    if spell.get("sup_pv_temp"):
        parts.append("+{} PV temporaires {} au-delà du {}".format(spell["sup_pv_temp"], per, ordinal_level(base)))
    if spell.get("sup_projectiles"):
        parts.append("+{} projectile(s) par niveau d'emplacement au-delà du {}".format(spell["sup_projectiles"],
                                                                                       ordinal_level(base)))
    if spell.get("sup_texte"):
        parts.append(spell["sup_texte"])
    return " ; ".join(parts)


def cantrip_multiplier(total_level: int) -> int:
    """Les sorts mineurs gagnent un dé aux niveaux 5, 11 et 17 (niveau global du personnage)."""
    return 1 + (total_level >= 5) + (total_level >= 11) + (total_level >= 17)


# --------------------------------------------------------------------------------------
# Compétences
# --------------------------------------------------------------------------------------
def skill_bonus(ability_mod: int, prof_bonus: int, proficient: bool, expertise: bool,
                half_prof: bool = False, half_prof_round_up: bool = False, misc: int = 0) -> int:
    """
    Valeur finale d'une compétence.
      - maîtrise : + bonus de maîtrise
      - expertise (uniquement si maîtrise) : bonus de maîtrise doublé
      - 'half_prof' : Touche-à-tout (arrondi inférieur) ou Athlète remarquable (arrondi supérieur)
        pour les compétences non maîtrisées
    """
    if proficient:
        return ability_mod + prof_bonus * (2 if expertise else 1) + misc
    if half_prof:
        half = math.ceil(prof_bonus / 2) if half_prof_round_up else prof_bonus // 2
        return ability_mod + half + misc
    return ability_mod + misc


# --------------------------------------------------------------------------------------
# Magie : types d'incantateurs, emplacements, sorts connus
# --------------------------------------------------------------------------------------
# kind : full / half / artificer / third / pact ; mode : known / prepared
CASTERS = {
    "Barde": dict(ability="Charisme", kind="full", mode="known", min_level=1),
    "Clerc": dict(ability="Sagesse", kind="full", mode="prepared", min_level=1),
    "Druide": dict(ability="Sagesse", kind="full", mode="prepared", min_level=1),
    "Ensorceleur": dict(ability="Charisme", kind="full", mode="known", min_level=1),
    "Magicien": dict(ability="Intelligence", kind="full", mode="prepared", min_level=1),
    "Occultiste": dict(ability="Charisme", kind="pact", mode="known", min_level=1),
    "Paladin": dict(ability="Charisme", kind="half", mode="prepared", min_level=2),
    "Rôdeur": dict(ability="Sagesse", kind="half", mode="known", min_level=2),
    "Artificier": dict(ability="Intelligence", kind="artificer", mode="prepared", min_level=1),
}
# Sous-classes lançant des sorts : (classe, sous-classe) -> description (liste de sorts du Magicien)
SUBCLASS_CASTERS = {
    ("Guerrier", "Chevalier occulte"): dict(ability="Intelligence", kind="third", mode="known",
                                            min_level=3, spell_list="Magicien"),
    ("Roublard", "Escroc arcanique"): dict(ability="Intelligence", kind="third", mode="known",
                                           min_level=3, spell_list="Magicien"),
    ("Roublard", "Arnaqueur arcanique"): dict(ability="Intelligence", kind="third", mode="known",
                                              min_level=3, spell_list="Magicien"),   # nom utilisé par Roublard.json
}

# Emplacements de sorts d'un incantateur complet selon son niveau d'incantateur (1..20)
_FULL_SLOTS = [
    [2], [3], [4, 2], [4, 3], [4, 3, 2], [4, 3, 3], [4, 3, 3, 1], [4, 3, 3, 2], [4, 3, 3, 3, 1],
    [4, 3, 3, 3, 2], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1, 1],
    [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 2, 1, 1, 1, 1], [4, 3, 3, 3, 3, 1, 1, 1, 1], [4, 3, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 2, 1, 1],
]

# Magie des pactes (Occultiste) : niveau -> (nombre d'emplacements, niveau des emplacements)
_PACT = {1: (1, 1), 2: (2, 1), 3: (2, 2), 4: (2, 2), 5: (2, 3), 6: (2, 3), 7: (2, 4), 8: (2, 4),
         9: (2, 5), 10: (2, 5), 11: (3, 5), 12: (3, 5), 13: (3, 5), 14: (3, 5), 15: (3, 5),
         16: (3, 5), 17: (4, 5), 18: (4, 5), 19: (4, 5), 20: (4, 5)}

_CANTRIPS = {  # (seuil1, seuil2, seuil3) -> (n1, n2, n3) : à partir des niveaux 1/4/10 sauf indication
    "Barde": (2, 3, 4), "Clerc": (3, 4, 5), "Druide": (2, 3, 4), "Ensorceleur": (4, 5, 6),
    "Magicien": (3, 4, 5), "Occultiste": (2, 3, 4),
}
_KNOWN = {
    "Barde": [4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 15, 16, 18, 19, 19, 20, 22, 22, 22],
    "Ensorceleur": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
    "Occultiste": [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15],
    "Rôdeur": [0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11],
    "third": [0, 0, 3, 4, 4, 4, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11, 11, 11, 12, 13],
}


def caster_index(kind: str, level: int) -> int:
    """Niveau d'incantateur équivalent pour un incantateur unique (table de classe)."""
    if kind == "full":
        return level
    if kind == "half":
        return 0 if level < 2 else math.ceil(level / 2)
    if kind == "artificer":
        return math.ceil(level / 2)
    if kind == "third":
        return 0 if level < 3 else math.ceil(level / 3)
    return 0


def multiclass_caster_level(kind: str, level: int) -> int:
    """Contribution au niveau d'incantateur en multiclassage (règle du Manuel des Joueurs / Tasha)."""
    if kind == "full":
        return level
    if kind == "half":
        return level // 2
    if kind == "artificer":
        return math.ceil(level / 2)
    if kind == "third":
        return level // 3
    return 0


def spell_slots(casters: list[tuple[str, int]]) -> list[int]:
    """
    Emplacements de sorts (hors Magie des pactes) pour une liste de (kind, niveau_de_classe)
    d'incantateurs actifs. Retourne une liste de 9 entiers (niveaux 1 à 9).
    """
    active = [(k, lv) for k, lv in casters if k != "pact" and caster_index(k, lv) > 0]
    if not active:
        return [0] * 9
    if len(active) == 1:
        idx = caster_index(*active[0])
    else:
        idx = sum(multiclass_caster_level(k, lv) for k, lv in active)
    idx = max(0, min(MAX_LEVEL, idx))
    slots = list(_FULL_SLOTS[idx - 1]) if idx else []
    return slots + [0] * (9 - len(slots))


def pact_slots(level: int) -> tuple[int, int]:
    """(nombre d'emplacements, niveau des emplacements) pour la Magie des pactes."""
    return _PACT[max(1, min(MAX_LEVEL, level))]


def cantrips_known(class_name: str, level: int, kind: str = "") -> int:
    """Nombre de sorts mineurs connus."""
    if class_name == "Artificier":
        return 2 if level < 10 else 3 if level < 14 else 4
    if kind == "third":
        return 0 if level < 3 else 2 if level < 10 else 3
    tbl = _CANTRIPS.get(class_name)
    if not tbl:
        return 0
    return tbl[0] if level < 4 else tbl[1] if level < 10 else tbl[2]


def spells_known(class_name: str, level: int, kind: str = "") -> Optional[int]:
    """Nombre de sorts connus (classes à sorts connus), ou None si non applicable."""
    key = "third" if kind == "third" else class_name
    tbl = _KNOWN.get(key)
    return tbl[max(1, min(MAX_LEVEL, level)) - 1] if tbl else None


def spells_prepared(class_name: str, level: int, ability_mod: int) -> Optional[int]:
    """Nombre de sorts préparés pour les classes à préparation, ou None sinon."""
    if class_name in ("Clerc", "Druide", "Magicien"):
        return max(1, ability_mod + level)
    if class_name in ("Paladin", "Artificier"):
        return max(1, ability_mod + level // 2)
    return None


def max_spell_level(kind: str, level: int) -> int:
    """Niveau de sort maximal accessible à une classe."""
    if kind == "pact":
        return pact_slots(level)[1]
    slots = spell_slots([(kind, level)])
    return max((i + 1 for i, n in enumerate(slots) if n), default=0)


def spell_save_dc(prof: int, ability_mod: int) -> int:
    return 8 + prof + ability_mod


def spell_attack_bonus(prof: int, ability_mod: int) -> int:
    return prof + ability_mod


# --------------------------------------------------------------------------------------
# Armes / armures
# --------------------------------------------------------------------------------------
def weapon_proficient(weapon_name: str, category: str, proficiencies: Iterable[str]) -> bool:
    """
    Le personnage maîtrise-t-il cette arme ? `proficiencies` provient des fichiers de classe :
    catégories ('Armes courantes', 'Armes de guerre') ou noms d'armes (au pluriel ou non).
    """
    w = _words(weapon_name)
    for p in proficiencies:
        pn = norm(p)
        if pn.startswith("armes courantes") and category == "courante":
            return True
        if pn.startswith("armes de guerre") and category == "guerre":
            return True
        if pn.startswith("armes courantes") or pn.startswith("armes de guerre"):
            continue
        if w and w <= _words(p):
            return True
    return False


def armor_proficient(category: str, proficiencies: Iterable[str]) -> bool:
    cat = norm(category)
    if cat in ("aucune", ""):
        return True
    for p in proficiencies:
        pn = norm(p)
        if "toutes" in pn:
            return True
        if cat.startswith("leg") and "legere" in pn:
            return True
        if cat.startswith("inter") and ("intermediaire" in pn or "moyenne" in pn):
            return True
        if cat.startswith("lourde") and "lourde" in pn:
            return True
    return False


def armor_class(base: int, dex_mod: int, dex_max: Optional[int], shield_bonus: int = 0, magic: int = 0) -> int:
    """CA avec armure : base + Dex (plafonnée si dex_max n'est pas None) + bouclier + bonus magique."""
    if dex_max is None:
        dex_part = dex_mod
    else:
        dex_part = min(dex_mod, dex_max)
    return base + dex_part + shield_bonus + magic


def martial_arts_die(monk_level: int) -> int:
    """Dé d'arts martiaux du moine (d4 -> d10)."""
    return 4 if monk_level < 5 else 6 if monk_level < 11 else 8 if monk_level < 17 else 10


# --------------------------------------------------------------------------------------
# Ressources de classe (affichage informatif)
# --------------------------------------------------------------------------------------
def invocations_known(level: int) -> int:
    """Nombre de manifestations (invocations) occultes connues de l'Occultiste selon son niveau."""
    table = [(18, 8), (15, 7), (12, 6), (9, 5), (7, 4), (5, 3), (2, 2)]
    return next((n for lv, n in table if level >= lv), 0)


# Caractéristique d'incantation des sorts raciaux quand le texte de la race ne la précise pas
# (règles du Manuel des Joueurs / Mordenkainen). Absente de la table : Int, Sag ou Cha au choix du joueur.
RACE_SPELL_ABILITY = {
    "Tieffelin": "Charisme", "Tieffelin féral": "Charisme", "Aasimar protecteur": "Charisme",
    "Aasimar déchu": "Charisme", "Gnome des forêts": "Intelligence", "Githyanki": "Intelligence",
    "Githzerai": "Sagesse", "Firbolg": "Sagesse", "Yuan-ti": "Charisme", "Duergar": "Intelligence",
    "Triton": "Charisme", "Kitsune": "Charisme", "Drow (Elfe noir)": "Charisme",
}

# Encombrement (Manuel des Joueurs) : capacité = Force × 7,5 kg ; règle optionnelle : encombré au-delà de
# Force × 2,5 kg (vitesse -3 m), lourdement encombré au-delà de Force × 5 kg (vitesse -6 m, désavantages).
KG_CAPACITY, KG_ENCUMBERED, KG_HEAVY = 7.5, 2.5, 5.0


def parse_cr(text: str) -> float:
    """Facteur de puissance « 1/4 (50 PX) » -> 0.25 ; « 2 (450 PX) » -> 2.0."""
    m = re.match(r"\s*(\d+)(?:/(\d+))?", text or "")
    if not m:
        return 0.0
    return int(m.group(1)) / int(m.group(2)) if m.group(2) else float(m.group(1))


def fmt_cr(value: float) -> str:
    """0.25 -> « 1/4 », 2.0 -> « 2 »."""
    for frac, label in ((0.125, "1/8"), (0.25, "1/4"), (0.5, "1/2")):
        if abs(value - frac) < 1e-9:
            return label
    return str(int(value)) if value == int(value) else str(value)


def wild_shape_limits(druid_level: int, moon: bool) -> dict:
    """
    Forme sauvage (Manuel des Joueurs) : FP maximal et déplacements autorisés selon le niveau de druide.
      druide classique : niv. 2 FP 1/4 (ni vol ni nage), niv. 4 FP 1/2 (pas de vol), niv. 8 FP 1.
      Cercle de la Lune (Formes de combat) : FP 1 dès le niv. 2, puis FP = niveau / 3 (arrondi inférieur) dès le niv. 6.
    Durée : moitié du niveau de druide en heures (arrondi inférieur). Utilisations : 2 par repos court (illimitées
    au niveau 20, Archidruide).
    """
    if druid_level < 2:
        return {"actif": False, "fp_max": 0.0, "nage": False, "vol": False, "duree": 0, "utilisations": 0}
    if moon:
        fp_max = 1.0 if druid_level < 6 else float(druid_level // 3)
    else:
        fp_max = 0.25 if druid_level < 4 else 0.5 if druid_level < 8 else 1.0
    return {"actif": True, "fp_max": fp_max, "nage": druid_level >= 4, "vol": druid_level >= 8,
            "duree": druid_level // 2, "utilisations": None if druid_level >= 20 else 2}


def rage_damage(level: int) -> int:
    """Bonus de dégâts de rage (PHB) : +2, +3 au niveau 9, +4 au niveau 16 (0 sans niveau de barbare)."""
    return 0 if level <= 0 else 2 if level < 9 else 3 if level < 16 else 4


def rage_uses(level: int):
    """Rages par repos long (None = illimitées au niveau 20)."""
    if level >= 20:
        return None
    return 2 if level < 3 else 3 if level < 6 else 4 if level < 12 else 5 if level < 17 else 6


def ki_points(level: int) -> int:
    """Points de ki du moine : égaux à son niveau (à partir du niveau 2)."""
    return level if level >= 2 else 0


def orb_click(total: int, used: int, index: int) -> int:
    """
    Règle de clic d'un compteur à sphères (rage, ki, emplacements...). Les sphères pleines sont toujours
    regroupées à gauche : cliquer une sphère PLEINE en dépense une, cliquer une sphère VIDE en récupère une.
    Retourne le nouveau nombre de ressources dépensées (toujours entre 0 et `total`).
    """
    available = total - used
    if not 0 <= index < total:
        return max(0, min(total, used))
    used = used + 1 if index < available else used - 1
    return max(0, min(total, used))


def is_asi_feature(name: str) -> bool:
    """« Amélioration de caractéristique(s) » (avec ou sans « ou choix d'un don ») — pas « Amélioration des auras »."""
    return bool(re.match(r"amelioration de caracteristique", norm(name)))


def lazy_slot_count(filled: list[bool], maximum: int = 4) -> int:
    """
    Nombre d'emplacements visibles pour une liste « à affichage progressif » : un seul au départ, puis un
    nouvel emplacement vide apparaît dès que le dernier visible est rempli (jusqu'à `maximum`).
    """
    last = max((i for i, f in enumerate(filled) if f), default=-1)
    return max(1, min(maximum, last + 2))


def class_resources(name: str, level: int, mods: dict[str, int], prof: int) -> list[tuple[str, str]]:
    """Petites ressources numériques propres à chaque classe (informatives)."""
    m = mods
    out: list[tuple[str, str]] = []
    if name == "Barbare":
        uses = "Illimitée" if level >= 20 else str(2 if level < 3 else 3 if level < 6 else 4 if level < 12
                                                   else 5 if level < 17 else 6)
        out += [("Rages / repos long", uses), ("Dégâts de rage", f"+{2 if level < 9 else 3 if level < 16 else 4}")]
    elif name == "Barde":
        die = 6 if level < 5 else 8 if level < 10 else 10 if level < 15 else 12
        out += [("Inspiration bardique", f"d{die} × {max(1, m['Charisme'])}/repos {'court' if level >= 5 else 'long'}")]
    elif name == "Clerc":
        if level >= 2:
            out.append(("Conduit divin / repos", str(1 if level < 6 else 2 if level < 18 else 3)))
    elif name == "Druide":
        if level >= 2:
            out.append(("Forme sauvage / repos court", "Illimitée" if level >= 20 else "2"))
    elif name == "Guerrier":
        out += [("Second souffle", f"1d10+{level}"), ("Sursaut d'activité", "2" if level >= 17 else "1" if level >= 2 else "—"),
                ("Attaques par action", str(4 if level >= 20 else 3 if level >= 11 else 2 if level >= 5 else 1))]
        ind = 3 if level >= 17 else 2 if level >= 13 else 1 if level >= 9 else 0
        if ind:
            out.append(("Indomptable / repos long", str(ind)))
    elif name == "Moine":
        out.append(("Dé d'arts martiaux", f"d{martial_arts_die(level)}"))
        if level >= 2:
            out += [("Points de ki", str(level)), ("DD de ki", str(8 + prof + m["Sagesse"]))]
    elif name == "Paladin":
        out.append(("Imposition des mains (réserve)", str(5 * level)))
        out.append(("Sens divin / repos long", str(1 + max(0, m["Charisme"]))))
        if level >= 3:
            out.append(("Conduit divin / repos", "1"))
    elif name == "Rôdeur":
        if level >= 5:
            out.append(("Attaques par action", "2"))
    elif name == "Roublard":
        out.append(("Attaque sournoise", f"{math.ceil(level / 2)}d6"))
    elif name == "Ensorceleur":
        if level >= 2:
            out.append(("Points de sorcellerie", str(level)))
    elif name == "Magicien":
        out.append(("Restauration arcanique", f"{math.ceil(level / 2)} niv. d'emplacements (max 5)"))
    elif name == "Occultiste":
        if level >= 2:
            out.append(("Manifestations occultes", str(invocations_known(level))))
    elif name == "Artificier":
        if level >= 2:
            inf = 4 if level < 6 else 6 if level < 10 else 8 if level < 14 else 10 if level < 18 else 12
            out.append(("Infusions connues", str(inf)))
    return out


# --------------------------------------------------------------------------------------
# Vitesse, poids, extraction des mécaniques d'un sort depuis son texte
# --------------------------------------------------------------------------------------
CELL_METERS = 1.5   # D&D 5e : 1 case = 1,50 m (5 pieds)


def fmt_meters(value: float) -> str:
    """9.0 -> '9' ; 7.5 -> '7,5' (notation française)."""
    text = f"{value:.1f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def meters_to_cells(meters: float) -> int:
    return int(round(meters / CELL_METERS))


def fmt_speed(meters: float) -> str:
    """Affiche une distance en mètres ET en cases : '9 m (6 cases)'."""
    cells = meters_to_cells(meters)
    return f"{fmt_meters(meters)} m ({cells} case{'s' if cells > 1 else ''})"


_WEIGHT = re.compile(r"([\d\s]*\d(?:[.,]\d+)?)\s*(kg|g)\b")


def parse_weight(text: str) -> float:
    """'2,5 kg' -> 2.5 ; '250 g' -> 0.25 ; '—' / 'Variable' -> 0.0 (en kilogrammes)."""
    m = _WEIGHT.search((text or "").lower().replace("\u202f", " "))
    if not m:
        return 0.0
    value = float(m.group(1).replace(" ", "").replace(",", "."))
    return value / 1000 if m.group(2) == "g" else value


_DMG_TYPE = {"acide": "acide", "feu": "feu", "froid": "froid", "foudre": "foudre", "tonnerre": "tonnerre",
             "poison": "poison", "necro": "nécrotique", "radiant": "radiant", "force": "force",
             "psychique": "psychique", "contondant": "contondant", "perforant": "perforant",
             "tranchant": "tranchant"}
_TYPE_RE = (r"(?:degats?\s+(?:d'|de\s+|du\s+)?|\bde\s+)"
            r"(acide|feu|froid|foudre|tonnerre|poison|necro\w*|radiant\w*|force|psychique\w*|contondant\w*|"
            r"perforant\w*|tranchant\w*)")


def parse_spell_mechanics(description: str) -> dict:
    """
    Déduit d'une description de sort : dégâts (dés), type, jet associé ('A' attaque à distance,
    'AC' corps à corps, 'Dex'/'Con'... jet de sauvegarde, 'Arme' attaque d'arme) et nombre de rayons.
    Les fichiers Magie-N.json ne contiennent pas ces champs ; ils sont extraits du texte.
    """
    n = norm(description)
    out = {"degats": "", "type_degats": "", "test": "", "rayons": False}
    for m in re.finditer(r"(\d+d\d+)", n):
        window = n[m.end():m.end() + 60]
        t = re.search(_TYPE_RE, window)
        between = window[:t.start()] if t else ""
        if t and (not re.search(r"\d+d\d+", between) or " ou " in between):
            key = next(k for k in _DMG_TYPE if t.group(1).startswith(k))
            out["degats"], out["type_degats"] = m.group(1), _DMG_TYPE[key]
            break
    if "attaque" in n and ("avec un sort" in n or "de sort" in n):
        out["test"] = "AC" if "corps a corps" in n else "A"
    elif "attaque avec une arme" in n:
        out["test"] = "Arme"
    else:
        s = re.search(r"jds\s+(?:de\s+|d')?(for|dex|con|int|sag|cha)", n)
        if s:
            out["test"] = s.group(1).capitalize()
    out["rayons"] = "rayons/niv" in n
    return out


def mod_label(ability: str) -> str:
    """« Modificateur de Force », « Modificateur d'Intelligence » (élision devant voyelle)."""
    return "Modificateur d'" + ability if norm(ability)[:1] in "aeiouy" else "Modificateur de " + ability
