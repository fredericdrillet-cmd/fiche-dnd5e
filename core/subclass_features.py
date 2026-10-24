"""
Sous-classes du Guerrier gérées en détail (v36), sur le modèle de la Lame psychique du Roublard :

    - Chevalier runique (Tasha) : choix des runes (2 au niveau 3, 3 au 7, 4 au 10, 5 au 15 ; colline et tempête dès
      le niveau 7), une utilisation de chaque rune par repos court ou long (deux au niveau 15, Maître des runes),
      passifs des runes, Puissance des géants (bonus de maîtrise / repos long ; 1d6, 1d8 au niveau 10 avec Grande
      stature, 1d10 au niveau 18), Bouclier runique (niveau 7, bonus de maîtrise / repos long) ;
    - Soldat psi (Tasha) : dés d'énergie psionique (2 × bonus de maîtrise ; d6, d8 au 5, d10 au 11, d12 au 17), tous
      récupérés au repos long, un dé regagné par une action bonus une fois par repos court ; Champ protecteur,
      Frappe psionique, Mouvement télékinétique, Bond psi (7), Esprit gardé (10), Rempart de force (15),
      Maître télékinétique (18) ;
    - Archer arcanique (Xanathar) : options de Tir arcanique (2 au niveau 3, une de plus aux niveaux 7, 10, 15 et 18),
      2 utilisations par repos court ou long, dégâts doublés au niveau 18.
Les choix (runes, options de tir) sont enregistrés dans `ch.options_classe` ; les actions produites ont le format
des actions de classe (core/class_actions.py) et apparaissent dans l'encart « Actions, capacités de classe ».
Noms et textes : terminologie française des données de l'application (« Puissance des géants », « Bond psi »…).
"""
from __future__ import annotations

import re
from typing import Optional

from .rules import norm

RUNE_DC = "DD des runes : 8 + bonus de maîtrise + modificateur de Constitution"
RUNES = {
    "Rune du feu": {
        "niveau": 3, "icone": "🔥", "type": "Spécial", "degats": "2d6", "type_degats": "feu",
        "passif": "Votre bonus de maîtrise est doublé pour les tests de caractéristique utilisant une maîtrise d'outil.",
        "actif": "Quand vous touchez une créature avec une attaque d'arme, des entraves enflammées surgissent : elle "
                 "subit 2d6 dégâts de feu supplémentaires et doit réussir un JS de Force ou être entravée pendant "
                 "1 minute, subissant 2d6 dégâts de feu au début de chacun de ses tours (nouveau JS à la fin de chacun "
                 "de ses tours)."},
    "Rune du nuage": {
        "niveau": 3, "icone": "☁️", "type": "Réaction",
        "passif": "Avantage aux tests de Dextérité (Escamotage) et de Charisme (Tromperie).",
        "actif": "Quand vous ou une créature que vous voyez à 9 m ou moins êtes touché par une attaque, vous "
                 "redirigez l'attaque vers une autre créature de votre choix à 9 m ou moins (autre que l'attaquant), "
                 "qui la subit avec le même jet."},
    "Rune du givre": {
        "niveau": 3, "icone": "❄️", "type": "Action bonus",
        "passif": "Avantage aux tests de Sagesse (Dressage) et de Charisme (Intimidation).",
        "actif": "Pendant 10 minutes, +2 à tous vos tests de caractéristique et jets de sauvegarde de Force et de "
                 "Constitution."},
    "Rune de la pierre": {
        "niveau": 3, "icone": "🪨", "type": "Réaction",
        "passif": "Avantage aux tests de Sagesse (Perspicacité) ; vision dans le noir à 36 m.",
        "actif": "Quand une créature que vous voyez termine son tour à 9 m ou moins de vous, elle doit réussir un JS de "
                 "Sagesse ou être charmée pendant 1 minute : elle est neutralisée et sa vitesse tombe à 0 (nouveau JS "
                 "à la fin de chacun de ses tours)."},
    "Rune de la colline": {
        "niveau": 7, "icone": "⛰️", "type": "Action bonus",
        "passif": "Avantage aux jets de sauvegarde contre l'empoisonnement ; résistance aux dégâts de poison.",
        "actif": "Pendant 1 minute, résistance aux dégâts contondants, perforants et tranchants."},
    "Rune de la tempête": {
        "niveau": 7, "icone": "⛈️", "type": "Action bonus",
        "passif": "Avantage aux tests d'Intelligence (Arcanes) ; vous ne pouvez pas être surpris tant que vous n'êtes "
                  "pas neutralisé.",
        "actif": "Pendant 1 minute, état prophétique : par une réaction, vous donnez l'avantage ou le désavantage au "
                 "jet d'attaque, au test ou au jet de sauvegarde d'une créature que vous voyez à 18 m ou moins."},
}

