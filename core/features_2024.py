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
