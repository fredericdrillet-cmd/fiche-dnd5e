"""
Effets passifs sans condition (v53) — logique pure mélangée à Engine.

Lus dans le texte des traits raciaux, des dons et des objets magiques portés (et harmonisés si besoin), quand ils
s'appliquent en permanence ou sous une condition que la fiche connaît elle-même (armure portée ou non) :
  - CA naturelle : « sans armure, votre CA est égale à 13 + votre modificateur de Dextérité » (Homme-lézard,
    Autognome, Loxodon, Locathah, Tortle, Cuir de dragon) — proposée parmi les calculs sans armure ;
  - bonus fixe à la CA (Protection intégrée du Forgelier), ou sans armure ni bouclier (Bracelets de défense) ;
  - vitesses de nage / vol / escalade / creusement (« égale à votre vitesse de marche » ou « de 12 m ») ;
  - vitesse de marche : bonus d'un objet (Bottes du bourlingueur), minimum (Bottes de sept lieues) ;
  - initiative : bonus de maîtrise (Conil), bonus fixe (Armure de scorpion), avantage (Disciple de Keranos) ;
  - capacité de charge doublée (« comptez comme une créature de taille supérieure pour… votre capacité de charge ») ;
  - sens : vision aveugle, perception des vibrations, vision véritable ;
  - bonus fixe à une compétence (Gants de chapardeur : +5 en Escamotage) ;
  - langues données par un objet (« vous pouvez parler, lire et écrire l'abyssal ») ;
  - PV maximum par niveau (Hache du berserker), immunité aux maladies.
Les dons dont l'effet est déjà calculé ailleurs (vitesse, initiative, PV : core/feat_effects.py) ne sont pas repris.
"""
from __future__ import annotations

import re

from .rules import norm

ABILITY = {"force": "Force", "dexterite": "Dextérité", "constitution": "Constitution",
           "intelligence": "Intelligence", "sagesse": "Sagesse", "charisme": "Charisme"}
SPEEDS = {"nage": "nage", "vol": "vol", "escalade": "escalade", "creusement": "creusement",
          "fouissement": "creusement"}
# conditions qui font d'une phrase un effet temporaire ou activé (jamais appliqué d'office)
TEMPORARY = ("pendant ", "par une action", "action bonus", "lorsque vous lancez", "quand vous lancez", "en rage",
             "tant que vous y etes", "apres chaque", "jusqu'a la fin", "potion", "buvez", "si vous ", "chaque fois",
             "une fois", "depensez", "depenser", "reaction", "au niveau 5", "a partir du niveau", "choisissez",
             "lorsque vous etes", "quand vous etes", "transform", "forme de", "vous devenez")


def _sentences(text: str) -> list[str]:
    return [s.strip(" •-\t") for s in re.split(r"(?<=[.!?])\s+|\n+|;", text or "") if s.strip(" •-\t")]


def _num(text: str) -> float:
    return float(text.replace(",", "."))


