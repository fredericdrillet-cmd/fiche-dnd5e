"""
Actions et capacités spéciales de classe (encart « Actions de classe » de l'onglet Combat) — logique pure.

Les actions sont décrites dans data/Actions_Classes.json (classe, sous-classe, niveau, coût, jet, dégâts...).
Ce module :
    - calcule les nouvelles ressources à sphères (dés de supériorité, Second souffle, Sursaut d'activité,
      Conduit divin, Inspiration bardique, Sens divin) en plus de la Rage et du Ki existants ;
    - filtre les actions réellement disponibles pour le personnage (classe, niveau, sous-classe) ;
    - résout les formules ({ARTS_MARTIAUX}, {SUPERIORITE}, {SOURNOISE}, {CHATIMENT}...) ;
    - utilise une action : vérifie la ressource (verrouillage à épuisement), la dépense, applique l'état associé
      et renvoie les jets à animer (d20 d'attaque, dés de dégâts / soins / dé de ressource).
"""
from __future__ import annotations

import math
import re
from typing import Optional

from . import dice as D
from . import rules as R
from .rules import norm

# clé de ressource -> (libellé, icône de sphère (OrbBar), récupération)
CLASS_RESOURCES = {
    "superiorite": ("Dés de supériorité", "superiorite", "repos court"),
    "superiorite_tech": ("Dé de supériorité (Technique supérieure)", "superiorite", "repos court"),
    "second_souffle": ("Second souffle", "souffle", "repos court"),
    "sursaut": ("Sursaut d'activité", "sursaut", "repos court"),
    "conduit": ("Conduit divin", "conduit", "repos court"),
    "inspiration": ("Inspiration bardique", "inspiration", "repos long"),
    "sens_divin": ("Sens divin", "sens", "repos long"),
    "imposition": ("Imposition des mains", "jauge", "repos long"),
    "chant_lame": ("Chant de la lame", "inspiration", "repos long"),
    "psionique": ("Dés psioniques", "psionique", "repos long"),
    # utilisations internes (sans sphères affichées) : première utilisation gratuite, récupération d'un dé
    "murmures_gratuit": ("Murmures psychiques gratuits", "ki", "repos long"),
    "voile_gratuit": ("Voile psychique gratuit", "ki", "repos long"),
    "rupture_gratuit": ("Rupture spirituelle gratuite", "ki", "repos long"),
    "psi_recup": ("Récupération psionique", "ki", "repos court"),     # réserve de PV : jauge, pas de sphères
}
SHORT_REST_KEYS = ("ki", "forme", "superiorite", "superiorite_tech", "second_souffle", "sursaut", "conduit",
                   "psi_recup")
SUPERIOR_TECHNIQUE = "Technique supérieure"


def psionic_die(rogue_level: int) -> int:
    """Lame psychique : d6 (niv. 3), d8 (5), d10 (11), d12 (17)."""
    return 6 if rogue_level < 5 else 8 if rogue_level < 11 else 10 if rogue_level < 17 else 12


def superiority(level: int) -> tuple[int, int]:
    """Maître de guerre : (nombre de dés, faces) — 4d8 au niveau 3, 5 au 7, d10 au 10, 6 au 15, d12 au 18."""
    count = 4 if level < 7 else 5 if level < 15 else 6
    sides = 8 if level < 10 else 10 if level < 18 else 12
    return count, sides


def bardic_die(level: int) -> int:
    return 6 if level < 5 else 8 if level < 10 else 10 if level < 15 else 12


def channel_divinity(cleric: int, paladin: int) -> int:
    clerc = 0 if cleric < 2 else 1 if cleric < 6 else 2 if cleric < 18 else 3
    pal = 1 if paladin >= 3 else 0
    return max(clerc, pal)


def clean_formula(text: str) -> str:
    """« 1d8++3 » / « 1d8+-1 » / « 1d8+0 » -> formule propre."""
    text = text.replace(" ", "").replace("+-", "-").replace("++", "+")
    text = re.sub(r"[+-]0(?!\d)", "", text)
    return text.strip("+")


CHANNEL_EFFECTS = {"arme sacree": "arme_sacree", "voeu d'hostilite": "voeu_inimitie", "voeu d'inimitie": "voeu_inimitie"}
_ACTIVE_RX = re.compile(r"par une action|action bonus|(votre|sa|une) reaction|depens|utilisations?\s*:|une fois par "
                        r"(repos|jour)|recuperee?s? (apres|au)|vous apprenez|vous connaissez|choisissez|incantation|"
                        r"emplacements? de sort|sorts? de|maitrise d")
SKIP_PASSIVE = re.compile(r"^(conduit divin|sorts? |incantation|magie|maitrises?|formation|style de combat)")