ARCANE_DC = "DD : 8 + bonus de maîtrise + modificateur d'Intelligence"
# nom : (dés avant / à partir du niveau 18, type de dégâts, effet)
ARCANE_SHOTS = {
    "Flèche bannissante": ("", "2d6", "force", "JS de Charisme ou la cible est bannie dans la Féerie jusqu'à la fin de "
                           "son prochain tour (neutralisée) ; au niveau 18, elle subit aussi 2d6 dégâts de force."),
    "Flèche charmeuse": ("2d6", "4d6", "psychiques", "JS de Sagesse ou la cible est charmée par un de vos alliés à 9 m "
                         "ou moins jusqu'au début de votre prochain tour."),
    "Flèche explosive": ("2d6", "4d6", "force", "La flèche explose : la cible et chaque créature à 3 m ou moins "
                         "d'elle subissent les dégâts de force."),
    "Flèche affaiblissante": ("2d6", "4d6", "nécrotiques", "JS de Constitution ou les dégâts des attaques d'arme de "
                              "la cible sont réduits de moitié jusqu'au début de votre prochain tour."),
    "Flèche de saisie": ("2d6", "4d6", "poison", "Des ronces enserrent la cible pendant 1 minute : vitesse réduite "
                         "de 3 m et 2d6 dégâts tranchants la première fois qu'elle bouge à chaque tour (test de Force "
                         "(Athlétisme) pour s'en défaire)."),
    "Flèche perforante": ("1d6", "2d6", "perforants", "Pas de jet d'attaque : ligne de 9 m × 30 cm ; JS de Dextérité, "
                          "dégâts de l'arme + les dés perforants (moitié en cas de réussite)."),
    "Flèche chercheuse": ("1d6", "2d6", "force", "Vise une créature vue dans la dernière minute à portée : elle ignore "
                          "l'abri ; JS de Dextérité, dégâts de l'arme + les dés de force (moitié en cas de réussite), "
                          "et vous savez où elle se trouve."),
    "Flèche d'ombre": ("2d6", "4d6", "psychiques", "JS de Sagesse ou la cible ne voit rien au-delà de 1,50 m jusqu'au "
                       "début de votre prochain tour."),
}


# Tiers-lanceurs (v36) : écoles imposées pour les sorts de niveau 1+, sauf les sorts « libres » appris aux niveaux
# 3, 8, 14 et 20 (n'importe quelle école de la liste du magicien). Les sorts mineurs sont libres.
SCHOOL_RULES = {
    ("Guerrier", "chevalier occulte"): ("Évocation", "Abjuration"),
    ("Roublard", "arnaqueur arcanique"): ("Enchantement", "Illusion"),
    ("Roublard", "escroc arcanique"): ("Enchantement", "Illusion"),
}
FREE_SCHOOL_LEVELS = (3, 8, 14, 20)
MAGE_HAND = "Main de mage"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", norm(text)).strip("-")


def runes_known(level: int) -> int:
    return 0 if level < 3 else 2 if level < 7 else 3 if level < 10 else 4 if level < 15 else 5


def arcane_shots_known(level: int) -> int:
    return 0 if level < 3 else 2 + sum(1 for lvl in (7, 10, 15, 18) if level >= lvl)


def psi_die(level: int) -> int:
    return 6 if level < 5 else 8 if level < 11 else 10 if level < 17 else 12


def giant_die(level: int) -> int:
    return 6 if level < 10 else 8 if level < 18 else 10


