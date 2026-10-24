"""
Maîtrises d'armes et d'armures (v43) — sources, multiclassage, équipement non maîtrisé, blocage de la magie.

Règles (Manuel des joueurs) :
  - classe de départ : toutes ses maîtrises ; classe ajoutée en multiclassage : seulement celles de la table du
    multiclassage (rules.MULTICLASS_PROFS) ;
  - certaines sous-classes accordent des maîtrises (Domaine de la Guerre, Collège de la Vaillance, Lame maudite…) ;
  - armure ou bouclier NON maîtrisé : désavantage aux tests de caractéristique, jets de sauvegarde et jets
    d'attaque basés sur la Force ou la Dextérité, et IMPOSSIBLE de lancer des sorts ;
  - arme non maîtrisée : le bonus de maîtrise ne s'ajoute pas au jet d'attaque.
"""
from __future__ import annotations

from typing import Optional

from . import rules as R
from .data_loader import FEAT_PROFICIENCIES
from .rules import norm

FEAT_SOURCE = "Accordé par le Don : {}"

ARMOR_WARNING = ("Attention : Vous ne maîtrisez pas cette armure ! Vous avez un désavantage aux jets de "
                 "caractéristique et jets d'attaque basés sur la Force ou la Dextérité.")
SHIELD_WARNING = ("Attention : Vous ne maîtrisez pas ce bouclier ! Vous avez un désavantage aux jets de "
                  "caractéristique et jets d'attaque basés sur la Force ou la Dextérité.")
WEAPON_WARNING = "Arme non maîtrisée : Le bonus de maîtrise ne s'applique pas au jet de toucher."
CAST_BLOCKED = "Impossible de lancer un sort tout en portant une armure non maîtrisée."

# (classe, fragment de sous-classe, niveau, armures, armes)
SUBCLASS_PROFS = [
    ("Clerc", "guerre", 1, ["Armures lourdes"], ["Armes de guerre"]),
    ("Clerc", "tempete", 1, ["Armures lourdes"], ["Armes de guerre"]),
    ("Clerc", "vie", 1, ["Armures lourdes"], []),
    ("Clerc", "nature", 1, ["Armures lourdes"], []),
    ("Clerc", "forge", 1, ["Armures lourdes"], []),
    ("Clerc", "ordre", 1, ["Armures lourdes"], []),
    ("Clerc", "crepuscule", 1, ["Armures lourdes"], ["Armes de guerre"]),
    ("Barde", "vaillance", 3, ["Armures intermédiaires", "Boucliers"], ["Armes de guerre"]),
    ("Barde", "epees", 3, ["Armures intermédiaires"], ["Cimeterres"]),
    ("Occultiste", "lame maudite", 1, ["Armures intermédiaires", "Boucliers"], ["Armes de guerre"]),
    ("Magicien", "chantelame", 2, ["Armures légères"], []),
    ("Artificier", "armurier", 3, ["Armures lourdes"], []),
    ("Artificier", "forgeur", 3, [], ["Armes de guerre"]),
]


