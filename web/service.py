"""
Façade web du moteur D&D 5e — AUCUNE règle de jeu ici.

Le serveur est « sans état » : le navigateur garde le personnage (format JSON identique à la sauvegarde de
l'application bureau) et l'envoie à chaque action. Pour chaque requête on :
  1. reconstruit `Character.from_dict(...)` puis `Engine(db, ch)` (code d'origine, inchangé) ;
  2. applique une liste d'opérations — chacune est l'équivalent exact d'un gestionnaire de l'interface PyQt6
     (ui/*.py) et appelle les mêmes méthodes du moteur ;
  3. normalise, puis renvoie le personnage + une « fiche » calculée (valeurs dérivées prêtes à afficher).

Ce module remplace donc seulement la couche ui/ : core/ et data/ sont utilisés tels quels.
"""
from __future__ import annotations

import random
import threading
from typing import Any, Callable

from core import companions as C
from core import dice as D
from core import effects as FX
from core import rules as R
from core.character import Character
from core.data_loader import Database
from core.engine import Engine
from core.paths import get_resource_path
from core.rules import ABILITIES, norm

# ---------------------------------------------------------------------------------------------------------------
# Base de données : chargée une seule fois par processus (lecture seule, partagée entre les requêtes)
# ---------------------------------------------------------------------------------------------------------------
_DB: Database | None = None
_DB_LOCK = threading.Lock()


def get_db() -> Database:
    global _DB
    if _DB is None:
        with _DB_LOCK:
            if _DB is None:
                _DB = Database(get_resource_path("data"))
    return _DB


class ActionError(ValueError):
    """Action refusée : le message est affiché tel quel à l'utilisateur."""


# Champs du personnage modifiables directement (équivalent des champs texte / cases de l'interface bureau)
SIMPLE_FIELDS: dict[str, type] = {
    "nom": str, "joueur": str, "alignement": str, "experience": int, "histoire": str, "traits": str,
    "notes": str, "inventaire": str, "langues": str, "pv_temporaires": int, "pv_actuels": int,
    "mort_reussites": int, "mort_echecs": int, "methode": str, "sac_sans_fond": bool, "pv_divers": int,
}
DICT_FIELDS = {"scores_manuel": int, "bonus_divers": int, "pieces": int}
LONG_TEXT = 20000


def _int(value: Any, lo: int = -10**6, hi: int = 10**6) -> int:
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        raise ActionError("Valeur numérique attendue.")