def parse_passives(text: str, kind: str = "race") -> dict:
    """Effets passifs d'un texte (kind : « race », « don », « objet »). Dictionnaire vide s'il n'y en a pas."""
    spec: dict = {}
    for s in _sentences(text):
        n = norm(s)
        temporary = any(w in n for w in TEMPORARY)
        # ---- CA naturelle
        m = re.search(r"ca (?:de base )?(?:est )?(?:egale a |de )(\d+)(?: \+ votre modificateur de (\w+))?", n)
        if m and re.search(r"sans armure|ne portez pas d'armure|ne portez aucune armure|carapace|"
                           r"votre modificateur de dexterite n'a aucun effet", n) and not temporary:
            ab = ABILITY.get(m.group(2) or "", "")
            if "n'a aucun effet" in n or "n'influe pas" in n:
                ab = ""
            elif not m.group(2):
                ab = ""
            spec["ca_naturelle"] = (int(m.group(1)), ab)
            continue
        # ---- bonus fixe à la CA
        m = re.search(r"(?:bonus de )?\+(\d) (?:a|de) (?:la |votre )?(?:ca|classe d'armure)\b", n)
        if m and not temporary and not re.search(r"jets de sauvegarde|vos allies|votre defenseur|abri", n):
            heavy = re.search(r"(?:tant que|lorsque) vous portez une armure (lourde|intermediaire|legere)", n)
            if re.search(r"ne porte[rz]? (?:aucune armure|pas d'armure)[^.]*bouclier|sans armure ni bouclier", n):
                spec["ca_sans_armure"] = int(m.group(1))
            elif heavy:
                spec["ca_si_armure"] = (heavy.group(1), int(m.group(1)))   # Âme de la forge : armure lourde
            elif kind == "objet" and re.search(r"armure lourde|bouclier", n):
                pass
            else:
                spec["ca"] = int(m.group(1))
        # ---- vitesses spéciales
        for mt in re.finditer(r"vitesse (?:de |d')(nage|vol|escalade|creusement|fouissement)(?: de base)? "
                              r"(?:egale a votre vitesse(?: de marche)?|de (\d+(?:[.,]\d+)?) ?(?:m\b|metres))", n):
            if temporary and not re.search(r"lorsque vous portez|tant que vous portez", n):
                continue
            spec.setdefault("vitesses", {})[SPEEDS[mt.group(1)]] = _num(mt.group(2)) if mt.group(2) else "marche"
        # ---- vitesse de marche (objets) : bonus / minimum
        if kind == "objet" and not temporary:
            m = re.search(r"vitesse de marche augmente de (\d+(?:[.,]\d+)?) ?m", n)
            if m:
                spec["vitesse_bonus"] = _num(m.group(1))
            m = re.search(r"vitesse de marche passe a (\d+(?:[.,]\d+)?) ?m", n)
            if m:
                spec["vitesse_min"] = _num(m.group(1))
        # ---- initiative
        if kind != "don":
            if re.search(r"(?:ajoutez|ajouter) votre bonus de maitrise a vos jets d'initiative", n):
                spec["init"] = "maitrise"
            m = re.search(r"bonus de \+(\d+) a (?:l'initiative|vos jets d'initiative)", n)
            if m:
                spec["init"] = int(m.group(1))
        if re.search(r"(?<!des)avantage aux jets d'initiative", n) and not temporary and kind == "don":
            spec["init_avantage"] = True
        # ---- capacité de charge doublée
        if re.search(r"(?:comptez|compte) comme une creature (?:de taille |d'une taille )?(?:grande|superieure|"
                     r"plus grande|d'une taille de plus)[^.]*capacite de charge|taille de plus pour determiner "
                     r"votre capacite de charge", n):
            spec["charge_x2"] = True
        if re.search(r"compter comme (?:une creature )?(?:de taille )?grand(?:e)? pour (?:la|votre) (?:capacite de )?charge", n):
            spec["charge_x2"] = True                      # Goliath : « Petit géant »
        if re.search(r"vitesse n'est pas reduite (?:lorsque vous portez|par le port d'|si vous portez) une armure lourde", n):
            spec["armure_lourde_sans_malus"] = True       # nains : pas de malus de vitesse en armure lourde
        # ---- sens
        for mt in re.finditer(r"(vision aveugle|perception des vibrations|vision (?:veritable|lucide))"
                              r"[^.\d]{0,40}?(\d+(?:[.,]\d+)?) ?(?:m\b|metres)", n):
            if temporary:
                continue
            label = {"vision lucide": "vision véritable", "vision veritable": "vision véritable"}.get(
                mt.group(1), mt.group(1))
            spec.setdefault("sens", {})[label] = _num(mt.group(2))
        # ---- objets : bonus de compétence, langues, PV par niveau, maladies
        if kind == "objet":
            for mt in re.finditer(r"bonus de \+(\d+) aux (?:jets|tests) de \w+ \(([^)]+)\)", s, re.I):
                spec.setdefault("competences", {})[mt.group(2).strip()] = int(mt.group(1))
            m = re.search(r"(?:pouvez|savez) parler, lire et ecrire (?:le |l'|la )?([^.]+)", n)
            if m:
                langs = re.split(r",| et ", m.group(1))
                spec["langues"] = [x.strip().removeprefix("le ").removeprefix("l'").removeprefix("la ").strip()
                                   for x in langs if x.strip()]
            if re.search(r"maximum de points de vie augmente de 1 pour chaque niveau", n):
                spec["pv_par_niveau"] = 1
            m = re.search(r"maximum de points de vie augmente d'un montant egal a (\d+) \+ votre niveau", n)
            if m:
                spec["pv_fixe_niveau"] = int(m.group(1))   # Armure de préservation : 10 + niveau
            m = re.search(r"vision dans le noir (?:dans un rayon de|jusqu'a une distance de|sur) (\d+) ?m", n)
            if m and not temporary:
                spec["vision_noir"] = _num(m.group(1))
            m = re.search(r"maitrise des arcs longs et courts", n)
            if m:
                spec["arcs_maitrise"] = True
            m = re.search(r"bonus de \+(\d) aux jets de degats des attaques a distance realise?e?s avec ces armes", n)
            if m:
                spec["arcs_degats"] = int(m.group(1))
            if re.search(r"immunise contre (?:toutes )?les maladies", n):
                spec["maladies"] = True
    return spec