class ProficiencyMixin:
    # ------------------------------------------------------------------ sources
    def proficiency_sources(self) -> list[dict]:
        """[{source, armures, armes, mode}] : classe de départ, multiclassage, sous-classes, espèce."""
        out = []
        for i, e in enumerate(self.ch.classes):
            if i == 0:
                info = self.db.start_info(e["nom"])
                out.append({"source": "{} (classe de départ)".format(e["nom"]), "classe": e["nom"],
                            "armures": [a for a in info["armures"] if norm(a) != "aucune"], "armes": list(info["armes"]),
                            "mode": "depart"})
            else:
                arm, wpn = R.MULTICLASS_PROFS.get(e["nom"], ([], []))
                out.append({"source": "{} (multiclassage)".format(e["nom"]), "classe": e["nom"], "armures": list(arm),
                            "armes": list(wpn), "mode": "multiclassage"})
        for cls, frag, lvl, arm, wpn in SUBCLASS_PROFS:
            e = self.ch.find_class(cls)
            if e and e["niveau"] >= lvl and frag in norm(e.get("sous_classe", "")):
                out.append({"source": "{} — {}".format(cls, e["sous_classe"]), "classe": cls, "armures": list(arm),
                            "armes": list(wpn), "mode": "sous_classe"})
        for feat in self.chosen_feats():                  # v45 : dons de maîtrise d'armures
            arm, wpn = FEAT_PROFICIENCIES.get(norm(feat), ([], []))
            if arm or wpn:
                out.append({"source": "Don : {}".format(feat), "classe": "", "don": feat, "armures": list(arm),
                            "armes": list(wpn), "mode": "don"})
        sub = self.subrace()
        race_arm = ["Armures légères", "Armures intermédiaires"] if sub and "montagnes" in norm(sub["nom"]) else []
        race_wpn = self.racial_weapon_proficiencies()
        if race_arm or race_wpn:
            out.append({"source": "Espèce : {}".format(sub["nom"] if sub and race_arm else self.ch.race),
                        "classe": "", "armures": race_arm, "armes": race_wpn, "mode": "espece"})
        return out

    def extra_armor_profs(self) -> list[str]:
        return [a for s in self.proficiency_sources() if s["mode"] in ("sous_classe", "don") for a in s["armures"]]

    def extra_weapon_profs(self) -> list[str]:
        return [a for s in self.proficiency_sources() if s["mode"] in ("sous_classe", "don") for a in s["armes"]]

    def proficiency_origin_labels(self, kind: str = "armures") -> list[str]:
        """v45 : maîtrises du personnage avec leur origine quand elle vient d'un don :
        « Armures lourdes (Accordé par le Don : Maîtrise des armures lourdes) »."""
        summ = self.proficiency_summary()
        by_feat: dict[str, str] = {}
        others = {p for s in summ["sources"] if s["mode"] != "don" for p in s[kind]}
        for s in summ["sources"]:
            if s["mode"] == "don":
                for p in s[kind]:
                    if p not in others:
                        by_feat.setdefault(p, s["don"])
        return [p + (" ({})".format(FEAT_SOURCE.format(by_feat[p])) if p in by_feat else "") for p in summ[kind]]

    def proficiency_summary(self) -> dict:
        armures = list(dict.fromkeys(self.armor_proficiencies()))
        armes = list(dict.fromkeys(self.weapon_proficiencies()))
        return {"armures": armures, "armes": armes, "sources": self.proficiency_sources()}

    def shield_proficient(self) -> bool:
        return any("bouclier" in norm(p) for p in self.armor_proficiencies())

    # ------------------------------------------------------------------ équipement porté
    def unproficient_gear(self) -> list[dict]:
        """Armure / bouclier portés sans maîtrise : [{type, nom, message}]."""
        out = []
        armor = self.db.armors.get(self.ch.armure.get("nom", ""))
        if armor and armor.get("categorie") != "aucune" and not R.armor_proficient(armor["categorie"],
                                                                                    self.armor_proficiencies()):
            out.append({"type": "armure", "nom": armor["nom"], "message": ARMOR_WARNING,
                        "affichage": self.ch.armure.get("affichage") or armor["nom"]})
        if self.ch.armure.get("bouclier") and not self.shield_proficient():
            name = self.ch.armure.get("bouclier") if isinstance(self.ch.armure.get("bouclier"), str) else "Bouclier"
            out.append({"type": "bouclier", "nom": name, "message": SHIELD_WARNING,
                        "affichage": self.ch.armure.get("bouclier_affichage") or name})
        return out

    def weapon_unproficient(self, slot: dict) -> bool:
        st = self.weapon_stats(slot) if slot and slot.get("nom") else None
        return bool(st) and not st["maitrise"] and st["nom"] != "Mains nues"

    def item_proficiency_warning(self, name: str) -> str:
        """Avertissement d'un objet ÉQUIPÉ (inventaire, mannequin) : armure, bouclier ou arme non maîtrisés."""
        for g in self.unproficient_gear():
            if name in (g["nom"], g.get("affichage")) or (g["type"] == "bouclier" and "bouclier" in norm(name)):
                return g["message"]
        for slot in list(self.ch.armes_cac) + list(self.ch.armes_distance):
            if name in (slot.get("nom"), slot.get("affichage")) and self.weapon_unproficient(slot):
                return WEAPON_WARNING
        return ""

    # ------------------------------------------------------------------ magie
    def spell_block_reason(self) -> Optional[tuple[str, str]]:
        """(« forme » | « armure », message) si aucun sort ne peut être lancé, sinon None."""
        if self.ch.forme_active and (self.ch.forme_type == "metamorphose" or self.class_level("Druide") < 18):
            return "forme", "Sous forme animale, vous ne pouvez pas lancer de sorts (la concentration en cours est " \
                            "maintenue)."
        if self.unproficient_gear():
            return "armure", CAST_BLOCKED
        return None
