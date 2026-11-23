"""
Tatouages magiques (v53, Le Chaudron de Tasha) — règles exactes, mélangées à Engine.

Un tatouage occupe une des quatre cases « tatouage » sous le mannequin ; s'il exige l'harmonisation, l'équiper
l'harmonise (il n'existe que tant que vous y êtes harmonisé). Effets :
  - Barrière : CA sans armure selon la rareté choisie (12 + Dex ; 15 + Dex max 2 ; 18), bouclier permis ;
  - Absorption : résistance au type de sa couleur (choix enregistré) + réaction « Absorption » 1 fois par aube ;
  - Griffe occulte : +1 attaque et dégâts à mains nues (magiques) ; « Maillet occulte » (action bonus, 1 / aube) :
    +1d6 force au corps à corps et allonge 4,50 m pendant 1 minute ;
  - Fureur sanglante : 10 charges — +4d6 nécrotiques au toucher (et soins) ; riposte en réaction ;
  - Préhension : action, JS de Force DD 14, 3d6 force et empoigné ;
  - Foulée spectrale : 3 charges, action bonus : forme immatérielle jusqu'à la fin du prochain tour ;
  - Enlumineur : écriture invisible (action, 1 / aube) ; Mascarade : Déguisement (action, 1 / aube, DD 13) ;
  - Gisombre : vision dans le noir 18 m, avantage en Discrétion, réaction « Défense de l'ombre » (1 / jour) ;
  - Fontaine de vie : résistance nécrotique ; à 0 PV, vous restez à 1 PV (1 / aube, automatique) ;
  - Sortilège : un sort (niveau 0 à 5) choisi à l'ajout ; lancé avec le DD et le bonus du tatouage, puis il
    disparaît.
Les utilisations « 1 fois par aube » sont des charges (1) regagnées au repos long, comme les autres objets.
"""
from __future__ import annotations

from typing import Optional

from .rules import norm

BARRIER = {"peu commun": (12, None), "rare": (15, 2), "tres rare": (18, 0)}     # (base, Dex max : None = libre)
SPELL_TATTOO = {0: ("commun", 3, 13, 5), 1: ("commun", 3, 13, 5), 2: ("peu commun", 3, 13, 5),
                3: ("peu commun", 4, 15, 7), 4: ("rare", 4, 15, 7), 5: ("rare", 5, 17, 9)}   # rareté, mod, DD, attaque


def tattoo_key(name: str) -> str:
    n = norm(name or "")
    for key in ("absorption", "barriere", "fureur sanglante", "prehension", "griffe occulte", "foulee spectrale",
                "enlumineur", "fontaine de vie", "mascarade", "gisombre", "sortilege"):
        if n.startswith("tatouage") and key in n:
            return key
    return ""


def _power(key, nom, kind, desc, charges=0, cout=0, **extra) -> dict:
    return dict({"cle": key, "nom": nom, "type": kind, "description": desc, "charges": charges, "cout": cout}, **extra)


