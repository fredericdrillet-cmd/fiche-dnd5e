"""
Jets de d20 (tests de caractéristique, compétences, jets de sauvegarde, attaques d'arme et de sort) — logique pure.

Un jet est décrit par un RollSpec : titre, liste de termes (« +3 (Modificateur de Force) », « +1d4 (Bénédiction) »)
et mode (normal / avantage / désavantage / échec automatique) avec ses sources. `roll_d20()` effectue le tirage ;
l'interface (ui/dice_dialog.py) se charge de l'animation et de l'application séquentielle des bonus.

Règles 5e appliquées : avantage = 2d20 on garde le plus haut, désavantage = le plus bas, les deux s'annulent ;
le code couleur critique (20 naturel vert, 1 naturel rouge) porte uniquement sur le résultat brut du d20.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field


@dataclass
class Term:
    label: str              # « Modificateur de Force », « Bénédiction »...
    value: int = 0          # bonus fixe
    dice: str = ""          # dé ajouté : « +1d4 » / « -1d4 »

    def text(self) -> str:
        if self.dice:
            return "{} ({})".format(self.dice, self.label)
        return "{:+d} ({})".format(self.value, self.label)


@dataclass
class RollSpec:
    title: str
    kind: str = "test"                                   # test | competence | sauvegarde | attaque | sort
    terms: list[Term] = field(default_factory=list)
    mode: str = ""                                       # "" | avantage | désavantage | échec
    avantage: list[str] = field(default_factory=list)    # sources
    desavantage: list[str] = field(default_factory=list)
    echec: list[str] = field(default_factory=list)
    note: str = ""                                       # ex. « Dégâts en cas de réussite : 1d8+3 tranchants »

    @property
    def flat(self) -> int:
        return sum(t.value for t in self.terms if not t.dice)

    def mode_lines(self) -> list[str]:
        out = []
        if self.avantage:
            out.append("Avantage — " + ", ".join(self.avantage))
        if self.desavantage:
            out.append("Désavantage — " + ", ".join(self.desavantage))
        if self.avantage and self.desavantage:
            out.append("Avantage et désavantage s'annulent : un seul d20.")
        if self.echec:
            out.append("Échec automatique — " + ", ".join(self.echec))
        return out


@dataclass
class RollResult:
    d20s: list[int]                  # 1 ou 2 dés lancés
    natural: int                     # dé retenu (résultat brut)
    term_values: list[int]           # valeur de chaque terme (dés de bonus lancés)
    total: int
    critical: str                    # "succes" (20 naturel) | "echec" (1 naturel) | ""
    auto_fail: bool = False


def roll_die_expr(expr: str, rng) -> int:
    """« +1d4 » -> +x ; « -1d6 » -> -x ; « 2d8 » -> somme."""
    m = re.fullmatch(r"([+-]?)(\d*)d(\d+)", expr.replace(" ", ""))
    if not m:
        return 0
    sign = -1 if m.group(1) == "-" else 1
    n = int(m.group(2) or 1)
    return sign * sum(rng.randint(1, int(m.group(3))) for _ in range(n))


def roll_d20(spec: RollSpec, rng=None) -> RollResult:
    rng = rng or random
    mode = spec.mode
    count = 2 if mode in ("avantage", "désavantage") else 1
    d20s = [rng.randint(1, 20) for _ in range(count)]
    natural = max(d20s) if mode == "avantage" else min(d20s) if mode == "désavantage" else d20s[0]
    values = [roll_die_expr(t.dice, rng) if t.dice else t.value for t in spec.terms]
    total = natural + sum(values)
    crit = "succes" if natural == 20 else "echec" if natural == 1 else ""
    return RollResult(d20s, natural, values, total, crit, auto_fail=mode == "échec")


def mode_of(avantage: list, desavantage: list, echec: list) -> str:
    if echec:
        return "échec"
    if avantage and desavantage:
        return ""
    return "avantage" if avantage else "désavantage" if desavantage else ""


def spec_from_detail(title: str, kind: str, detail: list, avantage=(), desavantage=(), echec=(),
                     note: str = "") -> RollSpec:
    """Construit un RollSpec à partir d'un détail de calcul [(source, « +3 » | « +1d4 »)] du moteur."""
    terms = []
    for label, val in detail:
        val = str(val).replace(" ", "")
        if re.fullmatch(r"[+-]?\d*d\d+", val):
            terms.append(Term(label, 0, val if val[0] in "+-" else "+" + val))
        else:
            try:
                n = int(val)
            except ValueError:
                continue
            if n or label.startswith("Modificateur"):       # le modificateur est affiché même à +0
                terms.append(Term(label, n))
    return RollSpec(title, kind, terms, mode_of(list(avantage), list(desavantage), list(echec)),
                    list(avantage), list(desavantage), list(echec), note)


