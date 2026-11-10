"""
Création de personnage au niveau 1 (v48, inspirée de Baldur's Gate 3) — logique pure.

1. Magie raciale au choix : un trait du type « Vous connaissez un sort mineur de votre choix de la liste du
   magicien » (Haut-elfe…) ouvre un emplacement de choix ; le sort choisi rejoint les sorts raciaux
   (`racial_spells()`), avec la mention [Sort Racial] dans l'onglet Magie et une tuile dans l'onglet Combat, quelle
   que soit la classe (un Guerrier haut-elfe lance son tour de magie racial).
2. Équipement de départ (Manuel des joueurs) :
     - paquetage de classe standard (option « a » des choix d'équipement de chaque classe) + équipement de
       l'historique et son or ;
     - OU boutique : budget = or de départ de la classe (règle « richesse de départ » : moyenne ou jet de dés)
       + or de l'historique ; l'équipement de l'historique reste offert ; le reste du budget devient la bourse.
   Le paquetage de classe équipe aussitôt armure, bouclier et armes (comme BG3).
"""
from __future__ import annotations

import random
import re
from typing import Optional

from .rules import norm

# or de départ de la classe (PHB, « Richesse de départ par classe ») : (nombre de d4, multiplicateur)
STARTING_GOLD = {"Barbare": (2, 10), "Barde": (5, 10), "Clerc": (5, 10), "Druide": (2, 10), "Ensorceleur": (3, 10),
                 "Guerrier": (5, 10), "Magicien": (4, 10), "Moine": (5, 1), "Paladin": (5, 10), "Rôdeur": (5, 10),
                 "Roublard": (4, 10), "Occultiste": (4, 10), "Artificier": (5, 10)}

# paquetage standard (option « a » des choix du PHB) : (quantité, nom)
CLASS_KITS = {
    "Barbare": [(1, "Hache à deux mains"), (2, "Hachette"), (1, "Paquetage d’explorateur"), (4, "Javeline")],
    "Barde": [(1, "Rapière"), (1, "Paquetage de diplomate"), (1, "Instrument de musique"), (1, "Armure de cuir"),
              (1, "Dague")],
    "Clerc": [(1, "Masse d’armes"), (1, "Armure d’écailles"), (1, "Arbalète légère"), (20, "Carreaux d'arbalète"),
              (1, "Paquetage d’ecclésiastique"), (1, "Bouclier"), (1, "Symbole sacré")],
    "Druide": [(1, "Bouclier"), (1, "Cimeterre"), (1, "Armure de cuir"), (1, "Paquetage d’explorateur"),
               (1, "Focaliseur druidique")],
    "Ensorceleur": [(1, "Arbalète légère"), (20, "Carreaux d'arbalète"), (1, "Sacoche à composantes"),
                    (1, "Paquetage d’exploration souterraine"), (2, "Dague")],
    "Guerrier": [(1, "Cotte de mailles"), (1, "Épée longue"), (1, "Bouclier"), (1, "Arbalète légère"),
                 (20, "Carreaux d'arbalète"), (1, "Paquetage d’exploration souterraine")],
    "Magicien": [(1, "Bâton de combat"), (1, "Sacoche à composantes"), (1, "Paquetage d’érudit"), (1, "Grimoire")],
    "Moine": [(1, "Épée courte"), (1, "Paquetage d’exploration souterraine"), (10, "Fléchette")],
    "Paladin": [(1, "Épée longue"), (1, "Bouclier"), (5, "Javeline"), (1, "Paquetage d’ecclésiastique"),
                (1, "Cotte de mailles"), (1, "Symbole sacré")],
    "Rôdeur": [(1, "Armure d’écailles"), (2, "Épée courte"), (1, "Paquetage d’exploration souterraine"),
               (1, "Arc long"), (20, "Flèches")],
    "Roublard": [(1, "Rapière"), (1, "Arc court"), (20, "Flèches"), (1, "Paquetage de cambrioleur"),
                 (1, "Armure de cuir"), (2, "Dague"), (1, "Outils de voleur")],
    "Occultiste": [(1, "Arbalète légère"), (20, "Carreaux d'arbalète"), (1, "Sacoche à composantes"),
                   (1, "Paquetage d’érudit"), (1, "Armure de cuir"), (1, "Bâton de combat"), (2, "Dague")],
    "Artificier": [(1, "Masse d’armes"), (1, "Arbalète légère"), (20, "Carreaux d'arbalète"),
                   (1, "Armure de cuir clouté"), (1, "Outils de voleur"), (1, "Paquetage d’exploration souterraine")],
}

