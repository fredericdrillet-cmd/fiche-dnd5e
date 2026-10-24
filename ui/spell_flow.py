"""
Résolution d'un sort depuis le Combat ou l'onglet Magie (v39), en trois temps :

    1. niveau d'emplacement : fenêtre de choix (niveau de base et niveaux supérieurs disponibles, dégâts recalculés
       pour chacun) ; un seul niveau possible (Magie des pactes) -> choisi d'office ;
    2. lancement (dépense de l'emplacement, concentration, effets) par `MagicTab.cast` ;
    3. résolution : attaque de sort (d20 -> « L'attaque touche-t-elle ? » -> dégâts ; un jet par rayon pour
       Décharge occulte), jet de sauvegarde (fenêtre du DD, effets en cas d'échec / de réussite, puis dégâts),
       dégâts automatiques (Projectile magique) ou soins (appliqués à vous ou à un allié).
"""
from __future__ import annotations

from typing import Callable, Optional

from core.rules import norm
from .dialogs import ask_choice, ask_yes_no
from .dice_dialog import roll_damage_dialog


def slot_choices(engine, spell: dict, class_name: str = "") -> list[tuple[int, str]]:
    """[(niveau, libellé)] des emplacements disponibles, le niveau par défaut (pacte compris) en premier."""
    base = int(spell.get("niveau") or 0)
    levels = engine.slot_levels_from(base)
    default = engine.default_slot_level(spell["nom"], class_name)
    levels = sorted(levels, key=lambda lvl: (lvl != default, lvl))
    count, plvl = engine.pact()
    out = []
    for lvl in levels:
        vals = engine.spell_values(spell["nom"], lvl, class_name) or {}
        what = ("dégâts {} {}".format(vals["degats"], vals.get("type_degats", "")).strip() if vals.get("degats") else
                "soins {}".format(vals["soins"]) if vals.get("soins") else "")
        pact = " (emplacement de Pacte)" if count and lvl == plvl else ""
        label = "Niveau {}{}{}{}".format(lvl, pact, " — sort de base" if lvl == base else " — surclassé",
                                         " — " + what if what else "")
        out.append((lvl, label))
    return out


def choose_slot_level(win, engine, spell: dict, class_name: str = "") -> Optional[int]:
    """Fenêtre de choix du niveau d'emplacement ; None si annulé ou plus aucun emplacement."""
    choices = slot_choices(engine, spell, class_name)
    if not choices:
        win.statusBar().showMessage("Aucun emplacement de niveau {} ou plus disponible.".format(spell["niveau"]), 6000)
        return None
    if len(choices) == 1:
        return choices[0][0]
    labels = {label: lvl for lvl, label in choices}
    picked = ask_choice(win, "Lancer {} — niveau d'emplacement".format(spell["nom"]),
                        "Choisissez le niveau de l'emplacement à dépenser (les dégâts et effets sont recalculés) :",
                        list(labels))
    return labels.get(picked) if picked else None


def resolve_spell(win, engine, name: str, level: int, class_name: str = "",
                  attack_flow: Optional[Callable] = None) -> str:
    """Jets du sort lancé au niveau `level`. Renvoie le mode de résolution (attaque, sauvegarde…)."""
    res = engine.spell_resolution(name, level, class_name)
    if not res:
        return ""
    mode = res["mode"]
    if mode == "attaque" and res["attaque"] is not None:
        if attack_flow is None:
            return mode
        if res["rayons"] and res["rayons"] > 1 and res["rayon_degats"] is not None:   # un jet d'attaque par rayon
            for i in range(res["rayons"]):
                spec = res["attaque"]
                spec.title = "{} — rayon {} / {}".format(res["nom"], i + 1, res["rayons"])
                attack_flow(spec, res["rayon_degats"])
        else:
            attack_flow(res["attaque"], res["degats"])
    elif mode == "sauvegarde":
        dd = "DD {} de sauvegarde de {}".format(res["dd"], res["carac"]) if res["dd"] else \
            "Jet de sauvegarde de {}".format(res["carac"])
        text = "{} — {}{}.\n\nÉchec : {}\nRéussite : {}\n\n{}".format(
            res["nom"], dd, " (niveau {})".format(res["niveau"]) if res["niveau"] else "", res["echec"], res["reussite"],
            {"moitie": "Succès = 1/2 dégâts", "aucun": "Succès = 0 dégât",
             "toujours": "Dégâts même en cas de succès"}.get(res.get("succes", ""), ""))
        if res["degats"] is not None:
            if ask_yes_no(win, "Jet de sauvegarde — " + dd, text + "\n\nLes cibles font leur jet. Lancer les dégâts ?",
                          yes="Lancer les dégâts", no="Fermer", default_no=False):
                spec = res["degats"]
                spec.note = "Échec : dégâts complets. Réussite : {}".format(res["reussite"].lower())
                r = roll_damage_dialog(win, spec)
                if r is not None:                         # v40 : demi-dégâts affichés pour les cibles qui réussissent
                    full = r.total
                    if res.get("succes") == "moitie":
                        text = "{} : échec = {} dégâts, réussite = {} (moitié).".format(res["nom"], full, full // 2)
                    elif res.get("succes") == "toujours":
                        text = "{} : {} dégâts, que le jet réussisse ou non.".format(res["nom"], full)
                    else:
                        text = "{} : échec = {} dégâts, réussite = aucun dégât.".format(res["nom"], full)
                    win.statusBar().showMessage(text, 12000)
        else:
            ask_yes_no(win, "Jet de sauvegarde — " + dd, text, yes="OK", no="Fermer", default_no=False)
    elif mode == "automatique" and res["degats"] is not None:
        roll_damage_dialog(win, res["degats"])
    elif mode == "soins" and res["soins"] is not None:
        r = roll_damage_dialog(win, res["soins"])
        if r is not None:
            picked = ask_choice(win, res["nom"], "Soins : {} PV. Qui est soigné ?".format(r.total),
                                ["Vous-même", "Un allié (rien n'est appliqué à votre fiche)"])
            if picked and norm(picked).startswith("vous"):
                gained = engine.heal(r.total)
                win.statusBar().showMessage("{} : +{} PV.".format(res["nom"], gained), 8000)
    return mode