# ---------------------------------------------------------------------------------------------------------------
# Opérations (une par gestionnaire de l'interface bureau)
# ---------------------------------------------------------------------------------------------------------------
class Controller:
    def __init__(self, eng: Engine):
        self.eng, self.ch, self.db = eng, eng.ch, eng.db
        self.messages: list[str] = []
        self.rolls: list[dict] = []

    def msg(self, text: str) -> None:
        if text:
            self.messages.append(text)

    # ---------- champs simples
    def op_set(self, field: str, value: Any) -> None:
        kind = SIMPLE_FIELDS.get(field)
        if kind is None:
            raise ActionError(f"Champ non modifiable : {field}")
        if kind is int:
            value = _int(value)
        elif kind is bool:
            value = bool(value)
        else:
            value = str(value or "")[:LONG_TEXT]
        if field == "methode" and value not in ("achat", "des", "manuel"):
            raise ActionError("Méthode inconnue.")
        if field == "alignement" and value not in R.ALIGNMENTS:
            raise ActionError("Alignement inconnu.")
        if field in ("mort_reussites", "mort_echecs"):
            value = max(0, min(3, value))
        if field == "pv_temporaires":
            value = max(0, value)
        if field == "pv_actuels":
            value = max(0, min(self.eng.hp_max(), value))
        setattr(self.ch, field, value)

    def op_setin(self, field: str, key: str, value: Any) -> None:
        if field not in DICT_FIELDS:
            raise ActionError(f"Champ non modifiable : {field}")
        target = getattr(self.ch, field)
        if field == "pieces":
            if key not in ("pc", "pa", "pe", "po", "pp"):
                raise ActionError("Pièce inconnue.")
            target[key] = _int(value, 0, 10**7)
        else:
            if key not in ABILITIES:
                raise ActionError("Caractéristique inconnue.")
            target[key] = _int(value, 1, 30) if field == "scores_manuel" else _int(value, -10, 10)

    # ---------- espèce / historique (ui/race_tab.py)
    def op_race(self, name: str) -> None:
        if name not in self.db.races:
            raise ActionError("Espèce inconnue.")
        if name != self.ch.race:
            removed = self.eng.change_race(name)
            if removed.get("langues") or removed.get("competences"):
                self.msg("Acquis de l'ancienne espèce retirés — langues : {} ; compétences : {}.".format(
                    ", ".join(removed["langues"]) or "aucune", ", ".join(removed["competences"]) or "aucune"))

    def op_subrace(self, name: str) -> None:
        if name and name not in [s["nom"] for s in self.db.subraces_of(self.ch.race)]:
            raise ActionError("Sous-espèce inconnue.")
        if name != self.ch.sous_race:
            self.ch.sous_race = name
            self.eng.apply_race_languages()
            self.eng.apply_race_skills()

    def op_background(self, name: str) -> None:
        if name not in self.db.backgrounds:
            raise ActionError("Historique inconnu.")
        self.ch.historique = name
        self.eng.apply_background()

    def op_background_gear(self) -> None:
        n = self.eng.add_background_gear()
        self.msg(f"Équipement d'historique ajouté ({n} ligne(s)).")

    def op_toggle_language(self, name: str) -> None:
        if name not in self.db.language_names():
            raise ActionError("Langue inconnue.")
        langs = [x for x in self.ch.langues_liste if x != name]
        if name not in self.ch.langues_liste:
            langs.append(name)
        self.ch.langues_liste = [n for n in self.db.language_names() if n in langs]

    # ---------- classes (ui/classes_tab.py)
    def op_class_change(self, idx: int, name: str) -> None:
        if name not in self.db.classes:
            raise ActionError("Classe inconnue.")
        if not self.eng.change_class(_int(idx), name):
            raise ActionError("Changement de classe impossible.")

    def op_class_level(self, idx: int, level: int) -> None:
        idx = _int(idx)
        if not 0 <= idx < len(self.ch.classes):
            raise ActionError("Classe introuvable.")
        self.eng.set_class_level(idx, _int(level, 1, R.MAX_LEVEL))

    def op_class_sub(self, idx: int, name: str) -> None:
        idx = _int(idx)
        if not 0 <= idx < len(self.ch.classes):
            raise ActionError("Classe introuvable.")
        entry = self.ch.classes[idx]
        if name and not self.db.subclass(entry["nom"], name):
            raise ActionError("Sous-classe inconnue.")
        entry["sous_classe"] = name

    def op_class_add(self, name: str) -> None:
        if name not in self.db.classes:
            raise ActionError("Classe inconnue.")
        if not self.ch.multiclassage:
            self.eng.set_multiclass(True)
        if not self.eng.add_class(name):
            raise ActionError("Impossible d'ajouter cette classe (déjà présente ou niveau 20 atteint).")

    def op_class_remove(self, idx: int) -> None:
        if not self.eng.remove_class(_int(idx)):
            raise ActionError("Impossible de retirer la dernière classe.")

    def op_multiclass(self, enabled: bool) -> None:
        for text in self.eng.set_multiclass(bool(enabled)) or []:
            self.msg(text)

    # ---------- caractéristiques (ui/abilities_tab.py)
    def op_buy(self, ability: str, delta: int) -> None:
        if ability not in ABILITIES:
            raise ActionError("Caractéristique inconnue.")
        if not self.eng.buy_step(ability, 1 if _int(delta) > 0 else -1):
            self.msg("Achat impossible (valeurs 8 à 15, budget de 27 points).")

    def op_reset_scores(self) -> None:
        self.eng.reset_scores()

    def _priority(self) -> list[str]:
        main = self.db.classes.get(self.eng.first_class(), {}).get("carac_principale", "")
        order = [ab for ab in ABILITIES if norm(ab) in norm(main)]
        for ab in ("Constitution", "Dextérité", "Sagesse", "Charisme", "Intelligence", "Force"):
            if ab not in order:
                order.append(ab)
        return order

    def op_roll_scores(self) -> None:
        rolls = R.roll_ability_set()
        self.ch.des_tirages = [{"total": t, "des": d} for t, d in rolls]
        self.ch.methode = "des"
        self.op_auto_assign()

    def op_auto_assign(self) -> None:
        if not self.ch.des_tirages:
            return
        ranked = sorted(range(len(self.ch.des_tirages)), key=lambda i: -self.ch.des_tirages[i]["total"])
        self.ch.des_affectation = {ab: ranked[k] for k, ab in enumerate(self._priority())}

    def op_assign_roll(self, ability: str, index: int) -> None:
        if ability not in ABILITIES:
            raise ActionError("Caractéristique inconnue.")
        idx = _int(index, -1, len(self.ch.des_tirages) - 1)
        for other, v in list(self.ch.des_affectation.items()):
            if other != ability and idx >= 0 and v == idx:
                self.ch.des_affectation[other] = self.ch.des_affectation.get(ability, -1)   # échange
        self.ch.des_affectation[ability] = idx

    def op_free_rule(self, enabled: bool) -> None:
        self.ch.regle_libre, self.ch.bonus_libres = bool(enabled), []

    def op_alt_rule(self, enabled: bool) -> None:
        self.ch.bonus_alt, self.ch.bonus_libres = bool(enabled), []

    def op_free_pick(self, k: int, ability: str) -> None:
        picks = list(self.ch.bonus_libres) + [""] * 3
        picks[_int(k, 0, 2)] = ability if ability in ABILITIES else ""
        self.ch.bonus_libres = picks[:3]

    # ---------- améliorations & dons (ui/progression_tab.py)
    def op_asi(self, slot: str, mode: str, a1: str = "Force", a2: str = "Dextérité", don: str = "",
               don_carac: str = "") -> None:
        if slot not in {s["id"] for s in self.eng.asi_slots()}:
            raise ActionError("Emplacement d'amélioration inconnu.")
        if mode not in ("aucun", "plus2", "plus1x2", "don"):
            raise ActionError("Choix inconnu.")
        if don and don not in self.db.feats:
            raise ActionError("Don inconnu.")
        self.ch.ameliorations[slot] = {"mode": mode, "a1": a1, "a2": a2, "don": don, "don_carac": don_carac}

    def op_gm_feat_add(self, name: str) -> None:
        if name not in self.db.feats:
            raise ActionError("Don inconnu.")
        if not self.eng.add_gm_feat(name):
            self.msg(f"« {name} » est déjà accordé par le MJ.")

    def op_gm_feat_remove(self, name: str) -> None:
        self.eng.remove_gm_feat(name)

    # ---------- compétences & sauvegardes (ui/skills_tab.py)
    def op_toggle_skill(self, name: str, kind: str = "maitrise") -> None:
        if name not in self.db.skill_names:
            raise ActionError("Compétence inconnue.")
        st = self.ch.competences.setdefault(name, {"maitrise": False, "expertise": False})
        if kind == "expertise":
            if not st.get("maitrise"):
                raise ActionError("L'expertise exige la maîtrise.")
            st["expertise"] = not st.get("expertise")
        else:
            st["maitrise"] = not st.get("maitrise")
            if not st["maitrise"]:
                st["expertise"] = False

    def op_toggle_save(self, ability: str) -> None:
        if ability not in ABILITIES:
            raise ActionError("Caractéristique inconnue.")
        if ability in self.eng.resilient_saves():
            raise ActionError("Maîtrise imposée par un don : non modifiable.")
        self.ch.sauvegardes[ability] = not self.ch.sauvegardes.get(ability, False)

    # ---------- combat (ui/combat_tab.py)
    def op_armor(self, nom: str, bonus: int = 0, bouclier: str = "") -> None:
        if nom not in self.db.armors:
            raise ActionError("Armure inconnue.")
        if bouclier and bouclier not in self.db.shields:
            raise ActionError("Bouclier inconnu.")
        a = self.ch.armure
        a["nom"], a["bonus"] = nom, _int(bonus, 0, 3)
        a["bouclier"], a["bouclier_nom"] = bool(bouclier), bouclier
        added = [n for n in (nom if nom != "Aucune armure" else "", bouclier) if n and self.eng.ensure_in_inventory(n)]
        if added:
            self.msg("Ajouté à l'inventaire : {}.".format(", ".join(added)))

    def op_weapon(self, key: str, i: int, nom: str = "", bonus: int = 0) -> None:
        if key not in ("armes_cac", "armes_distance"):
            raise ActionError("Emplacement d'arme inconnu.")
        slots = getattr(self.ch, key)
        i = _int(i)
        if not 0 <= i < len(slots):
            raise ActionError("Emplacement d'arme inconnu.")
        if nom and nom not in self.db.weapons:
            raise ActionError("Arme inconnue.")
        slot = slots[i]
        changed = slot.get("nom", "") != nom
        slot["nom"], slot["bonus"] = nom, _int(bonus, 0, 3)
        if changed:
            slot["maitrise"] = None                       # retour à la détection automatique
            if nom and self.eng.ensure_in_inventory(nom):
                self.msg(f"{nom} ajouté(e) à l'inventaire.")

    def op_style(self, slot: str, name: str = "") -> None:
        """Style de combat / modèle d'armure (ui/combat_tab.py)."""
        slots = {sl["id"]: sl for sl in self.eng.fighting_style_slots()}
        if slot not in slots:
            raise ActionError("Emplacement de style inconnu.")
        if not name:
            self.ch.styles_combat.pop(slot, None)
            return
        if name not in self.eng.style_options(slot):
            raise ActionError("Style non disponible pour cet emplacement.")
        self.ch.styles_combat[slot] = name

    def op_damage(self, amount: int) -> None:
        amount = _int(amount, 0, 10000)
        if self.ch.forme_active:
            self.msg(self.eng.damage_form(amount))
            return
        ch = self.ch
        absorbed = min(ch.pv_temporaires, amount)
        ch.pv_temporaires -= absorbed
        ch.pv_actuels = max(0, (ch.pv_actuels if ch.pv_actuels >= 0 else self.eng.hp_max()) - (amount - absorbed))
        text = f"{amount} dégât(s) subi(s)" + (f" dont {absorbed} absorbé(s) par les PV temporaires" if absorbed else "")
        if ch.concentration and amount > 0:
            text += f". JS de Constitution DD {max(10, amount // 2)} pour maintenir {ch.concentration}"
        if ch.pv_actuels == 0:
            if "inconscient" in FX.EFFECTS:
                self.eng.add_effect("inconscient")
            text += ". Vous tombez à 0 PV : jets contre la mort"
        self.msg(text + ".")

    def op_heal(self, amount: int) -> None:
        amount = _int(amount, 0, 10000)
        if self.ch.forme_active:
            self.eng.heal_form(amount)
            return
        gained = self.eng.heal(amount)
        if gained and self.ch.pv_actuels > 0:
            self.ch.mort_reussites = self.ch.mort_echecs = 0
            if "inconscient" in self.ch.effets_actifs:
                self.eng.remove_effect("inconscient")
        self.msg(f"{gained} PV récupéré(s).")

    def op_hit_die(self, die: str) -> None:
        res = self.eng.spend_hit_die(die)
        if not res:
            raise ActionError("Plus de dé de vie de ce type.")
        self.rolls.append({"titre": f"Dé de vie {die}", "total": res["jet"] + res["con"], "des": [res["jet"]],
                           "detail": f"{res['jet']} + {res['con']} (Con)"})
        self.msg(f"Dé de vie {die} : {res['jet']} {res['con']:+d} → {res['gain']} PV récupéré(s).")

    def op_short_rest(self) -> None:
        self.eng.short_rest()
        self.msg("Repos court terminé : emplacements de Pacte et ressources « repos court » récupérés.")

    def op_long_rest(self) -> None:
        self.eng.long_rest()
        self.msg("Repos long terminé : PV, emplacements et ressources récupérés.")

    def op_resource(self, key: str, used: int) -> None:
        if key not in {t["key"] for t in self.eng.resource_trackers()} | {"souffle"}:
            raise ActionError("Ressource inconnue.")
        self.eng.set_resource_used(key, _int(used, 0, 999))

    def op_effect_add(self, key: str) -> None:
        if key not in FX.EFFECTS:
            raise ActionError("Effet inconnu.")
        self.eng.add_effect(key)

    def op_effect_remove(self, key: str) -> None:
        self.eng.remove_effect(key)

    # ---------- magie (ui/magic_tab.py)
    def op_slot_used(self, level: int, used: int) -> None:
        level = _int(level, 1, 9)
        self.ch.emplacements_utilises[level - 1] = _int(used, 0, 9)

    def op_pact_used(self, used: int) -> None:
        self.ch.pacte_utilises = _int(used, 0, 9)

    def _caster_class(self, cls: str) -> str:
        if not self.eng.caster(cls):
            raise ActionError("Cette classe ne lance pas de sorts.")
        return cls

    def op_spell_add(self, cls: str, nom: str, force: bool = False) -> None:
        cls = self._caster_class(cls)
        sp = self.db.find_spell(nom)
        if not sp:
            raise ActionError("Sort inconnu.")
        lst = self.ch.sorts.setdefault(cls, [])
        if any(s["nom"] == sp["nom"] for s in lst):
            return
        if not force and not self.eng.can_learn(cls, sp["nom"]):
            raise ActionError(f"« {sp['nom']} » n'est pas apprenable à votre niveau (activez le mode MJ).")
        ok, why = self.eng.school_check(cls, sp)
        if not ok and not force:
            raise ActionError(f"« {sp['nom']} » ({sp.get('ecole', '')}) : {why}")
        lst.append({"nom": sp["nom"], "prepare": True})
        self.msg(f"« {sp['nom']} » ajouté." + (f" ({why})" if why else ""))

    def op_spell_remove(self, cls: str, nom: str) -> None:
        lst = self.ch.sorts.get(cls, [])
        entry = next((s for s in lst if s["nom"] == nom), None)
        if entry and entry.get("accorde"):
            raise ActionError(f"« {nom} » est accordé par votre sous-classe : il ne peut pas être retiré.")
        self.ch.sorts[cls] = [s for s in lst if s["nom"] != nom]

    def op_spell_prepare(self, cls: str, nom: str) -> None:
        for sp in self.ch.sorts.get(cls, []):
            if sp["nom"] == nom:
                sp["prepare"] = not sp.get("prepare", True)

    def op_cast(self, nom: str, use_slot: bool = True, slot_level: int = 0, target: str = "soi",
                effect: str = "", beast: str = "") -> None:
        sp = self.db.find_spell(nom)
        if not sp:
            raise ActionError("Sort inconnu.")
        if norm(sp["nom"]) == "metamorphose" and beast:      # Métamorphose sur soi : choix de la bête
            res = self.eng.cast_polymorph(beast, bool(use_slot))
            if not res["ok"]:
                raise ActionError(res["message"])
            self.msg(res["message"])
            return
        buffs = self.eng.buff_options(sp["nom"])
        if buffs and effect not in buffs:
            effect = buffs[0]
        if self.eng.spell_is_personal(sp["nom"]):
            target = "soi"
        if target not in ("soi", "allie"):
            target = "soi"
        res = self.eng.cast_spell(sp["nom"], bool(use_slot), target if buffs or sp.get("concentration") else "",
                                  effect if buffs else "", _int(slot_level, 0, 9))
        if not res["ok"]:
            raise ActionError(res["message"])
        self.msg(res["message"])

    def op_break_concentration(self) -> None:
        old = self.eng.break_concentration()
        self.msg(f"Concentration sur « {old} » rompue." if old else "Aucune concentration en cours.")

    # ---------- options de classe & d'espèce (ui/combat_tab.py, ui/manifestations_panel.py)
    def op_ancestry(self, kind: str, color: str = "") -> None:
        from core.engine_extras import DRACONIC
        if color and color not in DRACONIC:
            raise ActionError("Couleur inconnue.")
        if kind == "race":
            self.ch.ascendance_raciale = color
        elif kind == "sorc":
            self.ch.ascendance_ensorceleur = color
        else:
            raise ActionError("Ascendance inconnue.")

    def op_class_option(self, key: str, index: int, name: str = "") -> None:
        sets = {st["key"]: st for st in self.eng.option_sets()}
        if key not in sets:
            raise ActionError("Option de classe inconnue.")
        if name and name not in sets[key]["options"]:
            raise ActionError("Choix non disponible.")
        if name and name in sets[key]["chosen"]:
            raise ActionError("Déjà choisi.")
        self.eng.set_class_option(key, _int(index, 0, 30), name)

    def op_maneuver(self, name: str = "") -> None:
        if name and name not in self.db.maneuvers:
            raise ActionError("Manœuvre inconnue.")
        self.ch.technique_manoeuvre = name

    def op_pact(self, name: str = "") -> None:
        from core.data_loader import PACTS
        if name and name not in PACTS:
            raise ActionError("Pacte inconnu.")
        self.ch.pacte = name

    def op_manifestation_add(self, name: str) -> None:
        eng = self.eng
        if name not in self.db.manifestations or name in self.ch.manifestations:
            raise ActionError("Manifestation inconnue ou déjà choisie.")
        if len(self.ch.manifestations) >= eng.manifestation_slots()["total"]:
            raise ActionError("Toutes vos manifestations sont déjà choisies.")
        state, why = eng.manifestation_status(name)
        if state != "ok":
            raise ActionError(f"Prérequis non rempli : {why}.")
        self.ch.manifestations.append(name)

    def op_manifestation_remove(self, name: str) -> None:
        self.ch.manifestations = [m for m in self.ch.manifestations if m != name]

    def op_ritual_add(self, name: str) -> None:
        ok, why = self.eng.ritual_book_can_add(name)
        if not ok:
            raise ActionError(why)
        self.eng.add_ritual(name)

    def op_ritual_remove(self, name: str) -> None:
        self.eng.remove_ritual(name)

    # ---------- suivi du tour & actions de classe (ui/combat_tab.py : pied de tour, tuiles)
    def op_turn_toggle(self, kind: str) -> None:
        if kind not in ("Action", "Action bonus", "Réaction"):
            raise ActionError("Économie d'action inconnue.")
        self.eng.toggle_economy(kind)

    def op_turn_move(self, meters: float) -> None:
        try:
            self.eng.set_movement(max(0.0, min(1000.0, float(meters))))
        except (TypeError, ValueError):
            raise ActionError("Distance invalide.")

    def op_turn_new(self) -> None:
        self.eng.new_turn()
        self.msg("Nouveau tour : action, action bonus, réaction et déplacement disponibles.")

    def _refund(self, tile: str) -> None:
        kind = next((t["type"] for t in self.eng.turn_actions() if t["id"] == tile), "Action")
        if kind == "Action bonus":
            self.ch.tour_bonus = False
        elif kind == "Réaction":
            self.ch.reaction_utilisee = ""
        else:
            self.ch.tour_action = False

    def _roll_attack(self, spec, dmg, heal: bool = False) -> None:
        crit = False
        if spec is not None:
            r = D.roll_d20(spec)
            dice = " / ".join(str(x) for x in r.d20s)
            parts = ["d20 : {}{}".format(dice, " ({})".format(spec.mode) if spec.mode else "")]
            parts += ["{:+d} ({})".format(v, t.label) if not t.dice else "{} → {:+d} ({})".format(t.dice, v, t.label)
                      for t, v in zip(spec.terms, r.term_values)]
            crit = r.critical == "succes"
            self.rolls.append({"titre": spec.title, "total": r.total, "detail": " · ".join(parts),
                               "notes": spec.mode_lines() + ([spec.note] if spec.note else []),
                               "crit": crit, "fail": r.critical == "echec" or r.auto_fail})
        if dmg is not None:
            formula = D.critical_formula(dmg.formula) if crit else dmg.formula
            res = D.roll_damage(D.DamageSpec(dmg.title, formula, dmg.damage_type, dmg.note, dmg.kind))
            detail = "{} : {}{}".format(formula, " + ".join(str(v * sg) for _, v, sg in res.dice) or "—",
                                        " {:+d}".format(res.flat) if res.flat else "")
            label = "Soins" if heal or dmg.kind == "soins" else "Dégâts" + (" (critique)" if crit else "")
            title = dmg.title if norm(dmg.title).startswith(("degats", "soins")) else "{} — {}".format(label, dmg.title)
            if crit and "critique" not in norm(title):
                title += " (critique)"
            self.rolls.append({"titre": title, "total": res.total, "detail": detail,
                               "notes": [x for x in (dmg.damage_type, dmg.calcul) if x]})
            if heal:
                self.msg("{} PV récupéré(s).".format(self.eng.heal(res.total)))

    def op_turn_use(self, tile: str, beast: str = "", potion: int = -1) -> None:
        eng = self.eng
        if tile == "classe:cap:forme_sauvage" and not (beast and eng.beast_status(beast)[0]):
            raise ActionError("Choisissez une bête autorisée.")
        drinks = eng.drinkable_potions() if tile == "potion:boire" else []
        if tile == "potion:boire" and not 0 <= int(potion) < len(drinks):
            raise ActionError("Choisissez une potion.")
        res = eng.use_turn_action(tile)
        if not res.get("ok"):
            raise ActionError(res.get("message") or "Action indisponible.")
        self.msg(res.get("message", ""))
        if res.get("potion"):
            p = drinks[int(potion)]
            text = eng.use_consumable(p["source"], p["index"])
            if not text:
                self.ch.tour_bonus = False
                raise ActionError("Aucune potion bue.")
            self.msg(text)
            return
        if tile == "classe:cap:forme_sauvage":
            if not eng.assume_form(beast):
                self._refund(tile)
                raise ActionError("Forme sauvage impossible (plus d'utilisation ?).")
            self.msg(f"Forme sauvage : {beast}.")
            return
        if res.get("objet"):
            info = res["objet"]
            if info.get("description"):
                self.msg(info["description"][:400])
            return
        self._roll_attack(res.get("attaque"), res.get("degats"), bool(res.get("soin")))

    # ---------- forme sauvage / métamorphose (ui/druid_tab.py)
    def op_form_assume(self, name: str) -> None:
        ok, why = self.eng.beast_status(name)
        if not ok:
            raise ActionError(why)
        if not self.eng.assume_form(name):
            raise ActionError("Plus d'utilisation de Forme sauvage disponible.")
        self.msg(f"Forme sauvage : {name}.")

    def op_form_end(self) -> None:
        if self.ch.forme_active:
            self.eng.end_form()
            self.msg("Forme normale reprise.")

    # ---------- sorts accordés par le MJ (ui/magic_tab.py)
    def op_gm_spell_add(self, nom: str, usage: str = "À volonté", note: str = "") -> None:
        from core.engine_extras import GM_USAGES
        if usage not in GM_USAGES:
            usage = GM_USAGES[0]
        if not self.eng.add_gm_spell(str(nom)[:120], usage, str(note)[:300]):
            raise ActionError("Sort déjà accordé ou nom vide.")

    def op_gm_spell_remove(self, nom: str) -> None:
        self.eng.remove_gm_spell(nom)

    # ---------- objet magique sur mesure (ui/magic_items_panel.py)
    def op_custom_magic(self, nom: str, type: str = "Objet merveilleux", rarete: str = "peu commun",
                        lien: bool = False, description: str = "", poids: float = 0.0, ca: int = 0) -> None:
        try:
            poids = max(0.0, min(1000.0, float(poids or 0)))
        except (TypeError, ValueError):
            poids = 0.0
        name = self.eng.add_custom_magic_item(str(nom)[:100], str(type)[:60], str(rarete)[:40], bool(lien),
                                              str(description)[:4000], poids, _int(ca, 0, 10))
        if not name:
            raise ActionError("Nom d'objet vide.")
        self.msg(f"Objet sur mesure ajouté : {name}.")

    # ---------- ménagerie (ui/companions_tab.py)
    def op_menagerie_add(self, id: str, nom: str = "") -> None:
        if not self.eng.menagerie_add(id, str(nom)[:80]):
            raise ActionError("Créature inconnue.")

    def op_menagerie_remove(self, uid: str) -> None:
        self.eng.menagerie_remove(uid)

    def op_menagerie_set(self, uid: str, field: str, value: Any) -> None:
        inst = self.eng.menagerie_get(uid)
        if inst is None:
            raise ActionError("Créature introuvable.")
        if field == "nom":
            inst["nom"] = str(value or "").strip()[:80] or (self.eng.entity(inst["id"]) or {}).get("name", "")
        elif field == "statut":
            if value not in C.STATUSES:
                raise ActionError("Statut inconnu.")
            inst["statut"] = value
        elif field == "pv":
            top = self.eng.entity_sheet(inst)["pv_max"]
            inst["pv"] = _int(value, 0, top)
            if inst["pv"] == 0 and inst.get("statut") == "Actif":
                inst["statut"] = "À 0 PV"
        elif field == "pv_temp":
            inst["pv_temp"] = _int(value, 0, 999)
        elif field == "niveau_sort":
            inst["niveau_sort"] = _int(value, 1, 9)
            inst["pv"] = self.eng.entity_sheet(inst)["pv_max"]       # nouvelle convocation : PV pleins
        else:
            raise ActionError("Champ inconnu.")

    # ---------- inventaire (ui/inventory_tab.py, ui/magic_items_panel.py)
    def op_item_add(self, nom: str, qte: int = 1) -> None:
        nom = str(nom or "").strip()[:120]
        if not nom:
            raise ActionError("Nom d'objet vide.")
        self.eng.add_item(nom, _int(qte, 1, 9999))

    def op_pack_add(self, nom: str) -> None:
        """Bouton « Paquetage » : le paquetage est développé en objets individuels."""
        if nom not in self.db.equipment:
            raise ActionError("Paquetage inconnu.")
        n = self.eng.add_pack(nom, expand=True)
        self.msg(f"{nom} : {n} ligne(s) ajoutée(s) à l'inventaire.")

    def op_item_qty(self, idx: int, qte: int) -> None:
        idx = _int(idx)
        if not 0 <= idx < len(self.ch.equipement):
            raise ActionError("Objet introuvable.")
        qte = _int(qte, 0, 9999)
        if qte == 0:
            self.eng.remove_item(idx)
        else:
            self.ch.equipement[idx]["qte"] = qte

    def op_item_remove(self, idx: int) -> None:
        self.eng.remove_item(_int(idx))

    def op_magic_add(self, nom: str, bonus: int = 0) -> None:
        if nom not in self.db.magic_items:
            raise ActionError("Objet magique inconnu.")
        if not self.eng.add_magic_item(nom, _int(bonus, 0, 3)):
            self.msg(f"« {nom} » est déjà dans l'inventaire.")

    def op_magic_remove(self, idx: int) -> None:
        self.eng.remove_magic_item(_int(idx))

    def op_magic_equip(self, idx: int, value: bool) -> None:
        self.eng.set_equipped(_int(idx), bool(value))

    def op_magic_attune(self, idx: int, value: bool) -> None:
        if not self.eng.set_attuned(_int(idx), bool(value)):
            raise ActionError("Harmonisation impossible (limite atteinte, objet sans lien ou prérequis non rempli).")


