"""
Infusions d'artificier (2014, Chaudron de Tasha) (v53) — logique pure mélangée à Engine.

Deux côtés, sans lien entre les fiches :
  - n'importe quelle fiche peut porter un objet infusé : menu « Infusions d'objet » (onglet Inventaire) — on choisit
    l'infusion, un objet NON magique de l'inventaire filtré par type (ou un « objet ordinaire non listé »), le nom
    et le niveau de l'artificier (+1 / +2 au niveau 10) ; l'objet devient un objet magique « infusé » (effets,
    harmonisation, charges = tuile En partie). Retirer l'infusion rend l'objet ordinaire, à la même place.
  - l'artificier choisit ses infusions connues (comme la Métamagie) et suit ses « infusions en cours » : ses objets
    infusés + celles posées chez un allié (saisies à la main), avec le maximum d'objets infusés (+2 Armurier 9).
Reproduction d'objet magique : le vrai objet du catalogue (tables par niveau). Serviteur homoncule : la créature
est ajoutée à la Ménagerie.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Optional

from .paths import get_resource_path
from .rules import norm

KNOWN = ((18, 12), (14, 10), (10, 8), (6, 6), (2, 4))
INFUSED = ((18, 6), (14, 5), (10, 4), (6, 3), (2, 2))
RESIST_TYPES = ["acide", "froid", "feu", "force", "foudre", "nécrotique", "poison", "psychique", "radiant", "tonnerre"]
# objets ordinaires proposés quand l'inventaire n'en contient pas (option « objet ordinaire non listé »)
BASE_SUGGESTIONS = {"bottes": ["Bottes"], "casque": ["Casque"], "anneau": ["Anneau"],
                    "focaliseur": ["Baguette", "Bâton", "Sceptre"], "gemme": ["Gemme (100 po)"],
                    "armure_robe": ["Robe"], "reproduction": []}


@lru_cache(maxsize=1)
def infusion_defs() -> dict[str, dict]:
    """{nom: {nom, description, niveau, objet, lien, cible, tables}} — liste du Chaudron de Tasha (data/editions)."""
    try:
        with open(get_resource_path("data/editions/classes_fr.json"), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    out: dict[str, dict] = {}
    for c in data.get("classes", []):
        src = c.get("source") or {}
        if c.get("nom") != "Artificier" or src.get("livre") != "TCE":
            continue
        for o in c.get("options", []):
            if "infusion" not in norm(o.get("categorie", "")):
                continue
            desc = o.get("description", "") or ""
            m = re.search(r"niveau (\d+)", norm(o.get("prerequis") or ""))
            objet = o.get("objet_requis") or (re.search(r"Objet : ([^\n]+)", desc).group(1)
                                               if re.search(r"Objet : ([^\n]+)", desc) else "")
            out[o["nom"]] = {"nom": o["nom"], "description": desc, "niveau": int(m.group(1)) if m else 0,
                             "objet": objet, "lien": "harmonisation" in norm(objet), "cible": _target(o["nom"], objet),
                             "tables": o.get("tables_objets_reproductibles") or {}}
    return out


def _target(name: str, objet: str) -> str:
    n = norm(objet)
    if norm(name).startswith("reproduction"):
        return "reproduction"
    if "munitions" in n:
        return "arme_munitions"
    if "lancer" in n:
        return "arme_lancer"
    if "arme courante" in n:
        return "arme"
    if "armure ou un bouclier" in n:
        return "armure_bouclier"
    if "un bouclier" in n:
        return "bouclier"
    if "robes" in n:
        return "armure_robe"
    if "armure" in n:
        return "armure"
    if "sceptre" in n or "baguette" in n:
        return "focaliseur"
    for key in ("bottes", "casque", "anneau", "gemme"):
        if key in n:
            return key
    return "autre"


def scaled_bonus(name: str, level: int) -> int:
    """+1 (+2 au niveau 10 de l'artificier pour Arme améliorée, Défense améliorée, Focaliseur arcanique amélioré)."""
    n = norm(name)
    if n in ("arme amelioree", "defense amelioree", "focaliseur arcanique ameliore"):
        return 2 if level >= 10 else 1
    if n in ("arme radieuse", "tir repete", "arme de retour", "bouclier repulsif"):
        return 1
    return 0


def replicable_items(level: int) -> list[str]:
    """Objets magiques reproductibles jusqu'au niveau d'artificier donné (tables du Chaudron de Tasha)."""
    tables = (infusion_defs().get("Reproduction d'objet magique") or {}).get("tables", {})
    out = []
    for key, txt in tables.items():
        lvl = int(re.match(r"\d+", key).group(0))
        if lvl <= level:
            out += [re.sub(r"\s*\((?:Oui|Non)\)\s*$", "", x).strip() for x in txt.split(";") if x.strip()]
    return out


class InfusionsMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ côté artificier
    def infusion_known_count(self, lvl: Optional[int] = None) -> int:
        lvl = self.class_level("Artificier") if lvl is None else lvl
        return next((n for l, n in KNOWN if lvl >= l), 0)

    def infusion_max(self) -> int:
        lvl = self.class_level("Artificier")
        base = next((n for l, n in INFUSED if lvl >= l), 0)
        if base and hasattr(self, "armorer_level") and self.armorer_level() >= 9:
            base += 2                                     # Modifications d'armure (Armurier 9)
        return base

    def infusion_option_set(self) -> Optional[dict]:
        lvl = self.class_level("Artificier")
        total = self.infusion_known_count(lvl)
        if not total or self.sheet_edition == 2024:
            return None
        opts = {n: "{}{}".format("Prérequis : artificier de niveau {}. ".format(d["niveau"]) if d["niveau"] else "",
                                 d["description"][:600]) for n, d in infusion_defs().items() if d["niveau"] <= lvl}
        return {"key": "infusions", "label": "Infusions connues (Artificier)", "total": total, "options": opts,
                "chosen": [n for n in (self.ch.options_classe or {}).get("infusions", []) if n in opts]}

    def known_infusions(self) -> list[str]:
        s = self.infusion_option_set()
        return list(s["chosen"]) if s else []

    def infusions_in_progress(self) -> dict:
        """Infusions de cet artificier : {rows: [{type, infusion, objet, personnage, idx}], max, depasse}.
        type : « moi » (objet infusé de la fiche) ou « allie » (saisi à la main)."""
        rows = []
        me = norm(self.ch.nom or "")
        for i, e in enumerate(self.ch.objets_magiques):
            meta = e.get("infusion") or {}
            if meta and (meta.get("par_moi") or (me and norm(meta.get("artificier", "")) == me)):
                base = (meta.get("source") or {}).get("base") or self.magic_display_name(e)
                rows.append({"type": "moi", "infusion": meta.get("nom", ""), "objet": base,
                             "personnage": self.ch.nom or "moi", "idx": i, "ordre": meta.get("ordre", 0)})
        for j, a in enumerate(getattr(self.ch, "infusions_allies", []) or []):
            rows.append({"type": "allie", "infusion": a.get("infusion", ""), "objet": a.get("objet", ""),
                         "personnage": a.get("personnage", ""), "idx": j, "ordre": a.get("ordre", 0)})
        rows.sort(key=lambda r: r["ordre"])
        mx = self.infusion_max()
        return {"rows": rows, "max": mx, "depasse": max(0, len(rows) - mx) if mx else 0}

    def _next_order(self) -> int:
        orders = [(e.get("infusion") or {}).get("ordre", 0) for e in self.ch.objets_magiques]
        orders += [a.get("ordre", 0) for a in getattr(self.ch, "infusions_allies", []) or []]
        return max(orders + [0]) + 1

    def add_ally_infusion(self, infusion: str, objet: str, personnage: str) -> None:
        self.ch.infusions_allies.append({"infusion": infusion, "objet": objet.strip(), "personnage": personnage.strip(),
                                         "ordre": self._next_order()})

    def remove_ally_infusion(self, idx: int) -> None:
        if 0 <= idx < len(self.ch.infusions_allies):
            self.ch.infusions_allies.pop(idx)

    def oldest_infusion(self) -> Optional[dict]:
        rows = self.infusions_in_progress()["rows"]
        return rows[0] if rows else None

    # ------------------------------------------------------------------ côté porteur (toute fiche)
    def infusion_candidates(self, name: str) -> list[dict]:
        """Objets NON magiques de la fiche acceptant l'infusion : [{key, label}]. Clés : « slot:<case>:<i> »,
        « armure », « bouclier », « inv:<i> », « nouveau:<nom> » (objet ordinaire non listé)."""
        d = infusion_defs().get(name)
        if not d:
            return []
        cible, ch, out = d["cible"], self.ch, []

        def weapon_ok(wname: str) -> bool:
            w = self.db.weapons.get(wname)
            if not w or wname == "Mains nues":
                return False
            props = [norm(p) for p in w.get("proprietes", [])]
            return cible == "arme" or (cible == "arme_munitions" and "munitions" in props) or \
                (cible == "arme_lancer" and "lancer" in props)

        if cible.startswith("arme"):
            for key in ("armes_cac", "armes_distance"):
                for i, slot in enumerate(getattr(ch, key)):
                    if slot.get("nom") and not slot.get("objet") and weapon_ok(slot["nom"]):
                        out.append({"key": "slot:{}:{}".format(key, i), "label": "{} (en main)".format(slot["nom"])})
        armor = self.db.armors.get(ch.armure.get("nom", ""), {})
        if cible in ("armure", "armure_bouclier", "armure_robe") and armor and armor.get("categorie") != "aucune" \
                and not ch.armure.get("objet"):
            out.append({"key": "armure", "label": "{} (portée)".format(ch.armure["nom"])})
        if cible in ("bouclier", "armure_bouclier") and ch.armure.get("bouclier") and not ch.armure.get("bouclier_objet"):
            out.append({"key": "bouclier", "label": "{} (porté)".format(ch.armure.get("bouclier_nom") or "Bouclier")})
        for i, it in enumerate(ch.equipement):
            nm = it.get("nom", "")
            n = norm(nm)
            ok = (cible.startswith("arme") and weapon_ok(nm)) or \
                (cible in ("armure", "armure_bouclier", "armure_robe") and nm in self.db.armors and
                 self.db.armors[nm].get("categorie") != "aucune") or \
                (cible in ("bouclier", "armure_bouclier") and nm in (getattr(self.db, "shields", {}) or {})) or \
                (cible == "armure_robe" and n.startswith("robe")) or \
                (cible == "focaliseur" and re.match(r"(baguette|baton|sceptre)", n)) or \
                (cible == "bottes" and n.startswith("botte")) or (cible == "casque" and n.startswith("casque")) or \
                (cible == "anneau" and n.startswith("anneau")) or (cible == "gemme" and re.search(r"gemme|cristal|diamant|rubis|saphir|emeraude", n))
            if ok and int(it.get("qte", 1)) > 0:
                out.append({"key": "inv:{}".format(i), "label": "{} (inventaire)".format(nm)})
        arc = hasattr(self, "armorer_level") and self.armorer_level() >= 9 and self.arcane_armor_active()
        if arc:                                           # Modifications d'armure (Armurier 9) : pièces infusables
            if cible == "bottes":
                out.insert(0, {"key": "nouveau:Bottes (armure arcanique)", "label": "Bottes de l'armure arcanique"})
            if cible == "casque":
                out.insert(0, {"key": "nouveau:Casque (armure arcanique)", "label": "Casque de l'armure arcanique"})
            if cible.startswith("arme") and cible == "arme" and self.model_weapon_name():
                out.insert(0, {"key": "modele", "label": "{} (arme de l'armure arcanique)".format(
                    self.model_weapon_name())})
            for c in out:
                if c["key"] == "armure":
                    c["label"] = "{} — plastron de l'armure arcanique".format(ch.armure["nom"])
        for base in BASE_SUGGESTIONS.get(cible, []):
            out.append({"key": "nouveau:" + base, "label": "{} — objet ordinaire non listé".format(base)})
        if cible in ("arme", "arme_munitions", "arme_lancer", "armure", "bouclier", "armure_bouclier"):
            out.append({"key": "nouveau:", "label": "Objet ordinaire non listé (choisir l'arme / l'armure)"})
        return out

    def apply_infusion(self, name: str, target: str, artificer: str = "", level: int = 0, choice: str = "",
                       base_name: str = "") -> str:
        """Infuse l'objet ciblé (voir infusion_candidates). `choice` : type de dégâts (Armure résistante) ou objet
        reproduit (Reproduction d'objet magique) ; `base_name` : arme / armure d'un objet non listé.
        Renvoie le nom de l'objet magique créé (« » en cas d'échec)."""
        d = infusion_defs().get(name)
        if not d:
            return ""
        level = int(level or self.class_level("Artificier") or 2)
        artificer = (artificer or "").strip() or (self.ch.nom if self.class_level("Artificier") else "")
        par_moi = bool(self.class_level("Artificier")) and (not artificer or norm(artificer) == norm(self.ch.nom or ""))
        meta = {"nom": name, "artificier": artificer, "niveau": level, "par_moi": par_moi, "ordre": self._next_order()}
        ch = self.ch
        if d["cible"] == "reproduction":                  # le vrai objet du catalogue
            if not choice or not self.magic_item(choice):
                return ""
            item = self.magic_item(choice)
            if self.magic_gear_kind(item):
                bases = self.magic_base_options(choice)
                label = self.add_magic_gear(choice, base_name or (bases[0] if bases else ""))
            else:
                self.add_magic_item(choice)
                label = choice
            if not ch.objets_magiques:
                return ""
            entry = ch.objets_magiques[-1]
            entry["infusion"] = dict(meta, source={"kind": "reproduction"})
            return label
        # ---- objet de base
        source: dict = {"kind": "nouveau"}
        base = ""
        if target.startswith("slot:"):
            _, key, i = target.split(":")
            base, source = getattr(ch, key)[int(i)].get("nom", ""), {"kind": "slot", "slot": key, "index": int(i)}
        elif target == "armure":
            base, source = ch.armure.get("nom", ""), {"kind": "armure"}
        elif target == "bouclier":
            base, source = ch.armure.get("bouclier_nom") or "Bouclier", {"kind": "bouclier"}
        elif target.startswith("inv:"):
            idx = int(target.split(":")[1])
            if not 0 <= idx < len(ch.equipement):
                return ""
            base, source = ch.equipement[idx]["nom"], {"kind": "inv"}
            ch.equipement[idx]["qte"] = int(ch.equipement[idx].get("qte", 1)) - 1
            if ch.equipement[idx]["qte"] <= 0:
                ch.equipement.pop(idx)
        elif target.startswith("nouveau:"):
            base = target.split(":", 1)[1] or base_name
        elif target == "modele":                          # arme de l'armure arcanique (Armurier 9)
            base, source = self.model_weapon_name(), {"kind": "modele"}
        if not base:
            return ""
        source["base"] = base
        bonus = scaled_bonus(name, level)
        shields = getattr(self.db, "shields", {}) or {}
        is_weapon = base in self.db.weapons
        is_armor = (base in self.db.armors and self.db.armors[base].get("categorie") != "aucune") or base in shields
        extra = {}
        if norm(name) == "focaliseur arcanique ameliore":
            extra["bonus_sorts"] = 2 if level >= 10 else 1
        if norm(name) == "heaume de vigilance":
            extra["avantages"] = ["init"]
        if norm(name) == "armure resistante":
            extra["resistances"] = [choice] if choice in RESIST_TYPES else []
        if norm(name) == "armure de propulsion arcanique":
            extra["vitesse_bonus"] = 1.5
        label = name if (is_weapon or is_armor) else "{} ({})".format(name, base)   # affiché « Infusion (base) »
        n = 2
        while label in ch.objets_perso or label in self.db.magic_items:
            label = "{} {}".format(name, n) if (is_weapon or is_armor) else "{} {} ({})".format(name, n, base)
            n += 1
        type_ = "Arme" if is_weapon else "Armure" if is_armor else "Objet merveilleux"
        created = self.add_custom_magic_item(
            label, type_, "peu commun", lien=d["lien"], description=d["description"], base=base if (is_weapon or is_armor) else "",
            bonus=bonus if (is_weapon or is_armor) else 0, resistances=extra.get("resistances"),
            avantages=extra.get("avantages"))
        if not created:
            return ""
        item = ch.objets_perso[created]
        item.update({k: v for k, v in extra.items() if k in ("bonus_sorts", "vitesse_bonus")}, infusion=name)
        if source["kind"] == "modele":
            item["arme_modele_bonus"] = bonus             # bonus ajouté à l'arme du modèle (Armurier)
        if (is_weapon or is_armor) and not bonus:
            item["bonus_fixe"] = 0
        idx = len(ch.objets_magiques) - 1
        entry = ch.objets_magiques[idx]
        entry["infusion"] = dict(meta, source=source)
        if entry.get("base") and source["kind"] in ("slot", "armure", "bouclier"):
            slot = {"armure": "armure", "bouclier": "main_secondaire_bouclier"}.get(source["kind"])
            if source["kind"] == "slot":
                slot = {"armes_cac": "main_principale" if source["index"] == 0 else "main_secondaire",
                        "armes_distance": "distance"}[source["slot"]]
            self.equip_magic_gear(idx, slot)
        elif not entry.get("base"):
            entry["equipe"] = True
            if d["lien"] and not self.attune_blocked(idx):
                entry["harmonise"] = True
        if norm(name) == "serviteur homoncule" and hasattr(self, "menagerie_add"):
            inst = self.menagerie_add("serviteur_homoncule")
            if inst:
                entry["infusion"]["compagnon"] = inst.get("uid", "")
        return created

    def infused_entries(self) -> list[tuple[int, dict]]:
        return [(i, e) for i, e in enumerate(self.ch.objets_magiques) if e.get("infusion")]

    def remove_infusion(self, idx: int) -> str:
        """Retire l'infusion de l'objet n° idx : il redevient ordinaire, à la même place. Renvoie le message."""
        ch = self.ch
        if not 0 <= idx < len(ch.objets_magiques):
            return ""
        entry = ch.objets_magiques[idx]
        meta = entry.get("infusion") or {}
        if not meta:
            return ""
        src = meta.get("source") or {}
        label = self.magic_display_name(entry)
        uid = entry.get("uid")
        held = None
        if uid:
            for slot, holder in self._gear_slots():
                if holder.get(self._uid_key(slot)) == uid:
                    held = (slot, holder)
        ch.objets_magiques.pop(idx)
        if entry.get("nom") in ch.objets_perso and not any(e.get("nom") == entry["nom"] for e in ch.objets_magiques):
            ch.objets_perso.pop(entry["nom"], None)
        if meta.get("compagnon") and hasattr(self, "menagerie_remove"):
            self.menagerie_remove(meta["compagnon"])
        base = src.get("base", "")
        if src.get("kind") == "reproduction":
            return "{} : infusion retirée — l'objet reproduit disparaît.".format(label)
        if held is not None:                              # l'objet ordinaire reste dans la même case
            slot, holder = held
            if slot == "main_secondaire_bouclier":
                holder.update(bouclier=True, bouclier_nom=base, bonus_bouclier=0, bouclier_objet="",
                              bouclier_affichage="")
            else:
                holder.update(nom=base, bonus=0, objet="", affichage="")
        elif base and src.get("kind") != "modele" and "armure arcanique" not in norm(base):
            entry_inv = next((e for e in ch.equipement if e.get("nom") == base), None)
            if entry_inv:
                entry_inv["qte"] = int(entry_inv.get("qte", 1)) + 1
            else:
                ch.equipement.append({"nom": base, "qte": 1})
        if hasattr(self, "sync_magic_gear"):
            self.sync_magic_gear()
        return "{} : infusion retirée — l'objet redevient ordinaire ({}).".format(label, base or "—")

    def set_infusion_level(self, idx: int, level: int) -> None:
        """Niveau de l'artificier modifié après coup : bonus +1 / +2 recalculé."""
        if not 0 <= idx < len(self.ch.objets_magiques):
            return
        entry = self.ch.objets_magiques[idx]
        meta = entry.get("infusion")
        if not meta:
            return
        meta["niveau"] = int(level)
        item = self.ch.objets_perso.get(entry.get("nom", ""))
        if item:
            b = scaled_bonus(meta["nom"], int(level))
            if "bonus_fixe" in item:
                item["bonus_fixe"] = b
                if item.get("type") == "Armure":
                    item["ca"] = b
            if "bonus_sorts" in item:
                item["bonus_sorts"] = 2 if int(level) >= 10 else 1
        if hasattr(self, "sync_magic_gear"):
            self.sync_magic_gear()