COIN_RATES = {"po": 1.0, "pa": 0.1, "pc": 0.01, "pp": 10.0, "pe": 0.5}
RACIAL_CHOICE = re.compile(r"(?:sort mineur|tour de magie)s? (?:de votre choix|au choix) (?:de|dans) la liste "
                           r"(?:des sorts )?du (\w+)")
LIST_NAMES = {"magicien": "Magicien", "clerc": "Clerc", "druide": "Druide", "barde": "Barde",
              "ensorceleur": "Ensorceleur", "occultiste": "Occultiste", "sorcier": "Occultiste"}


def parse_price(text: str) -> float:
    """« 15 po » -> 15.0 ; « 2 pa » -> 0.2 ; « 5 pc » -> 0.05 ; « — » -> 0."""
    m = re.search(r"([\d\s]+(?:[.,]\d+)?)\s*(po|pa|pc|pp|pe)\b", norm(text or ""))
    if not m:
        return 0.0
    return float(m.group(1).replace(" ", "").replace(",", ".")) * COIN_RATES[m.group(2)]


def split_coins(po: float) -> dict:
    """15,37 po -> {po: 15, pa: 3, pc: 7}."""
    total_pc = int(round(po * 100))
    return {"po": total_pc // 100, "pa": (total_pc % 100) // 10, "pc": total_pc % 10}


class CreationMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ magie raciale au choix
    def racial_choice_slots(self) -> list[dict]:
        """Traits raciaux « sort mineur de votre choix de la liste du X » : [{cle, liste, source, choix}]."""
        out = []
        for cap in self.race_capacities():
            m = RACIAL_CHOICE.search(norm(cap.get("description", "")))
            if not m:
                continue
            key = cap.get("nom", "") or "Sort mineur"
            out.append({"cle": key, "liste": LIST_NAMES.get(m.group(1), m.group(1).capitalize()), "source": key,
                        "choix": (self.ch.sorts_raciaux or {}).get(key, "")})
        return out

    def racial_choice_options(self, key: str) -> list[dict]:
        slot = next((s for s in self.racial_choice_slots() if s["cle"] == key), None)
        if slot is None:
            return []
        return sorted((s for s in self.db.spells_for_class(slot["liste"]) if s["niveau"] == 0),
                      key=lambda s: norm(s["nom"]))

    def set_racial_choice(self, key: str, name: str) -> bool:
        if name and not any(s["nom"] == name for s in self.racial_choice_options(key)):
            return False
        if not any(s["cle"] == key for s in self.racial_choice_slots()):
            return False
        self.ch.sorts_raciaux = dict(self.ch.sorts_raciaux or {})
        if name:
            self.ch.sorts_raciaux[key] = name
        else:
            self.ch.sorts_raciaux.pop(key, None)
        self.normalize()
        return True

    def chosen_racial_spells(self) -> list[dict]:
        """Sorts raciaux CHOISIS (Haut-elfe…), au format de racial_spells()."""
        from . import rules as R
        out = []
        ab, ab_choice = self.racial_spell_ability()
        for slot in self.racial_choice_slots():
            spell = self.db.find_spell(slot["choix"]) if slot["choix"] else None
            if not spell:
                continue
            m = self.mod("Intelligence") if slot["liste"] == "Magicien" else self.mod(ab)
            out.append({"nom": spell["nom"], "sort": spell, "niveau": spell["niveau"], "niveau_requis": 1,
                        "debloque": True, "usage": "À volonté", "carac": "Intelligence" if slot["liste"] ==
                        "Magicien" else ab, "carac_choix": False, "dc": R.spell_save_dc(self.prof, m),
                        "attaque": R.spell_attack_bonus(self.prof, m), "source": slot["source"], "au_choix": True,
                        "choisi": True})
        return out

    def racial_choices_missing(self) -> int:
        return sum(1 for s in self.racial_choice_slots() if not s["choix"])

    # ------------------------------------------------------------------ or de départ
    def starting_gold(self, class_name: str = "") -> dict:
        """{formule, moyenne} de la richesse de départ de la classe (PHB)."""
        cls = class_name or (self.ch.classes[0]["nom"] if self.ch.classes else "")
        n, mult = STARTING_GOLD.get(cls, (4, 10))
        return {"formule": "{}d4{}".format(n, " × {}".format(mult) if mult > 1 else "") + " po",
                "moyenne": int(n * 2.5 * mult), "des": n, "mult": mult}

    def roll_starting_gold(self, class_name: str = "", rng: Optional[random.Random] = None) -> int:
        g = self.starting_gold(class_name)
        rng = rng or random.Random()
        return sum(rng.randint(1, 4) for _ in range(g["des"])) * g["mult"]

    def background_gold(self) -> int:
        return int((self.db.backgrounds.get(self.ch.historique) or {}).get("or", 0) or 0)

    # ------------------------------------------------------------------ paquetage standard
    def resolve_item(self, name: str) -> str:
        """Nom du catalogue correspondant (apostrophes et accents tolérés), sinon le nom donné."""
        if name in self.db.catalog:
            return name
        key = norm(name.replace("’", "'"))
        return next((n for n in self.db.catalog if norm(n.replace("’", "'")) == key), name)

    def class_kit(self, class_name: str = "") -> list[tuple[int, str]]:
        cls = class_name or (self.ch.classes[0]["nom"] if self.ch.classes else "")
        return [(q, self.resolve_item(n)) for q, n in CLASS_KITS.get(cls, [])]

    def background_items(self) -> list[tuple[int, str]]:
        bg = self.db.backgrounds.get(self.ch.historique)
        return [(q, n) for q, n, _ in self.db.parse_item_list(bg.get("inventaire_historique", ""))] if bg else []

    def auto_equip(self) -> list[str]:
        """Équipe armure, bouclier et armes de l'inventaire dans les cases vides (première de chaque type)."""
        ch, db, done = self.ch, self.db, []
        names = [e["nom"] for e in ch.equipement]
        if ch.armure.get("nom", "Aucune armure") in ("", "Aucune armure"):
            armor = next((n for n in names if n in db.armors and n != "Aucune armure"), "")
            if armor:
                ch.armure["nom"] = armor
                done.append(armor)
        if not ch.armure.get("bouclier"):
            shield = next((n for n in names if n in getattr(db, "shields", {})), "")
            if shield:
                ch.armure["bouclier"], ch.armure["bouclier_nom"] = True, shield
                done.append(shield)
        melee = [n for n in names if db.weapons.get(n, {}).get("type") == "cac"]
        ranged = [n for n in names if db.weapons.get(n, {}).get("type") == "distance"]
        if melee and not ch.armes_cac[0].get("nom"):
            ch.armes_cac[0] = {"nom": melee[0], "bonus": 0, "maitrise": None}
            done.append(melee[0])
        if ranged and not ch.armes_distance[0].get("nom"):
            ch.armes_distance[0] = {"nom": ranged[0], "bonus": 0, "maitrise": None}
            done.append(ranged[0])
        return done

    # ------------------------------------------------------------------ boutique
    def shop_items(self, category: str = "", text: str = "") -> list[dict]:
        """Catalogue achetable : [{nom, categorie, prix (po), prix_txt, poids_txt, description}] (prix > 0)."""
        t = norm(text or "")
        out = []
        for n, it in self.db.catalog.items():
            price = parse_price(it.get("prix", ""))
            if price <= 0 or (category and it.get("categorie") != category) or (t and t not in norm(n)):
                continue
            out.append({"nom": n, "categorie": it.get("categorie", ""), "prix": price, "prix_txt": it.get("prix", ""),
                        "poids_txt": it.get("poids_txt", ""), "description": it.get("description", "")})
        return sorted(out, key=lambda x: (x["categorie"], norm(x["nom"])))

    def cart_total(self, cart: dict) -> float:
        prices = {i["nom"]: i["prix"] for i in self.shop_items()}
        return round(sum(prices.get(n, 0.0) * q for n, q in cart.items()), 2)

    # ------------------------------------------------------------------ validation de l'équipement
    def apply_starting_equipment(self, mode: str, class_gold: int = 0, cart: Optional[dict] = None) -> dict:
        """mode « paquetage » : paquetage de classe + équipement et or de l'historique.
        mode « boutique » : équipement de l'historique + achats ; bourse = budget − achats.
        Renvoie {ajouts, equipes, bourse, depense}."""
        ch = self.ch
        ch.equipement = []
        ch.pieces = {"po": 0, "pa": 0, "pc": 0}
        added = []
        for q, n in self.background_items():
            self.add_item(n, q)
            added.append(n)
        spent = 0.0
        if mode == "boutique":
            cart = {n: int(q) for n, q in (cart or {}).items() if int(q) > 0}
            spent = self.cart_total(cart)
            budget = int(class_gold) + self.background_gold()
            if spent > budget + 1e-6:
                raise ValueError("Achats ({:.2f} po) supérieurs au budget ({} po).".format(spent, budget))
            for n, q in cart.items():
                self.add_item(n, q)
                added.append(n)
            ch.pieces = split_coins(budget - spent)
        else:
            for q, n in self.class_kit():
                self.add_item(n, q)
                added.append(n)
            ch.pieces = {"po": self.background_gold(), "pa": 0, "pc": 0}
        equipped = self.auto_equip()
        self.normalize()
        return {"ajouts": added, "equipes": equipped, "bourse": dict(ch.pieces), "depense": spent}