OPS: dict[str, Callable] = {name[3:]: fn for name, fn in vars(Controller).items() if name.startswith("op_")}


# ---------------------------------------------------------------------------------------------------------------
# Construction / application
# ---------------------------------------------------------------------------------------------------------------
def load_character(data: dict | None) -> tuple[Engine, Character]:
    db = get_db()
    if not data:
        ch = Engine.new_character(db)
    else:
        if not isinstance(data, dict) or "classes" not in data:
            raise ActionError("Ce fichier n'est pas une sauvegarde de personnage valide.")
        ch = Character.from_dict(data)
        if not ch.classes:
            ch.classes = Engine.new_character(db).classes
    eng = Engine(db, ch)
    eng.normalize()
    return eng, ch


def apply(data: dict | None, ops: list[dict] | None = None) -> dict:
    """Point d'entrée unique : personnage + opérations -> personnage normalisé + fiche calculée."""
    eng, ch = load_character(data)
    ctl = Controller(eng)
    errors: list[str] = []
    for op in ops or []:
        if not isinstance(op, dict) or op.get("op") not in OPS:
            errors.append("Opération inconnue.")
            continue
        args = {k: v for k, v in op.items() if k != "op"}
        try:
            OPS[op["op"]](ctl, **args)
        except ActionError as exc:
            errors.append(str(exc))
        except TypeError:
            errors.append("Paramètres invalides pour « {} ».".format(op["op"]))
        eng.normalize()
    return {"character": ch.to_dict(), "sheet": build_sheet(eng), "messages": ctl.messages,
            "errors": errors, "rolls": ctl.rolls}


