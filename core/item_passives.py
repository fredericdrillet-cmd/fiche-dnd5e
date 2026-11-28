"""
Effets passifs des objets magiques (v52) — logique pure mélangée à Engine.

Lus dans la description des objets officiels qui n'ont pas de règle dédiée (mechanics.ITEM_MECH), ou donnés par
les champs des objets sur mesure :
  - résistances (« la résistance aux dégâts de feu et de froid ») ; « un type de dégâts choisi par le MD » ->
    choix enregistré sur l'objet (`resistance_choisie`) ;
  - immunités aux dégâts (« immunisé contre les dégâts de poison ») et aux états (« contre l'état empoisonné ») ;
  - bonus à la CA et aux jets de sauvegarde (et aux tests : Pierre porte-bonheur) quand le catalogue ne les a pas.
Les phrases d'activation (action, charges, « pendant 1 minute »…) sont ignorées : ce ne sont pas des passifs.
"""
from __future__ import annotations

import re

from .rules import norm

DAMAGE_TYPES = ["acide", "contondant", "feu", "force", "foudre", "froid", "nécrotique", "perforant", "poison",
                "psychique", "radiant", "tonnerre", "tranchant"]
CONDITIONS = {"charme": "charme", "effraye": "effraye", "empoisonne": "empoisonne", "paralyse": "paralyse",
              "petrifie": "petrifie", "etourdi": "etourdi", "aveugle": "aveugle", "assourdi": "assourdi",
              "agrippe": "agrippe", "entrave": "entrave", "inconscient": "inconscient", "epuisement": "epuisement_1",
              "malad": "malade"}
ACTIVE_WORDS = ("une action", "action bonus", "reaction", "charge", "pendant 1", "pendant 10", "une fois",
                "par jour", "jusqu'a la fin", "quand vous lancez", "si vous lancez")
CHOSEN_TYPE = re.compile(r"r[ée]sistance [àa] un type de d[ée]g[âa]ts", re.I)


_ABILITY = {"force": "Force", "dexterite": "Dextérité", "constitution": "Constitution",
            "intelligence": "Intelligence", "sagesse": "Sagesse", "charisme": "Charisme"}
SKILLS = ["Acrobaties", "Arcanes", "Athlétisme", "Discrétion", "Dressage", "Escamotage", "Histoire", "Intimidation",
          "Investigation", "Médecine", "Nature", "Perception", "Perspicacité", "Persuasion", "Religion", "Représentation",
          "Survie", "Tromperie"]


# v53 : cibles d'avantage / de désavantage d'un objet sur mesure (clé, libellé)
ADVANTAGE_TARGETS = ([("comp:" + s, s) for s in SKILLS] + [("js:" + a, "JS de " + a) for a in _ABILITY.values()]
                     + [("init", "Initiative")])


def advantage_mech(adv: list, dis: list) -> dict:
    """Modificateur (format mechanics) des avantages / désavantages choisis pour un objet sur mesure. Avantage et
    désavantage sur le même jet s'annulent (dont le désavantage de Discrétion d'une armure lourde)."""
    m: dict = {}
    for keys, val in ((adv or [], "avantage"), (dis or [], "désavantage")):
        for k in keys:
            if k.startswith("comp:"):
                m.setdefault("competences", {}).setdefault(k[5:], []).append(val)
            elif k.startswith("js:"):
                m.setdefault("js", {}).setdefault(k[3:], []).append(val)
            elif k == "init":
                m.setdefault("initiative", []).append(val)
    return m


def damage_types_in(text: str) -> list[str]:
    n = norm(text)
    return [t for t in DAMAGE_TYPES if re.search(r"\b{}s?\b".format(norm(t)), n)]


def needs_resistance_choice(item: dict) -> bool:
    return bool(CHOSEN_TYPE.search((item or {}).get("description", "") or ""))