class PassivesMixin:
    """Mélangé à Engine : effets passifs lus dans les traits raciaux, les dons et les objets portés."""

    def passive_entries(self) -> list[tuple[str, dict]]:
        """[(libellé de la source, spec)] — mis en cache par état du personnage (appelé souvent)."""
        ch = self.ch
        key = (ch.race, ch.sous_race, tuple((e["nom"], e["niveau"], e.get("sous_classe", "")) for e in ch.classes),
               tuple(self.chosen_feats()), tuple(getattr(ch, "dons_mj", []) or []),
               tuple((e.get("nom"), e.get("equipe", True), e.get("harmonise"), e.get("detruit")) for e in
                     ch.objets_magiques), self.sheet_edition)
        cache = getattr(self, "_passives_cache", None)
        if cache and cache[0] == key:
            return cache[1]
        out: list[tuple[str, dict]] = []
        for c in self._race_trait_list() if hasattr(self, "_race_trait_list") else []:
            spec = parse_passives(c.get("description", "") or "", "race")
            if spec:
                out.append(("Trait racial : " + c.get("nom", ""), spec))
        for name in list(self.chosen_feats()) + list(getattr(ch, "dons_mj", []) or []):
            spec = parse_passives((self.db.feats.get(name) or {}).get("description", "") or "", "don")
            spec = {k: v for k, v in spec.items() if k in ("ca_naturelle", "init_avantage", "vitesses", "charge_x2")}
            if spec:
                out.append(("Don : " + name, spec))
        for e in ch.classes:                             # capacités de classe : seulement les bonus de CA
            for f in self.features(e):
                if not f.get("debloque") or self.feature_replaced(norm(f["nom"])):
                    continue
                desc = f.get("description", "") or ""
                spec = parse_passives(desc, "classe")
                spec = {k: v for k, v in spec.items() if k in ("ca", "ca_si_armure")}
                if any(w in norm(desc) for w in TEMPORARY):
                    spec.pop("ca", None)                  # capacité activée (action bonus, ki…) : pas un passif
                if spec:
                    out.append(("Capacité : " + f["nom"], spec))
        for entry in ch.objets_magiques:
            item = self.magic_item(entry.get("nom", "")) or {}
            if not entry.get("equipe", True) or entry.get("detruit") or (item.get("lien") and
                                                                          not entry.get("harmonise")):
                continue
            if item.get("perso") or norm(item.get("type", "")).startswith(("potion", "parchemin")):
                continue
            spec = parse_passives(item.get("description", "") or "", "objet")
            if item.get("ca"):
                spec.pop("ca", None)                      # déjà compté par le catalogue
            if spec:
                label = self.magic_display_name(entry) if entry.get("base") else entry.get("nom", "")
                out.append(("Objet : " + label, spec))
        self._passives_cache = (key, out)
        return out

    def passive_modifiers(self) -> list[tuple[str, dict]]:
        """Modificateurs (format mechanics) des passifs : CA, vitesse, compétences, PV max, maladies."""
        out = []
        armor = self.db.armors.get(self.ch.armure.get("nom", ""), {})
        no_armor = not armor or armor.get("categorie") == "aucune"
        for label, spec in self.passive_entries():
            m: dict = {}
            if spec.get("ca"):
                m["ca"] = spec["ca"]
            if spec.get("ca_sans_armure") and no_armor and not self.ch.armure.get("bouclier"):
                m["ca"] = m.get("ca", 0) + spec["ca_sans_armure"]
            if spec.get("ca_si_armure"):
                cat, val = spec["ca_si_armure"]
                if norm(armor.get("categorie", "")).startswith(cat[:6]):
                    m["ca"] = m.get("ca", 0) + val
            if spec.get("vitesse_bonus"):
                m["vitesse_bonus"] = spec["vitesse_bonus"]
            if spec.get("competences"):
                m["competences"] = {k: [v] for k, v in spec["competences"].items()}
            if spec.get("pv_par_niveau"):
                m["pv_max"] = spec["pv_par_niveau"] * self.total_level
            if spec.get("pv_fixe_niveau"):
                m["pv_max"] = m.get("pv_max", 0) + spec["pv_fixe_niveau"] + self.total_level
            if spec.get("maladies"):
                m["etats_immunises"] = ["malade"]
            if m:
                out.append((label, m))
        return out

    def natural_armor_options(self) -> dict:
        """Calculs de CA sans armure donnés par la race, un don ou un objet : {libellé: [(terme, valeur)]}."""
        out = {}
        for label, spec in self.passive_entries():
            if spec.get("ca_naturelle"):
                base, ab = spec["ca_naturelle"]
                terms = [(str(base), base)]
                if ab:
                    from . import rules as R
                    terms.append((R.ABBR[ab].capitalize(), self.mod(ab)))
                out[label.split(" : ", 1)[-1]] = terms
        return out

    def passive_speed_min(self) -> float:
        return max([spec.get("vitesse_min", 0) for _, spec in self.passive_entries()] or [0])

    def other_speeds(self) -> dict[str, float]:
        """Vitesses de nage, de vol, d'escalade, de creusement : {type: mètres} (la meilleure source)."""
        walk = self.speed()
        out: dict[str, float] = {}
        if hasattr(self, "swim_speed") and self.swim_speed():
            out["nage"] = self.swim_speed()               # Don des profondeurs (manifestation)
        for _, spec in self.passive_entries():
            for kind, val in (spec.get("vitesses") or {}).items():
                v = walk if val == "marche" else float(val)
                out[kind] = max(out.get(kind, 0.0), v)
        return out

    def other_speeds_text(self) -> str:
        from . import rules as R
        return " · ".join("{} {}".format(k, R.fmt_meters(v) + " m") for k, v in self.other_speeds().items())

    def passive_initiative(self) -> tuple[list[tuple[str, int]], list[str]]:
        terms, adv = [], []
        for label, spec in self.passive_entries():
            if spec.get("init") == "maitrise":
                terms.append((label.split(" : ", 1)[-1] + " (maîtrise)", self.prof))
            elif isinstance(spec.get("init"), int):
                terms.append((label.split(" : ", 1)[-1], spec["init"]))
            if spec.get("init_avantage"):
                adv.append(label)
        return terms, adv

    def item_darkvision(self) -> tuple[float, str]:
        """Vision dans le noir donnée par un objet porté (Lunettes de nuit : 18 m, +18 m si déjà présente)."""
        best = (0.0, "")
        for label, spec in self.passive_entries():
            if spec.get("vision_noir", 0) > best[0]:
                best = (spec["vision_noir"], label.split(" : ", 1)[-1])
        return best

    def bow_item_bonus(self, weapon_name: str) -> tuple[bool, int, str]:
        """Bracelets d'archer : (maîtrise, bonus aux dégâts, objet) pour l'arc long / l'arc court."""
        if norm(weapon_name) not in ("arc long", "arc court"):
            return False, 0, ""
        for label, spec in self.passive_entries():
            if spec.get("arcs_maitrise") or spec.get("arcs_degats"):
                return bool(spec.get("arcs_maitrise")), int(spec.get("arcs_degats") or 0), label.split(" : ", 1)[-1]
        return False, 0, ""

    def heavy_armor_no_slow(self) -> bool:
        return any(spec.get("armure_lourde_sans_malus") for _, spec in self.passive_entries())

    def passive_carry_x2(self) -> bool:
        return any(spec.get("charge_x2") for label, spec in self.passive_entries() if label.startswith("Trait"))

    def passive_senses(self) -> list[str]:
        out = []
        for label, spec in self.passive_entries():
            for sense, dist in (spec.get("sens") or {}).items():
                out.append("{} {} m ({})".format(sense.capitalize(), "{:g}".format(dist).replace(".", ","),
                                                  label.split(" : ", 1)[-1]))
        return out

    def natural_weapon(self) -> tuple[int, str, str]:
        """Arme naturelle de la race (Serres, Griffes, Cornes, Sabots, Morsure…) : (faces du dé, type de dégâts, nom),
        utilisée par les frappes à mains nues (1d6 tranchants au lieu de 1 + Force contondants). (0, "", "") sinon."""
        best = (0, "", "")
        for c in self._race_trait_list() if hasattr(self, "_race_trait_list") else []:
            d = norm(c.get("nom", "") + " : " + c.get("description", ""))
            if "arme naturelle" not in d and "armes naturelles" not in d and not re.match(
                    r"(griffes|serres|morsure|cornes|sabots|belier|crocs)\b", norm(c.get("nom", ""))):
                continue
            if any(w in d for w in ("action bonus", "pendant ", "lorsque vous vous transformez")):
                continue
            m = re.search(r"1d(\d+) \+ votre modificateur de force (?:points de )?degats (\w+)", d)
            if m and int(m.group(1)) > best[0]:
                kind = m.group(2)
                kind = {"tranchants": "tranchant", "perforants": "perforant", "contondants": "contondant"}.get(kind, kind)
                best = (int(m.group(1)), kind, c.get("nom", ""))
        return best

    def item_languages(self) -> list[tuple[str, str]]:
        """[(langue, objet)] parlées grâce à un objet porté."""
        out = []
        for label, spec in self.passive_entries():
            for lang in spec.get("langues") or []:
                out.append((lang, label.split(" : ", 1)[-1]))
        return out