# ---------------------------------------------------------------------------------------------------------------
# Fiche calculée (lecture seule)
# ---------------------------------------------------------------------------------------------------------------
def _spell_view(eng: Engine, name: str, cls: str = "") -> dict:
    sp = eng.db.find_spell(name) or {"nom": name, "niveau": 0}
    out = {k: sp.get(k) for k in ("nom", "niveau", "ecole", "temps", "portee", "composantes", "duree",
                                  "concentration", "rituel", "description", "degats", "type_degats", "test")}
    try:
        out["buff"] = bool(eng.buff_options(sp["nom"])) and not eng.spell_is_personal(sp["nom"])
    except Exception:
        out["buff"] = False
    try:
        if sp.get("niveau"):
            vals = eng.spell_values(sp["nom"], 0, cls) or {}
            out["calcul"] = {k: vals.get(k) for k in ("niveau", "degats", "type_degats", "soins", "pv_temp",
                                                      "regle_sup")}
        elif sp.get("nom") in eng.db.spells:
            st = eng.cantrip_stats(sp["nom"]) or {}
            out["calcul"] = {"degats": st.get("degats") or st.get("calcul") or ""}
    except Exception:                                   # un sort exotique ne doit jamais casser la fiche
        out["calcul"] = {}
    return out


def _options_view(eng: Engine) -> dict:
    """Choix de classe et d'espèce hors assistant : ascendance draconique, runes / tirs / manœuvres / métamagie,
    Technique supérieure, pacte, manifestations occultes, Livre des secrets anciens."""
    from core.data_loader import PACTS
    from core.engine_extras import DRACONIC
    ch, db = eng.ch, eng.db
    out: dict = {"couleurs": [{"nom": c, "description": "{} — {} — JS de {}".format(*v)} for c, v in DRACONIC.items()]}
    try:
        breath = eng.breath_weapon()
    except Exception:
        breath = None
    out["dragon_race"] = {"couleur": ch.ascendance_raciale,
                          "info": ("Souffle ({t}) : {z}, JS de {js} DD {dd}, {d}".format(
                              t=breath["type"], z=breath["zone"], js=breath["js"], dd=breath["dd"], d=breath["degats"])
                              if breath.get("type") else "")} if breath is not None else None
    try:
        sorc = eng.is_draconic_sorcerer()
        lineage = eng.sorcerer_lineage() if sorc else None
    except Exception:
        sorc, lineage = False, None
    out["dragon_sorc"] = {"couleur": ch.ascendance_ensorceleur,
                          "info": "Type de dégâts : {}".format(lineage["type"]) if lineage else ""} if sorc else None
    out["ensembles"] = [{"key": st["key"], "label": st["label"], "total": st["total"], "chosen": st["chosen"],
                         "options": [{"nom": n, "description": d} for n, d in st["options"].items()]}
                        for st in eng.option_sets()]
    out["technique"] = {"choix": ch.technique_manoeuvre,
                        "options": [{"nom": n, "description": d} for n, d in db.maneuvers.items()]} \
        if eng.superior_technique() else None
    slots = eng.manifestation_slots()
    warlock = eng.class_level("Occultiste") > 0
    out["pacte"] = {"disponible": eng.pact_available(), "choix": ch.pacte, "options": list(PACTS)} if warlock else None
    if slots["total"] or ch.manifestations:
        def info(n):
            m = db.manifestations.get(n, {})
            st, why = eng.manifestation_status(n)
            return {"nom": n, "description": m.get("description", ""), "etat": st, "raison": why,
                    "niveau": m.get("niveau") or 0, "pacte": m.get("pacte") or "",
                    "sorts": "; ".join("{} ({})".format(g["sort"], g["usage"]) for g in m.get("sorts", []))}
        out["manifestations"] = {"total": slots["total"], "choisies": [info(n) for n in ch.manifestations],
                                 "options": [info(n) for n in sorted(db.manifestations, key=norm)
                                             if n not in ch.manifestations]}
    else:
        out["manifestations"] = None
    if eng.ritual_book_active():
        out["rituels"] = {"choisis": list(ch.rituels_livre), "max": eng.ritual_book_max_level(),
                          "manquants": eng.ritual_book_missing(),
                          "options": [{"nom": sp["nom"], "niveau": sp["niveau"]} for sp in eng.ritual_book_options()
                                      if sp["nom"] not in ch.rituels_livre]}
    else:
        out["rituels"] = None
    return out


