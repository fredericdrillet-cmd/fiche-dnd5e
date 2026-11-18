"""
Aptitudes de classe appliquées automatiquement (v52) — 2014 et 2024, logique pure mélangée à Engine.

Dès qu'une aptitude est débloquée par le niveau, son effet chiffré est appliqué à la fiche :
- maîtrises de jets de sauvegarde (Âme diamantée, Survivant discipliné, Esprit fuyant) ;
- avantage aux JS de Dextérité (Sens du danger) ;
- vitesse (Nomade du rôdeur 2024), vision aveugle (Sens bestiaux) ;
- Corps et esprit du moine 2024 (+4 Dex et Sag, maximum 25) ;
- dés ajoutés aux dégâts des armes : Châtiment divin amélioré / Frappes radiantes (toujours), Frappe divine,
  Frappes bénies, Fureur élémentaire (une fois par tour, proposés dans la fenêtre de dégâts) ;
- Incantation puissante 2024 (mod. de Sagesse aux tours de magie de clerc ou de druide) ;
- expertises 2024 (Explorateur habile, Érudit), compétence de Connaissance primitive (Barbare 2024) ;
- ressources rendues à l'initiative (Inspiration supérieure, Rage persistante, Concentration parfaite, Yo
  perfectionné) ou au repos court (Restauration d'ensorceleur 2024).
Les options du Chaudron de Tasha (« option tasha ») ne s'appliquent jamais d'office.
"""
from __future__ import annotations

from .rules import ABILITIES, norm

BARBARIAN_SKILLS = ["Dressage", "Athlétisme", "Intimidation", "Nature", "Perception", "Survie"]
BLESSED = {"Clerc": ("frappes_benies", "Frappes bénies (Clerc 2024)", 7, 14, "radiants ou nécrotiques", {
    "Frappe divine": "Une fois par tour, quand vous touchez avec une arme : 1d8 dégâts radiants ou nécrotiques (2d8 au "
                     "niveau 14).",
    "Incantation puissante": "Ajoutez votre modificateur de Sagesse aux dégâts de vos tours de magie de clerc (au "
                             "niveau 14 : PV temporaires égaux au double)."}),
    "Druide": ("fureur_elementaire", "Fureur élémentaire (Druide 2024)", 7, 15, "froid, feu, foudre ou tonnerre", {
        "Frappe primitive": "Une fois par tour, quand vous touchez avec une arme ou une attaque de bête : 1d8 dégâts "
                            "de froid, de feu, de foudre ou de tonnerre (2d8 au niveau 15).",
        "Incantation puissante": "Ajoutez votre modificateur de Sagesse aux dégâts de vos tours de magie de druide "
                                 "(au niveau 15 : portée de 90 m au lieu de 9 m et plus)."})}