class ItemPassivesMixin:
    """Mélangé à Engine."""

    def item_passive_mech(self, entry: dict, item: dict) -> dict:
        """Modificateur (format mechanics) des effets passifs lus pour cet objet ; {} s'il n'y en a pas."""
        m: dict = {}
        res, imm, cond = [], [], []
        if item.get("perso"):                            # objet sur mesure : champs explicites
            res = list(item.get("resistances") or [])
            imm = list(item.get("immunites") or [])
            cond = list(item.get("immunites_etats") or [])
            m.update(advantage_mech(item.get("avantages"), item.get("desavantages")))   # v53
            if item.get("vitesse_bonus"):                # v53 : Armure de propulsion arcanique (infusion)
                m["vitesse_bonus"] = float(item["vitesse_bonus"])
            if item.get("js_bonus"):
                m.setdefault("js", {})["*"] = [int(item["js_bonus"])]
        else:
            desc = item.get("description", "") or ""
            if re.search(r"le (?:md|mj) choisit|determine de maniere aleatoire|determine aleatoirement", norm(desc)):
                desc = ""
            from .tattoos import tattoo_key
            if tattoo_key(item.get("nom", "")):          # v53 : tatouage — règles exactes dans core/tattoos.py
                desc = ""                                 # objet à variantes (plan, type…) : seul le choix compte
            conditional_block = False
            for sentence in re.split(r"(?<=[.!?:])\s+", desc):
                n = norm(sentence)
                if n.startswith("si ") and n.rstrip().endswith(":"):
                    conditional_block = True              # « Si vous êtes un nain lié à la hache : • … » : non passif
                    continue
                if conditional_block and (n.lstrip().startswith("•") or n.startswith("de plus")):
                    continue
                conditional_block = False
                if any(w in n for w in ACTIVE_WORDS) or not re.search(r"\bvous\b", n) or "ignore" in n:
                    continue
                for mt in re.finditer(r"resistan\w* aux degats (.{0,80}?)(?:tant que|lorsque|quand|,|\.|$)", n):
                    res += damage_types_in(mt.group(1))
                if "immunise" in n:
                    after = n[n.index("immunise"):]           # seulement ce qui suit « immunisé »
                    for mt in re.finditer(r"(?:aux|contre les|a l'egard des) degats (.{0,60}?)(?:tant que|lorsque|"
                                          r",|\.|$)", after):
                        if "sort" not in mt.group(1):
                            imm += damage_types_in(mt.group(1))
                if "immunise" in n and "etat" in n:
                    cond += [v for k, v in CONDITIONS.items() if re.search(r"etats? (?:\w+ )?{}".format(k), n)]
                if not item.get("js"):
                    mt = re.search(r"bonus de \+(\d) (?:aux jets de caracteristique et )?aux jets de sauvegarde", n)
                    if mt:
                        m["js"] = {"*": [int(mt.group(1))]}
                        if "jets de caracteristique" in n:
                            m["tests"] = {"*": [int(mt.group(1))]}
            if not re.match(r"potion|parchemin", norm(item.get("type", "") or "")):
                self._item_advantages(desc, m)            # v53 : Armure du zéphyr, Bouclier sentinelle…
            if needs_resistance_choice(item) and entry.get("resistance_choisie"):
                res.append(entry["resistance_choisie"])
        if res:
            m["resistances"] = list(dict.fromkeys(res))
        if imm:
            m["immunites"] = list(dict.fromkeys(imm))
        if cond:
            m["etats_immunises"] = list(dict.fromkeys(cond))
        return m

    def _item_advantages(self, desc: str, m: dict) -> None:
        """v53 — avantages passifs d'un objet porté : « l'avantage aux jets de Dextérité (Acrobaties) et aux jets
        de sauvegarde de Dextérité » (Armure du zéphyr), « à vos jets d'initiative » (Bouclier sentinelle).
        Un avantage restreint (« basés sur la vue », « pour vous cacher », « contre les sorts »…) n'est pas
        appliqué d'office : il reste lisible dans la description de l'objet."""
        from .mechanics import ADV
        skills = {norm(s): s for s in (getattr(self.db, "skill_names", None) or SKILLS)}
        skills.setdefault("intuition", skills.get("perspicacite", "Perspicacité"))   # nom 2024 / autres traductions
        for sentence in re.split(r"(?<=[.!?])\s+|\n", desc):
            n = re.split(r",? et vous pouvez ", norm(sentence))[0]   # Voile kagonesti : « …, et vous pouvez … »
            mt = re.search(r"(?<!des)avantage (?:a|aux|sur) ", n)
            if not mt or not re.search(r"\bvous\b", n[:mt.start()]) or any(w in n for w in ACTIVE_WORDS) or \
                    re.search(r"tant que vous (?:beneficiez|etes sous|jouez)|si vous|lorsque vous (?:lancez|utilisez)",
                              n[:mt.start()]):
                continue
            cond = r"^\s*(?:qui|bases|basees|lies|liees|effectues|faits|pour|lorsque|quand|contre|dirige|" \
                   r"concernant|visant|avec)"
            for part in re.split(r",| et (?=(?:a |aux )?(?:vos |tous les |les )?(?:jets|tests))", n[mt.end():]):
                found = list(re.finditer(r"(?:force|dexterite|constitution|intelligence|sagesse|charisme) "
                                         r"\(([^)]+)\)", part))
                if found:
                    if not re.search(cond, part[found[-1].end():]):
                        for f in found:
                            name = skills.get(norm(f.group(1)), "")
                            if name:
                                m.setdefault("competences", {})[name] = [ADV]
                    continue
                sv = re.search(r"jets? de sauvegarde (?:de |d')(force|dexterite|constitution|intelligence|sagesse|"
                               r"charisme)(.*)$", part)
                if sv and not re.search(cond, sv.group(2)):
                    m.setdefault("js", {})[_ABILITY[sv.group(1)]] = [ADV]
                    continue
                if re.search(r"jets? d'initiative", part):
                    m["initiative"] = [ADV]

    def item_condition_immunities(self) -> dict[str, str]:
        """États contre lesquels un objet porté (et harmonisé si besoin) vous immunise : {clé: source}."""
        out = {}
        for entry in self.ch.objets_magiques:
            item = self.magic_item(entry.get("nom", "")) or {}
            if not entry.get("equipe", True) or entry.get("detruit") or (item.get("lien") and
                                                                          not entry.get("harmonise")):
                continue
            for key in self.item_passive_mech(entry, item).get("etats_immunises", []):
                out.setdefault(key, "Objet : " + self.magic_display_name(entry))
        for label, m in self.passive_modifiers() if hasattr(self, "passive_modifiers") else []:
            for key in m.get("etats_immunises", []):     # v53 : Amulette de santé (maladies)
                out.setdefault(key, label)
        return out
