"""
Moteur de règles : calcule toutes les valeurs dérivées d'un `Character` à partir de la
base de données (`Database`) et expose les « commandes » métier (changer de niveau, ajouter une
classe, repos...). Aucune dépendance à l'interface graphique : ce module est entièrement testable.
"""
from __future__ import annotations

import functools
import math
import random
import re
from contextlib import contextmanager
from typing import Optional

from . import editions as E
from . import house_rules as HR
from . import rules as R
from .character import Character
from .data_loader import Database
from .rules import ABILITIES, norm

# francisation (v25) : « Lame psychique / Soulknife » -> « Lame psychique », langues…
NAME_MIGRATIONS = {
    "Lame psychique / Soulknife": "Lame psychique", "Bretteur (Swashbuckler)": "Bretteur",
    "Conspirateur (Mastermind)": "Conspirateur", "Éclaireur (Scout)": "Éclaireur",
    "Enquêteur (Inquisitive)": "Enquêteur", "Fantôme (Phantom)": "Fantôme",
    "Cercle des Fournaises (Wildfire)": "Cercle des Fournaises", "Guerrier Psi (Soldat psi)": "Soldat psi",
    "La Lame maudite (Magelame)": "La Lame maudite", "Profonde Parler (Deep Speech)": "Profond",
    "Commun des Profondeurs (Undercommon)": "Commun des profondeurs",
}

# espèces retirées du référentiel (doublons) : anciennes sauvegardes converties au chargement
RACE_RENAMED = {"Elfe sylvestre": ("Elfe", "Elfe des bois"), "Harengon": ("Conil", ""), "Mort-vivant": ("Revenant", ""),
                "Enfant de la lune": ("Féral", "")}


RESOURCE_LABELS_2024 = {
    "rages": "Rages / repos long", "degats_de_rage": "Dégâts de rage", "maitrise_des_armes": "Bottes d'arme maîtrisées",
    "second_souffle": "Second souffle (utilisations)", "arts_martiaux": "Dé d'arts martiaux",
    "points_de_concentration": "Points de concentration", "deplacement_sans_armure": "Déplacement sans armure",
    "conduit_divin": "Conduit divin (utilisations)", "formes_sauvages": "Formes sauvages (utilisations)",
    "points_de_sorcellerie": "Points de sorcellerie", "invocations": "Manifestations occultes",
    "emplacements_de_pacte": "Emplacements de pacte", "niveau_emplacements": "Niveau des emplacements de pacte",
    "attaque_sournoise": "Attaque sournoise", "de_d_inspiration": "Dé d'inspiration bardique",
    "ennemi_favori": "Ennemi juré (utilisations de Marque du chasseur)"}


def _fmt_cell(value) -> str:
    return str(value)


def memo(fn):
    """
    Mémorise le résultat d'une méthode pendant un lot de rafraîchissement (`Engine.batch()`).
    En dehors d'un lot, la méthode est simplement exécutée : aucun risque de valeur périmée.
    """
    name = fn.__name__

    @functools.wraps(fn)
    def wrapper(self, *args):
        cache = self._memo
        if cache is None:
            return fn(self, *args)
        try:
            key = (name, args)
            hash(key)
        except TypeError:                     # argument non hachable (dict de classe) : identité de l'objet
            key = (name, tuple(id(a) for a in args))
        if key in cache:
            return cache[key]
        value = fn(self, *args)
        cache[key] = value
        return value
    return wrapper


GRANT_TRAIT = re.compile(r"sort|magie|incantation|heritage infernal|langue du diable|feu astral|changement de saison")
GRANT_START = ("sort", "tour de magie", "connait", "lancement", "acces", "donne acces")
GRANT_EXCLUDE = ("fonctionnent sur vous", "immunite", "avantage aux js")


from . import mechanics as M  # noqa: E402
from . import effects as FX  # noqa: E402
from .engine_extras import ExtrasMixin  # noqa: E402
from .class_actions import SHORT_REST_KEYS, ClassActionsMixin  # noqa: E402
from .companions import CompanionsMixin
from .race_actions import RaceActionsMixin
from .missing import MissingChoicesMixin
from .levelup import LevelUpMixin
from .turn import TurnMixin
from .equipment import EquipmentMixin
from .subclass_features import SubclassFeaturesMixin  # noqa: E402
from .invocations import InvocationsMixin  # noqa: E402
from .combat_flow import CombatFlowMixin  # noqa: E402
from .class_tiles import ClassTilesMixin  # noqa: E402
from .proficiencies import ProficiencyMixin  # noqa: E402
from .spell_swap import SpellSwapMixin  # noqa: E402
from .magic_gear import MagicGearMixin  # noqa: E402
from .initiative import InitiativeMixin  # noqa: E402
from .creation import CreationMixin  # noqa: E402
from .class_guide import ClassGuideMixin  # noqa: E402


def pretty_formula(formula: str) -> str:
    """« 1d8+2 » -> « 1d8 + 2 » ; « 2d6-1 » -> « 2d6 - 1 »."""
    return re.sub(r"\s*([+-])\s*", r" \1 ", formula or "").strip()


def damage_calc(die: str, terms: list, result: str) -> str:
    """v46 — calcul détaillé des dégâts : « 1d8 - 1 (Mod. FOR) + 3 (Objet magique : Épée longue +3) = 1d8 + 2 »."""
    shown = [(label, v) for label, v in terms if v or label.startswith("Mod.")]
    if not shown:
        return pretty_formula(result or die)
    parts = "".join(" {} {} ({})".format("-" if v < 0 else "+", abs(v), label) for label, v in shown)
    return "{}{} = {}".format(pretty_formula(die), parts, pretty_formula(result))


