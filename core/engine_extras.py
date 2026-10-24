"""
Mécaniques « jeu vidéo » (inspirées de Baldur's Gate 3 / Solasta) branchées sur le moteur de règles 5e :

    - effets actifs (buffs, débuffs, états) et leurs modificateurs (CA, vitesse, notes de jets) ;
    - actions d'arme (bottes PHB 2024 + actions BG3 adaptées) avec DD calculé ;
    - munitions : choix de la munition d'une arme à distance, bonus magique, consommation du stock d'inventaire ;
    - réactions disponibles (attaque d'opportunité, sorts, aptitudes, dons, styles) et réaction du round ;
    - concentration : un seul sort à la fois, lancement d'un sort avec dépense d'emplacement ;
    - repos court / long interactifs : dés de vie, recharges, temps écoulé, rations (règle de survie).

Module pur : l'interface (ui/) appelle ces méthodes ; aucune dépendance Qt. Mixé dans `core.engine.Engine`.
"""
from __future__ import annotations

import random
import re
from typing import Optional

from . import dice as D
from . import effects as FX
from . import mechanics as M
from . import rules as R
from . import weapon_actions as WA
from .rules import norm

START_MINUTES = 8 * 60                      # l'aventure commence le jour 1 à 8 h 00
SHORT_REST_MIN, LONG_REST_MIN = 60, 8 * 60
DAY = 24 * 60

# type de munition attendu par arme (mot-clé recherché dans le nom de l'objet d'inventaire)
AMMO_BY_WEAPON = (("arbalete", "carreau"), ("arc", "fleche"), ("fronde", "bille"), ("sarbacane", "aiguille"),
                  ("mousquet", "balle"), ("pistolet", "balle"))
AMMO_EXCLUDE = ("etui", "carquois", "sacoche", "paquetage")

# réactions d'aptitudes (fragment de nom normalisé -> fiche) ; les autres aptitudes contenant « votre réaction »
# dans leur description sont ajoutées automatiquement.
REACTION_FEATURES = [
    ("projectiles", "🫴", "Une attaque à distance avec une arme vous touche.",
     "Réduisez les dégâts de 1d10 + votre modificateur de Dextérité + votre niveau de moine. S'ils tombent à 0, "
     "vous pouvez attraper le projectile et, pour 1 point de ki, le renvoyer (attaque à distance, portée 6/18 m)."),
    ("esquive instinctive", "🌀", "Un attaquant que vous voyez vous touche avec une attaque.",
     "Les dégâts de cette attaque sont divisés par deux."),
    ("chute ralentie", "🪶", "Vous tombez.", "Réduisez les dégâts de chute de 5 × votre niveau de moine."),
    ("egide projetee", "🛡", "Une créature à 9 m ou moins que vous voyez subit des dégâts.",
     "Votre Égide arcanique absorbe les dégâts à sa place."),
    ("fureur de l'ouragan", "⛈", "Une créature à 1,50 m vous touche.",
     "JS de Dextérité : 2d8 dégâts de foudre ou de tonnerre (moitié en cas de réussite)."),
    ("illumination protectrice", "✨", "Une créature à 9 m vous attaque.",
     "Imposez-lui le désavantage en l'aveuglant d'une lumière divine (créatures immunisées à l'aveuglement exclues)."),
    ("mots cinglants", "🗯", "Une créature à 18 m effectue un jet d'attaque, de dégâts ou un test.",
     "Dépensez une Inspiration bardique : soustrayez le dé au résultat."),
    ("bouclier spirituel", "👻", "Une créature à 9 m subit des dégâts pendant votre rage.",
     "Réduisez ces dégâts de 2d6 (3d6 au niveau 10, 4d6 au niveau 14)."),
    ("comme par hasard", "🎲", "Une créature que vous voyez fait un jet d'attaque, un test ou un JS.",
     "Dépensez 2 points de sorcellerie : ajoutez ou retranchez 1d4 au résultat."),
    ("riposte", "↩", "Une créature rate une attaque au corps à corps contre vous.",
     "Dépensez un dé de supériorité : attaque au corps à corps avec le dé ajouté aux dégâts."),
    ("parade", "🤺", "Une créature vous touche au corps à corps.",
     "Dépensez un dé de supériorité : réduisez les dégâts du dé + votre modificateur de Dextérité."),
]
REACTION_FEATS = [
    ("sentinelle", "🗡", "Une créature à 1,50 m attaque une cible autre que vous.",
     "Attaque d'arme au corps à corps contre elle ; vos attaques d'opportunité réduisent sa vitesse à 0."),
    ("tueur de mages", "🔮", "Une créature à 1,50 m lance un sort.", "Attaque d'arme au corps à corps contre elle."),
    ("maitre des armes d'hast", "🔱", "Une créature entre dans votre allonge.",
     "Attaque d'opportunité avec votre arme d'hast."),
    ("defenseur", "🛡", "Une attaque vous vise.", "Ajoutez votre bonus de maîtrise à votre CA contre cette attaque."),
]
REACTION_STYLES = [
    ("Protection", "🛡", "Une créature que vous voyez attaque une cible autre que vous à 1,50 m (bouclier requis).",
     "Imposez le désavantage au jet d'attaque."),
    ("Interception", "🤚", "Une créature à 1,50 m est touchée (arme ou bouclier en main).",
     "Réduisez les dégâts de 1d10 + votre bonus de maîtrise."),
]


def _batch_memo(fn):
    """Même principe que `engine.memo` : résultat mémorisé pendant un lot de rafraîchissement (Engine.batch)."""
    name = fn.__name__

    def wrapper(self, *args):
        cache = getattr(self, "_memo", None)
        if cache is None:
            return fn(self, *args)
        key = (name, args)
        if key not in cache:
            cache[key] = fn(self, *args)
        return cache[key]
    wrapper.__name__ = name
    wrapper.__doc__ = fn.__doc__
    return wrapper


# Ascendances draconiques (PHB) : couleur -> (type de dégâts, zone du souffle, caractéristique du JS)
DRACONIC = {
    "Noir": ("acide", "ligne de 1,50 × 9 m", "Dextérité"), "Bleu": ("foudre", "ligne de 1,50 × 9 m", "Dextérité"),
    "Airain": ("feu", "ligne de 1,50 × 9 m", "Dextérité"), "Bronze": ("foudre", "ligne de 1,50 × 9 m", "Dextérité"),
    "Cuivre": ("acide", "ligne de 1,50 × 9 m", "Dextérité"), "Or": ("feu", "cône de 4,50 m", "Dextérité"),
    "Vert": ("poison", "cône de 4,50 m", "Constitution"), "Rouge": ("feu", "cône de 4,50 m", "Dextérité"),
    "Argent": ("froid", "cône de 4,50 m", "Constitution"), "Blanc": ("froid", "cône de 4,50 m", "Constitution"),
}
GM_USAGES = ["À volonté", "1 fois par repos long", "1 fois par repos court", "Avec vos emplacements de sort",
             "Usage unique", "Autre (voir note)"]