# ================================================================================================ jets de dégâts
DIE_SIDES = (4, 6, 8, 10, 12, 20, 100)
_DMG_TOKEN = re.compile(r"([+-]?)(\d*)[dD](\d+)|([+-]?)(\d+)")


@dataclass
class DamageSpec:
    """Jet de dégâts (ou de soins / dé de ressource) : « 2d6+3 », type, détail des bonus fixes."""
    title: str
    formula: str
    damage_type: str = ""
    note: str = ""
    kind: str = "degats"                      # degats | soins | de (dé de supériorité, d'inspiration...)
    flat_labels: list[tuple[str, int]] = field(default_factory=list)   # provenance du bonus fixe (affichage)
    options: list[tuple[str, str]] = field(default_factory=list)       # v39 : bonus conditionnels (source, dés)
    calcul: str = ""                          # v46 : détail lisible « 1d8 - 1 (Mod. FOR) + 3 (…) = 1d8 + 2 »


def flat_breakdown(labels: list, total: int) -> str:
    """v46 : « -1 (Mod. FOR) + 3 (Objet magique : Épée longue +3) = +2 » (bonus fixe expliqué)."""
    shown = [(lab, v) for lab, v in labels if v]
    if not shown:
        return "{:+d}".format(total)
    first, rest = shown[0], shown[1:]
    txt = "{:+d} ({})".format(first[1], first[0]) + "".join(
        " {} {} ({})".format("-" if v < 0 else "+", abs(v), lab) for lab, v in rest)
    return txt if len(shown) == 1 and shown[0][1] == total else "{} = {:+d}".format(txt, total)


@dataclass
class DamageResult:
    dice: list[tuple[int, int, int]]          # (faces, valeur, signe)
    flat: int
    total: int

    @property
    def dice_sum(self) -> int:
        return sum(sign * v for _, v, sign in self.dice)


def parse_damage(formula: str) -> tuple[list[tuple[int, int, int]], int]:
    """« 2d6 + 1d4 - 1 » -> ([(signe, nombre, faces)...], bonus fixe). Le texte non chiffré est ignoré.
    Multiplicateur en tête (rayons, projectiles) : « 3 × 1d10+3 » ou « 5 × (1d4+1) +2 » -> 3d10+9, 5d4+7."""
    text = (formula or "").replace(" ", "").replace("−", "-")
    mult = (re.match(r"^(\d+)[×x\*]\(([^()]*)\)((?:[+-]\d+)?)$", text) or
            re.match(r"^(\d+)[×x\*]([^()]*)()$", text))
    if mult and "d" in mult.group(2):
        n = int(mult.group(1))
        inner, inner_flat = parse_damage(mult.group(2))
        extra = int(mult.group(3) or 0)
        return [(sg, k * n, f) for sg, k, f in inner], inner_flat * n + extra
    groups, flat = [], 0
    for m in _DMG_TOKEN.finditer(text):
        if m.group(3):
            sign = -1 if m.group(1) == "-" else 1
            groups.append((sign, int(m.group(2) or 1), int(m.group(3))))
        else:
            # un nombre isolé collé à une lettre (« 36m », « niv5 ») n'est pas un bonus de dégâts
            end = m.end()
            if end < len(text) and text[end].isalpha() and text[end].lower() != "d":
                continue
            flat += (-1 if m.group(4) == "-" else 1) * int(m.group(5))
    return groups, flat


def critical_formula(formula: str) -> str:
    """Coup critique : nombre de dés doublé, bonus fixe inchangé (« 1d8+3 » -> « 2d8+3 »)."""
    return re.sub(r"(\d*)d(\d+)", lambda m: "{}d{}".format(2 * int(m.group(1) or 1), m.group(2)), formula or "")


def has_dice(formula: str) -> bool:
    return bool(parse_damage(formula)[0])


def roll_damage(spec: DamageSpec, rng=None) -> DamageResult:
    rng = rng or random
    groups, flat = parse_damage(spec.formula)
    dice = []
    for sign, count, sides in groups:
        for _ in range(count):
            dice.append((sides, rng.randint(1, sides), sign))
    total = sum(sign * v for _, v, sign in dice) + flat
    return DamageResult(dice, flat, max(0, total) if spec.kind != "de" else total)