def _turn_view(eng: Engine) -> dict:
    try:
        tiles = eng.turn_actions()
    except Exception:                                    # le suivi du tour ne doit jamais casser la fiche
        tiles = []
    st = eng.turn_state()
    return {"etat": {k: st[k] for k in ("Action", "Action bonus", "Réaction")},
            "deplacement": st["deplacement"], "vitesse": st["vitesse"],
            "attaques": eng.attacks_per_action(), "attaques_faites": int(eng.ch.tour_attaques),
            "actions": [{"id": t["id"], "nom": t["nom"], "icone": t.get("icone", ""), "type": t["type"],
                         "origine": t.get("origine", ""), "description": t.get("description", ""),
                         "disponible": t["disponible"], "raison": t.get("raison", ""), "cout": t.get("cout", ""),
                         "groupe": t.get("groupe", "capacites"), "sort": (t.get("ref") or {}).get("sort", "")}
                        for t in tiles],
            "potions": [{"nom": p["nom"], "qte": p["qte"]} for p in eng.drinkable_potions()]}


def _beast_brief(eng: Engine, b: dict) -> dict:
    return {"nom": b["nom"], "fp": b.get("fp_txt", ""), "pv": eng.beast_hp_max(b["nom"]), "ca": eng.beast_ac(b),
            "vitesse": b.get("vitesse", ""), "type": b.get("type", ""), "actions": b.get("actions", []),
            "traits": b.get("traits", [])}


