"""
Actions et capacités actives de race (encart « Actions, capacités de classe et de race » de l'onglet Combat).

Les traits de l'espèce (et de la sous-espèce) sont lus dans les données de race : un trait est une action de race
s'il se déclenche par une action, une action bonus ou une réaction, ou s'il a un nombre d'utilisations limité
(« une fois par repos long », « un nombre de fois égal à votre bonus de maîtrise par repos long »…). Les traits de
sorts innés (gérés dans l'onglet Magie) et les traits de repos (Transe…) sont exclus.

Chaque action produite a le même format qu'une action de classe (core/class_actions.py) : elle est affichée,
verrouillée et dépensée par le même code. Les compteurs sont des ressources « race:<espèce>:<trait> » : ils
disparaissent d'eux-mêmes au changement d'espèce (normalize retire les ressources inconnues) et se rechargent au
repos indiqué par le trait.
"""
from __future__ import annotations

import re
from typing import Optional

from .rules import norm

_ACTIVE = re.compile(r"par une action|action bonus|votre reaction|fois par repos|nombre de fois egal|"
                     r"revient apres un repos|utilisable \d+ fois")
_SKIP_NAMES = re.compile(r"^(transe|trance|sans sommeil|repos de sentinelle|nature |amphibie|savoir astral|"
                         r"changement de saison|guerison|taille|langues?|vision|amelioration)")
_ABILITY = {"force": "Force", "dexterite": "Dextérité", "constitution": "Constitution",
            "intelligence": "Intelligence", "sagesse": "Sagesse", "charisme": "Charisme"}
_DAMAGE_TYPES = ("acide", "contondants", "feu", "force", "foudre", "froid", "necrotiques", "percants", "perforants",
                 "poison", "psychiques", "radiants", "tonnerre", "tranchants")
_DMG_TYPE_FR = {"necrotiques": "nécrotiques", "percants": "perçants"}
_ICONS = {"Action": "✋", "Action bonus": "⚡", "Réaction": "🛡", "Spécial": "✦"}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", norm(text)).strip("-")


def is_spell_trait(description: str) -> bool:
    """Sorts innés (« Sorts : *Thaumaturgie*… ») : gérés dans l'onglet Magie, pas dans les actions."""
    d = norm(description)
    return bool(re.search(r"\*[^*]+\*", description)) and ("sort" in d or "tour de magie" in d)


def is_race_action(name: str, description: str) -> bool:
    n, d = norm(name), norm(description)
    if _SKIP_NAMES.match(n) or is_spell_trait(description):
        return False
    return bool(_ACTIVE.search(d))


def action_type(description: str) -> str:
    d = norm(description)
    found = []                                           # le premier déclencheur cité l'emporte
    for kind, rx in (("Réaction", r"votre reaction"), ("Action bonus", r"(par|comme) une action bonus"),
                     ("Action", r"par une action(?! bonus)")):
        m = re.search(rx, d)
        if m:
            found.append((m.start(), kind))
    return min(found)[1] if found else "Spécial"


def uses_of(description: str, prof: int) -> Optional[int]:
    """Nombre d'utilisations entre deux repos (None = à volonté)."""
    d = norm(description)
    if "nombre de fois egal a votre bonus de maitrise" in d:
        return prof
    m = re.search(r"(\d+|une|deux|trois) fois par repos", d) or re.search(r"utilisable (\d+) fois", d)
    if m:
        return {"une": 1, "deux": 2, "trois": 3}.get(m.group(1)) or int(m.group(1))
    if "revient apres un repos" in d:
        return 1
    return None


def recovery_of(description: str) -> str:
    d = norm(description)
    return "repos court" if "repos court" in d else "repos long"


def min_level(description: str) -> int:
    m = re.search(r"(?:a partir du niveau|^niveau) (\d+)", norm(description))
    return int(m.group(1)) if m else 1