class Engine(ExtrasMixin, ClassActionsMixin, CompanionsMixin, RaceActionsMixin, MissingChoicesMixin,
             LevelUpMixin, TurnMixin, EquipmentMixin, SubclassFeaturesMixin, InvocationsMixin,
             CombatFlowMixin, ClassTilesMixin, ProficiencyMixin, SpellSwapMixin,
             MagicGearMixin, InitiativeMixin, CreationMixin, ClassGuideMixin):
    def __init__(self, db: Database, char: Character):
        self.ch = char
        self.db = db
        self._memo: Optional[dict] = None

    @contextmanager
    def batch(self):
        """
        Lot de rafraîchissement : les calculs dérivés (caractéristiques, aptitudes, CA, sorts...) sont calculés une
        seule fois puis réutilisés. Le personnage ne doit pas être modifié pendant le lot.
        """
        if self._memo is not None:
            yield
            return
        self._memo = {}
        try:
            yield
        finally:
            self._memo = None

    # ==================================================================================
    # Création / normalisation
    # ==================================================================================
    @staticmethod
    def new_character(db: Database) -> Character:
        ch = Character()
        first = "Guerrier" if "Guerrier" in db.classes else (db.class_names() or [""])[0]
        ch.classes = [{"nom": first, "niveau": 1, "sous_classe": "", "pv_jets": [], "edition": E.DEFAULT_EDITION}]
        races = db.race_names()
        ch.race = "Humain" if "Humain" in db.races else (races[0] if races else "")
        bgs = db.background_names()
        ch.historique = bgs[0] if bgs else ""
        eng = Engine(db, ch)
        eng.normalize()
        eng.apply_default_saves()
        eng.apply_background()
        return ch

    def normalize(self) -> None:
        """Garantit la cohérence de la structure après un chargement ou une modification."""
        if self._memo is not None:
            self._memo.clear()
        ch = self.ch
        ch.pv_mode = "moyenne"
        ch.edition_mode = E.normalize_mode(ch.edition_mode)            # v52 : éditions
        if ch.edition_mode == E.MODE_2024 and self.class_level("Occultiste"):   # 2024 : pacte = manifestation choisie
            from .data_loader import PACTS
            ch.pacte = next((n for n in ch.manifestations if n in PACTS), "")
        sheet = {E.MODE_2024: 2024, E.MODE_2014: 2014}.get(ch.edition_mode)   # une édition par fiche (hors libre)
        for entry in ch.classes:
            entry["edition"] = sheet or E.item_edition(entry)
        if "Halphen" in ch.langues_liste:                 # coquille corrigée (v34) : langue des halfelins
            ch.langues_liste = ["Halfelin" if x == "Halphen" else x for x in ch.langues_liste]
        if ch.race in RACE_RENAMED and ch.race not in self.db.races:      # espèce retirée (doublon) -> remplaçante
            ch.race, sub = RACE_RENAMED[ch.race]
            ch.sous_race = sub or ch.sous_race
        for slot in self.asi_slots():                   # emplacements « don uniquement » (Humain variant, MJ)
            if slot.get("don_seul"):
                c = ch.ameliorations.setdefault(slot["id"], {"mode": "don", "don": "", "don_carac": ""})
                c["mode"] = "don"
                if slot.get("mj"):
                    c["don"] = slot["id"][3:]
        for e in ch.classes:                             # francisation : anciens noms VF/VO des sous-classes
            if e.get("sous_classe") in NAME_MIGRATIONS:
                e["sous_classe"] = NAME_MIGRATIONS[e["sous_classe"]]
        if any(x in NAME_MIGRATIONS for x in ch.langues_liste):
            ch.langues_liste = [NAME_MIGRATIONS.get(x, x) for x in ch.langues_liste]
        if ch.forme_active and not ch.forme_type:
            ch.forme_type = "sauvage"
        if ch.forme_active and ch.forme_active in self.db.beasts and ch.forme_pv <= 0:
            ch.forme_pv = self.beast_hp_max(ch.forme_active)       # anciennes sauvegardes
        for name in self.db.skill_names:
            ch.competences.setdefault(name, {"maitrise": False, "expertise": False})
        for name in list(ch.competences):
            if not ch.competences[name].get("maitrise"):
                ch.competences[name]["expertise"] = False
        for ab in ABILITIES:
            ch.sauvegardes.setdefault(ab, False)
        ch.armure.setdefault("bouclier_nom", "")
        # Point Buy : une sauvegarde modifiée à la main ne doit jamais fausser le total de points
        ch.scores_achat = R.point_buy_normalize({ab: ch.scores_achat.get(ab, 8) for ab in ABILITIES})
        # styles de combat : on retire les choix devenus invalides (emplacement disparu, style non autorisé)
        valid = {sl["id"]: sl for sl in self.fighting_style_slots()}
        for sid in list(ch.styles_combat):
            name = ch.styles_combat[sid]
            ok = sid in valid and (name in self.model_names() if valid[sid]["kind"] == "modele"
                                   else name in self.db.styles_by_class.get(valid[sid]["classe"], {}))
            if not ok:
                del ch.styles_combat[sid]
        self.sanitize_class_options()                    # runes / options de tir : sous-classe et niveau
        self.ensure_granted_cantrips()                   # Arnaqueur arcanique : Main de mage d'office
        # style « Technique supérieure » remplacé : la manœuvre apprise disparaît (le dé suit, voir ci-dessous)
        if ch.technique_manoeuvre and (not self.superior_technique() or ch.technique_manoeuvre not in self.db.maneuvers):
            ch.technique_manoeuvre = ""
        # ressources de classe : jamais plus de dépenses que le total (rage, ki, sorcellerie)
        totals = {t["key"]: t["total"] for t in self.resource_trackers()}
        if self.has_breath():
            totals["souffle"] = 1                                       # souffle draconique : 1 / repos court
        for key in list(ch.ressources_utilisees):
            if key not in totals:
                del ch.ressources_utilisees[key]
            elif totals[key] is None:
                ch.ressources_utilisees[key] = 0                       # ressource illimitée
            else:
                ch.ressources_utilisees[key] = max(0, min(int(ch.ressources_utilisees[key]), totals[key]))
        # objets magiques : anciens objets « +1, +2 ou +3 » -> palier séparé (« Bouclier +2 »)
        for entry in ch.objets_magiques:
            if entry.get("nom") not in self.db.magic_items and "+1, +2 ou +3" in entry.get("nom", ""):
                tier = entry["nom"].replace("+1, +2 ou +3", "+{}".format(entry.get("bonus") or 1))
                if tier in self.db.magic_items:
                    entry["nom"], entry["bonus"] = tier, 0
        if ch.forme_active and (ch.forme_active not in self.db.beasts or
                                (ch.forme_type == "sauvage" and self.class_level("Druide") < 2)):
            ch.forme_active, ch.forme_type, ch.forme_pv = "", "", 0
        # objets magiques : structure, harmonisation limitée aux objets qui l'exigent et au maximum autorisé
        for entry in ch.objets_magiques:
            entry.setdefault("bonus", 0)
            entry.setdefault("equipe", True)
            entry.setdefault("harmonise", False)
            item = self.magic_item(entry["nom"])
            if not item or not item["lien"]:
                entry["harmonise"] = False
        self.purge_natural_attacks()                     # v41 : « Mains nues » n'est pas un objet d'inventaire
        self.sync_equipment_slots()                      # v31 : une case du mannequin par objet porté
        self.sync_magic_gear()                           # v45 : armes / armures magiques liées aux cases
        over = self.attuned_count() - self.attunement_limit()
        for entry in reversed(ch.objets_magiques):
            if over <= 0:
                break
            if entry["harmonise"]:
                entry["harmonise"] = False
                over -= 1
        self.migrate_manifestations()                    # v37 : « Etreinte de Hadar » -> « Étreinte de Hadar »
        ch.manifestations = [m for i, m in enumerate(ch.manifestations)
                             if m in self.db.manifestations and m not in ch.manifestations[:i]]
        self.sanitize_ritual_book()                      # v37 : Livre des secrets anciens (rituels valides)
        if ch.armure.get("nom") not in self.db.armors:
            ch.armure["nom"] = "Aucune armure"
        for c in ch.classes:
            c["niveau"] = max(1, min(R.MAX_LEVEL, int(c["niveau"])))
        while ch.niveau_total > R.MAX_LEVEL and ch.classes:
            big = max(ch.classes, key=lambda c: c["niveau"])
            big["niveau"] -= 1
        hp = self.hp_max()
        if ch.pv_actuels < 0 or ch.pv_actuels > hp:
            ch.pv_actuels = hp
        slots = self.spell_slots()
        for i in range(9):
            ch.emplacements_utilises[i] = max(0, min(ch.emplacements_utilises[i], slots[i]))
        n, _ = self.pact()
        ch.pacte_utilises = max(0, min(ch.pacte_utilises, n))
        if not isinstance(ch.menagerie, list):
            ch.menagerie = []
        self.menagerie_sync()                            # Esprit du feu sauvage d'office, entrées caduques retirées
        for m in ch.menagerie:                           # PV des entités : bornés par leur maximum (mise à l'échelle)
            top = self.entity_sheet(m)["pv_max"]
            m["pv"] = top if m.get("pv") is None else max(0, min(int(m["pv"]), top))

    # ==================================================================================
    # Niveau, expérience, classes
    # ==================================================================================
    @property
    def total_level(self) -> int:
        return max(1, self.ch.niveau_total)

    @property
    def prof(self) -> int:
        return R.proficiency_bonus(self.total_level)

    def level_from_xp(self) -> int:
        xp = self.ch.experience
        return max(i + 1 for i, t in enumerate(R.XP_THRESHOLDS) if xp >= t)

    def class_level(self, name: str) -> int:
        c = self.ch.find_class(name)
        return c["niveau"] if c else 0

    def active_subclass(self, entry: dict) -> str:
        """Sous-classe effective (vide si le niveau requis n'est pas atteint)."""
        need = self.subclass_level(entry["nom"])
        return entry.get("sous_classe", "") if entry["niveau"] >= need else ""

    # ---- commandes -------------------------------------------------------------------
    def _level_up_heal(self, total_before: int) -> None:
        """Après une montée de niveau, les PV actuels se calent sur les nouveaux PV maximums (aucun calcul manuel)."""
        if self.ch.niveau_total > total_before:
            if self.ch.pv_mode == "jets":
                self.ensure_hp_rolls()
            self.ch.pv_actuels = self.hp_max()

    def set_class_level(self, idx: int, level: int) -> None:
        before = self.ch.niveau_total
        others = before - self.ch.classes[idx]["niveau"]
        self.ch.classes[idx]["niveau"] = max(1, min(level, R.MAX_LEVEL - others))
        self.normalize()
        self._level_up_heal(before)

    def set_total_level(self, target: int, active_idx: int = 0) -> None:
        """Modifie le niveau global en ajustant d'abord la classe active, puis les autres."""
        cls = self.ch.classes
        before = self.ch.niveau_total
        target = max(len(cls), min(R.MAX_LEVEL, target))
        delta = target - before
        order = [active_idx] + [i for i in range(len(cls) - 1, -1, -1) if i != active_idx]
        for i in order:
            if delta == 0:
                break
            if delta > 0:
                cls[i]["niveau"] += delta
                delta = 0
            else:
                take = min(-delta, cls[i]["niveau"] - 1)
                cls[i]["niveau"] -= take
                delta += take
        self.normalize()
        self._level_up_heal(before)

    def add_class(self, name: str) -> bool:
        if name not in self.db.classes or self.ch.find_class(name) or self.ch.niveau_total >= R.MAX_LEVEL:
            return False
        before = self.ch.niveau_total
        self.ch.multiclassage = True                   # ajouter une classe = multiclassage (l'interface le verrouille)
        self.ch.classes.append({"nom": name, "niveau": 1, "sous_classe": "", "pv_jets": []})
        self.normalize()
        self._level_up_heal(before)
        return True

    def remove_class(self, idx: int) -> bool:
        if len(self.ch.classes) <= 1 or not 0 <= idx < len(self.ch.classes):
            return False
        removed = self.ch.classes.pop(idx)
        self.purge_class(removed["nom"])
        self.normalize()
        return True

    def change_class(self, idx: int, name: str) -> bool:
        """Remplace la classe située à l'index `idx` (sous-classe, tirages de PV et sorts réinitialisés)."""
        if name not in self.db.classes or self.ch.find_class(name) or not 0 <= idx < len(self.ch.classes):
            return False
        old = self.ch.classes[idx]["nom"]
        self.ch.classes[idx].update({"nom": name, "sous_classe": "", "pv_jets": []})
        self.purge_class(old)
        if idx == 0:
            self.apply_default_saves()
        self.normalize()
        return True

    def purge_class(self, old: str) -> None:
        """
        Retire les spécificités d'une classe quittée (changement ou retrait) pour éviter toute superposition :
        sorts et concentration de cette classe, états de classe (Rage, Chant de la lame…), ressources dépensées,
        forme sauvage, manifestations et pacte (Occultiste), ascendance (Ensorceleur), emplacements dépensés,
        sorts mineurs de combat devenus inaccessibles, réaction du round.
        """
        ch = self.ch
        lost = {s["nom"] for s in ch.sorts.pop(old, [])}
        if ch.concentration and ch.concentration in lost:
            self.break_concentration()
        key = norm(old)
        class_fx = {k for k, e in FX.EFFECTS.items() if key in norm(e.get("source", ""))}
        ch.effets_actifs = [k for k in ch.effets_actifs if k not in class_fx]
        ch.effets_retires = [k for k in ch.effets_retires if k not in class_fx]
        ch.emplacements_utilises = [0] * 9          # la table d'emplacements change : on repart d'une table neuve
        ch.pacte_utilises = 0
        ch.reaction_utilisee = ""
        if old == "Druide" and ch.forme_type == "sauvage":
            ch.forme_active, ch.forme_type, ch.forme_pv = "", "", 0
        if old == "Occultiste":
            ch.manifestations, ch.pacte = [], ""
        if old == "Ensorceleur":
            ch.ascendance_ensorceleur = ""
        self.normalize()                             # ressources et styles devenus invalides : retirés ici
        keep = set(self.available_cantrips())
        for c in ch.sorts_mineurs:
            if c.get("nom") and c["nom"] not in keep:
                c["nom"] = ""

    def set_multiclass(self, enabled: bool) -> list[str]:
        """Active / désactive l'option Multiclassage. Désactivée : seule la classe principale est conservée
        (les classes secondaires et leurs capacités sont retirées). Renvoie les classes retirées."""
        self.ch.multiclassage = bool(enabled)
        removed = []
        if not enabled:
            while len(self.ch.classes) > 1:
                removed.append(self.ch.classes[-1]["nom"])
                self.remove_class(len(self.ch.classes) - 1)
        self.normalize()
        return removed

    # ==================================================================================
    # Caractéristiques
    # ==================================================================================
    def base_score(self, ab: str) -> int:
        ch = self.ch
        if ch.methode == "achat":
            return ch.scores_achat.get(ab, 8)
        if ch.methode == "manuel":
            return ch.scores_manuel.get(ab, 10)
        idx = ch.des_affectation.get(ab, -1)
        if 0 <= idx < len(ch.des_tirages):
            return ch.des_tirages[idx]["total"]
        return 10

    def buy_step(self, ability: str, delta: int) -> bool:
        """Point Buy : monte/baisse une valeur d'un cran. Retourne False si le mouvement est interdit."""
        new = R.point_buy_step(self.ch.scores_achat, ability, delta)
        if new == self.ch.scores_achat:
            return False
        self.ch.scores_achat = new
        return True

    def reset_scores(self) -> None:
        """Réinitialise la méthode active : Point Buy -> 8 partout (27 points restants), saisie manuelle -> 10 partout."""
        if self.ch.methode == "manuel":
            self.ch.scores_manuel = {ab: 10 for ab in ABILITIES}
        else:
            self.ch.scores_achat = {ab: R.POINT_BUY_MIN for ab in ABILITIES}

    @memo
    def race_rule(self) -> dict:
        """
        Règle de bonus de caractéristiques de la race (champ « caracteristiques » de Races.json) :
        {'fixe': {carac: bonus}, 'libres': [bonus...], 'alternative': [..] ou [], 'libre_regle': bool}.
        """
        ch = self.ch
        bg_abilities = self.background_abilities()
        if bg_abilities:                                  # 2024 : bonus de l'historique, sur ses 3 caractéristiques
            return {"fixe": {}, "libres": [1, 1, 1] if ch.bonus_alt else [2, 1], "alternative": [1, 1, 1],
                    "libre_regle": True, "choix": bg_abilities, "origine": "historique"}
        info = self.db.race_ability_rule(ch.race)
        if ch.regle_libre or not info:
            return {"fixe": {}, "libres": [1, 1, 1] if ch.bonus_alt else [2, 1], "alternative": [1, 1, 1],
                    "libre_regle": True}
        libres = list(info["alternative"]) if ch.bonus_alt and info["alternative"] else list(info["libres"])
        return {"fixe": dict(info["fixe"]), "libres": libres, "alternative": list(info["alternative"]),
                "libre_regle": False}

    def _acquis(self) -> dict:
        acq = self.ch.race_acquis if isinstance(self.ch.race_acquis, dict) else {}
        for k in ("langues", "langues_texte", "competences"):
            acq.setdefault(k, [])
        self.ch.race_acquis = acq
        return acq

    def apply_race_languages(self) -> None:
        """Ajoute les langues de la race (Races.json) : celles de Langues.json sont cochées, les autres notées.
        Seules les langues réellement ajoutées sont mémorisées (retirées si l'on change de race)."""
        known = {norm(n): n for n in self.db.language_names()}
        acq = self._acquis()
        extras = []
        langs = list(self.db.race_languages(self.ch.race)) + list((self.subrace() or {}).get("langues", []))
        for lang in langs:
            key = norm(lang)
            if key in known:
                if known[key] not in self.ch.langues_liste:
                    self.ch.langues_liste.append(known[key])
                    acq["langues"].append(known[key])
            elif lang and "choix" not in key and lang not in self.ch.langues:
                extras.append(lang)
                acq["langues_texte"].append(lang)
        if extras:
            self.ch.langues = (self.ch.langues + ("; " if self.ch.langues else "") + "; ".join(extras)).strip()

    def purge_race_grants(self) -> dict:
        """
        Retire ce que l'ancienne race avait accordé : langues (sauf le Commun, langue de base) et compétences
        maîtrisées grâce à elle (sauf si l'historique les donne aussi). Sauvegardes anciennes sans suivi : on
        se fonde sur les données de la race quittée.
        """
        ch, acq = self.ch, self._acquis()
        langs, texts, skills = list(acq["langues"]), list(acq["langues_texte"]), list(acq["competences"])
        if not (langs or texts or skills) and ch.race:    # fiche sans suivi : on relit l'ancienne race
            known = {norm(n): n for n in self.db.language_names()}
            langs = [known[norm(x)] for x in self.db.race_languages(ch.race) if norm(x) in known]
            skills = self._race_skill_names()
        langs = [x for x in langs if norm(x) != "commun"]
        ch.langues_liste = [x for x in ch.langues_liste if x not in langs]
        if texts:
            parts = [p.strip() for p in ch.langues.split(";") if p.strip() and p.strip() not in texts]
            ch.langues = "; ".join(parts)
        background = set(ch.competences_historique)
        removed = []
        for sk in skills:
            if sk in background:
                continue
            entry = ch.competences.get(sk)
            if entry and entry.get("maitrise"):
                entry["maitrise"] = False
                entry["expertise"] = False
                removed.append(sk)
        ch.race_acquis = {"langues": [], "langues_texte": [], "competences": []}
        return {"langues": langs + texts, "competences": removed}

    def change_race(self, race: str) -> dict:
        """Changement de race : retrait des acquis de l'ancienne, remise à zéro des bonus, acquis de la nouvelle."""
        removed = self.purge_race_grants()
        ch = self.ch
        ch.race, ch.sous_race = race, ""
        ch.bonus_libres, ch.bonus_alt, ch.regle_libre = [], False, False
        self.normalize()
        self.apply_race_languages()
        self.apply_race_skills()
        self.normalize()
        return removed

    def subrace(self) -> Optional[dict]:
        for s in self.db.subraces_of(self.ch.race):
            if s["nom"] == self.ch.sous_race:
                return s
        return None

    @memo
    def race_bonus(self) -> dict[str, int]:
        out = {ab: 0 for ab in ABILITIES}
        rule = self.race_rule()
        for ab, v in rule["fixe"].items():
            if ab in out:
                out[ab] += v
        sub = self.subrace()
        if sub and not rule["libre_regle"]:
            for ab, v in sub.get("bonus", {}).items():
                if ab in out:
                    out[ab] += v
        used = set()
        allowed = set(rule.get("choix") or ABILITIES)
        for i, v in enumerate(rule["libres"]):          # bonus libres : caractéristiques toutes différentes
            pick = self.ch.bonus_libres[i] if i < len(self.ch.bonus_libres) else ""
            if pick in out and pick not in used and pick in allowed:
                out[pick] += v
                used.add(pick)
        return out

    @memo
    def asi_slots(self) -> list[dict]:
        """Emplacements d'amélioration de caractéristiques débloqués (un par capacité de classe)."""
        slots = []
        for e in self.ch.classes:
            cls = self.db.classes.get(e["nom"], {})
            for f in cls.get("capacites_classe", []):
                if R.is_asi_feature(f["nom"]) and f["niveau"] <= e["niveau"]:
                    slots.append({"id": f"{e['nom']}|{f['niveau']}", "classe": e["nom"], "niveau": f["niveau"],
                                  "label": f"{e['nom']} — niveau {f['niveau']}"})
        if self.race_grants_feat():                      # Humain variant : un don au niveau 1
            slots.insert(0, {"id": "race|don", "classe": "Race", "niveau": 1, "don_seul": True,
                             "label": "{} — don de départ".format(self.ch.race)})
        for name in self.ch.dons_mj:                     # dons accordés par le MJ, hors progression
            slots.append({"id": "mj|" + name, "classe": "MJ", "niveau": 0, "don_seul": True, "mj": True,
                          "label": "📜 Don accordé par le MJ"})
        return slots

    def race_grants_feat(self) -> bool:
        """Espèce qui accorde un don au choix (trait « Don » : Humain variant)."""
        return any(norm(c.get("nom", "")) == "don" for c in self.race_capacities())

    def add_gm_feat(self, name: str) -> bool:
        """Don accordé par le MJ : emplacement supplémentaire, don déjà choisi (bonus appliqués automatiquement)."""
        if name not in self.db.feats or name in self.ch.dons_mj:
            return False
        self.ch.dons_mj.append(name)
        self.ch.ameliorations["mj|" + name] = {"mode": "don", "don": name, "don_carac": "", "a1": "", "a2": ""}
        self.normalize()
        return True

    def remove_gm_feat(self, name: str) -> None:
        self.ch.dons_mj = [n for n in self.ch.dons_mj if n != name]
        self.ch.ameliorations.pop("mj|" + name, None)
        self.normalize()

    @memo
    def chosen_feats(self) -> list[str]:
        ids = {s["id"] for s in self.asi_slots()}
        origin = self.origin_feat()
        out = [origin] if origin else []                  # 2024 : don d'origine accordé par l'historique
        for sid, choice in self.ch.ameliorations.items():
            if sid in ids and choice.get("mode") == "don" and choice.get("don") in self.db.feats:
                out.append(choice["don"])
        return out

    def feat_effect(self, key: str) -> int:
        return sum(int(self.db.feats[f].get("effets", {}).get(key, 0)) for f in self.chosen_feats())

    def feat_choice_ability(self, choice: dict) -> str:
        """Caractéristique augmentée de +1 par un don (choix unique automatique, sinon choix du joueur)."""
        feat = self.db.feats.get(choice.get("don", ""))
        if not feat or not feat["carac_choix"]:
            return ""
        if len(feat["carac_choix"]) == 1:
            return feat["carac_choix"][0]
        return choice.get("don_carac", "") if choice.get("don_carac") in feat["carac_choix"] else feat["carac_choix"][0]

    @memo
    def asi_bonus(self) -> dict[str, int]:
        out = {ab: 0 for ab in ABILITIES}
        valid = {s["id"] for s in self.asi_slots()}
        for sid, c in self.ch.ameliorations.items():
            if sid not in valid:
                continue
            mode = c.get("mode")
            if mode == "plus2" and c.get("a1") in out:
                out[c["a1"]] += 2
            elif mode == "plus1x2":
                for key in ("a1", "a2"):
                    if c.get(key) in out:
                        out[c[key]] += 1
            elif mode == "don":
                ab = self.feat_choice_ability(c)
                if ab in out:
                    out[ab] += 1
        return out

    def resilient_saves(self) -> set[str]:
        """Maîtrises de jets de sauvegarde accordées par les dons « Résistant / Résilient »."""
        valid = {s["id"] for s in self.asi_slots()}
        out = set()
        for sid, c in self.ch.ameliorations.items():
            if sid in valid and c.get("mode") == "don" and norm(c.get("don", "")) in ("resistant", "resilient"):
                ab = self.feat_choice_ability(c)
                if ab:
                    out.add(ab)
        return out

    def feat_status(self, name: str) -> tuple[str, str]:
        """
        Évalue le prérequis d'un don. Retourne (état, message) avec état « ok », « ko » (non rempli)
        ou « ? » (formulation non reconnue : à vérifier à la main).
        """
        feat = self.db.feats.get(name)
        text = (feat or {}).get("prerequis", "")
        n = norm(text)
        if not feat or n in ("", "aucun", "aucune"):
            return "ok", ""
        ch = self.ch
        if "13 ou plus" in n or re.search(r"de \d+ ou plus", n):
            need = int(re.search(r"(\d+) ou plus", n).group(1))
            abs_ = [ab for ab in ABILITIES if norm(ab) in n]
            ok = any(self.score(ab) >= need for ab in abs_)
            return ("ok", "") if ok else ("ko", text)
        if "armures intermediaires" in n:
            return ("ok", "") if R.armor_proficient("intermédiaire", self.armor_proficiencies()) else ("ko", text)
        if "armures lourdes" in n:
            return ("ok", "") if R.armor_proficient("lourde", self.armor_proficiencies()) else ("ko", text)
        m = re.search(r"outils de (\w+)", n)
        if m:
            owned = " ".join(norm(t) for t in ch.outils) + " " + norm(
                self.db.backgrounds.get(ch.historique, {}).get("outil_maitrise", "") or "")
            return ("ok", "") if m.group(1) in owned else ("ko", text)
        if "lancer" in n and "sort" in n:
            return ("ok", "") if (self.casters() or self.pact()[0]) else ("ko", text)
        for other in self.db.feats:
            if norm(other) == n:
                return ("ok", "") if other in self.chosen_feats() else ("ko", text)
        race = norm(ch.race)
        small = ("halfelin", "gnome", "kobold", "gobelin")
        if "petite" in n and (race.startswith("nain") or any(race.startswith(x) for x in small)):
            return "ok", ""
        names = [norm(x) for x in re.split(r",| ou ", re.sub(r"\(.*?\)", "", text)) if x.strip()]
        known_races = [r for r in names if any(norm(rn).startswith(r) or r.startswith(norm(rn)) for rn in self.db.races)]
        if known_races:
            return ("ok", "") if any(race.startswith(r) or r.startswith(race) for r in known_races) else ("ko", text)
        return "?", text

    @memo
    def score_parts(self, ab: str) -> dict[str, int]:
        ch = self.ch
        beast = self.wild_form()
        mental_too = self.ch.forme_type == "metamorphose"               # Métamorphose : les 6 caractéristiques
        if beast is not None and (mental_too or ab in ("Force", "Dextérité", "Constitution")):
            score = beast["carac"][R.ABBR[ab].upper()][0]                       # de la bête
            return {"base": score, "race": 0, "asi": 0, "divers": 0, "total": score, "champion": 0,
                    "sans_effets": score, "effets": 0, "effets_sources": [], "forme": beast["nom"],
                    "forme_type": self.ch.forme_type}
        base = self.base_score(ab)
        race = self.race_bonus()[ab]
        asi = self.asi_bonus()[ab]
        champion = 4 if ab in ("Force", "Constitution") and self.class_level("Barbare") >= 20 else 0
        cap = 24 if champion else 20
        raw = min(base + race + asi + champion, cap)
        total = raw + ch.bonus_divers.get(ab, 0)
        fx_bonus, fx_floor, fx_src = self.ability_effects(ab)      # potions de force de géant, sorts...
        effective = max(min(total + fx_bonus, max(cap, total)), fx_floor)
        return {"base": base, "race": race, "asi": asi, "divers": ch.bonus_divers.get(ab, 0),
                "total": effective, "champion": champion, "sans_effets": total,
                "effets": effective - total, "effets_sources": fx_src}

    def score(self, ab: str) -> int:
        return self.score_parts(ab)["total"]

    def mod(self, ab: str) -> int:
        return R.ability_modifier(self.score(ab))

    def mods(self) -> dict[str, int]:
        return {ab: self.mod(ab) for ab in ABILITIES}

    # ==================================================================================
    # Classes : aptitudes, ressources, maîtrises
    # ==================================================================================
    @memo
    def features(self, entry: dict) -> list[dict]:
        """Toutes les aptitudes (classe + sous-classe choisie) avec leur état de déblocage."""
        cls = self.db.classes.get(entry["nom"], {})
        out = []
        for f in cls.get("capacites_classe", []):
            out.append({"niveau": f["niveau"], "nom": f["nom"], "description": f["description"],
                        "source": entry["nom"], "sous_classe": False, "debloque": f["niveau"] <= entry["niveau"]})
        sub = self.db.subclass(entry["nom"], entry.get("sous_classe", ""))
        if sub:
            for f in sub["capacites"]:
                out.append({"niveau": f["niveau"], "nom": f["nom"], "description": f["description"],
                            "source": sub["nom"], "sous_classe": True, "debloque": f["niveau"] <= entry["niveau"]})
        out.sort(key=lambda f: (f["niveau"], f["sous_classe"], f["nom"]))
        return out

    @memo
    def unlocked_feature_names(self) -> list[str]:
        names = []
        for e in self.ch.classes:
            names += [norm(f["nom"]) for f in self.features(e) if f["debloque"]]
        return names

    @memo
    def has_feature(self, fragment: str) -> bool:
        frag = norm(fragment)
        return any(frag in n for n in self.unlocked_feature_names())

    def resources(self, entry: dict) -> list[tuple[str, str]]:
        row = self.table_row(entry["nom"], entry["niveau"])
        if row:                                              # 2024 : ressources lues dans la table de progression
            return [(RESOURCE_LABELS_2024.get(k, k.replace("_", " ").capitalize()), _fmt_cell(v))
                    for k, v in row.items() if k not in ("niveau", "bonus_de_maitrise", "capacites", "emplacements",
                                                         "sorts_prepares", "tours_de_magie") and v not in (None, "", "—", 0)]
        return R.class_resources(entry["nom"], entry["niveau"], self.mods(), self.prof)

    def first_class(self) -> str:
        return self.ch.classes[0]["nom"] if self.ch.classes else ""

    def armor_proficiencies(self) -> list[str]:
        out = []
        for i, e in enumerate(self.ch.classes):
            out += self.db.start_info(e["nom"])["armures"] if i == 0 else R.MULTICLASS_PROFS.get(e["nom"], ([], []))[0]
        sub = self.subrace()
        if sub and "montagnes" in norm(sub["nom"]):
            out += ["Armures légères", "Armures intermédiaires"]
        return out + self.extra_armor_profs()             # v43 : sous-classes (Domaine de la Guerre…)

    def weapon_proficiencies(self) -> list[str]:
        out = []
        for i, e in enumerate(self.ch.classes):
            out += self.db.start_info(e["nom"])["armes"] if i == 0 else R.MULTICLASS_PROFS.get(e["nom"], ([], []))[1]
        return out + self.racial_weapon_proficiencies() + self.extra_weapon_profs()

    # ==================================================================================
    # Compétences et sauvegardes
    # ==================================================================================
    def default_saves(self) -> list[str]:
        return self.db.start_info(self.first_class())["sauvegardes"] if self.ch.classes else []

    def apply_default_saves(self) -> None:
        defaults = set(self.default_saves())
        for ab in ABILITIES:
            self.ch.sauvegardes[ab] = ab in defaults

    @memo
    def save_rows(self) -> list[dict]:
        rows = []
        aura = max(0, self.mod("Charisme")) if self.class_level("Paladin") >= 6 else 0
        res = self.resilient_saves()
        items = self.magic_item_bonuses()["js"]
        polymorph = self.ch.forme_type == "metamorphose" and bool(self.ch.forme_active)
        for ab in ABILITIES:
            prof = (self.ch.sauvegardes.get(ab, False) or ab in res) and not polymorph
            fx = self.save_mods(ab)
            value = self.mod(ab) + (self.prof if prof else 0) + aura + items + fx["bonus"]
            detail = [(R.mod_label(ab), "{:+d}".format(self.mod(ab)))]
            if prof:
                detail.append(("Maîtrise", "{:+d}".format(self.prof)))
            if aura:
                detail.append(("Aura de protection", "{:+d}".format(aura)))
            if items:
                detail.append(("Objets magiques", "{:+d}".format(items)))
            if ab == "Constitution" and self.concentration_advantage():
                detail.append(("Esprit occulte : avantage pour maintenir la concentration", "▲"))
            rows.append({"carac": ab, "maitrise": prof, "bonus": value, "auto": ab in res, "des": fx["des"],
                         "etat": M.adv_state(fx), "avantage": fx["avantage"], "desavantage": fx["desavantage"],
                         "echec": fx["echec"], "detail": detail + fx["detail"]})
        return rows

    @memo
    def skill_rows(self) -> list[dict]:
        jack = self.has_feature("touche-a-tout")
        remarkable = self.has_feature("athlete remarquable")
        beast_skills = self.beast_skills()
        granted_skills = self.invocation_skills()
        rows = []
        for s in self.db.skills:
            name, ab = s["nom"], s["carac"]
            st = self.ch.competences.get(name, {})
            prof = bool(st.get("maitrise")) or name in granted_skills     # Présence captivante (manifestation)
            exp = bool(st.get("expertise")) and prof
            half, up = False, False
            if not prof:
                if jack:
                    half = True
                elif remarkable and ab in ("Force", "Dextérité", "Constitution"):
                    half, up = True, True
            if self.ch.forme_type == "metamorphose" and self.ch.forme_active:   # maîtrises de la bête seulement
                prof = exp = half = up = False
            base = R.skill_bonus(self.mod(ab), self.prof, prof, exp, half, up)
            beast_bonus = beast_skills.get(norm(name))
            use_beast = beast_bonus is not None and (beast_bonus > base or self.ch.forme_type == "metamorphose")
            if use_beast:
                base = beast_bonus
            fx = self.check_mods(ab, name)
            detail = [(R.mod_label(ab), "{:+d}".format(self.mod(ab)))]
            if use_beast:
                detail = [("Compétence de la bête ({})".format(self.ch.forme_active), "{:+d}".format(base))]
            elif base != self.mod(ab):
                detail.append(("Expertise" if exp else "Maîtrise" if prof else "Demi-maîtrise",
                               "{:+d}".format(base - self.mod(ab))))
            rows.append({"nom": name, "carac": ab, "maitrise": prof, "expertise": exp, "bonus": base + fx["bonus"],
                         "historique": name in self.ch.competences_historique, "des": fx["des"],
                         "etat": M.adv_state(fx), "avantage": fx["avantage"], "desavantage": fx["desavantage"],
                         "echec": fx["echec"], "detail": detail + fx["detail"]})
        return rows

    def skill_bonus(self, name: str) -> int:
        return next((r["bonus"] for r in self.skill_rows() if r["nom"] == name), 0)

    def passive_perception(self) -> int:
        """10 + Perception (+5 avec avantage, -5 avec désavantage — PHB)."""
        row = next((r for r in self.skill_rows() if r["nom"] == "Perception"), {"bonus": 0, "etat": ""})
        adv = 5 if row["etat"] == "avantage" else -5 if row["etat"] in ("désavantage", "échec") else 0
        return 10 + row["bonus"] + adv + self.feat_effect("perception_passive")

    def class_skill_status(self) -> dict:
        """Compétences de classe : liste de choix, nombre autorisé, nombre coché (hors historique)."""
        info = self.db.start_info(self.first_class()) if self.ch.classes else {"competences": [], "nb_competences": 0}
        picked = [n for n, st in self.ch.competences.items()
                  if st.get("maitrise") and n not in self.ch.competences_historique]
        return {"options": info["competences"], "nombre": info["nb_competences"], "choisies": picked}

    def apply_background(self) -> None:
        """Applique les compétences de l'historique (et retire celles de l'ancien historique)."""
        bg = self.db.backgrounds.get(self.ch.historique)
        new = []
        if bg:
            for key in ("competence_1", "competence_2"):
                if bg.get(key):
                    new.append(self.db.canonical_skill(bg[key]))
        for s in self.ch.competences_historique:
            if s not in new and s in self.ch.competences:
                self.ch.competences[s] = {"maitrise": False, "expertise": False}
        for s in new:
            self.ch.competences.setdefault(s, {"maitrise": False, "expertise": False})["maitrise"] = True
        self.ch.competences_historique = new

    # ==================================================================================
    # Race
    # ==================================================================================
    def race_traits(self) -> list[dict]:
        race = self.db.races.get(self.ch.race)
        out = [{"nom": c["nom"], "description": c["description"]} for c in (race or {}).get("capacites", [])]
        sub = self.subrace()
        if sub and sub.get("capacites"):                 # sous-espèce décrite trait par trait (Haut-elfe…)
            out += [{"nom": "{} ({})".format(c["nom"], sub["nom"]), "description": c["description"]}
                    for c in sub["capacites"]]
        elif sub:
            out.append({"nom": f"Sous-race : {sub['nom']}", "description": sub.get("description", "")})
        return out

    def race_capacities(self) -> list[dict]:
        """Traits bruts de l'espèce + ceux de la sous-espèce choisie (sorts, effets innés, maîtrises)."""
        race = self.db.races.get(self.ch.race) or {}
        sub = self.subrace() or {}
        return list(race.get("capacites", [])) + list(sub.get("capacites", []))

    def racial_weapon_proficiencies(self) -> list[str]:
        """Maîtrises d'armes raciales (« Entraînement aux armes elfiques / drow », « Maîtrise d'armes ») :
        chaque arme citée dans le trait devient une maîtrise."""
        out = []
        for c in self.race_capacities():
            n = norm(c.get("nom", ""))
            if "armes" in n and ("entrainement" in n or "maitrise" in n):
                text = re.sub(r"^.*?(maitrise|maitrisez)\s+", "", norm(c["description"]))
                for item in re.split(r",|;|\bet\b", text):
                    item = re.sub(r"^\s*((de|des|du|la|le|les)\s+|[ld]')+", "", item).strip(" .")
                    if not item:
                        continue
                    parts = [x.strip() for x in item.split("/")]       # « épées courtes/longues »
                    head = parts[0].split()[0] if parts[0].split() else ""
                    out += [parts[0]] + [x if " " in x or not head else "{} {}".format(head, x) for x in parts[1:]]
        return out

    def _race_skill_names(self) -> list[str]:
        """Compétences nommées explicitement par les traits de la race (« Sens aiguisés » : Perception)."""
        out = []
        names = {norm(s): s for s in self.db.skill_names}
        for c in self.race_capacities():
            d = norm(c.get("description", ""))
            if "maitrise" not in d or "au choix" in d or "de votre choix" in d or "parmi" in d:
                continue
            out += [skill for key, skill in names.items() if re.search(r"\b" + re.escape(key) + r"\b", d)]
        return list(dict.fromkeys(out))

    def apply_race_skills(self) -> list[str]:
        """Compétences raciales explicites cochées au choix de l'espèce (mémorisées pour un retrait ultérieur)."""
        added = []
        acq = self._acquis()
        for skill in self._race_skill_names():
            entry = self.ch.competences.setdefault(skill, {"maitrise": False, "expertise": False})
            if not entry.get("maitrise"):
                entry["maitrise"] = True
                added.append(skill)
                acq["competences"].append(skill)
        return added

    def speed(self) -> float:
        """Vitesse de marche en mètres."""
        base = float(self.db.speeds.get(self.ch.race, 9))
        sub = self.subrace()
        if sub and "vitesse" in sub:
            base = float(sub["vitesse"])
        base += self.feat_effect("vitesse")
        armor = self.db.armors.get(self.ch.armure.get("nom", ""), {})
        heavy = armor.get("categorie") == "lourde"
        if self.class_level("Barbare") >= 5 and not heavy:
            base += 3
        if norm(self.armor_model()[0]).startswith("infiltre"):
            base += 1.5                                      # armure d'exocombat « Infiltré »
        monk = self.class_level("Moine")
        if monk >= 2 and armor.get("categorie", "aucune") == "aucune" and not self.ch.armure.get("bouclier"):
            base += 3 if monk < 6 else 4.5 if monk < 10 else 6 if monk < 14 else 7.5 if monk < 18 else 9
        beast = self.wild_form()
        if beast is not None:                                # Forme sauvage : vitesse de marche de la bête
            m = re.match(r"\s*([\d,\.]+)", beast["vitesse"])
            base = float(m.group(1).replace(",", ".")) if m else base
        fx = self.effect_mods()                              # effets actifs (Hâte ×2, Entravé 0, Grande foulée +3 m...)
        return max(0.0, (base + fx["vitesse_bonus"]) * fx["vitesse_mult"])

    def speed_text(self) -> str:
        """Vitesse en mètres ET en cases de 1,50 m : « 9 m (6 cases) »."""
        return R.fmt_speed(self.speed())

    def shield_bonus(self) -> int:
        a = self.ch.armure
        if not a.get("bouclier"):
            return 0
        sh = self.db.shields.get(a.get("bouclier_nom", "")) or self.db.shield
        return int(sh.get("bonus_ca", 2)) + int(a.get("bonus_bouclier", 0))

    # ==================================================================================
    # Points de vie
    # ==================================================================================
    def _hp_bonus_per_level(self, entry: dict) -> int:
        bonus = self.feat_effect("pv_par_niveau")
        sub = self.subrace()
        if sub:
            bonus += int(sub.get("pv_par_niveau", 0))
        race = self.db.races.get(self.ch.race, {})
        if any("+1 pv par niveau" in norm(c.get("description", "")) for c in race.get("capacites", [])):
            bonus += 1                                      # ex. « Ténacité naine » du nain des collines
        if entry["nom"] == "Ensorceleur" and "draconique" in norm(self.active_subclass(entry)):
            bonus += 1
        return bonus

    @staticmethod
    def _roll_index(class_idx: int, level: int) -> int:
        return level - 2 if class_idx == 0 else level - 1

    @memo
    def hp_breakdown(self) -> list[dict]:
        con = self.mod("Constitution")
        out = []
        for ci, e in enumerate(self.ch.classes):
            sides = R.die_sides(self.db.start_info(e["nom"])["de_vie"])
            extra = self._hp_bonus_per_level(e)
            total = 0
            for lvl in range(1, e["niveau"] + 1):
                if ci == 0 and lvl == 1:
                    gained = sides
                elif self.ch.pv_mode == "jets":
                    ri = self._roll_index(ci, lvl)
                    gained = e["pv_jets"][ri] if 0 <= ri < len(e["pv_jets"]) else R.average_die(sides)
                else:
                    gained = R.average_die(sides)
                total += max(1, gained + con + extra)
            out.append({"classe": e["nom"], "niveau": e["niveau"], "de": f"d{sides}", "pv": total})
        return out

    def hp_max(self) -> int:
        if not self.ch.classes:
            return 1
        fx = self.effect_mods()
        hp = max(1, sum(b["pv"] for b in self.hp_breakdown()) + self.ch.pv_divers + fx["pv_max"])   # Aide : +5
        return max(1, hp // 2) if fx["pv_moitie"] else hp                                        # Épuisement 4+

    def hit_dice(self) -> dict[str, int]:
        dice: dict[str, int] = {}
        for e in self.ch.classes:
            d = self.db.start_info(e["nom"])["de_vie"]
            dice[d] = dice.get(d, 0) + e["niveau"]
        return dice

    def roll_hp(self, rng: Optional[random.Random] = None) -> None:
        """Tire les dés de vie de tous les niveaux (hors premier niveau du personnage)."""
        rng = rng or random
        for ci, e in enumerate(self.ch.classes):
            sides = R.die_sides(self.db.start_info(e["nom"])["de_vie"])
            count = e["niveau"] - (1 if ci == 0 else 0)
            e["pv_jets"] = [rng.randint(1, sides) for _ in range(max(0, count))]
        self.ch.pv_mode = "jets"
        self.normalize()

    def ensure_hp_rolls(self, rng: Optional[random.Random] = None) -> None:
        """Complète les tirages manquants (quand le niveau augmente en mode « jets »)."""
        rng = rng or random
        for ci, e in enumerate(self.ch.classes):
            sides = R.die_sides(self.db.start_info(e["nom"])["de_vie"])
            need = max(0, e["niveau"] - (1 if ci == 0 else 0))
            while len(e["pv_jets"]) < need:
                e["pv_jets"].append(rng.randint(1, sides))

    # ==================================================================================
    # Combat
    # ==================================================================================
    def initiative(self) -> int:
        """v45 : Dextérité, dons (Alerte), effets actifs et aptitudes de classe (voir initiative_detail)."""
        return self.initiative_detail()["total"]

    # ---- Classe d'armure : valeur ET formule lisible ----------------------------------
    @staticmethod
    def _signed_sum(values: list[int]) -> str:
        """[10, -1, 2] -> '10 - 1 + 2'."""
        out = str(values[0])
        for v in values[1:]:
            out += f" - {abs(v)}" if v < 0 else f" + {v}"
        return out

    @memo
    def armor_class_detail(self) -> dict:
        """
        Calcule la CA et la décompose. Retourne :
          valeur   : CA finale
          formule  : « 12 + Dex (max 2) + 2 (bouclier) »   (règle appliquée, symbolique)
          chiffres : « 12 + 2 + 2 = 16 »                    (même calcul avec les valeurs du personnage)
          note     : origine du calcul sans armure (« Défense sans armure (barbare) »...) ou chaîne vide
          variable : False si la CA ne dépend d'aucune caractéristique (ex. harnois : « CA = 18 »)
        """
        beast = self.wild_form()
        if beast is not None:                                         # Forme sauvage : CA de la bête
            ca = self.beast_ac(beast)
            return {"valeur": ca, "formule": "CA de la bête ({})".format(beast["nom"]),
                    "chiffres": "{} = {}".format(ca, ca), "note": "Forme sauvage", "variable": False}
        a = self.ch.armure
        armor = self.db.armors.get(a.get("nom", "Aucune armure"))
        dex = self.mod("Dextérité")
        worn = armor is not None and armor["categorie"] != "aucune"
        ab = lambda name: R.ABBR[name].capitalize()  # noqa: E731  (« Dex », « Con », « Sag »...)
        note = ""
        if worn:
            base = armor["ca_base"]
            dm = armor.get("dex_max")
            if dm is None:
                terms = [(str(base), base), ("Dex", dex)]
            elif dm == 0:
                terms = [(str(base), base)]                       # armure lourde : pas de bonus de Dextérité
            else:
                terms = [(str(base), base), (f"Dex (max {dm})", min(dex, dm))]
        else:
            options = {"": [("10", 10), ("Dex", dex)]}
            if self.class_level("Barbare"):
                options["Défense sans armure (barbare)"] = [("10", 10), ("Dex", dex), ("Con", self.mod("Constitution"))]
            if self.class_level("Moine") and not a.get("bouclier"):
                options["Défense sans armure (moine)"] = [("10", 10), ("Dex", dex), ("Sag", self.mod("Sagesse"))]
            for e in self.ch.classes:
                if e["nom"] == "Ensorceleur" and "draconique" in norm(self.active_subclass(e)):
                    options["Résilience draconique"] = [("13", 13), ("Dex", dex)]
                if (e["nom"] == "Guerrier" and e["niveau"] >= 10 and "pancratiaste" in norm(self.active_subclass(e))
                        and not a.get("bouclier")):
                    options["Garde de pugiliste"] = [("10", 10), ("Dex", dex), ("Con", self.mod("Constitution"))]
            if "armure_mage" in self.active_effect_keys():             # effet actif « Armure du mage »
                options["Armure du mage"] = [("13", 13), ("Dex", dex)]
            note, terms = max(options.items(), key=lambda kv: sum(v for _, v in kv[1]))
        shield = self.shield_bonus()
        if shield:
            terms.append((f"{shield} (bouclier)", shield))
        if int(a.get("bonus", 0)):
            terms.append((f"{int(a['bonus'])} (bonus magique)", int(a["bonus"])))
        items_ac = self.magic_item_bonuses()["ca"]
        if items_ac:
            terms.append((f"{items_ac} (objets magiques)", items_ac))
        if worn and self.style_active("Défense"):
            terms.append(("1 (style Défense)", 1))
        fx_ca = self.effect_mods()["ca"]
        if fx_ca:
            terms.append((f"{fx_ca} (effets actifs)", fx_ca))
        if self.bladesong_active():                                   # Chant de la lame : + mod. Int (min +1)
            bonus = max(1, self.mod("Intelligence"))
            terms.append((f"{bonus} (Chant de la lame, Int)", bonus))
        values = [v for _, v in terms]
        ca_min = self.effect_mods()["ca_min"]
        if ca_min and sum(values) < ca_min:                           # Peau d'écorce : CA minimale 16
            terms, values, note = [(str(ca_min), ca_min)], [ca_min], "CA minimale {} (effet actif)".format(ca_min)
        total = sum(values)
        variable = any(not label[0].isdigit() for label, _ in terms)
        return {"valeur": total, "formule": " + ".join(label for label, _ in terms),
                "chiffres": f"{self._signed_sum(values)} = {total}", "note": note, "variable": variable,
                "termes": list(terms)}

    def ac_breakdown_text(self) -> str:
        """Calcul de la CA en clair (infobulle de l'en-tête, v36) :
        « CA de base (Armure de cuir clouté : 12) + Mod. Dextérité (+3) + Bouclier (+2) = 17 »."""
        d = self.armor_class_detail()
        terms = d.get("termes") or []
        if not terms:
            return "{} = {}".format(d["formule"], d["valeur"])
        names = {"Dex": "Dextérité", "Con": "Constitution", "Sag": "Sagesse", "Int": "Intelligence"}
        armor = self.ch.armure.get("nom", "")
        worn = armor and armor != "Aucune armure" and self.db.armors.get(armor, {}).get("categorie") != "aucune"
        parts = []
        for i, (label, value) in enumerate(terms):
            head = label.split(" ")[0]
            if i == 0 and label[0].isdigit():
                what = armor if worn else (d["note"] or "sans armure")
                parts.append("CA de base ({} : {})".format(what, value))
            elif head in names:
                extra = " max {}".format(label.split("max ")[1].rstrip(")")) if "max" in label else ""
                parts.append("Mod. {}{} ({:+d})".format(names[head], extra, value))
            elif "(" in label:
                parts.append("{} ({:+d})".format(label[label.index("(") + 1:].rstrip(")").capitalize(), value))
            else:
                parts.append("{:+d}".format(value))
        return " + ".join(parts) + " = {}".format(d["valeur"])

    def armor_class(self) -> tuple[int, str]:
        """(CA, formule) — la formule remplace l'ancien simple nom de l'armure."""
        d = self.armor_class_detail()
        return d["valeur"], d["formule"] + (f"  [{d['note']}]" if d["note"] else "")

    def armor_warnings(self) -> list[str]:
        armor = self.db.armors.get(self.ch.armure.get("nom", ""))
        out = []
        if armor and armor["categorie"] != "aucune":
            if not R.armor_proficient(armor["categorie"], self.armor_proficiencies()):
                out.append(f"⚠ Vous ne maîtrisez pas les armures {armor['categorie']}s : désavantage (Force, Dextérité) "
                           "et sorts impossibles.")
        if self.ch.armure.get("bouclier") and not self.shield_proficient():
            out.append("⚠ Vous ne maîtrisez pas les boucliers : désavantage (Force, Dextérité) et sorts impossibles.")
        if armor and armor["categorie"] != "aucune":
            if armor.get("force_min") and self.score("Force") < armor["force_min"]:
                out.append(f"Force {armor['force_min']} requise : vitesse réduite de 3 m.")
            if armor.get("desavantage_discretion"):
                out.append("Désavantage aux tests de Discrétion.")
        return out

    # ---- styles de combat ------------------------------------------------------------
    @memo
    def fighting_style_slots(self) -> list[dict]:
        """
        Emplacements de choix liés au combat, lus dans les aptitudes des classes et sous-classes :
          - « Style de combat » (Guerrier niv. 1, Paladin/Rôdeur niv. 2, Collège des Épées niv. 3,
            « Style de combat supplémentaire » du Champion niv. 10)      -> kind « style »
          - « Modèle d'armure » (Artificier armurier niv. 3)            -> kind « modele »
        Chaque emplacement indique son niveau requis et s'il est débloqué par le niveau actuel.
        """
        slots = []
        for e in self.ch.classes:
            feats = self.features(e)
            styles = sorted((f for f in feats if norm(f["nom"]).startswith("style de combat")),
                            key=lambda f: (f["niveau"], f["nom"]))
            for i, f in enumerate(styles, start=1):
                slots.append({"id": f"{e['nom']}|{i}", "kind": "style", "classe": e["nom"],
                              "niveau_requis": f["niveau"], "debloque": f["debloque"], "source": f["source"]})
            for i, f in enumerate((f for f in feats if norm(f["nom"]).startswith("modele d'armure")), start=1):
                slots.append({"id": f"{e['nom']}|modele{i}", "kind": "modele", "classe": e["nom"],
                              "niveau_requis": f["niveau"], "debloque": f["debloque"], "source": f["source"]})
        return slots

    def model_names(self) -> list[str]:
        """Modèles d'armure de base (Gardien, Infiltré) : les versions « parachevées » sont automatiques au niv. 15."""
        return [n for n in self.db.armor_models if "parachev" not in norm(n)]

    def style_options(self, slot_id: str) -> list[str]:
        """Choix proposés à un emplacement : liste de la classe (sans doublon de style), ou modèles d'armure."""
        if "|modele" in slot_id:
            return self.model_names()
        cls = slot_id.split("|")[0]
        taken = {v for k, v in self.ch.styles_combat.items() if k != slot_id and "|modele" not in k}
        return [n for n in self.db.styles_by_class.get(cls, {}) if n not in taken]

    def chosen_styles(self) -> list[str]:
        """Styles de combat effectivement actifs (emplacement débloqué + choix valide)."""
        out = []
        for slot in self.fighting_style_slots():
            name = self.ch.styles_combat.get(slot["id"], "")
            if slot["kind"] == "style" and slot["debloque"] and name in self.db.styles_by_class.get(slot["classe"], {}):
                out.append(name)
        return out

    def style_active(self, name: str) -> bool:
        return norm(name) in {norm(n) for n in self.chosen_styles()}

    def armor_model(self) -> tuple[str, str]:
        """(nom, description) du modèle d'armure actif ; « parachevé » dès le niveau 15 de l'artificier."""
        for slot in self.fighting_style_slots():
            name = self.ch.styles_combat.get(slot["id"], "")
            if slot["kind"] == "modele" and slot["debloque"] and name in self.db.armor_models:
                if self.class_level(slot["classe"]) >= 15 and f"{name} parachevé" in self.db.armor_models:
                    name = f"{name} parachevé"
                return name, self.db.armor_models[name]
        return "", ""

    # ---- manifestations occultes (invocations) ---------------------------------------
    @memo
    def manifestation_slots(self) -> dict:
        """
        Nombre de manifestations connues : celles de l'Occultiste (niveau de classe) + une par don du type
        « Initié aux arcanes occultes ». Retourne {'classe': n, 'dons': m, 'sources_dons': [...], 'total': n+m}.
        """
        occ = self.class_level("Occultiste")
        row = self.table_row("Occultiste", occ) if occ else {}
        from_class = int(row["invocations"]) if row.get("invocations") is not None else R.invocations_known(occ)
        feats = [f for f in self.chosen_feats() if "arcanes occultes" in norm(f)]
        return {"classe": from_class, "dons": len(feats), "sources_dons": feats, "total": from_class + len(feats)}

    def pact_available(self) -> bool:
        """Choix séparé du pacte (2014, niveau 3). En 2024, le pacte est une manifestation : pas de choix séparé."""
        return self.sheet_edition != 2024 and self.class_level("Occultiste") >= 3

    def manifestation_status(self, name: str) -> tuple[str, str]:
        """(« ok » | « ko », raison) : pacte et niveau d'Occultiste requis par la manifestation."""
        m = self.db.manifestations.get(name)
        if not m:
            return "ko", "manifestation inconnue"
        occ = self.class_level("Occultiste")
        pact_ok = self.ch.pacte == m["pacte"] and (self.sheet_edition == 2024 or self.pact_available())
        if m["pacte"] and not pact_ok:
            return "ko", f"requiert le {m['pacte']}"
        if m["niveau"] and occ < m["niveau"]:
            return "ko", f"Occultiste niveau {m['niveau']} requis"
        issue = self.invocation_prereq_issue(m)
        if issue:
            return "ko", issue
        return "ok", ""

    def granted_spells(self) -> list[dict]:
        """
        Sorts accordés « à volonté » ou gratuitement par les manifestations choisies. Ils sont injectés dans
        l'onglet Magie avec leur source : [{nom, niveau, usage, source, sort}] (sort = fiche de la bibliothèque ou None).
        """
        out = []
        for name in self.ch.manifestations:
            m = self.db.manifestations.get(name)
            if not m or self.manifestation_status(name)[0] != "ok":
                continue
            for g in m["sorts"]:
                spell = self.db.find_spell(g["sort"])
                key = self.grant_key(name, g["sort"]) if g.get("limite") else ""
                usage = g["usage"]
                if key:
                    usage += " — {} / 1 restant".format(self.granted_limit_left(key))
                out.append({"nom": spell["nom"] if spell else g["sort"], "niveau": spell["niveau"] if spell else None,
                            "usage": usage, "source": f"Manifestation : {name}", "sort": spell,
                            "categorie": "Manifestations occultes", "emplacement": bool(g.get("emplacement")),
                            "limite": g.get("limite", ""), "cle": key, "cible": g.get("cible", "")})
        out += self.ritual_book_spells()                 # Livre des secrets anciens : rituels inscrits
        for g in self.ch.sorts_mj:                       # sorts accordés par le MJ (roleplay)
            spell = self.db.find_spell(g["nom"])
            out.append({"nom": spell["nom"] if spell else g["nom"], "niveau": spell["niveau"] if spell else None,
                        "usage": g.get("usage", "À volonté"),
                        "source": "Accordé par le MJ" + (" — " + g["note"] if g.get("note") else ""),
                        "sort": spell, "categorie": "Accordés par le MJ", "mj": True,
                        "emplacement": "emplacement" in norm(g.get("usage", "")), "limite": "", "cle": ""})
        return out

    # ---- armes -----------------------------------------------------------------------
    def unarmed_die(self) -> tuple[int, list[str]]:
        """
        Dé de dégâts des frappes à mains nues (0 = dégâts fixes de 1 + mod.) et sources :
          Moine (Arts martiaux d4 -> d10), Guerrier Pancratiaste (Mains d'acier : d6, d8 au niveau 10),
          style « Combat à mains nues » (d6, d8 si aucune arme ni bouclier en main).
        Le plus grand dé s'applique.
        """
        best, notes = 0, []
        monk = self.class_level("Moine")
        if monk:
            best = self.martial_arts_die(monk)
            notes.append(f"Arts martiaux : d{best}")
        for e in self.ch.classes:
            if e["nom"] == "Guerrier" and "pancratiaste" in norm(self.active_subclass(e)):
                die = 8 if e["niveau"] >= 10 else 6
                notes.append(f"Mains d'acier (Pancratiaste) : d{die}")
                best = max(best, die)
        if self.style_active("Combat à mains nues"):
            notes.append("Combat à mains nues : d6 (d8 si aucune arme ni bouclier)")
            best = max(best, 6)
        return best, notes

    def _best_physical(self) -> str:
        return "Force" if self.mod("Force") >= self.mod("Dextérité") else "Dextérité"

    def weapon_stats(self, slot: dict, offhand: bool = False) -> Optional[dict]:
        """Statistiques d'une arme équipée. `offhand` (v39) : attaque en main secondaire (combat à deux armes) —
        le modificateur de caractéristique n'est PAS ajouté aux dégâts, sauf s'il est négatif ou avec le style
        « Combat à deux armes » ; le style Duel ne s'applique pas."""
        w = self.db.weapons.get(slot.get("nom", ""))
        if not w:
            return None
        props = [norm(p) for p in w.get("proprietes", [])]
        monk = self.class_level("Moine")
        unarmed = w["nom"] == "Mains nues"
        pancrace = unarmed and any(e["nom"] == "Guerrier" and "pancratiaste" in norm(self.active_subclass(e))
                                   for e in self.ch.classes)
        monk_weapon = (bool(monk) or pancrace) and (unarmed or w["nom"] == "Épée courte" or (
            w["categorie"] == "courante" and w["type"] == "cac" and not {"lourde", "deux mains"} & set(props)))
        if "finesse" in props or monk_weapon:
            ab = self._best_physical()
        elif w["type"] == "distance":
            ab = "Dextérité"
        else:
            ab = "Force"
        auto = R.weapon_proficient(w["nom"], w["categorie"], self.weapon_proficiencies()) or unarmed
        prof = auto if slot.get("maitrise") is None else bool(slot["maitrise"])
        magic = int(slot.get("bonus", 0))
        mod = self.mod(ab)
        attack = mod + (self.prof if prof else 0) + magic
        notes: list[str] = []
        if w["type"] == "distance" and self.style_active("Archerie"):
            attack += 2
            notes.append("Archerie : +2 au toucher")
        die = w["degats"]
        if unarmed:
            sides, sources = self.unarmed_die()
            if sides:
                die = f"1d{sides}"
                notes += sources
        twf = self.style_active("Combat à deux armes")
        mod_used = mod if (not offhand or mod < 0 or twf) else 0
        flat = mod_used + magic
        # v46 : détail des modificateurs de dégâts [(source, valeur)]
        terms = [("Mod. {}".format(R.ABBR.get(ab, ab)), mod_used)] if (mod_used or not offhand) else []
        if magic:
            terms.append(("Objet magique : {}".format(slot["affichage"]) if slot.get("affichage")
                          else "Arme magique", magic))
        if offhand:
            notes.append("Main secondaire : modificateur {} aux dégâts{}".format(
                "ajouté (style Combat à deux armes)" if twf and mod > 0 else
                "négatif conservé" if mod < 0 else "non ajouté", ""))
        # arme polyvalente (Épée longue, Bâton, Trident…) : maniée à deux mains si le commutateur est activé
        # et qu'aucun bouclier n'occupe l'autre main
        # v46 : prise AUTOMATIQUE des armes polyvalentes — main secondaire libre (ni bouclier, ni seconde arme)
        # -> à deux mains (dé supérieur) ; main secondaire occupée -> à une main
        versatile_ok = bool(w.get("polyvalent")) and not offhand and self.off_hand_free(slot)
        two_handed_grip = versatile_ok
        if two_handed_grip:
            die = w["polyvalent"]
            notes.append("Maniée à deux mains : {}".format(w["polyvalent"]))
        one_hand = (w["type"] == "cac" and not {"deux mains", "lourde"} & set(props) and not unarmed
                    and not two_handed_grip)
        duel = 2 if one_hand and self.style_active("Duel") and not offhand and not self.dual_wielding() else 0
        if duel:
            flat += duel
            terms.append(("Style de combat : Duel", duel))
            notes.append("Duel : +2 dégâts à une main")
        two_hand = w["type"] == "cac" and bool({"deux mains", "lourde", "polyvalente"} & set(props))
        if two_hand and self.style_active("Armes à deux mains"):
            notes.append("Armes à deux mains : relancez les 1 et 2 aux dés de dégâts")
        if "legere" in props and self.style_active("Combat à deux armes"):
            notes.append("Combat à deux armes : ajoutez le modificateur aux dégâts de la 2e arme")
        if "lancer" in props and self.style_active("Arme de lancer"):
            notes.append("Arme de lancer : +2 dégâts")
        fx_atk = self.attack_mods()                       # effets actifs : bonus, dés, avantage / désavantage
        attack += fx_atk["bonus"]
        for label, val in fx_atk["detail"]:
            notes.append("{} : {} au toucher".format(label, val))
        rage = self.rage_damage_bonus() if (w["type"] == "cac" and ab == "Force") else 0
        if rage:                                          # effet actif « Rage » : bonus aux attaques de Force au CaC
            flat += rage
            terms.append(("Rage", rage))
            notes.append("Rage : +{} dégâts".format(rage))
        ammo = self.selected_ammo(slot) if w["type"] == "distance" else None
        if ammo and ammo["bonus"]:                       # munition magique : bonus au toucher et aux dégâts
            attack += ammo["bonus"]
            flat += ammo["bonus"]
            terms.append(("Munition : {}".format(ammo["nom"]), ammo["bonus"]))
            notes.append("Munition {} : +{} attaque et dégâts".format(ammo["nom"], ammo["bonus"]))
        elif ammo:
            notes.append("Munition : " + ammo["nom"])
        text = R.add_flat(die, flat) if "d" in die else str(max(0, int(die) + flat)) if flat else die
        if unarmed and "d" not in die:
            text = str(max(1, 1 + mod))
        calc = damage_calc(die, terms, text)
        if w.get("polyvalent"):                           # les deux prises : à une main / à deux mains
            duel_one = 2 if (w["type"] == "cac" and self.style_active("Duel") and not offhand
                             and not self.dual_wielding()) else 0
            base = [t for t in terms if not t[0].startswith("Style de combat : Duel")]
            one_terms = base + ([("Style de combat : Duel", duel_one)] if duel_one else [])
            one_txt = R.add_flat(w["degats"], sum(v for _, v in one_terms))
            two_txt = R.add_flat(w["polyvalent"], sum(v for _, v in base))
            calc_1m, calc_2m = damage_calc(w["degats"], one_terms, one_txt), damage_calc(w["polyvalent"], base, two_txt)
        else:
            one_txt, two_txt = text, ""
            calc_1m, calc_2m = calc, ""
        versatile = (one_txt if two_handed_grip else two_txt) if w.get("polyvalent") else ""
        return {"nom": w["nom"], "affichage": slot.get("affichage") or w["nom"], "carac": ab, "maitrise": bool(prof), "auto_maitrise": bool(auto),
                "attaque": attack, "degats": text, "polyvalent": versatile, "type_degats": w["type_degats"],
                "polyvalente": bool(w.get("polyvalent")), "deux_mains": two_handed_grip,
                "deux_mains_possible": versatile_ok, "degats_1m": one_txt, "degats_2m": two_txt,
                "prise": ("à deux mains" if two_handed_grip else "à une main") if w.get("polyvalent") else "",
                "bonus_degats": list(terms), "calcul": calc, "calcul_1m": calc_1m, "calcul_2m": calc_2m,
                "proprietes": w.get("proprietes", []), "portee": w.get("portee", ""), "magique": magic,
                "botte": w.get("botte", "") if self.botte_allowed(w["nom"], bool(prof)) else "",
                "botte_desc": w.get("botte_desc", "") if self.botte_allowed(w["nom"], bool(prof)) else "", "origine": w.get("origine", ""),
                "styles": notes, "munition": ammo, "etat": M.adv_state(fx_atk), "des_attaque": fx_atk["des"],
                "avantage": fx_atk["avantage"], "desavantage": fx_atk["desavantage"]}

    # ==================================================================================
    # Magie
    # ==================================================================================
    @memo
    def casters(self) -> list[dict]:
        """Une entrée par classe (ou sous-classe) capable de lancer des sorts à son niveau actuel."""
        out = []
        for e in self.ch.classes:
            lvl = e["niveau"]
            sub = self.active_subclass(e)
            cfg = R.CASTERS.get(e["nom"]) or R.SUBCLASS_CASTERS.get((e["nom"], sub))
            if not cfg or lvl < E.min_casting_level(cfg["kind"], cfg["min_level"], self.class_edition(e)):
                continue
            ab = cfg["ability"]
            m = self.mod(ab)
            spell_list = cfg.get("spell_list", e["nom"])
            d = {"classe": e["nom"], "niveau": lvl, "carac": ab, "mod": m, "kind": cfg["kind"], "mode": cfg["mode"],
                 "edition": self.class_edition(e), "liste": spell_list, "dc": R.spell_save_dc(self.prof, m), "attaque": R.spell_attack_bonus(self.prof, m),
                 "mineurs_max": R.cantrips_known(e["nom"], lvl, cfg["kind"]), "connus_max": None, "prepares_max": None,
                 "niveau_max": R.max_spell_level(cfg["kind"], lvl)}
            row = self.table_row(e["nom"], lvl)
            if row.get("sorts_prepares") is not None:         # 2024 : sorts préparés et mineurs lus dans la table
                d.update(mode="prepared", connus_max=None, prepares_max=int(row["sorts_prepares"]),
                         mineurs_max=int(row.get("tours_de_magie") or 0))
            elif cfg["mode"] == "known":
                d["connus_max"] = R.spells_known(e["nom"], lvl, cfg["kind"])
            else:
                d["prepares_max"] = R.spells_prepared(e["nom"], lvl, m)
            out.append(d)
        return out

    def caster(self, class_name: str) -> Optional[dict]:
        return next((c for c in self.casters() if c["classe"] == class_name), None)

    @memo
    def spell_slots(self) -> list[int]:
        """Emplacements de sorts ; en multiclassage, chaque classe compte selon son édition (core/editions.py)."""
        return E.spell_slots([(c["kind"], c["niveau"], c.get("edition", E.DEFAULT_EDITION)) for c in self.casters()])

    # ------------------------------------------------------------------ v52 : éditions et règles de la table
    @property
    def db(self):
        """Base de règles ; une fiche 2024 voit les classes et sous-classes 2024 (core/edition_import.EditionView)."""
        base = self._db
        if E.normalize_mode(self.ch.edition_mode) == E.MODE_2024 and hasattr(base, "view_2024"):
            view = base.view_2024()
            if view.classes:
                return view
        return base

    @db.setter
    def db(self, value) -> None:
        self._db = getattr(value, "_base", value)

    @property
    def sheet_edition(self) -> int:
        """Édition des classes de la fiche (une seule par fiche)."""
        return 2024 if getattr(self.db, "edition", 2014) == 2024 else 2014

    def table_row(self, class_name: str, level: int) -> dict:
        """Ligne de la table de progression 2024 d'une classe (vide en 2014)."""
        return self.db.table_row(class_name, level) if self.sheet_edition == 2024 else {}

    def subclass_level(self, class_name: str) -> int:
        """Niveau du choix de sous-classe : 3 pour toutes les classes en 2024."""
        return 3 if self.sheet_edition == 2024 else R.SUBCLASS_LEVEL.get(class_name, 3)

    def martial_arts_die(self, monk_level: int) -> int:
        row = self.table_row("Moine", monk_level)
        m = re.match(r"d(\d+)", str(row.get("arts_martiaux", "")))
        return int(m.group(1)) if m else R.martial_arts_die(monk_level)

    @property
    def edition_mode(self) -> str:
        return E.normalize_mode(self.ch.edition_mode)

    @staticmethod
    def class_edition(entry: dict) -> int:
        return E.item_edition(entry)

    def house_rules(self) -> dict[str, bool]:
        """Règles de la table effectives (choix du personnage, complétés par les défauts du mode)."""
        return HR.resolve(self.ch.regles_optionnelles, self.edition_mode)

    def rule_active(self, key: str) -> bool:
        return self.house_rules().get(key, False)

    def set_edition_mode(self, mode: str) -> list[str]:
        """
        Change l'édition de la fiche ; l'espèce et l'historique passent à leur équivalent de l'autre édition
        quand il existe (« Humain » <-> « Humain (2024) »). Renvoie les incohérences éventuelles des classes.
        """
        self.ch.edition_mode = E.normalize_mode(mode)
        self.normalize()
        for table, attr in ((self.db.races, "race"), (self.db.backgrounds, "historique")):
            current = getattr(self.ch, attr)
            if current in table and self.allowed(table[current]):
                continue
            base = re.sub(r"\s*\(2024\)$", "", current)
            target = next((n for n in (current + " (2024)", base) if n in table and self.allowed(table[n])), "")
            if not target:
                continue
            if attr == "race":
                self.change_race(target)
            else:
                self.ch.historique = target
                self.apply_background()
        self.ch.bonus_libres = [a for a in self.ch.bonus_libres if not self.background_abilities()
                                or a in self.background_abilities()]
        self.normalize()
        return self.edition_problems()

    def set_house_rule(self, key: str, active: bool) -> None:
        if key in HR.BY_KEY:
            self.ch.regles_optionnelles = dict(self.ch.regles_optionnelles or {})
            self.ch.regles_optionnelles[key] = bool(active)

    def edition_problems(self) -> list[str]:
        return E.validate_classes(self.ch.classes, self.edition_mode)

    def background_abilities(self) -> list[str]:
        """2024 : les trois caractéristiques que l'historique propose aux augmentations (+2/+1 ou +1/+1/+1)."""
        if self.sheet_edition != 2024:
            return []
        bg = self.db.backgrounds.get(self.ch.historique) or {}
        return [a for a in bg.get("caracteristiques_2024") or [] if a in ABILITIES]

    def origin_feat(self) -> str:
        """2024 : don d'origine de l'historique (nom du don dans la base), ou ""."""
        if self.sheet_edition != 2024:
            return ""
        text = (self.db.backgrounds.get(self.ch.historique) or {}).get("don_origine", "")
        base = norm(re.split(r"\(", text, maxsplit=1)[0]) if text else ""
        if not base:
            return ""
        for name, f in self.db.feats.items():
            if f.get("edition") == 2024 and norm(re.sub(r"\s*\(2024\)$", "", name)) == base:
                return name
        return ""

    # ---- v52 : bottes d'arme (maîtrise des armes 2024) ----------------------------------------
    MASTERY_FEATURES = ("bottes d'arme", "maitrise des armes")

    def mastery_count(self) -> Optional[int]:
        """
        Nombre de bottes d'arme maîtrisées. Fiche 2024 : table de la classe (Barbare, Guerrier), sinon 2 pour les
        classes qui ont l'aptitude (Paladin, Rôdeur, Roublard) ; 0 sans l'aptitude. Fiche 2014 : None (illimité,
        règle de la table « Maîtrises d'armes sur l'arsenal 2014 ») ou 0 si la règle est inactive.
        """
        if self.sheet_edition != 2024:
            return None if self.rule_active("maitrises_armes_2014") else 0
        best = 0
        for e in self.ch.classes:
            if not any(norm(f["nom"]).startswith(self.MASTERY_FEATURES) and f["debloque"] for f in self.features(e)):
                continue
            best = max(best, int(self.table_row(e["nom"], e["niveau"]).get("maitrise_des_armes") or 2))
        return best

    def mastery_candidates(self) -> list[str]:
        """Armes maîtrisées qui ont une botte (choix proposés)."""
        profs = self.weapon_proficiencies()
        return sorted(n for n, w in self.db.weapons.items()
                      if w.get("botte") and R.weapon_proficient(n, w.get("categorie", ""), profs))

    def mastery_weapons(self) -> Optional[list[str]]:
        """Armes dont la botte s'applique (None = toutes les armes maîtrisées). Sans choix : armes équipées."""
        count = self.mastery_count()
        if count is None:
            return None
        cands = set(self.mastery_candidates())
        chosen = [n for n in self.ch.bottes_choisies if n in cands]
        if not chosen:
            equipped = [s.get("nom", "") for s in list(self.ch.armes_cac) + list(self.ch.armes_distance)]
            chosen = list(dict.fromkeys(n for n in equipped if n in cands))
        return chosen[:count]

    def set_mastery(self, weapon: str, on: bool) -> bool:
        """Coche / décoche une botte (2024 : dans la limite du nombre maîtrisé ; modifiable au repos long)."""
        count = self.mastery_count()
        current = list(self.mastery_weapons() or [])
        if on and weapon not in current:
            if count is not None and len(current) >= count:
                return False
            current.append(weapon)
        elif not on:
            current = [n for n in current if n != weapon]
        self.ch.bottes_choisies = current
        return True

    def botte_allowed(self, weapon_name: str, proficient: bool) -> bool:
        if not proficient:
            return False
        allowed = self.mastery_weapons()
        return allowed is None or weapon_name in allowed

    def allowed(self, item) -> bool:
        """L'élément (sort, don, historique, espèce…) est-il proposé dans le mode d'édition du personnage ?"""
        return E.allowed(item, self.edition_mode)

    def race_options(self) -> list[str]:
        return [n for n in self.db.race_names() if self.allowed(self.db.races[n]) or n == self.ch.race]

    def background_options(self) -> list[str]:
        return [n for n in self.db.background_names()
                if self.allowed(self.db.backgrounds[n]) or n == self.ch.historique]

    def feat_options(self) -> list[str]:
        return [n for n, f in self.db.feats.items() if self.allowed(f)]

    def edition_tips(self, items: dict) -> dict[str, str]:
        """Badge discret (info-bulle) « Édition 2014 / 2024 » des éléments en mode libre."""
        if self.edition_mode != E.MODE_LIBRE:
            return {}
        return {n: "Édition {} — {}".format(E.item_edition(it), it.get("source", "")).rstrip(" —")
                for n, it in items.items()}

    def pact(self) -> tuple[int, int]:
        """(nombre d'emplacements, niveau) de Magie des pactes (0, 0 si aucun occultiste)."""
        lvl = self.class_level("Occultiste")
        return R.pact_slots(lvl) if lvl else (0, 0)

    # niveaux de classe auxquels les sorts de domaine / serment / cercle sont toujours préparés : (paliers, sorts par palier)
    DOMAIN_TIERS = {"Clerc": ([1, 3, 5, 7, 9], 2), "Ensorceleur": ([1, 3, 5, 7, 9], 2),
                    "Paladin": ([3, 5, 9, 13, 17], 2), "Artificier": ([3, 5, 9, 13, 17], 2),
                    "Druide": ([3, 5, 7, 9], 2)}
    # variantes acceptées selon la longueur de la liste (Tasha : Fournaises, Astres ; homebrew à 3 paliers)
    DOMAIN_TIERS_BY_LEN = {("Druide", 10): ([2, 3, 5, 7, 9], 2), ("Druide", 6): ([3, 5, 7], 2),
                           ("Druide", 1): ([2], 1)}

    def domain_spells(self, entry: dict) -> list[str]:
        """
        Sorts toujours préparés accordés par la sous-classe (domaine du Clerc, serment du Paladin...), débloqués
        selon le niveau de classe. Deux formats sont reconnus : listes de 2 sorts par palier, ou paires
        « nom, niveau de sort » (Rôdeur). Les listes de sorts « d'école » ou « étendues » ne sont pas accordées.
        """
        sub = self.db.subclass(entry["nom"], self.active_subclass(entry))
        raw = list((sub or {}).get("sorts_domaine") or [])
        terrain = self.land_terrain(entry)
        if terrain:                                          # Cercle de la Terre : liste du terrain choisi
            raw = list(sub["terrains"][terrain])
        if any(re.fullmatch(r"\d+", x.strip()) for x in raw):
            thresholds = [3, 5, 9, 13, 17]
            pairs = [(raw[i], int(raw[i + 1])) for i in range(0, len(raw) - 1, 2)]
            return [n for n, lv in pairs if entry["niveau"] >= thresholds[max(1, min(lv, 5)) - 1]]
        cantrips = [n for n in raw if (self.db.find_spell(n) or {}).get("niveau") == 0]   # sort mineur offert
        raw = [n for n in raw if n not in cantrips]
        cfg = self.DOMAIN_TIERS_BY_LEN.get((entry["nom"], len(raw))) or self.DOMAIN_TIERS.get(entry["nom"])
        if not cfg or len(raw) != len(cfg[0]) * cfg[1]:
            return []
        tiers, per = cfg
        return cantrips + [n for i, n in enumerate(raw) if entry["niveau"] >= tiers[i // per]]

    def land_terrains(self, entry: dict) -> dict:
        """Terrains proposés par la sous-classe (Cercle de la Terre) : {terrain: [sorts]} ; {} sinon."""
        sub = self.db.subclass(entry["nom"], self.active_subclass(entry))
        return dict((sub or {}).get("terrains") or {})

    def land_terrain(self, entry: dict) -> str:
        """Terrain choisi (champ « terrain » de l'entrée de classe), ou terrain par défaut ; '' si sans objet."""
        terrains = self.land_terrains(entry)
        if not terrains:
            return ""
        chosen = entry.get("terrain", "")
        if chosen in terrains:
            return chosen
        sub = self.db.subclass(entry["nom"], self.active_subclass(entry))
        default = sub.get("terrain_defaut", "")
        return default if default in terrains else next(iter(terrains))

    def set_land_terrain(self, index: int, terrain: str) -> bool:
        entry = self.ch.classes[index]
        if terrain not in self.land_terrains(entry):
            return False
        entry["terrain"] = terrain
        return True

    def available_spells(self, class_name: str, include_all: bool = False) -> list[dict]:
        """
        Bibliothèque de sorts restreinte à ce que le personnage peut légalement apprendre : liste de la classe et
        niveau de sort maximal atteint (table de progression de la classe / sous-classe).
        `include_all` = mode « Ajout manuel par le MJ » : lève les deux restrictions (liste ET niveau).
        """
        c = self.caster(class_name)
        if not c:
            return []
        if include_all:
            return [s for s in self.db.all_spells() if self.allowed(s)]
        pool = self.db.spells_for_class(c["liste"])
        return [s for s in pool if (s["niveau"] == 0 or s["niveau"] <= c["niveau_max"]) and self.allowed(s)]

    def can_learn(self, class_name: str, spell_name: str) -> bool:
        """Sort apprenable sans intervention du MJ : dans la liste de la classe et au plus du niveau maximal."""
        return any(s["nom"] == spell_name for s in self.available_spells(class_name))

    def spell_counts(self, class_name: str) -> dict:
        chosen = self.ch.sorts.get(class_name, [])
        cantrips = [s for s in chosen if (self.db.find_spell(s["nom"]) or {}).get("niveau", 1) == 0]
        leveled = [s for s in chosen if s not in cantrips]
        swap = self.__dict__.get("_level_swaps", {}).get(class_name) or {}
        held = 1 if swap.get("oublie") and not swap.get("nouveau") else 0   # v44 : sort oublié en attente d'échange
        return {"mineurs": len(cantrips), "sorts": len(leveled) + held,
                "prepares": sum(1 for s in leveled if s.get("prepare"))}

    def available_cantrips(self) -> list[str]:
        """Sorts mineurs proposés dans les menus de combat : listes des classes du personnage + sorts mineurs raciaux."""
        lists = {c["liste"] for c in self.casters()}
        names = {s["nom"] for s in self.db.spells.values() if s["niveau"] == 0 and lists & set(s.get("classes", []))}
        names |= {r["nom"] for r in self.racial_spells() if r["niveau"] == 0 and r["debloque"]}
        return sorted(names)

    ELDRITCH_BLAST = "Décharge occulte"

    def cantrip_stats(self, name: str) -> Optional[dict]:
        spell = self.db.find_spell(name)
        if not spell or spell["niveau"] != 0:
            return None
        casters = self.casters()
        caster = next((c for c in casters if c["liste"] in spell.get("classes", [])), None)
        racial = next((r for r in self.racial_spells() if r["nom"] == spell["nom"]), None)
        if caster is None and racial is not None:          # sort mineur racial : caractéristique de la race
            caster = {"attaque": racial["attaque"], "dc": racial["dc"]}
        caster = caster or (casters[0] if casters else None)
        mult = R.cantrip_multiplier(self.total_level)
        dmg = spell.get("degats", "")
        eb = norm(spell["nom"]) == norm(self.ELDRITCH_BLAST)
        blast = self.eldritch_blast_bonus() if eb else {"plat": 0, "portee": "", "notes": [], "effets": []}
        bonus = self.spell_damage_bonus(spell)              # règle du sort / Incantation puissante (une fois)
        flat = sum(v for _, v in bonus)
        extra_lines = []
        if dmg and spell.get("rayons"):                     # Décharge occulte : 1 rayon par palier, 1d10 (+ CHA) chacun
            dmg = f"{mult} × {R.add_flat(dmg, blast['plat'])}"
            if flat:
                dmg += " {:+d}".format(flat)
        elif norm(spell["nom"]) == "lame retentissante":     # Tasha : dégâts au toucher + si la cible se déplace
            dmg = "{}d8".format(mult)
            extra_lines.append("Au toucher : {} tonnerre en plus des dégâts de l'arme ; si la cible se déplace avant "
                               "le début de votre prochain tour : {}d8 tonnerre.".format(
                                   "{}d8".format(mult - 1) if mult > 1 else "aucun dé", mult))
        elif norm(spell["nom"]) == "lame aux flammes vertes":
            m = self.casters()[0]["mod"] if self.casters() else 0
            dmg = R.add_flat("{}d8".format(mult - 1), m) if mult > 1 else str(m)
            extra_lines.append("Au toucher : {} feu en plus des dégâts de l'arme ; seconde créature à 1,50 m : {} feu "
                               "(modificateur d'incantation{}).".format(
                                   "{}d8".format(mult - 1) if mult > 1 else "aucun dé", dmg,
                                   " + dés" if mult > 1 else ""))
        elif dmg:
            if spell.get("echelle", True):
                dmg = R.scale_dice(dmg, mult)
            if flat:
                dmg = R.add_flat(dmg, flat)
        if norm(spell["nom"]) == "glas" and dmg:
            extra_lines.append("{} si la cible a déjà perdu des points de vie.".format(R.scale_dice("1d12", mult)))
        test = spell.get("test", "")
        if test in ("A", "AC"):
            check = f"Attaque {R.fmt_bonus(caster['attaque'])}" if caster else "Attaque de sort"
        elif test == "Arme":
            check = "Attaque d'arme"
        elif test:
            ab = R.ABBR_TO_FULL.get(norm(test)[:3], test)
            check = f"JS {ab} DD {caster['dc']}" if caster else f"JS {ab}"
        else:
            check = "—"
        notes = extra_lines + blast["effets"]
        if blast["plat"] or blast.get("plat_source"):
            notes.insert(0, "{} : {:+d} aux dégâts de chaque rayon.".format(blast["plat_source"], blast["plat"]))
        notes += ["{} : {:+d} aux dégâts.".format(lab, v) for lab, v in bonus]
        return {"nom": spell["nom"], "degats": dmg, "type_degats": spell.get("type_degats", ""), "test": check,
                "portee": blast["portee"] or spell.get("portee", ""), "rayons": mult if spell.get("rayons") else 0,
                "degats_rayon": R.add_flat(spell.get("degats", ""), blast["plat"]) if spell.get("rayons") else "",
                "effets": notes,
                "description": spell.get("description", "") + ("\n" + "\n".join(notes) if notes else "")}

    # ==================================================================================
    # Formules des descriptions (affichage des valeurs du personnage)
    # ==================================================================================
    @memo
    def formula_context(self, class_name: str = ""):
        """Contexte d'évaluation des formules (`core.formulas`) pour une aptitude de `class_name`."""
        from .formulas import FormulaContext
        caster = self.caster(class_name) if class_name else None
        return FormulaContext(mods=self.mods(), prof=self.prof, total_level=self.total_level,
                              levels={e["nom"]: e["niveau"] for e in self.ch.classes},
                              current_class=class_name, spell_mod=caster["mod"] if caster else None)

    # ==================================================================================
    # Sorts raciaux (Races.json)
    # ==================================================================================
    def racial_spell_ability(self) -> tuple[str, bool]:
        """(caractéristique d'incantation des sorts raciaux, au_choix). Au choix : meilleure de Int / Sag / Cha."""
        race = self.db.races.get(self.ch.race) or {}
        fixed = R.RACE_SPELL_ABILITY.get(self.ch.race)
        if "multivers" in norm(race.get("source", "")):     # Monstres du Multivers : Int, Sag ou Cha au choix
            fixed = None
        if fixed:
            return fixed, False
        return max(("Intelligence", "Sagesse", "Charisme"), key=lambda ab: self.mod(ab)), True

    @memo
    def racial_spells(self) -> list[dict]:
        """
        Sorts accordés par la race (noms en *italique* dans Races.json, retrouvés dans la bibliothèque de sorts) :
        [{nom, sort, niveau, niveau_requis, debloque, usage, carac, carac_choix, dc, attaque, source, au_choix}].
        Ils sont disponibles quelle que soit la classe (un Guerrier tieffelin lance Thaumaturgie).
        """
        race = self.db.races.get(self.ch.race)
        if not race:
            return []
        ab, ab_choice = self.racial_spell_ability()
        m = self.mod(ab)
        out, seen = [], set()
        for cap in self.race_capacities():
            desc = cap.get("description", "")
            dn = norm(desc)
            if not (GRANT_TRAIT.search(norm(cap.get("nom", ""))) or dn.startswith(GRANT_START)):
                continue
            if any(x in dn for x in GRANT_EXCLUDE):
                continue
            choice = "au choix" in dn or "selon la saison" in dn or " ou un sort" in dn
            for mt in re.finditer(r"\*([^*]+)\*", desc):
                spell = self.db.find_spell_fuzzy(mt.group(1))
                if not spell or spell["nom"] in seen:
                    continue
                seen.add(spell["nom"])
                clause_start = max(desc.rfind(";", 0, mt.start()), desc.rfind(".", 0, mt.start())) + 1
                before = desc[clause_start:mt.start()]
                after = re.match(r"\s*\(([^)]*)\)", desc[mt.end():])
                paren = after.group(1) if after else ""
                lvl = re.search(r"niv(?:eau|\.)?\s*(\d+)", paren, re.I) or re.search(r"niveau\s*(\d+)\s*:", before, re.I)
                req = int(lvl.group(1)) if lvl else 1
                if spell["niveau"] == 0:
                    usage = "À volonté"
                elif "emplacement" in norm(paren + before):
                    usage = "Avec vos emplacements de sort"
                else:
                    usage = "1 fois / repos long"
                out.append({"nom": spell["nom"], "sort": spell, "niveau": spell["niveau"], "niveau_requis": req,
                            "debloque": self.total_level >= req, "usage": usage, "carac": ab, "carac_choix": ab_choice,
                            "dc": R.spell_save_dc(self.prof, m), "attaque": R.spell_attack_bonus(self.prof, m),
                            "source": cap.get("nom", ""), "au_choix": choice})
        for r in self.chosen_racial_spells():            # v48 : sort mineur racial choisi (Haut-elfe…)
            if r["nom"] not in seen:
                seen.add(r["nom"])
                out.append(r)
        return out

    # ==================================================================================
    # Forme sauvage (Druide) et bestiaire
    # ==================================================================================
    @memo
    def wild_shape(self) -> dict:
        """Règles de Forme sauvage du druide actif : FP max, vol / nage, durée, utilisations, Cercle de la Lune."""
        entry = self.ch.find_class("Druide")
        lvl = entry["niveau"] if entry else 0
        moon = bool(entry) and "lune" in norm(self.active_subclass(entry))
        rules = R.wild_shape_limits(lvl, moon)
        rules.update(niveau=lvl, lune=moon, mouvements=(
            "vol et nage autorisés" if rules["vol"] else "nage autorisée, vol interdit" if rules["nage"]
            else "ni vol ni nage"))
        return rules

    def beast_status(self, name: str) -> tuple[bool, str]:
        """(autorisée, raison) : une bête est autorisée si son FP, son vol et sa nage respectent les règles du druide."""
        beast = self.db.beasts.get(name)
        ws = self.wild_shape()
        if not beast:
            return False, "bête inconnue"
        if not ws["actif"]:
            return False, "Forme sauvage : druide niveau 2 requis"
        if beast["nuee"]:
            return False, "une nuée n'est pas une bête unique"
        if beast["fp"] > ws["fp_max"] + 1e-9:
            return False, "FP {} > FP max {}".format(beast["fp_txt"], R.fmt_cr(ws["fp_max"]))
        if beast["vol"] and not ws["vol"]:
            return False, "vitesse de vol : druide niveau 8 requis"
        if beast["nage"] and not ws["nage"]:
            return False, "vitesse de nage : druide niveau 4 requis"
        return True, ""

    def allowed_beasts(self) -> list[dict]:
        return [b for n, b in self.db.beasts.items() if self.beast_status(n)[0]]

    def assume_form(self, name: str) -> bool:
        """Adopte une forme (dépense une utilisation de Forme sauvage si elle n'est pas illimitée)."""
        ok, _ = self.beast_status(name)
        if not ok:
            return False
        tracker = next((t for t in self.resource_trackers("druide") if t["key"] == "forme"), None)
        if tracker and tracker["total"] is not None:
            used = self.resource_used("forme")
            if used >= tracker["total"]:
                return False
            self.ch.ressources_utilisees["forme"] = used + 1
        self.ch.forme_active = name
        self.ch.forme_type = "sauvage"
        self.ch.forme_pv = self.beast_hp_max(name)       # PV tampon de la bête ; ceux du druide sont mis de côté
        self.add_effect("forme_sauvage")                  # la concentration éventuelle n'est PAS rompue
        return True

    def end_form(self, overflow: int = 0) -> None:
        """Fin de la forme (manuelle, repos, PV de la bête à 0) : les statistiques du druide sont restaurées ;
        les dégâts excédentaires (`overflow`) sont retirés de ses PV normaux."""
        polymorph = self.ch.forme_type == "metamorphose"
        self.ch.forme_active = ""
        self.ch.forme_pv = 0
        self.ch.forme_type = ""
        self.ch.effets_actifs = [k for k in self.ch.effets_actifs if k not in ("forme_sauvage", "metamorphose")]
        if polymorph and norm(self.ch.concentration) == "metamorphose":
            self.break_concentration()                   # fin de la transformation = fin du sort
        if overflow > 0:
            cur = self.ch.pv_actuels if self.ch.pv_actuels >= 0 else self.hp_max()
            self.ch.pv_actuels = max(0, cur - int(overflow))

    # ==================================================================================
    # Ressources de classe à suivre (rage, ki, points de sorcellerie)
    # ==================================================================================
    @memo
    def resource_trackers(self, where: str = "") -> list[dict]:
        """
        Compteurs de ressources dépensables : [{key, label, total, kind, recover, info, where}] (`total` None = illimité).
        where : « combat » (Rage, Ki) ou « magie » (points de sorcellerie). Seules les ressources réellement
        possédées (classe, niveau, don de métamagie) sont retournées.
        """
        out = []
        barb = self.class_level("Barbare")
        if barb:
            bonus = 2 if barb < 9 else 3 if barb < 16 else 4
            out.append({"key": "rage", "label": "Rages", "total": R.rage_uses(barb), "kind": "rage",
                        "recover": "repos long", "info": f"Dégâts de rage : +{bonus} — récupérées au repos long",
                        "where": "combat"})
        monk = self.class_level("Moine")
        if monk >= 2:
            dc = R.spell_save_dc(self.prof, self.mod("Sagesse"))
            out.append({"key": "ki", "label": "Points de ki", "total": R.ki_points(monk), "kind": "ki",
                        "recover": "repos court", "info": f"DD de ki : {dc} — récupérés au repos court ou long",
                        "where": "combat"})
        ws = self.wild_shape()
        if ws["actif"]:
            out.append({"key": "forme", "label": "Formes sauvages", "total": ws["utilisations"], "kind": "forme",
                        "recover": "repos court", "info": "FP max {} — {} — durée {} h — récupérées au repos court"
                        .format(R.fmt_cr(ws["fp_max"]), ws["mouvements"], ws["duree"]), "where": "druide"})
        sorc = self.class_level("Ensorceleur")
        points = sorc if sorc >= 2 else 0
        metamagic_feats = [f for f in self.chosen_feats() if "metamagie" in norm(f)]
        points += 2 * len(metamagic_feats)
        if points:
            src = []
            if sorc >= 2:
                src.append(f"Ensorceleur : {sorc}")
            if metamagic_feats:
                src.append("don : " + ", ".join(metamagic_feats))
            out.append({"key": "sorcellerie", "label": "Points de sorcellerie", "total": points, "kind": "sorcellerie",
                        "recover": "repos long", "info": " ; ".join(src) + " — récupérés au repos long", "where": "magie"})
        out += self.class_action_trackers()          # supériorité, second souffle, sursaut, conduit, inspiration...
        out += self.race_action_trackers()           # capacités de race limitées (Fureur des petits, souffle…)
        if self.sheet_edition == 2024:
            out = self._trackers_2024(out)
        return [t for t in out if not where or t["where"] == where]

    def _trackers_2024(self, out: list[dict]) -> list[dict]:
        """v52 : nombres des compteurs à sphères d'une fiche 2024, lus dans les tables de progression 2024."""
        def cell(cls: str, col: str):
            lvl = self.class_level(cls)
            return self.table_row(cls, lvl).get(col) if lvl else None

        result = []
        for t in out:
            t = dict(t)
            key = t["key"]
            if key in ("sens_divin", "cap:ennemi_jure"):   # 2024 : Sens divin = option de Conduit divin ;
                continue                                  # Ennemi juré = compteur « Marque du chasseur » ci-dessous
            if key == "rage" and cell("Barbare", "rages"):
                t["total"] = int(cell("Barbare", "rages"))
            elif key == "ki":
                t["label"] = "Points de concentration"
                t["info"] = t["info"].replace("DD de ki", "DD de concentration")
                if cell("Moine", "points_de_concentration"):
                    t["total"] = int(cell("Moine", "points_de_concentration"))
            elif key == "forme" and cell("Druide", "formes_sauvages"):
                t["total"] = int(cell("Druide", "formes_sauvages"))
                t["info"] += " — 2024 : 1 utilisation au repos court, toutes au repos long"
            elif key == "second_souffle" and cell("Guerrier", "second_souffle"):
                t["total"] = int(cell("Guerrier", "second_souffle"))
                t["info"] += " — 2024 : 1 utilisation au repos court, toutes au repos long"
            elif key == "conduit":
                n = max(int(cell("Clerc", "conduit_divin") or 0), int(cell("Paladin", "conduit_divin") or 0))
                if n:
                    t["total"] = n
                    t["info"] = "Utilisations de Conduit divin — 1 au repos court, toutes au repos long (2024)"
            elif key == "inspiration" and cell("Barde", "de_d_inspiration"):
                t["de"] = str(cell("Barde", "de_d_inspiration"))
            result.append(t)
        if self.class_level("Paladin") >= 2:              # Châtiment de paladin : 1 lancer gratuit par repos long
            result.append({"key": "chatiment_gratuit", "label": "Châtiment divin gratuit", "total": 1,
                           "kind": "conduit", "recover": "repos long", "where": "combat", "de": "",
                           "info": "Lancer Châtiment divin sans emplacement — repos long"})
        marks = cell("Rôdeur", "ennemi_favori")
        if marks:                                         # 2024 : Marque du chasseur sans emplacement
            result.append({"key": "ennemi_favori", "label": "Ennemi juré (Marque du chasseur)", "total": int(marks),
                           "kind": "conduit", "recover": "repos long", "where": "combat",
                           "info": "Lancer Marque du chasseur sans dépenser d'emplacement — repos long", "de": ""})
        return result

    def resource_used(self, key: str) -> int:
        return int(self.ch.ressources_utilisees.get(key, 0))

    def set_resource_used(self, key: str, used: int) -> None:
        """
        Met à jour un compteur et synchronise la barre d'états : dépenser une rage active l'état « Rage »,
        en récupérer une le retire ; dépenser une Forme sauvage active l'état « Forme sauvage ».
        """
        before = self.resource_used(key)
        self.ch.ressources_utilisees[key] = max(0, int(used))
        effect = {"rage": "rage", "forme": "forme_sauvage"}.get(key)
        if effect and used > before:
            self.add_effect(effect)
        elif effect and used < before and not (key == "forme" and self.ch.forme_active):
            self.remove_effect(effect)
        self.normalize()

    # ==================================================================================
    # Objets magiques et harmonisation
    # ==================================================================================
    @memo
    def attunement_limit(self) -> int:
        """
        Objets harmonisables simultanément : 3 par défaut, davantage si une aptitude débloquée l'indique
        (texte « Harmonisation avec N objets » : Artificier niveaux 10, 14 et 18 dans les JSON de classe).
        """
        best = 3
        for e in self.ch.classes:
            for f in self.features(e):
                if f["debloque"]:
                    m = re.search(r"harmonisation avec (\d+)", norm(f["description"]))
                    if m:
                        best = max(best, int(m.group(1)))
        return best

    def attuned_count(self) -> int:
        return sum(1 for e in self.ch.objets_magiques if e.get("harmonise"))

    def magic_item(self, name: str) -> Optional[dict]:
        """Fiche d'un objet magique : catalogue officiel, sinon objet sur mesure du personnage (v33)."""
        return self.db.magic_items.get(name) or (self.ch.objets_perso or {}).get(name)

    def all_magic_item_names(self) -> list[str]:
        return list(self.db.magic_items) + [n for n in (self.ch.objets_perso or {}) if n not in self.db.magic_items]

    def add_custom_magic_item(self, nom: str, type_: str = "Objet merveilleux", rarete: str = "peu commun",
                              lien: bool = False, description: str = "", poids: float = 0.0, ca: int = 0) -> str:
        """Objet sur mesure : fiche enregistrée avec le personnage puis ajoutée à l'équipement. Renvoie son nom
        (suffixé « (sur mesure) » s'il porte le nom d'un objet officiel), ou « » si le nom est vide."""
        nom = (nom or "").strip()
        if not nom:
            return ""
        if nom in self.db.magic_items:
            nom += " (sur mesure)"
        self.ch.objets_perso[nom] = {
            "id": "perso-" + norm(nom).replace(" ", "-"), "nom": nom, "type": type_ or "Objet merveilleux",
            "precision": "", "rarete": rarete or "peu commun", "lien": bool(lien), "condition": "",
            "description": (description or "").strip() or "Objet sur mesure.", "variable": False,
            "ca_variable": False, "ca": max(0, int(ca or 0)), "js": 0, "source": "Objet sur mesure",
            "poids": max(0.0, float(poids or 0)), "perso": True}
        self.add_magic_item(nom)
        return nom

    def add_magic_item(self, name: str, bonus: int = 0) -> bool:
        """Ajoute un objet du catalogue (avec son bonus choisi pour les objets « +1, +2 ou +3 »)."""
        item = self.magic_item(name)
        if not item:
            return False
        if self.is_ammo_item(item):                     # munitions magiques : rangées dans l'inventaire avec un stock
            entry = next((i for i in self.ch.equipement if i["nom"] == name), None)
            if entry:
                entry["qte"] = int(entry.get("qte", 0)) + 10
            else:
                self.ch.equipement.append({"nom": name, "qte": 10})
            return True
        self.ch.objets_magiques.append({"nom": name, "bonus": max(1, min(3, bonus)) if item["variable"] else 0,
                                        "equipe": True, "harmonise": False})
        return True

    @staticmethod
    def is_ammo_item(item: dict) -> bool:
        n = norm(item.get("nom", "")) + " " + norm(item.get("type", ""))
        return bool(re.search(r"\b(munition|fleche|carreau|bille)", n))

    def remove_magic_item(self, idx: int) -> None:
        if 0 <= idx < len(self.ch.objets_magiques):
            self.release_magic_gear(idx)                 # v45 : la case qui portait l'objet est vidée
            self.ch.objets_magiques.pop(idx)

    def set_attuned(self, idx: int, value: bool) -> bool:
        """(Dés)harmonise l'objet n° idx. Refusé si l'objet n'en a pas besoin ou si le maximum est atteint."""
        if not 0 <= idx < len(self.ch.objets_magiques):
            return False
        entry = self.ch.objets_magiques[idx]
        item = self.magic_item(entry["nom"])
        if not value:
            entry["harmonise"] = False
            return True
        if not item or not item["lien"] or self.attuned_count() >= self.attunement_limit():
            return False
        entry["harmonise"] = True
        return True

    def set_equipped(self, idx: int, value: bool) -> None:
        """Équiper un objet porté (anneau, bottes…) occupe sa case du mannequin et retire l'occupant précédent."""
        if 0 <= idx < len(self.ch.objets_magiques):
            if self.ch.objets_magiques[idx].get("base"):   # v45 : arme / armure magique -> case du mannequin
                if value:
                    self.equip_magic_gear(idx)
                else:
                    self.unequip_magic_gear(idx)
                return
            if value:
                self.equip_magic_item(idx)
            else:
                self.ch.objets_magiques[idx]["equipe"] = False
                self.ch.objets_magiques[idx]["emplacement"] = ""

    def attune_status(self, name: str) -> tuple[str, str]:
        """
        Prérequis d'harmonisation (champ « lien_condition ») : (« ok » | « ko » | « ? », condition).
        Reconnaît classes, lanceur de sorts, races et alignements ; le reste est signalé « ? » (à vérifier à la main).
        """
        item = self.magic_item(name)
        cond_text = (item or {}).get("condition", "")
        cond = norm(cond_text)
        if not cond or self.has_feature("erudit des objets magiques"):      # Artificier niv. 14 : plus aucune contrainte
            return "ok", ""
        ch = self.ch
        al = norm(ch.alignement)
        if "alignement" in cond:
            if "non loyal" in cond:
                align_ok = "loyal" not in al.split()
            elif "neutre bon" in cond:
                align_ok = al == "neutre bon"
            elif "alignement bon" in cond:
                align_ok = al.endswith("bon")
            elif "alignement mauvais" in cond:
                align_ok = al.endswith("mauvais")
            else:
                return "?", cond_text
            races = [r for r in ("demi-elfe", "elfe", "nain") if r in cond]
            race_ok = (not races) or any(norm(ch.race).startswith(r) for r in races)
            return ("ok", "") if (align_ok and race_ok) else ("ko", cond_text)
        if "lanceur de sorts" in cond:
            return ("ok", "") if (self.casters() or self.pact()[0]) else ("ko", cond_text)
        classes = [c for c in self.db.class_names() if norm(c) in cond]
        if classes:
            return ("ok", "") if any(self.class_level(c) for c in classes) else ("ko", cond_text)
        for r in ("nain", "elfe", "halfelin", "gnome", "tieffelin", "drakeide"):
            if r in cond:
                return ("ok", "") if norm(ch.race).startswith(r) else ("ko", cond_text)
        return "?", cond_text

    def active_magic_items(self) -> list[dict]:
        """Objets dont les effets s'appliquent : équipés et, si l'harmonisation est requise, harmonisés."""
        out = []
        for entry in self.ch.objets_magiques:
            item = self.magic_item(entry["nom"])
            if item and entry.get("equipe") and (not item["lien"] or entry.get("harmonise")):
                out.append({"entry": entry, "item": item})
        return out

    @memo
    def magic_item_bonuses(self) -> dict[str, int]:
        """Bonus cumulés des objets actifs : CA (anneau/cape de protection, armure ou bouclier +N...) et jets de sauvegarde."""
        ca = js = 0
        for a in self.active_magic_items():
            item, entry = a["item"], a["entry"]
            if entry.get("base"):                         # v45 : armure / bouclier +X -> bonus porté par la case
                continue
            ca += int(entry.get("bonus", 0)) if item["ca_variable"] else item["ca"]
            js += item["js"]
        if self.has_feature("ame de l'artifice"):                            # Artificier niv. 20 : +1 aux JS par objet harmonisé
            js += self.attuned_count()
        return {"ca": ca, "js": js}

    # ==================================================================================
    # Équipement
    # ==================================================================================
    def add_item(self, name: str, qty: int = 1) -> None:
        """Ajoute un objet à l'inventaire (fusionne avec une ligne existante de même nom)."""
        for it in self.ch.equipement:
            if it["nom"] == name:
                it["qte"] += qty
                return
        self.ch.equipement.append({"nom": name, "qte": max(1, qty)})

    def remove_item(self, idx: int) -> None:
        if 0 <= idx < len(self.ch.equipement):
            self.ch.equipement.pop(idx)

    def add_pack(self, pack_name: str, expand: bool = True) -> int:
        """Ajoute un paquetage : développé en objets individuels (sinon le paquetage seul). Retourne le nombre de lignes."""
        items = self.db.pack_contents(pack_name) if expand else []
        if not items:
            self.add_item(pack_name)
            return 1
        for qty, name, _ in items:
            self.add_item(name, qty)
        return len(items)

    def add_background_gear(self) -> int:
        """Ajoute l'équipement de l'historique (analysé et croisé avec le catalogue) et son or."""
        bg = self.db.backgrounds.get(self.ch.historique)
        if not bg:
            return 0
        items = self.db.parse_item_list(bg.get("inventaire_historique", ""))
        for qty, name, _ in items:
            self.add_item(name, qty)
        self.ch.pieces["po"] = self.ch.pieces.get("po", 0) + int(bg.get("or", 0))
        return len(items)

    def carried_weight(self) -> float:
        total = 0.0
        for it in self.ch.equipement:
            total += self.db.catalog.get(it["nom"], {}).get("poids", 0.0) * it["qte"]
        for e in self.ch.objets_magiques:                 # objets sur mesure : poids saisi par le joueur
            total += float((self.ch.objets_perso or {}).get(e.get("nom", ""), {}).get("poids", 0.0) or 0.0)
        return total

    def carry_multiplier(self) -> int:
        """×2 pour les races dotées de « Puissante carrure » (Goliath, Firbolg, Centaure...)."""
        race = self.db.races.get(self.ch.race, {})
        strong = any(norm(c.get("nom", "")).startswith("puissante carrure") for c in race.get("capacites", []))
        return 2 if strong else 1

    def carry_capacity(self) -> float:
        """Capacité de charge (Manuel des Joueurs) : Force × 7,5 kg (× 2 avec Puissante carrure)."""
        return self.score("Force") * R.KG_CAPACITY * self.carry_multiplier()

    def encumbrance(self) -> dict:
        """
        État de charge : {poids, capacite, seuil_encombre, seuil_lourd, etat, message, sac}.
        etat : « ok », « encombre », « lourd » (règle optionnelle), « surcharge » (au-delà de la capacité)
        ou « sac » (Sac sans fond : limite ignorée).
        """
        force, mult = self.score("Force"), self.carry_multiplier()
        weight, cap = self.carried_weight(), self.carry_capacity()
        enc, heavy = force * R.KG_ENCUMBERED * mult, force * R.KG_HEAVY * mult
        out = {"poids": weight, "capacite": cap, "seuil_encombre": enc, "seuil_lourd": heavy,
               "sac": bool(self.ch.sac_sans_fond)}
        if self.ch.sac_sans_fond:
            out.update(etat="sac", message="Sac sans fond : la limite de charge est ignorée.")
        elif weight > 2 * cap:
            out.update(etat="surcharge", message="Charge impossible : au-delà de 2 × la capacité, vous ne pouvez "
                                                 "plus déplacer ce poids.")
        elif weight > cap:
            out.update(etat="surcharge", message="Surcharge : vitesse réduite à 1,50 m (pousser, tirer ou "
                                                 "soulever seulement).")
        elif weight > heavy:
            out.update(etat="lourd", message="Lourdement encombré (règle optionnelle) : vitesse -6 m, désavantage "
                                             "aux tests et jets d'attaque / de sauvegarde de For, Dex et Con.")
        elif weight > enc:
            out.update(etat="encombre", message="Encombré (règle optionnelle) : vitesse -3 m.")
        else:
            out.update(etat="ok", message="Charge normale.")
        return out

    # ==================================================================================
    # Avertissements (règles non bloquantes)
    # ==================================================================================
    def warnings(self) -> list[str]:
        out: list[str] = []
        ch = self.ch
        if len(ch.classes) > 1:
            for e in ch.classes:
                reqs, how = R.MULTICLASS_PREREQ.get(e["nom"], ([], "et"))
                ok = [self.score(ab) >= mn for ab, mn in reqs]
                if reqs and not (any(ok) if how == "ou" else all(ok)):
                    need = (" ou " if how == "ou" else " et ").join(f"{ab} {mn}" for ab, mn in reqs)
                    out.append(f"Multiclassage : {e['nom']} demande {need}.")
        if ch.methode == "achat":
            ok, msg = R.point_buy_valid(ch.scores_achat)
            if not ok:
                out.append(msg)
        # oublis (valeurs non assignées, bonus libres, styles à choisir…) : voir missing_choices()
        rule = self.race_rule()
        if rule["libres"]:
            picks = [p for p in ch.bonus_libres[:len(rule["libres"])] if p]
            if len(set(picks)) < len(picks):
                out.append("Les bonus raciaux libres doivent viser des caractéristiques différentes.")
        st = self.class_skill_status()
        if len(st["choisies"]) > st["nombre"] and ch.classes:
            out.append(f"Compétences de classe : {len(st['choisies'])} cochées pour {st['nombre']} autorisées.")
        for c in self.casters():
            cnt = self.spell_counts(c["classe"])
            if cnt["mineurs"] > c["mineurs_max"]:
                out.append(f"{c['classe']} : {cnt['mineurs']} sorts mineurs pour {c['mineurs_max']} autorisés.")
            if c["connus_max"] is not None and cnt["sorts"] > c["connus_max"]:
                out.append(f"{c['classe']} : {cnt['sorts']} sorts connus pour {c['connus_max']} autorisés.")
            if c["prepares_max"] is not None and cnt["prepares"] > c["prepares_max"]:
                out.append(f"{c['classe']} : {cnt['prepares']} sorts préparés pour {c['prepares_max']} autorisés.")
        if self.attuned_count() > self.attunement_limit():
            out.append(f"Harmonisation : {self.attuned_count()} objets pour {self.attunement_limit()} autorisés.")
        for entry in ch.objets_magiques:
            if entry.get("harmonise"):
                state, cond = self.attune_status(entry["nom"])
                if state == "ko":
                    out.append(f"Objet « {entry['nom']} » : harmonisation réservée à {cond}.")
        slots_m = self.manifestation_slots()
        if len(ch.manifestations) > slots_m["total"]:
            out.append(f"Manifestations occultes : {len(ch.manifestations)} choisies pour {slots_m['total']} autorisées.")
        for name in ch.manifestations:
            state, why = self.manifestation_status(name)
            if state == "ko":
                out.append(f"Manifestation « {name} » : {why}.")
        for feat in self.chosen_feats():
            state, msg = self.feat_status(feat)
            if state == "ko":
                out.append(f"Don « {feat} » : prérequis non rempli ({msg}).")
        enc = self.encumbrance()
        if enc["etat"] == "surcharge":
            out.append("Surcharge : {} kg portés pour {} kg de capacité.".format(
                R.fmt_meters(round(enc["poids"], 2)), R.fmt_meters(enc["capacite"])))
        out += self.armor_warnings()
        out += self.equipment_warnings()                 # v31 : plus d'objets que de cases (3 anneaux…)
        for c in self.casters():                         # v36 : écoles imposées (Chevalier occulte, Arnaqueur)
            r = self.school_restriction(c["classe"])
            if r and r["libres_utilises"] > r["libres_max"]:
                out.append("{} : {} sort(s) hors {} pour {} sort(s) libre(s) autorisé(s).".format(
                    r["sous_classe"], r["libres_utilises"], " / ".join(r["ecoles"]), r["libres_max"]))
        if self.languages_excess():                      # v36 : quota de langues dépassé
            out.append("Langues : {} connues pour {} accordées (espèce, historique, dons).".format(
                self.languages_known(), self.languages_allowed()))
        return out

    # ==================================================================================
    # Repos
    # ==================================================================================
    def short_rest(self) -> None:
        """Repos court : emplacements de Pacte et points de ki récupérés ; Restauration de sorcellerie (niv. 20) : 4 points."""
        self.ch.pacte_utilises = 0
        for key in SHORT_REST_KEYS:                      # ki, formes, supériorité, second souffle, sursaut, conduit
            self.ch.ressources_utilisees.pop(key, None)
        for key in self.subclass_short_rest_keys():      # runes, Tir arcanique, utilisations gratuites psi
            self.ch.ressources_utilisees.pop(key, None)
        for key in self.invocation_short_rest_keys():    # Tombe de Levistus, Voile de mouches, Regard fantomatique
            self.ch.ressources_utilisees.pop(key, None)
        for key in self.class_tile_short_rest_keys():    # v39 : aptitudes de classe rechargées au repos court
            self.ch.ressources_utilisees.pop(key, None)
        for tr in self.race_action_trackers():           # capacités de race rechargées au repos court
            if tr["recover"] == "repos court":
                self.ch.ressources_utilisees.pop(tr["key"], None)
        if self.class_level("Barde") >= 5:               # Source d'inspiration : inspiration au repos court
            self.ch.ressources_utilisees.pop("inspiration", None)
        if self.class_level("Ensorceleur") >= 20:
            self.ch.ressources_utilisees["sorcellerie"] = max(0, self.ch.ressources_utilisees.get("sorcellerie", 0) - 4)

    def long_rest(self) -> None:
        ch = self.ch
        ch.pv_actuels = self.hp_max()
        ch.pv_temporaires = 0
        ch.emplacements_utilises = [0] * 9
        ch.pacte_utilises = 0
        ch.ressources_utilisees = {}                       # rages, ki, points de sorcellerie : tout est récupéré
        ch.mort_reussites = ch.mort_echecs = 0
        self.recharge_magic_items()                        # v45 : charges des objets magiques (« à l'aube »)
        for die, total in self.hit_dice().items():
            ch.des_vie_utilises[die] = max(0, ch.des_vie_utilises.get(die, 0) - max(1, total // 2))

    # ==================================================================================
    # Résumé texte (tests / débogage)
    # ==================================================================================
    def summary(self) -> str:
        ch = self.ch
        classes = " / ".join("{} {}".format(c["nom"], c["niveau"]) for c in ch.classes)
        scores = ", ".join("{} {} ({})".format(R.ABBR[a], self.score(a), R.fmt_bonus(self.mod(a))) for a in ABILITIES)
        lines = ["{} — {} — niveau {} ({})".format(ch.nom or "Sans nom", ch.race, self.total_level, classes),
                 "Carac : " + scores,
                 "PV {}  CA {}  Init {}  Vit {} m  Maîtrise {}".format(
                     self.hp_max(), self.armor_class()[0], R.fmt_bonus(self.initiative()), self.speed(),
                     R.fmt_bonus(self.prof))]
        return "\n".join(lines)