POWERS = {
    "absorption": [_power("absorption", "Absorption des dégâts", "Réaction",
                          "Quand vous subissez des dégâts du type du tatouage : immunité contre ces dégâts et vous "
                          "récupérez la moitié des dégâts que vous auriez subis. 1 fois par aube.", 1, 1)],
    "fureur sanglante": [_power("riposte", "Riposte sanglante", "Réaction",
                                "Quand une créature que vous voyez vous inflige des dégâts : 1 charge, attaque de "
                                "corps à corps contre elle avec avantage.", 10, 1, attaque=True)],
    "prehension": [_power("vrilles", "Vrilles agrippantes", "Action",
                          "Une créature visible à 4,50 m ou moins : JS de Force DD 14, sinon 3d6 dégâts de force et "
                          "empoignée (évasion : Athlétisme ou Acrobaties DD 14, par une action).",
                          degats="3d6", type_degats="force", dd="Force DD 14")],
    "griffe occulte": [_power("maillet", "Maillet occulte", "Action bonus",
                              "Pendant 1 minute : vos attaques de corps à corps (arme ou mains nues) atteignent une "
                              "cible jusqu'à 4,50 m et infligent 1d6 dégâts de force de plus. 1 fois par aube.", 1, 1,
                              effet="maillet_occulte")],
    "foulee spectrale": [_power("fantome", "Forme fantomatique", "Action bonus",
                                "Jusqu'à la fin de votre prochain tour : résistance aux dégâts contondants, perforants "
                                "et tranchants non magiques, impossible à empoigner ou entraver, traversée des "
                                "créatures et objets (terrain difficile ; 1d10 force si vous y finissez votre tour).",
                                3, 1, effet="forme_fantomatique")],
    "enlumineur": [_power("ecriture", "Écriture invisible", "Action",
                          "Touchez un écrit d'une page au plus et nommez une créature : il devient invisible pour "
                          "tous sauf vous et elle pendant 24 heures. 1 fois par aube.", 1, 1)],
    "mascarade": [_power("encre", "Encre fluide", "Action bonus",
                         "Changez la couleur, le motif et l'emplacement du tatouage sur votre peau."),
                  _power("deguisement", "Déguisement", "Action",
                         "Lance le sort Déguisement (DD 13 pour percer le déguisement). 1 fois par aube.", 1, 1,
                         sort="Déguisement")],
    "gisombre": [_power("ombre", "Défense de l'ombre", "Réaction",
                        "Quand vous subissez des dégâts : vous devenez immatériel un instant, les dégâts sont réduits "
                        "de moitié. 1 fois jusqu'au prochain coucher du soleil.", 1, 1)],
}


