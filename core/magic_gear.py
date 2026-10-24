"""
Armes, armures et boucliers magiques (v45) — logique pure.

Un objet magique de type « Arme » ou « Armure » (Arme +2, Armure +1, Bouclier +3, Bouclier expressif, Armure de
mithral…) est lié à un objet de BASE choisi à l'ajout (Épée à deux mains, Harnois, Bouclier…) :
    entrée de ch.objets_magiques : {"nom": "Arme +2", "base": "Épée à deux mains", "bonus": 2, "uid": "mg3",
                                    "equipe": bool, "harmonise": bool}
    nom affiché : « Épée à deux mains +2 » (objets +N) ou « Bouclier expressif (Bouclier) » (objets nommés).

Équiper l'objet le place dans la case du mannequin correspondante (main principale / secondaire / distance /
armure) ; la case garde le nom de base (statistiques du catalogue) et reçoit :
    bonus  -> +X au jet de toucher ET aux dégâts (arme), +X à la CA (armure : armure["bonus"], bouclier :
              armure["bonus_bouclier"]) — seulement si l'objet est harmonisé quand il l'exige ;
    objet  -> uid de l'objet (lien inventaire <-> case) ; affichage -> nom affiché.
Déséquiper / remplacer la case rompt le lien ; le bonus disparaît aussitôt.

Capacités activables (v45) : tout objet magique actif dont la description prévoit une action, une action bonus ou
une réaction, des charges ou un sort à lancer devient une tuile de l'onglet Combat (groupe « Objets magiques »,
origine « [Objet Magique : Nom] »). Les charges se décomptent ; elles se rechargent au repos long (« à l'aube »).
"""
from __future__ import annotations

import re
from typing import Optional

from .rules import norm

GEAR_TIER = re.compile(r"^(Arme|Armure|Bouclier|Munition) \+(\d)$")
CATEGORY_WORDS = {"legere": "légère", "intermediaire": "intermédiaire", "lourde": "lourde"}
ECONOMY_PATTERNS = [
    ("Réaction", re.compile(r"\br[ée]action\b", re.I)),
    ("Action bonus", re.compile(r"action bonus", re.I)),
    ("Action", re.compile(r"(par|utiliser|d[ée]penser|prendre)\s+(une|votre)\s+action\b(?!\s*bonus)|une action pour|"
                          r"action pour (prononcer|lancer|activer|utiliser)|en utilisant une action", re.I)),
]
CHARGES = re.compile(r"(\d+)\s+charges?\b", re.I)
NO_TILE_TYPES = ("Potion", "Parchemin")


SYNONYMS = {"epee": ("epee", "rapiere", "cimeterre"), "hache": ("hache", "hachette")}
GENERAL = ("toute", "toutes", "legere intermediaire ou lourde", "")


def _apos(text: str) -> str:
    return (text or "").replace("’", "'")


def _clean(prec: str) -> str:
    """« toute épée qui inflige des dégâts tranchants » -> « epee »."""
    p = _apos(prec)
    p = re.split(r"\s+(?:qui|mais|infligeant|sauf)\b", p)[0]
    p = re.sub(r"^(?:toute|toutes|tout|n'importe quelle)\s+", "", p.strip())
    return "" if p in ("toutes", "toute", "arme", "armes") else p


def _match_names(pool: list[str], prec: str) -> list[str]:
    """Noms exacts d'abord (« épée longue »), sinon familles (« épée » -> épées, rapière, cimeterre)."""
    if not prec:
        return []
    out: list[str] = []
    for phrase in re.split(r"\s+(?:et|ou)\s+(?:toute\s+|tout\s+)?|,\s*", prec):
        phrase = phrase.strip()
        if not phrase:
            continue
        exact = [n for n in pool if _apos(norm(n)) == phrase]
        if exact:
            out += exact
            continue
        inside = [n for n in pool if re.search(r"\b" + re.escape(phrase) + r"$", _apos(norm(n)))]
        if inside:                                        # « cuir clouté » -> « Armure de cuir clouté »
            out += inside
            continue
        word = phrase.split(" ")[0].rstrip("s")
        keys = SYNONYMS.get(word, (word,))
        out += [n for n in pool if any(_apos(norm(n)).startswith(k) for k in keys)]
    return list(dict.fromkeys(out))


class MagicGearMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ nature de l'objet
    def magic_gear_kind(self, name_or_item) -> str:
        """« arme », « armure », « bouclier » ou « » (objet non lié à une arme / armure de base)."""
        item = self.magic_item(name_or_item) if isinstance(name_or_item, str) else name_or_item
        if not item:
            return ""
        kind, prec, n = norm(item.get("type", "")), norm(item.get("precision", "")), norm(item.get("nom", ""))
        if kind == "arme":
            if "munition" in prec or n.startswith("munition") or self.is_ammo_item(item):
                return ""
            return "arme"
        if kind == "armure":
            return "bouclier" if ("bouclier" in prec or n.startswith("bouclier")) else "armure"
        return ""

    def magic_gear_tier(self, item: dict, entry: Optional[dict] = None) -> int:
        """Bonus +X de l'objet : palier du nom (« Arme +2 »), bonus choisi (+1, +2 ou +3) ou bonus de CA indiqué."""
        m = GEAR_TIER.match(item.get("nom", ""))
        if m:
            return int(m.group(2))
        if item.get("variable") and entry:
            return int(entry.get("bonus") or 1)
        if self.magic_gear_kind(item) in ("armure", "bouclier"):
            return int(item.get("ca") or 0)
        return 0

    def magic_base_options(self, name: str) -> list[str]:
        """Objets de base compatibles avec la précision du catalogue (« toute épée », « harnois », « intermédiaire ou
        lourde mais pas de peau »…) ; liste complète si la précision est générale ou non reconnue."""
        item = self.magic_item(name)
        kind = self.magic_gear_kind(item)
        if kind == "bouclier":
            return sorted(getattr(self.db, "shields", {}) or {"Bouclier": {}}, key=norm) or ["Bouclier"]
        prec = _clean(norm((item or {}).get("precision", "")))
        if kind == "arme":
            pool = [n for n in self.db.weapons if n != "Mains nues"]
            hits = _match_names(pool, prec)
            if "tranchant" in norm((item or {}).get("precision", "")):
                hits = [n for n in hits if "tranch" in norm(self.db.weapons[n].get("type_degats", ""))]
            return sorted(hits or pool, key=norm)
        if kind == "armure":
            pool = [n for n in self.db.armors if n != "Aucune armure"]
            cats = {label for w, label in CATEGORY_WORDS.items() if w in prec}
            hits = [n for n in pool if self.db.armors[n].get("categorie") in cats] if cats else _match_names(pool, prec)
            excl = re.search(r"(?:sauf|pas de|pas d')\s*([a-z]+)", norm((item or {}).get("precision", "")))
            if excl:
                hits = [n for n in (hits or pool) if excl.group(1).rstrip("x") not in norm(n)]
            return sorted(hits or pool, key=norm)
        return []

    @staticmethod
    def _gear_display(item_name: str, base: str, tier: int) -> str:
        if GEAR_TIER.match(item_name) or "+1, +2 ou +3" in item_name:
            return "{} +{}".format(base, tier)
        return "{} ({})".format(item_name, base)

    def magic_display_name(self, entry: dict) -> str:
        """Nom affiché d'une entrée d'objet magique : « Épée à deux mains +2 », « Bouclier +2 »…"""
        name = entry.get("nom", "")
        if entry.get("base"):
            item = self.magic_item(name) or {"nom": name}
            return self._gear_display(name, entry["base"], self.magic_gear_tier(item, entry))
        return name.replace("+1, +2 ou +3", "+{}".format(entry["bonus"])) if entry.get("bonus") else name

    # ------------------------------------------------------------------ ajout
    def _new_uid(self) -> str:
        nums = [int(e["uid"][2:]) for e in self.ch.objets_magiques if str(e.get("uid", "")).startswith("mg")
                and e["uid"][2:].isdigit()]
        return "mg{}".format(max(nums, default=0) + 1)

    def add_magic_gear(self, name: str, base: str, bonus: int = 0) -> str:
        """Ajoute une arme / armure / un bouclier magique sur l'objet de base choisi. Renvoie le nom affiché."""
        item = self.magic_item(name)
        if not item or not self.magic_gear_kind(item) or base not in self.magic_base_options(name):
            return ""
        entry = {"nom": name, "base": base, "bonus": max(1, min(3, bonus)) if item.get("variable") else 0,
                 "uid": self._new_uid(), "equipe": False, "harmonise": False}
        self.ch.objets_magiques.append(entry)
        return self.magic_display_name(entry)

    # ------------------------------------------------------------------ équipement
    def gear_entry(self, uid: str) -> Optional[dict]:
        return next((e for e in self.ch.objets_magiques if e.get("uid") == uid and e.get("base")), None)

    def gear_effective_bonus(self, entry: dict) -> int:
        """Bonus appliqué : 0 si l'objet exige une harmonisation qui n'est pas faite."""
        item = self.magic_item(entry.get("nom", "")) or {}
        if item.get("lien") and not entry.get("harmonise"):
            return 0
        return self.magic_gear_tier(item, entry)

    def gear_default_slot(self, entry: dict) -> str:
        kind = self.magic_gear_kind(entry.get("nom", ""))
        if kind == "armure":
            return "armure"
        if kind == "bouclier":
            return "main_secondaire"
        w = self.db.weapons.get(entry.get("base", ""), {})
        return "distance" if w.get("type") == "distance" else "main_principale"

    def equip_magic_gear(self, idx: int, slot: str = "") -> str:
        """Place l'arme / l'armure magique n° idx dans sa case ; bonus appliqué aussitôt. Renvoie le message."""
        if not 0 <= idx < len(self.ch.objets_magiques):
            return ""
        entry = self.ch.objets_magiques[idx]
        if not entry.get("base"):
            return ""
        slot = slot or self.gear_default_slot(entry)
        msg = self.equip_slot(slot, {"nom": entry["base"], "kind": "objet"})
        if msg.startswith("Main secondaire indisponible"):
            return msg
        self._bind_slot(slot, entry)
        self.sync_magic_gear()
        return msg.replace(entry["base"], self.magic_display_name(entry), 1)

    def unequip_magic_gear(self, idx: int) -> None:
        if not 0 <= idx < len(self.ch.objets_magiques):
            return
        uid = self.ch.objets_magiques[idx].get("uid")
        for slot, holder in self._gear_slots():
            if holder.get(self._uid_key(slot)) == uid:
                self.unequip_slot(slot)
        self.sync_magic_gear()

    @staticmethod
    def _uid_key(slot: str) -> str:
        return "bouclier_objet" if slot == "main_secondaire_bouclier" else "objet"

    def _gear_slots(self) -> list[tuple[str, dict]]:
        """(case, dictionnaire porteur) : armes, armure, bouclier (clés propres au bouclier)."""
        ch = self.ch
        out = [("main_principale", ch.armes_cac[0])]
        if len(ch.armes_cac) > 1:
            out.append(("main_secondaire", ch.armes_cac[1]))
        out.append(("distance", ch.armes_distance[0]))
        out.append(("armure", ch.armure))
        out.append(("main_secondaire_bouclier", ch.armure))
        return out

    def _bind_slot(self, slot: str, entry: dict) -> None:
        ch = self.ch
        bonus, label = self.gear_effective_bonus(entry), self.magic_display_name(entry)
        if self.magic_gear_kind(entry["nom"]) == "bouclier":
            ch.armure.update(bouclier=True, bouclier_nom=entry["base"], bonus_bouclier=bonus,
                             bouclier_objet=entry["uid"], bouclier_affichage=label)
        elif slot == "armure":
            ch.armure.update(nom=entry["base"], bonus=bonus, objet=entry["uid"], affichage=label)
        else:
            holder = {"main_principale": ch.armes_cac[0], "distance": ch.armes_distance[0]}.get(slot)
            if holder is None and slot == "main_secondaire" and len(ch.armes_cac) > 1:
                holder = ch.armes_cac[1]
            if holder is not None:
                holder.update(nom=entry["base"], bonus=bonus, objet=entry["uid"], affichage=label)

    def sync_magic_gear(self) -> None:
        """Cohérence cases <-> objets : lien rompu si l'objet a disparu ou si la case a changé d'objet ; bonus et
        nom affiché recalculés (harmonisation) ; « équipé » des objets liés = présent dans une case."""
        ch = self.ch
        for e in ch.objets_magiques:                      # anciennes sauvegardes : uid manquant
            if e.get("base") and not e.get("uid"):
                e["uid"] = self._new_uid()
        worn: dict[str, str] = {}
        for slot, holder in self._gear_slots():
            key = self._uid_key(slot)
            uid = holder.get(key)
            if not uid:
                continue
            entry = self.gear_entry(uid)
            base_key = "bouclier_nom" if key == "bouclier_objet" else "nom"
            still = entry is not None and holder.get(base_key) == entry["base"] and \
                (key != "bouclier_objet" or holder.get("bouclier"))
            if not still:
                holder.pop(key, None)
                if key == "bouclier_objet":
                    holder.pop("bouclier_affichage", None)
                    holder["bonus_bouclier"] = 0
                else:
                    holder.pop("affichage", None)
                    holder["bonus"] = 0
                continue
            bonus = self.gear_effective_bonus(entry)
            if key == "bouclier_objet":
                holder["bonus_bouclier"], holder["bouclier_affichage"] = bonus, self.magic_display_name(entry)
            else:
                holder["bonus"], holder["affichage"] = bonus, self.magic_display_name(entry)
            worn[uid] = "main_secondaire" if key == "bouclier_objet" else slot
        for e in ch.objets_magiques:
            if e.get("base"):
                e["equipe"] = e.get("uid") in worn
                e["emplacement"] = worn.get(e.get("uid"), "")

    def release_magic_gear(self, idx: int) -> None:
        """Avant de retirer un objet lié : sa case est vidée."""
        if 0 <= idx < len(self.ch.objets_magiques) and self.ch.objets_magiques[idx].get("base"):
            self.unequip_magic_gear(idx)

    def gear_candidates(self, slot: str) -> list[dict]:
        """Armes / armures magiques de l'inventaire pour une case du mannequin (choix « magique_arme »)."""
        out = []
        for i, e in enumerate(self.ch.objets_magiques):
            if not e.get("base"):
                continue
            kind = self.magic_gear_kind(e["nom"])
            w = self.db.weapons.get(e["base"], {})
            ok = (slot == "armure" and kind == "armure") or (slot == "main_secondaire" and kind == "bouclier") or \
                (kind == "arme" and ((slot == "main_principale" and w.get("type") == "cac") or
                                     (slot == "distance" and w.get("type") == "distance") or
                                     (slot == "main_secondaire" and w.get("type") == "cac" and
                                      any(norm(p) == "legere" for p in w.get("proprietes", [])))))
            if ok:
                out.append({"nom": self.magic_display_name(e), "kind": "magique_arme", "index": i,
                            "equipe": e.get("emplacement") == slot or (slot == "main_secondaire" and
                                                                      e.get("emplacement") == "main_secondaire")})
        return out

    # ------------------------------------------------------------------ capacités activables (tuiles)
    def magic_item_powers(self) -> list[dict]:
        """Capacités activables des objets actifs : [{id, entree, objet, nom, type, sort, charges, cout, description}]."""
        out = []
        for i, e in enumerate(self.ch.objets_magiques):
            item = self.magic_item(e.get("nom", "")) or {}
            if not item or item.get("type") in NO_TILE_TYPES or self.is_ammo_item(item):
                continue
            if not e.get("equipe") or (item.get("lien") and not e.get("harmonise")):
                continue
            desc = item.get("description", "") or ""
            hits = [(m.start(), k) for k, rx in ECONOMY_PATTERNS for m in [rx.search(desc)] if m]
            economy = min(hits)[1] if hits else ""         # la première mention de l'économie d'action
            m = CHARGES.search(desc)
            charges = int(m.group(1)) if m else 0
            spells = self._item_spells(desc)
            label = self.magic_display_name(e)
            key = e.get("uid") or "i{}".format(i)
            if not (economy or charges or spells):
                continue
            kind = economy or "Action"
            if not spells:                                # objet à sorts : une tuile par sort suffit
                out.append({"id": "objet:{}:effet".format(key), "entree": i, "objet": label, "nom": "Utiliser — " + label,
                            "type": kind, "sort": "", "charges": charges, "cout": 1 if charges else 0,
                            "description": desc})
            for sp in spells:
                cost = self._spell_charge_cost(desc, sp["nom"]) if charges else 0
                out.append({"id": "objet:{}:sort:{}".format(key, sp["nom"]), "entree": i, "objet": label,
                            "nom": "{} — {}".format(sp["nom"], label), "type": kind if economy else
                            self._spell_economy_label(sp), "sort": sp["nom"], "niveau": int(sp.get("niveau") or 0),
                            "charges": charges, "cout": cost, "description": desc})
        return out

    def _item_spells(self, desc: str) -> list[dict]:
        """Sorts lancés par l'objet : « lancer le sort boule de feu », « l'un des sorts suivants : a (1 charge), b… »."""
        found, seen = [], set()

        def add(text: str) -> None:
            words = re.sub(r"\(.*?\)", "", text).strip(" .;:").split()
            for n in range(min(6, len(words)), 0, -1):       # plus long nom de sort reconnu
                cand = " ".join(words[:n])
                sp = self.db.find_spell(cand) if len(cand) >= 4 else None
                if sp and sp["nom"] not in seen:
                    seen.add(sp["nom"])
                    found.append(sp)
                    return
        for m in re.finditer(r"sorts? suivants?[^:]*:\s*([^.]+)", desc, re.I):
            for part in re.split(r",|\s+ou\s+|\s+et\s+", m.group(1)):
                add(part)
        for m in re.finditer(r"(?:le sort|lancer|lancez)\s+(?:le sort\s+)?([^,.;(]{3,60})", desc, re.I):
            add(m.group(1))
        return found[:8]

    @staticmethod
    def _spell_charge_cost(desc: str, spell: str) -> int:
        m = re.search(re.escape(spell) + r"[^.;,]{0,40}?\((\d+)\s+(?:de\s+)?charges?", desc, re.I)
        if m:
            return int(m.group(1))
        m = re.search(r"d[ée]penser?\s+(?:de\s+)?(\d+)\s+(?:ou plus\s+|ou plusieurs\s+)?(?:de\s+)?(?:ses\s+)?charges?",
                      desc, re.I)
        return int(m.group(1)) if m else 1

    @staticmethod
    def _spell_economy_label(spell: dict) -> str:
        t = norm(spell.get("temps", ""))
        return "Réaction" if "reaction" in t else "Action bonus" if "bonus" in t else "Action"

    def item_charges_left(self, entry: dict, total: int) -> int:
        return max(0, int(total) - int(entry.get("charges_utilisees", 0)))

    def use_item_power(self, power_id: str) -> dict:
        """Décompte les charges de la capacité ; renvoie {ok, message, sort, niveau, description, objet}."""
        p = next((x for x in self.magic_item_powers() if x["id"] == power_id), None)
        if p is None:
            return {"ok": False, "message": "Capacité d'objet indisponible."}
        entry = self.ch.objets_magiques[p["entree"]]
        if p["cout"]:
            left = self.item_charges_left(entry, p["charges"])
            if left < p["cout"]:
                return {"ok": False, "message": "{} : plus assez de charges ({} / {}).".format(
                    p["objet"], left, p["charges"])}
            entry["charges_utilisees"] = int(entry.get("charges_utilisees", 0)) + p["cout"]
        left = self.item_charges_left(entry, p["charges"]) if p["charges"] else None
        msg = "[Objet Magique : {}] {}{}.".format(p["objet"], p["sort"] or "capacité utilisée",
                                                  " — charges : {} / {}".format(left, p["charges"])
                                                  if left is not None else "")
        return {"ok": True, "message": msg, "sort": p["sort"], "niveau": p.get("niveau", 0),
                "description": p["description"], "objet": p["objet"]}

    def recharge_magic_items(self) -> None:
        for e in self.ch.objets_magiques:
            e.pop("charges_utilisees", None)
