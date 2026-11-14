"""
Tour de combat (v30, inspiré de la barre d'action de Baldur's Gate 3) — logique pure.

    - `turn_actions()` : TOUT ce qui est jouable ce tour, réuni en tuiles typées Action / Action bonus / Réaction /
      Gratuit — armes équipées, sorts (mineurs, préparés ou connus, raciaux, accordés), actions de classe et de race,
      réactions, actions communes (Foncer, Se désengager, Esquiver, Aider, Se cacher, Bousculer, Saisir,
      Utiliser un objet, Interagir) ;
    - suivi du tour : action, action bonus, réaction (déjà suivie) et mètres de déplacement consommés ;
      « Nouveau round » remet tout à zéro ;
    - réactions programmables : Demander (par défaut) / Automatique (réaction par défaut, en tête) / Désactivée
      (masquée des tuiles, grisée dans l'encart Réactions).
Une tuile utilisée dépense l'élément d'économie d'action correspondant ; elle est grisée s'il est déjà dépensé
ou si sa ressource (emplacement, sphère) est épuisée.
"""
from __future__ import annotations

import re
from typing import Optional

from . import dice as D
from . import rules as R
from .rules import norm
from .data_loader import SAVE_TESTS, save_success_text

ECONOMY = ("Action", "Action bonus", "Réaction", "Gratuit")
REACTION_MODES = {"demander": "Demander", "auto": "Automatique", "off": "Désactivée"}

COMMON_ACTIONS = [
    ("foncer", "Foncer", "🏃", "Action", "foncer",
     "Déplacement supplémentaire égal à votre vitesse pour ce tour."),
    ("desengager", "Se désengager", "↩️", "Action", "desengagement",
     "Votre déplacement ne provoque pas d'attaque d'opportunité jusqu'à la fin du tour."),
    ("esquiver", "Esquiver", "🤺", "Action", "esquive",
     "Jusqu'au début de votre prochain tour : désavantage aux attaques contre vous (si vous voyez l'attaquant), "
     "avantage à vos jets de sauvegarde de Dextérité."),
    ("aider", "Aider", "🤝", "Action", "",
     "Un allié a l'avantage à son prochain test pour la tâche que vous l'aidez à accomplir, ou à sa prochaine "
     "attaque contre une créature à 1,50 m de vous."),
    ("cacher", "Se cacher", "🫥", "Action", "cache", "Test de Dextérité (Discrétion) pour devenir caché."),
    ("bousculer", "Bousculer", "💥", "Action", "",
     "Remplace une attaque : test de Force (Athlétisme) contre Athlétisme ou Acrobaties de la cible — la faire "
     "tomber à terre ou la repousser de 1,50 m."),
    ("saisir", "Saisir", "✊", "Action", "",
     "Remplace une attaque : test de Force (Athlétisme) contre Athlétisme ou Acrobaties de la cible — elle est "
     "agrippée."),
    ("objet", "Utiliser un objet", "🧪", "Action", "",
     "Utiliser un objet qui demande une action — dont administrer une potion à un allié (même inconscient)."),
    ("chercher", "Chercher", "🔎", "Action", "", "Test de Sagesse (Perception) ou d'Intelligence (Investigation)."),
    ("interagir", "Interagir", "🚪", "Gratuit", "",
     "Une interaction gratuite par tour : ouvrir une porte, dégainer une arme, ramasser un objet."),
    ("parler", "Parler", "💬", "Gratuit", "", "Quelques mots pendant votre tour."),
]


def spell_economy(spell: dict) -> str:
    """Temps d'incantation -> type d'action ('' si plus long qu'une action : hors combat)."""
    t = norm(spell.get("temps", ""))
    if "reaction" in t:
        return "Réaction"
    if "bonus" in t:
        return "Action bonus"
    if re.match(r"^1 action\b", t) or t == "action":
        return "Action"
    return ""


def class_economy(kind: str) -> str:
    return kind if kind in ("Action", "Action bonus", "Réaction") else "Gratuit"