class TattoosMixin:
    """Mélangé à Engine."""

    def active_tattoos(self) -> list[tuple[int, dict, str]]:
        """[(indice, entrée, clé)] des tatouages actifs (équipés, harmonisés s'ils l'exigent)."""
        out = []
        for i, e in enumerate(self.ch.objets_magiques):
            key = tattoo_key(e.get("nom", ""))
            if not key or not e.get("equipe") or e.get("detruit"):
                continue
            if (self.magic_item(e["nom"]) or {}).get("lien") and not e.get("harmonise"):
                continue
            out.append((i, e, key))
        return out

    def _tattoo(self, key: str) -> Optional[tuple[int, dict]]:
        return next(((i, e) for i, e, k in self.active_tattoos() if k == key), None)

    # ------------------------------------------------------------------ passifs
    def tattoo_unarmored(self) -> dict:
        """Option de CA sans armure du Tatouage barrière (rareté choisie, « peu commun » par défaut)."""
        hit = self._tattoo("barriere")
        if hit is None:
            return {}
        tier = norm(hit[1].get("palier") or "peu commun")
        base, dex_max = BARRIER.get(tier, BARRIER["peu commun"])
        dex = self.mod("Dextérité")
        terms = [(str(base), base)]
        if dex_max is None:
            terms.append(("Dex", dex))
        elif dex_max:
            terms.append(("Dex (max {})".format(dex_max), min(dex, dex_max)))
        return {"Tatouage barrière ({})".format(hit[1].get("palier") or "peu commun"): terms}

    def tattoo_unarmed_bonus(self) -> int:
        return 1 if self._tattoo("griffe occulte") else 0

    def tattoo_mech(self, key: str) -> dict:
        """Modificateur (format mechanics) des passifs non lus dans le texte."""
        from . import mechanics as M
        if key == "gisombre":
            return {"competences": {"Discrétion": [M.ADV]}}
        if key == "fontaine de vie":
            return {"resistances": ["nécrotique"]}
        return {}

    def tattoo_darkvision(self) -> float:
        return 18.0 if self._tattoo("gisombre") else 0.0

    def life_well_saves(self) -> str:
        """Fontaine de vie : à 0 PV, vous restez à 1 PV (1 fois par aube). Renvoie le message, « » sinon."""
        hit = self._tattoo("fontaine de vie")
        if hit is None or int(hit[1].get("charges_utilisees", 0)) >= 1:
            return ""
        hit[1]["charges_utilisees"] = 1
        self.ch.pv_actuels = 1
        return "Tatouage de fontaine de vie : vous restez debout à 1 PV (une fois par aube)"

    # ------------------------------------------------------------------ tuiles
    def tattoo_powers(self, i: int, e: dict, label: str, desc: str) -> Optional[list[dict]]:
        """Capacités exactes d'un tatouage (None : pas un tatouage géré -> lecture générique du texte)."""
        key = tattoo_key(e.get("nom", ""))
        if not key:
            return None
        uid = e.get("uid") or "i{}".format(i)
        base = {"entree": i, "objet": label, "multi": False, "elements": "", "destruction": False}
        out = []
        if key == "sortilege":
            sp = self.db.find_spell(e.get("sort_tatouage", "")) if e.get("sort_tatouage") else None
            if sp:
                lvl = int(sp.get("niveau") or 0)
                _r, mod, dd, atk = SPELL_TATTOO.get(lvl, SPELL_TATTOO[5])
                out.append(dict(base, id="objet:{}:sort:{}".format(uid, sp["nom"]), nom="{} — {}".format(
                    sp["nom"], label), type=self._spell_economy_label(sp), sort=sp["nom"], niveau=lvl, charges=0,
                    cout=0, consomme=True, stats={"dd": dd, "attaque": atk, "mod": mod},
                    description="Lance {} (DD {}, attaque +{}) ; le tatouage disparaît ensuite.".format(
                        sp["nom"], dd, atk)))
            return out
        for p in POWERS.get(key, []):
            charges = p["charges"]
            out.append(dict(base, id="objet:{}:{}".format(uid, p["cle"]), nom="{} — {}".format(p["nom"], label),
                            type=p["type"], sort=p.get("sort", ""), niveau=0, charges=charges, cout=p["cout"],
                            description=p["description"], effet=p.get("effet", ""), degats=p.get("degats", ""),
                            type_degats=p.get("type_degats", ""), dd=p.get("dd", ""), attaque=p.get("attaque", False)))
        return out

    def tattoo_on_hit(self, slot: Optional[dict]) -> list[dict]:
        """Fureur sanglante : +4d6 nécrotiques au toucher d'une attaque d'arme (1 charge)."""
        hit = self._tattoo("fureur sanglante")
        if hit is None or not slot or self.is_natural_attack(slot.get("nom", "")):
            return []
        i, e = hit
        if self.item_charges_left(e, 10) < 1:
            return []
        return [{"key": "tatouage:fureur", "label": "Fureur sanglante (1 charge : vous regagnez les PV des dégâts "
                 "nécrotiques)", "dice": "4d6 nécrotiques", "cout": "1 charge ({} / 10)".format(
                     self.item_charges_left(e, 10)), "action": "", "niveau": 0, "charge_objet": i,
                 "soin_egal": True}]

    @staticmethod
    def tattoo_choice(name: str) -> str:
        """Choix demandé à l'ajout : « palier » (Barrière : rareté), « sort » (Sortilège) ou « »."""
        return {"barriere": "palier", "sortilege": "sort"}.get(tattoo_key(name), "")

    def spell_tattoo_options(self) -> list[str]:
        """Sorts de niveau 0 à 5 de l'édition de la fiche (Tatouage sortilège)."""
        want = self.sheet_edition == 2024
        return sorted((s for s, sp in self.db.spells.items() if int(sp.get("niveau") or 0) <= 5
                       and want == ("(2024)" in s or sp.get("edition") == 2024)), key=norm)

    def set_tattoo_choice(self, index: int, value: str) -> None:
        """Rareté choisie (Tatouage barrière, objets à bonus selon la rareté) ou sort du Tatouage sortilège."""
        e = self.ch.objets_magiques[index]
        kind = self.tattoo_choice(e.get("nom", "")) or (
            "palier" if self.rarity_choice_needed(self.magic_item(e.get("nom", "")) or {}) else "")
        if kind == "palier" and norm(value) in BARRIER:
            e["palier"] = value
        elif kind == "sort" and self.db.find_spell(value):
            e["sort_tatouage"] = value

    def spend_item_charge(self, index: int, total: int, n: int = 1) -> bool:
        if not 0 <= index < len(self.ch.objets_magiques):
            return False
        e = self.ch.objets_magiques[index]
        if self.item_charges_left(e, total) < n:
            return False
        e["charges_utilisees"] = int(e.get("charges_utilisees", 0)) + n
        return True