def _forms_view(eng: Engine) -> dict:
    ch = eng.ch
    out: dict = {"forme": eng.form_status(), "druide": None, "metamorphose": []}
    if eng.class_level("Druide") >= 2:
        ws = eng.wild_shape()
        out["druide"] = {"regles": {k: ws.get(k) for k in ("fp_max", "mouvements", "lune", "niveau")},
                         "fp_max_txt": R.fmt_cr(ws.get("fp_max", 0)),
                         "betes": [_beast_brief(eng, b) for b in sorted(eng.allowed_beasts(),
                                                                         key=lambda b: (b["fp"], norm(b["nom"])))]}
    knows = any(norm(s["nom"]) == "metamorphose" for lst in ch.sorts.values() for s in lst)
    if knows:
        out["metamorphose"] = [_beast_brief(eng, b) for b in sorted(eng.polymorph_beasts(),
                                                                   key=lambda b: (b["fp"], norm(b["nom"])))]
    return out


def _menagerie_view(eng: Engine) -> list[dict]:
    out = []
    for m in eng.ch.menagerie:
        try:
            sh = eng.entity_sheet(m)
        except Exception:
            continue
        ent = sh["entite"]
        out.append({"uid": m["uid"], "id": m["id"], "nom": sh["nom"], "pv": m.get("pv"), "pv_temp": m.get("pv_temp", 0),
                    "statut": m.get("statut", "Actif"), "niveau_sort": m.get("niveau_sort"), "auto": m.get("auto", False),
                    "pv_max": sh["pv_max"], "ca": sh["ca"], "ca_note": sh["ca_note"], "taille": sh["taille"],
                    "type": ent.get("type", ""), "vitesses": sh["vitesses"], "stats": sh["stats"], "mods": sh["mods"],
                    "sauvegardes": sh["sauvegardes"], "competences": sh["competences"], "dd": sh["dd"],
                    "perception_passive": sh["perception_passive"], "niveau_sort_min": sh["niveau_sort_min"],
                    "sens": ent.get("senses", ""), "langues": ent.get("languages", ""),
                    "actions": [{"nom": a.get("name", ""), "description": a.get("description", ""),
                                 "attaque": a.get("attack_bonus"), "degats": a.get("damage_dice") or "",
                                 "type_degats": a.get("damage_type") or ""} for a in sh["actions"]],
                    "traits": [{"nom": t.get("name", ""), "description": t.get("description", "")} for t in sh["traits"]],
                    "reactions": [{"nom": t.get("name", ""), "description": t.get("description", "")}
                                  for t in sh["reactions"]]})
    return out