class TurnMixin:
    """Mélangé à Engine."""

    # ------------------------------------------------------------------ économie du tour
    def turn_state(self) -> dict:
        speed = self.speed() * (2 if "foncer" in self.ch.effets_actifs else 1)    # Foncer : vitesse doublée
        return {"Action": bool(self.ch.tour_action), "Action bonus": bool(self.ch.tour_bonus),
                "Réaction": bool(self.ch.reaction_utilisee), "Gratuit": False,
                "deplacement": float(self.ch.tour_deplacement), "vitesse": speed}

    def spend_economy(self, kind: str, key: str = "") -> None:
        if kind == "Action":
            self.ch.tour_action = True
        elif kind == "Action bonus":
            self.ch.tour_bonus = True
        elif kind == "Réaction":
            self.ch.reaction_utilisee = self.ch.reaction_utilisee or key or "reaction"

    def toggle_economy(self, kind: str) -> None:
        """Clic sur un voyant du pied de tour : bascule consommé / disponible (correction manuelle)."""
        if kind == "Action":
            self.ch.tour_action = not self.ch.tour_action
        elif kind == "Action bonus":
            self.ch.tour_bonus = not self.ch.tour_bonus
        elif kind == "Réaction":
            self.ch.reaction_utilisee = "" if self.ch.reaction_utilisee else "reaction"

    def set_movement(self, meters: float) -> None:
        self.ch.tour_deplacement = max(0.0, float(meters))

    def new_turn(self) -> None:
        """Nouveau round : action, action bonus, réaction et déplacement à nouveau disponibles."""
        self.new_round()

    def attacks_per_action(self) -> int:
        """Attaques par action Attaquer : Attaque supplémentaire (Guerrier 5 / 11 / 20, autres classes 5)."""
        best = 1
        ftr = self.class_level("Guerrier")
        if ftr:
            best = 1 + (ftr >= 5) + (ftr >= 11) + (ftr >= 20)
        if best < 2 and any(n.startswith("attaque supplementaire") for n in self.unlocked_feature_names()):
            best = 2
        if best < 2 and self.thirsting_blade():           # manifestation « Lame assoiffée » (arme de pacte)
            best = 2
        return best

    # ------------------------------------------------------------------ réactions programmables
    def reaction_programmable(self, key: str) -> bool:
        """v40 : plus de réglage Demander / Automatique / Désactivée — chaque réaction est une simple tuile cliquable,
        utilisable une fois par round (elle consomme la réaction du personnage)."""
        return False

    def reaction_mode(self, key: str) -> str:
        return "demander"

    def set_reaction_mode(self, key: str, mode: str) -> None:
        """Conservé pour les anciennes sauvegardes : sans effet depuis la v40."""
        return
        if mode not in REACTION_MODES or not self.reaction_programmable(key):
            return
        modes = dict(self.ch.modes_reactions or {})
        if mode == "demander":
            modes.pop(key, None)
        else:
            if mode == "auto":                           # une seule réaction par défaut à la fois
                modes = {k: v for k, v in modes.items() if v != "auto"}
            modes[key] = mode
        self.ch.modes_reactions = modes

    def auto_reaction(self) -> Optional[dict]:
        return next((r for r in self.reactions() if self.reaction_mode(r["cle"]) == "auto"), None)

    # ------------------------------------------------------------------ tuiles
    def turn_actions(self) -> list[dict]:
        out: list[dict] = []
        state = self.turn_state()

        def tile(tid, nom, icone, kind, origine, desc, ok=True, why="", cost="", ref=None):
            used = state.get(kind) if kind != "Gratuit" else False
            if ok and used:
                ok, why = False, "{} déjà utilisée ce tour.".format("Réaction" if kind == "Réaction" else kind)
            out.append({"id": tid, "nom": nom, "icone": icone, "type": kind, "origine": origine,
                        "description": desc, "disponible": ok, "raison": why, "cout": cost, "ref": ref or {}})

        # armes équipées : l'action Attaquer permet plusieurs attaques (Attaque supplémentaire)
        n_att, done = self.attacks_per_action(), int(self.ch.tour_attaques)
        attack_open = not self.ch.tour_action or 0 < done < n_att
        why_attack = "" if attack_open else ("Toutes les attaques de l'action Attaquer sont faites." if done
                                             else "Action déjà utilisée ce tour.")
        count_txt = " — attaque {} / {}".format(min(done + 1, n_att), n_att) if n_att > 1 else ""
        beast_form = bool(self.ch.forme_active)            # v45 : sous forme animale, les armes sont inutilisables
        for key, label in (("armes_cac", "corps à corps"), ("armes_distance", "distance")):
            for i, slot in enumerate(getattr(self.ch, key) if not beast_form else []):
                if not slot.get("nom") or (key == "armes_cac" and i == 1):
                    continue                              # main secondaire : tuile d'action bonus dédiée
                st = self.weapon_stats(slot)
                if not st:
                    continue
                hand = " (main principale)" if key == "armes_cac" and i == 0 else ""
                grip = " ({})".format(st["prise"]) if st.get("prise") else ""     # v46 : prise automatique
                unprof = not st["maitrise"] and st["nom"] != "Mains nues"     # v43 : sans bonus de maîtrise
                out.append({"id": "arme:{}:{}".format(key, i),
                            "nom": ("⚠ " if unprof else "") + "Attaque — " + st.get("affichage", st["nom"]) + grip
                                   + hand,
                            "icone": "⚔" if key == "armes_cac" else "🏹", "type": "Action",
                            "origine": "arme ({}){}".format(label, count_txt),
                            "description": "Jet de toucher {} ; si l'attaque touche : {} {}.\nCalcul des dégâts : "
                                           "{}{}".format(R.fmt_bonus(st["attaque"]), st["degats"],
                                                         st["type_degats"], st.get("calcul", ""),
                                                                "\n⚠ Arme non maîtrisée : Le bonus de maîtrise ne "
                                                                "s'applique pas au jet de toucher." if unprof else ""),
                            "disponible": attack_open, "raison": why_attack, "cout": "",
                            "ref": {"slot": key, "index": i}})
        if beast_form:                                     # v45 : attaques de la bête (forme sauvage / Métamorphose)
            beast = self.wild_form()
            poly = self.ch.forme_type == "metamorphose"
            for i, a in enumerate(self.beast_attacks()):
                out.append({"id": "bete:{}".format(i), "nom": "{} — {}".format(a["nom"], self.ch.forme_active),
                            "icone": "🦋" if poly else "🐾", "type": "Action",
                            "origine": "{} ({}){}".format("Métamorphose" if poly else "Forme sauvage",
                                                          self.ch.forme_active, count_txt),
                            "description": "Attaque de la bête : jet de toucher {} ; si l'attaque touche : {} {} — "
                                           "portée {}.{}".format(R.fmt_bonus(a["attaque"]), a["degats"], a["type"],
                                                                a["portee"], "\nTraits : " + " ; ".join(
                                                                    t.split(".")[0] for t in beast.get("traits", [])[:4])
                                                                if beast and beast.get("traits") else ""),
                            "disponible": attack_open, "raison": why_attack, "cout": "", "ref": {"bete": i}})
        if not beast_form and self.main_hand_slot() is None:   # main principale vide : attaque à mains nues
            st = self.weapon_stats(self.unarmed_slot())
            if st:
                out.append({"id": "arme:mains_nues", "nom": "Attaque à mains nues", "icone": "👊", "type": "Action",
                            "origine": "arme (corps à corps){}".format(count_txt),
                            "description": "Aucune arme en main principale. Jet de toucher {} ; dégâts {} {}.".format(
                                R.fmt_bonus(st["attaque"]), st["degats"], st["type_degats"]),
                            "disponible": attack_open, "raison": why_attack, "cout": "", "ref": {"mains_nues": True}})
        off = self.off_hand_slot() if not beast_form else None
        if off is not None:                                # combat à deux armes : action bonus
            st = self.weapon_stats(off, offhand=True)
            ok, why = self.offhand_status()
            if ok and state["Action bonus"]:
                ok, why = False, "Action bonus déjà utilisée ce tour."
            if st:
                out.append({"id": "arme:main_secondaire", "nom": "Attaque en main secondaire — " +
                            st.get("affichage", st["nom"]),
                            "icone": "🗡", "type": "Action bonus", "origine": "combat à deux armes",
                            "description": "Jet de toucher {} distinct ; dégâts {} {} (calcul : {}) — {}.".format(
                                R.fmt_bonus(st["attaque"]), st["degats"], st["type_degats"], st.get("calcul", ""),
                                "modificateur ajouté (style Combat à deux armes)" if self.style_active(
                                    "Combat à deux armes") else "sans modificateur de caractéristique (sauf s'il est "
                                                                "négatif)"),
                            "disponible": ok, "raison": why, "cout": "", "ref": {"main_secondaire": True}})
        # sorts
        blocked = self.spells_blocked()
        free = self.smite_levels()
        seen = set()
        for name in self.known_spell_names() + [s["nom"] for s in self.ch.sorts_mineurs if s.get("nom")]:
            spell = self.db.find_spell(name)
            if not spell or spell["nom"] in seen:
                continue
            seen.add(spell["nom"])
            kind = spell_economy(spell)
            if not kind:
                continue
            lvl = int(spell.get("niveau") or 0)
            racial = any(r["nom"] == spell["nom"] for r in self.racial_spells())
            grants = [g for g in self.granted_spells() if g["nom"] == spell["nom"]]
            known_normally = self.knows_spell(spell["nom"])
            granted = bool(grants) and not known_normally
            free_grant = next((g for g in grants if not g.get("emplacement")), None)
            needs_slot = lvl > 0 and not racial and (free_grant is None or known_normally)
            grant = free_grant or (grants[0] if grants else None)
            limit_key = grant.get("cle", "") if grant and not known_normally else ""
            if not needs_slot and grants and all(g.get("rituel_seul") for g in grants):
                continue                                  # Livre des secrets anciens : rituel hors combat
            ok, why = True, ""
            if blocked:
                ok, why = False, (self.spell_block_reason() or ("", "Sorts impossibles."))[1]
            elif needs_slot and not any(x >= lvl for x in free):
                ok, why = False, "Plus d'emplacement de niveau {} ou plus.".format(lvl)
            elif limit_key and not self.granted_limit_left(limit_key):
                ok, why = False, "Déjà utilisé — récupéré au repos long."
            eff = self.default_slot_level(spell["nom"]) if lvl and needs_slot else lvl
            origin = ("sort mineur" if lvl == 0 else "sort niv. {}".format(lvl) + (
                " ⇒ {}".format(eff) if eff > lvl else "")) + (" [Sort Racial]" if racial and not known_normally
                                                             else " (accordé)" if granted else "")
            desc = (spell.get("description") or "")[:400]
            if lvl:                                       # niveau effectif : surclassement d'office (pacte)
                vals = self.spell_values(spell["nom"], eff) or {}
                text, _ = R.describe_at(spell, eff)
                parts = []
                if vals.get("degats"):
                    parts.append("Dégâts : {} {}".format(vals["degats"], vals.get("type_degats", "")).strip())
                if vals.get("soins"):
                    parts.append("Soins : {} PV".format(vals["soins"]))
                if vals.get("pv_temp"):
                    parts.append("PV temporaires : {}".format(vals["pv_temp"]))
                head = "Niveau {}{} — ".format(eff, " (Magie des pactes)" if vals.get("pacte") else "") \
                    if eff > lvl else ""
                desc = head + (" — ".join(parts) + "\n" if parts else "") + text[:400]
                save = self.spell_resolution(spell["nom"], eff) if spell.get("test") in SAVE_TESTS else None
                if save and save.get("ligne_js"):           # v40 : JS de la cible et effet d'une réussite
                    desc += "\n{} — {}".format(save["ligne_js"], save_success_text(spell))
            if lvl == 0:                                  # sort mineur : valeurs calculées (rayons, manifestations)
                st = self.cantrip_stats(spell["nom"]) or {}
                if st.get("degats"):
                    desc = "{} — {} {} — portée {}{}".format(
                        st["test"], st["degats"], st["type_degats"], st["portee"],
                        "".join("\n• " + e for e in st.get("effets", [])))
                    if st.get("rayons"):
                        desc = "{} rayon{} — ".format(st["rayons"], "s" * (st["rayons"] > 1)) + desc
                    if spell.get("test") in SAVE_TESTS:
                        desc += "\n" + save_success_text(spell)
            tile("sort:" + spell["nom"], spell["nom"], "✦" if lvl else "✧", kind, origin, desc, ok, why,
                 ("emplacement de Pacte niv. {}".format(eff) if eff > lvl and eff == self.pact()[1]
                  else "emplacement niv. {}+".format(lvl)) if needs_slot else "", ref={"sort": spell["nom"], "niveau": lvl,
                                                                               "emplacement": needs_slot,
                                                                               "limite": limit_key,
                                                                               "niveau_effectif": eff})
        # actions de classe et de race
        for a in self.class_actions():
            kind = class_economy(a.get("type", ""))
            origin = {"race": "race", "manifestation": "manifestation"}.get(a.get("origine", ""), "classe")
            if a.get("attaque_arme") and kind == "Action":   # manœuvre offensive, Attaque sournoise : une attaque
                ok, why = a["disponible"], a.get("raison", "")
                if ok and not attack_open:
                    ok, why = False, why_attack
                out.append({"id": "classe:" + a["id"], "nom": a["nom"], "icone": a.get("icone", "⚔"), "type": kind,
                            "origine": origin + " — attaque d'arme" + count_txt, "description": a.get("description", ""),
                            "disponible": ok, "raison": why, "cout": a.get("cout_txt", ""), "ref": {"action": a["id"]}})
                continue
            tile("classe:" + a["id"], a["nom"], a.get("icone", "⚔"), kind, origin, a.get("description", ""),
                 a["disponible"] or bool(a.get("actif")), a.get("raison", ""), a.get("cout_txt", ""),
                 ref={"action": a["id"]})
        # réactions (attaque d'opportunité, sorts de réaction déjà listés, aptitudes, dons, styles)
        names = {norm(t["nom"]) for t in out}
        auto = self.auto_reaction()
        for r in self.reactions():
            mode = self.reaction_mode(r["cle"])
            if mode == "off" or norm(r["nom"]) in names:
                continue
            tile("reaction:" + r["cle"], ("★ " if auto and auto["cle"] == r["cle"] else "") + r["nom"],
                 r.get("icone", "⚡"), "Réaction", "réaction ({})".format(r.get("source", "")),
                 "Déclencheur : {}\nEffet : {}".format(r.get("declencheur", ""), r.get("effet", "")),
                 ref={"reaction": r["cle"]})
        # sorts de réaction désactivés : retirés aussi
        out = [t for t in out if not (t["type"] == "Réaction" and t["id"].startswith("sort:") and
                                      self.reaction_mode("sort:" + t["nom"]) == "off")]
        # actions communes
        for cid, nom, icone, kind, _effect, desc in COMMON_ACTIONS:
            tile("commune:" + cid, nom, icone, kind, "action commune", desc)
        # v45 — capacités activables des objets magiques équipés : badge « [Objet Magique : Nom] »
        for p in self.magic_item_powers():
            entry = self.ch.objets_magiques[p["entree"]]
            left = self.item_charges_left(entry, p["charges"]) if p["charges"] else None
            ok, why = True, ""
            if p["cout"] and left is not None and left < p["cout"]:
                ok, why = False, "Plus assez de charges ({} / {}) — rechargées au repos long.".format(left, p["charges"])
            elif p["sort"] and blocked:
                ok, why = False, (self.spell_block_reason() or ("", "Sorts impossibles."))[1]
            charge_txt = " — charges {} / {}".format(left, p["charges"]) if left is not None else ""
            tile(p["id"], p["nom"], "✨", p["type"], "[Objet Magique : {}]{}".format(p["objet"], charge_txt),
                 p["description"][:500], ok, why, "{} charge(s)".format(p["cout"]) if p["cout"] else "",
                 ref={"pouvoir": p["id"]})
        # v40 — règle optionnelle : boire soi-même une potion de son inventaire par une action bonus
        drinks = self.drinkable_potions()
        tile("potion:boire", "Boire une potion (Action bonus)", "🧪", "Action bonus", "règle optionnelle",
             "Vous buvez vous-même une potion de votre inventaire ({}). Administrer une potion à un allié reste une "
             "action (« Utiliser un objet »).".format(", ".join("{} ×{}".format(p["nom"], p["qte"]) for p in drinks)
                                                       if drinks else "aucune potion"),
             bool(drinks), "" if drinks else "Aucune potion dans l'inventaire.", "1 potion")
        order = {k: i for i, k in enumerate(ECONOMY)}
        actions = {a["id"]: a for a in self.class_actions()}
        for t in out:                                     # v41 : groupe d'affichage de l'onglet Combat
            t["groupe"] = self.tile_group(t, actions)
        auto_first = [t for t in out if t["nom"].startswith("★ ")]
        rest = [t for t in out if not t["nom"].startswith("★ ")]
        return auto_first + sorted(rest, key=lambda t: order.get(t["type"], 9))

    @staticmethod
    def tile_group(t: dict, actions: dict) -> str:
        """
        Groupe d'une tuile (v41) : « attaques » (armes, main secondaire, Attaque sournoise, manœuvres, capacités qui
        infligent des dégâts), « magie » (sorts, métamagie, manifestations), « reactions » (tout ce qui consomme la
        réaction), « generiques » (Foncer, Esquiver…, potion, Action astucieuse) et « capacites » (aptitudes de
        classe et de race sans jet d'attaque : Rage, Second souffle… — affichées sous les actions génériques).
        """
        tid = t["id"]
        if t["type"] == "Réaction":
            return "reactions"
        if tid.startswith(("arme:", "bete:")):
            return "attaques"
        if tid.startswith("objet:"):
            return "objets"
        if tid.startswith("sort:"):
            return "magie"
        if tid.startswith(("commune:", "potion:")):
            return "generiques"
        if tid.startswith("classe:"):
            a = actions.get(tid[7:], {})
            aid = a.get("id", tid[7:])
            if aid.startswith("ruse"):
                return "generiques"
            if aid.startswith("meta:") or a.get("origine") == "manifestation" and not a.get("degats"):
                return "magie"
            if (a.get("attaque_arme") or a.get("naturelle") or a.get("flux") or a.get("jet") == "attaque_mains_nues"
                    or (a.get("degats") and a.get("type_degats") and not a.get("soin"))
                    or aid in ("sournoise", "chatiment")):
                return "attaques"
            if a.get("origine") == "manifestation":
                return "magie"
        return "capacites"

    def turn_counts(self) -> dict:
        counts = {k: 0 for k in ECONOMY}
        for t in self.turn_actions():
            counts[t["type"]] = counts.get(t["type"], 0) + 1
        return counts

    # ------------------------------------------------------------------ utilisation d'une tuile
    def use_turn_action(self, tile_id: str) -> dict:
        """Dépense l'économie d'action et renvoie ce qu'il faut animer :
        {ok, message, attaque (RollSpec|None), degats (DamageSpec|None), soin, sort (nom à lancer via l'onglet Magie)}."""
        t = next((x for x in self.turn_actions() if x["id"] == tile_id), None)
        res = {"ok": False, "message": "", "attaque": None, "degats": None, "soin": False, "sort": ""}
        if t is None:
            res["message"] = "Action indisponible."
            return res
        if not t["disponible"]:
            res["message"] = "{} : {}".format(t["nom"], t["raison"])
            return res
        kind, ref = t["type"], t["ref"]
        if tile_id == "arme:main_secondaire":            # combat à deux armes : action bonus, d20 distinct
            slot = self.off_hand_slot()
            self.spend_economy("Action bonus")
            spec = self.weapon_attack_spec(slot)
            if spec is not None:
                spec.title = "Main secondaire — " + spec.title
            res.update(ok=True, attaque=spec, degats=self.weapon_damage_spec(slot, offhand=True),
                       message="{} : attaque (action bonus).".format(t["nom"]))
        elif tile_id.startswith("arme:"):
            slot = self.unarmed_slot() if ref.get("mains_nues") else getattr(self.ch, ref["slot"])[ref["index"]]
            self.ch.tour_attaques = int(self.ch.tour_attaques) + 1
            self.spend_economy(kind)
            n = self.attacks_per_action()
            res["degats"] = self.weapon_damage_spec(slot)
            res.update(ok=True, attaque=self.weapon_attack_spec(slot), message="{} : attaque {} / {}.".format(
                t["nom"], self.ch.tour_attaques, n) if n > 1 else "{} : attaque.".format(t["nom"]))
        elif tile_id.startswith("bete:"):                 # v45 : attaque de la bête
            attacks = self.beast_attacks()
            a = attacks[ref["bete"]] if ref["bete"] < len(attacks) else None
            if a is None:
                res["message"] = "Attaque de la bête indisponible."
                return res
            self.ch.tour_attaques = int(self.ch.tour_attaques) + 1
            self.spend_economy(kind)
            res.update(ok=True, attaque=self.beast_attack_spec(a),
                       degats=D.DamageSpec("{} — {}".format(self.ch.forme_active, a["nom"]), a["degats"], a["type"]),
                       message="{} : attaque.".format(t["nom"]))
        elif tile_id.startswith("objet:"):                # v45 : capacité d'un objet magique
            out = self.use_item_power(ref["pouvoir"])
            if out["ok"]:
                self.spend_economy(kind)
            res.update(ok=out["ok"], message=out["message"], objet=out if out["ok"] else None,
                       objet_sort=out.get("sort", ""), objet_niveau=out.get("niveau", 0))
        elif tile_id.startswith("sort:"):
            res.update(ok=True, sort=ref["sort"], message="{} : lancement.".format(t["nom"]),
                       emplacement=ref.get("emplacement", True), limite=ref.get("limite", ""),
                       niveau_effectif=ref.get("niveau_effectif", 0))
            self.spend_economy(kind, "sort:" + ref["sort"])   # l'emplacement est dépensé par le lancement
        elif tile_id.startswith("classe:"):
            out = self.use_class_action(ref["action"])
            res.update(ok=out["ok"], message=out["message"], attaque=out.get("attaque"), degats=out.get("degats"),
                       soin=out.get("soin", False))
            if out["ok"] and kind != "Réaction":            # la réaction est déjà synchronisée par use_class_action
                self.spend_economy(kind)
        elif tile_id.startswith("reaction:"):
            self.ch.reaction_utilisee = ref["reaction"]
            res.update(ok=True, message="{} : réaction du round utilisée.".format(t["nom"].lstrip("★ ")))
        elif tile_id == "potion:boire":                    # le choix et l'effet de la potion se font dans l'interface
            self.spend_economy("Action bonus")
            res.update(ok=True, potion=True, message="Boire une potion : action bonus.")
        elif tile_id.startswith("commune:"):
            effect = next((c[4] for c in COMMON_ACTIONS if "commune:" + c[0] == tile_id), "")
            if effect:
                self.add_effect(effect)
            self.spend_economy(kind)
            res.update(ok=True, message="{}{}.".format(t["nom"], " — effet actif" if effect else ""))
        return res

    def drinkable_potions(self) -> list[dict]:
        """Potions, élixirs, philtres et antitoxines de l'inventaire (les huiles s'appliquent, elles ne se boivent pas)."""
        return [c for c in self.consumables() if not norm(c["nom"]).startswith("huile")]

    def use_auto_reaction(self) -> dict:
        r = self.auto_reaction()
        if r is None:
            return {"ok": False, "message": "Aucune réaction réglée sur « Automatique »."}
        if self.ch.reaction_utilisee:
            return {"ok": False, "message": "Réaction déjà utilisée ce round."}
        self.ch.reaction_utilisee = r["cle"]
        return {"ok": True, "message": "{} : réaction du round utilisée.".format(r["nom"])}
