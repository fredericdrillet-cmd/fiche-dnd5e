"""
Emplacements rapides (v53), sous le mannequin : potions, élixirs, huiles et parchemins placés là ont leur tuile dans
l'onglet « En partie ». Boire une potion : action (action bonus avec la règle de la table « Potion en action
bonus ») ; huile, antitoxine appliquée, parchemin : action. Le parchemin de sort lance le sort choisi puis disparaît.
L'emplacement retient le NOM de l'objet (une pile de potions identiques) ; vidé quand le sac n'en contient plus.
"""
from __future__ import annotations

import re
from typing import Optional

from . import mechanics as M
from .rules import norm

QUICK_SLOTS = 4


class QuickSlotsMixin:
    """Mélangé à Engine."""

    @staticmethod
    def is_quick_item(name: str) -> bool:
        n = norm(name or "")
        return M.is_consumable(name or "") or n.startswith("parchemin")

    def _quick_find(self, name: str) -> Optional[dict]:
        """{nom, source, index, qte} de l'objet du sac portant ce nom (objets courants d'abord)."""
        for i, it in enumerate(self.ch.equipement):
            if it.get("nom") == name and int(it.get("qte", 0) or 0) > 0:
                return {"nom": name, "source": "equipement", "index": i, "qte": int(it.get("qte", 1))}
        hits = [i for i, e in enumerate(self.ch.objets_magiques) if e.get("nom") == name]
        if hits:
            return {"nom": name, "source": "objet", "index": hits[0], "qte": len(hits)}
        return None

    def quick_slots(self) -> list[Optional[dict]]:
        """Contenu des emplacements : None (vide) ou {nom, source, index, qte, genre, type}."""
        out = []
        for name in (list(self.ch.emplacements_rapides) + [""] * QUICK_SLOTS)[:QUICK_SLOTS]:
            found = self._quick_find(name) if name else None
            if found:
                found.update(genre=self.quick_kind(name), type=self.quick_tile_type(name))
            out.append(found)
        return out

    def sync_quick_slots(self) -> None:
        """Longueur fixe ; un emplacement dont le sac ne contient plus l'objet est vidé."""
        names = (list(self.ch.emplacements_rapides or []) + [""] * QUICK_SLOTS)[:QUICK_SLOTS]
        self.ch.emplacements_rapides = [n if n and self._quick_find(n) else "" for n in names]

    def set_quick_slot(self, n: int, key: str) -> tuple[bool, str]:
        """Place l'objet du sac `key` (`bag_key` : « #mg:<indice> » ou nom) dans l'emplacement n (0 à 3)."""
        if not 0 <= n < QUICK_SLOTS:
            return False, ""
        name = key
        if key.startswith("#mg:") and key[4:].isdigit():
            idx = int(key[4:])
            if idx >= len(self.ch.objets_magiques):
                return False, "Objet introuvable."
            name = self.ch.objets_magiques[idx]["nom"]
        if not self.is_quick_item(name) or self._quick_find(name) is None:
            return False, "« {} » ne va pas dans un emplacement rapide (potions, huiles, parchemins).".format(name)
        slots = (list(self.ch.emplacements_rapides) + [""] * QUICK_SLOTS)[:QUICK_SLOTS]
        slots = ["" if s == name else s for s in slots]          # un objet : un seul emplacement
        slots[n] = name
        self.ch.emplacements_rapides = slots
        return True, "Emplacement rapide {} : {}.".format(n + 1, name)

    def clear_quick_slot(self, n: int) -> None:
        slots = (list(self.ch.emplacements_rapides) + [""] * QUICK_SLOTS)[:QUICK_SLOTS]
        if 0 <= n < QUICK_SLOTS:
            slots[n] = ""
        self.ch.emplacements_rapides = slots

    @staticmethod
    def quick_kind(name: str) -> str:
        n = norm(name or "")
        if n.startswith("parchemin"):
            return "parchemin"
        if n.startswith("huile"):
            return "huile"
        return "potion"

    def quick_tile_type(self, name: str) -> str:
        if self.quick_kind(name) == "potion" and self.rule_active("potion_action_bonus"):
            return "Action bonus"
        return "Action"

    @staticmethod
    def scroll_level(name: str) -> Optional[int]:
        """Niveau du sort d'un « Parchemin de sort (niveau N) » (0 : sort mineur) ; None pour un autre parchemin."""
        n = norm(name or "")
        if not n.startswith("parchemin de sort"):
            return None
        if "sort mineur" in n or "tour de magie" in n:
            return 0
        m = re.search(r"niveau\s*(\d)", n)
        return int(m.group(1)) if m else None

    def scroll_spells(self, name: str) -> list[str]:
        """Sorts que peut contenir le parchemin (sorts de son niveau, édition de la fiche)."""
        lvl = self.scroll_level(name)
        if lvl is None:
            return []
        want = self.sheet_edition == 2024
        return sorted((s for s, sp in self.db.spells.items() if int(sp.get("niveau") or 0) == lvl
                       and want == ("(2024)" in s or sp.get("edition") == 2024)), key=norm)

    def consume_one(self, source: str, index: int) -> None:
        """Retire un exemplaire de l'objet (pile d'objets courants ou objet magique)."""
        if source == "equipement" and 0 <= index < len(self.ch.equipement):
            it = self.ch.equipement[index]
            it["qte"] = int(it.get("qte", 1)) - 1
            if it["qte"] <= 0:
                self.ch.equipement.pop(index)
        elif source == "objet":
            self.remove_magic_item(index)

    def quick_tiles(self, tile) -> None:
        """Tuiles des emplacements remplis (appelé par `turn_actions`)."""
        for n, s in enumerate(self.quick_slots()):
            if not s:
                continue
            item = self.magic_item(s["nom"]) or {}
            info = self.db.catalog.get(s["nom"], {}) if hasattr(self.db, "catalog") else {}
            desc = (item.get("description") or info.get("description") or "")[:400]
            what = {"potion": "boire la potion", "huile": "appliquer l'huile",
                    "parchemin": "lire le parchemin : le sort est lancé, le parchemin disparaît. Le sort doit figurer "
                                 "dans la liste de sorts de votre classe ; sinon, s'il est de niveau supérieur à ce que "
                                 "vous pouvez lancer, test d'Arcanes (DD 10 + niveau du sort)"}[s["genre"]]
            tile("rapide:{}".format(n), s["nom"], "📜" if s["genre"] == "parchemin" else "🧪", s["type"],
                 "Emplacement rapide {} — ×{}".format(n + 1, s["qte"]),
                 "{}.\n{}".format(what[0].upper() + what[1:], desc), cost="1 {}".format(s["nom"]))
