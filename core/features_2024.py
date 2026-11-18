"""
Aptitudes 2024 au mécanisme nouveau (v52) — logique pure, mélangée à Engine (fiches 2024 seulement).

- **Sorcellerie innée** (Ensorceleur 1) : action bonus, 1 minute ; DD des sorts d'ensorceleur +1 et avantage aux
  attaques de sorts d'ensorceleur ; 2 utilisations par repos long ; dès le niveau 7 (Sorcellerie incarnée), on peut
  l'activer en dépensant 2 points de sorcellerie.
- **Ordre divin** (Clerc 1) : Protecteur (armes de guerre, armures lourdes) ou Thaumaturge (un tour de magie de plus,
  modificateur de Sagesse — minimum +1 — aux tests d'Arcanes et de Religion).
- **Ordre primitif** (Druide 1) : Gardien (armes de guerre, armures intermédiaires) ou Magicien (un tour de magie de
  plus, modificateur de Sagesse — minimum +1 — aux tests d'Arcanes et de Nature).
"""
from __future__ import annotations

from .rules import norm as _norm_early

INNATE = "sorcellerie_innee"

# classe -> (clé de l'ensemble de choix, libellé, {option: (description, armures, armes, compétences)})
ORDERS_2024 = {
    "Clerc": ("ordre_divin", "Ordre divin (Clerc 2024)", {
        "Protecteur": ("Formé au combat : maîtrise des armes de guerre et des armures lourdes.",
                       ["Armures lourdes"], ["Armes de guerre"], ()),
        "Thaumaturge": ("Un tour de magie de clerc supplémentaire ; bonus égal au modificateur de Sagesse (minimum "
                        "+1) aux tests d'Intelligence (Arcanes ou Religion).", [], [], ("Arcanes", "Religion"))}),
    "Druide": ("ordre_primitif", "Ordre primitif (Druide 2024)", {
        "Gardien": ("Formé au combat : maîtrise des armes de guerre et des armures intermédiaires.",
                    ["Armures intermédiaires"], ["Armes de guerre"], ()),
        "Magicien": ("Un tour de magie de druide supplémentaire ; bonus égal au modificateur de Sagesse (minimum "
                     "+1) aux tests d'Intelligence (Arcanes ou Nature).", [], [], ("Arcanes", "Nature"))}),
}


# sous-classe 2024 -> sous-classe 2014 équivalente (noms normalisés) : les mécanismes 2014 (tuiles, compteurs,
# dés psioniques, incantation…) reconnaissent ainsi les sous-classes 2024 renommées
SUBCLASS_EQUIV_2024 = {
    "ame aceree": "lame psychique", "escroc arcanique": "arnaqueur arcanique",
    "abjurateur": "ecole d'abjuration", "devin": "ecole de divination", "evocateur": "ecole d'evocation",
    "illusionniste": "ecole d'illusion", "domaine de la duperie": "domaine de la ruse",
    "credo de l'ombre": "voie de l'ombre", "credo de la paume": "voie de la paume",
    "credo de la misericorde": "voie de la misericorde", "credo des elements": "voie des quatre elements",
    "vagabond feerique": "vagabond feerique",
}


def sub_norm_of(entry: dict) -> str:
    n = _norm_early((entry or {}).get("sous_classe", ""))
    return SUBCLASS_EQUIV_2024.get(n, n)


