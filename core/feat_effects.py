"""
Effets calculés des dons (v52) — 2014 et 2024, logique pure mélangée à Engine.

Un don choisi (emplacement d'amélioration, don d'origine de l'historique 2024, don du MJ) applique ici tout ce que la
fiche sait calculer : valeurs passives (initiative, vitesse, PV, CA…), maîtrises (armures, armes, compétences,
expertise, outils, jets de sauvegarde), résistances, sorts accordés (toujours préparés, 1 lancer gratuit par repos
long), compteurs (points de chance…), tuiles d'action (Faveur de récupération, Figure de proue…), plafond de 30 des
Faveurs épiques. Ce qui demande un choix du joueur (compétences, liste de sorts, sorts, résistances) passe par
`feat_option_sets()` : un sélecteur par choix dans l'onglet Progression, compté dans les choix manquants.

Les dons sont retrouvés par leur nom de base (« Robuste (2024) » → « robuste ») et leur édition : la version 2014 et
la version 2024 d'un même don ont chacune leur entrée quand leurs effets diffèrent.
"""
from __future__ import annotations

import re
from typing import Optional

from . import rules as R
from .rules import ABILITIES, norm

DAMAGE_TYPES_BOON = ["acide", "froid", "feu", "foudre", "nécrotique", "poison", "psychique", "radiant", "tonnerre"]
INIT_LISTS_2014 = {"Barde": "Charisme", "Clerc": "Sagesse", "Druide": "Sagesse", "Ensorceleur": "Charisme",
                   "Occultiste": "Charisme", "Magicien": "Intelligence"}
INIT_LISTS_2024 = ["Clerc", "Druide", "Magicien"]
MENTAL = ["Intelligence", "Sagesse", "Charisme"]


def feat_base(name: str) -> str:
    return norm(re.sub(r"\s*\((?:2024|2014)\)\s*$", "", name or ""))


def _skills(*names):
    return {"kind": "competence", "options": list(names)}


