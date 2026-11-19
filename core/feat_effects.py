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
    return norm(re.sub(r"\s*\(2024\)\s*$", "", name or ""))


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
            if f.get("categorie") == "Faveur épique":
                spec["cap30"] = True
            out.append((name, spec))
        return out

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
        for name, spec in self.feat_specs():
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
