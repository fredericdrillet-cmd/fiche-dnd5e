"""
Résolution unifiée des actions du Combat (v39) — logique pure, mélangée à `Engine`.

    - Armes : main principale (Action, Attaque supplémentaire), main secondaire (Action bonus, combat à deux armes :
      dégâts sans modificateur sauf s'il est négatif ou avec le style Combat à deux armes), mains nues si la main
      principale est vide. Les données viennent des cases « Main principale » / « Main secondaire » / « Distance »
      du mannequin (ch.armes_cac[0], ch.armes_cac[1], ch.armes_distance[0]).
    - Bonus de dégâts des effets actifs (Faveur divine, Marque du chasseur, Maléfice…) : inconditionnels ajoutés aux
      dés, conditionnels (« cible marquée ») proposés après un coup qui touche.
    - Maître de guerre : une tuile par manœuvre apprise (dé de supériorité dépensé ; manœuvres offensives = attaque
      avec l'arme équipée + dé aux dégâts, Attaque précise = dé au jet d'attaque, DD affiché).
    - Roublard : Attaque sournoise (arme de finesse ou à distance, 1 fois par tour, dégâts de l'arme + Xd6) et une
      tuile par option d'Action astucieuse (Foncer, Se désengager, Se cacher).
    - Sorts : `spell_resolution()` décrit le jet (attaque de sort, JS avec DD, automatique, soins) au niveau
      d'emplacement effectivement dépensé (surclassement, Magie des pactes).
"""
from __future__ import annotations

import math
import re
from typing import Optional

from . import dice as D
from . import effects as FX
from . import rules as R
from .rules import norm

# manœuvre -> (flux, type d'action) ; flux : « attaque » (attaque d'arme + dé aux dégâts), « precise » (dé ajouté au
# jet d'attaque), « riposte » (attaque d'arme en réaction + dé), « de » (seul le dé est lancé)
MANEUVER_FLOWS = {
    "Attaque menaçante": ("attaque", "Action"), "Attaque précise": ("precise", "Action"),
    "Attaque repoussante": ("attaque", "Action"), "Attaque avec feinte": ("de", "Action bonus"),
    "Croc-en-jambe": ("attaque", "Action"), "Désarmement": ("attaque", "Action"),
    "Distraction": ("attaque", "Action"), "Fente": ("attaque", "Action"), "Jeu de jambes": ("de", "Spécial"),
    "Manœuvre tactique": ("attaque", "Action"), "Parade": ("parade", "Réaction"), "Provocation": ("attaque", "Action"),
    "Ralliement": ("ralliement", "Action bonus"), "Riposte": ("riposte", "Réaction"),
    "Attaque balayage": ("balayage", "Action"), "Commandement": ("de", "Spécial"),
    # Chaudron des merveilles de Tasha
    "Embuscade": ("de", "Spécial"), "Échange de position": ("de", "Spécial"), "Garde préparée": ("riposte", "Réaction"),
    "Présence imposante": ("de", "Spécial"), "Frappe agrippante": ("de", "Action bonus"),
    "Lancer rapide": ("attaque_lancer", "Action bonus"), "Évaluation tactique": ("de", "Spécial"),
}
CUNNING = [("foncer", "Foncer", "🏃", "foncer"), ("desengager", "Se désengager", "↩️", "desengagement"),
           ("cacher", "Se cacher", "🫥", "cache")]
DUAL_WIELDER_FEATS = ("combattant a deux armes", "maitre des armes doubles")


def maneuvers_known(level: int) -> int:
    """Maître de guerre : 3 manœuvres au niveau 3, 5 au 7, 7 au 10, 9 au 15."""
    return 0 if level < 3 else 3 if level < 7 else 5 if level < 10 else 7 if level < 15 else 9


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", norm(text)).strip("-")