# ------------------------------------------------------------------ registre
# clé : (nom de base, édition) ; édition None = les deux éditions.
# champs : init (int | "prof"), vitesse (m), pv_niveau, pv_max, pp (perception passive), carac (liste des
# caractéristiques au choix si les données n'en donnent pas), js_carac (maîtrise du JS de la carac. choisie),
# armures / armes (maîtrises), outils (fixes), choix (liste de choix), sorts (fixes), tracker, actions,
# maitrise_armes (+n bottes d'arme), cap30, concentration, reaction, mains_nues (dé), lourde_maitrise,
# dex_inter (Dex max des armures intermédiaires), vision_veritable, vision_aveugle, mort_avantage, dernier_rempart,
# competences_toutes.
REG: dict[tuple, dict] = {
    # --- dons d'origine 2024 et dons 2014 au même effet
    ("vigilant", None): {"init": "prof"},
    ("alerte", 2014): {"init": 5},
    ("robuste", None): {"pv_niveau": 2},
    ("mobile", None): {"vitesse": 3},
    ("observateur", 2014): {"pp": 5},
    ("chanceux", 2014): {"tracker": ("chance", "Points de chance", 3, "repos long",
                                     "Dépensez un point : lancez un d20 de plus et choisissez le résultat")},
    ("chanceux", 2024): {"tracker": ("chance", "Points de chance", "prof", "repos long",
                                     "Dépensez un point : avantage à un test de d20, ou désavantage à une attaque "
                                     "contre vous")},
    ("doue", None): {"choix": [{"id": "maitrises", "label": "compétences ou outils", "n": 3, "kind": "comp_outil"}]},
    ("initie a la magie", 2014): {"init_magie": 2014},
    ("initie a la magie", 2024): {"init_magie": 2024},
    ("bagarreur de tavernes", 2024): {"mains_nues": 4},
    ("faconneur", 2024): {"choix": [{"id": "outils", "label": "outils d'artisan", "n": 3, "kind": "outil_artisan"}]},
    ("musicien", 2024): {"choix": [{"id": "instruments", "label": "instruments de musique", "n": 3,
                                    "kind": "instrument"}]},
    # --- dons généraux
    ("resilient", None): {"carac": list(ABILITIES), "js_carac": True},
    ("resistant", None): {"js_carac": True},
    ("observateur", 2024): {"choix": [dict(_skills("Perspicacité", "Investigation", "Perception"), id="competence",
                                           label="compétence (maîtrise, ou expertise si déjà maîtrisée)", n=1,
                                           mode="pe")]},
    ("esprit affute", 2024): {"choix": [dict(_skills("Arcanes", "Histoire", "Investigation", "Nature", "Religion"),
                                             id="competence", label="compétence (maîtrise, ou expertise si déjà "
                                                                    "maîtrisée)", n=1, mode="pe")]},
    ("discret", 2024): {"vision_aveugle": 3},
    ("expert", 2024): {"choix": [{"id": "competence", "label": "compétence maîtrisée", "n": 1, "kind": "competence"},
                                 {"id": "expertise", "label": "expertise", "n": 1, "kind": "competence",
                                  "mode": "expertise"}]},
    ("formation aux armes de guerre", None): {"armes": ["Armes de guerre"]},
    ("protection legere", None): {"armures": ["Armures légères"]},
    ("protection intermediaire", None): {"armures": ["Armures intermédiaires", "Boucliers"]},
    ("protection lourde", None): {"armures": ["Armures lourdes"]},
    ("maitre des armures intermediaires", None): {"dex_inter": 3},
    ("maitre d'armes", 2024): {"maitrise_armes": 1},
    ("mage de guerre", None): {"concentration": True},
    ("lanceur de sorts", 2014): {"concentration": True},           # War Caster 2014 (nom des données)
    ("gaillard", 2024): {"mort_avantage": True, "actions": ["recuperation_rapide"]},
    ("cogneur lourd", 2024): {"lourde_maitrise": True},
    ("chef cuisinier", None): {"outils": ["Ustensiles de cuisinier"]},
    ("empoisonneur", None): {"outils": ["Matériel d’empoisonneur"]},
    ("figure de proue", None): {"actions": ["performance"], "tracker": (
        "figure_proue", "Figure de proue", 1, "repos court", "PV temporaires après un repos court ou long")},
    ("duelliste defensif", None): {"reaction": ("🤺", "Une attaque au corps à corps vous touche alors que vous maniez "
                                                "une arme de finesse.", "Ajoutez votre bonus de maîtrise à votre CA "
                                                "contre cette attaque (et les suivantes du round en 2024).")},
    ("telekinesiste", None): {"sorts": [("Main de mage", "À volonté")]},
    ("telepathe", None): {"sorts": [("Détection des pensées", "libre")]},
    ("affinite feerique", 2024): {"sorts": [("Foulée brumeuse", "libre")],
                                  "choix": [{"id": "sort", "label": "sort de niveau 1 (divination ou enchantement)",
                                             "n": 1, "kind": "sort", "niveau": 1,
                                             "ecoles": ["Divination", "Enchantement"]}]},
    ("emissaire des fees", 2014): {"sorts": [("Foulée brumeuse", "libre")],
                                   "choix": [{"id": "sort", "label": "sort de niveau 1 (divination ou enchantement)",
                                              "n": 1, "kind": "sort", "niveau": 1,
                                              "ecoles": ["Divination", "Enchantement"]}]},
    ("faveur des ombres", 2024): {"sorts": [("Invisibilité", "libre")],
                                  "choix": [{"id": "sort", "label": "sort de niveau 1 (illusion ou nécromancie)",
                                             "n": 1, "kind": "sort", "niveau": 1, "ecoles": ["Illusion", "Nécromancie"]}]},
    ("adepte des ombres", 2014): {"sorts": [("Invisibilité", "libre")],
                                  "choix": [{"id": "sort", "label": "sort de niveau 1 (illusion ou nécromancie)",
                                             "n": 1, "kind": "sort", "niveau": 1, "ecoles": ["Illusion", "Nécromancie"]}]},
    ("haute magie drow", 2014): {"sorts": [("Détection de la magie", "À volonté"), ("Lévitation", "libre"),
                                           ("Dissipation de la magie", "libre")], "carac_sorts": "Charisme"},
    ("teleportation feerique", 2014): {"sorts": [("Foulée brumeuse", "libre court")], "carac_sorts": "Intelligence"},
    # --- Faveurs épiques (2024) : +1 jusqu'à 30, puis l'effet propre
    ("faveur de competence", 2024): {"competences_toutes": True,
                                     "choix": [{"id": "expertise", "label": "expertise", "n": 1, "kind": "competence",
                                                "mode": "expertise"}]},
    ("faveur de recuperation", 2024): {"dernier_rempart": True, "actions": ["vitalite"],
                                       "tracker": ("vitalite", "Récupérer la vitalité (d10)", 10, "repos long",
                                                   "Réserve de dix d10 : par une action bonus, lancez-en et regagnez "
                                                   "autant de PV")},
    ("faveur de resistance aux energies", 2024): {"choix": [{"id": "resistances", "label": "résistances", "n": 2,
                                                             "kind": "liste", "options": DAMAGE_TYPES_BOON}]},
    ("faveur de vigueur", 2024): {"pv_max": 40},
    ("faveur de haute magie", 2014): {"emplacement_9": True},
    ("arme de nyx", 2014): {"pouvoir": {"uses": 1, "recover": "repos long", "type": "Action bonus", "effet": "arme_de_nyx",
                                        "description": "Pendant 1 minute, l'arme que vous tenez inflige 1d8 dégâts "
                                        "radiants supplémentaires quand elle touche (nécrotiques pour Érébos, foudre "
                                        "pour Kéranos, feu pour Purphoros). Une fois par repos long."}},
    ("faveur de memoire des sorts", 2024): {"memoire_sorts": True},
    ("faveur de vitesse", 2024): {"vitesse": 9},
    ("faveur de vision veritable", 2024): {"vision_veritable": 18},
    ("faveur du destin", 2024): {"actions": ["destin"], "tracker": (
        "faveur_destin", "Faveur du destin", 1, "repos court", "2d4 en bonus ou en malus à un test de d20 — revient à "
        "l'initiative ou au repos court ou long")},
}


def spec_for(name: str, edition: int) -> dict:
    base = feat_base(name)
    return REG.get((base, edition)) or REG.get((base, None)) or {}


