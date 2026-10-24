"""
Mannequin d'équipement (v31, inspiré de l'inventaire de Baldur's Gate 3) — logique pure.

Douze emplacements : tête, amulette, cape, armure, gants, ceinture, bottes, anneau ×2, main principale, main
secondaire, distance.
    - armure, mains et distance REFLÈTENT les choix existants (onglet Combat : armure, bouclier, armes) ;
    - les objets magiques portables (anneaux, bottes, capes, amulettes…) occupent un emplacement : UN objet par
      case — équiper un objet dans une case occupée retire l'ancien (il reste dans l'inventaire, non équipé) ;
    - au chargement, chaque objet équipé reçoit une case libre de son type ; s'il n'en reste pas, une
      incohérence est signalée (« 3 anneaux équipés pour 2 emplacements ») ;
    - comparaison « équipé / survolé » : Δ de CA pour une armure, de bonus d'attaque et de dégâts moyens pour
      une arme, objet remplacé pour un objet magique.
"""
from __future__ import annotations

from typing import Optional

from . import dice as D
from .rules import norm

SLOTS = [
    ("tete", "Tête", "⛑"), ("amulette", "Amulette", "📿"), ("cape", "Cape, robe", "🧥"),
    ("armure", "Armure", "🛡"), ("gants", "Gants, bracelets", "🧤"), ("ceinture", "Ceinture", "🎗"),
    ("bottes", "Bottes", "👢"), ("anneau_1", "Anneau", "💍"), ("anneau_2", "Anneau", "💍"),
    ("main_principale", "Main principale", "⚔"), ("main_secondaire", "Main secondaire", "🛡"),
    ("distance", "Distance", "🏹"),
]
SLOT_LABELS = {k: lab for k, lab, _ in SLOTS}
KEYWORDS = [
    ("tete", ("chapeau", "heaume", "casque", "bandeau", "diademe", "couronne", "lunettes", "capuchon", "masque",
              "yeux", "serre-tete", "tiare", "voile")),
    ("amulette", ("amulette", "collier", "medaillon", "broche", "periapte", "pendentif", "scarabee")),
    ("cape", ("cape", "manteau", "robe", "capeline")),
    ("gants", ("gants", "gantelets", "bracelets", "brassards", "bracelet")),
    ("ceinture", ("ceinture", "ceinturon")),
    ("bottes", ("bottes", "chaussons", "chaussures", "sandales", "pantoufles", "souliers")),
]
MAGIC_SLOTS = ("tete", "amulette", "cape", "gants", "ceinture", "bottes", "anneau_1", "anneau_2")


def item_slot_kind(item: Optional[dict], name: str) -> str:
    """Type d'emplacement d'un objet magique (« anneau » pour les deux cases d'anneau) ; « » = non porté."""
    kind = norm((item or {}).get("type", ""))
    n = norm(name)
    first = n.split(" ")[0] if n else ""
    if kind == "anneau" or first in ("anneau", "bague"):     # « Baguette » n'est pas une bague
        return "anneau"
    if kind not in ("objet merveilleux", ""):
        return ""
    for slot, words in KEYWORDS:
        if first in words:
            return slot
    return ""


def slots_for(kind: str) -> list[str]:
    return ["anneau_1", "anneau_2"] if kind == "anneau" else [kind] if kind in MAGIC_SLOTS else []


def _avg(formula: str) -> float:
    groups, flat = D.parse_damage(formula or "")
    return sum(sign * n * (sides + 1) / 2 for sign, n, sides in groups) + flat


class EquipmentMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ cases des objets magiques
    def magic_slot_kind(self, name: str) -> str:
        return item_slot_kind(self.magic_item(name), name)

    def sync_equipment_slots(self) -> None:
        """Cohérence au chargement : objet non équipé = sans case ; équipé = case libre de son type si possible."""
        taken: dict[str, int] = {}
        entries = self.ch.objets_magiques
        for i, e in enumerate(entries):
            slot = e.get("emplacement", "")
            kind = self.magic_slot_kind(e.get("nom", ""))
            if not e.get("equipe") or slot not in slots_for(kind) or slot in taken:
                e["emplacement"] = ""
            else:
                taken[slot] = i
        for i, e in enumerate(entries):
            kind = self.magic_slot_kind(e.get("nom", ""))
            if e.get("equipe") and kind and not e.get("emplacement"):
                free = next((s for s in slots_for(kind) if s not in taken), "")
                if free:
                    e["emplacement"] = free
                    taken[free] = i

    def equip_magic_item(self, idx: int, slot: str = "") -> str:
        """Équipe l'objet n° idx dans `slot` (ou la première case libre de son type, sinon la première de son type) ;
        l'occupant précédent est déséquipé. Renvoie le nom de l'objet remplacé (« » si aucun)."""
        if not 0 <= idx < len(self.ch.objets_magiques):
            return ""
        entry = self.ch.objets_magiques[idx]
        kind = self.magic_slot_kind(entry["nom"])
        options = slots_for(kind)
        entry["equipe"] = True
        if not options:
            return ""
        occupied = {e.get("emplacement"): e for e in self.ch.objets_magiques if e is not entry and e.get("equipe")}
        if slot not in options:
            slot = next((s for s in options if s not in occupied), options[0])
        replaced = ""
        prev = occupied.get(slot)
        if prev is not None:
            prev["equipe"], prev["emplacement"] = False, ""
            replaced = prev["nom"]
        entry["emplacement"] = slot
        return replaced

    def unequip_slot(self, slot: str) -> None:
        """Vide une case : objet magique déséquipé, armure retirée, arme rangée, bouclier ôté."""
        ch = self.ch
        if slot == "armure":
            ch.armure["nom"], ch.armure["bonus"] = "Aucune armure", 0
        elif slot == "main_principale":
            ch.armes_cac[0] = {"nom": "", "bonus": 0, "maitrise": None}
        elif slot == "main_secondaire":
            ch.armure["bouclier"], ch.armure["bouclier_nom"] = False, ""
            if len(ch.armes_cac) > 1:
                ch.armes_cac[1] = {"nom": "", "bonus": 0, "maitrise": None}
        elif slot == "distance":
            ch.armes_distance[0] = {"nom": "", "bonus": 0, "maitrise": None}
        for e in ch.objets_magiques:
            if e.get("emplacement") == slot:
                e["equipe"], e["emplacement"] = False, ""

    @staticmethod
    def is_natural_attack(name: str) -> bool:
        """Attaque naturelle innée (Mains nues) : toujours disponible, ce n'est pas un objet du sac."""
        return norm(name or "").startswith("mains nues")

    def purge_natural_attacks(self) -> None:
        self.ch.equipement = [e for e in self.ch.equipement if not self.is_natural_attack(e.get("nom", ""))]

    def ensure_in_inventory(self, name: str) -> bool:
        """Arme (ou armure, bouclier) choisie dans l'onglet Combat mais absente du sac : ajoutée (1 exemplaire).
        Renvoie True si elle vient d'être ajoutée."""
        name = (name or "").strip()
        if not name or self.is_natural_attack(name) or any(e.get("nom") == name for e in self.ch.equipement):
            return False                                  # v41 : Mains nues = attaque innée, jamais un objet
        self.ch.equipement.append({"nom": name, "qte": 1})
        return True

    # ------------------------------------------------------------------ objets de l'inventaire selon le rôle de la case
    def _owned(self) -> list[str]:
        return [e["nom"] for e in self.ch.equipement if int(e.get("qte", 1) or 0) > 0]

    def two_handed_main(self) -> bool:
        """Arme de la main principale tenue à deux mains (propriété « Deux mains », ou polyvalente à deux mains)."""
        main = self.ch.armes_cac[0] if self.ch.armes_cac else {}
        w = self.db.weapons.get(main.get("nom", ""), {})
        return any(norm(p) == "deux mains" for p in w.get("proprietes", []))   # v46 : polyvalente = prise automatique

    def slot_inventory(self, slot: str) -> list[dict]:
        """Objets de l'inventaire qui peuvent aller dans cette case, selon son rôle :
        armure -> armures du sac ; main principale -> armes de corps à corps ; main secondaire -> boucliers et armes
        légères ; distance -> armes à distance ; autres cases -> objets magiques du bon type (anneau, cape…).
        [{nom, kind: 'objet'|'magique', index (magique), equipe}]"""
        ch, db = self.ch, self.db
        owned = list(dict.fromkeys(self._owned()))
        out = []
        if slot in MAGIC_SLOTS:
            doll = self.paperdoll()
            for i, name in self.slot_candidates(slot):
                out.append({"nom": name, "kind": "magique", "index": i,
                            "equipe": doll.get(slot, {}).get("index") == i})
            return out

        def weapon_ok(name: str, kind: str, light: bool = False) -> bool:
            w = db.weapons.get(name)
            if not w or w.get("type") != kind:
                return False
            return not light or any(norm(p) == "legere" for p in w.get("proprietes", []))

        if slot == "armure":
            names = [n for n in owned if n in db.armors and n != "Aucune armure"]
            cur = ch.armure.get("nom", "")
        elif slot == "main_principale":
            names = [n for n in owned if weapon_ok(n, "cac")]
            cur = ch.armes_cac[0].get("nom", "")
        elif slot == "main_secondaire":
            names = [n for n in owned if n in getattr(db, "shields", {})] + \
                    [n for n in owned if weapon_ok(n, "cac", light=True)]
            cur = ch.armure.get("bouclier_nom", "") if ch.armure.get("bouclier") else \
                (ch.armes_cac[1].get("nom", "") if len(ch.armes_cac) > 1 else "")
        elif slot == "distance":
            names = [n for n in owned if weapon_ok(n, "distance")]
            cur = ch.armes_distance[0].get("nom", "")
        else:
            return []
        gear = self.gear_candidates(slot)                # v45 : armes / armures / boucliers magiques
        bound = {"armure": ch.armure.get("objet"), "main_principale": ch.armes_cac[0].get("objet"),
                 "distance": ch.armes_distance[0].get("objet"),
                 "main_secondaire": ch.armure.get("bouclier_objet") or (ch.armes_cac[1].get("objet")
                                                                        if len(ch.armes_cac) > 1 else None)}.get(slot)
        return [{"nom": n, "kind": "objet", "equipe": n == cur and not bound} for n in names] + gear

    def equip_slot(self, slot: str, choice: dict) -> str:
        """Équipe l'objet choisi dans la case ; renvoie le message (objet remplacé, main libérée…)."""
        ch = self.ch
        if choice.get("kind") == "magique_arme":         # v45 : arme / armure magique liée à son objet de base
            return self.equip_magic_gear(choice["index"], slot)
        if choice.get("kind") == "magique":
            replaced = self.equip_magic_item(choice["index"], slot)
            return "{} : {}{}.".format(SLOT_LABELS.get(slot, slot), choice["nom"],
                                       " (remplace {})".format(replaced) if replaced else "")
        name = choice["nom"]
        note = ""
        if slot == "armure":
            ch.armure["nom"], ch.armure["bonus"] = name, 0
        elif slot == "main_principale":
            ch.armes_cac[0] = {"nom": name, "bonus": 0, "maitrise": None}
            if self.two_handed_main() and (ch.armure.get("bouclier") or (len(ch.armes_cac) > 1 and
                                                                        ch.armes_cac[1].get("nom"))):
                self.unequip_slot("main_secondaire")
                note = " — arme à deux mains : main secondaire libérée"
        elif slot == "main_secondaire":
            if self.two_handed_main():
                return "Main secondaire indisponible : l'arme de la main principale se tient à deux mains."
            if name in getattr(self.db, "shields", {}):
                ch.armure["bouclier"], ch.armure["bouclier_nom"] = True, name
                if len(ch.armes_cac) > 1:
                    ch.armes_cac[1] = {"nom": "", "bonus": 0, "maitrise": None}
            else:
                ch.armure["bouclier"], ch.armure["bouclier_nom"] = False, ""
                ch.armes_cac[1] = {"nom": name, "bonus": 0, "maitrise": None}
        elif slot == "distance":
            ch.armes_distance[0] = {"nom": name, "bonus": 0, "maitrise": None}
        return "{} : {}{}.".format(SLOT_LABELS.get(slot, slot), name, note)

    def equipment_warnings(self) -> list[str]:
        counts: dict[str, int] = {}
        for e in self.ch.objets_magiques:
            kind = self.magic_slot_kind(e.get("nom", ""))
            if e.get("equipe") and kind:
                counts[kind] = counts.get(kind, 0) + 1
        out = []
        for kind, n in counts.items():
            room = len(slots_for(kind))
            if n > room:
                label = "anneaux" if kind == "anneau" else "objets « {} »".format(SLOT_LABELS[kind].lower())
                out.append("{} {} équipés pour {} emplacement{}.".format(n, label, room, "s" * (room > 1)))
        return out

    # ------------------------------------------------------------------ vue du mannequin
    def paperdoll(self) -> dict[str, dict]:
        """{case: {nom, source, detail, harmonise, index}} — case vide = absente du dictionnaire."""
        out: dict[str, dict] = {}
        ch = self.ch
        armor = ch.armure.get("nom", "")
        if armor and armor != "Aucune armure":
            ca = self.armor_class()[0]
            out["armure"] = {"nom": ch.armure.get("affichage") or armor, "source": "armure", "detail": "CA {}".format(ca), "harmonise": False}
        main = ch.armes_cac[0] if ch.armes_cac else {}
        if main.get("nom"):
            st = self.weapon_stats(main)
            out["main_principale"] = {"nom": main.get("affichage") or main["nom"], "source": "arme",
                                      "detail": "{} {}".format(st["degats"], st["type_degats"]) if st else "",
                                      "harmonise": False}
        if ch.armure.get("bouclier"):
            out["main_secondaire"] = {"nom": ch.armure.get("bouclier_affichage") or ch.armure.get("bouclier_nom")
                                      or "Bouclier", "source": "bouclier",
                                      "detail": "+{} CA".format(self.shield_bonus()), "harmonise": False}
        elif len(ch.armes_cac) > 1 and ch.armes_cac[1].get("nom"):
            st = self.weapon_stats(ch.armes_cac[1])
            out["main_secondaire"] = {"nom": ch.armes_cac[1].get("affichage") or ch.armes_cac[1]["nom"],
                                      "source": "arme",
                                      "detail": "{} {}".format(st["degats"], st["type_degats"]) if st else "",
                                      "harmonise": False}
        rng = ch.armes_distance[0] if ch.armes_distance else {}
        if rng.get("nom"):
            st = self.weapon_stats(rng)
            out["distance"] = {"nom": rng.get("affichage") or rng["nom"], "source": "arme",
                               "detail": "{} {}".format(st["degats"], st["type_degats"]) if st else "",
                               "harmonise": False}
        bound = {"armure": ch.armure.get("objet"), "main_principale": main.get("objet"), "distance": rng.get("objet"),
                 "main_secondaire": ch.armure.get("bouclier_objet") if ch.armure.get("bouclier") else
                 (ch.armes_cac[1].get("objet") if len(ch.armes_cac) > 1 else None)}
        for key, uid in bound.items():                    # v45 : arme / armure magique dans la case
            if uid and key in out:
                out[key]["magique"] = True
        for i, e in enumerate(ch.objets_magiques):
            slot = e.get("emplacement", "")
            if e.get("equipe") and slot in MAGIC_SLOTS:
                item = self.magic_item(e["nom"]) or {}
                out[slot] = {"nom": e["nom"], "source": "objet", "index": i, "harmonise": bool(e.get("harmonise")),
                             "lien": bool(item.get("lien")), "detail": item.get("rarete", "")}
        return out

    def slot_candidates(self, slot: str) -> list[tuple[int, str]]:
        """Objets magiques de l'inventaire qui peuvent aller dans cette case : [(index, nom)]."""
        kind = "anneau" if slot.startswith("anneau") else slot
        return [(i, e["nom"]) for i, e in enumerate(self.ch.objets_magiques)
                if self.magic_slot_kind(e["nom"]) == kind]

    # ------------------------------------------------------------------ comparaison « équipé / survolé »
    def compare_armor(self, name: str) -> dict:
        sim = self.clone()
        sim.ch.armure["nom"] = name
        sim.normalize()
        armor = self.db.armors.get(name, {})
        return {"ca_avant": self.armor_class()[0], "ca_apres": sim.armor_class()[0],
                "delta": sim.armor_class()[0] - self.armor_class()[0],
                "discretion": bool(armor.get("desavantage_discretion")), "force": int(armor.get("force_min") or 0),
                "force_ok": self.score("Force") >= int(armor.get("force_min") or 0)}

    def compare_weapon(self, name: str, ranged: bool = False) -> dict:
        key = "armes_distance" if ranged else "armes_cac"
        cur = dict(getattr(self.ch, key)[0])
        new = dict(cur, nom=name, bonus=0, maitrise=None)
        a, b = self.weapon_stats(cur) if cur.get("nom") else None, self.weapon_stats(new)
        if not b:
            return {}
        spec_a = self.weapon_attack_spec(cur) if a else None
        spec_b = self.weapon_attack_spec(new)
        att_a = spec_a.flat if spec_a is not None else None
        att_b = spec_b.flat if spec_b is not None else None
        return {"actuelle": cur.get("nom", ""), "degats_avant": a["degats"] if a else "",
                "degats_apres": b["degats"], "moy_avant": _avg(a["degats"]) if a else 0.0,
                "moy_apres": _avg(b["degats"]), "delta_moy": _avg(b["degats"]) - (_avg(a["degats"]) if a else 0.0),
                "attaque_avant": att_a, "attaque_apres": att_b}

    def compare_magic(self, idx: int) -> dict:
        entry = self.ch.objets_magiques[idx]
        kind = self.magic_slot_kind(entry["nom"])
        options = slots_for(kind)
        doll = self.paperdoll()
        free = [s for s in options if s not in doll]
        target = free[0] if free else options[0] if options else ""
        return {"case": SLOT_LABELS.get(target, ""), "remplace": "" if free or not target else doll[target]["nom"],
                "portable": bool(options)}