class Features2024Mixin:
    """Mélangé à Engine : utilise sheet_edition, class_level, mod, ch."""

    # ------------------------------------------------------------------ Ordre divin / Ordre primitif
    def order_option_sets(self) -> list[dict]:
        if getattr(self, "sheet_edition", 2014) != 2024:
            return []
        out = []
        for cls, (key, label, options) in ORDERS_2024.items():
            if self.class_level(cls) >= 1:
                out.append({"key": key, "label": label, "total": 1,
                            "options": {n: v[0] for n, v in options.items()},
                            "chosen": list((self.ch.options_classe or {}).get(key, []))[:1]})
        return out

    def chosen_order(self, cls: str) -> str:
        if getattr(self, "sheet_edition", 2014) != 2024 or cls not in ORDERS_2024 or self.class_level(cls) < 1:
            return ""
        key, _, options = ORDERS_2024[cls]
        picked = [n for n in (self.ch.options_classe or {}).get(key, []) if n in options]
        return picked[0] if picked else ""

    def order_proficiency_sources(self) -> list[dict]:
        out = []
        for cls, (_, label, options) in ORDERS_2024.items():
            name = self.chosen_order(cls)
            if name and (options[name][1] or options[name][2]):
                out.append({"source": "{} : {}".format(label.split(" (")[0], name), "classe": cls,
                            "armures": list(options[name][1]), "armes": list(options[name][2]), "mode": "sous_classe"})
        return out

    def order_modifiers(self) -> list[tuple[str, dict]]:
        out = []
        for cls, (_, label, options) in ORDERS_2024.items():
            name = self.chosen_order(cls)
            if name and options[name][3]:
                out.append(("{} : {}".format(label.split(" (")[0], name),       # Sagesse, minimum +1
                            {"competences": {skill: ["mod:Sagesse"] for skill in options[name][3]}}))
        return out

    def order_extra_cantrips(self, cls: str) -> int:
        name = self.chosen_order(cls)
        return 1 if name and ORDERS_2024[cls][2][name][3] else 0

    # ------------------------------------------------------------------ Sorcellerie innée
    def innate_sorcery_active(self) -> bool:
        return getattr(self, "sheet_edition", 2014) == 2024 and INNATE in (self.ch.effets_actifs or [])


# ---------------------------------------------------------------------- prérequis des dons 2024
import re as _re

from .rules import ABILITIES as _ABILITIES, armor_proficient as _armor_ok, norm as _norm

_PREREQ_2024 = _re.compile(r"\d+\+|style de combat")


def is_prereq_2024(text: str) -> bool:
    """Formulation 2024 : « Niveau 4+, Force ou Dextérité 13+ », « Aptitude Style de combat »…"""
    return bool(_PREREQ_2024.search(_norm(text or "")))


class FeatPrereq2024Mixin:
    """Mélangé à Engine : évalue les prérequis des dons 2024 (niveau, caractéristiques, formations, aptitudes)."""

    def feat_status_2024(self, text: str) -> tuple[str, str]:
        parts = [p.strip() for p in _re.split(r"[,;]", _norm(text)) if p.strip()]
        unknown = False
        for p in parts:
            m = _re.fullmatch(r"niveau (\d+)\+", p)
            if m:
                if self.total_level < int(m.group(1)):
                    return "ko", text
                continue
            m = _re.search(r"(\d+)\+$", p)
            abs_ = [ab for ab in _ABILITIES if _norm(ab) in p]
            if m and abs_:
                if not any(self.score(ab) >= int(m.group(1)) for ab in abs_):
                    return "ko", text
                continue
            if "style de combat" in p:
                if not self.fighting_style_slots():
                    return "ko", text
                continue
            if "incantation" in p or "pacte" in p:
                if not (self.casters() or self.pact()[0]):
                    return "ko", text
                continue
            if "bouclier" in p:
                if not any("bouclier" in _norm(a) for a in self.armor_proficiencies()):
                    return "ko", text
                continue
            cat = next((c for c, w in (("légère", "legere"), ("intermédiaire", "intermediaire"), ("lourde", "lourde"))
                        if w in p), "")
            if cat:
                if not _armor_ok(cat, self.armor_proficiencies()):
                    return "ko", text
                continue
            unknown = True
        return ("?", text) if unknown else ("ok", "")


# ---------------------------------------------------------------------- sorts de sous-classe 2024
SUBCLASS_TIERS_2024 = {"Clerc": [3, 5, 7, 9], "Druide": [3, 5, 7, 9], "Ensorceleur": [3, 5, 7, 9],
                       "Occultiste": [3, 5, 7, 9], "Paladin": [3, 5, 9, 13, 17], "Rôdeur": [3, 5, 9, 13, 17]}