class FeatEffectsMixin:
    """Mélangé à Engine : utilise chosen_feats, db, ch, prof, mod, total_level, casters…"""

    # ------------------------------------------------------------------ accès
    def _feat_edition(self, name: str) -> int:
        f = self.db.feats.get(name) or {}
        return 2024 if str(f.get("edition", "")) == "2024" else 2014

    def feat_specs(self) -> list[tuple[str, dict]]:
        out, seen = [], set()
        for name in self.chosen_feats():
            if name in seen:
                continue
            seen.add(name)
            f = self.db.feats.get(name) or {}
            spec = dict(spec_for(name, self._feat_edition(name)))
            if not spec and f.get("mj_seulement"):        # v53 : don du MJ — effets lus dans son texte
                spec = self._gm_spec(name, f)
            if f.get("categorie") == "Faveur épique":
                spec["cap30"] = True
            out.append((name, spec))
        return out

    def _gm_spec(self, name: str, feat: dict) -> dict:
        cache = self.db.__dict__.setdefault("_gm_feat_specs", {})
        if name not in cache:
            spells = {norm(n): n for n in self.db.spells if "(2024)" not in n}
            cache[name] = gm_feat_spec(feat, spells, [s["nom"] for s in self.db.skills])
        return cache[name]

    def _gm_uses(self, value) -> int:
        if isinstance(value, str) and value.startswith("mod:"):
            return max(1, self.mod(value[4:]))
        return int(value or 1)

    def feat_ability_cap(self, ab: str) -> int:
        """v53 : plafond relevé par un don (Bénédiction de santé : Constitution jusqu'à 22)."""
        caps = [int(spec.get("plafond", {}).get(ab, 0)) for _, spec in self.feat_specs()]
        caps += [22 for name, spec in self.feat_specs() if spec.get("champion") and
                 self.feat_choice(name, "carac")[:1] == [ab]]
        return max(caps or [0])

    def feat_passive(self, key: str) -> int:
        total = 0
        for _, spec in self.feat_specs():
            v = spec.get(key)
            if v == "prof":
                total += self.prof
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                total += v
        return total

    def feat_flag(self, key: str) -> list[str]:
        return [n for n, spec in self.feat_specs() if spec.get(key)]

    @staticmethod
    def feat_slug(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", norm(name)).strip("_")

    def feat_choice(self, feat: str, cid: str) -> list[str]:
        return list((self.ch.options_classe or {}).get("don:{}:{}".format(self.feat_slug(feat), cid), []))

    def feat_ability_options(self, name: str) -> list[str]:
        f = self.db.feats.get(name) or {}
        return spec_for(name, self._feat_edition(name)).get("carac") or list(f.get("carac_choix") or [])

    # ------------------------------------------------------------------ choix du joueur
    def _base_skill_profs(self) -> set[str]:
        return {n for n, st in self.ch.competences.items() if st.get("maitrise")} | self.invocation_skills()

    def _choice_options(self, feat: str, c: dict) -> dict[str, str]:
        kind = c.get("kind")
        if kind == "competence":
            names = c.get("options") or [s["nom"] for s in self.db.skills]
            return {n: "" for n in names}
        if kind == "comp_outil":
            return {**{s["nom"]: "Compétence" for s in self.db.skills}, **{t["nom"]: "Outil" for t in self.db.tools}}
        if kind == "outil_artisan":
            return {t["nom"]: "" for t in self.db.tools if norm(t.get("categorie", "")).startswith("outils d'artisan")}
        if kind == "instrument":
            names = [t["nom"] for t in self.db.tools if "instrument" in norm(t["nom"]) and "navigateur" not in norm(t["nom"])]
            names += [i["nom"] for i in getattr(self.db, "instruments", []) or []]
            return {n: "" for n in dict.fromkeys(names)} or {"Instrument de musique": ""}
        if kind == "liste":
            return {n: "" for n in c["options"]}
        if kind == "sort":
            out = {}
            for s in self.db.spells.values():
                if int(s.get("niveau") or 0) != c["niveau"]:
                    continue
                if c.get("ecoles") and s.get("ecole") not in c["ecoles"]:
                    continue
                if c.get("liste") and c["liste"] not in s.get("classes", []):
                    continue
                if not self._spell_allowed(s):
                    continue
                out[s["nom"]] = "{} — {}".format(s.get("ecole", ""), (s.get("description") or "")[:200])
            return dict(sorted(out.items(), key=lambda kv: norm(kv[0])))
        return {}

    def _spell_allowed(self, spell: dict) -> bool:
        allowed = getattr(self, "allowed", None)
        return allowed(spell) if allowed else True

    def _feat_choices(self, name: str, spec: dict) -> list[dict]:
        """Choix du don, y compris ceux d'Initié à la magie (liste, caractéristique, tours de magie, sort)."""
        choices = list(spec.get("choix", []))
        mode = spec.get("init_magie")
        if mode:
            lists = INIT_LISTS_2024 if mode == 2024 else list(INIT_LISTS_2014)
            choices.append({"id": "liste", "label": "liste de sorts", "n": 1, "kind": "liste", "options": lists})
            if mode == 2024:
                choices.append({"id": "carac", "label": "caractéristique d'incantation", "n": 1, "kind": "liste",
                                "options": MENTAL})
            picked = self.feat_choice(name, "liste")
            if picked:
                choices.append({"id": "mineurs", "label": "tours de magie ({})".format(picked[0]), "n": 2,
                                "kind": "sort", "niveau": 0, "liste": picked[0]})
                choices.append({"id": "sort1", "label": "sort de niveau 1 ({})".format(picked[0]), "n": 1,
                                "kind": "sort", "niveau": 1, "liste": picked[0]})
        return choices

    def feat_option_sets(self) -> list[dict]:
        out = []
        for name, spec in self.feat_specs():
            for c in self._feat_choices(name, spec):
                key = "don:{}:{}".format(self.feat_slug(name), c["id"])
                opts = self._choice_options(name, c)
                if not opts:
                    continue
                out.append({"key": key, "label": "{} : {}".format(name, c["label"]), "total": c["n"],
                            "options": opts, "chosen": list((self.ch.options_classe or {}).get(key, []))[:c["n"]],
                            "don": name})
        return out

    # ------------------------------------------------------------------ maîtrises
    def feat_skill_grants(self) -> tuple[set[str], set[str]]:
        """(compétences maîtrisées, compétences en expertise) accordées par les dons."""
        skills = {s["nom"] for s in self.db.skills}
        base = self._base_skill_profs()
        prof, exp = set(), set()
        for name, spec in self.feat_specs():
            if spec.get("competences_toutes"):
                prof |= skills
            for c in self._feat_choices(name, spec):
                if c.get("kind") not in ("competence", "comp_outil"):
                    continue
                for pick in self.feat_choice(name, c["id"]):
                    if pick not in skills:
                        continue
                    if c.get("mode") == "expertise":
                        exp.add(pick)
                    elif c.get("mode") == "pe" and (pick in base or pick in prof):
                        exp.add(pick)
                    else:
                        prof.add(pick)
        return prof, exp

    def feat_tools(self) -> list[str]:
        skills = {s["nom"] for s in self.db.skills}
        out = []
        for name, spec in self.feat_specs():
            out += spec.get("outils", [])
            for c in self._feat_choices(name, spec):
                if c.get("kind") in ("comp_outil", "outil_artisan", "instrument"):
                    out += [p for p in self.feat_choice(name, c["id"]) if p not in skills]
        return list(dict.fromkeys(out))

    def granted_tools(self) -> list[str]:
        """Outils accordés par les dons et la sous-classe (Assassin 2024)."""
        return list(dict.fromkeys(self.feat_tools() + self.subclass24_tools()))

    def power_attack_feat(self, weapon: dict) -> str:
        """Don qui permet −5 / +10 avec cette arme (2014) : Tireur d'élite (à distance), Briseur d'armes lourdes
        (arme lourde de corps à corps) ; "" sinon."""
        props = {norm(p) for p in weapon.get("proprietes", [])}
        for f in self.chosen_feats():
            if self._feat_edition(f) != 2014:
                continue
            b = feat_base(f)
            if b == "tireur d'elite" and weapon.get("type") == "distance":
                return f
            if b == "briseur d'armes lourdes" and weapon.get("type") == "cac" and "lourde" in props:
                return f
        return ""

    def has_power_attack(self) -> bool:
        return any(feat_base(f) in ("tireur d'elite", "briseur d'armes lourdes") and self._feat_edition(f) == 2014
                   for f in self.chosen_feats())

    def feat_proficiency_sources(self) -> list[dict]:
        out = []
        for name, spec in self.feat_specs():
            if spec.get("armures") or spec.get("armes"):
                out.append({"source": "Don : {}".format(name), "classe": "", "don": name,
                            "armures": list(spec.get("armures", [])), "armes": list(spec.get("armes", [])),
                            "mode": "don"})
        return out

    def feat_saves(self) -> set[str]:
        """Maîtrises de JS accordées par Résilient / Résistant (caractéristique choisie avec le don)."""
        out = set()
        valid = {s["id"] for s in self.asi_slots()}
        for sid, c in self.ch.ameliorations.items():
            if sid in valid and c.get("mode") == "don" and spec_for(c.get("don", ""), self._feat_edition(
                    c.get("don", ""))).get("js_carac"):
                ab = self.feat_choice_ability(c)
                if ab:
                    out.add(ab)
        return out

    # ------------------------------------------------------------------ modificateurs (CA, résistances, JS…)
    def feat_modifiers(self) -> list[tuple[str, dict]]:
        out = []
        for name, spec in self.feat_specs():
            m = {}
            if spec.get("pv_max"):
                m["pv_max"] = spec["pv_max"]
            for k, v in (spec.get("mods") or {}).items():  # v53 : dons du MJ (CA, JS, carac., résistances…)
                m[k] = v
            if spec.get("champion"):                     # Champions de Theros : +2 à la caractéristique choisie
                picked = self.feat_choice(name, "carac")
                if picked:
                    m.setdefault("carac", {})[picked[0]] = 2
            for c in self._feat_choices(name, spec):
                if c["id"] == "resistances":
                    m["resistances"] = self.feat_choice(name, "resistances")
            if m:
                out.append(("Don : " + name, m))
        return out

    # ------------------------------------------------------------------ Faveurs épiques : plafond 30
    def epic_boon_bonus(self) -> dict[str, int]:
        out = {ab: 0 for ab in ABILITIES}
        valid = {s["id"] for s in self.asi_slots()}
        for sid, c in self.ch.ameliorations.items():
            if sid in valid and c.get("mode") == "don" and (self.db.feats.get(c.get("don", "")) or {}).get(
                    "categorie") == "Faveur épique":
                ab = self.feat_choice_ability(c)
                if ab in out:
                    out[ab] += 1
        return out

    # ------------------------------------------------------------------ sorts accordés
    def _feat_spell_ability(self, name: str, spec: dict) -> str:
        mode = spec.get("init_magie")
        if mode == 2014:
            lst = self.feat_choice(name, "liste")
            return INIT_LISTS_2014.get(lst[0], "Intelligence") if lst else "Intelligence"
        if mode == 2024:
            ab = self.feat_choice(name, "carac")
            return ab[0] if ab else "Intelligence"
        if spec.get("carac_sorts"):
            return spec["carac_sorts"]
        for c in self.ch.ameliorations.values():          # caractéristique augmentée par le don
            if c.get("mode") == "don" and c.get("don") == name:
                ab = self.feat_choice_ability(c)
                if ab in MENTAL:
                    return ab
        opts = [a for a in self.feat_ability_options(name) if a in MENTAL]
        return max(opts or MENTAL, key=self.mod)

    def feat_spells(self) -> list[dict]:
        """[{nom, sort, niveau, usage, source, cle, emplacement, carac, dc, attaque}] des sorts accordés par les dons."""
        out = []
        for name, spec in self.feat_specs():
            grants = list(spec.get("sorts", []))
            for c in self._feat_choices(name, spec):
                if c.get("kind") == "sort":
                    for pick in self.feat_choice(name, c["id"]):
                        grants.append((pick, "À volonté" if c["niveau"] == 0 else "libre"))
            if not grants:
                continue
            ab = self._feat_spell_ability(name, spec)
            m = self.mod(ab)
            for spell_name, usage in grants:
                spell = self._edition_spell(spell_name)
                if not spell:
                    continue
                key = ""
                text = usage
                if usage == "libre jamais":                  # v53 : charme — utilisations comptées en tout
                    key = "don_mj_" + self.feat_slug(name)
                    total = self._gm_uses(spec.get("sorts_utilisations") or 1)
                    left = max(0, total - self.resource_used(key))
                    out.append({"nom": spell["nom"], "niveau": spell["niveau"], "usage": "{} / {} restant(s)"
                                .format(left, total), "source": "Don : " + name, "sort": spell, "categorie": "Dons",
                                "emplacement": True, "limite": "1", "cle": "", "cible": "", "carac": ab,
                                "dc": R.spell_save_dc(self.prof, m), "attaque": R.spell_attack_bonus(self.prof, m),
                                "recover": spec.get("sorts_recup") or "jamais", "cle_charme": key})
                    continue
                if usage.startswith("libre"):
                    key = "don:{}:{}".format(self.feat_slug(name), self.feat_slug(spell["nom"]))
                    period = "repos court" if usage.endswith("court") else "repos long"
                    left = max(0, 1 - self.resource_used(key))
                    text = "1 fois sans emplacement / {} — {} / 1 restant ; aussi avec vos emplacements".format(
                        period, left)
                out.append({"nom": spell["nom"], "niveau": spell["niveau"], "usage": text, "source": "Don : " + name,
                            "sort": spell, "categorie": "Dons", "emplacement": bool(key), "limite": "1" if key else "",
                            "cle": key, "cible": "", "carac": ab, "dc": R.spell_save_dc(self.prof, m),
                            "attaque": R.spell_attack_bonus(self.prof, m),
                            "recover": "repos court" if usage.endswith("court") else "repos long"})
        return out

    def _edition_spell(self, name: str) -> Optional[dict]:
        """Fiche du sort dans l'édition de la fiche (« Foulée brumeuse (2024) » sur une fiche 2024)."""
        if getattr(self, "sheet_edition", 2014) == 2024 and not name.endswith("(2024)"):
            spell = self.db.find_spell(name + " (2024)")
            if spell:
                return spell
        return self.db.find_spell(name)

    def feat_spell(self, spell_name: str) -> Optional[dict]:
        return next((s for s in self.feat_spells() if s["nom"] == spell_name), None)

    # ------------------------------------------------------------------ compteurs et tuiles
    def feat_trackers(self) -> list[dict]:
        out = []
        for name, spec in self.feat_specs():
            tr = spec.get("tracker")
            if tr:
                key, label, total, recover, info = tr
                total = self.prof if total == "prof" else int(total)
                out.append({"key": "don_" + key, "label": label, "total": total, "kind": "sursaut",
                            "recover": recover, "where": "combat", "de": "d10" if key == "vitalite" else "",
                            "info": "{} — {} (don {})".format(info, recover, name)})
            pw = spec.get("pouvoir")
            if pw:                                       # v53 : pouvoir d'un don du MJ (1 / repos, charme…)
                out.append({"key": "don_mj_" + self.feat_slug(name), "label": name, "total": self._gm_uses(pw["uses"]),
                            "kind": "sursaut", "recover": pw["recover"], "where": "combat", "de": "",
                            "info": "{} — {}".format(pw["description"][:200], "ne revient pas" if pw["recover"] ==
                                                     "jamais" else pw["recover"])})
            if spec.get("sorts_utilisations"):           # charme / dévot : N lancers
                rec = spec.get("sorts_recup") or "jamais"
                out.append({"key": "don_mj_" + self.feat_slug(name), "label": name,
                            "total": self._gm_uses(spec["sorts_utilisations"]), "kind": "sursaut", "recover": rec,
                            "where": "combat", "de": "", "info": "Lancers du sort accordé ({})".format(
                                "ne reviennent pas" if rec == "jamais" else rec)})
            if spec.get("dernier_rempart"):
                out.append({"key": "don_dernier_rempart", "label": "Dernier rempart", "total": 1, "kind": "sursaut",
                            "recover": "repos long", "where": "combat", "de": "",
                            "info": "Appliqué automatiquement quand vous tombez à 0 PV : 1 PV puis la moitié de vos "
                                    "PV maximum — repos long"})
        for s in self.feat_spells():
            if s["cle"]:
                out.append({"key": s["cle"], "label": "{} ({})".format(s["nom"], s["source"]), "total": 1,
                            "kind": "sursaut", "recover": s["recover"], "where": "interne", "de": "",
                            "info": s["usage"]})
        return out

    def feat_short_rest_keys(self) -> list[str]:
        return [t["key"] for t in self.feat_trackers() if t["recover"] == "repos court"]

    def feat_actions(self) -> list[dict]:
        out = []
        base = {"classe": "Don", "sous_classe": "", "niveau": 1, "jet": "aucun", "degats": "", "type_degats": ""}
        bases = {feat_base(f): f for f in self.chosen_feats()}
        if self.has_power_attack():                      # v52 : dons de combat
            on = self.ch.attaque_puissante
            out.append(dict(base, id="don_puissance", nom="Attaque puissante (−5 / +10) : " + ("activée" if on
                            else "désactivée"), icone="💪", type="Gratuit", cout=None, bascule=True,
                            description="Avant d'attaquer : −5 au toucher et +10 aux dégâts avec une arme à distance "
                            "(Tireur d'élite) ou une arme lourde de corps à corps (Briseur d'armes lourdes). Un clic "
                            "active ou désactive (aussi sur la ligne de l'arme)."))
        polearm = next((f for b, f in bases.items() if b in ("maitre des armes d'hast", "maitre d'hast")), "")
        if polearm:
            out.append(dict(base, id="don_pommeau", nom="Attaque du talon (arme d'hast)", icone="🔱",
                            type="Action bonus", cout=None, attaque_arme=True, flux="pommeau",
                            description="Après l'action Attaquer avec une coutille, une hallebarde, un bâton{} : "
                            "attaque avec l'autre bout, 1d4 dégâts contondants.".format(
                                " ou une lance" if self._feat_edition(polearm) == 2024 else "")))
        if "expert en arbaletes" in bases:
            out.append(dict(base, id="don_arbalete", nom="Arbalète de poing (Expert en arbalètes)", icone="🏹",
                            type="Action bonus", cout=None, attaque_arme=True,
                            description="Après une attaque avec une arme à une main : attaque avec une arbalète de "
                            "poing chargée ; pas de désavantage au contact."))
        cleave = next((f for b, f in bases.items() if b in ("briseur d'armes lourdes", "cogneur lourd")), "")
        if cleave:
            out.append(dict(base, id="don_fauchage", nom="Attaque bonus après un critique ou un ennemi à 0 PV",
                            icone="🪓", type="Action bonus", cout=None, attaque_arme=True,
                            description="Juste après un coup critique au corps à corps ou une créature réduite à 0 PV : "
                            "une attaque d'arme de corps à corps ({}).".format(cleave)))
        if "maitre des boucliers" in bases:
            ed = self._feat_edition(bases["maitre des boucliers"])
            out.append(dict(base, id="don_bouclier", nom="Coup de bouclier", icone="🛡", type="Action bonus" if
                            ed == 2014 else "Spécial", cout=None,
                            description="2014 : après l'action Attaquer, bousculez une créature à 1,50 m avec votre "
                            "bouclier (test d'Athlétisme opposé)." if ed == 2014 else "2024 : une fois par tour, "
                            "quand vous touchez au corps à corps : JS de Force DD {} ou la cible est repoussée de "
                            "1,50 m ou tombe à terre.".format(8 + self.prof + self.mod("Force"))))
        for name, spec in self.feat_specs():
            pw = spec.get("pouvoir")
            if pw:                                       # v53 : tuile du pouvoir d'un don du MJ
                key = "don_mj_" + self.feat_slug(name)
                extra = {}
                if pw.get("soin_moitie"):
                    extra = {"soin_fixe": self.hp_max() // 2, "soin": True}
                if pw.get("pv_temp"):
                    extra["pv_temp"] = pw["pv_temp"]
                if pw.get("effet"):
                    extra["effet"] = pw["effet"]
                out.append(dict(base, id=key, nom=name, icone="✨", type=pw["type"],
                                cout={"ressource": key, "n": 1}, jet=pw.get("jet", "aucun"),
                                degats=pw.get("degats", ""), description=pw["description"], **extra))
            for aid in spec.get("actions", []):
                if aid == "vitalite":
                    out.append(dict(base, id="don_vitalite", nom="Récupérer la vitalité", icone="💗",
                                    type="Action bonus", cout={"ressource": "don_vitalite", "n": 1}, jet="degats",
                                    degats="1d10", soin=True, description="Faveur de récupération : dépensez un d10 "
                                    "de la réserve et regagnez autant de PV (un clic par dé)."))
                elif aid == "destin":
                    out.append(dict(base, id="don_destin", nom="Améliorer le destin", icone="🎲", type="Spécial",
                                    cout={"ressource": "don_faveur_destin", "n": 1}, jet="degats", degats="2d4",
                                    description="Lancez 2d4 et ajoutez ou retranchez le total à un test de d20 "
                                    "(vous ou une créature à 18 m)."))
                elif aid == "performance":
                    ab = max(("Sagesse", "Charisme") if self._feat_edition(name) == 2024 else ("Charisme",),
                             key=self.mod)
                    amount = self.total_level + self.mod(ab)
                    out.append(dict(base, id="don_performance", nom="Performance stimulante", icone="📣",
                                    type="Spécial", cout={"ressource": "don_figure_proue", "n": 1},
                                    pv_temp=max(0, amount), description="Après un repos court ou long : jusqu'à six "
                                    "alliés (vous compris) gagnent {} PV temporaires (niveau + mod. de {}) ; les "
                                    "vôtres sont appliqués.".format(amount, ab)))
                elif aid == "recuperation_rapide":
                    out.append(dict(base, id="don_recuperation_rapide", nom="Récupération rapide", icone="💗",
                                    type="Action bonus", cout=None, des_de_vie=True, soin=True, jet="degats",
                                    degats=self._hit_die_formula(),
                                    description="Gaillard : dépensez un dé de vie et regagnez le résultat en PV."))
        return out

    def _hit_die_left(self) -> str:
        """Plus grand dé de vie encore disponible ("" si tous sont dépensés)."""
        return next((p["de"] for p in self.hit_dice_pool() if p["restants"] > 0), "")

    def _hit_die_formula(self) -> str:
        die = self._hit_die_left()
        return "1" + die if die else ""


# ---------------------------------------------------------------------------------------------- dons du MJ (v53)
_NUM = {"une": 1, "un": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "dix": 10}
_ABILITY_WORDS = {"force": "Force", "dexterite": "Dextérité", "constitution": "Constitution",
                  "intelligence": "Intelligence", "sagesse": "Sagesse", "charisme": "Charisme"}


def gm_feat_spec(feat: dict, spell_names: dict, skill_names: list[str]) -> dict:
    """v53 — effets d'un don accordé par le MJ (faveurs épiques 2014, bénédictions, charmes, dons de Theros et de
    Ravenloft) lus dans son texte : caractéristiques (+N, plafond), PV maximum, vitesse, CA et JS, résistances et
    immunités, avantages, vision véritable, maîtrise de toutes les compétences, sorts accordés, et un « pouvoir »
    (tuile + compteur) pour ce qui s'utilise une fois par repos, par aube ou un nombre fixe de fois."""
    desc = (feat or {}).get("description", "") or ""
    n = norm(desc)
    spec: dict = {}
    mods: dict = {}
    from .item_passives import damage_types_in
    for w, ab in _ABILITY_WORDS.items():
        m = re.search(r"valeur de " + w + r" augmente de (\d+)(?:, jusqu'a un maximum de (\d+))?", n)
        if m:
            mods.setdefault("carac", {})[ab] = int(m.group(1))
            if m.group(2):
                spec.setdefault("plafond", {})[ab] = int(m.group(2))
    m = re.search(r"maximum de points de vie augmente de (\d+)", n)
    if m:
        spec["pv_max"] = int(m.group(1))
    m = re.search(r"vitesse de marche augmente de (\d+(?:[.,]\d+)?) m", n)
    if m:
        spec["vitesse"] = float(m.group(1).replace(",", "."))
    m = re.search(r"vision (?:lucide|veritable) jusqu'a une portee de (\d+)", n)
    if m:
        spec["vision_veritable"] = int(m.group(1))
    if "maitrise de toutes les competences" in n:
        spec["competences_toutes"] = True
    m = re.search(r"^vous gagnez un bonus de \+(\d) a la ca et aux jets de sauvegarde", n)
    if m:
        mods["ca"] = int(m.group(1))
        mods["js"] = {"*": [int(m.group(1))]}
    if re.search(r"^vous avez l'avantage aux jets de sauvegarde contre les sorts", n):
        mods.setdefault("js", {})["sorts"] = ["avantage"]
        spec["note_js"] = "Avantage aux JS contre les sorts et effets magiques"
    m = re.search(r"avantage aux jets de sauvegarde de (\w+)", n)
    if m and m.group(1) in _ABILITY_WORDS:
        mods.setdefault("js", {})[_ABILITY_WORDS[m.group(1)]] = ["avantage"]
    for mt in re.finditer(r"(?:bonus de \+(\d+)|l'avantage) aux jets de \w+ \(([^)]+)\)", desc, re.I):
        skill = next((s for s in skill_names if norm(s) == norm(mt.group(2))), "")
        if skill and not re.search(r"qui reposent|lorsque|quand", norm(desc[mt.end():mt.end() + 40])):
            mods.setdefault("competences", {})[skill] = [int(mt.group(1)) if mt.group(1) else "avantage"]
    for mt in re.finditer(r"immunise contre (?:les )?degats (?:de |d')([^.]+)", n):
        mods.setdefault("immunites", []).extend(damage_types_in(mt.group(1)))
    if "immunise contre toutes les maladies et tous les poisons" in n:
        mods.setdefault("immunites", []).append("poison")
        mods.setdefault("etats_immunises", []).append("empoisonne")
    if re.search(r"^vous avez la resistance aux degats contondants, perforants et tranchants", n):
        mods.setdefault("resistances", []).append("contondant, perforant et tranchant (armes non magiques)")
    else:
        for mt in re.finditer(r"vous avez (?:aussi |egalement )?la resistance aux degats ([^.;]{0,40})", n):
            before = n[max(0, mt.start() - 60):mt.start()]
            if not re.search(r"pendant|lorsque|quand|jusqu'a", before):    # passif (pas l'effet d'un pouvoir)
                mods.setdefault("resistances", []).extend(damage_types_in(mt.group(1)))
    # Champions de Theros : +2 à une caractéristique au choix, maximum relevé de 2
    m = re.search(r"augmenter votre valeur de (\w+) ou de (\w+) de 2 et augmenter egalement votre maximum", n)
    if m and m.group(1) in _ABILITY_WORDS and m.group(2) in _ABILITY_WORDS:
        opts = [_ABILITY_WORDS[m.group(1)], _ABILITY_WORDS[m.group(2)]]
        spec["choix"] = [{"id": "carac", "label": "caractéristique (+2, maximum 22)", "n": 1, "kind": "liste",
                          "options": opts}]
        spec["champion"] = True
    m = re.search(r"(?:la |le )?(force|dexterite|constitution|intelligence|sagesse|charisme) est votre caracteristique "
                  r"d'incantation", n)
    if m:
        spec["carac_sorts"] = _ABILITY_WORDS[m.group(1)]
    if mods:
        spec["mods"] = mods
    # sorts : « lancer le sort X … à volonté » ; « une fois … repos court / long »
    for mt in re.finditer(r"(?:lancer|lancez)(?: le sort)? ([a-zà-ÿœ'’ -]{3,40}?)(?: \(|,|\.| a volonte| à volonté| par une"
                          r"| sans| en vous| grâce| grace)", desc, re.I):
        key = norm(mt.group(1).replace("’", "'")).strip()
        sp = spell_names.get(key) or spell_names.get(re.sub(r"^frappe ", "chatiment ", key))   # « frappe courroucée »
        if sp and sp not in [s for s, _u in spec.get("sorts", [])]:
            usage = "À volonté" if "volonte" in norm(desc[mt.end() - 12:mt.end() + 30]) else \
                "libre court" if "repos court" in n else "libre"
            spec.setdefault("sorts", []).append((sp, usage))
    # pouvoir à usage limité (tuile + compteur)
    uses, recover = 0, ""
    m = re.search(r"ne pouvez plus (?:l'|la |le )?(?:utiliser|refaire|faire)[^.]*?avant (?:d'avoir termine un |la fin d'un |"
                  r"de terminer un )?(repos court|repos long|l'aube|que 7 jours|le prochain coucher|le prochain "
                  r"crepuscule)", n)
    if m:
        uses, recover = 1, {"repos court": "repos court"}.get(m.group(1), "repos long")
    m = re.search(r"nombre de fois egal a votre modificateur de (\w+)", n)
    if m and m.group(1) in _ABILITY_WORDS:              # « autant de fois que votre modificateur de Sagesse »
        uses, recover = "mod:" + _ABILITY_WORDS[m.group(1)], "repos long"
    m2 = re.search(r"une fois utilise (\w+) fois", n) or re.search(r"possede (\d+) charges", n)
    if m2:
        uses, recover = (int(m2.group(1)) if m2.group(1).isdigit() else _NUM.get(m2.group(1), 1)), "jamais"
    elif "le charme vous quitte" in n and not uses:
        uses, recover = 1, "jamais"
    if uses and not spec.get("sorts"):
        kind = "Réaction" if "votre reaction" in n else "Action bonus" if "action bonus" in n else \
            "Action" if re.search(r"par une action|utiliser une action|une action pour", n) else "Spécial"
        power = {"uses": uses, "recover": recover, "type": kind, "description": desc[:400]}
        if "d10" in n and ("ajouter" in n or "bonus ou malus" in n):
            power.update(jet="degats", degats="1d10")
        if "+20" in n:
            power["note"] = "+20 au jet d'attaque à distance"
        if "moitie de votre maximum de points de vie" in n:
            power["soin_moitie"] = True
        if "potion d'heroisme" in n:
            power["pv_temp"] = 10
        spec["pouvoir"] = power
    elif uses and spec.get("sorts"):                     # sorts à utilisations comptées (charme, dévot…)
        spec["sorts"] = [(s, "libre jamais") for s, _u in spec["sorts"]]
        spec["sorts_utilisations"] = uses
        spec["sorts_recup"] = recover
    return spec