class CombatFlowMixin:
    # ------------------------------------------------------------------ armes équipées (mannequin)
    def main_hand_slot(self) -> Optional[dict]:
        slot = self.ch.armes_cac[0] if self.ch.armes_cac else None
        return slot if slot and slot.get("nom") and slot["nom"] in self.db.weapons else None

    def off_hand_slot(self) -> Optional[dict]:
        slot = self.ch.armes_cac[1] if len(self.ch.armes_cac) > 1 else None
        return slot if slot and slot.get("nom") and slot["nom"] in self.db.weapons else None

    def ranged_slot(self) -> Optional[dict]:
        slot = self.ch.armes_distance[0] if self.ch.armes_distance else None
        return slot if slot and slot.get("nom") and slot["nom"] in self.db.weapons else None

    @staticmethod
    def unarmed_slot() -> dict:
        return {"nom": "Mains nues", "bonus": 0, "maitrise": None}

    def off_hand_free(self, slot: Optional[dict] = None) -> bool:
        """v46 : main secondaire libre (ni bouclier, ni seconde arme) — une arme polyvalente se tient alors à deux
        mains. `slot` = arme examinée : l'arme de la main secondaire elle-même est toujours à une main."""
        ch = self.ch
        if ch.armure.get("bouclier"):
            return False
        off = ch.armes_cac[1] if len(ch.armes_cac) > 1 else {}
        if slot is not None and off is slot:
            return False
        return not (off.get("nom") and off["nom"] in self.db.weapons)

    def dual_wielding(self) -> bool:
        return self.main_hand_slot() is not None and self.off_hand_slot() is not None

    def _props(self, slot: Optional[dict]) -> set[str]:
        w = self.db.weapons.get((slot or {}).get("nom", ""), {})
        return {norm(p) for p in w.get("proprietes", [])}

    def has_dual_wielder(self) -> bool:
        return any(norm(f).startswith(DUAL_WIELDER_FEATS) for f in self.chosen_feats())

    def offhand_status(self) -> tuple[bool, str]:
        """Attaque en main secondaire possible ? (règle du combat à deux armes, PHB p. 195)."""
        main, off = self.main_hand_slot(), self.off_hand_slot()
        if off is None:
            return False, "Aucune arme en main secondaire."
        if main is None:
            return False, "Aucune arme en main principale."
        feat = self.has_dual_wielder()
        for slot, label in ((main, "principale"), (off, "secondaire")):
            props = self._props(slot)
            w = self.db.weapons.get(slot["nom"], {})
            if w.get("type") != "cac" or "deux mains" in props:
                return False, "L'arme en main {} doit être une arme de corps à corps à une main.".format(label)
            if not feat and "legere" not in props:
                return False, ("L'arme en main {} doit avoir la propriété Légère (sauf don Combattant à deux "
                               "armes).".format(label))
        if int(self.ch.tour_attaques) <= 0:
            return False, "Faites d'abord l'action Attaquer avec l'arme de la main principale."
        return True, ""

    # ------------------------------------------------------------------ bonus de dégâts des effets actifs
    def damage_riders(self) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """([(source, dés)] toujours ajoutés, [(source, dés)] conditionnels) — Faveur divine, Marque du chasseur…"""
        always, conditional = [], []
        for key in self.active_effect_keys():
            fx = FX.EFFECTS.get(key) or {}
            text = str((fx.get("mods") or {}).get("degats", ""))
            m = re.match(r"^\+\s*(\d*d\d+)", text)
            if not m:
                continue
            (conditional if "(" in text and ("cible" in norm(text) or "1/tour" in norm(text)) else always).append(
                (fx["nom"], m.group(1)))
        return always, conditional

    def weapon_damage_spec(self, slot: dict, offhand: bool = False, extra: str = "",
                           extra_label: str = "") -> Optional["D.DamageSpec"]:
        """Dégâts d'une arme équipée (prise, main secondaire, effets actifs) + dé supplémentaire éventuel
        (dé de supériorité, Attaque sournoise)."""
        st = self.weapon_stats(slot, offhand)
        if not st or not st.get("degats"):
            return None
        always, conditional = self.damage_riders()
        formula = st["degats"]
        notes = []
        for label, dice in always:
            formula += "+" + dice
            notes.append("{} : +{}".format(label, dice))
        if extra:
            formula += "+" + extra
            notes.append("{} : +{}".format(extra_label or "Bonus", extra))
        if offhand:
            notes.append(next((n for n in st["styles"] if n.startswith("Main secondaire")), ""))
        grip = " ({})".format(st["prise"]) if st.get("prise") else ""
        calc = st.get("calcul", "")
        dice_extra = [(label, dice) for label, dice in always] + ([(extra_label or "Bonus", extra)] if extra else [])
        if dice_extra:                                    # v46 : dés ajoutés dans le calcul détaillé
            head, _, tail = calc.partition(" = ")
            calc = "{}{} = {}".format(head, "".join(" + {} ({})".format(d, lab) for lab, d in dice_extra),
                                      re.sub(r"\s*([+-])\s*", r" \1 ", formula))
        spec = D.DamageSpec("Dégâts — " + st.get("affichage", st["nom"]) + grip +
                            (" (main secondaire)" if offhand else ""), formula, st.get("type_degats", ""),
                            " ; ".join(n for n in notes if n))
        spec.flat_labels = [(label, v) for label, v in st.get("bonus_degats", []) if v]
        spec.calcul = calc                                # affiché par la fenêtre de dés (v46)
        spec.options = list(conditional)
        return spec

    # ------------------------------------------------------------------ Maître de guerre : manœuvres
    def battle_master_level(self) -> int:
        e = self.ch.find_class("Guerrier")
        return e["niveau"] if e and e["niveau"] >= 3 and norm(e.get("sous_classe", "")) == "maitre de guerre" else 0

    def maneuver_option_set(self) -> Optional[dict]:
        lvl = self.battle_master_level()
        if not lvl:
            return None
        return {"key": "manoeuvres", "label": "Manœuvres (Maître de guerre)", "total": maneuvers_known(lvl),
                "options": dict(self.db.maneuvers), "chosen": list((self.ch.options_classe or {}).get("manoeuvres", []))}

    def maneuver_actions(self) -> list[dict]:
        lvl = self.battle_master_level()
        if not lvl:
            return []
        dc = self.maneuver_dc()
        out = []
        for name in (self.ch.options_classe or {}).get("manoeuvres", []):
            if name not in self.db.maneuvers:
                continue
            flow, kind = MANEUVER_FLOWS.get(name, ("de", "Spécial"))
            desc = self.db.maneuvers[name]
            weapon = flow in ("attaque", "precise", "riposte", "balayage", "attaque_lancer")
            die = self.class_action_formula({"degats": "{SUPERIORITE}"})
            formula = "{SUPERIORITE}"
            if flow == "parade":                          # réduction = dé + mod. de Dextérité
                formula = R.add_flat(die, self.mod("Dextérité"))
            elif flow == "ralliement":                    # PV temporaires de l'allié = dé + mod. de Charisme
                formula = R.add_flat(die, self.mod("Charisme"))
            out.append({"id": "manoeuvre:" + _slug(name), "nom": name, "icone": "🎯", "classe": "Guerrier",
                        "sous_classe": "Maître de guerre", "niveau": 3, "type": kind,
                        "cout": {"ressource": "superiorite", "n": 1}, "jet": "degats", "degats": formula,
                        "type_degats": "", "manoeuvre": name, "flux": flow,
                        "attaque_arme": weapon and kind in ("Action", "Réaction", "Action bonus"),
                        "description": "{} (DD {} : 8 + maîtrise + mod. de Force ou de Dextérité). Dépense 1 dé de "
                                       "supériorité.".format(desc, dc)})
        return out

    # ------------------------------------------------------------------ Roublard
    def sneak_attack_dice(self) -> str:
        rogue = self.class_level("Roublard")
        return "{}d6".format(max(1, math.ceil(rogue / 2))) if rogue else ""

    def sneak_weapon(self) -> Optional[dict]:
        """Arme utilisable pour l'Attaque sournoise : finesse (main principale ou secondaire) ou arme à distance."""
        for slot in (self.main_hand_slot(), self.ranged_slot(), self.off_hand_slot()):
            if slot is None:
                continue
            w = self.db.weapons.get(slot["nom"], {})
            if "finesse" in self._props(slot) or w.get("type") == "distance":
                return slot
        return None

    def cunning_actions_tiles(self, base: dict) -> list[dict]:
        return [dict(base, id="ruse_" + cid, nom="Action astucieuse : " + nom, icone=icone, effet=effect,
                     choix="", description="Action bonus : {} (Action astucieuse du roublard).".format(nom))
                for cid, nom, icone, effect in CUNNING]

    # ------------------------------------------------------------------ arme d'une action « attaque d'arme »
    def action_weapon_slot(self, a: dict) -> Optional[dict]:
        if a.get("id") == "sournoise":
            return self.sneak_weapon()
        if a.get("flux") == "attaque_lancer":
            slot = self.main_hand_slot()
            return slot if slot and "lancer" in self._props(slot) else None
        return self.main_hand_slot() or self.ranged_slot() or self.unarmed_slot()

    def per_turn_used(self, aid: str) -> bool:
        return aid in (self.ch.tour_utilises or [])

    def mark_per_turn(self, aid: str) -> None:
        self.ch.tour_utilises = list(dict.fromkeys(list(self.ch.tour_utilises or []) + [aid]))

    def weapon_action_specs(self, a: dict, die: str) -> tuple[Optional["D.RollSpec"], Optional["D.DamageSpec"]]:
        """Jet d'attaque et dégâts d'une action qui se résout par une attaque d'arme (manœuvre, Attaque sournoise)."""
        if a.get("naturelle"):                                      # arme naturelle (Forme de la bête…)
            dice, dtype = a["naturelle"]
            st_mod = self.mod("Force")
            fx = self.attack_mods()
            detail = [(R.mod_label("Force"), "{:+d}".format(st_mod)), ("Maîtrise", "{:+d}".format(self.prof))]
            attack = D.spec_from_detail(a["nom"], "attaque", detail + fx["detail"], fx["avantage"],
                                        fx["desavantage"], fx["echec"])
            flat = st_mod + (self.rage_damage_bonus() if "rage" in self.active_effect_keys() else 0)
            formula = R.add_flat(dice, flat) + ("+" + die if die else "")
            return attack, D.DamageSpec("Dégâts — " + a["nom"], formula, dtype)
        slot = self.action_weapon_slot(a)
        if slot is None:
            return None, None
        attack = self.weapon_attack_spec(slot)
        label = ("Attaque sournoise" if a.get("id") == "sournoise" else
                 "Dé de supériorité ({})".format(a["manoeuvre"]) if a.get("manoeuvre") else a["nom"])
        if a.get("flux") == "precise" and attack is not None:      # Attaque précise : le dé s'ajoute au d20
            attack.terms.append(D.Term(label, 0, "+" + die))
            dmg = self.weapon_damage_spec(slot)
        elif a.get("flux") == "balayage":                           # Balayage : le dé touche une seconde créature
            dmg = self.weapon_damage_spec(slot)
            if dmg is not None:
                dmg.note = (dmg.note + " ; " if dmg.note else "") + "Seconde créature à 1,50 m : {} dégâts".format(die)
        elif die and D.has_dice(die):
            dmg = self.weapon_damage_spec(slot, extra=die, extra_label=label)
        elif die:                                                   # bonus fixe (Marque inébranlable…)
            dmg = self.weapon_damage_spec(slot)
            if dmg is not None:
                dmg.formula = R.add_flat(dmg.formula, int(die)) if str(die).lstrip("-").isdigit() else dmg.formula
                dmg.note = (dmg.note + " ; " if dmg.note else "") + "{} : +{}".format(label, die)
        else:
            dmg = self.weapon_damage_spec(slot)
        if attack is not None:
            attack.title = "{} — {}".format(a["nom"], attack.title)
        return attack, dmg

    # ------------------------------------------------------------------ sorts : résolution
    def spell_resolution(self, name: str, slot_level: int = 0, class_name: str = "") -> Optional[dict]:
        """
        Comment résoudre un sort lancé au niveau `slot_level` :
        {mode: attaque | sauvegarde | automatique | soins | aucun, dd, carac, attaque (RollSpec), degats (DamageSpec),
         rayons, reussite, echec, niveau}.
        """
        spell = self.db.find_spell(name)
        if not spell:
            return None
        lvl = int(spell["niveau"])
        caster = self.caster(class_name) if class_name else None
        caster = caster or next((c for c in self.casters() if c["liste"] in spell.get("classes", [])), None) or \
            (self.casters()[0] if self.casters() else None)
        racial = next((r for r in self.racial_spells() if r["nom"] == spell["nom"]), None)
        dc = caster["dc"] if caster else (racial["dc"] if racial else None)
        test = spell.get("test", "")
        rays = 0
        if lvl == 0:
            st = self.cantrip_stats(spell["nom"]) or {}
            formula, heal, level = st.get("degats", ""), "", 0
            rays = st.get("rayons", 0)
            per_ray = st.get("degats_rayon", "")
        else:
            vals = self.spell_values(spell["nom"], slot_level, class_name) or {}
            formula, heal, level = vals.get("degats", ""), vals.get("soins", ""), vals.get("niveau", lvl)
            per_ray = ""
        dtype = spell.get("type_degats", "")
        title = "{}{}".format(spell["nom"], " (niveau {})".format(level) if level and level > lvl else "")
        dmg = D.DamageSpec("Dégâts — " + title, formula, dtype) if formula and D.has_dice(formula) else None
        heal_spec = D.DamageSpec("Soins — " + title, heal, "", "", "soins") if heal and D.has_dice(heal) else None
        desc = norm(spell.get("description", ""))
        out = {"nom": spell["nom"], "niveau": level, "dd": dc, "carac": "", "attaque": None, "degats": dmg,
               "soins": heal_spec, "rayons": rays, "rayon_degats": D.DamageSpec("Dégâts — " + spell["nom"] +
                                                                                  " (un rayon)", per_ray, dtype)
               if per_ray else None, "reussite": "", "echec": "", "mode": "aucun"}
        if test in ("A", "AC"):
            out["mode"] = "attaque"
            out["attaque"] = self.spell_attack_spec(spell["nom"], class_name, slot_level)
        elif test in ("For", "Dex", "Con", "Int", "Sag", "Cha"):
            out["mode"] = "sauvegarde"
            out["carac"] = R.ABBR_TO_FULL.get(norm(test)[:3], test)
            rule = spell.get("js_succes", "moitie" if lvl else "aucun")
            out["succes"] = rule                                   # moitie | aucun | toujours | texte
            noun = {"acide": "d'acide"}.get(dtype, "de " + dtype if dtype in ("feu", "froid", "foudre", "force",
                                                                               "tonnerre", "poison") else dtype)
            out["echec"] = "{} dégâts {}".format(formula, noun).strip() if formula else "Subit l'effet du sort."
            if not formula:
                out["reussite"] = "Aucun effet (ou effet réduit, voir la description)."
            elif rule == "moitie":
                out["reussite"] = "Moitié des dégâts (arrondie à l'inférieur)."
            elif rule == "aucun":
                out["reussite"] = "Aucun dégât."
            elif rule == "toujours":
                out["reussite"] = "Dégâts complets (le jet de sauvegarde n'évite que l'effet)."
            else:
                out["reussite"] = rule[:1].upper() + rule[1:] + "."
            out["ligne_js"] = "Jet de sauvegarde de {} : DD {}".format(out["carac"], dc) if dc else \
                "Jet de sauvegarde de {}".format(out["carac"])
        elif heal_spec is not None:
            out["mode"] = "soins"
        elif dmg is not None:
            out["mode"] = "automatique"
        return out