class RaceActionsMixin:
    """Mélangé à Engine : utilise ch, db, prof, mod, total_level, race_capacities, breath_weapon."""

    def _race_trait_list(self) -> list[dict]:
        race = self.db.races.get(self.ch.race) or {}
        out = [dict(c, _src=self.ch.race) for c in race.get("capacites", [])]
        sub = self.subrace() or {}
        out += [dict(c, _src=sub.get("nom", "")) for c in sub.get("capacites", [])]
        return out

    def _race_formula(self, description: str) -> tuple[str, str, bool]:
        """(formule résolue, type de dégâts, soin ?) d'un trait : « 1d12 + votre modificateur de Constitution »,
        « dégâts égaux à votre bonus de maîtrise », « points de vie égal à votre niveau »…"""
        d = norm(description)
        heal = bool(re.search(r"(rend|rendez|regagne|regagnez|recupere|recuperez)[^.]{0,40}points de vie", d))
        dtype = ""
        m = re.search(r"degats(?: de)? (" + "|".join(_DAMAGE_TYPES) + r")", d) or \
            re.search(r"\d+d\d+[^.]{0,60}?(" + "|".join(_DAMAGE_TYPES) + r")", d)
        if m:
            dtype = _DMG_TYPE_FR.get(m.group(1), m.group(1))
        m = re.search(r"(\d+d\d+)(\s*\+\s*votre (modificateur de (\w+)|bonus de maitrise|niveau))?", d)
        if m:
            flat = 0
            if m.group(4):
                flat = self.mod(_ABILITY.get(m.group(4), "Force"))
            elif m.group(3) == "bonus de maitrise":
                flat = self.prof
            elif m.group(3) == "niveau":
                flat = self.total_level
            return (m.group(1) + ("{:+d}".format(flat) if flat else "")), dtype, heal
        m = re.search(r"(?:degats|points de vie|pv)[^.]{0,50}?eg(?:al|ale|aux|ales) a votre (bonus de maitrise|niveau)", d)
        if m:
            return str(self.prof if m.group(1) == "bonus de maitrise" else self.total_level), dtype, heal
        return "", dtype, heal

    def race_actions(self) -> list[dict]:
        """Actions de race au format des actions de classe (sans l'état d'utilisation)."""
        out = []
        breath = self.breath_weapon() if hasattr(self, "breath_weapon") else None
        for c in self._race_trait_list():
            name, desc = c.get("nom", ""), c.get("description", "")
            is_breath = breath is not None and "souffle" in norm(name) and "infini" not in norm(name)
            if not is_breath and not is_race_action(name, desc):
                continue
            lvl = min_level(desc)
            kind = action_type(desc)
            if is_breath:
                key, uses = "souffle", 1
                formula, dtype, heal = breath["degats"], breath["type"], False
                desc = "{} — {}, JS de {} DD {}, {} {} (moitié en cas de réussite).".format(
                    desc, breath["zone"] or "zone selon la couleur", breath["js"], breath["dd"], breath["degats"],
                    breath["type"] or "(choisissez la couleur du dragon ancestral)")
            else:
                key = "race:{}:{}".format(_slug(c["_src"] or self.ch.race), _slug(name))
                uses = uses_of(desc, self.prof)
                formula, dtype, heal = self._race_formula(desc)
            jet = "degats" if formula and ("d" in formula or heal) else "aucun"     # bonus fixe : affiché seulement
            out.append({"id": key, "nom": name, "icone": "🐉" if is_breath else _ICONS[kind],
                        "classe": "", "race": c["_src"] or self.ch.race, "niveau": lvl, "type": kind,
                        "cout": {"ressource": key, "n": 1} if uses else {}, "jet": jet, "degats": formula,
                        "type_degats": dtype, "soin": heal, "description": desc, "origine": "race",
                        "ressource_race": key if uses else "", "utilisations": uses or 0,
                        "recuperation": "repos court" if is_breath else recovery_of(desc)})
        level = self.total_level
        return [a for a in out if level >= a["niveau"]]

    def race_action_trackers(self) -> list[dict]:
        """Compteurs à sphères des actions de race limitées (le souffle draconique garde sa clé « souffle »)."""
        out = []
        for a in self.race_actions():
            if not a["ressource_race"]:
                continue
            out.append({"key": a["ressource_race"], "label": a["nom"], "total": a["utilisations"],
                        "kind": "souffle" if a["ressource_race"] == "souffle" else "inspiration",
                        "recover": a["recuperation"], "where": "combat", "de": "", "race": True,
                        "info": "Capacité de race ({}) — {} utilisation{} — récupération au {}".format(
                            a["race"], a["utilisations"], "s" * (a["utilisations"] > 1), a["recuperation"])})
        return out

    def has_race_actions(self) -> bool:
        return bool(self.race_actions())

    def race_reactions(self) -> list[dict]:
        """Réactions raciales (Endurance de pierre, Esquive hadozi, Gambade heureuse…) pour l'encart Réactions."""
        return [{"cle": "race:" + a["nom"], "nom": a["nom"], "icone": "🛡", "source": "Race : " + a["race"],
                 "declencheur": "Voir la description du trait.", "effet": a["description"]}
                for a in self.race_actions() if a["type"] == "Réaction"]