def build_sheet(eng: Engine) -> dict:
    ch, db = eng.ch, eng.db
    with eng.batch():
        mods = eng.mods()
        abilities = []
        for ab in ABILITIES:
            parts = eng.score_parts(ab)
            abilities.append({"nom": ab, "abbr": R.ABBR[ab], "score": eng.score(ab), "mod": mods[ab],
                              "parts": parts, "achat": ch.scores_achat.get(ab, 8),
                              "manuel": ch.scores_manuel.get(ab, 10), "divers": ch.bonus_divers.get(ab, 0),
                              "tirage": ch.des_affectation.get(ab, -1),
                              "peut_monter": R.can_raise(ch.scores_achat, ab)})
        classes = []
        for idx, entry in enumerate(ch.classes):
            feats = eng.features(entry)
            classes.append({
                "index": idx, "nom": entry["nom"], "niveau": entry["niveau"],
                "sous_classe": entry.get("sous_classe", ""), "de_vie": db.start_info(entry["nom"]).get("de_vie", ""),
                "sous_classes": [s["nom"] for s in db.subclasses(entry["nom"])],
                "niveau_sous_classe": eng.subclass_level(entry["nom"]),
                "aptitudes": [{"nom": f["nom"], "niveau": f["niveau"], "description": f["description"],
                               "source": f["source"], "debloque": f["debloque"]} for f in feats],
                "ressources": [list(r) for r in eng.resources(entry)],
            })
        ac = eng.armor_class_detail()
        trackers = []
        for tr in eng.resource_trackers():
            trackers.append({**{k: tr.get(k) for k in ("key", "label", "total", "recover", "info", "where")},
                             "used": eng.resource_used(tr["key"])})
        weapons = []
        for key in ("armes_cac", "armes_distance"):
            for i, slot in enumerate(getattr(ch, key)):
                st = None
                if slot.get("nom"):
                    try:
                        st = eng.weapon_stats(slot)
                    except Exception:
                        st = None
                weapons.append({"key": key, "index": i, "nom": slot.get("nom", ""), "bonus": slot.get("bonus", 0),
                                "stats": {k: st.get(k) for k in ("attaque", "degats", "type_degats", "calcul",
                                                                 "proprietes", "portee", "maitrise", "carac")}
                                if st else None})
        # ---- magie
        slots_total = eng.spell_slots()
        pact_n, pact_lvl = eng.pact()
        casters = []
        for c in eng.casters():
            cls = c["classe"]
            known = []
            for s in ch.sorts.get(cls, []):
                v = _spell_view(eng, s["nom"], cls)
                v.update(prepare=s.get("prepare", True), accorde=bool(s.get("accorde")))
                known.append(v)
            for dom in eng.domain_spells(next(e for e in ch.classes if e["nom"] == cls)) \
                    if any(e["nom"] == cls for e in ch.classes) else []:
                if not any(k["nom"] == dom for k in known):
                    v = _spell_view(eng, dom, cls)
                    v.update(prepare=True, accorde=True, domaine=True)
                    known.append(v)
            known.sort(key=lambda s: (s.get("niveau") or 0, norm(s["nom"])))
            casters.append({**{k: c.get(k) for k in ("classe", "niveau", "carac", "mod", "kind", "mode", "dc",
                                                      "attaque", "mineurs_max", "connus_max", "prepares_max",
                                                      "niveau_max")},
                            "compte": eng.spell_counts(cls), "sorts": known,
                            "apprenables": [s["nom"] for s in eng.available_spells(cls)]})
        try:
            granted = [{"nom": g.get("nom"), "source": g.get("source", ""), "usage": g.get("usage", "")}
                       for g in eng.granted_spells()]
        except Exception:
            granted = []
        try:
            racial = [{"nom": r.get("nom"), "usage": r.get("usage", ""), "niveau": r.get("niveau_obtention",
                                                                                        r.get("niveau", ""))}
                      for r in eng.racial_spells()]
        except Exception:
            racial = []
        block = eng.spell_block_reason()
        # ---- inventaire
        items = []
        for i, it in enumerate(ch.equipement):
            cat = db.catalog.get(it["nom"], {})
            items.append({"index": i, "nom": it["nom"], "qte": it.get("qte", 1), "poids": cat.get("poids", 0),
                          "categorie": cat.get("categorie", "Divers"), "description": cat.get("description", "")})
        magic = []
        for i, e in enumerate(ch.objets_magiques):
            item = eng.magic_item(e["nom"]) or {}
            state, cond = eng.attune_status(e["nom"])
            magic.append({"index": i, "nom": e["nom"], "equipe": e.get("equipe", True),
                          "harmonise": e.get("harmonise", False), "lien": bool(item.get("lien")),
                          "rarete": item.get("rarete", ""), "type": item.get("type", ""),
                          "description": item.get("description", ""), "prerequis": state, "condition": cond})
        effects = []
        for key in eng.active_effect_keys():
            fx = FX.EFFECTS.get(key, {"nom": "Concentration" if key == "concentration" else key})
            effects.append({"key": key, "nom": fx.get("nom", key), "icone": fx.get("icone", "✦"),
                            "categorie": fx.get("categorie", ""), "description": fx.get("description", ""),
                            "inne": bool(eng.innate_source(key)) if hasattr(eng, "innate_source") else False})
        sheet = {
            "resume": {"nom": ch.nom or "Sans nom", "niveau": eng.total_level, "maitrise": eng.prof,
                       "niveau_xp": eng.level_from_xp(), "xp_seuils": R.XP_THRESHOLDS,
                       "classes_txt": " / ".join(f"{c['nom']} {c['niveau']}" for c in ch.classes),
                       "race_txt": ch.sous_race or ch.race, "texte": eng.summary()},
            "abilities": abilities,
            "point_buy": {"restant": R.point_buy_remaining(ch.scores_achat), "total": R.POINT_BUY_TOTAL},
            "tirages": ch.des_tirages, "race_rule": eng.race_rule(), "race_bonus": eng.race_bonus(),
            "asi": [{**s, "choix": ch.ameliorations.get(s["id"], {"mode": "aucun"}),
                     "etat": list(eng.feat_status(ch.ameliorations.get(s["id"], {}).get("don", "")))
                     if ch.ameliorations.get(s["id"], {}).get("mode") == "don"
                     and ch.ameliorations.get(s["id"], {}).get("don") else None} for s in eng.asi_slots()],
            "dons": eng.chosen_feats(), "dons_mj": list(ch.dons_mj),
            "classes": classes,
            "sous_races": [s["nom"] for s in db.subraces_of(ch.race)],
            "race_traits": eng.race_traits(),
            "historique": db.backgrounds.get(ch.historique, {}),
            "saves": eng.save_rows(), "skills": eng.skill_rows(), "resilient": sorted(eng.resilient_saves()),
            "class_skills": eng.class_skill_status(),
            "perception_passive": eng.passive_perception(),
            "langues": {"connues": eng.languages_known(), "permises": eng.languages_allowed()},
            "maitrises": eng.proficiency_summary(),
            "combat": {"pv_max": eng.hp_max(), "pv": ch.pv_actuels, "pv_temp": ch.pv_temporaires,
                       "pv_detail": eng.hp_breakdown(), "des_vie": eng.hit_dice_pool(),
                       "ca": ac.get("valeur"), "ca_formule": ac.get("formule"), "ca_calcul": ac.get("chiffres"),
                       "ca_note": ac.get("note", ""), "initiative": eng.initiative(), "vitesse": eng.speed_text(),
                       "armure": ch.armure, "armes": weapons, "ressources": trackers,
                       "mort": [ch.mort_reussites, ch.mort_echecs], "effets": effects,
                       "concentration": ch.concentration, "forme": {"nom": ch.forme_active, "pv": ch.forme_pv}
                       if ch.forme_active else None,
                       "equipement_non_maitrise": eng.unproficient_gear(),
                       "styles": [{**sl, "choix": ch.styles_combat.get(sl["id"], ""),
                                   "options": [{"nom": n, "description": db.styles_by_class.get(sl["classe"], {}).get(n)
                                                or db.armor_models.get(n, "")} for n in eng.style_options(sl["id"])]}
                                  for sl in eng.fighting_style_slots()]},
            "magie": {"lanceurs": casters, "emplacements": slots_total, "utilises": ch.emplacements_utilises,
                      "pacte": {"n": pact_n, "niveau": pact_lvl, "utilises": ch.pacte_utilises},
                      "accordes": granted, "raciaux": racial, "bloque": block[1] if block else "",
                      "concentration": ch.concentration},
            "inventaire": {"objets": items, "pieces": ch.pieces, "charge": eng.encumbrance(),
                           "magiques": magic, "harmonises": eng.attuned_count(),
                           "harmonisation_max": eng.attunement_limit()},
            "options": _options_view(eng),
            "tour": _turn_view(eng), "formes": _forms_view(eng),
            "menagerie": _menagerie_view(eng),
            "conseils_compagnons": [{"niveau": h.get("niveau", "info"), "texte": h.get("texte", ""),
                                     "recommandes": list(h.get("recommandes", []))} for h in eng.companion_hints()],
            "sorts_mj": list(ch.sorts_mj),
            "alertes": eng.warnings(),
            "a_faire": [{"onglet": m["onglet"], "message": m["message"]} for m in eng.missing_choices()],
            "niveau_max_atteint": not eng.level_up_options(),
        }
    return sheet


# ---------------------------------------------------------------------------------------------------------------
# Catalogue (listes de choix, envoyées une fois puis gardées en cache par le navigateur)
# ---------------------------------------------------------------------------------------------------------------
_CATALOG: dict | None = None


def catalog() -> dict:
    global _CATALOG
    if _CATALOG is None:
        db = get_db()
        from ui.theme import THEMES                       # module pur Python (aucune dépendance Qt)
        themes = {k: {f: getattr(t, f) for f in ("name", "game", "bg", "panel", "panel_alt", "input_bg", "text",
                                                  "muted", "accent_text", "border", "ornament", "button_bg",
                                                  "button_hover", "button_text", "select_bg", "select_text",
                                                  "warn", "good", "locked", "font", "font_title")}
                  for k, t in THEMES.items()}
        _CATALOG = {
            "classes": db.class_names(), "races": db.race_names(), "historiques": db.background_names(),
            "alignements": R.ALIGNMENTS, "caracteristiques": ABILITIES, "abbr": R.ABBR,
            "langues": [{"nom": x["nom"], "categorie": x.get("categorie", "")} for x in db.languages],
            "armures": [{"nom": n, "categorie": a.get("categorie", ""), "ca": a.get("ca_base", "")}
                        for n, a in db.armors.items()],
            "boucliers": list(db.shields),
            "armes": [{"nom": n, "categorie": w.get("categorie", ""), "type": w.get("type", ""),
                       "degats": w.get("degats", ""), "lancer": "Lancer" in (w.get("proprietes") or [])}
                      for n, w in db.weapons.items()],
            "objets": [{"nom": n, "categorie": c.get("categorie", ""), "prix": c.get("prix", ""),
                        "poids": c.get("poids_txt", "")} for n, c in db.catalog.items()],
            "paquetages": [n for n in db.equipment if "paquetage" in norm(n)],
            "objets_magiques": [{"nom": m["nom"], "rarete": m.get("rarete", ""), "type": m.get("type", ""),
                                 "lien": bool(m.get("lien"))} for m in db.magic_items.values()],
            "dons": [{"nom": f["nom"], "prerequis": f.get("prerequis", ""), "asi": f.get("asi_texte", ""),
                      "carac_choix": f.get("carac_choix", []), "description": f.get("description", "")}
                     for f in sorted(db.feats.values(), key=lambda f: norm(f["nom"]))],
            "sorts": [{"nom": s["nom"], "niveau": s["niveau"], "ecole": s.get("ecole", ""),
                       "classes": s.get("classes", []), "concentration": s.get("concentration", False),
                       "rituel": s.get("rituel", False)} for s in db.spells.values()],
            "effets": [{"key": k, "nom": v["nom"], "icone": v.get("icone", ""), "categorie": v.get("categorie", "")}
                       for k, v in FX.EFFECTS.items() if v.get("categorie") in ("État", "Bonus", "Malus")],
            "themes": themes,
            "entites": [{"id": e["id"], "nom": e["name"], "type": e["entity_type"],
                         "type_label": C.TYPE_LABELS.get(e["entity_type"], e["entity_type"]),
                         "fp": e.get("cr", ""), "creature": e.get("type", ""),
                         "sources": ", ".join(x.get("name", "") for x in (e.get("summon_info") or {}).get("sources", [])
                                              if isinstance(x, dict))}
                        for e in sorted(db.entities.values(), key=lambda e: norm(e["name"]))],
            "statuts_compagnons": C.STATUSES,
            "usages_mj": __import__("core.engine_extras", fromlist=["GM_USAGES"]).GM_USAGES,
        }
    return _CATALOG


