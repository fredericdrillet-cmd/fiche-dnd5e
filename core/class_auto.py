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


# options de Tasha qui REMPLACENT une aptitude : jamais appliquées d'office, seulement si le joueur les choisit
TASHA_REPLACING = ("frappes benies", "ennemi favori", "explorateur expert", "conscience primordiale",
                   "voile de la nature", "vagabond", "infatigable")
# option choisie -> (classe, aptitudes remplacées, libellé de ce qui est remplacé)
TASHA_REPLACEMENTS = {
    "ennemi favori": ("Rôdeur", ("ennemi jure",), "Ennemi juré"),
    "explorateur expert": ("Rôdeur", ("explorateur-ne", "explorateur ne"), "Explorateur-né"),
    "conscience primordiale": ("Rôdeur", ("conscience primitive",), "Conscience primitive"),
    "voile de la nature": ("Rôdeur", ("camouflage",), "Camouflage"),
    "frappes benies": ("Clerc", ("frappe divine", "incantation puissante"), "Frappe divine ou Incantation puissante"),
}
FOLLOWS = {"vagabond": "explorateur expert", "infatigable": "explorateur expert"}


class ClassAutoMixin:
    """Mélangé à Engine : utilise class_level, unlocked_feature_names, sheet_edition, ch, prof, mod."""

    def tasha_on(self) -> bool:
        """Règle de la table « Options de Tasha (ajouts) » active sur une fiche 2014."""
        return getattr(self, "sheet_edition", 2014) == 2014 and self.rule_active("options_tasha")

    def feature_allowed(self, name: str) -> bool:
        """Aptitude prise en compte : toute aptitude normale (sauf si une option de Tasha choisie la remplace) ;
        une option de Tasha si elle s'ajoute, ou si c'est un remplacement choisi par le joueur."""
        n = norm(name)
        if "option tasha" not in n:
            return not self.feature_replaced(n)
        if not self.tasha_on():
            return False
        rep = next((r for r in TASHA_REPLACING if n.startswith(r)), "")
        if not rep:
            return True
        return FOLLOWS.get(rep, rep) in self.tasha_chosen()

    def tasha_chosen(self) -> list[str]:
        return [c for c in (self.ch.tasha_remplacements or []) if c in TASHA_REPLACEMENTS] if self.tasha_on() else []

    def feature_replaced(self, n: str) -> bool:
        """Aptitude 2014 remplacée par une option de Tasha que le joueur a choisie."""
        for cle in self.tasha_chosen():
            if any(n == o or n.startswith(o + " ") for o in TASHA_REPLACEMENTS[cle][1]):
                return True
        return False

    def tasha_replacement_options(self, class_name: str) -> list[dict]:
        """Options de Tasha qui remplacent une aptitude de cette classe : [{cle, nom, remplace, actif}]."""
        if not self.tasha_on():
            return []
        out = []
        for cle, (cls, _, label) in TASHA_REPLACEMENTS.items():
            if cls == class_name and self.class_level(cls):
                out.append({"cle": cle, "nom": cle.capitalize().replace("Frappes benies", "Frappes bénies"),
                            "remplace": label, "actif": cle in self.tasha_chosen()})
        return out

    def set_tasha_replacement(self, cle: str, on: bool) -> None:
        chosen = [c for c in (self.ch.tasha_remplacements or []) if c != cle]
        self.ch.tasha_remplacements = chosen + ([cle] if on and cle in TASHA_REPLACEMENTS else [])

    def has_tasha(self, fragment: str) -> bool:
        frag = norm(fragment)
        return self.tasha_on() and any(frag in n and "option tasha" in n and self.feature_allowed(n)
                                       for n in self.unlocked_feature_names())

    def _feat_on(self, *names: str) -> bool:
        have = [n for n in self.unlocked_feature_names() if self.feature_allowed(n)]
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
        if self.has_tasha("vagabond") and armor_category != "lourde":
            return 1.5                                    # Vagabond (Explorateur expert, Tasha)
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
        barb = self.class_level("Barbare")
        if barb >= 3 and (self._ed24 or self.has_tasha("connaissance primitive")):
            key = "connaissance_primitive"
            n = 2 if (not self._ed24 and barb >= 10) else 1                # Tasha : 2e compétence au niveau 10
            out.append({"key": key, "label": "Connaissance primitive ({}) : compétence{}".format(
                "Barbare 2024" if self._ed24 else "option de Tasha", "s" * (n > 1)),
                        "total": n, "options": {s: "" for s in BARBARIAN_SKILLS},
                        "chosen": list((self.ch.options_classe or {}).get(key, []))[:n]})
        if self.has_tasha("arme dediee"):
            from . import rules as R
            names = [w["nom"] for w in self.db.weapons.values() if w["nom"] != "Mains nues"
                     and not {"lourde", "speciale"} & {norm(p) for p in w.get("proprietes", [])}
                     and R.weapon_proficient(w["nom"], w["categorie"], self.weapon_proficiencies())]
            out.append({"key": "arme_dediee", "label": "Arme dédiée (option de Tasha) : arme de moine",
                        "total": 1, "options": {n: "" for n in sorted(names)},
                        "chosen": list((self.ch.options_classe or {}).get("arme_dediee", []))[:1]})
        if self._ed24:
            for cls, (key, label, lvl, _, _, options) in BLESSED.items():
                if self.class_level(cls) >= lvl:
                    out.append({"key": key, "label": label, "total": 1, "options": dict(options),
                                "chosen": list((self.ch.options_classe or {}).get(key, []))[:1]})
        return out

    def class_skill_grants(self) -> set[str]:
        barb = self.class_level("Barbare")
        if barb >= 3 and (self._ed24 or self.has_tasha("connaissance primitive")):
            n = 2 if (not self._ed24 and barb >= 10) else 1
            return set((self.ch.options_classe or {}).get("connaissance_primitive", [])[:n])
        return set()

    def dedicated_weapon(self) -> str:
        """Arme dédiée (Moine, option de Tasha) : arme choisie qui devient une arme de moine."""
        if not self.has_tasha("arme dediee"):
            return ""
        picked = (self.ch.options_classe or {}).get("arme_dediee", [])
        return picked[0] if picked else ""

    def tasha_extra_spells(self, class_name: str) -> list[dict]:
        """Sorts ajoutés à la liste de la classe par l'option « Sorts … supplémentaires » de Tasha."""
        import re as _re
        if not self.tasha_on():
            return []
        e = self.ch.find_class(class_name)
        if not e:
            return []
        out = []
        for f in self.features(e):
            n = norm(f["nom"])
            if not (f.get("debloque") and "option tasha" in n and "supplementaires" in n and n.startswith("sorts")):
                continue
            for piece in _re.split(r"[,;:.]|\bet\b|\(|\)", f.get("description", "")):
                sp = self.db.find_spell(piece.strip())
                if sp and sp not in out:
                    out.append(sp)
        return out

    def class_extra_expertise(self) -> int:
        n = 1 if self.has_tasha("explorateur expert") else 0       # Tasha : expertise d'Explorateur expert
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
        if self.has_tasha("frappes benies"):              # Tasha (remplace Frappe divine / Incantation puissante)
            once.append(("Frappes bénies (1/tour, radiants)", "1d8"))
        if self.ch.concentration == "Ennemi favori" and self.has_tasha("ennemi favori"):
            r = self.class_level("Rôdeur")
            once.append(("Ennemi favori (1/tour, cible marquée)", "1d8" if r >= 14 else "1d6" if r >= 6 else "1d4"))
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
        if self._ed24 and monk >= 2 and used.get("ki") and not used.get("metabolisme"):   # Métabolisme surnaturel
            import random as _random
            die = self.martial_arts_die(monk)
            gained = self.heal(_random.randint(1, die) + monk)
            used["ki"] = 0
            used["metabolisme"] = 1
            msgs.append("Métabolisme surnaturel : concentration récupérée, +{} PV".format(gained))
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
        if self._ed24 and self.class_level("Moine") >= 2:
            out.append({"key": "metabolisme", "label": "Métabolisme surnaturel", "total": 1, "kind": "sursaut",
                        "recover": "repos long", "where": "interne", "de": "",
                        "info": "À l'initiative : concentration récupérée et PV — une fois par repos long"})
        if self._ed24 and self.class_level("Ensorceleur") >= 5:
            out.append({"key": "restauration_ensorceleur", "label": "Restauration d'ensorceleur", "total": 1,
                        "kind": "sursaut", "recover": "repos long", "where": "interne", "de": "",
                        "info": "Points de sorcellerie récupérés au repos court — une fois par repos long"})
        return out

    # ================================================================== sous-classes (2014 et 2024)
    def _has(self, *frags: str) -> bool:
        names = [n for n in self.unlocked_feature_names() if self.feature_allowed(n)]
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

    # ================================================================== v52 : immunités aux états
    def condition_immunities(self) -> dict[str, str]:
        """États qui ne peuvent pas vous affecter : {clé d'effet: source} (2014 et 2024)."""
        out = {}
        if self._has("aura de devotion"):
            out["charme"] = "Aura de dévotion"
        if self._has("aura de courage"):
            out["effraye"] = "Aura de courage"
        if self._has("purete du corps"):
            out.update(empoisonne="Pureté du corps", malade="Pureté du corps")
        if self._has("protege de dame nature"):
            out["empoisonne"] = "Protégé de dame Nature"
            if not self._ed24:
                out["malade"] = "Protégé de dame Nature"
        if self._has("rage aveugle") and "rage" in self.active_effect_keys():
            out.setdefault("charme", "Rage aveugle (en rage)")
            out.setdefault("effraye", "Rage aveugle (en rage)")
        return out

    def effect_blocked(self, key: str) -> str:
        """Raison pour laquelle un état ne peut pas être ajouté ("" s'il peut l'être)."""
        src = self.condition_immunities().get(key)
        return "Immunité : {} — l'état « {} » ne vous affecte pas.".format(src, key.replace("_", " ")) if src else ""

    def purge_immune_conditions(self) -> list[str]:
        """Retire les états auxquels vous êtes (devenu) immunisé (ex. Rage aveugle en entrant en rage)."""
        imm = self.condition_immunities()
        gone = [k for k in self.ch.effets_actifs if k in imm]
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if k not in imm]
        return gone

    # ================================================================== v52 : options de Tasha (ajouts)
    def harness_divine_power(self) -> str:
        """Canalisation / Exploitation du pouvoir divin : rend le plus haut emplacement dépensé autorisé."""
        import math
        limit = math.ceil(self.prof / 2)
        for lvl in range(min(limit, 9), 0, -1):
            if self.ch.emplacements_utilises[lvl - 1] > 0:
                self.ch.emplacements_utilises[lvl - 1] -= 1
                return "emplacement de niveau {} récupéré".format(lvl)
        return "aucun emplacement dépensé de niveau {} ou moins à récupérer".format(limit)

    # ------------------------------------------------------------------ v52 : remplacements de Tasha choisis
    PRIMAL_AWARENESS = [(3, "Communication avec les animaux"), (5, "Sens animal"), (9, "Communication avec les plantes"),
                        (13, "Localisation de créature"), (17, "Communion avec la nature")]

    def tasha_granted_spells(self) -> list[dict]:
        """Conscience primordiale : sorts toujours préparés, chacun lançable une fois sans emplacement par repos
        long (format de granted_spells)."""
        if not self.has_tasha("conscience primordiale"):
            return []
        from . import rules as R
        lvl = self.class_level("Rôdeur")
        m = self.mod("Sagesse")
        out = []
        for need, name in self.PRIMAL_AWARENESS:
            spell = self.db.find_spell(name)
            if lvl < need or not spell:
                continue
            key = "tasha:conscience:" + norm(name).replace(" ", "_")
            left = max(0, 1 - self.resource_used(key))
            out.append({"nom": spell["nom"], "niveau": spell["niveau"], "sort": spell,
                        "usage": "1 fois sans emplacement / repos long — {} / 1 restant ; aussi avec vos emplacements"
                                 .format(left), "source": "Conscience primordiale (Tasha)", "categorie": "Rôdeur",
                        "emplacement": True, "limite": "1", "cle": key, "cible": "", "carac": "Sagesse",
                        "dc": R.spell_save_dc(self.prof, m), "attaque": R.spell_attack_bonus(self.prof, m),
                        "recover": "repos long"})
        return out

    def tasha_trackers(self) -> list[dict]:
        return [{"key": s["cle"], "label": s["nom"], "total": 1, "kind": "sursaut", "recover": "repos long",
                 "where": "interne", "de": "", "info": s["usage"]} for s in self.tasha_granted_spells()]