_SPELL_INDEX: dict = {}
# noms des sorts dans les textes 2024 -> nom de la bibliothèque (traductions différentes)
SPELL_ALIASES_2024 = {
    "foulee arboricole": "Passage par les arbres", "deplacement par les arbres": "Passage par les arbres",
    "fontaine de clair de lune": "Fontaine de lune", "rafale de vent": "Bourrasque",
    "conjuration d'elementaire": "Invocation d'élémentaire", "bras d'hadar": "Tentacules de Hadar",
    "famine d'hadar": "Voracité de Hadar", "message a distance": "Communication à distance",
    "protection contre l'energie": "Protection contre une énergie",
    "convocation de creature artificielle": "Convocation d'artificiel",
    "changement d'apparence": "Modification d'apparence", "terreur": "Peur",
    "connaissance des legendes": "Mythes et légendes", "eclair guide": "Éclair traçant",
    "trait guideur": "Éclair traçant", "revigoration": "Retour à la vie", "contrainte": "Compulsion",
    "croissance des plantes": "Croissance végétale",
}


def _spell_names(db) -> list[tuple[str, str]]:
    """[(nom normalisé sans « (2024) », nom de base)] triés du plus long au plus court."""
    key = id(db)
    if key not in _SPELL_INDEX:
        names = {}
        for n in db.spells:
            base = _re.sub(r"\s*\(2024\)$", "", n)
            names[_norm(base).replace("’", "'")] = base
        names.update({k: v for k, v in SPELL_ALIASES_2024.items() if v in db.spells})
        _SPELL_INDEX[key] = sorted(names.items(), key=lambda kv: -len(kv[0]))
    return _SPELL_INDEX[key]


def _read_spells(chunk: str, index, db=None) -> list[str]:
    """Sorts d'une case de table : séparés par des virgules ; le dernier peut être suivi d'un autre texte."""
    out = []
    pieces = [p for p in _re.split(r"[,;]", chunk) if p.strip()]
    for k, piece in enumerate(pieces):
        text = _norm(piece).replace("’", "'").strip(" ./|:\n\t")
        hit = next((base for n, base in index if text == n), None)
        if hit is None:                                   # nom suivi d'autre chose (« Double illusoire Vous… »)
            hit = next((base for n, base in index if text.startswith(n) and len(n) >= 4 and
                        (len(text) == len(n) or not text[len(n)].isalnum())), None)
        if hit is None:
            if k == 0 or len(text.split()) > 6:
                break
            continue                                      # sort absent de la bibliothèque : ignoré
        out.append(hit)
    return out


def parse_tier_spells(text: str, tiers: list[int], index, db=None) -> list[tuple[int, list[str]]]:
    """Table « niveau de classe → sorts » d'une aptitude 2024, quel que soit son format."""
    marks = [(m.start(), m.end(), int(m.group(1))) for m in _re.finditer(r"(?<![\w-])(\d{1,2})\s*[:|]?\s+", text)]
    out, want = [], 0
    for i, (s, e, n) in enumerate(marks):
        if want >= len(tiers) or n != tiers[want]:
            continue
        nxt = next((m[0] for m in marks[i + 1:] if want + 1 < len(tiers) and m[2] == tiers[want + 1]), len(text))
        spells = _read_spells(text[e:nxt], index, db)
        if spells:
            out.append((n, spells))
            want += 1
    return out


def subclass_spells_2024(db, cls: str, sub: dict) -> dict[str, list[tuple[int, list[str]]]]:
    """{terrain ou "": [(niveau, [sorts])]} des sorts toujours préparés d'une sous-classe 2024."""
    tiers = SUBCLASS_TIERS_2024.get(cls)
    if not tiers or not sub:
        return {}
    index = _spell_names(db)
    for f in sub.get("capacites", []):
        if not _norm(f.get("nom", "")).startswith("sorts") or "psychiques" in _norm(f["nom"]):
            continue
        text = f.get("description", "")
        parts = _re.split(r"\n\s*TERRE ([A-ZÉÈÀÂÎÔÛ]+)\s*\n", text)
        if len(parts) > 1:                                  # Cercle de la Terre : une table par type de terre
            return {parts[i].capitalize(): parse_tier_spells(parts[i + 1], tiers, index, db)
                    for i in range(1, len(parts) - 1, 2)}
        table = parse_tier_spells(text, tiers, index, db)
        if table:
            return {"": table}
    return {}