def spell_details(name: str, data: dict | None = None) -> dict:
    """Détail d'un sort (avec les calculs du personnage si fourni)."""
    db = get_db()
    sp = db.find_spell(name)
    if not sp:
        raise ActionError("Sort inconnu.")
    if data:
        eng, _ = load_character(data)
        return _spell_view(eng, sp["nom"])
    return {k: sp.get(k) for k in ("nom", "niveau", "ecole", "temps", "portee", "composantes", "duree",
                                   "concentration", "rituel", "description", "degats", "type_degats", "classes")}


def text_sheet(data: dict) -> str:
    """Fiche lisible (texte brut / Markdown léger) pour l'export « .txt »."""
    eng, ch = load_character(data)
    s = build_sheet(eng)
    L: list[str] = []
    r = s["resume"]
    L += [f"# {r['nom']}", "",
          f"{r['race_txt']} — {r['classes_txt']} (niveau {r['niveau']}) — {ch.historique} — {ch.alignement}",
          f"Joueur : {ch.joueur or '—'}   XP : {ch.experience}   Bonus de maîtrise : {R.fmt_bonus(r['maitrise'])}", ""]
    L.append("## Caractéristiques")
    L += ["- {} {} ({})".format(a["nom"], a["score"], R.fmt_bonus(a["mod"])) for a in s["abilities"]]
    c = s["combat"]
    L += ["", "## Combat",
          f"- PV : {c['pv']} / {c['pv_max']}" + (f" (+{c['pv_temp']} temporaires)" if c["pv_temp"] else ""),
          f"- CA : {c['ca']}  ({c['ca_formule']})", f"- Initiative : {R.fmt_bonus(c['initiative'])}",
          f"- Vitesse : {c['vitesse']}",
          "- Dés de vie : " + ", ".join(f"{d['restants']}/{d['total']} {d['de']}" for d in c["des_vie"])]
    for w in c["armes"]:
        if w["nom"] and w["stats"]:
            L.append("- {} : {} au toucher, {} {}".format(w["nom"], R.fmt_bonus(w["stats"]["attaque"] or 0),
                                                         w["stats"]["degats"], w["stats"]["type_degats"] or ""))
    for t in c["ressources"]:
        L.append("- {} : {} / {}".format(t["label"], (t["total"] or 0) - t["used"], t["total"] or "∞"))
    L += ["", "## Jets de sauvegarde"]
    L += ["- {}{} {}".format(x["carac"], " ●" if x["maitrise"] else "", R.fmt_bonus(x["bonus"])) for x in s["saves"]]
    L += ["", "## Compétences"]
    L += ["- {}{} ({}) {}".format(x["nom"], " ●●" if x["expertise"] else " ●" if x["maitrise"] else "",
                                  R.ABBR[x["carac"]], R.fmt_bonus(x["bonus"])) for x in s["skills"]]
    L += [f"- Perception passive : {s['perception_passive']}", "",
          "## Langues", ", ".join(ch.langues_liste) + (f" ; {ch.langues}" if ch.langues else "")]
    if s["dons"]:
        L += ["", "## Dons", ", ".join(s["dons"])]
    L += ["", "## Aptitudes"]
    for cl in s["classes"]:
        L.append(f"### {cl['nom']} {cl['niveau']}" + (f" — {cl['sous_classe']}" if cl["sous_classe"] else ""))
        L += [f"- (niv. {f['niveau']}) {f['nom']}" for f in cl["aptitudes"] if f["debloque"]]
    L += ["", "### Traits d'espèce"] + [f"- {t['nom']}" for t in s["race_traits"]]
    m = s["magie"]
    if m["lanceurs"]:
        L += ["", "## Magie"]
        L.append("Emplacements : " + ", ".join(f"niv. {i + 1} : {n - m['utilises'][i]}/{n}"
                                               for i, n in enumerate(m["emplacements"]) if n))
        if m["pacte"]["n"]:
            L.append(f"Pacte : {m['pacte']['n'] - m['pacte']['utilises']}/{m['pacte']['n']} (niveau {m['pacte']['niveau']})")
        for cs in m["lanceurs"]:
            L.append(f"### {cs['classe']} — DD {cs['dc']}, attaque {R.fmt_bonus(cs['attaque'])} ({cs['carac']})")
            for sp in cs["sorts"]:
                L.append("- [{}] {}{}".format("mineur" if not sp["niveau"] else sp["niveau"], sp["nom"],
                                              "" if sp.get("prepare", True) or not sp["niveau"] else " (non préparé)"))
    inv = s["inventaire"]
    L += ["", "## Inventaire",
          "Pièces : " + ", ".join(f"{v} {k}" for k, v in inv["pieces"].items())]
    L += [f"- {o['qte']} × {o['nom']}" for o in inv["objets"]]
    if inv["magiques"]:
        L += ["", "### Objets magiques"]
        L += ["- {}{}{}".format(o["nom"], " (équipé)" if o["equipe"] else "", " (harmonisé)" if o["harmonise"] else "")
              for o in inv["magiques"]]
    for title, text in (("Histoire", ch.histoire), ("Traits de personnalité", ch.traits), ("Notes", ch.notes),
                        ("Notes d'inventaire", ch.inventaire)):
        if text.strip():
            L += ["", f"## {title}", text.strip()]
    L += ["", "---", "Exporté depuis Fiche D&D 5e (web). Pour réimporter le personnage, utilisez l'export JSON."]
    return "\n".join(L) + "\n"


def roll_expression(expr: str) -> dict:
    """Lancer libre (« 2d6+3 ») avec le parseur du moteur."""
    dice, flat = R.parse_dice(expr or "")
    if not dice and not flat:
        raise ActionError("Expression de dés invalide (ex. 1d20+5, 2d6+3).")
    if sum(n for n, _ in dice) > 100:
        raise ActionError("100 dés maximum.")
    rolled = [[random.randint(1, sides) for _ in range(n)] for n, sides in dice]
    total = sum(sum(r) for r in rolled) + flat
    return {"expression": expr, "des": rolled, "faces": [s for _, s in dice], "bonus": flat, "total": total}
