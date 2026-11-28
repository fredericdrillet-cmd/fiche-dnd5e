"""
Artificier — Armurier (2014, Chaudron de Tasha) (v53) — logique pure mélangée à Engine.

- Armure arcanique (niv. 3) : l'armure portée devient arcanique — plus de Force requise (pas de malus de vitesse).
- Modèle d'armure (niv. 3), modifiable à la fin d'un repos court ou long (outils de forgeron en main) :
    Gardien  : Gantelets tonnants (arme courante au corps à corps, 1d8 tonnerre ; la cible touchée a le désavantage
               aux attaques contre d'autres que vous) ; Champ défensif (action bonus, PV temporaires = niveau
               d'artificier, bonus de maîtrise fois par repos long).
    Infiltré : Lance-foudre (arme courante à distance, 27 / 90 m, 1d6 foudre ; une fois par tour, +1d6 foudre) ;
               Pas motorisés (+1,50 m de vitesse) ; Champ d'atténuation (avantage en Discrétion : il annule le
               désavantage de l'armure lourde).
  Les armes du modèle utilisent l'Intelligence au lieu de la Force ou de la Dextérité (si elle est meilleure).
- Armure parachevée (niv. 15) : Gardien — attraction (réaction, JS de Force, mod. d'Intelligence fois par repos
  long) ; Infiltré — lueur (la cible touchée par le lance-foudre : prochaine attaque contre elle avec avantage,
  +1d6 foudre si elle touche).
"""
from __future__ import annotations

from typing import Optional

from .rules import norm

MODELS = ("Gardien", "Infiltré")
MODEL_WEAPONS = {
    "Gantelets tonnants": {"nom": "Gantelets tonnants", "categorie": "courante", "type": "cac", "degats": "1d8",
                           "type_degats": "tonnerre", "proprietes": [], "portee": "", "polyvalent": "",
                           "botte": "", "modele": "Gardien"},
    "Lance-foudre": {"nom": "Lance-foudre", "categorie": "courante", "type": "distance", "degats": "1d6",
                     "type_degats": "foudre", "proprietes": [], "portee": "27 / 90 m", "polyvalent": "",
                     "botte": "", "modele": "Infiltré"},
}
# tuiles de classe réservées à un modèle
MODEL_TILES = {"cap:champ_defensif": "Gardien", "cap:attraction_magnetique": "Gardien"}


class ArmorerMixin:
    """Mélangé à Engine."""

    def armorer_level(self) -> int:
        for e in self.ch.classes:
            if e["nom"] == "Artificier" and "armurier" in norm(self.active_subclass(e)) and e["niveau"] >= 3:
                return e["niveau"]
        return 0

    def armor_model_base(self) -> str:
        """« Gardien », « Infiltré » ou « » (sans le suffixe « parachevé »)."""
        name = self.armor_model()[0] if hasattr(self, "armor_model") else ""
        return next((m for m in MODELS if norm(name).startswith(norm(m))), "")

    def set_armor_model(self, name: str) -> bool:
        """Change le modèle d'armure (fin d'un repos court ou long, outils de forgeron en main)."""
        if name not in MODELS or not self.armorer_level():
            return False
        slot = next((s for s in self.fighting_style_slots() if s["kind"] == "modele" and s["debloque"]), None)
        if slot is None:
            return False
        self.ch.styles_combat[slot["id"]] = name
        return True

    def arcane_armor_active(self) -> bool:
        """Armure arcanique : armurier niveau 3+ portant une armure (pas « Aucune armure »)."""
        if not self.armorer_level():
            return False
        armor = self.db.armors.get(self.ch.armure.get("nom", ""), {})
        return bool(armor) and armor.get("categorie") not in ("aucune", None)

    def model_weapon(self, name: str) -> Optional[dict]:
        return MODEL_WEAPONS.get(name)

    def model_weapon_name(self) -> str:
        model = self.armor_model_base()
        return next((n for n, w in MODEL_WEAPONS.items() if w["modele"] == model), "")

    def model_slot(self) -> dict:
        return {"nom": self.model_weapon_name(), "bonus": 0, "maitrise": True, "affichage": self.model_weapon_name()}

    def armorer_modifiers(self) -> list[tuple[str, dict]]:
        if self.arcane_armor_active() and self.armor_model_base() == "Infiltré":
            return [("Champ d'atténuation (Infiltré)", {"competences": {"Discrétion": ["avantage"]}})]
        return []

    def armor_model_text(self, name: str) -> str:
        """Description du modèle avec les valeurs du personnage."""
        lvl = self.armorer_level() or 3
        intm = self.mod("Intelligence")
        dd = 8 + self.prof + intm
        base = next((m for m in MODELS if norm(name).startswith(norm(m))), name)
        perfected = lvl >= 15
        if base == "Gardien":
            txt = ("Gantelets tonnants : arme courante de corps à corps, 1d8 dégâts de tonnerre (Intelligence possible "
                   "pour l'attaque et les dégâts) ; une créature touchée a le désavantage aux jets d'attaque contre "
                   "d'autres cibles que vous jusqu'au début de votre prochain tour. Champ défensif : action bonus, {} PV "
                   "temporaires, {} fois par repos long.".format(lvl, self.prof))
            if perfected:
                txt += (" Armure parachevée : quand une créature de taille TG ou moins termine son tour à 9 m de vous, "
                        "réaction : JS de Force DD {} ou elle est attirée de 9 m vers vous (et attaquée si elle arrive "
                        "à 1,50 m), {} fois par repos long.".format(dd, max(1, intm)))
            return txt
        if base == "Infiltré":
            txt = ("Lance-foudre : arme courante à distance (27 / 90 m), 1d6 dégâts de foudre (Intelligence possible) ; "
                   "une fois par tour, +1d6 foudre sur un coup réussi. Pas motorisés : +1,50 m de vitesse. Champ "
                   "d'atténuation : avantage en Discrétion (annule le désavantage de l'armure).")
            if perfected:
                txt += (" Armure parachevée : une créature touchée par le lance-foudre scintille jusqu'au début de "
                        "votre prochain tour — la prochaine attaque contre elle a l'avantage et inflige 1d6 foudre de "
                        "plus si elle touche.")
            return txt
        return ""