class ClassAutoMixin:
    """Mélangé à Engine : utilise class_level, unlocked_feature_names, sheet_edition, ch, prof, mod."""

    def _feat_on(self, *names: str) -> bool:
        have = [n for n in self.unlocked_feature_names() if "option tasha" not in n]
        return any(n == x or n.startswith(x + " (") for x in map(norm, names) for n in have)

    @property
    def _ed24(self) -> bool:
        return getattr(self, "sheet_edition", 2014) == 2024

    # ------------------------------------------------------------------ jets de sauvegarde
    def auto_save_profs(self) -> set[str]:
        out = set()
        if self._feat_on("ame diamantee", "ame de diamant", "survivant discipline"):
            out |= set(ABILITIES)
        if self._feat_on("esprit fuyant"):
            out |= {"Sagesse", "Charisme"} if self._ed24 else {"Sagesse"}
        return out

    def class_modifiers(self) -> list[tuple[str, dict]]:
        out = []
        if self._feat_on("sens du danger"):
            out.append(("Sens du danger", {"js": {"Dextérité": ["avantage"]}}))
        return out

    # ------------------------------------------------------------------ vitesse, sens, caractéristiques
    def class_speed_bonus(self, armor_category: str) -> float:
        if self._ed24 and self.class_level("Rôdeur") >= 6 and armor_category != "lourde":
            return 3.0                                    # Nomade (Rôdeur 2024)
        return 0.0

    def class_senses(self) -> list[str]:
        out = []
        if self._ed24 and self.class_level("Rôdeur") >= 18:
            out.append("Vision aveugle 9 m (Sens bestiaux)")
        return out

    def class_score_bonus(self, ab: str) -> tuple[int, int]:
        """(bonus, plafond) des aptitudes de niveau 20 qui dépassent 20 (Champion primitif, Corps et esprit)."""
        if ab in ("Force", "Constitution") and self.class_level("Barbare") >= 20:
            return 4, 25 if self._ed24 else 24
        if self._ed24 and ab in ("Dextérité", "Sagesse") and self.class_level("Moine") >= 20:
            return 4, 25
        return 0, 20

    # ------------------------------------------------------------------ compétences
    def class_option_sets(self) -> list[dict]:
        out = []
        if self._ed24 and self.class_level("Barbare") >= 3:
            key = "connaissance_primitive"
            out.append({"key": key, "label": "Connaissance primitive (Barbare 2024) : compétence",
                        "total": 1, "options": {n: "" for n in BARBARIAN_SKILLS},
                        "chosen": list((self.ch.options_classe or {}).get(key, []))[:1]})
        if self._ed24:
            for cls, (key, label, lvl, _, _, options) in BLESSED.items():
                if self.class_level(cls) >= lvl:
                    out.append({"key": key, "label": label, "total": 1, "options": dict(options),
                                "chosen": list((self.ch.options_classe or {}).get(key, []))[:1]})
        return out

    def class_skill_grants(self) -> set[str]:
        if self._ed24 and self.class_level("Barbare") >= 3:
            return set((self.ch.options_classe or {}).get("connaissance_primitive", [])[:1])
        return set()

    def class_extra_expertise(self) -> int:
        n = 0
        if self._ed24 and self._feat_on("explorateur habile"):
            n += 1
        if self._ed24 and self.class_level("Magicien") >= 2:
            n += 1                                        # Érudit
        return n

    # ------------------------------------------------------------------ dégâts
    def _blessed_choice(self, cls: str) -> str:
        if not self._ed24 or cls not in BLESSED or self.class_level(cls) < BLESSED[cls][2]:
            return ""
        picked = (self.ch.options_classe or {}).get(BLESSED[cls][0], [])
        return picked[0] if picked else ""

    def class_weapon_riders(self, slot: dict) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """([(source, dés)] toujours ajoutés, [(source, dés)] une fois par tour) aux dégâts d'une arme."""
        always, once = [], []
        w = self.db.weapons.get(slot.get("nom", ""), {})
        melee = w.get("type") == "cac"
        if melee and self._feat_on("chatiment divin ameliore", "frappes radiantes"):
            always.append(("Frappes radiantes (radiants)" if self._ed24 else "Châtiment divin amélioré (radiants)",
                           "1d8"))
        clerc = self.class_level("Clerc")
        if not self._ed24 and clerc >= 8 and self._feat_on("frappe divine"):
            once.append(("Frappe divine (1/tour)", "{}d8".format(2 if clerc >= 14 else 1)))
        for cls, (key, label, lvl, lvl2, types, _) in BLESSED.items():
            choice = self._blessed_choice(cls)
            if choice.startswith("Frappe"):
                n = 2 if self.class_level(cls) >= lvl2 else 1
                once.append(("{} (1/tour, {})".format(choice, types), "{}d8".format(n)))
        return always, once

    def class_cantrip_bonus(self, spell: dict) -> list[tuple[str, int]]:
        out = []
        for cls in ("Clerc", "Druide"):
            if self._blessed_choice(cls) == "Incantation puissante" and cls in spell.get("classes", []):
                out.append(("Incantation puissante (Sagesse)", self.mod("Sagesse")))
                break
        return out

    # ------------------------------------------------------------------ ressources rendues
    def initiative_recovery(self) -> list[str]:
        """Appelé quand l'initiative est jetée : ressources rendues automatiquement. Renvoie les messages."""
        msgs = []
        used = self.ch.ressources_utilisees
        tr = {t["key"]: t for t in self.resource_trackers()}

        def refill_to(key: str, keep: int, label: str):
            t = tr.get(key)
            if not t or t["total"] is None:
                return
            left = t["total"] - used.get(key, 0)
            if left < keep:
                used[key] = max(0, t["total"] - keep)
                msgs.append(label)

        bard = self.class_level("Barde")
        if self._ed24 and bard >= 18:
            refill_to("inspiration", 2, "Inspiration supérieure : 2 dés d'inspiration")
        elif not self._ed24 and bard >= 20:
            refill_to("inspiration", 1, "Inspiration supérieure : 1 dé d'inspiration")
        monk = self.class_level("Moine")
        if self._ed24 and monk >= 15:
            refill_to("ki", 4, "Concentration parfaite : 4 points de concentration")
        elif not self._ed24 and monk >= 20:
            refill_to("ki", 4, "Yo perfectionné : 4 points de ki")
        if self.class_level("Barbare") >= 15 and self._ed24 and used.get("rage") and \
                not used.get("rage_persistante"):
            used["rage"] = 0
            used["rage_persistante"] = 1
            msgs.append("Rage persistante : rages récupérées")
        return msgs

    def short_rest_class_recovery(self) -> list[str]:
        msgs = []
        sorc = self.class_level("Ensorceleur")
        used = self.ch.ressources_utilisees
        if self._ed24 and sorc >= 5 and used.get("sorcellerie") and not used.get("restauration_ensorceleur"):
            back = min(used["sorcellerie"], sorc // 2)
            used["sorcellerie"] -= back
            used["restauration_ensorceleur"] = 1
            msgs.append("Restauration d'ensorceleur : {} point(s) de sorcellerie".format(back))
        return msgs

    def class_flag_trackers(self) -> list[dict]:
        """Indicateurs « déjà utilisé » (internes) des récupérations limitées à une fois par repos long."""
        out = []
        if self._ed24 and self.class_level("Barbare") >= 15:
            out.append({"key": "rage_persistante", "label": "Rage persistante", "total": 1, "kind": "sursaut",
                        "recover": "repos long", "where": "interne", "de": "",
                        "info": "Rages récupérées à l'initiative — une fois par repos long"})
        if self._ed24 and self.class_level("Ensorceleur") >= 5:
            out.append({"key": "restauration_ensorceleur", "label": "Restauration d'ensorceleur", "total": 1,
                        "kind": "sursaut", "recover": "repos long", "where": "interne", "de": "",
                        "info": "Points de sorcellerie récupérés au repos court — une fois par repos long"})
        return out

    # ================================================================== sous-classes (2014 et 2024)
    def _has(self, *frags: str) -> bool:
        names = [n for n in self.unlocked_feature_names() if "option tasha" not in n]
        return any(norm(f) in n for f in frags for n in names)

    def crit_min(self) -> int:
        """Plus petit résultat naturel critique des attaques d'arme (Champion : 19, puis 18)."""
        if self._has("critique superieur"):
            return 18
        if self._has("critique ameliore"):
            return 19
        return 20

    def subclass_initiative(self) -> tuple[list[tuple[str, int]], list[str]]:
        terms, adv = [], []
        if self._has("embuscade effrayante"):            # 2014 « Embusqué redoutable » : core/initiative.py
            terms.append(("Embuscade effrayante (Sagesse)", self.mod("Sagesse")))
        if self._ed24 and self._has("athlete accompli"):
            adv.append("Athlète accompli")
        if self._ed24 and self.class_level("Roublard") >= 3 and self._has("assassinat"):
            adv.append("Assassinat")
        return terms, adv

    def subclass_save_profs(self) -> set[str]:
        if self._has("mental d'acier", "esprit de fer"):
            have = {ab for ab, v in self.ch.sauvegardes.items() if v}
            return {"Sagesse"} if "Sagesse" not in have else {"Intelligence"}
        return set()

    FIENDISH_TYPES = ["acide", "contondant", "feu", "foudre", "froid", "nécrotique", "perforant", "poison",
                      "psychique", "radiant", "tonnerre", "tranchant"]

    def subclass_modifiers(self) -> list[tuple[str, dict]]:
        out = []
        if self._has("defenses psychiques", "bouclier mental"):
            out.append(("Défenses psychiques" if self._has("defenses psychiques") else "Bouclier mental",
                        {"resistances": ["psychique"]}))
        if self._has("ame radieuse", "ame rayonnante"):
            out.append(("Âme radieuse", {"resistances": ["radiant"]}))
        if self._has("resistance fielonne"):
            pick = (self.ch.options_classe or {}).get("resistance_fielonne", [])[:1]
            if pick:
                out.append(("Résistance fiélonne", {"resistances": pick}))
        if self._has("aura de celerite", "aura d'alacrite"):
            out.append(("Aura de célérité", {"vitesse_bonus": 3.0}))
        return out

    def subclass_option_sets(self) -> list[dict]:
        out = []
        if self._has("resistance fielonne"):
            out.append({"key": "resistance_fielonne", "label": "Résistance fiélonne (type de dégâts, après un repos)",
                        "total": 1, "options": {t: "" for t in self.FIENDISH_TYPES},
                        "chosen": list((self.ch.options_classe or {}).get("resistance_fielonne", []))[:1]})
        bard = self.ch.find_class("Barde")
        if bard and bard["niveau"] >= 3 and "savoir" in norm(bard.get("sous_classe", "")):
            out.append({"key": "savoir_competences", "label": "Maîtrises supplémentaires (Collège du savoir)",
                        "total": 3, "options": {s["nom"]: "" for s in self.db.skills},
                        "chosen": list((self.ch.options_classe or {}).get("savoir_competences", []))[:3]})
        return out

    def subclass_skill_grants(self) -> set[str]:
        out = set((self.ch.options_classe or {}).get("savoir_competences", [])[:3]) if any(
            s["key"] == "savoir_competences" for s in self.subclass_option_sets()) else set()
        if self._has("instruments de misericorde", "instrument de charite"):
            out |= {"Perspicacité", "Médecine"}
        return out

    def subclass_darkvision(self) -> float:
        """Vision dans le noir accordée (Vision ombreuse : 18 m, ou +18 m en 2024 / +9 m en 2014 si déjà acquise)."""
        return 18.0 if self._has("vision ombreuse", "vision des ombres") else 0.0

    def subclass_unarmored(self) -> dict:
        """Défenses sans armure de sous-classe {libellé: [(terme, valeur)]} (Pirouettes éblouissantes)."""
        if self._ed24 and self._has("pirouettes eblouissantes") and not self.ch.armure.get("bouclier"):
            return {"Pirouettes éblouissantes (barde)": [("10", 10), ("Dex", self.mod("Dextérité")),
                                                         ("Cha", self.mod("Charisme"))]}
        return {}

    def life_disciple_bonus(self, spell: dict, slot_level: int) -> int:
        """Disciple de la vie : +2 + niveau du sort aux soins d'un sort de niveau 1+."""
        if int(spell.get("niveau") or 0) >= 1 and self._has("disciple de la vie"):
            return 2 + int(slot_level or spell["niveau"])
        return 0

    def subclass_weapon_riders(self) -> list[tuple[str, str]]:
        """Dés ajoutés une fois par tour (Fureur divine du Zélote pendant la rage)."""
        out = []
        barb = self.class_level("Barbare")
        if barb >= 3 and self._has("fureur divine") and "rage" in (self.ch.effets_actifs or []):
            out.append(("Fureur divine (1/tour, radiants ou nécrotiques)", "1d6+{}".format(barb // 2)))
        return out