def is_passive(description: str) -> bool:
    return not _ACTIVE_RX.search(norm(description))


def short_text(text: str, limit: int = 140) -> str:
    """Mention courte (première phrase, début de description) affichée à côté d'un choix."""
    first = re.split(r"(?<=\.)\s", (text or "").strip(), maxsplit=1)[0]
    first = first[:1].upper() + first[1:]
    return first if len(first) <= limit else first[:limit - 1].rstrip(" ,;") + "…"


# sorts qui donnent des PV temporaires : (formule de base, PV supplémentaires par niveau d'emplacement au-delà du sort)
TEMP_HP_SPELLS = {"simulacre de vie": ("1d4+4", 5), "armure d'agathys": ("5", 5)}


class ClassActionsMixin:
    """Mélangé à Engine : utilise class_level, mod, prof, ch, db, resource_trackers, add_effect..."""

    # ------------------------------------------------------------------ ressources à sphères
    def class_action_trackers(self) -> list[dict]:
        out = []
        ftr = self.class_level("Guerrier")
        entry = self.ch.find_class("Guerrier")
        if ftr >= 3 and entry and norm(entry.get("sous_classe", "")) == norm("Maître de guerre"):
            n, sides = superiority(ftr)
            out.append(self._tracker("superiorite", n, "{} dés de supériorité (d{}) — DD des manœuvres {} — "
                                     "récupérés au repos court".format(n, sides, self.maneuver_dc()),
                                     de="d{}".format(sides)))
        if self.superior_technique():                     # style de combat (Tasha) : 1 dé de supériorité d6
            out.append(self._tracker("superiorite_tech", 1, "Technique supérieure : 1 dé de supériorité (d6) pour la "
                                     "manœuvre « {} » — DD {} — récupéré au repos court ou long".format(
                                         self.ch.technique_manoeuvre or "à choisir", self.maneuver_dc()), de="d6"))
        if ftr >= 1:
            out.append(self._tracker("second_souffle", 1, "Action bonus : 1d10 + {} PV — repos court".format(ftr)))
        if ftr >= 2:
            out.append(self._tracker("sursaut", 2 if ftr >= 17 else 1, "Une action supplémentaire — repos court"))
        cd = channel_divinity(self.class_level("Clerc"), self.class_level("Paladin"))
        if cd:
            out.append(self._tracker("conduit", cd, "Utilisations de Conduit divin — repos court"))
        bard = self.class_level("Barde")
        if bard:
            n = max(1, self.mod("Charisme"))
            out.append(self._tracker("inspiration", n, "Dé d'inspiration d{} — récupération au {}".format(
                bardic_die(bard), "repos court" if bard >= 5 else "repos long"),
                recover="repos court" if bard >= 5 else "repos long", de="d{}".format(bardic_die(bard))))
        rogue = self.ch.find_class("Roublard")
        if rogue and rogue["niveau"] >= 3 and norm(rogue.get("sous_classe", "")).startswith("lame psychique"):
            sides = psionic_die(rogue["niveau"])
            out.append(self._tracker("psionique", 2 * self.prof, "{} dés d'énergie psionique (d{}) = 2 × bonus de "
                                     "maîtrise — tous récupérés au repos long".format(2 * self.prof, sides),
                                     de="d{}".format(sides)))
            for key, lvl in (("murmures_gratuit", 3), ("voile_gratuit", 13), ("rupture_gratuit", 17)):
                if rogue["niveau"] >= lvl:
                    out.append(dict(self._tracker(key, 1, "Première utilisation gratuite par repos long"),
                                    where="interne"))
            out.append(dict(self._tracker("psi_recup", 1, "Action bonus : récupérer 1 dé (1 / repos court)"),
                            where="interne"))
        wiz = self.ch.find_class("Magicien")
        if wiz and wiz["niveau"] >= 2 and "chantelame" in norm(wiz.get("sous_classe", "")):
            out.append(self._tracker("chant_lame", self.prof, "Activations : bonus de maîtrise ({}) — CA + mod. d'INT, "
                                     "+3 m de vitesse, avantage en Acrobaties — repos long".format(self.prof)))
        out += self.subclass_trackers()                  # runes, Puissance des géants, dés psi, Tir arcanique
        out += self.invocation_trackers()                # manifestations occultes (v37)
        out += self.class_tile_trackers()                # v39 : aptitudes limitées des classes et sous-classes
        if self.class_level("Paladin"):
            pool = 5 * self.class_level("Paladin")
            out.append(self._tracker("imposition", pool, "Réserve de {} PV (5 × niveau de paladin) — soigne au "
                                     "toucher ; 5 points guérissent une maladie ou un poison — repos long".format(pool)))
            out.append(self._tracker("sens_divin", max(1, 1 + self.mod("Charisme")), "Détection du bien et du mal "
                                     "(céleste, fiélon, mort-vivant à 18 m) — repos long"))
        return out

    @staticmethod
    def _tracker(key: str, total: int, info: str, recover: str = "", de: str = "") -> dict:
        label, kind, rec = CLASS_RESOURCES[key]
        return {"key": key, "label": label, "total": total, "kind": kind, "recover": recover or rec,
                "info": info, "where": "combat", "de": de}

    def superior_technique(self) -> bool:
        """Style de combat « Technique supérieure » choisi (Guerrier, Tasha)."""
        return self.style_active(SUPERIOR_TECHNIQUE)

    def superior_technique_action(self) -> Optional[dict]:
        """Action « Manœuvre (Technique supérieure) » : la manœuvre apprise, 1 dé de supériorité d6."""
        name = self.ch.technique_manoeuvre
        if not self.superior_technique() or name not in self.db.maneuvers:
            return None
        return {"id": "manoeuvre_style", "nom": "Manœuvre : " + name, "icone": "🎯", "classe": "Guerrier",
                "niveau": 1, "type": "Réaction" if norm(name) in ("riposte", "parade") else "Spécial",
                "cout": {"ressource": "superiorite_tech", "n": 1}, "jet": "degats", "degats": "1d6",
                "manoeuvre": name, "source_style": SUPERIOR_TECHNIQUE,
                "description": "Technique supérieure — {} (DD {} si la manœuvre impose un jet de sauvegarde). "
                               "Dépense le dé de supériorité (d6), lancé et ajouté selon la manœuvre.".format(
                                   self.db.maneuvers[name], self.maneuver_dc())}

    def maneuver_dc(self) -> int:
        return 8 + self.prof + max(self.mod("Force"), self.mod("Dextérité"))

    # ------------------------------------------------------------------ catalogue filtré
    def class_actions(self) -> list[dict]:
        """Actions disponibles pour ce personnage (classe, niveau, sous-classe), avec leur état d'utilisation."""
        out = []
        maneuvers = self.maneuver_actions()              # v39 : une tuile par manœuvre apprise
        for a in getattr(self.db, "class_actions", []):
            if self.class_level(a["classe"]) < int(a.get("niveau", 1)):
                continue
            if a.get("sous_classe"):
                entry = self.ch.find_class(a["classe"])
                if not entry or norm(entry.get("sous_classe", "")) != norm(a["sous_classe"]):
                    continue
            if a["id"] == "manoeuvre" and maneuvers:
                for m in maneuvers:
                    out.append(dict(m, **self.class_action_state(m)))
                continue
            if a["id"] == "ruse":                         # Action astucieuse : Foncer / Se désengager / Se cacher
                for r in self.cunning_actions_tiles(a):
                    out.append(dict(r, **self.class_action_state(r)))
                continue
            if a["id"] == "sournoise":                    # attaque d'arme de finesse / à distance, 1 fois par tour
                a = dict(a, type="Action", attaque_arme=True, par_tour=True, icone=a.get("icone", "🗡"),
                         description="Une fois par tour : attaque avec une arme de finesse ou à distance (avantage, "
                                     "ou un allié à 1,50 m de la cible) ; si elle touche, dégâts de l'arme + {} "
                                     "d'Attaque sournoise.".format(self.sneak_attack_dice()))
            out.append(dict(a, **self.class_action_state(a)))
        for a in self.subclass_actions():                # Chevalier runique, Soldat psi, Archer arcanique
            out.append(dict(a, **self.class_action_state(a)))
        tech = self.superior_technique_action()
        if tech is not None:                             # style Technique supérieure : manœuvre apprise
            out.append(dict(tech, **self.class_action_state(tech)))
        for a in self.race_actions():                    # capacités actives de la race (Fureur des petits…)
            out.append(dict(a, **self.class_action_state(a)))
        for a in self.invocation_actions():              # manifestations occultes (Tombe de Levistus…)
            out.append(dict(a, **self.class_action_state(a)))
        for a in self.class_tile_actions():              # v39 : aptitudes actives des classes et sous-classes
            out.append(dict(a, **self.class_action_state(a)))
        return out

    def _tracker_by_key(self) -> dict:
        return {t["key"]: t for t in self.resource_trackers()}

    def class_action_state(self, a: dict, slot_level: int = 0) -> dict:
        """{disponible, raison, cout_txt, formule} : verrouillage si la ressource nécessaire est épuisée."""
        cost = a.get("cout") or {}
        ok, why, cost_txt = True, "", ""
        free_key = cost.get("gratuit")
        free_left = bool(free_key) and self._free_left(free_key)
        if free_left:
            cost_txt = "gratuit (1re utilisation)"
        elif cost.get("ressource") == "psionique":
            n = int(cost.get("n", 1))
            tr = self._tracker_by_key().get("psionique")
            cost_txt = "{} dé{} psionique{}".format(n, "s" * (n > 1), "s" * (n > 1))
            if tr is None or tr["total"] - self.resource_used("psionique") < n:
                ok, why = False, "Dés psioniques épuisés — récupération au repos long."
        elif cost.get("ressource"):
            key, n = cost["ressource"], int(cost.get("n", 1))
            tr = self._tracker_by_key().get(key)
            label = CLASS_RESOURCES.get(key, (key,))[0] if key in CLASS_RESOURCES else \
                tr["label"] if tr else {"rage": "rage", "ki": "ki"}.get(key, key)
            unit = {"ki": ("point de ki", "points de ki"), "rage": ("rage", "rages"),
                    "superiorite": ("dé de supériorité", "dés de supériorité"),
                    "superiorite_tech": ("dé de supériorité", "dés de supériorité"),
                    "psi_guerrier": ("dé psionique", "dés psioniques"),
                    "sorcellerie": ("point de sorcellerie", "points de sorcellerie"),
                    "inspiration": ("dé d'inspiration", "dés d'inspiration"),
                    "forme": ("Forme sauvage", "Formes sauvages")}.get(key, ("utilisation", "utilisations"))
            cost_txt = "1+ PV de la réserve" if key == "imposition" else "{} {}".format(n, unit[n > 1])
            if tr is None:
                ok, why = False, "Ressource non disponible à ce niveau."
            elif tr["total"] is not None and tr["total"] - self.resource_used(key) < n:
                ok, why = False, "{} épuisé(e)s — récupération au {}.".format(label, tr["recover"])
        elif cost.get("emplacement"):
            cost_txt = "1 emplacement de sort"
            if not self.smite_levels():
                ok, why = False, "Aucun emplacement de sort disponible."
        elif cost.get("pacte"):                          # Attaque occulte : emplacement de Pacte uniquement
            count, plvl = self.pact()
            cost_txt = "1 emplacement de Pacte (niveau {})".format(plvl) if count else "emplacement de Pacte"
            if not count or self.ch.pacte_utilises >= count:
                ok, why = False, "Plus d'emplacement de Pacte — récupération au repos court."
        if ok and a.get("requiert_effet") and a["requiert_effet"] not in self.active_effect_keys():
            ok, why = False, "Uniquement {}.".format("en rage" if a["requiert_effet"] == "rage" else
                                                     "sous l'effet requis")
        if ok and a.get("par_tour") and self.per_turn_used(a["id"]):
            ok, why = False, "Déjà utilisée ce tour (une fois par tour)."
        if ok and a.get("attaque_arme") and not a.get("naturelle") and self.action_weapon_slot(a) is None:
            ok, why = False, ("Arme de finesse ou à distance requise (cases Main principale / Distance)."
                              if a["id"] == "sournoise" else "Arme de lancer requise en main principale.")
        if ok and a.get("rend") and self.resource_used(a["rend"]) <= 0:
            ok, why = False, "Réserve de dés psioniques déjà pleine."
        active = bool(a.get("bascule") and a.get("effet") in self.ch.effets_actifs)
        if active:                                       # capacité en cours : y mettre fin est gratuit
            ok, why, cost_txt = True, "", "—"
        if ok and not active and a.get("effet") == "rage" and self.ch.forme_type == "metamorphose":
            ok, why = False, "Impossible sous Métamorphose."
        if ok and not active and a["id"] == "chant_lame":
            armor = self.db.armors.get(self.ch.armure.get("nom", ""), {})
            if armor.get("categorie") in ("intermédiaire", "lourde") or self.ch.armure.get("bouclier"):
                ok, why = False, "Impossible avec une armure intermédiaire ou lourde, ou un bouclier."
        if ok and not active and self.action_needs_reaction(a) and self.ch.reaction_utilisee:
            ok, why = False, "Réaction déjà utilisée ce round (nouveau round : encart Réactions)."
        return {"disponible": ok, "raison": why, "cout_txt": cost_txt, "actif": active,
                "formule": self.class_action_formula(a, slot_level)}

    # ------------------------------------------------------------------ réactions liées aux capacités
    @staticmethod
    def action_needs_reaction(a: dict, choice: str = "") -> bool:
        """Capacités qui consomment la réaction du round : type « Réaction », manœuvres Riposte / Parade."""
        if a.get("type") == "Réaction":
            return True
        if a.get("id") == "manoeuvre_style":
            return norm(a.get("manoeuvre", "")) in ("riposte", "parade")
        return a.get("id") == "manoeuvre" and norm(choice) in ("riposte", "parade")

    def reaction_key_for(self, name: str) -> str:
        """Clé de l'encart Réactions correspondant à une capacité (pour la cocher automatiquement)."""
        n = norm(name)
        r = next((r for r in self.reactions() if norm(r["nom"]) == n or n in norm(r["nom"])), None)
        return r["cle"] if r else "apt:" + name

    # ------------------------------------------------------------------ Conduit divin selon serment / domaine
    def channel_options(self, class_name: str) -> list[dict]:
        """Options de Conduit divin de la sous-classe choisie : [{nom, description, court}] (niveau atteint)."""
        entry = self.ch.find_class(class_name)
        sub = self.db.subclass(class_name, entry.get("sous_classe", "")) if entry else None
        if not sub:
            return []
        out = []
        for f in sub.get("capacites", []):
            if f["niveau"] > entry["niveau"] or not norm(f["nom"]).startswith("conduit divin"):
                continue
            names = [x.strip() for x in f["nom"].split(":", 1)[-1].split("&") if x.strip()]
            desc = f["description"]
            for i, name in enumerate(names):
                start = desc.find(name + " :")
                if start < 0 or len(names) == 1:
                    part = desc
                else:
                    nxt = [desc.find(n2 + " :") for n2 in names[i + 1:] if desc.find(n2 + " :") > start]
                    part = desc[start + len(name) + 2: min(nxt) if nxt else len(desc)].strip()
                out.append({"nom": name, "description": part, "court": short_text(part)})
        return out

    # ------------------------------------------------------------------ passifs de classe
    def class_passives(self) -> list[dict]:
        """Capacités passives débloquées (Rage implacable, Évasion, Aura de protection…) : [{nom, description, source}]."""
        curated = {norm(n) for names in getattr(self.db, "class_passives", {}).values() for n in names}
        action_names = {norm(a["nom"]) for a in self.class_actions()}
        best: dict[str, dict] = {}
        for e in self.ch.classes:
            for f in self.features(e):
                if not f["debloque"]:
                    continue
                n = norm(f["nom"])
                base = re.sub(r"\s*\(.*\)$", "", n)
                if base in action_names or n in action_names:
                    continue
                if base in curated or n in curated or (f["sous_classe"] and is_passive(f["description"]) and
                                                       not SKIP_PASSIVE.match(n)):
                    key = base
                    if key not in best or f["niveau"] >= best[key]["niveau"]:
                        best[key] = {"nom": f["nom"], "description": f["description"], "niveau": f["niveau"],
                                     "source": "{} niv. {}".format(f["source"], f["niveau"])}
        # styles de combat passifs choisis (Défense, Duel, Archerie…) : capacités permanentes ; seuls Protection et
        # Interception, qui consomment la réaction, restent dans l'encart Réactions
        from .engine_extras import REACTION_STYLES
        reaction_styles = {norm(r[0]) for r in REACTION_STYLES}
        for slot in self.fighting_style_slots():
            name = self.ch.styles_combat.get(slot["id"], "")
            desc = self.db.styles_by_class.get(slot["classe"], {}).get(name) and \
                self.db.style_description(slot["classe"], name)
            if slot["kind"] != "style" or not slot["debloque"] or not desc or norm(name) in reaction_styles:
                continue
            key = "style:" + norm(name)
            best.setdefault(key, {"nom": "Style de combat : " + name, "description": desc, "niveau": slot["niveau_requis"],
                                  "source": "{} niv. {}".format(slot["classe"], slot["niveau_requis"])})
        for p in self.subclass_passives():               # passifs des runes gravées
            best.setdefault("rune:" + norm(p["nom"]), p)
        for p in self.invocation_passives():             # manifestations occultes passives (v37)
            best.setdefault("manif:" + norm(p["nom"]) + norm(p["description"])[:20], p)
        return sorted(best.values(), key=lambda p: (p["niveau"], p["nom"]))

    def smite_levels(self) -> list[int]:
        """Niveaux d'emplacement encore disponibles (Châtiment divin), pacte compris."""
        slots = self.spell_slots()
        levels = [lvl for lvl in range(1, 10) if lvl - 1 < len(slots) and
                  self.ch.emplacements_utilises[lvl - 1] < slots[lvl - 1]]
        count, plvl = self.pact()
        if count and self.ch.pacte_utilises < count and plvl not in levels:
            levels.append(plvl)
        return sorted(levels)

    def class_action_formula(self, a: dict, slot_level: int = 0) -> str:
        text = a.get("degats", "")
        if not text:
            return ""
        monk = self.class_level("Moine")
        rogue = self.class_level("Roublard")
        _, sup = superiority(self.class_level("Guerrier"))
        level = slot_level or (self.smite_levels() or [1])[0]
        values = {
            "ARTS_MARTIAUX": "1d{}".format(R.martial_arts_die(monk)),
            "MOD_FINESSE": "{:+d}".format(max(self.mod("Force"), self.mod("Dextérité"))),
            "SUPERIORITE": "1d{}".format(sup),
            "SOURNOISE": "{}d6".format(max(1, math.ceil(rogue / 2))),
            "INSPIRATION": "1d{}".format(bardic_die(self.class_level("Barde"))),
            "CHATIMENT": "{}d8".format(min(5, 1 + max(1, level))),
            "PSI": "1d{}".format(psionic_die(self.class_level("Roublard"))),
            "OCCULTE": "{}d8".format(1 + (self.pact()[1] or 1)),
        }

        def repl(m):
            key = m.group(1)
            if key.startswith("NIV_"):
                return str(self.class_level(key[4:]))
            return values.get(key, "0")
        return clean_formula(re.sub(r"\{([A-Za-zÀ-ÿ_]+)\}", repl, text))

    # ------------------------------------------------------------------ utilisation
    def unarmed_attack_spec(self, title: str) -> "D.RollSpec":
        ab = "Force" if self.mod("Force") >= self.mod("Dextérité") else "Dextérité"
        detail = [(R.mod_label(ab), "{:+d}".format(self.mod(ab))), ("Maîtrise", "{:+d}".format(self.prof))]
        fx = self.attack_mods()
        return D.spec_from_detail(title, "attaque", detail + fx["detail"], fx["avantage"], fx["desavantage"],
                                  fx["echec"])

    def use_class_action(self, action_id: str, slot_level: int = 0, choice: str = "") -> dict:
        """
        Déclenche une action : dépense la ressource (ou l'emplacement), applique l'état associé et renvoie
        {ok, message, attaque (RollSpec|None), degats (DamageSpec|None), soin (bool)}.
        """
        a = next((x for x in self.class_actions() if x["id"] == action_id), None)
        if a is None:
            return {"ok": False, "message": "Action indisponible.", "attaque": None, "degats": None, "soin": False}
        state = self.class_action_state(a, slot_level)
        if not state["disponible"]:
            return {"ok": False, "message": "{} : {}".format(a["nom"], state["raison"]), "attaque": None,
                    "degats": None, "soin": False}
        if state.get("actif"):                           # capacité active : on y met fin, sans coût
            self.remove_effect(a["effet"])
            return {"ok": True, "message": "{} : fin de l'effet.".format(a["nom"]), "attaque": None, "degats": None,
                    "soin": False, "lancer_maintenant": False}
        needs_reaction = self.action_needs_reaction(a, choice) or (
            a.get("choix") == "conduit" and any(o["nom"] == choice and "reaction" in norm(o["description"])
                                                for o in self.channel_options(a["classe"])))
        if needs_reaction and self.ch.reaction_utilisee:
            return {"ok": False, "message": "Réaction déjà utilisée ce round.", "attaque": None, "degats": None,
                    "soin": False}
        cost = a.get("cout") or {}
        spent = ""
        if cost.get("gratuit") and self._free_left(cost["gratuit"]):
            self.set_resource_used(cost["gratuit"], self.resource_used(cost["gratuit"]) + 1)
            spent = "utilisation gratuite"
        elif cost.get("ressource") and not cost.get("verif_seul"):
            key = cost["ressource"]
            self.set_resource_used(key, self.resource_used(key) + int(cost.get("n", 1)))
            spent = state["cout_txt"]
        elif cost.get("emplacement"):
            levels = self.smite_levels()
            lvl = slot_level if slot_level in levels else levels[0]
            count, plvl = self.pact()
            slots = self.spell_slots()
            if lvl - 1 < len(slots) and self.ch.emplacements_utilises[lvl - 1] < slots[lvl - 1]:
                self.ch.emplacements_utilises[lvl - 1] += 1
            else:
                self.ch.pacte_utilises += 1
            spent = "emplacement de niveau {}".format(lvl)
            state["formule"] = self.class_action_formula(a, lvl)
        elif cost.get("pacte"):
            self.ch.pacte_utilises += 1
            spent = "emplacement de Pacte"
        if a.get("pv_temp"):                             # Tombe de Levistus : PV temporaires
            self.apply_temp_hp(int(a["pv_temp"]))
        if a.get("rend"):                                # Récupération psionique : un dé revient dans la réserve
            self.set_resource_used(a["rend"], max(0, self.resource_used(a["rend"]) - 1))
        effect = a.get("effet", "")
        if a["id"] == "ruse" and choice:                 # Action astucieuse : Foncer / Se désengager / Se cacher
            effect = {"foncer": "foncer", "se desengager": "desengagement", "se cacher": "cache"}.get(norm(choice), effect)
        if a.get("choix") == "conduit" and choice:      # Conduit divin : effets connus (Arme sacrée, Vœu…)
            effect = CHANNEL_EFFECTS.get(norm(choice), effect)
        if effect and effect != "rage":
            self.add_effect(effect)
        reaction = ""
        if needs_reaction:                               # synchronisation avec l'encart Réactions
            reaction = self.reaction_key_for(choice if a["id"] == "manoeuvre" or a.get("choix") == "conduit"
                                             else a["nom"])
            self.ch.reaction_utilisee = reaction
        title = a["nom"] + (" — " + choice if choice else "")
        if a.get("par_tour"):                            # v39 : capacités « une fois par tour »
            self.mark_per_turn(a["id"])
        if a.get("attaque_arme"):                        # v39 : attaque avec l'arme équipée + dé de la capacité
            attack, dmg = self.weapon_action_specs(a, state["formule"])
            if a.get("type") == "Action":
                self.ch.tour_attaques = int(self.ch.tour_attaques) + 1
                self.ch.tour_action = True
            msg = "{}{}{}.".format(a["nom"], " — {}".format(spent) if spent else "",
                                   " — réaction du round consommée" if reaction else "")
            return {"ok": True, "message": msg, "attaque": attack, "degats": dmg, "soin": False,
                    "lancer_maintenant": False}
        attack = self.unarmed_attack_spec(title) if a.get("jet") == "attaque_mains_nues" else None
        dmg = None
        if state["formule"] and a.get("jet") in ("degats", "attaque_mains_nues"):
            kind = "soins" if a.get("soin") else "de" if (a["id"] in ("manoeuvre", "manoeuvre_style", "inspiration") or
                                                         a.get("flux") or
                                                         a.get("type_degats") == "") else "degats"
            note = (self.maneuvers_note(choice) if a["id"] == "manoeuvre" else
                    self.maneuvers_note(a["manoeuvre"]) if a["id"] == "manoeuvre_style" or a.get("flux") else "")
            dmg = D.DamageSpec(title, state["formule"], a.get("type_degats", ""), note, kind)
        msg = "{}{}{}.".format(a["nom"], " — {}".format(spent) if spent else " : utilisé",
                               " — réaction du round consommée" if reaction else "")
        return {"ok": True, "message": msg, "attaque": attack, "degats": dmg, "soin": bool(a.get("soin")),
                "lancer_maintenant": a.get("jet") != "attaque_mains_nues"}

    def class_action_preview(self, action_id: str) -> Optional["D.DamageSpec"]:
        """Dé d'une action « dépensé seulement en cas de réussite » (Savoir-faire renforcé, Frappes autoguidées) :
        lancé AVANT toute dépense ; l'interface demande ensuite si le jet réussit."""
        a = next((x for x in self.class_actions() if x["id"] == action_id), None)
        if a is None or not a["disponible"] or not a["formule"]:
            return None
        return D.DamageSpec(a["nom"], a["formule"], "", "Le dé n'est dépensé que si le jet réussit grâce à lui.", "de")

    def _free_left(self, key: str) -> bool:
        tr = self._tracker_by_key().get(key)
        return bool(tr) and tr["total"] - self.resource_used(key) > 0

    def lay_on_hands_left(self) -> int:
        tr = self._tracker_by_key().get("imposition")
        return tr["total"] - self.resource_used("imposition") if tr else 0

    def use_lay_on_hands(self, amount: int, target: str = "soi", cure: bool = False) -> dict:
        """
        Imposition des mains : puise `amount` points dans la réserve (5 × niveau de paladin).
        target « soi » -> PV rendus immédiatement (plafonnés au maximum ; seuls les points utiles sont dépensés) ;
        « allie » -> points dépensés, à reporter sur la fiche de l'allié. cure=True : 5 points, guérit une maladie
        ou neutralise un poison (pas de PV rendus).
        """
        left = self.lay_on_hands_left()
        if cure:
            amount = 5
        amount = int(amount)
        if amount <= 0:
            return {"ok": False, "message": "Choisissez un nombre de points à dépenser.", "soin": 0, "depense": 0}
        if amount > left:
            return {"ok": False, "message": "Réserve insuffisante : {} point(s) restant(s).".format(left),
                    "soin": 0, "depense": 0}
        healed = 0
        if cure:
            msg = "Imposition des mains : maladie ou poison soigné (5 points)."
            if "empoisonne" in self.ch.effets_actifs and target == "soi":
                self.remove_effect("empoisonne")
                msg = "Imposition des mains : poison neutralisé (5 points)."
        elif target == "soi":
            current = self.ch.pv_actuels if self.ch.pv_actuels >= 0 else self.hp_max()
            amount = min(amount, self.hp_max() - current)          # on ne gaspille pas la réserve
            if amount <= 0:
                return {"ok": False, "message": "Vous avez déjà tous vos PV.", "soin": 0, "depense": 0}
            healed = self.heal(amount)
            msg = "Imposition des mains : +{} PV.".format(healed)
        else:
            msg = "Imposition des mains sur un allié : {} PV rendus.".format(amount)
        self.set_resource_used("imposition", self.resource_used("imposition") + amount)
        return {"ok": True, "message": msg + " Réserve : {} / {}.".format(self.lay_on_hands_left(),
                                                                           self._tracker_by_key()["imposition"]["total"]),
                "soin": healed, "depense": amount}

    def maneuvers_note(self, name: str) -> str:
        desc = getattr(self.db, "maneuvers", {}).get(name, "")
        return "{} — DD {}".format(desc, self.maneuver_dc()) if desc else ""

    # ------------------------------------------------------------------ PV temporaires (Simulacre de vie…)
    def temp_hp_spell(self, spell_name: str) -> bool:
        spell = self.db.find_spell(spell_name)
        return bool(spell) and norm(spell["nom"]) in TEMP_HP_SPELLS

    def temp_hp_formula(self, spell_name: str, slot_level: int = 0) -> str:
        """« 1d4+4 » au niveau 1 de Simulacre de vie, +5 par niveau d'emplacement supérieur (« 1d4+14 » au 3)."""
        spell = self.db.find_spell(spell_name)
        if not spell or norm(spell["nom"]) not in TEMP_HP_SPELLS:
            return ""
        base, per = TEMP_HP_SPELLS[norm(spell["nom"])]
        extra = per * max(0, int(slot_level or spell["niveau"]) - spell["niveau"])
        groups, flat = D.parse_damage(base)
        dice = "+".join("{}d{}".format(n, f) for _, n, f in groups)
        total_flat = flat + extra
        return clean_formula("{}+{}".format(dice, total_flat) if dice else str(total_flat))

    def slot_levels_from(self, level: int) -> list[int]:
        """Niveaux d'emplacement disponibles ≥ level (pacte compris) : choix du surclassement."""
        return [lvl for lvl in self.smite_levels() if lvl >= level]

    def apply_temp_hp(self, amount: int) -> int:
        """PV temporaires : ils ne se cumulent pas — on garde la valeur la plus haute."""
        self.ch.pv_temporaires = max(int(self.ch.pv_temporaires), max(0, int(amount)))
        return self.ch.pv_temporaires

    def wears_armor(self) -> str:
        """Nom de l'armure portée (hors bouclier), « » sinon — Armure de mage est alors sans effet."""
        name = self.ch.armure.get("nom", "")
        return "" if not name or name == "Aucune armure" else name

    def heal(self, amount: int) -> int:
        """Soins (Second souffle...) : PV actuels plafonnés au maximum ; renvoie les PV réellement regagnés."""
        before = self.ch.pv_actuels if self.ch.pv_actuels >= 0 else self.hp_max()
        after = min(self.hp_max(), before + max(0, int(amount)))
        self.ch.pv_actuels = after
        return after - before

    # ------------------------------------------------------------------ jets de dégâts (clic sur un libellé)
    def damage_spec(self, title: str, formula: str, damage_type: str = "", note: str = "") -> Optional["D.DamageSpec"]:
        return D.DamageSpec(title, formula, damage_type, note) if D.has_dice(formula) else None

    def spell_damage_formula(self, spell_name: str, slot_level: int = 0, class_name: str = "") -> str:
        """Dégâts d'un sort : sorts mineurs à l'échelle du niveau global ; sinon formule auditée au niveau
        d'emplacement choisi (surclassement), modificateur ajouté seulement si la règle le prévoit."""
        spell = self.db.find_spell(spell_name)
        if not spell:
            return ""
        if spell["niveau"] == 0:
            st = self.cantrip_stats(spell["nom"]) or {}
            return st.get("degats") or spell.get("degats", "")
        vals = self.spell_values(spell["nom"], slot_level, class_name) or {}
        return vals.get("degats") or ""
