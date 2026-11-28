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
from .features_2024 import sub_norm_of

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

    def unarmed_slot(self) -> dict:
        """Mains nues ; +1 au toucher et aux dégâts avec le Tatouage de la griffe occulte (v53)."""
        bonus = self.tattoo_unarmed_bonus() if hasattr(self, "tattoo_unarmed_bonus") else 0
        return {"nom": "Mains nues", "bonus": bonus, "maitrise": None}

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
        cls_always, cls_once = self.class_weapon_riders(slot)       # v52 : Frappes radiantes, Frappe divine…
        always, conditional = always + cls_always, conditional + cls_once + self.subclass_weapon_riders() + \
            self.subclass24_riders()
        item_always, item_cond = self.item_damage_riders(slot)       # v52 : Épée ardente, arme sur mesure…
        wtype = st.get("type_degats", "")
        parts = [(st["degats"], wtype)]
        formula = st["degats"]
        notes = [n for n in st.get("styles", []) if n.startswith(("Gantelets tonnants", "Armure parachevée"))]   # v53
        for label, dice in always:
            formula += "+" + dice
            notes.append("{} : +{}".format(label, dice))
            parts.append((dice, D.damage_type_in(label) or wtype))
        for label, dice, dtype in item_always:
            formula += "+" + dice
            notes.append(label)
            parts.append((dice, dtype or wtype))
            always = always + [(label.split(" : ")[0] + " ({})".format(dtype) if dtype else label, dice)]
        conditional = list(conditional) + [(label, dice) for label, dice, _t in item_cond]
        if extra:
            formula += "+" + extra
            notes.append("{} : +{}".format(extra_label or "Bonus", extra))
            parts.append((extra, D.damage_type_in(extra_label) or wtype))
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
        spec.parts = parts                                # v52 : total par type de dégâts après le jet
        return spec

    # ------------------------------------------------------------------ Maître de guerre : manœuvres
    def battle_master_level(self) -> int:
        e = self.ch.find_class("Guerrier")
        return e["niveau"] if e and e["niveau"] >= 3 and sub_norm_of(e) == "maitre de guerre" else 0

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
        if a.get("flux") == "pommeau":                              # v52 : talon d'une arme d'hast, 1d4 contondant
            st = self.weapon_stats(slot) or {}
            mod = self.mod(st.get("carac", "Force"))
            return attack, D.DamageSpec("Dégâts — talon de l'arme", R.add_flat("1d4", mod), "contondant")
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
        racial = next((r for r in self.racial_spells() if r["nom"] == spell["nom"]), None) or \
            self.feat_spell(spell["nom"])                # v52 : sort accordé par un don
        dc = caster["dc"] if caster else (racial["dc"] if racial else None)
        if getattr(self, "item_spell_override", None):   # v53 : sort lancé par un objet à DD fixe (tatouage)
            dc = self.item_spell_override["dd"]
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
        pool = self.hp_pool_spec(spell, slot_level)
        if pool is not None:                              # v52 : Sommeil, Couleurs dansantes (2014)
            out.update(mode="reserve", reserve=pool)
        return out

    # v52 : sorts 2014 qui affectent une réserve de PV (créatures par PV actuels croissants) : (dés, dés par niveau sup.)
    HP_POOL_SPELLS = {"sommeil": ("5d8", 2), "couleurs dansantes": ("6d10", 2)}

    def hp_pool_spec(self, spell: dict, slot_level: int = 0) -> Optional["D.DamageSpec"]:
        """Réserve de PV d'un sort 2014 (Sommeil : 5d8 + 2d8 par niveau d'emplacement au-delà du 1er)."""
        base = self.HP_POOL_SPELLS.get(norm(spell["nom"]))
        if base is None or " pv" not in " " + norm(spell.get("description", "")):   # Sommeil 2024 : un JS, pas de réserve
            return None
        dice, per = base
        n, faces = dice.split("d")
        lvl = int(spell["niveau"])
        up = max(0, int(slot_level or lvl) - lvl)
        formula = "{}d{}".format(int(n) + per * up, faces)
        title = "{} — PV de créatures affectés{}".format(spell["nom"], " (niveau {})".format(slot_level) if up else "")
        return D.DamageSpec(title, formula, "", "Les créatures sont affectées par ordre croissant de PV actuels, "
                            "tant que le total le permet (une créature n'est affectée que si ses PV n'excèdent pas "
                            "ce qui reste).", "reserve")