class SubclassFeaturesMixin:
    """Mélangé à Engine (utilise ch, db, prof, mod, class_level, resource_used, set_resource_used…)."""

    def _fighter_sub(self, name: str) -> int:
        """Niveau de Guerrier si la sous-classe `name` est choisie et active (niveau 3+), sinon 0."""
        e = self.ch.find_class("Guerrier")
        if not e or e["niveau"] < 3 or norm(e.get("sous_classe", "")) != norm(name):
            return 0
        return e["niveau"]

    # ------------------------------------------------------------------ choix (runes, options de tir)
    def option_sets(self) -> list[dict]:
        """Ensembles de choix de sous-classe : [{key, label, total, options: {nom: description}, chosen}]."""
        out = []
        rk = self._fighter_sub("Chevalier runique")
        if rk:
            opts = {n: "Passif : {}\nActif (1 fois par repos court ou long) : {}".format(r["passif"], r["actif"])
                    for n, r in RUNES.items() if rk >= r["niveau"]}
            out.append({"key": "runes", "label": "Runes (Chevalier runique)", "total": runes_known(rk),
                        "options": opts, "chosen": list((self.ch.options_classe or {}).get("runes", []))})
        aa = self._fighter_sub("Archer arcanique")
        if aa:
            opts = {n: "{}{}".format("{} dégâts {} — ".format(v[1] if aa >= 18 else v[0], v[2]) if (v[1] if aa >= 18
                                                                                                    else v[0]) else "",
                                     v[3]) for n, v in ARCANE_SHOTS.items()}
            out.append({"key": "tirs", "label": "Options de Tir arcanique (Archer arcanique)",
                        "total": arcane_shots_known(aa), "options": opts,
                        "chosen": list((self.ch.options_classe or {}).get("tirs", []))})
        bm = self.maneuver_option_set()                  # v39 : manœuvres du Maître de guerre
        if bm:
            out.append(bm)
        meta = self.metamagic_option_set()               # v39 : options de métamagie de l'Ensorceleur
        if meta:
            out.append(meta)
        return out

    def sanitize_class_options(self) -> None:
        """Choix invalides retirés (sous-classe quittée, rune de niveau insuffisant, trop de choix)."""
        sets = {s["key"]: s for s in self.option_sets()}
        clean = {}
        for key, chosen in (self.ch.options_classe or {}).items():
            s = sets.get(key)
            if s is None:
                continue
            keep = []
            for n in chosen:
                if n in s["options"] and n not in keep:
                    keep.append(n)
            clean[key] = keep[:s["total"]]
        self.ch.options_classe = clean

    def set_class_option(self, key: str, index: int, name: str) -> None:
        chosen = list((self.ch.options_classe or {}).get(key, []))
        while len(chosen) <= index:
            chosen.append("")
        chosen[index] = name
        self.ch.options_classe = dict(self.ch.options_classe or {}, **{key: [c for c in chosen if c]})
        self.normalize()

    def chosen_options(self, key: str) -> list[str]:
        return list((self.ch.options_classe or {}).get(key, []))

    # ------------------------------------------------------------------ ressources à sphères
    @staticmethod
    def _sub_tracker(key: str, label: str, total: int, kind: str, recover: str, info: str, de: str = "",
                     where: str = "combat") -> dict:
        return {"key": key, "label": label, "total": total, "kind": kind, "recover": recover, "info": info,
                "where": where, "de": de}

    def subclass_trackers(self) -> list[dict]:
        out = []
        rk = self._fighter_sub("Chevalier runique")
        if rk:
            uses = 2 if rk >= 15 else 1
            for name in self.chosen_options("runes"):
                out.append(self._sub_tracker("rune:" + _slug(name), name, uses, "sens", "repos court",
                                             "{} — {} utilisation{} par repos court ou long — {}".format(
                                                 name, uses, "s" * (uses > 1), RUNE_DC)))
            out.append(self._sub_tracker("puissance_geants", "Puissance des géants", self.prof, "sursaut", "repos long",
                                         "Bonus de maîtrise ({}) utilisations — +1d{} dégâts une fois par tour — "
                                         "repos long".format(self.prof, giant_die(rk)), de="d{}".format(giant_die(rk))))
            if rk >= 7:
                out.append(self._sub_tracker("bouclier_runique", "Bouclier runique", self.prof, "conduit", "repos long",
                                             "Réaction : l'attaquant relance son d20 — bonus de maîtrise ({}) "
                                             "utilisations par repos long".format(self.prof)))
        pw = self._fighter_sub("Soldat psi")
        if pw:
            sides = psi_die(pw)
            out.append(self._sub_tracker("psi_guerrier", "Dés d'énergie psionique", 2 * self.prof, "psionique",
                                         "repos long", "{} dés (d{}) = 2 × bonus de maîtrise — tous récupérés au repos "
                                         "long ; 1 dé regagné par une action bonus une fois par repos court".format(
                                             2 * self.prof, sides), de="d{}".format(sides)))
            for key, lvl, rec in (("tk_gratuit", 3, "repos court"), ("bond_gratuit", 7, "repos court"),
                                  ("rempart_gratuit", 15, "repos long"), ("tkm_gratuit", 18, "repos long"),
                                  ("psi_g_recup", 3, "repos court")):
                if pw >= lvl:
                    out.append(self._sub_tracker(key, key, 1, "ki", rec, "Utilisation gratuite", where="interne"))
        aa = self._fighter_sub("Archer arcanique")
        if aa:
            out.append(self._sub_tracker("tir_arcanique", "Tir arcanique", 2, "superiorite", "repos court",
                                         "2 utilisations, une fois par tour, récupérées au repos court ou long — "
                                         + ARCANE_DC))
        return out

    def subclass_short_rest_keys(self) -> list[str]:
        return [t["key"] for t in self.subclass_trackers() if t["recover"] == "repos court"]

    # ------------------------------------------------------------------ actions
    # ------------------------------------------------------------------ écoles imposées (tiers-lanceurs)
    def school_restriction(self, class_name: str) -> Optional[dict]:
        """{ecoles, libres_max, libres_utilises, sous_classe} pour le Chevalier occulte / l'Arnaqueur arcanique."""
        e = self.ch.find_class(class_name)
        if not e or e["niveau"] < 3:
            return None
        schools = SCHOOL_RULES.get((class_name, norm(e.get("sous_classe", ""))))
        if not schools:
            return None
        free_max = sum(1 for lvl in FREE_SCHOOL_LEVELS if e["niveau"] >= lvl)
        return {"ecoles": schools, "libres_max": free_max, "libres_utilises": self.off_school_count(class_name, schools),
                "sous_classe": e.get("sous_classe", "")}

    def off_school_count(self, class_name: str, schools=None) -> int:
        if schools is None:
            r = self.school_restriction(class_name)
            if r is None:
                return 0
            schools = r["ecoles"]
        n = 0
        for s in self.ch.sorts.get(class_name, []):
            sp = self.db.find_spell(s["nom"]) or {}
            if sp.get("niveau", 0) > 0 and sp.get("ecole") not in schools:
                n += 1
        return n

    def school_check(self, class_name: str, spell: dict) -> tuple[bool, str]:
        """(apprenable ?, explication) selon les écoles imposées ; toujours vrai hors Chevalier occulte / Arnaqueur."""
        r = self.school_restriction(class_name)
        if r is None or not spell or int(spell.get("niveau") or 0) == 0 or spell.get("ecole") in r["ecoles"]:
            return True, ""
        left = r["libres_max"] - r["libres_utilises"]
        if left > 0:
            return True, "Sort libre (toute école) : {} restant(s) sur {}.".format(left, r["libres_max"])
        return False, "{} : sorts d'{} uniquement — sorts libres (niveaux 3, 8, 14, 20) épuisés ({} / {}).".format(
            r["sous_classe"], " ou d'".join(x.lower() for x in r["ecoles"]), r["libres_utilises"], r["libres_max"])

    def ensure_granted_cantrips(self) -> None:
        """Arnaqueur arcanique : Main de mage connue d'office (retirée si la sous-classe est quittée)."""
        rogue = self.ch.find_class("Roublard")
        at = bool(rogue and rogue["niveau"] >= 3 and norm(rogue.get("sous_classe", "")) in
                  ("arnaqueur arcanique", "escroc arcanique"))
        lst = self.ch.sorts.get("Roublard", [])
        if at and self.db.find_spell(MAGE_HAND) and not any(s["nom"] == MAGE_HAND for s in lst):
            self.ch.sorts.setdefault("Roublard", []).append({"nom": MAGE_HAND, "prepare": True, "accorde": True})
        elif not at and lst:
            self.ch.sorts["Roublard"] = [s for s in lst if not (s["nom"] == MAGE_HAND and s.get("accorde"))]

    def _act(self, aid: str, nom: str, icone: str, kind: str, cost: dict, desc: str, degats: str = "",
             type_degats: str = "", niveau: int = 3, sous_classe: str = "", classe: str = "Guerrier", **extra) -> dict:
        return dict({"id": aid, "nom": nom, "icone": icone, "classe": classe, "sous_classe": sous_classe,
                     "niveau": niveau, "type": kind, "cout": cost, "jet": "degats" if degats else "aucun",
                     "degats": degats, "type_degats": type_degats, "description": desc, "origine_sc": True}, **extra)

    def subclass_actions(self) -> list[dict]:
        out = []
        rk = self._fighter_sub("Chevalier runique")
        if rk:
            sc = "Chevalier runique"
            dc = 8 + self.prof + self.mod("Constitution")
            for name in self.chosen_options("runes"):
                r = RUNES[name]
                key = "rune:" + _slug(name)
                out.append(self._act(key, name, r["icone"], r["type"], {"ressource": key, "n": 1},
                                     "{} (DD {}). Passif : {}".format(r["actif"], dc, r["passif"]),
                                     r.get("degats", ""), r.get("type_degats", ""), sous_classe=sc))
            out.append(self._act("puissance_geants", "Puissance des géants", "🗿", "Action bonus",
                                 {"ressource": "puissance_geants", "n": 1},
                                 "Pendant 1 minute : taille Grande{}, avantage aux tests et JS de Force, et une fois "
                                 "par tour une attaque d'arme ou à mains nues qui touche inflige 1d{} dégâts "
                                 "supplémentaires{}.".format(" (Très grande possible, allonge +1,50 m)" if rk >= 18
                                                            else "", giant_die(rk),
                                                            " (Grande stature, niveau 10)" if rk >= 10 else ""),
                                 "1d{}".format(giant_die(rk)), "", sous_classe=sc, effet=""))
            if rk >= 7:
                out.append(self._act("bouclier_runique", "Bouclier runique", "🛡", "Réaction",
                                     {"ressource": "bouclier_runique", "n": 1},
                                     "Quand une créature que vous voyez à 18 m ou moins est touchée par une attaque, "
                                     "l'attaquant relance le d20 et garde le nouveau résultat.", niveau=7,
                                     sous_classe=sc))
        pw = self._fighter_sub("Soldat psi")
        if pw:
            sc, die = "Soldat psi", "1d{}".format(psi_die(pw))
            intm = self.mod("Intelligence")
            dmg = die + ("{:+d}".format(intm) if intm else "")
            psi = {"ressource": "psi_guerrier", "n": 1}
            out.append(self._act("psi_champ", "Champ protecteur", "🛡", "Réaction", psi,
                                 "Quand vous ou une créature visible à 9 m subissez des dégâts : réduction de {} "
                                 "(dé + modificateur d'Intelligence).".format(dmg), dmg, "", sous_classe=sc))
            out.append(self._act("psi_frappe", "Frappe psionique", "💥", "Spécial", psi,
                                 "Une fois par tour, après un coup d'arme sur une cible à 9 m : {} dégâts de force "
                                 "(dé + modificateur d'Intelligence){}.".format(
                                     dmg, " ; Poussée télékinétique : JS de Force (DD {}) ou à terre / repoussée de "
                                          "3 m".format(8 + self.prof + intm) if pw >= 7 else ""),
                                 dmg, "force", sous_classe=sc))
            out.append(self._act("psi_tk", "Mouvement télékinétique", "🌀", "Action",
                                 dict(psi, gratuit="tk_gratuit"),
                                 "Déplacez de 9 m un objet ou une créature consentante de taille Grande ou moins à "
                                 "9 m (gratuit une fois par repos court ou long, sinon 1 dé).", sous_classe=sc))
            out.append(self._act("psi_recup_g", "Récupération psionique", "🔋", "Action bonus",
                                 {"ressource": "psi_g_recup", "n": 1}, "Regagnez 1 dé d'énergie psionique (une fois "
                                 "par repos court ou long).", sous_classe=sc, rend="psi_guerrier"))
            if pw >= 7:
                out.append(self._act("psi_bond", "Bond psi", "🪽", "Action bonus", dict(psi, gratuit="bond_gratuit"),
                                     "Vitesse de vol égale à deux fois votre vitesse au sol jusqu'à la fin du tour "
                                     "(gratuit une fois par repos court ou long, sinon 1 dé).", niveau=7,
                                     sous_classe=sc))
            if pw >= 10:
                out.append(self._act("psi_esprit", "Esprit gardé", "🧠", "Spécial", psi,
                                     "Au début de votre tour, si vous êtes charmé ou effrayé : dépensez 1 dé pour mettre "
                                     "fin à tous ces effets (résistance aux dégâts psychiques en permanence).",
                                     niveau=10, sous_classe=sc))
            if pw >= 15:
                out.append(self._act("psi_rempart", "Rempart de force", "🏰", "Action bonus",
                                     dict(psi, gratuit="rempart_gratuit"),
                                     "Jusqu'à {} créature(s) (vous compris) à 9 m : abri partiel (+2 CA et JS de "
                                     "Dextérité) pendant 1 minute (gratuit une fois par repos long, sinon 1 dé)."
                                     .format(max(1, intm)), niveau=15, sous_classe=sc))
            if pw >= 18:
                out.append(self._act("psi_maitre", "Maître télékinétique", "✋", "Action",
                                     dict(psi, gratuit="tkm_gratuit"),
                                     "Lancez Télékinésie sans composante (Intelligence) ; tant que vous vous "
                                     "concentrez, une attaque d'arme par une action bonus à chaque tour (gratuit une "
                                     "fois par repos long, sinon 1 dé).", niveau=18, sous_classe=sc))
        rogue = self.ch.find_class("Roublard")
        if rogue and rogue["niveau"] >= 3 and norm(rogue.get("sous_classe", "")) in ("arnaqueur arcanique",
                                                                                      "escroc arcanique"):
            out.append(self._act("main_arcanique", "Main de mage arcanique", "🫳", "Action bonus", {},
                                 "Passe-passe à distance : vous contrôlez votre Main de mage par une action bonus. Elle "
                                 "peut être invisible, ranger ou prendre un objet dans un contenant porté par une autre "
                                 "créature, crocheter une serrure ou désamorcer un piège à distance avec vos outils de "
                                 "voleur (Dextérité (Escamotage) opposée à la Sagesse (Perception) de la créature pour "
                                 "passer inaperçu).", classe="Roublard", sous_classe=rogue.get("sous_classe", "")))
        aa = self._fighter_sub("Archer arcanique")
        if aa:
            dc = 8 + self.prof + self.mod("Intelligence")
            for name in self.chosen_options("tirs"):
                low, high, dtype, effect = ARCANE_SHOTS[name]
                dice = high if aa >= 18 else low
                out.append(self._act("tir:" + _slug(name), name, "🏹", "Spécial",
                                     {"ressource": "tir_arcanique", "n": 1},
                                     "Une fois par tour, quand une flèche tirée d'un arc court ou long touche : {} "
                                     "(DD {}).".format(effect, dc), dice, dtype if dice else "",
                                     sous_classe="Archer arcanique"))
        return out

    def subclass_passives(self) -> list[dict]:
        rk = self._fighter_sub("Chevalier runique")
        return [{"nom": "{} (passif)".format(n), "description": RUNES[n]["passif"], "niveau": 3,
                 "source": "Chevalier runique niv. {}".format(RUNES[n]["niveau"])} for n in self.chosen_options("runes")
                if rk]

    def sub_action(self, aid: str) -> Optional[dict]:
        return next((a for a in self.subclass_actions() if a["id"] == aid), None)