# ---------------------------------------------------------------------------------------------- bonus de sorts
import re as _re  # noqa: E402

RARITY_TIER = {"peu commun": 1, "rare": 2, "tres rare": 3}
CLASS_WORDS = {"magicien": "Magicien", "artificier": "Artificier", "ensorceleur": "Ensorceleur", "druide": "Druide",
               "rodeur": "Rôdeur", "barde": "Barde", "clerc": "Clerc", "paladin": "Paladin", "occultiste": "Occultiste"}


def spell_bonus_rule(item: dict) -> Optional[dict]:
    """Bonus de sorts d'un objet : {attaque, dd (nombre ou « rarete »), classes} ; None s'il n'en donne pas.
    « bonus de +2 aux jets d'attaque des sorts » ; « bonus aux jets d'attaque de sort et aux DD de sauvegarde de vos
    sorts de magicien. Le bonus est déterminé par la rareté » (+1 peu commun, +2 rare, +3 très rare)."""
    n = norm((item or {}).get("description", "") or "")
    if "utilisant votre dd" in n or "lanceur d'origine" in n:
        return None
    atk = dd = None
    m = _re.search(r"bonus de \+(\d) aux jets d'attaque (?:de|des) sorts?", n)
    if m:
        atk = int(m.group(1))
    m = _re.search(r"bonus de \+(\d) au dd de sauvegarde de vos sorts", n)
    if m:
        dd = int(m.group(1))
    m = _re.search(r"bonus aux jets d'attaque (?:de|des) sorts?( et aux dd de sauvegarde de vos sorts)?([^.]*)\.\s*le "
                   r"bonus est determine par la rarete", n)
    if m:
        atk = "rarete"
        if m.group(1):
            dd = "rarete"
    if atk is None and dd is None:
        return None
    tail = n[n.find("sorts"):][:120] if "sorts" in n else ""
    m = _re.search(r"(?:vos|des) sorts? (d'|de )([a-z' ]+?)(?:\.|,| tant| et aux|$)", n)
    classes = [v for k, v in CLASS_WORDS.items() if m and k in m.group(0)]
    del tail
    return {"attaque": atk, "dd": dd, "classes": classes}


def _tier(item: dict, entry: dict) -> int:
    m = _re.search(r"\+(\d)\s*$", item.get("nom", "").strip())
    if m:
        return int(m.group(1))
    return RARITY_TIER.get(norm(entry.get("palier") or item.get("rarete", "")), 1)


class SpellItemBonusMixin:
    """Mélangé à Engine : bonus d'attaque et de DD des sorts donnés par les objets tenus ou portés (v53)."""

    def item_spell_bonuses(self, class_name: str = "") -> dict:
        """{attaque, dd, sources} pour les sorts de `class_name` (« » : toute classe)."""
        atk = dd = 0
        src = []
        for e in self.ch.objets_magiques:
            item = self.magic_item(e.get("nom", "")) or {}
            if not e.get("equipe") or e.get("detruit") or (item.get("lien") and not e.get("harmonise")):
                continue
            rule = spell_bonus_rule(item)
            if not rule or (rule["classes"] and class_name and class_name not in rule["classes"]):
                continue
            tier = _tier(item, e)
            a = tier if rule["attaque"] == "rarete" else int(rule["attaque"] or 0)
            d = tier if rule["dd"] == "rarete" else int(rule["dd"] or 0)
            if a or d:
                atk, dd = atk + a, dd + d
                src.append(self.magic_display_name(e))
        return {"attaque": atk, "dd": dd, "sources": src}

    @staticmethod
    def rarity_choice_needed(item: dict) -> bool:
        """Objet à rareté variable dont l'effet dépend de la rareté (bonus de sorts, Tatouage barrière)."""
        return norm(item.get("rarete", "")) == "variable" and (
            "determine par la rarete" in norm(item.get("description", "")) or tattoo_key(item.get("nom", "")) == "barriere")