class OnHitMixin:
    """v52 — « Quand vous touchez » : bonus de dégâts à cocher avant de lancer les dégâts (rien n'est coché d'office :
    l'Attaque sournoise dépend de l'avantage ou d'un allié, le Châtiment se décide après avoir touché)."""

    _HIT_WORDS = ("quand vous touchez", "lorsque vous touchez", "si l'attaque touche", "quand l'attaque touche")

    def on_hit_options(self, slot: Optional[dict] = None, riders: Optional[list] = None,
                       crit: bool = False) -> list[dict]:
        """[{key, label, dice, cout, action, niveau}] proposés après un coup réussi (crit : effets d'un 20 naturel
        de l'arme magique, cochés d'office — v53)."""
        out = [{"key": "rider:{}".format(i), "label": label, "dice": dice, "cout": "", "action": "", "niveau": 0}
               for i, (label, dice) in enumerate(riders or [])]
        if crit and slot is not None:
            out += self.item_crit_options(slot)
        w = self.db.weapons.get((slot or {}).get("nom", ""), {}) if slot else {}
        props = self._props(slot) if slot else []
        acts = {a["id"]: a for a in self.class_actions()}
        sneak = acts.get("sournoise")
        if sneak and not self.per_turn_used("sournoise") and slot and ("finesse" in props or w.get("type") == "distance"):
            out.append({"key": "sournoise", "label": "Attaque sournoise (une fois par tour : avantage, ou allié à "
                        "1,50 m de la cible)", "dice": self.sneak_attack_dice(), "cout": "1 fois par tour",
                        "action": "sournoise_hit", "niveau": 0})
        smite_24_used = self.sheet_edition == 2024 and (self.ch.tour_bonus or self.per_turn_used("chatiment") or
                                                         self.per_turn_used("chatiment_gratuit"))
        if slot and w.get("type") == "cac" and not smite_24_used:     # 2024 : sort en action bonus, 1 par tour
            for aid in ("chatiment_gratuit", "chatiment"):
                a = acts.get(aid)
                if not a or not a.get("disponible"):
                    continue
                levels = [1] if aid == "chatiment_gratuit" else self.smite_levels()
                for lvl in levels:
                    out.append({"key": "{}:{}".format(aid, lvl), "label": "{} (niveau {})".format(a["nom"], lvl),
                                "dice": self.class_action_formula(a, lvl), "cout": "gratuit" if aid ==
                                "chatiment_gratuit" else "emplacement de niveau {}".format(lvl),
                                "action": aid, "niveau": lvl, "groupe": "chatiment"})
        out += self._extra_on_hit(slot, acts)            # v53 : manœuvres, psi, Tueur de colosses, Frappe divine…
        out += self.tattoo_on_hit(slot)                  # v53 : Tatouage de fureur sanglante
        seen = {"sournoise", "chatiment", "chatiment_gratuit", "manoeuvre", "manoeuvre_style", "psi_frappe",
                "cap:tueur_colosses"}
        for a in acts.values():
            if a["id"].startswith("manoeuvre:"):
                continue
            if a["id"] in seen or not a.get("disponible") or a.get("attaque_arme") or not a.get("formule"):
                continue
            if any(x in norm(a.get("description", "")) for x in self._HIT_WORDS) and D.has_dice(a["formule"]):
                out.append({"key": a["id"], "label": a["nom"], "dice": a["formule"],
                            "cout": self.class_action_state(a).get("cout_txt", ""), "action": a["id"], "niveau": 0})
        return out

    def _extra_on_hit(self, slot: Optional[dict], acts: dict) -> list[dict]:
        """v53 — bonus de dégâts au toucher absents jusque-là : manœuvres qui ajoutent le dé aux dégâts (une par
        coup, un dé de supériorité), Frappe psionique (un dé psi, une fois par tour), Tueur de colosses, Frappe
        divine (2014) / Frappes bénies (2024), Fureur divine (Zélote en rage), Marque du chasseur et Maléfice."""
        out = []
        if not slot:
            return out
        if slot.get("nom") == "Lance-foudre" and not self.per_turn_used("lance_foudre"):   # v53 : Infiltré
            out.append({"key": "lance_foudre", "label": "Lance-foudre — dégâts de foudre (une fois par tour)",
                        "dice": "1d6", "cout": "1 fois par tour", "action": "", "niveau": 0, "tour": "lance_foudre"})
        sup = next((t for t in self.resource_trackers() if t["key"] == "superiorite"), None)
        sup_left = sup is not None and (sup.get("total") or 0) - self.resource_used("superiorite") > 0
        for a in acts.values():                          # une action « manoeuvre:<nom> » par manœuvre choisie
            if not a["id"].startswith("manoeuvre:") or not sup_left or not a.get("formule"):
                continue
            desc = norm(self.db.maneuvers.get(a["nom"], a.get("description", "")))
            if "aux degats" in desc and "subit" not in desc.split("aux degats")[0][-40:]:
                out.append({"key": "man:" + a["nom"], "label": "Manœuvre : " + a["nom"], "dice": a["formule"],
                            "cout": "1 dé de supériorité", "action": a["id"], "niveau": 0, "groupe": "manoeuvre"})
        tech = acts.get("manoeuvre_style")
        if tech and tech.get("disponible") and "aux degats" in norm(self.db.maneuvers.get(self.ch.technique_manoeuvre, "")):
            out.append({"key": "man_style", "label": "Manœuvre : " + self.ch.technique_manoeuvre, "dice": "1d6",
                        "cout": "dé de Technique supérieure", "action": "manoeuvre_style", "niveau": 0,
                        "groupe": "manoeuvre"})
        psi = acts.get("psi_frappe")
        if psi and psi.get("disponible") and psi.get("formule") and not self.per_turn_used("psi_frappe"):
            out.append({"key": "psi_frappe", "label": "Frappe psionique", "dice": psi["formule"],
                        "cout": "1 dé psi, une fois par tour", "action": "psi_frappe", "niveau": 0, "tour": "psi_frappe"})
        col = acts.get("cap:tueur_colosses")
        if col and col.get("formule") and not self.per_turn_used("tueur_colosses"):
            out.append({"key": "tueur_colosses", "label": "Tueur de colosses (cible déjà blessée)", "dice": col["formule"],
                        "cout": "une fois par tour", "action": "", "niveau": 0, "tour": "tueur_colosses"})
        clerc = self.class_level("Clerc")
        passives = {norm(p["nom"]) for p in self.class_passives()}
        blessed = "Frappe divine" in ((self.ch.options_classe or {}).get("frappes_benies") or [])
        if clerc >= 8 and ("frappe divine" in passives or blessed) and not self.per_turn_used("frappe_divine"):
            out.append({"key": "frappe_divine", "label": "Frappe divine", "dice": "2d8" if clerc >= 14 else "1d8",
                        "cout": "une fois par tour", "action": "", "niveau": 0, "tour": "frappe_divine"})
        if "fureur divine" in passives and "rage" in self.ch.effets_actifs and not self.per_turn_used("fureur_divine"):
            out.append({"key": "fureur_divine", "label": "Fureur divine (radiants ou nécrotiques)",
                        "dice": "1d6+{}".format(self.class_level("Barbare") // 2), "cout": "premier coup du tour en rage",
                        "action": "", "niveau": 0, "tour": "fureur_divine"})
        conc = norm(re.sub(r"\s*\(2024\)$", "", self.ch.concentration or ""))
        if conc in ("marque du chasseur", "malefice"):
            out.append({"key": "conc:" + conc, "label": ("Marque du chasseur" if conc.startswith("marque") else
                                                         "Maléfice (nécrotiques)"), "dice": "1d6",
                        "cout": "sort de concentration actif", "action": "", "niveau": 0})
        return out

    def apply_on_hit(self, options: list[dict], chosen: list[str]) -> list[tuple[str, str]]:
        """Dépense les coûts des bonus choisis et renvoie [(libellé, dés)] à ajouter aux dégâts."""
        out, smite_done, man_done = [], False, False
        self.last_on_hit_temp = 0
        for o in options:
            if o["key"] not in chosen:
                continue
            if o.get("groupe") == "chatiment":
                if smite_done:                            # un seul Châtiment par coup
                    continue
                smite_done = True
            if o.get("groupe") == "manoeuvre":            # v53 : une seule manœuvre par coup
                if man_done:
                    continue
                man_done = True
            if o.get("charge_objet") is not None and not self.spend_item_charge(o["charge_objet"], 10):
                continue                                  # v53 : charge de l'objet (Fureur sanglante)
            if o.get("tour"):
                self.mark_per_turn(o["tour"])
            if o.get("pv_temp"):                          # v53 : Épée voleuse de vie, Cri du faucheur
                self.apply_temp_hp(int(o["pv_temp"]))
                self.last_on_hit_temp = int(o["pv_temp"])
            if o["key"].startswith("crit:") and not o.get("dice"):
                continue                                  # PV temporaires seuls (Cri du faucheur)
            if o["action"] == "sournoise_hit":
                self.mark_per_turn("sournoise")
            elif o["action"]:
                res = self.use_class_action(o["action"], o.get("niveau") or 0)
                if not res.get("ok"):
                    continue
                if o.get("groupe") == "chatiment" and self.sheet_edition == 2024:
                    self.ch.tour_bonus = True                # Châtiment divin 2024 : action bonus
            out.append((o["label"].split(" (")[0], o["dice"]))
        if smite_done and SMITE_UNDEAD in chosen:          # v53 : +1d8 contre un fiélon ou un mort-vivant
            out.append(("Châtiment divin — fiélon ou mort-vivant", "1d8"))
        return out


SMITE_UNDEAD = "chatiment:fielon_mort_vivant"            # case de la fenêtre « touche ? » (Châtiment divin)

MASTERY_EFFECTS = {
    "Coup double": "Coup double : l'attaque supplémentaire de l'arme légère fait partie de l'action Attaquer (pas "
                   "d'action bonus), une fois par tour.",
    "Entaille": "Entaille : attaquez une seconde créature à 1,50 m de la première (dégâts sans le modificateur), "
                "une fois par tour.",
    "Ouverture": "Ouverture : vous avez l'avantage à votre prochaine attaque contre cette créature avant la fin de "
                 "votre prochain tour.",
    "Poussée": "Poussée : repoussez la cible (taille G ou moins) de 3 m en ligne droite.",
    "Ralentissement": "Ralentissement : la vitesse de la cible baisse de 3 m jusqu'au début de votre prochain tour.",
    "Renversement": "Renversement : JS de Constitution DD {dd} ou la cible tombe à terre.",
    "Sape": "Sape : la cible a le désavantage à son prochain jet d'attaque avant le début de votre prochain tour.",
}


class MasteryFlowMixin:
    """v52 — bottes d'arme appliquées dans le déroulé d'attaque (rappel au toucher, Effleurement sur un raté)."""

    def mastery_on_hit(self, slot: Optional[dict]) -> str:
        st = self.weapon_stats(slot) if slot else None
        botte = (st or {}).get("botte", "")
        if not botte or botte == "Effleurement":
            return ""
        text = MASTERY_EFFECTS.get(botte, "")
        if "{dd}" in text:
            text = text.format(dd=8 + self.prof + self.mod(st["carac"]))
        return "Botte d'arme — " + text if text else ""

    def mastery_on_miss(self, slot: Optional[dict]) -> str:
        st = self.weapon_stats(slot) if slot else None
        if (st or {}).get("botte") != "Effleurement":
            return ""
        dmg = max(0, self.mod(st["carac"]))
        return ("Botte d'arme — Effleurement : la cible subit quand même {} dégâts {} (modificateur de {})."
                .format(dmg, st.get("type_degats", ""), st["carac"])) if dmg else ""