class ExtrasMixin:
    # ==================================================================================
    # Temps de jeu
    # ==================================================================================
    def time_text(self, minutes: Optional[int] = None) -> str:
        t = START_MINUTES + int(self.ch.temps_minutes if minutes is None else minutes)
        return "Jour {}, {:02d}:{:02d}".format(1 + t // DAY, (t % DAY) // 60, t % 60)      # « Jour 1, 09:00 »

    def advance_time(self, minutes: int) -> None:
        self.ch.temps_minutes = int(self.ch.temps_minutes) + int(minutes)

    # ==================================================================================
    # Effets actifs (barre d'états) : effets ajoutés + traits innés (race, classe)
    # ==================================================================================
    CLASS_INNATE = [("Paladin", 6, "aura_protection"), ("Paladin", 10, "aura_courage")]
    _INNATE_SENTENCE = re.compile(r"\bvous\s+(?:avez|obtenez|gagnez|[êe]tes|b[ée]n[ée]ficiez|rend)\b", re.I)
    _CONDITIONAL = ("tant que", "pendant", "lorsque", "quand ", "si vous", "jusqu'", "par une action", "au choix",
                    "rage", "forme")

    @_batch_memo
    def innate_effects(self) -> dict[str, str]:
        """
        Effets permanents conférés par la race et les aptitudes de classe débloquées : {clé: source}.
        Ils s'affichent en permanence dans la barre d'états (sauf s'ils ont été retirés explicitement).
        """
        out: dict[str, str] = {}
        for cap in self.race_capacities():
            for key in M.innate_from_text(cap.get("description", "")):
                out.setdefault(key, "Trait racial : {} ({})".format(cap["nom"], self.ch.race))
        for e in self.ch.classes:
            for f in self.features(e):
                if not f["debloque"]:
                    continue
                activated = False                 # après une phrase d'activation, la suite décrit un état temporaire
                for sentence in re.split(r"(?<=[.;])\s+", f["description"]):
                    n = norm(sentence)
                    if any(c in n for c in self._CONDITIONAL):
                        activated = True
                        continue
                    if not activated and self._INNATE_SENTENCE.search(sentence):
                        for key in M.innate_from_text(sentence):
                            out.setdefault(key, "Aptitude de classe : {} ({} niv. {})".format(
                                f["nom"], e["nom"], f["niveau"]))
        color = self.ch.ascendance_raciale
        if color in DRACONIC and self.has_breath():      # Résistance draconique selon l'ascendance choisie
            out.setdefault("resist_" + DRACONIC[color][0], "Trait racial : Résistance draconique ({}, dragon {})".format(
                self.ch.race, color.lower()))
        # (Affinité élémentaire de l'ensorceleur : résistance activable en dépensant 1 point -> non permanente)
        for cls, lvl, key in self.CLASS_INNATE:
            if self.class_level(cls) >= lvl:
                out.setdefault(key, "Aptitude de classe : {} niv. {}".format(cls, lvl))
        return {k: v for k, v in out.items() if k in FX.EFFECTS}

    def innate_source(self, key: str) -> str:
        return self.innate_effects().get(key, "")

    @_batch_memo
    def active_effect_keys(self) -> list[str]:
        removed = set(self.ch.effets_retires)
        innate = [k for k in self.innate_effects() if k not in removed]
        conc = ["concentration"] if self.ch.concentration else []        # rappel dans la barre d'états
        return list(dict.fromkeys(conc + innate + [k for k in self.ch.effets_actifs if k in FX.EFFECTS]))

    def add_effect(self, key: str) -> bool:
        if key in self.ch.effets_retires:                 # trait inné retiré puis rétabli
            self.ch.effets_retires = [k for k in self.ch.effets_retires if k != key]
            return True
        if key not in FX.EFFECTS or key in self.ch.effets_actifs:
            return False
        if key.startswith("epuisement_"):                  # un seul niveau d'épuisement à la fois
            self.ch.effets_actifs = [k for k in self.ch.effets_actifs if not k.startswith("epuisement_")]
        self.ch.effets_actifs.append(key)
        return True

    def remove_effect(self, key: str) -> None:
        """Retire un effet ; un trait inné (race / classe) est mémorisé comme « retiré » (l'interface confirme)."""
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if k != key]
        self.ch.effets_potions = [k for k in self.ch.effets_potions if k != key]
        if key == "concentration":                        # retirer l'icône rompt la concentration
            self.break_concentration()
            return
        if self.innate_source(key) and key not in self.ch.effets_retires:
            self.ch.effets_retires.append(key)
        if key in ("forme_sauvage", "metamorphose") and self.ch.forme_active:   # retirer l'état = fin de la forme
            self.end_form()

    def clear_temporary_effects(self) -> int:
        """Bouton « nettoyage » : retire tous les effets ajoutés (les traits innés restent). Renvoie le nombre."""
        n = len(self.ch.effets_actifs)
        self.ch.effets_actifs = []
        self.ch.effets_potions = []
        self.ch.forme_active = ""
        return n

    def _expires(self, key: str, long_rest: bool) -> bool:
        """Un effet temporaire expire-t-il pendant ce repos (1 heure pour un repos court, 8 heures pour un long) ?"""
        if key in self.ch.effets_potions:                  # effet de potion / consommable : 1 heure au plus
            return True
        if key.startswith("epuisement_"):
            return False                                   # géré à part (−1 niveau au repos long)
        d = norm(FX.EFFECTS.get(key, {}).get("duree", ""))
        if any(x in d for x in ("permanente", "guerison", "jusqu'a utilisation", "liberation", "extinction",
                                "abri", "releve", "recuperation", "repere")):
            return long_rest and not any(x in d for x in ("permanente", "guerison"))
        if long_rest:
            return "24 heures" not in d
        short = any(x in d for x in ("minute", "tour", "round", "instantan", "1 heure", "jusqu'au debut",
                                     "jusqu'a la fin", "premier", "duree de la rage", "selon le sort"))
        return short or key in ("rage", "frenesie")

    def effects_ending(self, long_rest: bool) -> list[str]:
        """Noms des effets temporaires qui prendront fin avec ce repos (affichés dans la fenêtre de repos)."""
        conc = ["Concentration : " + self.ch.concentration] if self.ch.concentration else []
        return conc + [FX.EFFECTS[k]["nom"] for k in self.ch.effets_actifs
                       if k in FX.EFFECTS and self._expires(k, long_rest)]

    def purge_after_rest(self, long_rest: bool) -> list[str]:
        """Fin des effets temporaires après un repos (les traits innés et les effets plus longs restent)."""
        gone = [k for k in self.ch.effets_actifs if self._expires(k, long_rest)]
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if k not in gone]
        self.ch.effets_potions = [k for k in self.ch.effets_potions if k not in gone]
        if "forme_sauvage" in gone:
            self.ch.forme_active = ""
        return gone

    def rage_damage_bonus(self) -> int:
        """Bonus de dégâts de rage si l'état « Rage » est actif (selon le niveau de barbare, +2 si aucun)."""
        if "rage" not in self.active_effect_keys():
            return 0
        return R.rage_damage(self.class_level("Barbare")) or 2

    def bladesong_active(self) -> bool:
        """Chant de la lame actif et applicable : ni armure intermédiaire / lourde, ni bouclier."""
        if "chant_lame" not in self.active_effect_keys() or self.ch.armure.get("bouclier"):
            return False
        armor = self.db.armors.get(self.ch.armure.get("nom", ""), {})
        return armor.get("categorie", "aucune") in ("aucune", "légère", "legere")

    # ------------------------------------------------------------------ sources de modificateurs
    @_batch_memo
    def modifier_sources(self, with_equipment: bool = True) -> list[tuple[str, dict]]:
        """[(libellé de la source, modificateur MECH)] : effets actifs puis équipement (armure)."""
        out = []
        for k in self.active_effect_keys():
            m = M.mech(k)
            if m:
                out.append((FX.EFFECTS[k]["nom"], m))
        for entry in self.ch.objets_magiques:              # objets magiques équipés (et harmonisés si requis)
            item = (self.magic_item(entry.get("nom", "")) or {})
            m = M.item_mech(entry.get("nom", ""))
            if m and entry.get("equipe", True) and (entry.get("harmonise") or not item.get("lien")):
                out.append(("Objet : " + entry["nom"], m))
        if with_equipment:
            armor = self.db.armors.get(self.ch.armure.get("nom", ""))
            no_armor = not armor or armor.get("categorie") == "aucune"
            if no_armor and self.ch.armure.get("bouclier") and not self.shield_proficient():
                out.append(("Bouclier non maîtrisé", {"tests": {"Force": [M.DIS], "Dextérité": [M.DIS]},
                                                     "js": {"Force": [M.DIS], "Dextérité": [M.DIS]},
                                                     "attaque": [M.DIS]}))
            if armor and armor.get("categorie") != "aucune":
                if armor.get("desavantage_discretion"):
                    out.append(("Armure : " + armor["nom"], {"competences": {"Discrétion": [M.DIS]}}))
                if not R.armor_proficient(armor["categorie"], self.armor_proficiencies()) or (
                        self.ch.armure.get("bouclier") and not self.shield_proficient()):
                    out.append(("Armure non maîtrisée : " + armor["nom"],
                                {"tests": {"Force": [M.DIS], "Dextérité": [M.DIS]},
                                 "js": {"Force": [M.DIS], "Dextérité": [M.DIS]}, "attaque": [M.DIS]}))
                if armor.get("force_min") and self.score("Force") < armor["force_min"]:
                    out.append(("Armure trop lourde (Force {} requise)".format(armor["force_min"]),
                                {"vitesse_bonus": -3.0}))
        return out

    def ability_effects(self, ab: str) -> tuple[int, int, list[str]]:
        """(bonus de score, score minimum imposé, sources) dus aux effets actifs (potions de force de géant...)."""
        bonus, floor, src = 0, 0, []
        for label, m in self.modifier_sources(False):
            if ab in m.get("carac", {}):                   # (le plafond de 20 est appliqué par le moteur)
                bonus += m["carac"][ab]
                src.append("{} {:+d}".format(label, m["carac"][ab]))
            if ab in m.get("carac_min", {}):
                floor = max(floor, m["carac_min"][ab])
                src.append("{} : {} {}".format(label, ab, m["carac_min"][ab]))
        return bonus, floor, src

    @_batch_memo
    def check_mods(self, ab: str, skill: str = "") -> dict:
        """Modificateurs d'un test de caractéristique / d'une compétence (avantage, désavantage, bonus, dés)."""
        entries = []
        for label, m in self.modifier_sources():
            t = m.get("tests", {})
            entries.append((label, list(t.get("*", [])) + list(t.get(ab, []))))
            if skill:
                entries.append((label, list(m.get("competences", {}).get(skill, []))))
        return M.collect(entries, self.mods())

    @_batch_memo
    def save_mods(self, ab: str) -> dict:
        entries = []
        for label, m in self.modifier_sources():
            j = m.get("js", {})
            entries.append((label, list(j.get("*", [])) + list(j.get(ab, []))))
        return M.collect(entries, self.mods())

    @_batch_memo
    def attack_mods(self) -> dict:
        return M.collect([(label, list(m.get("attaque", []))) for label, m in self.modifier_sources()], self.mods())

    @_batch_memo
    def effect_mods(self) -> dict:
        """CA et vitesse dues aux effets (modificateurs structurés) + listes lisibles pour le récapitulatif."""
        res = FX.summary_mods(self.active_effect_keys())
        ca, mult, bonus, ca_min, pv_max, half = 0, 1.0, 0.0, 0, 0, False
        for _, m in self.modifier_sources():
            ca += int(m.get("ca", 0))
            if "vitesse_mult" in m:
                mult *= float(m["vitesse_mult"])
            bonus += float(m.get("vitesse_bonus", 0.0))
            ca_min = max(ca_min, int(m.get("ca_min", 0)))
            pv_max += int(m.get("pv_max", 0))
            half = half or bool(m.get("pv_max_moitie"))
        res.update({"ca": ca, "vitesse_mult": mult, "vitesse_bonus": bonus, "ca_min": ca_min, "pv_max": pv_max,
                    "pv_moitie": half})
        return res

    def defenses(self) -> dict:
        """Résistances et immunités en vigueur : {"resistances": [(type, source)], "immunites": [...]}."""
        out = {"resistances": [], "immunites": []}
        for label, m in self.modifier_sources(False):
            for t in m.get("resistances", []):
                out["resistances"].append((t, label))
            for t in m.get("immunites", []):
                out["immunites"].append((t, label))
        return out

    def effect_summary_lines(self) -> list[str]:
        """Rappel lisible des modificateurs en vigueur (« CA +2 », « Attaques : avantage (Hâte) »...)."""
        m, out = self.effect_mods(), []
        if m["ca"]:
            out.append("CA {:+d}".format(m["ca"]))
        if m["vitesse_mult"] != 1 or m["vitesse_bonus"]:
            out.append("Vitesse " + ("0" if m["vitesse_mult"] == 0 else
                                     ("×{:g}".format(m["vitesse_mult"]) if m["vitesse_mult"] != 1 else "")
                                     + (" {:+g} m".format(m["vitesse_bonus"]) if m["vitesse_bonus"] else "")))
        for key, label in (("attaque", "Attaques"), ("js", "Jets de sauvegarde"), ("tests", "Tests"),
                           ("degats", "Dégâts")):
            if m[key]:
                out.append("{} : {}".format(label, ", ".join(m[key])))
        return out + m["notes"]

    # ==================================================================================
    # Consommables (potions, huiles, élixirs, antitoxine)
    # ==================================================================================
    def consumables(self) -> list[dict]:
        """Consommables de l'inventaire : [{nom, source ('equipement' | 'objet'), index, qte}]."""
        out = []
        for i, it in enumerate(self.ch.equipement):
            if M.is_consumable(it.get("nom", "")) and int(it.get("qte", 0)) > 0:
                out.append({"nom": it["nom"], "source": "equipement", "index": i, "qte": int(it["qte"])})
        for i, it in enumerate(self.ch.objets_magiques):
            if M.is_consumable(it.get("nom", "")):
                out.append({"nom": it["nom"], "source": "objet", "index": i, "qte": 1})
        return out

    def use_consumable(self, source: str, index: int, rng=None, roll: Optional[int] = None,
                       choice: str = "") -> str:
        """
        Boit / applique un consommable et déclenche son effet officiel (soins, état actif, purge des états
        néfastes...). Le consommable est retiré de l'inventaire. Renvoie un message lisible.
        """
        items = self.ch.equipement if source == "equipement" else self.ch.objets_magiques
        if not 0 <= index < len(items):
            return ""
        name = items[index]["nom"]
        kind, arg = M.potion_action(name)
        rng = rng or random
        before_keys = set(self.ch.effets_actifs)
        msg = name + " : "
        if kind == "soin":
            dice = re.match(r"(\d+)d(\d+)\+(\d+)", arg)
            n, sides, flat = (int(x) for x in dice.groups())
            total = roll if roll is not None else sum(rng.randint(1, sides) for _ in range(n)) + flat
            before = self.ch.pv_actuels if self.ch.pv_actuels >= 0 else self.hp_max()
            self.ch.pv_actuels = min(self.hp_max(), before + total)
            msg += "{} ({}) → +{} PV".format(total, arg.replace("+", " + "), self.ch.pv_actuels - before)
        elif kind == "force":
            key = next((k for k in FX.EFFECTS if k.startswith("potion_force_") and
                        norm(FX.EFFECTS[k]["nom"]).replace("force de geant ", "") in norm(name)), None)
            if key:
                self.add_effect(key)
                msg += "état « {} » actif (1 heure)".format(FX.EFFECTS[key]["nom"])
        elif kind == "effet":
            self.add_effect(arg)
            msg += "état « {} » actif".format(FX.EFFECTS.get(arg, {}).get("nom", arg))
        elif kind == "purge":
            gone = [k for k in self.active_effect_keys() if k in arg]
            for k in gone:
                self.ch.effets_actifs = [x for x in self.ch.effets_actifs if x != k]
            msg += ("états retirés : " + ", ".join(FX.EFFECTS[k]["nom"] for k in gone)) if gone else \
                "aucun état néfaste à purger"
        elif kind == "antidote":
            self.ch.effets_actifs = [x for x in self.ch.effets_actifs if x != "empoisonne"]
            self.add_effect("antitoxine")
            msg += "poison purgé, avantage aux JS contre le poison (1 heure)"
        elif kind == "heroisme":
            self.ch.pv_temporaires = max(self.ch.pv_temporaires, 10)
            self.add_effect("ivresse_magique")
            msg += "10 PV temporaires et Bénédiction (1 heure)"
        elif kind == "resistance":
            types = M.damage_types_in(name)
            dtype = choice or (types[0] if types else "")
            if dtype in M.DAMAGE_TYPES:
                self.add_effect("resist_" + dtype)
                msg += "résistance aux dégâts {} (1 heure)".format(M.DAMAGE_TYPES[dtype][0])
            else:
                msg += "choisissez le type de dégâts de la potion (ajoutez l'état « Résistance (type) »)"
        elif kind == "poison":
            self.add_effect("empoisonne")
            msg += "empoisonné ! (3d6 dégâts de poison, JS Con DD 13 pour réduire)"
        else:
            msg += "effet narratif — voir la description de l'objet"
        for k in self.ch.effets_actifs:                    # effets apportés par le consommable : temporaires
            if k not in before_keys and k not in self.ch.effets_potions:
                self.ch.effets_potions.append(k)
        if source == "equipement":
            items[index]["qte"] = int(items[index].get("qte", 1)) - 1
            if items[index]["qte"] <= 0:
                items.pop(index)
        else:
            items.pop(index)
        return msg

    # ==================================================================================
    # Actions d'arme (BG3)
    # ==================================================================================
    def weapon_actions(self, slot: dict) -> list[dict]:
        w = self.db.weapons.get(slot.get("nom", ""))
        st = self.weapon_stats(slot)
        if not w or not st:
            return []
        return WA.weapon_action_rows(w, self.mod(st["carac"]), self.prof)

    # ==================================================================================
    # Munitions
    # ==================================================================================
    @staticmethod
    def ammo_kind(weapon: dict) -> str:
        if not any(norm(p).startswith("munition") for p in weapon.get("proprietes", [])):
            return ""
        n = norm(weapon.get("nom", ""))
        return next((kind for frag, kind in AMMO_BY_WEAPON if frag in n), "munition")

    def ammo_options(self, slot: dict) -> list[dict]:
        """Munitions de l'inventaire compatibles avec l'arme : [{nom, qte, bonus, magique, description}]."""
        w = self.db.weapons.get(slot.get("nom", ""))
        kind = self.ammo_kind(w) if w else ""
        if not kind:
            return []
        out = []
        for it in self.ch.equipement:
            n = norm(it.get("nom", ""))
            if any(x in n for x in AMMO_EXCLUDE) or not (kind in n or "munition" in n):
                continue
            plus = re.search(r"\+(\d)", it["nom"])
            magic = self.db.magic_items.get(it["nom"]) if isinstance(self.db.magic_items, dict) else None
            out.append({"nom": it["nom"], "qte": int(it.get("qte", 0)), "bonus": int(plus.group(1)) if plus else 0,
                        "magique": bool(magic or plus),
                        "description": (magic or {}).get("description", "")})
        return out

    def selected_ammo(self, slot: dict) -> Optional[dict]:
        name = slot.get("munition", "")
        return next((a for a in self.ammo_options(slot) if a["nom"] == name), None) if name else None

    def shoot(self, slot: dict) -> str:
        """Tir : consomme une munition choisie (ou une munition ordinaire si aucune n'est choisie)."""
        opts = self.ammo_options(slot)
        if not opts and not self.ammo_kind(self.db.weapons.get(slot.get("nom", ""), {})):
            return ""
        target = self.selected_ammo(slot) or next((a for a in opts if not a["magique"] and a["qte"] > 0), None)
        if target is None:
            return "Aucune munition compatible dans l'inventaire."
        item = next(i for i in self.ch.equipement if i["nom"] == target["nom"])
        if int(item.get("qte", 0)) <= 0:
            return f"Stock épuisé : {target['nom']}."
        item["qte"] = int(item["qte"]) - 1
        return f"{target['nom']} tiré(e) — reste {item['qte']}."

    # ==================================================================================
    # Réactions
    # ==================================================================================
    def known_spell_names(self) -> list[str]:
        names = []
        modes = {c["classe"]: c["mode"] for c in self.casters()}
        for cls, spells in self.ch.sorts.items():
            for s in spells:
                if s.get("prepare", False) or modes.get(cls) == "known":
                    names.append(s["nom"])
        for e in self.ch.classes:
            names += self.domain_spells(e)
        names += [s["nom"] for s in self.racial_spells() if s["debloque"]]
        names += [g["nom"] for g in self.granted_spells()]
        return list(dict.fromkeys(names))

    def reactions(self) -> list[dict]:
        """Réactions disponibles : [{cle, nom, icone, source, declencheur, effet}]."""
        out = [{"cle": "opportunite", "nom": "Attaque d'opportunité", "icone": "⚔", "source": "Règle de base (PHB)",
                "declencheur": "Une créature hostile que vous voyez quitte votre allonge.",
                "effet": "Une attaque au corps à corps contre elle, avant qu'elle ne sorte de votre allonge."}]
        for name in self.known_spell_names():
            spell = self.db.find_spell(name)
            if spell and "reaction" in norm(spell.get("temps", "")):
                out.append({"cle": "sort:" + spell["nom"], "nom": spell["nom"], "icone": "✦",
                            "source": "Sort de niveau {}".format(spell["niveau"]) if spell["niveau"] else "Sort mineur",
                            "declencheur": spell.get("temps", ""), "effet": spell.get("description", "")})
        seen = set()
        for e in self.ch.classes:
            for f in self.features(e):
                if not f["debloque"]:
                    continue
                n = norm(f["nom"])
                curated = next((c for c in REACTION_FEATURES if c[0] in n), None)
                generic = ("votre reaction" in norm(f["description"]) or "par une reaction" in norm(f["description"])) \
                    and not n.startswith("style de combat")    # Protection / Interception : voir plus bas
                if (curated or generic) and f["nom"] not in seen:
                    seen.add(f["nom"])
                    out.append({"cle": "apt:" + f["nom"], "nom": f["nom"], "icone": curated[1] if curated else "⚡",
                                "source": "{} niv. {}".format(f["source"], f["niveau"]),
                                "declencheur": curated[2] if curated else "Voir la description de l'aptitude.",
                                "effet": curated[3] if curated else f["description"]})
        for feat in self.chosen_feats():
            c = next((c for c in REACTION_FEATS if c[0] in norm(feat)), None)
            if c:
                out.append({"cle": "don:" + feat, "nom": feat, "icone": c[1], "source": "Don",
                            "declencheur": c[2], "effet": c[3]})
        out += self.race_reactions()                     # Endurance de pierre, Esquive hadozi, Gambade heureuse…
        for style, icon, trig, eff in REACTION_STYLES:
            if self.style_active(style):
                out.append({"cle": "style:" + style, "nom": style, "icone": icon, "source": "Style de combat",
                            "declencheur": trig, "effet": eff})
        return out

    def use_reaction(self, key: str) -> None:
        """Clic sur une réaction : la marque utilisée pour ce round (un second clic l'annule)."""
        self.ch.reaction_utilisee = "" if self.ch.reaction_utilisee == key else key

    def new_round(self) -> None:
        """Nouveau round : réaction, action, action bonus et déplacement de nouveau disponibles (v30)."""
        self.ch.reaction_utilisee = ""
        self.ch.tour_action = self.ch.tour_bonus = False
        self.ch.tour_attaques = 0
        self.ch.tour_deplacement = 0.0
        self.ch.tour_utilises = []                       # Attaque sournoise… : de nouveau disponibles

    # ==================================================================================
    # Concentration et lancement de sorts
    # ==================================================================================
    def concentration_conflict(self, spell_name: str) -> str:
        """Nom du sort dont la concentration serait rompue en lançant `spell_name` ('' si aucun conflit)."""
        spell = self.db.find_spell(spell_name)
        if not spell or not spell.get("concentration"):
            return ""
        current = self.ch.concentration
        return current if current and current != spell["nom"] else ""

    def break_concentration(self) -> str:
        old = self.ch.concentration
        if old:
            linked = self.ch.concentration_effet
            self.ch.effets_actifs = [k for k in self.ch.effets_actifs
                                     if k != linked and not (FX.EFFECTS.get(k, {}).get("concentration")
                                                             and norm(FX.EFFECTS[k]["nom"]).startswith(norm(old)))]
            if linked == "hate":                       # fin de Hâte : un tour de léthargie (PHB)
                self.add_effect("lethargie")
        self.ch.concentration = ""
        self.ch.concentration_cible = ""
        self.ch.concentration_effet = ""
        if old and norm(old) == "metamorphose" and self.ch.forme_type == "metamorphose" and self.ch.forme_active:
            self.end_form()                               # concentration rompue : la Métamorphose prend fin
        return old

    def lowest_free_slot(self, level: int) -> Optional[str]:
        """« slot:N » (emplacement de niveau N) ou « pacte » : le plus bas disponible de niveau ≥ level."""
        slots = self.spell_slots()
        for lvl in range(level, 10):
            if lvl - 1 < len(slots) and self.ch.emplacements_utilises[lvl - 1] < slots[lvl - 1]:
                return f"slot:{lvl}"
        count, plvl = self.pact()
        if count and plvl >= level and self.ch.pacte_utilises < count:
            return "pacte"
        return None

    # ------------------------------------------------------------------ sorts de buff (style BG3)
    def buff_options(self, spell_name: str) -> list[str]:
        """Effets bénéfiques que le sort peut appliquer (plusieurs : Agrandissement / Rapetissement, Amélioration
        de caractéristique…)."""
        if not hasattr(self.db, "_spell_buffs"):
            self.db._spell_buffs = M.spell_buffs(self.db)
        spell = self.db.find_spell(spell_name)
        return list(self.db._spell_buffs.get(norm(spell["nom"]), [])) if spell else []

    def spell_is_personal(self, spell_name: str) -> bool:
        """Portée « personnelle » (Bouclier, Flou, Esprits gardiens…) ou sort de zone centré sur le lanceur."""
        spell = self.db.find_spell(spell_name)
        if not spell:
            return False
        return norm(spell.get("portee", "")).startswith("personnel") or norm(spell["nom"]) in M.PERSONAL_BUFFS

    def slot_plan(self, level: int) -> dict:
        """Emplacement qui sera utilisé : {niveau, exact, pacte, disponible}. Repli sur un niveau supérieur."""
        if level <= 0:
            return {"niveau": 0, "exact": True, "pacte": False, "disponible": True}
        slot = self.lowest_free_slot(level)
        if slot is None:
            return {"niveau": None, "exact": False, "pacte": False, "disponible": False}
        if slot == "pacte":
            plvl = self.pact()[1]
            return {"niveau": plvl, "exact": plvl == level, "pacte": True, "disponible": True}
        n = int(slot[5:])
        return {"niveau": n, "exact": n == level, "pacte": False, "disponible": True}

    def cast_spell(self, spell_name: str, use_slot: bool = True, target: str = "", effect: str = "",
                   slot_level: int = 0) -> dict:
        """
        Lance un sort : dépense le plus petit emplacement disponible (sorts de niveau 1+) et, pour un sort de
        concentration, remplace la concentration en cours (l'interface a demandé confirmation avant).
        Renvoie {ok, message, emplacement}.
        """
        spell = self.db.find_spell(spell_name)
        if not spell:
            return {"ok": False, "message": f"Sort introuvable : {spell_name}", "emplacement": None}
        block = self.spell_block_reason()
        if block:
            return {"ok": False, "emplacement": None, "message": block[1]}
        slot = None
        if spell["niveau"] and use_slot:
            slot = self.lowest_free_slot(max(spell["niveau"], int(slot_level or 0)))   # niveau choisi (surclassement)
            if slot is None:
                return {"ok": False, "emplacement": None,
                        "message": "Aucun emplacement de niveau {} ou plus disponible.".format(spell["niveau"])}
            if slot == "pacte":
                self.ch.pacte_utilises += 1
            else:
                self.ch.emplacements_utilises[int(slot[5:]) - 1] += 1
        msg = "{} lancé".format(spell["nom"])
        cast_level = spell["niveau"]
        if slot:
            cast_level = self.pact()[1] if slot == "pacte" else int(slot[5:])
            msg += " (emplacement de Pacte, niveau {}{})".format(
                cast_level, ", niveau supérieur" if cast_level > spell["niveau"] else "") if slot == "pacte" else \
                " (emplacement de niveau {}{})".format(cast_level, ", niveau supérieur" if cast_level > spell["niveau"]
                                                       else "")
        vals = self.spell_values(spell["nom"], cast_level) if spell["niveau"] else None
        if vals and vals.get("degats"):                  # dégâts au niveau réellement lancé (surclassement)
            msg += " — Dégâts : {} {}".format(vals["degats"], vals.get("type_degats", "")).rstrip()
        elif vals and vals.get("soins"):
            msg += " — Soins : {} PV".format(vals["soins"])
        if spell.get("concentration"):
            old = self.break_concentration()
            self.ch.concentration = spell["nom"]
            self.ch.concentration_cible = target or "soi"
            msg += " — concentration" + (f" (remplace {old})" if old and old != spell["nom"] else "")
        if effect and target != "allie":              # sur soi : les bonus s'appliquent à la fiche
            self.add_effect(effect)
            if spell.get("concentration"):
                self.ch.concentration_effet = effect
            msg += " — effet « {} » actif sur vous".format(FX.EFFECTS[effect]["nom"])
        elif target == "allie":
            msg += " — lancé sur un allié (aucun bonus sur votre fiche)"
        return {"ok": True, "message": msg + ".", "emplacement": slot, "niveau": cast_level}

    # ==================================================================================
    # Repos
    # ==================================================================================
    def hit_dice_pool(self) -> list[dict]:
        out = []
        for die, total in sorted(self.hit_dice().items(), key=lambda kv: -R.die_sides(kv[0])):
            used = min(total, int(self.ch.des_vie_utilises.get(die, 0)))
            out.append({"de": die, "total": total, "utilises": used, "restants": total - used})
        return out

    def spend_hit_die(self, die: str, roll: Optional[int] = None, rng=None) -> Optional[dict]:
        """Dépense un dé de vie : PV regagnés = jet + modificateur de Constitution (minimum 0)."""
        pool = next((p for p in self.hit_dice_pool() if p["de"] == die), None)
        if not pool or pool["restants"] <= 0:
            return None
        sides = R.die_sides(die)
        roll = roll if roll is not None else (rng or random).randint(1, sides)
        con = self.mod("Constitution")
        gain = max(0, roll + con)
        before = self.ch.pv_actuels if self.ch.pv_actuels >= 0 else self.hp_max()
        self.ch.pv_actuels = min(self.hp_max(), before + gain)
        self.ch.des_vie_utilises[die] = pool["utilises"] + 1
        return {"de": die, "jet": roll, "con": con, "gain": self.ch.pv_actuels - before}

    def short_rest_recharges(self) -> list[str]:
        out = []
        if self.pact()[0]:
            out.append("Emplacements de Magie de pacte")
        if self.class_level("Moine") >= 2:
            out.append("Points de ki")
        if self.class_level("Druide") >= 2:
            out.append("Formes sauvages")
        if self.class_level("Guerrier"):
            out.append("Second souffle" + (" et Fougue" if self.class_level("Guerrier") >= 2 else ""))
        if self.class_level("Clerc") >= 2 or self.class_level("Paladin") >= 3:
            out.append("Conduit divin")
        if self.class_level("Barde") >= 5:
            out.append("Inspiration bardique (Source d'inspiration)")
        if self.class_level("Magicien"):
            out.append("Restauration arcanique possible (une fois par jour, à gérer dans l'onglet Magie)")
        if self.class_level("Ensorceleur") >= 20:
            out.append("4 points de sorcellerie (Restauration de sorcellerie)")
        out.append("Actions d'arme (1 utilisation par repos court)")
        out += ["{} (race)".format(t["label"]) for t in self.race_action_trackers() if t["recover"] == "repos court"]
        return out

    def long_rest_recharges(self) -> list[str]:
        out = ["Points de vie au maximum", "Moitié des dés de vie (minimum 1)", "Tous les emplacements de sorts"]
        for cls, label in (("Barbare", "Rages"), ("Moine", "Points de ki"), ("Druide", "Formes sauvages"),
                           ("Ensorceleur", "Points de sorcellerie"), ("Paladin", "Imposition des mains et Sens divin")):
            if self.class_level(cls):
                out.append(label)
        out += ["{} (race)".format(t["label"]) for t in self.race_action_trackers()]
        if any(k.startswith("epuisement_") for k in self.ch.effets_actifs):
            out.append("Épuisement réduit d'un niveau")
        out.append("Concentration et réaction réinitialisées")
        return out

    def rations_available(self) -> int:
        return sum(int(i.get("qte", 0)) for i in self.ch.equipement if norm(i.get("nom", "")).startswith("ration"))

    def consume_ration(self) -> bool:
        for it in self.ch.equipement:
            if norm(it.get("nom", "")).startswith("ration") and int(it.get("qte", 0)) > 0:
                it["qte"] = int(it["qte"]) - 1
                return True
        return False

    def darkvision(self) -> dict:
        """Vision dans le noir : {portee (m, 0 = vision normale), source, superieure, detail}.
        Lue dans les traits de l'espèce / sous-espèce ; le sort « Vision dans le noir » actif donne 18 m au moins."""
        best, src, text = 0.0, "", ""
        for c in self.race_capacities():
            n, d = norm(c.get("nom", "")), norm(c.get("description", ""))
            if "vision dans le noir" not in n and "dans le noir" not in d:
                continue
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:m\b|metres)", d)
            dist = float(m.group(1).replace(",", ".")) if m else 18.0
            if dist > best:
                best, src, text = dist, c["nom"], c.get("description", "")
        if "vision_noir" in self.ch.effets_actifs and best < 18:
            best, src, text = 18.0, "Sort « Vision dans le noir »", "La cible voit dans les ténèbres jusqu'à 18 m."
        magic = False
        if self.devils_sight():                          # manifestation occulte « Vision du diable »
            magic = True
            if best <= 36:
                best, src = 36.0, "Manifestation « Vision du diable »"
                text = "Vous voyez normalement dans les ténèbres, magiques ou non, jusqu'à 36 m."
            else:
                text += "\nVision du diable : ténèbres magiques comprises jusqu'à 36 m."
        return {"portee": best, "source": src, "superieure": best >= 36, "detail": text, "magique": magic}

    def has_trance(self) -> bool:
        """Transe elfique (Elfe et ses sous-espèces, Drow, Eladrin…) : trait racial « Transe »."""
        return any(norm(c.get("nom", "")).startswith("transe") or norm(c.get("nom", "")) == "trance"
                   for c in self.race_capacities())

    def long_rest_minutes(self) -> int:
        """Durée du repos long : 4 heures sous Transe elfique, 8 heures sinon."""
        return 4 * 60 if self.has_trance() else LONG_REST_MIN

    def long_rest_warning(self) -> str:
        last = int(self.ch.dernier_repos_long)
        if last >= 0 and self.ch.temps_minutes - last < DAY:
            return ("Règle officielle : un seul repos long par période de 24 heures (dernier repos long : {})."
                    .format(self.time_text(last)))
        return ""

    def do_short_rest(self) -> None:
        if self.ch.forme_active:
            self.end_form()                               # la forme sauvage prend fin avec le repos
        self.short_rest()
        self.break_concentration()                       # 1 heure : bien plus long que tout sort de concentration
        self.ch.ressources_utilisees.pop("souffle", None)
        self.purge_after_rest(long_rest=False)
        self.ch.reaction_utilisee = ""
        self.advance_time(SHORT_REST_MIN)

    def do_long_rest(self, eat_ration: bool = False) -> None:
        if self.ch.forme_active:
            self.end_form()
        self.long_rest()
        exhaustion = sorted(k for k in self.ch.effets_actifs if k.startswith("epuisement_"))
        if exhaustion:
            lvl = int(exhaustion[-1].split("_")[1])
            self.ch.effets_actifs = [k for k in self.ch.effets_actifs if not k.startswith("epuisement_")]
            if lvl > 1:
                self.ch.effets_actifs.append(f"epuisement_{lvl - 1}")
        self.break_concentration()
        self.purge_after_rest(long_rest=True)            # fin des effets temporaires (rage, sorts, potions...)
        self.ch.reaction_utilisee = ""
        if eat_ration:
            self.consume_ration()
        self.advance_time(self.long_rest_minutes())        # Transe elfique : 4 heures au lieu de 8
        self.ch.dernier_repos_long = self.ch.temps_minutes

    # ==================================================================================
    # Jets de d20 animés : description des bonus / malus de chaque jet (core/dice.py)
    # ==================================================================================
    def ability_check_spec(self, ab: str) -> "D.RollSpec":
        fx = self.check_mods(ab)
        detail = [(R.mod_label(ab), "{:+d}".format(self.mod(ab)))] + fx["detail"]
        return D.spec_from_detail("Test de " + ab, "test", detail, fx["avantage"], fx["desavantage"], fx["echec"])

    def skill_spec(self, name: str) -> "D.RollSpec":
        row = next(r for r in self.skill_rows() if r["nom"] == name)
        return D.spec_from_detail("{} ({})".format(name, row["carac"]), "competence", row["detail"],
                                  row["avantage"], row["desavantage"], row["echec"])

    def save_spec(self, ab: str) -> "D.RollSpec":
        row = next(r for r in self.save_rows() if r["carac"] == ab)
        return D.spec_from_detail("Jet de sauvegarde de " + ab, "sauvegarde", row["detail"],
                                  row["avantage"], row["desavantage"], row["echec"])

    def weapon_attack_spec(self, slot: dict) -> Optional["D.RollSpec"]:
        st = self.weapon_stats(slot)
        if not st:
            return None
        detail = [(R.mod_label(st["carac"]), "{:+d}".format(self.mod(st["carac"])))]
        if st["maitrise"]:
            detail.append(("Maîtrise", "{:+d}".format(self.prof)))
        if st["magique"]:
            detail.append(("Arme magique", "{:+d}".format(st["magique"])))
        if any(n.startswith("Archerie") for n in st["styles"]):
            detail.append(("Style Archerie", "+2"))
        ammo = st.get("munition")
        if ammo and ammo.get("bonus"):
            detail.append(("Munition : " + ammo["nom"], "{:+d}".format(ammo["bonus"])))
        fx = self.attack_mods()
        note = "Dégâts si le coup porte : {} {}{}".format(
            st["degats"], st["type_degats"], " (critique : doublez les dés)" if st["degats"] else "")
        return D.spec_from_detail("Attaque — " + st.get("affichage", st["nom"]), "attaque", detail + fx["detail"],
                                  fx["avantage"], fx["desavantage"], fx["echec"], note)

    def weapon_action_spec(self, slot: dict, row: dict) -> Optional["D.RollSpec"]:
        """Jet d'attaque d'une action / botte d'arme : attaque normale de l'arme + rappel de l'effet et du DD."""
        spec = self.weapon_attack_spec(slot)
        if spec is None:
            return None
        spec.title = "{} — {} {}".format(spec.title, row.get("icone", ""), row.get("nom", "")).strip()
        bits = []
        if row.get("sauvegarde"):
            bits.append("Si l'attaque touche : JS de {} DD {}".format(
                row["sauvegarde"], row["dd"] if row.get("dd") is not None else "8 + maîtrise + mod."))
        effect = row.get("echec") if row.get("echec") not in (None, "", "—") else row.get("succes", "")
        if effect and effect != "—":
            bits.append(("Échec : " if row.get("sauvegarde") else "Effet : ") + effect)
        spec.note = " — ".join(bits + ([spec.note] if spec.note else []))
        return spec

    def spell_attack_spec(self, spell_name: str, class_name: str = "", slot_level: int = 0) -> Optional["D.RollSpec"]:
        """Jet d'attaque de sort (sorts au test « A » / « AC ») avec la caractéristique de la classe ou de la race."""
        spell = self.db.find_spell(spell_name)
        if not spell or spell.get("test") not in ("A", "AC"):
            return None
        caster = self.caster(class_name) if class_name else None
        if caster is None:
            caster = next((c for c in self.casters() if c["liste"] in spell.get("classes", [])), None)
        if caster is not None:
            ab = caster["carac"]
        else:
            racial = next((r for r in self.racial_spells() if r["nom"] == spell["nom"]), None)
            if racial is None and not self.casters():
                return None
            ab = racial["carac"] if racial else self.casters()[0]["carac"]
        detail = [(R.mod_label(ab), "{:+d}".format(self.mod(ab))), ("Maîtrise", "{:+d}".format(self.prof))]
        fx = self.attack_mods()
        stats = self.cantrip_stats(spell["nom"]) if spell["niveau"] == 0 else None
        dmg = ((stats or {}).get("degats") or spell.get("degats", "")) if spell["niveau"] == 0 else \
            self.spell_damage_formula(spell["nom"], slot_level, class_name)
        if spell["niveau"]:
            lvl = max(int(slot_level or 0), spell["niveau"]) if slot_level else \
                self.default_slot_level(spell["nom"], class_name)
            if dmg and lvl > spell["niveau"]:
                dmg += " (niveau {}{})".format(lvl, ", Magie des pactes" if not slot_level and lvl == self.pact()[1]
                                              else "")
        note = "Dégâts si le sort touche : {} {}".format(dmg, spell.get("type_degats", "")) if dmg else ""
        return D.spec_from_detail("Attaque de sort — " + spell["nom"], "sort", detail + fx["detail"],
                                  fx["avantage"], fx["desavantage"], fx["echec"], note)

    # ==================================================================================
    # Ascendance draconique (Drakéide, Demi-dragon, Ensorceleur de lignée draconique)
    # ==================================================================================
    def has_breath(self) -> bool:
        race = self.db.races.get(self.ch.race) or {}
        return any("souffle" in norm(c.get("nom", "")) and "infini" not in norm(c.get("nom", ""))
                   for c in race.get("capacites", []))

    def breath_weapon(self) -> Optional[dict]:
        """Souffle draconique calculé selon la couleur choisie (type, zone, JS, DD, dés, utilisations)."""
        if not self.has_breath():
            return None
        color = self.ch.ascendance_raciale if self.ch.ascendance_raciale in DRACONIC else ""
        dtype, shape, save = DRACONIC.get(color, ("", "", "Dextérité"))
        if norm(self.ch.race) == "demi-dragon":          # homebrew : toujours un cône de 4,50 m
            shape = "cône de 4,50 m"
        lvl = self.total_level
        dice = "{}d6".format(2 if lvl < 6 else 3 if lvl < 11 else 4 if lvl < 16 else 5)
        dc = 8 + self.prof + self.mod("Constitution")
        return {"couleur": color, "type": dtype, "zone": shape, "js": save, "dd": dc, "degats": dice,
                "utilise": self.resource_used("souffle") >= 1}

    def sorcerer_lineage(self) -> Optional[dict]:
        entry = next((e for e in self.ch.classes if e["nom"] == "Ensorceleur"
                      and "draconique" in norm(self.active_subclass(e))), None)
        color = self.ch.ascendance_ensorceleur
        if entry is None or color not in DRACONIC:
            return None
        return {"couleur": color, "type": DRACONIC[color][0], "niveau": entry["niveau"],
                "bonus_degats": self.mod("Charisme") if entry["niveau"] >= 6 else 0}

    def is_draconic_sorcerer(self) -> bool:
        return any(e["nom"] == "Ensorceleur" and "draconique" in norm(self.active_subclass(e)) for e in self.ch.classes)

    def racial_combat_traits(self) -> list[dict]:
        """Traits raciaux utiles en combat (armes naturelles, souffle, réactions chiffrées...)."""
        race = self.db.races.get(self.ch.race) or {}
        out = []
        in_actions = {norm(a["nom"]) for a in self.race_actions()}      # déjà dans l'encart Actions
        for c in race.get("capacites", []):
            if norm(c.get("nom", "")) in in_actions and "souffle" not in norm(c.get("nom", "")):
                continue
            d = norm(c.get("description", ""))
            if (re.search(r"\d+d\d+", d) and any(k in d for k in ("degats", "attaque", "jet de sauvegarde",
                                                                       "js de", "reaction"))) \
                    or ("souffle" in norm(c["nom"]) and "infini" not in norm(c["nom"])):
                out.append({"nom": c["nom"], "description": c["description"],
                            "souffle": "souffle" in norm(c["nom"])})
        return out

    # ==================================================================================
    # Sorts accordés par le MJ (roleplay)
    # ==================================================================================
    def add_gm_spell(self, name: str, usage: str = "À volonté", note: str = "") -> bool:
        spell = self.db.find_spell(name)
        real = spell["nom"] if spell else name.strip()
        if not real or any(s["nom"] == real for s in self.ch.sorts_mj):
            return False
        self.ch.sorts_mj.append({"nom": real, "usage": usage or "À volonté", "note": note.strip()})
        return True

    def remove_gm_spell(self, name: str) -> None:
        self.ch.sorts_mj = [s for s in self.ch.sorts_mj if s["nom"] != name]

    # ==================================================================================
    # Forme sauvage : substitution des statistiques, PV tampon, attaques de la bête, soins du Cercle de la Lune
    # ==================================================================================
    def wild_form(self) -> Optional[dict]:
        return self.db.beasts.get(self.ch.forme_active) if self.ch.forme_active else None

    @staticmethod
    def _first_int(text: str, default: int = 0) -> int:
        m = re.search(r"\d+", str(text))
        return int(m.group(0)) if m else default

    def beast_hp_max(self, name: str) -> int:
        beast = self.db.beasts.get(name)
        return self._first_int(beast["pv"], 1) if beast else 0

    def beast_ac(self, beast: dict) -> int:
        return self._first_int(beast["ca"], 10)

    @staticmethod
    def beast_prof(beast: dict) -> int:
        """Bonus de maîtrise d'une créature selon son FP (MM) : +2 jusqu'à FP 4, +3 de 5 à 8, +4 de 9 à 12…"""
        fp = beast.get("fp", 0) or 0
        return 2 if fp <= 4 else 3 if fp <= 8 else 4 if fp <= 12 else 5 if fp <= 16 else 6

    def beast_skills(self) -> dict:
        """Compétences du statblock de la bête active : {nom normalisé: bonus}."""
        beast = self.wild_form()
        if beast is None:
            return {}
        return {norm(m.group(1)).strip(): int(m.group(2))
                for m in re.finditer(r"([A-Za-zÀ-ÿ' ]+?)\s*([+-]\d+)", beast.get("competences", "") or "")}

    def spells_blocked(self) -> bool:
        """Aucun sort possible : forme sauvage (avant Sorts bestiaux, niveau 18) ou armure / bouclier non maîtrisé."""
        return self.spell_block_reason() is not None

    def beast_attacks(self) -> list[dict]:
        """
        Attaques de la bête : [{nom, attaque, carac, mod, maitrise, portee, degats, type, estime}] calculées avec
        les modificateurs PROPRES à la créature (FOR / DEX et bonus de maîtrise selon son FP).
        """
        beast = self.wild_form()
        if beast is None:
            return []
        prof = self.beast_prof(beast)
        mods = {ab: int(beast["carac"][ab][1]) for ab in ("FOR", "DEX")}
        out = []
        for raw in beast["actions"]:
            m = re.match(r"^\s*([^.]+)\.\s*([+-]\d+)\s*,\s*(.+?\bm)\s*,\s*(\d+d\d+(?:\s*[+-]\s*\d+)?|\d+)\s*(.*)$", raw)
            name = raw.split(".")[0].strip()
            if norm(name).startswith("attaques multiples"):
                continue
            if m:
                bonus = int(m.group(2))
                ab = min(mods, key=lambda k: abs(bonus - prof - mods[k]))   # FOR ou DEX selon le statblock
                out.append({"nom": m.group(1).strip(), "attaque": bonus, "carac": ab, "mod": mods[ab],
                            "maitrise": prof, "ajustement": bonus - prof - mods[ab], "portee": m.group(3).strip(),
                            "degats": m.group(4).replace(" ", ""), "type": m.group(5).strip(" ."), "estime": False})
            elif not re.search(r"recharge|nuage|toile|engloutissement", norm(raw)):
                ab = "DEX" if mods["DEX"] > mods["FOR"] else "FOR"       # statblock sans bonus explicite : FOR/DEX de la bête
                out.append({"nom": name, "attaque": prof + mods[ab], "carac": ab, "mod": mods[ab], "maitrise": prof,
                            "ajustement": 0, "portee": "1,50 m", "degats": "1" if mods[ab] <= 0 else "1d4{:+d}".format(mods[ab]),
                            "type": "", "estime": True})
        return out

    def beast_attack_spec(self, attack: dict) -> "D.RollSpec":
        label = {"FOR": "Force", "DEX": "Dextérité"}[attack["carac"]]
        detail = [("{} de la bête".format(R.mod_label(label)), "{:+d}".format(attack["mod"])),
                  ("Maîtrise de la bête (FP {})".format(self.wild_form()["fp_txt"]), "{:+d}".format(attack["maitrise"]))]
        if attack["ajustement"]:
            detail.append(("Ajustement du statblock", "{:+d}".format(attack["ajustement"])))
        fx = self.attack_mods()
        note = "Dégâts si l'attaque touche : {} {}".format(attack["degats"], attack["type"]).strip()
        return D.spec_from_detail("{} — {}".format(self.ch.forme_active, attack["nom"]), "attaque",
                                  detail + fx["detail"], fx["avantage"], fx["desavantage"], fx["echec"], note)

    def damage_form(self, amount: int) -> str:
        """Dégâts subis sous forme sauvage : d'abord les PV de la bête ; à 0, la forme prend fin et l'excédent
        est retiré des PV normaux du druide."""
        if not self.ch.forme_active:
            return ""
        self.ch.forme_pv -= max(0, int(amount))
        if self.ch.forme_pv > 0:
            msg = "La bête encaisse {} dégâts (PV restants : {}).".format(amount, self.ch.forme_pv)
            if self.ch.forme_type == "metamorphose" and self.ch.concentration and amount > 0:
                msg += " JS de Constitution DD {} pour maintenir la concentration sur {}{}.".format(
                    max(10, int(amount) // 2), self.ch.concentration,
                    " (avantage : Esprit occulte)" if self.concentration_advantage() else "")
            return msg
        overflow = -self.ch.forme_pv
        name = self.ch.forme_active
        label = "la Métamorphose prend fin" if self.ch.forme_type == "metamorphose" else "forme normale reprise"
        self.end_form(overflow)
        msg = "{} tombe à 0 PV : {}, {} dégât(s) excédentaire(s) reportés sur vos PV ({}).".format(
            name, label, overflow, self.ch.pv_actuels)
        if self.ch.pv_actuels <= 0:
            self.add_effect("inconscient")
            msg += " Vous tombez inconscient (jets contre la mort)."
        return msg

    def heal_form(self, amount: int) -> None:
        if self.ch.forme_active:
            self.ch.forme_pv = min(self.beast_hp_max(self.ch.forme_active), self.ch.forme_pv + max(0, int(amount)))

    def moon_heal_available(self) -> bool:
        return bool(self.ch.forme_active) and self.ch.forme_type == "sauvage" and self.wild_shape()["lune"]

    def moon_heal(self, slot_level: int, rng=None, rolls: Optional[list] = None) -> Optional[dict]:
        """Cercle de la Lune (Forme sauvage de combat) : action bonus + un emplacement de sort de niveau N
        -> la bête regagne Nd8 PV."""
        if not self.moon_heal_available():
            return None
        slots = self.spell_slots()
        if not 1 <= slot_level <= len(slots) or self.ch.emplacements_utilises[slot_level - 1] >= slots[slot_level - 1]:
            return None
        self.ch.emplacements_utilises[slot_level - 1] += 1
        rng = rng or random
        dice = rolls if rolls is not None else [rng.randint(1, 8) for _ in range(slot_level)]
        before = self.ch.forme_pv
        self.heal_form(sum(dice))
        return {"des": dice, "total": sum(dice), "gain": self.ch.forme_pv - before, "niveau": slot_level}

    def moon_heal_levels(self) -> list[int]:
        slots = self.spell_slots()
        return [i + 1 for i, n in enumerate(slots) if n and self.ch.emplacements_utilises[i] < n]

    # ==================================================================================
    # Sort « Métamorphose » appliqué à soi-même (même moteur que la Forme sauvage)
    # ==================================================================================
    POLYMORPH = "Métamorphose"

    def polymorph_status(self, name: str) -> tuple[bool, str]:
        """Bête autorisée par Métamorphose : FP ≤ niveau de la cible (le personnage), pas de nuée."""
        beast = self.db.beasts.get(name)
        if not beast:
            return False, "bête inconnue"
        if beast["nuee"]:
            return False, "une nuée n'est pas une bête unique"
        if beast["fp"] > self.total_level + 1e-9:
            return False, "FP {} > votre niveau ({})".format(beast["fp_txt"], self.total_level)
        return True, ""

    def polymorph_beasts(self) -> list[dict]:
        return [b for n, b in self.db.beasts.items() if self.polymorph_status(n)[0]]

    def cast_polymorph(self, beast_name: str, use_slot: bool = True) -> dict:
        """
        Lance Métamorphose sur soi : dépense l'emplacement, prend la concentration (rompt toute autre
        concentration), puis applique la transformation (6 caractéristiques et PV de la bête).
        """
        ok, why = self.polymorph_status(beast_name)
        if not ok:
            return {"ok": False, "message": why}
        if self.ch.forme_active:
            return {"ok": False, "message": "Vous êtes déjà transformé."}
        res = self.cast_spell(self.POLYMORPH, use_slot)
        if not res["ok"]:
            return res
        self.ch.forme_active = beast_name
        self.ch.forme_type = "metamorphose"
        self.ch.forme_pv = self.beast_hp_max(beast_name)
        self.add_effect("metamorphose")
        res["message"] += " Vous voici : {}.".format(beast_name)
        return res

    def form_status(self) -> Optional[dict]:
        """État de transformation pour l'affichage : {icone, libelle, bete, pv, pv_max, ca} ou None."""
        beast = self.wild_form()
        if beast is None:
            return None
        poly = self.ch.forme_type == "metamorphose"
        return {"icone": "🦋" if poly else "🐺", "bete": beast["nom"],
                "libelle": "État actif : {} - {}".format("Métamorphose" if poly else "Forme Sauvage", beast["nom"]),
                "pv": self.ch.forme_pv, "pv_max": self.beast_hp_max(beast["nom"]), "ca": self.beast_ac(beast),
                "metamorphose": poly}

